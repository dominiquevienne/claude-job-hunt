#!/usr/bin/env python3
"""Factorial — an ATS, one tenant at a time: the tenant's career page on `<tenant>.factorial.es` / `<tenant>.factorialhr.com` (or `careers.factorialhr.com`) renders its whole job list in the page as `li.job-offer-item` cards (the list is the board), and each ad on `/job_posting/<slug>-<id>` carries one schema.org JobPosting; the team section's employee names, the street and the postal code never emitted. Issue #486.

  factorial.py jobs --tenant kampaoh [--country-code ES]          the tenant's positions (1 request)
  factorial.py jobs --tenant https://careers.factorialhr.com/
  factorial.py ad --url https://kampaoh.factorial.es/job_posting/limpiador-a-kampaoh-las-arenas-312764

WHAT IT IS. Factorial (Barcelona) is an HR suite for SMEs whose recruiting module hosts a
«career page» per employer — Spain and Portugal above all (`<tenant>.factorial.es`, `<tenant>.
factorialhr.com`, Factorial's own on `careers.factorialhr.com`). **One adapter covers every
employer that uses it; the user names the tenant** by its subdomain (`kampaoh`, on `factorial.es`
unless a host is given), its host, or any address on it.

THE RULES. Every tenant answers `robots.txt` read and open, no Crawl-delay; 2 s is ours. The
guard is taken on the exact path.

THE LIST, IN THE PAGE. `/` (200; 57–263 KB) renders the career page — values, benefits, **the
team with employee names and portraits**, offices — and the jobs as `<li class='job-offer-item'
… data-job-postings-url='https://<tenant>/job_posting/<slug>-<id>' data-contract-type='indefinite'
data-is-remote='false' data-location-id='…' data-team-id='…'>` with three text cells: the title, the
team, the workplace mode («Onsite» / «Presencial» / «Remoto» / «Híbrido»). Every card is in the
page (Factorial 135, Kampaoh 2); a tenant with none renders no `job-offer-item` (Vegenat, DIACONÍA)
— «0 positions», not an error. **No count is stated anywhere: the list is the board**, and `jobs`
prints its length beside the emitted count.

THE AD. `/job_posting/<slug>-<id>` (200, ~44 KB) carries one JobPosting — title, description,
datePosted, identifier (the id), hiringOrganization, jobLocation (a full street address in
`streetAddress`, postalCode, locality, region, country), and the page prints the contract, the
schedule and a salary band when the employer states one.

**WITHHELD:** the team section (names, roles, portraits) never read; `streetAddress` and
`postalCode` never emitted; e-mail addresses and telephones in the texts replaced («[e-mail
withheld]» / «[telephone withheld]»), dates left alone; `contacts_withheld` on every record; the
application (`/job_posting/<slug>-<id>/apply`) never touched.

`--country-code` STAMPS on the list (the cards state no country) and says so; on the ad it
filters on the posting's own country.

Measured 2026-09-21 08:03–08:05 UTC by the declared client, the guard on the exact path, two reads
each (identical bodies): `careers.factorialhr.com` 135 cards (263 310 B), `kampaoh.factorial.es` 2
(57 320 B), `vegenat.factorial.es` 0 (181 390 B — a team of many names, no job), `diaconia.
factorial.es` 0 (70 909 B); the Factorial ad `it-systems-engineer-323635` 200 ×2 (44 496 B, one
JobPosting with a full street address).
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

DOMAINS = ("factorial.es", "factorialhr.com", "factorial.pt", "factorial.de", "factorial.fr", "factorial.it", "factorial.mx", "factorial.com.br")
NOT_TENANTS = ("www", "app", "api", "assets", "help", "static", "login", "admin", "docs", "status")
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")   # «+34 93 000 00 00», «600 000 000»: 8+ digits with separators
DATE_RE = re.compile(r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b")                  # «desde el 01/10/2026» is a date, not a telephone — it stays
ITEM_RE = re.compile(r"<li class='job-offer-item[^']*'(.*?)</li>", re.S)
ATTR_RE = re.compile(r"data-([a-z-]+)='([^']*)'")
CELL_RE = re.compile(r'<div class="text-sm[^"]*">(.*?)</div>', re.S)
AD_RE = re.compile(r"^/job_posting/([^/]*?)-(\d+)/?$")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[factorial] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def host_of(arg):
    """`kampaoh`, `kampaoh.factorial.es`, `careers.factorialhr.com` or any URL on such a host → the host."""
    s = arg.strip()
    if "://" in s or "." in s.split("/")[0]:
        parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
        host = parts.netloc.lower()
    else:
        host = f"{s.lower()}.factorial.es"
    m = re.match(r"^([a-z0-9](?:[a-z0-9\-]*[a-z0-9])?)\.(" + "|".join(re.escape(d) for d in DOMAINS) + r")$", host)
    if not m:
        die(f"{arg}: a tenant is <tenant>.factorial.es / <tenant>.factorialhr.com — kampaoh, careers.factorialhr.com, or an address on it")
    if m.group(1) in NOT_TENANTS:
        die(f"{arg}: {host} is the vendor's, not a tenant — never sent", EXIT_REFUSED)
    return host


def request(url, host, accept="text/html,application/xhtml+xml"):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != host:
        die(f"{url}: not the tenant's host — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": accept, "Accept-Language": "es, pt, en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except urllib.error.URLError as e:
        if "nodename nor servname" in str(e) or "Name or service not known" in str(e) or "getaddrinfo" in str(e):
            die(f"{url}: the name does not resolve — no such tenant; {e.reason}", EXIT_GONE)
        die(f"{url}: {type(e).__name__}: {e}")
    except OSError as e:
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
    s = (s or "").strip()
    return s[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", s) else (s or None)


def ad_of(href, host):
    """A card's `data-job-postings-url` → (url on the tenant's host, id) or None."""
    parts = urllib.parse.urlsplit(htmlmod.unescape(href))
    m = AD_RE.match(parts.path)
    if not m or parts.netloc.lower() not in ("", host):
        return None
    return f"https://{host}{parts.path.rstrip('/')}", m.group(2)


def cards_of(markup, host):
    """The page's `li.job-offer-item` cards → [(id, fields)]."""
    out = []
    for item in ITEM_RE.findall(markup or ""):
        at = dict(ATTR_RE.findall(item))
        got = ad_of(at.get("job-postings-url", ""), host)
        if not got:
            continue
        cells = [text(c) for c in CELL_RE.findall(item)]
        cells = [c for c in cells if c]
        out.append((got[1], {"url": got[0], "title": cells[0] if cells else None, "team": cells[1] if len(cells) > 1 else None,
                             "workplace": cells[2] if len(cells) > 2 else None, "contract": at.get("contract-type") or None,
                             "remote": {"true": True, "false": False}.get((at.get("is-remote") or "").lower()),
                             "location_id": at.get("location-id") or None, "team_id": at.get("team-id") or None}))
    return out


def record(pid, f, host, stamp):
    return {
        "source": "factorial", "tenant": host, "country": stamp,
        "ledger_id": f"factorial:{host}:{pid}", "id": pid, "url": f.get("url"),
        "title": f.get("title"), "team": f.get("team"), "workplace": f.get("workplace"),
        "contract": f.get("contract"), "remote": f.get("remote"),
        "location_id": f.get("location_id"), "team_id": f.get("team_id"),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    host = host_of(a.tenant)
    stamp = a.country_code.upper() if a.country_code else None
    url = f"https://{host}/"
    code, body = request(url, host)
    if code == 404:
        die(f"{url}: HTTP 404 — no such tenant", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    if "job-postings" not in body and "job-offer-item" not in body and "job_posting" not in body:
        die(f"{url}: 200 without Factorial's career page (no `job-postings` controller) — not a tenant, or the page changed; not an empty board", EXIT_PARTIAL)
    rows, seen = [], set()
    for pid, f in cards_of(body, host):
        if pid in seen:
            continue
        seen.add(pid)
        rows.append(record(pid, f, host, stamp))
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if not rows:
        note(f"{host}: 0 positions — the career page renders no job card (200); not an error.")
    else:
        note(f"{th(len(rows))} emitted, the {th(len(seen))} cards the page carries for {host} — no count is stated anywhere, the list is the board.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the cards state no country.")
    note("the team section, streets and postal codes never emitted; texts scrubbed.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    host = host_of(parts.netloc) if parts.netloc else die(f"{a.url}: not a Factorial ad address (https://<tenant>/job_posting/<slug>-<id>)")
    got = ad_of(a.url, host) if parts.scheme == "https" else None
    if not got:
        die(f"{a.url}: not a Factorial ad address (https://<tenant>/job_posting/<slug>-<id>)")
    url, pid = got
    code, body = request(url, host)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    posts = _ldjson.postings(body)
    if not posts:
        die(f"{url}: 200 without a JobPosting — gone, or the page changed", EXIT_GONE if "job-offer-item" in body else EXIT_PARTIAL)
    p = posts[0]
    org = p.get("hiringOrganization") if isinstance(p.get("hiringOrganization"), dict) else {}
    jl = p.get("jobLocation")
    jl = jl[0] if isinstance(jl, list) and jl else (jl if isinstance(jl, dict) else {})
    addr = jl.get("address") if isinstance(jl.get("address"), dict) else {}
    ident = p.get("identifier") if isinstance(p.get("identifier"), dict) else {}
    cc = (addr.get("addressCountry") or "").strip()
    et = p.get("employmentType")
    row = {
        "source": "factorial", "tenant": host,
        "country": cc.upper() if len(cc) == 2 else None, "country_name": cc if cc and len(cc) != 2 else None,
        "ledger_id": f"factorial:{host}:{pid}", "id": pid, "url": url,
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
    note(f"{url}: read from the page's JobPosting; the street and the postal code never emitted; text scrubbed.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Factorial — one tenant's career page, its job cards rendered whole in the page; the team section, streets and postal codes never emitted. Issue #486.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="one tenant's whole board (1 request)")
    j.add_argument("--tenant", required=True, help="the subdomain (kampaoh → kampaoh.factorial.es), the host, or any address on it")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the cards state none)")
    j.set_defaults(fn=cmd_jobs)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.add_argument("--country-code", dest="country_code", metavar="ISO2", help="emit only if the ad's own country is this one")
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
