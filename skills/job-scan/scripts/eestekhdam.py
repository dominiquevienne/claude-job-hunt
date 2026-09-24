#!/usr/bin/env python3
"""E-Estekhdam (`www.e-estekhdam.com`, «ای استخدام», Iran): the aggregator's own list — a Nuxt shell of 8 383 bytes titled «بارگذاری» whose bundle calls `POST /search-api/search?page=N`, twenty a page, answering **201**; **the pager CLAMPS instead of ending**, and the board states no total anywhere, so every count this tool prints is a LOWER BOUND. Issue #632.

  eestekhdam.py jobs [--pages N | --all] [--where KEY] [--query Q] [--filter KEY=VALUE]
  eestekhdam.py filters

THE SHELL SAYS «LOADING» AND THE BUNDLE SAYS EVERYTHING. The root answers 200
at 8 383 bytes of Nuxt with no card and no count; the scripts live on
`cdn.e-estekhdam.com/_nuxt/assets/`, and `index.V1k0iVya.js` (3.3 MB) carries

    axios.create({ baseURL: "/search-api", headers: { "x-lang": "fa" } })
    search = async (e, B = {}) => client.post("/search", e, { params: B })

so the list is `POST https://www.e-estekhdam.com/search-api/search?page=N` with
a JSON filter object as the body (`{}` = everything).

**THE PAGER CLAMPS INSTEAD OF ENDING, AND BOTH USUAL STOP RULES FAIL SILENTLY.**
Measured 2026-09-23:

    no filter              page 100 == page 500 == page 5000, IDENTICAL TO THE BYTE
                           (md5 973706fe9df1), twenty items, `ok: true`
    {"where":["ایلام"]}    page 50 answers `data: {}` — empty: the real end

The server caps the page index at 100 and re-serves the hundredth for ever,
with no error. Found by bisection between 50 and 500: page 99 distinct, page
100 clamped. *So a walk that stops on «an empty page» NEVER stops on a broad
query; a walk that stops on «nothing new» stops at 2 000 and presents the cap
as the board.* This walk stops when a page **repeats the previous one** and
says the query hit the cap — and then its count is a lower bound for that
query, never a total. **It is #894's family, in its sharpest form: `new == 0`
does not return zero here, it returns a round number that is wrong.**

`data` IS A LIST WHEN FULL AND A DICT WHEN EMPTY. The empty answer is
`{"data": {}}`, not `{"data": []}` — so `data[0]` raises `KeyError` and any
code that indexes before checking dies on exactly the page that means «done».

NO STATED COUNT EXISTS ON THIS BOARD. `meta` carries a URL and a title and no
total; `POST /search-api/search/filter-options` returns 253 professions, 50
provinces, 29 sectors, 133 technologies — **and not one count**; `/sitemap.xml`
answers 404. There is therefore nothing to hold the emission against, and the
honest line is «N emitted, a LOWER BOUND, the board states no total». Coverage
past the cap goes through the province facet — **which does not partition**: a
nationwide advert carries `provinces` with **31 values** (of the hundred held,
99 carry one and one carries thirty-one), so the dedup by `id` is mandatory and
a sum over provinces is worth nothing as a witness.

THE RULES (read 2026-09-23), AND TWO THINGS HONOURED BEYOND THE LETTER.
`allowed('www.e-estekhdam.com', '/search-api/search')` → open, `certain: True`.

1. The file names **`ClaudeBot` with `Crawl-delay: 5`**; `Claude-User` is not
   named and falls into `*`, which imposes none. **This adapter paces at 5 s
   anyway**: the host set five seconds for every robot it names, and our token
   escapes it only through a gap in its file.
2. The `*` group refuses **`sort=` and `posted=`** on `/jobs` and `/search`,
   plus two named facets — `/jobs/*حقوق-از` (salary-from) and `/jobs/*-برای-`
   («for …»). Our path is covered by none of those lines, **but the intention is
   written**: `sort` and `posted` are refused by name in the body, and those two
   facets are never walked. *A written `Disallow` is an intention; a route that
   dodges it by the path betrays it all the same.*

NO `ad` COMMAND, AND THAT IS A MEASUREMENT. The advert's own address is the
same Nuxt shell, and the bundle exposes **no per-advert endpoint** — only
`/related-jobs/…`. What the list row carries is what this board gives.

WITHHELD: the **`gender`** field, present on every one of the hundred adverts
held (`0` 45×, `1` 31×, `2` 24×) — a criterion about a person, never carried
(#183, as on Karboom); e-mail addresses and telephone numbers in every text;
the board's internal identifiers. Country IR.
"""

import argparse
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

BOARD, COUNTRY = "eestekhdam", "IR"
HOST = "www.e-estekhdam.com"
API = f"https://{HOST}/search-api"
SEARCH = API + "/search"
FILTERS = SEARCH + "/filter-options"
SITE = f"https://{HOST}"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE = 20
# The server caps the page index here and re-serves this page for ever. It is NOT a stop condition on its
# own — the walk stops on the REPEAT, and this bound only spares it one useless request.
PAGE_CAP = 100
RETRY_WAIT = 15
# Refused by name in the body. The rules refuse `sort=` and `posted=` on the site's own search paths; this
# route is not covered by those lines, and sending them anyway would honour the path and not the intention.
REFUSED_KEYS = ("sort", "posted")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?[\d۰-۹][\d۰-۹\s().\-]{7,}[\d۰-۹](?!\w)")
# **Five seconds, though the group that applies to us imposes none.** The file names ClaudeBot and gives it
# `Crawl-delay: 5`; `Claude-User` falls into `*`, which has no delay. Taking the faster path would be reading
# the host's silence as a permission it plainly did not intend.
_PACE = Pace(HOST, own=5.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[eestekhdam] {msg}", file=sys.stderr)


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


def request(url, body, soft=False):
    """(status, text) — this host only, the guard first, 5 s apart. The list is a POST; there is no GET.

    `soft` renders a transport failure as `(None, reason)` instead of ending the process. It exists because a
    full walk here is a hundred requests over eight minutes and **the transport gave way twice in two days**:
    a connection reset on Zangia's 49th request (2026-09-23) and `SSL: UNEXPECTED_EOF_WHILE_READING` on this
    board's 40th (2026-09-24). A `die()` there ends the walk with an error line and NO witness — the reader
    is left with a pile of rows and nothing saying how far it got.
    """
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower() != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(wire_url(url), data=data, method="POST",
                                 headers={"User-Agent": UA, "Content-Type": "application/json",
                                          "Accept": "application/json", "x-lang": "fa",
                                          "X-Requested-With": "XMLHttpRequest"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        if soft:
            return None, f"{type(e).__name__}: {e}"
        die(f"{url}: {type(e).__name__}: {e}")


def request_twice(url, body):
    """(status, text, failed) — one retry after a wait longer than the pace, because a transport failure is
    neither a refusal nor an answer. Two in a row stop the walk; they do not empty it."""
    st, out = request(url, body, soft=True)
    if st is not None:
        return st, out, None
    note(f"{url}: {out} — one retry in {RETRY_WAIT} s.")
    time.sleep(RETRY_WAIT)
    st2, out2 = request(url, body, soft=True)
    if st2 is not None:
        return st2, out2, None
    return None, "", f"{out}; and again after {RETRY_WAIT} s: {out2}"


def status_of(st, url):
    # **201, not 200.** The list answers `201 Created` to a POST that creates nothing; a status check written
    # for `== 200` refuses every page of this board and reads like a host that closed.
    if st in (200, 201):
        return
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    die(f"{url}: HTTP {st}", EXIT_PARTIAL)


def text(markup):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ").replace("‌", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def items_of(d, url):
    """The adverts of one answer. **`data` is a LIST when full and a DICT when empty** — the empty page
    answers `{"data": {}}`, so anything that indexes before checking dies on the page that means «done»."""
    if not isinstance(d, dict) or "data" not in d:
        die(f"{url}: no `data` in the answer — the route changed shape.", EXIT_PARTIAL)
    raw = d["data"]
    if isinstance(raw, dict):
        return []                      # `{}` — the real end of a result set
    if not isinstance(raw, list):
        die(f"{url}: `data` is neither a list nor an empty object — the route changed shape.", EXIT_PARTIAL)
    return [x for x in raw if isinstance(x, dict) and x.get("id") is not None]


def body_of(a):
    """The filter object the site's own client sends. Empty values are dropped, exactly as its
    `normalizedSearchPrams` does — and `sort`/`posted` are refused by name.

    **THE REFUSAL HAS TO BE REACHABLE OR IT IS DECORATION.** A first version built this body from `--where`
    and `--query` alone and then checked it for `sort`/`posted`: the two keys could never be there, so the
    check could never fire, and the docstring above it claimed a discipline the code did not have — the inert
    guard that cites its own doctrine. `--filter k=v` is what makes the refusal a real gate: the board has
    fourteen other facets, a caller will want them, and that is exactly the path by which `sort=` would
    arrive.
    """
    b = {}
    if getattr(a, "where", None):
        b["where"] = [a.where]
    if getattr(a, "query", None):
        b["query"] = a.query
    for pair in (getattr(a, "filter", None) or []):
        if "=" not in pair:
            die(f"--filter {pair!r}: write it as key=value (see `filters` for the keys)")
        k, v = pair.split("=", 1)
        k = k.strip()
        if k in REFUSED_KEYS:
            die(f"--filter {k}=…: refused BY NAME. The rules disallow `{k}=` on this site's own search "
                f"paths (`/jobs?{k}=`, `/search?{k}=`); this route escapes those lines only by its path, "
                f"and honouring the path instead of the intention is not honouring the rules.", EXIT_REFUSED)
        if k in ("salary", "برای"):
            die(f"--filter {k}=…: refused BY NAME. The rules disallow the facets `/jobs/*حقوق-از` "
                f"(salary-from) and `/jobs/*-برای-` («for …») by name.", EXIT_REFUSED)
        if k == "where":
            b.setdefault("where", []).append(v)
        else:
            b[k] = v
    return b


def row(rec):
    rid = rec.get("id")
    url = rec.get("url") or ""
    return {
        "source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{rid}", "id": str(rid),
        "url": urllib.parse.urljoin(SITE, url) if url else None,
        "title": scrub(text(rec.get("title"))), "short_title": scrub(text(rec.get("short_title"))),
        "company": scrub(text(rec.get("brand_name"))) or None,
        "sector": rec.get("brand_sector") or None,
        "places": [p for p in (rec.get("provinces") or []) if isinstance(p, str)],
        "location_as_written": scrub(text(rec.get("location"))),
        "contract": [c for c in (rec.get("contract") or []) if isinstance(c, str)],
        "positions": [p for p in (rec.get("positions") or []) if isinstance(p, str)],
        "technologies": [t for t in (rec.get("technologies") or []) if isinstance(t, str)],
        "salary_as_written": scrub(text(rec.get("salary"))),
        "on_ats": bool(rec.get("ats")), "expired": bool(rec.get("expired")),
        # The board prints a gender beside every advert; it is never carried (#183). The claim is made once
        # per row because the field IS on every row — unlike Karboom, where it lives on the advert page only.
        "criteria_withheld": ["gender"] if "gender" in rec else [],
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    body = body_of(a)
    # **The rows go out AS THEY ARE READ, and this is the second time the lesson has been paid.** A walk here
    # is up to a hundred requests at five seconds apart — eight minutes — and holding them to print at the end
    # turns any interruption into zero lines and one error, which looks exactly like a board that gave
    # nothing. (Measured on Zangia, 2026-09-23: a connection reset on the 49th of 89 requests threw away
    # forty-eight pages that had been read and paid for.)
    seen, emitted, withheld, page, capped, last_ids, broke = set(), 0, 0, 1, False, None, None
    limit = PAGE_CAP if a.all_pages else max(1, a.pages or 3)
    while page <= min(limit, PAGE_CAP):
        url = f"{SEARCH}?page={page}"
        st, raw, failed = request_twice(url, body)
        if failed:
            broke = f"page {page}: {failed}"
            note(broke + " — stopped; the rows already written are kept.")
            page -= 1
            break
        status_of(st, url)
        try:
            d = json.loads(raw)
        except ValueError:
            die(f"{url}: the answer is not JSON — the route changed shape.", EXIT_PARTIAL)
        items = items_of(d, url)
        if not items:
            if page == 1:
                die(f"{url}: no advert in the first answer — the route changed shape, or the filter matches "
                    f"nothing.", EXIT_PARTIAL)
            note(f"page {page}: empty — the end of this result set.")
            page -= 1
            break
        ids = tuple(x["id"] for x in items)
        # **The stop that this board needs.** Past page 100 the server re-serves the hundredth for ever, so
        # the repeat — not an empty page, not «nothing new» — is what says the query has hit the cap.
        if last_ids is not None and ids == last_ids:
            capped = True
            note(f"page {page}: the server RE-SERVED page {page - 1} identically — the pager is CLAMPED "
                 f"(measured: page 100 = 500 = 5000 to the byte). Stopped; this query reaches no further.")
            page -= 1
            break
        last_ids = ids
        for rec in items:
            if rec["id"] not in seen:
                seen.add(rec["id"])
                r = row(rec)
                emitted += 1
                withheld += 1 if r["criteria_withheld"] else 0
                print(json.dumps(r, ensure_ascii=False), flush=True)
        page += 1
    else:
        page = min(limit, PAGE_CAP)
        if limit >= PAGE_CAP:
            capped = True
    n = emitted
    asked = f" (where={a.where})" if a.where else ""
    asked += f" «{a.query}»" if a.query else ""
    bounded = not a.all_pages and page >= (a.pages or 3)
    note(f"{th(n)} emitted over {th(page)} page(s) of {PAGE}{asked} — **a LOWER BOUND**: this board states no "
         f"total anywhere (`meta` carries none, `filter-options` carries none, `/sitemap.xml` is 404), so "
         f"there is nothing to hold this count against."
         + (" The walk was CUT by the transport before the end." if broke
            else " The query hit the page CAP (100), so it reaches no further: ask a narrower one." if capped
            else " The result set ended on its own." if not bounded else " A BOUNDED read (--pages), not the query."))
    note(f"{th(withheld)} of {th(n)} row(s) carry a gender the board "
         f"prints and this adapter does not (#183); contacts and internal identifiers are never read.")
    if broke:
        note("the walk did NOT reach the end of this query: the count above is what was read before the "
             "transport gave way, not what the query holds.")
        sys.exit(EXIT_PARTIAL)
    if capped and a.all_pages:
        sys.exit(EXIT_PARTIAL)


def cmd_filters(a):
    st, raw = request(FILTERS, {})
    status_of(st, FILTERS)
    try:
        d = json.loads(raw)
    except ValueError:
        die(f"{FILTERS}: the answer is not JSON — the route changed shape.", EXIT_PARTIAL)
    data = (d or {}).get("data") or {}
    for group in sorted(data):
        vals = data[group]
        if isinstance(vals, list):
            print(json.dumps({"group": group, "count": len(vals),
                              "keys": [v.get("key") for v in vals if isinstance(v, dict)][:200]},
                             ensure_ascii=False))
    note("the board's own facets — **and not one of them carries a count**, which is why no walk here has a "
         "witness. `where` is the useful one: it is how a query stays under the page cap.")


def main(argv=None):
    p = argparse.ArgumentParser(description="E-Estekhdam (Iran) — the JSON its Nuxt shell calls; the pager CLAMPS, so every count is a lower bound; the gender it prints is never carried. Issue #632.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="POST /search-api/search?page=N — twenty a page; stops on a REPEATED page")
    s.add_argument("--pages", type=int, help="how many pages to read (default 3 — a bounded read, said in the output)")
    s.add_argument("--all", dest="all_pages", action="store_true", help="walk to the end, or to the page cap")
    s.add_argument("--where", help="one province key (see `filters`) — how a query stays under the cap")
    s.add_argument("--query", help="the board's own free-text search")
    s.add_argument("--filter", action="append", metavar="KEY=VALUE",
                   help="one of the board's other facets (see `filters`); `sort` and `posted` are refused by name")
    s.set_defaults(fn=cmd_jobs)
    f = sub.add_parser("filters", help="the board's own facets, and the fact that none of them carries a count")
    f.set_defaults(fn=cmd_filters)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
