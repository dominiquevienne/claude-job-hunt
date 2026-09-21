#!/usr/bin/env python3
"""d.vinci — an ATS, one tenant at a time: the tenant's job list on `<tenant>.dvinci-easy.com/<lang>/jobs` carries every publication as JSON in the page (`var DvinciData = { "jobPublications": [...] }` — the list is the board, its length the count), and each ad on `/<lang>/jobs/<id>/<slug>` carries the same object for one publication plus a schema.org JobPosting; the addresses, coordinates and application routes never emitted. Issue #481.

  dvinci.py jobs --tenant fi-ts-karriere [--lang de] [--country-code DE]     the tenant's publications (1 request)
  dvinci.py jobs --tenant https://holzapfel-group.dvinci-easy.com/de/jobs
  dvinci.py ad --url https://fi-ts-karriere.dvinci-easy.com/de/jobs/71095/senior-servicenow-platform-developer-mwd

WHAT IT IS. d.vinci HR-Systeme (Hamburg) is the applicant-tracking system behind a German
employer's career page — Mittelstand, IT service, industry (FI-TS, Holzapfel Group, Altmann,
SICrystal). Its signature: `<tenant>.dvinci-easy.com/<lang>/jobs` (a tenant may also frame it
under its own `jobs.<employer>` host — that host is the same page; the user names the
`dvinci-easy.com` address). **One adapter covers every employer that uses it; the user names the
tenant** by its subdomain, its host, or any address on it.

THE RULES. Every tenant publishes `User-agent: * / Allow: /` and its sitemaps (155 B); no
Crawl-delay, 2 s is ours. The guard is taken on the exact path.

THE LIST, IN THE PAGE. `/<lang>/jobs` (200; 4 934 B for none, 18–108 KB for 6–46 publications)
renders the tenant's own template around `var DvinciData = { "jobPublications": [...] }` — every
publication: `id`, `language`, `position`, `subtitle`, `pageDescription`, `jobPublicationURL`,
`applicationFormURL`, `applicationApplyApiURL`, `applicationApplyWhatsAppURL`, `startDate`,
`endDate`, and `jobOpening` (`name`, `reference`, `location` — the tenant's label —,
`locations[]` with `name`, `city`, `country.isoA2`, `latitude`/`longitude`, `address` (street,
zip), `categories[]`, `targetGroups[]`, `workingTimes[]`, `contractPeriod`, `earliestEntryDate`,
`orgUnit`, `company`, `department`, `salary`, `salaryRange`, `createdDate`). **No count is stated
anywhere: the list is the board**, and `jobs` prints its length beside the emitted count. A tenant
with no publication renders `"jobPublications": []` — «0 publications», not an error.

THE AD. `/<lang>/jobs/<id>/<slug>` (200, 12–25 KB) carries `var DvinciData = { jobPublication:
{...} }` (the same object, one publication — a JavaScript literal whose key is unquoted) and one
schema.org `JobPosting` (title, description as HTML with inline styles, datePosted,
hiringOrganization with a logo, jobLocation with street and postal code, employmentType). The
adapter reads the object for the facts and the posting for the description.

**WITHHELD:** every `address` (street, zip), `latitude`/`longitude`, `applicationFormURL`,
`applicationApplyApiURL`, `applicationApplyWhatsAppURL`, the logo; the description scrubbed of
e-mail addresses and telephones (a Holzapfel ad prints two telephones in its text) — dates
(«ab 01.10.2026») left alone; `contacts_withheld` on every record; the application never touched.

`--country-code` filters on `locations[].country.isoA2` — any of a publication's locations — and
says when a publication carries no country.

Measured 2026-09-21 07:14–07:16 UTC by the declared client, the guard on the exact path, two
reads each: `fi-ts-karriere` 46 publications (108 082 B), `holzapfel-group` 6 (18 262 B),
`sicrystal` 0 (4 934 B — «Sie haben aktuell keine passende Stelle gefunden?»), `altmann`
`/en/jobs` 29 (the publications' own `language` is `de`); the FI-TS ad 200 ×2 (24 705 B);
`zzz-not-a-tenant-2026.dvinci-easy.com` does not resolve — no wildcard, not a tenant (exit 3).
"""

import argparse
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

import _ldjson
from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

DOMAIN = "dvinci-easy.com"
NOT_TENANTS = ("www", "app", "static", "api", "login", "admin")
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")   # «02772-603 515», «+49 (0)40 …»: 8+ digits with the separators German numbers use
DATE_RE = re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b")                       # «ab 01.10.2026» is a date, not a telephone — it stays
LIST_RE = re.compile(r"var\s+DvinciData\s*=\s*\{\s*\"?jobPublications\"?\s*:\s*")
ONE_RE = re.compile(r"var\s+DvinciData\s*=\s*\{\s*\"?jobPublication\"?\s*:\s*")
AD_RE = re.compile(r"^/([a-z]{2})/jobs/(\d+)(?:/[^/]*)?/?$")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[dvinci] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def host_of(arg):
    """`fi-ts-karriere`, `fi-ts-karriere.dvinci-easy.com` or any URL on it → the tenant's host."""
    s = arg.strip()
    if "://" in s or "." in s.split("/")[0]:
        parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
        host = parts.netloc.lower()
    else:
        host = f"{s.lower()}.{DOMAIN}"
    m = re.match(r"^([a-z0-9](?:[a-z0-9\-]*[a-z0-9])?)\." + re.escape(DOMAIN) + "$", host)
    if not m:
        die(f"{arg}: a tenant is <tenant>.{DOMAIN} — fi-ts-karriere, or fi-ts-karriere.{DOMAIN}, or an address on it")
    if m.group(1) in NOT_TENANTS:
        die(f"{arg}: {host} is the vendor's, not a tenant — never sent", EXIT_REFUSED)
    return host


def request(url, host, accept="text/html,application/xhtml+xml"):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != host:
        die(f"{url}: not the tenant's host — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": accept, "Accept-Language": "de, en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except urllib.error.URLError as e:
        if "nodename nor servname" in str(e) or "Name or service not known" in str(e) or "getaddrinfo" in str(e):
            die(f"{url}: the name does not resolve — {DOMAIN} has no such tenant (no wildcard); {e.reason}", EXIT_GONE)
        die(f"{url}: {type(e).__name__}: {e}")
    except OSError as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>|</dt>|</dd>", "\n", markup or "")
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span)\b[^>]*>", "", t)   # inline tags leave no space behind
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def decode_after(markup, pattern):
    """The JSON value that follows `pattern` in the page — the page's own data literal."""
    m = pattern.search(markup or "")
    if not m:
        return None
    try:
        v, _end = json.JSONDecoder().raw_decode(markup, m.end())
    except ValueError:
        return None
    return v


def city_of(loc):
    """The location's city — from its address's `city` (the one field of the address that is emitted), else its name."""
    addr = loc.get("address") if isinstance(loc.get("address"), dict) else {}
    return addr.get("city") or loc.get("city") or loc.get("name") or None


def names(seq):
    """`[{"name": …}, …]` → the names, or None."""
    if not isinstance(seq, list):
        return None
    out = [x.get("name") for x in seq if isinstance(x, dict) and x.get("name")]
    return out or None


def record(p, host, lang):
    jo = p.get("jobOpening") if isinstance(p.get("jobOpening"), dict) else {}
    locs = [l for l in (jo.get("locations") or []) if isinstance(l, dict)]
    countries = []
    for l in locs:
        c = (l.get("country") or {}).get("isoA2") if isinstance(l.get("country"), dict) else None
        if c and c.upper() not in countries:
            countries.append(c.upper())
    pid = str(p.get("id") or "").strip() or None
    company = jo.get("company") if isinstance(jo.get("company"), dict) else {}
    org = jo.get("orgUnit") if isinstance(jo.get("orgUnit"), dict) else {}
    cp = jo.get("contractPeriod") if isinstance(jo.get("contractPeriod"), dict) else {}
    return {
        "source": "dvinci", "tenant": host,
        "country": countries[0] if len(countries) == 1 else None, "countries": countries or None,
        "ledger_id": f"dvinci:{host}:{pid}", "id": pid,
        "url": p.get("jobPublicationURL") or (f"https://{host}/{lang}/jobs/{pid}" if pid else None),
        "title": (p.get("position") or jo.get("name") or "").strip() or None, "subtitle": p.get("subtitle") or None,
        "company": company.get("name") or None, "org_unit": org.get("name") or None,
        "reference": jo.get("reference") or None,
        "location": jo.get("location") or None, "places": [c for c in (city_of(l) for l in locs) if c] or None,
        "categories": names(jo.get("categories")), "target_groups": names(jo.get("targetGroups")), "working_times": names(jo.get("workingTimes")),
        "contract": cp.get("name") or None, "earliest_entry": jo.get("earliestEntryDate") or None,
        "salary": jo.get("salary") or jo.get("salaryRange") or None,
        "language": p.get("language") or None,
        "published": (p.get("startDate") or jo.get("createdDate") or "")[:10] or None, "expires": (p.get("endDate") or "")[:10] or None,
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    host = host_of(a.tenant)
    lang = (a.lang or "de").strip().lower()
    if not re.match(r"^[a-z]{2}$", lang):
        die(f"--lang {a.lang}: two letters (de, en)")
    url = f"https://{host}/{lang}/jobs"
    code, body = request(url, host)
    if code == 404:
        die(f"{url}: HTTP 404 — no such tenant or language", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    pubs = decode_after(body, LIST_RE)
    if not isinstance(pubs, list):
        die(f"{url}: 200 without `DvinciData.jobPublications` — not a d.vinci list, or the page changed; not an empty board", EXIT_PARTIAL)
    rows, seen = [], set()
    for p in pubs:
        if not isinstance(p, dict) or p.get("id") is None or str(p["id"]) in seen:
            continue
        seen.add(str(p["id"]))
        rows.append(record(p, host, lang))
    if a.country_code:
        cc = a.country_code.upper()
        blank = sum(1 for r in rows if not r["countries"])
        rows = [r for r in rows if r["countries"] and cc in r["countries"]]
        if blank:
            note(f"--country-code {cc}: {th(blank)} publication(s) carry no country in their locations — left out, not for {cc}.")
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if not pubs:
        note(f"{host}: 0 publications — the page's list is empty (200); not an error.")
    elif a.country_code:
        note(f"{th(len(rows))} emitted for {a.country_code.upper()} of the {th(len(seen))} publications the page lists for {host} — no count is stated anywhere, the list is the board.")
    else:
        note(f"{th(len(rows))} emitted, the {th(len(seen))} publications the page lists for {host} — no count is stated anywhere, the list is the board.")
    note("addresses, coordinates and application routes never emitted.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    host = host_of(parts.netloc) if parts.netloc else die(f"{a.url}: not a d.vinci ad address (https://<tenant>.{DOMAIN}/<lang>/jobs/<id>/<slug>)")
    m = AD_RE.match(parts.path)
    if parts.scheme != "https" or not m:
        die(f"{a.url}: not a d.vinci ad address (https://<tenant>.{DOMAIN}/<lang>/jobs/<id>/<slug>)")
    lang, pid = m.group(1), m.group(2)
    url = f"https://{host}{parts.path}"                      # the address as the page links it; any query dropped
    code, body = request(url, host)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    p = decode_after(body, ONE_RE)
    if not isinstance(p, dict) or str(p.get("id") or "") != pid:
        die(f"{url}: 200 without `DvinciData.jobPublication` for {pid} — gone, or the page changed", EXIT_GONE if p is None and "jobPublication" not in body else EXIT_PARTIAL)
    row = record(p, host, lang)
    posts = _ldjson.postings(body)
    desc = posts[0].get("description") if posts and isinstance(posts[0], dict) else None
    org = posts[0].get("hiringOrganization") if posts and isinstance(posts[0].get("hiringOrganization"), dict) else {}
    row["company"] = row["company"] or org.get("name") or None
    row["description"] = scrub(text(desc)) if desc else None
    row["url"] = url
    print(json.dumps(row, ensure_ascii=False))
    note(f"{url}: read from the page's own data and its JobPosting; addresses, coordinates, application routes and the logo never emitted; text scrubbed.")


def main(argv=None):
    p = argparse.ArgumentParser(description="d.vinci — one tenant's publications from the JSON its own list page carries; addresses and application routes never emitted. Issue #481.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="one tenant's whole board (1 request)")
    j.add_argument("--tenant", required=True, help="the subdomain (fi-ts-karriere), the host, or any address on it")
    j.add_argument("--lang", default="de", help="the list's language path (de, en) — default de")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="keep publications with a location in this country (locations[].country.isoA2)")
    j.set_defaults(fn=cmd_jobs)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
