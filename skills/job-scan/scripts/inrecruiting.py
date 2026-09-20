#!/usr/bin/env python3
"""Inrecruiting, ex-Intervieweb (Zucchetti's Italian ATS — one tenant at a time): the employer's career page (`<tenant>.intervieweb.it/<lang>/career/` or `inrecruiting.intervieweb.it/<Company>/<lang>/career`) carries the URL of its own list call — `app.php?opmode=guest&module=newcareer&ajax=1&IdAzienda=<id>&CSRFToken=&CSRFHash=` — POSTed with the page's `section` and a page number, answering `{success, data: <html>}`; the job page carries a JobPosting. Issue #476.

  inrecruiting.py jobs --tenant <career URL> [--country-code ISO2] [--max-pages N]
  inrecruiting.py ad --url https://<host>/<company>/jobs/<slug>/<lang>/

THE TENANT is the career page's own address as the employer links it —
two shapes: a subdomain (`berner.intervieweb.it/it/career/`,
`tecnicagroup.intervieweb.it/it/career`) or a path on the shared host
(`inrecruiting.intervieweb.it/juliaservice/it/career`) — found by the
family's signature, never composed. Rules (2026-09-20):
`inrecruiting.intervieweb.it` writes `User-agent: *` / `Allow: *` /
`Disallow: /*access*` / `/*recoveryForm*`; `berner.intervieweb.it` answers
404 (no rules); no Crawl-delay; 2 s between requests are ours.

THE ROUTE: the page holds `<input id="url-for-announces" value="…app.php?
opmode=guest&module=newcareer&ajax=1&IdAzienda=<id>&CSRFToken=<t>&CSRFHash
=<h>">` and its script POSTs `act1=vacancyListCareer&section=<id>&order=
<order>&page=<n>&country=&region=&function=&project=&text=&division=
&company=` with the session cookie; the answer's `data` is the list's HTML
— cards `div.row.vacancy__render` with the title link (`/<company>/jobs/
<slug-id>/<lang>/`), `span.subtitle__informations[title=Sede]` (the place),
`[title=Professione/Funzione]`, `vacancy__description` (an excerpt) — or
«Nessun annuncio disponibile» when the tenant has none. **No count is
stated and no pager was seen on the tenants measured** (Julia Service 6
cards in one page, Berner none): the walk asks the next page until it
brings nothing new, and says so. THE JOB PAGE: a schema.org JobPosting
(title, datePosted, validThrough, hiringOrganization, jobLocation with a
streetAddress — not emitted —, description).

WITHHELD: the street of the workplace; e-mail addresses and telephone
numbers in the texts; the application (a form with a session) never
touched; `contacts_withheld` on every record. The list states a place
(«Ascoli Piceno Italia»), no country code; `--country-code` on `jobs`
stamps the rows and says so.
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
from _ldjson import postings as ld_postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD = "inrecruiting"
DOMAIN = "intervieweb.it"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
HARD_CAP = 200                                  # pages: no count is stated, so the walk has a ceiling of its own

CAREER_RE = re.compile(r"^(/[A-Za-z0-9_\-]+)?/([a-z]{2})/career/?$")
JOB_RE = re.compile(r"^(/[A-Za-z0-9_\-]+)?/jobs/([A-Za-z0-9_\-]+)/([a-z]{2})/?$")
URL_FOR_RE = re.compile(r'id="url-for-announces"\s+value="([^"]+)"')
SECTION_RE = re.compile(r"'section':\s*'([^']+)'")
CARD_RE = re.compile(r'<div class="row vacancy__render">(.*?)(?=<div class="row vacancy__render">|<div class="vacancies__separator|$)', re.S)
TITLE_RE = re.compile(r'<a href="([^"]+/jobs/[^"]+)"[^>]*>\s*<h3>(.*?)</h3>', re.S)
INFO_RE = re.compile(r'<span class="subtitle__informations" title="([^"]+)">(.*?)</span>\s*(?=<span class="subtitle__informations|</div>)', re.S)
DESC_RE = re.compile(r'<div class="vacancy__description[^"]*">(.*?)</div>', re.S)
NONE_RE = re.compile(r"Nessun annuncio disponibile|No vacancies available|No job", re.I)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{6,}\d(?!\w)")
_PACES = {}
_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_JAR))
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[inrecruiting] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, data=None, headers=None):
    """The tenant's host and no other, one cookie jar: the list call carries the session the page opened."""
    parts = urllib.parse.urlsplit(url)
    host = parts.netloc.lower()
    if not TENANT["host"] or host != TENANT["host"] or not host.endswith("." + DOMAIN):
        die(f"{url}: not this run's Inrecruiting tenant ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()
    h = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/json", "Accept-Language": "it,en"}
    h.update(headers or {})
    req = urllib.request.Request(wire_url(url), headers=h, data=data, method="POST" if data is not None else "GET")
    try:
        with _OPENER.open(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = re.sub(r'<span class="sr-only">.*?</span>', "", t, flags=re.S)        # the screen-reader label, not a value
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", t)
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span|font|section)\b[^>]*>", "", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def tenant_of(arg):
    """The career page's address → (host, company path or '', lang)."""
    s = (arg or "").strip()
    parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
    host = parts.netloc.lower()
    m = CAREER_RE.match(parts.path)
    if not host.endswith("." + DOMAIN) or host in ("www." + DOMAIN,) or not m:
        die(f"{arg!r}: a tenant is the career page's own address — https://<tenant>.{DOMAIN}/<lang>/career/ or https://inrecruiting.{DOMAIN}/<Company>/<lang>/career — as the employer links it, never composed")
    return host, m.group(1) or "", m.group(2)


def cards_of(markup):
    out = []
    for blk in CARD_RE.findall(markup or ""):
        t = TITLE_RE.search(blk)
        if not t:
            continue
        infos = {htmlmod.unescape(k).strip(): text(v) for k, v in INFO_RE.findall(blk)}
        d = DESC_RE.search(blk)
        out.append((htmlmod.unescape(t.group(1)), text(t.group(2)), infos, text(d.group(1)) if d else None))
    return out


def row(url, title, infos, excerpt, host, stamp):
    m = JOB_RE.match(urllib.parse.urlsplit(url).path)
    slug = m.group(2) if m else url.rstrip("/").split("/")[-2]
    place = infos.get("Sede") or infos.get("Location") or infos.get("Luogo")
    return {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{slug}", "id": slug, "url": url,
        "title": title, "place": place, "country": stamp,
        "function": infos.get("Professione/Funzione") or infos.get("Profession/Function") or infos.get("Funzione"),
        "fields": infos, "summary": scrub(excerpt),
        "contacts_withheld": True,
    }


def list_call(page_body, host, referer, section, number):
    m = URL_FOR_RE.search(page_body or "")
    if not m:
        die(f"{referer}: no `url-for-announces` in the page — not an Inrecruiting career page, or its shape changed.", EXIT_PARTIAL)
    url = htmlmod.unescape(m.group(1))
    if urllib.parse.urlsplit(url).netloc.lower() != host:
        die(f"{referer}: the page's list call points at {url!r}, another host — not replayed.", EXIT_REFUSED)
    data = urllib.parse.urlencode({"act1": "vacancyListCareer", "section": section, "order": "date", "page": number, "country": "", "region": "",
                                   "function": "", "project": "", "text": "", "division": "", "company": ""}).encode()
    st, body = request(url, data=data, headers={"X-Requested-With": "XMLHttpRequest", "Referer": referer, "Content-Type": "application/x-www-form-urlencoded"})
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st} on page {number}", EXIT_PARTIAL)
    try:
        j = json.loads(body)
    except ValueError:
        die(f"{url}: not JSON ({len(body)} characters) on page {number}", EXIT_PARTIAL)
    if not isinstance(j, dict) or j.get("success") is not True or not isinstance(j.get("data"), str):
        die(f"{url}: the answer is not `{{success: true, data: <html>}}` on page {number}.", EXIT_PARTIAL)
    return j["data"]


def cmd_jobs(a):
    host, company, lang = tenant_of(a.tenant)
    TENANT["host"] = host
    stamp = (a.country_code or "").strip().upper() or None
    referer = f"https://{host}{company}/{lang}/career/" if company else f"https://{host}/{lang}/career/"
    st, page_body = request(referer)
    if st == 404:
        die(f"{referer}: HTTP 404 — no such career page", EXIT_GONE)
    if st in (403, 429):
        die(f"{referer}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{referer}: HTTP {st}", EXIT_PARTIAL)
    sm = SECTION_RE.search(page_body)
    if not sm:
        die(f"{referer}: no vacancy section in the page's script — not an Inrecruiting career page, or its shape changed.", EXIT_PARTIAL)
    section = sm.group(1)
    rows, seen, number, none_said = [], set(), 0, False
    while number < HARD_CAP and (not a.max_pages or number < a.max_pages):
        number += 1
        data = list_call(page_body, host, referer, section, number)
        cards = cards_of(data)
        if not cards:
            none_said = bool(NONE_RE.search(data))
            number -= 1 if number > 1 else 0
            break
        new = 0
        for url, title, infos, excerpt in cards:
            key = url
            if key in seen:
                continue
            seen.add(key)
            rows.append(row(url, title, infos, excerpt, host, stamp))
            new += 1
        if new == 0:                              # the next page repeated the last: the end, since no count is stated
            number -= 1
            break
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    n = len(rows)
    stamp_note = f"; country {stamp} stamped from --country-code (the list states a place, no country)" if stamp else ""
    if n == 0 and none_said:
        note(f"0 emitted — the tenant says «Nessun annuncio disponibile»: no vacancy today, not an error{stamp_note}.")
    elif a.max_pages and number >= a.max_pages:
        note(f"{th(n)} emitted over {number} page(s) by request (--max-pages) — no count is stated by the site; there may be more{stamp_note}.")
    else:
        note(f"{th(n)} emitted over {max(number, 1)} page(s) — no count is stated by the site: the walk stopped when a page brought nothing new{stamp_note}.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    host = parts.netloc.lower()
    m = JOB_RE.match(parts.path)
    if not host.endswith("." + DOMAIN) or host == "www." + DOMAIN or not m:
        die(f"{a.url!r}: not an Inrecruiting job address (https://<host>/<company>/jobs/<slug>/<lang>/)")
    TENANT["host"] = host
    url = f"https://{host}{m.group(1) or ''}/jobs/{m.group(2)}/{m.group(3)}/"
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped.", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    ps = ld_postings(body)
    if not ps:
        die(f"{url}: no JobPosting in the page — an Inrecruiting job page carries one; the shape changed, or the job is gone.", EXIT_PARTIAL)
    p = ps[0]
    org = p.get("hiringOrganization") if isinstance(p.get("hiringOrganization"), dict) else {}
    loc = p.get("jobLocation") if isinstance(p.get("jobLocation"), dict) else {}
    addr = loc.get("address") if isinstance(loc.get("address"), dict) else {}
    cc = addr.get("addressCountry")
    r = {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{m.group(2)}", "id": m.group(2), "url": url,
        "title": p.get("title"), "company": org.get("name"),
        "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None,
        "country": cc.strip().upper() if isinstance(cc, str) and len(cc.strip()) == 2 else None, "country_name": cc if isinstance(cc, str) and len(cc.strip()) > 2 else None,
        # streetAddress and postalCode are not emitted
        "posted": p.get("datePosted"), "closes": p.get("validThrough"), "employment_type": p.get("employmentType"),
        "description": (scrub(text(p.get("description"))) or "")[:20000] or None,
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Inrecruiting (Intervieweb) — one tenant's vacancies by the list call its career page makes (the page's own URL, section and session), walked until a page brings nothing new (no count is stated); the job page's JobPosting; the street withheld, no contact. Issue #476.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the career page, then its list call page by page, 2 s apart")
    s.add_argument("--tenant", required=True, help="the career page's address as the employer links it")
    s.add_argument("--country-code", help="ISO2 to stamp the rows with — the list states a place, no country")
    s.add_argument("--max-pages", type=int)
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one job by its page's JobPosting; street withheld, description scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
