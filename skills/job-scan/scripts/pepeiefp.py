#!/usr/bin/env python3
"""PEPE — IEFP Cabo Verde (`pepe.iefp.cv`), the public employment institute's platform: its two public lists — «Ofertas de Emprego» and «Ofertas de Estágio profissional Empresarial» — are rendered server-side in a table whose header names its own cells. Issue #693.

  pepeiefp.py jobs [--kind both] [--lang pt] [--country-code CV]     both lists (1 request each)

WHAT IT IS. PEPE («Plataforma de Estágios Profissionais e Emprego») is the platform of the
**Instituto do Emprego e Formação Profissional**, Cabo Verde's public employment service. Employers
file vacancies and internships on it and candidates apply through an account.

**THE ISSUE'S PREMISE WAS STALE, AND THIS IS THE READING THAT REOPENED IT.** #693 records, dated
2026-09-18, «aucune route publique trouvée par cette lecture ; ce qui rouvrirait l'issue : une page
de liste publique de la plateforme que la recherche n'a pas fait remonter» — the search had asked
`/frontend/web/pt/site/ofertas`, which answers 404. The platform's own Angular bundle
(`main.4fea70c6e545a598091f.js`) names the two pages it links to from its home cards:
`/frontend/web/<lang>/site/oferta-emprego` and `/oferta-estagio`. **Both answer 200 to the declared
client, with no account and no login**, and each renders its list as HTML. *The account is needed to
APPLY, not to read* — and those are two different statements about the same platform.

THE RULES. `pepe.iefp.cv` answers 200 to `/robots.txt` with a body that is the Angular shell, so no
rule is read: open, `certain: False`, no Crawl-delay; 2 s is ours. The guard is taken on the exact
path.

THE LIST. `/frontend/web/<lang>/site/oferta-emprego` (200; 9 444 B) and `.../oferta-estagio` (200;
10 131 B) each carry one `<table>` whose `<thead>` names five cells — Designação · Validade · Vagas ·
Entidade · Referência (Designation · Validity · Vacancies · Entity · Reference in `en`) — and one
`<tr>` a row. **The adapter reads the cells BY POSITION and refuses a header that does not carry
exactly five** (a column added or dropped would shift every field silently). There is **no pager and
no stated count**: what the table lists is what the platform publishes today, and the run says so
rather than printing a total it did not read.

**The row's own link answers 404.** The list publishes
`/frontend/web/<lang>/oportunidades/oferta-<kind>?value=<designação>` and that address answered
**404** on 2026-09-21 in both shapes (with and without `index.php`) — measured, not inferred. The
record carries the address **as the platform publishes it** (`url`, with `url_answered_404` naming
the day it was tried) and the adapter never follows it; a detail page that comes back is a change on
their side, not on ours.

**WITHHELD:** e-mail addresses and telephone numbers anywhere in a cell («[e-mail withheld]» /
«[telephone withheld]», a date never mistaken for a number); `contacts_withheld` on every record.
The platform states no place beyond the employer's name, so none is invented.

`--kind` picks a list (`emprego`, `estagio`, `both` — default both). `--lang` picks the interface
language (`pt`, `en`, `fr`; the entries themselves are Portuguese whatever it says, and the run does
not translate). `--country-code` STAMPS (the table states no country — every row is Cabo Verde by
the platform's own scope, and a stamp is still the user's) and the run says so.

Measured 2026-09-21 13:51–14:0x UTC by the declared client, the guard on the exact path, two reads
of each list: `oferta-emprego` 200 ×2 (9 444 B, md5 3cb132bfe3e5 / d0ada41efc4a — **the CSRF meta
moves, the list does not**: identical to the byte once that one tag is removed), **1 row**;
`oferta-estagio` 200 ×2 (10 131 B, fa8fdc74a617 / 481d8ad6f624, same identity once the tag is
removed), **3 rows**. **4 entries, no count stated.** `backend/web/index.php?r=api/empregos`, the
JSON call the home page's cards make, answers **404** — the two HTML lists are the route.
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

HOST = "pepe.iefp.cv"
KINDS = ("emprego", "estagio")
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\(?\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")   # «(+238) 261 64 46»: the paren comes BEFORE the plus here
DATE_RE = re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")
REF_RE = re.compile(r"^\d{1,4}/\d{4}$")        # «176/2024» is the platform's filing number, and it has the shape of a phone number
TABLE_RE = re.compile(r"<table[^>]*>(.*?)</table>", re.S)
HEAD_RE = re.compile(r"<thead>(.*?)</thead>", re.S)
TH_RE = re.compile(r"<th[^>]*>(.*?)</th>", re.S)
BODY_RE = re.compile(r"<tbody>(.*?)</tbody>", re.S)
TR_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
HREF_RE = re.compile(r"<a\s[^>]*href=(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))", re.S)   # the platform writes its hrefs UNQUOTED
CELLS = 5
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[pepeiefp] {msg}", file=sys.stderr)


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
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th_fmt(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return " ".join(t.split()) or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    if REF_RE.match(s.strip()):                  # a reference, not a number to call — measured on `176/2024`, 2026-09-21
        return s.strip()
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def when(s):
    """«02-06-2027» → `2027-06-02`; anything else as read."""
    s = (s or "").strip()
    m = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})$", s)
    return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}" if m else (s or None)


def count(s):
    """«3» → 3; a cell that is not a plain count stays out rather than becoming a wrong number."""
    s = (s or "").strip()
    return int(s) if re.match(r"^\d{1,4}$", s) else None


def href_of(cell):
    m = HREF_RE.search(cell or "")
    if not m:
        return None
    raw = htmlmod.unescape(m.group(1) or m.group(2) or m.group(3) or "")
    return urllib.parse.urljoin(f"https://{HOST}/", raw) if raw else None


def rows_of(markup, kind, url):
    """The list page → [(key, fields)]. The header must name exactly five cells, or the page changed."""
    tables = TABLE_RE.findall(markup or "")
    if not tables:
        return None, "no table"
    table = tables[0]
    head = HEAD_RE.search(table)
    heads = [text(h) for h in TH_RE.findall(head.group(1))] if head else []
    if len(heads) != CELLS:
        return None, f"the header names {len(heads)} cell(s), not {CELLS}: {heads}"
    body = BODY_RE.search(table)
    out = []
    for tr in TR_RE.findall(body.group(1) if body else ""):
        tds = TD_RE.findall(tr)
        if len(tds) != CELLS:
            return None, f"a row carries {len(tds)} cell(s), not {CELLS}"
        title, validity, vacancies, entity, reference = (text(c) for c in tds)
        if not title:
            continue
        key = reference or title
        out.append((f"{kind}:{key}", {
            "kind": kind, "title": title, "deadline": validity, "openings": vacancies,
            "employer": entity, "reference": reference, "url": href_of(tds[0]), "list_url": url,
            "headers": heads,
        }))
    return out, None


def record(key, f, stamp):
    return {
        "source": "pepeiefp", "country": stamp,
        "ledger_id": f"pepeiefp:{key}", "id": key,
        "kind": f["kind"],
        "title": scrub(f.get("title")),
        "employer": scrub(f.get("employer")),
        "deadline": when(f.get("deadline")),
        "openings": count(f.get("openings")),
        "reference": scrub(f.get("reference")),
        "url": f.get("url"),
        "url_answered_404": "2026-09-21",     # the address the list publishes, tried and consigned — never followed by the run
        "list_url": f.get("list_url"),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    lang = (a.lang or "pt").strip().lower()
    if not re.match(r"^[a-z]{2}$", lang):
        die(f"--lang {a.lang}: two letters (pt, en, fr)")
    kinds = KINDS if a.kind == "both" else (a.kind,)
    stamp = a.country_code.upper() if a.country_code else None
    rows, seen, read = [], set(), []
    for kind in kinds:
        url = f"https://{HOST}/frontend/web/{lang}/site/oferta-{kind}"
        code, body = request(url)
        if code == 404:
            die(f"{url}: HTTP 404 — no such list", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        found, why = rows_of(body, kind, url)
        if found is None:
            die(f"{url}: 200 but its table is not the one measured ({why}) — the page changed; not an empty list", EXIT_PARTIAL)
        read.append((kind, len(found)))
        for k, f in found:
            if k in seen:
                continue
            seen.add(k)
            rows.append(record(k, f, stamp))
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    listed = ", ".join(f"{kind} {th_fmt(n)}" for kind, n in read)
    if not rows:
        note(f"0 entries — the list(s) answered 200 and their table carries no row ({listed}); not an error.")
    else:
        note(f"{th_fmt(len(rows))} entries emitted from {th_fmt(len(read))} list(s) ({listed}); no pager and no stated count — what the table lists is the board.")
    note("the row's own link answered 404 on 2026-09-21 in both path shapes; it is published as the platform publishes it and never followed.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the table states no country.")
    note("PEPE needs an account to APPLY, not to read these two lists; the plugin creates none and never logs in.")


def main(argv=None):
    p = argparse.ArgumentParser(description="PEPE — IEFP Cabo Verde: the platform's two public lists, read from the table whose header names its cells. Issue #693.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the public lists (1 request each)")
    j.add_argument("--kind", choices=("emprego", "estagio", "both"), default="both", help="which list — default both")
    j.add_argument("--lang", default="pt", help="the interface language (pt, en, fr) — default pt")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the table states none)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
