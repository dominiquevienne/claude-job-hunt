#!/usr/bin/env python3
"""EmpleosEnUruguay (`www.empleosenuruguay.com`) — a Blogger blog whose every post is a rewritten job offer: the Blogger feed `/feeds/posts/default?alt=json` on the blog's own host states its total («openSearch:totalResults» 3 777 on 2026-09-16), pages by `start-index` fifty at a time, and carries each post's title, dates, labels and body; the count printed beside every walk; the body scrubbed. Issue #437.

  empleosenuruguay.py list [--pages N]    the feed's posts, newest first, fifty a page — 2 pages unless told (the feed is an archive back to 2023), the stated total beside them
  empleosenuruguay.py ad --url <https://www.empleosenuruguay.com/<yyyy>/<mm>/<slug>.html>

THE RULES. `User-agent: *` — `Disallow: /search` (the blog's own search and label pages); the feed
`/feeds/posts/default` is not `/search`, the post pages are not; `Sitemap:` declared. `/search` is
refused before the gate. No Crawl-delay; 2 s is ours.

THE FEED. `/feeds/posts/default?alt=json&max-results=50` (200, ~617 KB) is Blogger's JSON — the
feed's `openSearch$totalResults` (3 777), fifty entries, a `next` link (on `www.blogger.com`, which
the adapter does not follow: it asks the blog's own host for `start-index=51 …`). An entry: `id`
(`…post-<n>`), `published`, `updated`, `category` (the labels — a city, an area, a schedule, a
level: «Montevideo», «Jornada completa», «Cajero/a», «Bachillerato Completo»), `title`, `content`
(HTML, with AdSense stubs), an `alternate` link to `/<yyyy>/<mm>/<slug>.html`. The last page on the
day: `start-index=3751`, 27 entries — 3 750 + 27 = 3 777, equal. The oldest post is 2023-01-01:
**the feed is an archive, not a live list** — `list` walks two pages (100 posts) unless `--pages`
says more, and prints the stated total beside the emitted with the walk named as a bound. THE
POST. `ad --url` asks the feed for the one post by `path=` (`/feeds/posts/default?alt=json&path=
/<yyyy>/<mm>/<slug>.html`) — one request, the same entry shape, no page markup. **What the entry
carries is what the blog rewrote: no structured employer (some posts embed a JobPosting JSON-LD naming «Empresa empleadora» — its validThrough, employmentType, locality, region and industry are read, its text is kept out of the prose); «N Vacantes» and «$ 60.610» / «Sueldo
$41.969» when the title says them, read from the title; the body flattened, the AdSense stubs
dropped, e-mail addresses and Uruguayan telephone numbers withheld; `contacts_withheld` on every
record; the blog's «Postularse» link is the employer's own form or portal, never followed.**

Measured 2026-09-16 12:05 UTC by the declared client, the guard on the exact path: robots 200
(86 B); the feed 617 056 B, 3 777 stated, 50 entries; `start-index=3751` 27 entries; `path=` one
entry, 43 030 B; no e-mail and no phone in the fifty bodies read.
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
from _ldjson import one, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "www.empleosenuruguay.com"
FEED = f"https://{HOST}/feeds/posts/default"
PER_PAGE = 50
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+?598[\s\-]?)?(?:0?9\d[\s\-]?\d{3}[\s\-]?\d{3}|[24][\s\-]?\d{3}[\s\-]?\d{4})(?!\d)")   # Uruguayan mobiles 09x xxx xxx, Montevideo 2xxx xxxx, interior 4xxx xxxx, with or without +598
POST_RE = re.compile(r"^/(\d{4})/(\d{2})/([a-z0-9\-]+)\.html$")
REFUSED_RE = re.compile(r"^/search(?:/|\?|$)")
ADS_RE = re.compile(r"\(adsbygoogle\s*=\s*window\.adsbygoogle\s*\|\|\s*\[\]\)\.push\(\{\}\);?")
OPENINGS_RE = re.compile(r"(\d+)\s+Vacantes?", re.I)
SALARY_RE = re.compile(r"\$\s?(\d{1,3}(?:\.\d{3})+|\d{4,6})")

_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[empleosenuruguay] {msg}", file=sys.stderr)


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
        die(f"{url}: `/search` is refused in writing to `*` — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "application/json,text/html;q=0.9", "Accept-Language": "es"})
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
    t = re.sub(r"<script\b.*?</script>", " ", markup or "", flags=re.S | re.I)   # some posts embed a JobPosting JSON-LD in their body — read apart, never as prose
    t = ADS_RE.sub(" ", t)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def feed(url):
    code, body = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    try:
        f = json.loads(body)["feed"]
    except (ValueError, KeyError, TypeError):
        die(f"{url}: 200 and not Blogger's JSON feed — the shape changed", EXIT_PARTIAL)
    return f


def stated(f):
    """The feed's own total — `openSearch$totalResults` — or `None`."""
    try:
        return int(f["openSearch$totalResults"]["$t"])
    except (KeyError, ValueError, TypeError):
        return None


def val(x):
    return (x or {}).get("$t") if isinstance(x, dict) else None


def record(e):
    pid = (val(e.get("id")) or "").rsplit("post-", 1)[-1] or None
    url = next((l.get("href") for l in e.get("link", []) if l.get("rel") == "alternate"), None)
    title = htmlmod.unescape(val(e.get("title")) or "").strip() or None
    labels = [c.get("term") for c in e.get("category", []) if c.get("term")]
    haystack = " | ".join([title or ""] + labels)   # «7 Vacantes» and «$60.610» travel in the title or in a label
    om = OPENINGS_RE.search(haystack)
    sm = SALARY_RE.search(haystack)
    content = val(e.get("content")) or ""
    jp = (postings(content) or [None])[-1] or {}
    addr = one(one(jp.get("jobLocation")).get("address"))
    return {
        "source": "empleosenuruguay", "country": "UY", "ledger_id": f"empleosenuruguay:{pid}", "id": pid, "url": url,
        "title": title, "labels": labels or None,
        "openings": int(om.group(1)) if om else None, "salary_uyu": int(sm.group(1).replace(".", "")) if sm else None,
        "published": (val(e.get("published")) or "")[:10] or None, "updated": (val(e.get("updated")) or "")[:10] or None,
        "valid_through": (jp.get("validThrough") or "")[:10] or None, "employment_type": jp.get("employmentType") or None,
        "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None, "industry": jp.get("industry") or None,
        "jobposting": bool(jp),
        "text": scrub(text(content)),
        "contacts_withheld": True, "language": "es",
    }


def cmd_list(a):
    pages = a.pages if a.pages else 2
    out, seen, total, walked = [], set(), None, 0
    start = 1
    while walked < pages:
        f = feed(f"{FEED}?alt=json&start-index={start}&max-results={PER_PAGE}")
        if total is None:
            total = stated(f)
            if total is None:
                die(f"{FEED}: 200 and no openSearch:totalResults in the feed — the shape changed; not an empty blog", EXIT_PARTIAL)
        entries = f.get("entry") or []
        if not entries:
            if walked == 0:
                die(f"{FEED}: a feed that states {th(total)} and lists no entry", EXIT_PARTIAL)
            break
        new = 0
        for e in entries:
            r = record(e)
            if not r["id"] or r["id"] in seen:
                continue
            seen.add(r["id"])
            out.append(r)
            new += 1
        walked += 1
        if new == 0 or len(entries) < PER_PAGE or len(out) >= total:
            break
        start += PER_PAGE
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    if n < total and (a.pages is None or walked >= pages):
        note(f"{th(n)} emitted from {walked} page(s) of {PER_PAGE}, the feed states {th(total)} — walked by request ({pages} page(s); the feed is an archive back to 2023), not a shortfall.")
    else:
        verdict = "equal" if n == total else (f"{th(total - n)} short" if n < total else f"{th(n - total)} more emitted")
        note(f"{th(n)} emitted from {walked} page(s), the feed states {th(total)} — {verdict}.")
    note("bodies scrubbed; the employers' own application links never followed.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = POST_RE.match(parts.path)
    if parts.netloc not in (HOST, "empleosenuruguay.com") or not m:
        die(f"{a.url}: not a post address (https://{HOST}/<yyyy>/<mm>/<slug>.html)")
    f = feed(f"{FEED}?alt=json&path={urllib.parse.quote(parts.path)}")
    entries = f.get("entry") or []
    if not entries:
        die(f"{a.url}: the feed knows no post at this path — gone", EXIT_GONE)
    r = record(entries[0])
    print(json.dumps(r, ensure_ascii=False))
    note(f"{a.url}: read from the feed's own entry; body scrubbed; the application link never followed.")


def main():
    p = argparse.ArgumentParser(description="EmpleosEnUruguay — the Blogger feed's posts with its stated total beside them; bodies scrubbed. Issue #437.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the feed, fifty a page, newest first — 2 pages unless --pages")
    l_.add_argument("--pages", type=int, help="pages of 50 to walk (the feed is an archive back to 2023)")
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
