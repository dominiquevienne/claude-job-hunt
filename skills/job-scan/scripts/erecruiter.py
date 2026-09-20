#!/usr/bin/env python3
"""eRecruiter (Poland's most used ATS — one tenant at a time): the employer's career site on `<tenant>.pracujunas.pl` (eRecruiter's Career Sites Builder) carries in its `__NEXT_DATA__` the feed it renders — `offers.erecruiter.pl/skk/company/<id>/offers.json?hash=<key>` — replayed as the page carries it; the feed is the board (no count stated, no page); the offer page on `skk.erecruiter.pl` for `ad`. Issue #471.

  erecruiter.py jobs --tenant <name> [--country-code ISO2]
  erecruiter.py ad --url "https://skk.erecruiter.pl/Offer.aspx?oid=<n>&ejoId=<n>&ejorId=<n>&comId=<n>"

THE TENANT is the subdomain of `pracujunas.pl` the employer's career
site lives on (`zabka`, `dkms`, `steico`, `hopi`, `viessmann`) — found by
the family's signature («powered by eRecruiter», `<tenant>.pracujunas.pl`),
never composed. The application form the issue named
(`system.erecruiter.pl/FormTemplates/RecruitmentForm.aspx?WebID=`) is
per job and carries no list; the list is the career site's feed.

THE ROUTE. The site is a Next.js page whose `__NEXT_DATA__.props.pageProps
.companyData` names the company (`companyName` = the numeric id,
`companyDisplayName`, `subDomainName`) and its `offersLink` — a feed URL
with a `hash`, **the tenant's public feed key printed in every visitor's
page** (the SparkHire shape): the adapter replays it as given and nothing
else. The feed answers `{"jobs": [...]}` — one item per offer AND region
(`jobOfferId` the offer, `jobOfferRegionId` the item; Żabka: 25 items, 18
offers, 2026-09-20); `page=`, `take=`, `skip=`, `offset=` are ignored
(measured), no count is stated: **the feed is the board**, `jobs` prints
its length and says so. Rules: `<tenant>.pracujunas.pl` publishes
Cloudflare's content-signal comments and no directive (open, `certain:
False`); `offers.erecruiter.pl` and `skk.erecruiter.pl` publish no rules
file (404). 2 s between requests are ours.

THE ITEM: url (the offer page on `skk.erecruiter.pl`), urlWithLayout,
title, publishDate, expiryDate, company, partnership, location (towns),
referencenumber, country {isoCode}, region {name}, departments,
additionalFields, branches, applicationLink (the form), companyDescription,
requirements, opportunities, notes, clause (the GDPR text), experience,
positionDescription, geolocations, compensationPackage {salaryRanges,
benefits}. The offer page: `p.offComp`, `h1`, `#divWorkplace`,
`#divRegionName`, sections `#div<Name>` with `h2` and `div.desc`.

WITHHELD: e-mail addresses and telephone numbers in the texts (the feed's
descriptions name a contact on some tenants); the GDPR clause (not
emitted — legal text, 3 KB per item); the application form never
touched; the coordinates of the workplace; `contacts_withheld` on every
record.
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
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD = "erecruiter"
SITE_DOMAIN = "pracujunas.pl"
FEED_HOST = "offers.erecruiter.pl"
AD_HOST = "skk.erecruiter.pl"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

TENANT_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", re.I)
NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)
FEED_PATH_RE = re.compile(r"^/skk/company/(\d+)/offers\.json$")
COMP_RE = re.compile(r'<p class="offComp">(.*?)</p>', re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
WORKPLACE_RE = re.compile(r'<div id="divWorkplace">.*?</span>(.*?)<br', re.S)
REGION_RE = re.compile(r'<div id="divRegionName">.*?</span>(.*?)<br', re.S)
SECTION_RE = re.compile(r'<div id="div([A-Za-z]+)">\s*<h2>\s*<span[^>]*>(.*?)</span>\s*</h2>\s*<div class="desc">(.*?)</div>\s*</div>', re.S)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{6,}\d(?!\w)")
_PACES = {}
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[erecruiter] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    """The tenant's site, the feed host and the offer host — nothing else."""
    parts = urllib.parse.urlsplit(url)
    host = parts.netloc.lower()
    if host not in (TENANT["host"], FEED_HOST, AD_HOST) or not host:
        die(f"{url}: not this run's eRecruiter host ({TENANT['host'] or 'no tenant named'}, {FEED_HOST}, {AD_HOST}) — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "application/json, text/html", "Accept-Language": "pl,en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", t)
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span|font)\b[^>]*>", "", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def tenant_of(arg):
    s = (arg or "").strip().lower()
    if "://" in s or "/" in s:
        s = urllib.parse.urlsplit(s if "://" in s else "https://" + s).netloc
    if s.endswith("." + SITE_DOMAIN):
        s = s[: -len("." + SITE_DOMAIN)]
    if not s or "." in s or not TENANT_RE.match(s) or s in ("www",):
        die(f"{arg!r}: a tenant is the subdomain of {SITE_DOMAIN} the employer's career site lives on (zabka, dkms), found by the family's signature, never composed")
    return f"{s}.{SITE_DOMAIN}"


def company_of(markup):
    """The page's `companyData` — the feed link it renders from, and the company's names."""
    m = NEXT_DATA_RE.search(markup or "")
    if not m:
        return None
    try:
        d = json.loads(m.group(1))
    except ValueError:
        return None
    cd = (((d.get("props") or {}).get("pageProps") or {}).get("companyData")) if isinstance(d, dict) else None
    return cd if isinstance(cd, dict) and cd.get("offersLink") else None


def row(it, host, company, stamp):
    country = (it.get("country") or {}).get("isoCode") if isinstance(it.get("country"), dict) else None
    region = (it.get("region") or {}).get("name") if isinstance(it.get("region"), dict) else None
    comp = it.get("compensationPackage") if isinstance(it.get("compensationPackage"), dict) else {}
    sections = {k: scrub(text(it.get(k))) for k in ("positionDescription", "requirements", "opportunities", "notes", "companyDescription", "experience") if it.get(k)}
    return {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{it.get('jobOfferRegionId')}", "id": str(it.get("jobOfferRegionId") or ""),
        "offer_id": str(it.get("jobOfferId") or ""), "url": it.get("url"),
        "title": it.get("title"), "company": (it.get("company") or company or "").strip() or None, "brand": it.get("partnership") or None,
        "place": it.get("location") or None, "region": region, "country": (country or "").upper() or stamp, "country_name": None,
        "departments": it.get("departments") or [], "reference": it.get("referencenumber") or None,
        "published": it.get("publishDate"), "closes": it.get("expiryDate"), "updated": it.get("lastModificationDate"),
        "salary_ranges": comp.get("salaryRanges") or [], "benefits": scrub(text(comp.get("benefits"))),
        "description": (sections.get("positionDescription") or "")[:20000] or None,
        "sections": {k: v for k, v in sections.items() if k != "positionDescription" and v},
        # applicationLink (the form), clause (the GDPR text) and geolocations are not emitted
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    TENANT["host"] = host
    url = f"https://{host}/"
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404 — no such career site", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    cd = company_of(body)
    if not cd:
        die(f"{url}: no `companyData.offersLink` in the page's __NEXT_DATA__ — not an eRecruiter career site, or its shape changed.", EXIT_PARTIAL)
    feed = cd["offersLink"]
    fp = urllib.parse.urlsplit(feed)
    if fp.netloc.lower() != FEED_HOST or not FEED_PATH_RE.match(fp.path) or "hash=" not in fp.query:
        die(f"{url}: the page's offersLink is {feed!r}, not the feed shape this adapter knows ({FEED_HOST}/skk/company/<id>/offers.json?hash=…).", EXIT_PARTIAL)
    st, body = request(feed)
    if st in (403, 429):
        die(f"{feed}: HTTP {st} — the operator answering directly; stopped.", EXIT_REFUSED)
    if st != 200:
        die(f"{feed}: HTTP {st}", EXIT_PARTIAL)
    try:
        j = json.loads(body)
    except ValueError:
        die(f"{feed}: not JSON ({len(body)} characters)", EXIT_PARTIAL)
    if not isinstance(j, dict) or not isinstance(j.get("jobs"), list):
        die(f"{feed}: no `jobs` list in the answer — not the feed's shape.", EXIT_PARTIAL)
    stamp = (a.country_code or "").strip().upper() or None
    seen, rows = set(), []
    for it in j["jobs"]:
        if not isinstance(it, dict) or it.get("jobOfferRegionId") is None or it["jobOfferRegionId"] in seen:
            continue
        seen.add(it["jobOfferRegionId"])
        rows.append(row(it, host, cd.get("companyDisplayName"), stamp))
    emitted = [r for r in rows if not stamp or r["country"] == stamp]
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    offers = len({r["offer_id"] for r in rows})
    who = (cd.get("companyDisplayName") or host).strip()
    if stamp:
        note(f"{th(len(emitted))} emitted for {stamp} of the {th(len(rows))} items ({th(offers)} offers) the feed carries for {who} — the feed is the board: no count is stated, no page follows; an item without a country is stamped {stamp}.")
    else:
        note(f"{th(len(rows))} emitted ({th(offers)} offers, an offer in several regions is several items) — the feed is the board for {who}: no count is stated anywhere and no page follows.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    q = {k.lower(): v[0] for k, v in urllib.parse.parse_qs(parts.query).items()}
    if parts.netloc.lower() != AD_HOST or parts.path.lower() != "/offer.aspx" or not q.get("oid", "").isdigit():
        die(f"{a.url!r}: not an eRecruiter offer address (https://{AD_HOST}/Offer.aspx?oid=<n>&ejoId=<n>&ejorId=<n>&comId=<n>)")
    keep = [(k, q[k.lower()]) for k in ("oid", "ejoId", "ejorId", "comId") if q.get(k.lower())]
    url = f"https://{AD_HOST}/Offer.aspx?" + urllib.parse.urlencode(keep)
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped.", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    h1 = H1_RE.search(body)
    secs = SECTION_RE.findall(body)
    if not h1 or not secs:
        die(f"{url}: no title or no section in the page — not an eRecruiter offer page, or the offer is gone.", EXIT_PARTIAL)
    sections = {text(lab) or name: scrub(text(desc)) for name, lab, desc in secs}
    first = next(iter(sections.values()), None)
    comp = COMP_RE.search(body)
    wp = WORKPLACE_RE.search(body)
    rg = REGION_RE.search(body)
    r = {
        "source": BOARD, "ledger_id": f"{BOARD}:com{q.get('comid', '')}:{q['oid']}", "id": q["oid"], "url": url,
        "title": text(h1.group(1)), "company": text(comp.group(1)) if comp else None,
        "place": text(wp.group(1)) if wp else None, "region": text(rg.group(1)) if rg else None,
        "description": (first or "")[:20000] or None, "sections": sections,
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="eRecruiter — one tenant's offers from the feed its career site renders (the feed is the board: no count stated) and the offer page; the form, the GDPR clause and the coordinates never emitted, texts scrubbed. Issue #471.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the career site's feed, two requests (the page for its feed link, the feed)")
    s.add_argument("--tenant", required=True, help="the subdomain of pracujunas.pl (zabka), the host, or the site's URL")
    s.add_argument("--country-code", help="keep the items whose country is this ISO2 (the feed states it; an item without one is stamped)")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one offer by its page on skk.erecruiter.pl; texts scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
