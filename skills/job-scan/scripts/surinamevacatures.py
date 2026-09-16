#!/usr/bin/env python3
"""Suriname Vacatures (`surinamevacatures.com`) — «Stageplekken en vacatures in Suriname», a small WordPress board for Dutch-speaking students and graduates: two lists served whole on the server (`/vacatures-suriname`, `/stageplekken-suriname` — 13 and 16 cards on 2026-09-16, no pager, no count printed), and an ad page of `acf:` fields (employer, place, level, hours, pay) with titled sections; the lists' own card counts printed beside the walk; the texts scrubbed. Issue #446.

  surinamevacatures.py list [--kind vacatures|stages|all]     the two lists (2 requests), each card with its kind
  surinamevacatures.py ad --url <https://surinamevacatures.com/vacatures/<slug>/>

THE RULES. `User-agent: *` — `Disallow: /wp-admin/`, `Allow: /wp-admin/admin-ajax.php`, a
Sitemap line (`wp-sitemap.xml`, which answers 404 with its index in the body). `/wp-admin/`,
`/wp-json/`, `/xmlrpc.php` are never sent (refused before the gate); no Crawl-delay, 2 s is ours.

THE LISTS. `/vacatures-suriname` (200, ~67 KB) and `/stageplekken-suriname` (200, ~76 KB) are
Webflow-style exports served whole: `<div role="listitem" class="vacatures-item-wrapper …">` cards
— `<h2 item="title">`, `acf:text="plaatsnaam"` (the place), `acf:text="uren"` (the hours), an
`inline-text` level (MBO, HBO, WO), `<div class="categ">` labels, a link to `/vacatures/<slug>/`
(the stages live under the same path). No pager, no total anywhere: **the count is the list's own
cards, and `list` says so** («13 vacatures and 16 stages on the lists — the lists are the count»).
THE AD. `/vacatures/<slug>/` (200, ~35 KB): `<h2 item="title">`, `acf:text="bedrijfsnaam"` (the
employer), `plaatsnaam` twice (the place, then the level — the site reuses the attribute), `uren`,
`loon` («€ Uurloon vanaf 25,- srd per maand»), `acf:textarea="periode"`, then `acf:richtext`
sections under `acf:text="*_titel"` headings — «Bedrijfsprofiel», «Wie ben jij?», «Wat ga je
doen?», «Wat bieden wij?» — and a closing «Geïnteresseerd in deze functie?» that names the site's
own address. No JobPosting, no dates. **The sections are scrubbed of e-mail addresses and
Surinamese telephone numbers (the site's own `info@` included); `contacts_withheld` on every
record; «Solliciteren» (a form on the site) never touched.**

Measured 2026-09-16 21:42–21:43 UTC by the declared client, the guard on the exact path: robots
200 (122 B); `/` 60 894 B (identical to 2026-09-13); the two lists 13 and 16 cards; the ad 35 311 B.
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

HOST = "surinamevacatures.com"
LISTS = {"vacatures": f"https://{HOST}/vacatures-suriname", "stages": f"https://{HOST}/stageplekken-suriname"}
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+?597[\s\-]?)?(?:[678]\d{2}[\s\-]?\d{4}|[2345]\d{2}[\s\-]?\d{3})(?!\d)")   # Surinamese 7-digit mobiles and 6-digit landlines, with or without +597
AD_RE = re.compile(r"^/vacatures/([a-z0-9\-]+)/?$")
REFUSED_RE = re.compile(r"^/(?:wp-admin|wp-json|xmlrpc\.php|wp-login\.php)(?:/|$)")
CARD_RE = re.compile(r'<div role="listitem" class="vacatures-item-wrapper[^"]*">(.*?)<a href="(https://surinamevacatures\.com/vacatures/[^"]+)" class="vacatures-link[^"]*"></a>(.*?)(?=<div role="listitem" class="vacatures-item-wrapper|<div class="w-dyn-empty|</body>)', re.S)
TITLE_RE = re.compile(r'<h2 item="title"[^>]*>(.*?)</h2>', re.S)
ACF_RE = re.compile(r'acf:text="([a-z_]+)"[^>]*>(.*?)</', re.S)
LEVEL_RE = re.compile(r'<div class="inline-text">(.*?)</div>', re.S)
CATEG_RE = re.compile(r'<div class="categ">(.*?)</div>', re.S)
SECTION_RE = re.compile(r'<h3 acf:text="([a-z_]+)_titel"[^>]*>([^<]*)</h3>\s*(?:<div class="[^"]*">\s*)?<div acf:richtext="[a-z_]+"[^>]*>(.*?)</div>', re.S)
PERIOD_RE = re.compile(r'<p acf:textarea="periode"[^>]*>(.*?)</p>', re.S)

_PACE = Pace(HOST, own=2.0)   # no Crawl-delay written; 2 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[surinamevacatures] {msg}", file=sys.stderr)


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
        die(f"{url}: the admin and the REST API — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "nl"})
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


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def acf(markup):
    """`acf:text="<field>"` → text, in order of appearance (a repeated field keeps a list)."""
    out = {}
    for k, v in ACF_RE.findall(markup or ""):
        out.setdefault(k, []).append(text(v))
    return out


def cards(body, kind):
    out = []
    for head, href, tail in CARD_RE.findall(body):
        t = TITLE_RE.search(head)
        m = AD_RE.match(urllib.parse.urlsplit(href).path)
        if not t or not m:
            continue
        f = acf(head)
        lv = LEVEL_RE.search(head)
        out.append({
            "source": "surinamevacatures", "country": "SR", "ledger_id": f"surinamevacatures:{m.group(1)}", "id": m.group(1), "url": href, "kind": kind,
            "title": text(t.group(1)), "place": (f.get("plaatsnaam") or [None])[0], "hours": (f.get("uren") or [None])[0], "level": text(lv.group(1)) if lv else None,
            "categories": [text(c) for c in CATEG_RE.findall(tail) if text(c)] or None,
            "contacts_withheld": True, "language": "nl",
        })
    return out


def cmd_list(a):
    kinds = ["vacatures", "stages"] if a.kind == "all" else [a.kind]
    out, seen, counts = [], set(), {}
    for kind in kinds:
        code, body = request(LISTS[kind])
        if code != 200:
            die(f"{LISTS[kind]}: HTTP {code}", EXIT_GONE if code == 404 else EXIT_PARTIAL)
        cs = cards(body, kind)
        if not cs:
            die(f"{LISTS[kind]}: 200 and no card — the template changed; not an empty list", EXIT_PARTIAL)
        counts[kind] = len(cs)
        for c in cs:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            out.append(c)
    for c in out:
        print(json.dumps(c, ensure_ascii=False))
    listed = " and ".join(f"{th(counts[k])} {k}" for k in kinds)
    note(f"{th(len(out))} emitted — {listed} on the list(s), the site prints no total: the lists are the count" + (f" ({th(sum(counts.values()) - len(out))} on both lists, read once)" if sum(counts.values()) != len(out) else "") + ".")
    note("cards only — `ad --url` reads the ad's fields and sections, scrubbed; the application form never touched.")


def record(body, slug, url):
    t = TITLE_RE.search(body)
    f = acf(body)
    if not t or "bedrijfsnaam" not in f:
        return None
    pl = f.get("plaatsnaam") or []
    per = PERIOD_RE.search(body)
    sections = {}
    for key, heading, rich in SECTION_RE.findall(body):
        sections[text(heading) or key] = scrub(text(rich))
    return {
        "source": "surinamevacatures", "country": "SR", "ledger_id": f"surinamevacatures:{slug}", "id": slug, "url": url,
        "title": text(t.group(1)), "company": f["bedrijfsnaam"][0],
        "place": pl[0] if pl else None, "level": pl[1] if len(pl) > 1 else None, "hours": (f.get("uren") or [None])[0], "pay": (f.get("loon") or [None])[0],
        "period": text(per.group(1)) if per else None,
        "sections": sections or None,
        "contacts_withheld": True, "language": "nl",
    }


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    m = AD_RE.match(parts.path)
    if parts.netloc not in (HOST, "www." + HOST) or not m:
        die(f"{a.url}: not a job address (https://{HOST}/vacatures/<slug>/)")
    url = f"https://{HOST}/vacatures/{m.group(1)}/"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    rec = record(body, m.group(1), url)
    if rec is None:
        die(f"{url}: 200 without the ad's title and its `bedrijfsnaam` field — the template changed", EXIT_PARTIAL)
    print(json.dumps(rec, ensure_ascii=False))
    note(f"{url}: read from its fields and sections; texts scrubbed; the application form never touched.")


def main():
    p = argparse.ArgumentParser(description="Suriname Vacatures — the two lists served whole, each ad from its fields and sections; texts scrubbed. Issue #446.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the vacancies and the internships (2 requests)")
    l_.add_argument("--kind", choices=["vacatures", "stages", "all"], default="all")
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
