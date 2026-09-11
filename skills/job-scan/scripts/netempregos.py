#!/usr/bin/env python3
"""Net-Empregos (`www.net-empregos.com`) — Portugal's first adapter: two feeds
that hold, four that answer the home page, and an ad page whose dates are the
reader's clock.

    netempregos.py feed [--zona Lisboa] [--categoria "Informática / Programação"] [--limit N]
    netempregos.py list [--limit N]
    netempregos.py ad --id 15978698

WHAT THE HOST DECLARES, AND WHAT IT SERVES — measured 2026-09-11 14:22–14:25 UTC

**Rules open to everyone.** `robots.txt` (808 bytes, md5
`7fdd748d009fc9b74e72ebf8081704f6`, the same ×4 on apex and `www`): `*` →
`Allow: /`, no AI agent named, no `Crawl-delay`; the named refusals are SEO
crawlers and Yandex. **Seven `Sitemap:` lines, and only two hold**:

    Sitemap.asp             200   454 414 o   text, one URL per line   5 000 advertisement URLs, distinct, md5 stable ×2
    rss.asp                 200 1 251 967 o   RSS 2.0, iso-8859-1      1 000 <item>, dc:creator = employer on 1 000 of 1 000, md5 MOVES between reads
    rss_pesquisas.asp       200    71 193 o   THE HOME PAGE            «Emprego  Rss_pesquisas.asp  - Setembro 2026», 0 item
    trovit_all.asp          200    71 169 o   THE HOME PAGE
    careerjet_all.asp       200    71 193 o   THE HOME PAGE
    listagem_livre3.asp     200    71 209 o   THE HOME PAGE
    listagem_cv_livre.asp   NOT READ — a listing of candidates' CVs, not of advertisements

**Four of seven are a `200` that is not an answer** (`shared/never-fail-silently.md`):
a status check passes them, a size check passes them, a `text/xml` check
would be the first to notice — and only the count of advertisements extracted
is the test that cannot be fooled. *That count is printed beside every read
here, and a feed that yields zero items from tens of kilobytes dies through
`_zero.empty_first_page`.*

**RSS ⊂ Sitemap: 1 000 of 1 000 RSS links are in the sitemap's 5 000.** The
RSS is the 1 000 most recent, with fields; the sitemap is 5 000 addresses
without. *The two caps are the feeds' own — by construction, not by the size
of the board — and the site states no total anywhere read.*

**The ad page carries a `JobPosting`, and its dates are the reader's clock.**
`/15978698/…/` read at 14:24:44Z: `datePosted: 2026-9-11 15:24 UTC`; read
again at 14:25:21Z: `15:25 UTC` — Lisbon local time labelled UTC, and
`validThrough` is that plus 30 days. **The advertisement's date is the RSS's
`pubDate` (`Fri, 11 Sep 2026 15:19:31 GMT`) and `Data:` (`11-9-2026`)**; the
`JobPosting`'s two dates are emitted under names that say what they are.

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
from _ldjson import postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path
from _ua import UA
from _zero import empty_first_page

HOST = "www.net-empregos.com"
BASE = f"https://{HOST}"
RSS = BASE + "/rss.asp"
SITEMAP = BASE + "/Sitemap.asp"
RSS_CAP, SITEMAP_CAP = 1000, 5000          # the feeds' own, measured 2026-09-11
AD_URL = re.compile(r"https?://(?:www\.)?net-empregos\.com/(\d+)/([^/\s]+)/?")
ITEM = re.compile(r"<item>(.*?)</item>", re.S)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[net-empregos] {msg}", file=sys.stderr)


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


def to_text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?is)<br\s*/?>|</p>|</li>|</h\d>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    lines = [re.sub(r"[ \t]+", " ", htmlmod.unescape(l)).strip()
             for l in markup.split("\n")]
    return "\n".join(l for l in lines if l).strip()


def ad_url(ident, slug="oferta"):
    """Contract 4: the URL from the id. The site serves the page on the id
    alone; the slug is cosmetic and the sitemap's is used when known."""
    return f"{BASE}/{ident}/{slug}/"


def home_page(body):
    """The tell for the four declared feeds that answer the home page: an
    HTML document titled «Emprego … - <month> <year>»."""
    return bool(re.search(r"<title>\s*Emprego\s", body or "", re.I))


# ------------------------------------------------------------------- feeds --

def _cdata(block, tag):
    m = re.search(rf"<{tag}>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</{tag}>", block, re.S)
    return htmlmod.unescape(m.group(1)).strip() if m else None


def _field(desc, label):
    """`<b>Zona: </b> Setubal<br>` inside the description, once unescaped."""
    m = re.search(rf"<b>\s*{label}:\s*</b>\s*(.*?)\s*<br", desc or "", re.S | re.I)
    return htmlmod.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else None


def card_from_item(block):
    link = _cdata(block, "link") or ""
    m = AD_URL.search(link)
    ident = m.group(1) if m else None
    desc = _cdata(block, "description") or ""
    text = re.search(r"<b>\s*Descri[^:<]*:\s*</b>(.*)$", desc, re.S | re.I)
    return {
        "id": ident,
        "ledger_id": f"net-empregos:{ident}" if ident else None,
        "url": link,
        "title": _cdata(block, "title"),
        "company": _cdata(block, "dc:creator") or _field(desc, "Empresa"),
        "provider": "net-empregos",
        "location": _field(desc, "Zona"),
        "category": _field(desc, "Categoria"),
        "country": "PT",
        "countries": ["PT"],
        # the feed's two dates, named for what the feed calls them
        "date": _field(desc, "Data"),
        "pubdate": _cdata(block, "pubDate"),
        "teaser": to_text(text.group(1))[:600] if text else None,
        "language": "pt",
    }


def cmd_feed(a):
    status, body = get(RSS)
    if status != 200:
        die(f"{HOST} answered HTTP {status} on {RSS}", 4)
    items = ITEM.findall(body)
    if not items:
        # **A 200 that is not an answer.** Four of this host's seven declared
        # feeds serve the home page with this status — the count of items is
        # the only test that sees it.
        die(empty_first_page("net-empregos", body, what="<item>", where=RSS)
            + (" **This body is the HOME PAGE**, the shape four of the seven "
               "declared feeds answer with." if home_page(body) else ""), 6)
    kept = dropped = 0
    zones, cats = {}, {}
    for block in items:
        c = card_from_item(block)
        zones[c["location"]] = zones.get(c["location"], 0) + 1
        cats[c["category"]] = cats.get(c["category"], 0) + 1
        if a.zona and (c["location"] or "").strip().lower() != a.zona.strip().lower():
            dropped += 1
            continue
        if a.categoria and (c["category"] or "").strip().lower() != a.categoria.strip().lower():
            dropped += 1
            continue
        if a.limit and kept >= a.limit:
            continue
        print(json.dumps(c, ensure_ascii=False))
        kept += 1
    with_employer = sum(1 for b in items if "<dc:creator>" in b)
    note(f"{kept} emitted, {len(items)} items read, {dropped} dropped by the "
         f"filter(s); {with_employer} of {len(items)} name their employer. "
         f"**The feed holds at most {RSS_CAP} — its own cap, not the board's** "
         f"— and the site states no total anywhere read.")
    if (a.zona or a.categoria) and not kept:
        # **The filter is compared to what the feed spells**, and the spelling
        # is printed so a zero reads as «not that label» rather than «empty».
        seen = zones if a.zona else cats
        note(f"the feed is not empty — every item was filtered out. Values the "
             f"feed spells, with their counts: "
             + ", ".join(f"{k} {v}" for k, v in sorted(seen.items(),
                                                        key=lambda kv: -kv[1])
                         if k)[:600])


def cmd_list(a):
    status, body = get(SITEMAP)
    if status != 200:
        die(f"{HOST} answered HTTP {status} on {SITEMAP}", 4)
    lines = [l.strip() for l in body.splitlines()]
    urls = [l for l in lines if l.startswith("http")]
    ads = [(m.group(1), m.group(2)) for m in (AD_URL.search(u) for u in urls) if m]
    if not ads:
        die(empty_first_page("net-empregos", body, what="advertisement URL",
                             candidates=len(urls), where=SITEMAP)
            + (" **This body is the HOME PAGE.**" if home_page(body) else ""), 6)
    seen, kept = set(), 0
    for ident, slug in ads:
        if ident in seen:
            continue
        seen.add(ident)
        if a.limit and kept >= a.limit:
            continue                    # keep counting the distinct ids
        print(json.dumps({"id": ident, "ledger_id": f"net-empregos:{ident}",
                          "url": ad_url(ident, slug), "provider": "net-empregos",
                          "country": "PT"}, ensure_ascii=False))
        kept += 1
    note(f"{kept} emitted, {len(seen)} distinct ids in {len(ads)} advertisement "
         f"URLs from {len(urls)} lines, {len(ads) - len(seen)} duplicate id(s). "
         f"**The sitemap holds at most "
         f"{SITEMAP_CAP} — its own cap** — and these are addresses, not cards: "
         f"`feed` carries the fields, `ad` the text.")


# --------------------------------------------------------------------- ad --

def cmd_ad(a):
    if not a.id.isdigit():
        die(f"{a.id!r} is not a Net-Empregos id — the digits of `/<id>/<slug>/`.")
    status, body = get(ad_url(a.id))
    if status == 404:
        die(f"no advertisement {a.id} (HTTP 404) — it was filled or pulled. "
            f"Record it as discarded.", 3)
    if status != 200:
        die(f"{HOST} answered HTTP {status} for {a.id}", 4)
    jp = next(iter(postings(body)), None)
    if jp is None:
        die(f"{ad_url(a.id)}: 200, {len(body)} characters and no JobPosting — the "
            f"page carried one on 2026-09-11 (a `<script type = \"application/"
            f"ld+json\" >` with spaces); the markup moved, or this is not an ad.", 6)
    org = jp.get("hiringOrganization") or {}
    loc = (jp.get("jobLocation") or {})
    addr = loc.get("address") or {} if isinstance(loc, dict) else {}
    print(json.dumps({
        "id": a.id, "ledger_id": f"net-empregos:{a.id}", "url": ad_url(a.id),
        "provider": "net-empregos", "country": "PT",
        "title": jp.get("title"),
        "company": org.get("name") if isinstance(org, dict) else org,
        "location": addr.get("addressLocality"),
        "employment_type": jp.get("employmentType"),
        # **Named for what they are: the reader's clock.** `datePosted` was
        # 15:24 on a read at 14:24:44Z and 15:25 on a read at 14:25:21Z —
        # Lisbon local labelled UTC, minted at render time; `validThrough`
        # is that plus 30 days. The advertisement's date is the feed's.
        "rendered_at_as_datePosted": jp.get("datePosted"),
        "rendered_plus_30d_as_validThrough": jp.get("validThrough"),
        "description": to_text(jp.get("description") or ""),
        "language": "pt",
    }, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("feed", help="the RSS: the 1 000 most recent, with fields")
    f.add_argument("--zona", help="a zone as the feed spells it, e.g. Lisboa, Porto, Setubal")
    f.add_argument("--categoria", help="a category as the feed spells it")
    f.add_argument("--limit", type=int, default=0)
    f.set_defaults(func=cmd_feed)
    l = sub.add_parser("list", help="the sitemap: up to 5 000 advertisement ids, no fields")
    l.add_argument("--limit", type=int, default=0)
    l.set_defaults(func=cmd_list)
    d = sub.add_parser("ad", help="one advertisement's JobPosting, from its id")
    d.add_argument("--id", required=True)
    d.set_defaults(func=cmd_ad)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
