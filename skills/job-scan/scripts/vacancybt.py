#!/usr/bin/env python3
"""VacancyBT (`www.vacancybt.com`, Bhutan): the vacancy blog, walked against the last page it declares — and the first board in this corpus whose redaction turns on the LABEL and not on the dialling code. Issue #683.

  vacancybt.py jobs [--max-pages N] [--country-code BT]     the walk, against the declared last page
  vacancybt.py ad --url https://www.vacancybt.com/<slug>/

WHAT IT IS. A WordPress blog that republishes the vacancy announcements of Bhutan's public bodies
and private employers — dzongkhag administrations, ministries, the referral hospital, Bhutan
Telecom, UNDP. Each post names its employer in its own title.

THE RULES. `www.vacancybt.com/robots.txt` is read: group `*`, `Disallow: /wp-admin/` with an
`Allow` for `admin-ajax.php` — neither on our paths — open, `certain: True`, no `Crawl-delay`;
3 s is ours. It also DECLARES a sitemap index, which is where the second witness below comes from.
The guard is taken on the exact path. *The card declares the `www.` form; the bare host answers
and is open too, and both are accepted for an advert URL.*

**TWO INDEPENDENT WITNESSES, AND THEY AGREE — which is the whole reason this board was taken
first.** The pager's own links carry the LAST page (`/page/32/` on 2026-11-03), 6 posts a page and
4 on the last, so **31 × 6 + 4 = 190**; and `post-sitemap.xml` declares **191** `<loc>`, of which
one is the site root — **190**. *Two enumerators, built differently, meeting at the same number.
`caribbeanjobsonline` uses the same shape: a page count is the witness where no item count is
stated, and this card's `witness: none` of 2026-09-17 is retired by it.*

**AND THE BOUNDARY IS VERIFIED, not inferred**: `/page/32/` answers 200 with 4 posts and
`/page/33/` answers **404**. So the declared last page is true at its edge, and the walk's stop
condition is the 404 the site really serves.

**78 % OF A POST PAGE IS CSS AND SCRIPT, AND IT POISONS EVERY MOTIF UNTIL IT IS STRIPPED.** The
page writes its own class names inside its stylesheet, so a bare search for `entry-title` or
`entry-content` matches the CSS FIRST: unstripped, `entry-title` occurs twice on an advert and the
first hit is a rule about `p:last-child`. Measured: 74 734 B of markup become **16 332** once
`<style>` and `<script>` are out, and the advert's real text is **1 431 characters**. *Same shape
as counting `<script>` tags on a page that writes the word in its prose — here it is the page's own
class names that lie.*

THE LIST. A post is an `<article>` CARRYING an `entry-title`, and that conjunction is the
discriminant: the bare class name renders 7 on a page that holds 6 posts, the seventh being the CSS
rule. Each post gives its URL, its title (which names the employer), **`<time datetime>` as an ISO
instant with Bhutan's `+06:00` offset**, and an excerpt.

**THE BLOG IS SERVED NEWEST FIRST IN THE LARGE, AND IT IS NOT STRICTLY MONOTONE — the bound
matters and the first version of this file asserted the stronger thing on 18 posts.** Measured on
the FULL walk of 190: **28 inversions out of 189 pairs**, nearly all between posts of the SAME DAY
and a handful jumping a few days. What holds at the level that decides: **all 53 posts of 2026
occupy positions 1 to 53**, page 1 is EXACTLY the six most recent (6 of 6), and position 190 is the
oldest. *So a truncation does keep the newest, and that is why **no sort is imposed** — a sort that
is not a condition of correctness is taste, and this repository's own tests say so. `jobsbotswana`
needs its sort because its file is served OLDEST first; here the need does not arise. But the
reason is now measured on 190 and not on 18, and «&nbsp;strictly descending&nbsp;» was an
eighteen-post property read as a board property.*

**AND THE ARCHIVE REACHES BACK SEVEN YEARS** — the sitemap's `lastmod` run from 2019-02-17 to
today — so the list is a history and not a shortlist, exactly like `emploi-lenouvelliste` (#777).
**The difference is decisive and it is why this board ships**: there, no date exists in any form, so
what is open is unknowable; here every post declares its own ISO instant, so a caller can decide.

**THE REDACTION IS ANCHORED, AND THIS IS THE FIRST BOARD OF THE CORPUS WHERE THE *LABEL* DECIDES.**
Its numbers are written `Tel: 17940918` and `Tel: 02327513` — **local, with no dialling code at
all** — so the `+975` alternative returns ZERO on them and only the labelled alternative catches
them. On the three boards measured before this one (`+509` twice, `+230` once) it was the opposite:
the number carried its code and no label. *So both halves of the anchor are load-bearing, and
WHICH one decides is a property of the board, never of the motif. A remedy transposes between
boards; neither of its halves may be dropped on the evidence of one.*

Measured 2026-11-03 22:1x–22:3x UTC by the declared client, the guard on the exact paths in a turn
of its own: `/robots.txt` read (`*`, `Disallow: /wp-admin/`, sitemap declared), the root 200
(91 858 B, md5 6646837145dc) with 6 posts and `/page/32/` in its pager, `/page/2/` 200 (94 212 B)
with 6, `/page/32/` 200 (87 385 B) with 4, `/page/33/` **404**, `post-sitemap.xml` 200 (74 727 B)
with 191 `<loc>`, and one post at `/www-thimphucity-bt-vacancy/` 200 (74 734 B, md5 80913dea4c74).
The premise of #683 held: the pager was «established» and it is, and the «pas de compte énoncé» is
retired — the board states a PAGE count.
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

HOST = "www.vacancybt.com"
HOSTS = ("www.vacancybt.com", "vacancybt.com")   # both answer and both are open
ROOT = f"https://{HOST}/"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

# **FIRST, and 78 % of a post page is this.** The page writes its own class names inside its
# stylesheet, so every motif below would match the CSS before the content.
STRIP_RE = re.compile(r"(?s)<style.*?</style>|<script.*?</script>")
# a post is an <article> CARRYING an entry-title: the bare class name renders 7 where there
# are 6 posts, the seventh being a CSS rule
ARTICLE_RE = re.compile(r"(?s)<article[^>]*>(.*?)</article>")
TITLE_RE = re.compile(r'(?s)entry-title[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>')
TIME_RE = re.compile(r'<time[^>]*datetime="([^"]+)"[^>]*>(.*?)</time>', re.S)
# the terminator must be something the SLICE actually contains. The first version ended on
# `<footer` or `</article`, and the list block has NEITHER — `ARTICLE_RE` captures the
# inside and drops the closing tag — so the whole motif failed and `excerpt` came out
# null on 18 of 18, silently. `read-more-container` is the list's own next element and
# `\Z` closes the post page, where the content runs to the end of the slice.
EXCERPT_RE = re.compile(
    r'(?s)class="entry-(?:summary|content)[^"]*"[^>]*>(.*?)'
    r'(?=<\w+[^>]*read-more-container|<footer|</article|\Z)')   # <p> on the real page, not <div>
PAGER_RE = re.compile(r"/page/(\d+)/")
SLUG_RE = re.compile(r"^/([^/]+)/?$")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# ANCHORED, and on THIS board it is the LABELLED alternative that fires: its numbers are
# local (`Tel: 17940918`), with no dialling code for an anchor to hold.
PHONE_RE = re.compile(
    r"\+\s*\(?\s*975\s*\)?[\s.\-]?\d[\d\s.\-]{5,}\d"
    r"|(?:T[ée]l(?:[ée]phone)?|Phone|Mobile|Cell|Contact\s*No)\s*:?\s*\(?\+?\d[\d\s().\-]{5,}\d")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[vacancybt] {msg}", file=sys.stderr)


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
    if parts.scheme != "https" or parts.netloc not in HOSTS:
        die(f"{url}: not one of {', '.join(HOSTS)} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=3.0)).wait()   # no Crawl-delay written
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
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
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>|</tr>|</h\d>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    """Contacts out, and the record says which kinds were there."""
    if not s:
        return None, []
    took = []
    if MAIL_RE.search(s):
        took.append("email")
        s = MAIL_RE.sub("[e-mail withheld]", s)
    out = PHONE_RE.sub("[telephone withheld]", s)
    if out != s:
        took.append("telephone")
    return (out.strip() or None), took


def last_page(markup):
    """The last page the pager's own links name — the witness where no item count is stated."""
    seen = {int(n) for n in PAGER_RE.findall(markup or "")}
    return max(seen) if seen else None


def posts_of(markup):
    """A page → [(slug, fields)]. `<style>`/`<script>` are out FIRST: 78 % of a post page is
    CSS and it carries the class names these motifs look for."""
    out = []
    clean = STRIP_RE.sub("", markup or "")
    for block in ARTICLE_RE.findall(clean):
        t = TITLE_RE.search(block)
        if not t:                    # an <article> without an entry-title is not a post
            continue
        url = htmlmod.unescape(t.group(1))
        m = SLUG_RE.match(urllib.parse.urlsplit(url).path)
        if not m:
            continue
        when = TIME_RE.search(block)
        ex = EXCERPT_RE.search(block)
        out.append((m.group(1), {
            "url": url,
            "title": text(t.group(2)),
            "posted": when.group(1) if when else None,
            "posted_as_written": text(when.group(2)) if when else None,
            "excerpt": text(ex.group(1)) if ex else None,
        }))
    return out


def record(slug, f, stamp, position):
    took = []
    out = {}
    for k in ("title", "excerpt"):
        out[k], t = scrub(f.get(k))
        took += t
    r = {
        "source": "vacancybt", "country": stamp,
        "ledger_id": f"vacancybt:{slug}", "id": slug,
        "title": out["title"],
        "posted": f.get("posted"),                       # ISO, with Bhutan's +06:00 offset
        "posted_as_written": f.get("posted_as_written"),
        "excerpt": out["excerpt"],
        "url": f.get("url"),
        "list_position": position,
        "withheld_fields": sorted(set(took)),
    }
    if withheld_a_contact(r["withheld_fields"]):
        r["contacts_withheld"] = True
    return r


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    rows, seen, page, said, ended = [], set(), 1, None, None
    raw = 0
    while True:
        url = ROOT if page == 1 else f"{ROOT}page/{page}/"
        code, body = request(url)
        if code == 404:
            if page == 1:
                die(f"{url}: HTTP 404 — the blog is gone", EXIT_GONE)
            ended = f"page {page} answered 404, which is the site's own end of the walk"
            page -= 1
            break
        if code != 200:
            die(f"{url}: HTTP {code} — the walk ended at {th(len(seen))}", EXIT_PARTIAL)
        if page == 1:
            said = last_page(body)
        found = posts_of(body)
        if not found:
            if page == 1:
                die(f"{url}: 200 without a single post — the page changed; not an empty board",
                    EXIT_PARTIAL)
            ended = f"page {page} carried no post"
            page -= 1
            break
        keys = {s for s, _f in found}
        if page > 1 and keys <= seen:
            die(f"page {page} repeats the posts of the page before — the walk ended at "
                f"{th(len(seen))}", EXIT_PARTIAL)
        for slug, f in found:
            raw += 1
            if slug in seen:          # raw and distinct must be able to differ
                continue
            seen.add(slug)
            rows.append(record(slug, f, stamp, len(rows) + 1))
        if a.max_pages and page >= a.max_pages:
            ended = f"stopped by --max-pages at page {page}"
            break
        page += 1
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

    note(f"{th(len(rows))} post(s) emitted over {th(page)} page(s); {ended or 'the walk ended'}.")
    if said is None:
        note("**the pager named no last page this time** — it usually carries a `/page/N/` link "
             "to the last one, which is this board's witness, and the run says so rather than "
             "claiming one.")
    elif a.max_pages:
        note(f"the pager names page {th(said)} as its last; this run stopped early, so no "
             f"comparison is made.")
    elif said == page:
        note(f"the pager names page {th(said)} as its last and the walk ended there — they "
             f"agree. That page count is the witness: this board states no ITEM count, and "
             f"`caribbeanjobsonline` uses the same shape.")
    else:
        note(f"the pager names page {th(said)} as its last and the walk ended at page "
             f"{th(page)} — they DISAGREE, so one of the two is wrong and this count is not "
             f"witnessed.")
    if raw != len(seen):
        note(f"{th(raw)} post(s) seen for {th(len(seen))} distinct: {th(raw - len(seen))} "
             f"repeated across pages.")
    note("a post is an `<article>` CARRYING an `entry-title`, and `<style>`/`<script>` come out "
         "first: 78 % of a page is CSS that writes these very class names, so the bare name "
         "renders 7 where there are 6 posts.")
    note("the blog is served NEWEST FIRST in the large — 28 inversions of 189 pairs on the "
         "full walk, nearly all between posts of the SAME DAY, while the 53 posts of 2026 hold "
         "positions 1 to 53 and page 1 is exactly the six most recent — so a truncation keeps "
         "the newest and NO sort is imposed. It is NOT strictly monotone, and that bound is "
         "measured on 190 posts. Its archive reaches back to 2019: `posted` is an ISO instant "
         "and it is what decides whether a post is current — the list itself is a history.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the blog states none per post.")


def cmd_ad(a):
    url = a.url.strip()
    parts = urllib.parse.urlsplit(url)
    m = SLUG_RE.match(parts.path)
    if parts.scheme != "https" or parts.netloc not in HOSTS or not m or parts.query:
        die(f"--url {url}: a https://{HOST}/<slug>/ post, without a query string")
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the post is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    brut = len(body or "")
    clean = STRIP_RE.sub("", body)
    t = re.search(r"(?s)entry-title[^>]*>(.*?)</h\d>", clean)
    when = TIME_RE.search(clean)
    corps = EXCERPT_RE.search(clean)
    if not t or not corps:
        die(f"{url}: 200 without the post's title or its content — the page changed",
            EXIT_PARTIAL)
    took = []
    def pris(v):
        out, k = scrub(v)
        took.extend(k)
        return out
    r = {
        "source": "vacancybt", "country": a.country_code.upper() if a.country_code else None,
        "ledger_id": f"vacancybt:{m.group(1)}", "id": m.group(1),
        "title": pris(text(t.group(1))),
        "posted": when.group(1) if when else None,
        "posted_as_written": text(when.group(2)) if when else None,
        "body": pris(text(corps.group(1))),
        "url": url,
        "withheld_fields": sorted(set(took)),
    }
    if withheld_a_contact(r["withheld_fields"]):
        r["contacts_withheld"] = True
    print(json.dumps(r, ensure_ascii=False))
    note(f"{th(brut)} characters of markup became {th(len(clean))} once `<style>` and "
         f"`<script>` were out — 78 % of this page is CSS and script, and it carries the very "
         f"class names this adapter reads, so unstripped the title's motif matches a CSS rule.")
    if r["withheld_fields"]:
        note(f"withheld: {', '.join(r['withheld_fields'])}. **On this board the LABELLED half of "
             f"the anchor is what fires**: its numbers are local (`Tel: 17940918`), with no "
             f"dialling code for the `+975` half to hold — the opposite of the three boards "
             f"measured before it.")
    else:
        note("nothing was scrubbed from this post; `withheld_fields` is empty because it carried "
             "no contact, not because none was looked for.")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="VacancyBT (Bhutan) — the vacancy blog, walked against the last page its own "
                    "pager names. Issue #683.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the walk (6 posts a page), against the declared last page")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0,
                   help="stop after N pages (0 = until the site's own 404)")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on every record")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one post, its date and its text")
    d.add_argument("--url", required=True, help="the post's own address")
    d.add_argument("--country-code", dest="country_code", metavar="ISO2",
                   help="STAMP a country on the record")
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
