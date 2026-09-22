#!/usr/bin/env python3
"""Government of Antigua and Barbuda — «Current Vacancies» (`ab.gov.ag`): the State's own posts, each a line naming the department, the title, the deadline, and the PDF that IS the advertisement. Issue #728.

  abgovag.py jobs [--open-on 2026-09-22] [--country-code AG]      the page (1 request)

WHAT IT IS. The Government's portal. Its vacancies page carries the posts the ministries and
statutory bodies advertise — the Meteorological Service, the Treasury Department. *The One Stop
Employment Centre of the Labour Department has no site: its notices go through Facebook and through
Dadli Jobs (#730), which is a different card.* **This host is not `mpsl.gov.ag`** — the Ministry of
Public Safety and Labour, whose TLS chain is incomplete (#750, `blocked`). Two hosts, two tickets.

THE RULES. `ab.gov.ag` answers **404** to `/robots.txt` — a knowledge, not an ignorance: the host
looked and there is no file, so there is no rule to obey (open, `certain: True`), no Crawl-delay;
2 s is ours. The guard is taken on the exact path.

THE LIST. `/detail_template.php?page=media/vacancies` (200; 13 689 B) puts each post in its own
`ul.events_list`:

```
<h2>Current Vacancies</h2>
<ul class="events_list"><li><date>Deadline - October 03rd 2026</date> - <span>
  <a href="media/pdf/vacancies/AD_2026_Meteorological_Officer_III.pdf">
    <strong>Antigua and Barbuda Meteorological Service (ABMS)</strong> - Meteorological Officer III
  </a><span></li></ul>
```

**The `<span>` is never closed and `<date>` is not an element anyone else uses** — the markup is the
department's, and the reading follows it rather than a tidy version of it. The employer is the
`<strong>`, the title is what follows the dash **inside the same link**, and the deadline is the
`<date>`: «October 03rd 2026» carries an ordinal suffix that no date library parses by default.

**Nothing states a count.** The run prints the posts read, how many are already closed, and how many
the filter dropped — never a total it did not read.

**The page keeps closed posts**, and that is the department's filing: on 2026-09-22 the page lists
three, **one open** (2026-10-03) and two whose deadline passed (2026-07-06, 2026-03-31). *The
reading of 2026-09-18 found two, both closed, and this issue was opened on that — «rien d'ouvert le
18.09». A month with nothing open is not a page that publishes nothing.* They are emitted with
their date and counted, never dropped in silence.

**The advertisement is the PDF**: it is NAMED, never downloaded. **WITHHELD:** e-mail addresses and
telephone numbers in a title or a department name; `contacts_withheld` on every record.
`--country-code` STAMPS and the run says so.

Measured 2026-09-22 08:5x UTC by the declared client, the guard on the exact path:
200, 13 689 B, md5 bc57c674409f — **3 posts, 1 open**, three PDFs under `media/pdf/vacancies/`.
"""

import argparse
import html as htmlmod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _decode import decode_body
from _pace import Pace
from _robots import allowed as robots_allowed, full_path, wire_url
from _ua import UA

HOST = "ab.gov.ag"
PAGE = f"https://{HOST}/detail_template.php?page=media/vacancies"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\(?\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
DATE_RE = re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")
STRIP_RE = re.compile(r"(?s)<style.*?</style>|<script.*?</script>")
HEAD_RE = re.compile(r"<h2[^>]*>\s*Current\s+Vacancies\s*</h2>", re.I)
ITEM_RE = re.compile(r'<ul class="events_list">(.*?)</ul>', re.S | re.I)
END_RE = re.compile(r"<!--\s*Events content end|class=\"footerContainer\"", re.I)
DATE_TAG_RE = re.compile(r"<date[^>]*>(.*?)</date>", re.S | re.I)
LINK_RE = re.compile(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
STRONG_RE = re.compile(r"<strong[^>]*>(.*?)</strong>", re.S)
DEADLINE_RE = re.compile(r"Deadline\s*-?\s*([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?\s+(\d{4})", re.I)
MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[abgovag] {msg}", file=sys.stderr)


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
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # no rules file at all; 2 s is ours
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
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
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return " ".join(t.split()) or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub(lambda m: m.group(0) if DATE_RE.search(m.group(0)) else "[telephone withheld]", s).strip() or None


def when(s):
    """«Deadline - October 03rd 2026» → `2026-10-03`; the ordinal suffix is the department's own."""
    m = DEADLINE_RE.search(s or "")
    if not m or not MONTHS.get(m.group(1).lower()):
        return None
    return f"{m.group(3)}-{MONTHS[m.group(1).lower()]:02d}-{int(m.group(2)):02d}"


def slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (s or "").lower())).strip("-")


def entries_of(markup):
    """The page → [(employer, title, document, deadline)], read BELOW the «Current Vacancies» heading.

    Each post is its own `ul.events_list`; the employer is the `<strong>` INSIDE the link and the
    title is what follows the dash in the same link. The `<span>` around it is never closed, so the
    reading takes the link, not the span.
    """
    body = STRIP_RE.sub("", markup or "")
    head = HEAD_RE.search(body)
    if not head:
        return None
    # the scan is BOUNDED: the department closes its list with «Events content end», and the
    # footer of the same page carries a `ul.events_list` of its own (a policy PDF, deadline 2020).
    # Read to the end of the document and the footer's line becomes a vacancy.
    seg = body[head.end():]
    stop = END_RE.search(seg)
    if stop:
        seg = seg[:stop.start()]
    out = []
    for block in ITEM_RE.findall(seg):
        link = LINK_RE.search(block)
        if not link:
            continue
        inner = link.group(2)
        strong = STRONG_RE.search(inner)
        employer = text(strong.group(1)) if strong else None
        rest = text(STRONG_RE.sub("", inner))
        title = re.sub(r"^\s*[-–—]\s*", "", rest or "") or None
        d = DATE_TAG_RE.search(block)
        out.append((employer, title, htmlmod.unescape(link.group(1)), when(text(d.group(1)) if d else block)))
    return out


def record(employer, title, doc, deadline, stamp):
    doc_url = urllib.parse.urljoin(PAGE, doc) if doc else None
    name = urllib.parse.unquote((urllib.parse.urlsplit(doc_url or "").path or "").rsplit("/", 1)[-1])
    key = slug(name) or slug(f"{employer}-{title}")
    return {
        "source": "abgovag", "country": stamp,
        "ledger_id": f"abgovag:{key}", "id": key,
        "title": scrub(title), "employer": scrub(employer),
        "deadline": deadline,
        "document_url": doc_url, "document_downloaded": False,
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    on = (a.open_on or "").strip()
    if on and not re.match(r"^\d{4}-\d{2}-\d{2}$", on):
        die(f"--open-on {a.open_on}: a date, YYYY-MM-DD")
    stamp = a.country_code.upper() if a.country_code else None
    code, body = request(PAGE)
    if code == 404:
        die(f"{PAGE}: HTTP 404 — the page is gone", EXIT_GONE)
    if code != 200:
        die(f"{PAGE}: HTTP {code}", EXIT_PARTIAL)
    found = entries_of(body)
    if found is None:
        die(f"{PAGE}: 200 without its «Current Vacancies» heading — the page changed; not an empty list", EXIT_PARTIAL)
    rows, seen, dropped, undated = [], set(), 0, 0
    for employer, title, doc, deadline in found:
        r = record(employer, title, doc, deadline, stamp)
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        if not r["deadline"]:
            undated += 1
        if on and r["deadline"] and r["deadline"] < on:
            dropped += 1
            continue
        rows.append(r)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    today = time.strftime("%Y-%m-%d", time.gmtime())
    closed = sum(1 for r in rows if r["deadline"] and r["deadline"] < today)
    note(f"{th(len(rows))} post(s) emitted ({th(len(seen))} read); **the page states no count** — what it lists is the board.")
    if dropped:
        note(f"{th(dropped)} post(s) whose deadline is before {on} not emitted — OUR filter, on the date the page states.")
    if undated:
        note(f"{th(undated)} post(s) state no deadline; they are emitted with `deadline: null` rather than dropped.")
    note(f"{th(closed)} of the emitted post(s) state a deadline already past on {today} (UTC) — the department's own filing, never dropped in silence.")
    note("the advertisement is the PDF the department publishes: NAMED, never downloaded.")
    if stamp:
        note(f"country {stamp} is the user's stamp — the page states no country.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Government of Antigua and Barbuda — «Current Vacancies», read from the markup the department writes. Issue #728.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the page (1 request)")
    j.add_argument("--open-on", dest="open_on", metavar="YYYY-MM-DD", help="keep only the posts whose stated deadline is on or after this day (OUR filter)")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (the page states none)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
