#!/usr/bin/env python3
"""Refline — a Swiss ATS, one tenant at a time: the tenant's list on `apply.refline.ch/<tenant>/search.html?form.buttons.listAll=1` is a table whose cells are named by their class and whose page says «Es liegen N Angebote vor.» (the stated count); each ad on `/<tenant>/<id>/pub/<n>` carries one schema.org JobPosting and a contact block — the block, the street and the postal code never emitted. Issue #483.

  refline.py jobs --tenant 673276 [--country-code CH]        the tenant's positions (1 request)
  refline.py jobs --tenant https://apply.refline.ch/792841/search.html
  refline.py ad --url https://apply.refline.ch/673276/2176/pub/1/index.html

WHAT IT IS. Refline (Zürich) is the applicant-tracking system behind the career pages of Swiss
public bodies, universities, research institutes and banks — Empa, the FHNW, the Zürcher
Kantonalbank, cantonal administrations (named by `umantis.md`, present in the job-room feed). Its
signature: `apply.refline.ch/<six digits>/…` (the mobile mirror `m.refline.ch/<tenant>/` is the
same board — not this route). **One adapter covers every employer that uses it; the user names the
tenant** by its six-digit number, or any `apply.refline.ch` address that carries it.

THE RULES. One host, one file (1 117 B): `*` allowed `/`, refused `/rec01/1/` and `/rec03/1/`
(«demo, no indexing»), eighteen sitemaps declared; no Crawl-delay, 2 s is ours. The guard is
taken on the exact path.

THE LIST. `/<tenant>/search.html?form.buttons.listAll=1` (200; 11–41 KB for 16–49 positions)
renders every position in one table — no pager — whose cells are named by their class: `position`
(the title's link to `/<tenant>/<id>/pub/<n>[/index.html]`), `workload` («80% - 100%»),
`workplace`, `published` (dd.mm.yyyy), `operationArea`, `segment`, `locale` — the columns a
tenant shows are the tenant's choice. Above it, «Es liegen N Angebote vor.» — **the stated
count** — on the tenants that print it (Empa 23, FHNW 16; the ZKB prints none and lists 49).
**An unknown tenant number is answered 200 with the vendor's own landing page** («Refline -
Applicant Tracking System», no table): «not a tenant», exit 3 — never «an empty board».

THE AD. `/<tenant>/<id>/pub/<n>` (200; 13–24 KB) carries one JobPosting — title, description
(HTML), datePosted (ISO with microseconds), validThrough, employmentType (a list), hiringOrganization
with a logo, jobLocation (streetAddress, postalCode, locality, region, country), identifier
`refline-<tenant>-master` — and a contact block (`contactInfo`: a name, a telephone, an e-mail; the
ZKB writes «Dein Kontakt … Telefon: …» inside the description itself). **Emitted: the posting's
text, scrubbed; locality, region, country. Never: the street, the postal code, the contact block,
the logo, any e-mail address or telephone in the text.** `contacts_withheld` on every record; the
application (`/<tenant>/<id>/pub/<n>/apply`) never touched.

`--country-code` STAMPS on the list (the table states no country; the ad states one) and the run
says so; on the ad it filters on the posting's own country.

Measured 2026-09-21 07:30–07:32 UTC by the declared client, the guard on the exact path, two reads
each (identical bodies): Empa `673276` 23 stated / 23 rows (13 149 B), ZKB `792841` 49 rows, none
stated (41 280 B), FHNW `655298` 16 / 16 (11 259 B); the Empa ad 200 ×2 (24 058 B); `000001` 200
— the vendor's landing page (63 712 B).
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

HOST = "apply.refline.ch"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")   # «+41 58 765 4066», «044 292 27 95»: 8+ digits with separators
DATE_RE = re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b")                       # «per 01.01.2027» is a date, not a telephone — it stays
TENANT_RE = re.compile(r"^\d{6}$")
AD_RE = re.compile(r"^/(\d{6})/(\d+)/pub/(\d+)(?:/index\.html)?/?$")
STATED_RE = re.compile(r"Es lieg(?:en|t)\s+(\d+)\s+Angebot")
ROW_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL_RE = re.compile(r"<td class=\"([A-Za-z_]+)\"[^>]*>(.*?)</td>", re.S)
LINK_RE = re.compile(r"<a[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", re.S)
VENDOR_RE = re.compile(r"<title>\s*Refline - ")   # «Refline - Applicant Tracking System» / «Refline - Bewerbermanagement Software», by Accept-Language
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[refline] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def tenant_of(arg):
    """`673276`, or any apply.refline.ch address carrying it → the six-digit tenant."""
    s = arg.strip()
    if TENANT_RE.match(s):
        return s
    parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
    m = re.match(r"^/(\d{6})(?:/|$)", parts.path)
    if parts.netloc.lower() != HOST or not m:
        die(f"{arg}: a tenant is its six-digit number (673276) or an address on https://{HOST}/<tenant>/…")
    return m.group(1)


def request(url, accept="text/html,application/xhtml+xml"):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": accept, "Accept-Language": "de, fr, en"})
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
    """`16.03.2026` → ISO; `2026-03-16T09:10:18.577707+00:00` → its date; anything else as read."""
    s = (s or "").strip()
    m = re.match(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$", s)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    if re.match(r"^\d{4}-\d{2}-\d{2}", s):
        return s[:10]
    return s or None


def ad_of(href):
    """A link → (url without index.html or query, id, publication) when it is an ad on this host."""
    parts = urllib.parse.urlsplit(htmlmod.unescape(href))
    m = AD_RE.match(parts.path)
    if parts.netloc.lower() not in ("", HOST) or not m:
        return None
    return f"https://{HOST}/{m.group(1)}/{m.group(2)}/pub/{m.group(3)}", m.group(2), m.group(3), m.group(1)


def rows_of(markup, tenant):
    """The list's table → [(id, fields)]; a cell's class names its field."""
    out = []
    for row in ROW_RE.findall(markup or ""):
        f = {}
        for cls, inner in CELL_RE.findall(row):
            if cls == "position":
                lk = LINK_RE.search(inner)
                got = ad_of(lk.group(1)) if lk else None
                if got and got[3] == tenant:
                    f["url"], f["id"], f["pub"] = got[0], got[1], got[2]
                    f["title"] = text(lk.group(2))
                continue
            f[cls] = text(inner)
        if f.get("id"):
            out.append((f["id"], f))
    return out


def record(pid, f, tenant, stamp):
    return {
        "source": "refline", "tenant": tenant, "country": stamp,
        "ledger_id": f"refline:{tenant}:{pid}", "id": pid, "url": f.get("url"),
        "title": f.get("title"), "workload": f.get("workload"), "place": f.get("workplace"),
        "area": f.get("operationArea"), "segment": f.get("segment"), "language": f.get("locale"),
        "published": when(f.get("published")),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    tenant = tenant_of(a.tenant)
    stamp = a.country_code.upper() if a.country_code else None
    url = f"https://{HOST}/{tenant}/search.html?form.buttons.listAll=1"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — no such tenant", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    if VENDOR_RE.search(body) and '<td class="position"' not in body:
        die(f"{url}: 200 with the vendor's own landing page — {HOST} knows no tenant {tenant}", EXIT_GONE)
    found = rows_of(body, tenant)
    m = STATED_RE.search(text(body) or "")
    stated = int(m.group(1)) if m else None
    if not found and stated is None and '<td class="position"' not in body and "search.html" not in body:
        die(f"{url}: 200 without a Refline list — the page changed; not an empty board", EXIT_PARTIAL)
    rows, seen = [], set()
    for pid, f in found:
        if pid in seen:
            continue
        seen.add(pid)
        rows.append(record(pid, f, tenant, stamp))
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if stated is not None:
        note(f"{th(len(rows))} emitted, the page states {th(stated)} for tenant {tenant}" + (f" — {th(stated - len(rows))} short" if len(rows) < stated else "") + ".")
    elif not rows:
        note(f"tenant {tenant}: 0 positions — the list shows none and states no count (200); not an error.")
    else:
        note(f"{th(len(rows))} emitted for tenant {tenant} — the page states no count, the table is the board.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the list states no country.")
    note("the contact block, street and postal code never emitted; texts scrubbed.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    got = ad_of(a.url) if parts.netloc.lower() == HOST and parts.scheme == "https" else None
    if not got:
        die(f"{a.url}: not a Refline ad address (https://{HOST}/<tenant>/<id>/pub/<n>)")
    url, pid, _pub, tenant = got
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    posts = _ldjson.postings(body)
    if not posts:
        die(f"{url}: 200 without a JobPosting — gone, or the page changed", EXIT_GONE if VENDOR_RE.search(body) or "search.html" in body else EXIT_PARTIAL)
    p = posts[0]
    org = p.get("hiringOrganization") if isinstance(p.get("hiringOrganization"), dict) else {}
    jl = p.get("jobLocation")
    jl = jl[0] if isinstance(jl, list) and jl else (jl if isinstance(jl, dict) else {})
    addr = jl.get("address") if isinstance(jl.get("address"), dict) else {}
    cc = (addr.get("addressCountry") or "").strip()
    et = p.get("employmentType")
    row = {
        "source": "refline", "tenant": tenant,
        "country": cc.upper() if len(cc) == 2 else None, "country_name": cc if cc and len(cc) != 2 else None,
        "ledger_id": f"refline:{tenant}:{pid}", "id": pid, "url": url,
        "title": scrub(text(p.get("title") or "")), "company": org.get("name") or None,
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
    note(f"{url}: read from the page's JobPosting; the contact block, street, postal code and logo never emitted; text scrubbed.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Refline — one tenant's list on apply.refline.ch, the table read by its cells' classes against the page's stated count; the ad's JobPosting with contacts and street withheld. Issue #483.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="one tenant's whole board (1 request)")
    j.add_argument("--tenant", required=True, help="the six-digit tenant (673276) or any apply.refline.ch address carrying it")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the list states none)")
    j.set_defaults(fn=cmd_jobs)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.add_argument("--country-code", dest="country_code", metavar="ISO2", help="emit only if the ad's own country is this one")
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
