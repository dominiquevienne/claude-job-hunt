#!/usr/bin/env python3
"""Sweep St Lucia Business Online's vacancy posts (Saint Lucia) over plain HTTP.

    stluciabusinessonline.py jobs
    stluciabusinessonline.py jobs --since-days 60 --max-pages 2

WordPress 6.9.8 behind a business directory. The list is the REST route the
card named as «the adapter's first line», and it is taken because it carries a
count the site states itself:

    GET /wp-json/wp/v2/posts?categories=132&per_page=100&page=N
        &orderby=date&order=desc            -> X-WP-Total, X-WP-TotalPages

**AND `X-WP-Total` IS AN ARCHIVE, NOT AN INVENTORY — wiring it as a
completeness gate would make every run partial for ever.** Measured
2026-11-04: the `job-vacancies` category states **3 594** posts over **36**
pages at 100 per page, and page one alone spans **2026-03-03 to 2026-11-03** —
eight months. A vacancy has a deadline; three and a half thousand of them do
not describe what is open today. So the total is REPORTED as the archive, and
what this tool calls complete is *reaching the `--since-days` boundary*, which
is a thing a run can actually establish.

*The witness still earns its place: the category's own `count` and the header
`X-WP-Total` agree at 3 594, two numbers from the host and neither of them our
extraction. They answer «is this route still the whole category», not «did we
read everything».*

**THE SITE CARRIES OTHER TERRITORIES' VACANCIES IN THEIR OWN CATEGORIES** —
`trinidad-job-vacancies` (id 229, 11 posts) and `barbados-vacancy` (id 230, 8)
— so a post that sits in one of those is NOT Saint Lucia. Measured: **0 of the
100 most recent carries one**, and the guard exists anyway, because a window
that is clean today is not a property of the board. Emitting one as `LC` would
be another territory's advertisement in this country's ledger.

**TWO DATES, AND THEY DIFFER BY A DAY AT MIDNIGHT.** `date` is the site's local
time and `date_gmt` is UTC: the newest post reads `2026-11-02T20:14:36` local
and `2026-11-03T00:14:36` UTC. Two hands measured this board the same hour and
reported 02.11 and 03.11 — **both right, on different fields**. This emits
`date_gmt`, because a ledger that mixes zones cannot be compared with itself.

**TITLES ARRIVE HTML-ESCAPED**: 26 of 100 carry an entity (`&#038;` for `&`).
A ledger row is read by a person, so they are unescaped — and the same string
has several forms at the point of call, which is why the motifs here run on the
UNESCAPED text and never on the raw field.

**EXPURGATION IS AN OBLIGATION, measured: 65 of 100 posts carry an e-mail
address and 6 of 100 a `+1 758` number.** They leave the description and the
record says which kinds were there; the key is ABSENT when nothing was taken,
because a board that is merely poor must not read like a board we censored.

The human address is NOT composed: WordPress gives it in `link`.
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import datetime
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path
from _robots import verdict as robots_verdict
from _ua import UA
from _withheld import withheld_a_contact

HOST = "www.stluciabusinessonline.com"
# EXTRAITS de `/wp-json/wp/v2/categories`, jamais composes.
CAT_JOBS = 132
# Les territoires VOISINS que ce site heberge : un post qui en porte un n est
# pas de Sainte-Lucie, et l emettre en `LC` serait l annonce d un autre pays.
CAT_AILLEURS = {229: "trinidad-job-vacancies", 230: "barbados-vacancy"}
PER_PAGE = 100
TAG = "stluciabusinessonline"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

BALISE_RE = re.compile(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
# +1 758 est l indicatif de Sainte-Lucie.
TEL_RE = re.compile(r"\+?\s*\(?\s*1?\s*758\s*\)?[\s.\-]?\d[\d\s.\-]{5,}\d")

_CADENCE = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[{TAG}] {msg}", file=sys.stderr)


def gate(url):
    """La garde sur l URL EXACTE, au point ou chaque requete passe.

    **Cet hote PUBLIE des regles et en refuse deux chemins** — `/xmlrpc.php` et
    `/wp-admin/` — donc `sweep: True` dit seulement qu il n est pas ferme d un
    bloc : il ne dit PAS que le chemin voulu est ouvert. C est `allowed()` qui
    tranche, par chemin.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return
    a = robots_allowed(parts.netloc, full_path(parts), agents=("claude-user",))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)


def get(url):
    """`(status, body, headers)` — et les EN-TETES remontent, le temoin vit la.

    **La cadence se consulte A CHAQUE requete**, et cet hote n ecrit aucun
    `Crawl-delay` : elle est donc a nous, et un fichier muet ne dit pas qu il n y
    a pas de seuil — il ne dira pas ou il est, et la seule facon de l apprendre
    serait de le franchir.
    """
    gate(url)
    hote = urllib.parse.urlsplit(url).netloc
    if hote:
        _CADENCE.setdefault(hote, Pace(hote, own=1.0)).wait()
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], r.headers
    except urllib.error.HTTPError as e:
        return e.code, decode_body(e.read(), e.headers)[0], e.headers
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def texte(brut):
    """Les balises hors, les entites DEFAITES, les blancs aplatis.

    **L ordre compte** : on retire les balises AVANT de desechapper, sinon un
    `&lt;p&gt;` desechappe devient une balise que le retrait suivant mangerait
    avec son contenu.
    """
    return re.sub(r"\s+", " ", html.unescape(BALISE_RE.sub(" ", brut or ""))).strip()


def scrub(s):
    """`(texte, kinds)` — les contacts hors d UN CHAMP, et le champ dit lesquels.

    Il ne recoit jamais une page entiere : le `mailto:` d un gabarit serait alors
    retenu sur chaque enregistrement, ce qui est une fausse affirmation sur une
    discretion que personne n a exercee.
    """
    pris, out = [], s or ""
    if MAIL_RE.search(out):
        pris.append("email")
        out = MAIL_RE.sub("[e-mail withheld]", out)
    if TEL_RE.search(out):
        pris.append("telephone")
        out = TEL_RE.sub("[telephone withheld]", out)
    return out, pris


def ailleurs(post):
    """Les categories d un AUTRE territoire que porte ce post, s il en porte."""
    return sorted(CAT_AILLEURS[c] for c in (post.get("categories") or [])
                  if c in CAT_AILLEURS)


def card(post):
    corps, pris = scrub(texte((post.get("content") or {}).get("rendered")))
    r = {
        "id": str(post.get("id") or ""),
        "ledger_id": f"{TAG}:{post.get('id')}",
        # Donnee PAR L HOTE : rien a composer, donc rien a raisonner.
        "url": post.get("link"),
        "title": texte((post.get("title") or {}).get("rendered")) or None,
        "company": None,          # le post ne porte pas l employeur en champ
        "location_text": None,
        "country": "LC",
        # **`date_gmt`, et jamais `date`** : les deux diffèrent d un JOUR au
        # passage de minuit, et un registre qui melange les zones ne se compare
        # plus a lui-meme.
        "posted": (post.get("date_gmt") or "") + "Z" if post.get("date_gmt") else None,
        "posted_local_stated": post.get("date") or None,
        "status_stated": post.get("status"),
        "description": corps,
        "description_chars": len(corps),
        "withheld_fields": pris or None,
        "salary_stated": False,
    }
    if withheld_a_contact(pris):
        r["contacts_withheld"] = True
    return r


def cmd_jobs(a):
    v = robots_verdict(HOST)
    if not v["sweep"]:
        die(f"{HOST}: {v['reason']}",
            EXIT_UNKNOWN if v["sweep"] is None else EXIT_REFUSED)

    limite = (datetime.datetime.now(datetime.timezone.utc)
              - datetime.timedelta(days=a.since_days)).strftime("%Y-%m-%dT%H:%M:%S")
    vus, lignes, ecartes = set(), [], []
    archive, pages_archive, pages_lues, atteint = None, None, 0, False
    for page in range(1, a.max_pages + 1):
        q = {"categories": str(CAT_JOBS), "per_page": str(a.per_page),
             "page": str(page), "orderby": "date", "order": "desc"}
        url = f"https://{HOST}/wp-json/wp/v2/posts?" + urllib.parse.urlencode(q)
        status, body, hd = get(url)
        if status != 200:
            die(f"{url}: HTTP {status} — the status decides, not whether the body "
                f"reads.", EXIT_GONE if status in (400, 404, 410) else EXIT_BROKEN)
        try:
            posts = json.loads(body)
        except ValueError as e:
            die(f"{url}: the answer is not JSON ({e}); {len(body or '')} characters")
        if page == 1:
            archive = hd.get("X-WP-Total")
            pages_archive = hd.get("X-WP-TotalPages")
        pages_lues = page
        if not posts:
            atteint = True
            break
        for post in posts:
            cats = post.get("categories") or []
            # **Le filtre a-t-il tenu ?** Un post hors de la categorie demandee
            # veut dire que la requete n a pas filtre ce qu on croit.
            if CAT_JOBS not in cats:
                die(f"{url} returned post {post.get('id')} whose categories are "
                    f"{cats} and do not contain {CAT_JOBS}: the filter did not "
                    f"hold, and emitting would put another section's posts into "
                    f"a vacancies ledger")
            autres = ailleurs(post)
            if autres:
                # Mesure du 2026-11-04 : 0 des 100 plus recents. La garde existe
                # quand meme — une fenetre propre aujourd hui n est pas une
                # propriete du board.
                ecartes.append((post.get("id"), autres))
                continue
            quand = post.get("date_gmt") or ""
            if quand and quand < limite:
                atteint = True
                break
            pid = post.get("id")
            if pid is None or pid in vus:
                continue
            vus.add(pid)
            lignes.append(card(post))
        if atteint:
            break
        time.sleep(a.delay)

    for ligne in lignes[:a.limit] if a.limit else lignes:
        print(json.dumps(ligne, ensure_ascii=False))

    if ecartes:
        note(f"{len(ecartes)} post(s) also sit in another territory's category "
             f"and were NOT emitted as LC: "
             + ", ".join(f"{i} ({'/'.join(c)})" for i, c in ecartes[:6])
             + ". Measured 0 of the 100 most recent on 2026-11-04, so this is "
             f"new — and emitting them would put another country's "
             f"advertisements in this country's ledger.")
    retenus = sum(1 for r in lignes if r["withheld_fields"])
    dates = sorted(r["posted"] for r in lignes if r["posted"])
    fin = ("reached the --since-days boundary of %d day(s)" % a.since_days
           if atteint else
           f"stopped at the --max-pages ceiling of {a.max_pages}")
    note(f"{len(lignes)} vacancy post(s) over {pages_lues} page(s) — {fin}"
         + (f"; spanning {dates[0][:10]} to {dates[-1][:10]}" if dates else "")
         + f". **The site states {archive} posts over {pages_archive} page(s) in "
         f"this category — that is an ARCHIVE and not an inventory**, so it is "
         f"NOT what completeness is measured against: page one alone spans eight "
         f"months, and a vacancy has a deadline. The category's own `count` and "
         f"this header agreed at 3 594 on 2026-11-04, which is what the witness "
         f"is for. contacts taken out of {retenus} of {len(lignes)} "
         f"description(s); dates are `date_gmt` (UTC) because the site's local "
         f"`date` differs by a DAY at midnight.")
    if not atteint:
        note(f"the boundary was not reached, so older vacancies inside the "
             f"{a.since_days}-day window are missing — partial, and the exit "
             f"code says so.")
        sys.exit(EXIT_PARTIAL)


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the vacancy posts, newest first")
    s.add_argument("--since-days", type=int, default=120, dest="since_days",
                   help="how far back to walk; the archive holds years, and a "
                        "vacancy has a deadline")
    s.add_argument("--max-pages", type=int, default=5, dest="max_pages")
    s.add_argument("--per-page", type=int, default=PER_PAGE, dest="per_page")
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=1.0)
    s.set_defaults(func=cmd_jobs)
    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
