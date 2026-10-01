#!/usr/bin/env python3
"""KKTC Portal — iş ilanları (`kktcportal.net`), Northern Cyprus: a pager that actually ADVANCES, and the walk's end is an empty page rather than a stated count. Issue #724.

  kktcportal.py jobs [--country-code CY] [--max N]    the pager, then one request an advert

WHAT IT IS. The jobs section of a regional portal. Northern Cyprus's other named boards are
`iskibris` (delivered, #719), `kibriseleman`, `kibristailan`, `kariyerkktc`, `ekonomikibris`,
`worklinkcy`, `iscikler` and the Labour Department (#718–#726).

THE RULES. `kktcportal.net` serves its rules file (`state: read`, `certain: True`) and writes **no
Crawl-delay**; 2 s are ours. The guard is taken on each exact path.

THE ROUTE, and it is the plain one for once. `/is-ilanlari?sayfa=N` lists 24 adverts a page as
`/is-ilanlari/<slug>-<district>-<id>`, and **the pager advances**: measured 2026-10-01, page 1 and
page 2 share **no advert at all**, page 17 carries **6**, and page 18 carries **none**. *So the walk
asks page after page until one is empty* — 16 full pages plus a partial, **390 adverts**, where the
pager's own bound (17 × 24) suggested at most 408.

> **No count is stated anywhere**, so 390 is what the walk READ and not what the site claims. *The
> pager bounds it; the empty page ends it.* **Neither is a stated total, and the run says so.**

*This is worth marking because it is the exception: of the stop-rule family this repository has
collected — clamp, crush, reset, announce — **this board exhibits none**. Pages differ, the last is
partial, the next is empty. The adapter still checks for a page repeating its predecessor, because
that check costs one comparison and its absence is what the family is made of.*

**THE ADVERT CARRIES A `JobPosting`, AND THE LIST CARRIES ALMOST NOTHING.** *The list block holds the
title and the link, no employer and **no date**.* The advert page ships **two** `ld+json` blocks —
one an `Organization` + `WebSite` pair, the other the `JobPosting` — so the block is chosen **by its
`@type`** and never by its position. From it: `title`, `hiringOrganization`, `jobLocation`,
`employmentType`, `datePosted`, `validThrough`, `description`.

**A PREMISE OF THE 2026-09-18 CARD NO LONGER HOLDS, and it is recorded rather than quietly dropped.**
*That reading reported «&nbsp;the list's markup dates are aberrant, 26/05/1779&nbsp;».* **Measured
2026-10-01: the list markup carries no `jj/mm/aaaa` date at all** — zero, not an aberrant one. Either
the site changed or that figure described something else; **what is certain is that the date must come
from the advert's `datePosted`, which is what this adapter reads.**

**AND THE BOARD KEEPS EXPIRED ADVERTS LISTED.** *The first advert read states
`validThrough: 2026-08-23` — six weeks past.* **They are emitted, never dropped**, and the run counts
them: *a board that lists an expired advert is making a filing, and silently discarding it would
replace the board's statement with ours.* `valid_through` travels on every record.

**AND THE BOARD IS DORMANT, WHICH IS NOT THE SAME AS BROKEN.** *Measured 2026-10-01: the ids descend,
so the first page carries the newest adverts — and **every advert on it is dated 2026-07-09 with
`validThrough` 2026-08-23**, twelve weeks old and six weeks expired.* **The route works; the site has
stopped publishing.** The run says so, with the board's own `datePosted` as the bound rather than an
inference of ours — *a dormant board is this repository's fourth state, and reporting it as an empty
or broken one would be a claim about our tooling disguised as a claim about the market.*

**WITHHELD:** e-mail addresses and telephone numbers in the description. **There is no salary field
anywhere in this payload**, so neither the `baseSalary.currency` rule nor the telephone-digits rule
has anything to act on — said so that their absence reads as measured rather than forgotten.

`--country-code` STAMPS. Titles and descriptions are Turkish and are not translated.

**COST OF A FULL RUN:** 17 list pages + one request an advert = **407 requests at 2 s, about 14
minutes**. `--max` bounds it, and under `--max` the run states nothing about what the board holds.

Measured 2026-10-01 by the declared client, the guard on each exact path: `/is-ilanlari` 200,
374 788 B, 24 adverts; `?sayfa=2` 200, 386 467 B, 24, **no overlap with page 1**; `?sayfa=17` 200,
271 426 B, **6**; `?sayfa=18` 200, 232 719 B, **0 — the walk's end**; one advert 256 092 B with 2
`ld+json` blocks, the `JobPosting` giving `datePosted` 2026-07-09 and `validThrough` 2026-08-23.
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

HOST = "kktcportal.net"
LISTE = "/is-ilanlari"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
SLUG_RE = re.compile(r'/is-ilanlari/([a-z0-9-]+-\d+)["\'/]')
LD_RE = re.compile(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[kktcportal] {msg}", file=sys.stderr)


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
    gate(url)                                   # sur le CHEMIN exact, hote compris
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # aucun Crawl-delay ecrit
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def text(x):
    """Le texte d'un champ, l'ELEMENT `<i>` retire et non sa seule balise.

    Une police d'icones met son glyphe DANS l'element — retirer la balise seule
    le laisse dans le texte, ou il se lit comme un caractere de la langue du site.
    136 adaptateurs sur 138 portent encore ce defaut (`shared/boards/README.md`).
    """
    if not isinstance(x, str):
        return None
    t = re.sub(r"<i\b[^>]*>.*?</i>", " ", x, flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>|</p>|</li>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmlmod.unescape(t).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def posting_de(markup):
    """Le bloc qui se DECLARE `JobPosting`, choisi par son `@type`.

    La page en porte DEUX : l'un est une paire `Organization` + `WebSite`. Choisir
    par la position marcherait aujourd'hui et casserait le jour ou l'ordre change
    — et ce jour-la le champ serait vide sans que rien ne leve.
    """
    for bloc in LD_RE.findall(markup or ""):
        try:
            d = json.loads(bloc)
        except ValueError:
            continue
        for o in (d if isinstance(d, list) else [d]):
            if isinstance(o, dict) and o.get("@type") == "JobPosting":
                return o
    return {}


def slugs_de(markup):
    return list(dict.fromkeys(SLUG_RE.findall(markup or "")))


def lieu_de(ld):
    a = ld.get("jobLocation")
    a = a.get("address") if isinstance(a, dict) else None
    if not isinstance(a, dict):
        return None
    parts = [a.get(k) for k in ("addressLocality", "addressRegion", "addressCountry")]
    return ", ".join(text(p) or "" for p in parts if isinstance(p, str) and p.strip()) or None


def record(slug, ld, stamp):
    org = ld.get("hiringOrganization") if isinstance(ld.get("hiringOrganization"), dict) else {}
    ident = slug.rsplit("-", 1)[-1]
    return {
        "source": "kktcportal", "country": stamp,
        "ledger_id": f"kktcportal:{ident}", "id": ident,
        "url": ld.get("url") or f"https://{HOST}{LISTE}/{slug}",
        "slug": slug,
        "title": scrub(text(ld.get("title"))),
        "employer": scrub(text(org.get("name"))),
        "location": lieu_de(ld),
        "employment_type": text(ld.get("employmentType")),
        "posted": ld.get("datePosted"),
        # **Porte meme quand il est passe** : le board liste des annonces expirees, et
        # les jeter remplacerait sa declaration par la notre.
        "valid_through": ld.get("validThrough"),
        "description": scrub(text(ld.get("description"))),
        "contacts_withheld": True,
    }


def enumerer(a):
    """Les annonces, page apres page, jusqu'a une page qui n'en porte aucune.

    Mesure le 2026-10-01 : page 1 et page 2 ne partagent AUCUNE annonce, la 17 en
    porte 6, la 18 aucune. **Le controle de repetition est garde quand meme** : il
    coute une comparaison, et c'est de son absence que la famille clamp/crush/reset
    est faite.
    """
    tous, vus, page, fin = [], set(), 0, None
    while True:
        page += 1
        q = f"?sayfa={page}" if page > 1 else ""
        url = f"https://{HOST}{LISTE}{q}"
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
        slugs = slugs_de(body)
        if not slugs:
            fin = ("page vide", page)
            break
        neufs = [s for s in slugs if s not in vus]
        if page > 1 and not neufs:
            # **Le pager se REPETE** : on s'arrete plutot que de boucler, et on le DIT.
            die(f"page {page} repeats what page {page - 1} served and adds nothing"
                f" — the pager stopped advancing; {th(len(tous))} read before that",
                EXIT_PARTIAL)
        for s in neufs:
            vus.add(s)
            tous.append(s)
        if a.max_pages and page >= a.max_pages:
            fin = ("--max-pages", page)
            break
    return tous, page, fin


def cmd_jobs(a):
    if a.max is not None and a.max < 0:
        die("--max: a count, or 0 for every advert the pager serves")
    stamp = a.country_code.upper() if a.country_code else None

    slugs, pages, fin = enumerer(a)
    if not slugs:
        die(f"{LISTE}: 200 but the first page lists no advert — the page changed shape;"
            f" this is not an empty board", EXIT_PARTIAL)
    note(f"{th(len(slugs))} advert(s) enumerated over {th(pages - (1 if fin and fin[0] == 'page vide' else 0))}"
         f" page(s); the walk ended on {fin[0] if fin else 'the last page'}."
         f" **No count is stated anywhere**: this is what the pager SERVED, not what the site claims.")

    rows, manques, sans_ld, expirees = [], 0, 0, 0
    plus_recent = None          # pour distinguer un board DORMANT d'une route cassee
    for slug in slugs:
        if a.max and len(rows) >= a.max:
            break
        url = f"https://{HOST}{LISTE}/{slug}"
        code, page = request(url)
        if code != 200:
            manques += 1
            note(f"{slug}: HTTP {code} — advert skipped")
            continue
        ld = posting_de(page)
        if not ld:
            sans_ld += 1
            note(f"{slug}: no ld+json block declaring \"@type\":\"JobPosting\"")
            continue
        r = record(slug, ld, stamp)
        vt = r.get("valid_through")
        if isinstance(vt, str) and vt[:10] < a.today:
            expirees += 1
        dp = r.get("posted")
        if isinstance(dp, str) and (plus_recent is None or dp > plus_recent):
            plus_recent = dp
        rows.append(r)
        print(json.dumps(r, ensure_ascii=False))     # AU FIL DE L'EAU

    plafonne = bool(a.max and len(rows) >= a.max)
    note(f"{th(len(rows))} emitted"
         + (f", {th(manques)} unreachable" if manques else "")
         + (f", {th(sans_ld)} carrying no JobPosting block" if sans_ld else "")
         + (" — stopped by --max." if plafonne else " — every advert the pager served."))
    if expirees:
        note(f"{th(expirees)} emitted advert(s) state a `validThrough` already past on {a.today}"
             f" (UTC) — **the board's own filing, emitted and never dropped in silence**: it lists"
             f" them, and discarding them would replace its statement with ours.")
    if rows and expirees == len(rows):
        # **DORMANT, ce qui n'est pas CASSE** : la route fonctionne, le board ne publie plus.
        # Les ids descendent, donc la premiere page porte les plus recents : le `datePosted`
        # le plus eleve lu BORNE la fraicheur du board, et il n'est pas de nous.
        note(f"**EVERY advert emitted this run is past its `validThrough`, and the newest"
             f" `datePosted` read is {plus_recent}.** Ids descend, so the first page carries the"
             f" newest: this board is DORMANT, not broken — the route works and the site has"
             f" stopped publishing. *That is a statement about the board, dated, and it is the"
             f" board's own `datePosted` rather than an inference of ours.* A session re-running"
             f" this adapter later should expect the same until that date moves.")
    note("the advert's ld+json block is chosen by its `@type` and never by its position: the page"
         " carries two, the other being an Organization/WebSite pair.")
    note("the 2026-09-18 card reported aberrant list dates («26/05/1779»); measured today the list"
         " markup carries NO date at all, so the date comes from the advert's `datePosted`.")
    note("no salary field exists in this payload, so neither the baseSalary.currency rule nor the"
         " telephone-digits rule has anything to act on; said so that their absence reads as"
         " measured rather than forgotten.")
    if stamp:
        note(f"country {stamp} is the user's stamp.")
    if plafonne:
        note("stopped by --max, so NOTHING here is said about what the board holds: the figures"
             " above describe this run's cap, not the pager's verdict.")
    elif len(rows) + manques + sans_ld != len(slugs):
        die(f"{len(rows)} + {manques} + {sans_ld} != {len(slugs)} enumerated"
            f" — advert(s) dropped in silence", EXIT_PARTIAL)


def main(argv=None):
    import datetime
    p = argparse.ArgumentParser(
        description="KKTC Portal (Northern Cyprus) — the pager advances, the walk ends on an empty "
                    "page, and no count is stated. Issue #724.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the pager, then one request an advert")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on every record (the board states none)")
    j.add_argument("--max", type=int, default=0,
                   help="stop after N adverts (0 = every advert the pager serves)")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0,
                   help="stop enumerating after N list pages (0 = until a page is empty)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    a.fn(a)


if __name__ == "__main__":
    main()
