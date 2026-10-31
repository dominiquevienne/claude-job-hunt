#!/usr/bin/env python3
"""Online Job Malawi (`onlinejobmw.com`) — and THE FILTER IS A CONDITION OF
CORRECTNESS, not an optimisation.

**ONE POST TYPE CARRIES FOUR TERMS, AND ONLY ONE OF THEM IS JOBS — #676.**
`/wp-json/wp/v2/job-category?per_page=100` returns four terms, each with its own
`count`, which is a witness that is not our extraction. Measured 2026-10-31:

    jobs      Job Vacancies            id 1   count  967
    NOT jobs  Education & Trainings     id 2   count  279
              Annoucements              id 3   count   13
              Tender & Consultancy      id 4   count   13
                                              sum   1 272

> **So an unfiltered walk of the post type emits 305 records that are not
> advertisements**, and the unfiltered page 1 was school-admission copy. *The
> sum 1 272 is NOT the board's size either: a record may carry several terms,
> and 967 + 279 + 13 + 13 double-counts whatever overlaps.* **This tool
> therefore asks the host to filter, and there is no switch to turn that off.**

**COINCIDENCE, MEASURED ON BOTH OBJECTS AND NOT EXPLAINED:** `ntchito.md`, the
other Malawi board in this repository, sums its FOURTEEN terms to **1 272** as
well. Two boards, two taxonomies of different sizes, the same total. *It is
written down because the next reader will notice it, and because a number that
looks copied should be shown to have been measured — the four counts above were
read from this host's own taxonomy on 2026-10-31.*

**THE TERM ID IS NEVER HARDCODED.** `job-category` is read first and the jobs
term is matched on its SLUG (`job_vacancies`). *Its id happens to be `1` on this
installation; a hardcoded 1 would silently mean something else the day a term is
re-created, and `1` is exactly the id a fresh install hands to whatever was
created first.* The names come back HTML-escaped — «Education &amp; Trainings» —
so they are unescaped before being compared or printed.

**THE REST COLLECTION IS AN ENUMERATOR AND NOT A SOURCE OF AD TEXT.** Measured
on the 100 records of the filtered page 1 (HTTP 200, 124 123 B, md5
`096dc56f303f`, 2026-10-31): the record carries `id`, `date`, `modified`,
`slug`, `link`, `title`, `job-category` and `_links` — **and no `content`, no
`excerpt` and no `meta` at all**. So the advertisement's body lives on its
server-rendered page under `/vacancies/<slug>/`, and `ad` reads that page rather
than pretending the API holds it.

**NO CONTACT IS EXPOSED ON THIS ROUTE, AND IT IS MEASURED RATHER THAN ASSUMED:**
0 e-mail addresses in the whole 124 123-byte payload, and the record has no
`meta` dictionary in which a `_application` or `_company_name` could hide.
**And because an empty withheld list is exactly what a board that ships a person
would produce if we were careless, `contacts_exposed` is DERIVED from the
record's own values at runtime** — the fields scanned are the record's, not a
list borrowed from another board. *Naming `meta._application` here would be
composing this board's shape out of `ntchito`'s, which is the error this file
exists to avoid elsewhere.*

**THE HOST RATE-LIMITS AND WRITES NO `Crawl-delay`.** HTTP 429, 41 B, «Rate
limit exceeded. Please retry later.» — the first one arrived on the 12th request
in 4 min 51 s on 2026-10-30. *A threshold is only ever learnt by crossing it,
and crossing it once gives one point and not a limit: nothing here says where it
is, so `PACE` below is a JUDGEMENT and declared as one.*

> **AND ONE PAGE COSTS THE HOST TWO REQUESTS, NOT ONE.** `fetch()` runs
> `bin/fetch-body.py` as a SUBPROCESS and that tool takes its own guard, while
> `_robots._CACHE` keys on `(host, _FETCH)` inside ONE process — so every page
> is a fresh `robots.txt` read plus a body. *The card for this board wrote «10
> pages … that is 10 requests»; it is **20**, and the card had derived the
> per-process scope of the cache in the same breath without applying it to its
> own estimate.* **A 429 STOPS the walk and is never re-probed** (§2 quater), so
> what is printed is what was read.

    onlinejobmw.py terms
    onlinejobmw.py list [--pages N] [--limit N]
    onlinejobmw.py ad --url https://onlinejobmw.com/vacancies/<slug>/
"""
import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _robots                                                  # noqa: E402

EXIT_BROKEN = 2
EXIT_REFUSED = 7
EXIT_PACED = 9        # the host rate-limited us; NOT a verdict on the board

HOST = "onlinejobmw.com"
API = f"https://{HOST}/wp-json/wp/v2"
PER_PAGE = 100
DEFAULT_PAGES = 2
PACE = 10.0       # no Crawl-delay is written, so the pace is OURS — and a page
                  # costs the host TWO requests, see the module docstring

# **The jobs term, by SLUG.** Matched against what `job-category` returns, so
# this installation's ids never enter the code. Measured 2026-10-31; a term the
# host adds later is NOT jobs until someone measures it and adds it here — the
# allow-list fails as a MISSING row, never as a false inclusion.
JOB_SLUGS = ("job_vacancies",)

# An address is the only third-party datum this route could carry, there being
# no `meta`. The motif is deliberately loose: its cost is a withheld field that
# did not need withholding, never a published address.
ADDRESS = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def die(msg, code=EXIT_BROKEN):
    print(f"[onlinejobmw] {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[onlinejobmw] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    v = _robots.allowed(parts.netloc, _robots.full_path(parts))
    if v.get("allowed") is False:
        die(f"refused by the rules of {parts.netloc}: {v.get('rule')!r}",
            EXIT_REFUSED)
    if v.get("allowed") is None:
        die(f"the rules of {parts.netloc} could not be read — INDETERMINATE, "
            f"and an indeterminate is not probed", EXIT_REFUSED)
    return v


def fetch(url, first=False):
    """The body, or `(None, error)`. A 429 is named as such by the caller.

    The pace is applied BEFORE every request but the first, because the first
    one of a run has nothing to be paced against.
    """
    import subprocess
    import tempfile
    gate(url)
    if not first:
        time.sleep(PACE)
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    tool = os.path.join(root, "bin", "fetch-body.py")
    fd, tmp = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        p = subprocess.run([sys.executable, tool, url, "-o", tmp],
                           capture_output=True, text=True)
        if p.returncode != 0:
            err = (p.stderr or p.stdout).strip()
            # the STATUS is read from the record the tool writes, never parsed
            # out of its prose — a message is a property of the run (#4 ter)
            status = None
            prov = tmp + ".provenance.json"
            if os.path.exists(prov):
                try:
                    with open(prov, encoding="utf-8") as fh:
                        status = json.load(fh).get("status")
                except ValueError:
                    status = None
            return None, {"status": status, "error": err[:300]}
        with open(tmp, encoding="utf-8", errors="replace") as fh:
            return fh.read(), None
    finally:
        for q in (tmp, tmp + ".provenance.json"):
            if os.path.exists(q):
                os.unlink(q)


def as_json(body, url):
    try:
        return json.loads(body)
    except ValueError as e:
        die(f"{url} did not parse as JSON: {e}")


def unescape(s):
    """The taxonomy returns HTML entities — «Education &amp; Trainings».

    *One string, several forms: comparing an escaped name against a plain one
    finds nothing and says «no such term», which is a statement about our
    comparison and not about the host.*
    """
    return html.unescape(s or "").strip()


def terms(first=False):
    url = f"{API}/job-category?per_page={PER_PAGE}"
    body, err = fetch(url, first=first)
    if body is None:
        if err.get("status") == 429:
            die(f"the host rate-limited the taxonomy read (HTTP 429). The walk "
                f"is STOPPED and not re-probed.", EXIT_PACED)
        die(f"{url}: {err.get('error')}")
    ts = as_json(body, url)
    if not isinstance(ts, list) or not ts:
        die(f"{url} returned no term — without the taxonomy there is no filter, "
            f"and without the filter this tool would emit non-advertisements")
    return [{"id": t.get("id"), "slug": t.get("slug"),
             "name": unescape(t.get("name")), "count": t.get("count")}
            for t in ts if isinstance(t, dict) and t.get("id")]


def split(ts):
    """(job ids, other ids, stated jobs, stated others) — by SLUG, never id."""
    jid = [t["id"] for t in ts if (t["slug"] or "").lower() in JOB_SLUGS]
    nid = [t["id"] for t in ts if t["id"] not in jid]
    jn = sum(t["count"] or 0 for t in ts if t["id"] in jid)
    nn = sum(t["count"] or 0 for t in ts if t["id"] in nid)
    return jid, nid, jn, nn


def contacts_of(rec):
    """**A POSITIVE statement about the route, DERIVED and not asserted.**

    The fields scanned are the RECORD's own, so the day this host starts
    serving a `content` or a `meta` holding an address, the row says so by
    itself. Measured 0 of 100 on 2026-10-31 — and an empty list is exactly what
    a careless tool would also produce, which is why `inspected` names what was
    actually looked at.
    """
    inspected, withheld = [], []
    for key, value in sorted(rec.items()):
        if key in ("_links", "class_list"):
            continue
        blob = value if isinstance(value, str) else json.dumps(
            value, ensure_ascii=False)
        inspected.append(key)
        if ADDRESS.search(blob):
            withheld.append(key)
    return {"third_party_inspected": inspected,
            "third_party_withheld": withheld}


def row(rec, by_id):
    ident = rec.get("id")
    if not ident:
        return None
    t = rec.get("title") or {}
    titre = re.sub(r"<[^>]+>", "", unescape(
        t.get("rendered") if isinstance(t, dict) else t or "")).strip()
    noms = [by_id.get(i, {}).get("name") for i in (rec.get("job-category") or [])]
    tp = contacts_of(rec)
    return {
        "source": "onlinejobmw",
        "country": "MW",
        "ledger_id": f"onlinejobmw:{ident}",
        "id": ident,
        "url": rec.get("link") or None,
        "title": titre or None,
        "posted": rec.get("date") or None,
        "modified": rec.get("modified") or None,
        "kinds": [n for n in noms if n],
        # **The API serves NO body for this post type** — measured, 100 of 100
        # carry neither `content` nor `excerpt` — so the text lives on the
        # advertisement's own page and this says so rather than emitting an
        # empty string that would read as «the advert has no description».
        "body_source": "page",
        "contacts_exposed": bool(tp["third_party_withheld"]),
        "withheld_fields": tp["third_party_withheld"],
        **tp,
    }


def cmd_terms(a):
    ts = terms(first=True)
    jid, nid, jn, nn = split(ts)
    for t in sorted(ts, key=lambda x: -(x["count"] or 0)):
        mark = "JOB " if t["id"] in jid else "    "
        print(f"{mark}{t['id']:4d}  {str(t['count']):>5s}  {t['slug']:24s} {t['name']}")
    print()
    note(f"the host states {jn} across its job term(s) and {nn} across the "
         f"rest; **their sum is NOT the board's size** because a record may "
         f"carry several terms, so {jn + nn} double-counts, and no total is "
         f"stated anywhere")
    if not jid:
        die(f"no term whose slug is one of {JOB_SLUGS} — the filter cannot be "
            f"built, and an unfiltered walk would emit non-advertisements")
    return 0


def cmd_list(a):
    ts = terms(first=True)
    by_id = {t["id"]: t for t in ts}
    jid, nid, jn, nn = split(ts)
    if not jid:
        die(f"no term whose slug is one of {JOB_SLUGS} — REFUSING to walk the "
            f"post type unfiltered: it carries {nn} records that are not "
            f"advertisements")
    note(f"taxonomy read: {len(ts)} terms, {len(jid)} of them jobs ({jn} "
         f"stated) against {len(nid)} others ({nn} stated)")
    sel = ",".join(str(i) for i in jid)
    seen, kept, foreign, end = set(), [], 0, "complete"
    cap = a.pages if a.pages is not None else DEFAULT_PAGES
    for page in range(1, cap + 1):
        url = (f"{API}/vacancies?job-category={sel}"
               f"&per_page={PER_PAGE}&page={page}")
        body, err = fetch(url)
        if body is None:
            if err.get("status") == 429:
                note("HTTP 429 — the host rate-limited us. THE WALK STOPS HERE "
                     "and is not re-probed; what is printed is what was read.")
                end = "paced"
            elif err.get("status") == 400:
                # WP answers 400 past the last page, which is how it states the
                # page count — a REFUSAL that is also a witness
                end = "complete"
            else:
                note(f"page {page}: {err.get('error')}")
                end = "transport"
            break
        recs = as_json(body, url)
        if not isinstance(recs, list) or not recs:
            end = "complete"
            break
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            ids = [i for i in (rec.get("job-category") or [])
                   if isinstance(i, int)]
            if ids and not any(i in jid for i in ids):
                # the host filtered server-side, so this should be empty; it is
                # counted rather than assumed, because a filter believed and
                # not checked is the whole defect this tool was written for
                foreign += 1
                continue
            r = row(rec, by_id)
            if not r or r["id"] in seen:
                continue
            seen.add(r["id"])
            kept.append(r)
            print(json.dumps(r, ensure_ascii=False, sort_keys=True), flush=True)
            if a.limit and len(kept) >= a.limit:
                note(f"stopped at --limit {a.limit} — BOUNDED, not compared")
                end = "capped"
                break
        if end == "capped":
            break
        if len(recs) < PER_PAGE:
            end = "complete"
            break
        if a.pages is None and page >= DEFAULT_PAGES:
            end = "capped"
            break
    note(f"{len(kept)} emitted; {foreign} record(s) the host returned that do "
         f"NOT carry a job term (expected 0: the filter is server-side)")
    note(f"the host states {jn} for its job term(s). Ours is "
         f"{'a walk of all pages the API served' if end == 'complete' else 'a BOUNDED slice'}"
         f", and the board's size is the HOST's figure, never this count.")
    note({"complete": "ended of itself — the API ran out of pages",
          "capped": "CAPPED by this invocation, not by the board",
          "paced": "STOPPED BY THE HOST's rate limit — not a verdict on the board",
          "transport": "CUT BY THE TRANSPORT — what is printed is what was read"
          }[end])
    return 0 if kept else (EXIT_PACED if end == "paced" else EXIT_BROKEN)


def cmd_ad(a):
    m = re.search(r"/vacancies/([^/?#]+)", urllib.parse.urlsplit(a.url).path)
    if not m:
        die(f"{a.url}: not an Online Job Malawi advert address "
            f"(https://{HOST}/vacancies/<slug>/)")
    slug = urllib.parse.quote(m.group(1))
    body, err = fetch(f"{API}/vacancies?slug={slug}", first=True)
    if body is None:
        if err.get("status") == 429:
            die("HTTP 429 — rate-limited; not re-probed", EXIT_PACED)
        die(f"{a.url}: {err.get('error')}")
    recs = as_json(body, a.url)
    if not recs:
        note("the API returned no record for that slug — this tool reports "
             "what it did not find, and makes no claim about whether the "
             "advertisement is gone")
        return EXIT_BROKEN
    ts = terms()
    print(json.dumps(row(recs[0], {t["id"]: t for t in ts}),
                     ensure_ascii=False, sort_keys=True))
    note("the API serves no body for this post type: the advertisement's text "
         f"is on {recs[0].get('link')} and this row says so in `body_source`")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("terms", help="the host's taxonomy and its own counts")
    l = sub.add_parser("list", help="the advertisements, FILTERED — always")
    l.add_argument("--pages", type=int, default=None,
                   help=f"pages of {PER_PAGE} (default {DEFAULT_PAGES}, "
                        f"bounded and said so). Each page costs the host TWO "
                        f"requests, see the module docstring.")
    l.add_argument("--limit", type=int, default=0, help="stop after N rows")
    d = sub.add_parser("ad", help="one advertisement by its URL")
    d.add_argument("--url", required=True)
    a = p.parse_args()
    return {"terms": cmd_terms, "list": cmd_list, "ad": cmd_ad}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
