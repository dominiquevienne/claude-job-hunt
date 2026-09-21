#!/usr/bin/env python3
"""Myanmar's national portal — «Job & Vacancy» (`myanmar.gov.mm/vacancies`): the ministries' own vacancy notices, published in a Liferay asset publisher that **states its own total** and pages by a token the page prints. Issue #634.

  myanmargov.py jobs [--lang en] [--closing-after YYYY-MM-DD] [--country-code MM] [--max-pages N]

WHAT IT IS. `myanmar.gov.mm` is the Union government's portal; its **Job & Vacancy** page is where
ministries file their recruitment notices — the Treasury's selection notices, the Planning
department's calls, the Ministry of Commerce's SME posts. *The Labour Exchange Offices' own system,
`www.myanmarjob.gov.mm`, does not answer from here (two timeouts on 2026-09-17, its name resolving on
both public resolvers) — and several entries LINK to it, which the record shows as the address the
portal publishes and nothing more.*

THE RULES. `myanmar.gov.mm` answers its rules file and allows this path: open, `certain: True`, no
Crawl-delay; 2 s is ours. The guard is taken on the exact path.

THE LIST. `/vacancies` (200; 225 332 B) carries the portlet whose heading states **«Job & Vacancy -
183 items»** — a count the site itself publishes, printed beside the emitted count on every run. Each
entry is a `div.col-md-12.smallcardstyle`: a link, an `h2` title (Burmese), and label/value lines —
**Agency** and **Closing Date** on every entry read. The pager is Liferay's:

```
_<INSTANCE>_delta=10   how many an page holds        ← both READ FROM THE PAGE'S OWN PAGER LINKS
_<INSTANCE>_cur=N      the page number                  never composed: the INSTANCE token is the
p_p_id=…_INSTANCE_…    which portlet on the page        site's, and it changes when they rebuild
```

**The INSTANCE token (`idasset460` on 2026-09-21) is read from the pager links the page prints**, as
JobCentre Brunei's is: a token we compose is a guess about someone else's deployment. The walk stops
when the emitted count reaches the stated total, when a page carries no entry, or when a page repeats
the addresses of the one before (exit 6) — and the run says which of the three happened.

**The portal keeps closed notices.** Entries from 2018 sit beside entries closing in October 2026:
that is the ministries' filing, not a fault, and the adapter does not silently drop them — it counts
them («N of the 183 closed before today») and `--closing-after` filters ON THE DATE THE ENTRY STATES,
saying how many it dropped.

**What an entry links to is the portal's business, not ours**: a PDF under `/documents/…`, a
ministry's own site, or a `myanmarjob.gov.mm/job/view/<id>` page. **No document is ever downloaded**
— the record carries the address as the portal publishes it.

**WITHHELD:** e-mail addresses and telephone numbers anywhere in a title or an agency name
(«[e-mail withheld]» / «[telephone withheld]»), `contacts_withheld` on every record. The titles are
Burmese and the run does not translate them.

`--lang` picks the portal's language (`en` → `/vacancies`, `my` → `/my/vacancies`).
`--country-code` STAMPS (the portlet states no country) and the run says so.

Measured 2026-09-21 15:0x–15:1x UTC by the declared client, the guard on the exact path, two reads of
page 1 and one of each other page: page 1 200 ×2 (225 332 B, md5 c9711170b6d4 — a news block moves),
10 entries and «183 items» stated; page 19 200 (222 430 B) **3 entries** — 18 × 10 + 3 = **183, the
stated total to the unit**.
"""

import argparse
import hashlib
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

HOST = "myanmar.gov.mm"
PORTLET = "com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\(?\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
DATE_RE = re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")
CARD_RE = re.compile(r'<div class="col-md-12 smallcardstyle">(.*?)(?=<div class="col-md-12 smallcardstyle">|<div class="taglib-search-iterator|</section>)', re.S)
HREF_RE = re.compile(r'<a\s[^>]*href="([^"]+)"', re.S)
TITLE_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.S)
FIELD_RE = re.compile(r'<span class="graycolor[^"]*">(.*?)</span>\s*<span class="blueColor1">(.*?)</span>', re.S)
STATED_RE = re.compile(r'Job\s*&(?:amp;)?\s*Vacancy\s*-\s*<span[^>]*>\s*([\d,]+)\s*items', re.S | re.I)
INSTANCE_RE = re.compile(re.escape(PORTLET) + r"_INSTANCE_(\w+)_cur=\d+")
DELTA_FMT = re.escape(PORTLET) + r"_INSTANCE_%s_delta=(\d+)"      # the page size, read from the page too
MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[myanmargov] {msg}", file=sys.stderr)


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
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
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
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return " ".join(t.split()) or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def when(s):
    """«September 03, 2026» → `2026-09-03`; anything else as read."""
    s = (s or "").strip()
    m = re.match(r"^([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})$", s)
    if m and MONTHS.get(m.group(1).lower()):
        return f"{m.group(3)}-{MONTHS[m.group(1).lower()]:02d}-{int(m.group(2)):02d}"
    return s or None


def instance_of(markup):
    """The portlet's INSTANCE token, READ from the pager links the page prints — never composed."""
    found = INSTANCE_RE.findall(markup or "")
    return found[0] if found else None


def stated(markup):
    m = STATED_RE.search(markup or "")
    return int(m.group(1).replace(",", "")) if m else None


def entries_of(markup):
    """The portlet's cards → ([(address, fields)], cards skipped); the labels are read as labels."""
    out, skipped = [], 0
    for card in CARD_RE.findall(markup or ""):
        href = HREF_RE.search(card)
        title = TITLE_RE.search(card)
        if not href or not title:
            skipped += 1                 # counted, so «one short» has a candidate explanation
            continue
        fields = {}
        for label, value in FIELD_RE.findall(card):
            key = (text(label) or "").strip().rstrip(":").lower()
            if key:
                fields[key] = text(value)
        out.append((htmlmod.unescape(href.group(1)), {"title": text(title.group(1)),
                                                      "agency": fields.get("agency"),
                                                      "closing": fields.get("closing date")}))
    return out, skipped


def record(url, f, stamp):
    # The portal publishes no identifier and one address can carry two notices (a call and its
    # result), so the key is the address AND the title. The title is Burmese, and a slug made of
    # ASCII letters is EMPTY for it — twenty records shared one key that way — so the title is
    # folded by its digest, which is as distinct as the title itself, whatever the script.
    title = f.get("title") or ""
    key = f"{url}#{hashlib.sha1(title.encode('utf-8')).hexdigest()[:10]}" if title else url
    return {
        "source": "myanmargov", "country": stamp,
        "ledger_id": f"myanmargov:{key}", "id": key,
        "title": scrub(f.get("title")),
        "agency": scrub(f.get("agency")),
        "closing_date": when(f.get("closing")),
        "url": url,
        "key_is_ours": True,
        "document_downloaded": False,     # the portal links PDFs and other sites; we name them, we do not fetch them
        "contacts_withheld": True,
    }


def page_url(lang, instance, delta, cur):
    # the portlet's own parameter names carry a LEADING UNDERSCORE — without it Liferay ignores
    # them and serves page 1 again, which reads exactly like a board that repeats itself
    q = [("p_p_id", f"{PORTLET}_INSTANCE_{instance}"), ("p_p_lifecycle", "0"),
         ("p_p_state", "normal"), ("p_p_mode", "view"),
         (f"_{PORTLET}_INSTANCE_{instance}_delta", str(delta)),
         ("p_r_p_resetCur", "false"),
         (f"_{PORTLET}_INSTANCE_{instance}_cur", str(cur))]
    root = f"https://{HOST}/vacancies" if lang == "en" else f"https://{HOST}/{lang}/vacancies"
    return root + "?" + urllib.parse.urlencode(q)


def cmd_jobs(a):
    lang = (a.lang or "en").strip().lower()
    if not re.match(r"^[a-z]{2}$", lang):
        die(f"--lang {a.lang}: two letters (en, my)")
    after = (a.closing_after or "").strip()
    if after and not re.match(r"^\d{4}-\d{2}-\d{2}$", after):
        die(f"--closing-after {a.closing_after}: a date, YYYY-MM-DD")
    stamp = a.country_code.upper() if a.country_code else None
    first = f"https://{HOST}/vacancies" if lang == "en" else f"https://{HOST}/{lang}/vacancies"
    code, body = request(first)
    if code == 404:
        die(f"{first}: HTTP 404 — the page is gone", EXIT_GONE)
    if code != 200:
        die(f"{first}: HTTP {code}", EXIT_PARTIAL)
    instance = instance_of(body)
    if not instance:
        die(f"{first}: 200 but no pager naming the portlet's INSTANCE — the page changed; a token is never composed", EXIT_PARTIAL)
    m = re.search(DELTA_FMT % re.escape(instance), body)
    delta = int(m.group(1)) if m else 10
    said = stated(body)
    rows, seen, page, ended, dropped, skipped = [], set(), 1, None, 0, 0
    while True:
        found, skip = entries_of(body)
        skipped += skip
        if not found:
            ended = f"page {page} carried no entry"
            break
        keys = {(u, (f.get("title") or "")) for u, f in found}   # two notices can share one address
        if page > 1 and keys <= seen:
            die(f"page {page} repeats the entries of the page before — the walk ended at {th(len(rows))}", EXIT_PARTIAL)
        for url, f in found:
            key = (url, f.get("title") or "")
            if key in seen:
                continue
            seen.add(key)
            r = record(url, f, stamp)
            if r["closing_date"] and re.match(r"^\d{4}-\d{2}-\d{2}$", r["closing_date"]) and after:
                if r["closing_date"] < after:
                    dropped += 1
                    continue
            rows.append(r)
        if said is not None and len(seen) >= said:
            ended = f"the {th(said)} the portlet states were read"
            break
        if a.max_pages and page >= a.max_pages:
            ended = f"stopped by --max-pages at page {page}"
            break
        page += 1
        code, body = request(page_url(lang, instance, delta, page))
        if code != 200:
            die(f"page {page}: HTTP {code} — the walk ended at {th(len(seen))}", EXIT_PARTIAL)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    today = time.strftime("%Y-%m-%d", time.gmtime())
    closed = sum(1 for r in rows if r["closing_date"] and re.match(r"^\d{4}-\d{2}-\d{2}$", r["closing_date"]) and r["closing_date"] < today)
    read = th(len(seen))
    if said is None:
        note(f"{read} entry(ies) read over {th(page)} page(s); **the portlet stated no total this time** — it usually prints «Job & Vacancy - N items», and the run says so rather than claiming one.")
    elif said != len(seen):
        note(f"{read} entry(ies) read over {th(page)} page(s), the portlet states {th(said)} — {th(abs(said - len(seen)))} {'short' if said > len(seen) else 'more'}; {ended}.")
    else:
        note(f"{read} entry(ies) read over {th(page)} page(s), and the portlet states {th(said)} — they agree; {ended}.")
    note(f"{th(len(rows))} emitted{f' ({th(dropped)} dropped by --closing-after, which filters on the date the ENTRY states)' if dropped else ''}"
         f"{f'; {th(skipped)} card(s) carried no address or no title and were counted, not passed over in silence' if skipped else ''}"
         "; the portlet's INSTANCE token was read from its own pager, never composed.")
    note(f"the portal keeps closed notices: {th(closed)} of the emitted entries state a closing date before {today} (UTC) — the ministries' filing, not a fault, and never dropped in silence.")
    note("no document is downloaded: a PDF, a ministry's site or a `myanmarjob.gov.mm` page is named as the portal publishes it.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the portlet states no country.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Myanmar's national portal — the ministries' Job & Vacancy notices, walked by the pager the page prints. Issue #634.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the portlet's entries (1 request a page)")
    j.add_argument("--lang", default="en", help="the portal's language (en, my) — default en")
    j.add_argument("--closing-after", dest="closing_after", metavar="YYYY-MM-DD", help="keep only the entries stating a closing date on or after this day (OUR filter)")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the portlet states none)")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N pages (0 = until the stated total is read)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
