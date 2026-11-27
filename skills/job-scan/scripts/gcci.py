#!/usr/bin/env python3
"""Georgetown Chamber of Commerce & Industry (`gcci.gy`, Guyana) — the
«Career Opportunities» category: members' vacancy notices published as
WordPress posts (#709).

**THE LIST IS THE REST COLLECTION OF ONE CATEGORY.** The category is resolved
by its slug (`/wp-json/wp/v2/categories?slug=career-opportunities`, id 22 on
2026-11-27), never by a number written here, and its posts are read from
`/wp-json/wp/v2/posts?categories=<id>`. Measured 2026-11-27 23:2x UTC:

    categories?slug=…       count 42           the category's own statement
    posts?categories=22     42 records         `X-WP-Total` 42, one page of 100
    /category/…/page/1…5/   42 distinct posts  10·10·10·10·2, page 6 is 404

*The three were compared MEMBER BY MEMBER, not by size — the intersection of
the HTML pager and the REST collection is 42 on both sides.* So the count this
tool prints beside its own is the CATEGORY's `count`, read on its own request:
a witness that is not our extraction.

**IT IS AN ARCHIVE, AND IT SAYS NOTHING ABOUT WHAT IS STILL OPEN.** The newest
post is dated 2026-09-14, the oldest 2019-10-11, and the posts carry no expiry.
Every post is emitted with its own `posted` date and nothing is dropped by age;
the end line counts how many are older than a year. *An age filter written
here would be a guess about when a Chamber notice closes.*

**NOT EVERY POST IS A VACANCY, AND NONE IS DROPPED.** On 2026-11-27 the
newest post of the category was a vendor-engagement announcement and the
oldest a request for consultancy expressions of interest. The category is the
host's own declaration; the reader decides.

**THE NOTICE IS OFTEN AN IMAGE.** 19 of the 42 bodies carry no text, 17 of
them only a flyer. `ad` then says so (`notice_is_an_image: true`) and gives
the image URLs: OUR tool reads no image, and an empty description is not an
empty vacancy.

**CONTACTS.** The list fields carry none. The body does — an e-mail address on
12 of the 42, a telephone number on one (2026-11-27, every body read once) — and they are taken out and NAMED in
`withheld_fields`, from what was actually taken.

**ONLY THREE REST PATHS ARE EVER ASKED**, refused before sending otherwise:
the category lookup, the category's posts, one post by id.

Rules: `User-agent: *` / `Disallow: /wp-admin/` (and one plugin file) /
`Allow: /wp-admin/admin-ajax.php`; no `Crawl-delay`, so the cadence is ours
(one second).
"""
import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import datetime
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path
from _robots import verdict as robots_verdict
from _ua import UA
from _withheld import withheld_a_contact

HOST = "gcci.gy"
API = f"https://{HOST}/wp-json/wp/v2"
SLUG = "career-opportunities"
TAG = "gcci"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

PATHS = (re.compile(r"^/wp-json/wp/v2/categories$"),
         re.compile(r"^/wp-json/wp/v2/posts$"),
         re.compile(r"^/wp-json/wp/v2/posts/\d+$"))
TAG_RE = re.compile(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>")
IMG_RE = re.compile(r'<img\b[^>]*?\bdata-orig-file="([^"]+)"|<img\b[^>]*?\bsrc="([^"]+)"')
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
TEL_RE = re.compile(r"(?<![\w\d])(?:\+?592[\s-]?)?\(?\d{3}\)?[\s-]\d{4}(?!\d)")

_PACE = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[{TAG}] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts), agents=("claude-user",))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    if parts.netloc != HOST or not any(p.match(parts.path) for p in PATHS):
        die(f"{url}: not one of the three REST paths this tool asks — refused "
            f"before sending.", EXIT_REFUSED)


def get(url):
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    _PACE.setdefault(host, Pace(host, own=1.0)).wait()
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], r.headers
    except urllib.error.HTTPError as e:
        return e.code, decode_body(e.read(), e.headers)[0], e.headers
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def read_json(url, body):
    try:
        return json.loads(body)
    except ValueError as e:
        die(f"{url}: our parser did not read JSON there ({e})")


def text(raw):
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", raw or ""))).strip()


def scrub(s):
    """Take contacts out, and say which kinds were ACTUALLY taken."""
    taken, out = [], s or ""
    if MAIL_RE.search(out):
        taken.append("email")
        out = MAIL_RE.sub("[e-mail withheld]", out)
    if TEL_RE.search(out):
        taken.append("telephone")
        out = TEL_RE.sub("[telephone withheld]", out)
    return out, taken


def posted(post):
    d = post.get("date_gmt")
    return d + "Z" if d else None


def record(post):
    """One REST post -> one record. A post without id or link is not a
    record (returns None), and the caller COUNTS those."""
    pid, link = post.get("id"), post.get("link")
    if not pid or not link:
        return None
    return {
        "id": str(pid),
        "ledger_id": f"{TAG}:{pid}",
        "url": link,
        "title": text((post.get("title") or {}).get("rendered")) or None,
        "company": None,
        "country": "GY",
        "posted": posted(post),
        "expires_stated": None,
        "salary_stated": False,
    }


def category():
    """(id, count) of the category, both read from the host."""
    url = f"{API}/categories?slug={SLUG}&_fields=id,count,slug"
    status, body, _ = get(url)
    if status != 200:
        die(f"{url}: HTTP {status}", EXIT_GONE if status in (404, 410) else EXIT_BROKEN)
    rows = read_json(url, body)
    rows = [r for r in rows if isinstance(r, dict) and r.get("slug") == SLUG]
    if not rows or not rows[0].get("id"):
        die(f"{url}: no category with the slug `{SLUG}` — OUR lookup found "
            f"nothing; this says nothing about whether the Chamber publishes "
            f"vacancies.", EXIT_GONE)
    c = rows[0].get("count")
    return rows[0]["id"], (c if isinstance(c, int) else None)


def older_than(rows, days, today):
    cut = (today - datetime.timedelta(days=days)).isoformat()
    return sum(1 for r in rows if r["posted"] and r["posted"][:10] < cut)


def cmd_jobs(a):
    v = robots_verdict(HOST)
    if not v["sweep"]:
        die(f"{HOST}: {v['reason']}",
            EXIT_UNKNOWN if v["sweep"] is None else EXIT_REFUSED)
    cid, stated = category()
    rows, bad, seen, page, pages = [], 0, set(), 1, 1
    while page <= pages and page <= a.max_pages:
        url = (f"{API}/posts?categories={cid}&per_page=100&page={page}"
               f"&_fields=id,link,date_gmt,title")
        status, body, hd = get(url)
        if status != 200:
            die(f"{url}: HTTP {status}", EXIT_BROKEN)
        try:
            pages = int(hd.get("X-WP-TotalPages") or 1)
        except (TypeError, ValueError):
            pages = 1
        for post in read_json(url, body):
            r = record(post) if isinstance(post, dict) else None
            if r is None:
                bad += 1
                continue
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
        page += 1
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    today = datetime.datetime.now(datetime.timezone.utc).date()
    newest = max((r["posted"] for r in rows if r["posted"]), default=None)
    old = older_than(rows, 365, today)
    note(f"{len(rows)} post(s) emitted from the category `{SLUG}` (id {cid})"
         + (f"; {bad} post(s) without id or link and NOT emitted" if bad else "")
         + (f"; newest posted {newest[:10]}, {old} older than a year — an "
            f"archive, nothing dropped by age" if newest else "")
         + ". " + (f"The category states {stated} post(s) (`count`), a count "
                   f"our extraction did not make"
                   if stated is not None else
                   "The host stated NO count this run, so completeness is not "
                   "established"))
    if page <= pages:
        note(f"stopped at --max-pages {a.max_pages} of {pages} — partial.")
        sys.exit(EXIT_PARTIAL)
    if stated is not None and len(rows) < stated:
        note(f"{stated - len(rows)} short of the stated count — partial, and the "
             f"exit code says so.")
        sys.exit(EXIT_PARTIAL)


def ad_record(post):
    raw = (post.get("content") or {}).get("rendered") or ""
    desc, taken = scrub(text(raw))
    imgs = []
    for m in IMG_RE.finditer(raw):
        u = html.unescape(m.group(1) or m.group(2))
        if u not in imgs:
            imgs.append(u)
    r = {"id": str(post.get("id")), "ledger_id": f"{TAG}:{post.get('id')}",
         "url": post.get("link"),
         "title": text((post.get("title") or {}).get("rendered")) or None,
         "posted": posted(post),
         "description": desc, "description_chars": len(desc),
         "notice_is_an_image": bool(imgs) and not desc,
         "image_urls": imgs or None,
         "withheld_fields": taken or None}
    if withheld_a_contact(taken):
        r["contacts_withheld"] = True
    return r


def cmd_ad(a):
    pid = a.id.strip().rstrip("/").split("/")[-1]
    if not pid.isdigit():
        die(f"{a.id}: a post is named by its numeric id (the REST `id`).")
    url = f"{API}/posts/{pid}?_fields=id,link,date_gmt,title,content"
    status, body, _ = get(url)
    if status != 200:
        die(f"{url}: HTTP {status}", EXIT_GONE if status in (404, 410) else EXIT_BROKEN)
    print(json.dumps(ad_record(read_json(url, body)), ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="every post of the category, newest first")
    s.add_argument("--limit", type=int)
    s.add_argument("--max-pages", type=int, default=10)
    s.set_defaults(func=cmd_jobs)
    s = sub.add_parser("ad", help="one post's body, contacts taken out")
    s.add_argument("id", help="the numeric REST id")
    s.set_defaults(func=cmd_ad)
    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
