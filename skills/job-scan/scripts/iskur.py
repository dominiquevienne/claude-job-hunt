#!/usr/bin/env python3
"""İŞKUR (`esube.iskur.gov.tr`) — Türkiye's public employment agency, through the WebForms search its own page posts; «Toplam Kayıt: N» printed beside every walk; the employer's name is behind a login and stays there. Issue #381.

  iskur.py search [--il 34] [--pages N] [--limit N]
  iskur.py ad --url <https://esube.iskur.gov.tr/Istihdam/AcikIsIlanDetay.aspx?uiID=<11 digits>>

THE ROUTE IS THE FORM — `/Istihdam/AcikIsIlanAra.aspx`, ASP.NET WebForms:

  GET  the page                                   -> __VIEWSTATE, __EVENTVALIDATION, the selects (ctl04$ctlIl = province, 81 + «all»)
  POST every field + __EVENTTARGET=ctl04$ctlAcikIsPageCommand$CommandItem_Search   -> «Toplam Kayıt: 34049», «/ 2270 Sayfaya Git», 15 rows
  POST every field of the results + __EVENTTARGET=ctl04$ctlDataPagerDetay$btnNext  -> the next page (txtCurrentPage echoes it)

Measured 2026-09-13 18:08 UTC by the declared client: 34 049 open
postings, 2 270 pages of 15; page 2 by `btnNext`, page 5 by
`btnChangeCurrentPage` with `txtCurrentPage=5` — both answered with the
page asked. The rules (70 B): `*` Allow: /, one Disallow on a popup path
this adapter never touches; no Crawl-delay — 3 s is ours. **`--pages`
defaults to 10** (150 rows) and the note says the walk was bounded by
request; 2 270 pages is not a run.

THE ROW carries the occupation (the link text — the site's «title»),
the employer's TYPE (Özel / Kamu), period (Daimi / Geçici), work type
(Tam Zamanlı …), the number of open positions, the workplace («İl Geneli
Başvuru (Çalışma Yeri: ÇANKIRI / ŞABANÖZÜ)»), the id (11 digits), the
application deadline and the days left — and the same in the share
button's data attributes, which are what the adapter reads. **The
employer's NAME is not on the page: «İşyeri adını görmek için Sisteme
Üye Girişi yapmanız gerekmektedir» — a login is required, and this
adapter never logs in**; `employer` is null and `employer_hidden` says
why. THE DETAIL PAGE (`AcikIsIlanDetay.aspx?uiID=`) is served without a
login but shows only the occupation, the experience and the education
bounds — the job description too is behind the login. No contact is on
either page.
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

HOST = "esube.iskur.gov.tr"
BASE = f"https://{HOST}"
SEARCH = f"{BASE}/Istihdam/AcikIsIlanAra.aspx"
DETAIL_RE = re.compile(r"^https?://esube\.iskur\.gov\.tr/Istihdam/AcikIsIlanDetay\.aspx\?uiID=(\d{11})$")
PAGE_SIZE = 15
TOTAL_RE = re.compile(r"Toplam Kayıt:\s*([\d\.]+)")
PAGES_RE = re.compile(r"/\s*(\d+)\s*Sayfaya Git")
ROW_RE = re.compile(r"<a[^>]*class=\"[^\"]*share-toggle[^\"]*\"([^>]*)>", re.S)
LOGIN_NOTE = "İşyeri adını görmek için Sisteme Üye Girişi yapmanız gerekmektedir"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[iskur] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=3.0)   # no Crawl-delay in the rules; 3 s is ours
_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_JAR))


def request(url, data=None):
    """One request in the session — GET, or POST of an ordered field list."""
    gate(url)
    _PACE.wait()
    headers = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "tr"}
    body = None
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(wire_url(url), data=body, headers=headers)
    try:
        with _OPENER.open(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</td>|</th>|</tr>|</li>|</h\d>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def form_fields(body):
    """Every field a browser would post: hidden and text inputs, checked radios/boxes, each select's selected option — in document order, without the event pair."""
    out = []
    for m in re.finditer(r"<input([^>]*)>", body or ""):
        a = m.group(1)
        n = re.search(r'name="([^"]+)"', a)
        if not n or n.group(1) in ("__EVENTTARGET", "__EVENTARGUMENT"):
            continue
        t = (re.search(r'type="([^"]+)"', a) or [None, "text"])[1]
        v = re.search(r'value="([^"]*)"', a)
        val = htmlmod.unescape(v.group(1)) if v else ""
        if t in ("hidden", "text") or (t in ("radio", "checkbox") and re.search(r"\bchecked\b", a)):
            out.append((n.group(1), val))
    for m in re.finditer(r'<select[^>]*name="([^"]+)"[^>]*>(.*?)</select>', body or "", re.S):
        sel = re.search(r'<option[^>]*\bselected\b[^>]*value="([^"]*)"', m.group(2)) or re.search(r'<option[^>]*value="([^"]*)"', m.group(2))
        out.append((m.group(1), htmlmod.unescape(sel.group(1)) if sel else ""))
    return out


def postback(body, target, override=None):
    """The results form re-posted with one event target — the only way the page turns."""
    fields = [(k, v) for k, v in form_fields(body) if not (override and k in override)]
    fields = [("__EVENTTARGET", target), ("__EVENTARGUMENT", "")] + fields + [(k, v) for k, v in (override or {}).items()]
    code, out = request(SEARCH, fields)
    if code != 200:
        die(f"{SEARCH} ({target}): HTTP {code}", EXIT_PARTIAL)
    if "__VIEWSTATE" not in out:
        die(f"{SEARCH} ({target}): the answer carries no __VIEWSTATE ({len(out)} characters) — not the search page; a firewall page or a redirect.", EXIT_PARTIAL)
    return out


def stated(body):
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", body or ""))
    m = TOTAL_RE.search(t)
    p = PAGES_RE.search(t)
    return (int(m.group(1).replace(".", "")) if m else None, int(p.group(1)) if p else None)


def current_page(body):
    m = re.search(r'name="ctl04\$ctlDataPagerDetay\$txtCurrentPage"[^>]*value="(\d+)"', body or "")
    return int(m.group(1)) if m else None


def rows(body):
    """One row per share button — its data attributes are the row's own fields, and the occupation link beside them."""
    out = []
    for m in ROW_RE.finditer(body or ""):
        attrs = m.group(1)
        d = {k: htmlmod.unescape(v).strip() for k, v in re.findall(r"data-([a-z]+)='([^']*)'", attrs)}
        ident = d.get("ilanno")
        if not ident:
            continue
        pos = d.get("acikissayi")
        out.append({
            "source": "iskur", "country": "TR", "ledger_id": f"iskur:{ident}", "id": ident,
            "url": f"{BASE}/Istihdam/AcikIsIlanDetay.aspx?uiID={ident}",
            "title": d.get("meslekler") or None,                       # the occupation — the site's own heading for the posting
            "employer": None, "employer_hidden": "login required — the site prints «%s»" % LOGIN_NOTE,
            "employer_type": d.get("isverentur") or None,              # Özel (private) / Kamu (public)
            "work_type": d.get("calismasekli") or None,
            "workplace": re.sub(r"\s+", " ", d.get("il") or "").strip() or None,
            "positions": int(pos) if (pos or "").isdigit() else None,
            "application_deadline": d.get("sontarih") or None,        # DD.MM.YYYY as published
            "language": "tr",
        })
    return out


def cmd_search(a):
    code, page = request(SEARCH)
    if code != 200 or "__VIEWSTATE" not in page:
        die(f"{SEARCH}: HTTP {code}, {len(page)} characters — not the search form" + (" (a «Request Rejected» firewall page?)" if "Request Rejected" in page else ""), EXIT_PARTIAL)
    override = {"ctl04$ctlIl": a.il} if a.il else None
    body = postback(page, "ctl04$ctlAcikIsPageCommand$CommandItem_Search", override)
    total, pages_stated = stated(body)
    if total is None:
        if not rows(body):
            note("the page states no «Toplam Kayıt» and carries no row — the site says nothing matched this search.")
            return
        die(f"{SEARCH}: rows on the page and no «Toplam Kayıt: N» — the count line changed; a walk without it is not compared.", EXIT_PARTIAL)
    out, seen, pageno = [], set(), 1
    while True:
        new = 0
        for r in rows(body):
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            out.append(r)
            new += 1
        if new == 0 or len(out) >= total:
            break
        if a.pages and pageno >= a.pages:
            break
        if a.limit and len(out) >= a.limit:
            break
        pageno += 1
        body = postback(body, "ctl04$ctlDataPagerDetay$btnNext")
        now = current_page(body)
        if now != pageno:
            die(f"{SEARCH}: asked for page {pageno}, the pager says {now!r} — the page did not turn.", EXIT_PARTIAL)
    emitted = out[:a.limit] if a.limit else out
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    where = f"(il {a.il})" if a.il else "(all provinces)"
    bounded = (a.pages and pageno >= a.pages and total > pageno * PAGE_SIZE) or (a.limit and a.limit < total)
    if bounded:
        note(f"{th(n)} emitted of the {th(total)} the site states {where}, {th(pages_stated or 0)} page(s) of {PAGE_SIZE} — {pageno} walked by request (--pages/--limit), not a shortfall.")
    elif n == total:
        note(f"{th(n)} emitted over {pageno} page(s), site states {th(total)} {where} — equal.")
    else:
        note(f"{th(n)} emitted over {pageno} page(s), site states {th(total)} {where} — {th(abs(total - n))} " + ("short" if total > n else "more emitted than the site states") + ".")
    note(f"the employer's name is behind a login on every row — never read; `employer` is null on all {th(n)}.")


def cmd_ad(a):
    m = DETAIL_RE.match((a.url or "").strip())
    if not m:
        die(f"{a.url}: not a detail address — expected {BASE}/Istihdam/AcikIsIlanDetay.aspx?uiID=<11 digits>")
    ident = m.group(1)
    code, body = request(a.url)
    if code in (404, 410):
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    if "İşgücü İstemi" not in body:
        die(f"{a.url}: not the detail page ({len(body)} characters) — a firewall page or a redirect.", EXIT_PARTIAL)
    t = text(body)
    lines = [l.strip() for l in t.split("\n") if l.strip()]

    HEADINGS = {"İlan Geri Bildirim Formu", "Öğrenim ve Kişisel Bilgiler", "Meslek Bilgileri", "Nitelik ve Beceriler", "İş Tanımı", "Paylaş", "Bildirim Kategorisi"}

    def after(label):
        """The value right after a label — «:» is the page's separator; «×» (a modal's close glyph) or the next
        section's heading in that place means the value is empty, as it was for the upper education bound."""
        for i, l in enumerate(lines):
            if l == label:
                nxt = [x for x in lines[i + 1:i + 3] if x != ":"]
                v = nxt[0] if nxt else None
                return None if v is None or v == "×" or v in HEADINGS or v.endswith("Seviyesi") or v in ("Yıl", "Deneyim") else v
        return None
    print(json.dumps({
        "source": "iskur", "country": "TR", "ledger_id": f"iskur:{ident}", "id": ident, "url": a.url,
        "title": after("Deneyim") or after("Meslek"),
        "education_min": after("En Az Öğrenim Seviyesi"),
        "education_max": after("En Fazla Öğrenim Seviyesi"),
        # the description, the employer and the application are behind the login the page asks for; none is read
        "login_required_for": ["employer", "description", "application"],
        "login_note": "İlan detaylarını görmek ve iş başvurusu yapmak için sisteme giriş yapınız" if "sisteme giriş yapınız" in t else None,
        "language": "tr",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="İŞKUR — Türkiye's public employment agency through the WebForms search its page posts; «Toplam Kayıt: N» beside every walk; the employer's name stays behind the login. Issue #381.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="the open postings, 15 a page, 3 s apart, 10 pages unless told otherwise; --il narrows to a province (the site's numeric code, 34 = İstanbul)")
    s.add_argument("--il", help="province code as the site numbers them (1 Adana … 34 İstanbul … 81 Düzce)")
    s.add_argument("--pages", type=int, default=10)
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one public detail page — occupation and education bounds; the rest is behind the login")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
