#!/usr/bin/env python3
"""Nationale Vacaturebank (`www.nationalevacaturebank.nl`) — the Netherlands' largest general board (DPG Media), through the advertisement sitemap its rules declare; the search it refuses in writing is never taken. **And Intermediair (`www.intermediair.nl`), DPG's second board on the same template, by `--host intermediair` (#295).**

  nationalevacaturebank.py sitemap [--host intermediair] [--limit N] [--sample K]
  nationalevacaturebank.py ad --url <advertisement URL>            (the host is read off the address)

TWO HOSTS, ONE TEMPLATE. `--host` names the board — `nationalevacaturebank` (the default) or
`intermediair` — and everything below (the rules to the line, the sitemap layout with its file on
the apex host, the JobPosting on every page) was read the same on both: Intermediair measured
2026-09-13 16:15–16:17 UTC (2 495 distinct uuids in one file, 19 of 20 sampled served open, the
tab's «2.361 banen» not readable by HTTP) — `intermediair.md`. The record's `source` and
`ledger_id` carry the board's key, and `ad --url` reads the board off the address.

THE ROUTE IS THE SITEMAP, BECAUSE THE SEARCH IS REFUSED IN WRITING

`robots.txt` (`*`): `Disallow: /vacature/zoeken?*`, `/vacatures/*?page=`,
`/vacature/bladeren/`, `/archief/` — every paginated or queried listing is
refused to everyone, and this adapter never requests one (the bare
`/vacature/zoeken` is open and renders its count in the browser only, from
`api.nationalevacaturebank.nl`; not taken either — it is the same search).
A separate group names `ClaudeBot` and refuses everything; `Claude-User`
is under `*` — the decision of 2026-09-07. Ten `Sitemap:` lines; the one
that lists advertisements is `/cdn/sitemaps/vacature.xml`, an index whose
single `<sitemap>` element carries TWO `<loc>` (malformed, read as two
files) **on the apex host** `nationalevacaturebank.nl` — the guard is
taken there too, on the exact path (§3 bis). The files list
`/vacature/<uuid>/<slug>`, 50 000 + 39 733 = **89 733 distinct uuids** on
2026-09-13 15:27 UTC, no `<lastmod>` per entry; the index's own `lastmod`
(2026-09-02) is eleven days older than the files' contents.

THE SITE STATES NO FIGURE BY HTTP. Its «88.909 banen» (a browser tab,
13:07 UTC the same day) is rendered client-side from the API behind the
refused search — 824 fewer than the sitemap, and the adapter prints the
sitemap's count with that sentence, never a copied figure. **The second
source is a sample**: `--sample K` opens K advertisements spread over the
files and prints how many are still served with a `validThrough` on or
after today — and on 2026-09-13 15:30 UTC, **of 40 drawn at random, 24
were served (every one with an open validThrough), 12 answered 410 Gone
and 4 answered 404**. The sitemap lists what has left the board — its
89 733 is not the live inventory, and the adapter says so on the line.

EVERY ADVERTISEMENT CARRIES A JobPosting (`data-next-head`): title,
alternateName, description (HTML), datePosted, validThrough, employmentType,
hiringOrganization {name, email}, jobLocation {locality, region, NL,
postalCode, lat/lng}, baseSalary {EUR, min/max, MONTH}, workHours («1 - 40
uur per week»), educationRequirements, experienceRequirements
(monthsOfExperience), industry, directApply. The uuid is the id.
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
from _ldjson import absent_reason, postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARDS = {"nationalevacaturebank": "www.nationalevacaturebank.nl", "intermediair": "www.intermediair.nl"}   # DPG Media's two boards on one template — each measured before it was listed
BASE = "https://www.nationalevacaturebank.nl"
INDEX = f"{BASE}/cdn/sitemaps/vacature.xml"
UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
AD_RE = re.compile(r"^https://(?:www\.)?(nationalevacaturebank|intermediair)\.nl/vacature/(" + UUID + r")/([^/?#]+)/?$")
# the search and every paginated listing are refused in writing to `*` — never requested, whatever the caller asks
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
REFUSED_RE = re.compile(r"/vacature/zoeken\?|/vacatures/[^?]*\?.*page=|/vacature/bladeren/|/archief/")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[nationalevacaturebank] {msg}", file=sys.stderr)


def gate(url):
    if REFUSED_RE.search(url):
        die(f"{url}: a listing the rules refuse in writing (`Disallow: /vacature/zoeken?*`, `/vacatures/*?page=`) — not requested by any route.", EXIT_REFUSED)
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
        _PACES[host] = Pace(host, own=1.5)   # no Crawl-delay in either rules file; 1.5 s is ours
    return _PACES[host]


def board_of(name):
    """The board key → its host, or a clean exit naming the two the script knows."""
    key = (name or "nationalevacaturebank").strip().lower()
    if key not in BOARDS:
        die(f"--host {name!r}: the boards this script reads are {', '.join(BOARDS)} — each measured before it was listed")
    return key, BOARDS[key]


def get(url):
    gate(url)
    pace_for(urllib.parse.urlsplit(url).netloc).wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "nl"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
            if enc in ("gzip", "x-gzip") or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            return r.getcode(), decode_body(raw, r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    """Thousands with a space — the repo's figure style."""
    return f"{n:,}".replace(",", " ")


def locs(xml):
    """Every <loc> in document order — the index puts two in one <sitemap>, and a reader per element would keep one."""
    return [htmlmod.unescape(m.group(1)).strip() for m in re.finditer(r"<loc>\s*([^<]+?)\s*</loc>", xml or "")]


def today():
    import datetime
    return datetime.date.today().isoformat()


def cmd_sitemap(a):
    key, host = board_of(getattr(a, "host", None))
    index = f"https://{host}/cdn/sitemaps/vacature.xml"
    code, body = get(index)
    if code != 200:
        die(f"{index}: HTTP {code}", EXIT_PARTIAL)
    files = [u for u in locs(body) if u.endswith(".xml")]
    if not files:
        die(f"{index}: no sitemap file in the index ({len(body)} characters) — the shape changed or the body is not the index.", EXIT_PARTIAL)
    lastmod = re.search(r"<lastmod>\s*([^<]+?)\s*</lastmod>", body)
    rows, seen, per_file = [], set(), []
    for f in files:
        code, xml = get(f)
        if code != 200:
            die(f"{f}: HTTP {code} — {th(len(rows))} read before it; a partial walk is not a count.", EXIT_PARTIAL)
        n_here = 0
        for u in locs(xml):
            m = AD_RE.match(u)
            if not m or m.group(1) != key or m.group(2) in seen:   # a file that named the other board's host would be a fault, not a row
                continue
            seen.add(m.group(2))
            rows.append({"source": key, "country": "NL", "ledger_id": f"{key}:{m.group(2)}",
                         "id": m.group(2), "url": u, "slug": m.group(3)})
            n_here += 1
        per_file.append((f.rsplit("/", 1)[-1], n_here))
    if not rows:
        die(f"{len(files)} file(s) in the index and no advertisement address matched — a reading fault, not an empty board.", EXIT_PARTIAL)
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(rows)
    note(f"**{th(n)} distinct advertisement uuid(s)** on {host} in {len(files)} file(s) ({', '.join(f'{f} {th(c)}' for f, c in per_file)}); "
         f"{th(len(emitted))} emitted" + (f" (--limit {a.limit})" if a.limit else "") + f"; the index's own lastmod {lastmod.group(1) if lastmod else 'absent'}.")
    note("The site states no figure by HTTP — its «N banen» is rendered in a browser from the API behind the search the rules refuse; no second figure is compared here.")
    if a.sample:
        k = min(a.sample, n)
        step = max(1, n // k)
        picks = [rows[i] for i in range(0, n, step)][:k]
        open_, gone410, gone404, other = 0, 0, 0, 0
        for r in picks:
            code, page = get(r["url"])
            if code == 410:
                gone410 += 1
                continue
            if code == 404:
                gone404 += 1
                continue
            if code != 200:
                other += 1
                continue
            found = postings(page)
            vt = (found[0].get("validThrough") or "")[:10] if found else ""
            if vt and vt >= today():
                open_ += 1
            else:
                other += 1
        note(f"Sample of {k} spread over the file(s): {open_} served with a JobPosting whose validThrough is on or after {today()}, "
             f"{gone410} gone (410), {gone404} gone (404), {other} other (served without an open validThrough, or another code) — "
             f"**the sitemap lists what has left the board**; its count is not the live inventory.")


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not an advertisement address — expected https://www.<nationalevacaturebank|intermediair>.nl/vacature/<uuid>/<slug>")
    key, ident = m.group(1), m.group(2)
    code, body = get(a.url)
    if code in (404, 410):
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    found = postings(body)
    if not found:
        why = absent_reason(body)
        if getattr(why, "our_fault", False):
            die(f"{a.url}: {why.text} **The page announces a JobPosting and this read none.**")
        die(f"{a.url}: {why.text}", EXIT_PARTIAL)
    d = found[0]
    org = d.get("hiringOrganization") if isinstance(d.get("hiringOrganization"), dict) else {}
    loc = d.get("jobLocation") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    bs = d.get("baseSalary") if isinstance(d.get("baseSalary"), dict) else {}
    val = bs.get("value") if isinstance(bs.get("value"), dict) else bs
    et = d.get("employmentType")
    exp = d.get("experienceRequirements") if isinstance(d.get("experienceRequirements"), dict) else {}
    edu = d.get("educationRequirements") if isinstance(d.get("educationRequirements"), dict) else {}

    def money(v):
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return None
    print(json.dumps({
        "source": key, "country": "NL", "ledger_id": f"{key}:{ident}", "id": ident, "url": a.url,
        "title": text(d.get("title")), "alternate_name": d.get("alternateName"),
        "employer": org.get("name"),
        # `hiringOrganization.email` is a recruiter's own address on this template (a first name at the employer's domain) — a contact, never emitted (#295 fixed what #287 let through)
        "contacts_withheld": True,
        "employment_type": et if isinstance(et, list) else ([et] if et else []),
        "work_hours": d.get("workHours"),
        "city": addr.get("addressLocality"), "region": addr.get("addressRegion"), "postal_code": addr.get("postalCode"),
        "address_country": addr.get("addressCountry"),
        "industry": d.get("industry"), "occupational_category": d.get("occupationalCategory"),
        "posted": d.get("datePosted"), "valid_through": d.get("validThrough"),
        "salary_currency": bs.get("currency"), "salary_min": money(val.get("minValue")), "salary_max": money(val.get("maxValue")),
        "salary_unit": (val.get("unitText") or "").strip() or None,
        "months_of_experience": money(exp.get("monthsOfExperience")), "education": edu.get("credentialCategory"),
        "direct_apply": d.get("directApply"),
        "description": MAIL_RE.sub("[e-mail withheld]", text(d.get("description")))[:20000], "language": "nl",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Nationale Vacaturebank — the advertisement sitemap the rules declare (the search is refused in writing and never taken), a sample of pages as the freshness witness, and the JobPosting every advertisement carries.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sitemap", help="every advertisement uuid in the declared sitemap files — two files, ~16 MB of XML; --sample K opens K pages as a freshness witness")
    s.add_argument("--host", default="nationalevacaturebank", help="the board: nationalevacaturebank (default) or intermediair — DPG Media's two boards on one template")
    s.add_argument("--limit", type=int)
    s.add_argument("--sample", type=int, help="open K advertisements spread over the files and count those still open")
    s.set_defaults(fn=cmd_sitemap)
    d = sub.add_parser("ad", help="one advertisement, from its JSON-LD")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
