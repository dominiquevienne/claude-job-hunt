#!/usr/bin/env python3
"""Varbi (a Swedish ATS — one tenant at a time): the employer's site on `<tenant>.varbi.com` renders every open job in one table (`#table-position`: title, town, department, closing date), no page and no count stated — the table is the board; the job page `/se/what:job/jobID:<id>/` carries the advert and a «quick info» table. Issue #469.

  varbi.py jobs --tenant <name> [--lang se|en] [--country-code ISO2]
  varbi.py ad --url https://<tenant>.varbi.com/se/what:job/jobID:<id>/

THE TENANT is the subdomain of `varbi.com` the employer's site lives on
(`su`, `solna`, `regionstockholm`, `arbetsformedlingen`), found by the
family's signature, never composed. Rules (read 2026-09-20 on two tenants,
272 B): seven named crawlers refused `/` (SemrushBot, Teoma, Gigabot,
Robozilla, dotbot, AhrefsBot…), nothing for `*`, no Crawl-delay; the
vendor's `varbi.com` answers 0 bytes in 200. 2 s between requests are ours.

THE LIST: the tenant's root (or `/en/`) is the list — `<table
id="table-position">`, one `<tr>` per job with `td.pos-title` (a link to
`/se/what:job/jobID:<id>/`), `pos-town`, `pos-subcompany`, `pos-ends`.
**No page, no count**: Stockholm University 66 rows, Region Stockholm 476
ids in one page (2026-09-20); `jobs` prints the table's length as the
count and says no count is stated anywhere.

THE JOB PAGE: `<h1>`, `div.job-desc` (HTML), `table.quick-info` with
labelled rows — type of employment, hours, pay form, number of positions,
working hours, town, county, country, reference number, published, ends —
and two rows of people: `quick-info-union-representative` and the contact
persons, each a `contactList` of names, telephones and e-mails: NOT emitted.
The application is a login (`what:login/…/apply:1`), never touched.

WITHHELD: the contact and union rows of the quick info; e-mail addresses
and telephone numbers in the description; `contacts_withheld` on every
record. The list states the town, not the country; the job page does
(«Sverige» → SE); `--country-code` on `jobs` stamps the rows and says so.
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

BOARD = "varbi"
DOMAIN = "varbi.com"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

TENANT_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", re.I)
TABLE_RE = re.compile(r'<table[^>]*id="table-position"[^>]*>(.*?)</table>', re.S)
ROW_RE = re.compile(r"<tr>(.*?)</tr>", re.S)
CELL_RE = re.compile(r'<td class="[^"]*\bpos-([a-z]+)"[^>]*>(.*?)</td>', re.S)
JOB_RE = re.compile(r"jobID:(\d+)")
AD_PATH_RE = re.compile(r"^/([a-z]{2})/what:job/jobID:(\d+)/?$")
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
DESC_OPEN_RE = re.compile(r'<div class="job-desc[^"]*"[^>]*>')
DIV_RE = re.compile(r"<div\b|</div>", re.I)
QUICK_RE = re.compile(r'<tr class="quick-info-([a-z\-]+)">(.*?)</tr>', re.S)
PEOPLE_ROWS = ("union-representative", "contact", "contacts", "contact-person", "contact-persons")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{6,}\d(?!\w)")
COUNTRIES = {"sverige": "SE", "sweden": "SE", "norge": "NO", "norway": "NO", "danmark": "DK", "denmark": "DK", "finland": "FI", "suomi": "FI",
             "island": "IS", "iceland": "IS", "tyskland": "DE", "germany": "DE", "storbritannien": "GB", "united kingdom": "GB"}
_PACES = {}
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[varbi] {msg}", file=sys.stderr)


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
        die(f"{url}: not this run's Varbi tenant ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "sv,en"})
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


def inner_div(markup, open_re):
    m = open_re.search(markup or "")
    if not m:
        return None
    depth, pos = 1, m.end()
    for t in DIV_RE.finditer(markup, m.end()):
        depth += 1 if t.group(0).lower().startswith("<div") else -1
        if depth == 0:
            return markup[pos:t.start()]
    return markup[pos:]


def tenant_of(arg):
    s = (arg or "").strip().lower()
    if "://" in s or "/" in s:
        s = urllib.parse.urlsplit(s if "://" in s else "https://" + s).netloc
    if s.endswith("." + DOMAIN):
        s = s[: -len("." + DOMAIN)]
    if not s or "." in s or not TENANT_RE.match(s) or s in ("www", "career", "varbi"):
        die(f"{arg!r}: a tenant is the subdomain of {DOMAIN} the employer's site lives on (su, solna), found by the family's signature, never composed")
    return f"{s}.{DOMAIN}"


def rows_of(markup):
    """(rows or None) — None when the page carries no `#table-position` at all."""
    tm = TABLE_RE.search(markup or "")
    if not tm:
        return None
    out = []
    for tr in ROW_RE.findall(tm.group(1)):
        cells = {k: text(v) for k, v in CELL_RE.findall(tr)}
        jm = JOB_RE.search(tr)
        if jm and cells.get("title"):
            out.append((jm.group(1), cells))
    return out


def row(host, jid, cells, lang, country):
    return {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{jid}", "id": jid,
        "url": f"https://{host}/{lang}/what:job/jobID:{jid}/",
        "title": cells.get("title"), "place": cells.get("town") or None, "department": cells.get("subcompany") or None,
        "closes": cells.get("ends") or None, "country": country,
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    TENANT["host"] = host
    lang = (a.lang or "se").strip().lower()
    url = f"https://{host}/" + ("" if lang == "se" else f"{lang}/")
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    rows = rows_of(body)
    if rows is None:
        die(f"{url}: no `#table-position` in the page ({len(body)} characters) — not a Varbi tenant's site, or its shape changed.", EXIT_PARTIAL)
    country = (a.country_code or "").strip().upper() or None
    seen, out = set(), []
    for jid, cells in rows:
        if jid in seen:
            continue
        seen.add(jid)
        out.append(row(host, jid, cells, lang, country))
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    stamp = f"; country {country} stamped from --country-code (the list states towns, not countries)" if country else ""
    note(f"{th(len(out))} emitted — the table is the board: no count is stated anywhere and no page follows{stamp}.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    host = parts.netloc.lower()
    m = AD_PATH_RE.match(parts.path)
    if not host.endswith("." + DOMAIN) or not m:
        die(f"{a.url!r}: not a Varbi job address (https://<tenant>.{DOMAIN}/se/what:job/jobID:<id>/)")
    TENANT["host"] = host
    lang, jid = m.group(1), m.group(2)
    url = f"https://{host}/{lang}/what:job/jobID:{jid}/"
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped.", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    h1 = H1_RE.search(body)
    desc = inner_div(body, DESC_OPEN_RE)
    if not h1 or desc is None:
        die(f"{url}: no title or no `job-desc` in the page — not a Varbi job page, or the job is gone.", EXIT_PARTIAL)
    info, people = {}, []
    for key, tr in QUICK_RE.findall(body):
        if key in PEOPLE_ROWS or "contact" in key or "union" in key:
            people.append(key)                                  # the contact persons and the union representatives: names, telephones, e-mails — withheld
            continue
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)
        if len(cells) >= 2:
            label, val = text(cells[0]), text("".join(cells[1:]))
            if label and val:
                info[key] = (label, val)
    country_name = info.get("country", (None, None))[1]
    r = {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{jid}", "id": jid, "url": url,
        "title": text(h1.group(1)),
        "place": info.get("town", (None, None))[1], "region": info.get("county", (None, None))[1],
        "country": COUNTRIES.get((country_name or "").lower()) or (country_name.upper() if country_name and len(country_name) == 2 else None), "country_name": country_name,
        "employment_type": info.get("type-of-employment", (None, None))[1], "extent": info.get("hours", (None, None))[1], "pay": info.get("pay", (None, None))[1],
        "positions": info.get("number-of-positions", (None, None))[1], "working_hours": info.get("working-hours", (None, None))[1],
        "reference": info.get("reference-number", (None, None))[1], "published": info.get("published", (None, None))[1], "closes": info.get("ends", (None, None))[1],
        "fields": {lab: val for k, (lab, val) in info.items()},   # the tenant's own labels
        "description": (scrub(text(desc)) or "")[:20000] or None,
        "people_rows_withheld": sorted(people),
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Varbi — one tenant's open jobs from its one-page table (no count stated: the table is the board) and its job pages (the quick info, the contact and union rows withheld). Issue #469.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the tenant's table, one request")
    s.add_argument("--tenant", required=True, help="the subdomain (su), the host, or the site's URL")
    s.add_argument("--lang", default="se", help="se (default) or en — the site's own language paths")
    s.add_argument("--country-code", help="ISO2 to stamp the rows with — the list states towns, not countries")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one job by its page (/<lang>/what:job/jobID:<id>/); people withheld, description scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
