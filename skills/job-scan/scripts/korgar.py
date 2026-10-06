#!/usr/bin/env python3
"""Korgar (`korgar.tj`) — a Tajik generalist board whose declared sitemap is the enumerator, and whose FILTER is a safety condition rather than an optimisation.

  korgar.py list [--limit N] [--with-ads --max N] [--no-site-total]
  korgar.py ad --url <advertisement URL>

THE SITEMAP IS THE ROUTE, AND FOUR URLS IN FIVE OF IT MUST NEVER BE FETCHED

`/sitemap.xml` is 2 941 163 bytes and carries **42 851 `<loc>`, 42 761 of them
distinct** (2026-10-06 06:01 UTC). Its composition, measured by first path
segment:

    /rezume      33 646   78.5 %   CANDIDATE CVs (32 687 carry a terminal id)
    /vakanciya    6 701   15.6 %   the advertisements — 6 701 of 6 701 carry one
    /vakancii     1 248    2.9 %   FACETS: /vakancii/gorod/<city>, /kategorii — 0 ids
    /resume       1 248    2.9 %   FACETS of the CV section — 0 ids
    /soiskatel, /rabotodatel, /, /kontakti     7 pages

**The rules are 105 bytes with not one `Disallow`, so `allowed()` answers True on
`/rezume/<slug>_<id>` exactly as on `/vakanciya/<slug>_<id>`.** *A host that
forbids nothing has not thereby consented to our taking everything it exposes.*
So the filter here is a CONDITION OF SAFETY: an adapter that walked the whole
sitemap would harvest **32 687 CVs of real people**. No `/rezume/` or `/resume/`
URL has ever been fetched from here and none will be.

TWO LAYERS, AND THEY ARE INDEPENDENT ON PURPOSE. `ADVERT_RE` requires the
`/vakanciya/` segment AND a terminal `_<digits>`. Either alone would work today —
`/vakancii` does not contain `/vakanciya/`, and the 6 701 all carry ids — so the
redundancy is declared rather than silent: the first layer sorts the SECTION, the
second sorts an ADVERT from a facet of the same section. *`/rezume` is the proof
that one layer is not enough: 959 of its 33 646 are facets carrying no id, so a
section filter alone does not sort natures.*

A CORRECTION OF OUR OWN PUBLISHED FIGURE, 2026-10-06. `korgar.md` said «/rezume/
33 646 + /resume/ 1 248 = 34 894 CVs, 81.4 %». That added two families on the
RESEMBLANCE OF THEIR NAMES: `/resume/` holds the CV section's FACET pages, not
CVs. The CV count is **32 687 URLs carrying an identifier, 76.3 %** of the
sitemap. *The safety sentence does not soften — it sharpens.*

WHAT AN ADVERTISEMENT CARRIES, MEASURED ON THREE (first, middle and last of the
6 701, each URL taken FROM the sitemap and never composed): exactly ONE
`application/ld+json` block, holding one complete `JobPosting` with the same ten
keys on all three.

    identifier.value    the numeric id — 221488 / 157622 / 50087, and it is the
                        same number the URL ends in, so the key is attested twice
    identifier.name     «Компания» — the host LABELS this field *company* and
                        puts the ADVERT ID in it. The label is wrong; the value
                        is right. *A field name is not a field meaning.*
    hiringOrganization  name filled 3/3 **and filled with the WORD** «Компания»
                        — «company» — on all three. It is a PLACEHOLDER, so the
                        employer is NOT published in a field, and `employer`
                        comes back null while the host's own string is kept in
                        `employer_as_published` so that nothing is hidden.
                        *`identifier.name` is the same word: the host writes the
                        label into two different `name` fields.* **This is the
                        `$undefined` family — a field PRESENT and FILLED with a
                        constant — and `if x` calls it filled. Emitting it as an
                        employer would have written a fabricated company into a
                        ledger.** The employer does appear in the DESCRIPTION
                        prose on one of the three; prose is not parsed and no
                        employer is guessed from it.
    baseSalary          currency TJS, value.value, unitText MONTH — **0 on two of
                        the three**, so a zero is «not stated» and is emitted as
                        null, never as 0
    jobLocation.address addressCountry / addressRegion / addressLocality — and
                        also streetAddress and postalCode, WHICH THIS DOES NOT
                        EMIT
    employmentType      «CONTRACTOR» on all three — constant, so probably a
                        template default and not a statement about the post
    datePosted          real and spread: 2021-09-29, 2026-04-19, 2026-10-05
    description         413, 17 and 7 characters — a stub on two of three

**NO CONTACT IS PRESENT AND NONE IS WITHHELD.** Four patterns — an e-mail shape,
`+992`, an anchored nine-digit run, a messaging app — over every string field of
the `JobPosting` AND over the visible text of all three pages: zero. So the
record carries **no `withheld_fields` at all**, because a record claiming to have
withheld a contact nobody deposited would lie about our own discretion in the one
direction no outside guard can check.

**A 2021 ADVERTISEMENT IS STILL LISTED, AND THE SITEMAP HAS NO `lastmod`** — zero
of 42 851. So 6 701 is «advertisement URLs in the declared sitemap» and never
«live vacancies»; the living share is unknown and the walk says so. The site's own
figure is «Более 3000», which **under**states the sitemap by a factor of ~2.2.

THE SECOND DECLARED SITEMAP IS A 404. The rules declare `/sitemap.xml` AND
`/ru/sitemap.xml`; the second answers HTTP 404 (6 603 bytes, not saved). *So there
is ONE document and no locale multiplier — checked before any count was
published, because the same cluster had just produced a ×4 by locale on yora.tj
and a ×2 on isgar.com.tm.* No `/ru/`, `/tj/` or `/en/` prefix appears on any of
the 42 851.

THE RULES: 105 bytes, `state: read`, `certain: True`, zero `Disallow`, no
`Crawl-delay` — so our own 2 s floor applies. `identity()` answers `claude-user`
/ http. Guard taken on every exact path in turns distinct from the retrievals.
Measured 2026-10-06 06:01–06:04 UTC (#664).
"""

import argparse
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _ldjson import absent_reason, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _sitemap import count as sitemap_count, locs as sitemap_locs
from _ua import UA
from _zero import empty_first_page

HOST = "korgar.tj"
BASE = "https://korgar.tj"
SITEMAP = BASE + "/sitemap.xml"

# The SECTION, then the ADVERT. Two layers, declared redundant: see the module
# docstring. `/vakancii/gorod/dushanbe` fails the first; `/vakanciya/kategorii`,
# were it to appear, fails the second.
ADVERT_SEGMENT = "/vakanciya/"
ADVERT_RE = re.compile(r"^https://korgar\.tj/vakanciya/[^/]*_(\d+)$")

# Never fetched, never emitted, and named here so that a reader of this file can
# see WHAT the filter is protecting rather than only that it filters.
CANDIDATE_SEGMENTS = ("/rezume/", "/resume/", "/soiskatel")

# The host serves these inside `jobLocation.address` and this adapter drops them.
ADDRESS_DROPPED = ("streetAddress", "postalCode")

# `hiringOrganization.name` is this literal WORD — «company» — on 3 of 3
# advertisements measured 2026-10-06, and `identifier.name` is the same word.
# A placeholder, not a name: see the module docstring. The constant is named and
# dated here so that the day the host starts publishing real employers, this stops
# matching and `employer` fills itself without anyone editing a list.
EMPLOYER_PLACEHOLDER = "\u041a\u043e\u043c\u043f\u0430\u043d\u0438\u044f"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[korgar] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def refuse_candidate(url):
    """The filter, as a REFUSAL that can fire rather than a comprehension that
    cannot. `allowed()` permits these paths; we do not, and this is where that
    decision lives."""
    for seg in CANDIDATE_SEGMENTS:
        if seg in url:
            die(f"{url}: a candidate CV or jobseeker path. **The rules permit it and this "
                f"adapter refuses it: 32 687 of the sitemap's 42 851 URLs are CVs of real "
                f"people, and the filter on {ADVERT_SEGMENT} is a safety condition, not an "
                f"optimisation.**", EXIT_REFUSED)


_PACE = Pace(HOST, own=2.0)   # the host writes no Crawl-delay — our own floor applies


def get(url):
    refuse_candidate(url)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xml;q=0.9",
        "Accept-Language": "ru,tg;q=0.7,en;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def adverts(xml):
    """The two layers, in order, each returning its own count so the caller can
    print what the filter REMOVED and not only what it kept."""
    everything = sitemap_locs(xml)
    section = sitemap_locs(xml, contains=ADVERT_SEGMENT)
    out, rejected = [], 0
    for u in section:
        m = ADVERT_RE.match(u.strip())
        if m:
            out.append((u.strip(), m.group(1)))
        else:
            rejected += 1          # a facet of the advert section, if the host ever adds one
    return everything, section, out, rejected


def money(base):
    """`baseSalary` → (amount, currency, unit). **A zero is «not stated» and
    comes back as None**: measured 0 on two of three advertisements, and `if x`
    would have called that a filled field."""
    if not isinstance(base, dict):
        return None, None, None
    val = base.get("value")
    amount = val.get("value") if isinstance(val, dict) else val
    unit = val.get("unitText") if isinstance(val, dict) else None
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        amount = None
    if not amount:                 # 0 and None alike: the host states no salary
        amount = None
    return amount, (base.get("currency") or None), (unit or None)


def place(job_location):
    """City, region and country — and **never** `streetAddress` or `postalCode`,
    which this host does serve."""
    addr = job_location.get("address") if isinstance(job_location, dict) else None
    if isinstance(addr, str):
        return {"locality": text(addr) or None, "region": None, "country": None}
    addr = addr or {}
    return {"locality": (addr.get("addressLocality") or None),
            "region": (addr.get("addressRegion") or None),
            "country": (addr.get("addressCountry") or None)}


def published_employer(org):
    """`(employer, as_published)`. The second is always what the host sent; the
    first is None whenever that is the measured placeholder, because writing
    «Компания» into a ledger's `employer` would fabricate a company.

    *The test is on EQUALITY with a named, dated constant rather than membership
    of a growing refusal list — so it stops matching by itself the day this host
    publishes a real name, instead of needing someone to curate the list.*"""
    if not isinstance(org, dict):
        return None, None
    raw = (org.get("name") or "").strip() or None
    if raw is not None and raw == EMPLOYER_PLACEHOLDER:
        return None, raw
    return raw, raw


def record(url, ident, posting):
    org = posting.get("hiringOrganization") or {}
    amount, currency, unit = money(posting.get("baseSalary"))
    loc = place(posting.get("jobLocation") or {})
    # `identifier.name` is «Компания» on this host and its VALUE is the advert id.
    # The sitemap URL ends in the same number, so the id is attested twice; when
    # the two disagree the URL wins and the walk says so.
    idv = posting.get("identifier") or {}
    from_ld = str(idv.get("value") or "").strip() if isinstance(idv, dict) else ""
    return {
        "source": "korgar", "country": "TJ", "ledger_id": f"korgar:{ident}",
        "id": ident, "url": url,
        "id_in_jsonld": from_ld or None,
        "title": text(posting.get("title")) or None,
        # **A field PRESENT and FILLED with a constant is not a field with a
        # value.** The host's own string is kept beside the null so that this
        # drops nothing and claims nothing.
        "employer": published_employer(org)[0],
        "employer_as_published": published_employer(org)[1],
        "place": loc["locality"], "region": loc["region"], "country_code": loc["country"],
        "salary": amount, "salary_currency": currency, "salary_unit": unit,
        # constant «CONTRACTOR» on the three measured — carried, not interpreted
        "employment_type": posting.get("employmentType") or None,
        "posted": posting.get("datePosted") or None,
        "description": text(htmlmod.unescape(posting.get("description") or ""))[:20000] or None,
    }


def cmd_list(a):
    code, xml = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_PARTIAL)
    everything, section, found, rejected = adverts(xml)
    if not found:
        die(empty_first_page("korgar", xml, "advertisement", where=SITEMAP), EXIT_PARTIAL)
    counts = sitemap_count(xml)
    rows = []
    if a.with_ads:
        cap = a.max or 0
        cut = found[:cap] if cap else found
        for url, ident in cut:
            code, body = get(url)
            if code != 200:
                note(f"{url}: HTTP {code} — skipped, and counted as a gap.")
                continue
            p = postings(body)
            if not p:
                note(f"{url}: {absent_reason(body)}")
                continue
            rows.append(record(url, ident, p[0]))
        end = ("capped by --max" if cap and len(found) > cap else "walked to the end of the filter")
    else:
        rows = [{"source": "korgar", "country": "TJ", "ledger_id": f"korgar:{i}",
                 "id": i, "url": u} for u, i in found]
        end = "enumeration only — no advertisement page was fetched (pass --with-ads)"
    for r in (rows[:a.limit] if a.limit else rows):
        print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(rows))} emitted, the declared sitemap lists {th(len(found))} advertisement "
         f"URL(s) under {ADVERT_SEGMENT} — {end}.")
    note(f"the filter REMOVED {th(len(everything) - len(section))} URL(s) of {th(counts['locs'])}, "
         f"{th(len(sitemap_locs(xml, contains='/rezume/')))} of them under /rezume/: "
         f"**candidate CVs, which the rules permit and this adapter refuses**"
         + (f"; {rejected} URL(s) of the advert section carried no terminal id and were dropped as facets" if rejected else "")
         + ".")
    if counts["lastmods"] == 0:
        note("the sitemap carries ZERO `lastmod` over its "
             f"{th(counts['locs'])} entries, and a 2021 advertisement is still listed: "
             "this count is «advertisement URLs in the declared sitemap», never «live vacancies».")
    if not a.no_site_total:
        note("the site's own figure is «Более 3000», which UNDERstates the sitemap by ~2.2× — "
             "two numbers, two provenances, and the larger one is the enumerable.")


def cmd_ad(a):
    url = a.url.strip()
    refuse_candidate(url)
    if not ADVERT_RE.match(url):
        die(f"{url}: not an advertisement address — expected "
            f"{BASE}/vakanciya/<slug>_<id>. **A facet of the same section "
            f"(/vakancii/gorod/<city>) carries no terminal id and is not an advertisement.**")
    ident = ADVERT_RE.match(url).group(1)
    code, body = get(url)
    if code == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    found = postings(body)
    if not found:
        why = absent_reason(body)
        if getattr(why, "our_fault", False):
            die(f"{url}: {why} **The page announces a JobPosting and this read none.**")
        die(f"{url}: {why}", EXIT_PARTIAL)
    r = record(url, ident, found[0])
    print(json.dumps(r, ensure_ascii=False))
    if r["employer"] is None and r["employer_as_published"]:
        note(f"the employer is null: this host fills `hiringOrganization.name` with the "
             f"word {r['employer_as_published']!r} on every advertisement measured. "
             "**Nothing was withheld — there was nothing there.**")
    if r["id_in_jsonld"] and r["id_in_jsonld"] != r["id"]:
        note(f"the URL ends in {r['id']} and the JobPosting's identifier says "
             f"{r['id_in_jsonld']} — the URL wins, and the disagreement is said rather than hidden.")


def main():
    p = argparse.ArgumentParser(
        description="Korgar (Tajikistan) — the declared sitemap filtered to /vakanciya/<slug>_<id>; "
                    "the filter is a safety condition, four URLs in five of that sitemap being candidate CVs.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every advertisement URL in the declared sitemap; --with-ads also reads each page")
    s.add_argument("--limit", type=int)
    s.add_argument("--with-ads", action="store_true", help="fetch each advertisement and read its JobPosting (2 s apart)")
    s.add_argument("--max", type=int, help="with --with-ads, stop after N advertisements")
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advertisement, from the page's single JobPosting block")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
