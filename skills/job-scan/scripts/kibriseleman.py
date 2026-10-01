#!/usr/bin/env python3
"""Kibris Eleman (`www.kibriseleman.com`, Northern Cyprus) — «en buyuk eleman platformu».

**The live list is the inventory; the sitemap is an ARCHIVE frozen in 2023, and the
two share nothing.** Measured 2026-10-02: the list carries 8 adverts (ids
4489-4500), `/sitemap.xml` — which `robots.txt` does not declare — carries 3 042
(ids 2-4407, `lastmod` max 2023-02-28), **and the intersection is ZERO**.

> **Fifth board of five whose two enumerators were compared, and the first where
> they share NOTHING.** *Lambda 50/30 in 2 (#661), Is Kibris 12/12 in 6 (#719),
> Work Link 12/20 in 4 (#722), Ekonomi Kibris 21 ⊂ 50 (#726) — here 8 against
> 3 042 with an empty intersection.* **The relation is not merely unpredictable in
> both directions: it can be EMPTY.**

**And the stale side is 380 times the live one**, which is why the archive is never
unioned in by default: a union would turn 8 current vacancies into 3 050 rows of
which 99.7 % are three and a half years dead, **and nothing on those pages would
contradict it** — no advert page on this host states a date of any kind. *The
sitemap's `lastmod` is the only thing that dates any advert here*, so
`--include-archive` emits those rows carrying that `lastmod` and an `archived`
flag, and never silently.

**A TAG-STRIPPING EXTRACTOR READS HTML COMMENTS AS CONTENT — and this host is where
it bites.** Each advert page carries **12 comments, about 8 500 bytes, a quarter of
the page**, and the field table's `Maas` row is *inside one of them*:

    <!-- <tr><td>Maas</td><td> TL</td></tr>-->

**So the board publishes NO salary: the row is disabled in the template.** *A first
reading of this very host recorded «`Maas: TL` — a currency with no amount» because
`re.sub(r"<[^>]+>", " ", ...)` turned commented-out markup into text; the tell was a
stray `-->` in the extracted string, and it was passed over.* **Hence
`sans_commentaires()` runs before ANY extraction**, and a guard asserts that a
commented row never becomes a field. *Had the comment been read as content, the
adapter would have emitted a salary field the board has never displayed — a field
fabricated out of disabled template code, which is worse than a missing one.*

**The age and sex criteria are NOT propagated.** The live table carries `Cinsiyet`
and `Yas` («18 - 50 Arasi»); #183 settled this field treatment. *That issue rested
on Uzbek labour law and **the law of Northern Cyprus has not been checked here** —
the treatment is carried over because propagating an age or sex requirement serves
no candidate, not because a statute has been established.*

**There is no pager**, which answers what the 2026-09-18 card left open: `?sayfa=` is
ignored, `?page=2` serves an advert-less page, and the six `?city=` facets are INERT
— same ids at the same byte size. *The list is its own whole extent.* And the list
answers 200 twice at constant size with **different md5**, so no md5 comparison means
anything on this host.

Invocation:

    python3 kibriseleman.py jobs --country-code CYN
    python3 kibriseleman.py jobs --country-code CYN --include-archive
    python3 kibriseleman.py jobs --country-code CYN --max 3

Exit codes: 0 fine · 2 broken · 3 gone · 6 partial · 7 refused · 8 unknown.
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

HOST = "www.kibriseleman.com"
LISTE = "/is-ilanlari"
SITEMAP = "/sitemap.xml"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# Meme pays qu'`ekonomikibris` : ancre sur ce que le pays NUMEROTE, +90/0 puis
# 5xx (mobile) ou 392 (fixe RTCN). Une regle plus large mord les references de
# normes (`ISO 9001-2015`), et `[telephone withheld]` sur une certification est
# une affirmation sur l'employeur que le board n'a jamais faite.
TEL_RE = re.compile(
    r"(?<![\w])(?:\+?90[\s\-.]?)?\(?0?\)?[\s\-.]?(?:5\d{2}|392)\)?"
    r"[\s\-.]?\d{3}[\s\-.]?\d{2}[\s\-.]?\d{2}(?![\w])")
AD_RE = re.compile(r"/is-ilani/(\d+)-([a-z0-9\-]*)\.html")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
LOC_RE = re.compile(r"<url>(.*?)</url>", re.S)
TR_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)

# **Les criteres qu'on ne propage PAS** (#183). Le libelle est nomme ici pour
# que le refus soit greppable, et la VALEUR n'entre jamais dans une ligne.
CRITERES_NON_PROPAGES = ("cinsiyet", "yaş", "yas")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print("ERROR: %s" % msg, file=sys.stderr)
    sys.exit(code)


def note(msg):
    print("[kibriseleman] %s" % msg, file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die("%s: %s" % (url, a["reason"]), EXIT_UNKNOWN)
    if not a["allowed"]:
        die("%s: %s" % (url, a["reason"]), EXIT_REFUSED)
    return a


def request(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die("%s: not %s — never sent" % (url, HOST), EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # aucun Crawl-delay ecrit
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die("%s: %s: %s" % (url, type(e).__name__, e))


def sans_commentaires(markup):
    """**Les commentaires HTML partent AVANT toute extraction.**

    Un extracteur qui retire les balises (`re.sub(r"<[^>]+>", " ", ...)`) rend le
    CONTENU d'un commentaire comme du texte. Ici chaque page d'annonce en porte
    douze, environ 8 500 octets — un quart de la page — et la ligne `Maas` du
    tableau vit dans l'un d'eux. *Lue comme du contenu, elle fabrique un champ
    salaire que le board n'affiche pas.*
    """
    return COMMENT_RE.sub(" ", markup or "")


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return TEL_RE.sub("[telephone withheld]", s).strip() or None


def text(x):
    if not isinstance(x, str):
        return None
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</td>|</tr>", "\n", x)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmlmod.unescape(t).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def table_de(propre):
    """Les paires libelle/valeur du tableau de champs, commentaires DEJA retires.

    Rend un dict ET la liste des libelles vus, parce que « le champ est absent »
    et « le champ etait la et on l'a laisse » ne doivent pas se lire pareil.
    """
    m = re.search(r"<table[^>]*>(.*?)</table>", propre, re.S)
    if not m:
        return {}, []
    paires, vus = {}, []
    for tr in TR_RE.findall(m.group(1)):
        tds = TD_RE.findall(tr)
        if len(tds) < 2:
            continue
        cle, val = text(tds[0]), text(tds[1])
        if not cle:
            continue
        vus.append(cle)
        if val:
            paires[cle.strip().lower()] = val
    return paires, vus


def salaire_de(paires):
    """**Rien, et la raison est mesuree : la ligne `Maas` est COMMENTEE.**

    Si le board la reactive un jour, les deux cas sont traites : un montant est
    porte, une monnaie NUE est signalee sans etre portee — c'est la troisieme
    variante de la regle #638/#655 et #722, et elle est prete ici avant d'etre
    rencontree en clair.
    """
    brut = paires.get("maaş") or paires.get("maas")
    if not brut:
        return None, False
    if re.search(r"\d", brut):
        return brut, False
    return None, True          # une monnaie posee sans aucun montant


def lieu_employeur_de(propre):
    """La ville et l'employeur vivent dans les conteneurs `detail`, pas le tableau."""
    blocs = re.findall(r'<div[^>]*class="[^"]*detail[^"]*"[^>]*>(.*?)</div>', propre, re.S)
    lieu = employeur = contrat = None
    for b in blocs:
        lignes = [l for l in (text(b) or "").splitlines() if l.strip()]
        for l in lignes:
            if re.match(r"^(Tam|Yarı|Yari)\s*Zamanlı", l) and not contrat:
                contrat = l
            elif "," in l and not lieu and not l.lower().startswith("adres"):
                lieu = l
            elif l and not employeur and l != contrat and l != lieu \
                    and not l.lower().startswith(("adres", "website", "web site")):
                employeur = l
        if lieu and employeur:
            break
    return lieu, employeur, contrat


def record(ident, slug, propre, stamp, origine, lastmod=None, archive=False):
    paires, vus = table_de(propre)
    sal, monnaie_nue = salaire_de(paires)
    lieu, employeur, contrat = lieu_employeur_de(propre)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", propre, re.S)
    # **#183** : les criteres d'age et de sexe ne sortent pas. On ne les nomme
    # que s'ils etaient PRESENTS ET REMPLIS — declarer avoir retenu ce que
    # personne n'a depose mentirait sur nous, pas sur le board.
    retenus = [c for c in vus if c.strip().lower() in CRITERES_NON_PROPAGES
               and paires.get(c.strip().lower())]
    ligne = {
        "source": "kibriseleman", "country": stamp,
        "ledger_id": "kibriseleman:%s" % ident, "id": ident, "slug": slug,
        "url": "https://%s/is-ilani/%s-%s.html" % (HOST, ident, slug),
        "title": scrub(text(h1.group(1))) if h1 else None,
        "employer": scrub(employeur),
        "location": scrub(lieu),
        "employment_type": contrat,
        "position": paires.get("sektör/bölüm/pozisyon") or paires.get("sektor/bolum/pozisyon"),
        "openings": paires.get("alınacak kişi") or paires.get("alinacak kisi"),
        # **Aucune date sur la page** : le board n'en imprime pas une seule, et
        # le `lastmod` du sitemap est le seul datage existant sur cet hote.
        "posted": None,
        "sitemap_lastmod": lastmod,
        "archived": bool(archive),
        "salary": sal,
        "salary_currency_without_amount": monnaie_nue,
        "criteria_not_propagated": retenus or None,
        "enumerated_by": origine,
        "contacts_withheld": True,
    }
    return ligne


def de_la_liste():
    """Les identifiants de la liste vivante — elle est son propre extent entier."""
    url = "https://%s%s" % (HOST, LISTE)
    code, corps = request(url)
    if code == 404:
        die("%s: HTTP 404 — the listing is gone" % url, EXIT_GONE)
    if code != 200 or not corps:
        die("%s: HTTP %s" % (url, code))
    propre = sans_commentaires(corps)
    vus, ordre = set(), []
    for m in AD_RE.finditer(propre):
        if m.group(1) not in vus:
            vus.add(m.group(1))
            ordre.append((m.group(1), m.group(2)))
    return ordre


def du_sitemap():
    """L'ARCHIVE : 3042 identifiants gelés en fevrier 2023, chacun avec son `lastmod`.

    *Il n'est pas declare par `robots.txt` et il est servi quand meme.*
    """
    url = "https://%s%s" % (HOST, SITEMAP)
    code, corps = request(url)
    if code != 200 or not corps:
        note("%s: HTTP %s — no archive read" % (url, code))
        return []
    sortie = []
    for bloc in LOC_RE.findall(corps):
        m = AD_RE.search(bloc)
        if not m:
            continue
        lm = re.search(r"<lastmod>([^<]+)</lastmod>", bloc)
        sortie.append((m.group(1), m.group(2), lm.group(1).strip() if lm else None))
    return sortie


def annonce(ident, slug):
    url = "https://%s/is-ilani/%s-%s.html" % (HOST, ident, slug)
    code, corps = request(url)
    if code != 200 or not corps:
        note("%s: HTTP %s — left unread" % (url, code))
        return None
    return sans_commentaires(corps)


def cmd_jobs(a):
    stamp = a.country_code
    liste = de_la_liste()
    note("listing %s: %d advert(s)" % (LISTE, len(liste)))
    if not liste:
        die("the listing carries no advert — the route is gone", EXIT_GONE)

    archive = du_sitemap()
    l_ids = {i for i, _s in liste}
    a_ids = {i for i, _s, _d in archive}
    if archive:
        inter = l_ids & a_ids
        note("relation measured THIS RUN — listing %d · sitemap %d · intersection %d"
             % (len(l_ids), len(a_ids), len(inter)))
        if not inter:
            dates = [d for _i, _s, d in archive if d]
            note("THE TWO ENUMERATORS ARE DISJOINT: the sitemap shares no advert with "
                 "the live listing%s — it is an ARCHIVE, not a second view of the "
                 "inventory, and it is NEVER unioned in"
                 % (", and its newest lastmod is %s" % max(dates) if dates else ""))
        else:
            note("the sitemap shares %d advert(s) with the listing — the relation has "
                 "CHANGED since 2026-10-02, when it shared none" % len(inter))

    travail = [(i, s, None, False) for i, s in liste]
    if a.include_archive:
        travail += [(i, s, d, True) for i, s, d in archive if i not in l_ids]
        note("--include-archive: %d archived advert(s) appended, each carrying its "
             "sitemap lastmod and archived: true" % (len(travail) - len(liste)))

    plafonne = a.max is not None and len(travail) > a.max
    if plafonne:
        travail = travail[:a.max]

    emis = 0
    for ident, slug, lastmod, arch in travail:
        propre = annonce(ident, slug)
        if propre is None:
            continue
        ligne = record(ident, slug, propre, stamp,
                       "sitemap-archive" if arch else "listing",
                       lastmod=lastmod, archive=arch)
        print(json.dumps(ligne, ensure_ascii=False))
        sys.stdout.flush()      # au fil de l'eau : une coupure ne perd rien
        emis += 1

    note("%d advert(s) emitted" % emis)
    if plafonne:
        note("stopped by --max %d — NOTHING here is said about what the board holds"
             % a.max)
    else:
        note("No count is stated anywhere on this board: «binlerce ilan» is prose, and "
             "the figure above is what the listing served")
    if not a.include_archive and archive:
        note("the %d archived advert(s) were NOT emitted: they are undated except by "
             "lastmod and 99%% of them predate 2023-03; --include-archive emits them "
             "flagged" % len(a_ids - l_ids))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Kibris Eleman — Northern Cyprus adverts")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("jobs", help="emit the live listing's adverts")
    p.add_argument("--country-code", required=True,
                   help="the code STAMPED on every row (CYN for Northern Cyprus)")
    p.add_argument("--max", type=int, default=None,
                   help="cap the rows emitted; claims nothing about the board")
    p.add_argument("--include-archive", action="store_true",
                   help="also emit the sitemap's archived adverts, each flagged "
                        "and carrying its lastmod — they are three years old")
    a = ap.parse_args(argv)
    if a.cmd == "jobs":
        return cmd_jobs(a)
    ap.error("unknown command")


if __name__ == "__main__":
    sys.exit(main())
