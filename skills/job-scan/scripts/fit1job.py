#!/usr/bin/env python3
"""Fit1Job (`www.fit1job.ch`) — a Romandie IT recruitment agency, five live
advertisements, plain HTTP: no key, no cookie, no browser.

    fit1job.py list [--category it|finance|divers] [--fetch] [--since YYYY-MM-DD]
    fit1job.py ad --url https://www.fit1job.ch/poste/<slug>/

Requested in #868. **The request's premises were re-measured on 2026-10-05
rather than repeated, and two of them did not hold** — both are below.

THE RETIRED ADVERTISEMENT ANSWERS 200 AND CARRIES NO `JobPosting`

This is the finding, and it is the reason this adapter exists at all: the board
is small and its ads already reach a jobup sweep, so what it adds is a
**step-1b open/closed signal measured on a real retirement**.

    GET /poste/program-manager-fr-en-h-f/              200   96 407 B   JobPosting
    GET /poste/chef-fe-de-projet-informatique-fr-en/   200   84 908 B   NONE

The second is the example advertisement of #868. On 2026-10-05 it still answers
`200` with a full, ad-shaped page — masthead, menu, footer, 85 KB — **and the
`JobPosting` block is gone, with no visible notice anywhere in the body.** It
is in neither the listing nor the Yoast sitemap. *WP Job Manager emits the
structured block for a published listing and drops it when the listing is
unpublished; nothing else on the page changes.*

> **So «the ad page is still up» says nothing about this board**, and the
> discriminant is the presence of the structured block — not any text a reader
> could see. That is `shared/ats-open-check.md` step 1b in one measured case.

**And `validThrough` is not what retires an advertisement here.** #868 reports
reading `validThrough 2026-11-17` on that example on 2026-09-22 — *reported by
the issue, not re-measurable now, because the block that carried it is exactly
what disappeared*. What **is** measured today: it is retired on 2026-10-05, and
the oldest still-listed advertisement was posted **2026-08-24**, five weeks
earlier. *Retirement is the agency unpublishing a filled position, not an
expiry date arriving.* **A consumer that trusted `validThrough` would have held
this one open for another six weeks.**

TWO PREMISES OF #868 THAT DID NOT HOLD

- *«Each ad page carries a `JobPosting` JSON-LD block»* — **every LISTED one
  does; the retired one carries none.** The sentence is true of the board's
  live set and false of its URL space, and the difference is the whole signal
  above.
- *«Stable per-ad id? the URL slug»* — **there is a numeric id**, and it is
  published twice per card: `data-job_id="6328"` on the `<li>` and `post-6328`
  in the anchor's class list. It is the WordPress post id. This adapter keys on
  it and carries the slug beside it, because the canonical URL is rebuilt from
  the slug and contract 4 forbids scraping one out of the page.

THE CARD REGEX IS BOUNDED BY `</a></li>`, AND A NON-GREEDY `</li>` IS WRONG

**The cards nest a `<ul>` of `<li>`s inside each card**, so
`<li\\s+data-longitude=.*?</li>` stops at the card's own *location* item — it
yields the right number of cards and truncates each one before its date.
*Measured: that mistake printed five cards with five correct titles, five
correct towns and `date=None` on all five, which reads as a board that
publishes no dates.* The bound used here is the anchor's close, and each card
contains exactly one `</a>`, one `<time datetime=`, one `location-on`.

THE PAGE DECLARES ITS OWN CAP, SO THE WALK HAS THREE NAMED ENDS

    <div class="job_listings" data-per_page="10" data-show_pagination="false" …>

`data-per_page` is the board's own figure and not our extraction. Five cards
against a declared ten means **the first page is not full, therefore it is the
whole board** — `ended: complete`. Equal to the cap means the rest sits behind
`load_more_jobs` on `admin-ajax.php`, which this adapter does not follow:
`ended: capped`, and then the sitemap below says how many exist. A transport
failure is `ended: transport`. *Without those three words a capped read looks
like a smaller board.*

*The category pages declare a different cap and a different order —
`/categorie-poste/it/` carries `per_page="15" orderby="featured"` against the
archive's `10` / `date`.* So the cap is read per page, never assumed.

**And a `--category` read has its own fourth word, `complete-category`.** *The
first draft of this adapter printed «therefore it is the whole board» on
`/categorie-poste/it/`, and compared that one taxonomy term against a sitemap
that enumerates all of them.* Both were wrong in the same way — a bounded run
does not answer «how many are there» — **and neither showed up in the output,
because today all five advertisements carry `it` and the two agreed.** So the
scoped run says `complete-category`, and the witness is reported as answering a
different question rather than as a gap.

THE WITNESS IS YOAST'S SITEMAP, AND IT HAS NEVER BEEN EXERCISED ON A DIVERGENCE

`/job_listing-sitemap.xml` is written by a different plugin from the one that
renders the listing, so it is not our own extraction under another name — the
trap jobup's `ItemList.numberOfItems` set on 2026-10-05, where a page count
agreed with a board count on the narrow case and not on the broad one.

    sitemap 6 <loc>   =   5 advertisements  +  /les-postes/ itself
    listing   5 cards     same five, by MEMBERSHIP and not by cardinal

**The archive page is inside the job sitemap**, so anything that is not
`/poste/<slug>/` is dropped before counting.

> **And the limit is declared rather than glossed: today both say five, so this
> witness has never been read on a case where the two SHOULD differ.** *That
> case needs the listing to be capped, which needs ten advertisements, which
> this board has not had.* The suite exercises the divergence on a fixture; the
> live board has not.

WHAT THIS BOARD DOES NOT PUBLISH

- **The employer, ever.** `hiringOrganization.name` is `""` and the card's
  `data-company` is `""` on every advertisement read — *a field that is present
  and empty, which `if x` cannot tell from a field that is absent.* The agency
  describes the client (*«notre client, situé dans la banlieue de Fribourg»*)
  and never names it. So `employer` is `None` here and **the ledger's employer
  dedup cannot work on these rows**; nothing is invented from the host name.
- **No `jobLocation` in the structured data at all.** The geography is on the
  listing card only — `Corminboeuf, Fribourg, Suisse` — so `--fetch` enriches
  the dates and the text and takes the place from the card. *Checked for the
  Batiactu trap, where a region came from the employer's head office: the five
  towns are five different ones across three cantons, and only one is the
  agency's own.*
- **No salary, no `employmentType`.** The contract type is on the card as a
  class (`data-job_type_class="fixe"`), not in the JSON-LD.

ZERO-SHAPED ANSWERS (contract 5)

| What is seen | What it means |
| :-- | :-- |
| `200`, a full ad page, no `JobPosting` | **the advertisement is retired** — the case above |
| `200`, listing with 0 cards | the board is empty, or the shortcode changed: the sitemap count decides, and a disagreement is reported rather than resolved |
| cards == `data-per_page` | **capped, not complete** — more exist behind the AJAX route |
| `200`, `JobPosting` present, `ld+json` unreadable | *our* failure: `_ldjson.absent_reason().our_fault` is true and the run dies rather than reporting an empty board |

Config keys (contract 0): none. Nothing to obtain, nothing to log into.
"""

import argparse
import html as html_mod
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
from _ua import UA

BASE = "https://www.fit1job.ch"
LIST = BASE + "/les-postes/"
CATEGORY = BASE + "/categorie-poste/%s/"
SITEMAP = BASE + "/job_listing-sitemap.xml"
AD = BASE + "/poste/%s/"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL, EXIT_REFUSED, EXIT_UNKNOWN = 2, 3, 6, 7, 8

# **Bounded by the anchor's close, never by the first `</li>`** — see the
# module docstring: the cards nest a `<ul class="listing-icons">` of `<li>`s,
# and a non-greedy `</li>` truncates every card before its date.
CARD = re.compile(r"<li\s+data-longitude=.*?</a>\s*</li>", re.S)
JOB_ID = re.compile(r'data-job_id="(\d+)"')
CARD_TITLE = re.compile(r'data-title="([^"]*)"')
CARD_TYPE = re.compile(r'data-job_type_class="([^"]*)"')
CARD_HREF = re.compile(r'href="(https?://[^"]*?/poste/([^"/]+)/)"')
# The town sits in the card's own first `listing-icons` item, behind the theme's
# icon font. **One per card, and five in the whole page** — counted, not assumed.
CARD_PLACE = re.compile(r'location-on"></i>\s*([^<]+)<')
CARD_DATE = re.compile(r'<time datetime="(\d{4}-\d{2}-\d{2})"')
CARD_CATS = re.compile(r"job_listing_category-([a-z0-9-]+)")
CARD_TEASER = re.compile(r'class="listing-desc"><p>(.*?)</p>', re.S)
# The board's own cap, declared on the container that renders the list.
PER_PAGE = re.compile(r'<div class="job_listings\s*"[^>]*\bdata-per_page="(\d+)"')
SITEMAP_LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")
AD_PATH = re.compile(r"^/poste/([^/]+)/?$")

CATEGORIES = ("it", "finance", "divers")

_PACE = Pace("www.fit1job.ch", own=1.0)
_ANNOUNCED = False


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[fit1job] {msg}", file=sys.stderr)


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
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "fr-CH,fr;q=0.9,en;q=0.7",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def text(s):
    if not s:
        return None
    s = html_mod.unescape(re.sub(r"<[^>]+>", " ", str(s)))
    return re.sub(r"\s+", " ", s).strip() or None


def first(rx, s, group=1):
    m = rx.search(s)
    return m.group(group) if m else None


def place_of(card):
    """`Corminboeuf, Fribourg, Suisse` -> locality, region, country.

    **Split from the RIGHT**, because a locality can itself contain a comma
    (`Rond-Point-de-Rive, Genève, Suisse` has three parts and
    `Petit-Lancy, Genève, Suisse` has three; a four-part form would belong to
    the locality, not to a fourth administrative level). A shape this does not
    recognise is returned whole as the locality rather than silently split —
    an unparsed place is a question, a wrongly split one is an answer.
    """
    raw = text(first(CARD_PLACE, card))
    if not raw:
        return {"locality": None, "region": None, "country": None,
                "place_raw": None}
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if len(parts) >= 3:
        return {"locality": ", ".join(parts[:-2]), "region": parts[-2],
                "country": parts[-1], "place_raw": raw}
    if len(parts) == 2:
        return {"locality": parts[0], "region": None, "country": parts[1],
                "place_raw": raw}
    return {"locality": raw, "region": None, "country": None, "place_raw": raw}


def from_card(card):
    """One listing card. Everything here comes from the LISTING."""
    href = CARD_HREF.search(card)
    ident = first(JOB_ID, card)
    row = {
        "id": "fit1job:" + ident if ident else None,
        "job_id": ident,
        "slug": href.group(2) if href else None,
        "url": AD % href.group(2) if href else None,
        "title": text(first(CARD_TITLE, card)),
        # **Never the client.** `data-company` is present and empty on every
        # card read; the agency names itself nowhere in the data either.
        "employer": None,
        "poster": None,
        "contract_type": first(CARD_TYPE, card) or None,
        "categories": sorted(set(CARD_CATS.findall(card))) or None,
        # The card's date is an absolute `datetime` attribute, not a relative
        # label — so it is a real publication date and named as one. The ad
        # page's `datePosted` carries the same day with a time; `--fetch`
        # replaces this value and says so.
        "posted": first(CARD_DATE, card),
        "posted_measures": "the day the listing was published, from the card's "
                           "own <time datetime>",
        "teaser": text(first(CARD_TEASER, card)),
        "countries": ["CH"],
    }
    row.update(place_of(card))
    return row


def cards_of(page):
    return CARD.findall(page)


def sitemap_ads():
    """The Yoast job sitemap's advertisement slugs — the independent witness.

    **Anything that is not `/poste/<slug>/` is dropped**: the archive page
    `/les-postes/` is inside this sitemap, so counting `<loc>` would declare
    one advertisement more than exists. Returns `None` when the sitemap cannot
    be read — an unavailable witness is not a count of zero.
    """
    code, body = get(SITEMAP)
    if code != 200 or not body:
        note(f"{SITEMAP}: HTTP {code} — **no witness this run**, which is not "
             f"the same as a witness that agrees.")
        return None
    out = []
    for loc in SITEMAP_LOC.findall(body):
        m = AD_PATH.match(urllib.parse.urlsplit(loc).path)
        if m:
            out.append(m.group(1))
    return out


def detail(url, row):
    """Enrich one row from its own ad page, and read the retirement signal."""
    code, page = get(url)
    if code in (404, 410):
        row["status"] = "gone"
        row["missing_fields"] = ["page"]
        return row, f"HTTP {code}"
    if code != 200:
        row["status"] = "unknown"
        return row, f"HTTP {code}"
    jp = next(iter(postings(page)), None)
    if jp is None:
        why = absent_reason(page)
        if why.our_fault:
            # **A reading failure is never reported as a retirement.** The
            # asymmetry is the point: inventing a retirement is silent, and
            # this exit is not.
            die(f"{url}: {why.text}")
        # Measured 2026-10-05 on `/poste/chef-fe-de-projet-informatique-fr-en/`:
        # 200, 84 908 bytes, Yoast's blocks parse, no `JobPosting`, and no
        # visible notice in the body.
        row["status"] = "retired"
        row["retired_evidence"] = (
            f"HTTP 200, {len(page)} characters, "
            f"{why.kind}: the page is served in full and carries no JobPosting")
        return row, None
    row["status"] = "listed"
    posted = jp.get("datePosted")
    if posted:
        row["posted"] = posted
        row["posted_measures"] = "`datePosted` from the ad page's JobPosting"
    row["valid_through"] = jp.get("validThrough")
    row["valid_through_measures"] = (
        "the board's own field. **It is not what retires an advertisement "
        "here** — see the module docstring: a retired ad loses the whole block "
        "while its last known validThrough was still weeks away")
    row["title"] = text(jp.get("title")) or row["title"]
    row["description"] = text(jp.get("description"))
    row["direct_apply"] = jp.get("directApply")
    return row, None


def cmd_list(a):
    if a.category and a.category not in CATEGORIES:
        die(f"--category must be one of {', '.join(CATEGORIES)} "
            f"(the taxonomy the site publishes)")
    url = CATEGORY % a.category if a.category else LIST
    code, body = get(url)
    if code != 200:
        # **`ended: transport` and nothing else** — a failed read is not a
        # small board.
        print(json.dumps({"source": "fit1job", "country": "CH", "url": url,
                          "ended": "transport", "found": 0, "ads": []},
                         ensure_ascii=False, indent=1))
        die(f"{url}: HTTP {code}")

    declared = first(PER_PAGE, body)
    declared = int(declared) if declared else None
    cards = cards_of(body)
    rows = [from_card(c) for c in cards]
    rows = [r for r in rows if r["id"]]

    if declared is None:
        note("the listing container declares no `data-per_page` — **the cap is "
             "unknown**, so completeness cannot be claimed from the card count "
             "alone and the sitemap below is the only witness.")
        ended = "unknown-cap"
    elif len(cards) >= declared:
        ended = "capped"
    else:
        ended = "complete"

    # **A category read is a BOUNDED run, and the witness does not answer a
    # bounded question.** The sitemap enumerates the whole board, so comparing
    # it to one taxonomy term reports every advertisement of the other terms as
    # a shortfall — rocken.py's lesson («the anchor answers *how many are
    # there*, and a bounded run does not answer it»), here with a filter
    # instead of a page limit. *Today all five advertisements carry `it`, so
    # the two happen to agree and the defect would not have shown.*
    slugs = sitemap_ads()
    witness = len(slugs) if slugs is not None else None
    if slugs is not None and a.category:
        note(f"sitemap declares {witness} advertisement(s) for the WHOLE "
             f"board; this run read the `{a.category}` category only and holds "
             f"{len(rows)}. **No comparison is made** — the two answer "
             f"different questions, and a difference here would be the other "
             f"categories, not a gap.")
    elif slugs is not None:
        ours = {r["slug"] for r in rows}
        theirs = set(slugs)
        note(f"sitemap declares {witness} advertisement(s), this run holds "
             f"{len(rows)} — **compared by membership, not by cardinal.**")
        only_them = sorted(theirs - ours)
        only_us = sorted(ours - theirs)
        if only_them:
            note(f"    in the sitemap and not in the listing ({len(only_them)}): "
                 + ", ".join(only_them[:8]))
        if only_us:
            note(f"    in the listing and not in the sitemap ({len(only_us)}): "
                 + ", ".join(only_us[:8]))
        if not only_them and not only_us:
            note("    the two sets are identical. **This line prints either "
                 "way**, and the two sides were read from two different "
                 "documents written by two different plugins.")
        if ended == "capped" and only_them:
            note(f"**capped**: the page is full at its declared {declared} and "
                 f"{len(only_them)} further advertisement(s) exist. They sit "
                 f"behind `load_more_jobs` on admin-ajax.php, which this "
                 f"adapter does not follow.")
    if ended == "complete" and a.category:
        # **Not «the whole board».** A full category page says the category is
        # complete and nothing at all about the terms it filtered out.
        ended = "complete-category"
        note(f"{len(cards)} card(s) against a declared cap of {declared}: the "
             f"page is not full, so this is the whole `{a.category}` category "
             f"— **not the whole board** (`ended: complete-category`).")
    elif ended == "complete":
        note(f"{len(cards)} card(s) against a declared cap of {declared}: the "
             f"first page is not full, **therefore it is the whole board** — "
             f"`ended: complete`.")

    if a.fetch:
        broken = []
        for r in rows:
            r, err = detail(r["url"], r)
            if err:
                broken.append((r["job_id"], err))
        retired = [r for r in rows if r.get("status") == "retired"]
        if retired:
            note(f"{len(retired)} listed advertisement(s) answered 200 with no "
                 f"JobPosting — unexpected here, because the listing is what "
                 f"publishing drives. Named: "
                 + ", ".join(str(r["job_id"]) for r in retired))
        else:
            note("every listed advertisement carried a JobPosting. **Negative "
                 "control: printed either way** — the interesting case is a "
                 "URL that is no longer listed, which `ad --url` reads.")
        if broken:
            note(f"{len(broken)} unreadable: "
                 + "; ".join(f"{i} ({w})" for i, w in broken[:5]))
    if a.since:
        before = len(rows)
        rows = [r for r in rows
                if not r.get("posted") or r["posted"][:10] >= a.since]
        note(f"--since {a.since}: {len(rows)} of {before} kept; an "
             f"advertisement with no date is KEPT — absent is not old.")

    missing = [(r["job_id"], [k for k in ("title", "locality", "posted")
                              if not r.get(k)]) for r in rows]
    missing = [(i, m) for i, m in missing if m]
    if missing:
        note(f"{len(missing)} of {len(rows)} row(s) missing a field. Each is "
             f"named:")
        for i, m in missing:
            note(f"    {i:>6}  missing {', '.join(m)}")
    else:
        note(f"every one of {len(rows)} row(s) carries title, locality and a "
             f"date. **Printed either way.**")

    print(json.dumps({
        "source": "fit1job", "country": "CH", "url": url,
        "category": a.category, "declared_per_page": declared,
        "sitemap_declares": witness, "cards_seen": len(cards),
        "found": len(rows), "fetched": bool(a.fetch), "ended": ended,
        "ads": rows}, ensure_ascii=False, indent=1))
    if missing:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_PATH.match(parts.path)
    if not m or parts.netloc not in ("www.fit1job.ch", "fit1job.ch"):
        die("--url must be https://www.fit1job.ch/poste/<slug>/")
    slug = m.group(1)
    row = {"id": None, "job_id": None, "slug": slug, "url": AD % slug,
           "title": None, "employer": None, "poster": None,
           "countries": ["CH"],
           "locality": None, "region": None, "country": None,
           "place_note": "**not available from the ad page**: this board "
                         "publishes no `jobLocation`. The town is on the "
                         "listing card only — run `list` for it."}
    row, err = detail(row["url"], row)
    if err:
        print(json.dumps(row, ensure_ascii=False, indent=1))
        die(f"{a.url}: {err}", EXIT_GONE if row["status"] == "gone"
            else EXIT_BROKEN)
    print(json.dumps(row, ensure_ascii=False, indent=1))
    if row["status"] == "retired":
        note("**this advertisement is retired.** It answers 200 and carries no "
             "JobPosting, which on this board is what unpublishing looks "
             "like — there is no visible notice on the page. Record it as "
             "closed; do not read the 200 as an open position.")
        sys.exit(EXIT_GONE)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    li = sub.add_parser("list")
    li.add_argument("--category", help=f"one of {', '.join(CATEGORIES)}")
    li.add_argument("--fetch", action="store_true",
                    help="open each ad for its dates and full text")
    li.add_argument("--since", help="YYYY-MM-DD")
    li.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
