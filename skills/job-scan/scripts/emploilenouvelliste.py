#!/usr/bin/env python3
"""Le Nouvelliste — Emploi (`emploi.lenouvelliste.com`, Haiti): the daily's job board — the one Haitian route that answers a plain client. Issue #777.

  emploilenouvelliste.py jobs [--country-code HT]                 the list: ONE page, its whole history
  emploilenouvelliste.py ad --url https://emploi.lenouvelliste.com/offre-emploi/<id>/<slug>

WHAT IT IS. *Le Nouvelliste* is Haiti's oldest daily, and its board carries the posts of the
ministries, of the projects financed by the IDB and the EU, of the cooperatives and of private
employers. **Of the country's five known boards, one ships an adapter (`caribbeanjobsonline`, a
regional list), one refuses the connection outright (`job509`), and two render client-side
(`jwennjob`, a Next.js shell) — this one serves its list to a plain client.**

THE RULES. `emploi.lenouvelliste.com/robots.txt` is `User-agent: *` and an EMPTY `Disallow:` — open,
`certain: True`, no `Crawl-delay` and no sitemap declared; 3 s is ours. The guard is taken on the
exact path. *A silent rules file does not say there is no rate: it says none is written.*

THE LIST. `/recherche/offres-emploi` (200; 129 111 B) carries **every advert the site has ever
published on one page** — 118 of them on 2026-11-03, keyed by the site's own numeric id, and the ids
run **1 to 118 with no gap**. There is no pager: seven candidate forms (`?page=`, `&page=`,
`pagination`, `rel="next"`, `page-link`, «Suivant», «suivante») return **zero** each.

**THE BOARD STATES NO COUNT, AND THE THREE NUMBERS THAT LOOK LIKE ONE ARE TEMPLATE LITERALS.** They
are named here so that nobody wires one as a witness: «44554 résultat(s)» sits inside an HTML
comment on the list; «Plus de 4500 offres d'emploi vous attendent» is the root's marketing prose;
and «80 jobs» is printed **identically on three different employers' tiles** — OCCED'H, the Conseil
Électoral Provisoire and SOFALAM — which is what proves it is a literal and not a count.

**So the only witness is OUR OWN, and it is declared as such.** Ids contiguous from 1 to N with
exactly N adverts read cannot happen by accident if the parse dropped one, so its PRESENCE certifies
that the extraction is complete. Its ABSENCE certifies nothing: a gap is equally well explained by
the site having deleted an advert, and the run says so instead of choosing.

**THE LIST IS SERVED OLDEST FIRST** — id 1 heads the page and id 118 ends it — so the adverts are
emitted newest first. That sort is not taste: without it `--limit` returns the oldest adverts, all
long closed, and the board reads as dead (the same defect as `jobsbotswana`).

**AND THE BOARD CARRIES NO DATE, ANYWHERE.** Measured on 13 adverts drawn across the whole id range:
no `JobPosting`, no `application/ld+json`, no `<time>`, no `datetime`, no `datePosted`, no
`validThrough`, no `article:published`, and no `Last-Modified` on the wire. **The list carries
neither a date nor a location.** So *what is open* is not a question this board answers, and no
field of these records pretends it does.

THE ADVERT. `ad` reads one page. There is **no `<h1>` on any of the 13** — the title is the `<h3>`,
and the employer is the `<p>` that follows it — and the five blocks the site writes are present on
**13 of 13**: «Description des responsabilités», «Profil recherché», «Composition du dossier de
candidature» and «Autre remarque».

**A fifth heading, «Lieu de dépôt des candidatures», is 13 of 13 in the markup and 0 of 13 LIVE: it
sits inside an HTML comment on every advert.** Counting it was this adapter's first defect, found by
running it and not by reading it — the same shape as counting `<script>` tags on a page that writes
the word in its prose. So the comments come out before the blocks are read, and four is the number.

**AND A BLOCK THAT EXISTS IS NOT A BLOCK THAT IS FILLED.** On the procurement-style adverts the whole
text sits in «Description des responsabilités» (4 494 B on 118, 7 198 B on 109) and the next two
carry a **bare full stop** — so `if value` would emit «.» as a value. A block counts as filled only
when it carries a letter or a digit; otherwise the record says `null`. Advert 1, a classic job post,
fills all four.

**The body is bounded by the container the page uses**, `div.col-lg-8.job-post`, which occurs exactly
once on 13 of 13 and always before the aside. Unbounded, the last block swallowed the sidebar — an
identical 426 B of «Créez une alerte emploi» appeared as the advert's «Autre remarque» on three
adverts of four, which reads as content the advert does not have.

**The closing date lives in the advert's PROSE, and the motif is case-insensitive on purpose.** A
French date within 120 characters after a deadline phrase («date limite», «au plus tard», «avant
le», «dernier délai», «clôture») is emitted as `deadline_stated_in_prose`, with
`deadline_basis` naming the phrase it was read from — prose-derived, never a field the board
declares. Present on **12 of the 13** drawn; advert 89 states none. *The capitalised form of this
motif rendered **zero** on advert 118, which carries two: 118 writes «16 octobre 2026» in lower
case where 1 and 60 write «28 Septembre 2024». The case was the whole defect.*

**BASE64 IMAGES COME OUT FIRST.** Six of the 13 adverts embed `data:image/...;base64,...` inline in
the body — **up to 54 % of the page** (advert 89: 14 068 B of 26 014) — so they are replaced before
anything is read, or the record carries them and the text extraction is polluted by them.

**THE PHONE MOTIF IS ANCHORED, AND THE ANCHOR IS THE WHOLE POINT.** Haiti's public-procurement
adverts are built out of long reference numbers, and the bare motif used elsewhere in this
repository eats them: on the same 13 adverts it takes **7 strings of which 5 are not telephones** —
the grant numbers `2000004110` and `200005176`, the contract number `106-2026`, the publication
reference `527-05/19`, and a date followed by a list numeral — **and the date guard saves none of
them**. Anchored on the Haitian dialling code `+509` or on a written label, it takes **2 of the 2
real numbers and 0 of the 5 references**. Those references are how a candidate names the post he is
applying for, so destroying them is not a harmless excess of caution. *What repairs a redaction
rule is its anchor, not its list of fields.*

E-mail addresses are present on 12 of the 13 and are withheld by name; `withheld_fields` says what
was taken on every record, so a silence is never read as an absence.

`--country-code` STAMPS (the list states no country — the board is Haiti's by its own masthead,
«Offres d'emploi, appel d'offres et recrutement en Haïti», and a stamp is still the user's).

Measured 2026-11-03 19:16–19:3x UTC by the declared client, the guard taken on the exact paths in a
turn of its own: `/robots.txt` 200 (`User-agent: *`, empty `Disallow:`), `/recherche/offres-emploi`
200 (129 111 B, md5 e70ba749b299) with 118 adverts and ids 1–118 contiguous, the root 200 (34 341 B,
md5 db62575fd5eb), and 13 adverts read across the range (ids 1, 10, 20, 30, 40, 50, 60, 69, 79, 89,
99, 109, 118). The premise of #777 held and the board had grown: 111 adverts on 2026-09-20, 118 now.
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
from _ua import UA
from _withheld import withheld_a_contact

HOST = "emploi.lenouvelliste.com"
LIST = f"https://{HOST}/recherche/offres-emploi"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# the base64 payloads come out BEFORE anything is read: six adverts of thirteen embed them,
# one of them 54 % of its own bytes, and they pollute every text extraction downstream
B64_RE = re.compile(r"data:image/[a-z]+;base64,[A-Za-z0-9+/=]+")
STRIP_RE = re.compile(r"(?s)<style.*?</style>|<script.*?</script>")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# ANCHORED on the Haitian dialling code or a written label. The bare motif takes five
# reference numbers for every two telephones on this board, and the date guard used
# elsewhere saves none of them -- a grant number is neither a date nor a phone.
PHONE_RE = re.compile(
    r"\+\s?509[\s.\-]?\d[\d\s.\-]{6,}\d"
    r"|(?:T[ée]l(?:[ée]phone)?|Cell|Whatsapp|WhatsApp)\s*:?\s*\(?\+?\d[\d\s().\-]{5,}\d")
# the comments come out with the base64: a commented-out heading counted as a live block,
# and the list's «44554 résultat(s)» lives in one too
COMMENT_RE = re.compile(r"(?s)<!--.*?-->")
# the container the page uses for the advert's own body, once on 13 of 13, always before the aside
BODY_RE = re.compile(r'<div class="col-lg-8 job-post">')
ASIDE_RE = re.compile(r'<div class="col-lg-4|Créez une alerte emploi')
# a block counts as filled only if it carries a letter or a digit: this board writes a bare
# full stop in the sections it leaves empty, and `if value` would emit «.» as content
FILLED_RE = re.compile(r"[0-9A-Za-z\u00c0-\u024f]")
CARD_RE = re.compile(r'<div class="job-card">(.*?)(?=<div class="job-card">|\Z)', re.S)
HREF_RE = re.compile(r'<a href="(https://%s/offre-emploi/(\d+)/[^"]*)"' % re.escape(HOST))
CARD_TITLE_RE = re.compile(r"<h6[^>]*>\s*<strong>(.*?)</strong>\s*</h6>", re.S)
CARD_EMPLOYER_RE = re.compile(r'<div class="text-muted small[^"]*"[^>]*>(.*?)</div>', re.S)
AD_ID_RE = re.compile(r"/offre-emploi/(\d+)/")
AD_TITLE_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
# the employer is the paragraph that FOLLOWS the title: there is no <h1> and no class to key on
AD_EMPLOYER_RE = re.compile(r"</h3>\s*(?:</\w+>\s*)*<p>(.*?)</p>", re.S)
LEGEND_RE = re.compile(
    r"<legend>\s*<strong>\s*(.*?)\s*</strong>\s*</legend>(.*?)(?=<legend>|\Z)", re.S)
MONTHS = ("Janvier|F[ée]vrier|Mars|Avril|Mai|Juin|Juillet|Ao[ûu]t|"
          "Septembre|Octobre|Novembre|D[ée]cembre")
# re.I is load-bearing, not tidiness: advert 118 writes «16 octobre 2026» in lower case
# where 1 and 60 write «28 Septembre 2024», and the capitalised motif rendered ZERO on it
DATE_FR_RE = re.compile(r"\b(\d{1,2}\s+(?:%s)\s+\d{4})\b" % MONTHS, re.I)
DEADLINE_RE = re.compile(
    r"date limite|au plus tard|avant le|dernier d[ée]lai|cl[ôo]ture|date de cl", re.I)
# the three numbers this board prints that are NOT counts; named so none is ever a witness
TEMPLATE_NUMBERS = ("44554", "4500", "80 jobs")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[emploilenouvelliste] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=3.0)).wait()   # no Crawl-delay written; 3 s is ours
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>|</tr>|</h\d>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    """Contacts out, and the record says which kinds were there."""
    if not s:
        return None, []
    took = []
    if MAIL_RE.search(s):
        took.append("email")
        s = MAIL_RE.sub("[e-mail withheld]", s)
    out = PHONE_RE.sub("[telephone withheld]", s)
    if out != s:
        took.append("telephone")
    return (out.strip() or None), took


def deadline_of(prose):
    """The closing date as the advert's PROSE states it, with the phrase it was read from.

    Never a field: this board declares none. A date counts only when a deadline phrase
    stands within 120 characters before it, so a project's start date or a reference
    year does not become a closing date.
    """
    if not prose:
        return None, None
    for m in DATE_FR_RE.finditer(prose):
        before = prose[max(0, m.start() - 120):m.start()]
        p = DEADLINE_RE.search(before)
        if p:
            return m.group(1), p.group(0).lower()
    return None, None


def cards_of(markup):
    """The list page → [(id, fields)], in the order the page serves them (oldest first)."""
    out = []
    for block in CARD_RE.findall(STRIP_RE.sub("", B64_RE.sub(" ", markup or ""))):
        h = HREF_RE.search(block)
        if not h:
            continue
        t = CARD_TITLE_RE.search(block)
        e = CARD_EMPLOYER_RE.search(block)
        out.append((int(h.group(2)), {
            "url": htmlmod.unescape(h.group(1)),
            "title": text(t.group(1)) if t else None,
            "employer": text(e.group(1)) if e else None,
        }))
    return out


def record(ident, f, stamp, position):
    title, took_t = scrub(f.get("title"))
    employer, took_e = scrub(f.get("employer"))
    took = sorted(set(took_t + took_e))
    r = {
        "source": "emploilenouvelliste", "country": stamp,
        "ledger_id": f"emploilenouvelliste:{ident}", "id": str(ident),
        "title": title, "employer": employer,
        "url": f.get("url"),
        "list_position": position,   # the board's own order, oldest first
        "withheld_fields": took,
    }
    if withheld_a_contact(took):
        r["contacts_withheld"] = True
    return r


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    code, body = request(LIST)
    if code == 404:
        die(f"{LIST}: HTTP 404 — the list is gone", EXIT_GONE)
    if code != 200:
        die(f"{LIST}: HTTP {code}", EXIT_PARTIAL)
    found = cards_of(body)
    if not found:
        die(f"{LIST}: 200 without a single job card — the page changed; not an empty board",
            EXIT_PARTIAL)
    seen, rows = set(), []
    for position, (ident, f) in enumerate(found, start=1):
        if ident in seen:        # raw and distinct must be able to differ
            continue
        seen.add(ident)
        rows.append(record(ident, f, stamp, position))
    # newest first: the page serves oldest first, so without this `--limit` returns the
    # oldest adverts — all long closed — and the board reads as dead
    rows.sort(key=lambda r: int(r["id"]), reverse=True)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

    ids = sorted(seen)
    note(f"{th(len(found))} card(s) on the page, {th(len(rows))} distinct advert(s) emitted "
         f"newest first; the page serves them OLDEST first and `list_position` keeps its order.")
    note("the board states NO count. Its three numbers that look like one are template "
         "literals and none is a witness: «44554 résultat(s)» inside an HTML comment, "
         "«Plus de 4500 offres» on the root, and «80 jobs» printed identically on three "
         "different employers' tiles.")
    if ids and ids[0] == 1 and ids[-1] == len(ids):
        note(f"ids run 1 to {th(ids[-1])} with no gap and {th(len(ids))} adverts were read: "
             f"the extraction is COMPLETE. This witness is OUR OWN, not a count the board "
             f"states — it certifies by its presence and says nothing by its absence.")
    else:
        gaps = sorted(set(range(ids[0], ids[-1] + 1)) - seen) if ids else []
        note(f"ids run {ids[0] if ids else '-'} to {ids[-1] if ids else '-'} and "
             f"{th(len(gaps))} are missing{': ' + ', '.join(str(g) for g in gaps[:20]) if gaps else ''}. "
             f"**This does NOT say the parse failed**: a deleted advert leaves the same gap, "
             f"and nothing here separates the two. The contiguity witness certifies only when "
             f"it holds.")
    note("the board carries no date and no location on this list, and no record pretends "
         "otherwise: what is open is not a question it answers. `ad` reads the closing date "
         "from the advert's prose when the advert states one.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the list states no country.")


def cmd_ad(a):
    url = a.url.strip()
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST or not AD_ID_RE.search(parts.path):
        die(f"--url {url}: a https://{HOST}/offre-emploi/<id>/<slug> advert")
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the advert is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    b64 = len(B64_RE.findall(body))
    clean = COMMENT_RE.sub(" ", STRIP_RE.sub("", B64_RE.sub("[image]", body)))
    t = AD_TITLE_RE.search(clean)
    # the blocks are read from the advert's OWN container, never from the whole page
    start = BODY_RE.search(clean)
    if start:
        stop = ASIDE_RE.search(clean, start.end())
        region = clean[start.end():stop.start()] if stop else clean[start.end():]
    else:
        region = clean
    legends = LEGEND_RE.findall(region)
    if not t or not legends:
        die(f"{url}: 200 without the advert's title or any of its blocks — the page changed",
            EXIT_PARTIAL)
    e = AD_EMPLOYER_RE.search(clean)
    took = []
    title, tk = scrub(text(t.group(1)))
    took += tk
    employer, tk = scrub(text(e.group(1))) if e else (None, [])
    took += tk
    blocks, prose = {}, []
    for label, markup in legends:
        key = re.sub(r"[^a-z]+", "_", (text(label) or "").lower()).strip("_")
        value = text(markup)
        if value and not FILLED_RE.search(value):
            value = None          # a bare full stop is an EMPTY section, not a value
        if value:
            prose.append(value)
        value, tk = scrub(value)
        took += tk
        blocks[key] = value
    # the deadline is read from the prose BEFORE scrubbing: an address withheld in the
    # middle of the submission guideline must not move the date out of the phrase's reach
    deadline, basis = deadline_of("\n".join(prose))
    r = {
        "source": "emploilenouvelliste",
        "country": a.country_code.upper() if a.country_code else None,
        "ledger_id": f"emploilenouvelliste:{AD_ID_RE.search(parts.path).group(1)}",
        "id": AD_ID_RE.search(parts.path).group(1),
        "title": title, "employer": employer, "url": url,
        "deadline_stated_in_prose": deadline,
        "deadline_basis": basis,
    }
    r.update(blocks)
    r["withheld_fields"] = sorted(set(took))
    if withheld_a_contact(sorted(set(took))):
        r["contacts_withheld"] = True
    print(json.dumps(r, ensure_ascii=False))
    filled = sorted(k for k, v in blocks.items() if v)
    note(f"{th(len(legends))} live block(s), {th(len(filled))} filled: "
         f"{', '.join(filled) or 'none'}. A fifth heading, «Lieu de dépôt des candidatures», "
         f"is commented out on every advert and is not read; an empty section is written as a "
         f"bare full stop and is emitted as null, never as a full stop.")
    if b64:
        note(f"{th(b64)} inline base64 image(s) replaced before reading — six adverts of the "
             f"thirteen measured embed them, one of them 54 % of its own bytes.")
    if deadline:
        note(f"closing date «{deadline}» read from the advert's PROSE, after «{basis}» — "
             f"prose-derived, not a field: this board declares none.")
    else:
        note("this advert states no closing date in its prose, and the board declares none "
             "as a field — so nothing here says whether it is open. One of the thirteen "
             "measured was in this state.")
    if not r["withheld_fields"]:
        note("nothing was scrubbed from this advert; `withheld_fields` is empty because it "
             "carried no contact, not because none was looked for.")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Le Nouvelliste — Emploi (Haiti): the daily's board, its whole history on one "
                    "page, read against a contiguity witness of our own. Issue #777.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the list — ONE page, every advert the site has published")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on every record (the list states none)")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert, its five blocks, and its prose closing date")
    d.add_argument("--url", required=True, help="the advert's own address")
    d.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on the record")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
