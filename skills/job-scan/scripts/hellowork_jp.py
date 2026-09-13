#!/usr/bin/env python3
"""Hello Work (ハローワークインターネットサービス, `www.hellowork.mhlw.go.jp`) — Japan's public employment service (not `hellowork.com`, the French board of `hellowork.py`), through the session-bound search form it publishes; the count the site states is printed beside every walk. Issue #304.

  hellowork_jp.py search [--pref 13[,27,…]] [--word TEXT] [--kind 1] [--pages N] [--limit N]
  hellowork_jp.py ad --url <詳細を表示 address> [--pref …] [--word …]

THE ROUTE IS THE FORM — `/kensaku/GECA110010.do`, a Struts-style JSP:

  GET  ?action=initDisp&screenId=GECA110010     -> the form and a JSESSIONID (the bare .do without the query is the site's «システムエラー» page, 200)
  POST hidden fields + kjKbnRadioBtn + filters + searchBtn + action=searchBtn   -> «検索結果 N件 中 1～30件», 30 cards
  POST every field of the results form + fwListNaviBtnK=K + action=fwListNaviBtnK  -> page K (fwListNowPage echoes it)

**A page request that does not carry the whole results form is the
system-error page**, and so is a free word in ASCII: the site takes
full-width characters only («全角50文字以内»), so `--word python` is sent
as «ｐｙｔｈｏｎ» and the note says so. Measured 2026-09-13 17:04–17:08 UTC
by the declared client: 1 082 197 for 一般 with no filter; 102 981 for
Tokyo (`todohukenHidden=13`, a JIS prefecture code); 33 for Tokyo +
«ｐｙｔｈｏｎ», page 2 «31～33».

NO RULES FILE (404 — an absence, a knowledge) and no `Crawl-delay`; this
adapter spaces 3 s and never walks the whole inventory: `--pages`
defaults to 10 (300 cards) and the note says the walk was bounded by
request, never «short». A filterless walk of 36 000 pages is not a run.

THE CARD carries what the listing shows — 受付年月日, 紹介期限日, the
employment labels (正社員 / 有期雇用 / フル / パート), the workplace, 職種
(title), 仕事の内容 (an excerpt), 事業所名, 就業場所, 賃金 (a yen range,
月額 by the site's convention), 就業時間, 休日, 求人番号 (the id, `NNNNN-NNNNNNNN`,
the first five digits the REGISTERING OFFICE — a Tokyo search returns ids
from 04, 09, 11 offices whose workplace is Tokyo), 求人数. **No contact is
read**: the 求人票 (job sheet) and the detail page carry the employer's
address and telephone, and this adapter emits neither.
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

HOST = "www.hellowork.mhlw.go.jp"
BASE = f"https://{HOST}"
SEARCH = f"{BASE}/kensaku/GECA110010.do"
INIT = SEARCH + "?action=initDisp&screenId=GECA110010"
PAGE_SIZE = 30
COUNT_RE = re.compile(r"検索結果\s*([\d,]+)件\s*中\s*([\d,]+)～([\d,]+)")
ID_RE = re.compile(r"(\d{5}-\d{8})</div>")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[hellowork-jp] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=3.0)   # no rules file, no Crawl-delay; 3 s is ours
_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_JAR))


def request(url, data=None):
    """One request in the session — GET, or POST of an ordered field list."""
    gate(url)
    _PACE.wait()
    headers = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "ja"}
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
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</div>|</p>|</li>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t　]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def zenkaku(s):
    """ASCII to full-width — the form refuses anything else in the free word («全角50文字以内»)."""
    return "".join(chr(ord(c) + 0xFEE0) if 0x21 <= ord(c) <= 0x7E else c for c in s or "")


def form_fields(body):
    """Every field a browser would submit from the results form: hidden, text with a value, checked radio/checkbox — in document order."""
    out = []
    for m in re.finditer(r"<input([^>]*)>", body or ""):
        a = m.group(1)
        n = re.search(r'name="([^"]+)"', a)
        if not n:
            continue
        t = (re.search(r'type="([^"]+)"', a) or [None, "text"])[1]
        v = re.search(r'value="([^"]*)"', a)
        val = htmlmod.unescape(v.group(1)) if v else ""
        if t == "hidden" or (t == "text" and val) or (t in ("radio", "checkbox") and re.search(r"\bchecked\b", a)):
            out.append((n.group(1), val))
    return out


def hidden_fields(body):
    return [(k, v) for k, v in form_fields(body) if re.search(r'<input[^>]*name="%s"[^>]*type="hidden"|<input[^>]*type="hidden"[^>]*name="%s"' % (re.escape(k), re.escape(k)), body or "")]


def system_error(body):
    return "システムエラー" in (body or "")[:3000]


def stated(body):
    m = COUNT_RE.search(htmlmod.unescape(re.sub(r"<[^>]+>", " ", body or "")))
    return (int(m.group(1).replace(",", "")), int(m.group(2).replace(",", "")), int(m.group(3).replace(",", ""))) if m else None


def cards(body):
    """The 30 cards of a results page, each as the listing shows it."""
    starts = [m.start() for m in re.finditer(r'<table class="kyujin\b', body or "")]
    out = []
    for i, s in enumerate(starts):
        c = body[s:starts[i + 1] if i + 1 < len(starts) else s + 40000]
        ident = (ID_RE.search(c) or [None, None])[1]
        if not ident:
            continue
        rows = {}
        for m in re.finditer(r'<td class="label_col">(.*?)</td>\s*<td class="data_col">(.*?)</td>', c, re.S):
            rows[text(m.group(1)).split("\n")[0].strip()] = text(m.group(2))
        head = c[:c.find('<tr class="kyujin_body">')] if '<tr class="kyujin_body">' in c else c[:3000]
        dates = re.findall(r"(受付年月日|紹介期限日)</div>\s*<div>：?([^<]+)<", head)
        labels = [text(x) for x in re.findall(r'<span class="bg_label white_back">\s*<div>([^<]+)</div>', head)]
        place = (re.search(r'fa-map-marker[^>]*></i>\s*<div[^>]*>([^<]+)<', head) or [None, None])[1]
        detail = (re.search(r'href="([^"]*action=dispDetailBtn[^"]*)"', c) or [None, None])[1]
        salary = rows.get("賃金", "")
        sal = re.search(r"([\d,]+)円\s*〜\s*([\d,]+)円", salary)
        out.append({
            "source": "hellowork-jp", "country": "JP", "ledger_id": f"hellowork-jp:{ident}", "id": ident,
            "registering_office": ident[:5],
            "url": (SEARCH + "?" + htmlmod.unescape(detail).split("?", 1)[1]) if detail else None,
            "title": rows.get("職種", "").split("\n")[0].strip() or None,
            "employer": rows.get("事業所名", "").split("\n")[0].strip() or None,
            "workplace": rows.get("就業場所") or (place.strip() if place else None),
            "employment_labels": labels,
            "received": dict(dates).get("受付年月日"), "referral_deadline": dict(dates).get("紹介期限日"),
            "salary_text": salary or None,
            "salary_min": int(sal.group(1).replace(",", "")) if sal else None,
            "salary_max": int(sal.group(2).replace(",", "")) if sal else None,
            # the card prints a yen range under 賃金 and no period — 月額 is the site's convention, and «read as» is
            # not «stated»: the unit is emitted as not stated, as itjobs.py does
            "salary_currency": "JPY" if sal else None, "salary_unit": None, "salary_unit_stated": False,
            "hours": rows.get("就業時間"), "holidays": rows.get("休日"),
            "openings": int(op.group(1)) if (op := re.search(r"求人数：\s*(\d+)\s*名", c)) else None,
            "description": rows.get("仕事の内容"),
            "language": "ja",
        })
    return out


def open_session():
    code, body = request(INIT)
    if code != 200 or system_error(body) or "searchBtn" not in body:
        die(f"{INIT}: HTTP {code}, {len(body)} characters — not the search form" + (" (the site's system-error page)" if system_error(body) else ""), EXIT_PARTIAL)
    # **The hidden fields only, plus what the search needs.** Sending the form's checked defaults as well
    # (its radios and checkboxes) made the site answer its system-error page on 2026-09-13 17:09 UTC —
    # a duplicate radio value is a shape the JSP refuses; the page-K request is the opposite case.
    return [(k, v) for k, v in hidden_fields(body)]


def first_page(a):
    base = open_session()
    # the form's own hidden `action` and `screenId` are replaced, not doubled: a second `action` is read
    # first by the servlet and the answer is the system-error page (2026-09-13 17:10 UTC, found by that)
    fields = [(k, v) for k, v in base if not k.startswith("fwList") and k not in ("todohukenHidden", "action", "screenId")]
    fields += [("kjKbnRadioBtn", str(a.kind)), ("todohukenHidden", a.pref or "")]
    if a.word:
        w = zenkaku(a.word)
        if w != a.word:
            note(f"free word sent full-width, as the form requires: «{w}»")
        fields += [("freeWordInput", w), ("freeWordRadioBtn", "0")]
    fields += [("searchBtn", "検索する"), ("action", "searchBtn"), ("screenId", "GECA110010")]
    code, body = request(SEARCH, fields)
    if code != 200 or system_error(body):
        die(f"{SEARCH}: HTTP {code} — the search answered the system-error page; the form's fields or the session changed.", EXIT_PARTIAL)
    if "入力エラー" in body:
        die(f"{SEARCH}: the form reports an input error («入力エラーがあります») — a filter this adapter sent is not in the shape the site takes.", EXIT_PARTIAL)
    return body


def next_page(body, page):
    # every field of the results form, as a browser submits it, then the button — measured 2026-09-13 17:08 UTC:
    # this shape turns the page; the same request with the form's own `action` removed answers the error page
    # **and `screenId` is NOT appended**: the results form already carries one, and a second copy — the shape
    # that worked for the first search, where the form's own was dropped first — answers the error page
    fields = [(k, v) for k, v in form_fields(body) if k != "searchBtn"]
    fields += [(f"fwListNaviBtn{page}", str(page)), ("action", f"fwListNaviBtn{page}")]
    code, body = request(SEARCH, fields)
    if code != 200 or system_error(body):
        die(f"{SEARCH} page {page}: HTTP {code} — the system-error page; a page request must carry the whole results form.", EXIT_PARTIAL)
    return body


def cmd_search(a):
    body = first_page(a)
    st = stated(body)
    if st is None:
        if not cards(body):
            note("the page states no count and carries no card — the site says nothing matched this search.")
            return
        die(f"{SEARCH}: cards on the page and no «検索結果 N件» — the count line changed; a walk without it is not compared.", EXIT_PARTIAL)
    total = st[0]
    rows, seen, page = [], set(), 1
    while True:
        new = 0
        for c in cards(body):
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            rows.append(c)
            new += 1
        if new == 0 or len(rows) >= total:
            break
        if a.pages and page >= a.pages:
            break
        if a.limit and len(rows) >= a.limit:
            break
        page += 1
        body = next_page(body, page)
        now = dict(form_fields(body)).get("fwListNowPage")
        if now != str(page):
            die(f"{SEARCH}: asked for page {page}, the form says page {now!r} — the pager did not follow.", EXIT_PARTIAL)
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    bounded = (a.pages and page >= a.pages and total > page * PAGE_SIZE) or (a.limit and a.limit < total)
    where = f"({'一般' if str(a.kind) == '1' else 'kind ' + str(a.kind)}" + (f", pref {a.pref}" if a.pref else "") + (f", «{zenkaku(a.word)}»" if a.word else "") + ")"
    if bounded:
        note(f"{th(n)} emitted of the {th(total)} the site states {where} — {page} page(s) of {PAGE_SIZE} walked by request (--pages/--limit), not a shortfall.")
    elif n == total:
        note(f"{th(n)} emitted over {page} page(s), site states {th(total)} {where} — equal.")
    else:
        note(f"{th(n)} emitted over {page} page(s), site states {th(total)} {where} — {th(abs(total - n))} " + ("short" if total > n else "more emitted than the site states") + ".")


def cmd_ad(a):
    if "action=dispDetailBtn" not in (a.url or "") or not a.url.startswith(SEARCH):
        die(f"{a.url}: not a 詳細を表示 address — expected {SEARCH}?screenId=…&action=dispDetailBtn&kJNo=…")
    # the detail lives in the session that listed it: the same search is re-issued first
    first_page(a)
    code, body = request(a.url)
    if code != 200 or system_error(body):
        die(f"{a.url}: HTTP {code} — the system-error page; the detail is session-bound and the search that listed it must come first (--pref/--word as on the search).", EXIT_PARTIAL)
    ident = (re.search(r"kJNo=(\d{13})", a.url) or [None, ""])[1]
    if "求人情報</title>" not in body and "<th scope=\"row\">求人番号</th>" not in body:
        die(f"{a.url}: the answer is not the detail page (title «{text((re.search(r'<title>(.*?)</title>', body, re.S) or [None, ''])[1])}») — a detail is session-bound.", EXIT_PARTIAL)
    rows = {}
    for m in re.finditer(r'<th scope="row">(.*?)</th>\s*<td[^>]*>(.*?)</td>', body, re.S):
        k = text(m.group(1)).replace("\n", " ")
        rows.setdefault(k, text(m.group(2)))
    # **No contact leaves this adapter**: the detail page carries the employer's address, telephone, FAX,
    # the representative's name and the corporate number — every row whose label names one is dropped
    # before anything is printed, and the dropped labels are listed so the absence is visible.
    drop = ("所在地", "電話", "ＦＡＸ", "FAX", "メール", "担当者", "郵便番号", "法人番号", "代表者", "事業所番号")
    kept = {k: v for k, v in rows.items() if not any(d in k for d in drop)}
    # the detail's 就業場所 is a street address with a postal code; the listing prints it to the city — the same
    # granularity is kept here (prefecture + city/ward), the street and the 〒 dropped as a premises' address
    place = kept.get("就業場所") or ""
    city = re.search(r"((?:東京都|北海道|(?:京都|大阪)府|.{2,3}県).*?(?:市|区|町|村|郡))", place)
    kept["就業場所"] = city.group(1) if city else re.sub(r"〒\S+\s*", "", place).split("\n")[0]
    kept["職種"] = re.sub(r"\s*職種解説\s*", " ", kept.get("職種") or "").strip() or None   # the «職種解説» link text is not the title
    print(json.dumps({"source": "hellowork-jp", "country": "JP", "ledger_id": f"hellowork-jp:{ident[:5]}-{ident[5:]}" if ident else None,
                      "id": rows.get("求人番号") or (f"{ident[:5]}-{ident[5:]}" if ident else None), "url": a.url,
                      "title": kept.get("職種"), "employer": kept.get("事業所名"), "workplace": kept.get("就業場所"),
                      "received": kept.get("受付年月日"), "referral_deadline": kept.get("紹介期限日"),
                      "office": kept.get("受理安定所"), "industry": kept.get("産業分類"),
                      "fields": kept, "contact_dropped": sorted(k for k in rows if k not in kept), "language": "ja"}, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Hello Work — Japan's public employment service through its own search form (a session, a POST per page); the site's «検索結果 N件» printed beside every walk; no contact ever emitted. Issue #304.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="the 一般 listing, filtered by prefecture (JIS code, up to three comma-separated) and/or a free word; 30 a page, 3 s apart, 10 pages unless told otherwise")
    s.add_argument("--pref", help="JIS prefecture code(s), e.g. 13 for Tokyo, 27 for Osaka — '13,27' for both")
    s.add_argument("--word", help="free word (sent full-width, as the form requires)")
    s.add_argument("--kind", default="1", help="求人区分: 1 一般 (default), 2 新卒・既卒, 3 季節, 4 出稼ぎ, 5 障害者")
    s.add_argument("--pages", type=int, default=10)
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one detail page, within the session of the search that listed it; contact rows dropped")
    d.add_argument("--url", required=True)
    d.add_argument("--pref")
    d.add_argument("--word")
    d.add_argument("--kind", default="1")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
