#!/usr/bin/env python3
"""Expresso Emprego (`expressoemprego.pt`) — the Portuguese daily's job board,
read from the live listing because the sitemap it declares died in 2019.

    expressoemprego.py search [--q juristas] [--localizacao lisboa] [--pages 3] [--limit N]
    expressoemprego.py ad --id 2466610

WHAT THE HOST DECLARES, AND WHAT IT SERVES — measured 2026-09-11 18:38–18:41 UTC

**Rules: everything permitted.** 118 bytes, md5
`d6d89b11dac16fe0e3898f1a2fced780`, the same ×4 on apex and `www` (the
`www` redirects to the apex): `AhrefsBot / Disallow: /`, then `* /
Disallow:` — empty, so nothing is refused — and `Sitemap:
https://expressoemprego.pt/sitemap.xml`. No `Crawl-delay`.

**The declared sitemap is a FOSSIL.** 1 133 696 bytes, md5 stable across two
reads, 5 873 `<url>` of which 1 513 are `/emprego/<slug>/<id>` — **and every
one of the 1 513 carries a `lastmod` of October or November 2019** (1 411 +
102), ids 1 606 727 to 1 998 140, while the live listing shows ids at
2 466 6xx. *A reader that counted the sitemap would report 1 513
advertisements dead for seven years.* This adapter never reads it.

**The live route is the listing.** `/ofertas-emprego` — 15 advertisements a
page, `?page=N` (0-based), and **the site's own total in the page: «1 917
empregos para a sua pesquisa»**. Each row: title, employer, date
(`11.09.2026`), `Localidade, Portugal` when the ad states one, and
`Referência: <id>` — the id is the URL's last segment.

**The search is a routing by path segments, read off the site's own
`main.js`** (`getURLCriteriosPesquisa`): `/emprego/pesquisa/<query>/
<localizacao>/…`, each empty criterion replaced by its NAME (`query`,
`localizacao`), and the trailing run of names trimmed. So `--q juristas` is
`/emprego/pesquisa/juristas/`, `--localizacao lisboa` alone is
`/emprego/pesquisa/query/lisboa/`. **The total follows the filter**:
`jurista` → «2 empregos para a sua pesquisa», 2 rows.

**The ad page carries no `JobPosting`** (0 `ld+json` of that type on
2026-09-11); the text is HTML inside `div.wucAnuncioDet`, up to the
«EMPREGOS SEMELHANTES» block. `/emprego` bare answers a 200 «Oops» page of
43 KB with zero rows — a 200 that is not an answer, and the zero-row path
here dies through `_zero.empty_first_page` rather than reporting it.

Nothing is translated: the adapter emits what the site says, in Portuguese.
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
from _robots import allowed as robots_allowed, full_path
from _ua import UA
from _zero import empty_first_page

HOST = "expressoemprego.pt"
BASE = f"https://{HOST}"
ROW = re.compile(r'<div class="posRelative bgGray1 resultadosBox')
LINK = re.compile(r'<h3[^>]*>\s*<a href="(/emprego/[^"]+/(\d+))"[^>]*>(.*?)</a>', re.S)
COMPANY = re.compile(r"<h4[^>]*>(.*?)</h4>", re.S)
DATE_LOC = re.compile(r'<span class="px13 colorBlack">(.*?)</span>\s*<span class="colorBlue2 fontBold">\|</span>\s*<span class="colorGray8">Refer', re.S)
TOTAL = re.compile(r"<b>\s*([\d\s.]+?)\s*</b>\s*</span>\s*<span[^>]*>\s*empregos? para a sua pesquisa", re.S)
PAGE = re.compile(r'href="[^"]*\?page=(\d+)"')
NONE_FOUND = re.compile(r"N[ãa]o foram encontradas Ofertas de Emprego para a sua pesquisa", re.I)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[expressoemprego] {msg}", file=sys.stderr)


def _robots_gate(url, exit_code=7):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", 8)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    return a


_PACE = Pace(HOST, own=2.0)


def get(url):
    _robots_gate(url)
    _PACE.wait()
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90)
        return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach {HOST}: {e}")


def clean(s):
    return re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def to_text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?is)<br\s*/?>|</p>|</li>|</h\d>|</div>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    lines = [re.sub(r"[ \t]+", " ", htmlmod.unescape(l)).strip()
             for l in markup.split("\n")]
    return "\n".join(l for l in lines if l).strip()


def search_url(q=None, localizacao=None, page=0):
    """The site's own routing, read off its `main.js`: each criterion a path
    segment, an empty one replaced by its name, the trailing names trimmed."""
    if q or localizacao:
        segs = [urllib.parse.quote(q) if q else "query",
                urllib.parse.quote(localizacao) if localizacao else "localizacao"]
        while segs and segs[-1] in ("query", "localizacao"):
            segs.pop()
        path = "/emprego/pesquisa/" + "/".join(segs) + "/"
    else:
        path = "/ofertas-emprego"
    # **`?page=` is 1-based and `page=1` is the first page again** — measured
    # 2026-09-11: `?page=0` and `?page=1` both serve ids 2466610…, `?page=2`
    # serves 2466778…. So the n-th page (0-based here) is `?page=n+1`, and
    # the first is asked without the parameter.
    return BASE + path + (f"?page={page + 1}" if page else "")


def ad_url(ident, slug="oferta"):
    """Contract 4: from the id. The site routes on the id; the slug is cosmetic."""
    return f"{BASE}/emprego/{slug}/{ident}"


def stated_total(body):
    m = TOTAL.search(body)
    return int(re.sub(r"\D", "", m.group(1))) if m else None


def rows(body):
    out = []
    for box in ROW.split(body)[1:]:
        m = LINK.search(box)
        if not m:
            continue
        c = COMPANY.search(box)
        dl = DATE_LOC.search(box)
        date = loc = None
        if dl:
            parts = [clean(p) for p in re.split(r"<span[^>]*>\|</span>", dl.group(1))]
            parts = [p for p in parts if p]
            date = parts[0] if parts else None
            loc = parts[1] if len(parts) > 1 else None
        out.append({
            "id": m.group(2),
            "ledger_id": f"expressoemprego:{m.group(2)}",
            "url": BASE + m.group(1),
            "title": clean(m.group(3)),
            "company": clean(c.group(1)) if c else None,
            "provider": "expressoemprego",
            "location": loc,
            "country": "PT",
            "countries": ["PT"],
            "date": date,            # the listing's, `DD.MM.YYYY`
            "language": "pt",
        })
    return out


def cmd_search(a):
    seen, kept, total, read_pages = set(), 0, None, 0
    for page in range(a.pages):
        url = search_url(a.q, a.localizacao, page)
        status, body = get(url)
        if status != 200:
            die(f"{HOST} answered HTTP {status} on {url}", 4)
        rs = rows(body)
        if page == 0:
            total = stated_total(body)
            if not rs and total in (0, None):
                if total == 0 or NONE_FOUND.search(body):
                    # **The site's own zero sentence**: «Não foram encontradas
                    # Ofertas de Emprego para a sua pesquisa» — measured on a
                    # nonsense query, 80 552 characters and that line.
                    note(f"0 rows, and the site says «Não foram encontradas "
                         f"Ofertas de Emprego para a sua pesquisa» — a real "
                         f"zero, in the site's words.")
                    return
                die(empty_first_page("expressoemprego", body, what="result row",
                                     candidates=len(ROW.split(body)) - 1,
                                     where=url, what_asked=a.q)
                    + " And no «empregos para a sua pesquisa» total on the "
                      "page: the shape of the «Oops» page `/emprego` answers "
                      "with a 200.", 6)
            if not rs:
                die(empty_first_page("expressoemprego", body, what="result row",
                                     where=url, what_asked=a.q)
                    + f" And the site states {total} for this search: the two "
                      f"disagree.", 6)
        if not rs:
            note(f"page {page} carried no row — the end of the listing after "
                 f"{read_pages} page(s).")
            break
        read_pages += 1
        for c in rs:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            if a.limit and kept >= a.limit:
                continue
            print(json.dumps(c, ensure_ascii=False))
            kept += 1
    note(f"{kept} emitted, {len(seen)} distinct over {read_pages} page(s) of 15; "
         f"the site states {total} empregos for this search"
         + (f" — stopped at --pages {a.pages}, raise it to go further"
            if total and len(seen) < total and read_pages == a.pages else ""))


def cmd_ad(a):
    if not a.id.isdigit():
        die(f"{a.id!r} is not an Expresso Emprego id — the digits ending the ad URL.")
    status, body = get(ad_url(a.id))
    if status == 404:
        die(f"no advertisement {a.id} (HTTP 404) — filled or pulled. Record it as "
            f"discarded.", 3)
    if status != 200:
        die(f"{HOST} answered HTTP {status} for {a.id}", 4)
    i = body.find('class="wucAnuncioDet"')
    if i < 0:
        die(f"{ad_url(a.id)}: 200, {len(body)} characters and no `wucAnuncioDet` "
            f"block — the markup moved, or this is the «Oops» page.", 6)
    i = body.find(">", i) + 1               # after the container's opening tag
    j = body.find("EMPREGOS SEMELHANTES", i)
    seg = body[i:j] if j > i else body[i:]
    title = re.search(r"<title>(.*?)</title>", body, re.S)
    print(json.dumps({"id": a.id, "ledger_id": f"expressoemprego:{a.id}",
                      "url": ad_url(a.id), "provider": "expressoemprego",
                      "country": "PT",
                      "title": clean(title.group(1)).split(" | ")[0] if title else None,
                      "text": to_text(seg), "language": "pt"},
                     ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="the live listing, or the site's own search route")
    s.add_argument("--q", help="a query, one path segment")
    s.add_argument("--localizacao", help="a location as the site spells it, e.g. lisboa")
    s.add_argument("--pages", type=int, default=1, help="pages of 15 to read (default 1)")
    s.add_argument("--limit", type=int, default=0)
    s.set_defaults(func=cmd_search)
    d = sub.add_parser("ad", help="one advertisement's text, from its id")
    d.add_argument("--id", required=True)
    d.set_defaults(func=cmd_ad)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
