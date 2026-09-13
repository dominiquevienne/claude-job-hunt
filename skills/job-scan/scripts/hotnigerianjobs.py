#!/usr/bin/env python3
"""HotNigerianJobs — Nigeria's largest job blog, enumerated by its weekly sitemaps; the POST is the unit, and a post's «N positions» is a field, never a multiplier.

  hotnigerianjobs.py list [--file sitemap-37-2026.xml] [--limit N]
  hotnigerianjobs.py post --url <post URL>

THE SITEMAP ENUMERATES POSTS, AND A POST IS ONE OF THREE THINGS

`/sitemap.xml` is an index of weekly files, `sitemap-<week>-<year>.xml`,
newest first; on 2026-09-13 the newest, `sitemap-37-2026.xml`, held 4 190
`/hotjobs/<id>/<slug>.html` posts over five days (2026-09-07 … 09-11), ids
953270 … 957460, contiguous. A post is:

  a SINGLE     «Mobile Developer at Ardova Plc» — one JSON-LD `JobPosting`,
               `totalJobOpenings: "1"`, a `validThrough`, an `addressRegion`;
  a DIGEST     «BIC Nigeria Job Recruitment (4 Positions)» — no JSON-LD, a
               numbered list «1.) Title / Location: Lagos / Click Here To View
               Details» whose every link is a SINGLE of its own, in the SAME
               sitemap file (the four BIC positions are 956940 … 956946);
  a BAG        «HNJ Exclusive Job Goody Bag — September Week Two» — a weekly
               digest of digests.

**So the 4 190 posts double-count: a digest's positions are posts too.** The
adapter emits the POST — one row per `<loc>`, never one per position — with
`positions_in_slug` read from the slug when the slug says «-N-positions»
(228 posts, 1 208 positions declared, on 2026-09-13; the slug is cut at ~50
characters, so a digest whose number fell off the slug reads as a single
until its page is opened) and `kind` = single / digest / bag. It prints the
post count and the declared positions **apart**, and adds neither to the
other: *«4 190 posts; 228 digests declare 1 208 positions in their slugs —
positions that are posts of their own in the same file, so the two numbers
are not summed».* No stated total exists anywhere on the site; the sitemap
is the only enumeration, and `_sitemap.count` checks it against itself.

`post --url` reads ONE page: a single → the `JobPosting` (`title`,
`hiringOrganization.name`, `datePosted`, `validThrough`, `employmentType`,
`jobLocation.address.addressRegion` and `addressCountry`, `totalJobOpenings`
→ `positions`, `occupationalCategory`, `industry`, `description`); a digest
→ ONE row whose `positions` is the list of `{n, title, location, url}` read
from the numbered list, and `positions_stated` the «(N Positions)» of the
title, with the two compared and «k short» said when they differ. **The
adapter never walks a digest's links, and never turns one post into N rows.**
No `mailto:`, no phone — nothing of the kind is read.

THE RULES: 2 302 B — Cloudflare's managed block naming `ClaudeBot`, `*` open
bar `/kgb/` and `/images/` — `identity()` answers `claude-user`, `verdict()`
sweeps since #230, `certain: True`; no `Crawl-delay` (2 s is ours). Measured
2026-09-12 15:27 and 2026-09-13 16:05 UTC (#233, lot 7 → this adapter).
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
from _ldjson import absent_reason, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _sitemap import count as sitemap_count, count_says, locs as sitemap_locs
from _ua import UA

HOST = "www.hotnigerianjobs.com"
BASE = "https://" + HOST
INDEX = BASE + "/sitemap.xml"
WEEKLY_RE = re.compile(r"/sitemap-(\d{2})-(\d{4})\.xml$")
POST_RE = re.compile(r"^https://www\.hotnigerianjobs\.com/hotjobs/(\d+)/([a-z0-9-]+)\.html$")
ENTRY_RE = re.compile(r"<url>(.*?)</url>", re.S)
SLUG_POSITIONS_RE = re.compile(r"-(\d+)-positions?$")
TITLE_POSITIONS_RE = re.compile(r"\((\d+)\s+Positions?\)", re.I)
# «<strong>1.)&nbsp;Associate Manager …</strong>» then «<p>Location: Lagos</p>» then the link — the digest's numbered list; each marker opens a segment
ITEM_MARK_RE = re.compile(r"<strong>\s*(\d+)\.\)")
ITEM_LINK_RE = re.compile(r'href="(https://www\.hotnigerianjobs\.com/hotjobs/\d+/[^"]+)"')
POSTED_RE = re.compile(r"Posted on\s+\w{3}\s+(\d{1,2})(?:st|nd|rd|th)?\s+(\w{3}),\s+(\d{4})")
MONTHS = {m: i for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[hotnigerianjobs] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # no Crawl-delay declared; 2 s between requests is ours — the pages are 180 kB each


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.5", "Accept-Language": "en"})
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
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def kind_of(slug):
    """single / digest / bag, from the slug — a lossy witness (cut at ~50 chars), and it says so on the row."""
    if "goody-bag" in slug:
        return "bag", None
    m = SLUG_POSITIONS_RE.search(slug)
    if m:
        return "digest", int(m.group(1))
    return "single", None


def entry(block):
    m = re.search(r"<loc>\s*(.*?)\s*</loc>", block, re.S)
    if not m:
        return None
    url = htmlmod.unescape(m.group(1))
    p = POST_RE.match(url)
    if not p:
        return None
    ident, slug = p.group(1), p.group(2)
    lm = re.search(r"<lastmod>\s*(.*?)\s*</lastmod>", block, re.S)
    kind, n = kind_of(slug)
    return {"source": "hotnigerianjobs", "country": "NG", "ledger_id": f"hotnigerianjobs:{ident}", "id": ident, "url": url,
            "slug": slug, "kind": kind, "positions_in_slug": n, "lastmod": lm.group(1) if lm else None}


def newest_weekly(index_body):
    files = [u for u in sitemap_locs(index_body) if WEEKLY_RE.search(u)]
    if not files:
        return None, []
    # the index lists newest first, and the name carries the week — sort by (year, week) rather than trust the order
    files.sort(key=lambda u: (int(WEEKLY_RE.search(u).group(2)), int(WEEKLY_RE.search(u).group(1))), reverse=True)
    return files[0], files


def cmd_list(a):
    if a.file:
        url = a.file if a.file.startswith("https://") else f"{BASE}/{a.file.lstrip('/')}"
        files = [url]
    else:
        code, body = get(INDEX)
        if code != 200:
            die(f"{INDEX}: HTTP {code}", EXIT_PARTIAL)
        url, files = newest_weekly(body)
        if not url:
            die(f"{INDEX}: no sitemap-<week>-<year>.xml in the index — {count_says(body)}", EXIT_PARTIAL)
    code, body = get(url)
    if code == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    c = sitemap_count(body)
    if c["locs"] != c["urls"]:
        die(f"{url}: {c['locs']} <loc> against {c['urls']} <url> — the file does not agree with itself, and no count is printed.", EXIT_PARTIAL)
    rows, seen = [], set()
    for block in ENTRY_RE.findall(body):
        e = entry(block)
        if not e or e["id"] in seen:
            continue
        seen.add(e["id"])
        rows.append(e)
    if not rows:
        die(f"{url}: {c['locs']} <loc>, none of the shape /hotjobs/<id>/<slug>.html — {count_says(body)}", EXIT_PARTIAL)
    for r in rows[:a.limit] if a.limit else rows:
        print(json.dumps(r, ensure_ascii=False))
    days = sorted({(r["lastmod"] or "")[:10] for r in rows if r["lastmod"]})
    digests = [r for r in rows if r["kind"] == "digest"]
    declared = sum(r["positions_in_slug"] or 0 for r in digests)
    bags = sum(1 for r in rows if r["kind"] == "bag")
    note(f"{url.rsplit('/', 1)[1]} ({len(files)} weekly file(s) in the index): {c['locs']} <loc>, {c['urls']} <url>; **{th(len(rows))} distinct post(s)**"
         + (f" over {len(days)} day(s), {days[0]} … {days[-1]}" if days else "") + (f" ({a.limit} printed under --limit)" if a.limit and len(rows) > a.limit else "") + ".")
    note(f"{th(len(digests))} digest(s) declare {th(declared)} position(s) in their slugs, {bags} weekly bag(s) — a digest's positions are posts of their own in the same file, "
         "so the two numbers are printed apart and never summed; the slug is cut at ~50 characters, so a digest whose number fell off reads as a single until its page is opened.")
    note("the site states no total anywhere — the sitemap is the only enumeration, checked against itself (<loc> = <url>) and not against a figure the site does not give.")


def digest_items(body):
    """The numbered list as `{n, title, location, url}` — the segment between two markers, never one row per item at the output."""
    marks = list(ITEM_MARK_RE.finditer(body))
    items = []
    for i, m in enumerate(marks):
        seg = body[m.end():marks[i + 1].start() if i + 1 < len(marks) else m.end() + 4000]
        title = re.search(r"(.*?)</strong>", seg, re.S)
        loc = re.search(r"Location:\s*(.*?)</p>", seg, re.S | re.I)
        link = ITEM_LINK_RE.search(seg)
        items.append({"n": int(m.group(1)), "title": text(title.group(1)) if title else None,
                      "location": (text(loc.group(1)) or None) if loc else None, "url": link.group(1) if link else None})
    return items


def digest_row(ident, url, body):
    title = re.search(r"<title>(.*?)\s*\|", body, re.S)
    title = text(title.group(1)) if title else None
    stated = TITLE_POSITIONS_RE.search(title or "")
    stated = int(stated.group(1)) if stated else None
    posted = POSTED_RE.search(text(body))
    items = digest_items(body)
    return {"source": "hotnigerianjobs", "country": "NG", "ledger_id": f"hotnigerianjobs:{ident}", "id": ident, "url": url, "kind": "bag" if "goody-bag" in url else "digest",
            "title": title,
            "posted": f"{posted.group(3)}-{MONTHS.get(posted.group(2).lower(), 0):02d}-{int(posted.group(1)):02d}" if posted and posted.group(2).lower() in MONTHS else None,
            "positions_stated": stated, "positions_read": len(items), "positions": items, "language": "en"}


def cmd_post(a):
    m = POST_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not a post address — expected {BASE}/hotjobs/<id>/<slug>.html")
    ident = m.group(1)
    code, body = get(a.url)
    if code == 404:
        die(f"{a.url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    found = postings(body)
    if not found:
        # a digest carries no JSON-LD — it is a numbered list of links, and the row is the POST, never its N positions
        row = digest_row(ident, a.url, body)
        if not row["positions"]:
            why = absent_reason(body)
            die(f"{a.url}: no JobPosting and no numbered list of positions — {why}", EXIT_PARTIAL)
        print(json.dumps(row, ensure_ascii=False))
        if row["positions_stated"] is not None and row["positions_stated"] != row["positions_read"]:
            note(f"{row['positions_read']} position(s) read, the title states {row['positions_stated']} — {abs(row['positions_stated'] - row['positions_read'])} "
                 + ("short" if row["positions_stated"] > row["positions_read"] else "more read than stated") + "; one row either way.")
        else:
            note(f"{row['positions_read']} position(s) read" + (f", the title states {row['positions_stated']} — equal" if row["positions_stated"] is not None else ", the title states no number") + "; one row.")
        return
    d = found[0]
    org = d.get("hiringOrganization") or {}
    loc = d.get("jobLocation") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    et = d.get("employmentType")
    tjo = d.get("totalJobOpenings")
    print(json.dumps({
        "source": "hotnigerianjobs", "country": ((addr.get("addressCountry") or "").strip() or "NG") if isinstance(addr, dict) else "NG",
        "ledger_id": f"hotnigerianjobs:{ident}", "id": ident, "url": a.url, "kind": "single",
        "title": text(d.get("title")),
        "employer": (text(org.get("name")) or None) if isinstance(org, dict) else None,
        "employment_type": ", ".join(et) if isinstance(et, list) else et,
        "region": (text(addr.get("addressRegion")) or None) if isinstance(addr, dict) else None,
        "positions": int(tjo) if isinstance(tjo, (int, str)) and str(tjo).strip().isdigit() else None,
        "category": text(d.get("occupationalCategory")) or None, "industry": text(d.get("industry")) or None,
        "posted": d.get("datePosted"), "valid_through": d.get("validThrough"),
        # the description arrives entity-encoded INSIDE the JSON («&lt;p&gt;»): unescape once before the tags are stripped
        "description": text(htmlmod.unescape(d.get("description") or ""))[:20000], "language": "en",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="HotNigerianJobs — the newest weekly sitemap, one row per POST; a post's positions are a field, never a multiplier.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every post of the newest weekly sitemap (4 190 on 2026-09-13), from the index unless --file names a file")
    s.add_argument("--file", help="a weekly file, `sitemap-37-2026.xml` or its full URL")
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("post", help="one post — a single's JobPosting, or a digest's numbered list as ONE row")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_post)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
