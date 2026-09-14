#!/usr/bin/env python3
"""Eleman.net (`www.eleman.net`, Türkiye) — the old generalist of manual trades and the provinces, walked through the server-rendered list its rules leave open; the pager's own page count printed beside every walk; the ad's JSON-LD and labelled boxes read, the «İletişim» block — telephone numbers the site itself masks — never read. Issue #384.

  eleman.py list [--city <slug>] [--pages N] [--limit N]
  eleman.py ad --url <https://www.eleman.net/is-ilani/<slug>-i<id>>

THE RULES (473 B, `*`) refuse the legacy `.asp/.html/.htm` addresses, the search and its
parameters (`*?t=*`, `*?ilan_id=*`, `*?tip=*` …), the account and application pages
(`basvuru_yap.php`, `cv_guncelle.php`) — and nothing of `/is-ilanlari`, `/is-ilanlari/<city>`,
their pager `?sy=N`, or `/is-ilani/<slug>-i<id>`. **`sy` is the only parameter this adapter
ever sends; any other is refused before the gate.** No sitemap (`/sitemap.xml` 404, the
country page of 2026-09-01). No Crawl-delay; 2 s is ours.

THE LIST. `/is-ilanlari` («iş ilanları») prints 30 cards a page and a pager whose select
reads «1 / 243» — **the site's own page count, printed beside every walk** («walked 10 of the
243 pages the pager states»); the last page carried 18 on the day, so the list held about
7 278 postings — inferred from the pager, not stated. `/is-ilanlari/istanbul` is the same
list for a city (125 pages). A card: the ad's address (`/is-ilani/<slug>-i<id>`, the id at
the tail), title, employer, place («Ankara - Çankaya»), the benefits line, a snippet, and
three badges — «ACİL İLAN» (urgent), «Telefonla başvuru yapabilirsiniz» (applications by
telephone), «Maaş Bilgisi Olan» (a salary is stated). No date on the card; the list is
newest-first and the ad carries the date.

THE AD. A JSON-LD JobPosting — `datePosted`, `validThrough`, `employmentType`,
`jobBenefits`, `industry`, `hiringOrganization` (name, `/firma/` url), `jobLocation`
(a list of addresses), `baseSalary` (`value`, `unitText` MONTH — a period, so
`salary_unit_stated` is true) — and the page's labelled boxes (`is_ilani_ozellik_kutusu`):
«Maaş: 45.000 TL», «Yan Haklar», the gender wanted, the age range, «Kişi Sayısı» (positions),
the contract; the description in `d-information`, scrubbed. **The «İletişim» block prints
telephone numbers the site masks («0537 611 ** **») and unmasks only to a signed-in account
— never read, never asked for; the description is scrubbed of Turkish telephone numbers and
e-mail addresses; `contacts_withheld` on every record.** The application form
(`basvuru_yap.php`) is refused in writing and never touched.

Measured 2026-09-14 01:5x UTC by the declared client, the guard on the exact path: `/is-ilanlari`
200, 284 279 B, 30 cards, pager «1 / 243»; `?sy=243` 18 cards; `/is-ilanlari/istanbul?sy=2` 30
cards, «2 / 125»; the ad 108 250 B with its JobPosting.
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

HOST = "www.eleman.net"
LIST = f"https://{HOST}/is-ilanlari"
PAGE_SIZE = 30

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# 0537 611 22 33 · 0 (212) 555 44 33 · +90 537 611 22 33 · 05376112233 — and the site's own masked «0537 611 ** **»
PHONE_RE = re.compile(r"(?<![\d+])(?:\+90[\s ]?|0)[\s ]?\(?\d{3}\)?[\s ]?\d{3}[\s ]?(?:\d{2}|\*\*)[\s ]?(?:\d{2}|\*\*)(?!\d)")
CARD_RE = re.compile(r'<div class="c-box__body ilan_listeleme_bol([^"]*)"\s*>\s*<a href="(https://www\.eleman\.net/is-ilani/[^"]+)"(.*?)</a>\s*</div>', re.S)   # the class tail carries «renkli-ilan» on a highlighted card
ID_RE = re.compile(r"-i(\d+)/?$")
TITLE_RE = re.compile(r'<h3[^>]*>(.*?)(?:<div class="ilantik-grubu">|</h3>)', re.S)
SUBTITLE_RE = re.compile(r'<span class="c-showcase-box__subtitle">(.*?)</span>', re.S)
TEXT_RE = re.compile(r'<span class="c-showcase-box__text[^"]*"[^>]*>(.*?)</span>\s*</span>', re.S)
BENEFITS_RE = re.compile(r'hgi-eraser-add"></i>\s*<span[^>]*>(.*?)</span>', re.S)
PAGER_RE = re.compile(r'<option value="0" selected[^>]*>\s*(\d+)\s*/\s*(\d+)\s*<')
BOX_RE = re.compile(r'<span[^>]*class="is_ilani_ozellik_kutusu"[^>]*>(.*?)</span>', re.S)
DESC_RE = re.compile(r'<div class="d-information">\s*<div[^>]*>(.*?)</div>\s*<p', re.S)
NUM_RE = re.compile(r"(\d{1,3}(?:\.\d{3})+|\d+)")   # «45.000» is forty-five thousand; «45000» is too


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[eleman] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours


def request(url):
    q = urllib.parse.urlsplit(url).query
    if q and set(urllib.parse.parse_qs(q)) != {"sy"}:
        die(f"{url}: the rules refuse the site's other parameters in writing (`*?t=*`, `*?ilan_id=*` …) — only `sy` is sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "tr"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t ​]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def num(s):
    m = NUM_RE.search(s or "")
    return int(m.group(1).replace(".", "")) if m else None


def pager(body):
    """«1 / 243» in the pager's select → (current, pages), the site's own page count."""
    m = PAGER_RE.search(body)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def cards(body):
    out = []
    for classes, url, block in CARD_RE.findall(body):
        m = ID_RE.search(url)
        if not m:
            continue
        t = TITLE_RE.search(block)
        sub = SUBTITLE_RE.search(block)
        employer = place = None
        if sub:
            parts = [text(p) for p in re.split(r"<br\s*/?>", sub.group(1))]
            employer = parts[0] or None
            place = parts[1] if len(parts) > 1 and parts[1] else None
        ben = BENEFITS_RE.search(block)
        texts = TEXT_RE.findall(block)
        out.append({
            "source": "eleman", "country": "TR", "ledger_id": f"eleman:{m.group(1)}", "id": m.group(1),
            "url": url, "title": text(t.group(1)) if t else None,
            "employer": employer, "place": place,
            "benefits": text(ben.group(1)) if ben else None,
            "summary": scrub(text(texts[-1])) if texts else None,
            "urgent": "ACİL İLAN" in block,
            "apply_by_telephone": "Telefonla başvuru" in block,   # the badge; the number itself is never read
            "salary_stated": "Maaş Bilgisi Olan" in block,
            "highlighted": "renkli-ilan" in classes,   # a paid, coloured card
            "contacts_withheld": True, "language": "tr",
        })
    return out


def cmd_list(a):
    base = LIST + (f"/{a.city.strip('/').lower()}" if a.city else "")
    rows, seen, pageno, pages = [], set(), 0, None
    while True:
        pageno += 1
        url = base + (f"?sy={pageno}" if pageno > 1 else "")
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_GONE if code == 404 and pageno == 1 else EXIT_PARTIAL)
        cur, total = pager(body)
        if pages is None:
            pages = total
        page = cards(body)
        if not page:
            die(f"{url}: 200 and not one card — the template changed; not an empty market", EXIT_PARTIAL)
        new = 0
        for r in page:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
            new += 1
        if new == 0 or (pages and pageno >= pages):
            break
        if a.pages and pageno >= a.pages:
            break
        if a.limit and len(rows) >= a.limit:
            break
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    where = f"/is-ilanlari/{a.city}" if a.city else "/is-ilanlari"
    if pages is None:
        note(f"{th(n)} emitted over {pageno} page(s) of {where} — the pager's page count was not found; not compared.")
    elif pageno >= pages:
        note(f"{th(n)} emitted over {pageno} page(s) of {where} — the {pages} pages the pager states, all walked; the site states no total, the pager is the witness.")
    else:
        note(f"{th(n)} emitted over {pageno} of the {pages} page(s) the pager states for {where}, {PAGE_SIZE} a page — walked by request (--pages/--limit), not a shortfall; the site states no total.")
    note("the ad's «İletişim» block — telephone numbers the site masks — is never read; descriptions scrubbed; the application form is refused in writing and never touched.")


def ldjson(body):
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S):
        try:
            d = json.loads(m, strict=False)
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("@type") == "JobPosting":
            return d
    return None


def boxes(body):
    """The labelled boxes under the description: «Maaş: 45.000 TL», «Yan Haklar: Yemek», «Kadın veya Erkek», «24 - 55 arası», «No: 4762495», «Kişi Sayısı: 2», «Tam Zamanlı»."""
    out = {"salary_text": None, "benefits": None, "gender": None, "age_range": None, "positions": None, "contract": None}
    for b in BOX_RE.findall(body):
        t = text(b)
        if t.startswith("Maaş:"):
            out["salary_text"] = t[5:].strip()
        elif t.startswith("Yan Haklar:"):
            out["benefits"] = t[11:].strip()
        elif t.startswith("Kişi Sayısı:"):
            out["positions"] = num(t)
        elif t.startswith("No:"):
            continue
        elif re.match(r"^\d+\s*-\s*\d+\s+arası$", t):
            out["age_range"] = t
        elif t in ("Kadın veya Erkek", "Kadın", "Erkek"):
            out["gender"] = t
        elif t:
            out["contract"] = t
    return out


def locality(ad):
    """«Ankara,Çankaya» with region «Ankara» → «Ankara - Çankaya»; the region is added only when the locality does not already start with it."""
    loc = (ad.get("addressLocality") or "").strip()
    reg = (ad.get("addressRegion") or "").strip()
    parts = [p.strip() for p in loc.split(",") if p.strip()]
    if reg and (not parts or parts[0] != reg):
        parts = [reg] + parts
    return " - ".join(parts) or None


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = ID_RE.search(parts.path)
    if parts.netloc != HOST or not parts.path.startswith("/is-ilani/") or not m:
        die(f"{a.url}: not an ad address (https://{HOST}/is-ilani/<slug>-i<id>)")
    url = f"https://{HOST}{parts.path.rstrip('/')}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    ld = ldjson(body)
    bx = boxes(body)
    desc = DESC_RE.search(body)
    if not ld and not desc:
        die(f"{url}: 200 without a JobPosting or a description block — the template changed", EXIT_PARTIAL)
    ld = ld or {}
    org = ld.get("hiringOrganization") or {}
    addrs = (ld.get("jobLocation") or {}).get("address") or []
    addrs = addrs if isinstance(addrs, list) else [addrs]
    sal = (ld.get("baseSalary") or {}).get("value") or {}
    value = num(str(sal.get("value") or "")) if sal else None
    unit = (sal.get("unitText") or "").lower() or None
    if value is None and bx["salary_text"]:
        value = num(bx["salary_text"])
    print(json.dumps({
        "source": "eleman", "country": "TR", "ledger_id": f"eleman:{m.group(1)}", "id": m.group(1), "url": url,
        "title": htmlmod.unescape(ld.get("title") or "").strip() or (text(re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S).group(1)) if re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S) else None),
        "employer": htmlmod.unescape(org.get("name") or "").strip() or None, "employer_url": org.get("url") or None,
        "locations": [locality(ad) for ad in addrs if isinstance(ad, dict) and locality(ad)] or None,
        "region": next((ad.get("addressRegion") for ad in addrs if isinstance(ad, dict) and ad.get("addressRegion")), None),
        "employment_type": ld.get("employmentType") or bx["contract"], "industry": ld.get("industry") or None,
        "salary_text": bx["salary_text"], "salary_min": value, "salary_max": value, "salary_currency": "TRY" if value is not None else None,
        "salary_unit": unit if value is not None else None, "salary_unit_stated": bool(unit) and value is not None,
        "benefits": bx["benefits"] or ld.get("jobBenefits") or None,
        "positions": bx["positions"], "gender_wanted": bx["gender"], "age_range": bx["age_range"],
        "posted": (ld.get("datePosted") or "")[:10] or None, "valid_through": (ld.get("validThrough") or "")[:10] or None,
        "description": scrub(text(desc.group(1))) if desc else scrub(text(htmlmod.unescape(ld.get("description") or ""))),
        # the «İletişim» block — masked telephone numbers, unmasked to a signed-in account only — is never read
        "contacts_withheld": True, "language": "tr",
    }, ensure_ascii=False))
    note(f"{url}: read; the «İletişim» block is never read, the description is scrubbed.")


def main():
    p = argparse.ArgumentParser(description="Eleman.net — the Turkish generalist's server-rendered list, the pager's page count beside every walk; the ad's JobPosting and boxes; the masked telephone block never read. Issue #384.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the newest cards, 30 a page, 10 pages unless told otherwise")
    l_.add_argument("--city", help="a city slug of the site — istanbul, ankara, izmir …")
    l_.add_argument("--pages", type=int, default=10)
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
