#!/usr/bin/env python3
"""Vaga Servisu TL (`www.vagaservisu.com`) — a Blogger blog whose posts are Timor-Leste's NGO, UN and government vacancies, mixed with scholarships and public notices: the Blogger feed `/feeds/posts/default?alt=json` on the blog's own host states its total («openSearch:totalResults» 1 551 on 2026-11-05), carries each post's title, dates, labels and body, and **serves fewer entries than asked without saying so**. Issue #687.

  vagaservisu.py list [--pages N] [--kind vacancy|scholarship|other]   the feed's posts, newest first, the stated total beside them
  vagaservisu.py ad --url <https://www.vagaservisu.com/<yyyy>/<mm>/<slug>.html>

THE RULES. `/robots.txt` could not be read (`state: unrecognised`, `certain: False`) — an absence of
rules, so open, by the owner's decision of 2026-09-13 (#283). Nothing is written for any agent, so
**no `Crawl-delay` is declared and 3 s is ours**. The guard is taken on the exact path by `_robots`
before every request; `/search` is never asked for (the feed suffices), so no label or search page
is fetched.

THE WALK ADVANCES BY WHAT IT RECEIVED, NEVER BY WHAT IT ASKED. Measured 2026-11-05: the feed
declares `itemsPerPage=500` and `totalResults=1551`, and the windows `start-index=` 1 / 501 / 1001 /
1501 at `max-results=500` return **125, 145, 107 and 51** entries — **428 distinct against 1 551,
27.6 %, with no error, no non-zero code and no message**. The pagination is correct on the INDICES:
`start-index=126` after a page of 125 returns 108 entries with **zero overlap**, union exactly
233 = 125 + 108, and its first entry resumes on the same day the previous page stopped. So the
number of entries served is capped at a value that VARIES, and **the cause is not established here
and is not asserted**: what is measured is the behaviour. **And whether a page is short depends on the SIZE ASKED, which is why this
is not a property of the host**: at `max-results=50` the same feed serves 50, 50, 50 — full pages,
on which a walk stepping by `max-results` is correct and this guard is latent. So the defect is not
«this host serves short pages» but «no page size is known to be honoured, and a short page is
silent». Stepping by what was received is the only form correct at EVERY size; stepping by
`max-results` — the form `empleosenuruguay.py` uses, correct on ITS host, where 3 750 + 27 closed on
the stated total — is correct only at sizes the host happens to honour, which is neither knowable in
advance nor stable. The platform predicts the ROUTE, not the walk. Hence: `start += len(entries)`,
and **only an EMPTY page ends the walk** — a short page never does.

THE STATED TOTAL IS NOT A WITNESS FOR THE VACANCIES. `totalResults` counts ALL POSTS, and the blog
mixes vacancies with scholarships and public notices (22 `Anunsiu Vaga` against 3 scholarships in
the newest 25). The honest per-type witness is the feed's own label-scoped `totalResults`, which
Blogger states for each label: on 2026-11-05, `Anunsiu Vaga` 384 and `Job Vacancy` 801 — **the
labels are not synonymous**, which the first page cannot show (22 against 21 there, an agreement
that proves nothing). Inclusion is measured on MEMBERS and never on cardinals: 177 `Job Vacancy`
carry no `Anunsiu Vaga` and 2 `Anunsiu Vaga` carry no `Job Vacancy`.

**NOTHING IS DROPPED, AND THE CLASSIFICATION IS OURS AND SAID SO.** A label-only filter loses real
vacancies: of the 126 held posts carrying no vacancy label, the first is a scholarship but the
median is «National/International Consultant … — UNICEF» and the last is a PNTL police recruitment,
both vacancies labelled only by their ORGANISATION (`UN`, `UNICEF`, `CRS`, `CARE`) — and 4 carry a
title that begins with «Vaga Servisu» («job vacancy» in Tetum) with no vacancy label at all. So
every post is emitted with a `kind` derived from its labels AND its title, the distribution printed
beside the count, and `--kind` left to the caller. A board made poor by our own filter reads exactly
like a board that is poor.

THE POST. `ad --url` asks the feed for the one post by `path=`, one request, the same entry shape.
**What an entry carries is the blog's own rewrite: no JobPosting JSON-LD anywhere (0 of the 25
newest), so no structured employer — and 15 of those 25 bodies carry a recruiter's e-mail address
and 4 a Timor-Leste telephone, so both are withheld and `withheld_fields` is DERIVED from what was
actually removed, never asserted.** The phone pattern is anchored on Timor-Leste's own forms
(`+670`, 8-digit mobiles beginning 7, 7-digit landlines beginning 3) and was tried in both
directions against USD amounts — `USD 1,200`, `$35000`, `$1,500-$2,000` are untouched — because the
country pays in US dollars and a digit-count rule on a currency is how 113 of 115 salaries were
once destroyed.

Measured 2026-11-05 08:34–08:38 UTC by the declared client, the guard on the exact path in a turn
distinct from the retrieval: the feed 519 241 B for 25 entries, 1 551 stated; the four windows
above; `start-index=126` 108 entries, disjoint; the label-scoped feeds 384 / 801 / 6.
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
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
from _withheld import withheld_a_contact

HOST = "www.vagaservisu.com"
FEED = f"https://{HOST}/feeds/posts/default"
PER_PAGE = 500   # asked large ON PURPOSE: at 500 this host serves short pages, so the
                 # step-by-received is EXERCISED by the live walk instead of being latent
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# Timor-Leste: +670, mobiles of 8 digits beginning 7, landlines of 7 beginning 3.
# Tried against USD amounts in both directions -- the country pays in US dollars.
PHONE_RE = re.compile(r"(?<![\d+])(?:\+?670[\s\-]?)?(?:7\d{3}[\s\-]?\d{4}|3\d{2}[\s\-]?\d{4})(?!\d)")
POST_RE = re.compile(r"^/(\d{4})/(\d{2})/([a-z0-9\-]+)\.html$")
REFUSED_RE = re.compile(r"^/search(?:/|\?|$)")

# The board's own labels, read from the feed. Ours is the MAPPING, not the labels.
VACANCY_LABELS = {"anunsiu vaga", "vaga servicu", "vaga servisu", "job vacancy", "vacancy announcement", "job announcement", "job advertisement", "recruitment", "rekrutamentu"}
SCHOLARSHIP_LABELS = {"anunsiu bolsa estudu", "bolsa estudo", "bolsa estudu", "scholarship"}
# The title says it when the label is silent -- 4 of the 126 unlabelled posts held.
VACANCY_TITLE_RE = re.compile(r"(?i)\b(?:vaga\s*servisu|anunsiu\s*vaga|vacanc|recruitment|rekrutamentu|consultant|internship)\b")
SCHOLARSHIP_TITLE_RE = re.compile(r"(?i)\b(?:bolsa\s*estudu|bolsa\s*estudo|scholarship)\b")

_PACE = Pace(HOST, own=3.0)   # no Crawl-delay written; 3 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[vagaservisu] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url):
    if REFUSED_RE.search(urllib.parse.urlsplit(url).path):
        die(f"{url}: the blog's search and label pages are never asked for -- the feed suffices", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "application/json,text/html;q=0.9", "Accept-Language": "en"})
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
    t = re.sub(r"<script\b.*?</script>", " ", markup or "", flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    """Returns (text, what was ACTUALLY removed) -- the witness is derived, never asserted."""
    if not s:
        return None, []
    taken = []
    if MAIL_RE.search(s):
        taken.append("email")
        s = MAIL_RE.sub("[e-mail withheld]", s)
    if PHONE_RE.search(s):
        taken.append("telephone")
        s = PHONE_RE.sub("[telephone withheld]", s)
    return (s.strip() or None), taken


def feed(url):
    code, body = request(url)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
    try:
        f = json.loads(body)["feed"]
    except (ValueError, KeyError, TypeError):
        die(f"{url}: 200 and not Blogger's JSON feed -- the shape changed", EXIT_PARTIAL)
    return f


def stated(f):
    """The feed's own total -- `openSearch$totalResults`. It counts ALL POSTS, not vacancies."""
    try:
        return int(f["openSearch$totalResults"]["$t"])
    except (KeyError, ValueError, TypeError):
        return None


def val(x):
    return (x or {}).get("$t") if isinstance(x, dict) else None


def kind_of(title, labels):
    """OURS, not the board's: a label-only rule loses vacancies labelled by organisation."""
    low = {(l or "").strip().lower() for l in labels}
    t = title or ""
    if low & VACANCY_LABELS or VACANCY_TITLE_RE.search(t):
        return "vacancy"
    if low & SCHOLARSHIP_LABELS or SCHOLARSHIP_TITLE_RE.search(t):
        return "scholarship"
    return "other"


def record(e):
    pid = (val(e.get("id")) or "").rsplit("post-", 1)[-1] or None
    url = next((l.get("href") for l in e.get("link", []) if l.get("rel") == "alternate"), None)
    title = htmlmod.unescape(val(e.get("title")) or "").strip() or None
    labels = [c.get("term") for c in e.get("category", []) if c.get("term")]
    body, taken = scrub(text(val(e.get("content")) or ""))
    author = next((val(a.get("name")) for a in e.get("author", []) if val(a.get("name"))), None)
    r = {
        "source": "vagaservisu", "country": "TL", "ledger_id": f"vagaservisu:{pid}", "id": pid, "url": url,
        "title": title, "labels": labels or None,
        "kind": kind_of(title, labels), "kind_is_ours": True,
        "published": (val(e.get("published")) or "")[:10] or None,
        "updated": (val(e.get("updated")) or "")[:10] or None,
        "blog_author": author,
        "text": body,
        "withheld_fields": taken or None,
        "language": "tet",
    }
    # **`contacts_withheld` is NOT the truthiness of `withheld_fields`**: that list
    # mixes what reaches a PERSON with what was dropped for another reason, and the
    # judgement lives at ONE point of the repository (`_withheld`, #1238) so that four
    # copies of it cannot drift. A name it does not classify RAISES, on purpose.
    # The key is ABSENT when nothing that reaches a person left the record -- the
    # repository's form, and an `else` branch breaks the in-suite mutation that proves
    # this guard is not inert. An absence is not a claim; a `False` would be one.
    if withheld_a_contact(r["withheld_fields"]):
        r["contacts_withheld"] = True
    return r


def cmd_list(a):
    pages = a.pages if a.pages else 2
    out, seen, total, walked, served = [], set(), None, 0, []
    start = 1
    while walked < pages:
        f = feed(f"{FEED}?alt=json&start-index={start}&max-results={PER_PAGE}")
        if total is None:
            total = stated(f)
            if total is None:
                die(f"{FEED}: 200 and no openSearch:totalResults in the feed -- the shape changed; not an empty blog", EXIT_PARTIAL)
        entries = f.get("entry") or []
        if not entries:
            if walked == 0:
                die(f"{FEED}: a feed that states {th(total)} and lists no entry", EXIT_PARTIAL)
            break      # **only an EMPTY page ends the walk -- a SHORT page never does**
        served.append(len(entries))
        new = 0
        for e in entries:
            r = record(e)
            if not r["id"] or r["id"] in seen:
                continue
            seen.add(r["id"])
            out.append(r)
            new += 1
        walked += 1
        if new == 0 or len(out) >= total:
            break
        start += len(entries)      # **BY WHAT WAS RECEIVED, never by PER_PAGE -- see the docstring**
    kept = [r for r in out if a.kind is None or r["kind"] == a.kind]
    for r in kept:
        print(json.dumps(r, ensure_ascii=False))
    dist = {}
    for r in out:
        dist[r["kind"]] = dist.get(r["kind"], 0) + 1
    short = [n for n in served if n < PER_PAGE]
    note(f"{th(len(kept))} emitted"
         + (f" of {th(len(out))} read (--kind {a.kind})" if a.kind else "")
         + f" from {walked} page(s) asked at {PER_PAGE}, served {served} -- the feed states {th(total)} posts, "
         + "which counts ALL POSTS and not vacancies.")
    if short:
        note(f"{len(short)} page(s) served fewer entries than asked ({short}) -- walked by what was RECEIVED, so nothing was skipped; a short page is not the end of the feed.")
    note("kind is OURS, derived from the labels and the title, not a field of the board: "
         + ", ".join(f"{k} {v}" for k, v in sorted(dist.items())) + ".")
    nw = sum(1 for r in out if r.get("contacts_withheld"))
    note(f"bodies read; a contact was removed from {nw} of {len(out)} -- `withheld_fields` names what was actually taken; the employers' own application routes never followed.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = POST_RE.match(parts.path)
    if parts.netloc not in (HOST, "vagaservisu.com") or not m:
        die(f"{a.url}: not a post address (https://{HOST}/<yyyy>/<mm>/<slug>.html)")
    f = feed(f"{FEED}?alt=json&path={urllib.parse.quote(parts.path)}")
    entries = f.get("entry") or []
    if not entries:
        die(f"{a.url}: the feed knows no post at this path -- gone", EXIT_GONE)
    r = record(entries[0])
    print(json.dumps(r, ensure_ascii=False))
    note(f"{a.url}: read from the feed's own entry; kind `{r['kind']}` is OURS; "
         + (f"withheld {', '.join(r['withheld_fields'])}" if r["withheld_fields"] else "nothing to withhold")
         + "; the application route never followed.")


def main():
    p = argparse.ArgumentParser(description="Vaga Servisu TL -- the Blogger feed's posts with its stated total beside them; the walk advances by what it RECEIVED. Issue #687.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the feed, newest first -- 2 pages unless --pages (the feed is an archive)")
    l_.add_argument("--pages", type=int, help=f"pages asked at {PER_PAGE} to walk; the host serves fewer and the walk steps by what it received")
    l_.add_argument("--kind", choices=("vacancy", "scholarship", "other"), help="emit only this kind; the classification is OURS, and nothing is dropped without --kind")
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
