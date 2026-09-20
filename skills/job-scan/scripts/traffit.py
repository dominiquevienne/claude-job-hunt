#!/usr/bin/env python3
"""Traffit (a Polish ATS — one tenant at a time): the employer's career page on `<tenant>.traffit.com/career/` fills its list by `GET /public/an/list/?limit=&offset=&page=` — the call the page's own widget makes — whose answer states `count`; the advert page `/public/an/<hash>` is server-rendered. Issue #472.

  traffit.py jobs --tenant <name> [--country-code ISO2] [--max-pages N]
  traffit.py ad --url https://<tenant>.traffit.com/public/an/<hash>

THE TENANT is the subdomain of `traffit.com` the employer's career page
lives on (`scalo`, `vercom`, `itlt`, `welove`, `edugo`), found by the
family's signature (`<tenant>.traffit.com/career/`), never composed. Rules
(read 2026-09-20): `<tenant>.traffit.com/robots.txt` answers 404 with the
app's own page — no rules; 2 s between requests are ours.

THE ROUTE: the career page loads `/public/an/generateJs/`, the widget that
builds `request = {obj: {}, filter: [], limit, offset: 0, page: 1}` and
GETs `<site>public/an/list/?limit=…&offset=…&page=…` (the object
flattened to a query string); the answer is `{count, items[]}` — `count`
the stated total, `limit` honoured up to 50 (measured: 10 by the page, 50
by request), `offset`/`page` advancing (Scalo: 235 stated, 2026-09-20).
The item: advertId, advertPublishId, recruitmentId, nrRef, name, title
(«(11882) QA/Test Lead» — the id prefixed), url (`/public/an/<hash>`),
applicationForm (`/public/form/a/<id>`), validStart/validEnd (epoch),
language, confidential, remote, job {id, experienceLevel[]},
description / requirements / responsibilities / benefits (HTML),
locations[] (locality, region1..3, country, iso, postcode, latitude,
longitude), geolocation, headerPhoto, and custom fields under hashed keys
with no label (not emitted). The advert page: `h1.advert-data__name`,
`article.main__article > .article__content` sections.

WITHHELD: the application form; the workplace's postcode and coordinates
(locality, region and country kept); the hashed custom fields (unlabelled
— a salary or a contract type may be among them, but the key does not
say); e-mail addresses and telephone numbers in the texts;
`contacts_withheld` on every record. The country is the item's own
`iso`; `--country-code` filters on it (an item with no location is
stamped, said aloud).
"""

import argparse
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD = "traffit"
DOMAIN = "traffit.com"
LIST_PATH = "/public/an/list/"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
PAGE_SIZE = 50                                 # honoured by the list (the page asks 10)

TENANT_RE = re.compile(r"^[a-z0-9]([a-z0-9_-]*[a-z0-9])?$", re.I)
AD_PATH_RE = re.compile(r"^/public/an/([0-9a-f]{20,})/?$")
H1_RE = re.compile(r'<h1 class="advert-data__name"[^>]*>(.*?)</h1>', re.S)
ARTICLE_OPEN_RE = re.compile(r'<article class="main__article">\s*<div\s+class="article__content"\s*>', re.S)
DIV_RE = re.compile(r"<div\b|</div>", re.I)
HASH_KEY_RE = re.compile(r"^[0-9a-f]{32}$")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{6,}\d(?!\w)")
_PACES = {}
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[traffit] {msg}", file=sys.stderr)


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
    host = parts.netloc.lower()
    if not TENANT["host"] or host != TENANT["host"] or not host.endswith("." + DOMAIN):
        die(f"{url}: not this run's Traffit tenant ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "application/json, text/html", "Accept-Language": "pl,en"})
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
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", t)
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span|font)\b[^>]*>", "", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def articles_of(markup):
    """Every `article__content` of the advert page, each read balanced across its nested divs."""
    out, pos = [], 0
    while True:
        m = ARTICLE_OPEN_RE.search(markup, pos)
        if not m:
            return out
        depth, start = 1, m.end()
        end = len(markup)
        for t in DIV_RE.finditer(markup, m.end()):
            depth += 1 if t.group(0).lower().startswith("<div") else -1
            if depth == 0:
                end = t.start()
                break
        out.append(markup[start:end])
        pos = end


def when(v):
    try:
        return datetime.fromtimestamp(int(v), timezone.utc).strftime("%Y-%m-%d") if v not in (None, "", 0) else None
    except (TypeError, ValueError, OverflowError):
        return None


def tenant_of(arg):
    s = (arg or "").strip().lower()
    if "://" in s or "/" in s:
        s = urllib.parse.urlsplit(s if "://" in s else "https://" + s).netloc
    if s.endswith("." + DOMAIN):
        s = s[: -len("." + DOMAIN)]
    if not s or "." in s or not TENANT_RE.match(s) or s in ("www", "cdn3", "app"):
        die(f"{arg!r}: a tenant is the subdomain of {DOMAIN} the employer's career page lives on (scalo, vercom), found by the family's signature, never composed")
    return f"{s}.{DOMAIN}"


def places_of(it):
    out = []
    for l in it.get("locations") or []:
        if isinstance(l, dict):
            out.append({"place": l.get("locality") or None, "region": l.get("region1") or None, "country": (l.get("iso") or "").upper() or None, "country_name": l.get("country") or None})
    return out


def row(it, host, stamp):
    locs = places_of(it)
    first = locs[0] if locs else {}
    job = it.get("job") if isinstance(it.get("job"), dict) else {}
    return {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{it.get('advertId')}", "id": str(it.get("advertId") or ""),
        "recruitment_id": str(it.get("recruitmentId") or ""), "reference": it.get("nrRef") or None,
        "url": (it.get("url") or "").split("?")[0] or None, "title": it.get("name") or it.get("title"),
        "place": first.get("place"), "region": first.get("region"), "country": first.get("country") or stamp, "country_name": first.get("country_name"),
        "locations": locs, "remote": it.get("remote") if it.get("remote") not in (None, "") else None,
        "experience_level": job.get("experienceLevel") or None, "language": it.get("language") or None,
        "published": when(it.get("validStart")), "closes": when(it.get("validEnd")), "updated": when(it.get("updatedAt")),
        "description": (scrub(text(it.get("description"))) or "")[:20000] or None,
        "sections": {k: scrub(text(it.get(k))) for k in ("requirements", "responsibilities", "benefits") if it.get(k)},
        # applicationForm, headerPhoto, the hashed custom fields, the postcode and the coordinates are not emitted
        "contacts_withheld": True,
    }


def page(host, offset, number):
    url = f"https://{host}{LIST_PATH}?" + urllib.parse.urlencode([("limit", PAGE_SIZE), ("offset", offset), ("page", number)])
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404 — no such career page", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    try:
        j = json.loads(body)
    except ValueError:
        die(f"{url}: not JSON ({len(body)} characters) — a subdomain that is no tenant, or the shape changed", EXIT_PARTIAL)
    if not isinstance(j, dict) or "count" not in j or not isinstance(j.get("items"), list):
        die(f"{url}: no `count` / `items` in the answer — not the widget's response shape.", EXIT_PARTIAL)
    return j["count"], [i for i in j["items"] if isinstance(i, dict)]


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    TENANT["host"] = host
    stamp = (a.country_code or "").strip().upper() or None
    total, items = page(host, 0, 1)
    rows, seen, walked = [], set(), 1
    while True:
        new = 0
        for it in items:
            if it.get("advertId") is None or it["advertId"] in seen:
                continue
            seen.add(it["advertId"])
            rows.append(row(it, host, stamp))
            new += 1
        if items and new == 0:
            die(f"{host}: the call at offset {(walked - 1) * PAGE_SIZE} repeated the previous one — the offset is not advancing; {th(len(rows))} kept of the {th(total)} stated.", EXIT_PARTIAL)
        last = -(-(total or 0) // PAGE_SIZE)
        if not items or len(rows) >= (total or 0) or walked >= last or (a.max_pages and walked >= a.max_pages):
            break
        walked += 1
        _t, items = page(host, (walked - 1) * PAGE_SIZE, walked)
    emitted = [r for r in rows if not stamp or r["country"] == stamp]
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    if stamp:
        note(f"{th(n)} emitted for {stamp} of the {th(len(rows))} read over {walked} call(s) — the site states {th(total)}; an advert without a location is stamped {stamp}.")
    elif a.max_pages and walked >= a.max_pages and (total or 0) > len(rows):
        note(f"{th(n)} emitted of the {th(total)} the site states — {walked} call(s) of {PAGE_SIZE} by request (--max-pages), not a shortfall.")
    elif n == total:
        note(f"{th(n)} emitted over {walked} call(s) — the site states {th(total)}: equal.")
    else:
        note(f"{th(n)} emitted over {walked} call(s) — the site states {th(total)}: {th(abs((total or 0) - n))} " + ("short" if (total or 0) > n else "more emitted than stated") + ".")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    host = parts.netloc.lower()
    m = AD_PATH_RE.match(parts.path)
    if not host.endswith("." + DOMAIN) or not m:
        die(f"{a.url!r}: not a Traffit advert address (https://<tenant>.{DOMAIN}/public/an/<hash>)")
    TENANT["host"] = host
    url = f"https://{host}/public/an/{m.group(1)}"          # `?source=career_page` and the like dropped
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped.", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    h1 = H1_RE.search(body)
    arts = [scrub(text(x)) for x in articles_of(body)]
    arts = [x for x in arts if x]
    if not h1 or not arts:
        die(f"{url}: no `advert-data__name` or no `main__article` in the page — not a Traffit advert page, or the advert is gone.", EXIT_PARTIAL)
    r = {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:an:{m.group(1)[:12]}", "id": m.group(1), "url": url,
        "title": text(h1.group(1)), "description": "\n\n".join(arts)[:20000] or None, "sections": len(arts),
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Traffit — one tenant's adverts by the list call its career page makes (limit/offset/page, the stated count beside every walk) and the advert page; the form, the coordinates and the unlabelled custom fields never emitted, texts scrubbed. Issue #472.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the tenant's adverts, 50 a call, 2 s apart, to the stated count")
    s.add_argument("--tenant", required=True, help="the subdomain (scalo), the host, or the career page's URL")
    s.add_argument("--country-code", help="keep the adverts whose first location is this ISO2 country (one without a location is stamped)")
    s.add_argument("--max-pages", type=int)
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert by its page (/public/an/<hash>); texts scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
