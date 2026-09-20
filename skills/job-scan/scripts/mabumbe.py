#!/usr/bin/env python3
"""Mabumbe (`mabumbe.com`, Tanzania) — the WordPress REST collection of its `noo_job` posts, reached from the user's own tab because the declared client meets a Cloudflare challenge on every path; the JSON the tab hands over is normalised here. Issue #332.

  mabumbe.py jobs [--days N | --after YYYY-MM-DD] [--max-pages N]     the HTTP attempt (guard, then the REST route)
  mabumbe.py jobs --from page1.json [page2.json …] [--stated N]         the JSON saved from the tab
  mabumbe.py ad --url https://mabumbe.com/jobs/<slug>/  |  ad --from one.json

THE ROUTE, MEASURED 2026-09-20 14:16–14:22 UTC. `mabumbe.com/robots.txt`
(200, 1 956 B) names `ChatGPT-User`, `python`, `curl`, `wget` and thirty
SEO crawlers to refuse them, and for `*` closes `/wp-admin/`, `/wp-includes/`
and `/cgi-bin/` only — neither `Claude-User` nor `ClaudeBot` is named, so
the `*` group applies and `/wp-json/` and `/jobs/` are permitted. **The
transport refuses the declared client on every path** — `/jobs/`,
`/sitemap.xml`, `/wp-json/wp/v2/posts`, `/wp-json/wp/v2/noo_job`: HTTP 403
with a 5.6–5.8 KB «Just a moment...» interstitial whose md5 moves at
constant size, a Cloudflare challenge (never defeated, borne 2). **A
connected tab is served without the interstitial**, and from inside the
page `fetch()` of the same routes answers 200 — ten calls in a row on
2026-09-20, no second challenge. So `jobs` over HTTP dies with exit 9 and
the procedure below; the work is `jobs --from`.

THE COLLECTION. `GET /wp-json/wp/v2/noo_job?per_page=100&page=N&_embed=wp:term`
— `per_page` is capped at 100 (101 answers 400), `x-wp-total: 44523` and
`x-wp-totalpages: 446` on 2026-09-20, **the same 44 523 the archive page
`/jobs/` prints as «jobs found»**: every post ever filed as a job since the
site began, tenders and exam notices among them, never a count of live
advertisements. `after=2026-08-21T00:00:00` narrows it to the posts of the
last 30 days — **619**, 7 pages of 100 — and the last 7 days to **146**; the
adapter's `--days` (default 30) is that window, and the total it prints is
the window's `x-wp-total`, named as such. Each item: `id`, `date` (Dar es
Salaam time) and `date_gmt`, `modified`, `link`, `title.rendered`,
`content.rendered` (the whole advert, 2 000–16 000 characters of HTML),
`excerpt.rendered`, and with `_embed=wp:term` the resolved
`job_category` (NGO and Social Work 8 053, Administration 5 991, Government
5 123 …), `job_location` (60 terms; Dar es Salaam 26 956, Arusha 3 230,
Dodoma 2 807), `job_type` (Full time Jobs — the rest of that taxonomy is
SEO tags) and `job_tag` (Swahili SEO phrases, dropped). No JobPosting, no
employer field: **the employer is read from the title's own shape** — «IT
Support Officer job at Global Programs September 2026», «Executive Secretary
at NEEC September 2026» — the text between « at » and the trailing month and
year; null when the title has no « at ». The deadline is prose: «Deadline is
30th September 2026», «Application deadline: 30 September 2026»,
«Application Period 18/09/2026 – 01/10/2026» (the second date) — read when
one of those forms is there, null otherwise, never guessed.

THE PROCEDURE FROM THE TAB (the card says it too): open `https://mabumbe.com/jobs/`
in the user's Chrome, then in the page
  `await (await fetch('/wp-json/wp/v2/noo_job?per_page=100&page=1&_embed=wp:term&after=' + since)).text()`
one page at a time (`x-wp-totalpages` on the first answer says how many;
`x-wp-total` is `--stated`), save each answer to a file, and hand the files
to `jobs --from`. One request every 2 s from the tab as from here.

WITHHELD: the description is scrubbed of e-mail addresses and telephone
numbers (the adverts end with «Applications … should be sent via e-mail to
…» — the sentence stays, the address does not); the apply link the site
adds («CLICK HERE TO APPLY», an external form or the site's own link) is
never emitted; `job_tag` dropped; `contacts_withheld` on every record.
"""

import argparse
import datetime as dt
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
from _ua import UA, browser_fallback

BOARD, HOST, COUNTRY = "mabumbe", "mabumbe.com", "TZ"
BASE = f"https://{HOST}"
REST = BASE + "/wp-json/wp/v2/noo_job"
PER_PAGE = 100                     # the server's cap: 101 answers 400
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MONTHS = "january|february|march|april|may|june|july|august|september|october|november|december"
TITLE_AT_RE = re.compile(r"^(?P<title>.+?)\s+(?:job|jobs|vacancy|vacancies)?\s*at\s+(?P<company>.+?)(?:\s*[,–-]?\s*(?:" + MONTHS + r")\s*,?\s*\d{4})?\s*$", re.I)
TRAIL_RE = re.compile(r"\s*[,–-]?\s*(?:" + MONTHS + r")\s*,?\s*\d{4}\s*$", re.I)
DEADLINE_RES = (
    re.compile(r"(?:application\s+)?(?:deadline|closing\s+date)\s*(?:is|:|of|for\s+applications?\s*(?:is|:)?)?\s*(?:on\s+)?(?P<d>\d{1,2}(?:st|nd|rd|th)?\s+(?:" + MONTHS + r")[,\s]+\d{4}|\d{1,2}[/.]\d{1,2}[/.]\d{4})", re.I),
    re.compile(r"application\s+period\s*:?\s*\d{1,2}[/.]\d{1,2}[/.]\d{4}\s*(?:–|-|to|—)\s*(?P<d>\d{1,2}[/.]\d{1,2}[/.]\d{4})", re.I),
    re.compile(r"(?:apply|applications?\s+(?:should|must|to)\s+be\s+(?:sent|submitted|received))\s+(?:before|by|not\s+later\s+than|on\s+or\s+before)\s+(?P<d>\d{1,2}(?:st|nd|rd|th)?\s+(?:" + MONTHS + r")[,\s]+\d{4}|\d{1,2}[/.]\d{1,2}[/.]\d{4})", re.I),
)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
APPLY_RE = re.compile(r"<a\b[^>]*>\s*(?:click\s+here\s+to\s+apply|apply\s+(?:here|now|online))[^<]*</a>", re.I)
_PACE = Pace(HOST, own=2.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[mabumbe] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    """(status, body, headers) — this host only, the guard first, 2 s apart."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower() not in (HOST, "www." + HOST):
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "application/json, text/html"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, "", dict(e.headers or {})
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = APPLY_RE.sub(" ", t)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def clean_title(raw):
    return " ".join(htmlmod.unescape(re.sub(r"<[^>]+>", "", raw or "")).split()) or None


def company_of(title):
    """«Executive Secretary at NEEC September 2026» → («Executive Secretary», «NEEC»); no « at » → (title, None)."""
    if not title:
        return None, None
    m = TITLE_AT_RE.match(title)
    if not m or not m.group("company").strip():
        return TRAIL_RE.sub("", title).strip() or title, None
    return m.group("title").strip(), m.group("company").strip(" ,–-")


def deadline_of(plain):
    for rx in DEADLINE_RES:
        m = rx.search(plain or "")
        if m:
            return " ".join(m.group("d").split())
    return None


def iso(s):
    """`2026-09-19T05:34:51` (GMT) → `2026-09-19T05:34:51Z`; anything else as it came."""
    return (s + "Z") if s and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", s) else (s or None)


def terms(item, taxonomy):
    out = []
    for group in ((item.get("_embedded") or {}).get("wp:term") or []):
        for t in group or []:
            if isinstance(t, dict) and t.get("taxonomy") == taxonomy and t.get("name"):
                out.append(htmlmod.unescape(t["name"]))
    return out or None


def record(item, with_description=True):
    jid = item.get("id")
    if jid is None or not item.get("link"):
        return None
    raw_title = clean_title((item.get("title") or {}).get("rendered") if isinstance(item.get("title"), dict) else item.get("title"))
    title, company = company_of(raw_title)
    body = (item.get("content") or {}).get("rendered") if isinstance(item.get("content"), dict) else item.get("content")
    plain = text(body)
    embedded = "_embedded" in item
    r = {
        "source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{jid}", "id": str(jid), "url": item["link"],
        "title": title, "title_as_posted": raw_title, "company": company,
        "posted": iso(item.get("date_gmt")) or iso(item.get("date")), "modified": iso(item.get("modified_gmt")) or iso(item.get("modified")),
        "closes": deadline_of(plain),
        "locations": terms(item, "job_location") if embedded else None,
        "categories": terms(item, "job_category") if embedded else None,
        "job_type": terms(item, "job_type") if embedded else None,
        "term_ids": None if embedded else {k: item.get(k) for k in ("job_location", "job_category", "job_type") if item.get(k)},
        "description": (scrub(plain) or "")[:20000] or None if with_description else None,
        "contacts_withheld": True,
    }
    return r


def load_items(paths):
    """Every file is a JSON array as the REST route returns it, or one item; the order of the files is kept."""
    items = []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            die(f"{p}: not the route's JSON ({e})")
        if isinstance(data, dict) and "id" in data:
            data = [data]
        if not isinstance(data, list):
            die(f"{p}: not a list of noo_job items (a `code`/`message` object is the route's own error)")
        items.extend(x for x in data if isinstance(x, dict))
    return items


def emit(items, stated, window):
    seen, n = set(), 0
    for it in items:
        r = record(it)
        if r is None or r["id"] in seen:
            continue
        seen.add(r["id"])
        print(json.dumps(r, ensure_ascii=False))
        n += 1
    tail = f" (the archive's whole `noo_job` collection is 44 523 on 2026-09-20; {window} is the window read)"
    if stated is None:
        note(f"{th(n)} emitted — no x-wp-total handed over (`--stated`), so nothing to compare{tail}.")
    elif n == stated:
        note(f"{th(n)} emitted, the route states {th(stated)} for the window: equal{tail}.")
    else:
        note(f"{th(n)} emitted, the route states {th(stated)} for the window: {th(abs(stated - n))} " + ("short — hand over the missing pages" if stated > n else "more than stated") + tail + ".")


def since_of(a):
    if a.after:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.after):
            die(f"--after {a.after!r}: YYYY-MM-DD")
        return a.after + "T00:00:00"
    d = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.days)
    return d.strftime("%Y-%m-%dT00:00:00")


def cmd_jobs(a):
    since = since_of(a)
    window = f"since {since[:10]}"
    if a.from_files:
        emit(load_items(a.from_files), a.stated, window)
        return
    url = f"{REST}?per_page={PER_PAGE}&page=1&_embed=wp:term&after={since}"
    st, body, hdr = request(url)
    if st in (403, 429, 503):
        msg, code = browser_fallback(HOST, True, st, url)
        die(msg + f"\n  From the tab: open {BASE}/jobs/, then `fetch('/wp-json/wp/v2/noo_job?per_page=100&page=N&_embed=wp:term&after={since}')` one page at a time, save each answer, and run `mabumbe.py jobs --from <files> --stated <x-wp-total>`.", code)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    try:
        items = json.loads(body)
    except ValueError:
        die(f"{url}: not JSON — a 200 that is not the route", EXIT_PARTIAL)
    h = {k.lower(): v for k, v in hdr.items()}
    stated = int(h["x-wp-total"]) if str(h.get("x-wp-total", "")).isdigit() else None
    pages = int(h["x-wp-totalpages"]) if str(h.get("x-wp-totalpages", "")).isdigit() else 1
    for page in range(2, min(pages, a.max_pages) + 1):
        st, body, _ = request(f"{REST}?per_page={PER_PAGE}&page={page}&_embed=wp:term&after={since}")
        if st != 200:
            note(f"page {page}: HTTP {st} — stopped; the pages before are emitted.")
            break
        try:
            items.extend(json.loads(body))
        except ValueError:
            note(f"page {page}: not JSON — stopped.")
            break
    if pages > a.max_pages:
        note(f"{pages} pages for the window, {a.max_pages} read (--max-pages).")
    emit(items, stated, window)


def cmd_ad(a):
    if a.from_file:
        items = load_items([a.from_file])
        if not items:
            die(f"{a.from_file}: no item", EXIT_PARTIAL)
        print(json.dumps(record(items[0]), ensure_ascii=False))
        return
    parts = urllib.parse.urlsplit((a.url or "").strip())
    if parts.netloc.lower() not in (HOST, "www." + HOST) or not re.fullmatch(r"/jobs/[a-z0-9-]+/?", parts.path):
        die(f"{a.url!r}: not a Mabumbe advert address (https://{HOST}/jobs/<slug>/)")
    slug = parts.path.strip("/").split("/")[-1]
    url = f"{REST}?slug={urllib.parse.quote(slug)}&_embed=wp:term"
    st, body, _ = request(url)
    if st in (403, 429, 503):
        msg, code = browser_fallback(HOST, True, st, url)
        die(msg + f"\n  From the tab: `fetch('/wp-json/wp/v2/noo_job?slug={slug}&_embed=wp:term')`, save the answer, `mabumbe.py ad --from <file>`.", code)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    try:
        items = json.loads(body)
    except ValueError:
        die(f"{url}: not JSON", EXIT_PARTIAL)
    if not items:
        die(f"{url}: no post with that slug — gone, or never a job", EXIT_GONE)
    print(json.dumps(record(items[0]), ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Mabumbe (Tanzania) — the WordPress REST collection of its job posts, from the user's tab (the declared client is challenged); the archive's count named as an archive; no contact. Issue #332.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the posts of the last --days (default 30), 100 a page; or --from the JSON saved from the tab")
    s.add_argument("--days", type=int, default=30, help="the window: posts dated within the last N days (the whole collection is an archive)")
    s.add_argument("--after", help="YYYY-MM-DD instead of --days")
    s.add_argument("--max-pages", type=int, default=20, help="pages of 100 read over HTTP at most")
    s.add_argument("--from", dest="from_files", nargs="+", metavar="FILE", help="the route's JSON answers saved from the tab, one file per page")
    s.add_argument("--stated", type=int, help="the x-wp-total the tab read on the first page, to compare with the emitted number")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its address (the REST route by slug), or --from the JSON saved from the tab")
    d.add_argument("--url")
    d.add_argument("--from", dest="from_file", metavar="FILE")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    if a.cmd == "ad" and not (a.url or a.from_file):
        p.error("ad needs --url or --from")
    a.fn(a)


if __name__ == "__main__":
    main()
