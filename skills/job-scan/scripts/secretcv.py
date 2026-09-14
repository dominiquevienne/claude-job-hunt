#!/usr/bin/env python3
"""SecretCV (`www.secretcv.com`, Türkiye) — the generalist whose first pages and advertisement pages are served open and whose every parameterised address answers 410 to this client — so the list is read one first page at a time (the country's, then the city and sector lists the site links), never paged; the list's own «20.409 İş İlanı Listelendi» printed beside every read; the ad's JobPosting and its labelled table read, the text scrubbed; the application behind a login that is never touched. Issue #385.

  secretcv.py list [--sections all|<slug>,<slug>] [--limit N]    /is-ilanlari and the linked /is-ilanlari/<slug>-is-ilanlari lists, the first page of each (20 cards)
  secretcv.py ad --url <https://www.secretcv.com/<firm>-<firmId>/<slug>-is-ilanlari-<id>>

THE PAGER ANSWERS 410. `/is-ilanlari/?sf=2` — the address the page's own «Sonraki» link
carries — answers **HTTP 410 Gone** to this client (with or without the slash, with a
Referer, on `?sf=342`, on `?l=50`, on `?sr=4`: every parameterised address, 02:39–02:41 UTC),
and the 410 body carries the next page's cards. **A readable body is not an answer — the
code decides: the adapter never sends a parameter, reads the first page only, and says
so.** What multiplies the read is the site's own structure: 33 city and sector lists linked
from the listing (`/is-ilanlari/istanbul-is-ilanlari`, `/is-ilanlari/cagri-merkezi-is-ilanlari`
…), each a first page of 20, deduplicated by id. The pages beyond the first are a browser
candidate (a refusal by code with rules that open the path).

THE RULES (550 B): `User-agent: *` → `Allow: /`; `GPTBot` → `Allow: /`; `OAI-SearchBot` →
`Allow: /` and then nineteen `Disallow` lines (`*/?sf=*`, `*/?ilanId=*`, `*/?redirect=*`,
`*hesabim*`, `/is-ilanlari/ara`, `*ara?k=*` …) — **which the parser assigns to the
`OAI-SearchBot` group, so the `*` group this client falls in reads `Allow: /`** (the
guard's verdict, `certain: True`) — and the transport's 410 on every parameter says what
the file's layout does not: **no parameter is ever sent**, and one in an address is refused
before the gate; the search (`/ara`, `?k=`), the account (`hesabim`), the application
(`/giris-yap?redirect=1&ilanId=`) are not roads this adapter takes. No Crawl-delay; 2 s is ours. The issue's premise — «les fiches exigent
une connexion» — was the APPLICATION: the advertisement page itself answers 200 with a
JSON-LD JobPosting and its full description; the «İşe Başvur» button is the login.

THE LIST. `/is-ilanlari` («İş İlanları») prints «20.409 İş İlanı Listelendi» — the stated
count, printed beside every read — 20 cards a page, a pager `/is-ilanlari/?sf=N` whose
«Son Sayfa» names the last page (342 on the day) and which answers 410. A card: the ad's address
(`/<firm>-<firmId>/<slug>-is-ilanlari-<id>`, the id at the tail), title, employer
(`/firma/<slug>-<firmId>-is-ilanlari`), city («İstanbul Avrupa»), and the age the site
prints («İlan Tarihi: Bugün», «1 gün önce»).

THE AD. A JSON-LD JobPosting — title, `datePosted`, `validThrough`, `employmentType`,
`hiringOrganization` (name, `/firma/` url), `jobLocation` (locality = region = the city),
`qualifications`, `baseSalary` («-» on the day: a value is a number, `salary_unit_stated`
only with one) — and the page's labelled table («İlan Tarihi» 10-09-2026, «İstihdam Türü»,
«Sektör», «Eğitim Seviyesi», «Şehirler», «Yabancı Uyruklu Çalışabilir»); the description in
the `content-job` card («İş Açıklaması»), ended before the site's own «İlana başvuru
yapabilmeniz için…» boilerplate; **scrubbed of Turkish telephone numbers and e-mail
addresses; `contacts_withheld` on every record; the application is a login and is never
touched.**

Measured 2026-09-14 02:36–02:38 UTC by the declared client, the guard on the exact path:
the list 341 093 B, 20 cards, «20.409», «Son Sayfa» ?sf=342; the ad 155 557 B with its
JobPosting.
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

HOST = "www.secretcv.com"
LIST = f"https://{HOST}/is-ilanlari"
PAGE_SIZE = 20

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+|\[email(?:\s| |&#160;)*protected\]")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+90[\s ]?|0)[\s ]?\(?\d{3}\)?[\s ]?\d{3}[\s ]?\d{2}[\s ]?\d{2}(?!\d)")
COUNT_RE = re.compile(r"(\d[\d.  ]*)\s*İş İlanı Listelendi")
CARD_RE = re.compile(r'<div class="cv-job-box job-list[^"]*">(.*?)<a href="https://www\.secretcv\.com/giris-yap[^"]*"', re.S)
TITLE_RE = re.compile(r'<a href="(https://www\.secretcv\.com/[^"/]+/[^"]+-is-ilanlari-(\d+))"[^>]*class="title[^"]*">(.*?)</a>', re.S)
COMPANY_RE = re.compile(r'<a href="https://www\.secretcv\.com/firma/([^"]+)"[^>]*class="company[^"]*">(.*?)</a>', re.S)
CITY_RE = re.compile(r'<span class="city[^"]*">\s*<span>(.*?)</span>', re.S)
AGE_RE = re.compile(r"İlan Tarihi:\s*([^<]+)<")
LAST_RE = re.compile(r'href="https://www\.secretcv\.com/is-ilanlari/\?sf=(\d+)"\s+title="Son Sayfa"')
ID_RE = re.compile(r"-is-ilanlari-(\d+)/?$")
PAIR_RE = re.compile(r'<span class="title">\s*(.*?)\s*</span>\s*</div>\s*<div class="col-6">\s*<span class="desc">\s*(.*?)\s*</span>', re.S)
DESC_RE = re.compile(r'<span class="cj-title">\s*İş Açıklaması\s*</span>(.*?)(?=<a [^>]*giris-yap|İlana başvuru yapabilmeniz|<div class="cv-card-head|</div>\s*</div>\s*</div>)', re.S)   # ended at the «İşe Başvur» login button


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[secretcv] {msg}", file=sys.stderr)


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
    if urllib.parse.urlsplit(url).query:
        die(f"{url}: no parameter is ever sent — every parameterised address answered 410 to this client on the day, and the search, the account and the application parameters are refused to a named crawler in writing", EXIT_REFUSED)
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


def num(s):
    return int(re.sub(r"[\s  .]", "", s))


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def stated(body):
    m = COUNT_RE.search(text(body))
    return num(m.group(1)) if m else None


def last_page(body):
    m = LAST_RE.search(body)
    return int(m.group(1)) if m else None


def cards(body):
    out = []
    for block in CARD_RE.findall(body):
        t = TITLE_RE.search(block)
        if not t:
            continue
        url, jid, title = t.groups()
        c = COMPANY_RE.search(block)
        city = CITY_RE.search(block)
        age = AGE_RE.search(block)
        out.append({
            "source": "secretcv", "country": "TR", "ledger_id": f"secretcv:{jid}", "id": jid,
            "url": url, "title": text(title),
            "employer": text(c.group(2)) if c else None, "employer_slug": c.group(1) if c else None,
            "city": text(city.group(1)) if city else None,
            "age": text(age.group(1)) if age else None,   # «Bugün», «1 gün önce» — the site's own words
            "contacts_withheld": True, "language": "tr",
        })
    return out


SECTION_RE = re.compile(r'href="https://www\.secretcv\.com/is-ilanlari/([a-z0-9-]+-is-ilanlari)"')


def sections_of(body):
    """The city and sector lists the listing links — `/is-ilanlari/<slug>-is-ilanlari`, in the page's order, once each."""
    out = []
    for slug in SECTION_RE.findall(body):
        if slug not in out:
            out.append(slug)
    return out


def cmd_list(a):
    rows, seen, read = [], set(), []
    code, body = request(LIST)
    if code != 200:
        die(f"{LIST}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    total, last = stated(body), last_page(body)
    page = cards(body)
    if not page:
        die(f"{LIST}: 200 and not one card — the template changed; not an empty market", EXIT_PARTIAL)
    read.append(("/is-ilanlari", len(page)))
    for r in page:
        if r["id"] not in seen:
            seen.add(r["id"])
            rows.append(r)
    want, linked = [], sections_of(body)
    if a.sections:
        if a.sections.strip().lower() == "all":
            want = linked
        else:
            for slug in [x.strip() for x in a.sections.split(",") if x.strip()]:
                slug = slug if slug.endswith("-is-ilanlari") else f"{slug}-is-ilanlari"
                if slug not in linked:
                    die(f"--sections {slug!r}: not a list the site links from /is-ilanlari — " + ", ".join(linked[:12]) + " …")
                want.append(slug)
    for slug in want:
        if a.limit and len(rows) >= a.limit:
            break
        url = f"{LIST}/{slug}"
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        page = cards(body)
        if not page:
            die(f"{url}: 200 and not one card — the template changed; not an empty market", EXIT_PARTIAL)
        read.append((f"/is-ilanlari/{slug}", len(page)))
        for r in page:
            if r["id"] not in seen:
                seen.add(r["id"])
                r["section"] = slug
                rows.append(r)
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    where = f"{len(read)} first page(s) ({sum(c for _, c in read)} cards, {th(len(rows))} distinct)"
    if total is None:
        note(f"{th(n)} emitted from {where} — the list's own count («… İş İlanı Listelendi») was not found; not compared.")
    else:
        note(f"{th(n)} emitted from {where}, the list states {th(total)} over {last or '?'} pages — the pager answers 410 to this client: first pages only, never a shortfall claimed; --sections all reads the {len(linked)} lists the site links.")
    note("no parameter is ever sent (the pager included); the application («İşe Başvur») is a login and is never touched; the ad's text is scrubbed.")


def ldjson(body):
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S):
        try:
            d = json.loads(m, strict=False)
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("@type") == "JobPosting":
            return d
    return None


def pairs(body):
    return {text(k): re.sub(r"\s+", " ", text(v)) for k, v in PAIR_RE.findall(body)}


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = ID_RE.search(parts.path)
    if parts.netloc != HOST or not m or parts.path.count("/") != 2:
        die(f"{a.url}: not an advertisement address (https://{HOST}/<firm>-<firmId>/<slug>-is-ilanlari-<id>)")
    url = f"https://{HOST}{parts.path.rstrip('/')}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    ld = ldjson(body)
    desc = DESC_RE.search(body)
    if not ld and not desc:
        die(f"{url}: 200 without a JobPosting or a description block — the template changed", EXIT_PARTIAL)
    ld = ld or {}
    tb = pairs(body)
    org = ld.get("hiringOrganization") or {}
    addr = ((ld.get("jobLocation") or {}).get("address") or {}) if isinstance(ld.get("jobLocation"), dict) else {}
    sal = (ld.get("baseSalary") or {}).get("value") or {}
    value = num(str(sal.get("value"))) if re.fullmatch(r"[\d.  ]+", str(sal.get("value") or "").strip()) else None
    unit = (sal.get("unitText") or "").strip().lower() or None
    posted_tb = tb.get("İlan Tarihi")
    print(json.dumps({
        "source": "secretcv", "country": "TR", "ledger_id": f"secretcv:{m.group(1)}", "id": m.group(1), "url": url,
        "title": htmlmod.unescape(ld.get("title") or ld.get("name") or "").strip() or None,
        "employer": htmlmod.unescape(org.get("name") or "").strip() or None, "employer_url": org.get("url") or None,
        "city": addr.get("addressLocality") or tb.get("Şehirler"),
        "employment_type": ld.get("employmentType") or tb.get("İstihdam Türü"),
        "sector": tb.get("Sektör"), "education": tb.get("Eğitim Seviyesi"), "foreigners": tb.get("Yabancı Uyruklu Çalışabilir"),
        "salary_min": value, "salary_max": value, "salary_currency": ((ld.get("baseSalary") or {}).get("currency") or None) if value is not None else None,
        "salary_unit": unit if value is not None else None, "salary_unit_stated": bool(unit) and value is not None,
        "posted": (ld.get("datePosted") or "")[:10] or None,
        "posted_on_page": f"{posted_tb[6:10]}-{posted_tb[3:5]}-{posted_tb[0:2]}" if posted_tb and re.fullmatch(r"\d{2}-\d{2}-\d{4}", posted_tb) else posted_tb,
        "valid_through": (ld.get("validThrough") or "")[:10] or None,
        "qualifications": scrub(htmlmod.unescape(ld.get("qualifications") or "")) or None,
        "description": scrub(text(desc.group(1))) if desc else scrub(htmlmod.unescape(ld.get("description") or "")),
        # the «İşe Başvur» button is /giris-yap?redirect=1&ilanId=<id> — a login, never touched
        "contacts_withheld": True, "language": "tr",
    }, ensure_ascii=False))
    note(f"{url}: read; the text is scrubbed; the application is a login and is never touched.")


def main():
    p = argparse.ArgumentParser(description="SecretCV — the Turkish generalist's open list and ads; the list's own count beside every walk; the application login never touched; the text scrubbed. Issue #385.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the first page of /is-ilanlari (20 cards); --sections all adds the first page of every city and sector list the site links")
    l_.add_argument("--sections", help="all · or slugs separated by commas (istanbul, cagri-merkezi …)")
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
