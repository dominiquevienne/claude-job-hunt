#!/usr/bin/env python3
"""EURES (`europa.eu`, the EU's own job mobility portal) — a PUBLIC REST API that answers the declared client, three of the host's own totals that DISAGREE, and a ceiling the host PUBLISHES rather than one we infer.

  eures.py totals
  eures.py list [--page-size N] [--max N] [--no-notes]

THE FIRST USER-VOTED ADAPTER OF THIS REPOSITORY (#1014, one 👍).

THE ROUTE IS THE PORTAL'S OWN PUBLIC API, AND IT NEEDS NO KEY, NO ACCOUNT AND NO
FORM. Seventeen `/eures/api/` calls were observed from the portal, every one under
`/public/` and every one 200:

    POST  …/jv-searchengine/public/jv-search/search   {resultsPerPage, page} ALONE -> 200
    GET   …/jv-searchengine/public/properties         the ceiling, DECLARED
    GET   …/jv-searchengine/public/statistics/getNumberOfJobs

**THE CEILING IS A PUBLISHED PROPERTY, NOT AN INFERENCE FROM A PAGER.**
`jvse.max.faj.search.results` reads `'10000'`, and the pager shows 1 000 pages of
10 — the two agree, but it is the PROPERTY that is authoritative. *So this adapter
FETCHES the ceiling and refuses to walk when it cannot read one: a limit we
guessed and a limit the host declares are not the same object, and the second can
change without our noticing.*

TWO HOSTS, AND THEY DO NOT ASK FOR THE SAME RATE — reading the obvious one runs
FIVE TIMES too fast:

    europa.eu          4 930 B, `Crawl-delay: 10` under `*`   <- the offers live HERE
    eures.europa.eu    1 638 B, Drupal's stock file, NO delay

*Measured by passing the rules BODY to `delay_for`, because it takes a body and
not a host: handed a hostname it parses «europa.eu» as a rules file and returns
None — a zero fabricated by the argument.* **And a false cadence returns no error
at all: it returns an interstitial an hour later.**

**THREE OF THE HOST'S OWN TOTALS, AND THEY DISAGREE. This adapter publishes all
three under their own names and calls none of them the size of the board:**

    getNumberOfJobs            2 603 942     a separate endpoint
    numberRecords              1 940 004     an unfiltered search
    POSITION_LOCATION facet    1 940 303     EXCEEDS numberRecords by 299
    EURES_FLAG facet           1 940 004     partitions numberRecords EXACTLY

*So one facet partitions the total cleanly, another overshoots it, and a third
endpoint reports 663 938 more. **None of the three gaps is explained, and that
this adapter keeps saying so is the result** — a 299 discrepancy on 1 940 004 is
0,0154 %, so a 50-record sample expects 0,0077 of them and would need ~6 488 to
hope for one. A negative without power is indistinguishable from a true negative.*

**AN ADVERT IS NOT A POST.** `numberOfPosts` summed 156 over 50 records with a
maximum of 12, so the two counts differ by a factor of three on page one alone.
*The ledger counts ADVERTS — one record, one `ledger_id` — and `posts` traves
alongside as the host's own number. **The choice is declared here rather than
suffered downstream.***

**NO FIELD RATE IS TAKEN FROM PAGE ONE, AND THE HOST'S OWN FACET IS WHY.**
`euresFlag` is true on 42 of the 50 records of page one against 83 844 of
1 940 004 in the population — **a factor of about twenty.** *The default ordering
is not neutral and the facet proves it, which is the rare case where a board
hands over the population beside the sample.*

**`employer.website` EXISTS AND IS NEVER FILLED** — 0 of 50. *So a
`withheld_fields` written on «the key is present» would claim we withheld a site
nobody published, which lies about OUR discretion and not about the board.* The
floor is POSITIVE.

**AND `_provenance.third_party()` IS DELIBERATELY NOT CALLED, WHICH IS A DECISION
AND NOT AN OVERSIGHT.** *Exercised against both record shapes before being used: a
field it finds FILLED comes back as `third_party_withheld`, one the board never
filled as `third_party_absent`. The label is only true of fields an adapter
inspects and does NOT pass on — and this one passes both employer fields through,
so declaring them would print «withheld» over values that are in the record.*
**This board has no third-party contact field to withhold at all**, which is a
finding: no phone key, no e-mail key, and a `website` the board leaves empty. The
only real withholding is in the prose, and `scrub()` derives it.

THE RULES, EXERCISED IN BOTH DIRECTIONS: every API path is permitted on both
hosts; **`/search/` and `/search/node` are REFUSED on `eures.europa.eu` by the
rule `/search/` and PERMITTED on `europa.eu`** — so `refuse_drupal_search()` is a
refusal that can FIRE, and it fires on one host and not the other. Guard taken on
each exact path, host included, in a turn distinct from every retrieval.
Measured 2026-10-05 (card) and 2026-10-07 (this adapter).
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

HOST = "europa.eu"
BASE = "https://europa.eu/eures/api/jv-searchengine/public"
SEARCH = BASE + "/jv-search/search"
PROPS = BASE + "/properties"
NJOBS = BASE + "/statistics/getNumberOfJobs"

# The host WRITES 10 s under `*` on the offers host; `eures.europa.eu` writes none.
# Passed as the floor so a missing read can never make us faster than the written value.
WRITTEN_DELAY = 10.0

# The ceiling is the host's own property. We never invent a default for it.
CEILING_KEY = "jvse.max.faj.search.results"

# Refused IN WRITING on `eures.europa.eu`, permitted on `europa.eu` — the refusal
# must fire on the first and not on the second.
DRUPAL_SEARCH = "/search/"
REFUSING_HOST = "eures.europa.eu"

# Prose, and the only field that can carry what a poster typed.
SCRUBBED = ("description",)
MAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TEL_RE = re.compile(r"(?:\+\s?\d{1,3}[\s\-()]*)?(?<!\d)\d{9,13}(?!\d)")
MSG_RE = re.compile(r"(?i)\b(?:whats?app|telegram|viber|skype)\b[\s:：]*[+\d@][\w\d\s\-()@._]{3,}")

# **`_provenance.third_party()` IS DELIBERATELY NOT CALLED HERE, AND THE REASON IS
# ITS OWN VOCABULARY.** Exercised on 2026-10-07 against both record shapes: a field
# it finds FILLED comes back under `third_party_withheld`, and one the board never
# filled under `third_party_absent`. *So the label only tells the truth for fields
# an adapter inspects and does NOT pass on.* This adapter passes both employer
# fields through, so declaring them would print «withheld» over values that are in
# the record — the `withheld_fields` lie moved one notch, and it lies about OUR
# discretion rather than about the board.
#
# **AND THE BOARD HAS NO THIRD-PARTY CONTACT FIELD TO WITHHOLD, WHICH IS A FINDING
# AND NOT AN OMISSION**: the card's field-by-field reading names no phone and no
# e-mail key, and `employer.website` exists and was filled on 0 of 50 — *a present
# key is not a filled one, and that emptiness is the BOARD's and not ours.* The
# only real withholding here is in the prose, and `scrub()` derives it.
#
# *Called with my own flat record shape it returned everything `absent`, including a
# name that was filled — a plausible, well-formed answer produced by the argument.
# Measured before being used, not after.*

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[eures] {msg}", file=sys.stderr)


def refuse_drupal_search(url):
    """`/search/` is refused IN WRITING on `eures.europa.eu` and permitted on
    `europa.eu`. **A refusal that fires on one host and not the other is the
    only kind that proves `robots.txt` binds a HOST and not a brand** — and this
    one is reachable rather than decorative."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc == REFUSING_HOST and (parts.path or "/").startswith(DRUPAL_SEARCH):
        die(f"{url}: `Disallow: /search/` is written for `*` on {REFUSING_HOST}. "
            f"**A refusal in the rules is an intention and no route contours it.** "
            f"The same path is permitted on {HOST}, which is where the offers live — "
            f"`robots.txt` binds a host, not a brand.", EXIT_REFUSED)
    return None


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=WRITTEN_DELAY)


def call(url, body=None):
    """GET, or POST when `body` is given. **The body is a SCHEMA question and
    carries no personal value**: `{resultsPerPage, page}` and nothing else, which
    is exactly what the host answered 200 to."""
    refuse_drupal_search(url)
    gate(url)
    _PACE.wait()
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(wire_url(url), data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            if (r.headers.get("Content-Encoding") or "").lower() in ("gzip", "x-gzip") \
                    or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def as_json(url, body=None, what="response"):
    code, txt = call(url, body)
    if code != 200:
        die(f"{url}: HTTP {code}. **A readable body is not an answer — the code decides.**",
            EXIT_PARTIAL if code != 404 else EXIT_GONE)
    try:
        return json.loads(txt)
    except ValueError as e:
        die(f"{url}: the {what} is not JSON ({e}). "
            f"**A broken decode returns TEXT, not an error** — so this refuses rather "
            f"than reads an absence into it.", EXIT_PARTIAL)


def ceiling():
    """The host's DECLARED maximum, fetched. **Never a default**: a limit we
    invented and a limit the host publishes are different objects, and the second
    can change without our noticing. *An unreadable ceiling stops the walk —
    ignorance does not liberate.*"""
    props = as_json(PROPS, what="properties")
    raw = props.get(CEILING_KEY) if isinstance(props, dict) else None
    if raw is None:
        die(f"{PROPS}: `{CEILING_KEY}` is absent, so the ceiling this host declares "
            f"cannot be read. **The walk stops rather than substituting a number of "
            f"our own** — a guessed limit is indistinguishable from a published one "
            f"in the output, and only one of them is the host's.", EXIT_PARTIAL)
    try:
        return int(str(raw).strip())
    except ValueError:
        die(f"{PROPS}: `{CEILING_KEY}` reads {raw!r}, which is not a number.")


def epoch_ms(v):
    """Epoch MILLISECONDS to ISO-8601 UTC. **The magnitude is checked rather than
    assumed**: a value that is plainly seconds is not divided by a thousand a
    second time, and anything else is passed through untouched with its type."""
    if not isinstance(v, (int, float)) or v <= 0:
        return None
    import datetime
    secs = v / 1000.0 if v > 1e11 else float(v)
    if not (946684800 <= secs <= 4102444800):      # 2000-01-01 .. 2100-01-01
        return None
    return datetime.datetime.fromtimestamp(
        secs, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def text(s):
    if not isinstance(s, str):
        return None
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</p>|</li>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    out = "\n".join(" ".join(l.split()) for l in
                    htmlmod.unescape(s).splitlines() if l.strip()).strip()
    return out or None


def scrub(s):
    """The description with its contacts replaced, and the SET of what was found.
    *Prose cannot be dropped without dropping the advertisement, so it is
    scrubbed; a field whose meaning is known would be dropped instead.*"""
    if not isinstance(s, str) or not s.strip():
        return None, []
    found = []
    if MAIL_RE.search(s):
        found.append("description:e-mail")
    if MSG_RE.search(s):
        found.append("description:messaging")
    if TEL_RE.search(s):
        found.append("description:telephone")
    s = MAIL_RE.sub("[e-mail withheld]", s)
    s = MSG_RE.sub("[messaging contact withheld]", s)
    s = TEL_RE.sub("[telephone withheld]", s)
    return text(s), found


def held(v):
    """A POSITIVE floor: a value is a value only if it passes a test, never
    because it is missing from a list of refusals. *`"$undefined"` walks under a
    list that knows `undefined`, and the next sentinel will be encoded
    differently.*"""
    if v is None or isinstance(v, bool):
        return False
    if isinstance(v, str):
        t = v.strip()
        return bool(t) and not t.startswith("$") and t.lower() not in (
            "undefined", "null", "none", "n/a", "-")
    if isinstance(v, (int, float)):
        return True
    return bool(v)


def places(location_map):
    """`locationMap` is keyed by country and holds NUTS codes. **Country and NUTS
    region only — no street, no postcode**, by a positive floor that reads
    nothing else."""
    if not isinstance(location_map, dict):
        return []
    out = []
    for pays, regions in sorted(location_map.items()):
        if not held(pays):
            continue
        codes = [r for r in (regions or []) if isinstance(r, str) and held(r)] \
            if isinstance(regions, (list, tuple)) else []
        out.append({"country": pays.strip().upper(), "nuts": sorted(set(codes))})
    return out


def record(jv):
    desc, withheld = scrub(jv.get("description"))
    emp = jv.get("employer") if isinstance(jv.get("employer"), dict) else {}
    ident = jv.get("id")
    out = {
        "source": "eures", "ledger_id": f"eures:{ident}", "id": ident,
        "title": text(jv.get("title")),
        # `employer.website` EXISTS and was filled on 0 of 50 — a present key is
        # not a filled one, and the floor is what tells them apart.
        "employer": (emp.get("name") or "").strip() or None if held(emp.get("name")) else None,
        "employer_site": emp.get("website") if held(emp.get("website")) else None,
        "places": places(jv.get("locationMap")),
        "eures_flag": jv.get("euresFlag") if isinstance(jv.get("euresFlag"), bool) else None,
        # AN ADVERT IS NOT A POST: the ledger counts adverts, this travels beside
        # it as the host's own number.
        "posts": jv.get("numberOfPosts") if isinstance(jv.get("numberOfPosts"), int) else None,
        "offering_code": jv.get("positionOfferingCode") if held(jv.get("positionOfferingCode")) else None,
        "schedule_codes": [c for c in (jv.get("positionScheduleCodes") or []) if held(c)],
        "category_codes": [c for c in (jv.get("jobCategoriesCodes") or []) if held(c)],
        "created": epoch_ms(jv.get("creationDate")),
        "modified": epoch_ms(jv.get("lastModificationDate")),
        "languages": [l for l in (jv.get("availableLanguages") or []) if held(l)],
        "description": desc,
    }
    # DERIVED, and ABSENT when nothing was withheld — a poor advertisement must
    # never read as a censored one.
    if withheld:
        out["withheld_fields"] = sorted(set(withheld))
    return out


def th(n):
    return f"{n:,}".replace(",", " ")


def cmd_totals(a):
    nj = as_json(NJOBS, what="getNumberOfJobs")
    one = as_json(SEARCH, {"resultsPerPage": 1, "page": 1}, what="search")
    cap = ceiling()
    out = {
        "source": "eures",
        "getNumberOfJobs": nj.get("numberOfJobs") if isinstance(nj, dict) else None,
        "numberRecords": one.get("numberRecords") if isinstance(one, dict) else None,
        "declared_ceiling_per_query": cap,
        "ceiling_property": CEILING_KEY,
    }
    print(json.dumps(out, ensure_ascii=False))
    a_, b_ = out["getNumberOfJobs"], out["numberRecords"]
    note(f"THREE of this host's own totals disagree and NONE of them is published as the "
         f"size of this board: `getNumberOfJobs` {th(a_) if a_ else '?'}, an unfiltered "
         f"`numberRecords` {th(b_) if b_ else '?'}, and the POSITION_LOCATION facet which "
         f"EXCEEDED `numberRecords` by 299 when the card measured it while the EURES_FLAG "
         f"facet partitioned it EXACTLY. **None of the gaps is explained, and saying so is "
         f"the result.**")
    if a_ and b_:
        note(f"the two endpoints differ by {th(a_ - b_)} as read just now. **The 299 above is "
             f"the CARD's pair, measured 2026-10-05 against its own `numberRecords` of "
             f"1 940 004 — 0.0154 % — and it is NOT recomputed against today's total**: two "
             f"numbers from two moments do not make one quantity. *On that dated pair a "
             f"50-record sample expects 0.0077 discrepancies and would need ~6 488 to hope "
             f"for one, so a negative there is indistinguishable from a true negative.*")
    note(f"only {th(cap)} records are reachable per query, and that is the host's DECLARED "
         f"property `{CEILING_KEY}` — not a number inferred from a pager.")


def cmd_list(a):
    cap = ceiling()
    per = max(1, min(a.page_size, 50))
    limite = min(a.max, cap) if a.max else cap
    vus, page, total, gaps = 0, 1, None, 0
    while vus < limite:
        reste = limite - vus
        body = {"resultsPerPage": min(per, reste), "page": page}
        rep = as_json(SEARCH, body, what="search")
        if total is None:
            total = rep.get("numberRecords")
        lot = rep.get("jvs") or []
        if not isinstance(lot, list) or not lot:
            note(f"page {page}: no record in `jvs` — the walk ENDED HERE, which is not the "
                 f"same as the board being this size.")
            break
        for jv in lot:
            if not isinstance(jv, dict) or not held(jv.get("id")):
                gaps += 1
                continue
            print(json.dumps(record(jv), ensure_ascii=False))
            vus += 1
            if vus >= limite:
                break
        page += 1
    fin = ("capped by the host's DECLARED ceiling" if vus >= cap else
           "capped by --max" if a.max and vus >= a.max else
           "the walk ended on an empty page")
    note(f"{th(vus)} advertisement(s) emitted over {page - 1} page(s) of {per}; the host "
         f"states `numberRecords` {th(total) if total else '?'} and DECLARES a ceiling of "
         f"{th(cap)} per query — {fin}.")
    note("**the ledger counts ADVERTISEMENTS, not posts**: `numberOfPosts` summed 156 over "
         "the 50 records of page one with a maximum of 12, so the two counts differ by about "
         "a factor of three. The host's own number travels in `posts` beside each record.")
    if gaps:
        note(f"{gaps} record(s) carried no usable `id` and were counted as gaps, not as absent.")
    if not a.no_notes:
        note("**no field rate is derived from this walk**: on 2026-10-05 `euresFlag` was "
             "true on 42 of the 50 records of page one against 83 844 of 1 940 004 in the "
             "host's own facet — a factor of about twenty. **And on 2026-10-07 the first "
             "three records came back FALSE on all three**, which is a second reading in the "
             "opposite direction and makes the same point harder: the default ordering is not "
             "neutral, it is not even stable, and no page-one rate is a rate of this board.")
        note("two hosts, two cadences: `europa.eu` WRITES `Crawl-delay: 10` under `*` and the "
             f"offers live there, while `eures.europa.eu` writes none; this walk paced at "
             f"{WRITTEN_DELAY:.0f} s. **Reading the obvious host would have run five times too "
             "fast, and a false cadence returns no error — it returns an interstitial later.**")


def main():
    p = argparse.ArgumentParser(
        description="EURES — the EU portal's own public REST API: three of the host's "
                    "totals that disagree, and a ceiling the host declares.")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("totals", help="the host's own totals, each under its own name")
    t.set_defaults(fn=cmd_totals)
    l = sub.add_parser("list", help="walk the public search up to the DECLARED ceiling")
    l.add_argument("--page-size", type=int, default=50)
    l.add_argument("--max", type=int, help="stop after N advertisements")
    l.add_argument("--no-notes", action="store_true")
    l.set_defaults(fn=cmd_list)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
