#!/usr/bin/env python3
"""Ekonomi Kibris — «munhal duyurulari» (`www.ekonomikibris.com`, Northern Cyprus).

An economy newspaper's vacancy-notice section. **The notices are ARTICLES, not
`JobPosting`s**, and the route is the RSS feed.

**Four things this adapter exists to get right, and the first is the reason it
reads two enumerators instead of one.**

* **THE FEED CONTAINS THE PAGER — measured, and measured AGAIN at every run.**
  On 2026-10-02 `/is-ilanlari/` listed 21 notices, the feed carried 50, and the
  pager's 21 were ALL inside the feed: intersection 21, pager-only 0,
  feed-only 29. **This is the fourth board in this repository whose two
  enumerators were compared and the FIRST where one contains the other** —
  Lambda 50/30 intersecting in 2 (#661), Is Kibris 12/12 in 6 (#719), Work Link
  12/20 in 4 (#722), in none of which did either side hold the other.

  > *Three near-misses could have hardened into «never trust a feed», which is
  > the same error with the sign reversed.* **So containment is not assumed
  > here: the run reads both enumerators, intersects IDENTIFIERS, and says what
  > it found.** A pager-only identifier — none today — is fetched from its own
  > notice page rather than dropped, so the day the relation changes costs one
  > request per surprise instead of a silent loss.

* **the AJAX pager is CLAMPED.** The «Daha Fazla Getir» button posts to
  `/template/prime/news-category-ajax.php?katid=70&page=N`; pages 2, 3, 4 and 5
  each return 15 identifiers and **not one** the first page did not already
  carry. *`/is-ilanlari/page/2/` answers 404 and `?sayfa=2` is ignored.* **A
  pager one can SEE is not a pager that advances**, so the walk stops on the
  first page that adds nothing, and the stop is NAMED in the output.

* **the feed carries the whole body, so one request replaces fifty-one.**
  `content:encoded` holds the full article text; compared against the notice
  page's `articleBody` for one notice it agrees to 0.9986 with no differing run
  over twelve characters. *The adapter therefore reads bodies from the feed and
  SAYS so* — it does not claim the two are equal on all 50, which one comparison
  could not establish.

* **a `ld+json` block that RAISES is not a block that is absent.** When a notice
  page IS fetched, its third block — a `NewsArticle` — fails `json.loads` with
  «Invalid control character» on a raw newline inside a string and parses
  cleanly with `strict=False`. *The repository's decode lesson, inverted: there a
  broken decode returned TEXT and read like absent content; here a block that is
  present RAISES and reads like absent data.*

**And the withholding rule is anchored on what this country NUMBERS, because a
loose one misrepresents the board.** A pattern broad enough to catch a TRNC
landline (`0392 227 51 96`, in 2 of 50 bodies) also catches `9001-2015` and
`22000-2018` — **ISO standard references** — and `[telephone withheld]` stamped
over a quality certification is a claim about the employer that the board never
made. *Measured in both directions: the anchored rule bites the same 17 bodies,
splits `0548 838 10 53 / 0392 227 51 96` into the two numbers it is, and leaves
both ISO citations and `14.000m2` intact.* **That last figure is why no salary is
mined from the prose: the only money-shaped string in the corpus is a FLOOR AREA
in square metres.** This board states no salary anywhere, and the adapter carries
none rather than guess one out of free text.

**The section is DORMANT, which is not BROKEN.** All 50 items date between
2024-12-31 and 2025-01-06. *The route works and the section has stopped
publishing* — a statement about the board, bounded by the board's own newest
date, never by our clock alone.

Invocation:

    python3 ekonomikibris.py jobs --country-code CYN
    python3 ekonomikibris.py jobs --country-code CYN --max 5
    python3 ekonomikibris.py jobs --country-code CYN --feed-only

Exit codes: 0 fine · 2 broken · 3 gone · 6 partial · 7 refused · 8 unknown.
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

HOST = "www.ekonomikibris.com"
LISTE = "/is-ilanlari/"
FLUX = "/rss_is-ilanlari_70.xml"
AJAX = "/template/prime/news-category-ajax.php?katid=70&page=%d"
AJAX_MAX = 12                      # borne de securite : le pager mesure 5 et il est clampe

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# **Ancre sur ce que le pays NUMEROTE** : +90/0 puis 5xx (mobile) ou 392 (fixe
# RTCN). Une regle plus large mord `9001-2015` et `22000-2018` — des normes ISO —
# et imprimer `[telephone withheld]` sur une certification est une affirmation
# sur l'employeur que le board n'a jamais faite. Eprouvee dans les deux sens.
TEL_RE = re.compile(
    r"(?<![\w])(?:\+?90[\s\-.]?)?\(?0?\)?[\s\-.]?(?:5\d{2}|392)\)?"
    r"[\s\-.]?\d{3}[\s\-.]?\d{2}[\s\-.]?\d{2}(?![\w])")
# l'identite d'un avis est le segment NUMERIQUE de son adresse, jamais son slug
LIEN_RE = re.compile(r"https?://" + re.escape(HOST) + r"/([a-z0-9][a-z0-9\-]*)/(\d+)/")
ITEM_RE = re.compile(r"<item>(.*?)</item>", re.S)
LD_RE = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
# le board titre « <employeur> munhal duyurusu - Kibris is ilanlari »
TITRE_RE = re.compile(r"^(.*?)\s+m[uü]nhal\s+duyuru(?:su|lar[iı])\b", re.I)
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print("ERROR: %s" % msg, file=sys.stderr)
    sys.exit(code)


def note(msg):
    print("[ekonomikibris] %s" % msg, file=sys.stderr)


def th(n):
    return "{:,}".format(n).replace(",", " ")


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
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/rss+xml"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die("%s: %s: %s" % (url, type(e).__name__, e))


def scrub(s):
    """Les contacts ne sortent pas — et seulement les contacts (voir `TEL_RE`)."""
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return TEL_RE.sub("[telephone withheld]", s).strip() or None


def text(x):
    if not isinstance(x, str):
        return None
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>", "\n", x)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmlmod.unescape(t).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def balise(bloc, tag):
    m = re.search(r"<%s[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</%s>" % (tag, tag),
                  bloc or "", re.S)
    return m.group(1) if m else None


def ids_de(markup):
    """Les identifiants NUMERIQUES portes par un balisage, dans l'ordre vu."""
    vus, ordre = set(), []
    for m in LIEN_RE.finditer(markup or ""):
        ident, slug = m.group(2), m.group(1)
        if ident not in vus:
            vus.add(ident)
            ordre.append((ident, slug))
    return ordre


def instant(brut):
    """Une `pubDate` RFC 822 en ISO-8601, ou la chaine telle quelle si illisible.

    *On ne jette pas une date qu'on ne sait pas analyser : on la porte brute, et
    le lecteur voit ce que le board a ecrit.*
    """
    if not brut:
        return None
    try:
        d = email.utils.parsedate_to_datetime(brut.strip())
    except (TypeError, ValueError):
        return brut.strip() or None
    return d.isoformat() if d else brut.strip() or None


def article_de(markup):
    """Le bloc qui se DECLARE `NewsArticle` — la page en porte TROIS.

    **`strict=False`** : le troisieme bloc porte un saut de ligne brut dans une
    chaine et leve «Invalid control character» sous l'analyseur strict. *Un bloc
    qui LEVE n'est pas un bloc ABSENT* — le lire strictement enverrait un
    adaptateur gratter du HTML pour une donnee qui etait deja la.
    """
    for bloc in LD_RE.findall(markup or ""):
        try:
            d = json.loads(bloc, strict=False)
        except ValueError:
            continue
        for o in (d if isinstance(d, list) else [d]):
            if isinstance(o, dict) and o.get("@type") == "NewsArticle":
                return o
    return {}


def employeur_de(titre):
    """L'employeur, quand le titre suit la convention du board — sinon RIEN.

    *Les 50 titres mesures portent «<employeur> munhal duyurusu - ...». Deviner
    hors de ce motif fabriquerait un nom d'employeur, ce qui est pire que de
    n'en porter aucun.*
    """
    m = TITRE_RE.match(titre or "")
    if not m:
        return None
    return (m.group(1).strip(" -–—·,") or None)


def record(ident, slug, titre, poste, corps, origine, stamp, url=None):
    return {
        "source": "ekonomikibris", "country": stamp,
        "ledger_id": "ekonomikibris:%s" % ident, "id": ident, "slug": slug,
        "url": url or "https://%s/%s/%s/" % (HOST, slug, ident),
        "title": scrub(text(titre)),
        "employer": scrub(employeur_de(text(titre))),
        "posted": poste,
        # **Un avis n'est pas un `JobPosting`** : le board n'en publie aucun.
        # Emettre des champs vides pour le salaire, le type de contrat ou
        # l'echeance donnerait a un gabarit de PRESSE l'apparence d'une annonce
        # structuree dont les champs seraient simplement manquants.
        "markup": "NewsArticle",
        "structured_posting": False,
        "enumerated_by": origine,
        "description": scrub(text(corps)),
        "contacts_withheld": True,
    }


def du_flux():
    """Le flux : enumerateur ET contenu. Un seul appel pour les 50 avis."""
    url = "https://%s%s" % (HOST, FLUX)
    code, corps = request(url)
    if code == 404:
        die("%s: HTTP 404 — the feed is gone" % url, EXIT_GONE)
    if code != 200 or not corps:
        die("%s: HTTP %s" % (url, code))
    sortie = []
    for item in ITEM_RE.findall(corps):
        lien = (balise(item, "link") or "").strip()
        m = LIEN_RE.search(lien)
        if not m:
            continue
        sortie.append({
            "id": m.group(2), "slug": m.group(1), "url": lien,
            "title": balise(item, "title"),
            "posted": instant(balise(item, "pubDate")),
            # `content:encoded` porte le corps ENTIER ; `description` n'est
            # qu'un chapeau commun a tous les avis.
            "body": balise(item, "content:encoded") or balise(item, "description"),
        })
    return sortie


def du_pager(sans_pager=False):
    """La page puis l'AJAX, jusqu'a la premiere reponse qui n'AJOUTE rien.

    Rend `(ids, arret)` — `arret` NOMME la fin : « clamped at page N », « empty »,
    « bound ». *Sans ce nom, un pager clampe se lit comme un pager epuise.*
    """
    if sans_pager:
        return [], "not read (--feed-only)"
    url = "https://%s%s" % (HOST, LISTE)
    code, corps = request(url)
    if code == 404:
        return [], "HTTP 404 on the listing"
    if code != 200 or not corps:
        die("%s: HTTP %s" % (url, code))
    vus = ids_de(corps)
    connus = {i for i, _s in vus}
    note("listing %s: %d identifier(s)" % (LISTE, len(vus)))
    arret = "bound"
    page = 2
    while page <= AJAX_MAX:
        a_url = "https://%s%s" % (HOST, AJAX % page)
        code, bloc = request(a_url)
        if code != 200 or not bloc.strip():
            arret = "empty response at AJAX page %d" % page
            break
        neufs = [(i, s) for i, s in ids_de(bloc) if i not in connus]
        note("AJAX page %d: %d identifier(s), %d new" % (page, len(ids_de(bloc)), len(neufs)))
        if not neufs:
            # **Le pager est CLAMPE** : il repond, il repond PLEIN, et il ne
            # progresse pas. Continuer le parcourrait indefiniment.
            arret = "CLAMPED at AJAX page %d — it answers with %d id(s) and adds none" % (
                page, len(ids_de(bloc)))
            break
        vus += neufs
        connus |= {i for i, _s in neufs}
        page += 1
    else:
        arret = "stopped at the %d-page safety bound, still advancing" % AJAX_MAX
    return vus, arret


def avis_de(ident, slug):
    """Un avis lu sur SA page — le chemin des identifiants que le flux n'a pas."""
    url = "https://%s/%s/%s/" % (HOST, slug, ident)
    code, corps = request(url)
    if code != 200 or not corps:
        note("%s: HTTP %s — pager-only identifier left unread" % (url, code))
        return None
    ld = article_de(corps)
    if not ld:
        note("%s: no NewsArticle block — left unread" % url)
        return None
    return {"id": ident, "slug": slug, "url": url,
            "title": ld.get("headline"), "posted": ld.get("datePublished"),
            "body": ld.get("articleBody")}


def cmd_jobs(a):
    stamp = a.country_code
    flux = du_flux()
    note("feed %s: %d item(s)" % (FLUX, len(flux)))
    if not flux:
        die("the feed carries no <item> — the route is gone", EXIT_GONE)

    pager, arret = du_pager(a.feed_only)
    note("pager ended: %s" % arret)

    # **On intersecte des IDENTIFIANTS, jamais des cardinaux** — c'est la seule
    # operation qui distingue « 21 dans 50 » de « 21 a cote de 50 ».
    f_ids = {r["id"] for r in flux}
    p_ids = {i for i, _s in pager}
    inter, flux_seul, pager_seul = f_ids & p_ids, f_ids - p_ids, p_ids - f_ids
    if not a.feed_only:
        note("relation measured THIS RUN — feed %d · pager %d · intersection %d · "
             "feed-only %d · pager-only %d · union %d"
             % (len(f_ids), len(p_ids), len(inter), len(flux_seul),
                len(pager_seul), len(f_ids | p_ids)))
        if p_ids and not pager_seul:
            note("the feed CONTAINS the pager, as it did on 2026-10-02 — "
                 "measured, not assumed")
        elif pager_seul:
            note("THE RELATION HAS CHANGED since 2026-10-02: %d identifier(s) are in "
                 "the pager and not the feed — each is fetched from its own notice "
                 "page rather than dropped" % len(pager_seul))

    lignes = list(flux)
    slugs = dict(pager)
    for ident in sorted(pager_seul):
        extra = avis_de(ident, slugs[ident])
        if extra:
            lignes.append(extra)

    ordre = {r["id"]: n for n, r in enumerate(flux)}
    lignes.sort(key=lambda r: ordre.get(r["id"], 10 ** 6))

    plafonne = a.max is not None and len(lignes) > a.max
    if plafonne:
        lignes = lignes[:a.max]

    # **Emission AU FIL DE L'EAU** : une coupure de transport ne doit pas
    # emporter ce qui a deja ete lu.
    dates, emis = [], 0
    for r in lignes:
        origine = ("feed" if r["id"] in f_ids else "pager") + (
            " + pager" if r["id"] in inter else "")
        ligne = record(r["id"], r["slug"], r["title"], r["posted"], r["body"],
                       origine, stamp, url=r.get("url"))
        print(json.dumps(ligne, ensure_ascii=False))
        sys.stdout.flush()
        emis += 1
        if r["posted"]:
            dates.append(str(r["posted"])[:10])

    note("%d notice(s) emitted" % emis)
    if plafonne:
        # **Rien ici ne dit quoi que ce soit de ce que le board porte** : le
        # manque est le NOTRE, et une option ne fabrique pas un deficit de board.
        note("stopped by --max %d — NOTHING here is said about what the board "
             "holds" % a.max)
    else:
        note("No count is stated anywhere on this board: the figure above is what "
             "the feed served, never a claim the site makes")

    if dates:
        recent = max(dates)
        note("newest date stated by the board: %s" % recent)
        if recent < "2026-01-01":
            note("the board is DORMANT, not broken: the route answers and the "
                 "newest notice it carries is dated %s — a statement about the "
                 "board, bounded by the board's own date" % recent)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Ekonomi Kibris — vacancy notices")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("jobs", help="emit the notices of the is-ilanlari section")
    p.add_argument("--country-code", required=True,
                   help="the code STAMPED on every row (CYN for Northern Cyprus)")
    p.add_argument("--max", type=int, default=None,
                   help="cap the rows emitted; claims nothing about the board")
    p.add_argument("--feed-only", action="store_true",
                   help="read the feed alone and measure no relation")
    a = ap.parse_args(argv)
    if a.cmd == "jobs":
        return cmd_jobs(a)
    ap.error("unknown command")


if __name__ == "__main__":
    sys.exit(main())
