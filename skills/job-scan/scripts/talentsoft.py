#!/usr/bin/env python3
"""Fetch job ads from a Cegid Talentsoft careers site.

Talentsoft (Cegid) runs the careers sites of large French employers and public
bodies — ministries, airports, energy, publishing. It is the fifth and last of
the French ATS family here, after `taleez.md`, `flatchr.md`, `softy.md` and
`digitalrecruiters.md`.

Careers sites live at `https://<tenant>.talent-soft.com/`, where the tenant
label usually ends in `-recrute` or `-career`. Everything is **server-rendered
ASP.NET** — no JSON anywhere, and no JSON-LD either — so this parses HTML.

What makes that tolerable: the ad pages carry Talentsoft's **field model as
element ids** (`fldjobdescription_jobtitle`, `fldlocation_joblocation`, …).
Those come from the platform, not from a theme, so they hold across tenants and
across restyling — unlike the utility classes on `softy.md` and `cadremploi.md`.

Usage:
  talentsoft.py jobs --tenant businessfrance-recrute
  talentsoft.py jobs --tenant businessfrance-recrute --with-detail
  talentsoft.py ad --tenant businessfrance-recrute --path /offre-de-emploi/...aspx

Output: one JSON object per line (jobs), or one JSON object (ad).
"""

import argparse
import gzip
import html as html_mod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _robots import allowed as robots_allowed

BASE = "https://{}.talent-soft.com"
LIST = "/offre-de-emploi/liste-offres.aspx?page={}&LCID={}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

TENANT_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")
HOST_RE = re.compile(r"https?://([a-z0-9-]+)\.talent-soft\.com", re.I)

# One row per ad on the listing. `offerlist-item` is the semantic half of the
# pair; the ts- prefixed one is the theme's.
ROW_RE = re.compile(r'class="ts-offer-list-item offerlist-item')
LINK_RE = re.compile(r"href=\"(/offre-de-emploi/[^\"]+\.aspx)\"")
# The id is the numeric suffix of the ad's own path.
AD_ID_RE = re.compile(r"_(\d+)\.aspx")
COUNT_RE = re.compile(r"\((\d+)\s*offres?", re.I)
REF_RE = re.compile(r"R[ée]f\.?\s*:?\s*([A-Za-z0-9][\w./-]*)")
DATE_RE = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b")
CONTRACT_RE = re.compile(
    r"\b(CDI|CDD|Alternance|Stage|Int[ée]rim|Apprentissage|VIE|"
    r"Contrat de professionnalisation)\b", re.I)
# The row's fields are unlabelled fragments, and **what they are varies by
# tenant**. Business France: title, "Réf.", date, contract (CDI), address.
# place-ep-recrute: title, "Réf.", date, a public-service *status* phrase,
# address, employer. Taking "whatever is left" as the location put
# "Emploi ouvert aux titulaires et aux contractuels" in the location field —
# a well-formed, entirely wrong answer.
#
# So: label only what can be identified with confidence, and hand the rest
# back as `other_fields` rather than guessing at its meaning. A field this
# adapter cannot name is better as an unnamed string than as a wrong label.
JUNK_RE = re.compile(r"^(class=|title=|onclick=|<li|\s*$)")
# A French postcode, but not an id in brackets: this tenant carries a status
# field reading "Vacant (45823)", and a bare five-digit rule made that the
# job's location — a well-formed, entirely wrong answer, which is the exact
# failure this parser is written to avoid.
POSTCODE_RE = re.compile(r"(?<![(\d])\d{5}(?![)\d])")

# A row carries four or five fields — reference, date, contract or status,
# address, sometimes the employing body. The last block on a page also
# contains the whole footer, in `<li>` elements indistinguishable from the
# row's own. Taking a bounded number keeps the real fields, which come first,
# and drops the page furniture, which does not.
MAX_FIELDS = 8

# The ad page's fields, keyed by element id. These are Talentsoft's own field
# names, so they are the stable part of the page.
AD_FIELDS = {
    "fldjobdescription_jobtitle": "title",
    "fldjobdescription_contract": "contract",
    "fldjobdescription_professionalcategory": "professional_category",
    "fldjobdescription_customcodetablevalue2": "job_family",
    "fldlocation_location_geographicalareacollection": "geographical_area",
    "fldapplicantcriteria_educationlevel": "education_level",
    "fldapplicantcriteria_experiencelevel": "experience_level",
}
SECTIONS = {"JobDescription": "description",
            "Location": "location_block",
            "ApplicantCriteria": "applicant_criteria"}


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def check_robots(url):
    """Per tenant, and per path — because on this platform both vary.

    **A Talentsoft careers site is the employer's host**, so the rules file is
    the employer's decision and not the vendor's: two tenants of one platform
    have already been found declaring opposite things (#73). `icims` and
    `taleez` have asked per tenant for weeks; these seven did not. Issue #100.

    **And it asks about the path, not only the host.** `verdict()` answers *is
    this host closed in one block*; a careers site that refuses `/offre-de-`
    to `*` while leaving its root open would pass that and refuse every ad.
    Issue #101.

    A refusal **stops the command** with exit 7 and the module's own words.
    """
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", 7)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        print(f"[talentsoft] robots.txt for {a['requested_host']} was read "
              f"from {a['host']} — this platform has been rebranded to Cegid "
              f"and its own domain redirects there, so the file governing a "
              f"tenant is worth checking rather than assuming.",
              file=sys.stderr)
    return a


def fetch(url):
    check_robots(url)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Accept-Encoding": "gzip",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
            if r.headers.get("Content-Encoding", "").lower() == "gzip":
                body = gzip.decompress(body)
            return decode_body(body, r.headers)[0]
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            die(f"nothing at that URL (HTTP {e.code}). For a tenant, check the "
                "label against the careers URL the user gave — there is no "
                "directory. For an ad, record it as discarded.", code=3)
        die(f"Talentsoft returned HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        # A tenant that does not exist has no DNS record at all, so the
        # failure arrives as a resolver error rather than a 404. Say what it
        # means instead of passing the socket message through.
        if "nodename" in str(e) or "Name or service not known" in str(e):
            die("that careers host does not resolve — the tenant label is "
                "wrong. It is the first label of the URL the user gave, and "
                "it usually ends in -recrute or -career. There is no "
                "directory to check it against.", code=3)
        die(f"could not reach Talentsoft: {e}")


def tenant_of(a):
    if a.url:
        m = HOST_RE.search(a.url)
        if not m:
            die(f"could not read a tenant out of {a.url!r}. It should look "
                "like https://<tenant>.talent-soft.com/ — the label usually "
                "ends in -recrute or -career.")
        return m.group(1).lower()
    if not a.tenant:
        die("give --tenant or --url: the careers host's first label, e.g. "
            "`businessfrance-recrute`. **There is no tenant directory** — the "
            "URL comes from the user, as for umantis and the other ATS here.")
    if not TENANT_RE.match(a.tenant):
        die(f"{a.tenant!r} is not a tenant label. It is the first label of "
            "the host: `businessfrance-recrute` in "
            "businessfrance-recrute.talent-soft.com.")
    return a.tenant.lower()


def strip_tags(markup, sep=" "):
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", markup or "")
    txt = re.sub(r"<[^>]+>", sep, txt)
    txt = html_mod.unescape(txt).replace(" ", " ")
    return re.sub(r"\s+", " ", txt).strip()


def to_text(markup):
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", markup or "")
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", txt)
    txt = re.sub(r"(?i)<li[^>]*>", "- ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html_mod.unescape(txt).replace(" ", " ")
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", txt).strip()


def rows(page):
    """One block per ad.

    The **last** block runs to the end of the document, so it also contains
    the sidebar filters, the pagination and the footer. Those are `<li>`
    elements too — the same shape as the row's own fields — so they cannot be
    cut by structure. They are bounded by count instead: see MAX_FIELDS.
    """
    starts = [m.start() for m in ROW_RE.finditer(page)]
    return [page[a:b] for a, b in zip(starts, starts[1:] + [len(page)])]


def card(block, tenant):
    m = LINK_RE.search(block)
    if not m:
        return None
    path = m.group(1)
    ident = (AD_ID_RE.search(path) or [None, None])[1] if AD_ID_RE.search(path)\
        else None
    flat = strip_tags(block, sep=" | ")
    # The row block starts inside the opening tag, so the first fragment of
    # `flat` is leftover attribute text, not the title. Take the title from
    # its own element instead.
    tm = re.search(r'class="ts-offer-list-item__title-link[^"]*"[^>]*>(.*?)</a>',
                   block, re.S)
    title = strip_tags(tm.group(1)) if tm else None
    ref = (REF_RE.search(flat) or [None, None])[1] if REF_RE.search(flat)\
        else None
    date = (DATE_RE.search(flat) or [None, None])[1] if DATE_RE.search(flat)\
        else None

    parts = [x.strip() for x in flat.split("|") if x.strip()]
    rest, location, contract, taken = [], None, None, 0
    for x in parts:
        if taken >= MAX_FIELDS:
            break
        if JUNK_RE.match(x) or x == title:
            continue
        taken += 1
        if REF_RE.search(x) or DATE_RE.fullmatch(x):
            continue
        if contract is None and CONTRACT_RE.fullmatch(x):
            contract = x
            continue
        # A French postcode is the one unambiguous marker of an address. It
        # misses postings abroad, which is why they fall through to
        # `other_fields` instead of being mislabelled as the location.
        if location is None and POSTCODE_RE.search(x):
            location = x
            continue
        rest.append(x)
    return {
        "id": ident,
        "ledger_id": f"talentsoft:{tenant}:{ident}",
        "url": BASE.format(tenant) + path,
        "path": path,
        "title": title,
        # The employer's own reference, e.g. "2026-1563" — not the ledger key.
        "reference": ref,
        "published": date,
        # Only when it matches known contract vocabulary. This tenant's
        # "Emploi ouvert aux titulaires et aux contractuels" is a status, not
        # a contract, and lands in `other_fields`.
        "contract": contract,
        # Set only from a fragment carrying a French postcode. A posting
        # abroad has no postcode and no location here — it is in
        # `other_fields`, unlabelled, rather than wrong.
        "location": location,
        # Everything this adapter will not name: a public-service status, the
        # employing body, a foreign place. Which of these appear depends on
        # the tenant, so they are carried in order and not interpreted.
        "other_fields": rest,
    }


def ad_detail(page):
    out = {}
    for fid, key in AD_FIELDS.items():
        m = re.search(r'id="' + fid + r'"[^>]*>(.*?)</', page, re.S)
        if m:
            v = strip_tags(m.group(1))
            if v:
                out[key] = v
    for name, key in SECTIONS.items():
        m = re.search(r'<h2[^>]*class="[^"]*' + name +
                      r'[^"]*"[^>]*>.*?</h2>(.*?)(?=<h2|\Z)', page, re.S)
        if m:
            t = to_text(m.group(1))
            if t:
                out[key] = t
    return out


def cmd_jobs(a):
    tenant = tenant_of(a)
    base = BASE.format(tenant)
    first = fetch(base + LIST.format(1, a.lcid))
    total = int((COUNT_RE.search(first) or [0, 0])[1]) if COUNT_RE.search(first)\
        else None
    print(f"[talentsoft] {tenant}: {total if total is not None else '?'} ads "
          "announced", file=sys.stderr)
    seen, out, page, html = set(), [], 1, first
    while True:
        got = [c for c in (card(b, tenant) for b in rows(html)) if c]
        fresh = [c for c in got if c["url"] not in seen]
        if not fresh:
            break
        for c in fresh:
            seen.add(c["url"])
            out.append(c)
        if total is not None and len(out) >= total:
            break
        page += 1
        if page > a.max_pages:
            print(f"[talentsoft] stopping at page {a.max_pages}; raise "
                  "--max-pages if the count says there is more",
                  file=sys.stderr)
            break
        time.sleep(a.delay)
        html = fetch(base + LIST.format(page, a.lcid))
    if total is not None and len(out) != total:
        print(f"[talentsoft] collected {len(out)} of {total} announced — this "
              "sweep is incomplete, not the size of the board", file=sys.stderr)
    for c in out:
        if a.with_detail:
            time.sleep(a.delay)
            c.update(ad_detail(fetch(c["url"])))
        print(json.dumps(c, ensure_ascii=False))
    print(f"[talentsoft] {len(out)} cards returned", file=sys.stderr)


def cmd_ad(a):
    tenant = tenant_of(a)
    if not a.path:
        die("give --path, the ad's path on the careers site "
            "(/offre-de-emploi/…aspx).")
    url = BASE.format(tenant) + a.path
    d = ad_detail(fetch(url))
    if not d:
        die(f"no Talentsoft fields found at {url}. Either the ad is gone, or "
            "the field ids changed — report it with board-request rather than "
            "guessing.", code=3)
    ident = (AD_ID_RE.search(a.path) or [None, None])[1]\
        if AD_ID_RE.search(a.path) else None
    print(json.dumps({"id": ident, "ledger_id": f"talentsoft:{tenant}:{ident}",
                      "url": url, **d}, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    j = sub.add_parser("jobs", help="every ad on one careers site")
    j.add_argument("--tenant")
    j.add_argument("--url")
    j.add_argument("--lcid", default="1036", help="locale id; 1036 is French")
    j.add_argument("--with-detail", action="store_true",
                   help="read each ad page for the description and the "
                        "candidate criteria — one request per ad")
    j.add_argument("--max-pages", type=int, default=50)
    j.add_argument("--delay", type=float, default=1.0)
    j.set_defaults(func=cmd_jobs)

    d = sub.add_parser("ad", help="read one ad by path")
    d.add_argument("--tenant")
    d.add_argument("--url")
    d.add_argument("--path")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
