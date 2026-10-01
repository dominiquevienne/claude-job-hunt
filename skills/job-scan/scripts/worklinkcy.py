#!/usr/bin/env python3
"""Work Link (`www.worklinkcy.com`), Northern Cyprus: **a clamped pager holding 12 and a feed holding 20 that overlap in FOUR — and their union is exactly the 28 the board states.** Issue #722.

  worklinkcy.py jobs [--country-code CY] [--max N]    the pager and the feed, then one request an advert

WHAT IT IS. A bilingual board (`/tr/`, `/en/`). Northern Cyprus's other named boards are `iskibris`
(#719, delivered), `kktcportal` (#724, delivered), `kibriseleman`, `kibristailan`, `kariyerkktc`,
`ekonomikibris`, `iscikler` and the Labour Department.

THE RULES. `www.worklinkcy.com` serves its rules file (`state: read`, `certain: True`) on `/`,
`/tr/jobs` and `/tr/feed/jobs`, and writes **no Crawl-delay**; 2 s are ours.

**THE PAGER IS CLAMPED, AND IT ADVERTISES PAGES IT WILL NOT SERVE.** *`?page=2`, `?page=3` and
`?page=4` each return the SAME 12 slugs and the same «&nbsp;Showing 1 – 12 of 28 results&nbsp;».* The page
renders pager links, which is what made the 2026-09-18 reading record «&nbsp;pager `?page=2`,
`?page=3`&nbsp;» — **a pager one can see is not a pager that advances**, and only asking for page 2 and
comparing the identifiers tells them apart.

**AND THE FEED IS NOT THE INVENTORY EITHER.** `/tr/feed/jobs` is RSS 2.0 with **20 `<item>`**. *A feed
usually claims completeness; this one holds 20 of 28 and misses 8 that the clamped page 1 carries.*

    pager, page 1 (all pages identical)   12 slugs
    feed /tr/feed/jobs                    20 slugs
    intersection                           4
    pager only 8  ·  feed only 16
    UNION                                 28   ==   «Showing 1 – 12 of 28 results»

> **Third time in three days that two enumerators of one board neither contain nor equal each other**
> — Lambda 50 against 30 (#661), İş Kıbrıs 12 against 12 (#719), and here 12 against 20 overlapping
> in four. **It is a form, not three accidents.** *And this is the sharpest case: a FEED, the artefact
> most likely to be taken for the inventory, is the one missing a third of the board.*

**WHAT IS NEW HERE IS THAT THE UNION IS VERIFIABLE.** *On the first two boards no total was stated, so
the honest report was «&nbsp;the board's size is not established&nbsp;».* **This board states 28, and the
union of the two enumerators is exactly 28** — so the run asserts it, and says so when it fails.
*Intersecting enumerators is not prudence here: it is what achieves completeness, and the board's own
count is what proves it.*

**THE SALARY IS A TEMPLATE DEFAULT, AND CARRYING IT WOULD INVENT ONE.** *The advert's `JobPosting`
declares `baseSalary: {"currency": "EUR", "minValue": null, "maxValue": null, "unitText": "MONTHLY"}`
— a currency on an amount that does not exist — and the rendered page prints no salary at all.*
**A currency without a value is not a salary**, so nothing is carried: emitting `EUR` would declare a
figure the board never published, on every advert. *This is `baseSalary.currency` again (#638/#655),
in a third variant: there the currency was WRONG, here there is nothing for it to be wrong about.*

**AND THE TWO SOURCES DISAGREE ON THE DATE BY FIVE MONTHS.** *For `/tr/jobs/barber`: the advert's
`datePosted` reads **2025-10-03** (with `validThrough` 2025-11-17), the feed's `pubDate` reads **Tue,
10 Mar 2026**.* **Neither is adjudicated here.** Both travel, each named by its source — `posted` from
the advert, `feed_published` from the feed — and the run counts the disagreements. *Picking one
silently would publish a date whose provenance nobody could recover; and the two together are the
finding.*

**WITHHELD:** e-mail addresses and telephone numbers in the description. The telephone rule is safe
here because **there is no salary field to protect**: nothing in the payload carries an amount.

`--country-code` STAMPS. The Turkish front is read; `/en/jobs` serves the same adverts under the same
slugs and is not fetched twice.

Measured 2026-10-01 by the declared client, the guard on each exact path: `/tr/jobs` 200, 357 314 B,
12 slugs, «Showing 1 – 12 of 28 results»; `?page=2`, `?page=3`, `?page=4` each 12 slugs **identical to
page 1**; `/tr/feed/jobs` 200, 18 846 B, RSS with 20 `<item>`; one advert 86 376 B with **3** `ld+json`
blocks (`BreadcrumbList`, `WebSite`, `JobPosting`).
"""

import argparse
import email.utils
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

HOST = "www.worklinkcy.com"
LISTE = "/tr/jobs"
FLUX = "/tr/feed/jobs"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
SLUG_RE = re.compile(r"/(?:tr|en)/jobs/([a-z0-9][a-z0-9-]{2,})")
ENONCE_RE = re.compile(r"(\d+)\s*[–-]\s*(\d+)\s+of\s+(\d+)\s+results", re.I)
LD_RE = re.compile(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
ITEM_RE = re.compile(r"<item>(.*?)</item>", re.S)
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[worklinkcy] {msg}", file=sys.stderr)


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
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # aucun Crawl-delay ecrit
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/rss+xml"})
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
    """Le texte d'un champ, l'ELEMENT `<i>` retire et non sa seule balise."""
    if not isinstance(x, str):
        return None
    t = re.sub(r"<i\b[^>]*>.*?</i>", " ", x, flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>|</p>|</li>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmlmod.unescape(t).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def cdata(bloc, tag):
    m = re.search(r"<%s[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</%s>" % (tag, tag), bloc or "", re.S)
    return text(m.group(1)) if m else None


def posting_de(markup):
    """Le bloc qui se DECLARE `JobPosting` — la page en porte TROIS."""
    for bloc in LD_RE.findall(markup or ""):
        try:
            d = json.loads(bloc)
        except ValueError:
            continue
        for o in (d if isinstance(d, list) else [d]):
            if isinstance(o, dict) and o.get("@type") == "JobPosting":
                return o
    return {}


def salaire_de(ld):
    """**Rien, quand il n'y a rien** — et c'est le cas sur tout ce board.

    `baseSalary` y vaut `{"currency": "EUR", "minValue": null, "maxValue": null}`&nbsp;:
    une monnaie posee sur un montant qui n'existe pas, et la page rendue n'imprime
    aucun salaire. **Emettre «&nbsp;EUR&nbsp;» declarerait un chiffre que le board n'a jamais
    publie, sur chacune de ses annonces.** *Une monnaie sans valeur n'est pas un
    salaire&nbsp;: c'est un defaut de gabarit.* Troisieme variante de la regle #638/#655
    — la monnaie y etait FAUSSE, ici il n'y a rien dont elle puisse etre fausse.
    """
    bs = ld.get("baseSalary")
    if not isinstance(bs, dict):
        return None, False
    v = bs.get("value") if isinstance(bs.get("value"), dict) else bs
    bas, haut, un = v.get("minValue"), v.get("maxValue"), v.get("value")
    for x in (un, bas, haut):
        if x not in (None, "", []):
            # un montant EXISTE : on porte la chaine, jamais la monnaie
            if bas not in (None, "") and haut not in (None, "") and bas != haut:
                return f"{bas} - {haut}", True
            return str(x), True
    return None, bool(bs.get("currency"))     # vide, mais une monnaie etait posee


def lieu_de(ld):
    a = ld.get("jobLocation")
    a = a.get("address") if isinstance(a, dict) else None
    if not isinstance(a, dict):
        return None
    # Le champ du site porte sa propre ponctuation — `addressLocality` vaut
    # « Nicosia, » — et joindre tel quel rend « Nicosia,, TRNC ». On retire la
    # ponctuation de bord de CHAQUE part : c'est de la mise en forme, pas une
    # correction de la donnee, et le contenu reste celui du board.
    parts = [text(a.get(k)) for k in ("addressLocality", "addressRegion", "addressCountry")]
    parts = [x.strip(" ,;·") for x in parts if x and x.strip(" ,;·")]
    return ", ".join(parts) or None


def record(slug, ld, flux_date, origine, stamp):
    org = ld.get("hiringOrganization") if isinstance(ld.get("hiringOrganization"), dict) else {}
    sal, gabarit = salaire_de(ld)
    return {
        "source": "worklinkcy", "country": stamp,
        "ledger_id": f"worklinkcy:{slug}", "id": slug,
        "url": ld.get("url") or f"https://{HOST}{LISTE}/{slug}",
        "title": scrub(text(ld.get("title"))),
        "employer": scrub(text(org.get("name"))),
        "employer_url": org.get("url") or None,
        "location": lieu_de(ld),
        "employment_type": text(ld.get("employmentType")),
        # **Les deux dates, chacune NOMMEE par sa source** : elles divergent de mois,
        # et choisir en silence publierait une date dont personne ne pourrait
        # retrouver la provenance.
        "posted": ld.get("datePosted"),
        "feed_published": flux_date,
        "valid_through": ld.get("validThrough"),
        "salary": sal,                       # None partout sur ce board, et c'est mesure
        "salary_currency_without_amount": gabarit,
        "enumerated_by": origine,
        "description": scrub(text(ld.get("description"))),
        "contacts_withheld": True,
    }


def du_pager(a):
    """La page 1, et la PREUVE que le pager ne bouge pas.

    On demande la page 2 une fois : si elle rend les memes identifiants, le pager est
    verrouille et on s'arrete la — *un pager qu'on VOIT n'est pas un pager qui avance.*
    """
    code, p1 = request(f"https://{HOST}{LISTE}")
    if code != 200:
        die(f"{LISTE}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    s1 = list(dict.fromkeys(SLUG_RE.findall(p1)))
    if not s1:
        die(f"{LISTE}: 200 but no advert slug — the page changed shape;"
            f" this is not an empty board", EXIT_PARTIAL)
    m = ENONCE_RE.search(p1)
    enonce = int(m.group(3)) if m else None
    verrou = None
    if not a.no_clamp_check:
        code, p2 = request(f"https://{HOST}{LISTE}?page=2")
        if code == 200:
            s2 = list(dict.fromkeys(SLUG_RE.findall(p2)))
            verrou = bool(s2) and set(s2) == set(s1)
    return s1, enonce, verrou


def du_flux():
    code, body = request(f"https://{HOST}{FLUX}")
    if code != 200:
        note(f"{FLUX}: HTTP {code} — the feed is not readable this run")
        return [], {}
    slugs, dates = [], {}
    for it in ITEM_RE.findall(body):
        lk = re.search(r"<link[^>]*>(.*?)</link>", it, re.S)
        if not lk:
            continue
        sl = SLUG_RE.search(lk.group(1))
        if not sl:
            continue
        s = sl.group(1)
        if s not in dates:
            slugs.append(s)
        pd = re.search(r"<pubDate[^>]*>(.*?)</pubDate>", it, re.S)
        if pd:
            try:
                dates[s] = email.utils.parsedate_to_datetime(pd.group(1).strip()).isoformat()
            except (TypeError, ValueError):
                dates[s] = pd.group(1).strip()
        else:
            dates[s] = None
    return slugs, dates


def cmd_jobs(a):
    if a.max is not None and a.max < 0:
        die("--max: a count, or 0 for every advert the two enumerators name")
    stamp = a.country_code.upper() if a.country_code else None

    pager, enonce, verrou = du_pager(a)
    flux, flux_dates = du_flux()

    union, origine = [], {}
    for source, lot in (("pager", pager), ("feed", flux)):
        for s in lot:
            if s in origine:
                origine[s] += "+" + source
                continue
            origine[s] = source
            union.append(s)
    commun = sum(1 for v in origine.values() if "+" in v)

    note(f"the enumerators: the pager serves {th(len(pager))}, the feed {th(len(flux))},"
         f" {th(commun)} in common, **{th(len(union))} distinct**.")
    if verrou:
        note("**THE PAGER IS CLAMPED**: `?page=2` returned the same identifiers as page 1."
             " A pager one can SEE is not a pager that advances, and only asking for page 2 and"
             " comparing the identifiers tells them apart.")
    elif verrou is False:
        note("the pager ADVANCED this run (page 2 differs from page 1) — it was clamped on"
             " 2026-10-01, so this walk is now incomplete: extend it to follow the pages.")
    if enonce is None:
        note("the page states no total this run — it stated «of 28» on 2026-10-01, so the"
             " witness below is unavailable and the union is all we have.")
    elif len(union) == enonce:
        note(f"**the board states {th(enonce)} and the union is exactly {th(len(union))}** — so the"
             f" two enumerators TOGETHER are complete, and that is verified rather than assumed."
             f" *Neither alone reaches it: the pager is {th(len(pager))}, the feed {th(len(flux))}.*")
    else:
        note(f"**the board states {th(enonce)} and the union is {th(len(union))}** — they do not"
             f" agree, so the union is NOT complete and something enumerates adverts that neither"
             f" the pager nor the feed carries.")

    rows, manques, sans_ld, desaccords, gabarits = [], 0, 0, 0, 0
    for slug in union:
        if a.max and len(rows) >= a.max:
            break
        code, page = request(f"https://{HOST}{LISTE}/{slug}")
        if code != 200:
            manques += 1
            note(f"{slug}: HTTP {code} — advert skipped")
            continue
        ld = posting_de(page)
        if not ld:
            sans_ld += 1
            note(f"{slug}: no ld+json block declaring \"@type\":\"JobPosting\" (the page carries three)")
            continue
        r = record(slug, ld, flux_dates.get(slug), origine[slug], stamp)
        if r["posted"] and r["feed_published"] and r["posted"][:10] != r["feed_published"][:10]:
            desaccords += 1
        if r["salary_currency_without_amount"]:
            gabarits += 1
        rows.append(r)
        print(json.dumps(r, ensure_ascii=False))     # AU FIL DE L'EAU

    plafonne = bool(a.max and len(rows) >= a.max)
    note(f"{th(len(rows))} emitted"
         + (f", {th(manques)} unreachable" if manques else "")
         + (f", {th(sans_ld)} carrying no JobPosting block" if sans_ld else "")
         + (" — stopped by --max." if plafonne else " — every advert the two enumerators name."))
    if desaccords:
        note(f"**{th(desaccords)} advert(s) carry two dates that DISAGREE** — the advert's own"
             f" `datePosted` against the feed's `pubDate`, five months apart on the first one"
             f" measured. **Neither is adjudicated here**: both travel, each named by its source,"
             f" because picking one silently would publish a date whose provenance nobody could"
             f" recover — and the disagreement is itself the finding.")
    if gabarits:
        note(f"**{th(gabarits)} advert(s) declare a `baseSalary` currency with NO amount** —"
             f" `minValue` and `maxValue` null, and the rendered page prints no salary. *A currency"
             f" without a value is not a salary but a template default*, so nothing is carried:"
             f" emitting it would declare a figure the board never published.")
    if plafonne:
        note("stopped by --max, so nothing above describes what the board holds beyond this cap.")
    elif len(rows) + manques + sans_ld != len(union):
        die(f"{len(rows)} + {manques} + {sans_ld} != {len(union)} enumerated"
            f" — advert(s) dropped in silence", EXIT_PARTIAL)
    if stamp:
        note(f"country {stamp} is the user's stamp.")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Work Link (Northern Cyprus) — a clamped pager of 12 and a feed of 20 "
                    "overlapping in four, whose union is exactly the 28 the board states. "
                    "Issue #722.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the pager and the feed, then one request an advert")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on every record (the board states none)")
    j.add_argument("--max", type=int, default=0,
                   help="stop after N adverts (0 = every advert the enumerators name)")
    j.add_argument("--no-clamp-check", dest="no_clamp_check", action="store_true",
                   help="skip the one extra request that proves the pager does not advance")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
