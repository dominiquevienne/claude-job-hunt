#!/usr/bin/env python3
"""Betterteam — a small-business ATS, one tenant at a time: the tenant's hosted careers page on `<slug>.betterteam.com` is a React Router page rendered on the server — every open position is a card in its markup («Current Positions»), and each position's page carries a schema.org JobPosting. No API, no token: the adapter reads the page as a browser would see it. Issue #459.

  betterteam.py jobs --tenant pandarg-117 [--country-code US]     the tenant's positions (1 request)
  betterteam.py jobs --tenant https://careers.betterteam.com/
  betterteam.py ad --url https://pandarg-117.betterteam.com/assistant-manager-general-manager

WHAT IT IS. Betterteam is hiring software for restaurants, clinics, agencies and family-run
companies; it publishes each customer's «Careers» page on a subdomain of its own (Panda
Restaurant Group `pandarg-117`, Carilion Clinic `carilionclinic`, Betterteam's own `careers`).
**One adapter covers every employer that uses it, in every country; the user names the tenant**
by the subdomain the careers URL spells (`pandarg-117.betterteam.com` → `pandarg-117`).

THE RULES. `<slug>.betterteam.com/robots.txt` refuses `/resumes/` and `/cdn-cgi/` to `*` and
nothing else; no Crawl-delay, 2 s is ours. The guard is taken per host on the exact path.

THE PAGE. The careers page (200; 6.9–13.8 KB) is server-rendered (React Router, `ssr: true`): a
«Current Positions» section with one card per open position —
`<a class="font-semibold text-lg …" href="/<slug>">Title</a>` then a `text-sm` line of
`<span>Remote</span>` / a place with a tooltip carrying the full address / a country / the
employment type, joined by «•». A tenant with none says so in prose («doesn't have any openings
right now») — printed as «0 positions», not an error. No count is stated: the cards are the
board. The position page (200, 31 KB) carries a JobPosting — title, description (HTML),
datePosted, employmentType, hiringOrganization, jobLocation (a postal address), baseSalary,
identifier (the tenant's name, the position's slug); `directApply: true`.

Measured 2026-09-19 22:1x UTC by the declared client, the guard on the exact path: Panda
Restaurant Group (`pandarg-117`) 7 cards, Betterteam (`careers`) 2 cards (Remote • Australia,
Remote • Philippines), Carilion Clinic (`carilionclinic`) 0 — «doesn't have any openings»;
`nowhospitality` and `hivetalent` answer 404 «Page Not Found» (tenants gone). The ad
`/assistant-manager-general-manager` on Panda: a JobPosting with a USD 72 000–100 000 salary.

**WITHHELD:** descriptions scrubbed of e-mail addresses and telephone numbers; the address
tooltip's street line not emitted (the place and region are); `contacts_withheld` on every
record; the application (`/apply`, Betterteam's form) never touched.
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
from _ldjson import one as ld_one, postings as ld_postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST_RE = re.compile(r"^([a-z0-9][a-z0-9\-]*)\.betterteam\.com$")
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$])\+?\d[\d\s().\-]{7,}\d(?!\w)")   # an international shape: 9+ digits with separators
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]*$")
CARD_RE = re.compile(r'<a class="font-semibold text-lg[^"]*" href="(/[^"]+)"[^>]*>([^<]+)</a>(.*?)(?=<a class="font-semibold text-lg|</section>|<h2|$)', re.S)
TOOLTIP_RE = re.compile(r'aria-label="([^"]*)"')
NONE_RE = re.compile(r"doesn(?:'|’|&#x27;|&#39;)t have any openings", re.I)
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[betterteam] {msg}", file=sys.stderr)


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
    if not HOST_RE.match(parts.netloc) or parts.netloc in ("www.betterteam.com", "app.betterteam.com", "s.betterteam.com"):
        die(f"{url}: not a Betterteam careers host — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(parts.netloc, Pace(parts.netloc, own=2.0)).wait()   # no Crawl-delay written; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en"})
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
    t = re.sub(r"</?(?:b|strong|em|i|u|a|span|font)\b[^>]*>", "", t)   # inline tags leave no space behind
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def tenant_of(arg):
    """`<slug>` or the careers URL → slug."""
    s = arg.strip()
    if "://" in s or ".betterteam.com" in s:
        parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
        m = HOST_RE.match(parts.netloc)
        if not m or parts.netloc in ("www.betterteam.com", "app.betterteam.com", "s.betterteam.com"):
            die(f"{arg}: not a Betterteam careers address (https://<slug>.betterteam.com/)")
        return m.group(1)
    if not SLUG_RE.match(s) or s in ("www", "app", "s"):
        die(f"{arg}: a tenant is written as the subdomain the careers URL spells — pandarg-117")
    return s


def card_line(tail):
    """The `text-sm` line after a title: remote flag, place/region, country, type; and the tooltip's address."""
    line = re.search(r'<div class="text-sm">(.*?)</div>\s*</div>', tail, re.S)
    raw = line.group(1) if line else tail[:600]
    tip = TOOLTIP_RE.search(raw)
    parts = [p for p in (htmlmod.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.split(r'<span class="mx-2">•</span>', raw)) if p]
    remote = any(p.lower() == "remote" for p in parts)
    rest = [p for p in parts if p.lower() != "remote"]
    emp = rest.pop() if rest and re.match(r"^(?:full|part)-time$|^(?:contract|temporary|internship|seasonal|volunteer|per diem)", rest[-1], re.I) else None
    place = region = country = None
    if tip:
        lines = [l.strip() for l in tip.group(1).replace("\\n", "\n").splitlines() if l.strip()]
        if len(lines) >= 2:
            country = lines[-1]
            m = re.match(r"^(.*?)\s+[A-Z0-9 \-]{3,10}$", lines[-2])   # «Tennessee 37312»
            region = (m.group(1) if m else lines[-2]) or None
            place = lines[-3] if len(lines) >= 3 else None
    if rest and (place is None or not tip):
        loc = rest[0]
        if "," in loc and place is None:
            place, region = [x.strip() for x in loc.split(",", 1)]
        elif remote and place is None:
            country = loc
    return {"remote": remote or None, "place": place, "region": region, "country": country, "employment_type": emp, "location": rest[0] if rest else None}


def cmd_jobs(a):
    slug = tenant_of(a.tenant)
    url = f"https://{slug}.betterteam.com/"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 «Page Not Found» — no such tenant today", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    cards = CARD_RE.findall(body)
    if not cards and "Current Positions" not in body and not NONE_RE.search(body):
        die(f"{url}: 200 without a «Current Positions» section — the page changed; not an empty board", EXIT_PARTIAL)
    org = re.search(r"<title>(.*?)</title>", body, re.S)
    company = re.sub(r"\s+Careers\s*$", "", htmlmod.unescape(org.group(1)).strip()) if org else None
    rows, seen = [], set()
    for href, title, tail in cards:
        path = urllib.parse.unquote(href)
        if path in seen:
            continue
        seen.add(path)
        r = {"source": "betterteam", "tenant": slug, "ledger_id": f"betterteam:{slug}:{path.strip('/')}", "id": path.strip("/"),
             "url": f"https://{slug}.betterteam.com{href}", "title": htmlmod.unescape(title).strip() or None, "company": company or None}
        r.update(card_line(tail))
        r["contacts_withheld"] = True
        rows.append(r)
    if a.country_code:
        rows = [r for r in rows if (r["country"] or "").upper() in (a.country_code.upper(), _country_name(a.country_code))]
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    if not cards:
        note(f"{slug}: 0 positions — the page says it has no openings; not an error." if NONE_RE.search(body) else f"{slug}: 0 positions — «Current Positions» is served with no card; not an error.")
    else:
        note(f"{th(len(rows))} emitted{' for ' + a.country_code.upper() if a.country_code else ''} of the {th(len(seen))} cards the page carries — no count is stated anywhere, the cards are the board.")


_NAMES = {"US": "UNITED STATES", "AU": "AUSTRALIA", "PH": "PHILIPPINES", "GB": "UNITED KINGDOM", "CA": "CANADA", "AE": "UNITED ARAB EMIRATES"}


def _country_name(code):
    return _NAMES.get(code.upper(), code.upper())


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url.strip())
    m = HOST_RE.match(parts.netloc)
    if not m or not re.match(r"^/[^/]+/?$", parts.path):
        die(f"{a.url}: not a Betterteam position address (https://<slug>.betterteam.com/<position>)")
    slug = m.group(1)
    url = f"https://{parts.netloc}{parts.path}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — no such position", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    p = next((x for x in ld_postings(body) if isinstance(x, dict)), None)
    if not p:
        die(f"{url}: 200 without a JobPosting — the page changed", EXIT_PARTIAL)
    loc = ld_one(p.get("jobLocation"))
    addr = ld_one(loc.get("address")) if loc else {}
    org = ld_one(p.get("hiringOrganization"))
    sal = ld_one(p.get("baseSalary"))
    val = ld_one(sal.get("value")) if sal else {}
    ident = ld_one(p.get("identifier"))
    out = {
        "source": "betterteam", "tenant": slug, "country": addr.get("addressCountry") or None,
        "ledger_id": f"betterteam:{slug}:{parts.path.strip('/')}", "id": ident.get("value") or parts.path.strip("/"), "url": url,
        "title": (p.get("title") or "").strip() or None, "company": org.get("name") or None, "employer_url": org.get("sameAs") or None,
        "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None,
        "posted": (p.get("datePosted") or "")[:10] or None, "employment_type": p.get("employmentType") or None,
        "salary": {"currency": sal.get("currency"), "min": val.get("minValue"), "max": val.get("maxValue"), "unit": val.get("unitText")} if sal else None,
        "description": scrub(text(p.get("description"))),
        "contacts_withheld": True,
    }
    print(json.dumps(out, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Betterteam — one tenant's positions, from its hosted careers page")
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the tenant's positions")
    j.add_argument("--tenant", required=True, help="the subdomain (pandarg-117) or the careers URL")
    j.add_argument("--country-code", help="ISO2 — filters on the card's country (the tooltip's last line, or the remote card's country)")
    j.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one position")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
