#!/usr/bin/env python3
"""Offres d'emploi de l'État de Genève (`www.ge.ch`) — one employer, 82 vacancies, server-rendered.

  gech.py list [--type CDD|CDI|apprentissage] [--taux-max N] [--classe-min N]
               [--departement <part of its name>] [--no-rss-check] [--limit N]
  gech.py ad   --url <advertisement URL>   |   --id <integer>

ONE EMPLOYER, AND THAT IS THE POINT — #203, #204

The canton is one employer in law and eight departments, a judiciary, a court
of auditors and a parliament's secretariat in practice, each publishing on this
one list. *«&nbsp;un adaptateur pour un seul employeur peut avoir un
intérêt&nbsp;»* — the owner's rule of 2026-09-09: an adapter also exists so a
user can read ONE segment of the market. This one reads the canton's, with the
five filters the site's own form offers. **No apology for the single
employer**, and no claim that the shape generalises until a second canton is
measured.

THE LIST IS ONE PAGE, SERVER-RENDERED, AND STATES NO TOTAL

`GET /offres-emploi-etat-geneve/liste-offres` answers 200, ~245 kB, and every
vacancy is an `<article>` in the body — 82 of them on 2026-09-11, 75 on
2026-09-09 (#203). No pagination was found and none was needed: the page holds
the whole list. **Nothing on it states a total**, so «82 emitted, page states
no total» is what this adapter prints — and the anchor comes from a second
route instead:

  GET /rss/offres-emploi-etat-geneve?departement=0&…    82 <item>, 82 <guid>

The RSS and the list gave the SAME 82 ids on 2026-09-11. It is read by default
and compared id by id, because it is the only figure here that does not come
from the pattern that produced the count — **a second route of the same
operator on the same day**: it catches an `<article>` pattern that stopped
matching, and nothing else (a shared defect upstream would show in both).
Skipped with `--no-rss-check`, and never compared when a filter is on — the
two would then answer different questions.

EVERY ADVERTISEMENT CARRIES A JOBPOSTING IN JSON-LD

#203 counted 0 JSON-LD blocks — on the LIST page, which is right. The
advertisement page carries exactly one `JobPosting` (measured on id 2002,
2026-09-11): `datePosted`, `validThrough`, `jobStartDate`, `employmentType`,
`hiringOrganization` («Etat de Genève»), `employmentUnit.url` (the
department), `jobLocation.address` (a street and a postcode, one string),
`experienceRequirements` and `jobBenefits` — and a `description` whose text is
HTML-ESCAPED inside the JSON (`&#039;`), so it is unescaped after parsing.
**`experienceRequirements` is the field the report says decided its verdict**
— «Master en informatique», «8 ans minimum» — and it is not on the list card,
which is why `ad` exists.

The page adds what the JSON-LD lacks: the salary class («classe 25»), the rate
(«80 à 100%»), the closing date («Délai d'inscription : 25.09.2026»), and the
apply link (`sirhrecrutement/…/candidatAction.do?NOREFPOSTE=115353`) whose
`NOREFPOSTE` is the HR system's own reference, carried beside the URL id.

TWO DATE TRAPS. The RSS `pubDate` is not the posting date (id 2048: pubDate
11 Sep 09:50 UTC, the day of the read) — read `datePosted` on the page. And
`jobStartDate` in the JSON-LD is THE DAY OF THE READ when the page says «Dès
que possible» (id 2002: `jobStartDate: 2026-09-11`, read 2026-09-11, page
«Entrée en fonction : Dès que possible»). `starts_text` carries the words;
`starts` alone would say a job started the day you looked.

MEASURED ON ONE LIST PAGE, ONE RSS, ONE ADVERTISEMENT, 2026-09-11, and the
card says so.
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
from _ldjson import absent_reason, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BASE = "https://www.ge.ch"
LIST_PATH = "/offres-emploi-etat-geneve/liste-offres"
LIST = BASE + LIST_PATH
RSS = BASE + "/rss/offres-emploi-etat-geneve"
AD_RE = re.compile(r"^/offres-emploi-etat-geneve/liste-offres/(\d+)/?$")

# The five filters of the site's own form (`<form id="gech-offres-emploi-filters">`,
# 2026-09-11). Their values are the form's: department and domain are UUIDs
# read off the page at run time, never hard-coded; the class option is
# `classe - 3` (option 1 = «classe 04» … 30 = «classe 33»); the contract is the
# literal the site uses.
CONTRACT = {"cdd": "CDD", "cdi": "CDI",
            "apprentissage": "Contrat d'apprentissage"}
FILTER_KEYS = ("departement", "domaine_activite", "classe_fonction_min",
               "type_contrat", "taux_activite_max")

ARTICLE_RE = re.compile(r"(?s)<article\b[^>]*>(.*?)</article>")
ID_TITLE_RE = re.compile(
    r'(?s)href="/offres-emploi-etat-geneve/liste-offres/(\d+)"[^>]*>(.*?)</a>')
# The entity block has THREE shapes on one page (2026-09-11, 82 cards): a
# link to `www.ge.ch/organisation/<slug>` (66), a link to another host —
# `justice.ge.ch` for the judiciary — and a bare `<p>` with no link at all
# («Secrétariat général du Grand Conseil», «Autres»). A pattern written for
# the first read 66 of 82 and left 16 entities empty. What the three share is
# the class `text-label-medium`; the office is the `<p>` that follows.
ENTITY_RE = re.compile(
    r'(?s)(?:<a class="text-label-medium[^"]*"[^>]*href="([^"]*)"[^>]*>\s*<p>(.*?)</p>\s*</a>'
    r'|<p class="text-label-medium">(.*?)</p>)\s*<p>(.*?)</p>')
RATE_RE = re.compile(r'(?s)<span class="chips-outlined">\s*(.*?)\s*</span>')
# «classe 12» on 79 of 82; «À définir» on the three traineeships (2026-09-11).
# Carried as the site writes it — a pattern on `classe \d+` reported those
# three as having no class, which is not what the page says.
CLASS_RE = re.compile(r"(?s)<span data-text>\s*(.*?)\s*</span>")
OPTION_RE = re.compile(r'(?s)<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>')
SELECT_RE = re.compile(r'(?s)<select[^>]*name="([a-z_]+)"[^>]*>(.*?)</select>')
GUID_RE = re.compile(r"<guid>(\d+)</guid>")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[gech] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# The host declares no `Crawl-delay` (verdict read 2026-09-11); 2 s is ours, a
# default and not a margin under a measured ceiling.
_PACE = Pace("www.ge.ch", own=2.0)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "fr-CH,fr;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    # U+200B opens `experienceRequirements` and `jobBenefits` on the page
    # measured — a zero-width space glued to «Prérequis», invisible and kept
    # by `strip()`.
    # Twice: the JSON-LD strings are escaped once inside the JSON (`&#039;`)
    # and some a second time (`&amp;#58;` → `&#58;` → `:`), measured on id
    # 2067's `experienceRequirements`. A literal `&amp;` in prose would lose a
    # level too, and that is the cheaper error.
    markup = htmlmod.unescape(htmlmod.unescape(markup)).replace("\u200b", "")
    return re.sub(r"\s+", " ", markup).strip()


# ------------------------------------------------------------------ list --

def options(body):
    """`{select name: {label: value}}` — the form's own choices, read at run
    time so a department renamed or added never has to be edited here."""
    out = {}
    for name, inner in SELECT_RE.findall(body):
        out[name] = {text(label): value for value, label in OPTION_RE.findall(inner)}
    return out


def cards(body):
    """`[dict]` — one per `<article>` that links an advertisement.
    **Counted where they are decided**: `unlinked` grows in the branch where
    an `<article>` carries no advertisement link, so `linked + unlinked` is
    a check on the pattern and not an identity."""
    rows, unlinked, seen = [], 0, set()
    for inner in ARTICLE_RE.findall(body):
        m = ID_TITLE_RE.search(inner)
        if not m:
            unlinked += 1
            continue
        ident = m.group(1)
        if ident in seen:
            continue
        seen.add(ident)
        ent = ENTITY_RE.search(inner)
        href = ent.group(1) if ent else None
        rate = RATE_RE.search(inner)
        cls = CLASS_RE.search(inner)
        rows.append({
            "source": "gech", "country": "CH",
            "ledger_id": f"gech:{ident}", "id": ident,
            "url": f"{LIST}/{ident}",
            "title": text(m.group(2)),
            "employer": "Etat de Genève",
            "entity": text(ent.group(2) or ent.group(3)) if ent else None,
            "entity_url": href,
            "office": (text(ent.group(4)) or None) if ent else None,
            "rate": text(rate.group(1)) if rate else None,
            "salary_class": text(cls.group(1)) if cls else None,
        })
    return rows, unlinked


def resolve(label, choices, what):
    """The option whose label contains `label`, case-insensitively — exactly
    one, or the run stops and lists them. **Never a guess**: two departments
    share most of their words."""
    hits = {k: v for k, v in choices.items()
            if label.lower() in k.lower() and v != "0"}
    if len(hits) == 1:
        return next(iter(hits.items()))
    if not hits:
        die(f"no {what} matches {label!r}. The site offers: "
            + " · ".join(k for k, v in choices.items() if v != "0"))
    die(f"{len(hits)} {what}s match {label!r}: " + " · ".join(hits)
        + ". Say which.")


def cmd_list(a):
    params = {}
    if a.type:
        params["type_contrat"] = CONTRACT[a.type.lower()]
    if a.taux_max:
        params["taux_activite_max"] = str(a.taux_max)
    if a.classe_min:
        if not 4 <= a.classe_min <= 33:
            die("--classe-min takes a salary class from 4 to 33 (the site's range)")
        params["classe_fonction_min"] = str(a.classe_min - 3)
    filtered = bool(params) or bool(a.departement)
    # The department is a UUID the page itself lists; it costs the unfiltered
    # page once to read it, then the filtered page.
    url = LIST
    if a.departement:
        code, body = get(LIST)
        if code != 200:
            die(f"{LIST}: HTTP {code}. **A readable body is not an answer — the code decides.**")
        label, value = resolve(a.departement, options(body).get("departement", {}),
                               "department")
        params["departement"] = value
        note(f"--departement {a.departement!r} → {label!r}")
    if params:
        full = {k: params.get(k, "0") for k in FILTER_KEYS}
        url = LIST + "?" + urllib.parse.urlencode(full)
    code, body = get(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the list is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    rows, unlinked = cards(body)
    articles = len(rows) + unlinked
    if not rows:
        if "gech-offres-emploi-filters" not in body:
            die(f"{url}: {len(body)} characters, no `<article>` and not even "
                f"the filter form. **This is a page that changed shape, not "
                f"an empty list.**", EXIT_PARTIAL)
        note(f"0 advertisements on {url}: the filter form is there and no "
             f"`<article>` links one. "
             + ("With filters on, this is a real zero for THIS selection."
                if filtered else
                "**Unfiltered, that is the whole canton hiring nobody — read "
                "the page before believing it.**"))
    for i, r in enumerate(rows):
        if a.limit and i >= a.limit:
            break
        print(json.dumps(r, ensure_ascii=False))
    emitted = min(len(rows), a.limit) if a.limit else len(rows)
    line = (f"{emitted} emitted of {len(rows)} advertisement(s); {articles} "
            f"`<article>` on the page, {unlinked} without an advertisement "
            f"link; page states no total")
    if a.limit and emitted < len(rows):
        line += f" — --limit {a.limit} cut it, the board has {len(rows)}"
    note(line)
    if a.no_rss_check or filtered:
        note("RSS not compared" + (" — a filter is on, and the feed would answer "
                                   "another question." if filtered else "."))
        return
    # **The anchor, from the only route that does not share the pattern.**
    code, feed = get(RSS + "?" + urllib.parse.urlencode({k: "0" for k in FILTER_KEYS}))
    if code != 200:
        note(f"RSS answered HTTP {code} — no anchor this run.")
        return
    guids = set(GUID_RE.findall(feed))
    ours = {r["id"] for r in rows}
    if guids == ours:
        note(f"RSS lists {len(guids)}, the same {len(ours)} ids — "
             f"second route of the same operator, same day.")
    else:
        note(f"**RSS lists {len(guids)}, the page {len(ours)}: "
             f"{len(guids - ours)} only in the feed, {len(ours - guids)} only "
             f"on the page.** One of the two readings is short — the page's "
             f"`<article>` pattern is the first suspect.")


# -------------------------------------------------------------------- ad --

def ad_id(url):
    m = AD_RE.match(urllib.parse.urlsplit(url).path)
    return m.group(1) if m else None


LABEL_RE = {
    # «classe 25» inside a link to the salary scale, or «À définir» bare
    "salary_class": r"Rémunération\s*:</span>\s*(?:<a[^>]*>)?\s*([^<]+?)\s*<",
    "rate": r"Taux d'activité\s*:</span>\s*(?:<span>)?\s*([^<]+?)\s*<",
    "closes": r"Délai d'inscription\s*:</span>\s*([0-9.]+)",
    "starts_text": r"Entrée en fonction\s*:</span>\s*(?:<span>)?\s*([^<]+?)\s*<",
    "published_text": r"Date de publication\s*:\s*([^<]+?)\s*<",
}
APPLY_RE = re.compile(r'href="(https://ge\.ch/sirhrecrutement/[^"]*NOREFPOSTE=(\d+)[^"]*)"')


def cmd_ad(a):
    url = a.url or f"{LIST}/{a.id}"
    ident = ad_id(url)
    if ident is None:
        die(f"{url}: not an advertisement address — expected {LIST}/<integer>")
    code, body = get(url)
    if code == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}. **A readable body is not an answer.**")
    found = postings(body)
    if not found:
        why = absent_reason(body)
        if getattr(why, "our_fault", False):
            die(f"{url}: {why} **The page announces a JobPosting and this read "
                f"none — a misreading here, not a board that publishes nothing.**")
        die(f"{url}: {why}", EXIT_PARTIAL)
    if len(found) > 1:
        note(f"{len(found)} JobPosting blocks on one page — emitting the first.")
    d = found[0]
    org = d.get("hiringOrganization") or {}
    unit = d.get("employmentUnit") or {}
    loc = d.get("jobLocation") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = loc.get("address") if isinstance(loc, dict) else None
    page = {k: (lambda m: text(m.group(1)) if m else None)(re.search(p, body))
            for k, p in LABEL_RE.items()}
    apply_m = APPLY_RE.search(body)
    print(json.dumps({
        "source": "gech", "country": "CH",
        "ledger_id": f"gech:{ident}", "id": ident, "url": url,
        "title": text(d.get("title")),
        "employer": (org.get("name") if isinstance(org, dict) else None) or "Etat de Genève",
        "department_url": unit.get("url") if isinstance(unit, dict) else None,
        "address": text(addr) if isinstance(addr, str) else addr,
        "employment_type": d.get("employmentType"),
        "posted": d.get("datePosted"),
        "valid_through": d.get("validThrough"),
        "starts": d.get("jobStartDate"),
        "salary_class": page["salary_class"],
        "rate": page["rate"],
        "closes": page["closes"],
        "starts_text": page["starts_text"],
        "published_text": page["published_text"],
        "apply_url": apply_m.group(1) if apply_m else None,
        "reference": apply_m.group(2) if apply_m else None,
        # HTML-escaped inside the JSON: unescape, then strip the tags
        "experience_requirements": text(d.get("experienceRequirements")),
        "benefits": text(d.get("jobBenefits")),
        "description": text(d.get("description"))[:20000],
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description="Vacancies of the État de Genève, from its own list and "
                    "the JSON-LD every advertisement carries.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="the whole list, one request (two with the RSS anchor)")
    s.add_argument("--type", choices=sorted(CONTRACT), help="contract type")
    s.add_argument("--taux-max", type=int, choices=range(10, 101, 10),
                   metavar="N", help="maximum activity rate, 10..100 by tens")
    s.add_argument("--classe-min", type=int, metavar="N",
                   help="minimum salary class, 4..33")
    s.add_argument("--departement", help="part of a department's name, as the site spells it")
    s.add_argument("--no-rss-check", action="store_true",
                   help="skip the RSS anchor (one request)")
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one advertisement, JSON-LD plus the page's own fields")
    g = d.add_mutually_exclusive_group(required=True)
    g.add_argument("--url")
    g.add_argument("--id")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
