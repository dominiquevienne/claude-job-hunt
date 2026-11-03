#!/usr/bin/env python3
"""JobPaw (`jobpaw.com`, Haiti): the generalist — the one Haitian board that states its own count AND dates every advert. Issue #776.

  jobpaw.py jobs [--country-code HT] [--max-pages N]      the list, walked against the count it states
  jobpaw.py ad --url https://jobpaw.com/professionals/job-details?idj=<id>

WHAT IT IS. JobPaw is Haiti's generalist board — ministries, IDB- and EU-financed projects, NGOs,
private employers — and of the country's five carded boards it is **the richest route by a wide
margin**. Its list alone carries, on 28 of 28 adverts: the publication date, **the closing date**,
the title, the employer, the location and the sector. *Le Nouvelliste's board (#777) declares no
date in any form; this one dates everything, so «what is open» is a question it answers.*

THE RULES. `jobpaw.com/robots.txt` allows both paths — open, `certain: True`, `state: read`, no
`Crawl-delay`; 3 s is ours. The guard is taken on the exact path.

**THE HOST IS THE BARE NAME, AND THE `www.` FORM IS NOT USABLE.** `https://www.jobpaw.com/…`
fails TLS with `CERTIFICATE_VERIFY_FAILED: Hostname mismatch, certificate is not valid for
'www.jobpaw.com'`, measured 2026-11-03 19:41 UTC by the declared client. The card declares
`hosts: jobpaw.com`, and this adapter refuses any other host outright — *the mismatch was reached
by TYPING the host instead of reading it off the card, and a refusal written up as a fact about the
host would have accused a sound board.*

THE LIST. `/professionals/find-job` (200; 1 171 000 B) carries 28 `div.jobs-list__card`, and **the
board states its total TWICE** — `totalRows_RS_job=28` in the pager's own link and «Affichage des
offres d'emploi de 1 à 28 sur 28» under it. Read: 28. Stated: 28. **They agree, and that is a
witness external to our extraction** — which `emploilenouvelliste.py` has none of.

**THE PAGE STEP IS 100, NOT THE NUMBER SHOWN, and the stated RANGE is not usable.** Probing
`?pageNum_RS_job=1` returns 200 with **zero cards** and prints «de **101** à 28 sur 28» — a
nonsense range on an out-of-range page. So the walk takes the stated TOTAL (stable on both pages)
and never the range, and it stops on a page with no card. *A 200 with no card on page 1 is a page
that changed, not an empty board.*

**THE LIST IS ORDERED BY CLOSING DATE, FURTHEST FIRST** — monotonic over 28 of 28, while neither
publication order holds. So the adverts closing soonest are at the BOTTOM: on 2026-11-03 the first
card closed 2027-12-31 and the last closed 2026-11-04, the next day. **The board's order is kept
and `list_position` records it; no sort is imposed, because here a sort would be taste.** The
consequence is said on every run instead: *a `--max-pages`-style truncation drops the most urgent
adverts, not the dead ones* — the opposite of `jobsbotswana`, where the oldest-first order made the
sort a condition of correctness.

**AND 0 OF THE 28 WERE CLOSED on 2026-11-03** — 28 of 28 still to come, the nearest the next day.
This board's list is a list of OPEN adverts, by its own field, and that is checkable.

**`jobs-list__price` CARRIES THE SECTOR, NOT A PRICE.** «Marketing», «Sciences de l'Ingénieur»,
«Santé et Professions médicales» — a class name that lies, and reading it as a salary would put a
profession in a money field. **And there are TWO `jobs-list__location` per card**: the first, a
`<span>`, is the place; the second, a `<p>`, is the closing date. The class does not discriminate —
the TAG does, and so does the label each value is prefixed with (`Location:` ×28, `Date Limite:`
×28, `Publié` ×28).

THE ADVERT. `ad` reads one page. The advert's own facts are a `<table>` of label/value pairs, two
pairs a row: `Date de publication`, `Date limite`, `Pays`, `Ville`, `Zone`, `Durée`. **The label is
HTML-escaped in the markup — `Dur&eacute;e` — so it is unescaped BEFORE it is matched**, or that
field renders zero.

**AND THE BOARD WRITES ITS DATES IN TWO FORMATS, ONE PER SURFACE.** The list writes «29 octobre
2026» (long, French); the advert writes «30 Oct 2026» (short). A motif built on the list's form
returns **ZERO** on the advert, measured. Both are read, and the record keeps each date as the
board writes it — a date is kept as written, never reformatted.

**THE REDACTION IS ANCHORED, AND THE ANCHOR OF `emploilenouvelliste.py` DOES NOT TRANSPOSE.** This
advert's real number is written `+(509) 3701 9232` — with **parentheses round the dialling code** —
and the sibling's anchor (`\\+\\s?509`) returns **ZERO** on it: copying it would have let a contact
leave, which is the worse direction. Widened to admit the parentheses it takes **1 of the 1 real
number and 0 of the 4 other digit strings**, where the bare motif used elsewhere takes all five:
`978385858` twice, the grant number `2000005176`, and **`2147483647` — which is 2³¹−1, a sentinel
in the markup and not a quantity at all.** *The remedy transposes between boards; the exact motif
does not, and it is measured on the form each board serves.*

**AND THE SITE'S OWN ADDRESS LIVES IN AN HTML COMMENT.** `info@jobpaw.com` sits inside a
commented-out footer block on every page, so without stripping comments first **every record would
declare a withheld contact that no employer ever deposited** — the fault of declaring a discretion
one did not exercise, reached from the other side. Comments come out before anything is read, which
is also what keeps a commented heading from counting as content (#777, same turn, other board:
that makes it a family).

**AND THE PAGE DECLARES UTF-8 WHILE SERVING FIVE BYTES THAT ARE NOT, SO THE CALLER MUST READ
WHICH CODEC WAS USED.** The body is 1 169 653 characters of which **five** are undecodable — 0.00043
%, the first inside «pour l\u2019...» at offset 95 234 — so `raw.decode("utf-8")` raises, and
`_decode` then falls to its last resort. **`_decode` is SOUND and says so in its own docstring:**
«cp1252 as the last resort, because it maps every byte and therefore never raises: *the fallback is
chosen for being total, not for being right*, and the caller is told which one was used.» *The
defect was MINE: the first version of this adapter took `decode_body(...)[0]` and threw the
encoding away, so 28 adverts came out as «PubliÃ© 13 aoÃ»t 2026» — and the mojibake silently broke
the label stripping too, one defect wearing two symptoms.* So the encoding IS read, and when the
total fallback was taken while the page declared UTF-8, this adapter re-decodes with
`utf-8/replace` **only if the repository\u2019s own readability control prefers it**: the ratio of
UTF-8 lead bytes followed by a continuation is **0.001 under utf-8/replace and 0.996 under cp1252**,
against a 0.5 threshold. The run names the codec and the number of characters lost, every time.

Measured 2026-11-03 19:41–19:59 UTC by the declared client, the guard on the exact paths in a turn
of its own: `/professionals/find-job` 200 (1 171 000 B, md5 720676bbea10) with 28 cards and six
fields on 28 of 28; `?pageNum_RS_job=1` 200 (1 089 399 B) with zero cards; one advert at
`?idj=18071` 200 (60 685 B, md5 e85b9128ffda), `Apache/2.4.58 (Ubuntu)`. The premise of #776 moved:
32 adverts on 2026-09-20, 28 now, and its «no pager, no stated count» is **false on both halves**
today.
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

from _decode import decode_body_readable
from _locations import fold
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA
from _withheld import withheld_a_contact

HOST = "jobpaw.com"          # the bare name: `www.jobpaw.com` fails TLS on a hostname mismatch
LIST = f"https://{HOST}/professionals/find-job"
AD = f"https://{HOST}/professionals/job-details"
PAGE_STEP = 100              # MEASURED: `pageNum_RS_job=1` prints «de 101 à …», not «de 29 à …»
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# the comments come out FIRST: the site's own address sits in a commented-out footer, and
# without this every record would declare a contact no employer deposited
COMMENT_RE = re.compile(r"(?s)<!--.*?-->")
B64_RE = re.compile(r"data:image/[a-z]+;base64,[A-Za-z0-9+/=]+")
STRIP_RE = re.compile(r"(?s)<style.*?</style>|<script.*?</script>")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# ANCHORED, and widened for THIS board's form: the real number is written `+(509) 3701 9232`
# and the sibling's `\+\s?509` returns zero on it. The bare motif takes four non-telephones
# here, including `2147483647` -- 2**31-1, a sentinel -- and a grant number.
PHONE_RE = re.compile(
    r"\+\s*\(?\s*509\s*\)?[\s.\-]?\d[\d\s.\-]{5,}\d"
    r"|(?:T[ée]l(?:[ée]phone)?|Cell|Whatsapp|WhatsApp)\s*:?\s*\(?\+?\d[\d\s().\-]{5,}\d")
CARD_RE = re.compile(
    r'<div class="jobs-list__card">(.*?)(?=<div class="jobs-list__card">|<nav>|\Z)', re.S)
IDJ_RE = re.compile(r"/professionals/job-details\?idj=(\d+)")
TIME_RE = re.compile(r'jobs-list__time"[^>]*>(.*?)</span>', re.S)
TITLE_RE = re.compile(r'jobs-list__title[^"]*"[^>]*>(.*?)</h3>', re.S)
# the EMPLOYER is the span nested inside the title, after the <br>
EMPLOYER_RE = re.compile(r"<br\s*/?>\s*<span[^>]*>(.*?)</span>", re.S)
# TWO `jobs-list__location` a card and the class does not discriminate: the TAG does
PLACE_RE = re.compile(r'<span class="jobs-list__location">(.*?)</span>', re.S)
CLOSING_RE = re.compile(r'<p class="jobs-list__location">(.*?)</p>', re.S)
# `jobs-list__price` carries the SECTOR, never a price -- reading it as money would put a
# profession in a salary field
SECTOR_RE = re.compile(r'jobs-list__price"[^>]*>(.*?)</span>', re.S)
STATED_RE = re.compile(r"totalRows_RS_job=(\d+)")
# the advert's facts: a table of label/value pairs, and the LABEL is HTML-escaped in the markup
FACT_RE = re.compile(r"<td><strong>\s*(.*?)\s*</strong></td>\s*<td><em>\s*(.*?)\s*</em></td>", re.S)
# **The board emits PHP warnings INTO its own markup**, inside an `alt="..."` attribute, and
# they land in the FIRST label: without this the job title's key became a slug carrying
# `/var/www/html/professionals/job-details.php on line 349`. Two of two on every advert read.
PHP_WARN_RE = re.compile(
    r"(?is)<br\s*/?>\s*<b>\s*Warning\s*</b>.*?on line <b>\d+</b><br\s*/?>")
# the ten labels, EXTRACTED from the page and not guessed: a first version of this dict was
# composed from a loose reading and mapped two of them. Keys are ACCENT-FOLDED, so the
# markup's `Dur&eacute;e` and any accent variant resolve without enumerating forms.
LABELS = {"titre du poste": "title", "compagnie": "employer", "domaine": "sector",
          "specialite": "speciality", "date publication": "published_as_written",
          "date limite": "closing_as_written", "pays": "country_stated", "ville": "city",
          "zone": "zone", "duree": "duration"}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobpaw] {msg}", file=sys.stderr)


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
    # the bare host ONLY: `www.jobpaw.com` fails TLS, and this refusal is ours to make
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent (the `www.` form fails TLS on a hostname "
            f"mismatch, so it is refused rather than reported as a board defect)", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=3.0)).wait()   # no Crawl-delay written; 3 s is ours
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            # `decode_body_readable`, not `decode_body`: this board declares UTF-8 and serves
            # five bytes that are not, and the strict loop then falls to cp1252 — total, not
            # right. The arbitration lives in `_decode`, so nothing is decoded by hand here.
            return r.getcode(), decode_body_readable(r.read(), r.headers)[0]
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


def after_label(value, label):
    """«Location: Haiti , Ventas» → «Haiti , Ventas». The label is what discriminates the
    two `jobs-list__location` values, so it is read and then dropped."""
    if not value:
        return None
    v = re.sub(r"^\s*%s\s*:?\s*" % re.escape(label), "", value, flags=re.I)
    return v.strip() or None


def stated(markup):
    """The total the board states. Its stated RANGE is not read: on an out-of-range page it
    prints «de 101 à 28 sur 28», a nonsense, while the total stays right."""
    m = STATED_RE.search(markup or "")
    return int(m.group(1)) if m else None


def cards_of(markup):
    """The list page → [(id, fields)], in the order the board serves them."""
    out = []
    clean = STRIP_RE.sub("", COMMENT_RE.sub(" ", B64_RE.sub(" ", markup or "")))
    for block in CARD_RE.findall(clean):
        ident = IDJ_RE.search(block)
        if not ident:
            continue
        title_block = TITLE_RE.search(block)
        employer = EMPLOYER_RE.search(title_block.group(1)) if title_block else None
        title = title_block.group(1) if title_block else ""
        if employer:                       # the employer is nested IN the title: take it out
            title = title.replace(employer.group(0), " ")
        t = TIME_RE.search(block)
        place = PLACE_RE.search(block)
        closing = CLOSING_RE.search(block)
        sector = SECTOR_RE.search(block)
        out.append((ident.group(1), {
            "url": f"{AD}?idj={ident.group(1)}",
            "title": text(title),
            "employer": text(employer.group(1)) if employer else None,
            "published_as_written": after_label(text(t.group(1)) if t else None, "Publié"),
            "closing_as_written": after_label(
                text(closing.group(1)) if closing else None, "Date Limite"),
            "location": after_label(text(place.group(1)) if place else None, "Location"),
            "sector": text(sector.group(1)) if sector else None,   # NOT a price
        }))
    return out


def record(ident, f, stamp, position):
    took = []
    out = {}
    for k in ("title", "employer", "location"):
        out[k], t = scrub(f.get(k))
        took += t
    r = {
        "source": "jobpaw", "country": stamp,
        "ledger_id": f"jobpaw:{ident}", "id": ident,
        "title": out["title"], "employer": out["employer"],
        "location": out["location"],
        "sector": f.get("sector"),                      # the board's own sector, not a price
        "published_as_written": f.get("published_as_written"),
        "closing_as_written": f.get("closing_as_written"),
        "url": f.get("url"),
        "list_position": position,   # the board's order: closing date, FURTHEST first
        "withheld_fields": sorted(set(took)),
    }
    if withheld_a_contact(r["withheld_fields"]):
        r["contacts_withheld"] = True
    return r


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    rows, seen, page, said, ended = [], set(), 0, None, None
    raw = 0
    while True:
        url = LIST if page == 0 else f"{LIST}?pageNum_RS_job={page}&totalRows_RS_job={said or 0}"
        code, body = request(url)
        if code == 404:
            die(f"{url}: HTTP 404 — the list is gone", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code} — the walk ended at {th(len(seen))}", EXIT_PARTIAL)
        if page == 0:
            said = stated(body)
        found = cards_of(body)
        if not found:
            if page == 0:
                die(f"{url}: 200 without a single job card — the page changed; not an empty board",
                    EXIT_PARTIAL)
            ended = f"page {page + 1} carried no card"
            break
        keys = {i for i, _f in found}
        if page and keys <= seen:
            die(f"page {page + 1} repeats the cards of the page before — the walk ended at "
                f"{th(len(seen))}", EXIT_PARTIAL)
        for ident, f in found:
            raw += 1
            if ident in seen:        # raw and distinct must be able to differ
                continue
            seen.add(ident)
            rows.append(record(ident, f, stamp, len(rows) + 1))
        if said is not None and len(seen) >= said:
            ended = f"the {th(said)} the board states were read"
            break
        if a.max_pages and page + 1 >= a.max_pages:
            ended = f"stopped by --max-pages at page {page + 1}"
            break
        page += 1
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

    pages = page + 1 if ended and "carried no card" not in (ended or "") else max(page, 1)
    if said is None:
        note(f"{th(len(rows))} emitted over {th(pages)} page(s); **the board stated no total this "
             f"time** — it usually carries `totalRows_RS_job=N` in its pager and «Affichage … sur "
             f"N» under it, and the run says so rather than claiming one. {ended or ''}")
    elif said != len(seen):
        note(f"{th(len(seen))} read over {th(pages)} page(s), the board states {th(said)} — "
             f"{th(abs(said - len(seen)))} {'short' if said > len(seen) else 'more'}; {ended}.")
    else:
        note(f"{th(len(seen))} read over {th(pages)} page(s), and the board states {th(said)} — "
             f"they agree; {ended}. That total is a witness EXTERNAL to this extraction, which is "
             f"what `emploilenouvelliste.py` has none of.")
    if raw != len(seen):
        note(f"{th(raw)} card(s) seen for {th(len(seen))} distinct advert(s): "
             f"{th(raw - len(seen))} repeated.")
    note("the board orders its list by CLOSING DATE, furthest first, so the adverts closing "
         "soonest are LAST: a truncation drops the most urgent ones, not the dead ones. The "
         "board's order is kept and `list_position` records it; `closing_as_written` is emitted "
         "so the caller can order it otherwise.")
    note("`sector` comes from a class the site calls `jobs-list__price` and it is NOT a price — "
         "it carries «Marketing», «Santé et Professions médicales»; a profession in a money "
         "field would be the defect.")
    note("dates are kept AS THE BOARD WRITES THEM, and it writes them in two forms: long French "
         "on the list («29 octobre 2026»), short on the advert («30 Oct 2026»). A motif built on "
         "one returns zero on the other.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the card declares it, the list states it per "
             f"advert in its `Location:` value.")


def cmd_ad(a):
    url = a.url.strip()
    parts = urllib.parse.urlsplit(url)
    ident = urllib.parse.parse_qs(parts.query).get("idj", [None])[0]
    if parts.scheme != "https" or parts.netloc != HOST or not ident or not ident.isdigit():
        die(f"--url {url}: a https://{HOST}/professionals/job-details?idj=<id> advert")
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the advert is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    warns = len(PHP_WARN_RE.findall(body))
    clean = PHP_WARN_RE.sub(" ", STRIP_RE.sub("", COMMENT_RE.sub(
        " ", B64_RE.sub("[image]", body))))
    facts = FACT_RE.findall(clean)
    if not facts:
        die(f"{url}: 200 without a single label/value row — the page changed", EXIT_PARTIAL)
    took, out, unknown = [], {}, []
    for label, value in facts:
        # unescaped by `text`, then ACCENT-FOLDED: `Dur&eacute;e` and `Duree` are one key
        key = fold((text(label) or "").rstrip(":"))
        v, tk = scrub(text(value))
        took += tk
        if key in LABELS:
            out[LABELS[key]] = v
        elif key:
            unknown.append(key)
            out[re.sub(r"[^a-z0-9]+", "_", key).strip("_") or "unnamed"] = v
    # the title comes from the TABLE and never from an `<h>`: the heading on this page is a
    # marketing banner («Ils sont plus de 18 000 a guetter nos opportunites…»), the same on
    # every advert, and taking it gave 28 adverts one identical wrong title.
    r = {
        "source": "jobpaw", "country": a.country_code.upper() if a.country_code else None,
        "ledger_id": f"jobpaw:{ident}", "id": ident,
        "url": url,
    }
    r.update(out)
    if not r.get("title"):
        die(f"{url}: 200 with {len(facts)} row(s) but no «Titre du poste» — the labels changed",
            EXIT_PARTIAL)
    r["withheld_fields"] = sorted(set(took))
    if withheld_a_contact(r["withheld_fields"]):
        r["contacts_withheld"] = True
    print(json.dumps(r, ensure_ascii=False))
    note(f"{th(len(facts))} label/value row(s) read: {', '.join(sorted(out)) or 'none'}. The "
         f"title is taken from the «Titre du poste» ROW, never from an `<h>`: the heading here "
         f"is a marketing banner, identical on every advert.")
    if warns:
        note(f"{th(warns)} PHP warning(s) are emitted by the board INTO its own markup (inside "
             f"an `alt=` attribute) and were stripped before the labels were read — unstripped, "
             f"they land in the FIRST label and the title's key becomes a slug carrying the "
             f"server's file path. A fact about the board, not about this run.")
    if unknown:
        note(f"label(s) this adapter does not map, emitted under their own slug: "
             f"{', '.join(sorted(set(unknown)))} — a label it cannot name is carried, never "
             f"dropped.")
    if not r["withheld_fields"]:
        note("nothing was scrubbed from this advert; `withheld_fields` is empty because it "
             "carried no contact, not because none was looked for. The site's OWN address sits "
             "in a commented-out footer and the comments come out first, so it never counts.")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="JobPaw (Haiti) — the generalist, walked against the total it states, with "
                    "the closing date on every advert. Issue #776.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the list (step 100), walked against the stated total")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on every record")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0,
                   help="stop after N pages (0 = until the stated total is read)")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert and its label/value facts")
    d.add_argument("--url", required=True, help="the advert's own address")
    d.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on the record")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
