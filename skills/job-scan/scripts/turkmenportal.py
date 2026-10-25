#!/usr/bin/env python3
"""TURKMENPORTAL (`turkmenportal.com`) — a Turkmen portal whose job board is one page of twelve notices, and where the LOCALE in the path does not multiply the board: it FILTERS it.

  turkmenportal.py list [--limit N] [--locale ru|en|tm|tr]

THE «VITRINE» AND THE «CATEGORY» ARE THE SAME PATH, AND THE VARIABLE IS THE LOCALE.

The path this board's card recorded — `/work/rabota-v-turkmenistate/vakansii-v-turkmenistane`
— **redirects**, and the redirect is the whole story (measured 2026-10-25 06:19 UTC):

    url        /work/rabota-v-turkmenistate/vakansii-v-turkmenistane
    final_url  /ru/advertisement/posts/category/117-rabota

*So the 2026-10-06 relocation — «the board is not a section of the news portal, it is a
category of its classifieds module, and the recorded page is a shop window leading to it»
— and the 2026-10-24 relocation BACK to the «shop window» as «the only enumerator» are
both wrong in the same way: there was never more than one path.* **The 12-against-2 those
two measurements read as a difference of PATH is a difference of LOCALE**, and this host's
own `robots.txt` says so in English: *every real URL carries a locale prefix*.

THE LOCALE FILTERS, AND THE ALIAS IS NECESSARY WITHOUT BEING THE WHOLE RULE. Each item
carries `alias_tm`, `alias_ru`, `alias_en`, `alias_tr`. Both columns below are MEASURED, the
first on the `/ru` payload with a positive floor, the second by one request per locale
(`check-locales`), 2026-10-25:

    locale   alias filled on the 12      the locale's listing returns
    ru              12                            12      <- the MAXIMAL view, and the one read
    en               2                             2
    tm               2                             1      <- they DISAGREE
    tr               0                             0

**`en` 2 = 2 and `tr` 0 = 0, and `tm` is 2 against 1.** *So carrying that locale's alias is
NECESSARY to be listed under it and is not SUFFICIENT: three locales of four agree and one
does not, which makes the alias a good predictor and not the mechanism.* **The first version
of this docstring wrote the rule as an equivalence — «a per-locale listing shows only the
items whose alias for that locale is filled» — on the three agreeing locales, before the
fourth was measured.** *Kept and corrected rather than rewritten: a list closed on the
members that agree reads as exhaustive without ever saying so.*

And `/en` returning 2 was measured a day earlier by a different route, so **that half rests
on two independent measurements** while the `tm` disagreement rests on this one.

> **AND THIS IS THE MIRROR OF `yora.md`, WHERE FOUR LOCALES CARRY THE SAME PATHS.** *There
> the locale MULTIPLIES and the remedy is to dedup on the id — 8 URLs for 2 objects,
> «removing the dedup publishes 400 for a board of 100». Here the locale SUBTRACTS and the
> remedy is to read the maximal locale — reading `/en` publishes 2 for a board of 12.*
> **Nothing shared — the country's neighbourhood, the four-alias shape, the classifieds
> form — predicted one from the other, and the two errors point in OPPOSITE directions.**

AND THE FIRST VERSION OF THIS ADAPTER TRIED TO DERIVE THAT FILTER FROM ONE REQUEST, WHICH
CANNOT WORK — kept here because a correction cites what it corrects. It computed the alias
fill on the items the listing returned and warned when another locale's alias was filled
more often. **Run against `/en`, it printed `ru 2/2, en 2/2` and said nothing**, on exactly
the case it existed for.

> **A filter's magnitude cannot be derived from the filter's own output.** *An item missing
> from `/en` is absent from the array altogether, so it contributes to NO locale's count:
> the sample is the set of SURVIVORS, and the fill measures them rather than the filter.*
> **This is «a rate taken on page 1 is not a board's rate» one floor down — there the sort
> puts the sample on page 1, here the filter IS the sample — and the warning was the first
> species of a failing guard: a green that says «I did not look there».** *Found by RUNNING
> the adapter and not by re-reading it.*

So `list` states plainly that its count is a PER-LOCALE count and that the fill it prints is
on the survivors; and **`check-locales` is the only thing that answers the question**, at the
price it costs: one request per locale, which it says before making them.

NO COUNT IS STATED, AND THE ONLY FIELD NAMED `total` IS A LABEL: `"total": "Итого"`.
*Third host of this cluster where the i18n dictionary holds a word of the domain — `isgar`
carried `"Umumy iş tejribesi: {duration}"` beside its real 406.* **On a fully localised
site a count is never read by the NAME of its key.** `pageCount` is `0` here, and the same
payload carries `436` and `375` on other blocks, **so the `0` is a MEASURED value and not
an instrument's silence.** The section is therefore walked in ONE request and has no pager.

THE ANCHOR IS STRUCTURAL, AND THE FIRST MATCH IS NOT OURS. The payload holds THREE
`"models":[…]` arrays — 12, 4 and 4 items, of categories `117`, `{283,353}` and
`{362,363,364}` — so the block is chosen by `cat_id` and never by position. The walk back
to the balanced array **skips strings**, escapes included, because a `[` inside a title
would close the array early.

AND THE TWELFTH ITEM IS NOT A PARSING PROBLEM. Item `17371` carries escaped quotes in its
title, and the 2026-10-24 measurement read **eleven** items before reading twelve. *The
object was never at fault: decoding each `self.__next_f.push` literal on its own and
parsing the inner JSON yields 12 directly, item `17371` included.* **The off-by-one lived
in that measurement's own de-escaping, and its only symptom was a difference of cardinal —
11 items for 12 distinct `/advertisement/posts/<id>` links — which was explained away by an
invented cause («a sidebar link»).**

WHAT THE NINETEEN FIELDS HOLD, present / non-empty with a POSITIVE floor, on the 12:
`id` `title` `date` `updated_date` `cat_id` `cat_name` `status` `view_count` `creator`
`editor` at 12/12; `alias_ru` 12/12, `alias_tm` and `alias_en` 2/12, `alias_tr` **0/12**;
`phone` 7/12; `thumb_url` and `image_url` 6/12; `address` 3/12; `web_site` 2/12.

  * **`phone` is DROPPED and named** — 7 of 7 filled values carry `993`, 11 to 22 digits.
  * **`address` is DROPPED and named, AND THAT LOSES A LOCALITY — declared, not silent.**
    *The three filled values are 38 to 60 characters with two or three digits, and TWO of
    the three carry a recognisable Turkmen place name: this host ships street and city in
    ONE free-form string, and no separate locality field exists among the nineteen.* The
    repository's settled convention withholds the street and the postcode and KEEPS the
    locality (`yora`, and the WebForms tenant's `ADDRESS_DROPPED`); that split needs a
    structured field, and here there is none. **So this adapter is stricter than the
    convention, which is the shape nobody audits** — and what would lift it is named: a
    structured locality field on this host, or a Turkmen gazetteer, neither of which is
    worth writing against three values.
  * **`web_site` is EMITTED** — both filled values are URLs, with no `@` and no digit. An
    employer's site is not a person's contact, and `isgar` emits `company.website`.
  * **`creator` and `editor` are NEVER emitted, and the CARDINALITY is what establishes
    it**: 12/12 filled but only **4** and **5** distinct values, equal on 9 of 12. *A dozen
    advertisements written by four accounts are the portal's newsroom, not twelve
    advertisers.* **Filled 12/12, they are exactly the shape of an employer field.**

NO DIGIT HEURISTIC RUNS ON FREE TEXT HERE, AND THAT IS MEASURED RATHER THAN ASSUMED. The
titles carry no telephone — **0 of 12 under TWO patterns of different shapes**, the
dialling code as it is SERVED and any run of grouped digits — while the same dialling-code
pattern fires on **7 of 7** filled `phone` values. *So the expurgation is purely per-field,
which is the opposite of the Burmese currency trap where an ordinary monthly wage has as
many digits as a telephone number, and of the Madrid rule that destroyed 314 of 314 advert
ids for want of an anchor.*

`status` IS CONSTANT. It is `1` on 12 of 12 and `cat_name` has one distinct value, so
neither discriminates anything today. They are carried as facts and **read for no
decision**: a constant marker has the exact shape of a measurement and tells nothing apart.

THE PAGE CARRIES NO STRUCTURED DATA. `application/ld+json` appears as a STRING twice and as
a real `<script>` block **zero** times — the RSC payload repeats the string. *Fourth and
fifth host-page of this cluster where counting the string over-declares the blocks.*

THE RULES: `/api/` is refused IN WRITING, so no client-side route is taken even if one
existed — and the vue that returns nothing carries no `/api/` reference at all, so the
server renders the list and the list is simply empty for that locale. Of the host's nine
`Disallow`, **eight cannot fire** on the form it serves and the author says so in English
in the file itself; the ninth, `/*/dealer`, is the one they doubled on purpose. **We honour
the intention and not the prefix match: none of those paths is fetched.** No `Crawl-delay`
is written, so our own 2 s floor applies, and this board costs ONE request.

THE DATE THAT DECIDES IS NOT THE DATE OF THE MEASUREMENT. The most recent of the twelve is
**2022-07-12**, then four of 2021-03-20, one 2021-02-10, one 2020-09-07 and six of 2019 —
the section has received nothing for over four years while the portal publishes (its other
blocks carry 2026 items). **This is a MEASURE and not a verdict.** *The host answers 200,
nothing is missing from it, and the decision of what we give up reaching belongs to the
owner (§2 sexies). The adapter emits what the object holds.*

AND THE BODY'S LENGTH IS STABLE WHILE ITS DIGEST IS NOT: 395 033 bytes on 2026-10-24 and
again on 2026-10-25, `md5 bc47517345df` then `bf76c3d16911`. *A fixed-width rendered element
moves, so two digests of this page never compare — which is why the item count, and not the
digest, is what this adapter reports.*

Guard taken on every exact path in a turn DISTINCT from the retrieval, with a SINGLE token
(`claude-user`) and never the set: three open with `rule=None`, `state=read`,
`certain=True`, `crawl_delay=None`; `/api/` and `/ru/dealer` refused with their narrow
rule, which is the instrument's positive control. Measured 2026-10-25 (#668).
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
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
from _zero import empty_first_page

HOST = "turkmenportal.com"
BASE = "https://turkmenportal.com"
# the category IS the board; the editorial path the card recorded redirects here
LIST = BASE + "/{locale}/advertisement/posts/category/117-rabota"
CAT = 117
LOCALES = ("tm", "ru", "en", "tr")
# **Established by the alias fill, not chosen**: `ru` is the only locale whose alias is
# filled on all twelve, and `/en` returns 2. `list` re-derives this every run and says so
# if the locale it read is not the maximal one.
READ_LOCALE = "ru"

# NAMED fields whose MEANING is known: dropped, never filtered. `address` is here although
# it is a location and not a contact — see the module docstring: street and locality travel
# in ONE string and this host offers no structured locality.
CONTACT_FIELDS = ("phone", "address")
# The portal's own newsroom accounts — 4 and 5 distinct values for 12 items. Not employers,
# and never emitted; they are not «withheld» either, because nobody deposited them as a
# contact.
NEWSROOM = ("creator", "editor")

MAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Turkmen numbers as this host SERVES them: `+(99312) 34-23-03`. The bare run is ANCHORED
# at eight digits so that a house number or a four-digit year cannot be mistaken for one.
TEL_RE = re.compile(r"\+?\s?\(?\s?993[\s\-()\d]{4,}|(?<!\d)\d{8}(?!\d)")
MSG_RE = re.compile(r"(?i)\b(?:whats?app|telegram|viber|imo)\b[\s:：]*[+\d][\d\s\-()]{5,}")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[turkmenportal] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=2.0)   # the host writes no Crawl-delay -- our own floor


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xml;q=0.9",
        "Accept-Language": "ru,tk;q=0.8,en;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


PUSH_RE = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', re.S)


def payload(body):
    """The RSC payload, **decoding each push on its own and concatenating after**.

    *This is also what makes the escaped quotes of item `17371` a non-event: the outer
    literal is unescaped once, and the inner JSON is then ordinary JSON.* One unreadable
    push is not the document.
    """
    out = []
    for lit in PUSH_RE.findall(body):
        try:
            out.append(json.loads('"' + lit + '"'))
        except ValueError:
            continue
    return "".join(out)


def _balanced(pl, start):
    """The balanced `[...]` beginning at `start`, **skipping strings**.

    A `[` or a `]` inside a title would otherwise close the array early, and this payload's
    titles are free text.
    """
    depth, j = 0, start
    while j < len(pl):
        c = pl[j]
        if c == '"':
            k = j + 1
            while k < len(pl):
                if pl[k] == "\\":
                    k += 2
                    continue
                if pl[k] == '"':
                    break
                k += 1
            j = k
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return pl[start:j + 1]
        j += 1
    return None


def models(pl, cat=CAT):
    """The item array of category `cat`.

    **The block is chosen by its CONTENT and never by position**: this page carries three
    `"models"` arrays and ours is the first only by accident of today's layout.
    """
    for m in re.finditer(r'"models"\s*:\s*\[', pl):
        i = pl.index("[", m.start() + len('"models"'))
        blob = _balanced(pl, i)
        if blob is None:
            continue
        try:
            arr = json.loads(blob)
        except ValueError:
            continue
        if isinstance(arr, list) and any(
                isinstance(x, dict) and x.get("cat_id") == cat for x in arr):
            return [x for x in arr if isinstance(x, dict) and x.get("cat_id") == cat]
    return None


def held(value):
    """**A field PRESENT is not a field FILLED, and `if x` cannot tell them apart.**

    The floor is POSITIVE: a string counts only when it is not blank, not a wire sentinel
    and does not begin with `$` — `"$undefined"` passes under any list that knows
    `undefined`.
    """
    if value is None:
        return False
    if isinstance(value, str):
        v = value.strip()
        return bool(v) and v.lower() not in ("undefined", "null", "none") and not v.startswith("$")
    if isinstance(value, (list, tuple)):
        return any(held(x) for x in value)
    if isinstance(value, dict):
        return any(held(x) for x in value.values())
    if isinstance(value, bool):
        return value
    return bool(value)


def scrub(s):
    """Free text with its contacts replaced. **Nothing on this board reaches it today** —
    the titles carry no telephone, 0 of 12 under two patterns — and it exists so that a
    title which one day does is not emitted with it."""
    if not isinstance(s, str) or not s.strip():
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    s = MSG_RE.sub("[messaging contact withheld]", s)
    s = TEL_RE.sub("[telephone withheld]", s)
    return re.sub(r"[ \t]+", " ", htmlmod.unescape(s)).strip() or None


def locale_fill(rows):
    """`{locale: how many items carry that locale's alias}` — the FILTER, derived from the
    payload rather than fetched four times."""
    return {loc: sum(1 for x in rows if held(x.get("alias_" + loc))) for loc in LOCALES}


def record(ad, locale=READ_LOCALE):
    ident = str(ad.get("id") or "").strip() or None
    withheld = [k for k in CONTACT_FIELDS if held(ad.get(k))]
    out = {
        "source": "turkmenportal", "country": "TM",
        "ledger_id": f"turkmenportal:{ident}" if ident else None, "id": ident,
        # the form the PAGE itself links -- a numeric id, not the alias
        "url": f"{BASE}/{locale}/advertisement/posts/{ident}" if ident else None,
        "title": scrub(ad.get("title")),
        "category": ad.get("cat_name") or None,
        # constant on this corpus, so it discriminates nothing: carried, never read
        "status": ad.get("status"),
        "views": ad.get("view_count"),
        "posted": ad.get("date") or None,
        "updated": ad.get("updated_date") or None,
        # where this advertisement is LISTED at all -- see the module docstring
        "listed_locales": sorted(loc for loc in LOCALES if held(ad.get("alias_" + loc))),
    }
    if held(ad.get("web_site")):
        out["web_site"] = ad["web_site"].strip()
    # **Derived, and ABSENT when the set is empty** -- a `withheld_fields` naming what
    # nobody deposited lies about OUR discretion, and a poor board then reads as a
    # censored one.
    if withheld:
        out["withheld_fields"] = sorted(withheld)
    return out


def cmd_list(a):
    loc = a.locale or READ_LOCALE
    url = LIST.format(locale=loc)
    code, body = get(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    pl = payload(body)
    rows = models(pl)
    if rows is None:
        die(f"{url}: no `models` array of category {CAT} in the RSC payload. "
            "**This says what THIS tool did not find, not what the host does not serve.**",
            EXIT_PARTIAL)
    if not rows:
        die(empty_first_page("turkmenportal", "", "advertisement", where=url), EXIT_PARTIAL)

    out = [record(x, loc) for x in rows]
    for r in (out[:a.limit] if a.limit else out):
        print(json.dumps(r, ensure_ascii=False))

    fill = locale_fill(rows)
    note(f"{len(out)} advertisement(s) of category {CAT} from `/{loc}/`, in ONE request: "
         f"the section declares `pageCount` 0 and states no count — its only `total` is the "
         f"i18n label, so no count is read by the name of its key.")
    note(f"alias fill on the {len(rows)} item(s) read: "
         + ", ".join(f"{k} {v}/{len(rows)}" for k, v in fill.items())
         + f" — **a per-locale listing shows only the items whose alias for that locale is "
           f"filled, so this is a /{loc}/ count and never the board's.**")
    note(f"**that fill is computed on the SURVIVORS of the filter, so it cannot say how much "
         f"the filter removes** — an item absent from `/{loc}/` is not in the array at all and "
         f"contributes to no locale's count. *`turkmenportal.py check-locales` is the only "
         f"thing that answers it, and it costs one request per locale.* This is the mirror of "
         f"`yora`, where four locales carry the SAME paths and the remedy is to dedup on the id.")
    hidden = sum(1 for r in out if r.get("withheld_fields"))
    note(f"{hidden} of {len(out)} record(s) name a withheld field ({', '.join(CONTACT_FIELDS)}); "
         "the rest held none and say nothing. **`address` is dropped although it is a location: "
         "street and locality travel in one free-form string on this host and no structured "
         "locality field exists, so a declared loss is preferred to an emitted street.**")
    recent = max((x.get("date") or "") for x in rows)
    note(f"the most recent of the {len(rows)} is dated {recent[:10] or 'unknown'} — "
         "**a MEASURE and not a verdict: the host answers 200 and the decision of what we "
         "give up reaching belongs to the owner.**")


def cmd_check_locales(a):
    """One request per locale, because nothing cheaper can answer it."""
    note(f"about to make {len(LOCALES)} request(s), one per locale, {_PACE.own:g} s apart — "
         "the host writes no Crawl-delay, so this floor is ours.")
    counts, maxi = {}, None
    for loc in LOCALES:
        url = LIST.format(locale=loc)
        code, body = get(url)
        if code != 200:
            note(f"/{loc}/: HTTP {code} — not counted, and the set is therefore INCOMPLETE.")
            counts[loc] = None
            continue
        rows = models(payload(body))
        counts[loc] = 0 if rows is None else len(rows)
    known = {k: v for k, v in counts.items() if v is not None}
    for loc in LOCALES:
        v = counts[loc]
        print(f"{loc}\t{'unknown' if v is None else v}")
    if not known:
        die("no locale answered: the board's size is not established", EXIT_PARTIAL)
    maxi = max(known, key=lambda k: known[k])
    note(f"the maximal locale is `/{maxi}/` with {known[maxi]} advertisement(s) of category "
         f"{CAT}; `list` reads `/{READ_LOCALE}/` by default."
         + ("" if maxi == READ_LOCALE else
            f" **READ_LOCALE is `{READ_LOCALE}` and it is NOT the maximal one: `list` "
            f"UNDER-COUNTS this board by {known[maxi] - known.get(READ_LOCALE, 0)}.**"))
    if len(known) < len(LOCALES):
        note("**at least one locale did not answer, so `maximal` is maximal AMONG THOSE THAT "
             "DID.** *A set that lost a member does not say which.*")


def main():
    p = argparse.ArgumentParser(
        description="TURKMENPORTAL (Turkmenistan) — the job board is category 117 of the "
                    "portal's classifieds, walked in ONE request; the LOCALE in the path "
                    "filters the listing instead of multiplying it, so `/ru` is read.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="every advertisement of category 117, one request")
    s.add_argument("--limit", type=int)
    s.add_argument("--locale", choices=LOCALES,
                   help=f"which locale's listing to read (default {READ_LOCALE}, the maximal one)")
    s.set_defaults(fn=cmd_list)
    c = sub.add_parser("check-locales",
                       help="count each locale's listing — the only answer to «is my count "
                            "the board's count?», at one request per locale")
    c.set_defaults(fn=cmd_check_locales)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
