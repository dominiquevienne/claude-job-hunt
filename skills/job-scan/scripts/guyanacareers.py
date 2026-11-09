#!/usr/bin/env python3
"""Guyana Careers (`guyana-careers.com`, Guyana) — the declared enumerator is not one, and the employer is not published.

  guyanacareers.py list [--limit N] [--today YYYY-MM-DD]
  guyanacareers.py ad --url <vacancy URL>

THE `Sitemap:` THIS HOST DECLARES CANNOT EVER BE A SITEMAP

`robots.txt` is 73 bytes: `User-agent: *`, `Allow: /`, and
`Sitemap: https://guyana-careers.com/?sitemap.xml`. `sitemaps_for()` returns
it, `ignored_for()` returns `[]` — the parser dropped nothing — and
`delay_for()` returns `None`, so the 2 s pace is ours.

**Fetched, that URL returns 200 and 196 461 bytes of the HOME PAGE**:
`<!DOCTYPE html>`, `<title>Home - Guyana Careers</title>`, zero `<urlset`,
zero `sitemapindex`. The cause is structural and the trace names it —
`final_url` came back as `?sitemap_xml`: `.` is not legal in a PHP query
parameter name and is folded to `_`, so `?sitemap.xml` is an unknown query on
`/`, which WordPress serves as its front page. **This declaration can never
resolve to a sitemap, on this host or any other PHP one.**

So a walk of the declared enumerator would read a 196 kB page, find no
address, and report a board with nothing in it — a readable body is not a
response. This adapter does not walk it, and `is_sitemap()` exists so the
next shape change is a raised exception and not an empty count.

THE REAL ENUMERATOR ANSWERS ITS OWN COUNT, IN ITS BODY

`/wp-json/wp/v2/job_listing?per_page=100` returns **46** records, all
`status: publish`, dates 2026-08-28 to 2026-10-30. Forty-six is below the
hundred asked for, so **46 is the total and it is read off the array** — which
matters, because the count WordPress states for this query lives in the
`X-WP-Total` response HEADER and `bin/fetch-body.py` records no arbitrary
response header. A witness can be perfectly valid and reachable by no route
we have; this one is reachable because it is in the body.

And it is corroborated independently: `/job-list/` carries **10 distinct**
vacancies behind **20** `/job/<slug>/` links — each one is linked twice, so an
extractor that does not deduplicate reports double — and its pager names
pages 2, 3 and 5, bounding the board at 50. 46 sits inside that bound.

THE EMPLOYER IS NOT PUBLISHED, AND BOTH SOURCES AGREE ON THE WRONG-LOOKING ANSWER

The `JobPosting` on an ad page gives `hiringOrganization.name` as
**"Guyana Careers"** — the board itself. That looks like a defect worth
routing around, and it is not: `metas._job_employer_name` carries the same
string on **46 of 46**, so the field is CONSTANT and discriminates nothing.
The board posts under its own name and the hiring employer is nowhere in what
it serves. **So `employer` is `None` and the record says why**, because
writing "Guyana Careers" on all forty-six would be specific, plausible and
false on every one of them.

NO RECRUITER CONTACT IS DEPOSITED, SO NONE IS DECLARED WITHHELD

`metas._job_apply_email` is filled on **0 of 46** and no `_job_apply_url`
carries an `@` or a `mailto:`. Applying is `external` on 46/46, to a
third-party applicant tracker — `applicant.careerstruck.com` (36),
`employertube-applicant.vercel.app` (8), `applicant.employertube.com` (2).
A `withheld_fields` naming a contact here would claim a discretion this
adapter never had to exercise; the record states the absence instead, and
names the ATS host, which is where a candidate's application actually goes.

WHAT ELSE THE POPULATION HOLDS, measured over all 46 and not over page one

  `_job_expiry_date`                46/46, `YYYY-MM-DD`, 2026-11-30 or
                                    2026-12-31 — so expiry is decidable for
                                    the whole board, and `today` is a
                                    PARAMETER of `_expired()`, never the clock
  `_job_application_deadline_date`  18/46
  `_job_location`                   43/46, a `{term_id: name}` map that holds
                                    the CITY and the COUNTRY together on 12 of
                                    them (`{'178': 'Georgetown', '153':
                                    'Guyana'}`), so it is reduced rather than
                                    joined
  `_job_type`                       43/46, same map shape
  `_job_category`                   42/46, and its names carry HTML entities
                                    (`Food &amp; Beverage`), so they are
                                    unescaped
  `_job_address` · `_job_salary`    **0/46** — no salary is published, so the
                                    digit-threshold question does not arise

Measured 2026-11-09 19:20-19:34 UTC, guard on each exact path in a turn
distinct from retrieval, one token (`claude-user`). Issue #707.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import datetime
import html as htmlmod
import json
import re
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _ldjson import absent_reason, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BASE = "https://guyana-careers.com"
REST = BASE + "/wp-json/wp/v2/job_listing"
LIST = BASE + "/job-list/"
COUNTRY = "GY"

AD_RE = re.compile(r"^https://guyana-careers\.com/job/([a-z0-9][a-z0-9-]*)/$")
AD_LINK_RE = re.compile(r"https://guyana-careers\.com/job/([a-z0-9][a-z0-9-]*)/")
PAGER_RE = re.compile(r"/job-list/page/(\d+)/")
TITLE_RE = re.compile(r"(?is)<title>(.*?)</title>")
ISO_DAY_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


class ShapeMoved(Exception):
    """200, and not the shape this adapter knows.

    A pure function must not call `sys.exit`: raising is what lets `tests/`
    tell "the shape moved" from "the board is empty".
    """


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[guyanacareers] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# `delay_for()` returns None on this host's 73-byte rules file, so 2 s is ours
_PACE = Pace("guyana-careers.com", own=2.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "application/json,text/html;q=0.9",
        "Accept-Language": "en"})
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


ENTITY_RE = re.compile(r"&(?:[a-zA-Z][a-zA-Z0-9]{1,30}|#\d{1,6}|#x[0-9a-fA-F]{1,6});")


def second_unescape(value):
    """`(value, applied)` — a SECOND pass, and only when one is still owed.

    The JSON-LD on an ad page is **doubly** escaped (`&amp;amp;` ten times on
    the one measured), so a single unescape delivers `Management &amp;
    Accounting` to a reader. The REST path is NOT: measured over all 46
    records, **0** descriptions and **0** titles carry a residual entity after
    one pass, so the second is applied here and nowhere else.

    It is conditional because a blind second pass fabricates markup —
    `&amp;lt;3` becomes `<3`, measured — and the condition is the only thing
    that keeps a sound field untouched.
    """
    if not value or not ENTITY_RE.search(value):
        return value, False
    return htmlmod.unescape(value), True


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(markup)).strip()


def is_sitemap(body):
    """Does this body actually enumerate addresses?

    The `Sitemap:` this host declares returns its FRONT PAGE with a 200, so
    "we fetched the declared enumerator" and "we have an enumerator" are two
    different facts. Nothing in a status code separates them.
    """
    return bool(re.search(r"(?i)<(?:[a-z0-9]+:)?(urlset|sitemapindex)\b", body or ""))


def _terms(value):
    """The names out of a `{term_id: name}` map, unescaped and in order.

    WordPress serves these taxonomies as a map keyed by term id, and the
    names carry HTML entities (`Food &amp; Beverage`).
    """
    if not isinstance(value, dict):
        return []
    return [htmlmod.unescape(str(v)).strip() for v in value.values() if str(v).strip()]


def location_of(value):
    """`(place, terms)` — the city when the map holds both, never a join.

    12 of the 46 carry the city AND the country (`Georgetown` + `Guyana`), so
    joining them would write "Georgetown, Guyana" where the board means one
    place, and 10 carry `Guyana` alone, which is the country and not a place.
    """
    terms = _terms(value)
    if not terms:
        return None, []
    narrow = [t for t in terms if t.lower() != "guyana"]
    return (narrow[0] if narrow else None), terms


def _expired(iso, today):
    """`None` when the date is unreadable or `today` was not supplied.

    `today` is a PARAMETER: asserting expiry against the real clock is a
    dated literal in a test, and an unreadable deadline must read as unknown
    rather than as current.
    """
    m = ISO_DAY_RE.match(str(iso or "").strip())
    if not m or today is None:
        return None
    return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))) < today


def ads_on(markup):
    """The DISTINCT slugs of `/job-list/`, in the order the page links them.

    Every vacancy is linked twice on this page — 20 links for 10 vacancies —
    so an extractor that does not deduplicate reports the board at double its
    size, with a figure that is plausible and only wrong.
    """
    seen, out = set(), []
    for slug in AD_LINK_RE.findall(markup or ""):
        if slug not in seen:
            seen.add(slug)
            out.append(slug)
    return out


def pager_max(markup):
    """The highest page the pager NAMES — a bound, never a count.

    It names 2, 3 and 5 and omits 4, so this is an upper bound on the number
    of pages and nothing is inferred about how full the last one is.
    """
    pages = [int(n) for n in PAGER_RE.findall(markup or "")]
    return max(pages) if pages else None


def records(payload, today=None):
    """`[record]` from the REST list — **no network at all.**

    Raises rather than returning nothing when the payload is not the list of
    posts this adapter knows: an empty list and a moved shape read the same
    downstream.
    """
    if not isinstance(payload, list):
        raise ShapeMoved(f"{REST}: the payload is a {type(payload).__name__}, "
                         f"not the list of posts")
    out = []
    for e in payload:
        if not isinstance(e, dict) or "slug" not in e or "title" not in e:
            raise ShapeMoved(f"{REST}: an entry without `slug` and `title`")
        metas = e.get("metas") or {}
        slug = str(e.get("slug"))
        place, terms = location_of(metas.get("_job_location"))
        title = e.get("title")
        if isinstance(title, dict):
            title = title.get("rendered")
        body = e.get("content")
        if isinstance(body, dict):
            body = body.get("rendered")
        expiry = str(metas.get("_job_expiry_date") or "").strip() or None
        apply_url = str(metas.get("_job_apply_url") or "").strip() or None
        out.append({
            "source": "guyanacareers", "country": COUNTRY,
            "ledger_id": f"guyanacareers:{slug}", "id": slug,
            "url": e.get("link") or f"{BASE}/job/{slug}/",
            "title": text(title or "") or None,
            "language": "en",
            # the board posts under its own name on 46/46, so the hiring
            # employer is simply not in what it serves -- see `employer_note`
            "employer": None,
            "employer_note": "not published: the board carries its own name in "
                             "`_job_employer_name` and in the page's "
                             "`hiringOrganization` on every record measured",
            "place": place,
            "place_terms": terms,
            "employment_type": (_terms(metas.get("_job_type")) or [None])[0],
            "categories": _terms(metas.get("_job_category")),
            "posted": e.get("date"),
            "expires": expiry,
            "expired": _expired(expiry, today),
            "deadline": str(metas.get("_job_application_deadline_date") or "").strip() or None,
            "description": text(body or "")[:20000] or None,
            "apply_url": apply_url,
            "apply_host": (urllib.parse.urlsplit(apply_url).netloc or None) if apply_url else None,
            # 0 of 46 deposit an apply e-mail and none of the apply URLs carries
            # an `@`: there is nothing to withhold, and saying otherwise would
            # claim a discretion this adapter never exercised
            "contact": None,
            "withheld_fields": [],
        })
    return out


def parse_ad(url, body):
    """`(record, notes)` from one served ad page — **no network at all.**"""
    m = AD_RE.match(url)
    if not m:
        raise ShapeMoved(f"{url}: not {BASE}/job/<slug>/")
    slug = m.group(1)
    t = TITLE_RE.search(body)
    titre = text(t.group(1)) if t else None
    if titre:
        # the site appends « - Guyana Careers » to every title
        titre = re.sub(r"\s*-\s*Guyana Careers\s*$", "", titre)
    out = {
        "source": "guyanacareers", "country": COUNTRY,
        "ledger_id": f"guyanacareers:{slug}", "id": slug, "url": url,
        "title": titre, "language": "en",
        "employer": None,
        "employer_note": "not published: `hiringOrganization` names the board",
        "contact": None, "withheld_fields": [],
    }
    notes = []
    found = postings(body)
    if not found:
        why = absent_reason(body)
        if getattr(why, "our_fault", False):
            raise ShapeMoved(f"{url}: {why} **The page announces a JobPosting "
                             f"and this read none.**")
        notes.append(f"an ad page with NO JobPosting: {why}. The one measured on "
                     f"2026-11-09 carried a full one, so this is a change in the "
                     f"board and not an empty vacancy.")
        return out, notes
    d = found[0]
    loc = d.get("jobLocation")
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc or {}).get("address") if isinstance(loc, dict) else None
    # the address is a plain STRING here (`Berbice`), not the dict a reader
    # written against a sibling board would expect
    if isinstance(addr, dict):
        place = text(addr.get("addressLocality") or addr.get("addressRegion") or "")
    else:
        place = text(str(addr or ""))
    org = d.get("hiringOrganization") or {}
    org_name = org.get("name") if isinstance(org, dict) else None
    et = d.get("employmentType")
    out["title"] = text(d.get("title") or "") or titre
    desc, twice = second_unescape(text(str(d.get("description") or "")))
    out["title"] = second_unescape(out["title"] or "")[0] or None
    out.update({
        "place": place or None,
        "posted": d.get("datePosted"),
        "valid_through": d.get("validThrough"),
        "employment_type": ", ".join(et) if isinstance(et, list) else et,
        "direct_apply": d.get("directApply"),
        "description": desc[:20000] or None,
        "board_name_as_employer": org_name,
    })
    if twice:
        notes.append("the JSON-LD description was doubly escaped and a second "
                     "unescape was applied; the REST path needs none, measured "
                     "over all 46 records.")
    if org_name:
        notes.append(f"`hiringOrganization` is {org_name!r}, which is the board; "
                     f"`employer` stays None because `_job_employer_name` holds "
                     f"the same constant on every record measured.")
    return out, notes


def cmd_list(a):
    today = None
    if a.today:
        today = datetime.date.fromisoformat(a.today)
    code, body = get(f"{REST}?per_page=100")
    if code == 404:
        die(f"{REST}: 404 — the post type is no longer exposed", EXIT_GONE)
    if code != 200 or not body:
        die(f"{REST}: HTTP {code}", EXIT_BROKEN)
    try:
        payload = json.loads(body)
    except ValueError as e:
        die(f"{REST}: the body is not JSON: {e}")
    try:
        rows = records(payload, today)
    except ShapeMoved as e:
        die(str(e))
    asked = 100
    if len(rows) >= asked:
        note(f"{len(rows)} records for per_page={asked}: the page is FULL, so this "
             f"is a page and not the board. The count WordPress states lives in "
             f"`X-WP-Total`, which `bin/fetch-body.py` does not record.")
    # the cross-witness: the list page bounds the board independently
    lcode, lbody = get(LIST)
    bound = None
    if lcode == 200 and lbody:
        per, pages = len(ads_on(lbody)), pager_max(lbody)
        if per and pages:
            bound = per * pages
            note(f"cross-witness: /job-list/ links {per} DISTINCT vacancies and its "
                 f"pager names up to page {pages}, so the board is at most {bound}.")
            if len(rows) > bound:
                note(f"**{len(rows)} records against a bound of {bound}** — the two "
                     f"enumerators disagree and neither is corroborated.")
    else:
        note(f"{LIST}: HTTP {lcode} — no cross-witness this run, so the count below "
             f"is this adapter's own extraction with nothing against it.")
    if a.limit:
        rows = rows[:a.limit]
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{len(rows)} record(s) emitted from the REST list"
         + (f", bound {bound} from the pager" if bound else "")
         + ". The `Sitemap:` this host declares returns its front page with a 200 "
           "and is not walked; the employer is not published on any record, and no "
           "recruiter contact is deposited on any of them.")


def cmd_ad(a):
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: 404 — the vacancy is gone", EXIT_GONE)
    if code != 200 or not body:
        die(f"{a.url}: HTTP {code}", EXIT_BROKEN)
    try:
        rec, notes = parse_ad(a.url, body)
    except ShapeMoved as e:
        die(str(e))
    for n in notes:
        note(n)
    print(json.dumps(rec, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description="Guyana Careers — the REST list, which answers its own count, "
                    "and one vacancy.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="the whole board from the REST post type, with "
                                    "the list page's pager as a cross-witness")
    s.add_argument("--limit", type=int)
    s.add_argument("--today", help="YYYY-MM-DD; decides `expired` instead of the clock")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one vacancy from its served page")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
