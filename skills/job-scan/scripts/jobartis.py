#!/usr/bin/env python3
"""Jobartis — ONE codebase, two national instances: Angola (`.com`) and Gabon (`.ga`).

  jobartis.py list [--country GA] [--since 2026-08-01] [--form bare] [--limit 20]
  jobartis.py ad --slug emprego-abreu-cabondela-lameira-adao-agricultura
  jobartis.py ad --country GA --slug emploi-eramet-correspondant-energie-climat-site-f-h

**40 882 advertisements in one gzipped sitemap** on the Angolan instance, and 216
of them published since 1 August 2026. `angoemprego` holds 1 434 and published
924 in the same window: *that board is an archive, and the two other Angolan
cards already say so.* What this adapter adds is that the archive is bigger
than the repository recorded, and why.

TWO URL FORMS ON `.com`, AND ONLY ONE OF THEM HAD EVER BEEN COUNTED

    /emprego-<slug>    38 588   2 528 distinct dates   2018-01-15 .. 2026-09-06
    /<slug>             2 294      60 distinct dates   2018-01-17 .. 2026-07-30
    neither               212   the home page, sign-up, help, search
                       ------
                       41 094   = every <loc> in the file

**`angoemprego.md` and `angolaemprego.md` both record 38 547 for this board.**
That is the `/emprego-` form alone — my count of the same form today is 38 588,
which is 41 more after two days. **The 2 294 bare-slug advertisements are in
neither figure**, and they are advertisements: `/anonimo-caixeiro-de-pecas`
serves a vacancy, closed, *«&nbsp;Oferta aberta até 30/09/2014&nbsp;»*.

**They are not the same advertisements under a second URL.** 113 slugs appear
in both forms, and the pair that was fetched — `adding-talent-contabilista`
under each — is **two different vacancies from the same employer**: reference
`Con_2015` closing 22/01/2015 against one closing 04/09/2014. *Same employer,
same job title, different years.* So the two forms are distinct URL spaces and
the counts add.

*A pattern that matched one form returned 94 % of the board and looked
complete — a narrow extractor does not return less, it returns false.*

THE ARCHIVE IS ONE IMPORT AND A TRICKLE

    /emprego-  busiest day  2018-01-26   7 138   18.5 %
    /<slug>    busiest day  2018-01-24     956   41.7 %

**A high count of distinct dates does not protect against a single import**:
2 528 distinct dates, and one January day carries a fifth of the file. The
bare-slug corpus is worse and also frozen — its most recent entry is
2026-07-30, so it takes no new advertisements at all.

**`--since` is therefore the flag that makes this board usable**, and it costs
one request: `lastmod` is present on 40 882 of 40 882.

ONE SECOND BETWEEN REQUESTS IS TOO FAST FOR THIS HOST

Seven requests at roughly one second apart drew **alternating 503s** — the
same URL that failed succeeded twenty seconds later, and a different URL
failed in its place. *That is a rate, not a property of any URL.* This module
paces itself at five seconds and `list` needs exactly one request.

**A zero, or a refusal, produced by our own request rate is ours and not the
site's** — which is why the pace is here and not in a comment.

WHAT AN ADVERTISEMENT PAGE CARRIES

`data-job-id="59272"` is the board's own identifier, and it is the ledger key.
There is no `ld+json` and no `JobPosting` anywhere: the fields are `data-label`
pairs, in Portuguese — contract type, closing date, role, industry, number of
posts, minimum education, years of experience, nationality, languages,
functional area.

**The state is read from two markers and never inferred from one.** An open
advertisement carries *«&nbsp;Enviar candidatura&nbsp;»*; a closed one carries
*«&nbsp;Vaga fechada&nbsp;»*. A page with neither reports `None` rather than
being called open by default.

Verified against the live site on 2026-09-07.

================================ GABON, #1172 ================================

**The route transposes and the VOCABULARY does not — measured 2026-10-21, four
advertisement pages fetched under the declared identity at the five-second
pace, guard taken on each exact URL in a turn distinct from the retrieval.**

    .com (Angola, pt)   sitemap.xml.gz   flat urlset   /emprego-<slug>
    .ga  (Gabon,  fr)   sitemap.xml.gz   flat urlset   /emploi-<slug>

`shared/boards/jobartis-ga.md` established the SHAPE: 339 `<loc>`, all 339
distinct, no child sitemap, no `<![CDATA[`, **228 advertisements**. *That is
the `hays-fr` case and not the `randstad` case: the discriminant is whether the
URL SHAPE is shared, never whether the brand is.* **What that card could not
say — and says so — is what an advertisement page CARRIES, because none had
been opened.** This is that measurement:

    STRUCTURE TRANSPOSES          data-job-id 4/4 · <h1> 4/4 · the `data-label`
                                  pair motif finds 13 fields on 4/4 · no ld+json
    VOCABULARY DOES NOT           all ten field labels are FRENCH, and both
                                  Portuguese state markers are ABSENT on 4/4

**So the Angolan parser run unchanged against `.ga` would have emitted a
well-formed record with every one of its ten fields `null` and `state: null`** —
the shape of a silent falsehood, and the reason the field labels live in a
per-instance table instead of in the code that reads them.

THE GABONESE CORPUS IS FROZEN, AND THE FIGURE IS DERIVED AND NOT WRITTEN DOWN

    228 advertisements, lastmod 2019-02-20 .. 2021-03-26, 16 distinct dates
    227 of the 228 are dated 2019; ONE is dated 2021

**Four pages were sampled — the first, the median and the last of the sitemap
order, plus the single most recent advertisement in the corpus — and all four
carry «&nbsp;Offre d'emploi fermée&nbsp;».** *Including the newest one.* That is
not a reason to drop the board — *«à priori, il n'y a jamais aucune raison pour
que nous n'utilisions pas un board»*, and only the owner declares a host shut —
but it IS a reason for `list` to say the age of what it returns, which it now
computes from the file rather than carrying a literal that goes stale.

**THE OPEN MARKER IS UNMEASURED ON `.ga` AND IT IS DECLARED, NOT GUESSED.** No
sampled page carries one, so `OPEN` is `None` for this instance and a page
without the closed marker reports `state: None` — never «open» by default. *The
asymmetry is the one `shared/boards/` keeps paying for: reading one host's rule
onto another declares every closed post OPEN, and the plugin drafts for a
vacancy that is gone.*

TWO THINGS THE GABONESE INSTANCE DOES NOT SHARE

**1. It has no bare-slug advertisement form.** The `.com` carries 2 294 of them
beside its 38 588 prefixed; on `.ga` the non-`/emploi-`, non-`/emplois`
remainder is **three single-segment paths and they are chrome** — `/ajuda`,
`/search-job-offers`, `/emplois`. *Note `/ajuda`: three of the five chrome
pages are still in PORTUGUESE on the French host, which is the measured version
of «one codebase» rather than an inference from the brand.* **And `/emplois` is
exactly why this is a per-instance table**: the Angolan deny-list knows
`vagas-emprego` and not `emplois`, so the Angolan rules applied here would have
promoted the French listing index to an advertisement.

*Anything single-segment that is neither the prefix nor a known chrome page is
counted and NAMED rather than silently dropped or silently promoted — a list of
refusals bets that the problem was enumerated, so the unknown has to be loud.*

**2. The two instances must not share a ledger namespace.** Both number their
advertisements with a bare `data-job-id` — 59272 on `.com`, 37514 on `.ga` —
and nothing says the two sequences are disjoint. *A collision would file a
Gabonese vacancy over an Angolan one, and the ledger would look consistent.* So
`ledger_id` is prefixed with the instance key and `source` names the instance.

**THE CADENCE IS THE NETWORK'S AND IS NOT RE-DERIVED HERE.** `.ga` writes no
`Crawl-delay` — and a silent file does not say there is no limit — so the five
seconds measured on `.com` are honoured, same operator, same stack (`server:
cloudflare`, `via: 2.0 heroku-router` on both). *RESIDUE, DECLARED: the pacer is
keyed per HOST, so if the limit is per OPERATOR rather than per host, running
both instances at once doubles the rate against it. That has not been measured
and is not claimed either way.*

**AND `/curriculum-vitae/*` IS REFUSED IN WRITING** by the `.ga` rules file.
Nothing this adapter fetches goes near it — the sitemap carries no such path —
and it is recorded because the opposite case cost a measurement elsewhere: a
Tadjik board whose rules refused NOTHING exposed 34 894 candidate CVs, and
there the path filter was a safety condition rather than an optimisation.
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import collections
import gzip
import html as html_mod
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

ENTRY = re.compile(r"<url>(.*?)</url>", re.S)
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
LASTMOD = re.compile(r"<lastmod>\s*(?:<!\[CDATA\[)?(\d{4}-\d{2}-\d{2})", re.S)
JOBID = re.compile(r'data-job-id="(\d+)"')
FIELD = re.compile(r'<div class="data-label[^"]*">\s*([^<]{2,40}?)\s*</div>\s*'
                   r'<div class="[^"]*">\s*(.*?)\s*</div>', re.S)

# **One table per national instance, and every value in it was MEASURED on that
# instance.** The structure is shared — same sitemap shape, same `data-label`
# markup, same `data-job-id` — so what varies is a vocabulary, and a vocabulary
# read from the wrong country returns `null` for every field while still
# emitting a well-formed record.
#
# `labels` maps an OUTPUT key to the folded `data-label` text. **The folded
# keys were EXTRACTED from the fetched pages, never retyped**: `secteur
# d'activité` folds to `secteur_d'activite` carrying a U+0027 apostrophe, and a
# retyped U+2019 would have matched nothing while looking right.
INSTANCES = {
    "AO": {
        "country": "AO",
        "source": "jobartis",
        "base": "https://www.jobartis.com",
        "prefix": "emprego-",
        # **The bare single-segment form IS an advertisement here** — 2 294 of
        # them, checked by fetching two rather than assumed from the shape.
        "bare_is_ad": True,
        "chrome": {"", "ajuda", "search-job-offers", "vagas-emprego", "sitemap",
                   "aviso-legal", "politica-de-privacidade", "contacto"},
        "accept_language": "pt-AO,pt;q=0.9,en;q=0.8",
        "closed": "Vaga fechada",
        "open": "Enviar candidatura",
        "labels": {
            "open_until": "oferta_aberta_ate",
            "contract_type": "tipo_contrato",
            "role": "cargo",
            "industry": "industria",
            "posts": "numero_de_vagas",
            "education": "titulacao_minima",
            "experience": "experiencia_exigida",
            "nationality": "nacionalidade",
            "languages": "linguas",
            "functional_area": "area_funcional",
        },
    },
    "GA": {
        "country": "GA",
        "source": "jobartis-ga",
        "base": "https://www.jobartis.ga",
        "prefix": "emploi-",
        # **Measured 2026-10-21 and the opposite of `.com`**: the whole
        # non-prefixed remainder is three chrome paths, enumerated below.
        "bare_is_ad": False,
        "chrome": {"", "ajuda", "search-job-offers", "emplois"},
        "accept_language": "fr-GA,fr;q=0.9,en;q=0.8",
        "closed": "Offre d'emploi fermée",
        # **UNMEASURED, and that is why it is `None` and not a guess.** 4 of 4
        # sampled pages are closed, the newest advertisement in the corpus
        # included, so no page carrying an open marker was ever seen.
        "open": None,
        "labels": {
            "open_until": "delai_de_candidature",
            "contract_type": "type_de_contrat",
            "role": "bureau",
            "industry": "secteur_d'activite",
            "posts": "postes_a_pourvoir",
            "education": "education_minimum",
            "experience": "experience_requise",
            "nationality": "nationalite",
            "languages": "les_langues",
            "functional_area": "specialisations",
            "description": "la_description",
        },
    },
}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(inst, msg):
    print(f"[jobartis:{inst['country'].lower()}] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    # An unknown is not a refusal: `not None` is `True` for both.
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


# **Five seconds, measured rather than chosen.** At one second the `.com` host
# returned alternating 503s from the seventh request on; the URL that failed
# succeeded twenty seconds later. Neither host declares a `Crawl-delay`, so
# this figure is ours and is declared as ours — and it is honoured on `.ga`
# because the operator and the stack are the same, not because it was re-derived
# there. One pacer PER HOST; see the residue in the module docstring.
_PACERS = {}


def pacer(inst):
    host = urllib.parse.urlsplit(inst["base"]).netloc
    if host not in _PACERS:
        _PACERS[host] = Pace(host, own=5.0)
    return _PACERS[host]


def get(inst, url, binary=False):
    gate(url)
    pacer(inst).wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": inst["accept_language"],
    })
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = r.read()
            if binary:
                return r.getcode(), raw, r.headers
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return (e.code, b"", e.headers) if binary else (e.code, "")
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def ungzip(raw, headers):
    """**The magic bytes decide, not the file extension.**

    `.gz` in a URL is a name; a host that stops compressing keeps the name and
    starts serving XML. Decompressing on the extension would raise, and
    trusting the extension the other way would hand XML to gzip.

    **The decompressed bytes go through `decode_body`, not through
    `.decode("utf-8")`.** Decompressing recovers bytes, not text, and the
    declaration that says which encoding they are is inside them — a hand-rolled
    UTF-8 decode with `errors="replace"` would turn a Portuguese `ç` into a
    replacement character and report success. The repository's guard caught
    exactly that here.
    """
    was_gz = raw[:2] == b"\x1f\x8b"
    return decode_body(gzip.decompress(raw) if was_gz else raw, headers)[0], was_gz


def clean(s):
    return " ".join(html_mod.unescape(re.sub(r"<[^>]+>", " ", s or "")).split())


def fold(s):
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def iso(d):
    """`22/01/2015` -> `2015-01-22`, or `None` — never a guess."""
    m = re.search(r"\b(\d{2})/(\d{2})/(\d{4})\b", d or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def classify(url, inst):
    """The form of this URL on THIS instance, or `None`.

    Three answers and not two: the prefixed form, the bare form where the
    instance HAS one, and `"unknown"` for a single-segment path that is neither
    the prefix nor a chrome page on an instance with no bare form. **The third
    exists so that a second advertisement form appearing on `.ga` is LOUD
    instead of being dropped as chrome or promoted to an advertisement** — a
    deny-list bets that the problem was enumerated, and this one was enumerated
    on 2026-10-21 and will not stay enumerated by itself.
    """
    base = inst["base"]
    if not url.startswith(base + "/"):
        return None
    tail = url[len(base) + 1:]
    if "/" in tail or tail in inst["chrome"]:
        return None
    if tail.startswith(inst["prefix"]):
        return inst["prefix"].rstrip("-")
    return "bare" if inst["bare_is_ad"] else "unknown"


def entries(inst):
    sitemap = inst["base"] + "/sitemap.xml.gz"
    code, raw, headers = get(inst, sitemap, binary=True)
    if code != 200:
        die(f"{sitemap}: HTTP {code}")
    body, was_gz = ungzip(raw, headers)
    forms = (inst["prefix"].rstrip("-"),) + (("bare",) if inst["bare_is_ad"] else ())
    counts = {f: 0 for f in forms}
    counts.update({"not-an-ad": 0, "no-date": 0, "unknown": 0})
    rows, unknown = [], []
    for block in ENTRY.findall(body):
        loc = LOC.search(block)
        if not loc:
            continue
        url = html_mod.unescape(loc.group(1).strip())
        form = classify(url, inst)
        if form is None:
            counts["not-an-ad"] += 1
            continue
        if form == "unknown":
            counts["unknown"] += 1
            unknown.append(url)
            continue
        d = LASTMOD.search(block)
        if not d:
            counts["no-date"] += 1
        counts[form] += 1
        rows.append({
            "source": inst["source"],
            "url": url,
            "slug": url[len(inst["base"]) + 1:],
            "form": form,
            "lastmod": d.group(1) if d else None,
            "countries": [inst["country"]],
        })
    if not rows:
        die(f"{sitemap} parsed to zero advertisements from {len(body)} "
            f"characters (gzip={was_gz}) — read the bytes before believing "
            f"the zero.")
    rows.sort(key=lambda r: (r["lastmod"] or ""), reverse=True)
    return rows, counts, was_gz, unknown


def age_note(rows):
    """**Derived from the file in hand, never written down.**

    *A figure that PRESCRIBES — «this board is an archive, use `--since`» —
    goes stale with its input, so the `.com` docstring's 18.5 % is history and
    this is the measurement.* Returns `None` when no row carries a date, which
    is a fact about the file and not a count of zero.
    """
    dates = [r["lastmod"] for r in rows if r["lastmod"]]
    if not dates:
        return None
    jour, n = collections.Counter(dates).most_common(1)[0]
    return ("dated %s .. %s, %d distinct date(s); the busiest single day is %s "
            "with %d of %d (%.1f %%)"
            % (min(dates), max(dates), len(set(dates)), jour, n, len(dates),
               100.0 * n / len(dates)))


def state_of(page, inst):
    """`(state, basis)` — and the two markers are read, never inferred one from
    the other's absence.

    **An instance whose OPEN marker has never been MEASURED carries `None`, and
    then a page without the closed marker reports `state: None` and says why.**
    *It is never called open by default: reading one host's rule onto another
    declares every closed post open, and the plugin then drafts for a vacancy
    that is gone.* It lives in its own function so that a guard can exercise it
    without a request — the vocabulary it uses is in `INSTANCES` and the
    corpus that measured that vocabulary is named in the cards.
    """
    closed = inst["closed"] is not None and inst["closed"] in page
    open_ = inst["open"] is not None and inst["open"] in page
    if closed:
        return "closed", f"«{inst['closed']}»"
    if open_:
        return "open", f"«{inst['open']}»"
    if inst["open"] is None:
        return None, (f"no «{inst['closed']}» on the page, and this instance "
                      f"has NO measured open marker — not called open")
    return None, "neither marker on the page — not called open"


def cmd_list(a):
    inst = INSTANCES[a.country]
    rows, counts, was_gz, unknown = entries(inst)
    forme = inst["prefix"].rstrip("-")
    part = f"{counts[forme]} under `/{inst['prefix']}`"
    if inst["bare_is_ad"]:
        part += (f" and {counts['bare']} under a bare slug. **Both forms are "
                 f"advertisements and they are not each other** — 113 slugs "
                 f"appear in both, and the pair that was checked is two "
                 f"different vacancies")
    note(inst, f"{len(rows)} advertisement(s) in one request "
               f"(gzip={was_gz}): {part}.")
    note(inst, f"{counts['not-an-ad']} entr(y|ies) are not advertisements; "
               f"{counts['no-date']} advertisement(s) carry no `lastmod`.")
    if counts["unknown"]:
        # **NAMED, never counted alone.** A second advertisement form arriving
        # on an instance declared not to have one is exactly the thing a count
        # cannot tell from a new chrome page.
        note(inst, f"{counts['unknown']} single-segment path(s) are NEITHER the "
                   f"`{inst['prefix']}` form NOR a known chrome page, and they "
                   f"are NOT counted as advertisements: "
                   f"{', '.join(unknown[:10])}"
                   f"{' …' if len(unknown) > 10 else ''}. **Read them before "
                   f"believing either answer** — this instance is declared to "
                   f"have no bare advertisement form.")
    age = age_note(rows)
    if age:
        note(inst, f"The returned corpus is {age}. **A high count of distinct "
                   f"dates does not protect against a single import**, and a "
                   f"count without a date says almost nothing about the "
                   f"market: use `--since`.")
    if a.form:
        if a.form not in counts:
            die(f"`--form {a.form}` does not exist on {a.country}: this "
                f"instance serves {', '.join(repr(f) for f in counts if f in (forme, 'bare'))}")
        rows = [r for r in rows if r["form"] == a.form]
        note(inst, f"{len(rows)} in the `{a.form}` form")
    if a.since:
        rows = [r for r in rows if r["lastmod"] and r["lastmod"] >= a.since]
        note(inst, f"{len(rows)} dated {a.since} or later.")
    if a.search:
        needle = fold(a.search)
        rows = [r for r in rows if needle in fold(r["slug"])]
    if a.limit:
        rows = rows[: a.limit]
    out = {"source": inst["source"], "country": inst["country"],
           "sitemap_entries": sum(counts.values()) - counts["no-date"],
           "advertisements": sum(counts[f] for f in counts
                                 if f in (forme, "bare")),
           "by_form": {f: counts[f] for f in counts if f in (forme, "bare")},
           "not_advertisements": counts["not-an-ad"],
           "unclassified": unknown,
           "returned": len(rows),
           "ads": rows}
    print(json.dumps(out, ensure_ascii=False, indent=1))


def cmd_ad(a):
    inst = INSTANCES[a.country]
    slug = a.slug.strip("/")
    url = f"{inst['base']}/{slug}"
    code, page = get(inst, url)
    if code in (404, 410):
        die(f"{slug} is gone (HTTP {code}). Record it as discarded.",
            EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}")
    ident = JOBID.search(page)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    fields = {}
    for m in FIELD.finditer(page):
        key = fold(clean(m.group(1))).replace(" ", "_")
        fields[key] = clean(m.group(2)) or None
    state, basis = state_of(page, inst)
    lab = inst["labels"]
    rec = {
        "source": inst["source"], "url": url, "slug": slug,
        "form": classify(url, inst),
        "id": ident.group(1) if ident else None,
        # **Namespaced by instance**: both sites number their advertisements
        # with a bare integer and nothing says the sequences are disjoint, so
        # an un-namespaced key could file a Gabonese vacancy over an Angolan one.
        "ledger_id": f"{inst['source']}:{ident.group(1) if ident else slug}",
        "id_source": "data-job-id" if ident else "slug — the page carried no id",
        "title": clean(h1.group(1)) if h1 else None,
        "state": state,
        "state_basis": basis,
    }
    for out_key, label in lab.items():
        rec[out_key] = fields.get(label)
    rec["open_until"] = iso(fields.get(lab["open_until"]))
    # **Whatever this instance's table does not name, rather than dropping it.**
    # A vocabulary that drifts is then visible in the output instead of
    # becoming ten nulls that look like an empty page.
    rec["extra"] = {k: v for k, v in fields.items() if k not in set(lab.values())}
    rec["countries"] = [inst["country"]]
    rec["structured_data"] = "none — no ld+json and no JobPosting on this site"
    print(json.dumps(rec, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    li = sub.add_parser("list", help="every advertisement, from one request")
    # **`%` in an argparse help string is a format specifier.** A bare `18.5 %`
    # raises `badly formed help string` at `add_argument`, so the module dies
    # before it parses anything — a percentage written for a reader takes the
    # whole adapter down. It is doubled here and nowhere else in this file.
    li.add_argument("--since", metavar="YYYY-MM-DD",
                    help="`lastmod`, present on every advertisement. **Use "
                         "it**: on `.com` one 2018 day carries 18.5 %% of the "
                         "file, and `list` prints the age of what it returns")
    li.add_argument("--form", choices=("emprego", "emploi", "bare"),
                    help="the URL form; `bare` exists on AO only, where both "
                         "forms are advertisements and only the first had ever "
                         "been counted")
    li.add_argument("--search", help="match the slug; folds accents")
    li.add_argument("--limit", type=int)
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="one advertisement by its path tail")
    ad.add_argument("--slug", required=True,
                    help="the whole tail, the locale prefix included")
    ad.set_defaults(func=cmd_ad)

    for c in (li, ad):
        c.add_argument("--country", choices=sorted(INSTANCES), default="AO",
                       help="the national instance: AO is `www.jobartis.com` "
                            "and GA is `www.jobartis.ga`. They share a sitemap "
                            "shape and NOT a vocabulary")

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
