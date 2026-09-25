#!/usr/bin/env python3
"""MyWorld Careers (`www.myworld.com.mm`), Myanmar: a Yangon recruitment agency's board. The site DECLARES its sitemap in its own rules file, so the enumeration is published, not guessed — 219 advert URLs on 2026-09-25, and that count is printed beside the emitted one. Issue #638.

  myworldmm.py jobs [--country-code MM] [--max N]     the sitemap, then one request an advert

WHAT IT IS. An agency, not a job board: **its adverts are anonymised by design** — «Purchasing
Manager at a Leading International Chemicals Factory in Yangon». Myanmar's other routes are
`myjobsmm.py`, `jobnetmm.py`, `myanmargov.py` and `bestjobmyanmar.py`.

THE RULES. `www.myworld.com.mm` serves its rules file (`state: read`, `certain: True`), writes **no
Crawl-delay** (2 s are ours), and **names its sitemap there**. The guard is taken on the exact path.

**TWO FIELDS OF THE JSON-LD ARE WRONG, AND THEY ARE THE TWO A MACHINE WOULD TRUST MOST.**

Every advert carries a `JobPosting` JSON-LD. It is the site's own structured declaration, it parses,
and on two fields it says something the rendered page contradicts:

    baseSalary        {"currency": "£", "value": {"unitText": "YEAR", "minValue": 4}}
    the page          Salary   Up to 4,000,000 MMK + Other Allowances

**«£4 per year» for a job paying four million kyats.** The structured field has kept the leading
digit of «4,000,000» and a pound sign from a template. *An adapter that prefers JSON-LD because it
is structured would publish that, and nothing would contradict it: it is well-formed, parseable,
and plausible to anything that does not also read the page.* **The salary is therefore read from
the LABELLED field the page prints, and the JSON-LD's is not carried at all.**

    hiringOrganization   {"name": "MyWorld Myanmar", "sameAs": "https://www.myworld.com.mm"}

**That is the AGENCY, not the employer.** Taking it as the employer would attribute all 219 adverts
to one company. The employer is anonymised on purpose and the record says so — `employer` is null,
`employer_anonymised` is true, and the agency travels under its own name.

> **A structured field is not the truer one because it is structured.** *Here the machine-readable
> half of the page is the wrong half, and only reading both shows it.*

**AND THE CLASS NAMES ARE BUILD ARTEFACTS.** The pairs are `styles_metaLabel__qSmzr` /
`styles_metaValue__8o2_t` — CSS-module hashes that change on any rebuild. The patterns match the
stable prefix and ignore the hash; anchoring on `__qSmzr` would break silently at the next deploy,
and a board that suddenly yields no field reads exactly like a board that stopped publishing.

**WITHHELD:** e-mail addresses and telephone numbers in free text; the agency's consultants are
never contacted. **The salary is a labelled field and the telephone rule does not touch it** —
«4,000,000» is seven digits, the shape that destroyed 113 salaries on `myjobs.com.mm`.

`--country-code` STAMPS; the records carry «Yangon, Myanmar (Burma)» as the site writes it.

Measured 2026-09-25 18:1x UTC by the declared client, the guard on the exact path: the rules name
`https://www.myworld.com.mm/sitemap.xml`, which answers 200, 166 099 B — **836 `<loc>`, every one
with a `lastmod`, of which 219 under `/jobs/`**. `/jobs` answers 200, 56 887 B and states no count
and no pager, which is why the sitemap is the route.
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

HOST = "www.myworld.com.mm"
SITEMAP = "/sitemap.xml"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
LOC_RE = re.compile(r"<loc>\s*(.*?)\s*</loc>", re.S)
URL_RE = re.compile(r"<url>(.*?)</url>", re.S)
LASTMOD_RE = re.compile(r"<lastmod>\s*(.*?)\s*</lastmod>", re.S)
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
# **Le hash des modules CSS change a chaque build : on matche le prefixe, jamais le hash.**
META_RE = re.compile(r'<span class="styles_metaLabel__[^"]*">(.*?)</span>\s*'
                     r'<span class="styles_metaValue__[^"]*">(.*?)</span>', re.S)
REF_RE = re.compile(r"/jobs/([A-Z]{2,4}\d+)-")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[myworldmm] {msg}", file=sys.stderr)


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
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def money(s):
    """A LABELLED salary: the e-mail scrub only — «4,000,000 MMK» is seven digits."""
    return (MAIL_RE.sub("[e-mail withheld]", s).strip() or None) if s else None


def adverts_of(sitemap):
    """(url, lastmod) for every `/jobs/` entry the site's own sitemap names."""
    out = []
    for block in URL_RE.findall(sitemap or ""):
        loc = LOC_RE.search(block)
        if not loc or "/jobs/" not in loc.group(1):
            continue
        lm = LASTMOD_RE.search(block)
        out.append((htmlmod.unescape(loc.group(1)), lm.group(1) if lm else None))
    return out


def meta_of(markup):
    out = {}
    for lab, val in META_RE.findall(markup or ""):
        k = text(lab)
        if k and k not in out:
            out[k] = text(val)
    return out


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


def record(url, lastmod, meta, ld, stamp):
    ref = (REF_RE.search(url) or [None, meta.get("Reference")])[1] if REF_RE.search(url) else meta.get("Reference")
    agency = (ld.get("hiringOrganization") or {}).get("name")
    return {
        "source": "myworldmm", "country": stamp,
        "ledger_id": f"myworldmm:{ref}", "id": ref, "url": url,
        "title": scrub(ld.get("title")) or scrub(text(meta.get("Title"))),
        # **L'employeur est anonymise PAR L'AGENCE, et ce n'est pas une lacune.**
        # `hiringOrganization` nomme l'agence : la prendre pour l'employeur
        # attribuerait les 219 annonces a une seule entreprise.
        "employer": None, "employer_anonymised": True, "agency": agency,
        "sector": meta.get("Sector"), "location": meta.get("Location"),
        "contract_type": meta.get("Type"),
        # le salaire vient de la PAGE, jamais du JSON-LD (voir le docstring)
        "salary": money(meta.get("Salary")),
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
        die(f"{url}: 200 but no /jobs/ entry — the sitemap changed shape; not an empty board", EXIT_PARTIAL)

    rows, manques = [], 0
    for u, lm in named:
        if a.max and len(rows) >= a.max:
            break
        c, page = request(u)
        if c != 200:
            manques += 1
            note(f"{u}: HTTP {c} — advert skipped")
            continue
        rows.append(record(u, lm, meta_of(page), posting_of(page), stamp))

    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

    plafonne = bool(a.max and len(rows) >= a.max)
    note(f"{len(rows)} emitted, the site's own sitemap names {len(named)} advert(s)"
         + (f", {manques} unreachable" if manques else "")
         + (" — stopped by --max" if plafonne else ""))
    sans = sum(1 for r in rows if not r["salary"])
    if sans:
        note(f"{sans} of {len(rows)} advert(s) print no salary; the JSON-LD's baseSalary is never carried (it says «£4/YEAR» for 4,000,000 MMK).")
    note("employers are anonymised by the agency — `employer` is null by measurement, not by omission.")
    if stamp:
        note(f"country {stamp} is the user's stamp.")
    # **LA COMPARAISON PRECEDENTE ETAIT MORTE, PAS SEULEMENT INERTE — 25.09.2026.**
    # Elle disait `not manques and len(rows) != len(named)` : or une ligne est
    # ajoutee pour CHAQUE 200, donc `len(rows) != len(named)` n'arrive que si
    # `manques > 0`, ce que la meme condition exclut. **Elle ne pouvait pas tirer.**
    # *Une garde inerte peut au moins rougir un jour ; celle-la etait vide.*
    # Ce qui se controle vraiment est une INVARIANTE : tout ce que le sitemap nomme
    # est soit emis, soit compte comme injoignable. Si une ligne disparait en
    # silence — un `continue` ajoute plus tard, un enregistrement qui leve — la
    # somme cesse de coller et le dit.
    if not plafonne and len(rows) + manques != len(named):
        die(f"{len(rows)} emitted + {manques} unreachable != {len(named)} named by the sitemap"
            f" — {len(named) - len(rows) - manques} row(s) dropped in silence", EXIT_PARTIAL)


def main(argv=None):
    p = argparse.ArgumentParser(description="MyWorld Careers — the sitemap the rules file declares is the route; the salary is read from the page, never from the JSON-LD. Issue #638.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the sitemap, then one request an advert")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record")
    j.add_argument("--max", type=int, default=0, help="stop after N adverts (0 = all the sitemap names)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
