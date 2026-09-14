#!/usr/bin/env python3
"""Jobs.cz (`www.jobs.cz`, Alma Career) — the largest Czech board, through the search cards its pages render; «Našli jsme N nabídek» printed beside every walk; the contact block on every ad never leaves. Issue #351.

  jobscz.py search [--locality praha] [--pages N] [--limit N]
  jobscz.py ad --url <https://www.jobs.cz/rpd/<id>/>

THE ROUTE IS THE SEARCH PAGE, server-rendered as `<article class="SearchResultCard">`:

  GET /prace/<slug>/                 -> a locality's list from page 1: «Našli jsme 7 681 nabídek» (praha), 30 cards, ?page=2 …
  GET /prace/?page=N  (N ≥ 2)        -> the whole country: «Našli jsme 16 019 nabídek», 30 cards a page
  GET /prace/  and  /prace/?page=1   -> **the country-wide entry page, rendered on the client — the server sends no card**
  GET /rpd/<id>/                     -> one ad: the title, the company, the address, the salary, the text, the benefits — and a contact block

**The country-wide page 1 is not served to a client without a filter** (the site's
`SearchNoUserInputEntry`): a walk with no `--locality` starts at page 2 by the site's own
behaviour and the note says so — 30 of the count are not reachable by HTTP that way, and the
adapter never pretends otherwise. With `--locality <slug>` (`praha`, `brno`, `ostrava` … the
site's own `/prace/<slug>/` paths) every page is served from the first. The rules (349 B):
`*` with `/api/`, `/iapi/`, `/muj/` and a few account paths refused — nothing this adapter
touches; no sitemap, no Crawl-delay — 2 s is ours.

THE CARD carries `data-jobad-id`, the title (`data-test-ad-title`), the address (`/rpd/<id>/`,
the search token stripped), the employer (the footer's first item, `translate="no"`), the
locality (`data-test="serp-locality"` — «Ústecký kraj + 3 další lokality»), the status
(«Přidáno včera», «Příležitost dne»), and the tags: a salary tag «45 000 – 60 000 Kč» is read as
a range in CZK, `salary_unit_stated` false (the card prints no period), the others kept as
`tags`. THE AD: `<h1>`, `jd-info-item` (company, and the page's other info lines),
`jd-info-location`, `jd-salary`, `jd-benefits`, `jd-body-richtext` (the text). **The contact
block — `jd-contact-company` (a person's name), `jd-contact-address`, `jd-contact-phone` — is
not read, and the text is scrubbed of e-mail addresses and Czech telephone numbers.** The
«Odpovědět» application is the site's own form, never touched.

Measured 2026-09-14 00:1x UTC by the declared client: praha «7 681», the country «16 019»
(page 2 served, page 1 not); one ad read. **`--pages` defaults to 10** (300 rows) and the note
says the walk was bounded by request.
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

HOST = "www.jobs.cz"
BASE = f"https://{HOST}"
PAGE_SIZE = 30
COUNT_RE = re.compile(r"Našli jsme\s+([\d\s\u00a0\u202f]+)\s*nabíd")   # the figure sits in a <strong>, so the count is read from the page's TEXT
CARD_RE = re.compile(r'<article\s+class="SearchResultCard"\s*>(.*?)</article>', re.S)
DETAIL_RE = re.compile(r"^https?://www\.jobs\.cz/(rpd|fp|pd)/(\d+)/?(?:\?.*)?$")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+420[\s ]?)?\d{3}[\s ]?\d{3}[\s ]?\d{3}(?!\d)")
SALARY_RE = re.compile(r"^\s*(\d[\d\s\u00a0\u202f]*)\s*(?:[–-]\s*(\d[\d\s\u00a0\u202f]*))?\s*Kč")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobscz] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # no Crawl-delay in the rules; 2 s is ours


def request(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "cs"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</dd>|</dt>|</tr>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t  ‍]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def num(s):
    return int(re.sub(r"[\s\u00a0\u202f]", "", s))


def scrub(s):
    if not s:
        return s
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s)


def stated(body):
    m = COUNT_RE.search(text(body))
    return num(m.group(1)) if m else None


def salary(tag):
    """«45 000 – 60 000 Kč» on a card tag → (min, max); a single figure → (n, n). The card prints no period."""
    m = SALARY_RE.match(htmlmod.unescape(tag or ""))
    if not m:
        return None, None
    lo = num(m.group(1))
    hi = num(m.group(2)) if m.group(2) else lo
    return lo, hi


def cards(body):
    out = []
    for m in CARD_RE.finditer(body or ""):
        c = m.group(1)
        ident = re.search(r'data-jobad-id="(\d+)"', c)
        link = re.search(r'href="(https://www\.jobs\.cz/(?:rpd|fp|pd)/\d+/)', c)
        if not ident or not link:
            continue
        title = re.search(r'data-test-ad-title="([^"]*)"', c)
        emp = re.search(r'<li[^>]*SearchResultCard__footerItem[^>]*>(?:(?!</li>).)*?<span translate="no">(.*?)</span>', c, re.S)
        loc = re.search(r'<li[^>]*data-test="serp-locality"[^>]*>(.*?)</li>', c, re.S)
        status = re.search(r'data-test-ad-status="[^"]*"[^>]*>(.*?)</div>', c, re.S)
        tags = [text(t) for t in re.findall(r'<span\s+class="Tag[^"]*"[^>]*>(.*?)</span>', c, re.S)]
        smin, smax, rest = None, None, []
        for t in tags:
            lo, hi = salary(t)
            if lo is not None and smin is None:
                smin, smax = lo, hi
            else:
                rest.append(t)
        out.append({
            "source": "jobscz", "country": "CZ", "ledger_id": f"jobscz:{ident.group(1)}", "id": ident.group(1),
            "url": link.group(1),                                        # the search token (?searchId=…&rps=) stripped
            "title": htmlmod.unescape(title.group(1)).strip() if title else None,
            "employer": text(emp.group(1)) if emp else None,
            "workplace": text(loc.group(1)) if loc else None,            # «Ústecký kraj + 3 další lokality», as the card prints it
            "status": text(status.group(1)) if status else None,         # «Přidáno včera», «Příležitost dne»
            "tags": rest,
            "salary_min": smin, "salary_max": smax, "salary_currency": "CZK" if smin is not None else None, "salary_unit_stated": False,
            "language": "cs",
        })
    return out


def list_url(locality, page):
    base = f"{BASE}/prace/" + (locality.strip("/") + "/" if locality else "")
    return base if page == 1 else f"{base}?page={page}"


def cmd_search(a):
    where = f"({a.locality})" if a.locality else "(the whole country)"
    out, seen, total = [], set(), None
    pageno = 1 if a.locality else 2
    if not a.locality:
        note("the country-wide page 1 is the site's entry page, rendered on the client — the server sends no card; the walk starts at page 2 by the site's own behaviour, and 30 of the count are not reachable by HTTP this way. `--locality <slug>` is served from page 1.")
    first = True
    while True:
        url = list_url(a.locality, pageno)
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        s = stated(body)
        rows = cards(body)
        if first:
            first = False
            if s is None:
                if not rows:
                    note(f"no «Našli jsme N nabídek» and no card {where} — the site lists nothing.")
                    return
                die(f"{url}: cards on the page and no «Našli jsme N nabídek» — the count line changed; a walk without it is not compared.", EXIT_PARTIAL)
            total = s
        new = 0
        for r in rows:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            out.append(r)
            new += 1
        if new == 0 or len(out) >= total:
            break
        if a.pages and (pageno - (0 if a.locality else 1)) >= a.pages:
            break
        if a.limit and len(out) >= a.limit:
            break
        pageno += 1
    emitted = out[:a.limit] if a.limit else out
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    walked = pageno - (0 if a.locality else 1)
    bounded = (a.pages and walked >= a.pages and total > pageno * PAGE_SIZE) or (a.limit and a.limit < total)
    if bounded:
        note(f"{th(n)} emitted of the {th(total)} the site states {where} — {walked} page(s) of {PAGE_SIZE} walked by request (--pages/--limit), not a shortfall.")
    elif n == total:
        note(f"{th(n)} emitted over {walked} page(s), site states {th(total)} {where} — equal.")
    else:
        note(f"{th(n)} emitted over {walked} page(s), site states {th(total)} {where} — {th(abs(total - n))} " + ("short" if total > n else "more emitted than the site states")
             + (" (the 30 of the client-rendered page 1 among them)." if not a.locality and total > n else "."))


def hook(body, name, tag="div"):
    m = re.search(r'<%s[^>]*data-test="%s"[^>]*>(.*?)</%s>' % (tag, re.escape(name), tag), body or "", re.S)
    return text(m.group(1)) if m else None


def cmd_ad(a):
    m = DETAIL_RE.match((a.url or "").strip())
    if not m:
        die(f"{a.url}: not an ad address — expected {BASE}/rpd/<id>/")
    ident = m.group(2)
    code, body = request(f"{BASE}/{m.group(1)}/{ident}/")
    if code in (404, 410):
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    if not h1 or "jd-body-richtext" not in body:
        die(f"{a.url}: not an ad page ({len(body)} characters) — a redirect, or the site changed.", EXIT_PARTIAL)
    infos = [text(x) for x in re.findall(r'<div[^>]*data-test="jd-info-item"[^>]*>(.*?)</div>', body, re.S)]
    company = next((re.sub(r"^Společnost\s*", "", i).strip() or None for i in infos if i.startswith("Společnost")), None)
    sal = hook(body, "jd-salary")
    sal = re.sub(r"^Plat\s*", "", sal).strip() if sal else None      # the block's own label «Plat» dropped; the figure kept as printed
    smin, smax = salary(re.sub(r"^\D*", "", sal or "")) if sal else (None, None)
    desc = hook(body, "jd-body-richtext")
    benefits = [text(x) for x in re.findall(r'<div[^>]*data-test="jd-benefits"[^>]*>(.*?)</div>', body, re.S)]
    # the contact block — jd-contact-company (a person), jd-contact-address, jd-contact-phone — is never read
    print(json.dumps({
        "source": "jobscz", "country": "CZ", "ledger_id": f"jobscz:{ident}", "id": ident, "url": f"{BASE}/{m.group(1)}/{ident}/",
        "title": text(h1.group(1)) or None,
        "employer": company,
        "workplace": hook(body, "jd-info-location", "a"),                 # the workplace address as the page prints it — an employer's, not a person's
        "salary_text": sal, "salary_min": smin, "salary_max": smax, "salary_currency": "CZK" if smin is not None else None, "salary_unit_stated": False,
        "info": [scrub(i) for i in infos if not i.startswith("Společnost")],
        "benefits": benefits,
        "description": scrub(re.sub(r"^Pracovní nabídka\n", "", desc or ""))[:20000] or None,
        "contacts_withheld": True,
        "language": "cs",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Jobs.cz — the search cards the pages render; «Našli jsme N nabídek» beside every walk; the contact block never leaves. Issue #351.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="the listing, 30 a page, 2 s apart, 10 pages unless told otherwise; --locality is a path the site itself serves (praha, brno, ostrava…) and is served from page 1 — the country-wide list starts at page 2")
    s.add_argument("--locality")
    s.add_argument("--pages", type=int, default=10)
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one ad — the text, the salary, the benefits; the contact block withheld")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
