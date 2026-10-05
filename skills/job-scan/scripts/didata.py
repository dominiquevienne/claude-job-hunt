#!/usr/bin/env python3
"""DiData (`swissdidata.com`) — one Lausanne employer's own careers list:
laboratory data management (Di-LIMS, biobanking, clinical trials), hiring
Laravel/Vue full-stack, backend, DevOps and QA, almost all remote.

    didata.py list [--fetch] [--all]
    didata.py ad --url https://swissdidata.com/careers/<slug>

Requested in #864. **The premises were re-measured on 2026-10-05 rather than
repeated, and the most important one was wrong in the direction that hides
work**: the card field #864 read as *«a hidden, empty field, NOT a closure
signal»* is this board's closure signal, in its **other form**.

THE ONE FIELD, TWO FORMS, AND SIX POSITIONS THAT ARE CLOSED

    <span class="hidden">Not available</span>                        OPEN
    <span class="inline-flex … bg-yellow-200 … opacity-100">Not available</span>   CLOSED

#864 reports the first form *«present on all 14 cards»* on 2026-09-22 and
concludes it means nothing. On 2026-10-05 the page carries **14 cards: 8 in the
first form and 6 in the second** — a visible yellow badge reading «Not
available», on a card whose container also carries `cursor-not-allowed
opacity-60` and whose anchor is `href="#"`.

**Three independent markers, and they agree on all 14 of 14**: the badge's
visibility, the greyed container, and the dead anchor. *This adapter requires
them to agree and refuses to decide when they do not* — three redundant
markers that disagree mean the markup changed, and guessing which one still
means what is how a closed position gets reported as open.

> **And that is why #864 counted «11 distinct hrefs for 14 cards» and left it
> «not resolved».** The unlinked cards are the unavailable ones. The href count
> is the count of OPEN positions, and taking it for the board's size
> under-reads it by six — *`zero-lien-nest-pas-zero-contenu` in its partial
> form, where the loss is 43% and nothing errors.*

THE SIGNAL LIVES ON THE LISTING ONLY, AND THAT IS THE OPPOSITE OF FIT1JOB

Measured the same afternoon, on the detail pages of two positions the listing
marks unavailable:

    /careers/content-writer            200   32 316 B   no notice of any kind
    /careers/application-engineer-ch   200   43 507 B   no notice of any kind
    /careers/back-end  (OPEN)          200   32 910 B   no notice of any kind

**A closed position's detail page is indistinguishable from an open one's** —
same title, same `h1`, same `Type:` / `Location:`, same apply token, same
`mailto`, and no «Not available» anywhere. *So on this host step 1b must read
the LISTING; the ad page cannot answer.*

**Fit1Job (`fit1job.md`, delivered the same day) is the exact mirror**: there
the listing silently drops a retired advertisement and the ad page answers 200
without its `JobPosting`, so the signal is on the DETAIL page and only there.
**Two hosts, opposite answers to the same question** — which is the general
rule: *where a host states availability is a property of that host, and it is
found rather than assumed.*

THREE ENUMERATORS, AND NONE OF THEM CONTAINS THE OTHERS

    listing cards                        14   (8 open, 6 unavailable)
    listing hrefs                         8   exactly the open ones
    declared sitemap, default locale     13   slugs with a real detail page

*The sitemap holds detail pages for five of the six unavailable cards, and one
slug — `application-engineer-de` — that has **no card at all**. The listing
holds two cards, «Graphic Designer» and «Sales Manager», that the sitemap does
not name; `/careers/sales-manager` answers **404**.*

**And the slug sets DO nest, which is the trap**: all 8 linked slugs are in the
sitemap, so a reader comparing slug to slug sees a clean inclusion and concludes
the sitemap is the enumerator. *It is not — **six cards carry no slug at all**,
so the comparison cannot reach them, and two of those six answer to nothing the
sitemap names.*

> **A clean inclusion between the keys the two sides SHARE says nothing about
> the records that have no key.** So the size of this board is not established,
> and this adapter does not pretend otherwise: it walks both, emits the union,
> and **names the enumerator of every record** — which is what
> `shared/boards/README.md` asks when there is no witness that can arbitrate.

*And a card is never joined to a sitemap slug by resembling it.* «Application
Engineer - Switzerland» and `application-engineer-ch` are plainly the same
position to a human; matching them by pattern is an inference, and a wrong join
would attach one position's text to another's status.

THE SLUG SUFFIX IS NOT ONE DIMENSION, SO IT IS NOT A DEDUP KEY

    /careers/application-engineer-it   «Application engineer Italy»        Milan, Italy
    /careers/application-engineer-ch   «Application Engineer Switzerland»  Hybrid (CH)
    /careers/application-engineer-de   «Application Engineer Schweiz (Deutsch)»

**`-it` and `-ch` are places; `-de` is a LANGUAGE** — its own title says
*Schweiz*, so it is the German rendering of the `-ch` position under a
different slug. *Dedup by slug therefore over-counts by at least one, and no
rule here guesses which suffixes are languages.* **It is named, not resolved.**

The locale PATHS are different: `/fr/careers/<slug>` and `/de/careers/<slug>`
are translations of the same position — `/fr/careers/back-end` is
«Développeur·se Backend - Laravel», `lang="fr"`, a different document from the
default one. Those this adapter does drop, because the path says so.

WHAT THE BOARD PUBLISHES, AND WHAT IT DOES NOT

- **No `JobPosting`, no `ld+json`, no date of any kind** — not on the listing,
  not on 7 detail pages read. *So there is no `datePosted`, no `validThrough`,
  and the ledger's date stays EMPTY rather than being derived: an empty field
  is a question, a wrong date is an answer.*
- **The apply route is an email with a mandatory subject token** — `FULLSTACK26`
  on automation-engineer, `CW26` on content-writer, `APPENGCH26` on
  application-engineer-ch. **#864 proposes the token doubles as a rough date
  («…23 for a posting evergreen since 2023»); the measurement refutes it as a
  date and keeps the shape**: the suffix is `26` on **12 of 12** tokens read on
  2026-10-05, and #864 read `backendev23` on `back-end` on 2026-09-22. *So it
  is year-shaped and it MOVED in thirteen days: it tracks the employer's edit,
  not the posting, and it is neither a date for the advertisement nor a stable
  key.*
- **The mailbox itself is NOT emitted here.** It is the employer's own
  candidate contact and `README.md` distinguishes that from a leak, *but this
  session works under a standing instruction that no e-mail address appears in
  its output*, so the row says an address is present and where to read it. **A
  rule I was given is not mine to relax because a precedent would allow it**;
  it is raised, not worked around.
- **The employer is this employer**, so `employer` is filled — unusual here,
  and it makes the ledger's employer dedup work against the Indeed mirror.

ZERO-SHAPED ANSWERS (contract 5)

| What is seen | What it means |
| :-- | :-- |
| a card with a visible «Not available» badge | **the position is closed** — and its detail page will not say so |
| the three markers disagreeing | **the markup changed**: no status is emitted for that card and the run exits partial |
| 8 hrefs for 14 cards | normal — the hrefs are the open ones, not the board |
| `/careers/<slug>` answering 404 | the card outlives its page (`sales-manager`, measured) |
| 0 cards with a 200 listing | the markup changed: the sitemap's count is reported beside the zero |

Config keys (contract 0): none. No browser, no login, no key (contract 1).
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
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BASE = "https://swissdidata.com"
LIST = BASE + "/careers"
SITEMAP_INDEX = BASE + "/sitemap.xml"
AD = BASE + "/careers/%s"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL, EXIT_REFUSED, EXIT_UNKNOWN = 2, 3, 6, 7, 8

# **The CARD is the container, never the anchor** — the anchor is `href="#"` on
# every closed position, so anchors enumerate the open ones and nothing else.
CARD = re.compile(
    r'<div class="(?P<cls>[^"]*rounded-xl px-4 pb-6 pt-8[^"]*)">'
    r'<div class="flow-root">(?P<body>.*?)</div></div></div>', re.S)
TITLE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
# The field whose two forms are this board's whole signal.
BADGE = re.compile(r'<span class="([^"]*)">Not available</span>')
HREF = re.compile(r'href="([^"]*)"')
SECTION = re.compile(r'md:w-1/6 md:py-4"><h2[^>]*>([^<]+)</h2>')
# `<!-- -->` is React's text-node separator and sits between the label and the
# value; a reader that does not skip it returns an empty string, which looks
# exactly like a board that publishes no locations.
FIELD = r"%s:</span>\s*(?:<!--\s*-->)?\s*([^<]*)"
H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
TOKEN = re.compile(r"application email:\s*([A-Za-z0-9]+)")
LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")
# The default locale only: `/fr/` and `/de/` are translations of the same
# position, and the path says so.
SITEMAP_AD = re.compile(r"^/careers/([^/]+)/?$")

_PACE = Pace("swissdidata.com", own=1.0)
_ANNOUNCED = False


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[didata] {msg}", file=sys.stderr)


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
        "Accept-Language": "en;q=0.9,fr;q=0.8,de;q=0.7",
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
    s = html_mod.unescape(re.sub(r"<!--\s*-->", "", re.sub(r"<[^>]+>", " ",
                                                           str(s))))
    return re.sub(r"\s+", " ", s).strip() or None


def field(page, label):
    m = re.search(FIELD % re.escape(label), page)
    return text(m.group(1)) if m else None


def rendered(page):
    """The server-rendered HTML, with the React Flight payload removed.

    **The payload repeats the cards as escaped strings**: «Not available»
    occurs 28 times in the page and 14 times in the rendering, so a count taken
    on the raw body is exactly double. *The payload also names a build artefact
    (`page-2ab93bb6ffa11502`) that looks like a slug.*
    """
    return re.sub(r"<script[^>]*>.*?</script>", "", page or "", flags=re.S)


def status_of(cls, body):
    """The three markers, and what to do when they disagree.

    Returns `("open"|"closed"|None, evidence dict)`. **`None` is a refusal to
    decide**, not a default: a closed position reported as open is silent and
    costs the candidate an application, so disagreement exits partial instead.
    """
    badge = BADGE.search(body)
    href = HREF.search(body)
    marks = {
        "badge_visible": bool(badge) and "hidden" not in badge.group(1),
        "container_greyed": "cursor-not-allowed" in cls or "opacity-60" in cls,
        "anchor_dead": (href.group(1) if href else None) in (None, "#", ""),
    }
    if all(marks.values()):
        return "closed", marks
    if not any(marks.values()):
        return "open", marks
    return None, marks


def cards(page):
    """Every card, with its section heading, in page order."""
    body = rendered(page)
    heads = [(m.start(), m.group(1).strip()) for m in SECTION.finditer(body)]

    def section_at(pos):
        cur = None
        for p, n in heads:
            if p < pos:
                cur = n
        return cur

    out = []
    for m in CARD.finditer(body):
        inner, cls = m.group("body"), m.group("cls")
        state, marks = status_of(cls, inner)
        href = HREF.search(inner)
        link = href.group(1) if href else None
        slug = None
        if link and link.startswith("/careers/"):
            slug = link[len("/careers/"):].strip("/") or None
        out.append({
            "id": "didata:" + slug if slug else None,
            "slug": slug,
            "url": AD % slug if slug else None,
            "title": text(TITLE.search(inner).group(1))
            if TITLE.search(inner) else None,
            "employer": "DiData",
            "section": section_at(m.start()),
            "location": field(inner, "Location"),
            "contract_type": field(inner, "Type"),
            "status": state,
            "status_markers": marks,
            "enumerator": "listing",
            # **No date exists anywhere on this board**, and deriving one would
            # be an answer where the honest value is a question.
            "posted": None,
            "posted_measures": "this board publishes no date at all — not on "
                               "the card, not on the ad page, no ld+json",
            "countries": ["CH"],
        })
    return out, [n for _p, n in heads]


def sitemap_slugs():
    """The declared sitemap's `/careers/<slug>` pages, default locale only.

    Returns `None` when it cannot be read: **an unavailable witness is not a
    witness that agrees**, and here it is the only count that is not ours.
    """
    code, body = get(SITEMAP_INDEX)
    if code != 200 or not body:
        note(f"{SITEMAP_INDEX}: HTTP {code} — no witness this run.")
        return None
    children = [u for u in LOC.findall(body) if u.endswith(".xml")]
    out = []
    for child in children or []:
        code, page = get(child)
        if code != 200:
            note(f"{child}: HTTP {code} — the index names a sitemap that does "
                 f"not answer, so the witness is INCOMPLETE and not absent.")
            return None
        for loc in LOC.findall(page):
            m = SITEMAP_AD.match(urllib.parse.urlsplit(loc).path)
            if m and m.group(1) != "careers":
                out.append(m.group(1))
    return sorted(set(out))


def detail(url, row):
    """One ad page. **It carries no availability signal — by measurement.**"""
    code, page = get(url)
    if code in (404, 410):
        row["status_detail"] = "gone"
        return row, f"HTTP {code}"
    if code != 200:
        return row, f"HTTP {code}"
    body = rendered(page)
    h1 = H1.search(body)
    title_tag = re.search(r"<title>(.*?)</title>", page, re.S)
    tok = TOKEN.search(text(body) or "")
    row["detail_title"] = text(h1.group(1)) if h1 else None
    row["page_title"] = text(title_tag.group(1)) if title_tag else None
    # **The card's title and the page's title are different strings** — card
    # «Backend Developer», h1 «Backend - Laravel». A ledger keyed on the title
    # would see two positions, so the slug is the key.
    row["detail_location"] = field(body, "Location")
    row["detail_contract_type"] = field(body, "Type")
    row["experience"] = field(body, "Experience")
    row["apply_route"] = "email with a mandatory subject token"
    row["apply_subject_token"] = tok.group(1) if tok else None
    row["apply_subject_token_measures"] = (
        "read from the ad page. **It tracks the employer's edit, not the "
        "posting**: the suffix is `26` on 12 of 12 tokens read on 2026-10-05, "
        "and #864 read `backendev23` on this very slug on 2026-09-22. So it "
        "is year-shaped and it MOVED — it cannot date an individual "
        "advertisement and it is not a stable key")
    # The address is deliberately not emitted — see the module docstring.
    row["apply_mailbox"] = ("present on the ad page as a mailto link; the "
                            "value is not emitted by this adapter")
    row["detail_says_availability"] = False
    return row, None


def cmd_list(a):
    code, body = get(LIST)
    if code != 200:
        print(json.dumps({"source": "didata", "country": "CH",
                          "ended": "transport", "found": 0, "ads": []},
                         ensure_ascii=False, indent=1))
        die(f"{LIST}: HTTP {code}")
    rows, sections = cards(body)
    hrefs = sorted({r["slug"] for r in rows if r["slug"]})
    undecided = [r for r in rows if r["status"] is None]

    note(f"{len(rows)} card(s) in {len(sections) or 1} section(s) "
         f"({', '.join(sections) or 'unlabelled'}); "
         f"{sum(1 for r in rows if r['status'] == 'open')} open, "
         f"{sum(1 for r in rows if r['status'] == 'closed')} marked «Not "
         f"available», {len(undecided)} undecided.")
    if not rows:
        note("**zero cards on a 200 listing**: the container class changed. "
             "The sitemap count below is the only figure left, and it is not "
             "a count of open positions.")
    if undecided:
        note(f"{len(undecided)} card(s) whose three markers DISAGREE — no "
             f"status is emitted for them, because guessing which marker "
             f"still means what is how a closed position is reported as open:")
        for r in undecided:
            note(f"    {r['title']}  {r['status_markers']}")
    else:
        note("every card's three markers agree. **This line prints either "
             "way**, and the markers are the badge's visibility, the greyed "
             "container and the dead anchor.")
    note(f"{len(hrefs)} of {len(rows)} cards carry a real href. **That is not "
         f"a shortfall**: the unlinked ones are the unavailable ones, and "
         f"taking the href count for the board's size under-reads it.")

    slugs = sitemap_slugs()
    extra = []
    if slugs is not None:
        only_map = [s for s in slugs if s not in hrefs]
        only_list = [s for s in hrefs if s not in slugs]
        note(f"declared sitemap: {len(slugs)} `/careers/<slug>` page(s) in the "
             f"default locale, against {len(hrefs)} linked from the listing — "
             f"**compared by membership, not by cardinal.**")
        if only_map:
            note(f"    a detail page the listing does not link "
                 f"({len(only_map)}): {', '.join(only_map)}")
        if only_list:
            note(f"    linked by the listing and absent from the sitemap "
                 f"({len(only_list)}): {', '.join(only_list)}")
        # **The two sets are not comparable on the cards that have no slug**,
        # and that is the real reason the size is unsettled — not whether the
        # slug sets happen to nest today. *On 2026-10-05 the sitemap contains
        # all 8 linked slugs and 5 more, so the slug sets DO nest; six cards
        # carry no key at all, and two of them («Graphic Designer», «Sales
        # Manager») answer to nothing in the sitemap. Saying so would need a
        # title-to-slug join, which this adapter refuses to make.*
        sans_cle = [r for r in rows if not r["slug"]]
        if sans_cle:
            note(f"**the size of this board is NOT established**: "
                 f"{len(sans_cle)} card(s) carry no slug, so they cannot be "
                 f"compared with the sitemap at all — the nesting of the slug "
                 f"sets says nothing about them. Both enumerators are walked, "
                 f"the union is emitted, and every record names where it came "
                 f"from.")
        elif only_map and only_list:
            note("**Neither enumerator contains the other, so the size of "
                 "this board is NOT established.**")
        if a.all:
            known = {r["slug"] for r in rows}
            for s in only_map:
                if s in known:
                    continue
                extra.append({
                    "id": "didata:" + s, "slug": s, "url": AD % s,
                    "title": None, "employer": "DiData", "section": None,
                    "location": None, "contract_type": None,
                    # **Not «open».** The listing is the only thing that states
                    # availability here, and it says nothing about this slug.
                    "status": None,
                    "status_markers": {"not_on_the_listing": True},
                    "enumerator": "sitemap",
                    "posted": None,
                    "posted_measures": "this board publishes no date at all",
                    "countries": ["CH"],
                })
            note(f"--all: {len(extra)} sitemap-only slug(s) added, each with "
                 f"`status: null` — **the listing is the only thing that "
                 f"states availability, and it does not mention them**. A card "
                 f"is never joined to a slug by resembling it.")

    rows = rows + extra
    if a.fetch:
        broken = []
        for r in rows:
            if not r["slug"]:
                r["detail"] = "none — this card carries no link and no slug"
                continue
            r, err = detail(r["url"], r)
            if err:
                broken.append((r["slug"], err))
        if broken:
            note(f"{len(broken)} detail page(s) unreadable: "
                 + "; ".join(f"{s} ({w})" for s, w in broken[:6])
                 + ". **A card can outlive its page** — `sales-manager` "
                   "answered 404 on 2026-10-05.")
        else:
            note("every slug yielded a detail page. **Printed either way.**")

    print(json.dumps({
        "source": "didata", "country": "CH", "employer": "DiData",
        "cards_seen": len(rows) - len(extra), "hrefs_seen": len(hrefs),
        "sitemap_declares": len(slugs) if slugs is not None else None,
        "sitemap_only": len(extra), "found": len(rows),
        "open": sum(1 for r in rows if r["status"] == "open"),
        "closed": sum(1 for r in rows if r["status"] == "closed"),
        # **Two different nulls, and collapsing them makes the partial exit
        # fire on every normal `--all` run** — a warning that always fires is
        # no better than one that never does. `undecided` is a DISAGREEMENT
        # between the three markers; `not_on_listing` is a slug the only
        # thing that states availability does not mention.
        "undecided": len(undecided),
        "not_on_listing": len(extra),
        "board_size_established": False,
        "fetched": bool(a.fetch), "ads": rows},
        ensure_ascii=False, indent=1))
    # **Exits partial only on a real disagreement.** A sitemap-only row's null
    # status is by construction and is not a defect to report.
    if undecided:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = SITEMAP_AD.match(parts.path)
    if not m or parts.netloc not in ("swissdidata.com", "www.swissdidata.com"):
        die("--url must be https://swissdidata.com/careers/<slug> — and the "
            "DEFAULT locale: /fr/ and /de/ are translations of the same "
            "position")
    slug = m.group(1)
    row = {"id": "didata:" + slug, "slug": slug, "url": AD % slug,
           "employer": "DiData", "countries": ["CH"],
           "status": None,
           "status_note": "**the ad page carries no availability signal on "
                          "this board** — measured 2026-10-05 on two "
                          "positions the listing marks «Not available»: their "
                          "pages are indistinguishable from an open one's. "
                          "Run `list` for the status."}
    row, err = detail(row["url"], row)
    if err:
        print(json.dumps(row, ensure_ascii=False, indent=1))
        die(f"{a.url}: {err}", EXIT_GONE)
    print(json.dumps(row, ensure_ascii=False, indent=1))
    note("status is null by construction here, not by failure: see "
         "`status_note`.")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    li = sub.add_parser("list")
    li.add_argument("--fetch", action="store_true",
                    help="open each ad page for its text and apply token")
    li.add_argument("--all", action="store_true",
                    help="also emit sitemap slugs the listing does not link, "
                         "with status null")
    li.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
