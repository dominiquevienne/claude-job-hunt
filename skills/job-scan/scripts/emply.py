#!/usr/bin/env python3
"""Emply (a Danish ATS, Paychex since 2026 — one tenant at a time): the employer's career site on `<tenant>.career.emply.com` fills its vacancy section by `POST /api/integration/vacancy/get-page` with the config the page carries (`sectionId`, `langCode`, `count`, `offset`), the answer states `count`; the vacancy page `/ad/<slug>/<shortId>` is server-rendered. Issue #468.

  emply.py jobs --tenant <name> [--page /ledige-stillinger] [--country-code ISO2] [--max-pages N]
  emply.py ad --url https://<tenant>.career.emply.com/ad/<slug>/<shortId>

THE TENANT is the subdomain of `career.emply.com` the employer's career
site lives on (`aarhus`, `aalborg`, `toender`, `via`), found by the
family's signature, never composed. The site's root usually IS the vacancy
list (`aalborg`, `aarhus`); when the root carries no vacancy section the
adapter tries `/ledige-stillinger` and `/vacancies`, or reads the page the
user names with `--page`. Rules (read 2026-09-20 on four tenants): `User-agent:
* / Allow: /`, no Crawl-delay; 2 s between requests are ours.

THE ROUTE: the page's script declares `var config = { count: N, filters:
[], langCode: languageKey, offset: 0, searchText: '', sectionId: '<guid>',
sortByProjectDataId: 'deadline', sortAscending: true, light: false,
isJobAgent: false, siteId: null }` and POSTs it as JSON to
`/api/integration/vacancy/get-page`; the answer is `{count, vacancies[]}`
— `count` the stated total, `offset` advancing by the vacancies received
(measured 2026-09-20: Aarhus Kommune 35 stated, 30 + 5). The vacancy:
`id`, `shortId`, `titleAsUrl` (the page builds `/ad/<titleAsUrl>/<shortId>`
and `/apply/…`), `number`, `created`, `published`, `deadline`,
`department`, `location` («Kingosvej 1-7, 8230, Åbyhøj, Denmark» — the
street and postcode are NOT emitted), `talentPool`, `externalCseAdLink`,
and `translations[]` with `title`, `content` (HTML, the whole advert) and
`factDatas` (the tenant's own labelled fields). One tenant (`au`, Aarhus
University) answers 403 «Checking search engine crawler…» to the declared
client — a challenge, consigned, not crossed.

WITHHELD: the street and the postcode of the workplace (the `location`
trimmed to city and country, in the row and in the location fact); the
facts that name a contact («1. Kontaktperson», telephone, e-mail);
descriptions scrubbed of e-mail addresses
and telephone numbers (the adverts name a contact with both); the
application (`/apply/…`, a form with reCAPTCHA) never touched;
`contacts_withheld` on every record.
"""

import argparse
import html as htmlmod
import http.cookiejar
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

BOARD = "emply"
DOMAIN = "career.emply.com"
API_PATH = "/api/integration/vacancy/get-page"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
LIST_PAGES = ("/", "/ledige-stillinger", "/vacancies")

TENANT_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", re.I)
LANG_RE = re.compile(r"var languageKey\s*=\s*'([^']*)'")
CONFIG_RE = re.compile(r"var config = \{\s*count:\s*(\d+),\s*filters:\s*\[\],\s*langCode:\s*languageKey,\s*offset:\s*0,\s*searchText:\s*'',\s*sectionId:\s*'([0-9a-fA-F-]{36})',\s*sortByProjectDataId:\s*'([^']*)',\s*sortAscending:\s*(true|false)", re.S)
AD_PATH_RE = re.compile(r"^/ad/([^/]+)/([A-Za-z0-9]+)/?$")
TITLE_RE = re.compile(r'<h1 class="css_headline"[^>]*>(.*?)</h1>', re.S)
BODY_OPEN_RE = re.compile(r'<div class="csa_jobadText"[^>]*>')
DIV_RE = re.compile(r"<div\b|</div>", re.I)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{6,}\d(?!\w)")
CONTACT_FACT_RE = re.compile(r"kontakt|contact|telefon|phone|mail|ansvarlig|recruiter|rekrutter", re.I)   # a fact naming a person or how to reach them
STREET_RE = re.compile(r"\d")            # a segment with a digit is a street («Kingosvej 1-7») or a postcode («8230») — both left behind
COUNTRIES = {"denmark": "DK", "danmark": "DK", "norway": "NO", "norge": "NO", "sweden": "SE", "sverige": "SE", "germany": "DE", "deutschland": "DE",
             "tyskland": "DE", "finland": "FI", "iceland": "IS", "island": "IS", "united kingdom": "GB", "netherlands": "NL", "greenland": "GL", "grønland": "GL"}
_PACES = {}
_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_JAR))
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[emply] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, data=None, headers=None):
    """The tenant's host and no other, one cookie jar (the page's SERVERID cookie is replayed on the API call, as the page does)."""
    parts = urllib.parse.urlsplit(url)
    host = parts.netloc.lower()
    if not TENANT["host"] or host != TENANT["host"] or not host.endswith("." + DOMAIN):
        die(f"{url}: not this run's Emply tenant ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()
    h = {"User-Agent": UA, "Accept": "application/json" if data is not None else "text/html,application/xhtml+xml", "Accept-Language": "da,en"}
    h.update(headers or {})
    req = urllib.request.Request(wire_url(url), headers=h, data=data, method="POST" if data is not None else "GET")
    try:
        with _OPENER.open(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        try:
            return e.code, decode_body(e.read(), e.headers)[0]
        except Exception:                                  # noqa: BLE001 — the code is what matters
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


def inner_div(markup, open_re):
    m = open_re.search(markup or "")
    if not m:
        return None
    depth, pos = 1, m.end()
    for t in DIV_RE.finditer(markup, m.end()):
        depth += 1 if t.group(0).lower().startswith("<div") else -1
        if depth == 0:
            return markup[pos:t.start()]
    return markup[pos:]


def without_address(location):
    """«Kingosvej 1-7, 8230, Åbyhøj, Denmark» → ["Åbyhøj", "Denmark"] — the street and the postcode left behind."""
    parts = [p.strip() for p in (location or "").split(",") if p.strip()]
    return [p for p in parts if not STREET_RE.search(p)]


def place_of(location):
    """(city, country code, country name) of a location label."""
    kept = without_address(location)
    country_name = kept[-1] if kept and kept[-1].lower() in COUNTRIES else None
    if country_name:
        kept = kept[:-1]
    return (kept[-1] if kept else None), (COUNTRIES.get(country_name.lower()) if country_name else None), country_name


def tenant_of(arg):
    s = (arg or "").strip().lower()
    if "://" in s or "/" in s:
        s = urllib.parse.urlsplit(s if "://" in s else "https://" + s).netloc
    if s.endswith("." + DOMAIN):
        s = s[: -len("." + DOMAIN)]
    if not s or "." in s or not TENANT_RE.match(s) or s in ("www", "hr"):
        die(f"{arg!r}: a tenant is the subdomain of {DOMAIN} the employer's career site lives on (aarhus, aalborg), found by the family's signature, never composed")
    return f"{s}.{DOMAIN}"


def translation_of(v, lang):
    ts = [t for t in (v.get("translations") or []) if isinstance(t, dict)]
    for t in ts:
        if lang and t.get("languageKey") == lang:
            return t
    return ts[0] if ts else {}


def row(v, host, lang, stamp):
    t = translation_of(v, lang)
    city, cc, cn = place_of(v.get("location"))
    facts = {}
    for f in (t.get("factDatas") or []):
        if not isinstance(f, dict) or not f.get("title") or not f.get("text") or f.get("factId") == "job_title":
            continue
        if CONTACT_FACT_RE.search(f["title"]) or CONTACT_FACT_RE.search(str(f.get("factId") or "")):
            continue                                        # «1. Kontaktperson» and its kind: the contact, withheld
        val = f["text"]
        if val == v.get("location"):                        # the location fact repeats the address — trimmed the same way
            val = ", ".join(without_address(val)) or None
        if val:
            facts[f["title"]] = val
    url = v.get("externalCseAdLink") or f"https://{host}/ad/{v.get('titleAsUrl')}/{v.get('shortId')}"
    return {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{v.get('shortId') or v.get('id')}", "id": v.get("shortId") or v.get("id"),
        "number": v.get("number"), "url": url, "title": t.get("title") or v.get("title"),
        "department": v.get("department") or None, "place": city, "country": cc or stamp, "country_name": cn,
        # the street and the postcode in `location` are the workplace's address and are not emitted
        "published": v.get("published"), "closes": v.get("deadline"), "talent_pool": bool(v.get("talentPool")),
        "language": t.get("languageKey"), "fields": facts,
        "description": (scrub(text(t.get("content"))) or "")[:20000] or None,
        "contacts_withheld": True,
    }


def list_page(host, pages):
    """The first page that carries a vacancy section: its `sectionId`, the page size the section uses, the language."""
    for path in pages:
        url = f"https://{host}{path}"
        st, body = request(url)
        if st == 404:
            continue
        if st in (403, 429):
            die(f"{url}: HTTP {st} — the operator answering directly (Aarhus University's tenant shows «Checking search engine crawler…», a challenge); stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
        if st != 200:
            die(f"{url}: HTTP {st}", EXIT_PARTIAL)
        secs = CONFIG_RE.findall(body)
        if secs:
            count, sid, sort, asc = max(secs, key=lambda s: int(s[0]))
            lang = (LANG_RE.search(body) or [None, "da-DK"])[1] if LANG_RE.search(body) else "da-DK"
            return url, sid, int(count), sort, asc == "true", lang
        if API_PATH not in body and "emply" not in body.lower():
            die(f"{url}: not an Emply career site (no vacancy section, no `{API_PATH}` in the page).", EXIT_PARTIAL)
    die(f"{host}: no vacancy section on {', '.join(pages)} — name the list page with --page.", EXIT_PARTIAL)


def get_page(host, referer, sid, count, sort, asc, lang, offset):
    cfg = {"count": count, "filters": [], "langCode": lang, "offset": offset, "searchText": "", "sectionId": sid,
           "sortByProjectDataId": sort, "sortAscending": asc, "light": False, "isJobAgent": False, "siteId": None}
    url = f"https://{host}{API_PATH}"
    st, body = request(url, data=json.dumps(cfg).encode(), headers={"Content-Type": "application/json", "Referer": referer, "X-Requested-With": "XMLHttpRequest"})
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st} at offset {offset}", EXIT_PARTIAL)
    try:
        j = json.loads(body)
    except ValueError:
        die(f"{url}: not JSON ({len(body)} characters) at offset {offset}", EXIT_PARTIAL)
    if not isinstance(j, dict) or "count" not in j or not isinstance(j.get("vacancies"), list):
        die(f"{url}: no `count` / `vacancies` in the answer — not the page's response shape.", EXIT_PARTIAL)
    return j["count"], [v for v in j["vacancies"] if isinstance(v, dict)]


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    TENANT["host"] = host
    pages = (a.page,) if a.page else LIST_PAGES
    referer, sid, size, sort, asc, lang = list_page(host, pages)
    stamp = (a.country_code or "").strip().upper() or None
    total, vs = get_page(host, referer, sid, size, sort, asc, lang, 0)
    rows, seen, walked, offset = [], set(), 1, 0
    while True:
        new = 0
        for v in vs:
            key = v.get("shortId") or v.get("id")
            if not key or key in seen:
                continue
            seen.add(key)
            rows.append(row(v, host, lang, stamp))
            new += 1
        if vs and new == 0:
            die(f"{host}: the call at offset {offset} repeated the previous one — the offset is not advancing; {th(len(rows))} kept of the {th(total)} stated.", EXIT_PARTIAL)
        offset += len(vs)
        last = -(-(total or 0) // max(size, 1))
        if not vs or offset >= (total or 0) or walked >= last or (a.max_pages and walked >= a.max_pages):
            break
        walked += 1
        _t, vs = get_page(host, referer, sid, size, sort, asc, lang, offset)
    emitted = [r for r in rows if not stamp or r["country"] == stamp]
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    if stamp:
        note(f"{th(n)} emitted for {stamp} of the {th(len(rows))} read over {walked} call(s) of {size} — the site states {th(total)}; a vacancy whose location names no country is stamped {stamp}.")
    elif a.max_pages and walked >= a.max_pages and (total or 0) > len(rows):
        note(f"{th(n)} emitted of the {th(total)} the site states — {walked} call(s) of {size} by request (--max-pages), not a shortfall.")
    elif n == total:
        note(f"{th(n)} emitted over {walked} call(s) of {size} — the site states {th(total)}: equal.")
    else:
        note(f"{th(n)} emitted over {walked} call(s) of {size} — the site states {th(total)}: {th(abs((total or 0) - n))} " + ("short" if (total or 0) > n else "more emitted than stated") + ".")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    host = parts.netloc.lower()
    m = AD_PATH_RE.match(parts.path)
    if not host.endswith("." + DOMAIN) or not m:
        die(f"{a.url!r}: not an Emply vacancy address (https://<tenant>.{DOMAIN}/ad/<slug>/<shortId>)")
    TENANT["host"] = host
    url = f"https://{host}/ad/{m.group(1)}/{m.group(2)}"
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped.", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    t = TITLE_RE.search(body)
    c = inner_div(body, BODY_OPEN_RE)
    if not t or c is None:
        die(f"{url}: no `css_headline` or no `csa_jobadText` in the page — not a vacancy page, or the vacancy is gone.", EXIT_PARTIAL)
    r = {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{m.group(2)}", "id": m.group(2), "url": url,
        "title": text(t.group(1)),
        "description": (scrub(text(c)) or "")[:20000] or None,
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Emply — one tenant's vacancies by the get-page call its career site makes, with the page's own section and language, the stated count beside every walk; the vacancy page; streets and postcodes withheld, no contact. Issue #468.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the tenant's vacancies, the section's own page size, 2 s apart, to the stated count")
    s.add_argument("--tenant", required=True, help="the subdomain (aarhus), the host, or the site's URL")
    s.add_argument("--page", help="the list page's path when the root and /ledige-stillinger carry no section (e.g. /da/ledige-stillinger)")
    s.add_argument("--country-code", help="keep the vacancies whose location names this ISO2 country (one naming none is stamped with it)")
    s.add_argument("--max-pages", type=int)
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one vacancy by its page (/ad/<slug>/<shortId>); description scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
