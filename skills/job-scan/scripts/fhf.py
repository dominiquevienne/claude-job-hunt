#!/usr/bin/env python3
"""Read emploi.fhf.fr — France's public hospitals and medico-social sector.

The Fédération Hospitalière de France's own board: CHUs, centres hospitaliers,
EHPADs, USLDs, EPSMs. **13 175 ads** on the day this was written, from nurses
and aides-soignants to hospital directors, IT and finance.

Server-rendered Drupal, no JSON and no JSON-LD, so this parses HTML. What makes
that safe: the fields are named after Drupal **field machine names**
(`field--name-field-publish-date`) on the list, and after **visible French
labels** (*"Etablissement"*, *"Personne à contacter"*) on the ad — neither is
theme decoration, so both survive a redesign the way a class like `.col-md-4`
would not.

Three things it gives that most boards do not:

  * **a full postal address on every ad** — establishment, street, postcode,
    town: 36 out of 36 sampled. That is the field the `job-room-ch` module
    records as the one most often missing from a PRE;
  * **a named contact** — a person, their role, their line — on half of them;
  * **the employer itself**, never an intermediary. The board belongs to the
    hospitals' own federation.

And one thing worth knowing before trusting a number from it: **the first page
is served from a cache that was four days old when measured.** See `bust`.

Usage:
  fhf.py list [--search infirmier] [--category SOI] [--department 69]
              [--contract CDI] [--structure 1561] [--posted-within-days 14]
              [--pages 5] [--details]
  fhf.py ad    --id 488708
  fhf.py check --id 488708
  fhf.py categories
"""

from __future__ import annotations

import argparse
import datetime as dt
import html as html_mod
import json
import random
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
SITE = "https://emploi.fhf.fr"
SEARCH = SITE + "/emploi/search"
AD = SITE + "/emploi/{}"
PAGE_SIZE = 9          # fixed; `items_per_page` is accepted and ignored
DELAY = 0.4            # polite pause between requests, in seconds

# The job categories, from the board's own "Toutes les catégories" select.
# A sub-category is written parent/child and is passed through verbatim.
CATEGORIES = {
    "ADM": "Administratif / technique",
    "ADM/DIR": "Administration - Direction",
    "ADM/ENS": "Enseignement",
    "ADM/INF": "Informatique",
    "ADM/LAB": "Laboratoire - recherche",
    "ADM/SGT": "Services généraux et techniques",
    "SOI": "Soignant / médico technique",
    "SOI/MET": "Médico-techniques",
    "SOI/PAR": "Paramédical",
    "SOI/SED": "Socio-éducatif",
    "MED": "Médical / pharmaceutique",
    "MED/SPE": "Medical",
    "MED/PHA": "Pharmacie",
    "INS": "Offres institutionnelles",
    "REM": "Remplacements médicaux",
}

CARD_RE = re.compile(r'<article class="card card-offer">(.*?)</article>', re.S)
FIELD_RE = r'<div class="field--name-field-{}">(.*?)</div>'
SECTION_RE = re.compile(
    r'<div class="section">\s*<div class="section-title">(.*?)</div>'
    r'(.*?)</div>\s*(?=<div class="section"|</div>)', re.S)
TOTAL_RE = re.compile(r"([0-9]+)\s+Offres")
ID_RE = re.compile(r'href="/emploi/(\d+)"')
# "45  Rue Cognacq Jay" / "51092 Reims" — the postcode line is what anchors it.
POSTCODE_RE = re.compile(r"^(\d{5})\s+(.+)$")
DATE_RE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
PHONE_RE = re.compile(r"\b0\d(?:[ .-]?\d\d){4}\b")
URL_LINE_RE = re.compile(r"https?://|URL de l")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def _robots_gate(url, tag, exit_code=7):
    """Ask before fetching — per host and **per path**. Issues #100, #101.

    `verdict()` answers *is this host closed in one block*. **A site that
    refuses its ad path while leaving its root open passes that and refuses
    every advertisement** — `empleate.gob.hn` does exactly that, closing
    `/Vacantes/` to `User-agent: *` with `/` absent.

    It sits **inside the fetch function**, so every request is covered rather
    than the first one, and a refusal **stops the command** with exit 7 and the
    module's own words. **This adapter decides nothing about what a refusal
    means** — deciding is what turns a check into a decoration.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return None
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        print(f"[hellowork] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def bust(params: dict, fresh: bool) -> dict:
    """Add a cache-buster, because the edge cache serves stale job ads.

    Measured on 2026-08-31. The same page, three ways:

        /emploi/search              age 345 688 s (4.0 days), 13 520 ads,
                                    newest ad dated 27.08 16:31
        /emploi/search?page=0       age   6 586 s (1.8 hours), 13 159 ads,
                                    newest ad dated 31.08 14:56
        /emploi/search?cb=<random>  age       0 s,             13 175 ads,
                                    newest ad dated 31.08 16:46

    `cache-control: max-age=604800` — a week — and the bare URL had been sitting
    at the edge for four days. **It answered 200 with nine plausible ads and a
    headline count 345 higher than the board actually held.** Nothing on the
    page says it is old; the only tell is the `age` response header.

    So every request carries a per-run token by default. `--cached` opts back
    into the edge cache when speed matters more than the last few hours.
    """
    if fresh:
        params = {**params, "_": str(random.randint(10 ** 8, 10 ** 9))}
    return params


def get(url: str, params: dict | None = None):
    _robots_gate(url, 'fhf')
    """Return (body, status). 404 is a value, not an error — ads get pulled."""
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "fr-FR,fr;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read().decode("utf-8", "replace"), r.status
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, 404
        die(f"{url} returned HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach {urllib.parse.urlparse(url).netloc}: {e}")


def text(markup: str | None) -> str:
    if not markup:
        return ""
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", markup)
    t = re.sub(r"(?i)<br\s*/?>", "\n", t)
    t = re.sub(r"(?i)</(p|div|li|tr)>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html_mod.unescape(t)
    # Teasers are cut to a character budget, entities included, so they end on
    # fragments like `d&apos…`. Drop the fragment rather than pass it on.
    t = re.sub(r"&[a-zA-Z]{2,8}(?=\s*…\s*$)", "", t)
    lines = [l.strip() for l in t.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def fold(s) -> str:
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def iso(s: str) -> str | None:
    """`27.08.2026 16:31` → `2026-08-27`. Returns None rather than guessing."""
    m = DATE_RE.search(s or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def field(card: str, name: str) -> str:
    m = re.search(FIELD_RE.format(name), card, re.S)
    return text(m.group(1)) if m else ""


def split_establishment(s: str) -> tuple[str, str | None]:
    """`Hopital Gaston Ramon  (Sens)` → name, town. No parens → no town."""
    m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", s.strip())
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip(), m.group(2).strip()
    return re.sub(r"\s+", " ", s).strip(), None


def list_card(card: str) -> dict | None:
    m = ID_RE.search(card)
    if not m:
        return None
    ad_id = m.group(1)
    company, qualifier = split_establishment(field(card, "establishment"))
    title = re.search(r'<h3 class="card-title">(.*?)</h3>', card, re.S)
    return {
        "id": ad_id,
        "ledger_id": f"fhf:{ad_id}",
        "url": AD.format(ad_id),
        "title": text(title.group(1)) if title else None,
        "company": company or None,
        # **The list carries no location, and this is not it.** The
        # establishment line ends in parentheses that are usually a town —
        # `Hôpital Lapeyronie (MONTPELLIER)` — and sometimes are not:
        # `site de Fleyriat`, `siège`. Calling that `location` would put a
        # building name in the town field of a PRE. It is passed through under
        # its own name, and the real address comes from `--details`.
        "site": qualifier,
        "published": iso(field(card, "publish-date")),
        # The employer's own closing date, when they set one — a real deadline,
        # not datePosted plus a constant. Present on 10 of 36 sampled ads.
        "closes": iso(field(card, "limit-date")),
        "teaser": field(card, "description") or None,
    }


def parse_sections(page: str) -> dict:
    out = {}
    for m in SECTION_RE.finditer(page):
        out[text(m.group(1))] = text(m.group(2))
    return out


def parse_address(block: str) -> dict:
    """Establishment name, street, postcode, town — from the label's own block.

    Never guessed by position: the postcode line is the anchor, the line above
    it is the street, and everything above that is the establishment. A block
    that does not carry a postcode yields no postcode, rather than a plausible
    line promoted to one.
    """
    lines = [l for l in block.splitlines() if l.strip()]
    lines = [l for l in lines
             if not re.match(r"^(Voir la fiche|Je candidate)", l)]
    out, idx = {}, None
    for i, line in enumerate(lines):
        m = POSTCODE_RE.match(line.strip())
        if m:
            out["postal_code"], out["locality"] = m.group(1), m.group(2).strip()
            idx = i
            break
    if idx is None:
        return {"name": " ".join(lines[:1]) or None} if lines else {}
    if idx >= 1:
        out["street"] = lines[idx - 1].strip()
    if idx >= 2:
        out["name"] = " ".join(l.strip() for l in lines[:idx - 1])
    return {k: v for k, v in out.items() if v}


def parse_contact(block: str) -> dict:
    """The contact block, and the one thing this adapter refuses to do.

    Addresses on this site are wrapped in Cloudflare's email protection: the
    visible text is the literal placeholder `[email protected]` and the real
    address sits in a `data-cfemail` hex attribute, trivially reversible.

    **It is not reversed here.** That obfuscation exists to stop harvesting,
    and a sweep decoding it on every ad is harvesting whatever the intent. The
    card says an address is there and gives the ad URL; a candidate opening the
    page they are about to apply to reads it in one click.
    """
    lines = [l.strip() for l in block.splitlines() if l.strip()]
    url = re.search(r"https?://[^\s<\"]+", block)
    phone = PHONE_RE.search(block)
    rest = [l for l in lines
            if "[email" not in l and not URL_LINE_RE.search(l)
            and not (phone and l == phone.group(0))]
    # **No `name` and no `role` field, deliberately.** The block's shape is not
    # stable: one ad reads `MAESEELE Arnaud / Arnaud MAESEELE (DRH) /
    # Laetitia KUBIAK (Cadre de santé)` — two people, not a person and a job
    # title — the next reads `Pour plus de simplicité, postulez…`. Any rule
    # that promotes line 2 to "role" produces a field that is filled, plausible
    # and wrong on a third of ads. What is recognisable is labelled; the rest
    # is handed over as lines, for a human to read.
    return {
        "lines": rest or None,
        "phone": phone.group(0) if phone else None,
        "email_protected": "[email" in block,
        "apply_url": url.group(0) if url else None,
    }


def read_ad(ad_id: str, fresh: bool) -> dict | None:
    page, status = get(AD.format(ad_id), bust({}, fresh))
    if status == 404:
        return None
    secs = parse_sections(page)
    sub = re.search(r'<div class="subtitle text-uppercase">(.*?)</div>',
                    page, re.S)
    company, qualifier = split_establishment(text(sub.group(1)) if sub else "")
    title = re.search(r'<h1 class="page-title">(.*?)</h1>', page, re.S)
    info = re.search(r'<div class="publication-info">(.*?)</div>\s*</div>',
                     page, re.S)
    info_txt = text(info.group(1)) if info else ""
    pub = re.search(r"Publié le\s+(.+)", info_txt)
    lim = re.search(r"Date de limite de candidatures\s+(.+)", info_txt)
    address = parse_address(secs.get("Etablissement", ""))
    contact = parse_contact(secs.get("Personne à contacter", ""))
    # `Contrat` is multi-valued and semicolon-separated on this board —
    # "Détachement; Mutation; Stage" is one ad open to three statuses, not
    # three ads. Splitting it is what lets a status filter mean anything.
    contracts = [c.strip() for c in secs.get("Contrat", "").split(";")
                 if c.strip()]
    external = contact.get("apply_url")
    return {
        "id": ad_id,
        "ledger_id": f"fhf:{ad_id}",
        "url": AD.format(ad_id),
        "apply_url": external or AD.format(ad_id),
        "title": text(title.group(1)) if title else secs.get("Poste proposé"),
        "company": address.get("name") or company or None,
        # Only ever the town off the postal address — never the parenthesised
        # qualifier, which is a building as often as a commune.
        "location": address.get("locality"),
        "site": qualifier,
        "address": address or None,
        "published": iso_fr(pub.group(1)) if pub else None,
        "closes": iso_fr(lim.group(1)) if lim else None,
        "contracts": contracts,
        "contact": contact,
        # An ad the hospital also runs on its own ATS. The host is the useful
        # part: it is how a Beetween or Softy tenant becomes discoverable.
        "external": bool(external),
        "external_host": (urllib.parse.urlparse(external).netloc
                          if external else None),
        "description": secs.get("Descriptif") or None,
    }


MONTHS = {"janv": 1, "fév": 2, "fev": 2, "mars": 3, "avr": 4, "mai": 5,
          "juin": 6, "juil": 7, "aoû": 8, "aou": 8, "sept": 9, "oct": 10,
          "nov": 11, "déc": 12, "dec": 12}


def iso_fr(s: str) -> str | None:
    """`31 aoû. 2026` → `2026-08-31`. The ad page writes dates in words.

    The list writes `31.08.2026`; the ad writes `31 aoû. 2026`. Same board,
    two formats — so both are parsed, and an unrecognised month yields None
    rather than a month number picked by position.
    """
    if iso(s):
        return iso(s)
    m = re.search(r"(\d{1,2})\s+([A-Za-zéûôà]+)\.?\s+(\d{4})", s or "")
    if not m:
        return None
    mon = MONTHS.get(fold(m.group(2))[:4]) or MONTHS.get(fold(m.group(2))[:3])
    return f"{m.group(3)}-{mon:02d}-{int(m.group(1)):02d}" if mon else None


def build_params(a) -> dict:
    p = {}
    if a.search:
        p["keyword"] = a.search
    if a.category:
        # Two different <select> elements on this site are both named `type`:
        # the job category (ADM/SOI/MED…) and the site-wide "Que recherchez-
        # vous" (etablissement/direction/personne/service). They share one GET
        # parameter. Passing a value from the wrong one answers 200 with an
        # empty board and no total — which reads exactly like a search that
        # matched nothing.
        if a.category not in CATEGORIES:
            die(f"unknown category {a.category!r} — run `fhf.py categories`. "
                f"A value the board does not know returns an empty page, not "
                f"an error.", code=2)
        p["type"] = a.category
    if a.department:
        # **Scalar, never an array.** The site's own form posts `department[]`
        # and `contract[]`; the GET route honours neither. `?department[]=75`
        # returns zero ads with HTTP 200, where `?department=75` returns 377.
        # Copying the field name out of the HTML is how you get an empty board
        # that looks like a quiet market.
        p["department"] = a.department
    if a.contract:
        p["contract"] = a.contract
    if a.structure:
        p["structure"] = a.structure
    return p


def sweep(params: dict, max_pages: int, fresh: bool, delay: float):
    """Page until the board runs out. It runs out honestly.

    Past the last page the site answers 200 with **no cards at all** — not a
    repeat of the final page — so an empty page is a real end. The seen-set is
    still kept, because a pinned ad can reappear across pages.
    """
    seen, out, announced = set(), [], None
    for page in range(0, max_pages):
        body, _ = get(SEARCH, bust({**params, "page": page}, fresh))
        if announced is None:
            m = TOTAL_RE.search(body or "")
            announced = int(m.group(1)) if m else None
        cards = [c for c in (list_card(m.group(1))
                             for m in CARD_RE.finditer(body or "")) if c]
        fresh_cards = [c for c in cards if c["id"] not in seen]
        if not fresh_cards:
            break
        seen.update(c["id"] for c in fresh_cards)
        out.extend(fresh_cards)
        if len(cards) < PAGE_SIZE:
            break
        time.sleep(delay)
    return out, announced


def keep(card: dict, a) -> bool:
    if a.posted_within_days:
        if not card.get("published"):
            return False
        try:
            age = (dt.date.today()
                   - dt.date.fromisoformat(card["published"])).days
        except ValueError:
            return False
        if age > a.posted_within_days:
            return False
    return True


def cmd_list(a):
    params = build_params(a)
    rows, announced = sweep(params, a.pages, not a.cached, a.delay)
    kept = [r for r in rows if keep(r, a)]

    print(f"[fhf] {len(kept)} of {len(rows)} ads kept "
          f"({a.pages} page(s) requested, {PAGE_SIZE}/page)", file=sys.stderr)
    if announced:
        print(f"  the board announces {announced} ads for this search",
              file=sys.stderr)
    if len(rows) >= a.pages * PAGE_SIZE:
        print("  that is the page budget, not the end of the board — raise "
              "--pages or narrow the filters rather than reading this as the "
              "whole sector.", file=sys.stderr)
    if a.cached:
        print("  --cached: served from the site's edge cache, which was "
              "measured four days stale on the unparameterised page.",
              file=sys.stderr)

    for r in kept:
        if a.details:
            full = read_ad(r["id"], not a.cached)
            time.sleep(a.delay)
            if full:
                r = {**r, **{k: v for k, v in full.items() if v is not None}}
            else:
                r["verdict"] = "closed"
        print(json.dumps(r, ensure_ascii=False))
    return 0


def cmd_ad(a):
    row = read_ad(a.id, not a.cached)
    if row is None:
        die(f"no ad {a.id} — it was filled or withdrawn. Record it as "
            f"discarded.", code=3)
    print(json.dumps(row, ensure_ascii=False, indent=1))
    return 0


def cmd_check(a):
    row = read_ad(a.id, not a.cached)
    if row is None:
        verdict, why = "closed", "the site answers 404 for this id"
    else:
        closes = row.get("closes")
        gone = False
        if closes:
            try:
                gone = dt.date.fromisoformat(closes) < dt.date.today()
            except ValueError:
                gone = False
        verdict = "expired" if gone else "open"
        why = (f"closing date {closes} is in the past" if gone
               else f"published, closing date {closes or 'not set'}")
    print(json.dumps({"id": a.id, "verdict": verdict, "why": why,
                      "url": AD.format(a.id)}, ensure_ascii=False))
    return 0 if verdict == "open" else 3


def cmd_categories(a):
    for code, label in CATEGORIES.items():
        print(f"{code:<8} {label}")
    return 0


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cached", action="store_true",
                   help="use the site's edge cache (faster, up to a week old)")
    p.add_argument("--delay", type=float, default=DELAY,
                   help=f"pause between requests, seconds (default {DELAY})")
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="sweep the board")
    li.add_argument("--search", help="keywords (maps to `keyword`)")
    li.add_argument("--category", help="job category code — see `categories`")
    li.add_argument("--department", help="département code, e.g. 69 or 2A")
    li.add_argument("--contract", help="e.g. CDI, CDD, Mutation, Détachement")
    li.add_argument("--structure", help="numeric establishment id")
    li.add_argument("--posted-within-days", type=int)
    li.add_argument("--pages", type=int, default=5,
                    help=f"page budget (default 5 = up to {5 * PAGE_SIZE} ads)")
    li.add_argument("--details", action="store_true",
                    help="read each ad for address, contract and contact "
                         "(one extra request per ad)")

    ad = sub.add_parser("ad", help="one ad in full")
    ad.add_argument("--id", required=True)

    ck = sub.add_parser("check", help="is this ad still live?")
    ck.add_argument("--id", required=True)

    sub.add_parser("categories", help="list the job category codes")

    a = p.parse_args()
    return {"list": cmd_list, "ad": cmd_ad, "check": cmd_check,
            "categories": cmd_categories}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
