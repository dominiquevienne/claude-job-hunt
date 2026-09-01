#!/usr/bin/env python3
"""Fetch farm jobs from lagriculture-recrute.org — the ANEFA board.

**2 818 offres** of French agricultural work: harvests, vineyards, livestock,
market gardening, farm machinery. The ANEFA is the sector's own employment
association, so this is the one place these ads are gathered — no generalist
board carries the seasonal ones in any useful number.

The ads answer the questions seasonal work actually turns on, and no other
board in this repository has these fields at all:

    Hébergement possible        Oui / Non   + free-text details
    Repas sur place possible    Oui / Non   + free-text details
    Type d'agriculture          Conventionnelle / Bio
    CertiPhyto, Caces, Permis   the certificates a farm asks for

For someone driving 300 km for six weeks of picking, whether there is a bed is
the question that decides, before the pay.

  GET /rechercher/offres
      ?offer_search[geography][type]=department
      &offer_search[geography][department]=<internal id>
      &page=<n>                                        20 ads a page

**The department parameter is not the department number.** It is an internal
ordinal, and Corsica makes it drift: see `departments()`. The map is read from
the site's own form, never computed.

Usage:
  anefa.py departements
  anefa.py search --departement 29 --pages 5
  anefa.py search --all --pages 3

Output: one JSON object per line.
"""

import argparse
import html as html_mod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://www.lagriculture-recrute.org"
LIST = BASE + "/rechercher/offres"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

PER_PAGE = 20

AD_RE = re.compile(r"/rechercher/offres/(\d+)")
TOTAL_RE = re.compile(r"(\d[\d\s ]*)\s*offres", re.I)
DEPT_SELECT_RE = re.compile(
    r'name="offer_search\[geography\]\[department\]"(.*?)</select>', re.S)
OPTION_RE = re.compile(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)')
# <div class="form-group"><label>Nom</label><br /><span …>Valeur</span></div>
FIELD_RE = re.compile(
    r'<label>(.*?)</label>\s*<br\s*/?>(.*?)'
    r'(?=<div class="form-group">|</div>\s*</div>)', re.S | re.I)
REF_RE = re.compile(r"Référence\s+(\S+)")
PLACE_RE = re.compile(r"Lieu de la mission\s+([^()]+)\((\d{5})\)")
TITLE_RE = re.compile(r"Retour aux offres\s+(.{5,140}?)\s+Modalités")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def get(url, params=None, retries=2):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "fr-FR,fr;q=0.9",
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            die(f"anefa returned HTTP {e.code} for {url}")
        except Exception as e:  # noqa: BLE001 - network shape varies
            if attempt == retries:
                die(f"could not reach anefa: {e}")
            time.sleep(1.5)


def strip(markup):
    txt = re.sub(r"<[^>]+>", " ", markup or "")
    return re.sub(r"\s+", " ", html_mod.unescape(txt)).strip()


def text_of(page):
    body = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", page)
    return re.sub(r"\s+", " ", html_mod.unescape(re.sub(r"<[^>]+>", " ", body)))


def total(page):
    m = TOTAL_RE.search(text_of(page))
    if not m:
        return None
    return int(re.sub(r"\D", "", m.group(1)))


def departments():
    """{'29': '30', …} — department number to the site's internal id.

    **Read, never computed.** The values are an ordinal over a list in which
    **Corsica takes two slots (2A and 2B) where the numbering has one**, so
    from department 21 onwards the id is the department **plus one**:

        01…19 → 1…19        identity
        2A → 20, 2B → 21    the two slots
        21 → 22 … 95 → 96   department + 1
        971… → 97…          different again overseas

    Getting this wrong is not an error, it is a plausible wrong answer:
    asking for `29` returns **24 ads in the Eure-et-Loir (28)**, 400 km from
    the Finistère, every one a genuine French farm job. The right id, 30,
    returns 200 ads in the Finistère.
    """
    page = get(LIST)
    m = DEPT_SELECT_RE.search(page)
    if not m:
        die("could not find the department select on the search page. The "
            "form changed; do not fall back to using the department number "
            "as the id — read `departments()` for why.")
    out = {}
    for value, label in OPTION_RE.findall(m.group(1)):
        label = strip(label)
        if not value or " - " not in label:
            continue
        out[label.split(" - ")[0].strip()] = value
    if not out:
        die("the department select was found but held no options.")
    return out


def card(ident):
    page = get(f"{BASE}/rechercher/offres/{ident}")
    t = text_of(page)
    fields = {}
    for m in FIELD_RE.finditer(page):
        k, v = strip(m.group(1)), strip(m.group(2))
        if k and k not in fields:
            fields[k] = v or None
    place = PLACE_RE.search(t)
    ref = REF_RE.search(t)
    title = TITLE_RE.search(t)
    desc = None
    i = t.find("Descriptif du poste")
    if i >= 0:
        desc = t[i + len("Descriptif du poste"):].split("Partager")[0].strip()
    return {
        "id": ident,
        "ledger_id": f"anefa:{ident}",
        "url": f"{BASE}/rechercher/offres/{ident}",
        "reference": ref.group(1) if ref else None,
        "title": title.group(1).strip() if title else None,
        "locality": place.group(1).strip() if place else None,
        "postcode": place.group(2) if place else None,
        # No employer field exists on this board — see the adapter doc. What
        # the farm is appears in the description prose, when it appears.
        "company": None,
        "contract": fields.get("Contrat proposé"),
        "contract_months": fields.get("Durée du contrat"),
        # Free text, not a number: "Taux horaire brut: entre 12 et 14 €".
        "salary_text": fields.get("Salaire"),
        "starts": fields.get("Date prévue d'embauche"),
        "positions": fields.get("Nombre de postes recherchés"),
        "experience": fields.get("Expérience requise"),
        "training_level": fields.get("Niveau de formation"),
        "sectors": fields.get("Secteurs"),
        "farming_type": fields.get("Type d'agriculture"),
        # The fields that decide a seasonal job and exist on no other board
        # here. Present on every ad measured.
        "housing": fields.get("Hébergement possible"),
        "housing_details": fields.get("Détails concernant l`hébergement"),
        "meals": fields.get("Repas sur place possible"),
        "meals_details": fields.get("Détails concernant les repas"),
        "caces": fields.get("Caces"),
        "certiphyto": fields.get("CertiPhyto"),
        "licence": fields.get("Permi souhaité"),
        "benefits": fields.get("Avantages"),
        "description": desc,
        # Anything the page labelled that this adapter does not name, kept
        # rather than dropped — the site adds sector-specific fields.
        "other_fields": {k: v for k, v in fields.items() if k not in {
            "Contrat proposé", "Durée du contrat", "Salaire",
            "Date prévue d'embauche", "Nombre de postes recherchés",
            "Expérience requise", "Niveau de formation", "Secteurs",
            "Type d'agriculture", "Hébergement possible", "Repas sur place possible",
            "Détails concernant l`hébergement", "Détails concernant les repas",
            "Caces", "CertiPhyto", "Permi souhaité", "Avantages"}},
    }


def sweep(params, pages, delay, details, label):
    seen, rows, page_no, announced = set(), 0, 1, None
    while page_no <= pages:
        p = dict(params)
        if page_no > 1:
            p["page"] = page_no
        page = get(LIST, p)
        if announced is None:
            announced = total(page)
            print(f"[anefa] {announced if announced is not None else '?'} "
                  f"offres for {label}", file=sys.stderr)
        ids = [i for i in dict.fromkeys(AD_RE.findall(page)) if i not in seen]
        if not ids:
            # Measured exact: 140 pages of 20 then 18, and page 142 onwards
            # comes back with no ads at all — and no total either.
            break
        for ident in ids:
            seen.add(ident)
            print(json.dumps(card(ident) if details else {
                "id": ident, "ledger_id": f"anefa:{ident}",
                "url": f"{BASE}/rechercher/offres/{ident}"},
                ensure_ascii=False))
            rows += 1
            if details:
                time.sleep(delay)
        page_no += 1
        time.sleep(delay)
    print(f"[anefa] {rows} ads collected", file=sys.stderr)
    if announced and rows < announced and page_no > pages:
        print(f"[anefa] {rows} of {announced} — raise --pages", file=sys.stderr)


def cmd_departements(_a):
    for dep, ident in sorted(departments().items(),
                             key=lambda kv: (len(kv[0]), kv[0])):
        print(f"{dep}\t{ident}")


def cmd_search(a):
    if a.all and a.departement:
        die("--all and --departement are exclusive.")
    if a.all:
        params, label = {}, "France entière"
    elif a.departement:
        table = departments()
        dep = a.departement.strip().upper()
        if dep not in table:
            die(f"{dep!r} is not a department this board knows. Run "
                "`departements` for the list — and do not pass the "
                "department number as the id: this board's ids are an "
                "ordinal that drifts by one past Corsica, so a wrong value "
                "returns a full page of ads in the wrong department rather "
                "than an error.")
        params = {
            # Both are required. With only the value and no `type`, the
            # filter is dropped in silence and the whole board comes back.
            "offer_search[geography][type]": "department",
            "offer_search[geography][department]": table[dep],
        }
        label = f"département {dep} (id {table[dep]})"
    else:
        die("give --departement or --all.")
    sweep(params, a.pages, a.delay, not a.no_details, label)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("departements",
                   help="department → internal id, read live").set_defaults(
        func=cmd_departements)
    s = sub.add_parser("search", help="sweep one department, or all")
    s.add_argument("--departement", help="the real number: 29, 2A, 971")
    s.add_argument("--all", action="store_true", help="the whole board")
    s.add_argument("--pages", type=int, default=5, help="20 ads each")
    s.add_argument("--delay", type=float, default=0.5)
    s.add_argument("--no-details", action="store_true")
    s.set_defaults(func=cmd_search)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
