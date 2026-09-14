#!/usr/bin/env python3
"""MyJobMag — one generalist on five fronts (`www.myjobmag.com` Nigeria, `.co.ke` Kenya, `.co.za` South Africa, `myjobmagghana.com` Ghana, `.co.uk` UK), the front named by `--host`; the listing walked newest-first and bounded by date, because the site states no count and its list is an archive going back years; every position of an advert read; the «Method of Application» text scrubbed, no contact ever emitted. Issue #391.

  myjobmag.py list [--host ng|ke|za|gh|uk] [--days 30] [--pages N] [--limit N]
  myjobmag.py ad --url <https://<front>/job/<slug> | /jobs/<slug>>

THE FRONTS. One template, one operator, five hosts; the rules on each (320–403 B) refuse
**every URL with a query string (`/*?`)**, the search, the account pages and `/apply-now/` —
and nothing of `/jobs`, `/jobs/page/N`, `/job/<slug>`, `/jobs/<slug>`. So the adapter never
sends a `?`: the pager is the path `/jobs/page/N`, and no filter is sent (the site's filters are
query strings). No Crawl-delay; 2 s is ours.

THE LIST STATES NO COUNT AND IS AN ARCHIVE. `/jobs` («Jobs in Nigeria») prints 35 dated cards a
page and a pager without an end — page 1 000 on the day answered 200 with cards of 12 February;
the title says «1000+ Jobs Posted Daily» and nothing counts. The two job sitemaps stop at
exactly 45 000 and 45 001 rows — a cap, not a count. **So the walk is bounded by DATE**: cards
are newest-first, each dated («12 September», «10 June, 2024» when not this year), and the
adapter stops at the first card older than `--days` (30 unless told) or at the pager's end, and
says so — «walked by date, not a shortfall». A page that answers 200 without one card is a
changed template (exit 6), never an empty market.

TWO KINDS OF CARD. A card links to `/job/<slug>` — one position — or to `/jobs/<slug>` — an
ADVERT holding several positions («Medical Consultants at Bergstein Hospital»: four). The
listing record carries `kind`; `ad --url` reads either page and emits ONE RECORD PER POSITION:
each `<h2 id="jobNNNNNNN">` block with its `job-key-info` labels (Job Type, Qualification,
Experience, Location, City, Job Field, Salary Range — «₦150,000 - ₦200,000/month», a period
printed, so `salary_unit_stated` is true) and its `job-details` text; the page's «Posted:» and
«Deadline:», the employer (`/jobs-at/<slug>`), and — on a single-position page — the JSON-LD
JobPosting, whose `description` carries raw newlines (parsed with `strict=False`; a JobPosting
`json.loads` rejects is not «none»). **The «Method of Application» block is where an employer
writes an address to send a CV to: scrubbed of e-mail addresses and telephone numbers, like the
description; the site's «Apply Now» form is never touched; `contacts_withheld` on every record.**

Measured 2026-09-14 01:3x UTC by the declared client, the guard on the exact path:
Nigeria 35 cards a page dated 12 September on page 1; Kenya 25 (13 September); South Africa 18
(13 September); UK 20 (16 May — stale); **Ghana 18, the first dated 18 February and the rest
May–June 2024 — a dormant front, served and said**.
"""

import argparse
import datetime
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

BOARDS = {"ng": "www.myjobmag.com", "ke": "www.myjobmag.co.ke", "za": "www.myjobmag.co.za",
          "gh": "www.myjobmagghana.com", "uk": "www.myjobmag.co.uk"}
COUNTRY = {"ng": "NG", "ke": "KE", "za": "ZA", "gh": "GH", "uk": "GB"}
DEFAULT = "ng"

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# Nigerian 0803 123 4567 / +234 803 123 4567, Kenyan 07xx xxx xxx / +254, South African 0xx xxx xxxx / +27, Ghanaian 0xx xxx xxxx / +233, UK 07xxx xxxxxx / +44
PHONE_RE = re.compile(r"(?<![\d+])(?:\+\d{1,3}[\s -]?)?\(?0?\d{2,4}\)?[\s -]?\d{3,4}[\s -]?\d{3,4}(?:[\s -]?\d{1,3})?(?!\d)")
CARD_RE = re.compile(r'<li class="job-list-li">(.*?)<li id="job-date">([^<]*)</li>', re.S)
TITLE_RE = re.compile(r'<h2><a[^>]*href="(/jobs?/[^"]+)"[^>]*>(.*?)</a></h2>', re.S)
EMPLOYER_RE = re.compile(r'href="/jobs-at/([^"]+)"[^>]*>\s*<img[^>]*\balt="([^"]*)"')
DESC_RE = re.compile(r'<li class="job-desc">(.*?)</li>', re.S)
NEXT_RE = re.compile(r"""href=['"]/jobs/page/(\d+)['"]""")
BLOCK_RE = re.compile(r'<h2[^>]*\bid="job(\d+)"[^>]*>(.*?)</h2>(.*?)(?=<h2[^>]*\bid="job\d+"|<h2[^>]*\bid="application-method"|$)', re.S)
KEY_RE = re.compile(r'<span class="jkey-title">(.*?)</span>\s*<span class="jkey-info">(.*?)</span>', re.S)
DETAILS_RE = re.compile(r'<div class="job-details">(.*?)</div>\s*(?:<p|<h2|<div|$)', re.S)
POSTED_RE = re.compile(r'<b[^>]*>Posted:</b>\s*([^<]+)<')
DEADLINE_RE = re.compile(r'<b[^>]*>Deadline:</b>\s*([^<]+)<')
METHOD_RE = re.compile(r'<h2[^>]*\bid="application-method"[^>]*>.*?</h2>\s*<div[^>]*>(.*?)</div>', re.S)
SALARY_RE = re.compile(r"([^\d\s]{1,4})\s?([\d,]+)(?:\s*-\s*[^\d\s]{0,4}\s?([\d,]+))?\s*(?:/\s*(\w+))?")
MONTHS = {m: i for i, m in enumerate(("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"), 1)}
MONTHS.update({k[:3]: v for k, v in MONTHS.items()})


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[myjobmag] {msg}", file=sys.stderr)


def board_of(host):
    """`--host ng` or a hostname → (key, host); an unknown one is refused before any request."""
    if host is None:
        return DEFAULT, BOARDS[DEFAULT]
    h = host.strip().lower()
    if h in BOARDS:
        return h, BOARDS[h]
    for k, v in BOARDS.items():
        if h == v or h == v.replace("www.", ""):
            return k, v
    die(f"--host {host!r}: not a front of this board — {', '.join(f'{k} ({v})' for k, v in BOARDS.items())}")


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
        _PACES[host] = Pace(host, own=2.0)   # no Crawl-delay written on any front; 2 s is ours
    return _PACES[host]


def request(url):
    if "?" in url:
        die(f"{url}: every front refuses a query string in writing (`Disallow: /*?`) — not sent", EXIT_REFUSED)
    gate(url)
    pace_for(urllib.parse.urlsplit(url).netloc).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
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
    out = re.sub(r"[ \t ​]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def card_date(s, today=None):
    """«12 September» is this year; «10 June, 2024» carries its year — ISO, or None."""
    today = today or datetime.date.today()
    m = re.match(r"\s*(\d{1,2})\s+([A-Za-z]+)(?:,?\s*(\d{4}))?\s*$", s or "")
    if not m or m.group(2) not in MONTHS:
        return None
    y = int(m.group(3)) if m.group(3) else today.year
    try:
        d = datetime.date(y, MONTHS[m.group(2)], int(m.group(1)))
    except ValueError:
        return None
    if not m.group(3) and d > today + datetime.timedelta(days=1):
        d = d.replace(year=y - 1)    # «30 December» read on 2 January
    return d.isoformat()


def page_date(s):
    """«Sep 12, 2026» on the ad → ISO, or the text as printed («Not specified»)."""
    m = re.match(r"\s*([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})\s*$", s or "")
    if m and m.group(1)[:3] in MONTHS:
        return datetime.date(int(m.group(3)), MONTHS[m.group(1)[:3]], int(m.group(2))).isoformat()
    return (s or "").strip() or None


def cards(body, key, host, today=None):
    out = []
    for block, date in CARD_RE.findall(body):
        t = TITLE_RE.search(block)
        if not t:
            continue
        path, title = t.group(1), text(t.group(2))
        emp = EMPLOYER_RE.search(block)
        desc = DESC_RE.search(block)
        kind = "advert" if path.startswith("/jobs/") else "position"
        slug = path.rsplit("/", 1)[1]
        employer = htmlmod.unescape(emp.group(2)).strip() if emp else None
        if not employer and " at " in title:
            employer = title.rsplit(" at ", 1)[1].strip() or None   # an employer without a `/jobs-at/` page is named by the card's title only
        out.append({
            "source": f"myjobmag-{key}", "country": COUNTRY[key], "ledger_id": f"myjobmag-{key}:{kind}:{slug}", "id": slug,
            "kind": kind,   # a position, or an advert that holds several — `ad` reads either and emits one record per position
            "url": f"https://{host}{path}",
            "title": title, "employer": employer, "employer_slug": emp.group(1) if emp else None,
            "posted": card_date(date, today), "posted_text": date.strip(),
            "summary": scrub(text(desc.group(1))) if desc else None,
            "contacts_withheld": True, "language": "en",
        })
    return out


def cmd_list(a):
    key, host = board_of(getattr(a, "host", None))
    days = a.days if a.days is not None else 30
    today = datetime.date.today()
    floor = (today - datetime.timedelta(days=days)).isoformat()
    rows, seen, pageno, stopped = [], set(), 0, None
    while True:
        pageno += 1
        url = f"https://{host}/jobs" + (f"/page/{pageno}" if pageno > 1 else "")
        code, body = request(url)
        if code != 200:
            die(f"{url}: HTTP {code}" + (" — the list has moved" if code == 404 else ""), EXIT_GONE if code == 404 and pageno == 1 else EXIT_PARTIAL)
        page = cards(body, key, host, today)
        if not page:
            die(f"{url}: 200 and not one card — the template changed; not an empty market", EXIT_PARTIAL)
        for r in page:
            if r["posted"] and r["posted"] < floor:
                stopped = r["posted"]
                break
            if r["ledger_id"] in seen:
                continue
            seen.add(r["ledger_id"])
            rows.append(r)
        if stopped:
            break
        nxt = {int(n) for n in NEXT_RE.findall(body)}
        if pageno + 1 not in nxt:
            stopped = "end"
            break
        if a.pages and pageno >= a.pages:
            break
        if a.limit and len(rows) >= a.limit:
            break
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    where = f"{host} ({COUNTRY[key]})"
    if stopped == "end":
        note(f"{th(n)} card(s) emitted over {pageno} page(s) on {where} — the pager ended; the site states no count.")
    elif stopped:
        note(f"{th(n)} card(s) emitted over {pageno} page(s) on {where}, newest-first, stopped at the first card dated {stopped} — older than --days {days}; the site states no count and its list is an archive: walked by date, not a shortfall.")
    else:
        note(f"{th(n)} card(s) emitted over {pageno} page(s) on {where} — bounded by --pages/--limit, not a shortfall; the site states no count.")
    adverts = sum(1 for r in emitted if r["kind"] == "advert")
    note(f"{th(adverts)} of them are adverts holding several positions — `ad --url` reads each and emits one record per position; no contact is emitted on any route.")


def key_info(block):
    out = {}
    for k, v in KEY_RE.findall(block):
        out[text(k).lower().replace(" ", "_")] = text(v) or None
    return out


def salary(s):
    """«₦150,000 - ₦200,000/month» → (150000, 200000, '₦', 'month'); the period is the site's own print."""
    m = SALARY_RE.search(s or "")
    if not m:
        return None, None, None, None
    lo = int(m.group(2).replace(",", ""))
    hi = int(m.group(3).replace(",", "")) if m.group(3) else lo
    return lo, hi, m.group(1), (m.group(4) or "").lower() or None


def ldjson(body):
    """The single-position page's JobPosting — its `description` carries raw newlines, so `strict=False`; none on an advert page."""
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S):
        try:
            d = json.loads(m, strict=False)
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("@type") == "JobPosting":
            return d
    return None


def positions(body, url, key, host):
    """One record per `<h2 id="jobN">` block — one on a position page, several on an advert."""
    posted = POSTED_RE.search(body)
    deadline = DEADLINE_RE.search(body)
    emp = re.search(r'href="/jobs-at/([^"]+)"[^>]*>\s*View Jobs at ([^<]+)<', body)
    method = METHOD_RE.search(body)
    ld = ldjson(body)
    addr = ((ld or {}).get("jobLocation") or {}).get("address") or {} if ld else {}
    out = []
    for pid, head, block in BLOCK_RE.findall(body):
        link = re.search(r"""href=['"](/job/[^'"]+)['"]""", head)
        info = key_info(block)
        det = DETAILS_RE.search(block)
        smin, smax, cur, unit = salary(info.get("salary_range"))
        out.append({
            "source": f"myjobmag-{key}", "country": COUNTRY[key], "ledger_id": f"myjobmag-{key}:position:{pid}", "id": pid,
            "url": f"https://{host}{link.group(1)}" if link else url, "advert_url": url if "/jobs/" in url else None,
            "title": text(head), "employer": htmlmod.unescape(emp.group(2)).strip() if emp else ((ld or {}).get("hiringOrganization") or {}).get("name"),
            "employer_slug": emp.group(1) if emp else None,
            "job_type": info.get("job_type"), "qualification": info.get("qualification"), "experience": info.get("experience"),
            "location": info.get("location"), "city": info.get("city"), "job_field": info.get("job_field"),
            "salary_text": info.get("salary_range"), "salary_min": smin, "salary_max": smax, "salary_currency_sign": cur,
            "salary_unit": unit, "salary_unit_stated": bool(unit),
            "posted": page_date(posted.group(1)) if posted else ((ld or {}).get("datePosted") or "")[:10] or None,
            "deadline": page_date(deadline.group(1)) if deadline else None,
            "valid_through": ((ld or {}).get("validThrough") or "")[:10] or None,
            "employment_type": (ld or {}).get("employmentType"), "industry": (ld or {}).get("industry"),
            "region": addr.get("addressRegion"), "address_country": addr.get("addressCountry"),
            "description": scrub(text(det.group(1))) if det else None,
            "application_method": scrub(text(method.group(1))) if method else None,   # where an employer writes an address to send a CV to — scrubbed
            "contacts_withheld": True, "language": "en",
        })
    return out


def cmd_ad(a):
    parts = urllib.parse.urlsplit(a.url)
    key = next((k for k, v in BOARDS.items() if parts.netloc == v), None)
    if not key or not re.match(r"^/jobs?/[^/]+/?$", parts.path):
        die(f"{a.url}: not a position (/job/<slug>) or an advert (/jobs/<slug>) on one of the five fronts")
    host = BOARDS[key]
    url = f"https://{host}{parts.path.rstrip('/')}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    rows = positions(body, url, key, host)
    if not rows:
        die(f"{url}: 200 and no position block (`<h2 id=\"jobN\">`) — the template changed", EXIT_PARTIAL)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    note(f"{len(rows)} position(s) on {url}; the «Method of Application» text and the description are scrubbed; no contact is emitted.")


def main():
    p = argparse.ArgumentParser(description="MyJobMag — five fronts by --host; the archive-list walked newest-first and bounded by date; one record per position of an advert; the application text scrubbed, no contact emitted. Issue #391.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help="the newest cards, 35 a page on Nigeria, stopped at the first older than --days")
    l_.add_argument("--host", help="ng (default) · ke · za · gh · uk — or the hostname")
    l_.add_argument("--days", type=int, help="stop at the first card older than this many days (30)")
    l_.add_argument("--pages", type=int)
    l_.add_argument("--limit", type=int)
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad", help="a position or an advert page — one record per position")
    ad.add_argument("--url", required=True)
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
