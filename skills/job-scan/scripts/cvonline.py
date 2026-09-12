#!/usr/bin/env python3
"""CV-Online (`www.cv.ee`, and the same stack on `www.cv.lv`, `www.cvonline.lt`) — read through the search service the page itself calls, with the job sitemap as the second document.

  cvonline.py search [--host www.cv.ee] [--own] [--limit N] [--no-site-total]
  cvonline.py ad --url <advertisement URL>

TWO NUMBERS, ONE STORE, AND THE FLAG THAT SEPARATES THEM

`/api/v1/vacancy-search-service/search?limit=100&offset=N` is the endpoint
behind `/et/search` (read in the page's own bundle: `_app-*.js` adds
`showHidden: true` to every search). **Without the flag the service counts
1 426; with it, 3 853 — the figure the visitor sees («Kuva 3853
tööpakkumist»).** The 2 427 «hidden» ones are, 91 of 91 sampled, published
by «Töötukassa vahendatud pakkumised» — advertisements mediated by
Töötukassa, Estonia's public employment service — every one with an external
id, none with a promotion, **and none in `jobs-sitemap.xml`, which lists
exactly the 1 426 own ones.** Measured 2026-09-12 12:03–12:07 UTC (#233,
lot 5 → this adapter). So: `search` emits what the visitor sees (3 853, with
`mediated_by` set on the Töötukassa rows), `--own` restricts to the 1 426,
and the adapter prints both checks each run — «own N, sitemap lists M —
equal / k short» and «total T = own N + hidden H».

THE ROW is the service's own object: id, title, employer, publish and
expiration dates, salary from/to (a range on 1 of 5 own rows; the mediated
ones carry one figure), town / county / country as ids **resolved through
the `locations` table the search page inlines** (countries with ISO codes —
`countryId 1` is EE, and 18 of 3 853 are elsewhere: 157 ×7, 144 ×6…), remote
flags, work times, categories, and a text snippet. `ad` reads the vacancy
page's Next.js state (`position`, `details.standardDetails`, `employer`,
`settings.dateStart/dateTo`, `applyingUrl`) — **and never the `contacts`
block, which carries a recruiter's e-mail and phone.**

THE OTHER TWO HOSTS — `www.cv.lv` (LV) and `www.cvonline.lt` (LT) — publish
the same rules and the same stack, **and both answer the 25-byte static 403
to this client on the root and on the service** (2026-09-12 12:07 UTC, #233
lot 6). The adapter accepts them and says so on a 403; `countries:` declares
EE alone until a transport answers. `cvonline.lt` also carries
`Content-Signal: ai-train=no, use=reference` — the use here is reference.

THE RULES: Cloudflare's managed block (`ClaudeBot` named and refused, `*`
open — `identity()` answers `claude-user`, `verdict()` sweeps since #230)
plus the operator's lines; no `Crawl-delay` (2 s is ours); `certain: True`.
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
from _sitemap import locs as sitemap_locs
from _ua import UA
from _zero import empty_first_page

HOSTS = {"www.cv.ee": ("EE", "et"), "www.cv.lv": ("LV", "lv"), "www.cvonline.lt": ("LT", "lt")}
SEARCH = "/api/v1/vacancy-search-service/search"
MEDIATED = "Töötukassa vahendatud pakkumised"     # Estonia's public employment service, syndicated
AD_RE = re.compile(r"^https://(www\.cv\.ee|www\.cv\.lv|www\.cvonline\.lt)/(?:[a-z]{2}/)?vacancy/(\d+)(?:/|$)")
PAGE = 100

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[cvonline] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACES = {}


def get(url):
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "application/json,text/html;q=0.9,*/*;q=0.5",
        "Accept-Language": HOSTS.get(host, ("", "en"))[1]})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def refused(host, code, url):
    if code == 403:
        die(f"{url}: HTTP 403 — the transport refuses this client on {host} today "
            f"(www.cv.lv and www.cvonline.lt did on 2026-09-12: the static 25-byte provider default, #222); "
            f"nothing here says the board is empty.", EXIT_PARTIAL)
    die(f"{url}: HTTP {code}", EXIT_PARTIAL)


def next_data(html):
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except ValueError:
        return None


def locations(host, lang):
    """The countries / counties / towns tables the search page inlines —
    one request, and the names for every id the service returns."""
    code, body = get(f"https://{host}/{lang}/search")
    d = next_data(body) if code == 200 else None
    loc = ((d or {}).get("props", {}).get("pageProps", {}).get("initialReduxState", {}) or {}).get("locations") or {}
    countries = {int(k): v for k, v in (loc.get("countries") or {}).items()} if isinstance(loc.get("countries"), dict) else {}
    counties = {int(k): v for k, v in (loc.get("counties") or {}).items()} if isinstance(loc.get("counties"), dict) else {}
    towns = {t["id"]: t for t in (loc.get("towns") or []) if isinstance(t, dict) and "id" in t}
    if not countries:
        note(f"{host}/{lang}/search carries no locations table this run (HTTP {code}) — ids emitted, not names.")
    return countries, counties, towns


def search(host, offset, limit, hidden):
    q = {"limit": limit, "offset": offset}
    if hidden:
        q["showHidden"] = "true"
    url = f"https://{host}{SEARCH}?" + urllib.parse.urlencode(q)
    code, body = get(url)
    if code != 200:
        refused(host, code, url)
    try:
        d = json.loads(body)
    except ValueError:
        die(f"{url}: HTTP 200 and not JSON — {body[:120]!r}", EXIT_PARTIAL)
    if not isinstance(d, dict) or "total" not in d:
        die(f"{url}: no `total` in the answer — the service changed shape; nothing here says the board is empty.", EXIT_PARTIAL)
    return d


def row(host, cc, v, countries, counties, towns):
    c = countries.get(v.get("countryId")) or {}
    t = towns.get(v.get("townId")) or {}
    k = counties.get(v.get("countyId")) or {}
    emp = v.get("employerName") or ""
    return {
        "source": "cvonline", "board": host,
        # the ISO from the site's own countries table; the board's country only when the table says nothing
        "country": c.get("iso") or (cc if v.get("countryId") in (None, 1) else v.get("countryId")),
        "ledger_id": f"cvonline:{host}:{v['id']}", "id": str(v["id"]),
        "url": f"https://{host}/{HOSTS[host][1]}/vacancy/{v['id']}/",
        "title": text(v.get("positionTitle")),
        "employer": emp or None,
        # Töötukassa's syndicated advertisements: the employer is inside the text, the row says who mediated
        "mediated_by": "Töötukassa" if emp == MEDIATED else None,
        "posted": v.get("publishDate"), "expires": v.get("expirationDate"), "renewed": v.get("renewedDate"),
        "salary_min": v.get("salaryFrom"), "salary_max": v.get("salaryTo"), "salary_hourly": bool(v.get("hourlySalary")),
        "salary_currency": "EUR",
        "city": t.get("name"), "county": k.get("name"),
        "remote": bool(v.get("remoteWork")), "remote_type": v.get("remoteWorkType"),
        "work_times": v.get("workTimes") or [], "categories": v.get("categories") or [],
        "quick_apply": bool(v.get("quickApply")),
        "snippet": text(v.get("positionContent"))[:600],
    }


def cmd_search(a):
    host = a.host
    if host not in HOSTS:
        die(f"{host}: not a CV-Online host — one of {', '.join(HOSTS)}")
    cc, lang = HOSTS[host]
    countries, counties, towns = locations(host, lang)
    rows, seen, offset, total = [], set(), 0, None
    while True:
        d = search(host, offset, PAGE, hidden=not a.own)
        total = d["total"]
        items = d.get("vacancies") or []
        if offset == 0 and not items:
            if total:
                die(f"{host}: the service states {total} and served no row on the first page — a shape change, not an empty board.", EXIT_PARTIAL)
            die(empty_first_page("cvonline", json.dumps(d)[:2000], "vacancy", where=f"https://{host}{SEARCH}"), EXIT_PARTIAL)
        for v in items:
            if v.get("id") in seen:
                continue
            seen.add(v.get("id"))
            rows.append(row(host, cc, v, countries, counties, towns))
        offset += len(items)
        if not items or offset >= total or (a.limit and len(rows) >= a.limit):
            break
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    mediated = sum(1 for r in rows if r["mediated_by"])
    scope = "own" if a.own else "visible (showHidden)"
    note(f"{host}: **{th(len(rows))} distinct id(s)** of the {th(total)} the service states for the {scope} search"
         + (f" ({a.limit} printed under --limit, the walk stopped there)" if a.limit else "")
         + f"; {th(mediated)} mediated by Töötukassa" + ("; ids, not names, for places" if not countries else "") + ".")
    if a.no_site_total or a.limit:
        return
    # the two checks: own against the sitemap, and total = own + hidden
    own_total = search(host, 0, 1, hidden=False)["total"]
    all_total = search(host, 0, 1, hidden=True)["total"]
    code, xml = get(f"https://{host}/jobs-sitemap.xml")
    listed = len({u for u in sitemap_locs(xml) if "/vacancy/" in u}) if code == 200 else None
    if listed is None:
        note(f"{host}/jobs-sitemap.xml: HTTP {code} — no second document this run.")
    elif listed == own_total:
        note(f"own {th(own_total)}, sitemap lists {th(listed)} — equal.")
    else:
        note(f"own {th(own_total)}, sitemap lists {th(listed)} — {th(abs(listed - own_total))} "
             + ("short" if listed > own_total else "more in the service than the sitemap lists") + ".")
    note(f"total {th(all_total)} = own {th(own_total)} + hidden {th(all_total - own_total)}"
         + (f"; this run emitted {th(len(rows))} of the {th(all_total if not a.own else own_total)} — "
            + ("equal." if len(rows) == (all_total if not a.own else own_total) else f"{th(abs((all_total if not a.own else own_total) - len(rows)))} short.")))


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected https://<host>/<lang>/vacancy/<id>/…")
    host, ident = m.group(1), m.group(2)
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        refused(host, code, a.url)
    d = next_data(body)
    v = (((d or {}).get("props", {}).get("pageProps", {}).get("vacancy") or {}).get(ident)) if d else None
    if not isinstance(v, dict) or "position" not in v:
        die(f"{a.url}: the page carries no vacancy {ident} in its state — the shape changed, or the advertisement is gone.", EXIT_PARTIAL)
    st = v.get("settings") or {}
    det = v.get("details") or {}
    hi = v.get("highlights") or {}
    parts = [f"{text(x.get('title'))}: {text(x.get('content'))}" for x in (det.get("standardDetails") or []) if isinstance(x, dict)]
    # the body lives in one of four places, and the row says which: text on the page,
    # a file (an image or PDF behind files-service), a URL on the employer's site, or styled HTML
    fd, ud, sd = det.get("fileDetails") or {}, det.get("urlDetails"), det.get("styleDetails")
    if parts:
        kind, body_url = "text", None
    elif fd.get("fileId"):
        kind, body_url = "file", f"https://{host}/api/v1/files-service/{fd['fileId']}"
    elif ud:
        kind, body_url = "url", ud if isinstance(ud, str) else None
    elif sd:
        kind, body_url = "styled", None
        parts = [text(sd if isinstance(sd, str) else json.dumps(sd, ensure_ascii=False))]
    else:
        kind, body_url = "none", None
    loc = (d.get("props", {}).get("pageProps", {}).get("locations") or {})
    towns = {t["id"]: t for t in (loc.get("towns") or []) if isinstance(t, dict) and "id" in t}
    countries = {int(k): x for k, x in (loc.get("countries") or {}).items()} if isinstance(loc.get("countries"), dict) else {}
    where = hi.get("location") or {}
    emp = v.get("employerName") or ""
    print(json.dumps({
        "source": "cvonline", "board": host,
        "country": (countries.get(where.get("countryId")) or {}).get("iso") or HOSTS[host][0],
        "ledger_id": f"cvonline:{host}:{ident}", "id": ident, "url": a.url,
        "title": text(v.get("position")),
        "employer": emp or None,
        "mediated_by": "Töötukassa" if emp == MEDIATED else None,
        "employer_about": text((v.get("employer") or {}).get("about")) or None,
        "employer_site": (v.get("employer") or {}).get("webpageUrl"),
        "posted": v.get("firstPublishDate"), "modified": v.get("dateModified"),
        "valid_from": st.get("dateStart"), "valid_through": st.get("dateTo"),
        "categories": st.get("categories") or [], "apply_url": st.get("applyingUrl"),
        "city": (towns.get(where.get("townId")) or {}).get("name"),
        "salary_min": hi.get("salaryFrom"), "salary_max": hi.get("salaryTo"), "salary_per": hi.get("ratePer"), "salary_currency": "EUR",
        "remote_type": hi.get("remoteWorkType"),
        "language": v.get("languageIso"), "status": v.get("status"),
        "details_kind": kind, "details_url": body_url,
        "description": "\n".join(parts)[:20000],
        # `contacts` — a recruiter's e-mail and phone — is on the page and is not emitted
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="CV-Online — cv.ee (and the same stack on cv.lv, cvonline.lt) through the search service its page calls; the job sitemap and the hidden/own split as the checks.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="every visible advertisement (showHidden, what the visitor sees) — ~40 requests of 100 on cv.ee; --own for the 1 426 own ones")
    s.add_argument("--host", default="www.cv.ee", help="www.cv.ee (default), www.cv.lv, www.cvonline.lt")
    s.add_argument("--own", action="store_true", help="the service's default search: own advertisements, the ones the sitemap lists")
    s.add_argument("--limit", type=int)
    s.add_argument("--no-site-total", action="store_true")
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one advertisement, from the vacancy page's state — contacts never emitted")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
