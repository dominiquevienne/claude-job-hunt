#!/usr/bin/env python3
"""Read one employer's board from Recruitee — a salary on more than half the
ads, and a country field written in the tenant's own language.

Recruitee is a European ATS (Dutch, now part of Tellent) used across the
Netherlands, Belgium, Germany, Poland and beyond. Each tenant publishes its
whole board as public JSON:

  GET https://<tenant>.recruitee.com/api/offers/   → every published offer
  https://<tenant>.recruitee.com/o/<slug>          → the ad, for a human

**No browser, no account, no key.** One request returns the employer's entire
board with descriptions — 145 offers in one 454 KB response on the largest
tenant measured. `robots.txt` is two lines and closes only `/v/`; the API path
is not disallowed and no crawler or AI agent is named.

Measured on **238 offers across six tenants** on 2026-09-01.

IT PAYS BETTER THAN MOST BOARDS HERE, AND THE UNIT IS THE TRAP. `salary` is an
object on **238 of 238** — so a presence check reports full coverage, the shape
`platsbanken.md` and `turijobs.md` both punish — but unlike those two it is
often real: **133 of 238 carry an actual figure**, which is better than every
national board in this repository except SwissDevJobs.

    "salary": {"min": "2990", "max": "3992", "period": "month", "currency": "EUR"}

**`period` is `month` on 124 of the 133, `hour` on 6 and `year` on 1**, and two
carry figures with no period at all. A monthly Dutch salary read as an annual
one is wrong by a factor of twelve — the same class of error as `join.md`'s
minor units and `arbeitsagentur.md`'s hourly rates. The period is emitted
beside every figure and never assumed.

THE COUNTRY IS WRITTEN IN THE TENANT'S LANGUAGE, AND THE VALUES MIX. Across one
sweep of six tenants:

    Nederland 231 · Frankrijk 2 · Duitsland 2 · Switzerland 1 ·
    Oostenrijk 1 · Denemarken 1

Five Dutch names and one English one, in the same result set. A filter written
`country == "Germany"` matches nothing, and `country == "Netherlands"` matches
nothing either. **`country_code` is on 238 of 238 and is the only reliable
one**; the localised string is carried beside it as `country_label` so nobody
mistakes it for a key.

REMOTE, HYBRID AND ON-SITE ARE THREE BOOLEANS AND THEY OVERLAP.

    on_site only            120
    hybrid only              67
    hybrid AND on_site       49
    remote AND on_site        1
    remote AND hybrid AND on_site   1

They are not an enum and cannot be collapsed into one. Reading `remote` alone
misses the 49 that are hybrid-and-on-site; treating them as mutually exclusive
misclassifies 51 of 238. All three are emitted, plus a `work_model` list, and
never a single value.

Usage:
  recruitee.py jobs --tenant gmk
  recruitee.py jobs --tenant ballastnedam --country-code NL
  recruitee.py tenants --country NL      (finds tenants through HiringCafe)

Output: one JSON object per line.
"""

import argparse
import collections
import html as html_mod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _child import run as child_run
from _decode import decode_body
from _robots import allowed as robots_allowed

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
TENANT_RE = re.compile(r"https?://([a-z0-9][a-z0-9-]*)\.recruitee\.com", re.I)


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



def note(msg):
    print(f"[recruitee] {msg}", file=sys.stderr)


def host(tenant):
    if "." in tenant:
        h = re.sub(r"^https?://", "", tenant).split("/")[0]
        m = TENANT_RE.match("https://" + h)
        return m.group(1) if m else h.split(".")[0]
    return tenant


def api(tenant, retries=2):
    url = f"https://{host(tenant)}.recruitee.com/api/offers/"
    _robots_gate(url, "recruitee")
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(decode_body(r.read(), r.headers)[0]), url
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                die(f"{url} answered 404. Recruitee returns JSON "
                    '{"error":"Not Found"} for a tenant that does not exist, '
                    "so this is a wrong tenant rather than an employer with "
                    "nothing open. There is no tenant directory — see "
                    "`recruitee.py tenants`.")
            if attempt == retries:
                die(f"{url}: HTTP {exc.code}")
            time.sleep(1.5 * (attempt + 1))
        except (urllib.error.URLError, OSError) as exc:
            if attempt == retries:
                die(f"{url}: {exc}")
            time.sleep(1.5 * (attempt + 1))
    return {}, url


def text_of(raw):
    if not isinstance(raw, str):
        return None
    return WS_RE.sub(" ", TAG_RE.sub(" ", html_mod.unescape(raw))).strip() or None


def money(s):
    """A figure and its period, or nothing — and never a figure alone.

    `period` is `month` on 124 of the 133 offers that state an amount. A Dutch
    monthly salary read as annual is wrong by twelve.
    """
    s = s or {}
    lo, hi = s.get("min") or None, s.get("max") or None
    if not (lo or hi):
        return None, None, None, None
    def num(v):
        try:
            return float(str(v).replace(",", "."))
        except (TypeError, ValueError):
            return None
    return num(lo), num(hi), s.get("period"), s.get("currency")


def work_model(o):
    """Three independent booleans that overlap — never one value."""
    out = [k for k in ("remote", "hybrid", "on_site") if o.get(k)]
    return out or None


def card(tenant, o):
    lo, hi, period, currency = money(o.get("salary"))
    locs = o.get("locations") or []
    return {
        "id": o.get("id"),
        "ledger_id": "recruitee:{}:{}".format(host(tenant), o.get("id")),
        "url": o.get("careers_url"),
        "apply_url": o.get("careers_apply_url"),
        "reference": o.get("guid"),
        "title": o.get("title"),
        "company": o.get("company_name"),
        "tenant": host(tenant),
        "department": o.get("department"),
        "location_text": o.get("location"),
        "city": o.get("city"),
        "region": o.get("state_name"),
        # `country` is localised per tenant — Nederland, Duitsland,
        # Switzerland in one sweep. Only the code is a key.
        "country_code": o.get("country_code"),
        "country_label": o.get("country"),
        "postcode": o.get("postal_code"),
        "locations_count": len(locs) or 1,
        # Three overlapping booleans, not an enum. See the module docstring.
        "remote": bool(o.get("remote")),
        "hybrid": bool(o.get("hybrid")),
        "on_site": bool(o.get("on_site")),
        "work_model": work_model(o),
        "employment_type": o.get("employment_type_code"),
        "experience": o.get("experience_code"),
        "education": o.get("education_code"),
        "category": o.get("category_code"),
        "min_hours_per_week": o.get("min_hours_per_week") or o.get("min_hours"),
        "max_hours_per_week": o.get("max_hours_per_week") or o.get("max_hours"),
        "salary_min": lo,
        "salary_max": hi,
        # Emitted beside the figures, always. month on 124 of 133.
        "salary_period": period,
        "salary_currency": currency,
        "published": o.get("published_at"),
        "updated": o.get("updated_at"),
        # Present in the payload and set on 0 of 238 measured.
        "closes": o.get("close_at"),
        # `published` on 238 of 238 — this endpoint serves nothing else, so
        # the field distinguishes nothing.
        "status": o.get("status"),
        "tags": o.get("tags") or None,
        "description": text_of(o.get("description")),
        # A separate field from the description, and empty on 60 of 238.
        "requirements": text_of(o.get("requirements")),
    }


def cmd_jobs(a):
    data, url = api(a.tenant)
    offers = data.get("offers")
    if offers is None:
        die(f"{url} returned no `offers` key. That is the only container in "
            "this payload, so its absence is a read failure rather than an "
            "employer with nothing open.")
    note(f"{len(offers)} published offers — {url}")
    if not offers:
        note("a real zero: the endpoint answered with an empty offers list, "
             "which is what an employer with nothing open looks like.")
        return
    kept = 0
    sal = collections.Counter()
    periods = collections.Counter()
    countries = collections.Counter()
    models = collections.Counter()
    for o in offers:
        c = card(a.tenant, o)
        if a.country_code and (c["country_code"] or "").upper() != \
                a.country_code.upper():
            continue
        if a.city and a.city.lower() not in (c["city"] or "").lower():
            continue
        has_figure = bool(c["salary_min"] or c["salary_max"])
        sal["figure" if has_figure else "none"] += 1
        # Count the period only where there is an amount to attach it to: a
        # period on an offer with no figure describes nothing, and counting
        # both together reports more units than salaries.
        if has_figure and c["salary_period"]:
            periods[c["salary_period"]] += 1
        elif c["salary_period"]:
            periods["(period, no figure)"] += 1
        countries[c["country_code"]] += 1
        models[tuple(c["work_model"] or ())] += 1
        print(json.dumps(c, ensure_ascii=False))
        kept += 1
    note(f"{kept} returned of {len(offers)}")
    note(f"salary: {sal['figure']} of {kept} state a figure — and the period "
         f"is {dict(periods)}. A monthly figure read as annual is wrong by "
         "twelve; salary_period is on every card.")
    if len(countries) > 1:
        note(f"country codes seen: {dict(countries)}. The `country` label is "
             "written in the tenant's own language — Nederland, Duitsland, "
             "Switzerland in one sweep — so filter on country_code.")
    overlap = sum(v for k, v in models.items() if len(k) > 1)
    if overlap:
        note(f"{overlap} of {kept} set more than one of remote/hybrid/on_site. "
             "They are three independent booleans, not an enum: work_model "
             "carries the list.")


def cmd_tenants(a):
    """Find tenants the way this adapter's own tenants were found.

    Recruitee publishes no directory and no cross-tenant search. HiringCafe
    indexes some Recruitee ads and records the apply URL, so its cards are a
    source of real tenant names — which is how the six measured for this
    adapter were located. It is a hint, not a census.
    """
    root = a.plugin_root or "."
    cmd = [sys.executable, f"{root}/skills/job-scan/scripts/hiringcafe.py",
           "search", "--country", a.country, "--pages", str(a.pages)]
    # **This read `.stdout` and nothing else.** `subprocess.run` does not
    # raise on a non-zero exit, so a child that refused, crashed or was never
    # found produced an empty string here — and the loop below counted it into
    # a tenant list that was then printed as a measurement. `pinpoint.py` had
    # the check and this file did not; both use one helper now. Issue #123.
    out = child_run(cmd, die, "hiringcafe.py")
    seen = collections.Counter()
    for line in out.splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        for k in ("apply_url", "url", "job_url", "source_url"):
            v = d.get(k)
            if isinstance(v, str):
                m = TENANT_RE.match(v)
                if m:
                    seen[m.group(1).lower()] += 1
                    break
    for t, n in seen.most_common():
        print(json.dumps({"tenant": t, "ads_seen_on_hiringcafe": n,
                          "api": f"https://{t}.recruitee.com/api/offers/"},
                         ensure_ascii=False))
    note(f"{len(seen)} tenants seen in HiringCafe's {a.country} cards. **This "
         "is a hint, not a directory**: HiringCafe indexes a fraction of "
         "Recruitee, so an employer missing here is not an employer without "
         "a board. Ask the user for the careers URL when they have one.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("jobs", help="one employer's whole board")
    c.add_argument("--tenant", required=True,
                   help="tenant name or careers hostname — `gmk` or "
                        "`gmk.recruitee.com`")
    c.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="keep one country. **Filter on the code, never on "
                        "the country label**")
    c.add_argument("--city")
    c.set_defaults(func=cmd_jobs)

    c = sub.add_parser("tenants",
                       help="tenant names seen in HiringCafe's cards — a "
                            "hint, not a directory")
    c.add_argument("--country", required=True, metavar="ISO2")
    c.add_argument("--pages", type=int, default=3)
    c.add_argument("--plugin-root", dest="plugin_root",
                   help="repository root; defaults to the working directory")
    c.set_defaults(func=cmd_tenants)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
