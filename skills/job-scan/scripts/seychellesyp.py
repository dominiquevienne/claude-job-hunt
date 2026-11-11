#!/usr/bin/env python3
"""Seychelles YP jobs (`www.seychellesyp.com/jobs`) — the jobs section of a Seychellois
business directory, served whole on the server: `/jobs/all` pages twenty cards and PRINTS
ITS OWN TOTAL (`<div class="total"><strong>33</strong> results` on 2026-11-11), the pager is
a bare segment (`/jobs/all/2`, `rel="next"`), and the ad page is a labelled info block plus
a presentation. Issue #716.

  seychellesyp.py list [--max N]                      the walk, 1 request per page of 20
  seychellesyp.py ad --url <https://www.seychellesyp.com/job/<id>/<slug>>

THE RULES, read ENTIRE before any bundle (200, 575 B). `User-agent: *` — fourteen
`Disallow` and NO `Allow`, none of them matching `/jobs`, `/jobs/all`, its pager or
`/job/<id>/<slug>`; **no `Host:` line and no `Sitemap:` line**, so no other canonical name
and no enumerator on a third host. A second group NAMES Yandex, Baiduspider ×3, AhrefsBot,
DuckDuckBot, aspiegelbot, sogouspider and GPTBot and gives it `Crawl-delay: 10`: it does not
bind us, and `delay_for` says so. **3 s is OURS** — above this repository's usual 2 s
because the operator writes 10 for every crawler he names, and an unwritten threshold is not
an absence of one. `/admin/`, `/user/`, `/edit/`, `/sign-in/`, `/redir/`, `/gadgets/`,
`/comments/reply/`, `/getnav*`, `/getlogin`, `/getsearch`, `/autocomplete`, `/userszone` and
`*/get_table_results` are never sent (exit 7 before the gate) — the intention is honoured,
not the prefix match.

THE LIST. `/jobs/all` (200, 24 777 B): `<div class="company">` cards, each
`<h4><a href="/job/<id>/<slug>">` plus a `more_button` link to the SAME address — **40 raw
hrefs for 20 distinct ads, so an extractor that reads HREFS doubles its count**; this one
reads one card per `<div class="company">` chunk and takes only the heading's link, so the
chunking settles it and a per-page dedup here is DEAD CODE (measured: the bench's mutation
of it came back green). **The dedup that can fire is ACROSS pages**, in `merge` — an ad
inserted between the two requests shifts the window and pushes page 1's twentieth onto
page 2 — with `<div class="address">` naming the POSTER (`/company/<id>/<slug>`, «JOB BY JOBO.sc»,
a feeder and not the employer), a `cont` line («8 days ago | Employee | Full Time») and a
TRUNCATED `cont desc`, which is why no description is emitted from the list. Page 2
(`/jobs/all/2`, 200, 20 512 B) holds 13 and carries no `rel="next"`: the walk ends of
itself, and 20 + 13 = 33 = the printed total.

THE AD. `/job/<id>/<slug>` (200, ~17–24 KB), a block of `<div class="label">` headings
measured on SEVEN ads spread over the thirty-three (first, quartiles, median, last two):
`Announced`, `Job Status`, `Job Type`, `Expiration Date`, `Job Title`, `Work At`,
`Job Presentation` on 7/7, `Job Category` on 6/7. **The two labels are placed by what they
CARRY, never by what they say: `Job Status` holds «Full Time» and `Job Type` holds
«Employee» — and both were CONSTANT on 7/7, so they discriminate nothing on that
sample.** Dates are `dd/mm/yyyy`. `How to Apply` carries an outward link to the feeder's own
page (`https://jobo.sc/jobs/<slug>/`), an address a candidate can follow and not a way to
reach a person, so it is emitted and nothing is withheld for it.

**WITHHELD, and the witness is DERIVED from what the redaction actually took.** `Work At`
holds the employer's name and, inside a `<small>`, its TELEPHONE — on 7/7 — so the name is
emitted and the number leaves the record as `employer_phone`. The presentation is scrubbed
of e-mail addresses and Seychellois numbers; on the seven measured it carried NEITHER, so
`description_contacts_withheld` is False there and the record does not claim a redaction
nobody filed. The poster's own address block (its logo, its street, its number) is never
emitted.

Measured 2026-11-11 16:29–16:35 UTC by the declared client, the guard on the exact path
first and in a turn distinct from the retrieval, `bin/fetch-body.py`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import html as htmlmod
import json
import re
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA
from _withheld import withheld_a_contact
from _zero import EXIT_INDETERMINATE, empty_first_page

HOST = "www.seychellesyp.com"
BASE = "https://" + HOST
LIST = BASE + "/jobs/all"
COUNTRY = "SC"

EXIT_BROKEN, EXIT_GONE = 2, 3
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

#  The paths this host refuses in writing, plus the two login routes. Written out so the
#  refusal is OURS and reaches a reader, instead of resting on a prefix match the operator
#  may have mis-spelt: `/jobs/get_table_results` matches `*/get_table_results` and
#  `/jobsomething` would not match `/jobs`.
REFUSED_RE = re.compile(
    r"^/(?:admin|user|edit|sign-in|redir|gadgets|comments/reply|userszone"
    r"|getnavprofile|getnav|getlogin|getsearch|autocomplete)(?:/|$)"
    r"|/get_table_results$")

AD_RE = re.compile(r"^/job/(\d+)/(.+)$")
PAGE_RE = re.compile(r"^/jobs/all(?:/(\d+))?$")

CARD_RE = re.compile(
    r'<div class="company">(.*?)(?=<div class="company">|<div class="ad336">'
    r'|<div class="pages_container">|</main>|</body>)', re.S)
CARD_LINK_RE = re.compile(r'<h4><a href="/job/(\d+)/([^"]*)"[^>]*>(.*?)</a></h4>', re.S)
POSTER_RE = re.compile(r'<div class="address">.*?<a href="/company/(\d+)/([^"]*)"[^>]*>(.*?)</a>', re.S)
CONT_RE = re.compile(r'<div class="cont">(.*?)</div>', re.S)
NEXT_RE = re.compile(r'<a href="(/jobs/all/\d+)" class="pages_arrow" rel="next"')
TOTAL_RE = re.compile(r'<div class="total"><strong>(\d+)</strong>\s*results', re.S)

INFO_RE = re.compile(
    r'<div class="(?:info j_info|info)"><div class="label">([^<]+)</div>'
    r'(?:<div class="text[^"]*">(.*?)</div>|<b>(.*?)</b>)', re.S)
SMALL_RE = re.compile(r"<small>.*?</small>", re.S)
APPLY_RE = re.compile(r'<h3>How to Apply</h3>(.*?)(?=<div class="review_reply")', re.S)
HREF_RE = re.compile(r'href="(https?://[^"]+)"')
DMY_RE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")

MAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
#  Seychellois numbers are SEVEN digits, landlines on 4 and mobiles on 2. STRICT: an
#  explicit +248, or seven digits SEPARATED as the site writes them («428 5800»). A bare
#  run of seven digits is not matched -- it reaches a salary, a reference or a year range.
TEL_RE = re.compile(r"(?<![\d+])(?:\+\s?248[\s.\-]?[24]\d{2}[\s.\-]?\d{4}"
                    r"|[24]\d{2}[\s.\-]\d{4})(?![\d])")

_PACE = Pace(HOST, own=3.0)   # `Crawl-delay: 10` binds the NAMED crawlers, not us; 3 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[seychellesyp] {msg}", file=sys.stderr)


def refuse_if_written_off(url):
    """A path this host refuses in writing is never sent, and the refusal SAYS so.

    One point of application, called from both entries: `request`, which protects any
    address this script builds, and `cmd_ad`, BEFORE the shape test -- without which this
    branch could not fire from the command line at all, `/admin/x` being rejected one line
    higher as «not a job address». A guard that cannot fail on what it claims to watch is
    worse than absent (`CLAUDE.md` §4 ter).
    """
    if REFUSED_RE.search(urllib.parse.urlsplit(url).path):
        die(f"{url}: a path this host refuses in writing — never sent", EXIT_REFUSED)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    refuse_if_written_off(url)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def th(n):
    return f"{n:,}".replace(",", " ")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def date_of(markup):
    """`dd/mm/yyyy` → `yyyy-mm-dd`, the `<small>` dropped FIRST.

    The cell is `<div class="text">04/11/2026<small>8 days ago</small></div>`, and the
    relative part is the site's own arithmetic against the day it served the page. Taking
    the text of the whole cell leaves `04/11/2026 8 days ago`, which `DMY_RE` does not
    match -- so `iso` returned the string AS WRITTEN and the field was ISO on an ad whose
    `<small>` happened to be empty and dd/mm/yyyy on the others. A date field right on one
    record and wrong on six reads exactly like a date.
    """
    written = text(SMALL_RE.sub("", markup or ""))
    m = DMY_RE.match((written or "").strip())
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else (written or None)


def scrub(prose):
    """Remove what reaches a person, and say WHAT was taken.

    The witness is DERIVED from the substitutions actually made -- never from whether a
    block was non-empty. A name in `withheld_fields` nobody filed lies about OUR
    discretion, and the output is identical either way (#1007).
    """
    if not prose:
        return prose, ()
    taken = []
    out, n = MAIL_RE.subn("[e-mail withheld]", prose)
    if n:
        taken.append("email")
    out, n = TEL_RE.subn("[telephone withheld]", out)
    if n:
        taken.append("telephone")
    return out, tuple(taken)


def cards(body):
    """The cards of one list page.

    Each ad is linked TWICE (its heading and its «Apply for this Job» button), and that is
    settled by the CHUNKING: one card per `<div class="company">`, and only the heading's
    link is read. A dedup inside this function could therefore never fire -- the bench
    proved it green -- so it is not written here. The one that can fire is `merge`.
    """
    out = []
    for chunk in CARD_RE.findall(body):
        link = CARD_LINK_RE.search(chunk)
        if not link:
            continue
        jid, slug, title = link.group(1), link.group(2), text(link.group(3))
        if not title:
            continue
        poster = POSTER_RE.search(chunk)
        conts = [text(c) for c in CONT_RE.findall(chunk)]
        out.append({
            "source": "seychellesyp", "country": COUNTRY,
            "ledger_id": f"seychellesyp:{jid}", "id": jid,
            "url": f"{BASE}/job/{jid}/{slug}",
            "title": title,
            #  The directory's own feeder, named «JOB BY» on the card. It is NOT the
            #  employer -- the ad page's `Work At` is -- so it is emitted under its own name.
            "posted_by": text(poster.group(3)) if poster else None,
            "posted_relative": conts[0] if conts else None,
            "language": "en",
        })
    return out


def merge(groups):
    """The pages' cards into one list, each ad read once — `(records, seen_twice)`.

    The board pages twenty at a time and the walk takes one request per page: an ad posted
    BETWEEN two requests shifts the window and pushes the twentieth of page 1 onto page 2.
    Emitting it twice would put the same vacancy in the ledger under one `ledger_id` twice,
    and the count would exceed the total the board prints without anything being wrong with
    the board. The note says how many were seen twice rather than hiding it.
    """
    out, seen, twice = [], set(), 0
    for g in groups:
        for c in g:
            if c["id"] in seen:
                twice += 1
                continue
            seen.add(c["id"])
            out.append(c)
    return out, twice


def cmd_list(a):
    groups, pages, total, url, capped = [], 0, None, LIST, False
    while url:
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}",
                EXIT_GONE if code == 404 and pages == 0 else EXIT_INDETERMINATE)
        cs = cards(body)
        if not cs and pages == 0:
            die(empty_first_page("seychellesyp", body, what="card",
                                 where=url, what_asked="the jobs board"),
                EXIT_INDETERMINATE)
        pages += 1
        if total is None:
            m = TOTAL_RE.search(body)
            total = int(m.group(1)) if m else None
        groups.append(cs)
        if a.max and sum(len(g) for g in groups) >= a.max:
            capped = True
            break
        nxt = NEXT_RE.search(body)
        url = BASE + nxt.group(1) if nxt else None
    out, twice = merge(groups)
    if capped and a.max:
        out = out[:a.max]
    for c in out:
        print(json.dumps(c, ensure_ascii=False))
    stated = f"board states {th(total)}" if total is not None else "the board stated no total"
    seen_twice = f" ({th(twice)} ad(s) on two pages, read once)" if twice else ""
    if capped:
        note(f"{th(len(out))} emitted over {pages} page(s) — walk capped at the requested "
             f"{th(a.max)}; {stated}{seen_twice}.")
    elif total is None:
        note(f"{th(len(out))} emitted over {pages} page(s) — the walk ended of itself and "
             f"THIS ROUTE PRINTED NO TOTAL: the size of the board is NOT ESTABLISHED{seen_twice}.")
    elif len(out) == total:
        note(f"{th(len(out))} emitted over {pages} page(s) — {stated}, and the walk ended "
             f"of itself: the two agree{seen_twice}.")
    else:
        note(f"{th(len(out))} emitted over {pages} page(s) — {stated}: "
             f"{th(abs(total - len(out)))} {'short' if len(out) < total else 'over'}{seen_twice}.")
    note("cards only — the list's own description is TRUNCATED, so none is emitted from it; "
         "`ad --url` reads the ad's labelled block and its presentation, scrubbed.")


def record(body, jid, slug, url):
    info = {}
    for label, div, bold in INFO_RE.findall(body):
        info.setdefault(label.strip(), div or bold)
    if "Job Title" not in info or "Work At" not in info:
        return None
    #  `Work At` is the employer's name and, inside a <small>, its telephone. The name is
    #  emitted; the number leaves the record and the witness says so.
    work_raw = info["Work At"]
    employer = text(SMALL_RE.sub("", work_raw))
    took_employer = bool(TEL_RE.search(text(work_raw) or "")
                         or MAIL_RE.search(text(work_raw) or ""))
    desc, from_prose = scrub(text(info.get("Job Presentation")))
    apply_url = None
    ap = APPLY_RE.search(body)
    if ap:
        hrefs = [h for h in HREF_RE.findall(ap.group(1)) if "seychellesyp.com" not in h]
        apply_url = hrefs[0] if hrefs else None

    withheld = sorted(set((["employer_phone"] if took_employer else [])
                          + list(from_prose)))
    out = {
        "source": "seychellesyp", "country": COUNTRY,
        "ledger_id": f"seychellesyp:{jid}", "id": jid, "url": url,
        "title": text(info["Job Title"]),
        "employer": employer,
        "posted": date_of(info.get("Announced")),
        "expires": date_of(info.get("Expiration Date")),
        #  Placed by what they CARRY and not by what they say: this host's `Job Status`
        #  holds «Full Time» and its `Job Type` holds «Employee». Both were CONSTANT on
        #  the seven ads measured, so neither discriminates anything on that sample.
        "schedule": text(info.get("Job Status")),
        "engagement": text(info.get("Job Type")),
        "category": text(info.get("Job Category")),
        "description": desc,
        "description_contacts_withheld": bool(from_prose),
        "apply_url": apply_url,
        "withheld_fields": withheld,
        "language": "en",
    }
    #  The declaration follows what the redaction ACTUALLY took.
    if withheld_a_contact(withheld):
        out["contacts_withheld"] = True
    return out


def cmd_ad(a):
    refuse_if_written_off(a.url)
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc not in (HOST, "seychellesyp.com") or not m:
        die(f"{a.url}: not a job address (https://{HOST}/job/<id>/<slug>)")
    url = f"{BASE}/job/{m.group(1)}/{m.group(2)}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_INDETERMINATE)
    rec = record(body, m.group(1), m.group(2), url)
    if rec is None:
        die(f"{url}: 200 without its `Job Title` and `Work At` labels — the template "
            f"changed; this is not an ad without an employer", EXIT_INDETERMINATE)
    print(json.dumps(rec, ensure_ascii=False))
    took = rec.get("withheld_fields") or []
    note(f"{url}: read from its labelled block and its presentation; "
         + (f"withheld {', '.join(took)}" if took
            else "the redaction took nothing, and the record says so")
         + "; the poster's own address block never emitted.")


def main():
    p = argparse.ArgumentParser(
        description="Seychelles YP jobs — the walk of `/jobs/all` against the total the "
                    "board prints, each ad from its labelled block. Issue #716.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the walk of /jobs/all, 20 cards a page")
    l_.add_argument("--max", type=int, default=0, help="stop after N records")
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
