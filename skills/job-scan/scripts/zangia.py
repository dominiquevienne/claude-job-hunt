#!/usr/bin/env python3
"""Zangia (`www.zangia.mn`, Mongolia): the country's generalist — `/job/list` is a Next.js SHELL, and the adverts come from the JSON its own bundle calls, `https://new-api.zangia.mn/api/jobs/search`, ninety a page with the board's own `meta.total` beside them; **the recruiter's telephone rides in every list row and is never emitted** (84 rows of 90 carried one on 2026-09-23). Issue #660.

  zangia.py jobs [--pages N | --all] [--type T] [--query Q] [--from FILE]
  zangia.py ad --url https://www.zangia.mn/job/_<code>
  zangia.py types
  zangia.py levels

THE SECOND WITNESS IS A PARTITION. The walk's own witness is the `meta.total`
the same answer carries, and a total that agrees with itself is not a check.
`levels` asks a different question ten times — how many adverts at each of the
board's own job levels — and on 2026-09-23 the ten came to **7 945 against the
7 945 stated**: every advert has exactly one level, and the total agrees with a
decomposition computed apart from it.

THE SHELL SAYS NOTHING AND THE BUNDLE SAYS EVERYTHING. `/job/list` answers 200
at 47 512 bytes of Next.js App Router markup: no card, no count, and an RSC
payload that carries neither. The page PRECONNECTS to `cdn.zangia.mn` and
`lib.zangia.mn` — and the data host is NEITHER of them: the fifty-four
`_next/static` chunks carry `axios` with `baseURL:"https://new-api.zangia.mn/api"`,
and the list component calls `GET /jobs/search`. *A preconnect names a host the
page will open early; it does not name the host that answers the question.*

**A 404 ON A CHUNK IS A STALE HASH, NOT A REFUSAL.** The route chunk named by
a copy taken 2026-09-22 17:07 UTC — `page-3b033792772fb37e.js` — answered
**404** on 2026-09-23, with and without its parentheses percent-encoded; the
page read a minute later named `page-c18b61710934368a.js`, which answered 200.
*The site had redeployed between the two reads.* A bundle is addressed by a
content hash, so yesterday's copy of the shell points at addresses that no
longer exist, and the 404 it earns reads exactly like a host that has closed.
**Re-read the shell in the same session as the chunk.**

THE RULES (read 2026-09-23 16:1x UTC): both `www.zangia.mn` and
`new-api.zangia.mn` answer **404 on `/robots.txt`** — no file, so no rules, and
that is knowledge and not a refusal: `allowed(...)` → open, `certain: True`, no
`Crawl-delay`. The guard is taken on each exact path all the same.

**PAST THE LAST PAGE THE ENVELOPE RESTATES ITS TOTAL AS ZERO.** Measured
2026-09-23 16:1x UTC: page 89 of 89 carries 25 items and `meta.total: 7945`;
page 90 carries none and `{"total": 0, "page": 0, "limit": 0, "totalPages": 0}`.
*A walk that re-reads the total each round therefore ends holding ZERO as the
board's stated count, and «7 945 emitted — the site states 0» is a witness that
accuses the walk of over-reading when the walk was exact.* The stated total and
the last page are read on **page one and never again**.

THE ORDER IS A BUMP STAMP, AND THAT IS THE ONE LOSS THIS WALK CANNOT PREVENT.
`sort_time` is not the posting date (`time` is): it moves when an employer
raises an advert, and the list is ordered by it. An advert bumped in the middle
of a walk jumps to page one, behind the reader, and pushes an unread one across
a page boundary. Nothing in the answer signals it. **The dedup by `code` keeps
it from being counted twice, and the emitted-against-stated witness is what
makes the loss visible** — it is the reason that witness is printed even when
the walk is bounded.

`limit` IS HONOURED BEYOND THE CLIENT'S OWN. `limit=200` answers 200 items and
`totalPages: 40`. The walk asks **90**, the value the site's own page sends,
because a walk that asks for more than the client asks is measuring a route
nobody serves.

WITHHELD: **`contact`** — the recruiter's telephone numbers, present on 84 of
the 90 rows of page one, dropped WHOLE and never scrubbed into a placeholder;
e-mail addresses and telephone numbers inside every text (Mongolian mobiles,
Ulaanbaatar landlines, `1800` service numbers); the employer's logo key; the
advert's **`lat`/`lng`**, which pin a workplace more precisely than a street;
the board's internal identifiers and its `hits`/`applies`/`shares` counters.

THE CRITERIA ARE NOT PROPAGATED, AND THE BOARD'S OWN FILTERS REPLACE THEM
(#183). `age_requires` (20 rows of 90), `for_hbi` and `is_retired` are never
emitted, and `criteria_withheld` names only the ones a given record actually
carries (#885: a claim about the board does not belong in a field that reads as
a claim about the advert). What a candidate loses by that is given back on the
QUESTION side: `--type 45plus`, `--type disability`, `--type student` are the
board's own facets, and each one REDUCES — 412, 11 and a reduced count against
7 945 — so the adverts are findable without a single row printing an age.
Country MN.
"""

import argparse
import datetime
import html as htmlmod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD, COUNTRY = "zangia", "MN"
HOST = "www.zangia.mn"
API_HOST = "new-api.zangia.mn"
API = f"https://{API_HOST}/api"
SEARCH = API + "/jobs/search"
SITE = f"https://{HOST}"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE = 90
MAX_PAGES = 2000
RETRY_WAIT = 15
# The constant the site's own client sends on every search; it is not a timestamp, and the RECORD's `time`
# field — which is one — is a different thing entirely.
CACHE_BUST = "1"
AD_PATH_RE = re.compile(r"^/job/_([A-Za-z0-9]+)$")
# The three criteria the board prints about a PERSON. The list answer carries all three; the advert answer
# carries only `for_hbi` — which is why `criteria()` separates «not set» from «not said».
CRITERIA = (("age_requires", "age"), ("for_hbi", "disability"), ("is_retired", "retirement"))
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# Mongolia dials eight digits. The three shapes the board's own `contact` column actually holds, measured on
# the ninety rows of page one: a mobile (`99112233`, `80254000`), an Ulaanbaatar or aimag landline
# (`11317798`), and a service line (`1800-1600`). **The first digit matters**: opening the class to `[1-9]`
# for a bare run would mask `12000000` — a salary in tugriks — and the whole point of the pattern is that it
# takes contacts and leaves the pay. Exercised both ways: the ninety contacts are covered (only the
# extensions behind `|` and `/` survive, and an extension alone is not a contact), and not one of the ninety
# `salary_phrase` values, nor a date, nor `09:00-18:00`, is touched.
PHONE_RE = re.compile(
    r"(?<![\d+])(?:\+?976[\s.\-]?)?(?:"
    r"(?:1800|1900)[\s.\-]?\d{4}"
    r"|(?:11|21)[\s.\-]?\d{6}"
    r"|[5-9]\d(?:[\s.\-]?\d){6}"
    r")(?!\d)")
# The board's own facets, read out of its bundle (`8476-*.js`). Each one is a QUESTION the site answers, and
# each one reduces: `45plus` 412, `disability` 11, `isRemote` 21, `part_time` 55, against 7 945.
TYPES = {
    "english": {"isEnglish": "true"},
    "leader": {"leader": "true"},
    "isRemote": {"isRemote": "true"},
    "onDarkhan": {"onDarkhan": "true"},
    "onErdenet": {"onErdenet": "true"},
    "45plus": {"ageRequires": "true"},
    "part_time": {"timetypeId[]": "2"},
    "disability": {"for_hbi": "true"},
    "no_experience": {"isReqExp": "true"},
    "no_language": {"noLanguage": "true"},
    "student": {"isStudent": "true"},
    "freelancer": {"isFreelancer": "true"},
    "isTrending": {"isTrending": "true"},
    "highSalary": {"highSalary": "true"},
}
_PACE = Pace(API_HOST, own=2.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[zangia] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, soft=False):
    """(status, text) — the API host only, the guard first, 2 s apart. `soft` renders a transport failure as
    `(None, reason)` instead of ending the process, and it exists for ONE reason: a walk of this board is
    eighty-nine requests over nine minutes, and the host reset the connection on the forty-ninth on
    2026-09-23. A `die()` there threw away forty-eight pages that had already been read and paid for.

    The advert's public address is on `www.zangia.mn`; it is EMITTED and never fetched, so this host check
    refusing anything but the API host is not a narrowing — it is the whole of what this adapter asks for.
    """
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower() != API_HOST:
        die(f"{url}: not {API_HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "application/json", "Accept-Language": "mn,en"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        if soft:
            return None, f"{type(e).__name__}: {e}"
        die(f"{url}: {type(e).__name__}: {e}")


def request_twice(url):
    """One retry, after a wait LONGER than the pace, because a reset is not a refusal and it is not an answer
    either. Two failures in a row stop the walk; they do not empty it."""
    st, body = request(url, soft=True)
    if st is not None:
        return st, body, None
    note(f"{url}: {body} — one retry in {RETRY_WAIT} s.")
    time.sleep(RETRY_WAIT)
    st2, body2 = request(url, soft=True)
    if st2 is not None:
        return st2, body2, None
    return None, "", f"{body}; and again after {RETRY_WAIT} s: {body2}"


def status_of(st, url):
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)


def text(markup):
    """The advert bodies are HTML the employer typed into a rich-text box."""
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def when(v):
    """A Unix second as the board writes it, in UTC. `time` is the posting; `sort_time` is a BUMP and is not
    emitted; `end_on` is the expiry."""
    try:
        n = int(v)
    except (TypeError, ValueError):
        return None
    return datetime.datetime.fromtimestamp(n, datetime.timezone.utc).isoformat() if n > 0 else None


def search_url(page, a):
    q = {"limit": str(PAGE), "page": str(page), "time": CACHE_BUST}
    if getattr(a, "type", None):
        q.update(TYPES[a.type])
    if getattr(a, "query", None):
        q["query"] = a.query
    return SEARCH + "?" + urllib.parse.urlencode(q)


def criteria(rec):
    """(withheld, unknown) — what the board prints beside THIS record and this adapter does not carry (#183),
    and what THIS ROUTE cannot say either way.

    `age_requires` is a number of years; `for_hbi` marks an advert the board files under «a citizen with a
    disability can work here»; `is_retired` under retirees. None of the three is ever emitted, and the
    board's own facet (`--type 45plus`, `--type disability`) is how they stay findable.

    **THE TWO ROUTES DO NOT CARRY THE SAME KEYS, AND AN EMPTY LIST WOULD HIDE IT.** The search answer holds
    all three; `/api/jobs/<code>` holds **only `for_hbi`**. Read with `rec.get(...)` alone, the detail of the
    advert measured on 2026-09-23 — `age` and `retirement` on its list row — came back `criteria_withheld:
    []`, which says *the board prints no criterion here* when the truth is *this route does not say*. That is
    the defect of #885 turned around: there, a field claimed a withholding that never happened; here, its
    emptiness claims a knowledge nobody has. A key that is ABSENT goes in `criteria_unknown`; only a key that
    is present and set goes in `criteria_withheld`.
    """
    held = [name for key, name in CRITERIA if rec.get(key)]
    unknown = [name for key, name in CRITERIA if key not in rec]
    return held, unknown


def row(rec):
    code = rec.get("code")
    held, unknown = criteria(rec)
    return {
        "source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{code}", "id": code,
        "url": f"{SITE}/job/_{code}",
        "title": scrub(rec.get("title")), "company": scrub(rec.get("company_name")),
        "company_en": scrub(rec.get("company_name_en")) or None,
        "place": scrub(rec.get("address")),
        "salary_as_written": scrub(rec.get("salary_phrase")),
        "salary_min": rec.get("salary_min") or None, "salary_max": rec.get("salary_max") or None,
        # **The board never writes the unit in the field, and its own page writes it at render:**
        # `Intl.NumberFormat("mn-MN").format(e) + "₮"` in the bundle. A single-country board is exactly where
        # a currency gets left out because it is obvious to whoever wrote the adapter — and `2500000` alone
        # is a number, not a wage.
        "salary_currency": "MNT" if (rec.get("salary_min") or rec.get("salary_max")) else None,
        "employment_type": rec.get("timetype") or None, "job_level": rec.get("job_level") or None,
        "english_required": bool(rec.get("eng_req")), "remote": bool(rec.get("remote")),
        "posted": when(rec.get("time")), "valid_through": when(rec.get("end_on")),
        "criteria_withheld": held, "criteria_unknown": unknown,
        # The recruiter's telephone is in `contact` on 84 rows of 90, and the coordinates are in `lat`/`lng`
        # on all of them. Neither is scrubbed into a placeholder: neither is read at all.
        "contacts_withheld": True,
    }


def envelope(body, url):
    try:
        d = json.loads(body)
    except ValueError:
        die(f"{url}: the answer is not JSON — the route changed shape.", EXIT_PARTIAL)
    if not isinstance(d, dict) or "items" not in d:
        die(f"{url}: no `items` in the answer — the route changed shape.", EXIT_PARTIAL)
    m = d.get("meta") or {}
    items = [x for x in d["items"] if isinstance(x, dict) and x.get("code")]
    return items, m


def cmd_jobs(a):
    if a.type and a.type not in TYPES:
        die(f"--type {a.type!r}: not one of the board's facets ({', '.join(sorted(TYPES))})")
    seen, criteria_seen, broke = set(), 0, None

    def emit(rec):
        """One row out, the moment it is read."""
        nonlocal criteria_seen
        r = row(rec)
        if r["criteria_withheld"]:
            criteria_seen += 1
        seen.add(r["id"])
        print(json.dumps(r, ensure_ascii=False), flush=True)

    if a.from_file:
        with open(a.from_file, encoding="utf-8") as f:
            items, meta = envelope(f.read(), a.from_file)
        stated, last, pages_read = meta.get("total"), meta.get("totalPages"), 1
        for it in items:
            if it["code"] not in seen:
                emit(it)
    else:
        stated, last, page = None, None, 1
        while page <= MAX_PAGES:
            url = search_url(page, a)
            st, body, failed = request_twice(url)
            if failed:
                broke = f"page {page}: {failed}"
                note(broke + " — stopped; the rows already written are kept.")
                page -= 1
                break
            status_of(st, url)
            items, meta = envelope(body, url)
            if page == 1:
                # **Read here and NEVER AGAIN.** Page 90 of an 89-page list answers `{"total": 0, "page": 0,
                # "limit": 0, "totalPages": 0}` — a re-read would end the walk holding zero as the board's
                # stated count, and the witness would accuse an exact walk of over-reading.
                stated, last = meta.get("total"), meta.get("totalPages")
                if not items:
                    die(f"{url}: no advert in the answer — the route changed shape, or the filter matches nothing.",
                        EXIT_PARTIAL)
                if stated is None:
                    die(f"{url}: the envelope states no `meta.total` — the route changed shape. The stated count is "
                        f"this walk's only witness, and a walk without one cannot say whether it read the board.",
                        EXIT_PARTIAL)
            new = 0
            for it in items:
                if it["code"] not in seen:
                    emit(it)
                    new += 1
            if not items or new == 0:
                if page > 1:
                    note(f"page {page}: {'no advert' if not items else 'only repeats'} — stopped.")
                break
            if not a.all_pages and page >= (a.pages or 3):
                break
            if last and page >= last:
                break
            page += 1
        pages_read = page
    n = len(seen)
    bounded = bool(a.from_file) or (not a.all_pages and (a.pages or 3) < (last or 0))
    asked = f" ({a.type})" if a.type else ""
    asked += f" \u00ab{a.query}\u00bb" if a.query else ""
    note(f"{th(n)} emitted over {th(pages_read)} page(s) of {PAGE}{asked} — the site states "
         f"{th(stated) if stated is not None else 'no total'}"
         + (f", its pager ending at page {th(last)}" if last else "")
         + ("; a BOUNDED read ({}), not the board".format("one saved page" if a.from_file else "--pages") if bounded
            else (": equal." if stated == n else f": {th(abs(stated - n))} short." if stated is not None else ".")))
    note("the list is ordered by `sort_time`, which an employer MOVES by raising an advert: one raised during "
         "a walk jumps behind the reader and can push an unread advert across a page boundary. Nothing in the "
         "answer says so \u2014 the count above is what shows it.")
    note(f"the recruiter's telephone (`contact`) and the workplace coordinates are never read; "
         f"{th(criteria_seen)} of {th(n)} row(s) carry a criterion the board prints and this adapter does not "
         f"(#183) \u2014 ask for them by `--type 45plus`, `--type disability`, `--type student`.")
    if broke:
        note("the walk did NOT reach the end of the board: the count above is what was read before the "
             "transport gave way, not what the board holds.")
        sys.exit(EXIT_PARTIAL)
    if stated is not None and not bounded and stated != n:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    code = a.code
    if a.url:
        parts = urllib.parse.urlsplit(a.url)
        m = AD_PATH_RE.match(parts.path or "")
        # The address carries an UNDERSCORE before the code — `/job/_1jd5q7pvwy`, not `/job/1jd5q7pvwy`.
        # It is the site's own shape, read out of its bundle (`href:"/job/_".concat(t.code)`).
        if parts.netloc.lower() != HOST or not m:
            die(f"{a.url!r}: not a Zangia advert address (https://{HOST}/job/_<code>)")
        code = m.group(1)
    if not code:
        die("give --url or --code")
    url = f"{API}/jobs/{urllib.parse.quote(code)}"
    st, body = request(url)
    status_of(st, url)
    try:
        d = json.loads(body)
    except ValueError:
        die(f"{url}: the answer is not JSON — the route changed shape.", EXIT_PARTIAL)
    if not isinstance(d, dict) or not d.get("code"):
        die(f"{url}: no advert in the answer — gone, or the route changed shape.", EXIT_PARTIAL)
    rec = row(d)
    # The detail carries the body the list does not, and the site's own canonical address.
    if d.get("url"):
        rec["url"] = d["url"]
    rec["profession"] = d.get("profession") or None
    rec["branch"] = d.get("branch") or None
    rec["skills"] = [s for s in (d.get("skills") or []) if isinstance(s, str)]
    rec["archived"] = bool(d.get("isArchive"))
    parts = [text(d.get(k)) for k in ("description", "requirements", "additional")]
    rec["description"] = (scrub("\n\n".join(p for p in parts if p)) or "")[:20000] or None
    print(json.dumps(rec, ensure_ascii=False))


def cmd_levels(a):
    """**The second witness, and it is a PARTITION.**

    A walk has one witness here: the `meta.total` the same answer carries — and a total that agrees with
    itself proves nothing (*a sum that matches its source is not a check*). This command asks the board a
    different question ten times: how many adverts at each of its own job levels. Measured 2026-09-23:

        1:93  2:3 127  3:454  4:2 676  5:255  6:938  7:171  8:128  9:66  10:37   =  7 945

    and the board states **7 945**. The sum landing exactly on an independently stated total is what makes
    it a proof rather than a coincidence: **it says every advert has exactly one level — no advert counted
    twice, none missing a level** — and it says the total is not a stored claim, since it agrees with a
    decomposition the board computes separately. *An excess would mean the facets overlap; a shortfall, that
    some adverts carry no level, and then the total and the walk would be measuring different populations.*
    """
    url = SEARCH + "?" + urllib.parse.urlencode({"limit": "1", "page": "1", "time": CACHE_BUST})
    st, body, failed = request_twice(url)
    if failed:
        die(f"{url}: {failed}", EXIT_PARTIAL)
    status_of(st, url)
    _, meta = envelope(body, url)
    stated = meta.get("total")
    total, seen = 0, []
    for lid in range(1, (a.max_level or 12) + 1):
        u = SEARCH + "?" + urllib.parse.urlencode({"limit": "1", "page": "1", "time": CACHE_BUST, "jobLevelId[]": str(lid)})
        st, body, failed = request_twice(u)
        if failed:
            die(f"{u}: {failed}", EXIT_PARTIAL)
        status_of(st, u)
        _, m = envelope(body, u)
        n = m.get("total") or 0
        seen.append((lid, n))
        total += n
        print(json.dumps({"job_level_id": lid, "stated": n}, ensure_ascii=False))
    note(" ".join(f"{i}:{th(n)}" for i, n in seen if n))
    note(f"the levels sum to {th(total)} and the board states {th(stated) if stated is not None else 'no total'}"
         + (": the facet PARTITIONS the board \u2014 every advert has exactly one level, and the total agrees with "
            "a decomposition the board computes apart from it." if total == stated
            else f": they DISAGREE by {th(abs(total - (stated or 0)))} \u2014 an excess means the facets overlap, a "
                 "shortfall that some adverts carry no level, and either way the walk's witness and the board's "
                 "own arithmetic are not measuring the same population."))
    if stated is None or total != stated:
        sys.exit(EXIT_PARTIAL)


def cmd_types(a):
    for k in sorted(TYPES):
        print(json.dumps({"type": k, "params": TYPES[k]}, ensure_ascii=False))
    note("the board's own facets; each is a question it answers, and each reduces. `45plus` and `disability` "
         "are how an advert stays findable when its criterion is not carried (#183).")


def main(argv=None):
    p = argparse.ArgumentParser(description="Zangia (Mongolia) — the JSON the site's own bundle calls, against the count that JSON states; the recruiter's telephone never emitted. Issue #660.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="/api/jobs/search — ninety a page; «N emitted … the site states M»")
    s.add_argument("--pages", type=int, help="how many pages to read (default 3 — a bounded read, said in the output)")
    s.add_argument("--all", dest="all_pages", action="store_true", help="walk to the last page the first answer names")
    s.add_argument("--type", help="one of the board's own facets (see `types`)")
    s.add_argument("--query", help="the board's own free-text search")
    s.add_argument("--from", dest="from_file", metavar="FILE", help="a saved copy of one search answer")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its address or its code; the body, the skills, contacts withheld")
    d.add_argument("--url")
    d.add_argument("--code")
    d.set_defaults(fn=cmd_ad)
    t = sub.add_parser("types", help="the board's own facets and what each one asks")
    t.set_defaults(fn=cmd_types)
    lv = sub.add_parser("levels", help="the SECOND witness: the per-level counts, and whether they sum to the board's own total")
    lv.add_argument("--max", dest="max_level", type=int, help="highest job level id to ask for (default 12; ten are populated)")
    lv.set_defaults(fn=cmd_levels)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
