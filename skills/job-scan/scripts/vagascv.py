#!/usr/bin/env python3
"""Vagas CV (`www.vagascv.info`) — «o maior portal de emprego de Cabo Verde», a Blogger blog of vacancies, internships and concursos whose **feed is refused IN WRITING** and whose POSTS are opened by an explicit `Allow`: the enumerator is `/sitemap.xml` (405 post paths on 2026-11-05) and the record is read from the post page itself. Issue #694.

  vagascv.py list [--max N]   the newest posts the sitemap enumerates, the stated total beside them
  vagascv.py ad --url <https://www.vagascv.info/<yyyy>/<mm>/<slug>.html>

THE RULES REFUSE THE ROUTE THE ISSUE NAMED, AND THEY OPEN A RICHER ONE. Measured
2026-11-05, the guard on the exact path in a turn distinct from the retrieval:

    /feeds*       Disallow to `User-agent: *`   <- the Blogger feed, REFUSED IN WRITING
    /search*      Disallow to `User-agent: *`   <- the label and search pages
    /*.html       an EXPLICIT Allow             <- the posts, opened on purpose
    /sitemap.xml  no rule                       <- allowed by absence

`state: read`, `certain: True`. **borne 1** therefore closes the feed by every route, the
browser included, and `bin/fetch-body.py` refuses it of its own accord. **The apex without
`www` returns `allowed=True` for the same path and is NOT a loophole**: using it would
circumvent a written refusal through a sibling host. Written down so that nobody
«discovers» it as an opening. `/search*` is never requested either — the labels are read
from the LINK TEXTS of a page we legitimately hold, never by asking for that path.

**`Disallow: /20*` would read as forbidding every post** — each path begins `/2026/`,
`/2025/` — and it does not: `Allow: /*.html` is the more specific match, **and the editor's
intention is written in the comments** («this line will disallow archieve section of
Blogger», «allow all post and pages of the blog»). So the standard's resolution and the
intention COINCIDE here rather than conflict, which is what makes the route safe.

THE SITEMAP EXHAUSTS THE POSTS, and that is measured rather than assumed: `/sitemap.xml`
(200, 50 137 B) lists **405 `<loc>`, all distinct, all post paths**, no CDATA, no
per-language over-counting; `?page=2` returns an EMPTY urlset and `?page=1` returns the
405, so the parameter is HONOURED and the empty page is an answer and not an ignored
argument; and the second declared sitemap, `sitemap-pages.xml`, holds **16 static `/p/`
pages and ZERO post**. No `Crawl-delay` is written for any agent, so **3 s is ours**.

**THE JSON-LD IS AN AUTHORING ARTEFACT AND NOT A DATA SOURCE — this is why the record is
read from the PAGE.** Measured on 26 posts spread across the whole sitemap (every 15th,
index 0 to 375), never the newest 26:

    no `application/ld+json` block at all   18/26   69 %
    a block that will not parse              7/26   27 %
    a clean block                            1/26    4 %

And **all 18 without a block are plainly vacancies** — «Su-Chef de Cozinha», «Engenheiro
Civil», «Rececionista», «Mecânico de Primeira» — so the hypothesis that an absent block
means «not a vacancy» is **REFUTED**: an adapter built on the JSON-LD would emit 8 of 26
and lose eighteen real adverts. The cause is in the page: the theme's own script GENERATES
the block at authoring time (`return { html: html, code: html + '<script type=...ld+json'`),
so it is absent when the author did not fill the widget and malformed when a field was left
empty. The malformations are TWO superposed defects — a bare control character inside the
`description` string, which `strict=False` repairs, and then `"minValue": ,` / `"maxValue": ,`,
an empty value that it does not. Both are handled, and the block is a BONUS: the record
never depends on it.

THE PAGE CARRIES EVERYTHING, 26/26 on the same spread sample: `<h1 class='vcv-vsrc__title'>`,
`og:title`, `og:url`, `data-id`, `data-url`, an ISO timestamp beside `data-id`, the label
link texts, and a body whose extracted text runs 1 150 to 4 167 characters, median 1 627.
**The attributes are written with SINGLE quotes**, and a first probe that assumed double
ones reported every field ABSENT — the motif is tried on the form the data has AT THE POINT
OF CALL.

**THE CONTACTS ARE REAL AND THE WITNESS IS DERIVED.** 21 of those 26 bodies (81 %) carry a
recruiter's e-mail address and 3 a telephone, so the redaction is heavily exercised rather
than theoretical. `withheld_fields` names what was ACTUALLY removed and the declaration
goes through the repository's single point of judgement (`_withheld`), never the truthiness
of that list. The phone pattern is Cabo Verde's own (`+238`, seven digits beginning 2, 5 or
9) and was tried **in both directions against the escudo**, the country's currency: `50.000$00`,
`100 000$00`, `CVE 60000`, `1.500.000$00` and `75.000 escudos` are untouched, while the three
real forms found in the corpus are caught. *Residue declared: a BARE seven-digit amount
beginning 2, 5 or 9 would be taken for a number. Zero such amount appears in the 26 bodies —
escudos are written with separators and the `$00` suffix — so this is a measured risk and not
a measured defect.*

Measured 2026-11-05 18:4x-19:1x UTC by the declared client, the guard on each exact path.
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
from _withheld import withheld_a_contact

HOST = "www.vagascv.info"
SITEMAP = f"https://{HOST}/sitemap.xml"
DEFAULT_MAX = 25
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# Cabo Verde: +238, seven digits beginning 2 (fixed), 5 or 9 (mobile). Tried in BOTH
# directions against the escudo -- the country's currency -- because a digit-count rule
# on a currency is how 113 of 115 salaries were once destroyed.
PHONE_RE = re.compile(r"(?<![\d.$])(?:\+?238[\s\-]?)?[259]\d{2}[\s\-]?\d{2}[\s\-]?\d{2}(?!\d)")
POST_RE = re.compile(r"^/(\d{4})/(\d{2})/([^/]+)\.html$")
# **REFUSED IN WRITING to `*`: never sent, by any route.** `/20*` is NOT in this list --
# `Allow: /*.html` is the more specific match and the editor's comments say so.
REFUSED_RE = re.compile(r"^/(?:feeds|search)(?:/|\?|$)")

LOC_RE = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", re.S)
TITLE_RE = re.compile(r"<h1[^>]*class=['\"][^'\"]*vcv-vsrc__title[^'\"]*['\"][^>]*>(.*?)</h1>", re.S | re.I)
OG_RE = r"<meta[^>]*content=['\"]([^'\"]*)['\"][^>]*property=['\"]og:%s['\"]"
ID_RE = re.compile(r"data-id=['\"](\d+)['\"]")
WHEN_RE = re.compile(r"['\"](\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})['\"]\s+data-id")
ANCRE_RE = re.compile(r"<a\b[^>]*>", re.I)        # chaque ancre, puis on EXIGE les deux marques
LABEL_RE = re.compile(r"/search/label/([^'\"?#]+)")
BODY_RE = re.compile(r"<div[^>]*class=['\"][^'\"]*vcv-vsrc__body[^'\"]*['\"][^>]*>(.*?)"
                     r"(?:<div[^>]*class=['\"][^'\"]*vcv-src__labels|</article>)", re.S | re.I)
LD_RE = re.compile(r"<script[^>]*type=['\"]application/ld\+json['\"][^>]*>(.*?)</script>", re.S | re.I)
VIDE_RE = re.compile(r':\s*(?=[,}\]])')      # `"minValue": ,` -- the theme emits an empty value


AFFILIE = ("go.hotmart.com", "hotmart.com/", "/ref=", "utm_source=afil")
ALERTE_RE = re.compile(r"<div[^>]*class=['\"][^'\"]*elementskit_alert[^'\"]*['\"][^>]*>", re.I)
DIV_RE = re.compile(r"<div\b|</div\s*>", re.I)


def sans_affilie(markup):
    """Drops the author's affiliate block from a post body -- **only when it CARRIES an
    affiliate link**, never on the class alone.

    The author pastes `<div class="elementskit_alert alert_success">` with `go.hotmart.com`
    links («Quer Monetizar blogs? | Clique Aqui») INSIDE the advert, and 17 of 26 bodies in
    a spread sample carried it. Dropping it on the CLASS alone would eat a legitimate
    notice written in the same box, and an over-redaction is the one defect whose output
    does not differ from a well-conducted discretion. The close is found by COUNTING
    `<div>`/`</div>`, because the block nests an `alert_message` and a non-greedy `</div>`
    would cut inside it."""
    out, i = [], 0
    while True:
        m = ALERTE_RE.search(markup, i)
        if not m:
            out.append(markup[i:])
            return "".join(out)
        prof, j = 1, m.end()
        while prof and j < len(markup):
            t = DIV_RE.search(markup, j)
            if not t:
                j = len(markup)
                break
            prof += 1 if t.group(0).lower().startswith("<div") else -1
            j = t.end()
        bloc = markup[m.start():j]
        out.append(markup[i:m.start()])
        if not any(a in bloc for a in AFFILIE):
            out.append(bloc)          # a legitimate notice in the same box is KEPT
        i = j

_PACE = Pace(HOST, own=3.0)   # no Crawl-delay written; 3 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[vagascv] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    """**The refusal below is UNREACHABLE from `list` and `ad`, by construction, and that is
    declared rather than left to look like a live guard**: `list` only ever asks the sitemap
    and the post paths the sitemap gives, and `ad` rejects a non-post address before getting
    here. It is defence in depth for a future caller, so the suite EXERCISES it directly --
    a guard nobody can reach and nobody tests is inert, and its green says nothing."""
    parts = urllib.parse.urlsplit(url)
    if REFUSED_RE.search(parts.path):
        die(f"{url}: `/feeds` and `/search` are refused IN WRITING to `*` -- never sent, "
            f"by any route", EXIT_REFUSED)
    if parts.netloc and parts.netloc != HOST:
        die(f"{url}: only `{HOST}` is asked -- the apex answers `allowed=True` for the "
            f"refused paths and using it would circumvent a written refusal through a "
            f"sibling host", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xml;q=0.9", "Accept-Language": "pt"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def fetch(url, quoi):
    code, body = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    if not body:
        die(f"{url}: 200 and an empty body -- {quoi} unreadable", EXIT_PARTIAL)
    return body


def text(markup):
    t = re.sub(r"<script\b.*?</script>", " ", markup or "", flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    """Returns (text, what was ACTUALLY removed) -- the witness is derived, never asserted."""
    if not s:
        return None, []
    taken = []
    if MAIL_RE.search(s):
        taken.append("email")
        s = MAIL_RE.sub("[e-mail withheld]", s)
    if PHONE_RE.search(s):
        taken.append("telephone")
        s = PHONE_RE.sub("[telephone withheld]", s)
    return (s.strip() or None), taken


def ldjson(page):
    """The theme's own block when it parses -- a BONUS, never the record's source.

    Two superposed defects, both measured: a bare control character inside the
    `description` string, which `strict=False` accepts, and `"minValue": ,`, an empty
    value the theme emits when a field was left blank. Returns `None` rather than
    guessing, and the caller does not depend on it."""
    for raw in reversed(LD_RE.findall(page)):
        for essai in (raw.strip(), VIDE_RE.sub(": null", raw.strip())):
            for strict in (True, False):
                try:
                    d = json.loads(essai, strict=strict)
                except ValueError:
                    continue
                for it in (d if isinstance(d, list) else [d]):
                    if isinstance(it, dict) and it.get("@type") == "JobPosting":
                        return it
    return None


def one(x):
    return x if isinstance(x, dict) else {}


def record(url, page):
    m_id = ID_RE.search(page)
    pid = m_id.group(1) if m_id else None
    t = TITLE_RE.search(page)
    if not t:
        t = re.search(OG_RE % "title", page, re.I)
    titre = htmlmod.unescape(text(t.group(1)) or "").strip() if t else None
    when = WHEN_RE.search(page)
    og = re.search(OG_RE % "url", page, re.I)
    # **SCOPED to the post's own anchors (`vcv-src__l`) and never to the page.** Unscoped,
    # the field named the BLOG's taxonomy while claiming the POST's: measured 29 label links
    # on one page, of which 11 sit in a dropdown, 11 in the sidebar and 5 in the footer --
    # and two more came from a template COMMENT that mentions `/search/label/` in prose, the
    # third time on this host that the page talks about itself. A field that over-declares
    # is worse than an absent one. `/search` itself is never requested: this reads the link
    # TEXTS of a page we already hold.
    labels = sorted({htmlmod.unescape(urllib.parse.unquote(m.group(1))).strip()
                     for tag in ANCRE_RE.findall(page) if "vcv-src__l" in tag
                     for m in [LABEL_RE.search(tag)] if m}) or None
    b = BODY_RE.search(page)
    corps, taken = scrub(text(sans_affilie(b.group(1))) if b else None)
    jp = ldjson(page) or {}
    addr = one(one(jp.get("jobLocation")).get("address"))
    r = {
        "source": "vagascv", "country": "CV", "ledger_id": f"vagascv:{pid}", "id": pid,
        "url": (og.group(1) if og else url),
        "title": titre, "labels": labels,
        "published": (when.group(1)[:10] if when else None),
        "employer": (one(jp.get("hiringOrganization")).get("name") or None),
        "valid_through": (jp.get("validThrough") or "")[:10] or None,
        "employment_type": jp.get("employmentType") or None,
        "region": addr.get("addressRegion") or None,
        "ldjson": bool(jp),
        "text": corps,
        "withheld_fields": taken or None,
        "language": "pt",
    }
    # The key is ABSENT when nothing that reaches a person left the record -- the
    # repository's form (`_withheld`, #1238): `contacts_withheld` is NOT the truthiness of
    # `withheld_fields`, which mixes what reaches a PERSON with what was dropped for
    # another reason, and an `else` branch breaks the in-suite mutation that proves the
    # guard is not inert. An absence is not a claim; a `False` would be one.
    if withheld_a_contact(r["withheld_fields"]):
        r["contacts_withheld"] = True
    return r


def posts():
    """The sitemap's post paths, newest first -- the ONLY enumerator, the feed being
    refused in writing. Measured: 405, all distinct, all post paths, and `?page=2` is an
    empty urlset while `?page=1` returns the 405, so the set is exhausted."""
    body = fetch(SITEMAP, "the sitemap")
    locs = LOC_RE.findall(body)
    out, seen = [], set()
    for u in locs:
        p = urllib.parse.urlsplit(u)
        if p.netloc == HOST and POST_RE.match(p.path) and u not in seen:
            seen.add(u)
            out.append(u)
    if not out:
        die(f"{SITEMAP}: 200, {len(locs)} <loc> and NOT ONE post path -- the shape changed; "
            f"not an empty blog", EXIT_PARTIAL)
    return out, len(locs)


def cmd_list(a):
    urls, total = posts()
    borne = a.max if a.max else DEFAULT_MAX
    pris = urls[:borne]
    out = []
    for u in pris:
        out.append(record(u, fetch(u, "a post page")))
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    sansid = [r["url"] for r in out if not r["id"]]
    note(f"{th(n)} emitted of the {th(len(urls))} post paths the sitemap enumerates "
         f"({th(total)} <loc> in all, the rest being static pages) -- walked BY REQUEST "
         f"(--max {borne}), not a shortfall; the feed is refused IN WRITING so the sitemap "
         f"is the only enumerator.")
    nl = sum(1 for r in out if r["ldjson"])
    note(f"the record is read from the PAGE: {nl} of {n} also carried a parseable "
         f"`JobPosting`, which is the theme's own authoring artefact and a BONUS -- 69 % of "
         f"a spread sample carry none at all, and all of those are vacancies.")
    nw = sum(1 for r in out if r.get("contacts_withheld"))
    note(f"a contact was removed from {nw} of {n} -- `withheld_fields` names what was "
         f"actually taken; `/search` and `/feeds` never requested, the apex never asked, "
         f"and the employers' own application routes never followed.")
    if sansid:
        note(f"{len(sansid)} page(s) carried no `data-id`: {sansid[:3]}")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    if parts.netloc != HOST or not POST_RE.match(parts.path):
        die(f"{a.url}: not a post address (https://{HOST}/<yyyy>/<mm>/<slug>.html); the "
            f"apex is not asked either")
    r = record(a.url, fetch(a.url, "a post page"))
    if not r["id"] and not r["title"]:
        die(f"{a.url}: 200 and neither a `data-id` nor a title -- the shape changed", EXIT_PARTIAL)
    print(json.dumps(r, ensure_ascii=False))
    note(f"{a.url}: read from the page; `JobPosting` {'read as a bonus' if r['ldjson'] else 'absent or unparseable, which changes nothing'}; "
         + (f"withheld {', '.join(r['withheld_fields'])}" if r["withheld_fields"] else "nothing to withhold")
         + "; the application route never followed.")


def main():
    p = argparse.ArgumentParser(description="Vagas CV -- the sitemap enumerates, the POST PAGE is the record, and the Blogger feed is refused in writing. Issue #694.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help=f"the newest posts the sitemap enumerates -- {DEFAULT_MAX} unless --max")
    l_.add_argument("--max", type=int, help="how many post pages to read (one request each, 3 s apart)")
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
