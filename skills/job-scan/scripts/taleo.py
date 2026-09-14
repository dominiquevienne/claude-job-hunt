"""Oracle Taleo Enterprise — one tenant's careersection, read the way its own page reads itself.

Taleo is an ATS: each employer runs it on its own host (`<tenant>.taleo.net`) and
publishes its jobs under `/careersection/<section>/joblist.ftl`. One adapter, one
tenant per invocation — the user names the host AND the career section, both taken
from the employer's careers URL (`dubaiholding.taleo.net`, `jum_ext_quickapply`).
`/careersection/` alone lands on an administrative table of contents, not on a list,
so the section is not guessed.

THE PAGE IS A DATA ISLAND, NOT A TABLE. The list page ships its rows in a hidden
field, `initialHistory`, as one `!|!`-separated string, and its JavaScript fills a
template row from that string by POSITION. The position's meaning is declared beside
it: the page's inline script carries, for the list `listRequisition`, an array `_hlid`
whose k-th entry names the k-th slot of every row (`reqlistitem.title`,
`reqlistitem.contestnumber`, `reqlistitem.basiclocations`, `reqlistitem.postingdate`,
`reqlistitem.organization`, `reqlistitem.jobschedule`…). A row is `len(_hlid)` values;
this file zips the two, exactly as the page does, so a tenant that shows other columns
changes nothing here. Values are `escape()`-encoded (`%26`, `%u2019`), a colon is
written `\\:`, and an HTML value starts with `!*!`.

THE PAGER IS AN AJAX POST. The pages beyond the first come from
`POST joblist.ajax` with the pager component's parameters (`ftlcompid=rlPager`,
`ftlcompclass=PagerComponent`, `rlPager.currentPage=N`) plus the page's `ftlpageid`
and `ftlhistory` — no session, no cookie beyond `locale`. Its answer is four `!$!`
sections: request id, pager header, the rows, and field values among which
`listRequisition.nbElements` is THE COUNT THE PORTAL STATES — the witness, machine-
readable, beside the `(N jobs found)` the page prints. The first page is read by the
same POST as the others: the island of the HTML page and the ajax pages sort
differently (5 of 32 overlapped on the tenant read), and mixing them would count short.

The job page (`jobdetail.ftl?job=<contest>`) is the same island under the list
`descRequisition`: `reqlistitem.title`, `.contestnumber`, `.description`,
`.qualification`, `.primarylocation`, `.jobfield`, `.organization`, `.joblevel`,
`.postingdate` — tenant-configured, keyed the same way.

MEASURED on `dubaiholding.taleo.net` (Jumeirah, section `jum_ext_quickapply`),
2026-09-14 04:11–04:2x UTC: `robots.txt` 404 (no rules, certain); the page prints
«Job Openings (32 jobs found)»; page 1 by ajax 25 rows, page 2 7 rows, union 32,
`nbElements` 32 — equal. The island of the HTML page alone gave 25 with 5 of them
repeated on ajax page 2: hence the first page by POST. A POST whose body encodes a
space as `+` answers HTTP 500 «A system error has occurred»; `%20` is served. Six
guessed tenant hosts (emerson, tetrapak, mattel, cn, bbraun, tdbank `.taleo.net`) do
not resolve on 2026-09-14 — the family has shrunk to the tenants that still run it,
and a tenant is named, never guessed. Taleo Business Edition (`tbe.taleo.net/tbe/…`)
is another product with another URL shape: not read here, no tenant named.

Contacts: the description is the employer's own HTML; e-mail addresses and telephone
numbers in it are withheld. The apply route (`Apply`, `Apply by Email`) is never
followed.

    python3 taleo.py list --host dubaiholding.taleo.net --section jum_ext_quickapply --all
    python3 taleo.py ad --url 'https://dubaiholding.taleo.net/careersection/jum_ext_quickapply/jobdetail.ftl?job=2600001H&lang=en'

Exits: 0 read; 2 broken; 3 the job is gone; 6 partial (a bounded walk that fell short
of the stated count, a page the portal refused); 7 refused by the rules; 8 the rules
could not be read.
"""

import argparse
import html
import http.cookiejar
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

DEFAULT_PAGES = 10
AD_RE = re.compile(r"^https?://([a-z0-9.-]+)/careersection/([A-Za-z0-9_+-]+)/jobdetail\.ftl\?(?:.*&)?job=([A-Za-z0-9]+)(?:&.*)?$", re.I)
FOUND_RE = re.compile(r"\((\d[\d,.]*) jobs? found\)")
HLID_RE = r"%s\s*:\s*\{[^}]*?_hlid\s*:\s*\[([^\]]*)\]"
HIDDEN_RE = re.compile(r'<input[^>]*\bname="(ftlpageid|ftlhistory|initialHistory)"[^>]*\bvalue="([^"]*)"')
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\d[\d\s().-]{6,}\d(?!\w)")

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

_PACES = {}
_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_JAR))


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[taleo] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, data=None):
    """One GET, or one POST when `data` (a list of pairs) is given — `(code, body)`."""
    gate(url)
    host = urllib.parse.urlsplit(url).netloc
    _PACES.setdefault(host, Pace(host, own=3.0)).wait()
    headers = {"User-Agent": UA, "Accept": "text/html, */*"}
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data, quote_via=urllib.parse.quote).encode()   # `+` for a space is answered HTTP 500
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(wire_url(url), data=body, headers=headers)
    try:
        with _OPENER.open(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def unesc(v):
    """The island's `escape()` encoding, then Taleo's `\\:` for a colon."""
    v = re.sub(r"%u([0-9A-Fa-f]{4})", lambda m: chr(int(m.group(1), 16)), v or "")
    v = re.sub(r"%([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), v)
    return v.replace("\\:", ":")


def clean(s):
    s = re.sub(r"<(script|style|svg)\b.*?</\1>", "", s or "", flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h\d>|</tr>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def value(v):
    """One island value as text — an HTML value (`!*!` prefix) cleaned, a plain one unescaped."""
    v = unesc(v)
    return clean(v[3:]) if v.startswith("!*!") else html.unescape(v).strip()


def redact(s):
    s = EMAIL_RE.sub("[e-mail withheld]", s or "")
    return PHONE_RE.sub(lambda m: "[phone withheld]" if sum(c.isdigit() for c in m.group(0)) >= 9 else m.group(0), s)


def norm_host(h):
    h = re.sub(r"^https?://", "", (h or "").strip().lower()).split("/")[0]
    if not h:
        die("--host is required: the tenant, e.g. dubaiholding.taleo.net.")
    return h


def norm_section(s):
    s = (s or "").strip().strip("/")
    if not re.fullmatch(r"[A-Za-z0-9_+-]+", s):
        die("--section is required: the career section in the employer's URL, e.g. jum_ext_quickapply (from /careersection/jum_ext_quickapply/…).")
    return s


def hlid(page, list_name):
    """The declared slot names of a list — `['reqlistitem.no', 'reqlistitem.title', …]`."""
    m = re.search(HLID_RE % re.escape(list_name), page or "", re.S)
    if not m:
        return None
    return [x.strip().strip("'\"") for x in m.group(1).split(",") if x.strip()]


def hidden(page):
    return {k: html.unescape(v) for k, v in HIDDEN_RE.findall(page or "")}


def rows_of(values, keys):
    """The flat value list cut into rows of `len(keys)`, each a dict; a slot named twice keeps its first non-empty value."""
    n = len(keys)
    out = []
    for i in range(0, len(values) - n + 1, n):
        row = {}
        for k, v in zip(keys, values[i:i + n]):
            if k == "reqlistitem.no":
                continue
            k = k.split(".", 1)[-1]
            if k not in row or not row[k]:
                row[k] = v
        out.append(row)
    return out


def island(page):
    """`initialHistory` of an HTML page → `[ajxinf, header, values, fields]`, each a list."""
    h = hidden(page).get("initialHistory")
    if not h:
        return None
    return [s.split("!|!") for s in h.split("!%24!")]


def ajax_sections(body):
    return [s.split("!|!") for s in (body or "").split("!$!")]


def record(host, section, row, lang):
    ident = value(row.get("contestnumber", ""))
    title = redact(value(row.get("title", "")))
    return {
        "source": "taleo", "country": None, "tenant": host, "ledger_id": f"taleo:{host}:{ident}", "id": ident,
        "url": f"https://{host}/careersection/{section}/jobdetail.ftl?job={ident}&lang={lang}",
        "title": title or None,
        "location": redact(value(row.get("basiclocations", "") or row.get("primarylocation", ""))) or None,
        "company": redact(value(row.get("organization", ""))) or None,
        "schedule": value(row.get("jobschedule", "")) or None,
        "posted": value(row.get("postingdate", "")) or None,
    }


def cmd_list(a):
    host, section, lang = norm_host(a.host), norm_section(a.section), a.lang
    if a.pages is not None and a.pages < 1:
        die("--pages must be at least 1 (or use --all).")
    limit_pages = None if a.all else (a.pages or DEFAULT_PAGES)
    base = f"https://{host}/careersection/{section}/"
    code, page = request(f"{base}joblist.ftl?lang={lang}")
    if code == 404:
        die(f"{base}joblist.ftl: HTTP 404 — no such career section on this tenant.", EXIT_GONE)
    if code != 200:
        die(f"{base}joblist.ftl: HTTP {code}", EXIT_PARTIAL)
    keys = hlid(page, "listRequisition")
    hid = hidden(page)
    if not keys or "ftlpageid" not in hid:
        die(f"{base}joblist.ftl: no `listRequisition._hlid` and `ftlpageid` on the page ({len(page)} characters) — not the Taleo careersection this file reads.", EXIT_PARTIAL)
    printed = FOUND_RE.search(page)
    printed = int(re.sub(r"[^\d]", "", printed.group(1))) if printed else None
    q = [("ftlpageid", hid["ftlpageid"]), ("ftlinterfaceid", "requisitionListInterface"), ("ftlcompid", "rlPager"), ("jsfCmdId", "rlPager"),
         ("ftlcompclass", "PagerComponent"), ("ftlcallback", "ftlPager_processResponse")]
    seen, emitted, pageno, site, size = set(), 0, 0, None, None
    while True:
        pageno += 1
        data = q + [("ftlajaxid", f"ftlx{pageno}"), ("rlPager.currentPage", str(pageno)), ("ftlhistory", hid.get("ftlhistory", ""))]
        code, body = request(f"{base}joblist.ajax", data)
        if code != 200:
            die(f"{base}joblist.ajax page {pageno}: HTTP {code}" + (f" — {th(emitted)} emitted over {pageno - 1} page(s)" if emitted else ""), EXIT_PARTIAL)
        secs = ajax_sections(body)
        if len(secs) < 4:
            die(f"{base}joblist.ajax page {pageno}: not a four-section answer ({len(body)} characters).", EXIT_PARTIAL)
        fields = dict(zip(secs[3][0::2], secs[3][1::2]))
        if fields.get("listRequisition.nbElements", "").isdigit():
            site = int(fields["listRequisition.nbElements"])
        if fields.get("listRequisition.size", "").isdigit():
            size = int(fields["listRequisition.size"])
        rows = rows_of(secs[2], keys)
        new = 0
        for row in rows:
            r = record(host, section, row, lang)
            if not r["id"] or r["id"] in seen:
                continue
            seen.add(r["id"])
            print(json.dumps(r, ensure_ascii=False))
            emitted += 1
            new += 1
            if a.limit and emitted >= a.limit:
                break
        where = f"{host}/careersection/{section}"
        if a.limit and emitted >= a.limit:
            note(f"{th(emitted)} emitted over {pageno} page(s) ({where}) — walk bounded by request (--limit), not compared.")
            return
        if not rows or new == 0 or (site is not None and size and pageno * size >= site):
            break
        if limit_pages is not None and pageno >= limit_pages:
            note(f"{th(emitted)} emitted over {pageno} page(s) ({where}), portal states {th(site) if site is not None else 'no count'} — walk bounded by request (--pages {limit_pages}; --all reads to the end), not compared.")
            return
    if site is None:
        note(f"{th(emitted)} emitted over {pageno} page(s) ({where}) — the portal states no count (no `listRequisition.nbElements`), not compared.")
        return
    both = f"portal states {th(site)}" + (f", the page prints {th(printed)}" if printed is not None and printed != site else "")
    if emitted == site:
        note(f"{th(emitted)} emitted over {pageno} page(s), {both} ({where}) — equal.")
    else:
        note(f"{th(emitted)} emitted over {pageno} page(s), {both} ({where}) — {th(abs(site - emitted))} {'short' if emitted < site else 'over'}.")
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    m = AD_RE.match(a.url.strip())
    if not m:
        die(f"{a.url}: not a Taleo job URL (https://<tenant>.taleo.net/careersection/<section>/jobdetail.ftl?job=<number>).")
    host, section, ident = m.groups()
    host = norm_host(host)
    lang = (re.search(r"[?&]lang=([A-Za-z_-]+)", a.url) or [None, "en"])[1]
    code, page = request(a.url.strip())
    if code == 404:
        die(f"{a.url}: HTTP 404 — the job is gone.", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}", EXIT_PARTIAL)
    keys = hlid(page, "descRequisition")
    isl = island(page)
    if not keys or not isl or len(isl) < 3:
        die(f"{a.url}: no `descRequisition` island on the page — gone, or not the template this file reads.", EXIT_GONE)
    rows = rows_of(isl[2], keys)
    if not rows or not value(rows[0].get("contestnumber", "")):
        die(f"{a.url}: the island carries no job — gone.", EXIT_GONE)
    row = rows[0]
    parts = [value(row.get("description", "")), value(row.get("qualification", ""))]
    r = record(host, section, row, lang)
    r.update({
        "url": a.url.strip(),
        "job_field": value(row.get("jobfield", "")) or None,
        "job_level": value(row.get("joblevel", "")) or None,
        "description": redact("\n".join(p for p in parts if p)) or None,
    })
    if r["id"] != ident:
        note(f"the page carries job {r['id']} where the URL asked for {ident} — the island wins.")
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="one tenant's career section, page after page by its own ajax pager")
    l.add_argument("--host", required=True, help="the tenant, e.g. dubaiholding.taleo.net")
    l.add_argument("--section", required=True, help="the career section in the employer's URL, e.g. jum_ext_quickapply")
    l.add_argument("--lang", default="en")
    g = l.add_mutually_exclusive_group()
    g.add_argument("--pages", type=int, default=None, help=f"pages to read (default {DEFAULT_PAGES}, bounded and said so)")
    g.add_argument("--all", action="store_true", help="read to the end and compare with the count the portal states")
    l.add_argument("--limit", type=int, default=0)
    l.set_defaults(fn=cmd_list)
    d = sub.add_parser("ad", help="one job by its public URL")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
