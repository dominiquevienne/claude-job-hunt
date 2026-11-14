#!/usr/bin/env python3
"""JobPosting (`www.jobposting.pro`) — a multi-country white-label board whose DECLARED sitemap enumerates 22 988 adverts while its paginated list carries 268 the sitemap does NOT, so neither enumerator contains the other and the board is LARGER than its own enumerator declares. Issue #1311.

  jobposting.py list [--max N] [--pages N]   the union of both enumerators, each record naming its own
  jobposting.py ad --id <N> | --url <URL>    one advert, by the id its own record carries

NEITHER ENUMERATOR CONTAINS THE OTHER, and that is the measurement that decides the walk.
Measured 2026-11-14 between 03:24 and 03:27 UTC, the guard taken on every exact path in a turn
distinct from the retrieval, one token (`claude-user`), every body through `bin/fetch-body.py`:

    /sitemap.xml                 200,       325 B   an INDEX of 2 children
    /sitemap-offres.xml          200, 2 873 607 B   22 988 <loc>, 22 988 distinct, ALL adverts
    /offres                      200,   999 270 B   4 000 ids distinct
    /offres?p=2                  200, 1 005 294 B   4 000 ids distinct
    /offres?p=3                  200,   981 694 B   4 000 ids distinct
    ------------------------------------------------------------------------------------------
    sitemap \\ pages  11 270      pages \\ sitemap  268      intersection  11 718

**The 268 the sitemap lacks are the NEWEST adverts and they are all on page 1** — ids from
2750294 upward, while `p2` and `p3` are both SUBSETS of the sitemap. So the sitemap lags the list
and the list does not reach the sitemap's tail: `CLAUDE.md` §4's shape where two enumerators
are quasi-disjoint, and both are walked because the union is the only honest answer. The
asymmetry is DERIVED from what the two return in a run, never recopied from this docstring.

THE PAGER DECLARES EIGHT PAGES AND THE EIGHTH IS EMPTY — so `4 000 × 8` is not a total and the
pager is not a witness. `?p=7` and `?p=8` both answer **200 with 9 263 B and the SAME md5
`b9b9e6cd4b49`**: one «Aucune offre en ce moment.» page, byte-identical, still printing
«Page 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8». The pager is therefore a CONSTANT of the template and
says nothing about where the content stops.

> **A page with zero ids is the stop condition, and it is the only one available.** Pages 1–3
> are full and 7–8 are empty; where exactly the content ends, in 4..6, is NOT established and
> was not probed — three more megabytes would not have changed this design.

THE PAGES ARE NOT STRICTLY DISJOINT, so the walk DEDUPLICATES and says so: `p1 ∩ p2 = 0` and
`p1 ∩ p3 = 0`, but **`p2 ∩ p3 = 14`**. A reading of one pair would have concluded disjointness
and an extractor that trusted it would have double-counted fourteen adverts — *«un échantillon
où deux modèles coïncident ne tranche rien»*. 4 000 is a PAGE SIZE; it is not a plateau and not
a total.

THE HOST STATES NO COUNT, AND THE 22 988 IS A COUNT OF **OURS**. It is the number of rows we
extracted from a file the host serves, not a figure the host asserts anywhere — so it is an
ENUMERATOR SIZE and never a board total, and the 268 exclusives prove the board exceeds it. A
run prints both sides and declares the size NOT established.

THE MARKUP IS THE PLATFORM'S AND IT IS ESTABLISHED ON TWO EMPLOYERS, which is what a single
specimen could not do. Each advert page carries exactly ONE `application/ld+json` `JobPosting`;
the LIST carries none at all, raw or HTML-escaped, so a verdict of rendering taken on `/offres`
says nothing about an advert page:

    /emploi-2750653-1   14 700 B   ISEC FORMATION OUEST   Le Port 97420 FR   INTERN
    /emploi-2749564-1   19 583 B   Algoteque              Warszawa 00-105 PL  CONTRACTOR

**The same fourteen keys on both, and `identifier.name` is `JobPosting.pro` on both** — the
platform emits the block, which is why it is consistent across employers. *Still two adverts
and not a census: a gabarit predicts the ROUTE and never the ANALYSE, so every field below is
read defensively and a missing one is ABSENT rather than invented.*

**AND `hiringOrganization.name` IS THE REAL EMPLOYER HERE** — «ISEC FORMATION OUEST»,
«Algoteque» — not the board's own name. That is the opposite of `maliemploi`, where the field
held «Mali Emploi ·» on 5 of 5 and emitting it would have put the board in every employer. The
difference is measured, not assumed, and the floor is on the VALUE either way.

EVERY ADVERT PAGE IS AT THE EMPLOYER'S OWN BRAND: `<title>` reads «… | ISEC FORMATION OUEST»
and «… | Algoteque», with the employer's own navigation. So `/emploi-N-1` serves a white-label
career page and what lives OUTSIDE the `JobPosting` block can differ from employer to employer.
Nothing outside that block is read.

THE ADDRESS IS TAKEN FROM THE RECORD. `JobPosting.url` equals the page asked on 2 of 2, so
composing it would be correct today and is still not done: the record states its own address,
and an adapter that composes one inherits every future change of shape.

NO SALARY AT ALL: `baseSalary` is ABSENT from the key set on both adverts, so nothing is
emitted for it. **And there is no digit-run branch in the redaction**, which matters precisely
because a salary could appear in prose later: the Burmese kyat specimen — `350000 - 450000 MMK`
turned into `[telephone withheld] MMK` on 113 of 115 adverts — is what a «nine digits is a
telephone» rule costs on a board whose currency is written large. The telephone pattern here
requires an international prefix or a French national form with its separators, and a Polish
postal code (`00-105`) cannot satisfy either.

CONTACTS: **zero `mailto:`, zero `tel:`, zero e-mail in clear on both adverts.** Two specimens
is not a census, so the redaction is *theoretical on what has been read* — it is exercised in
both directions by the suite, and `withheld_fields` is DERIVED from what was actually removed,
never asserted, so a record cannot claim a discretion nobody exercised (#1007).

NO `language` IS EMITTED. The two adverts read are in FRENCH and POLISH, nothing in the markup
declares a language, and `addressCountry` is a country and not a tongue. A field guessed from
the country would be wrong on any advert written in English for a French employer.

WHAT IS NEVER ASKED, and it is a POSITIVE floor rather than a list of refusals. This host's
rules forbid NOTHING — 71 bytes, one `*` group whose `Disallow:` has an empty value — so the
guard answers `allowed=True` on every path, and *«the rules permit» is not «it is ours to
take»*: the Tajik board where 34 894 of 42 851 `<loc>` were real people's CVs sat behind a
105-byte file with no `Disallow` at all. A list of forbidden paths would bet that the problem
has been enumerated; instead only four SHAPES are requestable, and anything else — the client
area, any account or applicant path this board may grow — is refused by construction.
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

HOST = "www.jobposting.pro"
HOTES = (HOST, "jobposting.pro")
LISTE = f"https://{HOST}/offres"
INDEX = f"https://{HOST}/sitemap.xml"
DEFAULT_MAX = 25
DEFAULT_PAGES = 1          # page 1 is the fresh head the sitemap lacks; --pages walks further
PAGES_MAX = 40             # the pager says 8 and the pager is a template constant
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# **the id is the number in `/emploi-<N>-1`**, and the boundary is a NEGATIVE LOOKAHEAD on
# a digit rather than a list of followers. A first version ended `(?:[/?#]|$)` and rendered
# **ZERO on the list**, where the address is followed by the APOSTROPHE closing the `href`
# attribute -- while still rendering 22 988 from the sitemap, because there the match is
# taken on the PARSED path, which ends the string. A motif false by its FORM, and nothing
# caught it by reading: what caught it is that this motif DISAGREED with a hand-rolled one
# on the same held bytes, 0 against 4 000. The suffix is `1` on 22 988 + 4 000 occurrences
# read, and the lookahead still refuses `-10`, `-11` and `-2`.
AD_RE = re.compile(r"/emploi-(\d+)-1(?!\d)")
LD_RE = re.compile(r"<script[^>]*application/ld\+json[^>]*>(.*?)</script>", re.S | re.I)
LOC_RE = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
URLSET_RE = re.compile(r"<url>(.*?)</url>", re.S)
LASTMOD_RE = re.compile(r"<lastmod>\s*(.*?)\s*</lastmod>", re.S)

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# **TWO branches, and NEITHER on a bare run of digits.** An international prefix, or the French
# national form with its separators REQUIRED. A Polish postal code (`00-105`) satisfies neither,
# and no salary written large can satisfy either -- which is the whole point (the kyat).
PHONE_RE = re.compile(
    r"(?<![\d\w/=])(?:\+|00)\s?\d{1,3}(?:[\s.\-/]?\d){6,11}(?![\d\w])"
    r"|(?<![\d\w/=.])0[1-9](?:[\s.\-]\d\d){4}(?![\d\w])")

# **A POSITIVE floor: only these four SHAPES are ever requested.** A list of refusals bets the
# problem has been enumerated; this bets nothing. The rules here forbid NOTHING, so the guard
# permits everything and the restriction is ours.
DEMANDABLE = (
    re.compile(r"^/robots\.txt$"),
    re.compile(r"^/sitemap[a-z0-9._-]*\.xml$"),
    re.compile(r"^/offres(?:\?p=\d{1,3})?$"),
    re.compile(r"^/emploi-\d{1,12}-1$"),
)

_PACE = Pace(HOST, own=6.0)   # no Crawl-delay written for any agent; six seconds are OURS


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobposting] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    if not a.get("certain"):
        note(f"{url}: the rules were not read with certainty (state={a.get('state')!r})")
    return a


def request(url):
    parts = urllib.parse.urlsplit(url)
    if parts.netloc and parts.netloc not in HOTES:
        die(f"{url}: only `{HOST}` is asked", EXIT_REFUSED)
    cible = full_path(parts)
    if not any(m.match(cible) for m in DEMANDABLE):
        die(f"{url}: never asked -- only `/offres`, `/offres?p=N`, `/emploi-<N>-1`, "
            f"`/sitemap*.xml` and `/robots.txt` are requestable on this host. The rules "
            f"forbid nothing here, and that is not a permission.", EXIT_REFUSED)
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


def one(x):
    return x if isinstance(x, dict) else {}


def jobposting(page):
    """The advert page's own `JobPosting` -- exactly one block on 2 of 2, none on the LIST."""
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


def mois_experience(req):
    """`monthsOfExperience` only when it is FILLED -- 1 and 60 on the two read.

    A present field is not a filled one, and `if x` would also swallow a legitimate 0."""
    v = one(req).get("monthsOfExperience")
    if isinstance(v, bool) or v is None:
        return None
    try:
        n = int(str(v).strip())
    except (TypeError, ValueError):
        return None
    return n if n >= 0 else None


def record(url, page, par, lastmod=None):
    """`par` names the enumerator(s) this advert came from -- NEITHER contains the other."""
    jp = jobposting(page)
    if not jp:
        return None
    ident = one(jp.get("identifier")).get("value")
    if not ident:
        m = AD_RE.search(urllib.parse.urlsplit(url).path)
        ident = m.group(1) if m else None
    corps, pris = scrub(txt(jp.get("description")))
    addr = one(one(jp.get("jobLocation")).get("address"))
    employeur = " ".join(str(one(jp.get("hiringOrganization")).get("name") or "").split()) or None
    r = {
        "source": "jobposting",
        "ledger_id": f"jobposting:{ident}" if ident else None,
        "id": ident,
        # TAKEN from the record: it equals the page asked on 2 of 2 and is still not composed.
        "url": (jp.get("url") or url),
        "asked": url,
        "title": " ".join((jp.get("title") or "").split()) or None,
        # the REAL employer here -- measured on two, and the opposite of `maliemploi`
        "employer": employeur,
        "city": addr.get("addressLocality") or None,
        "postal_code": addr.get("postalCode") or None,
        # per RECORD and never a constant: FR and PL on the two read
        "country": addr.get("addressCountry") or None,
        "published": (jp.get("datePosted") or "")[:10] or None,
        "valid_through": (jp.get("validThrough") or "")[:10] or None,
        "employment_type": jp.get("employmentType") or None,
        "direct_apply": jp.get("directApply") if isinstance(jp.get("directApply"), bool) else None,
        "months_of_experience": mois_experience(jp.get("experienceRequirements")),
        "text": corps,
        "enumerator": par,
        "withheld_fields": pris or None,
    }
    if lastmod:
        r["sitemap_lastmod"] = lastmod[:10]
    if withheld_a_contact(r["withheld_fields"]):
        r["contacts_withheld"] = True
    return r


def enfants_du_sitemap():
    """The children the DECLARED index names -- read, never composed (`/sitemap-offres.xml`
    is not guessed: the index states it)."""
    body = fetch(INDEX, "the declared sitemap index")
    return [u.strip() for u in LOC_RE.findall(body) if u.strip().endswith(".xml")]


def du_sitemap():
    """{id: (url, lastmod)} from every child the index names that carries adverts."""
    out, lus = {}, []
    for enfant in enfants_du_sitemap():
        body = fetch(enfant, "a declared sitemap child")
        n = 0
        for bloc in URLSET_RE.findall(body):
            loc = LOC_RE.search(bloc)
            if not loc:
                continue
            u = loc.group(1).strip()
            m = AD_RE.search(urllib.parse.urlsplit(u).path)
            if not m:
                continue
            lm = LASTMOD_RE.search(bloc)
            out.setdefault(m.group(1), (u, lm.group(1) if lm else None))
            n += 1
        lus.append((enfant, n))
    return out, lus


def de_la_liste(pages):
    """{id: url} from the paginated list, and the per-page counts.

    **Stops on a page with ZERO ids**: `?p=7` and `?p=8` answer 200 with the same 9 263-byte
    «Aucune offre» body and the pager still prints eight, so the pager cannot say where the
    content ends. Pages are NOT strictly disjoint -- `p2 ∩ p3 = 14` on 2026-11-14 -- so the
    overlap is counted and reported rather than assumed away."""
    out, par_page, chevauchement = {}, [], 0
    for p in range(1, max(1, min(pages, PAGES_MAX)) + 1):
        url = LISTE if p == 1 else f"{LISTE}?p={p}"
        body = fetch(url, f"list page {p}")
        vus = []
        for m in AD_RE.finditer(body):
            i = m.group(1)
            if i not in vus:
                vus.append(i)
        par_page.append((p, len(vus)))
        if not vus:
            note(f"page {p} carries ZERO advert ids -- the walk stops there. The pager prints a "
                 f"fixed eight pages and an empty page is byte-identical whatever `p` says, so "
                 f"the pager is not a witness.")
            break
        for i in vus:
            if i in out:
                chevauchement += 1
            else:
                out[i] = f"https://{HOST}/emploi-{i}-1"
    return out, par_page, chevauchement


def cmd_list(a):
    sm, enfants = du_sitemap()
    liste, par_page, chevauchement = de_la_liste(a.pages)
    # the UNION, list FIRST because the list holds the freshest adverts the sitemap lacks
    ordre = list(liste) + [i for i in sm if i not in liste]
    borne = a.max if a.max else DEFAULT_MAX
    rows, sansjp = [], []
    for ident in ordre[:borne]:
        dans_sm, dans_l = ident in sm, ident in liste
        par = ("sitemap+list" if dans_sm and dans_l else ("list" if dans_l else "sitemap"))
        url = liste.get(ident) or sm[ident][0]
        lm = sm[ident][1] if dans_sm else None
        r = record(url, fetch(url, "an advert page"), par, lm)
        if r is None:
            sansjp.append(ident)
            continue
        rows.append(r)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

    seul_sm = sorted(set(sm) - set(liste))
    seul_l = sorted(set(liste) - set(sm))
    note(f"{len(rows)} emitted from the UNION of two enumerators: the DECLARED sitemap "
         f"({'; '.join(f'{u} -> {n}' for u, n in enfants)}) and the paginated list "
         f"({'; '.join(f'p{p}={n}' for p, n in par_page)}).")
    # **DERIVED from this run, never recopied**: on 2026-11-14 neither contained the other.
    note(f"**NEITHER ENUMERATOR CONTAINS THE OTHER IN THIS RUN**: {len(seul_sm)} id(s) only in "
         f"the sitemap, {len(seul_l)} only in the list"
         + (f" (e.g. {seul_l[:3]})" if seul_l else "") + ". So the union is what was emitted and "
         f"each record names where it came from. If one side ever became a superset of the "
         f"other, THIS line is what would say so.")
    note(f"**The SIZE of this board is NOT established.** The host states no count anywhere: the "
         f"{len(sm)} the sitemap yields is a count of OURS over rows it serves, and the list "
         f"carried {len(seul_l)} id(s) the sitemap does not. "
         + (f"So the board EXCEEDS its own enumerator by at least that many. "
            if seul_l else
            f"The list added nothing beyond the sitemap IN THIS RUN, which is not the same "
            f"as the sitemap being complete: 268 such ids were measured on 2026-11-14 and "
            f"a short walk may simply not have reached any. ")
         + f"A conclusion here rests on two enumerators that disagree and on a pager that "
           f"prints a constant.")
    if chevauchement:
        note(f"the list pages OVERLAP: {chevauchement} id(s) seen on more than one page, so they "
             f"were deduplicated. 4 000 is a PAGE SIZE, not a plateau and not a total.")
    nw = sum(1 for r in rows if r.get("contacts_withheld"))
    ne = sum(1 for r in rows if r.get("employer"))
    note(f"a contact was removed from {nw} of {len(rows)}; `withheld_fields` names what was "
         f"ACTUALLY taken. The rule has NO branch on a bare run of digits -- a salary written "
         f"large must not read as a telephone -- and both adverts measured on 2026-11-14 carried "
         f"no contact at all, so the redaction is exercised by the suite and not by this board.")
    note(f"{ne} of {len(rows)} carry an `employer`: `hiringOrganization` holds the REAL employer "
         f"here, unlike `maliemploi` where it held the board's own name. No `baseSalary` key "
         f"exists on the adverts read, so nothing is emitted for pay, and no `language` is "
         f"emitted -- the two adverts read are in French and Polish and nothing declares a "
         f"tongue.")
    note("only `/offres`, `/offres?p=N`, `/emploi-<N>-1`, `/sitemap*.xml` and `/robots.txt` are "
         "requestable: the rules forbid NOTHING on this host, and that is not a permission.")
    if sansjp:
        note(f"{len(sansjp)} advert(s) carried no `JobPosting`: {sansjp[:10]}")


def cmd_ad(a):
    if a.id is not None:
        if not re.fullmatch(r"\d{1,12}", str(a.id)):
            die(f"{a.id!r}: an advert id is the number N in `/emploi-<N>-1`, which the record's "
                f"own `identifier` also carries")
        url = f"https://{HOST}/emploi-{a.id}-1"
    else:
        parts = urllib.parse.urlsplit(a.url)
        if parts.netloc not in HOTES or not AD_RE.search(parts.path):
            die(f"{a.url}: not an advert address on `{HOST}` -- an advert is spelled "
                f"`/emploi-<N>-1`")
        url = f"https://{HOST}{parts.path}"
    r = record(url, fetch(url, "an advert page"), "asked")
    if r is None:
        die(f"{url}: 200 and no `JobPosting` block -- the advert page carried one on 2 of 2 on "
            f"2026-11-14, so this is a change in the host and not an empty advert", EXIT_PARTIAL)
    print(json.dumps(r, ensure_ascii=False))
    if r.get("valid_through"):
        note(f"`validThrough` {r['valid_through']} -- reaching an advert by its id says nothing "
             f"about it still being current.")


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="jobposting.py",
        description="JobPosting (www.jobposting.pro) -- the union of a declared sitemap and a "
                    "paginated list, neither of which contains the other. #1311")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("list", help="the union of both enumerators")
    pl.add_argument("--max", type=int, default=DEFAULT_MAX,
                    help=f"how many adverts to FETCH (default {DEFAULT_MAX}); the enumerators "
                         f"hold tens of thousands and each advert is one request")
    pl.add_argument("--pages", type=int, default=DEFAULT_PAGES,
                    help=f"list pages to walk (default {DEFAULT_PAGES}); page 1 is the fresh "
                         f"head the sitemap lacks, and the walk stops on a page with zero ids")
    pl.set_defaults(fn=cmd_list)

    pa = sub.add_parser("ad", help="one advert")
    g = pa.add_mutually_exclusive_group(required=True)
    g.add_argument("--id", help="the number N in /emploi-<N>-1")
    g.add_argument("--url", help="the advert's own address")
    pa.set_defaults(fn=cmd_ad)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
