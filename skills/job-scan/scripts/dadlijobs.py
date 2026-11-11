#!/usr/bin/env python3
"""Dadli Jobs (`dadlijobs.com`, Antigua and Barbuda) — the only enumerator a plain
client can see is the sitemap, and the board never states a count.

  dadlijobs.py list [--limit N] [--hydrate N] [--today YYYY-MM-DD]
  dadlijobs.py ad --url <vacancy URL>

THE LIST ROUTE IS INVISIBLE TO A PLAIN CLIENT, AND THE SITEMAP IS NOT

`robots.txt` is 366 bytes: one `*` group whose six `Disallow` lines are all
WooCommerce (`/wp-content/uploads/wc-logs/`, `/*?add-to-cart=`, `/wp-admin/`),
one `Allow: /wp-admin/admin-ajax.php`, and two `Sitemap:` lines.
`group_for()` returns that group, `sitemaps_for()` returns both declarations,
`ignored_for()` returns `[]` — the parser dropped nothing — and `delay_for()`
returns `None`, so the 2 s pace below is ours and not the host's.

The theme is JobSearch/Careerfy. Its list pages SERVE one page and no pager:
`/` says «Displayed Here: 1 – 25 Jobs» and links 27 vacancies,
`/jobs-listing/` says «Displayed Here: 1 - 15 Jobs» and links 15 behind
**31** `/job/<slug>/` hrefs — each vacancy is linked about twice, so an
extractor that does not deduplicate reports double. Both strings are page
RANGES and neither is a total. Pagination runs through
`jobsearch_job_pagenation_ajax` on `admin-ajax.php`, so **a plain client sees
page one and nothing tells it there is more**.

`/sitemap.xml` is a real `sitemapindex` (All in One SEO) naming six children,
of which `job-sitemap.xml` is the vacancies and `jobtype-`, `skill-`,
`sector-` and `product_cat-` are FACET archives — a path prefix reads like a
nature and is not one. The job sitemap carried **100** distinct
`/job/<slug>/` addresses when this was written.

A HUNDRED IS A ROUND NUMBER, SO IT WAS EPROUVED AND NOT BELIEVED

AIOSEO paginates a child sitemap as `job-sitemap1.xml`, `job-sitemap2.xml`…
and lists each page in the index; the index listed ONE child for jobs.
Fetched, `job-sitemap1.xml` returns 200 with `final_url`
`https://dadlijobs.com/job-sitemap.xml` — the paginated form REDIRECTS to the
canonical one, which is what that generator does when the type fits in a
single page. The two bodies carry **the same 100 addresses**, difference empty
in both directions, and their `md5` differ only by the generation timestamp
the file states in its own comment. So 100 is the sitemap's whole population
and not a truncation of it.

It is still not a count the board states. **The board states no total
anywhere**, and `is_urlset()` exists so that the next shape change raises
instead of reporting an empty board.

AND THERE IS NO REST WITNESS, ESTABLISHED BY ASKING WORDPRESS WHAT IT EXPOSES

`/wp-json/wp/v2/types` lists fifteen types — `post`, `page`, `product`,
Elementor's, the block-editor's — and **the job type is not among them**.
That is measured by reading what the host publishes about itself, not by
probing a path and reading a 404 as an absence.

THE EMPLOYER IS PUBLISHED HERE, AND IT VARIES

Measured over ten ads spread across the sitemap by rank (0, 11, 22 … 99, not
the first ten — the first by date are one genre): the employer is filled on
**10 of 10** with **7 distinct** values — `One Stop Employment Centre (OSEC)`
four times, then six private employers. So it discriminates, and it is read.

It is read from INSIDE `<figure class="jobsearch-jobdetail-list">` and never
from the page, because a `/employer/<slug>/` href also appears in the related
-jobs rail: one sampled ad carries two distinct employer slugs page-wide and
exactly one inside the figure.

ONE ESCAPE PASS, AND A SECOND WOULD FABRICATE

Employer names carry entities — `Fries Guys &#038; The Side Cafe`,
`Roddy&#8217;s Barbuda`. Measured over the ten: **zero** occurrences of the
doubled form `&amp;<entity>;`, and **zero** residual entities across twenty
emitted fields after a single `html.unescape`. So this adapter unescapes once.
A second pass here has nothing to consume and could only turn an escaped
`&amp;lt;3` into markup — the opposite of the Guyana Careers path measured
2026-11-09, where the doubling was real. The conduct does not transport.

THE CONTACT IS DEPOSITED ON SOME ADS AND ON OTHERS NOTHING IS, SO THE
DECLARATION IS DERIVED FROM WHAT WAS TAKEN

The split is exact on 10 of 10, and both halves are structural:

  * a `mailto:` apply button whose `data-id` EQUALS the Job ID, and the same
    address written in the description («To Apply: …», «submit applications
    via email to: …») — 6 of 10, six distinct recruiter addresses;
  * no button, an `N Application(s)` counter in the detail block, and no
    recruiter EMAIL anywhere in the ad — 4 of 10, the OSEC notices.

That split is about the APPLY ROUTE and not about whether a contact is
deposited, which a first pass of this measurement got wrong: the OSEC notices
publish OSEC's own jobseeker lines in their prose (« please contact:
462-9472 | 562-1795 »), seven local digits with no 268 prefix, and a phone
pattern anchored on 268 cannot see them. **All ten sampled ads deposit at
least one contact form**, so `withheld_fields` is non-empty on 10 of 10 —
three distinct values: `[contact_email]`, `[contact_phone]`, and both.

So `withheld_fields` names `contact_email` or `contact_phone` **only when
`redact()` actually removed one**, and it stays empty on the ads that deposit
nothing: naming a contact there would claim a discretion never exercised.
That last branch is DEAD on the corpus measured — see below.

And `contacts_withheld` is DERIVED from that same witness through `_withheld`,
which classifies `contact_email` and `contact_phone` as things that reach a
person: it is absent rather than false when nothing was taken. Since the
witness is non-empty on 10 of 10, the declaration is True on 10 of 10 and it is
its FALSE branch that is dead on this corpus — the mirror of `jobsdz`, whose
redaction is silent on all three of its ads.

The board's own address and phone — `dadlidirectory@gmail.com` and
`268-773-6837`, constant on 10 of 10 — live in the page FOOTER and in neither
the figure nor the description, so scoping the redaction to the ad's own
blocks keeps them out without any list of constants to maintain.

TWO THINGS THE CORPUS DOES NOT EXERCISE, DECLARED RATHER THAN FOUND LATER

`expired` is **False on 10 of 10**, so it is CONSTANT on this sample and
discriminates nothing today: every address the sitemap carries has an `Apply
Before` at or after the day it was read, which suggests the generator drops
closed vacancies — suggested by ten, established by none, so the field stays
and reports what it read.

And **none of this adapter's five note branches fires on any of the ten**: the
employer-outside-the-figure note, the residual-entity note, the
`data-id`/Job ID mismatch note, the no-apply-route note and the
nothing-withheld note are all reachable from a fixture and silent on the
corpus. They are kept because each turns a future shape change into a sentence
instead of a plausible field, and `tests/` is the only place they are
exercised: a mutation of one reddens on a fixture and would have changed
nothing in the world as it stood on 2026-11-10.

Two of the six mutations below come back GREEN and each one teaches something
the colour alone would not. `strip_style` made the identity creates a
measurable difference and reddens NOTHING: what keeps the stylesheet out of
the description locator is the TIGHT `<div class="..."` form, which the CSS
cannot contain, and not the strip -- measured, a bare substring lands at
215 829 inside `<style>` while the real div is at 671 315. It is kept as a
belt for the day a pattern loosens, and declared non-load-bearing rather than
claimed as a guard. And reading the employer page-wide instead of from inside
the figure is an EQUIVALENT mutant ON THE CORPUS -- the figure's slug sits at
offset 17 184 and the rail's at 27 983, so a page-wide search is right BY
LUCK -- so the guard is exercised on an adversarial fixture that puts the rail
first, where it reddens. Green on the corpus, red on the fixture: declared.

Dénominateur 10, one day: these are forms observed, not frequencies, and the
counts above are a DATED specimen. What does not depend on the sample is the
shape: the balanced-`div` description reader, the figure anchor, and the
`data-id == Job ID` cross-control.

WHAT THE ADAPTER DOES NOT TAKE

The Google-Maps href in the location line carries latitude and longitude to
thirteen decimals. The place NAME is what serves a candidate; the
coordinates add nothing and are exactly the class of field whose arrival
reopens an expurgation question, so they are read and dropped, and
`location_precision` says so.
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
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA
from _withheld import withheld_a_contact

BASE = "https://dadlijobs.com"
INDEX = BASE + "/sitemap.xml"
JOBMAP = BASE + "/job-sitemap.xml"
COUNTRY = "AG"

AD_RE = re.compile(r"^https://dadlijobs\.com/job/([a-z0-9][a-z0-9._-]*)/$")
LOC_RE = re.compile(r"(?is)<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>")
MOD_RE = re.compile(r"(?is)<lastmod>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</lastmod>")
URLSET_RE = re.compile(r"(?i)<(?:[a-z0-9]+:)?urlset\b")
INDEX_RE = re.compile(r"(?i)<(?:[a-z0-9]+:)?sitemapindex\b")
STYLE_RE = re.compile(r"(?is)<(script|style)\b[^>]*>.*?</\1>")
DIV_RE = re.compile(r"(?i)<div\b|</div\s*>")
ENTITY_RE = re.compile(r"&(?:[a-zA-Z][a-zA-Z0-9]{1,30}|#\d{1,6}|#x[0-9a-fA-F]{1,6});")

FIGURE_RE = re.compile(
    r'(?is)<figure class="jobsearch-jobdetail-list">(.*?)</figure>')
TITLE_RE = re.compile(r'(?is)<h1[^>]*class="[^"]*job-title[^"]*"[^>]*>(.*?)</h1>')
EMPLOYER_RE = re.compile(
    r'(?is)<a href="https://dadlijobs\.com/employer/([a-z0-9._-]+)/"[^>]*>\s*@?([^<]+)</a>')
TYPE_RE = re.compile(
    r'(?is)<a href="[^"]*"[^>]*class="jobsearch-jobdetail-type"[^>]*>(.*?)</a>')
SECTOR_RE = re.compile(
    r'(?is)<small class="post-in-category">\s*in\s*<a[^>]*>(.*?)</a>')
PLACE_RE = re.compile(
    r'(?is)<li>\s*<i class="jobsearch-icon jobsearch-maps-and-flags"></i>(.*?)</li>')
COORD_RE = re.compile(r"maps/search/([0-9.+\-]+)%2C([0-9.+\-]+)")
DATE_LI_RE = re.compile(r"(?is)<li>.*?</i>\s*([A-Za-z ]+?)\s*:\s*(.*?)</li>")
APPS_RE = re.compile(r"(\d+)\s*Application\(s\)")
JOBID_RE = re.compile(r"(?is)Job ID\s*<small>\s*(\d+)\s*</small>")
APPLY_RE = re.compile(
    r'(?is)<a href="(mailto:[^"]+)"[^>]*data-id="(\d+)"[^>]*class="(jobsearch-applyjob[^"]*)"')
DESC_OPEN_RE = re.compile(r'(?i)<div class="jobsearch-description"')

MAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TEL_RE = re.compile(
    r"(?<!\d)(?:\+?1[\s.\-]?)?\(?268\)?[\s.\-]?\d{3}[\s.\-]?\d{4}(?!\d)"
    r"|(?<!\d)\d{3}[\s.\-]\d{4}(?!\d)")

MONTHS = {m: i for i, m in enumerate(
    ("january february march april may june july august september october "
     "november december").split(), 1)}

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
    print(f"[dadlijobs] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# `delay_for()` returns None on this host's 366-byte rules file, so 2 s is ours
_PACE = Pace("dadlijobs.com", own=2.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "application/xml,text/html;q=0.9",
        "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0], r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


# ---------------------------------------------------------------- pure readers

def is_urlset(body):
    """A readable body is not a response: this says it is an address list."""
    return bool(URLSET_RE.search(body or ""))


def is_sitemap_index(body):
    return bool(INDEX_RE.search(body or ""))


def locs(body):
    """(address, lastmod) pairs, CDATA-aware.

    Every `<loc>` this host serves is wrapped in `<![CDATA[...]]>`, so the
    usual `<loc>([^<]+)</loc>` returns ZERO on a sitemap that carries a
    hundred addresses -- a false zero that reads as an empty board.
    """
    urls = [u.strip() for u in LOC_RE.findall(body or "")]
    mods = [m.strip() for m in MOD_RE.findall(body or "")]
    mods += [None] * (len(urls) - len(mods))
    return list(zip(urls, mods[:len(urls)]))


def job_sitemap_of(index_body):
    """The vacancies child of the index, by NAME and never by position."""
    if not is_sitemap_index(index_body):
        raise ShapeMoved("/sitemap.xml is no longer a <sitemapindex>")
    for u, _ in locs(index_body):
        if u.rstrip("/").endswith("/job-sitemap.xml"):
            return u
    raise ShapeMoved(
        "the sitemap index no longer names job-sitemap.xml; it names "
        + ", ".join(u.rsplit("/", 1)[-1] for u, _ in locs(index_body)))


def ads_of(pairs):
    """Addresses that are vacancies, deduplicated, order preserved."""
    seen, out = set(), []
    for u, mod in pairs:
        m = AD_RE.match(u)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            out.append((u, m.group(1), mod))
    return out


def strip_style(markup):
    """Drop `<script>`/`<style>` BEFORE locating anything.

    This page's inline CSS names `.jobsearch-description` and
    `.jobsearch-jobdetail-services`, so a search run on the raw markup finds
    the STYLESHEET first and reports the block as absent.
    """
    return STYLE_RE.sub(" ", markup or "")


def div_block(markup, start):
    """The `<div>` opened at `start`, closed by BALANCING.

    A non-greedy `(.*?)</div>` stops at the first nested close and truncates
    the description -- measured: 317 characters where the block holds 1 282,
    and the recruiter address that lives past the cut then reads as absent.
    """
    depth = 0
    for m in DIV_RE.finditer(markup, start):
        depth += 1 if m.group(0)[1:2] != "/" else -1
        if depth == 0:
            return markup[start:m.end()]
    raise ShapeMoved("a <div> opened and never closed")


def text_of(markup):
    return re.sub(r"\s+", " ", htmlmod.unescape(
        re.sub(r"<[^>]+>", " ", markup or ""))).strip()


def unescape_once(value):
    """One pass, measured sufficient; a second would fabricate markup."""
    return htmlmod.unescape(value) if value else value


def residual_entities(value):
    """For the adapter to SAY when a field still carries an entity."""
    return bool(value) and bool(ENTITY_RE.search(value))


def redact(value):
    """Return (text without contacts, the field names actually REMOVED).

    The declaration is derived from what this took, never from what the ad
    happens to contain: an ad that deposits nothing gets an empty list.
    """
    if not value:
        return value, []
    took = []
    out, n = MAIL_RE.subn("[e-mail withheld]", value)
    if n:
        took.append("contact_email")
    out, n = TEL_RE.subn("[phone withheld]", out)
    if n:
        took.append("contact_phone")
    return out, took


def parse_date(value):
    """«November 12, 2026» -> «2026-11-12», without a locale."""
    m = re.search(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", value or "")
    if not m:
        return None
    mon = MONTHS.get(m.group(1).lower())
    if not mon:
        return None
    try:
        return datetime.date(int(m.group(3)), mon, int(m.group(2))).isoformat()
    except ValueError:
        return None


def expired(iso, today):
    """None when either term is missing: an ignorance is not a verdict."""
    if not iso or today is None:
        return None
    try:
        return datetime.date.fromisoformat(iso) < today
    except ValueError:
        return None


def parse_ad(url, body, today=None):
    """One vacancy from its served page. Raises ShapeMoved when the shape has."""
    if not AD_RE.match(url or ""):
        raise ShapeMoved(f"{url!r} is not a https://dadlijobs.com/job/<slug>/ address")
    markup = strip_style(body or "")
    fig = FIGURE_RE.search(markup)
    if not fig:
        raise ShapeMoved(
            "no <figure class=\"jobsearch-jobdetail-list\"> on the page: the "
            "theme's detail header has moved and every field below reads from it")
    figure = fig.group(1)
    notes = []

    t = TITLE_RE.search(figure)
    title = unescape_once(text_of(t.group(1))) if t else None
    if not title:
        raise ShapeMoved("the detail header carries no job title")

    emp = EMPLOYER_RE.search(figure)          # INSIDE the figure, never page-wide
    emp_slug = emp.group(1) if emp else None
    emp_name = unescape_once(text_of(emp.group(2))) if emp else None
    if EMPLOYER_RE.search(markup) and not emp:
        notes.append("an /employer/ href exists on the page but not inside the "
                     "detail figure, so no employer is claimed: the related-jobs "
                     "rail carries those links too.")

    ty = TYPE_RE.search(figure)
    sec = SECTOR_RE.search(figure)
    pl = PLACE_RE.search(figure)
    place, coords = None, None
    if pl:
        inner = pl.group(1)
        c = COORD_RE.search(inner)
        coords = bool(c)
        place = unescape_once(text_of(re.sub(r"(?is)<a\b.*?</a>", " ", inner))) or None

    dates = {k.strip().lower(): text_of(v) for k, v in DATE_LI_RE.findall(figure)}
    posted = parse_date(dates.get("post date", ""))
    expires = parse_date(dates.get("apply before", ""))

    apps = APPS_RE.search(text_of(figure))
    jid = JOBID_RE.search(markup)
    job_id = jid.group(1) if jid else None

    d = DESC_OPEN_RE.search(markup)
    if not d:
        raise ShapeMoved("no <div class=\"jobsearch-description\"> in the markup "
                         "(the inline CSS names the class, the markup must too)")
    desc_raw = text_of(div_block(markup, d.start()))
    desc, took = redact(unescape_once(desc_raw))

    ap = APPLY_RE.search(markup)
    route = "on_site" if apps else ("email" if ap else None)
    if ap:
        _, took_apply = redact(ap.group(1))
        took = sorted(set(took) | set(took_apply))
        if job_id and ap.group(2) != job_id:
            notes.append(f"the apply button's data-id is {ap.group(2)} and the "
                         f"detail block states Job ID {job_id}: the two no longer "
                         f"name the same vacancy, so neither is used as the key.")
            job_id = None

    rec = {
        "source": "dadlijobs",
        "country": COUNTRY,
        "url": url,
        "slug": AD_RE.match(url).group(1),
        "job_id": job_id,
        "title": title,
        "employer": emp_name,
        "employer_slug": emp_slug,
        "employment_type": unescape_once(text_of(ty.group(1))) if ty else None,
        "sector": unescape_once(text_of(sec.group(1))) if sec else None,
        "location": place,
        "location_precision": (None if not place else
                               "place name; the page's map href carries lat/lon, "
                               "read and dropped" if coords else "place name"),
        "posted": posted,
        "expires": expires,
        "expired": expired(expires, today),
        "applications": int(apps.group(1)) if apps else None,
        "apply_route": route,
        "description": desc[:20000] or None,
        "contact": None,
        "withheld_fields": sorted(set(took)),
    }
    if withheld_a_contact(took):
        rec["contacts_withheld"] = True
    if not took:
        notes.append("nothing was removed from this ad, so withheld_fields is "
                     "empty: it deposits no recruiter contact "
                     + ("and applies through the board itself."
                        if route == "on_site" else "and names no apply route."))
    for k in ("title", "employer", "description"):
        if residual_entities(rec[k]):
            notes.append(f"{k} still carries an HTML entity after one unescape; "
                         f"this host's escaping was measured single, so the field "
                         f"is emitted as served rather than unescaped twice.")
    if route is None:
        notes.append("neither an Application(s) counter nor a mailto apply button: "
                     "how one applies to this vacancy is not stated on the page.")
    return rec, notes


# -------------------------------------------------------------- subcommands

def cmd_list(a):
    today = datetime.date.fromisoformat(a.today) if a.today else None
    code, body, _ = get(INDEX)
    if code != 200 or not body:
        die(f"{INDEX}: HTTP {code}", EXIT_BROKEN)
    try:
        child = job_sitemap_of(body)
        others = [u.rsplit("/", 1)[-1] for u, _ in locs(body)
                  if not u.rstrip("/").endswith("/job-sitemap.xml")]
        ccode, cbody, final = get(child)
        if ccode != 200 or not cbody:
            die(f"{child}: HTTP {ccode}", EXIT_BROKEN)
        if not is_urlset(cbody):
            raise ShapeMoved(
                f"{child} returned {len(cbody.encode())} bytes with no <urlset: "
                f"a declared sitemap is retrieved and VERIFIED, never believed")
        pairs = locs(cbody)
        ads = ads_of(pairs)
    except ShapeMoved as e:
        die(str(e))
    if others:
        note(f"the index also names {', '.join(others)} — facet archives, not "
             f"vacancies; a path prefix reads like a nature and is not one.")
    if len(ads) != len(pairs):
        note(f"{len(pairs)} addresses in the job sitemap and {len(ads)} are "
             f"vacancies at /job/<slug>/.")
    note(f"{len(ads)} vacancies in {child}. **The board states no total**: both "
         f"«Displayed Here» strings it serves are page ranges, and the job post "
         f"type is absent from /wp-json/wp/v2/types, so there is no second count "
         f"to set against this one.")
    rows = ads[:a.limit] if a.limit else ads
    hydrate = min(a.hydrate or 0, len(rows))
    for i, (u, slug, mod) in enumerate(rows):
        if i < hydrate:
            acode, abody, _ = get(u)
            if acode != 200 or not abody:
                note(f"{u}: HTTP {acode} — emitted as an address only")
                print(json.dumps({"source": "dadlijobs", "country": COUNTRY,
                                  "url": u, "slug": slug, "lastmod": mod,
                                  "hydrated": False}, ensure_ascii=False))
                continue
            try:
                rec, ns = parse_ad(u, abody, today)
            except ShapeMoved as e:
                die(str(e))
            rec["lastmod"] = mod
            rec["hydrated"] = True
            for n in ns:
                note(f"{slug}: {n}")
            print(json.dumps(rec, ensure_ascii=False))
        else:
            print(json.dumps({"source": "dadlijobs", "country": COUNTRY,
                              "url": u, "slug": slug, "lastmod": mod,
                              "hydrated": False}, ensure_ascii=False))
    if hydrate < len(rows):
        note(f"{hydrate} of {len(rows)} record(s) hydrated; the rest are addresses "
             f"and their lastmod. The sitemap carries no field but those two, and "
             f"the list pages serve one page with no pager to a plain client.")


def cmd_ad(a):
    code, body, _ = get(a.url)
    if code == 404:
        die(f"{a.url}: 404 — the vacancy is gone", EXIT_GONE)
    if code != 200 or not body:
        die(f"{a.url}: HTTP {code}", EXIT_BROKEN)
    today = datetime.date.fromisoformat(a.today) if a.today else None
    try:
        rec, notes = parse_ad(a.url, body, today)
    except ShapeMoved as e:
        die(str(e))
    for n in notes:
        note(n)
    print(json.dumps(rec, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description="Dadli Jobs — the sitemap, which is the only enumerator a "
                    "plain client can see, and one vacancy.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="the vacancies the job sitemap carries; "
                                    "--hydrate N also fetches the first N pages")
    s.add_argument("--limit", type=int)
    s.add_argument("--hydrate", type=int, default=0)
    s.add_argument("--today", help="YYYY-MM-DD; decides `expired` instead of the clock")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one vacancy from its served page")
    d.add_argument("--url", required=True)
    d.add_argument("--today", help="YYYY-MM-DD; decides `expired` instead of the clock")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
