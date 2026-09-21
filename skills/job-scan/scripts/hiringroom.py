#!/usr/bin/env python3
"""Hiring Room (`<tenant>.hiringroom.com`, Latin America's ATS — one tenant at a time): the tenant's `/jobs` page states its count («49 vacantes») and fills its list by `POST /jobs/getVacanciesForPortal/<page>` — the call its own script makes — twenty cards a page to an empty page; `/jobs/get_vacancy/<id>` is the advert. Issue #492.

  hiringroom.py jobs --tenant <name|host|url>
  hiringroom.py ad --url https://<tenant>.hiringroom.com/jobs/get_vacancy/<id>

THE TENANT is the subdomain of `hiringroom.com` the employer's job portal
lives on (`kpmg`, `fravega`, `ecuaquimica`, `danec`, `lgconsultores`),
found by the family's signature `hiringroom.com/jobs` in a search engine
on 2026-09-21 — never composed. The vendor's `www`, `jobs` (the aggregated
portal) and `hiringroom.com` itself are not tenants.

THE RULES: `/robots.txt` on a tenant answers HTTP 404 with the
application's own page (81 896 B) — no rules file, `certain: True`, open;
the vendor's `hiringroom.com` publishes 149 B closing a few non-job paths
(the issue's reading of 13.09). No Crawl-delay; 2 s between requests are
ours.

THE LIST, MEASURED 2026-09-21 06:34–06:36 UTC. `/jobs` (200; KPMG
Argentina 220 869 B, Frávega 124 516 B) prints the count — «Ver 49
vacantes» — and the first twenty cards, and its `main.js` fills the list
by `POST /jobs/getVacanciesForPortal/<page>` with `typePortal` (the page
declares it: `typePortal = "external"`; a microsite adds `microSiteId`)
and the filters the user ticks (none here): the answer is JSON —
`result: success`, `data.total_vacancies` (49), `data.htmlContent` (the
cards), `data.pagination`, `data.paginationLabel` («21-40 de 49
vacantes»), `data.filtersOptions`. KPMG: pages 1–3 held 20, 20, 9 = 49,
page 4 answered «61-49 de 49» with no card — the empty page ends the walk.
Frávega: «0 vacantes», an empty board said so. A card: `a[href="/jobs/get_vacancy/<24-hex>"]`,
`h4.name__vacancy` the title, the location line (`hr-Location-pin`), the
area line (`hr-Work-area`, «Área / Subárea»), the tags (`tag-vacancy`:
Full-time, Híbrido / Remoto / Presencial, the seniority) and a relative
age («Hace 2 meses»). The key is the 24-hex id.

THE ADVERT (200, 140 660 B, no JobPosting): `div.hero__title h2` the
title, the location and area lines, the three hero tags, the relative
age, then `h6` sections each with a `div.job-description-content`:
«Descripción del puesto», «Requisitos», «Beneficios» (HTML). The employer
is the page's `<title>` («… en KPMG Argentina») or the list's
(«¡Oportunidades de Empleo en KPMG Argentina!»). «Postularse» links the
vendor's form on `hiringroom.com` — never followed, never emitted.

WITHHELD: the sections scrubbed of e-mail addresses and telephone
numbers; the apply link, the banners and logos never emitted;
`contacts_withheld` on every record. The country is the last element of
the location line («…, Argentina») when the line ends with a name this
adapter knows; `--country-code` stamps what the user names otherwise.
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

BOARD, DOMAIN = "hiringroom", "hiringroom.com"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
NOT_TENANTS = {"www", "jobs", "app", "api", "admin", "login", "help", "ayuda"}
PER_PAGE = 20

TENANT_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", re.I)
COUNT_RE = re.compile(r"Ver\s*(?:<[^>]+>\s*)*(\d[\d.]*)\s*(?:<[^>]+>\s*)*vacantes?", re.I | re.S)
TYPE_RE = re.compile(r"typePortal\s*=\s*[\"']([a-z_]+)[\"']")
MICRO_RE = re.compile(r"microSiteId\s*=\s*[\"']?([A-Za-z0-9_-]+)")
CARD_RE = re.compile(r'<a href="(?:https?://[a-z0-9.-]+)?/jobs/get_vacancy/(?P<id>[0-9a-f]{24})"[^>]*>(?P<body>.*?)</a>', re.S)
TITLE_RE = re.compile(r'<h4[^>]*name__vacancy[^>]*>(.*?)</h4>', re.S)
LOC_RE = re.compile(r'<i class="[^"]*hr-Location-pin[^"]*"></i>(.*?)</span>', re.S)
AREA_RE = re.compile(r'<i class="[^"]*hr-Work-area[^"]*"></i>(.*?)</span>', re.S)
TAG_RE = re.compile(r'<i class="(?P<icon>[^"]*)"></i>\s*(?P<text>[^<]+)</span>', re.S)
AGE_RE = re.compile(r'(?:vacancy-time|hero__time-new)[^>]*>\s*(Hace[^<]+)<', re.S)
HERO_TITLE_RE = re.compile(r'<div class="hero__title">\s*<h2[^>]*>(.*?)</h2>', re.S)
HERO_LOC_RE = re.compile(r'<span class="hr-Location-pin"></span>(.*?)</p>', re.S)
HERO_AREA_RE = re.compile(r'<span class="hr-Work-area"></span>(.*?)</p>', re.S)
HERO_TAG_RE = re.compile(r'<div class="(?:commonstxt )?hero__tag">\s*<span class="[^"]*\b(hr-Clock|hr-Company|hr-Remote|hr-Campus)\b[^"]*"></span>\s*([^<]+)', re.S)
SECTION_RE = re.compile(r'<h6[^>]*>\s*<i[^>]*></i>\s*(?P<label>[^<]+?)\s*</h6>\s*<div class="[^"]*job-description-content[^"]*">(?P<body>.*?)</div>\s*(?=<!--|<h6|<div class="main__button)', re.S)
PAGE_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
COUNTRIES = {"argentina": "AR", "chile": "CL", "colombia": "CO", "méxico": "MX", "mexico": "MX", "perú": "PE", "peru": "PE", "uruguay": "UY", "paraguay": "PY", "ecuador": "EC", "bolivia": "BO", "brasil": "BR", "brazil": "BR", "costa rica": "CR", "panamá": "PA", "panama": "PA", "guatemala": "GT", "honduras": "HN", "el salvador": "SV", "nicaragua": "NI", "república dominicana": "DO", "venezuela": "VE", "españa": "ES", "estados unidos": "US"}
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
_PACES = {}
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[hiringroom] {msg}", file=sys.stderr)


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


def request(url, data=None):
    """(status, body) — this run's tenant only, the guard first, 2 s apart; `data` makes it the POST the page's own script sends."""
    parts = urllib.parse.urlsplit(url)
    host = parts.netloc.lower()
    if not TENANT["host"] or host != TENANT["host"] or not host.endswith("." + DOMAIN):
        die(f"{url}: not this run's Hiring Room tenant ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()
    headers = {"User-Agent": UA, "Accept": "application/json, text/html", "Accept-Language": "es,en"}
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["X-Requested-With"] = "XMLHttpRequest"
    req = urllib.request.Request(wire_url(url), data=body, headers=headers)
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
    """`kpmg`, `kpmg.hiringroom.com` or a URL on it → the host."""
    s = (arg or "").strip().lower()
    if "://" in s or "/" in s:
        s = urllib.parse.urlsplit(s if "://" in s else "https://" + s).netloc
    if not s:
        die(f"--tenant {arg!r}: name the tenant (kpmg), its host or its /jobs URL")
    if "." not in s:
        if not TENANT_RE.match(s) or s in NOT_TENANTS:
            die(f"--tenant {arg!r}: not a tenant (the vendor's own hosts are not a board)")
        return f"{s}.{DOMAIN}"
    sub = s[: -len("." + DOMAIN)] if s.endswith("." + DOMAIN) else None
    if not sub or not TENANT_RE.match(sub) or sub in NOT_TENANTS:
        die(f"--tenant {arg!r}: not a Hiring Room tenant host (<tenant>.{DOMAIN})")
    return s


def country_of(location, stamp=None):
    last = (location or "").rsplit(",", 1)[-1].strip().lower()
    return COUNTRIES.get(last) or stamp


def status_of(st, url, host):
    if st == 404:
        die(f"{url}: HTTP 404 — {host} is not a Hiring Room tenant, or the page is gone.", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)


def parse_cards(html):
    rows = []
    for m in CARD_RE.finditer(html or ""):
        b = m.group("body")
        t = TITLE_RE.search(b)
        loc = LOC_RE.search(b)
        area = AREA_RE.search(b)
        tags = [(i, text(v)) for i, v in TAG_RE.findall(b)]
        age = AGE_RE.search(b)
        rows.append({"id": m.group("id"), "title": text(t.group(1)) if t else None, "location": text(loc.group(1)) if loc else None, "area": text(area.group(1)) if area else None,
                     "schedule": next((v for i, v in tags if "hr-Clock" in i), None), "modality": next((v for i, v in tags if "hr-Company" in i or "hr-Remote" in i), None),
                     "seniority": next((v for i, v in tags if "hr-Campus" in i), None), "age": text(age.group(1)) if age else None})
    return rows


def company_of(body):
    pt = PAGE_TITLE_RE.search(body or "")
    if not pt:
        return None
    t = htmlmod.unescape(pt.group(1)).strip()
    m = re.search(r"(?:empleo en|empleo:.*? en)\s+(.+?)\s*!?\s*(?:- Hiring Room)?\s*$", t, re.S | re.I)
    return " ".join(m.group(1).split()).rstrip("!") if m else None


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    TENANT["host"] = host
    stamp = (a.country_code or "").strip().upper() or None
    url = f"https://{host}/jobs"
    st, body = request(url)
    status_of(st, url, host)
    tm = TYPE_RE.search(body or "")
    cm = COUNT_RE.search(body or "")
    if not tm or "getVacanciesForPortal" not in body and cm is None:
        die(f"{url}: no `typePortal` in the page — not a Hiring Room job portal, or the page changed shape.", EXIT_PARTIAL)
    stated = int(cm.group(1).replace(".", "")) if cm else None
    company = company_of(body)
    params = {"typePortal": tm.group(1)}
    mm = MICRO_RE.search(body)
    if tm.group(1) == "microsite" and mm:
        params["microSiteId"] = mm.group(1)
    seen, out, total = set(), [], None
    for page in range(1, a.max_pages + 1):
        params["selectedPage"] = page
        purl = f"https://{host}/jobs/getVacanciesForPortal/{page}"
        st, ans = request(purl, params)
        status_of(st, purl, host)
        try:
            j = json.loads(ans)
        except ValueError:
            die(f"{purl}: not JSON — the list call answered something else.", EXIT_PARTIAL)
        d = j.get("data") or {}
        if j.get("result") != "success" or "htmlContent" not in d:
            die(f"{purl}: the list call did not answer `success` with `htmlContent` ({str(j)[:120]}).", EXIT_PARTIAL)
        if isinstance(d.get("total_vacancies"), int):
            total = d["total_vacancies"]
        cards = parse_cards(d["htmlContent"])
        fresh = [c for c in cards if c["id"] not in seen]
        if not fresh:
            break                       # the empty page (KPMG page 4: «61-49 de 49») ends the walk
        for c in fresh:
            seen.add(c["id"])
            out.append({"source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{c['id']}", "id": c["id"], "url": f"https://{host}/jobs/get_vacancy/{c['id']}",
                        "title": c["title"], "company": company, "country": country_of(c["location"], stamp), "location": c["location"], "area": c["area"],
                        "schedule": c["schedule"], "modality": c["modality"], "seniority": c["seniority"], "posted_relative": c["age"], "contacts_withheld": True})
        if total is not None and len(out) >= total:
            break
    else:
        note(f"{a.max_pages} pages read (--max-pages) and the last still had cards — the walk is truncated.")
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    ref = total if total is not None else stated
    src = "the list call states" if total is not None else "the page prints"
    tail = f"; country {stamp} stamped where the location names none" if stamp else ""
    if ref is None:
        note(f"{th(n)} emitted — no count stated{tail}.")
    elif n == ref:
        note(f"{th(n)} emitted — {src} {th(ref)}: equal{tail}.")
    else:
        note(f"{th(n)} emitted — {src} {th(ref)}: {th(abs(ref - n))} " + ("short" if ref > n else "more emitted than stated") + tail + ".")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    host = parts.netloc.lower()
    m = re.fullmatch(r"/jobs/get_vacancy/([0-9a-f]{24})/?", parts.path)
    sub = host[: -len("." + DOMAIN)] if host.endswith("." + DOMAIN) else None
    if not sub or not TENANT_RE.match(sub) or sub in NOT_TENANTS or not m:
        die(f"{a.url!r}: not a Hiring Room advert address (https://<tenant>.{DOMAIN}/jobs/get_vacancy/<id>)")
    TENANT["host"] = host
    jid = m.group(1)
    url = f"https://{host}/jobs/get_vacancy/{jid}"
    st, body = request(url)
    status_of(st, url, host)
    ht = HERO_TITLE_RE.search(body or "")
    if not ht or not text(ht.group(1)):
        die(f"{url}: no `hero__title` in the page — not a Hiring Room advert page, or the advert is gone.", EXIT_PARTIAL)
    loc = HERO_LOC_RE.search(body)
    area = HERO_AREA_RE.search(body)
    tags = {i: text(v) for i, v in HERO_TAG_RE.findall(body)}
    age = AGE_RE.search(body)
    sections = {}
    for lab, sec in SECTION_RE.findall(body):
        k = " ".join(htmlmod.unescape(lab).split())
        if k and k not in sections:
            sections[k] = scrub(text(sec))
    location = text(loc.group(1)) if loc else None
    r = {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{jid}", "id": jid, "url": url,
        "title": text(ht.group(1)), "company": company_of(body),
        "country": country_of(location, (a.country_code or "").strip().upper() or None), "location": location, "area": text(area.group(1)) if area else None,
        "schedule": tags.get("hr-Clock"), "modality": tags.get("hr-Company") or tags.get("hr-Remote"), "seniority": tags.get("hr-Campus"),
        "posted_relative": text(age.group(1)) if age else None,
        "description": (sections.get("Descripción del puesto") or next(iter(sections.values()), None) or "")[:20000] or None,
        "sections": {k: (v or "")[:8000] for k, v in sections.items() if v} or None,
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Hiring Room — one tenant's job portal: the list by the call its page makes, twenty a page to the empty page, the count it states beside; the advert page; the apply link never followed. Issue #492.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the tenant's /jobs, then its list call page after page; the stated total beside the emitted number")
    s.add_argument("--tenant", required=True, help="the subdomain (kpmg), the host or the /jobs URL")
    s.add_argument("--max-pages", type=int, default=50)
    s.add_argument("--country-code", help="ISO2 to stamp rows whose location names no country this adapter knows")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its page (/jobs/get_vacancy/<id>); sections scrubbed")
    d.add_argument("--url", required=True)
    d.add_argument("--country-code")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
