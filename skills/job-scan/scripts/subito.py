#!/usr/bin/env python3
"""Subito (`www.subito.it`, Italy) — the generalist classifieds board whose employment section has a SIBLING category where people offer THEMSELVES, and whose advertiser carries a named telephone on 8 of 42.

  subito.py totals
  subito.py list [--max N] [--page-size N] [--no-notes]

THE COUNT FOLLOWS THE QUERY, AND IT TOOK TWO SECTIONS TO ESTABLISH IT.

    /annunci-italia/vendita/offerte-lavoro/   total  42 306   pages 1 411   29,98/page
    /annunci-italia/vendita/informatica/      total 298 478   pages 9 950   30,00/page

*They differ, so `total` counts the SECTION interrogated and not the site — and a
single reading is consistent with both hypotheses, which is why the card refused
the attribution until a second section existed.* **The host's own two fields check
each other at 30 per page on both, an arithmetic that belongs to the HOST and not
to our extraction.** And the figure moves: 42 172, then 42 306 within a day, so it
is a reading with an hour and never the size of a board.

**THE SIBLING CATEGORY IS THE SAFETY QUESTION, AND IT IS THE KORGAR QUESTION
AGAIN.** `cerco-lavoro` — «I am looking for work» — appears **15 times** in the
employment section's own payload, and all fifteen are SEO cross-links to a
separate category: `/annunci-lombardia/vendita/cerco-lavoro/bergamo/`,
`/annunci-italia/vendita/cerco-lavoro/?q=badanti`. *Those are people offering
THEMSELVES.*

    les 42 annonces du jeu de resultats   42 sur 42 sous /offerte-lavoro/
    `cerco-lavoro`                        15 liens de categorie SOEUR, 0 resultat

**So this path is the offers sub-category and the walk never leaves it.**
`refuse_seekers()` is a refusal that can FIRE — *the host's rules forbid nothing
here, exactly as korgar's 105-byte file forbade nothing while exposing 34 894 CVs:
a host that forbids nothing has not consented to our taking everything it exposes,
and what decides is what the object CONTAINS.*

**AND THE PROSE CARRIES A STREET, BECAUSE PRIVATE INDIVIDUALS POST HERE.** One
body of the 42 held reads `Via Spluga 2` and two say «sono un privato», so an
address in an advert can be a home rather than business premises and the text does
not tell them apart. *The street is scrubbed and the advert survives — hours, pay
and task are what a candidate needs.* **`via` is also an Italian preposition**, so
the pattern was measured on the real corpus before being written: **4 prepositional
uses against 1 real street**, and the form excludes the known objects by name and
requires a capitalised street name — safe by construction, not by luck.

**THE ADVERTISER IS THE EXPURGATION PROBLEM, AND THE MEASUREMENT DECIDED IT —
counted over the 42 of page one, values never reproduced:**

    advertiser.phone     REMPLI sur 8 de 42      un champ dont le SENS est connu
    advertiser.userId    9 chiffres sur 42 de 42 un identifiant de PERSONNE
    advertiser.shopName  rempli sur 6            un nom de SOCIETE
    advertiser.name      rempli sur 17 — et TOUJOURS quand `shopName` manque (17/17),
                         1 a 4 mots, et **9 des 17 ne portent AUCUNE marque de societe**

**`phone` is DROPPED and `userId` is never emitted. And `name` is NOT emitted
either**, because on nine of seventeen it cannot be shown to be a company and may
be a private individual's: *the record says WHAT the advertiser is — company flag
and type — without naming someone who answered a classified advert.* `shopName`
travels, because a shop is a business by construction.

**AND THE DIGIT RULE TOUCHES ONLY THE PROSE, FOR A REASON THAT IS MEASURED HERE
AND NOT TRANSPORTED.** The advert identifier is **9 digits on 42 of 42**
(`663545106`) and `advertiser.userId` is **9 digits on 42 of 42**: an anchored
nine-digit telephone rule applied to the record would destroy BOTH. *That is the
Madrid lesson — the same rule, unanchored, destroyed an offer id on 314 of 314 —
and the Burmese one, where «nine digits» destroyed 113 salaries of 115.* **Here
the money field is checked instead of assumed: `features./price` carries `24000`,
`30000` and `8000`, five digits or four, so it does not cross the rule — measured
on this board.**

**AND IT IS NOT CALLED A SALARY, BECAUSE ITS UNIT IS NOT ESTABLISHED.** The host
labels it «Prezzo» — the generalist classifieds PRICE field — and the 8 000 sits
on an hourly cleaning post where 24 000 and 30 000 sit on full posts. *Annual,
monthly and a rate cannot be told apart on three readings, so the field is emitted
as `price_declared` with the host's own label and the reserve travels with it.
Calling it `salary_eur` would have published a unit nobody stated.*

THE ADVERT, 12 KEYS: `subject` (the title), `body` (957 characters of prose on the
one read), `date`, `advertiser`, `category`, `features` (`/contract_type`,
`/degree`, `/job_category`, `/price`, `/work_hour`, `/work_level`), `geo` (`city`,
`town`, `region`, `label`, `uri` — **town level, no street and no postcode**),
`images`, `kind`, `type`, `urls`, `urn`. *`urn` reads `id:ad:<uuid>:list:<id>`, so
the numeric id appears in both the urn and the URL and is the ledger key.*

**THE PAYLOAD IS READ BY BALANCED BRACES ANCHORED ON `"urn"`, NOT BY CHUNK
SPLITTING** — 42 of 42 parsed on the body held. *So the `self.__next_f` hazard
that put a chunk of 1 259 declared characters at 77 434 read does not arise here;
the adapter COUNTS its parse failures rather than skipping them silently, because
an object that will not parse is a gap and not an absence.*

Guard taken on both host forms and on each exact path in a turn distinct from
every retrieval: rules READ (`state: read`), nothing refuses our paths,
`claude-user` over ordinary HTTP. No `Crawl-delay` is written, so our own floor
applies. Measured 2026-10-06 (card) and 2026-10-07 (this adapter), #1061.
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
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "www.subito.it"
SECTION = "/annunci-italia/vendita/offerte-lavoro/"
BASE = "https://www.subito.it"

# The sibling category where people offer THEMSELVES. Never fetched.
SEEKERS = "cerco-lavoro"

# A field whose MEANING is known is DROPPED, not scrubbed.
DROPPED = ("phone",)
# A personal identifier: nine digits on 42 of 42, and never emitted.
NEVER = ("userId",)

# Prose. The digit rule runs HERE and nowhere else, because the advert id and
# `userId` are both nine digits on 42 of 42.
MAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TEL_RE = re.compile(r"(?:\+\s?39[\s\-.()]*)?(?<!\d)3\d{2}[\s\-.]?\d{3}[\s\-.]?\d{3,4}(?!\d)"
                    r"|\+\s?39[\s\-.()\d]{6,}")
MSG_RE = re.compile(r"(?i)\b(?:whats?app|telegram|viber)\b[\s:：]*[+\d@][\w\d\s\-.()@]{3,}")

# **A STREET IN THE PROSE, because this board carries private advertisers.** One
# body of the 42 held reads `Via Spluga 2`, and another says «sono un privato» — so
# an address in an advert here can be a home and not business premises, and the two
# are not distinguishable from the text. *The street goes and the advert survives:
# the hours, the pay and the task are what the candidate needs.*
#
# **AND `via` IS ALSO AN ITALIAN PREPOSITION** — «inviare il CV via email entro il
# 15» — so a pattern of «via + words + number» destroys legitimate text. Measured
# on the real corpus: **4 prepositional uses** (`VIA MAIL`, `via email`, `via
# whatsapp`, `via email`) against **1 real street**. The form below excludes the
# known prepositional objects BY NAME and requires the street name to be
# capitalised, so it is safe by construction rather than by luck — *its cost is to
# MISS a street, never to fabricate one.*
_PREP = r"(?i:e-?mail|mail|pec|posta|whats?app|telegram|telefono|tel|fax|sms|web|sito|link|raccomandata)"
RUE_RE = re.compile(r"\b(?:Via|Viale|V\.le|Piazza|P\.zza|Corso|C\.so|Largo|Strada|Vicolo)\s+"
                    r"(?!" + _PREP + r"\b)[A-ZÀ-Þ][A-Za-zÀ-ÿ'’\.\- ]{1,38}?[, ]\s*\d{1,4}\b")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[subito] {msg}", file=sys.stderr)


def refuse_seekers(url):
    """`cerco-lavoro` is where people offer THEMSELVES. **The host's rules forbid
    nothing here — and a host that forbids nothing has not consented to our taking
    everything it exposes.** *This is korgar's 105-byte file all over again: what
    decides is what the object CONTAINS, and the path filter is a SAFETY condition
    rather than an optimisation.*"""
    if SEEKERS in urllib.parse.urlsplit(url).path.lower():
        die(f"{url}: `{SEEKERS}` is the sibling category where PEOPLE offer "
            f"themselves, not where employers post. **Nothing in this host's rules "
            f"forbids it, and that is not a permission** — walking it would put "
            f"individuals' own postings into a jobs ledger. Refused.", EXIT_REFUSED)
    return None


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # the host writes no Crawl-delay — our own floor


def get(url):
    refuse_seekers(url)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html", "Accept-Language": "it,en;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            if (r.headers.get("Content-Encoding") or "").lower() in ("gzip", "x-gzip") \
                    or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def adverts(body):
    """Every advert object, by BALANCED BRACES anchored on `"urn"`.

    **Returns `(objects, failures)` — a failure is a GAP and not an absence**, so
    the caller can print a count that does not come from its own extraction. *42
    of 42 parsed on the body held when this was written; an object that stops
    parsing tomorrow must be visible rather than skipped.*
    """
    out, rates = [], 0
    for m in re.finditer(r'"urn"\s*:\s*"id:ad:', body):
        deb = body.rfind("{", 0, m.start())
        if deb < 0:
            rates += 1
            continue
        prof, j = 0, deb
        while j < len(body):
            if body[j] == "{":
                prof += 1
            elif body[j] == "}":
                prof -= 1
                if prof == 0:
                    break
            j += 1
        try:
            out.append(json.loads(body[deb:j + 1]))
        except ValueError:
            rates += 1
    return out, rates


def stated(body):
    """`total` and `totalPages` as the HOST states them for THIS query. *They sit
    together in the payload, which is what makes the pair a statement about the
    query just answered rather than about the site.*"""
    d = {}
    for m in re.finditer(r'"(total|totalPages)"\s*:\s*(\d+)', body):
        d.setdefault(m.group(1), int(m.group(2)))
    return d.get("total"), d.get("totalPages")


def held(v):
    """A POSITIVE floor. *A string is a value only if it passes a test, never
    because it is missing from a list of refusals — `"$undefined"` walks under a
    list that knows `undefined`.*"""
    if v is None or isinstance(v, bool):
        return False
    if isinstance(v, str):
        t = v.strip()
        return bool(t) and not t.startswith("$") and t.lower() not in (
            "undefined", "null", "none", "n/a", "-")
    return bool(v) or isinstance(v, (int, float))


def text(s):
    if not isinstance(s, str):
        return None
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</p>|</li>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    out = "\n".join(" ".join(l.split()) for l in
                    htmlmod.unescape(s).splitlines() if l.strip()).strip()
    return out or None


def scrub(s):
    """The prose with its contacts replaced. **This runs on `body` ONLY.** *The
    advert id and `userId` are nine digits on 42 of 42, so a digit rule let loose
    on the record would destroy both — the Madrid defect, where the same rule
    unanchored destroyed an offer id on 314 of 314.*"""
    if not isinstance(s, str) or not s.strip():
        return None, []
    found = []
    if MAIL_RE.search(s):
        found.append("body:e-mail")
    if MSG_RE.search(s):
        found.append("body:messaging")
    if TEL_RE.search(s):
        found.append("body:telephone")
    if RUE_RE.search(s):
        found.append("body:street")
    s = MAIL_RE.sub("[e-mail withheld]", s)
    s = MSG_RE.sub("[messaging contact withheld]", s)
    s = TEL_RE.sub("[telephone withheld]", s)
    s = RUE_RE.sub("[street withheld]", s)
    return text(s), found


def place(geo):
    """Town, city and region — **and nothing else**, by a positive floor. *`geo`
    carries `uri` and `label` too; a key the host adds tomorrow cannot arrive by
    default.*"""
    if not isinstance(geo, dict):
        return None
    out = {}
    for src, dst in (("town", "town"), ("city", "city"), ("region", "region")):
        v = geo.get(src)
        if isinstance(v, dict):
            v = v.get("value") or v.get("shortName") or v.get("friendlyName")
        if held(v) and isinstance(v, str):
            out[dst] = v.strip()
    return out or None


def feature(features, uri):
    """One `features` entry by its `uri`, returning the structured value. *The
    salary is read from `values[].key` and never parsed out of prose.*"""
    f = (features or {}).get(uri) if isinstance(features, dict) else None
    if not isinstance(f, dict):
        return None
    vals = f.get("values")
    if isinstance(vals, list) and vals and isinstance(vals[0], dict):
        k = vals[0].get("key")
        return k if held(k) else None
    return None


def advertiser(adv):
    """What the advertiser IS, without naming someone who may be an individual.

    **`phone` is DROPPED** — a field whose meaning is known. **`userId` is never
    emitted** — nine digits on 42 of 42, a person's identifier. **And `name` is
    not emitted either**: filled on 17 of 42 and ALWAYS when `shopName` is absent,
    one to four words, and *nine of the seventeen carry no company marker at all*,
    so it cannot be shown to be a business. `shopName` travels, because a shop is
    one by construction.

    Returns `(fields, withheld)` — and the withheld set is DERIVED from what was
    actually FILLED, never from a key being present. *A `withheld_fields` naming
    what nobody deposited lies about OUR discretion rather than about the board.*
    """
    adv = adv if isinstance(adv, dict) else {}
    out, withheld = {}, []
    shop = adv.get("shopName")
    if held(shop) and isinstance(shop, str):
        out["employer"] = shop.strip()
    elif held(adv.get("name")):
        # A name is there and is NOT reproduced; the record says so instead.
        withheld.append("advertiser:name")
    if held(adv.get("phone")):
        withheld.append("advertiser:phone")
    if isinstance(adv.get("company"), bool):
        out["advertiser_is_company"] = adv["company"]
    if isinstance(adv.get("type"), int):
        out["advertiser_type"] = adv["type"]
    return out, withheld


def record(ad):
    urn = ad.get("urn") or ""
    ident = urn.rsplit(":", 1)[-1] if ":" in urn else None
    uuid = None
    m = re.match(r"id:ad:([0-9a-f-]{36}):", urn)
    if m:
        uuid = m.group(1)
    url = ((ad.get("urls") or {}).get("default")
           if isinstance(ad.get("urls"), dict) else None)
    body, withheld = scrub(ad.get("body"))
    champs, w2 = advertiser(ad.get("advertiser"))
    out = {
        "source": "subito", "country": "IT",
        "ledger_id": f"subito:{ident}" if held(ident) else None,
        "id": ident if held(ident) else None,
        "uuid": uuid,
        "url": url if held(url) else None,
        "title": text(ad.get("subject")),
        "place": place(ad.get("geo")),
        "posted": ad.get("date") if held(ad.get("date")) else None,
        "contract": feature(ad.get("features"), "/contract_type"),
        "work_hour": feature(ad.get("features"), "/work_hour"),
        "work_level": feature(ad.get("features"), "/work_level"),
        "job_category": feature(ad.get("features"), "/job_category"),
        # **NOT called a salary, because the UNIT is not established.** The host
        # labels this field «Prezzo» — a generalist classifieds PRICE — and the
        # three read carry 24000, 30000 and 8000, the last on an hourly cleaning
        # post. *Annual, monthly or a rate cannot be told apart from three, so the
        # name says what the host says and the reserve travels with it.* Read from
        # the STRUCTURED value, never parsed out of the prose.
        "price_declared": feature(ad.get("features"), "/price"),
        "description": body,
    }
    out.update(champs)
    tout = sorted(set(withheld) | set(w2))
    if tout:
        out["withheld_fields"] = tout
    return out


def th(n):
    return f"{n:,}".replace(",", " ") if isinstance(n, int) else "?"


def cmd_totals(a):
    code, body = get(BASE + SECTION)
    if code != 200:
        die(f"{BASE + SECTION}: HTTP {code}", EXIT_PARTIAL)
    total, pages = stated(body)
    ads, rates = adverts(body)
    print(json.dumps({"source": "subito", "country": "IT", "section": SECTION,
                      "stated_total": total, "stated_pages": pages,
                      "adverts_on_page_one": len(ads)}, ensure_ascii=False))
    note(f"the host states {th(total)} for THIS SECTION and {th(pages)} pages; "
         f"{len(ads)} advert objects parsed on page one"
         + (f", {rates} that would not parse and are counted as GAPS" if rates else "")
         + ".")
    if total and pages:
        note(f"its own two fields check each other at {total / pages:.2f} per page — "
             f"**an arithmetic that belongs to the HOST and not to our extraction.** "
             f"*`total` was established to follow the QUERY by reading a SECOND "
             f"section (`informatica`, 298 478 over 9 950), which a single reading "
             f"could never have shown.*")
    note("**the figure MOVES**: 42 172, then 42 306 within a day — a reading with an "
         "hour, never the size of a board. *And it is not established that all of "
         "them are job OFFERS rather than including seekers' own postings; what IS "
         f"established is that the 42 of page one are 42 of 42 under `{SECTION}` and "
         f"that `{SEEKERS}` is a SIBLING category this adapter refuses.*")


def cmd_list(a):
    per = 30
    vus, page, total, rates, pages = 0, 1, None, 0, None
    limite = a.max if a.max else None
    while True:
        url = BASE + SECTION + (f"?o={page}" if page > 1 else "")
        code, body = get(url)
        if code != 200:
            note(f"page {page}: HTTP {code} — the walk was CUT BY THE TRANSPORT here, "
                 f"which is not the same as the board being this size.")
            break
        if total is None:
            total, pages = stated(body)
        lot, r = adverts(body)
        rates += r
        if not lot:
            note(f"page {page}: no advert object parsed — the walk ENDED HERE.")
            break
        for ad in lot:
            rec = record(ad)
            if not rec["ledger_id"]:
                rates += 1
                continue
            print(json.dumps(rec, ensure_ascii=False))
            vus += 1
            if limite and vus >= limite:
                break
        if limite and vus >= limite:
            break
        page += 1
    note(f"{th(vus)} advertisement(s) emitted over {page} page(s); the host states "
         f"{th(total)} for this section over {th(pages)} pages — "
         + ("capped by --max" if limite and vus >= limite else
            "the walk ended on its own") + ".")
    if rates:
        note(f"{rates} object(s) would not parse or carried no id: counted as GAPS, "
             f"not as absent.")
    if not a.no_notes:
        note(f"**`{SEEKERS}` is REFUSED and never fetched** — the sibling category "
             f"where PEOPLE offer themselves. *Nothing in this host's rules forbids "
             f"it, and that is not a permission: a host that forbids nothing has not "
             f"consented to our taking everything it exposes.*")
        note("**`advertiser.phone` is DROPPED and `advertiser.userId` is never "
             "emitted** (nine digits on 42 of 42, a person's identifier), and "
             "`advertiser.name` is NOT reproduced either — filled on 17 of 42, always "
             "when `shopName` is absent, and nine of those seventeen carry no company "
             "marker, so it cannot be shown to be a business. *The record says WHAT "
             "the advertiser is, not WHO.*")
        note("**the digit rule runs on the PROSE only**: the advert id and `userId` "
             "are both nine digits on 42 of 42, so a rule let loose on the record "
             "would destroy both — and the money field was CHECKED rather than "
             "assumed, `features./price` carrying 24000, 30000 and 8000.")
        note("**`price_declared` is NOT called a salary**: the host labels it "
             "«Prezzo», the generalist classifieds price field, and 8 000 sits on an "
             "hourly cleaning post where 24 000 and 30 000 sit on full ones. *Annual, "
             "monthly and a rate are not distinguishable on three readings, so the "
             "unit is NOT established and the name does not claim one.*")
        note("`contract`, `work_hour` and `work_level` travel as the HOST's own codes "
             "— one of them reads `zzzzzother`, a sort-hack for «other». *It is the "
             "host's value and not a corruption of ours, and it is not translated "
             "into a vocabulary we would have invented.*")


def main():
    p = argparse.ArgumentParser(
        description="Subito (Italy) — the offers sub-category of a generalist "
                    "classifieds board, with the seekers' sibling category refused.")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("totals", help="what the host states for THIS section")
    t.set_defaults(fn=cmd_totals)
    l = sub.add_parser("list", help="walk the offers section")
    l.add_argument("--max", type=int)
    l.add_argument("--page-size", type=int, default=30)
    l.add_argument("--no-notes", action="store_true")
    l.set_defaults(fn=cmd_list)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
