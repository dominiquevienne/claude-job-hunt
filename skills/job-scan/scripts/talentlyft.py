#!/usr/bin/env python3
"""TalentLyft (a Croatian ATS — one tenant at a time): the employer's careers site on `<tenant>.talentlyft.com` writes a rules file WITHOUT a group that refuses `/JobList` and `/JobsSimple` (the call the page's list makes) and asks `Crawl-delay: 150`; the permitted way is the sitemap it declares — `/sitemap.xml` naming every `/jobs/<slug>` page — and the job pages, each with a JobPosting. Issue #474.

  talentlyft.py jobs --tenant <name> [--country-code ISO2] [--max-pages N]
  talentlyft.py ad --url https://<tenant>.talentlyft.com/jobs/<slug>

THE TENANT is the subdomain of `talentlyft.com` the employer's careers site
lives on (`secret-level`, `flyer-one-ventures`, `taleolithic`), found by the
family's signature, never composed.

THE RULES, AS WRITTEN (2026-09-20, the same 202 B on two tenants):
`Crawl-delay: 150`, `Disallow: /JobList`, `/ArticleList`, `/joblist`,
`/articlelist`, `/JobsSimple`, `/js`, `Sitemap: /sitemap.xml` — and no
`User-agent:` line at all. The guard reads a file without a group as
addressed to nobody: a `Disallow` in it is INDETERMINATE on its path
(`_robots`: «declares no group at all»), and an indeterminate is not
probed. So the page's own list call (`/JobList`, which fills
`#jobs-list-<id>` after load) is never requested; **the sitemap the file
declares is the list**, and every `/jobs/<slug>` it names is read. **The
Crawl-delay is honoured as written — 150 s between requests — although
it is addressed to no group**: a run reads the sitemap, then one page per
job, and says how long the walk takes; `--max-pages` bounds it.

THE JOB PAGE carries a schema.org JobPosting (title, datePosted,
employmentType, hiringOrganization, jobLocation with streetAddress —
«Los Angeles, CA, United States of America (Remote)» —, addressLocality,
addressRegion, postalCode, addressCountry, description as escaped HTML).

WITHHELD: the postal code and the street line of the address (the
locality, region and country kept); e-mail addresses and telephone
numbers in the description; `contacts_withheld` on every record.
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

BOARD = "talentlyft"
DOMAIN = "talentlyft.com"
WRITTEN_DELAY = 150.0                      # the file's own Crawl-delay, addressed to no group, honoured as written
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

TENANT_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", re.I)
LOC_RE = re.compile(r"<loc>\s*(.*?)\s*</loc>", re.S)
LASTMOD_RE = re.compile(r"<url>\s*<loc>\s*(.*?)\s*</loc>(?:\s*<lastmod>\s*(.*?)\s*</lastmod>)?", re.S)
JOB_PATH_RE = re.compile(r"^/jobs/([A-Za-z0-9][A-Za-z0-9_\-]*)/?$")
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{6,}\d(?!\w)")
_PACES = {}
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[talentlyft] {msg}", file=sys.stderr)


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
        die(f"{url}: not this run's TalentLyft tenant ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=WRITTEN_DELAY)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml", "Accept-Language": "en"})
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
    t = htmlmod.unescape(markup or "")                       # the JobPosting's description is escaped HTML
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
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
    if not s or "." in s or not TENANT_RE.match(s) or s in ("www", "help", "careers", "app"):
        die(f"{arg!r}: a tenant is the subdomain of {DOMAIN} the employer's careers site lives on (secret-level), found by the family's signature, never composed")
    return f"{s}.{DOMAIN}"


def sitemap_jobs(host, body):
    """The job pages the sitemap names, in its order — the root and anything not under /jobs/ left out."""
    out = []
    for loc, lastmod in LASTMOD_RE.findall(body or ""):
        p = urllib.parse.urlsplit(loc.strip())
        m = JOB_PATH_RE.match(p.path)
        if p.netloc.lower() == host and m:
            out.append((m.group(1), f"https://{host}/jobs/{m.group(1)}", lastmod or None))
    return out


def posting_row(p, host, slug, url, lastmod, stamp):
    org = p.get("hiringOrganization") if isinstance(p.get("hiringOrganization"), dict) else {}
    loc = p.get("jobLocation") if isinstance(p.get("jobLocation"), dict) else {}
    addr = loc.get("address") if isinstance(loc.get("address"), dict) else {}
    cc = addr.get("addressCountry")
    country = (cc.strip().upper() if isinstance(cc, str) and len(cc.strip()) == 2 else None) or stamp
    street = addr.get("streetAddress") or ""
    return {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{slug}", "id": slug, "url": url,
        "title": p.get("title"), "company": org.get("name"),
        "place": addr.get("addressLocality") or None, "region": addr.get("addressRegion") or None, "country": country,
        "remote": True if "remote" in street.lower() else None,       # the street line is where the tenant writes «(Remote)»; the line itself is not emitted
        "employment_type": p.get("employmentType"), "posted": p.get("datePosted"), "closes": p.get("validThrough"), "updated": lastmod,
        "description": (scrub(text(p.get("description"))) or "")[:20000] or None,
        # streetAddress and postalCode are not emitted
        "contacts_withheld": True,
    }


def read_job(host, slug, url, lastmod, stamp):
    st, body = request(url)
    if st == 404:
        return None, "gone"
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        return None, f"HTTP {st}"
    ps = ld_postings(body)
    if not ps:
        return None, "no JobPosting"
    return posting_row(ps[0], host, slug, url, lastmod, stamp), None


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    TENANT["host"] = host
    stamp = (a.country_code or "").strip().upper() or None
    url = f"https://{host}/sitemap.xml"
    st, body = request(url)
    if st == 404:
        die(f"{url}: HTTP 404 — no sitemap on this host: not a TalentLyft careers site, or its rules changed", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)
    if "<urlset" not in body and "<sitemapindex" not in body:
        die(f"{url}: not a sitemap ({len(body)} characters).", EXIT_PARTIAL)
    jobs = sitemap_jobs(host, body)
    seen, todo = set(), []
    for slug, u, lm in jobs:
        if slug not in seen:
            seen.add(slug)
            todo.append((slug, u, lm))
    total = len(todo)
    if a.max_pages:
        todo = todo[: a.max_pages]
    if todo:
        note(f"the sitemap names {th(total)} job page(s); reading {th(len(todo))} at the written Crawl-delay of {int(WRITTEN_DELAY)} s — about {th(int(len(todo) * WRITTEN_DELAY // 60))} min.")
    rows, gone = [], []
    for slug, u, lm in todo:
        r, why = read_job(host, slug, u, lm, stamp)
        if r:
            rows.append(r)
        else:
            gone.append((slug, why))
    emitted = [r for r in rows if not stamp or r["country"] == stamp]
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    tail = f"; {len(gone)} named page(s) without a posting ({', '.join(f'{s}: {w}' for s, w in gone[:5])})" if gone else ""
    if stamp:
        note(f"{th(n)} emitted for {stamp} of the {th(len(rows))} read — the sitemap names {th(total)} job page(s); a posting without a country is stamped {stamp}{tail}.")
    elif a.max_pages and len(todo) < total:
        note(f"{th(n)} emitted of the {th(total)} job pages the sitemap names — {th(len(todo))} read by request (--max-pages), not a shortfall{tail}.")
    elif n == total:
        note(f"{th(n)} emitted — the sitemap names {th(total)} job page(s): equal (a sitemap's count is the pages it names, not a count the site states){tail}.")
    else:
        note(f"{th(n)} emitted — the sitemap names {th(total)} job page(s): {th(total - n)} short{tail}.")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    host = parts.netloc.lower()
    m = JOB_PATH_RE.match(parts.path)
    if not host.endswith("." + DOMAIN) or not m or host.split(".")[0] in ("www", "help", "careers", "app"):
        die(f"{a.url!r}: not a TalentLyft job address (https://<tenant>.{DOMAIN}/jobs/<slug>)")
    TENANT["host"] = host
    url = f"https://{host}/jobs/{m.group(1)}"
    r, why = read_job(host, m.group(1), url, None, None)
    if not r:
        die(f"{url}: {why}", EXIT_GONE if why == "gone" else EXIT_PARTIAL)
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="TalentLyft — one tenant's jobs by the sitemap its rules declare and the JobPosting on each job page, at the Crawl-delay the rules write (150 s); the list call the page makes is refused in a file without a group and never requested. Issue #474.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the sitemap, then one page per job, 150 s apart as written")
    s.add_argument("--tenant", required=True, help="the subdomain (secret-level), the host, or the site's URL")
    s.add_argument("--country-code", help="keep the postings whose addressCountry is this ISO2 (one without is stamped)")
    s.add_argument("--max-pages", type=int, help="read at most N job pages")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one job by its page's JobPosting; street and postal code withheld, description scrubbed")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
