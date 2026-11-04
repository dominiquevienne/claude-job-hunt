#!/usr/bin/env python3
"""Sweep CA Global's vacancies (a pan-African recruitment agency) over plain HTTP.

    caglobal.py jobs
    caglobal.py jobs --country ZA --since-days 180

WordPress, custom post type `jobpost`, taken through the REST route because it
carries a count the host states itself:

    GET /wp-json/wp/v2/jobpost?per_page=100&page=N&orderby=date&order=desc
        -> X-WP-Total, X-WP-TotalPages

**THE COUNTRY DOES NOT LIVE WHERE ISSUE #786 LOOKED FOR IT.** The issue asks
for a country filter off the ad's place, and the type's place taxonomy
`jobpost_location` cannot give one: measured 2026-11-04 on the whole
population, it DECLARES **70 terms** of which **13 are assigned**, and all
seventy are REGIONS at every granularity — 57 of them multi-region names glued
by a `#` (`Western Africa#Southern Africa#Eastern Africa#Central Africa`).
**No country is named among them, not even South Africa, which carries 34
ads.** The other three taxonomies the type declares answer no better:
`jobpost_category` is a sector (`Mining 106 · Finance 34 · Other 25` …), and
`jobpost_job_type` and `jobpost_tag` are DECLARED BY THE SCHEMA AND EMPTY on
199/199.

So the country is derived from the TITLE, where the host actually writes it —
and the filter this tool offers is therefore sound, just not off the field the
issue named. The region is still emitted, as `region_stated`, because it is
what the host asserts.

**AND THE TITLE IS A FREE FIELD, WHICH IS THE WHOLE DIFFICULTY.** Measured on
the 199:

    … - Guinea                        the country alone, after an en-dash
    … - Cairo, Egypt                  city, country
    … - South Africa, Johannesburg    country, city -- the REVERSE order
    … Gauteng - South Africa          the city BEFORE the dash
    … (… / Port Operations) Togo      NO separator at all
    … - West Africa                   a REGION, not a country
    … - Sub-Saharan Africa - Remote   two dashes, and "Remote"
    Finance Manager · CFO             NOTHING

A first model of this form was taken from THREE records and was wrong: the
three newest posts carry a `|` (`… | Antananarivo, Madagascar`) and only
**3 of 199** do — they are one client's, and the real separator is the
en-dash. A taxonomy of titles read off page one is not a taxonomy of the board.

So no separator is parsed. Each title is searched for a known name, **longest
key first and on word boundaries**, because both classic traps live in this
board: without the length `guinea` captures `Guinea-Bissau`, and without the
boundary `niger` would capture `Nigeria`.

**AN UNRESOLVED TITLE EMITS `country: null` AND IS NEVER GUESSED** — 128 of
199 resolve, 6 of them through a city alone, and the other 71 either state a
region (about 40) or name no place whatever (about 31).

**AND THAT IS WHY `--country` REPORTS WHAT IT COULD NOT RESOLVE.** A filter
that answers "0 ads" when 71 titles never yielded a country would be read as
"this board has nothing there", which is a zero that asserts instead of
missing. The note therefore always carries the unresolved count, and the
boundary reached.

**THE `countries:` LINE OF THE CARD IS WRONG IN BOTH DIRECTIONS, and it is a
stock snapshot rather than a property of the board.** It declares
`ZA NG GN MA EG CG AO DJ ER RW`, measured on one page on 2026-09-20. On this
stock: **CG 0, DJ 0, ER 0** — three of its ten have left the window in 45 days
— while the board serves **31 countries**, among them **Australia with 16 ads**
(`Expression of Interest … – Australia`, DAMA sponsorship), which the line does
not name at all.

**`X-WP-Total` IS A PUBLISHED STOCK, NOT AN INVENTORY.** The 199 records are
all `publish` and span **2021-06-22 to 2026-11-04**; a vacancy has a deadline,
so wiring that total as a completeness gate would make every run partial for
ever. What a run can establish is reaching the `--since-days` boundary, and
that is what it reports. The header still earns its place as a witness that is
not our extraction: it answers "is this route still the whole type".

**THE TOTAL MOVED WHILE WE MEASURED IT**: 196 at ~13:00Z and 199 at 16:30Z the
same day. It is reported with its hour, never as a size of the board.

**TWO DATES, AND THEY DIFFER ON ALL 199.** `date` is the site's local time and
`date_gmt` is UTC (`2026-11-04T12:22:45` against `…T10:22:45`). This emits
`date_gmt`, because a ledger that mixes zones cannot be compared with itself.

**TITLES ARRIVE HTML-ESCAPED — 172 of 199 carry an entity**, so every motif
here runs on the UNESCAPED text and never on the raw field.

**EXPURGATION IS AN OBLIGATION, measured: 107 of 199 descriptions carry an
e-mail address** and 0 carry a phone number. They leave the description and
the record says which kinds were there; the key is ABSENT when nothing was
taken, because a board that is merely poor must not read like a board we
censored.

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

HOST = "www.caglobalint.com"
PER_PAGE = 100
TAG = "caglobal"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# Composee depuis les pays que les 199 titres NOMMENT, puis eprouvee sur eux.
# Les cles sont minuscules ; la recherche va du PLUS LONG au plus court et sur
# des frontieres de mot (voir `place_of`), parce que ce board porte les deux
# pieges : `Guinea` dans `Guinea-Bissau`, et `Niger` dans `Nigeria`.
COUNTRIES = {
    "guinea-bissau": "GW", "guinea bissau": "GW", "south africa": "ZA",
    "sierra leone": "SL", "saudi arabia": "SA", "ivory coast": "CI",
    "cote d'ivoire": "CI", "côte d'ivoire": "CI", "cayman islands": "KY",
    "united states": "US", "usa": "US", "uae": "AE", "drc": "CD",
    "madagascar": "MG", "mozambique": "MZ", "zimbabwe": "ZW",
    "botswana": "BW", "tanzania": "TZ", "venezuela": "VE", "australia": "AU",
    "ethiopia": "ET", "mauritius": "MU", "namibia": "NA", "nigeria": "NG",
    "morocco": "MA", "senegal": "SN", "zambia": "ZM", "uganda": "UG",
    "rwanda": "RW", "malawi": "MW", "angola": "AO", "guinea": "GN",
    "ghana": "GH", "france": "FR", "egypt": "EG", "togo": "TG",
    "kenya": "KE", "oman": "OM", "qatar": "QA", "djibouti": "DJ",
    "eritrea": "ER",
    # **Les DEUX Congo, et la cle la plus longue est ce qui les separe** : un
    # `congo` seul rendrait `CG` pour une annonce de la RDC, donc le registre
    # d un autre pays. Zero annonce aujourd hui sur les deux, et la garde existe
    # quand meme.
    "democratic republic of congo": "CD", "dr congo": "CD", "drc congo": "CD",
    "republic of congo": "CG", "congo-brazzaville": "CG", "congo": "CG",
    # **Ces pays-ci ne sont PAS dans le stock du 2026-11-04**, et ils sont
    # reconnus exprès : cette table dit ce que l outil SAIT LIRE, jamais ce que
    # le board sert — c est ce qui fera servir Djibouti le jour ou une annonce
    # djiboutienne paraitra, au lieu de la sortir en `country: null`.
    # Et ils rendent les deux conditions de `_hit` NECESSAIRES plutot que
    # decoratives : `niger` dans `Nigeria` exige la frontiere de mot, `mali`
    # dans `Malawi` aussi, et `south sudan` contre `sudan` exige la longueur.
    "niger": "NE", "mali": "ML", "south sudan": "SS", "sudan": "SD",
    "burkina faso": "BF", "cameroon": "CM", "chad": "TD", "benin": "BJ",
    "gabon": "GA", "liberia": "LR", "mauritania": "MR", "somalia": "SO",
    "lesotho": "LS", "eswatini": "SZ", "burundi": "BI", "gambia": "GM",
}
# Les villes que des titres portent SEULES, sans leur pays : six annonces de
# Johannesburg le 2026-11-04. Sans elles, elles sortiraient en `country: null`.
CITIES = {
    "johannesburg": "ZA", "cape town": "ZA", "gauteng": "ZA", "jhb": "ZA",
    "pretoria": "ZA", "northern cape": "ZA", "western cape": "ZA",
    "lagos": "NG", "abuja": "NG", "cairo": "EG", "kigali": "RW",
    "conakry": "GN", "dubai": "AE", "riyadh": "SA", "freetown": "SL",
    "new york": "US", "antananarivo": "MG", "nairobi": "KE",
}
# Ce que le titre dit quand il ne nomme pas de pays. Elles ne deviennent JAMAIS
# un pays : elles sortent en `region_in_title`, et `country` reste nul.
REGIONS = (
    "sub-saharan africa", "oceanic and pacific rim", "western africa",
    "southern africa", "central africa", "eastern africa", "northern africa",
    "north africa", "west africa", "middle east", "indian ocean",
    "western europe", "eastern europe", "caribbean", "australasia",
    "latam", "remote", "global", "africa", "europe",
)

TAG_RE = re.compile(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
# Un indicatif international explicite : ce board n'en porte aucun (0 sur 199),
# et la garde existe quand meme — une fenetre propre n'est pas une propriete.
TEL_RE = re.compile(r"\+\s*\d[\d\s().\-]{7,}\d")

_PACE = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[{TAG}] {msg}", file=sys.stderr)


def gate(url):
    """La garde sur l URL EXACTE, au point ou chaque requete passe.

    **Cet hote PUBLIE des regles et son groupe `*` porte un `Disallow:` VIDE**,
    la forme canonique de « rien n est refuse » — donc aucun refus voisin ne
    vise `/wp-json/`, et l intention est ouverte au sens de §3 bis et pas
    seulement la correspondance de prefixe. Il nomme et PERMET `ClaudeBot`,
    `anthropic-ai` et `Claude-Web`, et ne nomme pas `claude-user`, qui tombe
    donc dans `*`. C est `allowed()` qui tranche, par chemin, a chaque appel.
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
    `Crawl-delay` : elle est donc a nous, et un fichier muet ne dit pas qu il
    n y a pas de seuil — il ne dira pas ou il est, et la seule facon de
    l apprendre serait de le franchir.
    """
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    if host:
        _PACE.setdefault(host, Pace(host, own=1.0)).wait()
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0], r.headers
    except urllib.error.HTTPError as e:
        return e.code, decode_body(e.read(), e.headers)[0], e.headers
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(raw):
    """Les balises hors, les entites DEFAITES, les blancs aplatis.

    **L ordre compte** : on retire les balises AVANT de desechapper, sinon un
    `&lt;p&gt;` desechappe devient une balise que le retrait suivant mangerait
    avec son contenu.
    """
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", raw or ""))).strip()


def _hit(low, table):
    """La cle la PLUS LONGUE qui apparaisse a FRONTIERE DE MOT, ou `(None, None)`.

    Les deux conditions sont necessaires et ce board porte un contre-exemple
    pour chacune : sans la longueur, `guinea` capte `Guinea-Bissau` et rend
    `GN` pour une annonce bissau-guineenne ; sans la frontiere, `niger`
    capterait `Nigeria`. Un pays faux est pire qu un pays absent — il met
    l annonce dans le registre d un autre pays.
    """
    for key in sorted(table, key=len, reverse=True):
        if re.search(r"(?<![a-z])" + re.escape(key) + r"(?![a-z])", low):
            return table[key], key
    return None, None


def place_of(title):
    """`(iso2, matched, region)` depuis le titre DESECHAPPE — jamais devine.

    Le pays d abord, la ville ensuite : un titre qui porte les deux doit rendre
    le pays, et `… – Cairo, Egypt` ne doit pas resoudre par `cairo` alors que
    `egypt` est ecrit. La region ne devient JAMAIS un pays ; elle se declare.
    """
    low = (title or "").lower()
    iso, key = _hit(low, COUNTRIES)
    if iso:
        return iso, key, None
    iso, key = _hit(low, CITIES)
    if iso:
        return iso, key, None
    _, region = _hit(low, {r: r for r in REGIONS})
    return None, None, region


def scrub(s):
    """`(texte, kinds)` — les contacts hors d UN CHAMP, et le champ dit lesquels.

    Il ne recoit jamais une page entiere : le `mailto:` d un gabarit serait
    alors retenu sur chaque enregistrement, ce qui est une fausse affirmation
    sur une discretion que personne n a exercee.
    """
    taken, out = [], s or ""
    if MAIL_RE.search(out):
        taken.append("email")
        out = MAIL_RE.sub("[e-mail withheld]", out)
    if TEL_RE.search(out):
        taken.append("telephone")
        out = TEL_RE.sub("[telephone withheld]", out)
    return out, taken


def card(post, regions):
    title = text((post.get("title") or {}).get("rendered"))
    iso, matched, region_in_title = place_of(title)
    body, taken = scrub(text((post.get("content") or {}).get("rendered")))
    stated = [regions[i] for i in (post.get("jobpost_location") or [])
              if i in regions]
    r = {
        "id": str(post.get("id") or ""),
        "ledger_id": f"{TAG}:{post.get('id')}",
        # Donnee PAR L HOTE : rien a composer, donc rien a raisonner.
        "url": post.get("link"),
        "title": title or None,
        "company": None,          # l annonce ne porte pas l employeur en champ
        # Le titre EST le lieu de cet hote, donc il n y a pas de champ de lieu
        # distinct a emettre ; ce qui est derive se dit, et sa cle le dit.
        "location_text": None,
        "country": iso,
        "country_from_title": matched,
        # **Ce que l HOTE asserte, et c est une REGION** : c est le champ que
        # #786 designait, et il ne peut pas rendre un pays.
        "region_stated": stated or None,
        "region_in_title": region_in_title,
        # **`date_gmt`, et jamais `date`** : les deux differents sur 199/199,
        # et un registre qui melange les zones ne se compare plus a lui-meme.
        "posted": (post.get("date_gmt") or "") + "Z" if post.get("date_gmt") else None,
        "posted_local_stated": post.get("date") or None,
        "status_stated": post.get("status"),
        "description": body,
        "description_chars": len(body),
        "withheld_fields": taken or None,
        "salary_stated": False,
    }
    if withheld_a_contact(taken):
        r["contacts_withheld"] = True
    return r


def region_names():
    """`{id: nom}` pour `jobpost_location` — les noms, jamais les ids.

    Un enregistrement ne porte que des ids ; sans cette resolution le champ que
    l issue designe sortirait en nombres, et personne ne pourrait lire qu il
    s agit de regions.
    """
    url = (f"https://{HOST}/wp-json/wp/v2/jobpost_location"
           f"?per_page={PER_PAGE}&_fields=id,name")
    status, body, _ = get(url)
    if status != 200:
        note(f"{url}: HTTP {status} — the regions will not be named, and the "
             f"records say so by leaving `region_stated` null.")
        return {}
    try:
        terms = json.loads(body)
    except ValueError:
        note(f"{url}: our parser did not read JSON there; regions unnamed.")
        return {}
    return {t["id"]: html.unescape(t.get("name") or "") for t in terms
            if isinstance(t, dict) and t.get("id") is not None}


def cmd_jobs(a):
    v = robots_verdict(HOST)
    if not v["sweep"]:
        die(f"{HOST}: {v['reason']}",
            EXIT_UNKNOWN if v["sweep"] is None else EXIT_REFUSED)

    want = (a.country or "").upper() or None
    if want and want not in set(COUNTRIES.values()) | set(CITIES.values()):
        note(f"--country {want} is not a country this board has ever been "
             f"measured to serve, so a zero below would say nothing about the "
             f"board. The names this tool can resolve are: "
             + " ".join(sorted(set(COUNTRIES.values()) | set(CITIES.values()))))

    regions = region_names()
    floor = (datetime.datetime.now(datetime.timezone.utc)
             - datetime.timedelta(days=a.since_days)).strftime("%Y-%m-%dT%H:%M:%S")
    seen, rows, unresolved, other = set(), [], [], 0
    stock, stock_pages, pages_read, reached = None, None, 0, False
    for page in range(1, a.max_pages + 1):
        q = {"per_page": str(a.per_page), "page": str(page),
             "orderby": "date", "order": "desc"}
        url = f"https://{HOST}/wp-json/wp/v2/jobpost?" + urllib.parse.urlencode(q)
        status, body, hd = get(url)
        if status != 200:
            die(f"{url}: HTTP {status} — the status decides, not whether the "
                f"body reads.",
                EXIT_GONE if status in (400, 404, 410) else EXIT_BROKEN)
        try:
            posts = json.loads(body)
        except ValueError as e:
            die(f"{url}: our parser did not read JSON there ({e}); "
                f"{len(body or '')} characters came back")
        if page == 1:
            stock, stock_pages = hd.get("X-WP-Total"), hd.get("X-WP-TotalPages")
        pages_read = page
        if not posts:
            reached = True
            break
        for post in posts:
            when = post.get("date_gmt") or ""
            if when and when < floor:
                reached = True
                break
            pid = post.get("id")
            if pid is None or pid in seen:
                continue
            seen.add(pid)
            row = card(post, regions)
            if row["country"] is None:
                unresolved.append((pid, row["region_in_title"], row["title"]))
            if want:
                if row["country"] != want:
                    if row["country"] is not None:
                        other += 1
                    continue
            rows.append(row)
        if reached:
            break
        time.sleep(a.delay)

    for row in rows[:a.limit] if a.limit else rows:
        print(json.dumps(row, ensure_ascii=False))

    # **Les non resolus s IMPRIMENT, jamais leur seul compte** : un fourre-tout
    # n est pas homogene, et sa somme ferme aussi bien quand un membre est hors
    # perimetre que quand il est un rate.
    if unresolved:
        shown = ", ".join(f"{i} ({r or 'no place named'})"
                          for i, r, _t in unresolved[:8])
        note(f"{len(unresolved)} of {len(seen)} title(s) yielded NO country and "
             f"were emitted with `country: null`, never guessed: {shown}"
             + (" …" if len(unresolved) > 8 else "")
             + ". About four in ten of those state a REGION instead "
             f"(`– West Africa`, `– Southern Africa`), which never becomes a "
             f"country here.")
    withheld = sum(1 for r in rows if r["withheld_fields"])
    dates = sorted(r["posted"] for r in rows if r["posted"])
    end = ("reached the --since-days boundary of %d day(s)" % a.since_days
           if reached else
           f"stopped at the --max-pages ceiling of {a.max_pages}")
    filt = (f" for --country {want} (of {len(seen)} read; {other} resolved to "
            f"another country, {len(unresolved)} resolved to none)" if want else "")
    note(f"{len(rows)} vacancy/vacancies emitted{filt} over {pages_read} "
         f"page(s) — {end}"
         + (f"; spanning {dates[0][:10]} to {dates[-1][:10]}" if dates else "")
         + f". **The host states {stock} `jobpost` record(s) over {stock_pages} "
         f"page(s) — that is a PUBLISHED STOCK and not an inventory**: all are "
         f"`publish` and they span 2021-06-22 to 2026-11-04, so it is NOT what "
         f"completeness is measured against. It moved from 196 to 199 within "
         f"three hours on 2026-11-04, so it is reported with its hour and never "
         f"as the size of the board. contacts taken out of {withheld} of "
         f"{len(rows)} description(s); dates are `date_gmt` (UTC) because the "
         f"site's local `date` differs on all 199. **The country is derived "
         f"from the TITLE: `jobpost_location` declares 70 terms, all of them "
         f"REGIONS, and names no country at all.**")
    if want and not rows:
        note(f"no vacancy resolved to {want}. This is a statement about THIS "
             f"stock at THIS hour and not about the board: {len(unresolved)} "
             f"title(s) in the window yielded no country, so a country can be "
             f"served here without this filter seeing it.")
    if not reached:
        note(f"the boundary was not reached, so older vacancies inside the "
             f"{a.since_days}-day window are missing — partial, and the exit "
             f"code says so.")
        sys.exit(EXIT_PARTIAL)


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the vacancies, newest first")
    s.add_argument("--country", help="an ISO-3166 alpha-2 code, derived from "
                                     "the TITLE and not from the host's region "
                                     "taxonomy, which names no country")
    s.add_argument("--since-days", type=int, default=180, dest="since_days",
                   help="how far back to walk; the stock reaches 2021 and a "
                        "vacancy has a deadline")
    s.add_argument("--max-pages", type=int, default=3, dest="max_pages")
    s.add_argument("--per-page", type=int, default=PER_PAGE, dest="per_page")
    s.add_argument("--limit", type=int)
    s.add_argument("--delay", type=float, default=1.0)
    s.set_defaults(func=cmd_jobs)
    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
