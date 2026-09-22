#!/usr/bin/env python3
"""Government of Saint Lucia — the portal's «Job Opportunities» (`www.govt.lc/jobs`): the public-sector vacancies, inlined whole in the page **with the count the portal states itself**. Issue #746.

  govtlc.py jobs [--country-code LC]                    the list (1 request; 14 stated and 14 inlined on 2026-09-22)
  govtlc.py ad --url https://www.govt.lc/jobs/<slug>    one notice, its text as the editor published it

WHAT IT IS. The Government of Saint Lucia's own portal. Its `/jobs` page is where ministries, the
Attorney General's Chambers, the Youth Economy Agency and the statutory bodies advertise; `/vacancies`
is the wider archive (2 718 records on 2026-09-21 — jobs, scholarships, consultancies and tenders
together), paged through a POST web method this adapter does not replay.

**THE ISSUE WAS BLOCKED ON A PAGE THAT NOW ANSWERS.** On 2026-09-18 `/jobs` and `/vacancies` both
returned **HTTP 500** to every client — an ASP.NET «ExecuteReader requires an open and available
Connection» — and #746 was opened `blocked` on that measurement. The control deposited for
2026-09-21 found them **served**, and this reading confirms it: *a dated failure is not a verdict,
and the ticket said exactly what would lift it.*

THE RULES. `www.govt.lc` answers something that is not a rules file (`unrecognised`), so no rule is
read: open, `certain: False`, no Crawl-delay; 2 s is ours. The guard is taken on the exact path.

THE LIST. `/jobs` (200; 438 854 B) initialises its own list in the page:

```
new ResourceSummaryList('Resource', {"ResourceTypeNames":"jobs", …}, [ …14 items… ],
                        'm_summaries_container', {"TotalRecords":14, …})
```

The items array is read **by balancing its brackets**, not by a regular expression that stops at the
first `]` — a description holds `]` often enough. **`TotalRecords` is the portal's own count**, and
it is printed beside the emitted count on every run: 14 stated, 14 inlined, they agree today, and
the run says «N short» the day they do not.

**The page's own «No Vacancies to display. 0» is NOT a count** — it is the Knockout branch
`ko if: Items().length == 0`, present in the markup whatever the list holds. *A reader who trusted
the visible text would have published zero on a page carrying fourteen.*

**WITHHELD:** every item carries `Latitude` and `Longitude` — **coordinates are never emitted**, and
the record names them in `withheld_fields` so the absence is declared rather than silent; e-mail
addresses and telephone numbers in a title or a notice; and, in a notice's text, the postal address
an applicant is told to write to («P.O. Box 1234», «3 Manoel Street») — an address is not carried,
and `withheld_fields` says so. The rest of the notice is the editor's text as published.

`--country-code` STAMPS (the list states no country — every post is Saint Lucia's by the portal's own
scope, and a stamp is still the user's) and the run says so.

Measured 2026-09-22 09:0x–09:1x UTC by the declared client, the guard on the exact path: `/jobs` 200
(438 854 B, md5 943c903b455f — a ViewState moves between reads, so the md5 is not a stable witness
and the COUNT is), **14 items inlined, `TotalRecords: 14`**, dated 2024-05-02 to 2026-09-18 (the
portal keeps its existing vacancies listed); a notice read at
`/jobs/senior-crown-counsel-attorney-general-s-chambers-saint-lucia` 200 (214 946 B) carries its
title, «Published:» and the whole «Description:» as HTML.
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

HOST = "www.govt.lc"
LIST = f"https://{HOST}/jobs"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\(?\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
DATE_RE = re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")
# the two forms a notice uses to tell an applicant where to write; an address is never carried
BOX_RE = re.compile(r"\bP\.?\s?O\.?\s?Box\s+[\w-]+", re.I)
STREET_RE = re.compile(r"\b\d{1,4}[A-Za-z]?,?\s+[A-Z][\w'’-]*(?:\s+[A-Z][\w'’-]*)?\s+"
                       r"(?:Street|St\.|Avenue|Ave\.|Road|Rd\.|Boulevard|Blvd\.|Lane|Drive|Highway)\b")
LIST_RE = re.compile(r"new\s+ResourceSummaryList\s*\(")
TOTAL_RE = re.compile(r'"TotalRecords"\s*:\s*(\d+)')
STRIP_RE = re.compile(r"(?s)<style.*?</style>|<script.*?</script>")
MID_RE = re.compile(r'<div id="home-mid">(.*?)</div>\s*<div', re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
CELL_RE = re.compile(r"<td[^>]*>\s*(Published|Description)\s*:?\s*</td>\s*<td[^>]*>(.*?)</td>", re.S | re.I)
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[govtlc] {msg}", file=sys.stderr)


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
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no rules file read; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>|</tr>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    """Contacts out; an ADDRESS out too — a notice tells an applicant where to write, and we do not carry it."""
    if not s:
        return None, []
    took = []
    if MAIL_RE.search(s):
        took.append("email")
        s = MAIL_RE.sub("[e-mail withheld]", s)
    if BOX_RE.search(s) or STREET_RE.search(s):
        took.append("postal_address")
        s = STREET_RE.sub("[address withheld]", BOX_RE.sub("[address withheld]", s))
    out = PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s)
    if out != s:
        took.append("telephone")
    return (out.strip() or None), took


def when(s):
    """«2026-09-18T12:23:31.2900000Z» → `2026-09-18`; «9/17/2026 10:06:28 AM» → `2026-09-17`."""
    s = (s or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})T", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    return s or None


def items_of(markup):
    """The page's own `ResourceSummaryList(…)` → (items, stated).

    The items array is read by BALANCING brackets from the first `[` after the query object: a
    description holds `]` often enough that a regular expression stopping at the first one would cut
    the list in the middle and emit whatever survived.
    """
    m = LIST_RE.search(markup or "")
    if not m:
        return None, None
    seg = markup[m.end():]
    opening = re.search(r",\s*\[", seg)          # the array starts after the query object, spaced or not
    if not opening:
        return None, None
    start = opening.end() - 1
    depth, end, in_string, escaped = 0, None, False, False
    for i in range(start, len(seg)):
        c = seg[i]
        if in_string:
            # a BRACKET INSIDE A STRING is text: «Duties [see schedule]» and a lone «annex 2]» both
            # occur in these descriptions, and counting them cuts the list in the middle
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                in_string = False
            continue
        if c == '"':
            in_string = True
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        return None, None
    try:
        items = json.loads(seg[start:end + 1])
    except ValueError:
        return None, None
    total = TOTAL_RE.search(seg[end:end + 2000])
    return items, (int(total.group(1)) if total else None)


def record(it, stamp):
    title, took = scrub(text(it.get("Title")))
    withheld = ["coordinates"] + took          # every item carries Latitude/Longitude: never emitted
    url = it.get("Url") or ""
    return {
        "source": "govtlc", "country": stamp,
        "ledger_id": f"govtlc:{(url.rsplit('/', 1)[-1] or it.get('Id'))}",
        "id": url.rsplit("/", 1)[-1] or str(it.get("Id") or ""),
        "title": title,
        "url": urllib.parse.urljoin(LIST, url) if url else None,
        "published": when(it.get("Date")), "updated": when(it.get("LastUpdatedDate")),
        "kind": it.get("ResourceSubTypeName"),
        "withheld_fields": withheld,
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    code, body = request(LIST)
    if code == 404:
        die(f"{LIST}: HTTP 404 — the page is gone", EXIT_GONE)
    if code == 500:
        die(f"{LIST}: HTTP 500 — the portal's database is down again, as it was on 2026-09-18; nothing read", EXIT_PARTIAL)
    if code != 200:
        die(f"{LIST}: HTTP {code}", EXIT_PARTIAL)
    items, stated = items_of(body)
    if items is None:
        die(f"{LIST}: 200 without the page's own ResourceSummaryList — the page changed; not an empty list "
            f"(its «No Vacancies to display.» is a template branch, never a count)", EXIT_PARTIAL)
    rows, seen = [], set()
    for it in items:
        r = record(it, stamp)
        if not r["id"] or r["id"] in seen:
            continue
        seen.add(r["id"])
        rows.append(r)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if stated is None:
        note(f"{th(len(rows))} inlined and emitted; **the page stated no total this time** — it usually carries `TotalRecords`, and the run says so rather than claiming one.")
    elif stated != len(items):
        note(f"{th(len(items))} item(s) inlined, the portal states {th(stated)} — {th(abs(stated - len(items)))} {'short' if stated > len(items) else 'more'}; the gap is the page's.")
    else:
        note(f"{th(len(items))} item(s) inlined, and the portal states {th(stated)} — they agree.")
    note(f"{th(len(rows))} emitted; the page's «No Vacancies to display. 0» is a Knockout branch present whatever the list holds, and is never read as a count.")
    note("coordinates are never emitted (every item carries Latitude/Longitude) — each record names them in `withheld_fields`.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the list states no country.")


def cmd_ad(a):
    url = a.url.strip()
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST or not parts.path.startswith("/jobs/") or parts.query:
        die(f"--url {url}: a https://{HOST}/jobs/<slug> notice, without a query string")
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the notice is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    mid = MID_RE.search(STRIP_RE.sub("", body))
    if not mid:
        die(f"{url}: 200 without the notice's own block — the page changed", EXIT_PARTIAL)
    block = mid.group(1)
    h1 = H1_RE.search(block)
    if not h1:
        die(f"{url}: 200 without a title — the page changed", EXIT_PARTIAL)
    cells = {k.lower(): v for k, v in CELL_RE.findall(block)}
    title, took_t = scrub(text(h1.group(1)))
    description, took_d = scrub(text(cells.get("description")))
    r = {
        "source": "govtlc", "country": a.country_code.upper() if a.country_code else None,
        "ledger_id": f"govtlc:{parts.path.rsplit('/', 1)[-1]}", "id": parts.path.rsplit("/", 1)[-1],
        "title": title, "url": url,
        "published": when(text(cells.get("published"))),
        "description": description,
        "withheld_fields": sorted(set(took_t + took_d)),
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))
    if r["withheld_fields"]:
        note(f"withheld from this notice: {', '.join(r['withheld_fields'])} — named, so the removal is not a silence.")
    else:
        note("nothing to withhold in this notice: it carries no address, no e-mail and no number.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Government of Saint Lucia — the portal's job list, read from the page's own ResourceSummaryList against the count it states. Issue #746.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the list (1 request)")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the list states none)")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one notice and its text")
    d.add_argument("--url", required=True, help="the notice's own address")
    d.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on the record")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
