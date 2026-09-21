#!/usr/bin/env python3
"""Bizneo HR (`<tenant>.bizneo.com` or the employer's own host, a Spanish ATS — one tenant at a time): the career site's `/jobs?page=N` is a server-rendered list of cards walked to its empty page; the advert page carries its fields as labelled rows and its body as HTML. Issue #489.

  bizneo.py jobs --tenant <name|host|url> [--max-pages N]
  bizneo.py ad --url https://<tenant host>/jobs/<slug>[-<uuid>]

THE TENANT is the subdomain of `bizneo.com` the employer's career site
lives on (`icp`, `lefties`, `groundforce`), or the employer's own host
when the site is served under it (`unete.icp.es` is `icp.bizneo.com`'s
advert host) — found by the family's signature `bizneo.com/jobs` in a
search engine on 2026-09-20; never composed. **A subdomain that is no
tenant answers 404 with the vendor's blueprint page** (`groundforce`:
HTTP 404, 24 433 B, «32- blueprint-2») — the adapter dies with 3 there.
`telepizza.bizneo.com`, the address the engine still lists, has no
address on two resolvers (NODATA on 1.1.1.1 and 8.8.8.8): a tenant that
has left.

THE RULES are the same 130 bytes on every host read (`icp`, `lefties`,
`groundforce`, `unete.icp.es`, md5 2f18bd135435): `User-agent: *`,
`Disallow: /admin` — the job pages are open, no agent named, no
Crawl-delay; 2 s between requests are ours.

THE LIST, MEASURED 2026-09-20 18:04 UTC and again on 2026-09-21. `/jobs`
(200, ~11 KB) carries a filter form (a `location` select of the tenant's
provinces) and `div#job-board` with `a.job-card` cards, **five a page**,
each linking to the advert — on the tenant's own host when it has one
(`https://unete.icp.es/jobs/<slug>-<uuid>`) or on `<tenant>.bizneo.com`
otherwise — with `div.title` and the `div.details` spans (the place; a
work mode such as «Presencial» when the tenant shows it). The pager
(`ul.pagination`) numbers the pages (ICP: 1 … 8); **the page past the
last answers 200 with an empty board** (`?page=9`: 0 cards, an empty-state
icon), which ends the walk. The page states no count: the adapter prints
the emitted number beside the pager's last page — «N emitted over P
pages, the pager numbered Q» — equal when the walk reached the pager's
last page and stopped on the empty one. ICP: 8 pages; Lefties: 6 cards on
one page, `?page=2` empty. The key is the address: the trailing UUID of
the slug when there is one (`…-985a54af-adbf-481f-92c6-f92c0b54c331`),
the slug itself otherwise (`sustitucion-compras-senior`).

THE ADVERT (200, ~18 KB, no JobPosting): `<h1>` title, «Publicada
<i>15 de Septiembre</i>» (no year — emitted as written), the labelled
rows `div[title="Ubicación"]`, `Categoría`, `Subcategoría`, `Sector`,
`Jornada laboral`, `Modalidad de trabajo`, `Nivel profesional`,
`Departamento` (each a `span.font-bold`), the body in `div.general-content`
blocks (the description, then «Requisitos mínimos» and the tenant's other
sections, each under a bold `<p>`), the employer's name as the `<title>`'s
prefix («ICP | Desarrollador Junior .NET»). Applying is «¡Aplica ahora!» /
«Iniciar sesión» — an account, never touched.

WITHHELD: the description scrubbed of e-mail addresses and telephone
numbers; the logo (a signed S3 URL, 5 minutes) never emitted; the share
links dropped; `contacts_withheld` on every record. The site states no
country: the family is Spanish and the tenants' places are the only
geography; `--country-code` stamps the rows with what the user names.
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

BOARD, DOMAIN = "bizneo", "bizneo.com"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

TENANT_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", re.I)
HOST_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$", re.I)
CARD_RE = re.compile(r'<a class="job-card"[^>]*href="(?P<url>[^"]+)"(?P<body>.*?)</a>', re.S)
TITLE_RE = re.compile(r'<div class="title">(.*?)</div>', re.S)
DETAILS_RE = re.compile(r'<div class="details">(.*?)</div>', re.S)
SPAN_RE = re.compile(r"<span>(.*?)</span>", re.S)
PAGER_RE = re.compile(r'<ul class="pagination">(.*?)</ul>', re.S)
PAGE_NO_RE = re.compile(r'href="[^"]*[?&]page=(\d+)"')
BOARD_RE = re.compile(r'<div id="job-board"')
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
PUB_RE = re.compile(r"Publicada\s*<i>(.*?)</i>", re.S)
ROW_RE = re.compile(r'<div title="([^"]+)" class="flex items-center[^"]*">(.*?)</div>\s*</div>', re.S)
ROW_VAL_RE = re.compile(r'<span class="font-bold[^"]*">(.*?)</span>', re.S)
CONTENT_RE = re.compile(r'<div class="general-content">(.*?)</div>\s*</div>', re.S)
SECTION_RE = re.compile(r'<p class="font-bold[^"]*">(.*?)</p>\s*<div class="general-content">(.*?)</div>', re.S)
PAGE_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
UUID_RE = re.compile(r"-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?$")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
_PACES = {}
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[bizneo] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    """(status, body) — this run's tenant host only, the guard first, 2 s apart."""
    parts = urllib.parse.urlsplit(url)
    host = parts.netloc.lower()
    if not TENANT["host"] or host != TENANT["host"]:
        die(f"{url}: not this run's Bizneo tenant ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "es,en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


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
    """`icp`, `icp.bizneo.com`, `unete.icp.es` or a URL on one of them → the host."""
    s = (arg or "").strip().lower()
    if "://" in s or "/" in s:
        s = urllib.parse.urlsplit(s if "://" in s else "https://" + s).netloc
    if not s:
        die(f"--tenant {arg!r}: name the tenant (icp), its host (icp.bizneo.com, unete.icp.es) or its /jobs URL")
    if "." not in s:
        if not TENANT_RE.match(s) or s in ("www", "hello", "help", "assets", "app", "api"):
            die(f"--tenant {arg!r}: not a tenant name (the vendor's own hosts are not a board)")
        return f"{s}.{DOMAIN}"
    if not HOST_RE.match(s) or s in ("www." + DOMAIN, DOMAIN, "hello." + DOMAIN, "help." + DOMAIN, "assets." + DOMAIN):
        die(f"--tenant {arg!r}: not a tenant host (the vendor's own site is not a board)")
    return s


def key_of(url):
    """The trailing UUID of the slug, else the slug; None when the address is not `/jobs/<slug>`."""
    parts = urllib.parse.urlsplit((url or "").strip())
    m = re.fullmatch(r"/jobs/([A-Za-z0-9._-]+)/?", parts.path)
    if not m:
        return None
    slug = m.group(1)
    u = UUID_RE.search("-" + slug + "/")
    return u.group(1) if u else slug


def parse_list(body):
    """(cards, last_page) — cards None when the page is not a career-site list."""
    if not BOARD_RE.search(body or ""):
        return None, None
    cards = []
    for m in CARD_RE.finditer(body):
        url = htmlmod.unescape(m.group("url"))
        b = m.group("body")
        t = TITLE_RE.search(b)
        d = DETAILS_RE.search(b)
        spans = [text(x) for x in SPAN_RE.findall(d.group(1))] if d else []
        spans = [x for x in spans if x]
        cards.append({"url": url, "title": text(t.group(1)) if t else None, "place": spans[0] if spans else None, "details": spans[1:] or None})
    pager = PAGER_RE.search(body)
    last = max((int(x) for x in PAGE_NO_RE.findall(pager.group(1))), default=1) if pager else 1
    return cards, last


def status_of(st, url, host):
    if st == 404:
        die(f"{url}: HTTP 404 — the vendor's blueprint page: {host} is not a Bizneo tenant, or the page is gone.", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    TENANT["host"] = host
    country = (a.country_code or "").strip().upper() or None
    seen, out, last_seen, pages = set(), [], 1, 0
    for page in range(1, a.max_pages + 1):
        url = f"https://{host}/jobs" + (f"?page={page}" if page > 1 else "")
        st, body = request(url)
        status_of(st, url, host)
        cards, last = parse_list(body)
        if cards is None:
            die(f"{url}: no `job-board` in the page — not a Bizneo career site (the vendor's own site answers 200 too).", EXIT_PARTIAL)
        pages = page
        last_seen = max(last_seen, last or 1)
        fresh = [c for c in cards if c["url"] not in seen]
        if not cards or not fresh:
            pages = page - 1           # the empty page (or a page of repeats) is not a page of the board
            break
        for c in fresh:
            seen.add(c["url"])
            k = key_of(c["url"])
            out.append({
                "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{k or c['url']}", "id": k or c["url"], "url": c["url"],
                "title": c["title"], "country": country, "place": c["place"], "details": c["details"], "contacts_withheld": True,
            })
    else:
        note(f"{a.max_pages} pages read (--max-pages) and the last still had cards — the walk is truncated.")
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    stamp = f"; country {country} stamped from --country-code (the site states none)" if country else ""
    if pages == last_seen:
        note(f"{th(n)} emitted over {pages} page(s), the pager numbered {last_seen}: equal — the walk stopped on the empty page{stamp}.")
    else:
        note(f"{th(n)} emitted over {pages} page(s), the pager numbered {last_seen}: " + ("short — the walk ended before the pager's last page" if pages < last_seen else "more pages than the pager showed") + stamp + ".")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    host = parts.netloc.lower()
    k = key_of(a.url)
    if not host or not HOST_RE.match(host) or host in (DOMAIN, "www." + DOMAIN) or not k:
        die(f"{a.url!r}: not a Bizneo advert address (https://<tenant host>/jobs/<slug>)")
    TENANT["host"] = host
    url = f"https://{host}{parts.path.rstrip('/')}"
    st, body = request(url)
    status_of(st, url, host)
    h1 = H1_RE.search(body)
    rows = {htmlmod.unescape(lab): text(" ".join(ROW_VAL_RE.findall(inner))) for lab, inner in ROW_RE.findall(body)}
    if not h1 or not rows:
        die(f"{url}: no title or no labelled rows in the page — not a Bizneo advert page, or the advert is gone.", EXIT_PARTIAL)
    contents = CONTENT_RE.findall(body)
    sections = {text(lab): text(inner) for lab, inner in SECTION_RE.findall(body)}
    pub = PUB_RE.search(body)
    pt = PAGE_TITLE_RE.search(body)
    company = htmlmod.unescape(pt.group(1)).split("|")[0].strip() if pt and "|" in pt.group(1) else None
    r = {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{k}", "id": k, "url": url,
        "title": text(h1.group(1)), "company": company or None,
        "posted": text(pub.group(1)) if pub else None,
        "place": rows.get("Ubicación"), "category": rows.get("Categoría"), "subcategory": rows.get("Subcategoría"),
        "sector": rows.get("Sector"), "schedule": rows.get("Jornada laboral"), "work_mode": rows.get("Modalidad de trabajo"),
        "level": rows.get("Nivel profesional"), "department": rows.get("Departamento"),
        "fields": {k2: v for k2, v in rows.items() if v},                 # the tenant's own labels, all of them
        "description": (scrub(text(contents[0])) if contents else None) and (scrub(text(contents[0])) or "")[:20000] or None,
        "sections": {k2: (scrub(v) or "")[:8000] for k2, v in sections.items() if v} or None,
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Bizneo HR — one tenant's career site: the /jobs list walked to its empty page, the advert's labelled rows and body; no contact. Issue #489.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the tenant's /jobs list, page after page to the empty page; the pager's last page beside the emitted number")
    s.add_argument("--tenant", required=True, help="the subdomain (icp), the host (icp.bizneo.com, unete.icp.es) or the /jobs URL")
    s.add_argument("--max-pages", type=int, default=40)
    s.add_argument("--country-code", help="ISO2 to stamp the rows with — the site states no country")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its page; description scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
