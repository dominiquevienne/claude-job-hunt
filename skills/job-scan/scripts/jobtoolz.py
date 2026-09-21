#!/usr/bin/env python3
"""Jobtoolz (a Belgian ATS — one tenant at a time): the employer's jobsite on `<tenant>.jobtoolz.com/<lang>` carries its whole list inline — `window.jobComponent([jobs], pageSize, locations, types, filters)` — so one request is the board; the job page `/<lang>/<slug>` on the same host carries a JobPosting. Issue #478.

  jobtoolz.py jobs --tenant <name> [--lang en|nl|fr] [--country-code ISO2]
  jobtoolz.py ad --url https://<tenant>.jobtoolz.com/<lang>/<slug>

THE TENANT is the subdomain of `jobtoolz.com` the employer's jobsite lives
on (`cnh-industrial`, `altebra`), found by the family's signature, never
composed. Rules (2026-09-20, 78 B, the same on `api.jobtoolz.com`):
`googlebot` `Allow: *`; `User-agent: *` / `Disallow: /*?` / `Disallow:
/*.pdf$` — **every address with a query string is refused in writing**, so
this adapter sends none: no `?page=`, no `?lang=`, no API call (the page
also carries a public bearer token for `api.jobtoolz.com`, never used). No
Crawl-delay; 2 s between requests are ours.

THE LIST: `<div id="jobs" x-data="window.jobComponent([{id, title,
button, url, image_url, location, types, filters: {filterIds, locationId,
types}}, …], 8, [locations], [types], [filter groups])">` — the whole
list, filtered and paged client-side (8 a page). The `url` points at the
employer's own domain when the jobsite is white-labelled
(`www.cnhind-belgium.be/en/<slug>`); the same slug is served on the
tenant host (`<tenant>.jobtoolz.com/en/<slug>`), which is what `ad` reads.
No count is stated: the inline list IS the board, and the note says so.
THE JOB PAGE: a schema.org JobPosting (title, datePosted, employmentType[],
hiringOrganization, jobLocation.address with streetAddress and postalCode —
not emitted —, addressLocality, addressCountry, description).

WITHHELD: the street and the postal code of the workplace; e-mail
addresses and telephone numbers in the description; the application (a
form on the job page) never touched; `contacts_withheld` on every record.
The list states a town, no country; `--country-code` stamps the rows and
says so; the job page says which.
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
from _ldjson import postings as ld_postings
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

BOARD = "jobtoolz"
DOMAIN = "jobtoolz.com"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

TENANT_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", re.I)
LANG_RE = re.compile(r"^[a-z]{2}$")
COMPONENT_RE = re.compile(r'<div id="jobs" x-data="window\.jobComponent\(\s*(.*?)\s*\)"', re.S)
JOB_PATH_RE = re.compile(r"^/([a-z]{2})/([A-Za-z0-9][A-Za-z0-9_\-]*)/?$")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{6,}\d(?!\w)")
_PACES = {}
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobtoolz] {msg}", file=sys.stderr)


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
        die(f"{url}: not this run's Jobtoolz tenant ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
    if parts.query:
        die(f"{url}: carries a query string — refused in writing to every agent (`Disallow: /*?`); never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en,nl,fr"})
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


def tenant_of(arg):
    s = (arg or "").strip().lower()
    if "://" in s or "/" in s:
        s = urllib.parse.urlsplit(s if "://" in s else "https://" + s).netloc
    if s.endswith("." + DOMAIN):
        s = s[: -len("." + DOMAIN)]
    if not s or "." in s or not TENANT_RE.match(s) or s in ("www", "api", "jobs", "help", "app"):
        die(f"{arg!r}: a tenant is the subdomain of {DOMAIN} the employer's jobsite lives on (cnh-industrial), found by the family's signature, never composed")
    return f"{s}.{DOMAIN}"


def component_of(markup):
    """The five arguments the page hands to `window.jobComponent`: jobs, page size, locations, types, filter groups — or None."""
    m = COMPONENT_RE.search(markup or "")
    if not m:
        return None
    arg = htmlmod.unescape(m.group(1))
    dec, pos, parts = json.JSONDecoder(), 0, []
    try:
        while pos < len(arg):
            while pos < len(arg) and arg[pos] in ", \n\t\r":
                pos += 1
            if pos >= len(arg):
                break
            v, pos = dec.raw_decode(arg, pos)
            parts.append(v)
    except ValueError:
        return None
    if not parts or not isinstance(parts[0], list):
        return None
    return parts


def labels(groups, ids):
    out = []
    for g in groups or []:
        for f in (g.get("filters") or []) if isinstance(g, dict) else []:
            if isinstance(f, dict) and f.get("id") in ids and f.get("id") not in ("", None):
                out.append(f.get("alias"))
    return out


def row(j, host, lang, groups, stamp):
    filt = j.get("filters") if isinstance(j.get("filters"), dict) else {}
    slug = urllib.parse.urlsplit(j.get("url") or "").path.rstrip("/").split("/")[-1] or None
    return {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{j.get('id')}", "id": str(j.get("id") or ""),
        "url": f"https://{host}/{lang}/{slug}" if slug else None, "employer_url": j.get("url") or None,
        "title": j.get("title"), "place": j.get("location") or None, "country": stamp,
        "schedule": j.get("types") or None, "categories": labels(groups, set(filt.get("filterIds") or [])),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    TENANT["host"] = host
    lang = (a.lang or "en").strip().lower()
    if not LANG_RE.match(lang):
        die(f"--lang {a.lang!r}: two letters (en, nl, fr)")
    stamp = (a.country_code or "").strip().upper() or None
    url = f"https://{host}/{lang}"
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404 — no such jobsite, or not in this language", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    parts = component_of(body)
    if parts is None:
        die(f"{url}: no `window.jobComponent([...])` in the page — not a Jobtoolz jobsite, or its shape changed.", EXIT_PARTIAL)
    jobs = [j for j in parts[0] if isinstance(j, dict)]
    groups = parts[4] if len(parts) > 4 and isinstance(parts[4], list) else []
    seen, rows = set(), []
    for j in jobs:
        if j.get("id") is None or j["id"] in seen:
            continue
        seen.add(j["id"])
        rows.append(row(j, host, lang, groups, stamp))
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    st_note = f"; country {stamp} stamped from --country-code (the list states a town, no country)" if stamp else ""
    note(f"{th(len(rows))} emitted — the inline list is the board: no count is stated, the page carries every job and pages them client-side ({parts[1] if len(parts) > 1 else '?'} a page){st_note}.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    host = parts.netloc.lower()
    m = JOB_PATH_RE.match(parts.path)
    if not host.endswith("." + DOMAIN) or host.split(".")[0] in ("www", "api", "jobs", "help", "app") or not m:
        die(f"{a.url!r}: not a Jobtoolz job address on a tenant host (https://<tenant>.{DOMAIN}/<lang>/<slug>)")
    TENANT["host"] = host
    url = f"https://{host}/{m.group(1)}/{m.group(2)}"        # any query string dropped — refused in writing
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped.", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    ps = ld_postings(body)
    if not ps:
        die(f"{url}: no JobPosting in the page — a Jobtoolz job page carries one; the shape changed, or the job is gone.", EXIT_PARTIAL)
    p = ps[0]
    org = p.get("hiringOrganization") if isinstance(p.get("hiringOrganization"), dict) else {}
    loc = p.get("jobLocation") if isinstance(p.get("jobLocation"), dict) else {}
    addr = loc.get("address") if isinstance(loc.get("address"), dict) else {}
    cc = addr.get("addressCountry")
    et = p.get("employmentType")
    r = {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{m.group(2)}", "id": m.group(2), "url": url,
        "title": p.get("title"), "company": org.get("name"),
        "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None,
        "country": cc.strip().upper() if isinstance(cc, str) and len(cc.strip()) == 2 else None,
        # streetAddress and postalCode are the premises' address and are not emitted
        "employment_type": et if isinstance(et, list) else ([et] if et else None), "posted": p.get("datePosted"), "closes": p.get("validThrough"),
        "description": (scrub(text(p.get("description"))) or "")[:20000] or None,
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Jobtoolz — one tenant's jobsite, whose page carries its whole list inline (no count stated, no query string ever sent — refused in writing), and its job pages' JobPosting; street and postal code withheld, no contact. Issue #478.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the jobsite page, one request; the inline list is the board")
    s.add_argument("--tenant", required=True, help="the subdomain (cnh-industrial), the host, or the jobsite's URL")
    s.add_argument("--lang", default="en", help="the jobsite's language path (en, nl, fr) — a path, never a query string")
    s.add_argument("--country-code", help="ISO2 to stamp the rows with — the list states a town, no country")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one job by its page on the tenant host (/<lang>/<slug>); street and postal code withheld, description scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
