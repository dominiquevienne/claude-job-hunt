#!/usr/bin/env python3
"""Ostendis — a Swiss ATS, one tenant at a time: the employer embeds Ostendis's job list on its own site with a «publication place» token (`<script src="https://odm.ostendis.com/ojp/assets/loader" data-token="…">`), and that loader fills the list by GET `odm.ostendis.com/ojp/data/<version>/jobs/<token>/<LANG>?domain=<site>` — the adapter replays that call with the page's own token, language and domain; each ad on `…/publication/<slug>/<token>` carries one schema.org JobPosting; postal codes, streets and logos never emitted. Issue #484.

  ostendis.py jobs --tenant https://www.mepersonal.ch/stellenangebote [--lang DE] [--country-code CH]   the page's token read, then the list (3 requests)
  ostendis.py jobs --tenant blsr7vzflvim1wk2s4y77yxts5m9sanr --domain www.mepersonal.ch                  the token named, the domain it is embedded on (2 requests)
  ostendis.py ad --url https://jobs.ostendis.com/publication/mitarbeiter-in-lead-generation/ly0mfrgf…

WHAT IT IS. Ostendis AG (Boniswil) is a Swiss e-recruiting system — SMEs, hotels, clinics,
municipalities (ME Personal, Thurvita, Lactalis Suisse). It has no hosted career site: **the
employer's own page embeds the list** (`OSTENDISJOBS.embed(token, "DE", "#ostendisJobs")`), and
the ads live on `jobs.ostendis.com/publication/<slug>/<64 chars>`, `link.ostendis.com/…`, or the
tenant's own CNAME (`jobs.mepersonal.ch/publication/…`). **One adapter covers every employer that
uses it; the user names the tenant** by the page that embeds the list (the token and the domain
are read from it) or by the 32-character token with `--domain`.

THE RULES. `odm.ostendis.com`, `jobs.ostendis.com`, `link.ostendis.com` answer no rules file
(`robots.txt` 404 with an HTML page, `_robots.allowed` open, `certain: False` / absent); the
tenant's page host has its own file, read on the exact path. No Crawl-delay anywhere; 2 s is ours,
per host.

THE CALL. The loader (`/ojp/assets/loader`, 80 KB) GETs `/ojp/assets/version/<token>` → `{"version":
"v55"}`, loads `/ojp/assets/v55/script`, and that script GETs `/ojp/data/v55/jobs/<token>/<LANG>?
domain=<window.location.hostname>` → `{"jobs": [...], "error": {"message": ""}, "options": {…},
"translations": {…}}` — every published job with `id`, `reference`, `title`, `country`,
`countrycode`, `city`, `zip`, `published`, `timestamp`, `type`, `position`, `workload` («40 - 60%»,
with `workload_min` / `workload_max`), `company`, `department`, `detail` (the ad's address),
`action`, `image`, `text`, `startdate`, `language`, `langcode`. **No count is stated anywhere: the
list is the board**, its length printed beside the emitted count. The adapter replays the version
call, then the data call, with the page's own token, language and domain.

THE AD. `/publication/<slug>/<64 chars>` (200, ~26 KB) carries one JobPosting — title, description
(HTML), datePosted, employmentType (a list), hiringOrganization with a logo, jobLocation
(streetAddress, postalCode, locality, country), identifier — and the CVdropper application link.

**WITHHELD:** `zip` / `postalCode` and `streetAddress`; `image` and the logo; e-mail addresses
and telephones in the texts replaced («[e-mail withheld]» / «[telephone withheld]»), dates left
alone; `contacts_withheld` on every record; the application (the CVdropper) never touched.

`--country-code` filters on `countrycode` — every job carries one.

Measured 2026-09-21 07:38–07:41 UTC by the declared client, the guard on the exact path: the
vendor's own list (token `7ha0m3iy…` on `www.ostendis.com/de/career/`) 2 jobs ×2 (2 782 B,
identical); ME Personal (`blsr7vzf…` on `www.mepersonal.ch/stellenangebote`) 4 jobs ×2 (3 754 B,
identical; the ads on `jobs.mepersonal.ch`); the Lactalis Suisse ad on `link.ostendis.com` 200 ×2
(25 972 B, one JobPosting); `jobs.ostendis.com/` 404.
"""

import argparse
import html as htmlmod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import _ldjson
from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

DATA_HOST = "odm.ostendis.com"
AD_HOSTS = ("jobs.ostendis.com", "link.ostendis.com")
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")   # «+41 62 767 88 00», «062 767 88 00»: 8+ digits with separators
DATE_RE = re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b")                       # «per 01.01.2027» is a date, not a telephone — it stays
TOKEN_RE = re.compile(r"^[a-z0-9]{32}$")
LOADER_TOKEN_RE = re.compile(r'<script[^>]*src="https://odm\.ostendis\.com/ojp/assets/loader"[^>]*\bdata-token="([a-z0-9]{32})"|<script[^>]*\bdata-token="([a-z0-9]{32})"[^>]*src="https://odm\.ostendis\.com/ojp/assets/loader"', re.S)
EMBED_RE = re.compile(r'OSTENDISJOBS\.embed\(\s*"([a-z0-9]{32})"\s*,[^"]*"([A-Za-z]{2})"', re.S)
AD_PATH_RE = re.compile(r"^/publication/([^/]+)/([a-z0-9]{64})/?$")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[ostendis] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, hosts, accept="text/html,application/xhtml+xml,*/*;q=0.8"):   # link.ostendis.com answers 406 to an Accept without */*
    """One GET under the declared identity — only to the hosts this run has named."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc.lower() not in hosts:
        die(f"{url}: not a host this run names — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": accept})   # no Accept-Language: link.ostendis.com answers 406 to one with spaces, and the list carries its own language
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
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", markup or "")
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span)\b[^>]*>", "", t)   # inline tags leave no space behind
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def when(s):
    """A Unix timestamp (`"1787875200"`) or an ISO date → YYYY-MM-DD; empty → None."""
    s = str(s or "").strip()
    if re.match(r"^\d{9,11}$", s) and s != "0":
        return time.strftime("%Y-%m-%d", time.gmtime(int(s)))
    if re.match(r"^\d{4}-\d{2}-\d{2}", s):
        return s[:10]
    return None


def tenant_of(arg, domain):
    """A 32-character token (with `--domain`) or the page that embeds the list → (token, domain, lang from the page or None, page url or None)."""
    s = arg.strip()
    if TOKEN_RE.match(s):
        if not domain:
            die(f"{s}: a token names the list but the call carries the domain it is embedded on — give --domain <the site's host> or the page's URL")
        return s, domain.strip().lower(), None, None
    parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
    if parts.scheme != "https" or not parts.netloc or not re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", parts.netloc.lower()):
        die(f"{arg}: a tenant is the page that embeds its Ostendis list (https://<site>/<careers page>) or the 32-character token with --domain")
    return None, parts.netloc.lower(), None, s


def places_of_page(url, host):
    """The page → (the loader's token, [(publication place token, LANG), …] as the page's `OSTENDISJOBS.embed` calls name them)."""
    code, body = request(url, {host})
    if code == 404:
        die(f"{url}: HTTP 404 — no such page", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    m = LOADER_TOKEN_RE.search(body)
    loader = (m.group(1) or m.group(2)) if m else None
    places = []
    for t, lang in EMBED_RE.findall(body):
        if (t, lang.upper()) not in places:
            places.append((t, lang.upper()))
    if not loader and not places:
        die(f"{url}: 200 without Ostendis's loader (`data-token`) nor an `OSTENDISJOBS.embed` call — the page embeds no Ostendis list: not a tenant (today)", EXIT_GONE)
    if not places:
        places = [(loader, None)]
    return loader or places[0][0], places


def version_of(token):
    url = f"https://{DATA_HOST}/ojp/assets/version/{token}"
    code, body = request(url, {DATA_HOST}, accept="application/json")
    if code == 404:
        die(f"{url}: HTTP 404 — {DATA_HOST} knows no publication place {token}: not a tenant", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    try:
        v = json.loads(body).get("version")
    except (ValueError, AttributeError):
        v = None
    if v is None:
        die(f"{url}: {{\"version\": null}} — {DATA_HOST} knows no publication place {token}: not a tenant", EXIT_GONE)
    if not isinstance(v, str) or not re.match(r"^v\d+$", v):
        die(f"{url}: 200 without a version — the loader's route changed", EXIT_PARTIAL)
    return v


def jobs_of(token, lang, domain, version):
    url = f"https://{DATA_HOST}/ojp/data/{version}/jobs/{token}/{lang}?" + urllib.parse.urlencode({"domain": domain})
    code, body = request(url, {DATA_HOST}, accept="application/json")
    if code == 404:
        die(f"{url}: HTTP 404 — no list for {token} in {lang}", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    try:
        data = json.loads(body)
    except ValueError:
        die(f"{url}: 200 and not JSON — the route changed", EXIT_PARTIAL)
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        die(f"{url}: 200 without `jobs` — the route changed; not an empty board", EXIT_PARTIAL)
    err = (data.get("error") or {}).get("message") if isinstance(data.get("error"), dict) else None
    if err:
        die(f"{url}: the list answers an error — {err[:120]}", EXIT_PARTIAL)
    return [j for j in data["jobs"] if isinstance(j, dict)]


def record(j, token, domain):
    pid = str(j.get("id") or "").strip() or None
    return {
        "source": "ostendis", "tenant": domain, "publication_place": token,
        "country": (j.get("countrycode") or "").upper() or None, "country_name": j.get("country") or None,
        "ledger_id": f"ostendis:{token}:{pid}", "id": pid,
        "url": j.get("detail") or j.get("action") or None,
        "title": (j.get("title") or "").strip() or None, "reference": j.get("reference") or None,
        "company": j.get("company") or None, "department": j.get("department") or None,
        "place": j.get("city") or None,
        "workload": j.get("workload") or None, "type": j.get("type") or None, "position": j.get("position") or None,
        "start": j.get("startdate") or None, "published": when(j.get("timestamp")) or when(j.get("published")),
        "language": (j.get("langcode") or "").upper() or None,
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    token, domain, _lang, page = tenant_of(a.tenant, a.domain)
    places = [(token, None)]
    if page:
        token, places = places_of_page(page, domain)
    version = version_of(token)
    rows, seen, read = [], set(), 0
    for place, page_lang in places:
        lang = (a.lang or page_lang or "DE").strip().upper()
        if not re.match(r"^[A-Z]{2}$", lang):
            die(f"--lang {a.lang}: two letters (DE, FR, IT, EN)")
        jobs = jobs_of(place, lang, domain, version)
        read += len(jobs)
        for j in jobs:
            pid = str(j.get("id") or "")
            if not pid or pid in seen:
                continue
            seen.add(pid)
            rows.append(record(j, place, domain))
    if a.country_code:
        cc = a.country_code.upper()
        rows = [r for r in rows if r["country"] == cc]
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    where = f"{domain} ({th(len(places))} publication place(s), {version})"
    if not read:
        note(f"{where}: 0 jobs — the list answered an empty `jobs` (200); not an error.")
    elif a.country_code:
        note(f"{th(len(rows))} emitted for {a.country_code.upper()} of the {th(len(seen))} jobs the lists carry for {where} — no count is stated anywhere, the list is the board.")
    else:
        note(f"{th(len(rows))} emitted, the {th(len(seen))} jobs the lists carry for {where}" + (f" ({th(read - len(seen))} listed twice across places)" if read > len(seen) else "") + " — no count is stated anywhere, the list is the board.")
    note("postal codes, streets and images never emitted; texts scrubbed.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    host = parts.netloc.lower()
    m = AD_PATH_RE.match(parts.path)
    if parts.scheme != "https" or not host or not m or not re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", host):
        die(f"{a.url}: not an Ostendis ad address (https://<jobs.ostendis.com | link.ostendis.com | the tenant's jobs host>/publication/<slug>/<64 characters>)")
    url = f"https://{host}/publication/{m.group(1)}/{m.group(2)}"        # any query dropped
    code, body = request(url, {host})
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    posts = _ldjson.postings(body)
    if not posts:
        die(f"{url}: 200 without a JobPosting — gone, or the page changed", EXIT_GONE if "Diese Seite existiert nicht" in body or "404" in body[:600] else EXIT_PARTIAL)
    p = posts[0]
    org = p.get("hiringOrganization") if isinstance(p.get("hiringOrganization"), dict) else {}
    jl = p.get("jobLocation")
    jl = jl[0] if isinstance(jl, list) and jl else (jl if isinstance(jl, dict) else {})
    addr = jl.get("address") if isinstance(jl.get("address"), dict) else {}
    ident = p.get("identifier") if isinstance(p.get("identifier"), dict) else {}
    cc = (addr.get("addressCountry") or "").strip()
    et = p.get("employmentType")
    row = {
        "source": "ostendis", "tenant": host,
        "country": cc.upper() if len(cc) == 2 else None, "country_name": cc if cc and len(cc) != 2 else None,
        "ledger_id": f"ostendis:{host}:{m.group(2)}", "id": m.group(2), "url": url,
        "title": scrub(text(p.get("title") or "")), "company": org.get("name") or None, "reference": ident.get("value") or None,
        "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None,
        "employment_type": et if isinstance(et, list) else ([et] if et else None),
        "published": when(p.get("datePosted")), "expires": when(p.get("validThrough")),
        "description": scrub(text(p.get("description") or "")),
        "contacts_withheld": True,
    }
    if a.country_code and row["country"] and row["country"] != a.country_code.upper():
        note(f"{url}: the ad is in {row['country']}, not {a.country_code.upper()} — 0 emitted.")
        return
    print(json.dumps(row, ensure_ascii=False))
    note(f"{url}: read from the page's JobPosting; the street, the postal code and the logo never emitted; text scrubbed.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Ostendis — one tenant's list through the call its own page makes, with the page's token, language and domain; postal codes, streets and images never emitted. Issue #484.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="one tenant's whole list (the page, the version, the data)")
    j.add_argument("--tenant", required=True, help="the page that embeds the list (https://<site>/<careers page>), or the 32-character token with --domain")
    j.add_argument("--domain", help="with a token: the host the list is embedded on (the call carries it)")
    j.add_argument("--lang", help="the list's language (DE, FR, IT, EN) — default: the page's embed call, else DE")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="keep one country (the job's countrycode)")
    j.set_defaults(fn=cmd_jobs)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.add_argument("--country-code", dest="country_code", metavar="ISO2", help="emit only if the ad's own country is this one")
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
