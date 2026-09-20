#!/usr/bin/env python3
"""ReachMee (Talentech's Swedish ATS — one tenant at a time): the employer's list at `web<NNN>.reachmee.com/ext/<I0xx>/<nnn>/main?site=<n>&lang=SE&validator=<hash>` is one server-rendered table (`#jobsTable`) with the tenant's own columns; no page, no count stated — the table is the board; the job page `…/job?…&job_id=<id>` carries the advert and a contact section. Issue #470.

  reachmee.py jobs --tenant "https://web103.reachmee.com/ext/I011/853/main?site=6&lang=SE&validator=<hash>" [--country-code ISO2]
  reachmee.py ad --url "https://web103.reachmee.com/ext/I011/853/job?site=6&lang=SE&validator=<hash>&job_id=29920"

THE TENANT is the list's own address — the employer's site links it —
`ext/<instance>/<customer>/main?site=<n>&validator=<hash>`: the
`validator` is the tenant's public list key, printed in every visitor's
address (the SparkHire shape), replayed as given, never composed. The
hosts are `web103.reachmee.com`, `web106.reachmee.com`, …: any
`web<digits>.reachmee.com` the address names, one per run. Rules (read
2026-09-20): `web103.reachmee.com/robots.txt` 404 — no rules; 2 s between
requests are ours.

THE LIST: `<table id='jobsTable'>` — `<th id='col-N'>` labels the
tenant chose (col-1 the title, col-6 the closing date, col-9 the town,
col-8 the county, col-17 the employment form, col-3 the reference, col-11
/ col-14 business and experience areas), one `<tr>` per job with the title
linked to `…/job?…&job_id=<id>`. **No page, no count** (Linköping
University 45 rows, Sodexo 23 — 2026-09-20): `jobs` prints the table's
length and says no count is stated.

THE JOB PAGE: `h1#jobad-heading`, `p.extid` (the town, the reference),
`div.jobad-body` (HTML), `section.contact` with `contact-person` blocks
(name, position, telephone, e-mail) — NOT emitted; a login to apply.

WITHHELD: the contact section, e-mail addresses and telephone numbers in
the advert, the application; `contacts_withheld` on every record. The
list states towns and counties, not countries; `--country-code` stamps
the rows and says so.
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

BOARD = "reachmee"
HOST_RE = re.compile(r"^web\d+\.reachmee\.com$")
LIST_PATH_RE = re.compile(r"^/ext/([A-Za-z0-9]+)/(\d+)/main/?$")
JOB_PATH_RE = re.compile(r"^/ext/([A-Za-z0-9]+)/(\d+)/job/?$")
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

TABLE_RE = re.compile(r"<table[^>]*id='jobsTable'[^>]*>(.*?)</table>", re.S)
HEAD_RE = re.compile(r"<th id='col-(\d+)'>(.*?)</th>", re.S)
ROW_RE = re.compile(r"<tr>(.*?)</tr>", re.S)
CELL_RE = re.compile(r"<td>(.*?)</td>", re.S)
JOB_ID_RE = re.compile(r"job_id=(\d+)")
H1_RE = re.compile(r'<h1 id="jobad-heading"[^>]*>(.*?)</h1>', re.S)
EXTID_RE = re.compile(r'<p class="text-color-muted extid">(.*?)</p>', re.S)
BODY_OPEN_RE = re.compile(r'<div class="jobad-body"[^>]*>')
DIV_RE = re.compile(r"<div\b|</div>", re.I)
CONTACT_RE = re.compile(r'<section class="contact">.*?</section>', re.S)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{6,}\d(?!\w)")
COLS = {"1": "title", "6": "closes", "9": "place", "8": "region", "17": "employment_type", "3": "reference"}
_PACES = {}
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[reachmee] {msg}", file=sys.stderr)


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
    if not TENANT["host"] or host != TENANT["host"] or not HOST_RE.match(host):
        die(f"{url}: not this run's ReachMee host ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
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
    t = re.sub(r'<span[^>]*style="display:\s*none[^"]*"[^>]*>.*?</span>', "", t, flags=re.S)   # the sort key, not a value
    t = re.sub(r"<span class='show-mobile'>.*?</span>", "", t, flags=re.S)                       # the mobile label, not a value
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
    """The list's address → (host, instance, customer, {site, lang, validator})."""
    s = (arg or "").strip()
    parts = urllib.parse.urlsplit(s if "://" in s else "https://" + s)
    host = parts.netloc.lower()
    m = LIST_PATH_RE.match(parts.path)
    q = {k.lower(): v[0] for k, v in urllib.parse.parse_qs(parts.query).items()}
    if not HOST_RE.match(host) or not m or not q.get("validator") or not q.get("site"):
        die(f"{arg!r}: a tenant is the list's own address — https://web<NNN>.reachmee.com/ext/<instance>/<customer>/main?site=<n>&lang=SE&validator=<hash> — as the employer's site links it, never composed")
    return host, m.group(1), m.group(2), {"site": q["site"], "lang": q.get("lang") or "SE", "validator": q["validator"]}


def list_url(host, inst, cust, q):
    return f"https://{host}/ext/{inst}/{cust}/main?" + urllib.parse.urlencode([("site", q["site"]), ("lang", q["lang"]), ("validator", q["validator"])])


def job_url(host, inst, cust, q, jid):
    return f"https://{host}/ext/{inst}/{cust}/job?" + urllib.parse.urlencode([("site", q["site"]), ("lang", q["lang"]), ("validator", q["validator"]), ("job_id", jid)])


def rows_of(markup):
    tm = TABLE_RE.search(markup or "")
    if not tm:
        return None, None
    heads = [(cid, text(lab)) for cid, lab in HEAD_RE.findall(tm.group(1))]
    out = []
    for tr in ROW_RE.findall(tm.group(1)):
        cells = CELL_RE.findall(tr)
        if not cells:
            continue
        jm = JOB_ID_RE.search(cells[0])
        if not jm:
            continue
        out.append((jm.group(1), [text(c) for c in cells]))
    return heads, out


def row(host, inst, cust, q, jid, cells, heads, country):
    named, fields = {}, {}
    for (cid, label), val in zip(heads, cells):
        if not val:
            continue
        if cid in COLS:
            named[COLS[cid]] = val
        fields[label or f"col-{cid}"] = val
    return {
        "source": BOARD, "tenant": f"{host}/ext/{inst}/{cust}?site={q['site']}", "ledger_id": f"{BOARD}:{cust}:{jid}", "id": jid,
        "url": job_url(host, inst, cust, q, jid),
        "title": named.get("title"), "place": named.get("place"), "region": named.get("region"), "closes": named.get("closes"),
        "employment_type": named.get("employment_type"), "reference": named.get("reference"), "country": country,
        "fields": {k: v for k, v in fields.items() if k not in (heads[0][1] if heads else None,)},   # the tenant's own labels, the title once
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    host, inst, cust, q = tenant_of(a.tenant)
    TENANT["host"] = host
    url = list_url(host, inst, cust, q)
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    heads, rows = rows_of(body)
    if rows is None:
        die(f"{url}: no `#jobsTable` in the page ({len(body)} characters) — not a ReachMee list (a wrong validator or site answers a page without it), or its shape changed.", EXIT_PARTIAL)
    country = (a.country_code or "").strip().upper() or None
    seen, out = set(), []
    for jid, cells in rows:
        if jid in seen:
            continue
        seen.add(jid)
        out.append(row(host, inst, cust, q, jid, cells, heads, country))
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    stamp = f"; country {country} stamped from --country-code (the list states towns and counties, not countries)" if country else ""
    note(f"{th(len(out))} emitted — the table is the board: no count is stated anywhere and no page follows{stamp}.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    host = parts.netloc.lower()
    m = JOB_PATH_RE.match(parts.path)
    q = {k.lower(): v[0] for k, v in urllib.parse.parse_qs(parts.query).items()}
    if not HOST_RE.match(host) or not m or not q.get("validator") or not q.get("site") or not (q.get("job_id") or "").isdigit():
        die(f"{a.url!r}: not a ReachMee job address (https://web<NNN>.reachmee.com/ext/<instance>/<customer>/job?site=<n>&lang=SE&validator=<hash>&job_id=<id>)")
    TENANT["host"] = host
    qq = {"site": q["site"], "lang": q.get("lang") or "SE", "validator": q["validator"]}
    url = job_url(host, m.group(1), m.group(2), qq, q["job_id"])
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped.", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    h1 = H1_RE.search(body)
    desc = inner_div(body, BODY_OPEN_RE)
    if not h1 or desc is None:
        die(f"{url}: no `jobad-heading` or no `jobad-body` in the page — not a ReachMee job page, or the job is gone.", EXIT_PARTIAL)
    ext = [text(x) for x in EXTID_RE.findall(body)]
    ref = next((x.split(" ", 1)[1] if " " in x else None for x in ext if x and x.lower().startswith(("referensnummer", "reference"))), None)
    place = next((x for x in ext if x and not x.lower().startswith(("referensnummer", "reference"))), None)
    r = {
        "source": BOARD, "tenant": f"{host}/ext/{m.group(1)}/{m.group(2)}?site={qq['site']}", "ledger_id": f"{BOARD}:{m.group(2)}:{q['job_id']}", "id": q["job_id"], "url": url,
        "title": text(h1.group(1)), "place": place, "reference": ref,
        "description": (scrub(text(CONTACT_RE.sub("", desc))) or "")[:20000] or None,   # the contact section is never inside the body, but a template could move it
        "contact_section_withheld": bool(CONTACT_RE.search(body)),
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="ReachMee — one tenant's jobs from its one-page table (no count stated: the table is the board) and its job pages (the contact section withheld). Issue #470.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the tenant's table, one request")
    s.add_argument("--tenant", required=True, help="the list's address as the employer's site links it (…/main?site=&lang=&validator=)")
    s.add_argument("--country-code", help="ISO2 to stamp the rows with — the list states towns and counties, not countries")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one job by its page (…/job?…&job_id=); the contact section withheld, the advert scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
