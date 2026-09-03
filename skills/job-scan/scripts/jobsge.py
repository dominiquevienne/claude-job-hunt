#!/usr/bin/env python3
"""Read jobs.ge — Georgia's independent generalist, and the whole board is one
request.

**No key, no cookie, no browser, and no pagination.** The home page carries
**every live vacancy**: 308 distinct ad ids on 2026-09-03, on both language
versions, with no `page` parameter anywhere on it. A complete sweep costs one
fetch.

`robots.txt` is **54 bytes**: one `Disallow: /data/clients/`, no sitemap, no AI
agent named — and **`Crawl-delay: 5`**, which is a published rate limit and the
default here. It is the first explicit crawl delay in this repository's
adapters, and it is honoured rather than noted.

  GET /ge/                      → every live ad, as `?view=jobs&id=<n>` links
  GET /ge/?view=jobs&id=<n>     → one ad, server-rendered, no structured data
  GET /en/?view=jobs&id=<n>     → the same ad, and usually **a stub**

**THE ENGLISH PAGE IS A STUB, AND IT ANSWERS 200.** On the same advertisement:

    /en/   614 visible characters   "See full text of this announcement in Georgian"
    /ge/  3 943 visible characters   the whole posting

**An adapter reading `/en/` scores the ad on one sentence** — a well-formed
page, a correct status, and the wrong question answered. So this file reads
`/ge/` by default and **refuses to hand back an English body silently**: the
card carries `is_stub`, and `--lang en` says what it costs.

**The ratio is not the test — the sentence is.** One sampled ad ran 623
characters in English against 767 in Georgian, a factor of 1.2, and was a stub
all the same. A threshold on length would have passed it.

A FALSE POSITIVE WORTH KNOWING: the ad page contains the words **"All Job Ads
on a Single Page"**, which reads exactly like a full-board view. **It is the
caption of a banner advertisement for one employer.** A string that describes a
feature and is a advert.

Verified against the live site on **2026-09-03**.
"""

import argparse
import html as html_mod
import json
import re
import sys
import time
import urllib.error
import urllib.request

from _robots import verdict as robots_verdict
from _zero import zero_note

BASE = "https://www.jobs.ge"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

# **Published in robots.txt, so it is the default and not a suggestion.**
CRAWL_DELAY = 5.0

EXIT_BROKEN, EXIT_GONE, EXIT_REFUSED = 2, 3, 7

AD_RE = re.compile(r"view=jobs&(?:amp;)?id=(\d+)")
# `<title>` is `JOBS.GE - <role> - <employer>` in both languages, and it is the
# only place either appears as a clean field.
TITLE_RE = re.compile(r"(?is)<title>\s*(?:JOBS\.GE|ჯობს\.გე)\s*-\s*(.*?)</title>")
# **The site declares its own stub, in whichever language the stub is**, and
# that symmetry is the whole design. Measured on 12 ads: eleven English pages
# say *"See full text of this announcement in Georgian"*; the twelfth is the
# mirror — its **Georgian** page says *"იხილეთ ამ განცხადების სრული ტექსტი
# ინგლისურ ენაზე"* and the English one carries the advertisement.
#
# **So "Georgian is the complete one" is false, and a length threshold is
# worse than useless**: one sampled ad's Georgian page ran 767 characters —
# shorter than several stubs — and was the complete text. **A string that the
# site prints needs no threshold; a ratio does.**
STUB_RE = re.compile(r"See full text of this announcement|"
                     r"სრული ტექსტი", re.I)
# **Bounded to a day and a month, and that is not pedantry.** Read off the
# flattened text, `([^\n<]+)` has no newline to stop at and swallows the whole
# advertisement into `deadline_text` — 3 400 characters of body filed as a
# date. Caught by looking at the field.
_DAY_MONTH = r"(\d{1,2}\s+\S+)"
DATES_EN = re.compile(r"Published:\s*" + _DAY_MONTH + r"\s*/\s*Deadline:\s*"
                      + _DAY_MONTH)
DATES_KA = re.compile(r"გამოქვეყნდა:\s*" + _DAY_MONTH +
                      r"\s*/\s*ბოლო ვადა:\s*" + _DAY_MONTH)

LANGS = {"ge": "ka-GE,ka;q=0.9", "en": "en-US,en;q=0.9"}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobs.ge] {msg}", file=sys.stderr)


def get(path, lang="ge", timeout=45):
    url = f"{BASE}/{lang}/{path}" if not path.startswith("http") else path
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": LANGS.get(lang, LANGS["ge"]),
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.getcode(), r.read().decode("utf-8", "replace"), url
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {e}")


def visible(html):
    b = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html or "")
    return re.sub(r"\s+", " ", html_mod.unescape(
        re.sub(r"<[^>]+>", " ", b))).strip()


def check_robots():
    v = robots_verdict("www.jobs.ge")
    if not v["sweep"]:
        die(f"www.jobs.ge: {v['reason']}", EXIT_REFUSED)
    return v


def cmd_search(a):
    check_robots()
    code, html, url = get("", a.lang)
    if code != 200:
        die(f"{url}: HTTP {code}")
    ids = sorted(set(AD_RE.findall(html)), key=int, reverse=True)
    if not ids:
        die(zero_note("jobs.ge", extra=(
            "The home page answered 200 and carried no `view=jobs&id=` link. "
            "This board has no pagination, so that is the whole board — "
            "check the markup before reading it as an empty market.")))
    for ident in (ids[:a.limit] if a.limit else ids):
        print(json.dumps({
            "id": ident,
            "ledger_id": f"jobs.ge:{ident}",
            "url": f"{BASE}/{a.lang}/?view=jobs&id={ident}",
            "description_needs_georgian": a.lang == "en",
        }, ensure_ascii=False))
    note(f"{len(ids)} distinct advertisement(s) — **the whole board, in one "
         f"request.** This site has no pagination: what the home page carries "
         f"is what it has.")


def card(html, ident, lang, url):
    t = TITLE_RE.search(html)
    role = company = None
    if t:
        parts = [p.strip() for p in html_mod.unescape(t.group(1)).split(" - ")]
        role = parts[0] or None
        company = parts[1] if len(parts) > 1 else None
    txt = visible(html)
    m = (DATES_EN if lang == "en" else DATES_KA).search(txt)
    stub = bool(STUB_RE.search(txt))
    return {
        "id": ident,
        "ledger_id": f"jobs.ge:{ident}",
        "url": url,
        "lang": lang,
        "title": role,
        "company": company,
        # As printed by the site — a day and a month name, no year. Not
        # normalised: guessing the year across a December/January boundary is
        # exactly the kind of quiet error this repository keeps finding.
        "published_text": m.group(1).strip() if m else None,
        "deadline_text": m.group(2).strip() if m else None,
        # **True means this page is not the advertisement.** The English
        # version routinely carries a sentence and a pointer to the Georgian
        # text; the length ratio does not catch it and this sentence does.
        "is_stub": stub,
        "visible_chars": len(txt),
    }


def cmd_ad(a):
    check_robots()
    ident = a.id or (AD_RE.search(a.url or "") or [None, None])[1]
    if not ident:
        die("give --id, or a --url carrying `view=jobs&id=<n>`.")
    code, html, url = get(f"?view=jobs&id={ident}", a.lang)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_GONE)
    out = card(html, ident, a.lang, url)
    switched = None
    if out["is_stub"] and not a.no_follow:
        # **Follow the pointer, because the site gave one.** This is not a
        # guess about which language is fuller — the page says where its text
        # is, and the direction goes both ways.
        other = "en" if a.lang == "ge" else "ge"
        time.sleep(CRAWL_DELAY)
        c2, h2, u2 = get(f"?view=jobs&id={ident}", other)
        if c2 == 200:
            alt = card(h2, ident, other, u2)
            if not alt["is_stub"]:
                switched = (a.lang, other, out["visible_chars"],
                            alt["visible_chars"])
                html, out = h2, alt
    if a.with_text:
        out["description"] = visible(html)
    out["followed_stub"] = bool(switched)
    print(json.dumps(out, ensure_ascii=False))
    if switched:
        frm, to, n_from, n_to = switched
        note(f"the {frm!r} page is a stub — {n_from} visible characters and "
             f"a sentence pointing at the other language — **so this card is "
             f"the {to!r} page**, {n_to} characters. The site declared the "
             f"switch; nothing here guessed it.")
    elif out["is_stub"]:
        note(f"**this page is a stub and the other language is one too, or "
             f"did not answer.** {out['visible_chars']} visible characters. "
             f"Do not score it: a score computed here is a score of one "
             f"sentence.")


def cmd_compare(a):
    """What the English version costs, measured rather than asserted."""
    check_robots()
    code, html, _ = get("", "ge")
    if code != 200:
        die(f"home page: HTTP {code}")
    ids = sorted(set(AD_RE.findall(html)), key=int, reverse=True)
    step = max(1, len(ids) // max(a.sample, 1))
    rows, stubs = [], 0
    for ident in ids[::step][:a.sample]:
        c_en, h_en, _ = get(f"?view=jobs&id={ident}", "en")
        time.sleep(a.delay)
        c_ka, h_ka, _ = get(f"?view=jobs&id={ident}", "ge")
        time.sleep(a.delay)
        if c_en != 200 or c_ka != 200:
            continue
        en, ka = card(h_en, ident, "en", ""), card(h_ka, ident, "ge", "")
        stubs += 1 if en["is_stub"] else 0
        rows.append({"id": ident, "en_chars": en["visible_chars"],
                     "ge_chars": ka["visible_chars"], "en_is_stub": en["is_stub"]})
        print(json.dumps(rows[-1], ensure_ascii=False))
    if not rows:
        die("no ad could be read in both languages.")
    note(f"{stubs} of {len(rows)} English pages are stubs, out of "
         f"{len(ids)} ads on the board.")
    ratios = sorted(r["en_chars"] / max(r["ge_chars"], 1) for r in rows)
    note(f"length ratios en/ge run {ratios[0]:.2f} to {ratios[-1]:.2f} — "
         f"**so length is not the test.** The sentence the page prints is.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lang", choices=["ge", "en"], default="ge",
                   help="`ge` is the complete text; `en` is usually a stub")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="every live ad — one request, no pages")
    s.add_argument("--limit", type=int)
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("ad", help="one ad by id or URL")
    d.add_argument("--id")
    d.add_argument("--url")
    d.add_argument("--with-text", action="store_true", dest="with_text")
    d.add_argument("--no-follow", action="store_true", dest="no_follow",
                   help="do not switch language when the page is a stub")
    d.set_defaults(func=cmd_ad)

    c = sub.add_parser("compare",
                       help="measure what reading English costs, on a sample")
    c.add_argument("--sample", type=int, default=12)
    c.add_argument("--delay", type=float, default=CRAWL_DELAY)
    c.set_defaults(func=cmd_compare)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
