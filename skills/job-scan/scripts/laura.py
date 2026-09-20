#!/usr/bin/env python3
"""LAURA Rekrytointi (`<tenant>.rekrytointi.com`, a Finnish ATS — one tenant at a time): the tenant's open-jobs list `/paikat/index.php?o=A_LOJ&list=1` is a server-rendered table with its count in the page («Avoimia työpaikkoja: 20» / «Open jobs: 16»); the job page `/paikat/index.php?o=A_RJ&jid=<id>` carries the advert. Issue #466.

  laura.py jobs --tenant <name> [--list N] [--lang fi|en|se] [--country-code ISO2]
  laura.py ad --url https://<tenant>.rekrytointi.com/paikat/index.php?o=A_RJ&jid=<id>

THE TENANT is the subdomain of `rekrytointi.com` the employer's careers site
lives on (`tuni`, `finnlines`, `fca`), found by the family's signature
`rekrytointi.com/paikat/index.php?o=A_LOJ` — never composed: **a subdomain
that is no tenant answers 200 with the vendor's marketing site**
(`pingviini.rekrytointi.com`, 76 260 B of laura.fi, measured 2026-09-20),
so the adapter checks the answer for the list's own markup and dies with 6
otherwise. Rules (read 2026-09-20 on three tenants): `*` refused `/list/`
only — not the list, which is under `/paikat/`; `ClaudeBot` is refused by
name and `Claude-User` is not (the decision of 2026-09-07: two tokens, the
`*` group applies); no Crawl-delay for `*`. 2 s between requests are ours.

THE LIST: `<div class='result_count'>Avoimia työpaikkoja: N</div>`, then
`<table id='auto_list_table_open_jobs'>` whose columns the tenant chooses
(`col_Name`, `col_ApplyEndDate`, `col_Department`, …), one `<tr
class='odd'|'even'>` per job, every cell a link to
`/paikat/index.php?jid=<id>&…&o=A_RJ&rspvt=<session>`. **`rspvt` is a
session token** (the tenants' own rules mark it `Clean-param`): never
emitted, never replayed — the job's address is `?o=A_RJ&jid=<id>`, as the
page's own «direct link» spells it. No pager was seen (20 of 20, 16 of 16);
a list shorter than its count is reported short, not walked blind.

THE JOB PAGE: `<h1>` title, `<div class='job_description'>` (HTML),
`job_start_end_times` (application period start and end), the employer's
name from its logo, the language switch (`lang=`). No JobPosting.

WITHHELD: the description scrubbed of e-mail addresses and telephone
numbers (the «Lisätietoja» paragraph names the contact — the address is
scrubbed, the paragraph stays as the tenant wrote it); the application
(`o=A_A`, an account) never touched; `contacts_withheld` on every record.
The list states no country; the family is Finnish and `--country-code`
stamps the rows with what the user names, saying so.
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

BOARD = "laura"
DOMAIN = "rekrytointi.com"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

TENANT_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", re.I)
COUNT_RE = re.compile(r"<div class='result_count'>\s*([^<:]*):\s*([\d\s]+)\s*</div>")
TABLE_RE = re.compile(r"<table class='results[^']*' id='auto_list_table_open_jobs'[^>]*>(.*?)</table>", re.S)
ROW_RE = re.compile(r"<tr class='(?:odd|even)'>(.*?)</tr>", re.S)
CELL_RE = re.compile(r"<td class='col_([A-Za-z0-9_]+)'>(.*?)</td>", re.S)
HEAD_RE = re.compile(r"<th class='col_([A-Za-z0-9_]+)'>(.*?)(?:<a class='sort_icon'|</th>)", re.S)
JID_RE = re.compile(r"jid=(\d+)")
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
DESC_RE = re.compile(r"<div class='job_description'[^>]*>(.*?)</div>\s*<div class='job_start_end_times'>", re.S)
DESC_LOOSE_RE = re.compile(r"<div class='job_description'[^>]*>(.*)", re.S)
PERIOD_RE = re.compile(r"<span class='se_text'>([^<]*)</span><span class='se_date'>([^<]*)</span>")
LOGO_RE = re.compile(r"<div class=\"applicant_logo\">.*?<img[^>]*\balt=\"([^\"]*)\"", re.S)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
_PACES = {}
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[laura] {msg}", file=sys.stderr)


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
        die(f"{url}: not this run's LAURA tenant ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "fi,en"})
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
    """`tuni`, `tuni.rekrytointi.com` or the list's URL → the host."""
    s = (arg or "").strip().lower()
    if "://" in s or "/" in s:
        s = urllib.parse.urlsplit(s if "://" in s else "https://" + s).netloc
    if s.endswith("." + DOMAIN):
        s = s[: -len("." + DOMAIN)]
    if not s or "." in s or not TENANT_RE.match(s) or s in ("www", "osaajapankki"):
        die(f"{arg!r}: a tenant is the subdomain of {DOMAIN} the employer's careers site lives on (tuni, finnlines), found by the family's signature, never composed")
    return f"{s}.{DOMAIN}"


def job_url(host, jid, lang=None):
    return f"https://{host}/paikat/index.php?o=A_RJ&jid={jid}" + (f"&lang={lang}" if lang else "")


def parse_list(body):
    """(stated count or None, [(jid, {column: text})]) — the vendor's site, served to a non-tenant, has neither."""
    cm = COUNT_RE.search(body)
    tm = TABLE_RE.search(body)
    if not cm and not tm:
        return None, None
    total = int(re.sub(r"\s", "", cm.group(2))) if cm else None
    heads = {k: text(v) for k, v in HEAD_RE.findall(tm.group(1))} if tm else {}
    rows = []
    for tr in (ROW_RE.findall(tm.group(1)) if tm else []):
        cells = {k: text(v) for k, v in CELL_RE.findall(tr)}
        jm = JID_RE.search(tr)
        if jm:
            rows.append((jm.group(1), cells, heads))
    return total, rows


def row(host, jid, cells, heads, lang, country):
    labelled = {(heads.get(k) or k): v for k, v in cells.items() if v and k != "Name"}
    return {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{jid}", "id": jid, "url": job_url(host, jid, lang),
        "title": cells.get("Name"), "country": country,
        "place": cells.get("Location") or cells.get("City") or cells.get("Municipality"),
        "department": cells.get("Department"), "closes": cells.get("ApplyEndDate"),
        "fields": labelled,                     # the tenant's own column labels
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    TENANT["host"] = host
    url = f"https://{host}/paikat/index.php?o=A_LOJ&list={a.list}" + (f"&lang={a.lang}" if a.lang else "")
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    total, rows = parse_list(body)
    if rows is None:
        die(f"{url}: no open-jobs list in the page (no `result_count`, no `auto_list_table_open_jobs`) — a subdomain that is no tenant answers 200 with the vendor's own site; {host} is not a LAURA tenant, or its list is another `--list`.", EXIT_PARTIAL)
    country = (a.country_code or "").strip().upper() or None
    seen, out = set(), []
    for jid, cells, heads in rows:
        if jid in seen:
            continue
        seen.add(jid)
        out.append(row(host, jid, cells, heads, a.lang, country))
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    stamp = f"; country {country} stamped from --country-code (the list states none)" if country else ""
    if total is None:
        note(f"{th(n)} emitted — the page states no count{stamp}.")
    elif n == total:
        note(f"{th(n)} emitted — the page states {th(total)}: equal{stamp}.")
    else:
        note(f"{th(n)} emitted — the page states {th(total)}: {th(abs(total - n))} " + ("short (the list shows fewer rows than it counts — a page the adapter does not walk)" if total > n else "more emitted than stated") + f"{stamp}.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    q = urllib.parse.parse_qs(parts.query)
    jid = (q.get("jid") or [""])[0]
    host = parts.netloc.lower()
    if not host.endswith("." + DOMAIN) or parts.path != "/paikat/index.php" or not jid.isdigit():
        die(f"{a.url!r}: not a LAURA job address (https://<tenant>.{DOMAIN}/paikat/index.php?o=A_RJ&jid=<id>)")
    TENANT["host"] = host
    lang = (q.get("lang") or [None])[0]
    url = job_url(host, jid, lang)
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped.", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    h1 = H1_RE.search(body)
    dm = DESC_RE.search(body) or DESC_LOOSE_RE.search(body)
    if not h1 or not dm:
        die(f"{url}: no title or no `job_description` in the page — not a LAURA job page, or the job is gone (the vendor's site answers 200 to a non-tenant).", EXIT_PARTIAL)
    period = {k.strip().rstrip(":").lower(): v.strip() for k, v in PERIOD_RE.findall(body)}
    starts = next((v for k, v in period.items() if "start" in k or "alkaa" in k), None)
    ends = next((v for k, v in period.items() if "end" in k or "päättyy" in k), None)
    logo = LOGO_RE.search(body)
    r = {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{jid}", "id": jid, "url": job_url(host, jid, lang),
        "title": text(h1.group(1)), "company": htmlmod.unescape(logo.group(1)) if logo and logo.group(1) else None,
        "posted": starts, "closes": ends, "language": lang,
        "description": (scrub(text(dm.group(1))) or "")[:20000] or None,
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="LAURA Rekrytointi — one tenant's open-jobs list (server-rendered, its count in the page) and job pages; the session token never emitted; no contact. Issue #466.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the tenant's open-jobs list, one request; the count beside the emitted number")
    s.add_argument("--tenant", required=True, help="the subdomain (tuni), the host, or the list's URL")
    s.add_argument("--list", type=int, default=1, help="the tenant's list id (list=1 is the usual; some tenants have more)")
    s.add_argument("--lang", help="fi, en or se — the page's own language switch")
    s.add_argument("--country-code", help="ISO2 to stamp the rows with — the list states no country")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one job by its page (?o=A_RJ&jid=); description scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
