#!/usr/bin/env python3
"""inPA (`inpa.gov.it`, Italy) — Italy's public-sector recruitment portal, read through the sitemap its own rules declare and the fields every detail page serves.

  inpa.py sitemap [--limit N]
  inpa.py ad --url <advertisement URL>

THE ROUTE THE ISSUE PRESCRIBED IS REFUSED IN WRITING, AND IT IS A COOKIE BANNER

`shared/boards/inpa-it.md` (measured 2026-10-06) named
`/wp-json/wcc/v1/` as "the route to build on". **Both halves of that are
wrong, and the second is the one nobody had looked at.**

`robots.txt` is identical byte for byte on `inpa.gov.it` and
`www.inpa.gov.it` — 202 bytes, `md5 86be41489815` — puts us under
`User-agent: *`, and writes `Disallow: /wp-json/`. Guarded on the exact
paths, in a turn distinct from any retrieval, with one token:
`/wp-json/` and `/wp-json/wcc/v1/` both answer
`allowed=False, state=read, certain=True, kind=disallow, rule=/wp-json/`
**on both host forms.** That is a written refusal on our path, so it binds
every route, the browser included. The card's guard had been taken on the
ROOT: its verdict was true of `/` and silent about the route.

**And that namespace would never have served a vacancy.** `wcc` is
WebToffee Cookie Consent. The single occurrence of `wcc/v1` in a 103 KB
detail page is `var _wccApi = {"base": "…/wp-json/wcc/v1/", "nonce": "…"}`,
in a block whose `sourceURL` is `webtoffee-cookie-consent-js-extra`. The
2026-10-06 read saw a `wp-json` namespace in the page and took it for the
content route.

THE PERMITTED ENUMERATOR IS THE ONE THE RULES FILE DECLARES

`Sitemap: https://www.inpa.gov.it/sitemap.xml`, and `_robots.sitemaps_for()`
returns it. `group_for()` drops `Host:` and `Sitemap:` in silence — that is
what `shared/robots-policy.md` documents — **but the dedicated parser exists
and answers**, so nothing here was out of the tooling's reach; it had simply
not been called. `delay_for()` returns `None`: no `Crawl-delay` is declared,
so the 2 s pace below is ours and not the operator's.

The sitemap is an INDEX of three members. **This adapter walks all three and
matches every `<loc>` against the advertisement shape** rather than trusting
the member named `bandi`: which member carries the advertisements is the
site's business, and a hard-coded member is a silent zero the day it is
renamed. On 2026-11-07 19:19 UTC, `sitemap-bandi.xml` (448 219 bytes,
`md5 ddda2ca7a3c4`) held **1 915 `<loc>`, all distinct, one single path
shape** — `/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id=<32 hex>` —
and `pages` and `posts` held none. **The slug is a QUERY STRING, not a path
segment**, which is why the shape is matched on the whole address.

Those 1 915 name the **APEX**, while the card's 2026-10-06 line says every
internal link points at `www.`. Both host forms are guarded and permitted,
so the shape below accepts either and the address is emitted as published.

`<lastmod>` ran from 2023-09-20 to 2026-11-06, 1 249 of them in 2026-10 and
501 in 2026-11 — consistent with a rebuild, and this repository's own rule
is that reading a board moves its `lastmod`. **So it is not read as a date
here**; the dates are the two candidature fields on the advertisement.

THE DETAIL PAGE IS SERVER-RENDERED, AND IT CARRIES NO JSON-LD

First, median and last member of the sorted sitemap, each guarded before
retrieval: HTTP 200, 102–104 KB, 2 240 to 3 173 characters of text visible
outside every script — and **0 `JobPosting`, 0 `ld+json`, 0
`__NEXT_DATA__`, 0 `data-page`, 0 `self.__next_f`**. There is nothing for
`_ldjson` to read: the fields are in the markup, as
`<span class="concorso-label">LABEL: </span><span class="concorso-content">VALUE</span>`.

**TWO TRAPS IN THAT MARKUP, both of which a single composed motif walks into.**

  1. `Data chiusura candidature`'s value span is **not closed by `</p>`** —
     the markup is `</span></div>`, with the `</p>` missing. A motif
     anchored on `</p>` fails on exactly that field, which is the deadline.
  2. **`Stato` does not use `concorso-content` at all.** It is
     `<span class="concorso-status Aperto …"><strong>Aperto</strong></span>`,
     so one motif over `concorso-content` misses it in silence — and it is
     the field that says whether the vacancy is open. It is read from the
     CLASS, with the `<strong>` text as a second source, and the two are
     compared on every advertisement rather than assumed to agree.

**And the field set is not fixed:** `Link al sito della PA` was on 2 of the
3 measured. So the pairs are ITERATED and carried through under their own
Italian labels; naming them would drop whatever the next page adds.
`Descrizione` and `Bando/Avviso e Allegati` carry no value span at all —
their content follows the label in a sibling block — so each has its own
motif. Attachments are `portale.inpa.gov.it/api/media/<uuid>` with the
filename in `title`.

`portale.inpa.gov.it` is a THIRD host, carrying the apply link and the
attachments. **This adapter never fetches it** — it emits the addresses and
stops. It is deliberately not added to the card's `hosts:`: that host has
not been guarded, and emitting a URL is not retrieving it.

**DATES CARRY NO OFFSET.** The page prints `30 Novembre 2026  10:00` —
Italian month name, two spaces — and declares no zone anywhere. They are
emitted as naive ISO-8601 with no `Z` and no offset, and `*_tz` says
`None`: Italy is CET/CEST, but inventing an offset would be a figure the
page does not carry. The original string travels beside the parse.

Measured 2026-11-07 19:19–19:21 UTC and 2026-11-09 11:1x UTC. Issue #1055.
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
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

APEX = "https://inpa.gov.it"
WWW = "https://www.inpa.gov.it"
SITEMAP = WWW + "/sitemap.xml"
LISTING = WWW + "/bandi-e-avvisi/"
COUNTRY = "IT"

# the slug is a QUERY STRING, so the shape is matched on the whole address;
# either host form is accepted -- both are guarded and permitted, and the
# sitemap names the apex while the card's 2026-10-06 line says `www.`
AD_RE = re.compile(
    r"^https://(?:www\.)?inpa\.gov\.it/bandi-e-avvisi/dettaglio-bando-avviso/"
    r"\?concorso_id=([0-9a-f]{32})$")

H1_RE = re.compile(r"(?is)<h1[^>]*>(.*?)</h1>")
# the value span is OPTIONAL: `Descrizione` and `Bando/Avviso e Allegati`
# carry none, and `Data chiusura candidature`'s is not closed by `</p>` --
# so nothing here may anchor on the paragraph
PAIR_RE = re.compile(
    r'<span class="concorso-label[^"]*">\s*([^<]+?)\s*:\s*</span>'
    r'(?:\s*<span class="concorso-content[^"]*">(.*?)</span>)?', re.S)
# `Stato` lives in the CLASS, not in a `concorso-content` span
STATUS_RE = re.compile(
    r'<span class="concorso-status\s+([^\s"]+)[^"]*">(.*?)</span>', re.S)
DESC_RE = re.compile(
    r'Descrizione:\s*</span>\s*</p>\s*<div class="font-lora">(.*?)</div>', re.S)
ATTACH_RE = re.compile(
    r'<a href="(https://portale\.inpa\.gov\.it/api/media/[^"]+)"\s+title="([^"]*)"')
# **anchored on the CLASS, not on the host.** The page carries TWO
# `/ui/public-area/` links and the header's «Accedi all'area personale» login
# comes FIRST: a motif on the host alone captures that one, which is 47
# characters, identical on every advertisement, and wrong. Its constancy
# across three pages was the only tell. The apply button carries
# `class="… invia-candidatura …"`, and its `returnUrl` carries the
# advertisement's OWN id -- a cross-check that cannot pass by accident.
APPLY_RE = re.compile(r'<a href="([^"]+)"[^>]*class="[^"]*invia-candidatura')

MONTHS = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
          "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
          "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}
DATE_RE = re.compile(r"^(\d{1,2})\s+([^\s\d]+)\s+(\d{4})(?:\s+(\d{1,2}):(\d{2}))?$")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


class ShapeMoved(Exception):
    """The page answered 200 and carried neither shape this adapter knows.

    **A pure function must not call `sys.exit`**: raising is what lets
    `tests/` assert the distinction between «the shape moved» and «the
    advertisement is empty», which is the whole point of the message.
    """


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[inpa] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# no `Crawl-delay` is declared -- `delay_for()` returns None -- so 2 s is ours
_PACE = Pace("inpa.gov.it", own=2.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "it,en;q=0.5"})
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
    out = htmlmod.unescape(markup)
    return re.sub(r"[ \t]+", " ", out).strip()


def th(n):
    """Thousands with a space -- «1 915» -- the repo's figure style."""
    return f"{n:,}".replace(",", " ")


def when(s):
    """`(iso, None)` from «30 Novembre 2026  10:00», or `(None, why)`.

    **The page declares no offset anywhere**, so the second member is the
    zone and it is always `None`: Italy is CET/CEST and saying so here would
    be a figure the page does not carry. The original string is emitted
    beside this, so a wrong month map cannot hide behind a null.
    """
    s = re.sub(r"\s+", " ", (s or "")).strip()
    if not s:
        return None, "no value"
    m = DATE_RE.match(s)
    if not m:
        return None, f"not the shape «DD Mese YYYY HH:MM»: {s!r}"
    day, mon, year, hh, mm = m.groups()
    num = MONTHS.get(mon.lower())
    if num is None:
        return None, f"month not recognised: {mon!r}"
    return ("%04d-%02d-%02dT%02d:%02d" % (int(year), num, int(day),
                                          int(hh or 0), int(mm or 0))), None


def _slug(label):
    """An Italian label to a stable key, accents and spaces folded."""
    k = label.lower().replace("/", " ")
    k = re.sub(r"[^a-z0-9]+", "_", k).strip("_")
    return k or "campo"


def cmd_sitemap(a):
    code, xml = get(SITEMAP)
    if code != 200:
        die(f"{SITEMAP}: HTTP {code}", EXIT_PARTIAL)
    members = [u.strip() for u in sitemap_locs(xml)]
    if not members:
        die(empty_first_page("inpa", xml, "<loc>", where=SITEMAP), EXIT_PARTIAL)
    rows, seen, per, raw, unmatched = [], set(), [], 0, 0
    # every member is walked: which one carries the advertisements is the
    # site's business, and a hard-coded member is a silent zero the day it
    # is renamed
    for m in members:
        mcode, mxml = get(m)
        if mcode != 200:
            note(f"{m}: HTTP {mcode} — this member was not read, so the count "
                 f"below is a FLOOR and not the board.")
            per.append((m, None))
            continue
        got = 0
        for loc in sitemap_locs(mxml):
            raw += 1
            hit = AD_RE.match(loc.strip())
            if not hit:
                unmatched += 1
                continue
            got += 1
            ident = hit.group(1)
            if ident in seen:
                continue
            seen.add(ident)
            rows.append({"source": "inpa", "country": COUNTRY,
                         "ledger_id": f"inpa:{ident}", "id": ident,
                         "url": loc.strip()})
        per.append((m, got))
    if raw == 0:
        die(empty_first_page("inpa", xml, "<loc>", where=SITEMAP), EXIT_PARTIAL)
    if not rows:
        die(f"{SITEMAP}: {th(raw)} <loc> across {len(members)} member(s) and not one of "
            f"the shape /bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id=<32 hex> — "
            f"the advertisement addresses moved. **Nothing here says the board is "
            f"empty.**", EXIT_PARTIAL)
    for r in (rows[:a.limit] if a.limit else rows):
        print(json.dumps(r, ensure_ascii=False))
    short = ", ".join(f"{u.rsplit('/', 1)[-1]} {'unread' if n is None else th(n)}"
                      for u, n in per)
    unread = [u for u, n in per if n is None]
    note(f"{len(members)} member(s) in the index ({short}); {th(raw)} <loc> read, "
         f"{th(raw - unmatched)} matched the advertisement shape and {th(unmatched)} did "
         f"not; **{th(len(rows))} distinct advertisement id(s)**"
         + (f" ({a.limit} printed under --limit)" if a.limit else "") + ".")
    if unread:
        note(f"{len(unread)} member(s) could not be read, so this is a FLOOR: " +
             ", ".join(unread))
    note("No second source: the board states no count of its own that this adapter "
         "reads, so the figure above is this adapter's own extraction and nothing "
         "corroborates it. **A count names a SIZE, never a NATURE** — the shape was "
         "confirmed by opening the first, median and last member on 2026-11-07.")


def parse_ad(ident, url, body):
    """`(record, notes)` from one served detail page — **no network at all.**

    The extraction is separated from the fetch on purpose: welded inside the
    command it could only ever be exercised against the live site, and
    `tests/` would have had nothing to hold. `tests/test_core.py` calls this
    with the three bodies measured on 2026-11-07.
    """
    h1 = H1_RE.search(body)
    title = text(h1.group(1)) if h1 else ""

    fields, labels = {}, []
    for label, val in PAIR_RE.findall(body):
        labels.append(label)
        fields[_slug(label)] = text(val) if val else None

    # `Stato` is in the class; the `<strong>` text is the second source
    st = STATUS_RE.search(body)
    status = text(st.group(1)) if st else None
    status_text = text(st.group(2)) if st else None
    status_note = None
    if status and status_text and status.lower() != status_text.lower():
        status_note = (f"the status class says {status!r} and the text says "
                       f"{status_text!r} — two sources, one grandeur, and they "
                       f"disagree on this advertisement")

    desc = DESC_RE.search(body)
    description = text(desc.group(1)) if desc else None

    attachments = [{"url": u, "name": htmlmod.unescape(n)}
                   for u, n in ATTACH_RE.findall(body)]
    apply_m = APPLY_RE.search(body)
    apply_url = apply_m.group(1) if apply_m else None
    apply_note = None
    if apply_url and ident not in apply_url:
        apply_note = (f"the apply link does not carry this advertisement's id "
                      f"({ident}) — {apply_url!r}. **Either the button is not "
                      f"this advertisement's, or the portal stopped round-"
                      f"tripping the id**; it is emitted as served.")

    opens, opens_why = when(fields.get("data_apertura_candidature"))
    closes, closes_why = when(fields.get("data_chiusura_candidature"))
    posts = fields.get("numero_di_posti")
    try:
        posts_n = int(posts) if posts else None
    except ValueError:
        posts_n = None

    if not title and not fields:
        raise ShapeMoved(
            f"{url}: HTTP 200 and neither an <h1> nor one `concorso-label` "
            f"pair. **This says the page shape moved, not that the "
            f"advertisement is empty.**")

    out = {
        "source": "inpa", "country": COUNTRY,
        "ledger_id": f"inpa:{ident}", "id": ident, "url": url,
        "title": title or None,
        "employer": fields.get("ente_di_riferimento"),
        "employer_site": fields.get("link_al_sito_della_pa"),
        "region": fields.get("area_geografica"),
        "selection": fields.get("valutazione"),
        "status": status,
        "status_text": status_text,
        # `*_raw` is the string AS SERVED with runs of spaces collapsed, like
        # every other field here -- the page prints two spaces before the
        # time. It is carried so that a wrong month map cannot hide behind a
        # null, which collapsing whitespace does not defeat; it is not a
        # byte-for-byte copy, and calling it so would be a figure too strong.
        "opens": opens, "opens_raw": fields.get("data_apertura_candidature"),
        "closes": closes, "closes_raw": fields.get("data_chiusura_candidature"),
        # the page declares no zone: naming one would be a figure it does not carry
        "dates_tz": None,
        "posts": posts_n, "posts_raw": posts,
        "description": (description or "")[:20000] or None,
        "attachments": attachments,
        "apply_url": apply_url,
        # every page measured is Italian and none declares a language per
        # advertisement; this is the portal's language, not a read of the text
        "language": "it",
        # the Italian labels as SERVED, so a field this adapter does not name
        # is still visible to whoever reads the output
        "fields_seen": labels,
    }
    notes = []
    if apply_note:
        out["apply_mismatch"] = apply_note
        notes.append(apply_note)
    for why, which in ((opens_why, "data apertura"), (closes_why, "data chiusura")):
        if why:
            notes.append(f"{which}: {why} — emitted raw, parsed as null.")
    if status_note:
        out["status_disagreement"] = status_note
        notes.append(status_note)
    return out, notes


def cmd_ad(a):
    url = a.url.strip()
    hit = AD_RE.match(url)
    if not hit:
        die(f"{url}: not an advertisement address — expected "
            f"{APEX}/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id=<32 hex>")
    code, body = get(url)
    if code == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}. **A readable body is not an answer — the code "
            f"decides.**")
    try:
        out, notes = parse_ad(hit.group(1), url, body)
    except ShapeMoved as e:
        die(str(e), EXIT_PARTIAL)
    print(json.dumps(out, ensure_ascii=False))
    for n in notes:
        note(n)


def main():
    p = argparse.ArgumentParser(
        description="inPA — Italy's public-sector recruitment portal, through the "
                    "sitemap its rules declare and the fields its pages serve.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="distinct advertisement ids, from every "
                                       "member of the declared index")
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one advertisement, from the fields it serves")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
