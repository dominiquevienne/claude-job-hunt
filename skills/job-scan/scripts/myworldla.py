#!/usr/bin/env python3
"""MyWorld Careers Laos (`laos.myworld-careers.com`) — Laos's SECOND adapter, and NOT the same build as the agency's Myanmar front. The issue proposed one script per `--host` across the agency's country fronts; measurement refutes it. What the two fronts share is a declared sitemap and the agency's reference codes — not one line of markup. Issue #655.

  myworldla.py jobs [--country-code LA] [--max N]     the sitemap, then one request an advert

WHAT IT IS. The Vientiane front of the agency whose Myanmar front is `myworldmm.py` (#638). **Its
adverts are anonymised by the agency** — «Maintenance Manager at a Global Manufacturing
Organization in Pakse, Laos».

**WHY THIS IS A SECOND SCRIPT AND NOT A `--host` FLAG.** #655 proposed «un même script par `--host`
pour les fronts de l'agence». Measured 2026-09-26 on both fronts:

    styles_metaLabel__ / styles_metaValue__   Myanmar: every field     Laos: 0
    the page's labelled field pairs           Myanmar: 5 per advert    Laos: absent
    /jobs listing                             Myanmar: 56 887 B        Laos: 25 137 B, no advert link

*A `--host` flag over `myworldmm.py` would have produced a reader returning `None` on every field* —
what this repository calls «a reader inherited from the neighbour returns `None`, not an error».
**What the fronts DO share is the approach: a sitemap named in the rules file, and the agency's
`TMY…`/`ASI…` consultant codes.** Sharing a markup is not sharing a meaning, and here they do not
even share the markup.

THE RULES. `laos.myworld-careers.com` serves its rules file (`state: read`, `certain: True`), writes
**no Crawl-delay** (2 s are ours) and **names its sitemap**, which answers 200 — 179 `<loc>`, every
one with a `lastmod`, of which **44 adverts** under `/jobs/`. The guard is on the exact path.

**THE STRUCTURED SALARY IS WRONG ON BOTH FRONTS, IN TWO DIFFERENT WAYS.**

    Myanmar   baseSalary  {"currency": "£",   "value": {"minValue": 4}}     <- the number truncated
    Laos      baseSalary  {"currency": "GBP", "value": {"value": "Up to 45,000,000 LAK + Allowances"}}
    Laos page Salary      Up to 45,000,000 LAK + Allowances                 <- the string agrees

Here the *string* is right and the **currency field is wrong**: GBP on a salary the same object
prints in LAK. There the number itself was corrupt. **The rule covering both: carry the salary as the
site prints it, and never carry `baseSalary.currency`** — a British currency on a South-East Asian
salary, twice, from one vendor. *And «45,000,000» is eight digits, so the salary is a labelled field
the telephone rule must not touch.*

**`employmentType` IS THE LITERAL STRING «undefined».** A JavaScript artefact that parses cleanly and
means nothing; it is dropped, and the run says how many adverts carried it. *A field whose value is
«undefined» is worse than absent: `if x` keeps it.*

**AND `jobLocation` SMEARS ONE STRING ACROSS FIVE FIELDS.** `streetAddress`, `addressLocality`,
`addressRegion` **and** `addressCountry` all read «Pakxe, Laos», with `postalCode` «-». Carrying
`addressCountry` would publish a town as a country. **One field is carried, and the record says the
site fills them identically** — so a front that one day fills them properly shows up as a
disagreement instead of passing unnoticed.

**WITHHELD:** e-mail addresses and telephone numbers in free text; the agency's consultants are never
contacted. The employer is anonymised by the agency — `employer` is null **by measurement**,
`employer_anonymised` says so, and `hiringOrganization` (the agency) travels under its own name.

`--country-code` STAMPS.

Measured 2026-09-26 19:2x–22:4x UTC by the declared client, the guard on the exact path: the rules
name `https://laos.myworld-careers.com/sitemap.xml`, 200, 37 086 B — **179 `<loc>`, 44 under
`/jobs/`**; `/jobs` 200, 25 137 B and carries no advert link; one advert read at 94 097 B.
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

HOST = "laos.myworld-careers.com"
SITEMAP = "/sitemap.xml"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
URL_RE = re.compile(r"<url>(.*?)</url>", re.S)
LOC_RE = re.compile(r"<loc>\s*(.*?)\s*</loc>", re.S)
LASTMOD_RE = re.compile(r"<lastmod>\s*(.*?)\s*</lastmod>", re.S)
# La page porte DEUX blocs ld+json : on prend celui qui se declare JobPosting.
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
ADVERT_RE = re.compile(r"/jobs/([A-Z]{2,4}\d+)-")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[myworldla] {msg}", file=sys.stderr)


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
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    # L'element des icones se retire AVANT le strip de balises : une police a
    # ligatures met le nom du pictogramme dans le texte (mesure sur cvconnect.la).
    t = re.sub(r"<i\b[^>]*>.*?</i>", " ", markup or "", flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def money(s):
    """A LABELLED salary: the e-mail scrub only — «45,000,000 LAK» is eight digits."""
    return (MAIL_RE.sub("[e-mail withheld]", s).strip() or None) if s else None


def posting_of(markup):
    for block in LD_RE.findall(markup or ""):
        if '"JobPosting"' not in block:
            continue
        try:
            d = json.loads(block)
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("@type") == "JobPosting":
            return d
    return {}


def adverts_of(sitemap):
    out = []
    for block in URL_RE.findall(sitemap or ""):
        loc = LOC_RE.search(block)
        if not loc:
            continue
        u = htmlmod.unescape(loc.group(1))
        if not ADVERT_RE.search(u):        # `/jobs/` seul est l'index, pas une annonce
            continue
        lm = LASTMOD_RE.search(block)
        out.append((u, lm.group(1) if lm else None))
    return out


def salaire_de(ld):
    """The salary STRING the site prints; never `baseSalary.currency` — see the docstring."""
    bs = ld.get("baseSalary") or {}
    v = bs.get("value")
    val = v if isinstance(v, dict) else {}
    brut = val.get("value")
    if brut is None or isinstance(brut, (int, float)):
        # la forme birmane : un nombre tronque, qui ne dit rien — on ne l'invente pas
        return None
    return money(text(str(brut)))


def lieu_de(ld):
    """One address field, and whether the site filled them identically."""
    a = ((ld.get("jobLocation") or {}).get("address") or {})
    champs = [a.get(k) for k in ("addressLocality", "addressRegion", "streetAddress", "addressCountry")]
    presents = [c for c in champs if c]
    identiques = bool(presents) and len(set(presents)) == 1
    return (presents[0] if presents else None), identiques


def record(url, lastmod, ld, stamp):
    m = ADVERT_RE.search(url)
    ref = m.group(1) if m else None
    ident = ((ld.get("identifier") or {}).get("value")) or ref
    lieu, smeared = lieu_de(ld)
    etype = ld.get("employmentType")
    if isinstance(etype, str) and etype.strip().lower() in ("undefined", "null", ""):
        etype = None                       # « undefined » est pire qu'absent : `if x` le garde
    return {
        "source": "myworldla", "country": stamp,
        "ledger_id": f"myworldla:{ident}", "id": ident, "url": url,
        "reference": ref,
        "title": scrub(ld.get("title")),
        "employer": None, "employer_anonymised": True,
        "agency": (ld.get("hiringOrganization") or {}).get("name"),
        "salary": salaire_de(ld), "contract_type": etype,
        "location": scrub(lieu), "location_fields_identical": smeared,
        "posted": ld.get("datePosted"), "valid_through": ld.get("validThrough"),
        "lastmod": lastmod,
        "description": scrub(text(ld.get("description"))),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    url = f"https://{HOST}{SITEMAP}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the sitemap the rules file names is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    named = adverts_of(body)
    if not named:
        die(f"{url}: 200 but no advert entry — the sitemap changed shape; not an empty board", EXIT_PARTIAL)

    rows, manques, sans_ld, undef, smear = [], 0, 0, 0, 0
    for u, lm in named:
        if a.max and len(rows) >= a.max:
            break
        c, page = request(u)
        if c != 200:
            manques += 1
            note(f"{u}: HTTP {c} — advert skipped")
            continue
        ld = posting_of(page)
        if not ld:
            sans_ld += 1
        brut_type = ld.get("employmentType")
        r = record(u, lm, ld, stamp)
        if r["contract_type"] is None and isinstance(brut_type, str) and brut_type.strip():
            undef += 1
        if r["location_fields_identical"]:
            smear += 1
        rows.append(r)

    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

    plafonne = bool(a.max and len(rows) >= a.max)
    note(f"{len(rows)} emitted, the site's own sitemap names {len(named)} advert(s)"
         + (f", {manques} unreachable" if manques else "")
         + (" — stopped by --max" if plafonne else ""))
    if sans_ld:
        note(f"{sans_ld} advert(s) carried no JobPosting JSON-LD — fields null by absence, not by parse failure.")
    if undef:
        note(f"{undef} advert(s) wrote `employmentType: \"undefined\"` — dropped; it parses cleanly and means nothing.")
    if smear:
        note(f"{smear} advert(s) fill every address field with the SAME string — one is carried, `location_fields_identical` says so.")
    note("baseSalary.currency is never carried: this vendor writes GBP (Laos) and £ (Myanmar) on South-East Asian salaries.")
    note("employers are anonymised by the agency — `employer` is null by measurement, not by omission.")
    if stamp:
        note(f"country {stamp} is the user's stamp.")
    if not plafonne and len(rows) + manques != len(named):
        die(f"{len(rows)} emitted + {manques} unreachable != {len(named)} named — row(s) dropped in silence", EXIT_PARTIAL)


def main(argv=None):
    p = argparse.ArgumentParser(description="MyWorld Careers Laos — the sitemap the rules file declares is the route; the salary string is carried and never baseSalary.currency. Issue #655.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the sitemap, then one request an advert")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record")
    j.add_argument("--max", type=int, default=0, help="stop after N adverts (0 = all the sitemap names)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
