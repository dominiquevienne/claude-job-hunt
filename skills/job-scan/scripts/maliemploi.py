#!/usr/bin/env python3
"""Mali Emploi (`maliemploi.org`) — a WordPress board running `wpjobportal`, whose two declared enumerators AGREE and serve exactly the unexpired adverts, while an expired one stays reachable at its own address. Issue #1279.

  maliemploi.py list [--max N]   the union of both enumerators, each record naming its own
  maliemploi.py ad --id <N>      one advert, by the numeric id its own record carries

TWO ENUMERATORS, AND THEY AGREE — which is what the measurement says after a motif of MINE was
caught being wrong by its characters. Measured 2026-11-06, the guard on each exact URL in a turn
distinct from the retrieval, one token (`claude-user`), every body retrieved by
`bin/fetch-body.py`:

    /feed/wpjobportal_jobsfeed/   200,   7 466 B   4 items  ->  ids {26, 51, 54, 56}
    /emplois/                     200,  84 766 B   4 links  ->  ids {26, 51, 54, 56}
    ------------------------------------------------------------------------------------
    identical, and those four are EXACTLY the four adverts whose `validThrough` is to come

**AND A FIRST READING SAID THE OPPOSITE, FROM A DEFECT IN MY OWN MOTIF.** A hand-rolled
`/emplois/job/[a-z0-9-]*?(\\d+)\\b`, NON-ANCHORED and non-greedy, takes the FIRST number in the
slug — and the slug `grand-recrutement-50-agents-commerciaux-terrain-h-f-a-bamako-bamako-54`
carries «50» from its own TITLE. So the feed read as {26, **50**, 51, 56} and the list as
{26, 51, **54**, 56}: a fabricated disjointness, a fabricated «no witness», and a design
justified by a defect of the instrument. Anchored on `$` it takes the LAST number, which is the
id — same held body, two motifs, `{26, 50, 51, 56}` against `{26, 51, 54, 56}`.

> **Nothing caught this by reading. What caught it is that the adapter's own anchored motif
> DISAGREED with the hand-rolled one on the same bytes** — `CLAUDE.md` §4's third way for a
> motif to be false, by its FORM, and the only control that finds it is to seek the same object
> by two motifs of different shapes. *The direction is the expensive one: it does not refuse
> anything and it does not publish a wrong number — it publishes a wrong REASON, and a design
> resting on it would have looked measured.*

**WHAT IS TRUE, AND IT IS A BETTER POSITION THAN THE FALSE FINDING.** The four ids both
enumerators serve are exactly the four adverts still valid on 2026-11-06, and the fifth advert
the host holds — id 50, `validThrough 2026-10-24`, thirteen days past — **is listed by NEITHER
and still answers 200 with a complete `JobPosting`**. So the enumerators are consistent with
each other AND with the validity dates, and what does NOT enumerate is the per-id address:
reaching an advert by its id says nothing about it being current. `ad` therefore prints whether
the advert it read is expired, and `valid_through` travels in every record.

**BOTH ARE WALKED ANYWAY, and the reason is not redundancy for its own sake:** they agreed on
the day measured, so either alone would have done, and walking both costs ONE extra request
while making a future divergence VISIBLE in the run's own output instead of silent. The union
is computed from what the two actually return, never from this docstring.

The root states no count, there is no pager and no facet on `/emplois/` (measured: zero
`/emplois/?...` parameter on the page), and the 7 posts this card counted on 2026-09-12 cannot
be recounted — «Publié il y a» now returns zero. **So the board's SIZE is still not established
as a count, and a run says its conclusion rests on two short enumerators.**

THREE URL FORMS FOR ONE ADVERT, so the address is TAKEN from the record and never composed:

    the list links     /offre/?wpjobportalme=job&wpjobportallt=viewjob&wpjobportalid=<N>
    the feed links     /emplois/job/<slug>-<N>
    the record states  /offre/job/<slug>-<N>     <- `JobPosting.url`, and this is what is emitted

THE SAFETY BORNE DECIDES BEFORE ANY OPTIMISATION, and it is a CONDITION rather than a filter.
The root declares `/cvtheque/` and `/deposer-cv/` — a database of CVs of REAL PEOPLE — and this
host's rules forbid NOTHING, so the guard answers `allowed=True` on both. **«The rules permit»
is not «it is ours to take»**: the family measured on a Tajik board where 34 894 of 42 851
`<loc>` were candidates' CVs behind a 105-byte `robots.txt` with no `Disallow` at all. Both
paths are NAMED on the pages we legitimately hold — 3 and 4 occurrences on `/emplois/` — so an
adapter that walked its links would reach them. They are never requested, the refusal is
exercised in both directions by the suite, and `wpjobportalme=resume` / `viewresume` return
ZERO on every page read, which is a measured absence and not a protection.

**THIS HOST ONCE SERVED AN APACHE ERROR PAGE AS ITS `robots.txt`**, and two issues came out of
it (#128, #138: «a refusal in prose is still a refusal», so `allowed` is False and `certain`
False). Today the guard answers `state=read`, `certain=True`, group `*`, `rule=None` on every
path below — **so a real file was recognised, and `certain` is the field that tells the two
states apart.** It is read from `tests/` rather than rediscovered: a measured fact survives
best in a test docstring, and that is exactly where nobody looks for it.

THE RECORD IS THE ADVERT PAGE'S OWN `JobPosting`, present on 5 of 5 — and the ROOT carries
none, which is why a verdict of rendering taken on `/` says nothing about an advert page.
**Three of its fields are PLACEHOLDERS, measured on the population and not inferred from one
specimen:**

    hiringOrganization.name   «Mali Emploi ·»   5 of 5   <- the BOARD's own name, NEVER the employer
    baseSalary.currency       «$»               5 of 5   <- and Mali's currency is the CFA franc
    baseSalary.value.value    «»                5 of 5   <- the field is PRESENT and never FILLED

*Emitting `employer: "Mali Emploi ·"` would put the board's name in the employer of every
advert it serves, and `currency: "$"` would state a currency this market does not use. A floor
on the VALUE is what separates a present field from a filled one (#1007: declaring you withheld
what nobody filed, taken by the other end).* `employmentType` is `CDI` on 5 of 5 and
`addressLocality` is `Bamako` on 5 of 5, so neither discriminates anything today, and that is
said rather than published as a property of the board.

THE CONTACTS ARE REAL AND HEAVILY EXERCISED HERE: **an e-mail on 3 of 5 and a telephone on 2 of
5**, the opposite of a board where the redaction is theoretical. And the pattern has **NO branch
on a bare run of digits**, which is a decision taken from the corpus rather than a precaution:

    CAUGHT   +223 70 57 43 57 (« Infos : »)  ·  94 48 32 30 (« par WhatsApp au : »)
             00223 76 12 34 56 · +223 76123456 · 70.57.43.57 · 76-12-34-56 · the three e-mails
    INTACT   24 000 FCFA · 150 000 FCFA · 1 500 000 FCFA · 750 000 XOF · 85 000 000
             75000000 FCFA · 24/10 · 14 & 15 NOVEMBRE 2026 · 223 postes · Bamako 1334

**The one long bare run in the corpus is NOT a telephone**, and only reading its clause said
so: `6755939312` sits inside `https://apps.apple.com/us/app/telimani/id6755939312` — an App
Store app id. A digit-count rule would have withheld it, mangling a legitimate URL, and a
digit-count rule on a currency is how 113 of 115 salaries were once destroyed; the CFA franc is
written in exactly those magnitudes. *Residue DECLARED: a Mali mobile written as eight BARE
digits, with no separator and no dialling code, is MISSED. Both real numbers in the corpus carry
either the code or separated pairs, so this is a measured risk and not a guess — and the error
it avoids is the costly one.* A form (`forms.gle`) is not a contact and is emitted.
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

HOST = "maliemploi.org"
FEED = f"https://{HOST}/feed/wpjobportal_jobsfeed/"
LISTE = f"https://{HOST}/emplois/"
DEFAULT_MAX = 25
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# **TWO branches, and NEITHER on a bare run of digits.** The dialling code, or the Mali
# mobile in SEPARATED PAIRS. The CFA franc is written in large numbers, and the only long
# bare run in the corpus is an App Store app id INSIDE a URL -- read by its clause, not by
# its shape. The lookbehind blocks a letter, a slash and an `=` so a number that is part of
# a path or a query can never be taken for a telephone.
PHONE_RE = re.compile(r"(?:\+|00)\s?223(?:[\s .\-/]?\d){8}"
                      r"|(?<![\d.,\w/=])[6-9]\d(?:[\s .\-]\d\d){3}(?![\d\w])")

LD_RE = re.compile(r"<script[^>]*application/ld\+json[^>]*>(.*?)</script>", re.S | re.I)
ID_RE = re.compile(r"wpjobportalid=(\d+)")
# the feed and the record spell the advert as `<slug>-<N>`; the id is the LAST number
SLUG_ID_RE = re.compile(r"/(?:emplois|offre)/job/[a-z0-9-]*?(\d+)/?$")
ITEM_RE = re.compile(r"<item>(.*?)</item>", re.S | re.I)
LINK_RE = re.compile(r"<link>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</link>", re.S | re.I)

# **NEVER REQUESTED, and it is a CONDITION rather than an optimisation.** The rules forbid
# nothing here, so the guard PERMITS these paths -- and they hold CVs of real people. Both
# are named on the pages we hold, so a link walk would reach them.
JAMAIS_DEMANDE = (
    (re.compile(r"^/(?:cvtheque|deposer-cv)(?:/|$)"),
     "a database of CVs of REAL PEOPLE -- the rules permit it and that is not a permission"),
    (re.compile(r"wpjobportalme=(?:resume|cv)|viewresume", re.I),
     "the resume side of `wpjobportal` -- a candidate's own record, never a vacancy"),
)

_PACE = Pace(HOST, own=3.0)   # no Crawl-delay written for any agent; 3 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[maliemploi] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    # **`certain` is the field that tells a READ file from a body nobody recognised**, and
    # this host served an Apache 403 page as its `robots.txt` once (#128, #138). An
    # uncertain verdict is not a refusal and does not stop us -- it is SAID.
    if not a.get("certain"):
        note(f"{url}: the rules were not read with certainty (state={a.get('state')!r}) -- "
             f"this host once served an Apache error page as its `robots.txt`")
    return a


def request(url):
    parts = urllib.parse.urlsplit(url)
    cible = full_path(parts)
    for motif, pourquoi in JAMAIS_DEMANDE:
        if motif.search(cible):
            die(f"{url}: never asked -- {pourquoi}", EXIT_REFUSED)
    if parts.netloc and parts.netloc not in (HOST, f"www.{HOST}"):
        die(f"{url}: only `{HOST}` is asked", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(
        wire_url(url),
        headers={"User-Agent": UA, "Accept": "text/html,application/xml;q=0.9",
                 "Accept-Language": "fr"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def fetch(url, quoi):
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 -- {quoi} is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    if not body:
        die(f"{url}: 200 and an empty body -- {quoi} unreadable, which is not an empty board",
            EXIT_PARTIAL)
    return body


def txt(markup):
    if not markup:
        return None
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", str(markup))
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    """Returns (text, what was ACTUALLY removed) -- the witness is DERIVED, never asserted."""
    if not s:
        return None, []
    taken = []
    if MAIL_RE.search(s):
        taken.append("email")
        s = MAIL_RE.sub("[e-mail withheld]", s)
    if PHONE_RE.search(s):
        taken.append("telephone")
        s = PHONE_RE.sub("[telephone withheld]", s)
    return (s.strip() or None), taken


def jobposting(page):
    """The advert page's own `JobPosting`, present on 5 of 5 -- and the ROOT carries none."""
    for raw in LD_RE.findall(page):
        try:
            d = json.loads(raw.strip())
        except ValueError:
            continue
        pool = d if isinstance(d, list) else (d.get("@graph") or [d])
        for x in (pool if isinstance(pool, list) else [pool]):
            if isinstance(x, dict) and x.get("@type") == "JobPosting":
                return x
    return None


def one(x):
    return x if isinstance(x, dict) else {}


def un_vrai_employeur(nom):
    """**`hiringOrganization.name` is the BOARD's own name on 5 of 5, never the employer.**

    Emitting it would put «Mali Emploi» in the employer of every advert the board serves.
    The test is on the board's OWN name rather than on a list of placeholders, because a
    list of refusals bets that the problem has been enumerated."""
    n = " ".join((nom or "").split()).strip(" ·.-")
    if not n:
        return None
    plat = re.sub(r"[^a-z]", "", n.lower())
    return None if plat in ("maliemploi", "maliemploiorg") else n


def salaire(bs):
    """(amount, currency) -- and NOTHING unless the VALUE is filled.

    `currency` is «$» on 5 of 5 with an EMPTY value: a field that is PRESENT and never
    FILLED. `if x` on the currency would state a currency this market does not use on every
    record, and «$» is not the CFA franc."""
    v = one(bs).get("value")
    montant = (one(v).get("value") if isinstance(v, dict) else v)
    montant = " ".join(str(montant or "").split()).strip()
    if not montant:
        return None, None
    dev = " ".join(str(one(bs).get("currency") or "").split()).strip()
    return montant, (dev if dev and dev != "$" else None)


def record(url, page, par):
    """`par` names the enumerator(s) this advert came from -- NEITHER contains the other."""
    jp = jobposting(page)
    if not jp:
        return None
    ident = one(jp.get("identifier")).get("value")
    if not ident:
        m = ID_RE.search(url) or SLUG_ID_RE.search(urllib.parse.urlsplit(url).path)
        ident = m.group(1) if m else None
    corps, pris = scrub(txt(jp.get("description")))
    addr = one(one(jp.get("jobLocation")).get("address"))
    montant, devise = salaire(jp.get("baseSalary"))
    r = {
        "source": "maliemploi", "country": "ML",
        "ledger_id": f"maliemploi:{ident}" if ident else None,
        "id": ident,
        # **the address is TAKEN from the record**: three forms exist for one advert, and the
        # one the record states is neither the list's nor the feed's.
        "url": (jp.get("url") or url),
        "asked": url,
        "title": " ".join((jp.get("title") or "").split()) or None,
        # ABSENT rather than the board's own name -- see `un_vrai_employeur`
        "employer": un_vrai_employeur(one(jp.get("hiringOrganization")).get("name")),
        "city": addr.get("addressLocality") or None,
        "published": (jp.get("datePosted") or "")[:10] or None,
        "valid_through": (jp.get("validThrough") or "")[:10] or None,
        "employment_type": jp.get("employmentType") or None,
        "text": corps,
        "enumerator": par,
        "withheld_fields": pris or None,
        "language": "fr",
    }
    if montant:
        r["salary"] = montant
        if devise:
            r["currency"] = devise
    if withheld_a_contact(r["withheld_fields"]):
        r["contacts_withheld"] = True
    return r


def du_flux():
    """The ids the declared feed names, with the advert URL it states for each."""
    body = fetch(FEED, "the declared feed")
    out = {}
    for item in ITEM_RE.findall(body):
        for lien in LINK_RE.findall(item):
            m = SLUG_ID_RE.search(urllib.parse.urlsplit(lien.strip()).path)
            if m:
                out[m.group(1)] = lien.strip()
    return out, len(ITEM_RE.findall(body))


def de_la_liste():
    """The ids `/emplois/` links, in its own query form."""
    body = fetch(LISTE, "the list")
    ids = []
    for i in ID_RE.findall(body):
        if i not in ids:
            ids.append(i)
    return {i: (f"https://{HOST}/offre/?wpjobportalme=job&wpjobportallt=viewjob&"
                f"wpjobportalid={i}") for i in ids}, len(ids)


def cmd_list(a):
    flux, n_items = du_flux()
    liste, n_liens = de_la_liste()
    # **the UNION, and each record says where it came from.** Neither set contains the other,
    # so taking one as the enumerator would silently drop the other's exclusive member.
    ordre = list(liste) + [i for i in flux if i not in liste]
    borne = a.max if a.max else DEFAULT_MAX
    rows, sansjp = [], []
    for ident in ordre[:borne]:
        par = ("feed+list" if ident in flux and ident in liste
               else ("feed" if ident in flux else "list"))
        url = liste.get(ident) or flux[ident]
        r = record(url, fetch(url, "an advert page"), par)
        if r is None:
            sansjp.append(ident)
            continue
        rows.append(r)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    seul_flux = sorted(set(flux) - set(liste))
    seul_liste = sorted(set(liste) - set(flux))
    note(f"{len(rows)} emitted from the UNION of two enumerators -- the declared feed "
         f"({n_items} item(s), ids {sorted(flux)}) and `/emplois/` ({n_liens} link(s), ids "
         f"{sorted(liste)}).")
    # **the agreement or the divergence is DERIVED from what the two returned in this run**,
    # never recopied from the docstring: on 2026-11-06 they agreed, and a first reading said
    # otherwise only because a non-anchored motif of ours took a number out of a slug's title.
    if seul_flux or seul_liste:
        note(f"**THE TWO ENUMERATORS DIVERGE IN THIS RUN**: {seul_flux or 'none'} only in the "
             f"feed, {seul_liste or 'none'} only in the list — so neither is a witness, the "
             f"union is what was emitted, and each record names where it came from. They AGREED "
             f"when this adapter was written, so this is a change in the host and not its "
             f"ordinary state.")
    else:
        note("the two enumerators AGREE in this run, so either alone would have done; both are "
             "walked because the disagreement is what would otherwise be silent.")
    note(f"**The SIZE of this board is not established as a count**: the root states no count, "
         f"`/emplois/` declares no pager and no facet, and the 7 posts counted on 2026-09-12 "
         f"cannot be recounted. What the enumerators serve is the adverts still VALID -- an "
         f"expired one (id 50, `validThrough` 2026-10-24) is listed by neither and still answers "
         f"200 at its own address, so reaching an advert by its id says nothing about it being "
         f"current.")
    nw = sum(1 for r in rows if r.get("contacts_withheld"))
    ne = sum(1 for r in rows if r.get("employer"))
    note(f"a contact was removed from {nw} of {len(rows)}; `withheld_fields` names what was "
         f"actually taken, and the rule has NO branch on a bare run of digits -- the one long "
         f"run in the corpus is an App Store app id inside a URL, and the CFA franc is written "
         f"in those magnitudes.")
    note(f"{ne} of {len(rows)} carry an `employer`: `hiringOrganization` holds the BOARD's own "
         f"name on every advert read, so the field is ABSENT rather than false, and `baseSalary` "
         f"is emitted only when its VALUE is filled.")
    note("`/cvtheque/` and `/deposer-cv/` were never requested -- the rules permit them and "
         "that is not a permission.")
    if sansjp:
        note(f"{len(sansjp)} advert(s) carried no `JobPosting`: {sansjp}")


def cmd_ad(a):
    if a.id is not None:
        if not re.fullmatch(r"\d{1,9}", str(a.id)):
            die(f"{a.id!r}: an advert id is the number `wpjobportalid=<N>` the list links and "
                f"the record's own `identifier` carries")
        url = (f"https://{HOST}/offre/?wpjobportalme=job&wpjobportallt=viewjob&"
               f"wpjobportalid={a.id}")
    else:
        parts = urllib.parse.urlsplit(a.url)
        if parts.netloc not in (HOST, f"www.{HOST}") or not (
                ID_RE.search(a.url) or SLUG_ID_RE.search(parts.path)):
            die(f"{a.url}: not an advert address on `{HOST}` -- the list spells it "
                f"`/offre/?...wpjobportalid=<N>`, the feed `/emplois/job/<slug>-<N>` and the "
                f"record `/offre/job/<slug>-<N>`; all three name the same advert")
        url = a.url
    r = record(url, fetch(url, "an advert page"), "asked")
    if r is None:
        die(f"{url}: 200 and no `JobPosting` -- the advert page carries one on every advert "
            f"read, so this is a shape change and not an empty page", EXIT_PARTIAL)
    print(json.dumps(r, ensure_ascii=False))
    # **a per-id address is not an enumerator**: an expired advert still answers 200 here and
    # is listed by neither enumerator, so the state is SAID rather than left to the caller.
    import datetime
    vt = r.get("valid_through")
    etat = ("EXPIRED on " + vt if vt and vt < datetime.date.today().isoformat()
            else ("valid through " + vt if vt else "no deadline stated"))
    note(f"{r['id']}: read from the page's own `JobPosting`; {etat}; "
         + (f"withheld {', '.join(r['withheld_fields'])}" if r["withheld_fields"]
            else "nothing to withhold")
         + f"; employer {'read' if r['employer'] else 'ABSENT (the field held the board name)'}"
         + f"; the address is the one the RECORD states, not the one asked.")


def main():
    p = argparse.ArgumentParser(
        description="Mali Emploi -- two DISJOINT enumerators, so the union is walked and the "
                    "board's size is not established. Issue #1279.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help=f"the union of both enumerators -- {DEFAULT_MAX} unless --max")
    l_.add_argument("--max", type=int, help="how many adverts to read (one request each, 3 s apart)")
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad", help="one advert")
    g = ad.add_mutually_exclusive_group(required=True)
    g.add_argument("--id", help="the numeric id the list links and the record carries")
    g.add_argument("--url", help="any of the three forms that name an advert")
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
