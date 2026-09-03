#!/usr/bin/env python3
"""Fetch job ads from a Flatchr careers site — a French ATS for SMEs and ETI.

Flatchr is the other French ATS this plugin sweeps, alongside `taleez.md`. Same
shape as `umantis.md`: one employer per careers site, **no tenant directory**,
and the user supplies the URL.

Its careers sites are Next.js, and the whole job list — **descriptions
included** — is server-rendered into the page's `__NEXT_DATA__` payload. So one
request per employer returns everything, with no per-ad read at all. That is
the difference from Taleez, whose listing carries no description.

  GET https://<tenant>.flatchr.io/                     ← same payload
  GET https://careers.flatchr.io/fr/company/<tenant>   ← as this one
  GET https://careers.flatchr.io/vacancy/<slug>/       ← one ad, same shape

Usage:
  flatchr.py jobs --tenant pokawa
  flatchr.py jobs --url https://pokawa.flatchr.io/
  flatchr.py ad <slug>

Output: one JSON object per line (jobs), or one JSON object (ad).
"""

import argparse
import gzip
import html as html_mod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

TENANT_URL = "https://{}.flatchr.io/"
AD_URL = "https://careers.flatchr.io/vacancy/{}/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

TENANT_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")
HOST_RE = re.compile(r"https?://([a-z0-9-]+)\.flatchr\.io", re.I)
COMPANY_PATH_RE = re.compile(r"/company/([a-z0-9-]+)", re.I)
NEXT_RE = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)

# `mensuality` is the period the `salary` number is expressed in. A figure
# without it is meaningless: 12.31 an hour, 2700 a month and 45000 a year all
# appear on the same board.
PERIOD = {"h": "HOUR", "m": "MONTH", "y": "YEAR"}


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _robots_gate(url, tag, exit_code=7):
    """Ask per tenant and per path before fetching. Issues #100 and #101.

    **On a tenant platform the rules file is the employer's, not the vendor's**
    — two Teamtailor tenants declared opposite things while this repository
    recorded the permissive one as platform policy (#73). `icims` and `taleez`
    have asked per tenant for weeks; this adapter did not.

    **And it asks about the path.** `verdict()` answers *is this host closed in
    one block*; a careers site that refuses its ad path while leaving its root
    open passes that check and refuses every advertisement.

    A refusal **stops the command** with exit 7 and the module's own words —
    nothing here decides what a refusal means.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return None
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        print(f"[{tag}] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts, and a platform that "
              f"has been renamed reaches us this way before it reaches us as "
              f"a rename.", file=sys.stderr)
    return a



def fetch(url):
    _robots_gate(url, "flatchr")
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
            return body.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            die("nothing at that URL (HTTP 404). For a tenant, check the slug "
                "against the careers URL the user gave — there is no tenant "
                "directory, so a wrong slug is the likeliest cause. For an ad, "
                "record it as discarded.", code=3)
        die(f"Flatchr returned HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach Flatchr: {e}")


def payload(page, what):
    m = NEXT_RE.search(page)
    if not m:
        die(f"no __NEXT_DATA__ block on the {what} page. Either the site was "
            "rebuilt on something other than Next.js, or the page is an error "
            "shell — report it with board-request rather than guessing at "
            "selectors.", code=3)
    try:
        return json.loads(m.group(1))["props"]
    except Exception as e:  # noqa: BLE001
        die(f"could not read the {what} payload: {e}")


def tenant_of(a):
    if a.url:
        # The /company/<slug> path is checked FIRST: careers.flatchr.io serves
        # every tenant, so reading the host there yields "careers", which is
        # not a tenant and fetches a page with no payload at all.
        m = COMPANY_PATH_RE.search(a.url)
        if not m:
            m = HOST_RE.search(a.url)
            if m and m.group(1).lower() in ("careers", "www", "api"):
                die(f"{a.url!r} points at a shared Flatchr host with no "
                    "tenant in it. Give either https://<tenant>.flatchr.io/ "
                    "or a .../fr/company/<tenant> URL.")
        if not m:
            die(f"could not read a tenant out of {a.url!r}. It should look "
                "like https://<tenant>.flatchr.io/ or "
                ".../fr/company/<tenant>. A careers site on the employer's "
                "own domain does not expose the tenant — ask the user to open "
                "a job and read the careers.flatchr.io address off it.")
        return m.group(1).lower()
    if not a.tenant:
        die("give --tenant or --url. **There is no tenant directory** — the "
            "sitemap at careers.flatchr.io belongs to the marketing site and "
            "carries no vacancies at all, so an employer cannot be resolved "
            "from a name. The careers URL comes from the user, as for umantis "
            "and Taleez.")
    if not TENANT_RE.match(a.tenant):
        die(f"{a.tenant!r} is not a tenant slug. It is the first label of the "
            "host: `pokawa` in pokawa.flatchr.io.")
    return a.tenant.lower()


def to_text(markup):
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", markup or "")
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", txt)
    txt = re.sub(r"(?i)<li[^>]*>", "- ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html_mod.unescape(txt).replace(" ", " ")
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", txt).strip()


def card(v):
    addr = v.get("address") or {}
    company = v.get("company") or {}
    slug = v.get("slug")
    # The employer chose whether these are public. Publishing a figure they
    # hid would put something on the user's screen the ad does not show.
    show_salary = v.get("show_salary")
    show_address = v.get("show_address")
    skills = v.get("skills") or ""
    return {
        "id": v.get("id"),
        "ledger_id": f"flatchr:{v.get('id')}",
        "url": AD_URL.format(slug) if slug else None,
        "slug": slug,
        "vacancy_id": v.get("vacancy_id"),
        "reference": v.get("reference"),
        "title": v.get("title"),
        # A Flatchr careers site belongs to one employer, so this is the
        # workplace, never an intermediary.
        "company": company.get("name"),
        "city": addr.get("locality") if show_address else None,
        "location": v.get("addressFormatted") if show_address else None,
        "lat": addr.get("location_lat") if show_address else None,
        "lon": addr.get("location_lng") if show_address else None,
        "contract": v.get("contract_type"),
        "metier": v.get("metier"),
        "activity": v.get("activity"),
        "education_level": v.get("education_level"),
        "experience_years": v.get("experience"),
        "remote": v.get("remote"),
        "worker_status": v.get("worker_status"),
        "salary_min": v.get("salary") if show_salary else None,
        "salary_max": v.get("salary_max") if show_salary else None,
        "salary_currency": v.get("currency") if show_salary else None,
        "salary_period": PERIOD.get(v.get("mensuality")) if show_salary
        else None,
        "salary_public": show_salary,
        "code_rome": v.get("code_rome"),
        "skills": [s for s in skills.split(";") if s],
        "language": v.get("language"),
        "published": v.get("created_at"),
        "updated": v.get("updated_at"),
        "start_date": v.get("start_date"),
        "end_date": v.get("end_date"),
        # Screening questions the employer will ask. `cover-letter` never
        # answers one by guessing, so knowing they exist is worth carrying.
        "screening_questions": [q.get("text") for q in (v.get("questions") or [])
                                if q.get("text")],
        "description": to_text(v.get("description")),
        "mission": to_text(v.get("mission")),
        "profile": to_text(v.get("profile")),
    }


def cmd_jobs(a):
    tenant = tenant_of(a)
    props = payload(fetch(TENANT_URL.format(tenant)), "careers")
    items = ((props.get("data") or {}).get("items")) or []
    name = ((props.get("config") or {}).get("company") or {}).get("name")
    print(f"[flatchr] {name or tenant}: {len(items)} ads", file=sys.stderr)
    if not items:
        print("[flatchr] the tenant is real and has nothing open — that is a "
              "zero, not a failure. A wrong slug is a 404 instead.",
              file=sys.stderr)
    rows = 0
    for it in items:
        # Each item is a *diffusion* wrapper — id, status, dates and little
        # else. The ad is the nested `vacancy`, and reading the wrapper
        # instead yields a board of empty rows rather than an error.
        v = it.get("vacancy")
        if not v:
            print(f"[flatchr] item {it.get('id')} carries no `vacancy` object "
                  "— skipped, and worth reporting if it repeats",
                  file=sys.stderr)
            continue
        print(json.dumps(card(v), ensure_ascii=False))
        rows += 1
    print(f"[flatchr] {rows} cards returned", file=sys.stderr)


def cmd_ad(a):
    props = payload(fetch(AD_URL.format(a.slug)), "vacancy")
    v = (props.get("spontaneousApply")
         or ((props.get("data") or {}).get("spontaneousV")))
    if not v or v.get("slug") != a.slug:
        items = ((props.get("data") or {}).get("items")) or []
        v = next((i.get("vacancy") for i in items
                  if (i.get("vacancy") or {}).get("slug") == a.slug), v)
    if not v:
        die(f"could not find the ad {a.slug!r} in that page's payload.",
            code=3)
    print(json.dumps(card(v), ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    j = sub.add_parser("jobs", help="every ad on one tenant, in one request")
    j.add_argument("--tenant", help="the host's first label")
    j.add_argument("--url", help="the careers URL, if that is what you have")
    j.set_defaults(func=cmd_jobs)

    d = sub.add_parser("ad", help="read one ad by slug")
    d.add_argument("slug")
    d.set_defaults(func=cmd_ad)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
