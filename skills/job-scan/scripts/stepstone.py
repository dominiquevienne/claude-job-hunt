#!/usr/bin/env python3
"""Fetch ads from the StepStone platform — eleven domains, six inventories, one
result list that pads itself with ads that do not match.

One application serves Totaljobs, Jobsite, Caterer, CWJobs, IrishJobs, NIJobs,
Jobs.ie and StepStone DE/AT/BE/NL. They run **the same bundle** (`client-bundle.js`,
v4.107.0 on 2026-09-02), the same design system (`data-genesis-element`), the
same card contract (`data-at="job-item"`) and the same ad markup, and they are
told apart by one number — `siteId`, in `window.__PRELOADED_STATE__.header`.

  GET /jobs/<keyword>                     → the result list, 25 cards, HTTP 200
  GET /jobs/<keyword>/in-<place>          → the same, narrowed by location
  GET /jobs/<keyword>?page=<n>            → page n, where the site allows it
  GET /job/x/y-job<id>                    → the ad (UK/IE), slug ignored
  GET /stellenangebote--x--<id>-inline.html → the ad (StepStone), slug ignored

**No browser, no account, no key** — but two constraints that decide the code.

THE COUNT ON THE PAGE IS NOT THE COUNT OF ADS THAT MATCH. Every result list
carries an analytics payload, `data-atx-onpageview-payload`, and it breaks its
own total down:

    stepstone.nl  "software developer"  total:26   main:1    semantic:25
    stepstone.be  "software developer"  total:607  main:110  semantic:497
    stepstone.at  "softwareentwickler"  total:519  main:248  semantic:271
    stepstone.de  "softwareentwickler"  total:4962 main:4892 semantic:70
    totaljobs     "software developer"  total:3786 main:3785 semantic:1
    irishjobs     "software developer"  total:408  main:408  semantic:0

**`semantic` is the platform's own word for ads it decided were related.** On
stepstone.nl, 25 of the 26 results for "software developer" are that — the
board holds **one** literal match and serves a full page of 25 cards anyway.
Nothing in the visible list separates the two populations, and the payload
gives counts, not per-card attribution. Adding a location adds a third:
`regional`, 796 of 1 862 on Totaljobs "software developer in-london".

So every command here prints the split, and `search` refuses to stay quiet when
the padding is the majority. The honest reading of a page is *main*, and *main*
is not what you counted.

THE OTHER CONSTRAINT IS THE TRANSPORT. A request to this platform can fail
**with no HTTP status at all** — `HTTP/2 stream not closed cleanly:
INTERNAL_ERROR`, or a read timeout. It hits cold ad-page requests over HTTP/2,
and it hits any host after a burst. It is not a 429, not a 403, and not a page:
a client that reads "no status" as a network blip will retry for ever.

`urllib` speaks HTTP/1.1 only, which is why this script does not see the first
form. It still sees the second, so it retries **once**, slowly, and then stops
and says the sweep was truncated. Never loop.

Everything here was verified against the live sites on **2026-09-02**.
"""

import argparse
import collections
import html as html_mod
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from _zero import zero_note

from _locations import fold, matches_city

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

# `pages` is the number of result pages robots.txt leaves open, per site, and
# they are not the same number — see stepstone.md, *The depth is a per-site
# field*. `None` means the site's own robots.txt reopens `page=` when the query
# carries `q=`, so the depth is the result set.
SITES = {
    "totaljobs":    dict(host="www.totaljobs.com", country="GB", lang="en-GB",
                         seg="/jobs", ad="/job/x/y-job{id}", pages=5,
                         inventory="uk"),
    "jobsite":      dict(host="www.jobsite.co.uk", country="GB", lang="en-GB",
                         seg="/jobs", ad="/job/x/y-job{id}", pages=1,
                         inventory="uk"),
    "caterer":      dict(host="www.caterer.com", country="GB", lang="en-GB",
                         seg="/jobs", ad="/job/x/y-job{id}", pages=None,
                         inventory="uk"),
    "irishjobs":    dict(host="www.irishjobs.ie", country="IE", lang="en-IE",
                         seg="/jobs", ad="/job/x/y-job{id}", pages=None,
                         inventory="ie"),
    "nijobs":       dict(host="www.nijobs.com", country="GB-NIR", lang="en-GB",
                         seg="/jobs", ad="/job/x/y-job{id}", pages=None,
                         inventory="ie"),
    "jobs-ie":      dict(host="www.jobs.ie", country="IE", lang="en-IE",
                         seg="/jobs", ad="/job/x/y-job{id}", pages=None,
                         inventory="ie"),
    "stepstone-de": dict(host="www.stepstone.de", country="DE", lang="de-DE",
                         seg="/jobs", pages=1, inventory="de",
                         ad="/stellenangebote--x--{id}-inline.html"),
    "stepstone-at": dict(host="www.stepstone.at", country="AT", lang="de-AT",
                         seg="/jobs", pages=1, inventory="at",
                         ad="/stellenangebote--x--{id}-inline.html"),
    "stepstone-be": dict(host="www.stepstone.be", country="BE", lang="en-BE",
                         seg="/jobs", pages=1, inventory="be",
                         ad="/jobs--x--{id}-inline.html"),
    "stepstone-nl": dict(host="www.stepstone.nl", country="NL", lang="nl-NL",
                         seg="/vacatures", pages=1, inventory="nl",
                         ad="/banen--x--{id}-inline.html"),
}

# Not a board. 50 of 50 cards on cwjobs.co.uk/jobs/software-developer link to
# www.totaljobs.com/job/…, none to cwjobs.co.uk, and its ids resolve on
# Totaljobs. Sweeping it duplicates Totaljobs by construction.
NOT_A_BOARD = {
    "cwjobs": ("cwjobs.co.uk is a filtered view of Totaljobs, not a separate "
               "board: 50 of 50 result cards link to www.totaljobs.com/job/…, "
               "0 to cwjobs.co.uk (measured 2026-09-02). Sweep `totaljobs` "
               "instead — every CWJobs ad is in it."),
}

# Salary strings that are the field being filled with the word "empty".
# 73 of 100 IrishJobs cards said "€ Not Disclosed"; Totaljobs says
# "Unspecified", "Competitive" and "Negotiable".
UNDISCLOSED = re.compile(
    r"not disclosed|unspecified|competitive|negotiable|doe|on application",
    re.I)

CARD = re.compile(r'<article\b[^>]*id="job-item-(\d+)"[^>]*>(.*?)</article>',
                  re.S)
TAG = re.compile(r"<(/?)([a-zA-Z][\w-]*)\b[^>]*?(/?)>")
VOID = {"br", "img", "input", "path", "use", "source", "meta", "hr"}
PAYLOAD = re.compile(r'data-atx-onpageview-payload="([^"]+)"')
LD = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
                re.S)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[stepstone] {msg}", file=sys.stderr)


class Session:
    """One host, one cookie jar, one pace.

    The first request to a host is a plain result list — warming it costs
    nothing and the platform answers ad URLs more reliably afterwards.
    """

    def __init__(self, site, delay=2.0):
        self.s = SITES[site]
        self.name = site
        self.delay = delay
        self.jar = {}
        self.last = 0.0
        self.truncated = False

    def get(self, path, referer=None, retry=True):
        url = f"https://{self.s['host']}{path}"
        wait = self.delay - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": self.s["lang"] + ",en;q=0.8",
        })
        if self.jar:
            req.add_header("Cookie", "; ".join(
                f"{k}={v}" for k, v in self.jar.items()))
        if referer:
            req.add_header("Referer", f"https://{self.s['host']}{referer}")
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                for raw in r.headers.get_all("Set-Cookie") or []:
                    k, _, v = raw.split(";")[0].partition("=")
                    self.jar[k.strip()] = v.strip()
                self.last = time.time()
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            self.last = time.time()
            if exc.code == 404:
                return None
            die(f"{url}: HTTP {exc.code}")
        except (urllib.error.URLError, OSError) as exc:
            # No status code. This is the platform going quiet, not a page.
            self.last = time.time()
            if retry:
                note(f"{url}: no HTTP status ({exc}) — one slow retry, then "
                     f"the sweep stops. This is never a retry loop.")
                time.sleep(15)
                return self.get(path, referer=referer, retry=False)
            self.truncated = True
            note(f"{url}: no HTTP status on the retry either. The platform "
                 f"has stopped answering this host; what follows is "
                 f"INCOMPLETE.")
            return None


def inner(block, at):
    """Text of the element carrying data-at="<at>", nesting and icons removed."""
    m = re.search(r'<([a-zA-Z][\w-]*)\b[^>]*data-at="%s"[^>]*?(/?)>'
                  % re.escape(at), block)
    if not m or m.group(2) == "/":
        return None
    name, depth, end = m.group(1), 1, len(block)
    for t in TAG.finditer(block, m.end()):
        if t.group(2).lower() != name.lower():
            continue
        if t.group(3) == "/" or t.group(2).lower() in VOID:
            continue
        depth += -1 if t.group(1) else 1
        if depth == 0:
            end = t.start()
            break
    text = re.sub(r"<(style|svg)[^>]*>.*?</\1>", " ", block[m.end():end],
                  flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return html_mod.unescape(re.sub(r"\s+", " ", text)).strip() or None


def payload(page):
    """The list's own analytics blob: the totals, and how padded they are."""
    m = PAYLOAD.search(page or "")
    if not m:
        return {}
    try:
        d = json.loads(html_mod.unescape(m.group(1)))
    except ValueError:
        return {}
    ext = {}
    for part in (d.get("searchResultsJobCountByExtension") or "").split(","):
        k, _, v = part.partition(":")
        if v.isdigit():
            ext[k] = int(v)
    return {
        "total": d.get("searchResultsTotalJobCount"),
        "shown": d.get("searchResultsDisplayedJobCount"),
        "page": d.get("searchResultsDisplayedPageNumber"),
        "location": d.get("searchResultsLocationSearched"),
        "extension": ext,
    }


def slug(text):
    return urllib.parse.quote(re.sub(r"[^a-z0-9]+", "-",
                                     (text or "").lower()).strip("-"))


def list_path(site, keyword, location=None, page=1):
    s = SITES[site]
    path = s["seg"] + "/" + slug(keyword) if keyword else s["seg"]
    if location:
        path += "/in-" + slug(location)
    if page > 1:
        path += f"?page={page}"
    return path


def flatten(text):
    """Padded, folded text for whole-word containment tests.

    The folding itself now lives in `_locations.fold`, shared with every other
    adapter — this file had the only correct copy and keeping it private is
    how a rule becomes a habit in one script and a bug in ten (issue #65).
    The padding is local: it makes ` term ` match a whole word rather than a
    prefix.
    """
    return " " + fold(text) + " "


def classify(row, keyword, location):
    """Mark ONE card, from the card's own title and location.

    The payload counts the padding but does not say which card is which
    (`report_mix`), so this is the only per-row attribution available. It is a
    literal test and it is wrong in known ways — see stepstone.md, *Marking a
    card*: a Dutch title under an English search reads as padding, a keyword
    that lives in the description and not the title reads as padding, and a
    location field naming the region rather than the city reads as regional.
    Hence `semantic?` and `regional?` keep their question marks; only
    `literal` is asserted.
    """
    title = flatten(row.get("title"))
    where = flatten(row.get("location_text"))
    if location:
        # `matches_city` compares the first segment with diacritics folded, so
        # "Zürich, Zurich, CH" and "Zurich, Zurich, CH" — both live on one
        # page of results — do not land on opposite sides of the test.
        if not matches_city(row.get("location_text"), location) \
                and fold(location) not in where:
            return "regional?", ("the card's location does not contain "
                                 f"'{location}'")
    if keyword:
        terms = [t for t in flatten(keyword).split() if len(t) > 2] \
            or flatten(keyword).split()
        missing = [t for t in terms if f" {t} " not in title]
        if missing:
            return "semantic?", ("the title does not contain "
                                 + ", ".join(missing))
    return "literal", None


def card(site, ident, block):
    s = SITES[site]
    salary = inner(block, "job-item-salary-info")
    disclosed = bool(salary) and not UNDISCLOSED.search(salary) \
        and bool(re.search(r"\d", salary))
    return {
        "id": ident,
        "ledger_id": f"{site}:{ident}",
        # The slug in an ad URL is decorative: /job/x/y-job<id> answers 200 on
        # every UK/IE site, and --x--<id>-inline.html on every StepStone one.
        "url": f"https://{s['host']}" + s["ad"].format(id=ident),
        "site": site,
        "country": s["country"],
        "inventory": s["inventory"],
        "title": inner(block, "job-item-title"),
        "company": inner(block, "job-item-company-name"),
        "location_text": inner(block, "job-item-location"),
        # Absent from the card on all four StepStone domains — the element is
        # not rendered at all, which is not the same as an empty salary.
        "salary_text": salary,
        # False when the field is present and says "Not Disclosed",
        # "Competitive", "Negotiable" — a filled field meaning empty.
        "salary_disclosed": disclosed if salary is not None else None,
        "posted_text": inner(block, "job-item-timeago"),
        "work_from_home": 'data-at="job-item-work-from-home"' in block,
    }


def read_list(sess, site, keyword, location, page):
    path = list_path(site, keyword, location, page)
    body = sess.get(path, referer=list_path(site, keyword, location, 1)
                    if page > 1 else None)
    if body is None:
        return [], {}
    rows = []
    for i, b in CARD.findall(body):
        row = card(site, i, b)
        row["match"], row["match_reason"] = classify(row, keyword, location)
        rows.append(row)
    return rows, payload(body)


def report_mix(meta, where):
    ext = meta.get("extension") or {}
    total = ext.get("total") or meta.get("total")
    main = ext.get("main")
    if main is None or not total:
        return
    parts = ", ".join(f"{k} {v}" for k, v in ext.items() if k != "total")
    note(f"{where}: {total} reported — {parts}")
    if main < total:
        pct = 100 - main * 100 // total
        note(f"{where}: {pct}% of what this board reports is NOT a literal "
             f"match. `semantic` is the platform's own related-ads padding "
             f"and `regional` is outside the location asked for. The cards "
             f"do not say which is which — treat `main` ({main}) as the "
             f"answer and read the rest as suggestions.")


def cmd_count(a):
    sess = Session(a.site, a.delay)
    _, meta = read_list(sess, a.site, a.keyword, a.location, 1)
    if not meta:
        die("no analytics payload on the result list — either the search "
            "returned nothing or the markup moved. Re-verify stepstone.md.")
    report_mix(meta, a.site)
    print(json.dumps({
        "site": a.site,
        "country": SITES[a.site]["country"],
        "query": {"keyword": a.keyword, "location": a.location},
        "reported": meta.get("total"),
        "literal_matches": (meta.get("extension") or {}).get("main"),
        "extension": meta.get("extension"),
        "location_resolved": meta.get("location"),
    }, ensure_ascii=False))


def cmd_search(a):
    s = SITES[a.site]
    cap = a.pages if a.pages else (s["pages"] or 20)
    if s["pages"] and a.pages and a.pages > s["pages"]:
        die(f"{a.site} reopens {s['pages']} result page(s) to `*` in its own "
            f"robots.txt and no more. Narrow the search instead of asking for "
            f"page {a.pages}; see stepstone.md.")
    sess = Session(a.site, a.delay)
    seen, kept, meta = set(), 0, {}
    marks = collections.Counter()
    for page in range(1, cap + 1):
        rows, m = read_list(sess, a.site, a.keyword, a.location, page)
        if page == 1:
            meta = m
            report_mix(m, a.site)
        if not rows:
            note(f"page {page} returned no cards — stopping.")
            break
        for c in rows:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            marks[c["match"]] += 1
            print(json.dumps(c, ensure_ascii=False))
            kept += 1
            if a.limit and kept >= a.limit:
                break
        if a.limit and kept >= a.limit:
            break
    total = meta.get("total")
    ext = meta.get("extension") or {}
    main = ext.get("main")
    if kept == 0:
        note(zero_note("stepstone", what=a.keyword, where=a.location))
    note(f"{kept} ads returned from {a.site}; the board reported {total} "
         f"({main} literal).")
    note("marked per card: "
         + ", ".join(f"{k} {v}" for k, v in marks.most_common()))
    if kept and marks["literal"] < kept:
        note(f"{kept - marks['literal']} of the {kept} rows written are "
             f"flagged as padding rather than matches. The flag is a literal "
             f"test on the card's own title and location — see stepstone.md, "
             f"*Marking a card*, for the three ways it is wrong.")
    # The payload's own split is the control: when the per-card share drifts
    # far from what the site reports, the heuristic has, not the site.
    if kept and main is not None and total:
        site_share = main * 100 // total
        mine = marks["literal"] * 100 // kept
        if abs(site_share - mine) > 25:
            note(f"the per-card marking ({mine}% literal) and the site's own "
                 f"payload ({site_share}% main) disagree by more than 25 "
                 f"points. Trust the payload for the shape of the board and "
                 f"treat the per-card flags as suspect on this search — a "
                 f"keyword in another language does exactly this.")
    if sess.truncated:
        note("THE SWEEP IS INCOMPLETE — the platform stopped answering. "
             "Re-run later at a slower --delay rather than immediately.")


def cmd_ad(a):
    sess = Session(a.site, a.delay)
    s = SITES[a.site]
    # Warm the host: a cold ad request is the one that has been seen to fail
    # without a status code.
    sess.get(s["seg"] + "/")
    body = sess.get(s["ad"].format(id=a.id), referer=s["seg"] + "/")
    if body is None:
        die(f"{a.site}: ad {a.id} did not answer. A 404 here means the ad is "
            f"gone; no status at all means the platform went quiet.", 3)
    posting = None
    for m in LD.finditer(body):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            continue
        for o in (d if isinstance(d, list) else [d]):
            if isinstance(o, dict) and o.get("@type") == "JobPosting":
                posting = o
    if posting is None:
        die(f"{a.site}: ad {a.id} answered but carries no JobPosting JSON-LD. "
            f"That is the one thing every ad on this platform had on "
            f"2026-09-02 — re-verify stepstone.md before trusting the parse.",
            3)
    org = posting.get("hiringOrganization") or {}
    print(json.dumps({
        "id": a.id,
        "ledger_id": f"{a.site}:{a.id}",
        "url": f"https://{s['host']}" + s["ad"].format(id=a.id),
        "title": posting.get("title"),
        "company": org.get("name"),
        "description": posting.get("description"),
        "description_chars": len(posting.get("description") or ""),
        "posted": (posting.get("datePosted") or "")[:10] or None,
        # Present on 60 of 60 ads sampled across six sites — a real expiry,
        # which is more than most boards here carry.
        "expires": (posting.get("validThrough") or "")[:10] or None,
        "employment_type": posting.get("employmentType"),
        "direct_apply": posting.get("directApply"),
        "industry": posting.get("industry"),
        "location": posting.get("jobLocation"),
        # 11 of 12 on Totaljobs, 0 of 12 on Caterer, IrishJobs, NIJobs and all
        # four StepStone sites. On those, the card's salary is the only one.
        "base_salary": posting.get("baseSalary"),
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, h in (("count", cmd_count, "how many match, and how many of "
                                             "those are literal matches"),
                        ("search", cmd_search, "read the result cards"),
                        ("ad", cmd_ad, "read one ad by id")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--site", required=True,
                       choices=sorted(SITES) + sorted(NOT_A_BOARD))
        c.add_argument("--delay", type=float, default=2.0,
                       help="seconds between requests. The platform goes "
                            "silent under a burst — do not go below 2")
        if name == "ad":
            c.add_argument("--id", required=True)
        else:
            c.add_argument("--keyword")
            c.add_argument("--location",
                           help="a place name; it becomes an /in-<place> path "
                                "segment. Adds a `regional` extension to the "
                                "count — ads outside it, served anyway")
        if name == "search":
            c.add_argument("--limit", type=int)
            c.add_argument("--pages", type=int,
                           help="result pages to read. Capped per site by that "
                                "site's own robots.txt")
        c.set_defaults(func=fn)
    a = p.parse_args()
    if a.site in NOT_A_BOARD:
        die(NOT_A_BOARD[a.site])
    if a.cmd in ("count", "search") and not a.keyword and not a.location:
        die("give --keyword or --location. The bare result list is the whole "
            "board, and this platform pads a result list with ads that do not "
            "match the search.")
    a.func(a)


if __name__ == "__main__":
    main()
