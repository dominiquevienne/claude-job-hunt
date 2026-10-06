#!/usr/bin/env python3
"""Yora / Vazifa (`yora.tj`, `vazifa.tj`) — one board under two names, whose declared sitemap over-counts FOUR-FOLD by locale and whose date field dates nothing at all.

  yora.py list [--limit N] [--with-ads --max N] [--no-sitemap-note]
  yora.py ad --url <advertisement URL>

THE SITEMAP IS THE ENUMERATOR AND ITS COUNT IS A TRAP

`/sitemap.xml` is 66 970 bytes and carries **416 `<loc>`, all 416 distinct**
(2026-10-06 12:26 UTC) — and that is exactly why the figure is dangerous:

    416 <loc>      ALL DISTINCT as strings
    4 locales      /en /uz /ru /tj, 104 paths each, IDENTICAL path sets
    400 of them    /<locale>/vacancies/<id>
    100            DISTINCT ids — the multiplier is 4.00x, measured
    16             static pages: root, /vacancies, /privacy-policy,
                   /delete-account, once per locale

**«All the URLs are distinct» says nothing about the number of OBJECTS.** A naive
count publishes 416 or 400 for a board of 100. *This is the dedup trap of
`jobs.sicpa.com` with a locale multiplier instead of a duplicated link, and the
remedy is the same: collapse before counting — here on the numeric id, which is
the only part of the URL the four locales share.*

**AND 100 IS A ROUND NUMBER.** That smells of a cap on the sitemap rather than a
board total, and it is NOT established either way, so this adapter emits «distinct
advertisements in the declared sitemap» and never «the size of the board».

`lastmod` DATES NOTHING — 416 OF 416, NOT «MOST OF THEM». All 416 rows carry a
timestamp inside the SECOND of our own request: six distinct values spanning three
milliseconds (`2026-10-06T12:26:46.838Z` ×111, `.839Z` ×116, `.840Z` ×96).
*Measured 400 of 416 the day before and 416 of 416 today, so the field is
generated at render for every row.* **So `list` ignores it and SAYS it ignores it;
the date a record carries is the `JobPosting`'s `datePosted`, which is real and
spread (2026-07-06, 2026-10-01, 2026-10-06 on the three read).**

WHAT AN ADVERTISEMENT CARRIES, ON THREE — the smallest, the median and the
largest of the 100 ids, each URL taken FROM the sitemap and never composed. All
three serve **three** `application/ld+json` blocks of which exactly one is a
`JobPosting`, and all three carry the SAME eight keys:

    title · description · datePosted · directApply · hiringOrganization ·
    jobLocation · @context · @type

**There is NO `baseSalary`, NO `employmentType` and NO `validThrough` on any of
them** — so this adapter does not emit those fields at all rather than emit nulls
that invite filling. *`korgar.md`, same country and same week, DOES carry a
`baseSalary`: a shared standard does not predict which of its fields a host
fills.*

`hiringOrganization.name` IS A REAL EMPLOYER and not a placeholder — «КОИНОТИ
НАВ», «ЗАО "Шивер Таджикистан"» — **but the same name on two of the three**, so
one employer posts several advertisements and an employer count is not an
advertisement count.

TWO EXPURGATION REMEDIES, AND READING THREE INSTEAD OF ONE IS WHAT FOUND THE
SECOND.

    description      an e-mail on 3 of 3, a messaging app on 2 of 3, `+992` on
                     1 of 3, an anchored nine-digit run on 0 of 3
                     -> the ONLY prose field, and it is SCRUBBED
    jobLocation      `address.streetAddress` on 2 of 3
                     -> DROPPED: the record carries `addressLocality` only

**The card this adapter was written from named neither.** It had read ONE
advertisement — whose address happened to carry no street and whose description
held one e-mail — and it reported «1 and 1». *A card names what it looked for; the
class is measured.* **And no single pattern covers: the anchored nine-digit run
touches 0 of 3 here while `+992` touches 1 of 3, so the scrubber needs all four.**

ONE BOARD, TWO NAMES. `vazifa.tj` serves a rules file byte-identical to
`yora.tj`'s and declares the SAME sitemap host, so the two are one board; this
adapter uses `yora.tj` and says so. *Nothing else on `vazifa.tj` has been read.*

THE RULES: 473 bytes refusing four AI crawlers outright — `GPTBot`, `Claude-Web`,
`Bytespider`, `cohere-ai`, each `Disallow: /` — and giving `*` an `Allow: /` plus
`Allow: /api/avatar` plus **`Disallow: /api`**. `Claude-User` is not named, so we
fall under `*` and `identity()` answers `claude-user` / http. **`/api` is refused
in writing, so borne 1 would close this board to EVERY route including a browser
had the advertisements needed it — and they do not, being server-rendered.**
`refuse_api()` is a refusal that can FIRE and is exercised both ways: `/api`,
`/api/jobs` and `/api/v1/vacancies` return False by the rule `/api`, while
`/api/avatar` returns True by its own `Allow` — a whitelist inside a blacklist.
No `Crawl-delay`, so our own 2 s floor applies. Guard taken on every exact path in
turns distinct from the retrievals. Measured 2026-10-06 (#665).
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

HOST = "yora.tj"
BASE = "https://yora.tj"
SITEMAP = BASE + "/sitemap.xml"
TWIN = "vazifa.tj"          # same rules file to the byte, same declared sitemap

# The four locales carry IDENTICAL path sets. We read one and say which.
LOCALES = ("en", "uz", "ru", "tj")
READ_LOCALE = "en"

# The id is the only part of the URL the four locales share, so it is the dedup key.
ADVERT_RE = re.compile(r"^https://yora\.tj/(" + "|".join(LOCALES) + r")/vacancies/(\d+)$")

# Refused in writing to `*`, and never needed: the advertisements are server-rendered.
API_PREFIX = "/api"
API_ALLOWED = "/api/avatar"

# Dropped from the address: a street is not a locality.
ADDRESS_DROPPED = ("streetAddress", "postalCode")

# The only prose field, and it carries contacts on every advertisement measured.
MAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TEL_RE = re.compile(r"(?:\+\s?992[\s\-()]*)?(?<!\d)\d{9}(?!\d)|\+\s?992[\s\-()\d]{4,}")
MSG_RE = re.compile(r"(?i)\b(?:whats?app|telegram|viber|imo)\b[\s:：]*[+\d@][\w\d\s\-()@._]{3,}")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[yora] {msg}", file=sys.stderr)


def refuse_api(url):
    """The host refuses `/api` IN WRITING, so borne 1 closes it to every route.
    This is a refusal that can FIRE rather than a path we merely never build —
    and `/api/avatar` is allowed by its own rule, a whitelist inside a
    blacklist."""
    path = urllib.parse.urlsplit(url).path or "/"
    if path.startswith(API_ALLOWED):
        return None
    if path == API_PREFIX or path.startswith(API_PREFIX + "/"):
        die(f"{url}: `Disallow: /api` is written for `*`. **A refusal in the rules is an "
            f"intention and no route contours it — not HTTP, not a browser.** The "
            f"advertisements are server-rendered and this path is never needed.", EXIT_REFUSED)
    return None


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # the host writes no Crawl-delay — our own floor


def get(url):
    refuse_api(url)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xml;q=0.9",
        "Accept-Language": "en,ru;q=0.8,tg;q=0.5"})
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
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</li>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return "\n".join(" ".join(l.split()) for l in
                     htmlmod.unescape(markup).splitlines() if l.strip()).strip()


def scrub(s):
    """The description with its contacts replaced. **No single pattern covers**:
    the anchored nine-digit run touched 0 of 3 while `+992` touched 1 of 3 and a
    messaging handle 2 of 3, so all four run."""
    if not isinstance(s, str) or not s.strip():
        return None, []
    found = []
    if MAIL_RE.search(s):
        found.append("description:e-mail")
    if MSG_RE.search(s):
        found.append("description:messaging")
    if TEL_RE.search(s):
        found.append("description:telephone")
    s = MAIL_RE.sub("[e-mail withheld]", s)
    s = MSG_RE.sub("[messaging contact withheld]", s)
    s = TEL_RE.sub("[telephone withheld]", s)
    return (text(s) or None), found


def place(job_location):
    """`addressLocality` and nothing else. A POSITIVE floor: `streetAddress` arrives
    on 2 of the 3 advertisements measured and `postalCode` could arrive tomorrow,
    and neither is named here to be excluded — nothing is read but the locality."""
    loc = job_location if isinstance(job_location, dict) else {}
    addr = loc.get("address")
    addr = addr if isinstance(addr, dict) else {}
    v = addr.get("addressLocality")
    return v.strip() or None if isinstance(v, str) else None


def th(n):
    return f"{n:,}".replace(",", " ")


def adverts(xml):
    """`(all_locs, per_locale, {id: url})` — the dedup is the point, so the
    caller gets the three numbers and can print the multiplier rather than
    assert it."""
    every = sitemap_locs(xml)
    per = {}
    by_id = {}
    for u in every:
        m = ADVERT_RE.match(u.strip())
        if not m:
            continue
        loc, ident = m.group(1), m.group(2)
        per[loc] = per.get(loc, 0) + 1
        # THE DEDUP. Removing this condition emits 400 records for 100 adverts,
        # and every count printed downstream is then four times the truth.
        if ident not in by_id or loc == READ_LOCALE:
            by_id[ident] = u.strip()
    return every, per, by_id


def record(url, ident, posting):
    org = posting.get("hiringOrganization") or {}
    desc, withheld = scrub(posting.get("description"))
    out = {
        "source": "yora", "country": "TJ", "ledger_id": f"yora:{ident}",
        "id": ident, "url": url, "locale_read": READ_LOCALE,
        "title": text(posting.get("title")) or None,
        # a real name, and the SAME on two of the three read: an employer count
        # is not an advertisement count
        "employer": (org.get("name") or "").strip() or None if isinstance(org, dict) else None,
        # `addressLocality` only — `streetAddress` arrives on 2 of 3 and is dropped
        "place": place(posting.get("jobLocation")),
        "direct_apply": posting.get("directApply"),
        # the JobPosting's own date, which is REAL — never the sitemap's `lastmod`
        "posted": posting.get("datePosted") or None,
        "description": desc,
    }
    if withheld:
        out["withheld_fields"] = sorted(set(withheld))
    return out


def cmd_list(a):
    code, xml = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_PARTIAL)
    every, per, by_id = adverts(xml)
    if not by_id:
        die(empty_first_page("yora", xml, "advertisement", where=SITEMAP), EXIT_PARTIAL)
    counts = sitemap_count(xml)
    ids = sorted(by_id, key=int)
    rows, gaps = [], 0
    if a.with_ads:
        cut = ids[:a.max] if a.max else ids
        for ident in cut:
            url = by_id[ident]
            code, body = get(url)
            if code != 200:
                note(f"{url}: HTTP {code} — skipped and counted as a gap.")
                gaps += 1
                continue
            p = postings(body)
            if not p:
                note(f"{url}: {absent_reason(body)}")
                gaps += 1
                continue
            rows.append(record(url, ident, p[0]))
        end = f"capped by --max at {len(cut)} of {len(ids)}" if a.max and len(ids) > a.max \
              else "every advertisement the sitemap declares"
    else:
        rows = [{"source": "yora", "country": "TJ", "ledger_id": f"yora:{i}",
                 "id": i, "url": by_id[i], "locale_read": READ_LOCALE} for i in ids]
        end = "enumeration only — no advertisement page fetched (pass --with-ads)"
    for r in (rows[:a.limit] if a.limit else rows):
        print(json.dumps(r, ensure_ascii=False))
    mult = (sum(per.values()) / len(by_id)) if by_id else 0
    note(f"{th(len(rows))} emitted; the sitemap carries {th(counts['locs'])} `<loc>`, "
         f"{th(sum(per.values()))} of them `/<locale>/vacancies/<id>` over {len(per)} locale(s) "
         f"{sorted(per)}, for **{th(len(by_id))} DISTINCT ids** — a {mult:.2f}x over-count by "
         f"LANGUAGE. *All 416 are distinct AS STRINGS, which says nothing about the number of "
         f"objects.* {end}.")
    note(f"{th(len(by_id))} is published as «distinct advertisements in the declared sitemap» and "
         "never as the size of the board: it is a ROUND number, which smells of a cap on the "
         "sitemap, and that is not established either way.")
    if counts["lastmods"]:
        note(f"the sitemap's {th(counts['lastmods'])} `lastmod` are IGNORED and this says so: "
             "every row carries a timestamp inside the second of our own request (416 of 416, six "
             "values over three milliseconds when measured). **The date a record carries is the "
             "JobPosting's `datePosted`.**")
    if gaps:
        note(f"{gaps} advertisement(s) could not be read and are counted as gaps, not as absent.")
    if not a.no_sitemap_note:
        note(f"one board under two names: `{TWIN}` serves a rules file byte-identical to this "
             f"host's and declares the same sitemap; this walk used `{HOST}` and read the "
             f"`/{READ_LOCALE}/` locale. The other three were compared by PATH SET, never by "
             "content.")


def cmd_ad(a):
    url = a.url.strip()
    refuse_api(url)
    m = ADVERT_RE.match(url)
    if not m:
        die(f"{url}: not an advertisement address — expected "
            f"https://yora.tj/<{'|'.join(LOCALES)}>/vacancies/<id>")
    ident = m.group(2)
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
    if not r.get("withheld_fields"):
        note("no contact was found in the description of this advertisement, so the record names "
             "none. **An e-mail was present on 3 of the 3 measured, so an absence here is this "
             "advertisement's and not the board's.**")


def main():
    p = argparse.ArgumentParser(
        description="Yora / Vazifa (Tajikistan) — the declared sitemap deduplicated on the "
                    "advert id, because four locales carry identical path sets and 416 distinct "
                    "URLs are 100 objects.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every advertisement the sitemap declares, deduplicated by id")
    s.add_argument("--limit", type=int)
    s.add_argument("--with-ads", action="store_true", help="fetch each advertisement (2 s apart)")
    s.add_argument("--max", type=int, help="with --with-ads, stop after N advertisements")
    s.add_argument("--no-sitemap-note", action="store_true")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advertisement, from the page's single JobPosting block")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
