#!/usr/bin/env python3
"""CareerHub (`www.careerhub.mu`, Mauritius): a bilingual board whose every advert is a complete `JobPosting` — and which serves 24 of the 158 it states. Issue #701.

  careerhub.py jobs [--lang fr|en] [--country-code MU]      the served page, against the stated total
  careerhub.py ad --url https://www.careerhub.mu/fr/jobs/<uuid>

WHAT IT IS. CareerHub is a Mauritian board in French and English, and **its structured data is the
richest this repository has measured in these three countries**: the list declares an `ItemList`
with its own total, and every advert is a full `JobPosting` carrying `datePosted` and
`validThrough` as ISO instants, `hiringOrganization`, `jobLocation` as a `PostalAddress`, and
**`baseSalary` in MUR with a min and a max** — where the Haitian boards of #777 and #776 declare
no salary at all and #777 declares no date in any form.

THE RULES. `www.careerhub.mu/robots.txt` is read: group `*`, no `Disallow` on these paths, open and
`certain: True`, no `Crawl-delay`; 3 s is ours. The guard is taken on the exact path. **The host is
the `www.` form, which is what the card declares** — the sibling `jobpaw.com` is the bare name and
its `www.` fails TLS, so the form is read off the card and never typed.

**WHAT IT SERVES, AND WHAT IT DOES NOT — THIS IS THE WHOLE SHAPE OF THIS ADAPTER.** `/fr/jobs`
(200; 218 980 B) carries an `ItemList` stating **`numberOfItems: 158`** and exactly **24**
`itemListElement`, each with its advert's URL, title and position; 24 `href="/fr/jobs/<uuid>"` in
the markup agree with them. The remaining **134 are behind a client-side loader** — the page is a
Next.js App Router app (`self.__next_f` ×16) and the «Voir 24 offres de plus» control is a
`<button>` with no URL in the markup: no `wire:`, no `hx-`, no `/api/`, no cursor, no offset.
**And `?page=2` is MEASURED as ignored**: it returns 200 with the *same* 24 UUIDs, positions 1–24,
identical set. So this adapter emits **24 of 158 — 15 %** and says so on every run, against a
total the board states itself.

*That is weaker than a whole board, and it is declared weaker. It is not a «partial» that cries
wolf: the proportion is a measured constant of what the host serves to a plain client, the board's
own total is the denominator, and 24 current Mauritian openings are 24 a candidate did not have.*

THE WITNESS, AND WHY IT IS NOT TAKEN FROM `_ldjson.objects()`. The total lives on the `ItemList`
container, and **`objects()` expands that container into its items — 26 objects on this page, of
types `ListItem`, `Organization`, `WebSite`, and no `ItemList` among them.** So the container's
`numberOfItems` is gone by the time `objects()` has spoken. This adapter reads `_ldjson.blocks()`
and finds the `ItemList` itself: *a helper that flattens a container loses the container's count,
and the count is the only witness external to our own extraction.*

THE ADVERT. `ad` reads the `JobPosting` through `_ldjson.postings()` — which handles the two
deviations that module documents, single-quoted `type='…'` and a parser that needs `strict=False`.
**Reading the posting also BOUNDS the redaction structurally**, and that is the point: the site's
own address (`hello@mooove.group`) and its own telephone (`+230 268 2222`, four times) live in the
page's footer, OUTSIDE the posting. Scrubbing the whole page would declare a withheld contact on
every record for a contact no employer ever deposited — the fault of claiming a discretion one did
not exercise. Scrubbing the posting's own fields cannot.

**THE PHONE MOTIF IS ANCHORED, AND NEITHER SIBLING'S ANCHOR TRANSPOSES.** Mauritius dials `+230`,
not `+509`, so `jobpaw.py`'s and `emploilenouvelliste.py`'s anchors return ZERO here. And the bare
motif used elsewhere takes **8 strings on this advert of which 4 are not telephones** —
`0035-4483`, `4786-8585`, `1679-4753`, `68560804`, which are the page's own identifiers. Anchored
on `+230` or a written label it takes the real number and none of the four. *The remedy transposes
between boards; the exact motif never does, and it is measured on the form each board serves.*

**TWO HOST FORMS, AND THE BOARD'S OWN CANONICAL IS NOT THE ONE THE CARD DECLARES.** The card
has `www.careerhub.mu`; the page declares `rel="canonical" href="https://careerhub.mu/fr/jobs"`
and **all 26 URLs in its `ItemList` use the bare form**. So an `ad` that accepted only the card's
form refused the URLs of its own list — measured, by running it. Both forms are guarded (`*`, no
`Disallow`, `state: read`, `certain: True` on each) and both are accepted; the list is built on the
card's form because that is what the card declares, and the divergence is recorded rather than
normalised away. *This is the third board in one slot where the DATA names a different host from
the PAGE, after `bast.af`\u2019s `db.` and `myjob.mu`\u2019s `app.` — and the `app.` one is refused by
written rules, so the direction matters.*

**AND `one()` IS NOT `label()`, WHICH `_ldjson` SAYS IN ITS OWN DOCSTRING.** The first version of
this adapter read every text field with `one()` and emitted **24 adverts with an empty title**:
`one()` returns `{}` for a bare string, deliberately — «*A string is not silently turned into a
name: use `label()` when the field may legitimately be text*» — and `ItemList`\u2019s `name` is a bare
string. `one()` is for the fields that must be OBJECTS, so that `.get()` is always legal whether
the board sent an object, a list or a string; `label()` is for the ones that are text. The module
is sound and documents the distinction; using the wrong half of it was the defect.

Measured 2026-11-03 21:1x UTC by the declared client, the guard on the exact paths in a turn of its
own: `/robots.txt` read (`*`, no `Disallow`, `certain: True`), `/fr/jobs` 200 (218 980 B,
md5 057662b4f12d) with `numberOfItems: 158` and 24 items, `?page=2` 200 (219 723 B) with the SAME
24, one advert at `/fr/jobs/845ca852-…` 200 (96 520 B, md5 4a9be6ccb23b) carrying a complete
`JobPosting`. The premise of #701 moved: «163 offres» on 2026-09-18, **158** now, and its «la liste
et l'annonce ne sont pas encore lues» is answered.
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

import _ldjson
from _decode import decode_body
from _locations import fold
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA
from _withheld import withheld_a_contact

# the card declares the `www.` form; the board's own canonical and every `ItemList` URL use
# the BARE one. Both are guarded and both are accepted — an `ad` that took only the card's
# form refused the URLs of its own list.
HOST = "www.careerhub.mu"
HOSTS = ("www.careerhub.mu", "careerhub.mu")
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# ANCHORED on the MAURITIAN dialling code or a written label. Neither sibling's anchor works
# here (+509 is Haiti), and the bare motif takes four of this page's own identifiers.
PHONE_RE = re.compile(
    r"\+\s*\(?\s*230\s*\)?[\s.\-]?\d[\d\s.\-]{5,}\d"
    r"|(?:T[ée]l(?:[ée]phone)?|Phone|Mobile|Cell|Whatsapp|WhatsApp)\s*:?\s*\(?\+?\d[\d\s().\-]{5,}\d")
AD_RE = re.compile(r"^/(?:fr|en)/jobs/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[careerhub] {msg}", file=sys.stderr)


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
    if parts.scheme != "https" or parts.netloc not in HOSTS:
        die(f"{url}: not one of {', '.join(HOSTS)} — never sent", EXIT_REFUSED)
    gate(url)
    # the pace is PER HOST, and the two forms are two hosts to a rate limiter
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=3.0)).wait()   # no Crawl-delay written; 3 s is ours
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ") if isinstance(n, int) else str(n)


def scrub(s):
    """Contacts out of the POSTING's own text, and the record says which kinds were there."""
    if not isinstance(s, str) or not s:
        return s, []
    took = []
    if MAIL_RE.search(s):
        took.append("email")
        s = MAIL_RE.sub("[e-mail withheld]", s)
    out = PHONE_RE.sub("[telephone withheld]", s)
    if out != s:
        took.append("telephone")
    return (out.strip() or None), took


def item_list(html):
    """The `ItemList` CONTAINER, read from the raw blocks.

    Not from `_ldjson.objects()`: that expands the container into its items, so
    `numberOfItems` — the only witness external to this extraction — is gone by then.
    """
    for raw in _ldjson.blocks(html or ""):
        try:
            d = json.loads(raw, strict=False)
        except ValueError:
            continue
        for o in (d if isinstance(d, list) else [d]):
            if isinstance(o, dict) and o.get("@type") == "ItemList":
                return o
    return None


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    url = f"https://{HOST}/{a.lang}/jobs"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the list is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    lst = item_list(body)
    if lst is None:
        die(f"{url}: 200 without an `ItemList` block — the page changed; not an empty board",
            EXIT_PARTIAL)
    said = lst.get("numberOfItems")
    said = said if isinstance(said, int) else None
    elements = [e for e in (lst.get("itemListElement") or []) if isinstance(e, dict)]
    # the markup's own hrefs, as a SECOND reading of the same object
    hrefs = {m for m in re.findall(r'href="(/(?:fr|en)/jobs/[0-9a-f-]{36})"', body or "")}
    rows, seen = [], set()
    for e in elements:
        u = e.get("url")
        if not isinstance(u, str):
            continue
        ident = urllib.parse.urlsplit(u).path.rstrip("/").rsplit("/", 1)[-1]
        if ident in seen:          # raw and distinct must be able to differ
            continue
        seen.add(ident)
        # `label`, not `one`: the `ItemList`'s `name` is a bare STRING and `one()` returns
        # `{}` for a string by design — that is what emptied all 24 titles
        title, took = scrub(_ldjson.label(e.get("name")))
        r = {
            "source": "careerhub", "country": stamp,
            "ledger_id": f"careerhub:{ident}", "id": ident,
            "title": title, "url": u,
            "list_position": e.get("position"),
            "withheld_fields": sorted(set(took)),
        }
        if withheld_a_contact(r["withheld_fields"]):
            r["contacts_withheld"] = True
        rows.append(r)
    if not rows:
        die(f"{url}: an `ItemList` with no usable item — the page changed", EXIT_PARTIAL)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

    note(f"{th(len(rows))} advert(s) emitted from the page's own `ItemList`.")
    if said is None:
        note("**the list states no total this time** — it usually carries `numberOfItems` on its "
             "`ItemList`, and the run says so rather than claiming one.")
    elif said > len(rows):
        note(f"the board states **{th(said)}** and serves **{th(len(rows))}** to a plain client: "
             f"{th(said - len(rows))} are behind a client-side loader. The «Voir N offres de "
             f"plus» control is a button with no URL in the markup — no `wire:`, no `hx-`, no "
             f"`/api/`, no cursor — and `?page=2` is MEASURED as ignored: it returns the SAME "
             f"items, positions 1 to {th(len(rows))}. **So this is {100 * len(rows) // said} % "
             f"of the board, and the denominator is the board's own.**")
    else:
        note(f"{th(len(rows))} emitted and the board states {th(said)} — they agree.")
    if hrefs and len(hrefs) != len(rows):
        note(f"the markup carries {th(len(hrefs))} advert link(s) for {th(len(rows))} item(s) in "
             f"the `ItemList`: the two readings of the same page DISAGREE, so one of them is "
             f"incomplete and the count above is the `ItemList`'s.")
    note("the total is read from the `ItemList` CONTAINER and not from `_ldjson.objects()`, "
         "which expands it into its items and loses `numberOfItems` — the only witness external "
         "to this extraction.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the list states none per advert.")


def cmd_ad(a):
    url = a.url.strip()
    parts = urllib.parse.urlsplit(url)
    m = AD_RE.match(parts.path)
    if parts.scheme != "https" or parts.netloc not in HOSTS or not m:
        die(f"--url {url}: a https://<{' | '.join(HOSTS)}>/fr|en/jobs/<uuid> advert")
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the advert is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    posts = _ldjson.postings(body)
    if not posts:
        die(f"{url}: 200 without a `JobPosting` block — {_ldjson.absent_reason(body)}",
            EXIT_PARTIAL)
    p = posts[0]
    took = []
    def pris(v):
        out, t = scrub(v)
        took.extend(t)
        return out
    # `one()` HERE, and this is what it is for: it renders `{}` for a string, a list or
    # None, so `.get()` is legal whatever shape the board sent
    org = _ldjson.one(p.get("hiringOrganization"))
    addr = _ldjson.one(_ldjson.one(p.get("jobLocation")).get("address"))
    sal = _ldjson.one(p.get("baseSalary"))
    val = _ldjson.one(sal.get("value"))
    r = {
        "source": "careerhub", "country": a.country_code.upper() if a.country_code else None,
        "ledger_id": f"careerhub:{m.group(1)}", "id": m.group(1),
        "title": pris(_ldjson.label(p.get("title"))),
        "employer": pris(_ldjson.label(org)),
        "posted": _ldjson.label(p.get("datePosted")),
        "valid_through": _ldjson.label(p.get("validThrough")),
        "employment_type": _ldjson.label(p.get("employmentType")),
        "city": _ldjson.label(addr.get("addressLocality")),
        "region": _ldjson.label(addr.get("addressRegion")),
        "country_stated": _ldjson.label(addr.get("addressCountry")),
        "salary_currency": _ldjson.label(sal.get("currency")),
        "salary_min": val.get("minValue"),
        "salary_max": val.get("maxValue"),
        "experience": _ldjson.label(p.get("experienceRequirements")),
        "description": pris(_ldjson.label(p.get("description"))),
        "url": url,
        "withheld_fields": sorted(set(took)),
    }
    if withheld_a_contact(r["withheld_fields"]):
        r["contacts_withheld"] = True
    print(json.dumps(r, ensure_ascii=False))
    note(f"read from the advert's own `JobPosting`: "
         f"{', '.join(k for k, v in r.items() if v not in (None, [], ''))}.")
    note("the redaction is BOUNDED to the posting's own fields, and that is structural: the "
         "site's own address and telephone live in the page footer, OUTSIDE the posting. "
         "Scrubbing the whole page would declare a withheld contact on every record for one no "
         "employer deposited.")
    if not r["withheld_fields"]:
        note("nothing was scrubbed from this advert; `withheld_fields` is empty because the "
             "posting carried no contact, not because none was looked for.")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="CareerHub (Mauritius) — every advert a complete `JobPosting`, and 24 of the "
                    "158 the board states served to a plain client. Issue #701.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the served page, against the total the board states")
    j.add_argument("--lang", choices=("fr", "en"), default="fr", help="the board is bilingual")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on every record")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert, from its own `JobPosting`")
    d.add_argument("--url", required=True, help="the advert's own address")
    d.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on the record")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
