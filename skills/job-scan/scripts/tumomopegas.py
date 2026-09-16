#!/usr/bin/env python3
"""TumomoPegas (`tumomopegas.com`) — a Bolivian generalist on a SmartJobBoard-style engine: the list `/todos-los-empleos/?page=N` serves ten cards a page on the server with the site's own count («37 Empleos»), and each ad is a page of labelled fields («ID Oferta», «Ciudad», «Rango Salarial», «Tipo de contrato», «Publicado», «Categorías», «Descripción del puesto») with no JobPosting; the count printed beside every walk; the description scrubbed. Issue #432.

  tumomopegas.py list [--pages N]     the cards of /todos-los-empleos/?page=1 … until a page brings nothing new (4 pages on the day, 2 s apart), the stated count beside them
  tumomopegas.py ad --url <https://tumomopegas.com/display-job/<id>/<slug>.html>

THE RULES. `User-Agent: *` — `Disallow: /files/files/` and nothing else; a dozen scrapers refused by
name (Zealbot, WebStripper, Teleport …), none of ours; no Crawl-delay, 2 s is ours. The accounts
(`/ingresar/`, `/registrarse/`, `/add-listing/`) and the banner redirects (`/go-link/`) are never
sent — refused before the gate, by the adapter's own list.

THE LIST. `/todos-los-empleos/` (200, ~83 KB) prints «37 Empleos» and ten cards — `<h3
class="title-job-list"><a id="listing_<id>" href="…/display-job/<id>/<slug>.html?searchId=…&page=1">`,
the employer as a `/company/<id>/<slug>/` link, «dd.mm.yyyy», «City, DPT» — and a pager
`?searchId=…&action=search&page=2&view=list`; `?page=N` alone is honoured (page 2 opens on the
eleventh card). The per-page form is a POST the adapter does not send. The walk stops when a page
brings no new card, dies (exit 6) on a 200 without a card or with page 1's cards again, and prints
emitted against the stated count. THE AD. `/display-job/<id>/<slug>.html` (200, ~63 KB): `<h1>`,
the employer link, then `<h3>Label:</h3><div class="displayField">value</div>` blocks — ID Oferta,
Ciudad, Rango Salarial («Salario Negociable» or a range), Vistas, Tipo de contrato, Publicado,
Categorías (bold family: speciality, one per line), Descripción del puesto (HTML) — no JSON-LD
JobPosting (only MonetaryAmount fragments). **The description is scrubbed of e-mail addresses and
Bolivian telephone numbers; «Vistas» (the site's own counter) is not emitted; `contacts_withheld`
on every record; the application («Postular a Empleo», a candidate account) never touched.**

Measured 2026-09-16 06:15–06:17 UTC by the declared client, the guard on the exact path: robots 200
(1 048 B); `/` 156 546 B; `/todos-los-empleos/` 83 142 B, «37 Empleos», 10 cards; `?page=2` 10 more;
the ad 62 594 B.
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

HOST = "tumomopegas.com"
LIST = f"https://{HOST}/todos-los-empleos/"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+?591[\s\-]?)?(?:[67]\d{7}|[2-4][\s\-]?\d{6,7})(?!\d)")   # mobiles 6xxxxxxx / 7xxxxxxx, landlines 2/3/4 + 6–7 digits, with or without +591
AD_RE = re.compile(r"^/display-job/(\d+)/([^/?]+)\.html$")
REFUSED_RE = re.compile(r"^/(?:files/files|ingresar|registrarse|add-listing|go-link|social|my-|mi-cuenta)(?:/|$)")
CARD_RE = re.compile(r'<h3 class="title-job-list"><a id="listing_(\d+)" href="([^"?]+)[^"]*">(.*?)</a></h3>(.*?)(?=<h3 class="title-job-list">|<div class="pagination|</ul>|$)', re.S)
COMPANY_RE = re.compile(r'<a [^>]*?href="https://tumomopegas\.com/company/(\d+)/[^"]*"[^>]*>\s*(?:<strong>)?(.*?)(?:</strong>)?\s*</a>', re.S)
DATE_RE = re.compile(r'class="job-date">.*?(\d{2})\.(\d{2})\.(\d{4})', re.S)
PLACE_RE = re.compile(r'class="location">.*?&nbsp;([^<]+)<', re.S)
COUNT_RE = re.compile(r"(\d[\d\.,]*)\s*Empleos\b")
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
FIELD_RE = re.compile(r'<h3>([^<]+?):</h3>\s*<div class="displayField">(.*?)</div>', re.S)

_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[tumomopegas] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    if REFUSED_RE.search(urllib.parse.urlsplit(url).path):
        die(f"{url}: the accounts, the listing forms and the banner redirects — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "es"})
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
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t))
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def stated(body):
    """The count the list prints — «37 Empleos» — or `None`."""
    m = COUNT_RE.search(body or "")
    return int(re.sub(r"\D", "", m.group(1))) if m else None


def iso(d, m, y):
    return f"{y}-{m}-{d}"


def cards(body):
    out = []
    for jid, href, title, tail in CARD_RE.findall(body):
        comp = COMPANY_RE.search(tail)
        dt = DATE_RE.search(tail)
        pl = PLACE_RE.search(tail)
        out.append({
            "source": "tumomopegas", "country": "BO", "ledger_id": f"tumomopegas:{jid}", "id": jid, "url": href,
            "title": text(title), "company": text(comp.group(2)) if comp else None, "company_id": comp.group(1) if comp else None,
            "posted": iso(*dt.groups()) if dt else None, "place": text(pl.group(1)) if pl else None,
            "contacts_withheld": True, "language": "es",
        })
    return out


def cmd_list(a):
    out, seen, first_ids, pages, total = [], set(), None, 0, None
    n = 1
    while True:
        url = LIST if n == 1 else f"{LIST}?page={n}"
        code, body = request(url)
        if code == 404:
            break
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if n == 1:
            total = stated(body)
            if total is None:
                die(f"{url}: 200 and no «N Empleos» in the page — the template changed; not an empty market", EXIT_PARTIAL)
        cs = cards(body)
        if not cs:
            die(f"{url}: 200 and no card — the template changed; not an empty page", EXIT_PARTIAL)
        ids = [c["id"] for c in cs]
        if first_ids is None:
            first_ids = ids
        elif ids == first_ids:
            die(f"{url}: the same cards as page 1 — the pager is not honoured; stopped", EXIT_PARTIAL)
        new = 0
        for c in cs:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            out.append(c)
            new += 1
        pages += 1
        if new == 0 or len(out) >= total or (a.pages and pages >= a.pages):
            break
        n += 1
    for c in out:
        print(json.dumps(c, ensure_ascii=False))
    emitted = len(out)
    if a.pages and pages >= a.pages and emitted < total:
        note(f"{th(emitted)} emitted from {pages} page(s); the site states {th(total)} — walked by request (--pages), not a shortfall.")
    else:
        verdict = "equal" if emitted == total else (f"{th(total - emitted)} short" if emitted < total else f"{th(emitted - total)} more emitted")
        note(f"{th(emitted)} emitted from {pages} page(s), the site states {th(total)} — {verdict}.")
    note("cards only — `ad --url` reads the ad's fields, scrubbed; the accounts never touched.")


def record(body, jid, url):
    h1 = H1_RE.search(body)
    fields = {text(k): v for k, v in FIELD_RE.findall(body)}
    if not h1 or "Descripción del puesto" not in fields:
        return None
    comp = COMPANY_RE.search(body)
    dt = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", fields.get("Publicado", "") or "")
    cats = [" ".join(l.split()) for l in (text(fields.get("Categorías", "")) or "").splitlines() if l.strip()]
    salary = text(fields.get("Rango Salarial", ""))
    return {
        "source": "tumomopegas", "country": "BO", "ledger_id": f"tumomopegas:{jid}", "id": jid, "url": url,
        "title": text(h1.group(1)), "company": text(comp.group(2)) if comp else None, "company_id": comp.group(1) if comp else None,
        "place": text(fields.get("Ciudad", "")), "salary": None if not salary or salary.lower().startswith("salario negociable") else salary, "salary_negotiable": bool(salary and salary.lower().startswith("salario negociable")),
        "contract": text(fields.get("Tipo de contrato", "")), "posted": iso(*dt.groups()) if dt else None,
        "categories": cats or None,
        "description": scrub(text(fields.get("Descripción del puesto", ""))),
        "contacts_withheld": True, "language": "es",
    }


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc not in (HOST, "www." + HOST) or not m:
        die(f"{a.url}: not a job address (https://{HOST}/display-job/<id>/<slug>.html)")
    url = f"https://{HOST}{parts.path}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    rec = record(body, m.group(1), url)
    if rec is None:
        die(f"{url}: 200 without the ad's heading and its «Descripción del puesto» — the template changed", EXIT_PARTIAL)
    print(json.dumps(rec, ensure_ascii=False))
    note(f"{url}: read from its labelled fields; description scrubbed; the application never touched.")


def main():
    p = argparse.ArgumentParser(description="TumomoPegas — the list's cards with the site's stated count beside them, each ad from its labelled fields; descriptions scrubbed. Issue #432.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="/todos-los-empleos/?page=1 … until a page brings nothing new, 2 s apart")
    l_.add_argument("--pages", type=int, help="stop after N pages (a bound, printed as such)")
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
