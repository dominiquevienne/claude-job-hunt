#!/usr/bin/env python3
"""Práce za rohem (`www.pracezarohem.cz`, Czechia) and Práca za rohom (`www.pracazarohom.sk`, Slovakia) — Alma Career's «work around the corner» boards, one Next.js stack on two hosts named by `--host`; the listing server-rendered with its data in `__NEXT_DATA__` and its own `numFound` printed beside every walk; the ad page's own state read, **its `recruiter` object — name, e-mail, telephone — never emitted**. Issues #355, #347.

  pracezarohem.py list [--host cz|sk] [--region <slug>] [--pages N] [--limit N]
  pracezarohem.py ad --url <https://www.pracezarohem.cz/dl/jd/<id> | https://www.pracazarohom.sk/dl/jd/<id>>

THE RULES (270 B, the same file on both hosts, `*`): `Disallow: /b2c`, `/apply`, `/cv`,
`/deeplink`, `/deeplink2`, `/deeplinks`; three sitemaps named — `.cz`, `.pl`, `.sk`. The
listing, its `?page=N` pager and the ad (`/dl/jd/<id>`) are open. **The sitemaps are FACETS,
not ads**: 90 files of ~49 000 `/nabidky/<region>/<profession>` rows each on `.cz`, and the
`.sk` host serves the very same Czech facet rows — they are not read. No Crawl-delay; 2 s is
ours.

THE LIST. `/nabidky` («Nabídky práce», CZ) and `/ponuky` (SK) are one Next.js page
(`/advrts/[[...slugs]]`) whose `__NEXT_DATA__` carries `adverts.adverts` (50 a page),
**`adverts.numFound` — the site's own count, 20 758 on `.cz` and 18 586 on `.sk` on the day,
printed beside every walk** — and `navigators.location` with a count per region (Praha 3 607,
Bratislavský 6 666 …); `?page=N` pages it, counted from one; `--region <slug>` walks
`/nabidky/<region>` (the site's own slugs: `hlavni-mesto-praha`, `bratislavsky` …). A card:
`id` (`PZRG-<uuid>`, `PROF-<uuid>`, `G2-<n>-…` — the board's key of the ad), title, company,
`location.place` / `placeDetail`, `salary` when the card prints one, `ageGroupStr` («Jen pár
hodin», «Dnešné»), `validEnd`, `personalAgency`, `toppedPzr`, and the employer's Atmoskop
rating when shown. The address of the ad is `/dl/jd/<id>` on the same host.

THE AD. `/dl/jd/<id>` is server-rendered with `advert` in its `__NEXT_DATA__`: title, company,
`salary` / `salaryDetailed` («25 190 - 36 210 Kč hrubého»), `descFields.jobProperties`
(labelled: Úvazek, Smlouva, …), `descFields.jobText` (HTML), `locations`, `validEnd`,
`ageGroupStr`, `replyMethod`, `language` — **and `recruiter` {name, email, phone}, which is
never emitted; the texts are scrubbed of e-mail addresses and Czech/Slovak telephone numbers;
`contacts_withheld` on every record.** The `appLink` (a deep link into the app, `b2c.pzr.sk`)
and the `?mode=b2b` address are never followed.

Measured 2026-09-14 03:0x UTC by the declared client, the guard on the exact path: `.cz`
`/nabidky` 207 862 B, 50 cards, `numFound` 20 758, `?page=2` 50 other cards; `.sk` `/ponuky`
151 709 B, 50 cards, `numFound` 18 586; the ad 33 837 B with its `advert` and its `recruiter`.
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

BOARDS = {"cz": {"host": "www.pracezarohem.cz", "country": "CZ", "lang": "cs", "list": "/nabidky", "key": "pracezarohem"},
          "sk": {"host": "www.pracazarohom.sk", "country": "SK", "lang": "sk", "list": "/ponuky", "key": "pracazarohom"}}
DEFAULT = "cz"
PAGE_SIZE = 50

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+42[01][\s ]?|0042[01][\s ]?|0)?\d{3}[\s ]?\d{3}[\s ]?\d{3}(?!\d)")   # +420 771 264 896 · 771264896 · +421 905 123 456 · 0905 123 456
NEXT_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)
AD_RE = re.compile(r"^/dl/jd/([A-Za-z0-9][A-Za-z0-9_.-]+)/?$")


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[pracezarohem] {msg}", file=sys.stderr)


def board_of(host):
    if host is None:
        return dict(BOARDS[DEFAULT], code=DEFAULT)
    h = host.strip().lower()
    for k, b in BOARDS.items():
        if h == k or h == b["host"] or h == b["host"].replace("www.", ""):
            return dict(b, code=k)
    known = ", ".join(f"{k} ({b['host']})" for k, b in BOARDS.items())
    die(f"--host {host!r}: not a front of this board — {known}")


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACES = {}


def pace_for(host):
    if host not in _PACES:
        _PACES[host] = Pace(host, own=2.0)   # no Crawl-delay written; 2 s is ours
    return _PACES[host]


def request(url):
    q = urllib.parse.urlsplit(url).query
    if q and set(urllib.parse.parse_qs(q)) != {"page"}:
        die(f"{url}: only the pager's `page` is ever sent — `mode=b2b` and the app's parameters are not roads this adapter takes", EXIT_REFUSED)
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    pace_for(host).wait()
    lang = next((b["lang"] for b in BOARDS.values() if b["host"] == host), "cs")
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": lang})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t ​]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def next_data(body):
    m = NEXT_RE.search(body)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except ValueError:
        return None


def salary_of(s):
    """«25 190 - 36 210 Kč», «od 1 000 €», «45 000 Kč» → (min, max, currency); the card prints no period."""
    if not s:
        return None, None, None
    nums = [int(re.sub(r"[\s  ]", "", n)) for n in re.findall(r"\d[\d\s  ]{2,}", s)]
    cur = "CZK" if "Kč" in s else ("EUR" if "€" in s else None)
    if not nums:
        return None, None, cur
    if "od " in s and len(nums) == 1:
        return nums[0], None, cur
    return nums[0], (nums[1] if len(nums) > 1 else nums[0]), cur


def card(a, b):
    loc = a.get("location") or {}
    smin, smax, cur = salary_of(a.get("salary"))
    atm = a.get("atmoskop") or {}
    return {
        "source": b["key"], "country": b["country"], "ledger_id": f"{b['key']}:{a.get('id')}", "id": a.get("id"),
        "url": f"https://{b['host']}/dl/jd/{a.get('id')}",
        "title": (a.get("title") or "").strip() or None, "employer": (a.get("company") or "").strip() or None,
        "place": loc.get("place") or None, "address": loc.get("placeDetail") or None,
        "salary_text": a.get("salary") or None, "salary_min": smin, "salary_max": smax, "salary_currency": cur, "salary_unit_stated": False,
        "age": a.get("ageGroupStr") or None, "valid_end": a.get("validEnd"),
        "agency": bool(a.get("personalAgency")), "topped": bool(a.get("toppedPzr")),
        "employer_rating": atm.get("stars") if atm else None, "employer_reviews": atm.get("numberOfReviews") if atm else None,
        "contacts_withheld": True, "language": b["lang"],
    }


def cmd_list(a):
    b = board_of(getattr(a, "host", None))
    base = f"https://{b['host']}{b['list']}" + (f"/{a.region.strip('/')}" if a.region else "")
    rows, seen, pageno, total, regions, first = [], set(), 0, None, None, None
    while True:
        pageno += 1
        url = base + (f"?page={pageno}" if pageno > 1 else "")
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}" + (" — not a region slug the site serves" if code == 404 and a.region else ""), EXIT_GONE if code == 404 and pageno == 1 else EXIT_PARTIAL)
        d = next_data(body)
        pp = ((d or {}).get("props") or {}).get("pageProps") or {}
        ads = (pp.get("adverts") or {})
        page = ads.get("adverts") or []
        if not isinstance(page, list) or not page:
            die(f"{url}: 200 and no advert in the page's state — the template changed; not an empty market", EXIT_PARTIAL)
        if total is None:
            total = ads.get("numFound")
            nav = ((pp.get("navigators") or {}).get("location") or {}).get("navigators") or []
            regions = [(x.get("areaName"), x.get("count")) for x in ((nav[0] if nav else {}).get("items") or [])] or None
        ids = [x.get("id") for x in page]
        if first is None:
            first = ids
        elif ids == first:
            die(f"{url}: the same adverts as page 1 — the pager is not paging; not counted twice", EXIT_PARTIAL)
        new = 0
        for x in page:
            r = card(x, b)
            if not r["id"] or r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
            new += 1
        if new == 0 or (total and len(seen) >= total):
            break
        if a.pages and pageno >= a.pages:
            break
        if a.limit and len(rows) >= a.limit:
            break
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    where = f"{b['host']}{b['list']}" + (f"/{a.region}" if a.region else "")
    if total is None:
        note(f"{th(n)} emitted over {pageno} page(s) of {where} — the site's `numFound` was not found; not compared.")
    elif n < total:
        note(f"{th(n)} emitted over {pageno} page(s) of {PAGE_SIZE}, the site states {th(total)} on {where} — walked by request (--pages/--limit), not a shortfall.")
    else:
        note(f"{th(n)} emitted over {pageno} page(s), the site states {th(total)} on {where} — " + ("equal." if n == total else f"{th(n - total)} more emitted than stated."))
    if regions:
        note("regions the site counts: " + ", ".join(f"{name} {th(c)}" for name, c in regions if name) + ".")
    note("the ad's `recruiter` object (name, e-mail, telephone) is never emitted; texts scrubbed; the app deep link and the b2b address never followed.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    b = next((dict(v, code=k) for k, v in BOARDS.items() if v["host"] == parts.netloc), None)
    m = AD_RE.match(parts.path) if b else None
    if not b or not m:
        die(f"{a.url}: not an ad address on one of the two hosts (https://<host>/dl/jd/<id>)")
    url = f"https://{b['host']}/dl/jd/{m.group(1)}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    d = next_data(body)
    ad = (((d or {}).get("props") or {}).get("pageProps") or {}).get("advert")
    if not isinstance(ad, dict) or not ad.get("title"):
        die(f"{url}: 200 and no `advert` in the page's state — the template changed", EXIT_PARTIAL)
    df = ad.get("descFields") or {}
    props = {(p.get("label") or "").strip(): text(p.get("value") or "") for p in (df.get("jobProperties") or []) if isinstance(p, dict) and p.get("label")}
    body_text = "\n".join(text(t.get("value") or "") for t in (df.get("jobText") or []) if isinstance(t, dict)) or text(ad.get("desc") or "")
    company_text = "\n".join(text(t.get("value") or "") for t in (df.get("companyText") or []) if isinstance(t, dict))
    smin, smax, cur = salary_of(ad.get("salary"))
    locs = [l.get("label") for l in (ad.get("locations") or []) if isinstance(l, dict) and l.get("label")]
    atm = ad.get("atmoskop") or {}
    print(json.dumps({
        "source": b["key"], "country": b["country"], "ledger_id": f"{b['key']}:{m.group(1)}", "id": m.group(1), "url": url,
        "title": (ad.get("title") or "").strip() or None, "employer": (ad.get("company") or "").strip() or None, "employer_url": ad.get("companyWeb") or None,
        "locations": locs or None, "address": (ad.get("location") or {}).get("label"),
        "salary_text": ad.get("salaryDetailed") or ad.get("salary") or None, "salary_min": smin, "salary_max": smax, "salary_currency": cur, "salary_unit_stated": False,
        "properties": props or None,
        "age": ad.get("ageGroupStr") or None, "valid_end": ad.get("validEnd"), "valid": ad.get("valid"),
        "reply_method": ad.get("replyMethod"), "cv_required": ad.get("cvRequired"),
        "employer_rating": atm.get("stars") if atm else None, "employer_reviews": atm.get("numberOfReviews") if atm else None,
        "description": scrub(body_text), "employer_text": scrub(company_text),
        # `recruiter` — {name, email, phone} — is in the page's state and is never emitted
        "contacts_withheld": True, "language": ad.get("language") or b["lang"],
    }, ensure_ascii=False))
    note(f"{url}: read from the page's own state; `recruiter` withheld; texts scrubbed; the app deep link never followed.")


def main():
    p = argparse.ArgumentParser(description="Práce za rohem / Práca za rohom — two hosts by --host; the listing's own numFound beside every walk; the ad's recruiter never emitted. Issues #355, #347.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the newest ads, 50 a page, 3 pages unless told")
    l_.add_argument("--host", help="cz (default) · sk — or the hostname")
    l_.add_argument("--region", help="the site's region slug — hlavni-mesto-praha, jihomoravsky, bratislavsky …")
    l_.add_argument("--pages", type=int, default=3)
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
