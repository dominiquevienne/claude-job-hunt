#!/usr/bin/env python3
"""JobsDZ (`jobsdz.com`, Algeria) — the list route a plain client can reach is
the sitemap, and the board's own count comes from a route that renders NOTHING.

  jobsdz.py list [--limit N] [--hydrate N] [--today YYYY-MM-DD]
  jobsdz.py ad --url <vacancy URL>
  jobsdz.py count

THE RULES PERMIT THE AJAX ROUTE BY AN `Allow:` THAT IS WRITTEN, NOT BY SILENCE

`robots.txt` is 593 bytes, HTTP 200, md5 `3c58e22b05f0d8fb867bb1b53b204bb2`,
read 2026-11-10 11:33Z: one `*` group whose three `Disallow` lines are
`/wp-admin/` and two WooCommerce upload paths, and **one `Allow:
/wp-admin/admin-ajax.php`** — the Rank Math recommendation, whose own Arabic
comment calls it a safe WordPress robots.txt. So the verdict on the AJAX route
is `allowed=True` with `kind='allow'` and the deciding rule NAMED: the `Allow`
matches at least as much of the path as the `Disallow: /wp-admin/` does.

**Reading only the `Disallow` lines would have closed this board under borne 1
and it is open.** That direction is the restrictive one, and nobody audits a
prudence. `ignored_for()` returns `[]`, `delay_for()` returns `None` — so the
2 s pace below is OURS and not the host's — and the single `Sitemap:` names
`https://jobsdz.com/sitemap_index.xml`, on the SAME host, so no guard has to
be retaken elsewhere.

THE AJAX ROUTE ANSWERS WITH A COUNT AND AN EMPTY `html`, THREE TIMES OVER

WP Job Manager's `admin-ajax.php?action=job_manager_get_listings` is what the
shell calls, and the shell declares its own parameters in the markup
(`data-per_page="10"`, `data-orderby="featured"`, `data-order="DESC"`).
Replayed with exactly those, then with the plugin JS's full set
(`search_keywords`, `search_location`, `search_categories`,
`show_pagination`, `form_data`), then with `X-Requested-With:
XMLHttpRequest` and a `Referer` of the shell: **HTTP 200, 741 bytes, `html`
empty every time**, and the first two bodies are identical to the octet
(md5 `291ab46abd08`). So the route is not the adapter's route, and the issue
that asked for it named a first line the object does not have.

AND `found_jobs` IS A BOOLEAN, SO THE WITNESS THE ISSUE NAMED IS NOT A COUNT

What the route does carry is `max_num_pages`, and it is a witness BECAUSE IT
VARIES — the control that separates a measurement from a constant:

    per_page=10   max_num_pages=256  ->  total in [2551 ; 2560]
    per_page=100  max_num_pages=26   ->  total in [2501 ; 2600]
    intersection                         [2551 ; 2560]

That interval is the board's own `job_listing` query, not our extraction, and
it is the discriminant a zero needs. The front's «2,400+ وظيفة» is a rounded
claim and agrees with it. `count` prints this interval and nothing else.

THE SITEMAP CARRIES 1 571 ADDRESSES, WHICH IS NOT THE BOARD'S COUNT

`/sitemap_index.xml` is a real `sitemapindex` naming 22 children.
`job_listing-sitemap.xml` is the vacancies: 226 653 bytes, **1 680 `<loc>`
for 1 572 distinct** — so each of about a hundred vacancies is listed twice
and an extractor that does not deduplicate reports 1 677. The ads live at
**`/job/<slug>/`**, not at `/ar/<post>/` as `shared/boards/jobsdz.md` and
#787 both state.

And they live under TWO prefixes: **1 569 at `/job/<slug>/`, 2 at
`/ar/job/<slug>/`**, plus the `/job-listings/` archive — 1 572 exactly. The
two Arabic-prefixed ones were found because a wider motif and `AD_RE`
disagreed by two, and then by READING the two members: a count never says
WHICH are missing, and an omission by MEMBERS leaves no other trace.

1 571 against 2 551–2 560 is a gap of about a thousand. **Neither enumerator
is established to contain the other**, so this adapter emits the sitemap's
population, says what it is, and claims no board size. The sitemap carries
stale vacancies — the last address by sitemap order was posted 2025-12-25 and
declares no `validThrough` at all — which is a reason the two can differ and
not a measurement of why.

WHAT IS NOT TAKEN, AND THE FIRST REASON IS NOT TECHNICAL

The index also names `resume-sitemap.xml`, `resume_category-sitemap.xml` and
`resume_region-sitemap.xml`. Those are CANDIDATES' CVs. Every one of them
returns `allowed=True` from the guard, and none is retrieved: a host that
forbids nothing has not thereby consented to our taking everything it
exposes, and the filter is a condition of SAFETY and not an optimisation.
`/ar/submit-resume/` and `/ar/add-job/` are declined on the same ground.

Three further children — `jobpost-sitemap1.xml`, `jobpost-sitemap2.xml`,
`emlpois-hors-algerie-sitemap.xml` — look like a second and third ad-bearing
post type. **Their nature is not established: no member of any of them has
been opened.** A path prefix reads like a nature and is not one, so they are
named in a note and left alone rather than marched on their names.

THE AD PAGE CARRIES A REAL `JobPosting`, AND TWO OF ITS FIELDS CHANGE SHAPE

Measured on three members taken at the FIRST, MEDIAN and LAST rank of the
sitemap — never the first three, which are one genre:

  * `jobLocation.address` is a bare STRING on two (`'Alger'`, `'Blida'`) and a
    `PostalAddress` OBJECT on the third (`addressLocality`, `addressRegion`,
    `addressCountry`). **A reader written for either one returns `None` on the
    other**, which is a field that reads as absent rather than as an error.
  * `validThrough` and `employmentType` are PRESENT on two and ABSENT on the
    third: the key sets are 11 and 9, so `expires` and `employment_type` are
    read as optional and their absence is reported, not defaulted.
  * `hiringOrganization.name` is **present and EMPTY** on the third. `if x`
    does not separate that from absent, so the floor here is positive and
    `employer_declared` says which of the two was read.

Dénominateur 3, one day: these are FORMS observed, not frequencies. What does
not depend on the sample is the shape — both address forms read, both optional
fields optional, and a positive floor on the employer.

THE ESCAPING IS NOT UNIFORM, SO THE DESCRIPTION IS UNESCAPED ONCE AND SAID SO

`description` is HTML-escaped inside the JSON-LD. One `html.unescape` clears
every entity on two of the three ads (172 and 148 entities to zero). On the
third it leaves ONE — `&#8217;` inside the place name «Oued S’mar» — which
clears on a second pass, so that ad is doubly escaped at the source.

**It is still unescaped ONCE.** Unescaping twice would turn a legitimate
literal `&amp;` in an employer's own text into an `&`, and that is a silent
corruption of content; a visible `&#8217;` is honest. `description_entities`
carries the residual count so the next shape change is a number rather than a
guess.

WHAT THE ADAPTER DOES NOT EMIT

No contact was found in any of the three descriptions once DECODED — the
probe run on the escaped form would have found none either way, which is why
it runs on the decoded one. The redaction is therefore reachable and silent on
this corpus, kept because it turns the first recruiter address this board
publishes into a withheld field instead of a leak. It runs on the free-text
description ONLY: `title`, `employer` and `location` have a known meaning, and
an Algerian monthly wage in dinars is five or six figures while the phone form
below demands a leading `0` or `+213` and eight more.

`contacts_withheld` is DERIVED from what `redact` actually took, through
`_withheld`, so it is absent rather than false when nothing was removed — and
on this corpus of three it is absent on 3 of 3, which makes its TRUE branch
dead in the world and alive only in `tests/` (§4 ter, fifth species: a branch
green on its fixtures can be dead on the corpus, and the two instruments are
disjoint). It is kept because the first recruiter address this board publishes
would otherwise leave the record without a word said about it.
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

BASE = "https://jobsdz.com"
INDEX = BASE + "/sitemap_index.xml"
AJAX = BASE + "/wp-admin/admin-ajax.php"
COUNTRY = "DZ"

JOBMAP_NAME = "job_listing-sitemap.xml"
#  Named so the note can say what is left alone, and WHY, instead of silently
#  skipping it. The three resume children are candidates' CVs.
CV_NAMES = ("resume-sitemap.xml", "resume_category-sitemap.xml",
            "resume_region-sitemap.xml")
UNESTABLISHED = ("jobpost-sitemap1.xml", "jobpost-sitemap2.xml",
                 "emlpois-hors-algerie-sitemap.xml")

#  BOTH prefixes: this host serves 1 569 ads at /job/<slug>/ and 2 at
#  /ar/job/<slug>/, and a motif that sees one form drops the other in
#  silence -- found by the count of a wider motif disagreeing by two, then
#  by READING the two members rather than trusting the difference.
AD_RE = re.compile(r"^https://jobsdz\.com/(?:ar/)?job/([^/?#]+)/$")
LOC_RE = re.compile(r"(?is)<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>")
MOD_RE = re.compile(r"(?is)<lastmod>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</lastmod>")
URLSET_RE = re.compile(r"(?i)<(?:[a-z0-9]+:)?urlset\b")
INDEX_RE = re.compile(r"(?i)<(?:[a-z0-9]+:)?sitemapindex\b")
LD_RE = re.compile(
    r'(?is)<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>')
TAG_RE = re.compile(r"(?s)<[^>]+>")
ENTITY_RE = re.compile(
    r"&(?:[a-zA-Z][a-zA-Z0-9]{1,30}|#\d{1,6}|#x[0-9a-fA-F]{1,6});")

MAILTO_RE = re.compile(r"(?i)mailto:[^\s\"'<>]+")
MAIL_RE = re.compile(r"[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}")
#  A leading 0 or +213 and EIGHT more digits. A dinar wage is five or six.
TEL_RE = re.compile(r"(?<![\d])(?:\+213|00213|0)[\s.\-/]?\d(?:[\s.\-/]?\d){7,9}(?![\d])")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


class ShapeMoved(Exception):
    """The page's shape has moved: raise rather than report an empty board."""


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobsdz] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# `delay_for()` returns None on this host's 593-byte rules file, so 2 s is ours
_PACE = Pace("jobsdz.com", own=2.0)


def _send(url, data=None, accept="application/xml,text/html;q=0.9"):
    gate(url)
    _PACE.wait()
    body = None
    headers = {"User-Agent": UA, "Accept": accept, "Accept-Language": "ar,fr;q=0.9"}
    if data is not None:
        body = urllib.parse.urlencode(data).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(wire_url(url), data=body, headers=headers)
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


def get(url):
    return _send(url)


def post_listings(per_page, page=1):
    """The board's own `job_listing` query. Its `html` is empty; its count is not."""
    return _send(AJAX, data={"action": "job_manager_get_listings",
                             "page": str(page), "per_page": str(per_page),
                             "orderby": "featured", "order": "DESC"},
                 accept="application/json,*/*;q=0.5")


# ---------------------------------------------------------------- pure readers

def is_urlset(body):
    """A readable body is not a response: this says it is an address list."""
    return bool(URLSET_RE.search(body or ""))


def is_sitemap_index(body):
    return bool(INDEX_RE.search(body or ""))


def locs(body):
    """(address, lastmod) pairs, CDATA-aware even where this host does not use it."""
    urls = [u.strip() for u in LOC_RE.findall(body or "")]
    mods = [m.strip() for m in MOD_RE.findall(body or "")]
    mods += [None] * (len(urls) - len(mods))
    return list(zip(urls, mods[:len(urls)]))


def job_sitemap_of(index_body):
    """The vacancies child, BY NAME and never by position."""
    if not is_sitemap_index(index_body):
        raise ShapeMoved(f"{INDEX} is no longer a <sitemapindex>")
    for u, _ in locs(index_body):
        if u.rstrip("/").endswith("/" + JOBMAP_NAME):
            return u
    raise ShapeMoved(
        f"the sitemap index no longer names {JOBMAP_NAME}; it names "
        + ", ".join(u.rsplit("/", 1)[-1] for u, _ in locs(index_body)))


def children_named(index_body, names):
    """Which of `names` the index actually declares, so a note states fact."""
    have = {u.rsplit("/", 1)[-1] for u, _ in locs(index_body)}
    return [n for n in names if n in have]


def ads_of(pairs):
    """Addresses that are vacancies, deduplicated, order preserved."""
    seen, out = set(), []
    for u, mod in pairs:
        m = AD_RE.match(u)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            out.append((u, m.group(1), mod))
    return out


def job_posting(markup):
    """The `JobPosting` of a page's JSON-LD, found anywhere in the graph."""
    def walk(x):
        if isinstance(x, dict):
            if x.get("@type") == "JobPosting":
                return x
            for v in x.values():
                r = walk(v)
                if r is not None:
                    return r
        elif isinstance(x, list):
            for v in x:
                r = walk(v)
                if r is not None:
                    return r
        return None
    for block in LD_RE.findall(markup or ""):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        found = walk(data)
        if found is not None:
            return found
    return None


def unescape_once(value):
    """ONE pass. Twice would turn a literal `&amp;` in an employer's text into `&`."""
    return htmlmod.unescape(value) if isinstance(value, str) else value


def residual_entities(value):
    return ENTITY_RE.findall(value or "") if isinstance(value, str) else []


def text_of(value):
    """Tags out, whitespace squeezed. Run AFTER one unescape, never before."""
    if not isinstance(value, str):
        return None
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", value)).strip() or None


def address_of(job_location):
    """Both forms this host serves, and WHICH one was read.

    A bare string on two of three ads, a `PostalAddress` object on the third.
    A reader written for either returns `None` on the other -- a field that
    reads as absent instead of raising.
    """
    if not isinstance(job_location, dict):
        return None, None
    addr = job_location.get("address")
    if isinstance(addr, str):
        return (text_of(unescape_once(addr)), "string")
    if isinstance(addr, dict):
        parts = [addr.get(k) for k in
                 ("addressLocality", "addressRegion", "addressCountry")]
        parts = [text_of(unescape_once(p)) for p in parts if isinstance(p, str)]
        keep = []
        for p in parts:
            #  EQUALITY is not enough: this host serves addressLocality
            #  'Algiers, Algeria' beside addressCountry 'Algeria', so a dedup on
            #  == keeps both and the emitted field repeats the country.
            if p and not any(p in k for k in keep):
                keep = [k for k in keep if k not in p] + [p]
        return ((", ".join(keep) or None), "PostalAddress")
    return None, None


def declared(value):
    """A POSITIVE floor: present-and-empty is not absent, and `if x` conflates them."""
    if value is None:
        return None, "absent"
    if isinstance(value, str) and not value.strip():
        return None, "present but empty"
    return value, "declared"


def redact(value):
    """Withhold recruiter contacts from FREE TEXT, and report what was taken.

    The witness is DERIVED from what was actually removed, so it cannot
    declare having withheld what nobody deposited.
    """
    if not isinstance(value, str) or not value:
        return value, []
    took, out = [], value
    if MAILTO_RE.search(out):
        out = MAILTO_RE.sub("[mailto withheld]", out)
        took.append("mailto")
    if MAIL_RE.search(out):
        out = MAIL_RE.sub("[e-mail withheld]", out)
        took.append("email")
    if TEL_RE.search(out):
        out = TEL_RE.sub("[telephone withheld]", out)
        took.append("telephone")
    return out, took


def parse_date(value):
    """The ISO-8601 instant this host serves, kept as the DATE it names."""
    if not isinstance(value, str) or not value.strip():
        return None
    m = re.match(r"\s*(\d{4}-\d{2}-\d{2})", value)
    return m.group(1) if m else None


def expired(iso, today=None):
    """`None` when the ad declares no expiry -- absent is not 'still open'."""
    if not iso:
        return None
    day = today or datetime.date.today()
    try:
        return datetime.date.fromisoformat(iso) < day
    except ValueError:
        return None


def parse_ad(url, body, today=None):
    """One vacancy from its served page. Raises ShapeMoved when the shape has."""
    m = AD_RE.match(url or "")
    if not m:
        raise ShapeMoved(f"{url!r} is not a https://jobsdz.com/job/<slug>/ address")
    jp = job_posting(body or "")
    if jp is None:
        raise ShapeMoved(
            "no JobPosting in this page's JSON-LD: every field below reads from "
            "it, and the list routes carry no JobPosting at all, so there is no "
            "second surface to fall back to")
    notes = []

    title = text_of(unescape_once(jp.get("title")))
    if not title:
        raise ShapeMoved("the JobPosting carries no title")

    org = jp.get("hiringOrganization")
    #  `declared` runs on the RAW value. `text_of` returns None for an empty
    #  string, so normalising FIRST collapses 'present but empty' into 'absent'
    #  and the positive floor becomes inert -- measured on the third ad, whose
    #  hiringOrganization.name IS an empty string.
    org_name, org_state = declared(
        (org or {}).get("name") if isinstance(org, dict) else None)
    org_name = text_of(unescape_once(org_name)) if org_name else None
    if org_state == "present but empty":
        notes.append("hiringOrganization.name is present and EMPTY, so no "
                     "employer is claimed; `if x` does not separate that from "
                     "absent and employer_declared says which was read.")

    place, place_form = address_of(jp.get("jobLocation"))
    if jp.get("jobLocation") is not None and place is None:
        notes.append("jobLocation is served in a shape neither the string form "
                     "nor PostalAddress covers, so no location is claimed: "
                     + json.dumps(jp.get("jobLocation"), ensure_ascii=False)[:200])

    etypes = jp.get("employmentType")
    if isinstance(etypes, str):
        etypes = [etypes]
    if etypes is None:
        notes.append("no employmentType on this ad; the field is optional on "
                     "this host and its absence is reported, not defaulted.")

    expires = parse_date(jp.get("validThrough"))
    if jp.get("validThrough") is None:
        notes.append("no validThrough on this ad, so `expired` is null rather "
                     "than false: an absent expiry is not an open vacancy.")

    desc_once = unescape_once(jp.get("description") or "")
    desc_text = text_of(desc_once) or ""
    desc, took = redact(desc_text)
    left = residual_entities(desc)
    if left:
        notes.append(
            f"{len(left)} entity(ies) survive ONE unescape in the description "
            f"(first {left[0]!r}): this host is doubly escaped on some ads. The "
            f"field is emitted as served after one pass -- a second would turn a "
            f"literal &amp; in the employer's own text into &.")

    salary = jp.get("baseSalary")
    rec = {
        "source": "jobsdz",
        "country": COUNTRY,
        "url": url,
        "slug": m.group(1),
        "title": title,
        "employer": org_name,
        "employer_declared": org_state,
        "employment_type": etypes,
        "location": place,
        "location_form": place_form,
        "posted": parse_date(jp.get("datePosted")),
        "expires": expires,
        "expired": expired(expires, today),
        "direct_apply": jp.get("directApply"),
        "salary_declared": salary is not None,
        "description": desc[:20000] or None,
        "description_entities": len(left),
        "contact": None,
        "withheld_fields": sorted(set(took)),
    }
    if withheld_a_contact(took):
        rec["contacts_withheld"] = True
    if not took:
        notes.append("nothing was removed from this ad, so withheld_fields is "
                     "empty: it deposits no recruiter contact in its description.")
    if rec["direct_apply"] is False and not took:
        notes.append("directApply is false and the description names no contact: "
                     "how one applies is not stated in the structured data.")
    return rec, notes


# -------------------------------------------------------------- subcommands

def board_interval():
    """The board's OWN count, as an interval, and only if it VARIES.

    A `max_num_pages` that did not move with `per_page` would have the form of
    a measurement and discriminate nothing, so the second call is the control
    and not a refinement.
    """
    out = []
    for pp in (10, 100):
        code, body, _ = post_listings(pp)
        if code != 200 or not body:
            die(f"{AJAX}: HTTP {code} at per_page={pp}", EXIT_BROKEN)
        try:
            data = json.loads(body)
        except ValueError:
            raise ShapeMoved(
                f"the AJAX route returned {len(body.encode())} bytes that are "
                f"not JSON at per_page={pp}")
        if "max_num_pages" not in data:
            raise ShapeMoved(
                "the AJAX route no longer carries max_num_pages; it carries "
                + ", ".join(sorted(data)))
        pages = data["max_num_pages"]
        if not isinstance(pages, int) or pages < 1:
            raise ShapeMoved(f"max_num_pages is {pages!r} at per_page={pp}")
        out.append((pp, pages, (pages - 1) * pp + 1, pages * pp,
                    len(data.get("html") or "")))
    lo = max(o[2] for o in out)
    hi = min(o[3] for o in out)
    if lo > hi:
        raise ShapeMoved(
            "the two per_page probes give DISJOINT intervals ("
            + " and ".join(f"[{o[2]};{o[3]}] at per_page={o[0]}" for o in out)
            + "): the count moved between the two calls, so no interval is claimed")
    constant = len({o[1] for o in out}) == 1
    return lo, hi, out, constant


def cmd_count(a):
    try:
        lo, hi, probes, constant = board_interval()
    except ShapeMoved as e:
        die(str(e))
    for pp, pages, plo, phi, hlen in probes:
        note(f"per_page={pp}: max_num_pages={pages} -> [{plo};{phi}], "
             f"html {hlen} byte(s)")
    if constant:
        die("max_num_pages did not move when per_page did: it is a constant, "
            "which has the form of a measurement and discriminates nothing",
            EXIT_BROKEN)
    print(json.dumps({"source": "jobsdz", "country": COUNTRY,
                      "board_count_low": lo, "board_count_high": hi,
                      "basis": "WP Job Manager max_num_pages at two per_page "
                               "values, intersected; the board's own query and "
                               "not this adapter's extraction"},
                     ensure_ascii=False))


def cmd_list(a):
    today = datetime.date.fromisoformat(a.today) if a.today else None
    code, body, _ = get(INDEX)
    if code != 200 or not body:
        die(f"{INDEX}: HTTP {code}", EXIT_BROKEN)
    try:
        child = job_sitemap_of(body)
        cvs = children_named(body, CV_NAMES)
        unknown = children_named(body, UNESTABLISHED)
        ccode, cbody, _ = get(child)
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
    if not ads:
        die(f"{child} carries {len(pairs)} address(es) and none is a "
            f"/job/<slug>/ vacancy", EXIT_BROKEN)
    if cvs:
        note("the index also names " + ", ".join(cvs) + " — candidates' CVs. "
             "The guard permits them and they are NOT retrieved: a host that "
             "forbids nothing has not consented to our taking all it exposes.")
    if unknown:
        note("the index also names " + ", ".join(unknown) + " — these look like "
             "further ad-bearing post types and their nature is NOT established: "
             "no member has been opened, and a path prefix reads like a nature "
             "without being one.")
    if len(ads) != len(pairs):
        note(f"{len(pairs)} address(es) in {child.rsplit('/', 1)[-1]} and "
             f"{len(ads)} distinct vacancies at /job/<slug>/: each of about a "
             f"hundred is listed twice, so an extractor that does not "
             f"deduplicate reports high.")
    note(f"{len(ads)} vacancies in the sitemap. This is the SITEMAP's "
         f"population and not the board's size: `jobsdz.py count` asks the "
         f"board's own query, which answered [2551;2560] on 2026-11-10, and "
         f"neither enumerator is established to contain the other.")
    rows = ads[:a.limit] if a.limit else ads
    hydrate = min(a.hydrate or 0, len(rows))
    for i, (u, slug, mod) in enumerate(rows):
        if i < hydrate:
            acode, abody, _ = get(u)
            if acode != 200 or not abody:
                note(f"{u}: HTTP {acode} — emitted as an address only")
                print(json.dumps({"source": "jobsdz", "country": COUNTRY,
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
            print(json.dumps({"source": "jobsdz", "country": COUNTRY,
                              "url": u, "slug": slug, "lastmod": mod,
                              "hydrated": False}, ensure_ascii=False))
    if hydrate < len(rows):
        note(f"{hydrate} of {len(rows)} record(s) hydrated; the rest are "
             f"addresses and their lastmod. The two list surfaces serve NO ad "
             f"to a plain client and the AJAX route renders an empty html, so "
             f"there is no cheaper place to read a field than the ad page.")


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
        description="JobsDZ — the sitemap, which is the only enumerator that "
                    "yields an ad address to a plain client, one vacancy, and "
                    "the board's own count.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="the vacancies the job_listing sitemap "
                                    "carries; --hydrate N also fetches the "
                                    "first N ad pages")
    s.add_argument("--limit", type=int)
    s.add_argument("--hydrate", type=int, default=0)
    s.add_argument("--today", help="YYYY-MM-DD; decides `expired` instead of the clock")
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one vacancy from its served page")
    d.add_argument("--url", required=True)
    d.add_argument("--today", help="YYYY-MM-DD; decides `expired` instead of the clock")
    d.set_defaults(fn=cmd_ad)
    c = sub.add_parser("count", help="the board's own job_listing count, as an "
                                     "interval, from two per_page probes")
    c.set_defaults(fn=cmd_count)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
