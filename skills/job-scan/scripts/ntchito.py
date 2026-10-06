#!/usr/bin/env python3
"""Ntchito Malawi (`ntchito.com`) — and MOST OF THIS BOARD IS NOT JOBS.

**THE SEPARATION IS THE HOST'S OWN TAXONOMY, NOT A CLASSIFICATION WE INVENT —
#674.** `/wp-json/wp/v2/job-types` returns 14 terms each carrying its own
`count`, which is a witness that is not our extraction. Measured 2026-10-06:

    jobs      Internationally Recruited 314, Job Vacancy in Malawi 202,
              Internship 12, VISA Sponsorship Job 4                  ~532
    NOT jobs  Tender 192, Grants 165+111+60, Trainings & Fellowships 79,
              PhD & Postdoc 53, Consultancy 42, Opportunity 28,
              Scholarships 10                                        ~740

> **Everything is filed under one post type, `job_listing`.** *So emitting the
> post type as «jobs» would inflate the count by more than half, and the first
> page by date was entirely grants and fellowships.* **This tool therefore
> classifies by the TERM NAME resolved at runtime, and defaults to jobs only.**

**THE IDS ARE NEVER HARDCODED.** They are this installation's, not the
plugin's: `job-types` is read first and the names are matched. *A hardcoded 63
would silently mean something else the day a term is re-created.*

**AND NEITHER `/jobs/` NOR `/jobs-in-malawi/` IS A LIST** — #674's premise.
Each answers 200 with exactly ONE `<article>`, the page's own prose, no
`JobPosting` in its JSON-LD; `/jobs/` names itself `wp-json/wp/v2/pages/96`,
a PAGE, and its listing sits behind a JavaScript chooser. *Counting a keyword
there measured the INTERFACE: five «Showing/results» were menu toggles, a
select's `data-no_results_text`, and a noscript notice.*

**NO CONTACT IS EXPOSED ON THIS ROUTE, AND THAT IS MEASURED RATHER THAN
ASSUMED:** `_application`, `_company_name` and `_job_location` were empty on
5 of 5 and the payload held no e-mail address at all. **So `withheld_fields`
is legitimately EMPTY here — and because an empty list is exactly what a
board that ships a person would also produce if we were careless, each row
carries `contacts_exposed` as a POSITIVE statement about the route.** *That is
the JobToday lesson (#1005) taken from the other end: there the silence was
the lie; here the silence is true and says so.*

**THE AVAILABILITY SURFACE IS THE LISTING** — `_filled`, a per-record flag on
the API itself, which is the `closure: listing` shape of #1003. A record
marked filled is emitted with `filled: True` rather than dropped, because
dropping it would make a closed advert indistinguishable from one that never
existed.

**THE BOARD STATES NO TOTAL, AND THE SUM OF THE TERM COUNTS IS NOT ONE.** A
record carries several terms — one read showed three — so the sum of 1 272
double-counts. *This tool prints the host's per-term counts beside its own
emission and says the size is not established.*

    ntchito.py types
    ntchito.py list [--kind jobs|all] [--pages N] [--limit N]
    ntchito.py ad --url https://ntchito.com/job/<slug>/
"""
import argparse
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _robots                                                  # noqa: E402
import _provenance                                              # noqa: E402

EXIT_BROKEN = 2
EXIT_REFUSED = 7

HOST = "ntchito.com"
API = f"https://{HOST}/wp-json/wp/v2"
PER_PAGE = 100
DEFAULT_PAGES = 2
PACE = 2.0        # no Crawl-delay is written, so the pace is ours

# **The job terms, by NAME.** Matched case-insensitively against what
# `job-types` returns, so this installation's ids never enter the code.
# Measured 2026-10-06; a term the host adds later is NOT a job until someone
# measures it and adds it here — the allow-list fails as a MISSING row, never
# as a false inclusion.
JOB_TERMS = ("job vacancy in malawi", "internationally recruited",
             "internship", "visa sponsorship job")

# **The third-party fields this board MIGHT carry, inspected by NAME — #1007.**
# Measured 2026-10-06: all three empty on 5 of 5, and no address anywhere in the
# payload. *So the withheld list is legitimately empty here — and that is exactly
# why the names are declared: the tri-state puts them under `absent` with
# `inspected` non-empty, instead of leaving an empty list to be read either way.*
# **On JobToday the silence would have been the lie; here it is true and says so.**
# **AND `_job_location` IS NOT ONE OF THEM — my own list was wrong and the
# mechanism said so.** I put it here on a 5-record sample where it was empty on
# 5 of 5, and the tri-state then reported `contacts_exposed: True` on a real
# record. Measured properly on 20: **filled on 17**, holding TOWN names —
# «Lilongwe», «Blantyre & Lilongwe». *It is the workplace's town, which the
# doctrine KEEPS, not a third party's datum; withholding it was over-withholding
# and the false claim was mine, not the board's.*
#
# **The five-record sample was also biased, not merely small: those five were
# all grants, and grants carry no workplace.** A rate taken from the first page
# by date measured the kind of record, not the field.
INSPECT = ("meta._application", "meta._company_name",
           "meta._company_website", "meta._company_twitter")


def die(msg, code=EXIT_BROKEN):
    print(f"[ntchito] {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[ntchito] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    v = _robots.allowed(parts.netloc, parts.path or "/")
    if v.get("allowed") is False:
        die(f"refused by the rules of {parts.netloc}: {v.get('rule')!r}",
            EXIT_REFUSED)
    if v.get("allowed") is None:
        die(f"the rules of {parts.netloc} could not be read — INDETERMINATE, "
            f"and an indeterminate is not probed", EXIT_REFUSED)
    return v


def fetch(url):
    import subprocess
    import tempfile
    gate(url)
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    tool = os.path.join(root, "bin", "fetch-body.py")
    fd, tmp = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        p = subprocess.run([sys.executable, tool, url, "-o", tmp],
                           capture_output=True, text=True)
        if p.returncode != 0:
            return None, (p.stderr or p.stdout).strip()[:300]
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
    """The taxonomy returns HTML entities — «Grants for NGOs &amp; Institutions».

    *One string, several forms: comparing the escaped name against a plain one
    finds nothing and says «no such term», which is a statement about our
    comparison and not about the host.*
    """
    import html
    return html.unescape(s or "").strip()


def terms():
    """This installation's `job-types`, with the host's OWN counts."""
    body, err = fetch(f"{API}/job-types?per_page={PER_PAGE}")
    if body is None:
        die(f"job-types: {err}")
    out = []
    for t in as_json(body, "job-types"):
        if isinstance(t, dict) and t.get("id"):
            out.append({"id": t["id"], "name": unescape(t.get("name")),
                        "count": t.get("count")})
    if not out:
        die("job-types returned no term — this tool cannot classify without "
            "the host's taxonomy, and it will not guess")
    return out


def split(ts):
    """(job ids, non-job ids, and the counts the HOST states for each side)."""
    jid, nid, jn, nn = set(), set(), 0, 0
    for t in ts:
        if t["name"].lower() in JOB_TERMS:
            jid.add(t["id"]); jn += (t["count"] or 0)
        else:
            nid.add(t["id"]); nn += (t["count"] or 0)
    return jid, nid, jn, nn


def kinds_of(rec, jid, nid):
    """What the record's own terms say it is. A record may carry several."""
    ids = [i for i in (rec.get("job-types") or []) if isinstance(i, int)]
    return ([i for i in ids if i in jid], [i for i in ids if i in nid])


def row(rec, ts_by_id):
    ident = rec.get("id")
    if not ident:
        return None
    t = rec.get("title") or {}
    titre = re.sub(r"<[^>]+>", "", unescape(
        t.get("rendered") if isinstance(t, dict) else t or "")).strip()
    meta = rec.get("meta") or {}
    noms = [ts_by_id.get(i, {}).get("name") for i in (rec.get("job-types") or [])]
    sal = (meta.get("_job_salary") or "").strip() or None
    tp = _provenance.third_party(rec, INSPECT)
    return {
        "source": "ntchito",
        "country": "MW",
        "ledger_id": f"ntchito:{ident}",
        "id": ident,
        "url": rec.get("link") or None,
        "title": titre or None,
        "posted": rec.get("date") or None,
        "modified": rec.get("modified") or None,
        "kinds": [n for n in noms if n],
        # `_filled` is the LISTING's availability flag — the closure surface
        # of #1003. Emitted, never used to drop the row.
        "filled": str(meta.get("_filled") or "0") not in ("", "0"),
        # free text, and on this board it is sometimes a GRANT amount — so it
        # travels as the host's own string and is never read as a salary
        "amount_text": sal,
        # the TOWN, which the doctrine keeps — measured filled on 17 of 20
        "location_text": (meta.get("_job_location") or "").strip() or None,
        # **A POSITIVE statement about the route, DERIVED and not asserted.**
        # It used to be a hardcoded `False` — true on this board and a claim
        # nothing checked. Now it follows the tri-state of #1007, so the day
        # this host starts filling `_application` the row says so by itself.
        "contacts_exposed": bool(tp["third_party_withheld"]),
        "withheld_fields": tp["third_party_withheld"],
        **tp,
    }


def cmd_types(a):
    ts = terms()
    jid, nid, jn, nn = split(ts)
    for t in sorted(ts, key=lambda x: -(x["count"] or 0)):
        mark = "JOB " if t["id"] in jid else "    "
        print(f"{mark}{t['id']:6d}  {str(t['count']):>5s}  {t['name']}")
    print()
    note(f"the host states {jn} across the job terms and {nn} across the rest; "
         f"**their sum is NOT the board's size** because a record carries "
         f"several terms, so {jn + nn} double-counts and no total is stated.")
    return 0


def cmd_list(a):
    ts = terms()
    by_id = {t["id"]: t for t in ts}
    jid, nid, jn, nn = split(ts)
    note(f"taxonomy read: {len(ts)} terms, {len(jid)} of them job terms "
         f"({jn} stated) against {len(nid)} others ({nn} stated)")
    seen, kept, skipped, end = set(), [], 0, "complete"
    cap = a.pages if a.pages is not None else DEFAULT_PAGES
    for page in range(1, cap + 1):
        url = f"{API}/job-listings?per_page={PER_PAGE}&page={page}"
        body, err = fetch(url)
        if body is None:
            note(f"page {page}: {err}")
            end = "transport"
            break
        recs = as_json(body, url)
        if not isinstance(recs, list) or not recs:
            end = "complete"
            break
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            j, n = kinds_of(rec, jid, nid)
            if a.kind == "jobs" and not j:
                skipped += 1
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
    note(f"{len(kept)} emitted; {skipped} record(s) skipped as NOT jobs by the "
         f"host's own taxonomy (tenders, grants, fellowships, consultancies)")
    note(f"the host states {jn} across its job terms — ours is a walk of "
         f"{'all pages read' if end == 'complete' else 'a BOUNDED slice'}, and "
         f"THE SIZE OF THIS BOARD IS NOT ESTABLISHED (no total is stated, and "
         f"the term counts double-count multi-term records)")
    note({"complete": "ended of itself — the API ran out of pages",
          "capped": "CAPPED by this invocation, not by the board",
          "transport": "CUT BY THE TRANSPORT — what is printed is what was read"
          }[end])
    return 0 if kept else EXIT_BROKEN


def cmd_ad(a):
    m = re.search(r"/job/([^/?#]+)", urllib.parse.urlsplit(a.url).path)
    if not m:
        die(f"{a.url}: not a Ntchito advert address (https://{HOST}/job/<slug>/)")
    body, err = fetch(f"{API}/job-listings?slug={urllib.parse.quote(m.group(1))}")
    if body is None:
        die(f"{a.url}: {err}")
    recs = as_json(body, a.url)
    if not recs:
        note("the API returned no record for that slug — this tool reports what "
             "it did not find, and makes no claim about whether the advert is gone")
        return EXIT_BROKEN
    print(json.dumps(row(recs[0], {t["id"]: t for t in terms()}),
                     ensure_ascii=False, sort_keys=True))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("types", help="the host's taxonomy and its own counts")
    l = sub.add_parser("list", help="the adverts, jobs only by default")
    l.add_argument("--kind", choices=("jobs", "all"), default="jobs",
                   help="jobs (default) emits only records the HOST's taxonomy "
                        "calls jobs; all emits every record and names its kinds")
    l.add_argument("--pages", type=int, default=None,
                   help=f"pages of {PER_PAGE} (default {DEFAULT_PAGES}, bounded "
                        f"and said so)")
    l.add_argument("--limit", type=int, default=0, help="stop after N rows")
    d = sub.add_parser("ad", help="one advert by its URL")
    d.add_argument("--url", required=True)
    a = p.parse_args()
    return {"types": cmd_types, "list": cmd_list, "ad": cmd_ad}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
