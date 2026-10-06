#!/usr/bin/env python3
"""JobToday (`jobtoday.com`) — hourly and shift work in Spain, the UK and the US.

**EVERY ADVERT NAMES A PERSON, AND NO CONTACT-SHAPED RULE CAN SEE IT — #1005.**
Each record carries `company.hiringManager` with `name`, `image` and
`lastOnline`, and `addressInfo` with `coordinates` and `ghash`. Measured on the
Madrid facet on 2026-10-06: **48 of 48 on all five**. The same payload holds
**no contact address and not one key matching phone, email or tel**.

> So a redaction rule written around the FORMS of contact — an `@`, a run of
> digits — finds nothing here and would record *«nothing withheld»* on a board
> that ships a named individual, their photograph and the time they were last
> online. **It is the mirror of claiming a withholding nobody deposited, and it
> is the worse half: the dishonest output is the SILENT one.**

**AND THE PATTERN FAILS IN BOTH DIRECTIONS AT ONCE, measured here:** a plain
e-mail regex over this page returns **seven** matches and **not one is a
contact** — a Sentry DSN, an obfuscated token, and the filename
`share-pict-1200x630@2x.jpg`. *It invents matches where there is nothing and
misses the person who is actually there.* **So the expurgation is named by
FIELD, never by pattern**, and a field whose meaning we cannot state is withheld
rather than passed through.

**What is kept and what is dropped was decided by the owner on 2026-10-06
(#1007), and is not ours to revisit:**

    company.hiringManager.name        KEEP   a cover letter may address someone
    company.hiringManager.image       DROP
    company.hiringManager.lastOnline  DROP   presence history, never a contact
    addressInfo.coordinates / ghash   DROP   the town is carried instead
    addressInfo.display / itemId      DROP   measured, not in the issue: a
                                             STREET address, and the ghash again

*`lastOnline` is the hour a named recruiter was last connected. It is not a way
to reach them; it would sit in the candidate's ledger for the life of the row
without ever being used.*

**THE DECLARATION FOLLOWS THE RECORD, NEVER THE BOARD.** `withheld_fields` names
only what this record actually carried — a record without `ghash` declares no
`ghash` — because naming what was never there lies about our own discretion
instead of about the host.

**THE SALARY IS STRUCTURED AND THE BOARD FLAGS ITS OWN VALIDITY.** `isValid` is
honoured and costs nothing: the invalid ones carry no amount at all. *Measured
2026-10-06 on Madrid: present on 24 of 48, valid on 21, periods MONTHLY 19 and
YEARLY 2 — against 28 / 26 and MONTHLY 14 / YEARLY 9 / HOURLY 3 the day before,
on a board whose freshest advert was 73 seconds old. The rates are a reading,
not a property.* **A figure without its period means nothing, so the two travel
together or neither does.**

**THE BOARD ANNOUNCES NO TOTAL.** No integer exists in the payload;
`pagination.pages` has 20 entries and the title says «1000+ ofertas» — a FLOOR.
So about 960 adverts are reachable per facet, **the scope is PER FACET, and the
size of the board is not established**. This tool says so rather than emitting
its own count as an inventory.

**AND THE DECLARED SITEMAP CONTAINS NO ADVERT, twice over** — `/sitemap.xml` is
478 blog posts, and the `Positions` index's four Spanish children are 168 854
distinct three-segment facet URLs carrying no identifier, a cross product of
6 714 categories by 1 306 cities. *Never present 168 854 as a count of adverts.*
This tool therefore does not walk a sitemap at all.

**TWO STRUCTURAL TRAPS, both met while writing this:**
  * the job items are ENVELOPES — `{"type": "job", "payload": {...}}` — so the
    advert's own keys are one level down;
  * `pagination` sits at `props.pageProps.pagination`, **not** under `feed`.
  * and the section is chosen by the TYPE of its items, never by its index: on
    2026-10-06 sections 0 and 1 were empty and the jobs were in section 2, which
    is a fact about that page and not about the host.

    jobtoday.py hosts
    jobtoday.py list --city madrid [--country es] [--pages N] [--limit N]
    jobtoday.py ad   --url https://jobtoday.com/es/trabajo/<role>-<key>
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
# **7, not 3 — the suite enforces one meaning per code across every adapter.**
# `AnExitCodeMeansTheSameThingInEveryAdapter` caught a 3 here, which is
# `EXIT_GONE` elsewhere: a caller reading the code would have been told an
# advert had disappeared where the rules had refused us.
EXIT_REFUSED = 7

HOSTS = ("jobtoday.com", "www.jobtoday.com")
COUNTRIES = {"es": "trabajos", "gb": "jobs", "us": "jobs"}
NEXT_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
DEFAULT_PAGES = 3
PACE = 2.0          # no Crawl-delay is written, so the pace is ours — #1005

# **Named fields, not patterns.** The value side is never emitted; the NAME is,
# so the output says what was withheld instead of staying silent about it.
DROP = (
    ("company", "hiringManager", "image"),
    ("company", "hiringManager", "lastOnline"),
    ("addressInfo", "coordinates"),
    ("addressInfo", "ghash"),
    # **TWO MORE THAN THE ISSUE NAMED, AND FOUND BY MEASURING RATHER THAN BY
    # READING IT.** #1005 lists `coordinates` and `ghash`. On 2026-10-06 the
    # payload also carries, on 48 of 48:
    #   * `addressInfo.display.fullName` — a STREET ADDRESS: «36 Avenida de
    #     Monforte de Lemos, Fuencarral-El Pardo, 28029, Madrid, MD, España».
    #     *More precise than the pair of floats the issue did name.*
    #   * `addressInfo.itemId` — equal to `ghash` on every record measured
    #     (both `539940`): the same geohash under a second name.
    # The owner's rule decides both without a new question: a field whose
    # meaning we cannot state is withheld, and the town is carried instead of
    # the point. *An issue names the specimen; the class is measured.*
    ("addressInfo", "display"),
    ("addressInfo", "itemId"),
)


def die(msg, code=EXIT_BROKEN):
    print(f"[jobtoday] {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobtoday] {msg}", file=sys.stderr)


def facet_url(host, country, city, page=1):
    seg = COUNTRIES[country]
    base = f"https://{host}/{country}/{seg}/{urllib.parse.quote(city)}"
    return base if page <= 1 else f"{base}?page={page}"


def gate(url):
    """The rules, on the EXACT path — `_robots` answers for the host that replied."""
    parts = urllib.parse.urlsplit(url)
    v = _robots.allowed(parts.netloc, parts.path or "/")
    if v.get("allowed") is False:
        die(f"refused by the rules of {parts.netloc}: {v.get('rule')!r} "
            f"(group {v.get('group')!r})", EXIT_REFUSED)
    if v.get("allowed") is None:
        die(f"the rules of {parts.netloc} could not be read — INDETERMINATE, "
            f"and an indeterminate is not probed", EXIT_REFUSED)
    return v


def fetch(url):
    """One retrieval through the repository's fetcher, which declares us."""
    import subprocess
    import tempfile
    gate(url)
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    tool = os.path.join(root, "bin", "fetch-body.py")
    fd, tmp = tempfile.mkstemp(suffix=".html")
    os.close(fd)
    try:
        p = subprocess.run([sys.executable, tool, url, "-o", tmp],
                           capture_output=True, text=True)
        if p.returncode != 0:
            return None, (p.stderr or p.stdout).strip()[:300]
        with open(tmp, encoding="utf-8", errors="replace") as fh:
            return fh.read(), None
    finally:
        for p2 in (tmp, tmp + ".json"):
            if os.path.exists(p2):
                os.unlink(p2)


def next_data(body, url):
    m = NEXT_RE.search(body or "")
    if not m:
        die(f"no `__NEXT_DATA__` script found at {url} — this tool did not find "
            f"the payload it expects; that is a statement about our pattern, "
            f"not about what the host serves")
    try:
        return json.loads(m.group(1))
    except ValueError as e:
        die(f"`__NEXT_DATA__` at {url} did not parse: {e}")


def jobs_of(data):
    """The job payloads, selected by the TYPE of the items and never by index.

    The items are envelopes: `{"type": "job", "payload": {...}}`. Choosing
    `sections[2]` would have worked on 2026-10-06 and says nothing about
    tomorrow — two of the three sections were empty that day.
    """
    props = ((data.get("props") or {}).get("pageProps") or {})
    secs = ((props.get("feed") or {}).get("sections") or [])
    out = []
    for s in secs:
        for it in (s.get("items") or []):
            if isinstance(it, dict) and it.get("type") == "job" \
                    and isinstance(it.get("payload"), dict):
                out.append(it["payload"])
    return out, props


def pages_declared(props):
    """`pagination.pages` — at `pageProps`, NOT under `feed`. A list of page
    descriptors, so its LENGTH is the reach; it is not a count of adverts."""
    pg = props.get("pagination") or {}
    pages = pg.get("pages")
    return len(pages) if isinstance(pages, list) else None


def withheld_of(job):
    """The names of the fields THIS record carried and we did not emit.

    **Now a call into the shared mechanism — `shared/third-party-fields.md`,
    #1007.** It used to be a local walk with a deny-list of empties, and it
    was right on this board; what it could not do is make an EMPTY result
    readable. *The tri-state does: what was LOOKED FOR travels beside what was
    dropped, so «we looked and the board sent nothing» stops being
    indistinguishable from «our rule looked for the wrong thing».*
    """
    return _provenance.third_party(job, [".".join(p) for p in DROP])


def salary_of(job):
    """Honour `isValid`, and carry the period WITH the figures or neither.

    The board flags its own validity and the invalid records carry no amount at
    all, which is what makes honouring the flag cost nothing.
    """
    s = job.get("salary")
    if not isinstance(s, dict) or not s.get("isValid"):
        return None
    lo, hi, per = s.get("from"), s.get("to"), s.get("period")
    if lo is None and hi is None:
        return None
    if not per:
        return None            # a figure without its period means nothing
    return {"from": lo, "to": hi, "period": per,
            "currency": s.get("currencyCode")}


def row(job, host, country):
    key = job.get("key")
    if not key:
        return None
    path = job.get("canonicalUrl") or ""
    url = urllib.parse.urljoin(f"https://{host}/", path) if path else None
    addr = job.get("addressInfo") or {}
    co = job.get("company") or {}
    hm = co.get("hiringManager") if isinstance(co.get("hiringManager"), dict) else {}
    tp = withheld_of(job)
    return {
        "source": "jobtoday",
        "country": country.upper(),
        "ledger_id": f"jobtoday:{key}",
        "id": key,
        "url": url,
        "title": job.get("role") or None,
        "employer": job.get("companyName") or None,
        # **THE TOWN, NEVER THE POINT — #1007 — and `addressInfo` carries no
        # town at all.** Its keys are `countryCode`, `ghash`, `itemId`,
        # `coordinates`, `display` and `type`: no `city`, no `region`, no
        # `town`. A first version of this row read `addr["city"]` and emitted
        # **null on 48 of 48** — *a field empty everywhere is a reading defect
        # until proven otherwise, and it was.* The town-level string is the
        # advert's own `address`: «Fuencarral-El Pardo, Madrid, Comunidad de
        # Madrid, España» — district, city, region, country, and NO street.
        "address_text": job.get("address") or None,
        "country_code": (addr.get("countryCode") or "").upper() or None,
        # KEPT by the owner's decision: a cover letter may address someone
        "hiring_manager_name": hm.get("name") or None,
        "salary": salary_of(job),
        "employment_type": job.get("employmentType") or None,
        "experience_not_required": job.get("experienceNotRequired"),
        "immediate_start": job.get("immediateStart"),
        "posted_seconds_ago": job.get("postedSecondsAgo"),
        "create_date": job.get("createDate") or None,
        # **The tri-state, not a bare list — #1007.** `withheld_fields` stays
        # for the readers that already use it; `third_party_*` is what makes an
        # empty one mean something.
        "withheld_fields": tp["third_party_withheld"],
        **tp,
    }


def cmd_hosts(a):
    for h in HOSTS:
        v = _robots.allowed(h, "/")
        print(f"{h}\tallowed={v.get('allowed')}\tstate={v.get('state')}\t"
              f"certain={v.get('certain')}")
    return 0


def cmd_list(a):
    country = a.country.lower()
    if country not in COUNTRIES:
        die(f"country {country!r} is not one of {sorted(COUNTRIES)}")
    host = HOSTS[0]
    seen, rows, declared = set(), [], None
    cap = a.pages if a.pages is not None else DEFAULT_PAGES
    end = "complete"
    for page in range(1, cap + 1):
        url = facet_url(host, country, a.city, page)
        body, err = fetch(url)
        if body is None:
            note(f"page {page}: {err}")
            end = "transport"
            break
        data = next_data(body, url)
        jobs, props = jobs_of(data)
        if declared is None:
            declared = pages_declared(props)
        if not jobs:
            note(f"page {page}: no record of type «job» at the expected path")
            end = "complete"
            break
        fresh = 0
        for j in jobs:
            r = row(j, host, country)
            if not r or r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
            fresh += 1
            print(json.dumps(r, ensure_ascii=False, sort_keys=True), flush=True)
            if a.limit and len(rows) >= a.limit:
                note(f"stopped at --limit {a.limit} — BOUNDED, not compared")
                end = "capped"
                break
        if end == "capped":
            break
        if a.pages is None and page >= DEFAULT_PAGES:
            end = "capped"
            break
    kept = sum(len(r["withheld_fields"]) > 0 for r in rows)
    note(f"{len(rows)} advert(s) emitted from facet «{a.city}» ({country}); "
         f"{kept} of them declared withheld fields")
    # **No total exists, and the tool says so instead of implying an inventory.**
    note(f"the board states NO total: `pagination.pages` lists "
         f"{declared if declared is not None else 'an unread number of'} pages "
         f"and the page title gives a FLOOR («1000+»), so the reach is about "
         f"{(declared or 0) * 48} per facet and THE SIZE OF THIS BOARD IS NOT "
         f"ESTABLISHED. The scope of this run is ONE facet.")
    note({"complete": "ended of itself — the facet ran out",
          "capped": "CAPPED by this invocation, not by the board",
          "transport": "CUT BY THE TRANSPORT — what is printed is what was read"}[end])
    return 0 if rows else EXIT_BROKEN


def cmd_ad(a):
    body, err = fetch(a.url)
    if body is None:
        die(f"{a.url}: {err}", EXIT_BROKEN)
    data = next_data(body, a.url)
    jobs, _props = jobs_of(data)
    parts = urllib.parse.urlsplit(a.url)
    country = (parts.path.lstrip("/").split("/") or ["es"])[0]
    if not jobs:
        note("the advert page carries no record of type «job» at the expected "
             "path — this tool reports what it did not find, and makes no claim "
             "about whether the advert is gone")
        return EXIT_BROKEN
    r = row(jobs[0], parts.netloc or HOSTS[0],
            country if country in COUNTRIES else "es")
    print(json.dumps(r, ensure_ascii=False, sort_keys=True))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("hosts", help="the host forms and what their rules say")
    l = sub.add_parser("list", help="one facet page at a time")
    l.add_argument("--city", required=True, help="e.g. madrid")
    l.add_argument("--country", default="es", help=f"one of {sorted(COUNTRIES)}")
    l.add_argument("--pages", type=int, default=None,
                   help=f"pages to read (default {DEFAULT_PAGES}, bounded and said so)")
    l.add_argument("--limit", type=int, default=0, help="stop after N rows")
    d = sub.add_parser("ad", help="one advert")
    d.add_argument("--url", required=True)
    a = p.parse_args()
    return {"hosts": cmd_hosts, "list": cmd_list, "ad": cmd_ad}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
