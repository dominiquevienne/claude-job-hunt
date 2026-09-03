#!/usr/bin/env python3
"""Fetch ads from a Personio careers site — the DACH ATS, one employer at a
time.

Personio is the applicant-tracking system most German, Austrian and **Swiss**
SMEs run their careers page on. Each tenant publishes a **documented XML feed**
of its open positions, with the full description, and it needs nothing:

  GET https://<tenant>.jobs.personio.de/xml     → every open position
  GET https://<tenant>.jobs.personio.com/xml    → the same bytes
  https://<tenant>.jobs.personio.de/job/<id>    → the ad, for a human

**No browser, no account, no key.** Unlike `arbeitsagentur.md` there is not
even a published key to send, and unlike the country boards there is no window:
one request returns the employer's whole board, descriptions included.

Verified against a live tenant on 2026-09-01.

THE TRAP THAT OUTLIVES THE BOARD: **`?language=` empties the ads without
emptying the board.**

    /xml                 7 positions, 7 with text, median 4 556 characters
    /xml?language=de     7 positions, 7 with text, median 4 556
    /xml?language=en     7 positions, 1 with text, median 0
    /xml?language=fr     7 positions, 0 with text, median 0

Same count, same ids, HTTP 200, valid XML — and on `fr` **not one of the seven
ads carries a word of its own description**. The parameter does not filter the
board or translate it; it serves whatever translation the employer happened to
enter, and returns the position with an empty body when there is none.

It is the worst shape this failure takes, because the request that triggers it
is a reasonable one: anybody asking for the language they read gets a
full-looking board of empty ads. So the adapter **reads the default feed**, and
when a language is requested it fetches both and refuses to report a language
whose text is missing — see `language_check`.

THE SECOND ONE IS ISSUE #55's, IN A NEW TAG. Every `<value>` in
`<jobDescriptions>` is wrapped in CDATA:

    <value><![CDATA[<span style="…">ottonova - wir sind …</span>]]></value>

A `<value>([^<]*)</value>` extractor returns nothing at all from a perfectly
valid feed. It is the same wrapper `hays-fr.md` found in `<loc>`, in a
different element, on a different vendor — which is the argument for the
tolerant pattern being the house default rather than a per-board fix.

THERE IS NO TENANT DIRECTORY. Like `umantis.md`, `taleez.md` and `flatchr.md`,
Personio publishes no cross-tenant search and its own marketing sitemap lists
no employer. **Ask the user for the careers URL and never guess a tenant** — a
wrong one answers a Next.js 404 page, not an error.

*(`robots.txt` on a tenant host is a 404: none is published, so nothing is
disallowed. The marketing host `www.personio.de` answered **429 on every
attempt**, so its own robots.txt could not be read — that is not established,
and it is recorded as not established rather than assumed either way. The
adapter reads only tenant hosts.)*

Usage:
  personio.py jobs --tenant ottonova
  personio.py jobs --tenant ottonova --language en
  personio.py check --tenant ottonova

Output: one JSON object per line.
"""

import argparse
import html as html_mod
import json
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _robots import verdict as robots_verdict

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

POSITION_RE = re.compile(r"(?s)<position>(.*?)</position>")
# Issue #55's tolerant pattern, carried to a new element: every <value> in this
# feed is CDATA-wrapped, and a `<value>([^<]*)` extractor returns nothing.
CDATA_RE = re.compile(r"(?s)<!\[CDATA\[(.*?)\]\]>")
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[personio] {msg}", file=sys.stderr)


def host(tenant):
    if "." in tenant:
        # A full careers URL or hostname was given; keep the host only.
        h = re.sub(r"^https?://", "", tenant).split("/")[0]
        return h
    return f"{tenant}.jobs.personio.de"


def get(url, retries=2):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/xml,text/xml,*/*;q=0.9",
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace"), r.headers.get(
                    "Content-Type", "")
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                if attempt == retries:
                    die(f"{url}: HTTP 429, rate limited. Personio throttles "
                        "per host; wait and retry rather than parallelising.")
                time.sleep(5.0 * (attempt + 1))
                continue
            if attempt == retries:
                die(f"{url}: HTTP {exc.code}")
            time.sleep(1.5 * (attempt + 1))
        except (urllib.error.URLError, OSError) as exc:
            if attempt == retries:
                die(f"{url}: {exc}")
            time.sleep(1.5 * (attempt + 1))
    return "", ""


def feed(tenant, language=None):
    url = f"https://{host(tenant)}/xml"
    if language:
        url += "?" + urllib.parse.urlencode({"language": language})
    body, ctype = get(url)
    if "xml" not in (ctype or "").lower() and "<position>" not in body:
        # A wrong tenant answers the careers app's own 404 page, as HTML.
        die(f"{url} did not return XML (content-type {ctype!r}, "
            f"{len(body)} characters). A tenant that does not exist answers "
            "the careers app's 404 page rather than an error, so check the "
            "careers URL — there is no tenant directory to look it up in.")
    return body, url


def text_of(raw):
    return WS_RE.sub(" ", TAG_RE.sub(" ", html_mod.unescape(raw or ""))).strip()


def one(tag, block):
    m = re.search(r"(?s)<%s>(.*?)</%s>" % (tag, tag), block)
    if not m:
        return None
    v = m.group(1)
    cd = CDATA_RE.search(v)
    v = cd.group(1) if cd else v
    v = html_mod.unescape(v).strip()
    return v or None


def sections(block):
    """`jobDescriptions` is a list of named sections, each CDATA-wrapped.

    The employer writes their own headings — DEIN TEAM, DEINE AUFGABEN — so
    this is the description already split, the way `join.md`'s is. Kept as
    named parts and also joined, because a cover letter wants the whole thing
    and a scorer wants the requirements.
    """
    out = []
    for jd in re.findall(r"(?s)<jobDescription>(.*?)</jobDescription>", block):
        name = one("name", jd)
        val = one("value", jd)
        if val:
            out.append({"heading": name, "text": text_of(val)})
    return out


def offices(block):
    main = one("office", block)
    extra = []
    m = re.search(r"(?s)<additionalOffices>(.*?)</additionalOffices>", block)
    if m:
        extra = [html_mod.unescape(x).strip()
                 for x in re.findall(r"<office>(.*?)</office>", m.group(1))]
    return main, [x for x in extra if x and x != main]


def positions(body):
    blocks = POSITION_RE.findall(body)
    if not blocks:
        # The invariant from issue #55: an empty result is only credible if
        # the document is empty too.
        die(f"no <position> elements in {len(body)} characters of feed. A "
            "tenant with nothing open returns an empty <workzag-jobs/>, so "
            "this is more likely a reading fault or the wrong host.")
    return blocks


def card(tenant, block):
    ident = one("id", block)
    main, extra = offices(block)
    secs = sections(block)
    body = " ".join(s["text"] for s in secs).strip()
    return {
        "id": ident,
        "ledger_id": f"personio:{host(tenant)}:{ident}",
        "url": f"https://{host(tenant)}/job/{ident}",
        "title": one("name", block),
        # The legal entity, which on a group tenant is not the tenant name.
        "company": one("subcompany", block),
        "tenant": host(tenant),
        "office": main,
        "additional_offices": extra or None,
        "locations_count": 1 + len(extra),
        "department": one("department", block),
        "category": one("recruitingCategory", block),
        "employment_type": one("employmentType", block),
        "seniority": one("seniority", block),
        "schedule": one("schedule", block),
        "occupation": one("occupation", block),
        "occupation_category": one("occupationCategory", block),
        "keywords": one("keywords", block),
        "published": one("createdAt", block),
        "description": body or None,
        "description_sections": secs or None,
    }


def coverage(blocks):
    lens = [len(" ".join(s["text"] for s in sections(b))) for b in blocks]
    return (sum(1 for x in lens if x > 200),
            int(statistics.median(lens)) if lens else 0)


# Tried when the feed in hand turns out to be mostly empty. The default is
# NOT reliably the full one — see `text_check`.
ALTERNATES = (None, "de", "en")


def text_check(tenant, language, blocks):
    """Refuse to serve a feed whose ads have lost their text — either way.

    `?language=` does not translate the board: it serves whatever translation
    the employer entered, and returns the position with an empty body when
    there is none. Same count, same ids, HTTP 200.

    **And the default feed is not reliably the full one.** Measured across
    four tenants:

        ottonova     default 7/7 described   en 1/7    fr 0/7
        autarcenergy default 11/12           en 3/12   fr 0/12
        dieseo-gmbh  default 64/69           en 12/69  fr 0/69
        merantix     default 1/16            en 15/16  fr 0/16

    On `merantix` the DEFAULT is the empty one and English carries the text.
    An adapter that trusts the default and refuses every language would hand
    that tenant's user fifteen empty ads and reject the feed that works.

    So the check is symmetric: whichever feed was asked for, if it is mostly
    empty, the alternatives are measured and the caller is told which one
    carries the ads — never handed the empty one.
    """
    with_text, median = coverage(blocks)
    if with_text >= max(1, len(blocks) // 2):
        return
    rows = [(language, len(blocks), with_text, median)]
    for alt in ALTERNATES:
        if alt == language:
            continue
        try:
            body, _ = feed(tenant, alt)
            b = positions(body)
        except SystemExit:
            continue
        w, m = coverage(b)
        rows.append((alt, len(b), w, m))
        time.sleep(0.5)
    best = max(rows, key=lambda r: r[2])
    table = "\n".join(
        f"    {'(default)' if lang is None else '--language ' + lang:16} "
        f"{n:3} positions, {w:3} with text, median {m}"
        for lang, n, w, m in rows)
    asked = "(default)" if language is None else f"--language {language}"
    if best[2] <= max(1, best[1] // 2):
        die(f"{asked} returned {len(blocks)} positions and only {with_text} "
            f"carry any description, and no other feed does better:\n{table}\n"
            "This tenant publishes positions without text in every language "
            "measured. There is nothing here for cover-letter to read.")
    better = "(default)" if best[0] is None else f"--language {best[0]}"
    die(f"{asked} returned {len(blocks)} positions and only {with_text} carry "
        f"any description (median {median} characters):\n{table}\n"
        f"**{better} carries the text on this tenant** — {best[2]} of "
        f"{best[1]}. The language parameter does not translate the board, it "
        "serves whatever the employer entered, and the default feed is not "
        "reliably the full one. Re-run with that feed.")


def cmd_jobs(a):
    _v = robots_verdict(f"{a.tenant}.jobs.personio.de")
    if not _v["sweep"]:
        die(f"{_v['host']}: {_v['reason']} On Personio the host belongs to the employer, so this is that employer's "
            f"answer and not the platform's. Issue #73.",
                8 if _v["sweep"] is None else 7)
    body, url = feed(a.tenant, a.language)
    blocks = positions(body)
    note(f"{len(blocks)} open positions — {url}")
    text_check(a.tenant, a.language, blocks)
    kept = 0
    for b in blocks:
        c = card(a.tenant, b)
        if a.office and (a.office.lower() not in
                         " ".join(filter(None, [c["office"]]
                                         + (c["additional_offices"] or []))
                                  ).lower()):
            continue
        print(json.dumps(c, ensure_ascii=False))
        kept += 1
    with_text, median = coverage(blocks)
    note(f"{kept} returned; {with_text} of {len(blocks)} carry a description, "
         f"median {median} characters")
    multi = sum(1 for b in blocks if offices(b)[1])
    if multi:
        note(f"{multi} are posted in more than one office — additionalOffices "
             "is a sibling element, and an ad read as single-site would put "
             "the candidate in the wrong city.")


def cmd_check(a):
    _v = robots_verdict(f"{a.tenant}.jobs.personio.de")
    if not _v["sweep"]:
        die(f"{_v['host']}: {_v['reason']} On Personio the host belongs to the employer, so this is that employer's "
            f"answer and not the platform's — and it refuses the content, not just the sweep. Issue #73.",
                8 if _v["sweep"] is None else 7)
    body, url = feed(a.tenant)
    blocks = positions(body)
    with_text, median = coverage(blocks)
    row = {"tenant": host(a.tenant), "url": url, "positions": len(blocks),
           "with_description": with_text, "median_chars": median,
           "languages": {}}
    for lang in (a.language and [a.language]) or ["en", "fr"]:
        try:
            b2, _ = feed(a.tenant, lang)
            p2 = positions(b2)
            w2, m2 = coverage(p2)
            row["languages"][lang] = {"positions": len(p2),
                                      "with_description": w2,
                                      "median_chars": m2}
        except SystemExit:
            row["languages"][lang] = None
        time.sleep(a.delay)
    print(json.dumps(row, ensure_ascii=False))
    for lang, v in row["languages"].items():
        if v and v["positions"] and v["with_description"] < v["positions"]:
            note(f"--language {lang} keeps all {v['positions']} positions but "
                 f"only {v['with_description']} keep their text. Do not sweep "
                 "this tenant in that language.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, h in (("jobs", cmd_jobs, "the employer's open positions"),
                        ("check", cmd_check,
                         "what the tenant publishes, and in which languages")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--tenant", required=True,
                       help="the tenant name or the careers hostname — "
                            "`ottonova` or `ottonova.jobs.personio.de`. "
                            "**There is no directory: ask the user for the "
                            "URL, never guess**")
        c.add_argument("--language", help="a language code. Read the trap "
                                          "before using it")
        c.add_argument("--delay", type=float, default=1.0)
        if name == "jobs":
            c.add_argument("--office", help="keep positions in this office")
        c.set_defaults(func=fn)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
