#!/usr/bin/env python3
"""Prekoveze.me — Montenegro's second stock, and the same sitemap skeleton as
`zaposli.me` under markup that shares none of its anchors.

    prekoveze.py list [--since YYYY-MM-DD] [--live] [--fetch] [--limit N]
    prekoveze.py ad --url https://prekoveze.me/posao/<id>/<employer>/<slug>

THE RESEMBLANCE IS THE TRAP

    prekoveze.me/sitemap.xml -> /sitemap/oglasi.xml + /sitemap/pretrage.xml
    zaposli.me/sitemap.xml   -> /sitemap/oglasi.xml + /sitemap/pretrage.xml
    both serve advertisements at   /posao/<id>/<employer>/<title>

**Identical file names, identical URL scheme, and `zaposli.py`'s four anchors
return `None` on three of three pages here.** *`zaposli` has two `<h1>`, the
first a banner; this board has one, and it is the title. `zaposli` marks its
fields with `mdi-` icons and spells its dates «&nbsp;10. septembar 2026.&nbsp;»;
this one uses `fas fa-` icons and writes «&nbsp;10.9.2026.&nbsp;».* **A sitemap
that looks like a neighbour's says nothing about the page it points at.**

WHERE THE FIELDS ARE, AND WHY NOT WHERE THEY LOOK

**The visible text is truncated and the tooltip is not.** The city and category
cells render as `Administracija, Nekr&hellip;` while
`data-original-title="Kategorije: Administracija, Nekretnine, Prodaja"` carries
the whole value. **Every field here is read from the tooltip**, and an extractor
taking the link text would return a silently shortened string — *not an empty
one, which is why it would never be noticed.*

**And the `ld+json` on this page is a decoy.** There are two blocks and neither
is a `JobPosting`: an `Organization` and a `WebSite`, both describing the site.
*The `addressLocality` in them is `Podgorica` — the publisher's own office, on
every advertisement, including the ones in Bar and Budva.*

TWO ANCHORS FOR THE DEADLINE, AND THEY ARE CHECKED AGAINST EACH OTHER

    <i class="fas fa-calendar-alt"> … 22.9.2026.
    <meta name="googlebot" content="unavailable_after: 2026-09-22">

**The same date in two independent places**, so this adapter parses both and
reports every disagreement by name. *A numeric `d.m.yyyy` is exactly the format
where a day and a month swap without producing anything invalid.*

WHAT `--since` CAN AND CANNOT DO HERE

**The advertisement publishes no posting date — only a deadline, on 3 of 3
pages read.** So the sitemap's `<lastmod>` has nothing on the page to be checked
against, and this adapter **cannot** say what it means. `--since` filters on it
and **prints that limitation every time it is used**. *On `zaposli` the same
filter is honest because `lastmod` was compared to the site's own posting date
on ten advertisements; here there is no such date to compare to, and the
difference between the two boards is evidence, not carelessness.*
"""

import argparse
import datetime
import html as html_mod
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

BASE = "https://prekoveze.me"
INDEX = BASE + "/sitemap.xml"
ADS_CHILD = "/sitemap/oglasi.xml"      # named, matched on the index's own <loc>
FACETS_CHILD = "/sitemap/pretrage.xml"  # counted, never read
AD_PREFIX = "/posao/"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL, EXIT_REFUSED, EXIT_UNKNOWN = 2, 3, 6, 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
SITEMAP = re.compile(r"<sitemap>(.*?)</sitemap>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)

# **Each counted one-per-advertisement on three pages before being used.**
TITLE = re.compile(r"<h1>(.*?)</h1>", re.S)
EMPLOYER = re.compile(r'global\.firma\s*=\s*"(.*?)"', re.S)
DEADLINE = re.compile(
    r'fa-calendar-alt"></i>.*?>\s*(\d{1,2}\.\d{1,2}\.\d{4})\.', re.S)
UNAVAILABLE = re.compile(
    r'name="googlebot"\s+content="unavailable_after:\s*(\d{4}-\d{2}-\d{2})')
TOWN = re.compile(
    r'fa-location-arrow"></i>.*?data-original-title="Mjesta:\s*([^"]*)"', re.S)
CATEGORY = re.compile(
    r'fa-tags"></i>.*?data-original-title="Kategorije:\s*([^"]*)"', re.S)

DATE = re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$")

_PACE = Pace("prekoveze.me", own=1.0)
_ANNOUNCED = False


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[prekoveze] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)


def get(url):
    global _ANNOUNCED
    gate(url)
    if not _ANNOUNCED:
        _ANNOUNCED = True
        note(_PACE.source())
    _PACE.wait()
    # **Through `wire_url`, and here it is not a precaution.** 210 of this
    # board's 243 addresses carry `ž`, `č`, `š`, `ć` or `đ` — 86 % — and
    # `urllib` raises on every one of them. The neighbouring board lost 87 % to
    # exactly this before the encoder moved into `_robots`.
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "sr-ME,sr;q=0.9,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def text(fragment):
    if fragment is None:
        return None
    s = html_mod.unescape(html_mod.unescape(re.sub(r"<[^>]+>", "", fragment)))
    return re.sub(r"\s+", " ", s).strip() or None


def one(rx, page):
    m = rx.search(page)
    return text(m.group(1)) if m else None


def parse_date(s):
    """`22.9.2026` -> `2026-09-22`, or None. Never raises."""
    if not s:
        return None
    m = DATE.match(s.strip())
    if not m:
        return None
    try:
        return datetime.date(
            int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
    except ValueError:
        return None


def ads_child(index_body):
    """The advertisement child, matched on the index's own `<loc>`."""
    children = [LOC.search(b).group(1).strip()
                for b in SITEMAP.findall(index_body) if LOC.search(b)]
    ads = [u for u in children if urllib.parse.urlsplit(u).path == ADS_CHILD]
    facets = [u for u in children if
              urllib.parse.urlsplit(u).path == FACETS_CHILD]
    if not ads:
        die(f"the index declares no {ADS_CHILD}; it lists "
            + ", ".join(urllib.parse.urlsplit(u).path for u in children))
    note(f"{len(children)} child sitemap(s); {len(facets)} facet file(s) "
         f"counted and not read")
    return ads[0]


def entries():
    code, body = get(INDEX)
    if code != 200:
        die(f"{INDEX}: HTTP {code}")
    code, body = get(ads_child(body))
    if code != 200:
        die("the advertisement sitemap: HTTP %d" % code)
    rows, seen, raw = [], set(), 0
    for blk in ENTRY.findall(body):
        m = LOC.search(blk)
        if not m:
            continue
        u = m.group(1).strip()
        if AD_PREFIX not in urllib.parse.urlsplit(u).path:
            continue
        # **`raw` counts before the set, and that is the whole point.** The
        # first version of this line printed `len(seen)` against `len(rows)`,
        # which are equal by construction: the counter could not differ from
        # the thing it was checking, so it printed a reassurance and could
        # never print a warning. *An inert control reads exactly like a passing
        # one*, and this one was written in the same hour as a card about a
        # total that agreed with its own source.
        raw += 1
        if u in seen:
            continue
        seen.add(u)
        d = LASTMOD.search(blk)
        rows.append((u, d.group(1) if d else None))
    if raw != len(rows):
        note(f"raw {raw} / distinct {len(rows)} — {raw - len(rows)} address(es) "
             f"appear more than once in the advertisement sitemap.")
    else:
        note(f"{len(rows)} advertisement(s), raw {raw} / distinct {len(rows)}, "
             f"no duplicate. **This line prints either way**, and the two "
             f"numbers are counted on different sides of the set.")
    return rows


def card(url, lastmod, page):
    numeric = parse_date(one(DEADLINE, page))
    meta = one(UNAVAILABLE, page)
    # **The cross-check, and it is the reason both are parsed.** A `d.m.yyyy`
    # can swap day and month without becoming invalid; the ISO form cannot.
    disagree = bool(numeric and meta and numeric != meta)
    row = {
        "id": "prekoveze:" + url.rstrip("/").split("/")[4],
        "url": url,
        "title": one(TITLE, page),
        "employer": one(EMPLOYER, page),
        "town": one(TOWN, page),
        "categories": one(CATEGORY, page),
        "deadline": meta or numeric,
        "deadline_numeric": numeric,
        "deadline_meta": meta,
        "deadline_forms_disagree": disagree,
        "posted_sitemap": lastmod,
    }
    missing = [k for k in ("title", "employer", "town", "deadline")
               if not row[k]]
    row["missing_fields"] = missing or None
    return row


def cmd_list(a):
    if a.live and not a.fetch:
        die("`--live` needs `--fetch`: the deadline is on the advertisement, "
            "and this board publishes no posting date at all.", EXIT_UNKNOWN)

    rows = entries()
    raw = len(rows)
    if a.since:
        kept = [(u, d) for u, d in rows if d and d >= a.since]
        undated = sum(1 for _u, d in rows if not d)
        note(f"--since answered from the sitemap: {len(kept)} of {raw}. "
             f"**What `<lastmod>` means here was NOT established**: the "
             f"advertisement publishes a deadline and no posting date, so "
             f"there is nothing on the page to compare it against. On "
             f"`zaposli.me` the same filter was checked against the site's own "
             f"posting date; here it cannot be.")
        if undated:
            note(f"{undated} entries carry no <lastmod> and are dropped by "
                 f"--since; counted here rather than lost.")
        rows = kept
    if a.limit:
        rows = rows[:a.limit]

    if not a.fetch:
        print(json.dumps({"source": "prekoveze", "country": "ME",
                          "sitemap_entries": raw, "selected": len(rows),
                          "fetched": False,
                          "ads": [{"id": "prekoveze:" + u.rstrip("/").split("/")[4],
                                   "url": u, "posted_sitemap": d}
                                  for u, d in rows]},
                         ensure_ascii=False, indent=1))
        return

    today = datetime.date.today().isoformat()
    kept, broken, expired, incomplete, clash = [], [], 0, [], []
    for u, d in rows:
        code, page = get(u)
        if code != 200:
            broken.append((u, f"HTTP {code}"))
            continue
        c = card(u, d, page)
        if c["missing_fields"]:
            incomplete.append((c["id"], c["missing_fields"]))
        if c["deadline_forms_disagree"]:
            clash.append((c["id"], c["deadline_numeric"], c["deadline_meta"]))
        if a.live and c["deadline"] and c["deadline"] < today:
            expired += 1
            continue
        kept.append(c)

    # **Both negative controls print whether or not anything failed.**
    if incomplete:
        note(f"{len(incomplete)} of {len(rows)} advertisements are missing at "
             f"least one field. Each is named:")
        for i, fields in incomplete:
            note(f"    {i:>18}  missing {', '.join(fields)}")
    else:
        note(f"every one of {len(rows)} advertisements yielded title, "
             f"employer, town and deadline. **Negative control**: this line "
             f"prints whether or not anything failed.")
    if clash:
        note(f"{len(clash)} advertisement(s) give two different deadlines; "
             f"the ISO meta is kept and each is named:")
        for i, n, m in clash:
            note(f"    {i:>18}  d.m.yyyy {n}  vs  meta {m}")
    else:
        note(f"the two deadline forms agreed on all {len(rows)}. **Negative "
             f"control**: printed either way.")
    if broken:
        note(f"{len(broken)} unreadable: "
             + "; ".join(f"{u.split('/')[4]} ({w})" for u, w in broken[:5]))
    if a.live:
        note(f"{expired} dropped on a past deadline; those without one are "
             f"kept — absent is not past.")

    print(json.dumps({"source": "prekoveze", "country": "ME",
                      "sitemap_entries": raw,
                      "read": len(kept) + len(broken) + expired,
                      "kept": len(kept), "unreadable": len(broken),
                      "incomplete": len(incomplete),
                      "deadline_disagreements": len(clash),
                      "expired_dropped": expired if a.live else None,
                      "ads": kept}, ensure_ascii=False, indent=1))
    if broken and not kept:
        sys.exit(EXIT_BROKEN)
    if broken or incomplete or clash:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    if not urllib.parse.urlsplit(a.url).path.startswith(AD_PREFIX):
        die(f"--url must be an advertisement under {AD_PREFIX}")
    code, page = get(a.url)
    if code in (404, 410):
        die(f"{a.url} is gone (HTTP {code}). Record it as discarded.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}")
    c = card(a.url, None, page)
    print(json.dumps(c, ensure_ascii=False, indent=1))
    if c["missing_fields"]:
        note(f"missing: {', '.join(c['missing_fields'])}")
        sys.exit(EXIT_PARTIAL)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    li = sub.add_parser("list")
    li.add_argument("--since", help="YYYY-MM-DD, on an UNVERIFIED sitemap date")
    li.add_argument("--live", action="store_true", help="needs --fetch")
    li.add_argument("--fetch", action="store_true")
    li.add_argument("--limit", type=int)
    li.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
