#!/usr/bin/env python3
"""MyJobs (`myjobs.com.mm`), Myanmar: the list states no total, but the home page names **thirty categories with a count each** and the pager names its own last page — **three figures that predict one another before the walk begins**, and they were verified before a line of this adapter was written. Issue #636.

  myjobsmm.py jobs [--category SLUG] [--since-days N] [--country-code MM] [--max-pages N]
  myjobsmm.py categories        the site's own thirty categories: slug, name, count (1 request)

WHAT IT IS. A Myanmar generalist (Next.js, server-rendered). Myanmar's other routes are
`jobnetmm.py` (2 077 live adverts) and `myanmargov.py` (the state portal's 182 notices, 181 of them
closed — an archive). This is the country's second living board.

THE RULES. `myjobs.com.mm` opens on `/`, `/jobs` and `/job`, `certain: True`, **no Crawl-delay**;
2 s is ours. The guard is taken on the exact path.

**THREE FIGURES THAT PREDICT ONE ANOTHER, CHECKED BEFORE WRITING.** On 2026-09-23 the home page
named **30 categories summing to 177**; `/jobs` paged **twelve** adverts and its pager named **15**
as the largest, so 15 × 12 = 180 bounds it; and if the board holds 177 then page 15 must carry
exactly **177 − 14 × 12 = 9**. *It carried 9, and page 16 carried none.* **That is what separates
this board from the others measured this week**: on Yemen HR and HireLebanese the total and the
per-category counts came off the SAME page, so they could agree by construction — here the
categories, the pager and the last page's fill are three separate statements, and a walk that
disagrees with them disagrees with something.

THE WALK. `/jobs?page=N`, **twelve a page — the board's own default, and it offers 18 in a
«/Page» selector**, so the bound below is arithmetic on the default and would move with it. The
walk runs until a page carries no advert. The largest page number is
read **from page 1** — *not from every page*: the pager is a sliding window, and page 15 itself
offers a link to 16, which is empty. The run prints the emitted count beside **the sum of the
categories** and beside the bound, and says whether they agree.

**THE FIELDS ARE READ BY WHAT THEY ARE, NEVER BY POSITION.** A card's text begins with a badge on
some cards («Latest») and with the employer's name on others, so the third element is the title on
one card and the location on the next. So: the **title** is the advert link's `aria-label`, the
**employer** is the text of the `/companies/…` link, and of what remains the **category** is
recognised by matching one of the site's own thirty category names — its vocabulary, not ours — the
**employment type** and the **location** by shape.

**A SALARY THE BOARD HIDES IS DECLARED, NOT DROPPED.** Six of the twelve cards on page 1 print
«Hidden» where a salary would be, others «Negotiable». *A field a site hides is not a field the site
lacks, and only the record can tell them apart*: `salary_hidden: true` and `salary_negotiable: true`
say which, and a figure is carried as written.

**A SALARY IS NOT FREE TEXT, AND THE TELEPHONE RULE DOES NOT TOUCH IT.** `350000 - 450000 MMK`
is twelve digits with a separator — the exact shape the nine-digit rule catches — and applying it
there destroyed **113 of the 115 written salaries** on the first full run. *The rule was right about
the shape and wrong about the field*: on the Syrian board the same threshold separated seven-digit
salaries from ten-digit numbers cleanly, and here it cannot, because the currency is smaller. The
guard caught it before delivery, with a real Myanmar figure in its fixture.

**WITHHELD:** e-mail addresses everywhere, and telephone numbers in FREE TEXT at a threshold of nine
digits;
`contacts_withheld` on every record. **Nothing is de-obfuscated**: the pages carry Cloudflare
`/cdn-cgi/l/email-protection#<hex>` addresses, that path is never requested, and the hex is never
decoded. The advert page is not fetched — the card carries what the board shows — `detail_read:
false`.

**TWO CATEGORIES THE SITE NAMES ALMOST ALIKE ARE CARRIED AS TWO.**
`sales-business-development` (32) and `sales-and-business-development` (1) are distinct slugs with
distinct counts. **They are not merged** — merging would invent a decision the site has not made.
*And it is the mirror of HireLebanese, where three ids lived under one truncated label and telling
them apart would have invented the distinction.* **Both times the rule is the same: carry what the
site exposes, never what we infer from it.**

**AND THE FINGERPRINT IS MUTE BY A NAMED CAUSE.** Two reads of the root give different md5 at
identical length: **1 342 positions differ, every one of them inside a
`/cdn-cgi/l/email-protection#<hex>`**, which Cloudflare re-keys per request. *Mute by a named cause
is not mute*: what held twice — the twelve adverts, the thirty counts, the pager — is what may be
carried.

`--category` walks one of the site's own slugs. `--since-days` keeps what the card dates within N
days («about 12 hours ago», «1 day ago» — the board prints an age, not a date, and the record
carries both the words and the day they imply). `--country-code` STAMPS.

Measured 2026-09-23 16:34–16:5x UTC by the declared client, the guard on the exact path, two reads
of the root and of the list: `/` 200 ×2, 812 162 B; `/jobs` 200 ×2, 523 096 B — 12 adverts, pager
naming 15; `/jobs/category/sales-business-development` 200, 273 139 B — 12 adverts, its pager on
`?functionalAreaId=…`; `/jobs?page=15` 200, **9 adverts as predicted**; `/jobs?page=16` 200, none.
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

HOST = "myjobs.com.mm"
PAGE_SIZE = 12
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

CARD_RE = re.compile(r'<div class="col-span-1">')
AD_RE = re.compile(r'href="(/jobs/(?!category)[a-z0-9\-]+)"[^>]*aria-label="([^"]*)"')
COMPANY_RE = re.compile(r'href="(/companies/[a-z0-9\-]+)"')
# The name is the FIRST `<p>` after the link, and the count the parenthesis further on. Taking
# «the first non-digit string of the block» instead returned `>` — the capture's own first
# character — and every category then read zero against the cards. *A name extracted by
# elimination is a name nobody chose.*
CAT_RE = re.compile(r'href="/jobs/category/([a-z0-9\-]+)"[^>]*>.{0,300}?<p[^>]*>(.{0,120}?)</p>.{0,400}?\((?:<!-- -->)?(\d[\d,]*)(?:<!-- -->)?\s*(?:<!-- -->)?Jobs', re.S)
PAGER_RE = re.compile(r'href="/jobs\?page=(\d+)"')
AGE_RE = re.compile(r"^(?:about\s+)?(\d+|an?)\s+(hour|day|week|month|minute)s?\s+ago$", re.I)
TYPE_WORDS = ("Full-time", "Part-time", "Contract", "Internship", "Freelance", "Temporary", "Remote")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
RUN_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{5,}\d(?!\w)")
DATE_TEXT_RE = re.compile(r"\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}|\d{4}-\d{2}-\d{2}")
DIGITS_FOR_A_PHONE = 9
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[myjobsmm] {msg}", file=sys.stderr)


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


def request(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    if parts.path.startswith("/cdn-cgi/"):
        die(f"{url}: the obfuscated-address path is never requested and never decoded", EXIT_REFUSED)
    if re.search(r"/(?:login|register|signup)\b", parts.path, re.I):
        die(f"{url}: an account path is never requested", EXIT_REFUSED)
    a = gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=a.get("crawl_delay") or 2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
                                                         "Accept-Language": "en, my"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def pieces(markup):
    """A card's visible strings, in the order it writes them — with the SVGs dropped."""
    t = re.sub(r"<!--[^>]*-->", "", markup or "")
    t = re.sub(r"(?s)<svg.*?</svg>", "", t)
    t = re.sub(r"(?s)<style.*?</style>", "", t)
    return [htmlmod.unescape(x).strip() for x in re.sub(r"<[^>]+>", "\x01", t).split("\x01") if x.strip()]


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)

    def one(m):
        run = m.group(0)
        if DATE_TEXT_RE.fullmatch(run.strip()):
            return run
        if sum(1 for c in run if c.isdigit()) < DIGITS_FOR_A_PHONE:
            return run
        return "[telephone withheld]"

    return RUN_RE.sub(one, s).strip() or None


def money(s):
    """A salary is a LABELLED field printing an amount — the telephone rule does not apply to it.

    **Measured before delivery, by the guard: `350000 - 450000 MMK` became
    `[telephone withheld] MMK`, and 113 of the 115 written salaries on the board were destroyed
    the same way.** A Myanmar salary range is twelve digits with a separator, which is exactly the
    shape the nine-digit rule exists to catch — *the rule was right about the shape and wrong about
    the field*. On the Syrian board the same threshold separated salaries (seven digits) from
    numbers (ten) cleanly; here it cannot, and the difference is the currency, not the rule.

    So the phone rule is not applied to a field whose meaning is known. The e-mail scrub stays,
    costing nothing. *Free text — a title, an employer's name — keeps both.*
    """
    return MAIL_RE.sub("[e-mail withheld]", s).strip() or None if s else None


def days_of(age):
    """«about 12 hours ago» → 0, «1 day ago» → 1, «2 weeks ago» → 14; None when unread."""
    m = AGE_RE.match((age or "").strip())
    if not m:
        return None
    n = 1 if m.group(1).lower() in ("a", "an") else int(m.group(1))
    unit = m.group(2).lower()
    return {"minute": 0, "hour": 0, "day": n, "week": n * 7, "month": n * 30}[unit] if unit in ("minute", "hour") else \
        {"day": n, "week": n * 7, "month": n * 30}[unit]


def categories_of(markup):
    """The site's own categories: `[(slug, name, count)]`, in the order the home page writes them."""
    out = []
    for slug, name, count in CAT_RE.findall(markup or ""):
        label = " ".join(htmlmod.unescape(re.sub(r"<[^>]+>|<!--[^>]*-->", "", name)).split())
        out.append((slug, label or slug, int(count.replace(",", ""))))
    return out


def cards_of(markup, cat_names):
    """The page's advert cards → `[dict]`.

    **Read by what each field IS, never by its position.** Some cards open with a badge
    («Latest») and others with the employer's name, so the third string is a title on one card
    and a location on the next. The title comes from the link's `aria-label`, the employer from
    the `/companies/` link, and of what remains the category is the one the SITE names — its
    own thirty labels — the type and the place by shape.
    """
    out = []
    for block in CARD_RE.split(markup or "")[1:]:
        ad = AD_RE.search(block)
        if not ad:
            continue
        strings = pieces(block)
        company = COMPANY_RE.search(block)
        employer = None
        if company:
            slug_words = company.group(1).rsplit("/", 1)[-1]
            for s in strings:
                if s and s.lower().replace(" ", "-").replace(",", "").replace(".", "") in slug_words:
                    employer = s
                    break
            if employer is None:
                for s in strings:
                    if s not in ("Latest", "Highlight", "Save") and not AGE_RE.match(s):
                        employer = s
                        break
        title = htmlmod.unescape(ad.group(2)).strip() or None
        rest = [s for s in strings if s not in (title, employer)]
        category = next((s for s in rest if s in cat_names), None)
        etype = next((s for s in rest if s in TYPE_WORDS), None)
        age = next((s for s in rest if AGE_RE.match(s)), None)
        salary = next((s for s in rest if s in ("Hidden", "Negotiable")), None)
        place = next((s for s in rest if "," in s and s not in (category, etype, salary)), None)
        if salary is None:
            salary = next((s for s in rest if s not in (category, etype, age, place, "Latest", "Highlight", "Save")
                           and re.search(r"\d", s)), None)
        out.append({"path": ad.group(1), "title": title, "employer": employer, "company_path": company.group(1) if company else None,
                    "category": category, "employment_type": etype, "place": place, "salary": salary, "age": age})
    return out


def record(c, stamp):
    ident = c["path"].rsplit("-", 1)[-1]
    rec = {
        "source": "myjobsmm", "country": stamp,
        "ledger_id": f"myjobsmm:{ident}", "id": ident,
        "url": f"https://{HOST}{c['path']}",
        "title": scrub(c["title"]), "employer": scrub(c["employer"]),
        "company_url": f"https://{HOST}{c['company_path']}" if c["company_path"] else None,
        "place": c["place"], "category": c["category"], "employment_type": c["employment_type"],
        "posted_as_written": c["age"], "posted_days_ago": days_of(c["age"]),
        "detail_read": False, "contacts_withheld": True,
    }
    # **A salary the board HIDES is declared, not dropped** — «Hidden» and «Negotiable» are two
    # different statements, and neither is «no salary field».
    if c["salary"] == "Hidden":
        rec["salary_hidden"] = True
    elif c["salary"] == "Negotiable":
        rec["salary_negotiable"] = True
    elif c["salary"]:
        rec["salary_as_written"] = money(c["salary"])
    return rec


def read_categories():
    code, body = request(f"https://{HOST}/")
    if code != 200:
        note(f"the home page answered HTTP {code} — the site's own category counts were not read, "
             f"so the walk has no second witness this run.")
        return []
    return categories_of(body)


def cmd_categories(a):
    cats = read_categories()
    for slug, name, count in cats:
        print(json.dumps({"slug": slug, "name": name, "count": count}, ensure_ascii=False))
    note(f"{th(len(cats))} category(ies) read from the home page, summing to "
         f"{th(sum(c for _s, _n, c in cats))}. The list itself states no total.")


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    cats = read_categories()
    names = {n for _s, n, _c in cats}
    total = sum(c for _s, _n, c in cats) if cats else None
    if a.category and cats and a.category not in [s for s, _n, _c in cats]:
        die(f"--category {a.category}: the site does not name that slug. It names: "
            + ", ".join(s for s, _n, _c in cats), EXIT_BROKEN)

    base = f"https://{HOST}/jobs/category/{a.category}" if a.category else f"https://{HOST}/jobs"
    rows, seen, page, bound = [], set(), 0, None
    while True:
        page += 1
        url = base + (f"?page={page}" if page > 1 else "")
        code, body = request(url)
        if code == 404:
            die(f"{url}: HTTP 404 — the list is gone", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if page == 1:
            # **The largest page number is read from PAGE 1 only.** The pager is a sliding
            # window: page 15 itself links to 16, which carries nothing. A bound taken from
            # every page would follow the window instead of bounding the walk.
            bound = max((int(x) for x in PAGER_RE.findall(body)), default=1)
        found = cards_of(body, names)
        if page == 1 and not found:
            die(f"{url}: 200 and no card — the template changed; this is not an empty board", EXIT_PARTIAL)
        if not found:
            page -= 1
            break
        fresh = [c for c in found if c["path"] not in seen]
        if page > 1 and not fresh:
            die(f"page {th(page)} repeats the previous page's advertisements — the walk ended at "
                f"{th(len(rows))}", EXIT_PARTIAL)
        for c in fresh:
            seen.add(c["path"])
            rows.append(c)
        if a.max_pages and page >= a.max_pages:
            break

    kept = [record(c, stamp) for c in rows
            if not (a.since_days and (days_of(c["age"]) is None or days_of(c["age"]) > a.since_days))]
    for rec in kept:
        print(json.dumps(rec, ensure_ascii=False))

    dropped = len(rows) - len(kept)
    note(f"{th(len(kept))} emitted over {th(page)} page(s) of {PAGE_SIZE}"
         + (f", {th(dropped)} left out by --since-days" if dropped else "")
         + (f"; the list states no total, and the home page's {th(len(cats))} categories sum to {th(total)}"
            if cats else "; the list states no total and the categories were not read")
         + (f" — {'they agree' if total == len(rows) else f'{th(abs(total - len(rows)))} apart'}"
            if total is not None and not (a.category or a.max_pages) else "")
         + ".")
    if bound and not (a.category or a.max_pages):
        note(f"the pager named {th(bound)} as its largest page on page 1, so {th(bound)} × {PAGE_SIZE} = "
             f"{th(bound * PAGE_SIZE)} bounds the walk; {th(page)} page(s) were walked and the last "
             f"carried {th(len(rows) - PAGE_SIZE * (page - 1))}"
             + (f" — the bound, the categories and the last page's fill agree" if total == len(rows) else
                f", against the {th(total)} the categories sum to" if total is not None else "") + ".")
    if cats and not (a.category or a.since_days or a.max_pages):
        mine = {}
        for c in rows:
            if c["category"]:
                mine[c["category"]] = mine.get(c["category"], 0) + 1
        ok = [n for _s, n, c in cats if mine.get(n, 0) == c]
        off = [f"{n}: site {c}, read {mine.get(n, 0)}" for _s, n, c in cats if mine.get(n, 0) != c]
        note(f"{th(len(ok))} of {th(len(cats))} category counts the site states are the counts the "
             f"cards give" + (f" — APART: {'; '.join(off[:6])}" + ("…" if len(off) > 6 else "") if off else "")
             + ". Two of its categories are named almost alike and are NOT merged: the site names "
               "them separately, and merging would invent a decision it has not made.")
    # **A field the cards sometimes lack is COUNTED, not left as a silent null.** Two of the 177
    # carry no `/companies/` link at all, so no name could be read: that is the site's doing and
    # the run says how often rather than leaving two nulls to be discovered by whoever reads the
    # output.
    faceless = sum(1 for r in kept if not r["employer"])
    typeless = sum(1 for r in kept if not r["employment_type"])
    if faceless or typeless:
        note((f"{th(faceless)} card(s) carry no employer — the site prints no company link on them "
              f"and no name was read; " if faceless else "")
             + (f"{th(typeless)} carry no employment type; " if typeless else "")
             + "counted, never guessed.")
    hidden = sum(1 for r in kept if r.get("salary_hidden"))
    nego = sum(1 for r in kept if r.get("salary_negotiable"))
    note(f"salary hidden on {th(hidden)} and «Negotiable» on {th(nego)} of {th(len(kept))} — a field "
         f"the board hides is declared, not dropped.")
    note("advert pages NOT read (`detail_read: false`); contacts scrubbed; the obfuscated-address "
         "path is never requested and its hex never decoded.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the cards state a city, not a country.")
    if not kept:
        note("0 emitted — check the filters before reading this as an empty board.")


def main(argv=None):
    p = argparse.ArgumentParser(description="MyJobs (Myanmar) — the list walked by GET, checked against the home page's thirty category counts and the pager's own bound. Issue #636.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the board (1 request a page of 12, plus one for the categories)")
    j.add_argument("--category", help="walk one of the site's own category slugs (see `categories`)")
    j.add_argument("--since-days", dest="since_days", type=int, help="keep cards the board dates within N days")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N pages (0 = the board)")
    j.set_defaults(fn=cmd_jobs)
    c = sub.add_parser("categories", help="the site's own categories and their counts (1 request)")
    c.set_defaults(fn=cmd_categories)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
