#!/usr/bin/env python3
"""softgarden — an ATS, one tenant at a time: the tenant's «Karriere Board» on `<tenant>.softgarden.io/<lang>/vacancies` renders its WHOLE list in the page (the search, the paging and the count are client-side over it, `complete_job_id_list` is the page's own count), and each ad on `/job/<id>/<slug>` carries one schema.org JobPosting; `/*/widgets/`, `/api/`, `/rest/` and `/apply/` are refused in writing and never asked. Issue #480.

  softgarden.py jobs --tenant gruen [--lang de] [--country-code DE]        the tenant's board (1 request)
  softgarden.py jobs --tenant https://infodas.softgarden.io/de/widgets/jobs   (any address on the tenant's host names it; the widget path itself is refused and never asked)
  softgarden.py ad --url "https://gruen.softgarden.io/job/66860360/Duales-Studium-Elektrotechnik-B.Eng.-?jobDbPVId=285261432&l=de"

WHAT IT IS. softgarden e-recruiting (Berlin) is the applicant-tracking system behind a German
employer's «Karriere Board» — SMEs, Mittelstand, hospitals (INFODAS, GRÜN Software Group, HOST
GmbH / Universitätsmedizin Frankfurt). Its signature: `<tenant>.softgarden.io`. **One adapter
covers every employer that uses it; the user names the tenant** by its subdomain (`gruen`), its
host, or any address on it.

THE RULES. Every tenant publishes the same file (273 B): `*` refused `/just-hire/`, `/hrFrontend/`,
`/hrManagement/`, `/hrd/`, `/hrc/`, `/api/`, `/strategy-board/`, `/apply/`, `/apply-choice*`,
`/rest/`, **`/*/widgets/`** and `/wicket/bookmarkable/`; no Crawl-delay, 2 s is ours. So the
widget address the search engines index (`/de/widgets/jobs`) is a refused route — the adapter
reads the board itself, `/<lang>/vacancies`, which the root redirects to and which the file
leaves open; `/job/<id>/<slug>` is open too. The guard is taken on the exact path.

THE BOARD, IN THE PAGE. `/de/vacancies` (200; 34–56 KB for 7–31 positions) is a Wicket page
whose search form is client-side (`jobSearchLive.js` filters, orders and pages the cards already
in the DOM, 10 a screen — nothing is fetched): `var complete_job_id_list = jobs_selected =
[49734098, …]` is **the page's own list of every position, and its length the stated count**;
each `<div class="matchElement" id="job_id_<id>">` carries `matchValue` cells whose class names
the field — `title` (with the link `../job/<id>/<slug>?jobDbPVId=<n>&l=de`),
`ProjectGeoLocationCity`, `sg_company_id`, `audience`, `date` (dd.mm.yy), `jobcategory` — the
columns a tenant shows are the tenant's choice. The count printed beside the emitted count is
the id list's length; a card without an id in that list, or an id without a card, is said.

THE AD. `/job/<id>/<slug>?jobDbPVId=…&l=de` (200, ~40 KB) carries one JobPosting — title,
description (HTML), datePosted and validThrough (ISO with an offset), employmentType (a list),
hiringOrganization, jobLocation (streetAddress, postalCode, locality, region, country as a
NAME — «Deutschland»), baseSalary (0–0 when not stated), identifier (the organization's
`#organization` URL) — and a «Kontakt» footer with the recruiter's name and e-mail. **Emitted:
the posting's text, scrubbed; locality, region, country name. Never: the street, the postal
code, the contact footer, the logo, a salary of 0, any e-mail address or telephone in the
text.** `contacts_withheld` on every record; the application (`jobdb.softgarden.de/…/
applyonline`) never touched.

`--country-code` STAMPS: the board states no country on its cards (the ad states a name), so
the code is written on every record and the run says it is the user's, not the page's.

Measured 2026-09-21 07:06–07:09 UTC by the declared client, the guard on the exact path, two
reads each: `host.softgarden.io` (7, `/` → `/de/vacancies`, identical bodies), `gruen` (31),
`infodas` (22; `/de/vacancies` directly); the GRÜN ad 200 ×2 (40 471 B, one JobPosting, one
e-mail in the footer); `zzz-not-a-tenant-2026.softgarden.io` 404 «Unknown subdomain.» — not a
tenant, exit 3.
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

DOMAIN = "softgarden.io"
NOT_TENANTS = ("www", "app", "static", "api", "jobdb", "support")
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")   # «030 884 940 400», «+49 (0)30 …»: 8+ digits with the separators German numbers use
DATE_RE = re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b")                       # «ab 01.10.2026» is a date, not a telephone — it stays
ID_LIST_RE = re.compile(r"complete_job_id_list\s*=\s*(?:jobs_selected\s*=\s*)?\[([\d\s,]*)\]")
CARD_RE = re.compile(r'<div class="matchElement" id="job_id_(\d+)">(.*?)(?=<div class="matchElement"|<div class="pagination)', re.S)
CELL_RE = re.compile(r'<div[^>]*class="matchValue ([A-Za-z_]+)"[^>]*>(.*?)</div>\s*(?=<div[^>]*class="matchValue|\s*$)', re.S)
LINK_RE = re.compile(r'<a href="([^"]+)"')
AD_RE = re.compile(r"^/job/(\d+)/[^/]*$")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[softgarden] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def host_of(arg):
    """`gruen`, `gruen.softgarden.io` or any URL on it → the tenant's host; the vendor's own hosts refused."""
    s = arg.strip()
    if "://" in s or "." in s.split("/")[0]:
        parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
        host = parts.netloc.lower()
    else:
        host = f"{s.lower()}.{DOMAIN}"
    m = re.match(r"^([a-z0-9](?:[a-z0-9\-]*[a-z0-9])?)\." + re.escape(DOMAIN) + "$", host)
    if not m:
        die(f"{arg}: a tenant is <tenant>.{DOMAIN} — gruen, or gruen.{DOMAIN}, or an address on it")
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
    """`15.09.25` / `15.09.2025` → ISO; `2026-09-20T15:15:12.048+02:00` → its date; anything else as read."""
    s = (s or "").strip()
    m = re.match(r"^(\d{1,2})\.(\d{1,2})\.(\d{2}|\d{4})$", s)
    if m:
        y = int(m.group(3))
        return f"{y + 2000 if y < 100 else y:04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    if re.match(r"^\d{4}-\d{2}-\d{2}", s):
        return s[:10]
    return s or None


def cards_of(markup, host, lang):
    """The board's cards → [(id, fields)]; `fields` keyed by the cell's class, the title's link resolved."""
    out = []
    for pid, body in CARD_RE.findall(markup or ""):
        f = {}
        for cls, inner in CELL_RE.findall(body):
            if cls == "title":
                m = LINK_RE.search(inner)
                if m:
                    href = htmlmod.unescape(m.group(1))
                    f["url"] = urllib.parse.urljoin(f"https://{host}/{lang}/vacancies", href)
            f[cls] = text(inner)
        out.append((pid, f))
    return out


def board(host, lang):
    url = f"https://{host}/{lang}/vacancies"
    code, body = request(url, host)
    if code == 404:
        die(f"{url}: HTTP 404 — {DOMAIN} knows no such tenant («Unknown subdomain.»)", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    m = ID_LIST_RE.search(body)
    if not m:
        die(f"{url}: 200 without `complete_job_id_list` — not a softgarden board, or the page changed; not an empty board", EXIT_PARTIAL)
    ids = [x.strip() for x in m.group(1).split(",") if x.strip()]
    return ids, cards_of(body, host, lang)


def record(pid, f, host, lang, stamp):
    return {
        "source": "softgarden", "tenant": host, "country": stamp,
        "ledger_id": f"softgarden:{host}:{pid}", "id": pid,
        "url": f.get("url") or f"https://{host}/job/{pid}/?l={lang}",
        "title": f.get("title"), "company": f.get("sg_company_id"),
        "place": f.get("ProjectGeoLocationCity"), "audience": f.get("audience"), "category": f.get("jobcategory"),
        "published": when(f.get("date")),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    host = host_of(a.tenant)
    lang = (a.lang or "de").strip().lower()
    if not re.match(r"^[a-z]{2}$", lang):
        die(f"--lang {a.lang}: two letters (de, en)")
    stamp = a.country_code.upper() if a.country_code else None
    ids, cards = board(host, lang)
    by = dict(cards)
    rows, seen = [], set()
    for pid in ids:
        if pid in by and pid not in seen:
            seen.add(pid)
            rows.append(record(pid, by[pid], host, lang, stamp))
    extra = [pid for pid, _f in cards if pid not in seen]
    for pid in extra:
        seen.add(pid)
        rows.append(record(pid, by[pid], host, lang, stamp))
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if not ids and not cards:
        note(f"{host}: 0 positions — the board's id list is empty and it shows no card (200); not an error.")
    else:
        missing = len([pid for pid in ids if pid not in by])
        note(f"{th(len(rows))} emitted, the page's own list names {th(len(ids))} for {host}"
             + (f" — {th(missing)} named without a card" if missing else "") + (f", {th(len(extra))} card(s) not in the list" if extra else "") + ".")
    if stamp:
        note(f"country {stamp} is the user's stamp — the board states no country on its cards.")
    note("the ad's contact footer, street and postal code never emitted; texts scrubbed.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    host = host_of(parts.netloc) if parts.netloc else die(f"{a.url}: not a softgarden ad address (https://<tenant>.{DOMAIN}/job/<id>/<slug>)")
    m = AD_RE.match(parts.path)
    if parts.scheme != "https" or not m:
        die(f"{a.url}: not a softgarden ad address (https://<tenant>.{DOMAIN}/job/<id>/<slug>)")
    pid = m.group(1)
    q = urllib.parse.parse_qs(parts.query)
    keep = {k: v[0] for k, v in q.items() if k in ("jobDbPVId", "l")}       # the page's own parameters, nothing else
    url = f"https://{host}{parts.path}" + (("?" + urllib.parse.urlencode(keep)) if keep else "")
    code, body = request(url, host)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    posts = _ldjson.postings(body)
    if not posts:
        die(f"{url}: 200 without a JobPosting — gone, or the page changed", EXIT_GONE if "Not Found" in body[:400] else EXIT_PARTIAL)
    p = posts[0]
    org = p.get("hiringOrganization") if isinstance(p.get("hiringOrganization"), dict) else {}
    jl = p.get("jobLocation")
    jl = jl[0] if isinstance(jl, list) and jl else (jl if isinstance(jl, dict) else {})
    addr = jl.get("address") if isinstance(jl.get("address"), dict) else {}
    et = p.get("employmentType")
    cn = (addr.get("addressCountry") or "").strip() or None
    row = {
        "source": "softgarden", "tenant": host,
        "country": cn.upper() if cn and len(cn) == 2 else None, "country_name": cn if cn and len(cn) != 2 else None,
        "ledger_id": f"softgarden:{host}:{pid}", "id": pid, "url": url,
        "title": scrub(text(p.get("title") or "")),
        "company": org.get("name") or None,
        "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None,
        "employment_type": et if isinstance(et, list) else ([et] if et else None),
        "published": when(p.get("datePosted")), "expires": when(p.get("validThrough")),
        "description": scrub(text(p.get("description") or "")),
        "contacts_withheld": True,
    }
    print(json.dumps(row, ensure_ascii=False))
    note(f"{url}: read from the page's JobPosting; the contact footer, street, postal code and logo never emitted; text scrubbed.")


def main(argv=None):
    p = argparse.ArgumentParser(description="softgarden — one tenant's Karriere Board, rendered whole in its page; the refused widget/API routes never asked; contacts and streets never emitted. Issue #480.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="one tenant's whole board (1 request)")
    j.add_argument("--tenant", required=True, help="the subdomain (gruen), the host, or any address on it")
    j.add_argument("--lang", default="de", help="the board's language path (de, en) — default de")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the board states none)")
    j.set_defaults(fn=cmd_jobs)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
