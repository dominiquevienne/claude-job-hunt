#!/usr/bin/env python3
"""Sweep jobup.ch and jobs.ch over plain HTTP — no browser, no cookie, no login.

**The adapter files made the Chrome extension a prerequisite**, so a user
without it had no Swiss sweep at all, on the two largest boards in this
repository. Measured 2026-09-02: twelve ads and three listing pages answer
`200` to a plain request, and **the structured data is in the HTML that
arrives**. Issue #68.

WHERE THE DATA IS, WHICH IS NOT WHERE THE ISSUE EXPECTED IT. The listing page
carries **one `JobPosting` per card**, wrapped in an `ItemList`:

    {"@type": "ItemList", "itemListElement":
       [{"@type": "ListItem", "position": 1,
         "item": {"@type": "JobPosting", …}}, …]}

and those carry **title, employer, date, employment type, url, identifier and
the location** — `addressLocality` filled on 13 of 20. **The ad page's own
`jobLocation` is empty on 12 of 12**, so the geography lives on the listing and
only there. A sweep that reads ad pages for location loses it.

*(`_ldjson.py` unwraps `ItemList` because of this: it previously saw zero
postings on a page holding twenty.)*

TWO THINGS THE LISTING DOES NOT CARRY: the full description and any salary.
The description is on the ad page, in its own `JobPosting`, 1 443 to 6 247
characters. `--with-description` fetches it, one request per ad.

A PROMOTED CARD IS REPEATED ACROSS PAGES. Measured: one ad sat at position 13
of page 1 **and position 1 of page 2**. So ids are deduplicated and the repeats
are counted out loud — **but a repeat is not a pagination failure**, and the
two are told apart: a page whose ids are *entirely* contained in what came
before has not advanced (exit 6), while a handful of repeats is paid placement.

AND AN AD URL ANSWERS IN FOUR WAYS, WHICH `ad` READS BEFORE ITS BODY.
`shared/boards/jobup.md` has the table: `410` is gone and still serves the ad's
own block, an expired ad **redirects to its trade's category page** carrying
twenty valid postings and no mention of the job, `404` never existed, and only
a plain `200` is the advert. **The block count decides none of it** (#88).

AND THE LIST CAN BE A CACHED BODY OLDER THAN THE SWEEP ITSELF — #1260, measured
2026-11-04. Both hosts answer `Vary: Accept-Encoding`, so their CDN keys its
cache per encoding variant, and this adapter asked for `identity` (#71) — a
variant **nobody else on earth requests**, so nothing ever refreshed it. Ten
listing keys at one edge POP: the eight served from cache all carried `Age`
**51.6 h**, to a tenth of an hour, which is one snapshot written at one instant
— our own sweep two days earlier. On gzip, eight of the ten reads were MISSES,
so the origin's own answer; **ONE uncontaminated HIT at `Age` 11.5 h** says real
traffic reaches that variant, and the other HIT was our own write minutes
earlier. One specimen either way. Status 200, `exit 0`, "ended by itself", well-formed ads: **three daily
sweeps running with no new advertisement at all, and the only symptom was an
absence.**

**THE CASE WAS A RED HERRING AND IT LOOKED LIKE THE CAUSE.** The issue reported
`Chef de projet` frozen where `chef de projet` was fresh, and lowercasing the
term was the suggested fix. It would have bought one day: changing any
character makes a NEW key whose `identity` variant is not populated yet, so a
MISS, so fresh — and `Chef de Projet` and `CHEF DE PROJET`, both CAPITALISED,
measured fresh the same minute. A fixed key freezes as soon as our own sweep
populates it, whatever its case.

So the request asks for gzip and `decompress_body` undoes it, the size reserve
of #71 being honoured on the DECOMPRESSED body; and **because that remedy could
go stale in its turn, the symptom has its own guard**: a page served from cache
older than `MAX_BODY_AGE` makes the run exit `EXIT_STALE` after its rows are on
stdout, saying which page and what age. The witness is the `Age` the host
declares, never a publication date — page 1 is sorted by RELEVANCE, and
`Laravel` and `Symfony` carry a newest ad of 30.10 and 19.10 on BOTH variants,
so a date-based guard would redden on correct data.

    jobup.py search --site jobup --term developpeur --pages 2
    jobup.py search --site jobs-ch --term entwickler --location Bern
    jobup.py ad --url https://www.jobup.ch/fr/emplois/detail/<uuid>/
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body, decompress_body
from _ldjson import label, one, postings

from _locations import drop_report

from _robots import allowed as robots_allowed, full_path
from _robots import verdict as robots_verdict

from _zero import empty_first_page, zero_note

SITES = {
    "jobup": {"host": "www.jobup.ch", "path": "/fr/emplois/",
              "detail": "/fr/emplois/detail/"},
    "jobs-ch": {"host": "www.jobs.ch", "path": "/de/stellenangebote/",
                "detail": "/de/stellenangebote/detail/"},
}
from _ua import UA

DEFAULT_SITE = "jobup"
EXIT_PARTIAL = 6
# **5, et il est DECLARE parce qu un code hors contrat se lit comme le voisin le
# plus proche.** Le contrat de ces adaptateurs, mesure sur les 238 du depot par
# l arbre et non au grep : 2 casse, 3 disparu, 6 partiel, 7 refuse, 8 inconnu.
# Le 9 porte DEJA deux sens ailleurs (`EXIT_PACED`, `EXIT_NEEDS_BROWSER`), donc
# un troisieme y serait pire que l invention ; le 5 est libre chez les
# adaptateurs. Il dit : les lignes sur stdout sont bonnes, et la liste d ou
# elles sortent n est pas celle d aujourd hui.
EXIT_STALE = 5
# **24 h, et le seuil est pose DANS UN FOSSE MESURE, pas choisi.** 2026-11-04,
# dix cles de liste au meme POP d edge : les huit servies depuis le cache sous
# `Accept-Encoding: identity` portaient toutes `Age` 51.6 h — a un dixieme d
# heure pres, donc UN instantane — pendant que les memes URL en gzip allaient de
# un seul HIT NON CONTAMINE, a 11.5 h — les huit autres lectures gzip etaient
# des MISS, donc notre propre ecriture, donc muettes sur la chaleur de la
# variante. **UN specimen, et le fosse ne porte donc pas le seuil.**
# **SA RAISON EST L USAGE, et c est la seule qui tienne :** un balayage quotidien ne
# peut rien apprendre d un corps plus vieux que son propre intervalle — c est
# exactement le symptome de #1260, trois balayages sans une annonce neuve.
MAX_BODY_AGE = 86400


def cache_age(headers):
    """`(secondes, hit)` — quel age a le corps que cette reponse portait. #1260.

    `secondes` sort de l en-tete `Age`, `None` quand il est absent ou illisible ;
    `hit` dit si l edge l a servi depuis son cache.

    **UN `Age` ABSENT N EST PAS UN INCONNU QUAND IL N Y A PAS DE HIT :** sur un
    MISS il n y en a pas, et le corps vient de l origine — donc frais par
    construction. Le seul cas illisible est un `Age` qu on ne sait pas lire sur
    une reponse qui dit `Hit`, et celui-la se DIT au lieu d etre compte d un cote
    ou de l autre : l ignorance ne libere pas, et elle n accuse pas non plus.

    **Et ce temoin est le bon parce qu un grand `Age` ne peut pas etre la par
    accident** — c est l hote qui declare l age de ce qu il vient d envoyer. La
    date de l annonce la plus recente, elle, ne tranche RIEN : la page 1 est
    triee par PERTINENCE, et mesure le 2026-11-04 sur `Laravel` et `Symfony`,
    les deux variantes rendaient une annonce la plus recente du 30.10 et du
    19.10 — des listes legitimement maigres. Une garde batie sur cette date
    aurait rougi sur du correct.
    """
    if headers is None:
        return None, False
    def champ(nom):
        try:
            return (headers.get(nom) or headers.get(nom.lower())
                    or headers.get(nom.upper()))
        except AttributeError:          # quelque chose sans `.get`
            return None
    brut = champ("Age")
    try:
        sec = int(str(brut).strip()) if brut is not None else None
    except ValueError:
        sec = None
    return sec, "hit" in (champ("X-Cache") or "").lower()


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


# **The tag named one of the two boards this adapter reads, always.** Running
# `--site jobs-ch` printed `[jobup] 20 ad(s) …` while the records carried
# `jobs-ch:` ids and `www.jobs.ch` URLs — the data was right and every
# sentence about it was wrong. A reader checks the sentence. Issue #129's
# shape, on the tag itself.
_TAG = "jobup"


def note(msg):
    print(f"[{_TAG}] {msg}", file=sys.stderr)


def gate(url):
    """Ask on the exact URL, at the point every request passes. #176.

    **This module decided on `verdict(host)["sweep"]` and nothing else.**
    `sweep` answers *is this host closed in one block* under `OUR_AGENTS` —
    six names a site may use **about** us, four of which we never send. So the
    owner's decision of 2026-09-07, that a named refusal binds only the token
    it names, reached `allowed()` and reached this module not at all.

    **And a sweep verdict is not a path verdict.** `hiringcafe.com` answers
    `sweep: True` above its own reason — *"this host refuses 17 path(s) to
    `*`"* — so deciding on `sweep` alone fetches paths the rules close.

    The pre-flight `sweep` check stays where it is: it is a **report** about
    the host, and this is the **decision** about the path.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return
    a = robots_allowed(parts.netloc, full_path(parts))
    # An unknown is not a refusal, and `not None` is `True` for both.
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", 8)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", 7)


def get(url):
    """`(status, body, landed, headers)`. **Where it landed is half the signal,
    and how OLD the body is turned out to be the other half (#1260).**

    **This string used to sit AFTER the `gate(url)` call**, which made it a
    no-op expression and `get.__doc__` `None`: the contract of this function
    was written nowhere a reader could reach it. It moves up here with the
    arity it now has to describe.
    """
    gate(url)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        # **gzip, and the reason is a CACHE and not a size — #1260.** #71 asked
        # for `identity` so that one body would have one size rather than two.
        # But both hosts answer `Vary: Accept-Encoding`, so their CDN keys its
        # cache **per encoding variant**, and we were the only client of the
        # `identity` variant — nothing on earth refreshed it. Measured
        # 2026-11-04 at one edge POP: eight listing keys served from cache at
        # `Age` **51.6 h** each, to a tenth of an hour, so one snapshot written
        # at one instant (our own sweep two days earlier). On gzip, eight of
        # ten reads were MISSES — our own writes, so mute on warmth — and the
        # ONE uncontaminated HIT was at `Age` 11.5 h. **The size reserve of #71 is
        # honoured by DECOMPRESSING and measuring the result** — the two
        # variants carry the same content, measured: on the two keys our sweeps
        # had not populated, the stated totals matched to the unit.
        #
        # **And no `br`:** the standard library cannot decode it, and
        # `decompress_body` refuses rather than hand back bytes that would be
        # read one layer down as a charset fault.
        "Accept-Encoding": "gzip, deflate",
        "Accept": "text/html,application/xhtml+xml",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            # A failure to decompress raises `BadGzipFile`, which IS an
            # `OSError`, so it lands in the clause below and dies naming the
            # URL. It does not fall through as unreadable bytes.
            raw = decompress_body(r.read(), r.headers)
            return (r.getcode(), decode_body(raw, r.headers)[0], r.geturl(),
                    r.headers)
    except urllib.error.HTTPError as e:
        raw = decompress_body(e.read(), e.headers)
        return (e.code, decode_body(raw, e.headers)[0],
                getattr(e, "url", url), e.headers)
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def card(site, p):
    """One row, from the listing's own JobPosting. Values, never keys."""
    ident = one(p.get("identifier")).get("value")
    org = one(p.get("hiringOrganization"))
    addr = one(one(p.get("jobLocation")).get("address"))
    sal = one(p.get("baseSalary"))
    amount = one(sal.get("value"))
    # **The salary block is a shell.** Served as MonetaryAmount + an empty
    # QuantitativeValue on every ad measured: counting the key gives 100%,
    # counting the value gives 25% (#67).
    figure = amount.get("value") or amount.get("minValue") or amount.get("maxValue")
    return {
        "id": ident,
        "ledger_id": f"{site}:{ident}",
        "url": p.get("url"),
        "title": p.get("title"),
        "company": org.get("name"),
        # The ad page's own jobLocation is empty on every ad measured; this is
        # the only place the town appears.
        "location_text": addr.get("addressLocality"),
        "country": addr.get("addressCountry"),
        "posted": p.get("datePosted"),
        "employment_type": label(p.get("employmentType")),
        "salary_stated": bool(figure),
        "salary_value": figure,
        "salary_currency": sal.get("currency"),
    }


def resolve_site(chosen):
    """`(site, message_or_None)` — the default, and whether to say so.

    **A pure function on purpose.** The announcement used to sit inline, and a
    test could only assert *where* the line was written, never *when* it runs.
    A `if True:` nested in the same span kept it in place and fired it on every
    call, and the check stayed green: it was reading position, not condition.
    **Here the condition is the return value**, so a case can call it twice and
    compare.
    """
    if chosen is not None:
        return chosen, None
    return DEFAULT_SITE, (
        f"no --site given, reading **{SITES[DEFAULT_SITE]['host']}**. This "
        f"adapter serves {len(SITES)} boards ({', '.join(sorted(SITES))}) and "
        f"defaults to `{DEFAULT_SITE}` — **if you meant the other one, say "
        f"so**: the records would carry `{DEFAULT_SITE}:` ids and look like a "
        f"normal answer.")


# **LE COMPTE QUI NE VIENT PAS DE NOTRE PROPRE EXTRACTION — #924.** Les deux hotes
# impriment leur total dans un attribut : `data-cy="total-hits" title="36 offres
# d'emploi"`. Mesure du 2026-10-05 : jobup `"Laravel"` -> 4 annonces pour un total
# annonce de 4 ; jobup `developpeur` -> 20 pour 36 ; jobs.ch `entwickler` -> 20 pour
# 511. **C'est ce temoin qui separe «la marche est finie» de «la pagination est
# bloquee»**, la ou une page courte ne separe rien.
#
# **ET CE N'EST PAS `numberOfItems` DE L'`ItemList`, qui est un piege.** Sur la requete
# etroite il vaut 4 et egale le total ; sur la large il vaut **20** quand le total est
# **36** — c'est le compte DE LA PAGE, donc notre propre extraction sous un autre nom.
# Il aurait eu l'air juste sur le cas qui a motive l'issue.
TOTAL_HITS = re.compile(r'data-cy="total-hits"[^>]*title="\s*([\d\u00a0\u202f \']+)', re.I)

# Mesuree, plus inferee : la requete large rend 20 annonces en page 1 pour 36 au total,
# donc une page pleine en porte 20. L'issue la donnait comme deduite de 11 recherches.
PAGE_FULL = 20


def stated_total(body):
    """The total the site prints beside its results — or None when unreadable."""
    m = TOTAL_HITS.search(body or "")
    if not m:
        return None
    try:
        return int(re.sub(r"[^\d]", "", m.group(1)))
    except ValueError:
        return None


def cmd_search(a):
    # **An invocation that cannot return anything must not be accepted.**
    # `search` with no filter fetches the bare listing, which serves no
    # structured data at all — measured 2026-09-03: `/fr/emplois/` is 275 kB
    # with **zero** `JobPosting`, while `?term=developpeur` is 534 kB with
    # **22**. So a filterless run returned zero, reliably, and the zero was
    # read as the board being empty. **A tool that accepts a call which cannot
    # succeed manufactures false results.** Issue #126.
    if not (a.term or a.location):
        die("give --term, or --location, or both.\n"
            "  **A zero from the unfiltered listing cannot be read**, and "
            "that is the reason — not that it is always empty.\n"
            "  Measured 2026-09-03: `/fr/emplois/` was 275 kB with **zero** "
            "`JobPosting`, against 534 kB and 22 for `?term=developpeur`. "
            "**Measured again 2026-09-04, the same URL carried 20** — and so "
            "did `jobs.ch`'s. **Two observations a day apart, opposite, and "
            "nothing here can tell a deployment from an intermittency.**\n"
            "  So the refusal stands on what holds either way: **a count "
            "taken from this URL means one thing today and another "
            "yesterday**, and a zero from it was already read once as a dead "
            "board — this board, this repository, #122. A filter makes the "
            "answer interpretable. No request was made.", 2)

    global _TAG
    # **`--site` used to default silently to `jobup`.** Two boards share this
    # adapter, and somebody who enabled jobs.ch and typed the general form got
    # twenty jobup.ch advertisements, HTTP 200, no warning — the `ledger_id`
    # prefix was the only tell, and it is in the JSON, not in the message.
    #
    # **The default still holds; it no longer holds quietly.** The line is
    # printed only when nobody chose, because a warning that fires on correct
    # use is noise.
    a.site, said = resolve_site(a.site)
    if said:
        note(said)
    _TAG = a.site
    site = SITES[a.site]
    v = robots_verdict(site["host"])
    if not v["sweep"]:
        die(f"{site['host']}: {v['reason']}", 8 if v["sweep"] is None else 7)
    seen, rows, repeats, partial = set(), [], 0, False
    board_total, pages_read, last_page, ended = None, 0, 0, "capped"
    # (page, age en secondes ou None, servi depuis le cache) — #1260
    fraicheur = []
    for page in range(1, a.pages + 1):
        # **`location` goes into the URL.** It used to be applied only after
        # the fetch, by `drop_report`, so `--location Lausanne` alone
        # requested the *unfiltered* listing — zero results — and then
        # filtered nothing. The site accepts it: `?location=Lausanne` answers
        # with 22 `JobPosting` on jobup. Issue #126.
        q = {}
        if a.term:
            q["term"] = a.term
        if a.location:
            q["location"] = a.location
        if page > 1:
            q["page"] = page
        url = f"https://{site['host']}{site['path']}?" + urllib.parse.urlencode(q)
        status, body, _, entetes = get(url)
        age, depuis_cache = cache_age(entetes)
        fraicheur.append((page, age, depuis_cache))
        if status != 200:
            die(f"{url}: HTTP {status}")
        pages_read = page
        if page == 1:
            board_total = stated_total(body)
        found = postings(body)
        if not found and page == 1:
            # #181: page 1 with no JobPosting used to print the three-causes
            # sentence below and exit 0 with an empty stdout — the admission
            # on stderr, the verdict on the exit code, and the exit code said
            # fine. Page 1 is INDETERMINATE, exit 6, size beside the zero.
            die(empty_first_page(a.site, body, "JobPosting",
                                 what_asked=", ".join(f"{k}={v!r}" for k, v in
                                                      (("term", a.term), ("location", a.location)) if v) or None), 6)
        if not found:
            # **Three causes, and the message used to name two.** The one
            # it left out is the one that produced a false report of a dead
            # board: a query this site does not answer with structured data.
            # Naming two of three is not a false statement, and it had the
            # same effect as one — it pointed at "the board is broken".
            # Issue #126.
            asked = ", ".join(f"{k}={v!r}" for k, v in
                              (("term", a.term), ("location", a.location))
                              if v) or "nothing"
            note(f"page {page} carried no JobPosting — stopping. "
                 f"**Three things look like this and they are not the "
                 f"same.** (1) The end of the results. (2) A reading failure "
                 f"— the markup changed and a page with cards is being "
                 f"misread. (3) **A query this site did not answer with "
                 f"structured data**: you asked for {asked}. On "
                 f"{site['host']}, `location` alone is honoured by jobup and "
                 f"**not** by jobs.ch — `?location=` and the bare URL return "
                 f"byte-identical pages there. **And the unfiltered listing "
                 f"has been measured both ways within a day** (#126), so a "
                 f"zero from it dates faster than a card can record it. Try "
                 f"a `--term` before reading this as an empty board.")
            break
        ids = {one(p.get("identifier")).get("value") for p in found}
        # Entirely repeated → the pagination did not advance. A few repeats →
        # paid placement, which is what a promoted card looks like.
        if ids and ids <= seen:
            # **The sentence was right and the behaviour contradicted it.**
            # `sys.exit` here left the loop *and* skipped the print stage
            # below, so the run announced "N row(s) so far and they are good"
            # on stderr and put nothing on stdout — a total, silent loss for
            # anything reading stdout, which is the whole chain. The other
            # early stop in this loop uses `break` and does reach the print;
            # two exits from one loop, and only one of them worked. #134.
            # **UNE MARCHE A TROIS FINS, ET CELLE-CI EN MANQUAIT UNE — #924.**
            # Mesure du 2026-09-28 : exit 6 sur 5 recherches sur 5 dont la page 1
            # n'etait pas pleine, et aucune des 11 a page pleine. Quand il n'y a pas
            # de page 2, ce site **renvoie la page 1** — la marche etait COMPLETE et
            # l'outil annoncait «partiel». *Un avertissement qui tire toujours ne vaut
            # pas mieux qu'un avertissement qui ne tire jamais, et il est plus dur a
            # retirer parce qu'il a l'air prudent.*
            if board_total is not None and len(rows) >= board_total:
                note(f"page {page} repeats page {page - 1}: **the results end "
                     f"there.** {len(rows)} emitted, board states "
                     f"{board_total} — complete. When there is no page {page}, "
                     f"this site serves page {page - 1} again; that is the end "
                     f"of the results and not a pagination failure.")
                ended = "complete"
                break
            if board_total is None and last_page < PAGE_FULL:
                note(f"page {page} repeats page {page - 1}, and page "
                     f"{page - 1} held {last_page} < {PAGE_FULL} — **the "
                     f"results end there.** The site's own total could not be "
                     f"read on this run, so this rests on the page being short "
                     f"rather than on a count: weaker, and said so.")
                ended = "complete-inferred"
                break
            note(f"page {page} repeats page {page - 1} entirely — the "
                 f"pagination did not advance. Stopping rather than looping; "
                 f"{len(rows)} row(s) so far and they are good, and they are "
                 f"on stdout below."
                 + (f" The board states {board_total}, so "
                    f"{board_total - len(rows)} are missing."
                    if board_total is not None else
                    " The board's own total could not be read, so how many "
                    "are missing is unknown."))
            partial = True
            ended = "stuck"
            break
        last_page = len(found)
        for p in found:
            row = card(a.site, p)
            if not row["id"] or row["id"] in seen:
                repeats += 1
                continue
            seen.add(row["id"])
            rows.append(row)
        time.sleep(a.delay)
    if a.location:
        # Three values, not two — `(kept, dropped, labels)`. Unpacking two
        # raised `ValueError` on every `--location` run, after the sweep had
        # already been paid for.
        rows, dropped, labels = drop_report(rows, a.location)
        if dropped:
            note(f"{dropped} row(s) dropped by the `{a.location}` filter, "
                 f"applied again here on the text the cards carry: "
                 f"{dict(sorted(labels.items(), key=lambda kv: -kv[1])[:5])}")
    for row in rows[:a.limit] if a.limit else rows:
        print(json.dumps(row, ensure_ascii=False))
    if not rows:
        note(zero_note(a.site, what=a.term, where=a.location))
    stated = sum(1 for r in rows if r["salary_stated"])
    located = sum(1 for r in rows if r["location_text"])
    # **Et le plafond atteint n'est pas une fin si le total est atteint.** Avec
    # `--pages 2` sur 36 annonces a 20 par page, la boucle epuise sa plage en ayant
    # TOUT lu : «stopped at the --pages ceiling» serait exact sur la cause et faux
    # sur le fait. Le temoin du site tranche ici aussi.
    if ended == "capped" and board_total is not None and len(rows) >= board_total:
        ended = "complete"
    # **Trois fins, nommees.** «over {a.pages} page(s)» disait le PLAFOND et non ce
    # qui a ete lu : une marche arretee en page 2 d'un plafond de 5 s'annoncait sur 5.
    fin = {"complete": "ended by itself — the board's total was reached",
           "complete-inferred": "ended by itself — inferred from a short page, "
                                "the board's total being unreadable",
           "stuck": "stopped: the pagination did not advance",
           "capped": f"stopped at the --pages ceiling of {a.pages}"}[ended]
    note(f"{len(rows)} ad(s) over {pages_read} page(s) read"
         + (f" of {a.pages} asked" if pages_read != a.pages else "")
         + f" — {fin}"
         + (f"; board states {board_total}" if board_total is not None else
            "; the board's own total was not readable")
         + ". "
         f"salary: {stated} of {len(rows)} carry a figure — **the block is "
         f"present on all of them and empty on most** (#67). "
         f"location: {located} of {len(rows)}; the ad page does not carry it "
         f"at all, so this is the only source.")
    if repeats:
        note(f"{repeats} card(s) repeated across pages and were deduplicated — "
             f"paid placement, not a pagination failure: one ad was measured "
             f"at position 13 of page 1 and position 1 of page 2.")
    # **UNE LISTE PEUT ETRE SERVIE DEPUIS UN CACHE PLUS VIEUX QUE LE BALAYAGE
    # LUI-MEME, ET RIEN DANS LA SORTIE NE LE DISAIT — #1260.** Statut 200,
    # `exit 0`, « ended by itself — the board's total was reached », des annonces
    # bien formees : trois balayages quotidiens de suite sans une seule annonce
    # neuve, et le seul symptome etait une ABSENCE.
    #
    # Elle tire sur le SYMPTOME et pas sur la cause du jour : le jour ou ce n est
    # plus la variante d encodage, un corps vieux reste un corps vieux.
    vieux = [(p, a) for p, a, _h in fraicheur if a is not None and a > MAX_BODY_AGE]
    muets = [p for p, a, h in fraicheur if a is None and h]
    if muets:
        # Un enonce sur l INSTRUMENT, pas sur le verdict : il sort sans changer
        # le code, parce qu on ne sait pas, et ne pas savoir n accuse pas.
        note(f"page(s) {', '.join(map(str, muets))}: served from the edge's "
             f"cache and carrying no readable `Age` — **this run cannot "
             f"establish how old that body was.** Not counted as stale and not "
             f"counted as fresh; said, because the two read alike in a log.")
    if vieux:
        pire = max(vieux, key=lambda pa: pa[1])
        note(f"**STALE LIST — the rows above are good and they are not "
             f"today's.** Page {pire[0]} was served from the edge's cache with "
             f"`Age: {pire[1]}` s = {pire[1] / 3600.0:.1f} h, and "
             f"{len(vieux)} of {len(fraicheur)} page(s) read were older than "
             f"{MAX_BODY_AGE / 3600.0:.0f} h. **So every sentence above "
             f"describes that body and not this hour** — including the count, "
             f"the board's own total and whichever of the three ends was "
             f"named. A daily sweep cannot learn anything from a body older "
             f"than its own interval, which is why this exits "
             f"{EXIT_STALE} rather than 0.")
        # Deux codes ne peuvent pas sortir par la meme porte. Les deux FAITS se
        # disent sur stderr, et c est le plus fondamental qui prend le code :
        # « la pagination n a pas avance » porte sur une liste dont on vient d
        # etablir qu elle n est pas celle d aujourd hui.
        sys.exit(EXIT_STALE)
    if partial:
        # **The status still says partial; only its timing changed.** Exit 6
        # after stdout has the rows, not instead of them.
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    global _TAG
    host = urllib.parse.urlsplit(a.url).netloc
    # **The second way in, and it had the same defect.** `ad` takes a URL
    # rather than `--site`, so nothing here ever set the tag: reading a
    # `www.jobs.ch` advertisement printed `[jobup]` over every line about it.
    for name, cfg in SITES.items():
        if cfg["host"] == host:
            _TAG = name
            break
    v = robots_verdict(host)
    if not v["sweep"]:
        die(f"{host}: {v['reason']}", 8 if v["sweep"] is None else 7)
    status, body, landed, _entetes = get(a.url)
    # **Status, then where it landed, then the ad's own isActive — the block
    # count decides none of it.** jobup.md carries the four-state table (#88).
    if status == 410:
        die(f"{a.url}: HTTP 410 — the board says this ad is gone. It still "
            f"serves the ad's own text and its own JobPosting block, so a "
            f"check that counts blocks would call it open.", 3)
    if status == 404:
        die(f"{a.url}: HTTP 404 — this id never existed on this board. That is "
            f"a different fact from an ad that closed.", 3)
    if landed.rstrip("/") != a.url.rstrip("/"):
        die(f"{a.url} redirected to {landed}. **It is forbidden to conclude "
            f"'open' from a page reached by a redirect**: an expired ad lands "
            f"on its trade's category page, which carries ~20 valid "
            f"JobPosting blocks and no mention of the job (#88).", 3)
    found = postings(body)
    if not found:
        die(f"{a.url}: HTTP 200, no redirect, and no JobPosting. Read the page "
            f"before concluding anything — this is neither a served ad nor a "
            f"recognised absence.")
    p = found[0]
    row = card("jobup" if "jobup" in host else "jobs-ch", p)
    row["url"] = a.url
    desc = p.get("description") or ""
    row["description_chars"] = len(desc)
    if a.with_text:
        row["description"] = desc
    print(json.dumps(row, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="read the listing, one request per page")
    # `default=None`, not `default="jobup"`: argparse cannot otherwise tell
    # a chosen `jobup` from an unchosen one, and the announcement below has to.
    s.add_argument("--site", choices=sorted(SITES), default=None,
                   help=f"which of the two boards ({', '.join(sorted(SITES))})"
                        f"; defaults to {DEFAULT_SITE}, and says so when it "
                        f"does")
    s.add_argument("--term")
    s.add_argument("--location", help="town filter, accent-insensitive")
    s.add_argument("--pages", type=int, default=1)
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=1.0)
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="one ad, with its open/closed state")
    d.add_argument("--url", required=True)
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.set_defaults(func=cmd_ad)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
