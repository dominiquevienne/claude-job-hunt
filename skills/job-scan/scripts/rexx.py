#!/usr/bin/env python3
"""rexx systems — an ATS, one tenant at a time: the tenant's portal on `<tenant>-portal.rexx-recruitment.com` lists its positions on `/stellenangebote.html?start=N` (100 a page, a `joblist_navigator` pager; a table or cards, the tenant's choice), and each ad on `/<slug>-<lang>-j<id>.html` carries one schema.org JobPosting with four text sections; the street, the postal code and the session id never emitted. Issue #482.

  rexx.py jobs --tenant stadtfrankfurt [--country-code DE] [--max-pages N]     the tenant's positions (ceil(N/100) requests)
  rexx.py jobs --tenant https://msig-portal.rexx-recruitment.com/stellenangebote.html
  rexx.py ad --url https://msig-portal.rexx-recruitment.com/Underwriter-Casualty-mwd-de-j560.html

WHAT IT IS. rexx systems (Hamburg) sells an HR suite whose recruiting portal is hosted on
`<tenant>-portal.rexx-recruitment.com` — Stadt Frankfurt, MSIG Europe, CODESYS, WPP Media, the
Institut für Auslandsbeziehungen; a tenant often frames it under its own host
(`stadtfrankfurtjobs.de`), and the portal's links then carry that host and a `?sid=` session id.
**One adapter covers every employer that uses it; the user names the tenant** by its portal
subdomain (`stadtfrankfurt`, with or without `-portal`), its host, or any address on it.

THE RULES. Every portal publishes the same file (382 B): seventeen HTTP libraries named by their
default tokens — wget, python-requests, python-urllib, Go-http-client, Java, Scrapy, axios,
node-fetch… — and refused `/`; no `*` group, no other name, no Crawl-delay. **The plugin's token
is not named and no `*` group binds it** (`_robots.allowed`: open, certain) — the file refuses
default library identities, not a declared agent; 2 s is ours. The guard is taken on the exact
path.

THE LIST. `/stellenangebote.html?start=N` (200; 24–83 KB) renders the tenant's positions in one of
two layouts: **a table** `#joboffers.real_table` whose `<th>` links name the columns by their
`order[field]` (`stellenbezeichnung`, `standort_bez`, `taetigkeiten`, `valid_until`) and whose rows
carry the title's link, or **cards** `.joboffer_container` with the title's link, `.job_standort`
(the city), `.job_details_second` (the level), `.joboffer_informations`. The ad's address is
`/<slug>-<lang>-j<id>.html` — the id is the key; `?sid=…` is a session id, dropped, and a custom
host in the link is rewritten to the tenant's portal host. A `#joblist_navigator` pager carries
`start=` links 100 apart; the walk follows `nav_next` until it is empty, and a page whose ids
repeat the previous one ends the walk (exit 6). **No count is stated anywhere**: the adapter prints
the emitted count with the pages walked.

THE AD. `/<slug>-<lang>-j<id>.html` (200; 79–191 KB) carries one JobPosting — title, `description`,
`responsibilities`, `qualifications`, `jobBenefits` (HTML, entity-escaped), datePosted,
validThrough, employmentType, hiringOrganization, jobLocation (streetAddress, postalCode,
locality, region, country). A tenant's text may be double-encoded («Ã¼» for «ü», Stadt
Frankfurt) — repaired when the repair reads as UTF-8 and removes the artefact.

**WITHHELD:** `streetAddress` and `postalCode`; the session id; every e-mail address and telephone
in the texts replaced («[e-mail withheld]» / «[telephone withheld]»), dates left alone;
`contacts_withheld` on every record; the application (a form on the portal) never touched.

`--country-code` filters on the ad's country only for `ad`; for `jobs` the list states no country,
so the code STAMPS every record and the run says so.

Measured 2026-09-21 07:22–07:24 UTC by the declared client, the guard on the exact path, two
reads each: `stadtfrankfurt-portal` 100 rows on `start=0` and 4 on `start=100` (the table
layout), `msig-portal` 5 cards, `codesys-portal` 6 cards; the MSIG ad 200 ×2 (191 421 B), a
Frankfurt ad on the portal host 200 (its links name `stadtfrankfurtjobs.de`).
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

DOMAIN = "rexx-recruitment.com"
NOT_TENANTS = ("www", "app", "static", "api", "login", "admin")
PAGE_SIZE = 100
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")   # «069 212-12345», «+49 (0)221 …»: 8+ digits with the separators German numbers use
DATE_RE = re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b")                       # «bis 25.10.2026» is a date, not a telephone — it stays
AD_PATH_RE = re.compile(r"^/([^/]*?)-([a-z]{2})-j(\d+)\.html$")
ROW_RE = re.compile(r"<tr class=\"alternative_[01]\">(.*?)</tr>", re.S)
TH_RE = re.compile(r"<th class=\"(real_table_col\d+)\">(.*?)</th>", re.S)
CELL_RE = re.compile(r"<td class=\"(real_table_col\d+)\">(.*?)</td>", re.S)
CARD_RE = re.compile(r"<(?:article|div) class=\"joboffer_container\"(.*?)(?=<(?:article|div) class=\"joboffer_container\"|<div id=\"joblist_navigator\"|</form>|</main>|</body>)", re.S)
LINK_RE = re.compile(r"<a[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", re.S)
SPAN_RE = re.compile(r"<span class=\"(job_standort|job_details_second|job_details_first)\">(.*?)</span>", re.S)
INFO_RE = re.compile(r"<div class=\"joboffer_informations joboffer_box\">(.*?)</div>", re.S)
NEXT_RE = re.compile(r"<li class=\"nav_next\">\s*<a[^>]*href=\"([^\"]+)\"", re.S)
NAV_RE = re.compile(r"<div id=\"joblist_navigator\">")
FIELD_NAMES = {"stellenbezeichnung": "title", "standort_bez": "location", "taetigkeiten": "level", "valid_until": "deadline",
               "einsatzort": "place", "unternehmensbereich": "department", "karrierelevel": "level"}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[rexx] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def host_of(arg):
    """`stadtfrankfurt`, `stadtfrankfurt-portal`, `stadtfrankfurt-portal.rexx-recruitment.com` or any URL on it → the portal host."""
    s = arg.strip()
    if "://" in s or "." in s.split("/")[0]:
        parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
        host = parts.netloc.lower()
    else:
        host = f"{s.lower()}.{DOMAIN}" if s.lower().endswith("-portal") else f"{s.lower()}-portal.{DOMAIN}"
    m = re.match(r"^([a-z0-9](?:[a-z0-9\-]*[a-z0-9])?)\." + re.escape(DOMAIN) + "$", host)
    if not m:
        die(f"{arg}: a tenant is <tenant>-portal.{DOMAIN} — stadtfrankfurt, msig-portal, or an address on the portal")
    if re.sub(r"-portal$", "", m.group(1)) in NOT_TENANTS:
        die(f"{arg}: {host} is the vendor's, not a tenant — never sent", EXIT_REFUSED)
    return host


def request(url, host, accept="text/html,application/xhtml+xml"):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != host:
        die(f"{url}: not the tenant's portal host — never sent", EXIT_REFUSED)
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
            die(f"{url}: the name does not resolve — {DOMAIN} has no such portal; {e.reason}", EXIT_GONE)
        die(f"{url}: {type(e).__name__}: {e}")
    except OSError as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


_TRAIL = re.escape("".join(sorted(set(bytes(range(0x80, 0xC0)).decode("cp1252", errors="ignore") + bytes(range(0x80, 0xC0)).decode("latin-1")))))
MOJIBAKE_RE = re.compile("[\u00c2-\u00f4][" + _TRAIL + "]{1,3}")    # a UTF-8 lead byte read as a character, then its trail bytes


def unmojibake(s):
    """«Ã¼» → «ü», «â€‚» → U+2002: the text was UTF-8 read as cp1252 once (Stadt Frankfurt's ads).
    Repaired run by run — a word that does not read as UTF-8 after re-encoding is left alone."""
    if not s or not MOJIBAKE_RE.search(s):
        return s

    def fix(m):
        run = m.group(0)
        for enc in ("cp1252", "latin-1"):
            try:
                return run.encode(enc).decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
        return run
    return MOJIBAKE_RE.sub(fix, s)


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", markup or "")
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span)\b[^>]*>", "", t)   # inline tags leave no space behind
    t = unmojibake(htmlmod.unescape(re.sub(r"<[^>]+>", " ", t))).replace("\xa0", " ")   # the repair before the nbsp swap: «Â » is a mojibaked nbsp
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def when(s):
    """`25.10.2026` → ISO; `00.00.0000` (no deadline) → None; ISO dates as read."""
    s = (s or "").strip()
    m = re.match(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$", s)
    if m:
        if m.group(3) == "0000":
            return None
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    if re.match(r"^\d{4}-\d{2}-\d{2}", s):
        return s[:10]
    return s or None


def ad_of(href, host):
    """A link → (url on the portal host without the session id, lang, id) or None."""
    parts = urllib.parse.urlsplit(htmlmod.unescape(href))
    m = AD_PATH_RE.match(parts.path)
    if not m:
        return None
    return f"https://{host}{parts.path}", m.group(2), m.group(3)


def rows_of(markup, host):
    """The list page → [(id, fields)] from its table or its cards; `fields` carry url, title, lang and the columns."""
    out = []
    cols = {}
    for cls, inner in TH_RE.findall(markup or ""):
        m = re.search(r"order%5Bfield%5D=([a-z_]+)", inner) or re.search(r"order\[field\]=([a-z_]+)", inner)
        cols[cls] = FIELD_NAMES.get(m.group(1), m.group(1)) if m else (text(inner) or cls)
    for row in ROW_RE.findall(markup or ""):
        f = {}
        for cls, inner in CELL_RE.findall(row):
            lk = LINK_RE.search(inner)
            if lk and ad_of(lk.group(1), host):
                f["url"], f["lang"], f["id"] = ad_of(lk.group(1), host)
                f["title"] = text(lk.group(2))
                continue
            f[cols.get(cls, cls)] = text(inner)
        if f.get("id"):
            out.append((f["id"], f))
    if out:
        return out
    for card in CARD_RE.findall(markup or ""):
        f = {}
        lk = LINK_RE.search(card)
        if not lk or not ad_of(lk.group(1), host):
            continue
        f["url"], f["lang"], f["id"] = ad_of(lk.group(1), host)
        f["title"] = text(lk.group(2))
        for cls, inner in SPAN_RE.findall(card):
            f[{"job_standort": "place", "job_details_second": "level", "job_details_first": "department"}[cls]] = text(inner)
        info = INFO_RE.search(card)
        if info and "place" not in f:
            f["place"] = text(re.sub(r"<div class=\"jobcategory_details\">.*", "", info.group(1), flags=re.S))
        out.append((f["id"], f))
    return out


def record(pid, f, host, stamp):
    return {
        "source": "rexx", "tenant": host, "country": stamp,
        "ledger_id": f"rexx:{host}:{pid}", "id": pid, "url": f.get("url"),
        "title": f.get("title"), "lang": f.get("lang"),
        "place": f.get("place"), "location": f.get("location"), "department": f.get("department"),
        "level": f.get("level"), "deadline": when(f.get("deadline")),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    host = host_of(a.tenant)
    stamp = a.country_code.upper() if a.country_code else None
    rows, seen, page, start = [], set(), 0, 0
    while True:
        page += 1
        url = f"https://{host}/stellenangebote.html" + (f"?start={start}" if start else "")
        code, body = request(url, host)
        if code == 404:
            die(f"{url}: HTTP 404 — no such portal", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if page == 1 and "stellenangebote.html" not in body and "joboffer" not in body and "joboffers" not in body:
            die(f"{url}: 200 without a rexx list — not a portal, or the page changed; not an empty board", EXIT_PARTIAL)
        found = rows_of(body, host)
        ids = {pid for pid, _f in found}
        if page > 1 and ids and ids <= seen:
            die(f"page {page} (start={start}) repeats the previous page's ids — the walk ended at {th(len(rows))}", EXIT_PARTIAL)
        for pid, f in found:
            if pid in seen:
                continue
            seen.add(pid)
            rows.append(record(pid, f, host, stamp))
        nxt = NEXT_RE.search(body)
        if not nxt or not found or (a.max_pages and page >= a.max_pages):
            break
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(htmlmod.unescape(nxt.group(1))).query)
        try:
            nstart = int(q.get("start", ["0"])[0])
        except ValueError:
            die(f"{url}: the pager's next link carries no start — {nxt.group(1)[:80]}", EXIT_PARTIAL)
        if nstart <= start:
            break
        start = nstart
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if not rows:
        note(f"{host}: 0 positions — the list shows none (200); not an error.")
    else:
        note(f"{th(len(rows))} emitted over {page} page(s) for {host} — no count is stated anywhere; the pager was followed to its end" + (" (stopped by --max-pages)" if a.max_pages and page >= a.max_pages and nxt else "") + ".")
    if stamp:
        note(f"country {stamp} is the user's stamp — the list states no country.")
    note("streets, postal codes and the session id never emitted; texts scrubbed.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    host = host_of(parts.netloc) if parts.netloc else die(f"{a.url}: not a rexx ad address (https://<tenant>-portal.{DOMAIN}/<slug>-<lang>-j<id>.html)")
    got = ad_of(parts.path, host)
    if parts.scheme != "https" or not got:
        die(f"{a.url}: not a rexx ad address (https://<tenant>-portal.{DOMAIN}/<slug>-<lang>-j<id>.html)")
    url, lang, pid = got
    code, body = request(url, host)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    posts = _ldjson.postings(body)
    if not posts:
        die(f"{url}: 200 without a JobPosting — gone, or the page changed", EXIT_GONE if "stellenangebote.html" in body else EXIT_PARTIAL)
    p = posts[0]
    org = p.get("hiringOrganization") if isinstance(p.get("hiringOrganization"), dict) else {}
    jl = p.get("jobLocation")
    jl = jl[0] if isinstance(jl, list) and jl else (jl if isinstance(jl, dict) else {})
    addr = jl.get("address") if isinstance(jl.get("address"), dict) else {}
    cc = (addr.get("addressCountry") or "").strip()
    sections = {}
    for key, label in (("description", "description"), ("responsibilities", "responsibilities"), ("qualifications", "qualifications"), ("jobBenefits", "benefits")):
        v = p.get(key)
        if isinstance(v, str) and v.strip():
            sections[label] = scrub(text(v))
    et = p.get("employmentType")
    row = {
        "source": "rexx", "tenant": host,
        "country": cc.upper() if len(cc) == 2 else None, "country_name": cc if cc and len(cc) != 2 else None,
        "ledger_id": f"rexx:{host}:{pid}", "id": pid, "url": url, "lang": lang,
        "title": scrub(text(p.get("title") or "")), "company": org.get("name") or None,
        "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None,
        "employment_type": et if isinstance(et, list) else ([et] if et else None),
        "published": when(p.get("datePosted")), "expires": when(p.get("validThrough")),
        "sections": sections or None,
        "contacts_withheld": True,
    }
    if a.country_code and row["country"] and row["country"] != a.country_code.upper():
        note(f"{url}: the ad is in {row['country']}, not {a.country_code.upper()} — 0 emitted.")
        return
    print(json.dumps(row, ensure_ascii=False))
    note(f"{url}: read from the page's JobPosting; the street, the postal code and the session id never emitted; texts scrubbed.")


def main(argv=None):
    p = argparse.ArgumentParser(description="rexx systems — one tenant's portal, its list walked by the pager, its ads read from their JobPosting; streets, postal codes and session ids never emitted. Issue #482.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="one tenant's whole board (the pager walked, 100 a page)")
    j.add_argument("--tenant", required=True, help="the portal subdomain (stadtfrankfurt, msig-portal), the host, or any address on it")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the list states none)")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N list pages (0 = to the pager's end)")
    j.set_defaults(fn=cmd_jobs)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.add_argument("--country-code", dest="country_code", metavar="ISO2", help="emit only if the ad's own country is this one")
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
