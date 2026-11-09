#!/usr/bin/env python3
"""GuyanaJobs.net (`guyanajobs.net`, Guyana) — TWO populations of vacancy, and only one of them carries text at all.

  guyanajobs.py sitemap [--limit N] [--kind job|flyer]
  guyanajobs.py ad --url <vacancy URL>

THE BOARD PUBLISHES TWO THINGS AND THEY ARE NOT THE SAME KIND OF OBJECT

`robots.txt` is 118 bytes, refuses only `/wp-admin/`, declares **no
`Crawl-delay`** (`delay_for()` returns `None`, so the 2 s pace is ours) and
DECLARES its enumerator: `Sitemap: https://guyanajobs.net/sitemap_index.xml`.
**That is not `/sitemap.xml`**, which is the §3 bis case exactly — a path
declared elsewhere is covered by no verdict taken at the root — so it is
guarded on its own exact path. `sitemaps_for()` returns it; `group_for()`
drops it in silence, and the dedicated parser is what answers.

The index has five members, and TWO of them could carry vacancies:

  `job_listing-sitemap.xml`   **3** entries, `/job/<slug>/` — the job-board
                              plugin. Each carries a FULL `JobPosting` in
                              JSON-LD: `hiringOrganization`, `jobLocation`
                              (`Region 4 Demerara-Mahaica`), `datePosted`,
                              `validThrough`, `employmentType`, `directApply`,
                              and a description measured at **4 035
                              characters**.
  `post-sitemap.xml`          **18** flyers, `/<slug>/` — ordinary WordPress
                              posts. `_ldjson.postings()` returns **0** and
                              `absent_reason()` says `no-jobposting`,
                              `our_fault=False`: **the vacancy text is inside
                              the image.** We do not OCR, so a flyer yields
                              its title, its address and its date and nothing
                              else — and it says so in the record rather than
                              emitting an empty description.

**So #705's blocker — "ce qu'une annonce porte comme texte n'est pas encore
mesuré" — is answered, and the answer is DIFFERENT for the two populations.**
The record carries `kind` for exactly that reason: a consumer that treats the
two alike will either throw away three complete vacancies or believe eighteen
empty ones.

COUNTING `<loc>` WOULD REPORT THIS BOARD TWO AND A HALF TIMES TOO LARGE

`_sitemap.count_says()` said it before anything else did:

    post-sitemap.xml          46 `<loc>` against 19 `<url>`
    job_listing-sitemap.xml    5 `<loc>` against  3 `<url>`

The excess are `<image:loc>` — a flyer's image, a company logo — and
`_sitemap.locs()` matches them because it is deliberately tolerant of a
namespace prefix, which is right for its own job. **So the count here is taken
on `<url>` blocks and the address on the FIRST `<loc>` inside each**, which
makes the image structurally unable to be counted as a vacancy rather than
filtered out afterwards. *`locs()` is SOUND and is not to be "repaired": its
tolerance is what makes it work on prefixed sitemaps.*

NO WITNESS IS REACHABLE BY OUR ROUTE, AND THAT IS A FINDING RATHER THAN A GAP

#705 proposes the WordPress REST `X-WP-Total` as the count. It is a response
HEADER, and `bin/fetch-body.py` — the only retrieval route — records
`status`, `bytes`, `md5`, `agent`, `cache.headers` (`vary` only),
`content_encoding`, `final_url` and `vendor`, and **no arbitrary response
header**. So that witness is not readable without either extending the tool
or leaving the sanctioned route, and neither is this adapter's business. **The
site states no count anywhere**, which the card already said. The figures
below are therefore this adapter's own extraction with nothing corroborating
them — and they are small enough that the `<url>`/`<loc>` split above is the
only thing standing between 21 and 51.

Measured 2026-11-09 12:37-12:40 UTC, guard on each exact path in a turn
distinct from retrieval, one token. Issue #705.
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
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
from _sitemap import maybe_gunzip
from _ua import UA
from _zero import empty_first_page

BASE = "https://guyanajobs.net"
INDEX = BASE + "/sitemap_index.xml"
COUNTRY = "GY"

JOB_RE = re.compile(r"^https://guyanajobs\.net/job/([^/]+)/$")
FLYER_RE = re.compile(r"^https://guyanajobs\.net/([^/]+)/$")
TITLE_RE = re.compile(r"(?is)<title>(.*?)</title>")
# the `<url>` blocks, and the FIRST `<loc>` inside each -- an `<image:loc>`
# then cannot be counted as a vacancy, rather than being filtered out after
URL_BLOCK_RE = re.compile(r"(?is)<url\b.*?</url>")
FIRST_LOC_RE = re.compile(r"(?is)<(?:[a-z0-9]+:)?loc>\s*(.*?)\s*</(?:[a-z0-9]+:)?loc>")
LASTMOD_RE = re.compile(r"(?is)<(?:[a-z0-9]+:)?lastmod>\s*(.*?)\s*</(?:[a-z0-9]+:)?lastmod>")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


class ShapeMoved(Exception):
    """200, and neither shape this adapter knows.

    A pure function must not call `sys.exit`: raising is what lets `tests/`
    tell "the shape moved" from "the vacancy is empty".
    """


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[guyanajobs] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# `delay_for()` returns None on this host's 118-byte rules file, so 2 s is ours
_PACE = Pace("guyanajobs.net", own=2.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
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


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(markup)).strip()


def entries(xml):
    """`[(address, lastmod)]` from the `<url>` blocks — **never from `<loc>`.**

    `<loc>` counts 46 where there are 19 on this host's post sitemap, the
    excess being `<image:loc>`. Taking the FIRST `<loc>` of each `<url>` makes
    an image structurally uncountable instead of filtered afterwards.
    """
    out = []
    for block in URL_BLOCK_RE.findall(xml):
        loc = FIRST_LOC_RE.search(block)
        if not loc:
            continue
        lm = LASTMOD_RE.search(block)
        out.append((loc.group(1).strip(), lm.group(1).strip() if lm else None))
    return out


# which member an address came from, mapped to what that member HOLDS
MEMBER_KIND = {"job_listing-sitemap.xml": "job", "post-sitemap.xml": "flyer"}


def kind_from_member(member):
    """What a member of the declared index HOLDS — `"job"`, `"flyer"` or `None`.

    **THE KIND COMES FROM THE MEMBER AND NEVER FROM THE URL SHAPE**, because a
    flyer and an ordinary page are the SAME shape: a flat `/<slug>/`. Deciding
    on the shape counted `page-sitemap.xml` as twelve flyers — `/about-us/`,
    `/contact-us/`, `/privacy-policy/`, `/cv-template/`,
    `/terms-and-conditions/`, `/blog/`, `/employer-submit-job/`,
    `/employer-job-dashboard/`, `/sponsored-jobs/`, `/guyana-jobs-telegram/`,
    `/government-ministries-directory-guyana/` and
    `/job-listing/find-your-next-job-in-guyana/` — and reported **30 flyers**
    where there are **18**. A plausible number, and the shape could not tell
    them apart. `category-` and `job_listing_region-` are facets and hold
    neither.
    """
    return MEMBER_KIND.get(member.rsplit("/", 1)[-1])


def shape_of(url):
    """The STRUCTURAL reading alone: `"job"`, `"flat"` or `None`.

    `"flat"` is deliberately not called `"flyer"`: a flat slug is a flyer OR
    an ordinary page, and **nothing in the address distinguishes them**. Only
    the member does, which is why the sitemap walk never calls this to decide
    a kind.
    """
    if JOB_RE.match(url):
        return "job"
    if "/wp-content/" in url or "/job/" in url or url == BASE + "/":
        return None
    return "flat" if FLYER_RE.match(url) else None


def parse_ad(url, body):
    """`(record, notes)` from one served page — **no network at all.**

    A plugin entry yields everything from its `JobPosting`; a flyer yields
    its title and says IN THE RECORD that its text is in the image, because
    an empty `description` and a description that does not exist read the
    same downstream.
    """
    notes = []
    sh = shape_of(url)
    if sh is None:
        raise ShapeMoved(f"{url}: neither {BASE}/job/<slug>/ nor {BASE}/<slug>/")
    k = "job" if sh == "job" else "flyer"
    t = TITLE_RE.search(body)
    titre = text(t.group(1)) if t else None
    if titre:
        # the site appends « - guyanajobs.net » to every title
        titre = re.sub(r"\s*-\s*guyanajobs\.net\s*$", "", titre)
    slug = (JOB_RE.match(url) or FLYER_RE.match(url)).group(1)
    out = {
        "source": "guyanajobs", "country": COUNTRY,
        "ledger_id": f"guyanajobs:{slug}", "id": slug, "url": url,
        "kind": k, "title": titre, "language": "en",
    }
    if k == "job":
        found = postings(body)
        if not found:
            why = absent_reason(body)
            if getattr(why, "our_fault", False):
                raise ShapeMoved(
                    f"{url}: {why} **The page announces a JobPosting and this "
                    f"read none.**")
            notes.append(f"a plugin entry with NO JobPosting: {why}. The three "
                         f"measured on 2026-11-09 all carried one, so this is a "
                         f"change in the board and not an empty vacancy.")
            out["text_in_image"] = None
            return out, notes
        d = found[0]
        org = d.get("hiringOrganization") or {}
        loc = d.get("jobLocation")
        if isinstance(loc, list):
            loc = loc[0] if loc else {}
        addr = (loc or {}).get("address") if isinstance(loc, dict) else None
        if isinstance(addr, dict):
            region = text(addr.get("addressRegion")) or text(addr.get("addressLocality"))
        else:
            region = text(addr) if addr else None
        et = d.get("employmentType")
        out.update({
            "title": text(d.get("title")) or titre,
            "employer": org.get("name") if isinstance(org, dict) else None,
            "region": region or None,
            "posted": d.get("datePosted"),
            "valid_through": d.get("validThrough"),
            "employment_type": ", ".join(et) if isinstance(et, list) else et,
            "direct_apply": d.get("directApply"),
            "description": text(str(d.get("description") or ""))[:20000] or None,
            # a plugin entry carries its text; the flag exists so the two
            # populations are distinguishable without inspecting `kind`
            "text_in_image": False,
        })
        return out, notes
    # a flyer: measured to carry no JobPosting, and its text is in the image
    why = absent_reason(body)
    out.update({
        "employer": None, "region": None, "posted": None, "valid_through": None,
        "employment_type": None, "direct_apply": None, "description": None,
        "text_in_image": True,
        # a flat slug is a flyer OR an ordinary page and the ADDRESS cannot
        # tell them apart -- only the member of the index can, and a single
        # URL given by hand carries no member
        "kind_from_shape_only": True,
        "why_no_text": (f"a flyer post: {why}. **The vacancy text is inside the "
                        f"image** — 18 of these were measured on 2026-11-09 and "
                        f"none carried a JobPosting. This adapter does not read "
                        f"images, so the title and the address are all it can "
                        f"honestly give."),
    })
    notes.append(out["why_no_text"])
    return out, notes


def cmd_sitemap(a):
    code, xml = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}", EXIT_PARTIAL)
    membres = [u for u, _ in entries(xml)] or \
              [m.group(1).strip() for m in FIRST_LOC_RE.finditer(xml)]
    membres = [u for u in membres if u.endswith(".xml")]
    if not membres:
        die(empty_first_page("guyanajobs", xml, "<loc>", where=INDEX), EXIT_PARTIAL)
    rows, seen, par, illisibles = [], set(), {}, []
    for m in membres:
        mcode, mxml = get(m)
        if mcode != 200:
            illisibles.append(m)
            note(f"{m}: HTTP {mcode} — not read, so the counts below are a FLOOR.")
            continue
        got = entries(mxml)
        k = kind_from_member(m)
        gardes = 0
        for u, lm in got:
            # the kind is the MEMBER's; the shape only says the address is one
            if k is None or shape_of(u) is None:
                continue
            if k == "job" and shape_of(u) != "job":
                continue
            if k == "flyer" and shape_of(u) != "flat":
                continue
            gardes += 1
            slug = (JOB_RE.match(u) or FLYER_RE.match(u)).group(1)
            if (k, slug) in seen:
                continue
            seen.add((k, slug))
            rows.append({"source": "guyanajobs", "country": COUNTRY,
                         "ledger_id": f"guyanajobs:{slug}", "id": slug,
                         "url": u, "kind": k, "lastmod": lm})
        par[m.rsplit("/", 1)[-1]] = (len(got), k or "ni l un ni l autre", gardes)
    if not rows:
        die(f"{INDEX}: {len(membres)} member(s) and not one address of either shape "
            f"— they moved. **Nothing here says the board is empty.**", EXIT_PARTIAL)
    gardees = [r for r in rows if not a.kind or r["kind"] == a.kind]
    for r in (gardees[:a.limit] if a.limit else gardees):
        print(json.dumps(r, ensure_ascii=False))
    note("per member, as `<url>` blocks and NEVER `<loc>`, and the kind is the "
         "MEMBER's and never the shape's: "
         + " · ".join(f"{nom} {u} url → holds {k}, kept {g}"
                      for nom, (u, k, g) in par.items()))
    nj = sum(1 for r in rows if r["kind"] == "job")
    nf = sum(1 for r in rows if r["kind"] == "flyer")
    note(f"**{nj} plugin entry(ies) and {nf} flyer(s)**"
         + (f"; {len(gardees)} printed under --kind {a.kind}" if a.kind else "")
         + (f" ({a.limit} under --limit)" if a.limit else "") + ".")
    if illisibles:
        note(f"{len(illisibles)} member(s) unread, so this is a FLOOR: "
             + ", ".join(illisibles))
    note("**The two are not the same kind of object.** A plugin entry carries a full "
         "`JobPosting` (4 035 characters of description on the one measured); a flyer "
         "carries NO JobPosting and its vacancy text is inside the image, which this "
         "adapter does not read. Counting `<loc>` instead of `<url>` would report 51 "
         "here instead of 21, the excess being `<image:loc>`. No count is stated "
         "anywhere on the site, and the `X-WP-Total` that #705 proposed is a response "
         "HEADER that `bin/fetch-body.py` does not record — so there is no second "
         "source for these figures.")


def cmd_ad(a):
    url = a.url.strip()
    if shape_of(url) is None:
        die(f"{url}: not a vacancy address — expected {BASE}/job/<slug>/ (plugin "
            f"entry) or {BASE}/<slug>/ (flyer)")
    code, body = get(url)
    if code == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}. **A readable body is not an answer — the code "
            f"decides.**")
    try:
        out, notes = parse_ad(url, body)
    except ShapeMoved as e:
        die(str(e), EXIT_PARTIAL)
    print(json.dumps(out, ensure_ascii=False))
    for n in notes:
        note(n)


def main():
    p = argparse.ArgumentParser(
        description="GuyanaJobs.net — the plugin's vacancies and the flyer posts, "
                    "which are two different kinds of object.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="both populations from the DECLARED index, "
                                       "labelled by kind")
    s.add_argument("--limit", type=int)
    s.add_argument("--kind", choices=("job", "flyer"))
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one vacancy; a plugin entry gives everything, a "
                                  "flyer gives its title and says why")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
