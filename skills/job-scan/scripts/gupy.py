#!/usr/bin/env python3
"""Gupy (`<tenant>.gupy.io`, Brazil's main ATS — one career page at a time): the career page's root ships every published job in its Next.js `__NEXT_DATA__` and prints the count in the page («161 vagas»); `/jobs/<id>` ships the whole job the same way. Issue #491.

  gupy.py jobs --tenant <name|host|url>
  gupy.py ad --url https://<tenant>.gupy.io/jobs/<id>

THE TENANT is the subdomain of `gupy.io` the employer's career page lives
on (`farm`, `renner`, `lojasrenner`, `youcom`, `motiva`, `randon`…), found
by the family's signature in a search engine on 2026-09-21 — never
composed. A company may run several career pages (Lojas Renner's group
page `renner` links `lojasrenner`, `youcom`, `realize`, `camicadocarreiras`
…): each is a tenant of its own; the job's `company.subdomain` (`gruposoma`
behind `farm`) is emitted as `group`. The vendor's own hosts (`www`,
`portal`, `suporte`, `attachments`, `front-statics-assets`) are not boards.

THE RULES: `/robots.txt` on a tenant answers the application's own HTML
page (21 525 B, a Next.js route named `robots`), not a rules file —
`_robots` reads it as `unrecognised`, no rules, `certain: False`: open, a
policy applied to an absence. The aggregated `portal.gupy.io` publishes 67
bytes allowing everything (the issue's reading of 04.09). No Crawl-delay
anywhere; 2 s between requests are ours.

THE LIST, MEASURED 2026-09-21 06:26 UTC. The root (200; FARM 179 064 B,
Lojas Renner 160 204 B) is a Next.js page whose `__NEXT_DATA__`
`props.pageProps.jobs` carries **every published job** — id, title,
`type` (`vacancy_type_effective`, …), `department`, `workplace.address`
(country, state, city), `workplaceType`, `quickApply` — and whose text
prints the count («161 vagas»): FARM 161 = 161, Lojas Renner 92. No
paging, no search call: one request is the board. The job's address is
`/jobs/<id>` (the page links it with `?jobBoardSource=gupy_public_page`,
a tracking parameter never added here).

THE JOB PAGE (200, ~105 KB): `pageProps.job` — `name`, `description`,
`responsibilities`, `prerequisites`, `relevantExperiences` (HTML each),
`publishedAt`, `expiresAt` / `registerEndDate`, `jobType`, `workplaceType`,
`handicapped` (open to people with disabilities), `addressCity`,
`addressState`, `addressCountry`, `addressLine` (a street and a
postcode — never emitted), `jobSteps` (the process, names only),
`company.subdomain`, `careerPage.name`, `code`. No JobPosting.

WITHHELD: the street and postcode (`addressLine`); the pictures and logos;
e-mail addresses and telephone numbers scrubbed from the texts; the
application (an account, `quickApply` or the form) never touched;
`contacts_withheld` on every record. The country comes from the job
itself (`addressCountryShortName`, `workplace.address.country`), never
stamped.
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

BOARD, DOMAIN = "gupy", "gupy.io"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
NOT_TENANTS = {"www", "portal", "suporte", "suporte-candidatos", "attachments", "front-statics-assets", "api", "app", "login", "admin"}

TENANT_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", re.I)
NEXT_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)
COUNT_RE = re.compile(r"\b(\d[\d.]*)\s+vagas?\b", re.I)
COUNTRIES = {"brasil": "BR", "brazil": "BR", "argentina": "AR", "chile": "CL", "colombia": "CO", "colômbia": "CO", "méxico": "MX", "mexico": "MX", "portugal": "PT", "peru": "PE", "perú": "PE", "uruguai": "UY", "uruguay": "UY", "paraguai": "PY", "paraguay": "PY", "estados unidos": "US"}
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
_PACES = {}
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[gupy] {msg}", file=sys.stderr)


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


def request(url):
    parts = urllib.parse.urlsplit(url)
    host = parts.netloc.lower()
    if not TENANT["host"] or host != TENANT["host"] or not host.endswith("." + DOMAIN):
        die(f"{url}: not this run's Gupy tenant ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "pt-BR,pt,en"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


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
    """`farm`, `farm.gupy.io` or a URL on it → the host."""
    s = (arg or "").strip().lower()
    if "://" in s or "/" in s:
        s = urllib.parse.urlsplit(s if "://" in s else "https://" + s).netloc
    if not s:
        die(f"--tenant {arg!r}: name the career page (farm), its host (farm.gupy.io) or its URL")
    if "." not in s:
        if not TENANT_RE.match(s) or s in NOT_TENANTS:
            die(f"--tenant {arg!r}: not a career page (the vendor's own hosts are not a board)")
        return f"{s}.{DOMAIN}"
    sub = s[: -len("." + DOMAIN)] if s.endswith("." + DOMAIN) else None
    if not sub or not TENANT_RE.match(sub) or sub in NOT_TENANTS:
        die(f"--tenant {arg!r}: not a Gupy career page host (<tenant>.{DOMAIN})")
    return s


def next_data(body):
    m = NEXT_RE.search(body or "")
    if not m:
        return None
    try:
        return json.loads(m.group(1)).get("props", {}).get("pageProps", {})
    except ValueError:
        return None


def stated_count(body):
    t = re.sub(r"<script.*?</script>", "", body or "", flags=re.S)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t))
    m = COUNT_RE.search(t)
    return int(m.group(1).replace(".", "")) if m else None


def country_of(name, short=None):
    if short and re.fullmatch(r"[A-Za-z]{2}", short):
        return short.upper()
    return COUNTRIES.get((name or "").strip().lower())


def status_of(st, url, host):
    if st == 404:
        die(f"{url}: HTTP 404 — {host} is not a Gupy career page, or the page is gone.", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    TENANT["host"] = host
    url = f"https://{host}/"
    st, body = request(url)
    status_of(st, url, host)
    pp = next_data(body)
    if pp is None or not isinstance(pp.get("jobs"), list):
        die(f"{url}: no `__NEXT_DATA__` with `pageProps.jobs` in the page — not a Gupy career page, or the page changed shape.", EXIT_PARTIAL)
    page = pp.get("careerPage") or {}
    company = page.get("publicationName") or page.get("name")
    seen, out = set(), []
    for j in pp["jobs"]:
        if not isinstance(j, dict) or j.get("id") is None or str(j["id"]) in seen:
            continue
        seen.add(str(j["id"]))
        wp = j.get("workplace") or {}
        ad = wp.get("address") or {}
        out.append({
            "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{j['id']}", "id": str(j["id"]), "url": f"https://{host}/jobs/{j['id']}",
            "title": (j.get("title") or "").strip() or None, "company": company, "department": j.get("department") or None,
            "country": country_of(ad.get("country")), "state": ad.get("stateShortName") or ad.get("state") or None, "place": ad.get("city") or None,
            "job_type": j.get("type"), "workplace_type": wp.get("workplaceType"), "contacts_withheld": True,
        })
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n, total = len(out), stated_count(body)
    if total is None:
        note(f"{th(n)} emitted — the page prints no «N vagas» count.")
    elif n == total:
        note(f"{th(n)} emitted — the page prints {th(total)} vagas: equal.")
    else:
        note(f"{th(n)} emitted — the page prints {th(total)} vagas: {th(abs(total - n))} " + ("short" if total > n else "more emitted than printed") + ".")


def cmd_ad(a):
    parts = urllib.parse.urlsplit((a.url or "").strip())
    host = parts.netloc.lower()
    m = re.fullmatch(r"/jobs?/(\d+)/?", parts.path)
    sub = host[: -len("." + DOMAIN)] if host.endswith("." + DOMAIN) else None
    if not sub or not TENANT_RE.match(sub) or sub in NOT_TENANTS or not m:
        die(f"{a.url!r}: not a Gupy job address (https://<tenant>.{DOMAIN}/jobs/<id>)")
    TENANT["host"] = host
    jid = m.group(1)
    url = f"https://{host}/jobs/{jid}"
    st, body = request(url)
    status_of(st, url, host)
    pp = next_data(body)
    job = (pp or {}).get("job")
    if not isinstance(job, dict) or not job.get("name"):
        die(f"{url}: no `pageProps.job` in the page — the job is gone, or the id is another career page's.", EXIT_PARTIAL)
    page = job.get("careerPage") or {}
    parts_txt = [(k, scrub(text(job.get(k)))) for k in ("description", "responsibilities", "prerequisites", "relevantExperiences")]
    r = {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{host}:{jid}", "id": jid, "url": url,
        "title": job["name"].strip(), "company": page.get("name") or None, "group": (job.get("company") or {}).get("subdomain"),
        "code": job.get("code"), "status": job.get("status"),
        "posted": job.get("publishedAt"), "closes": job.get("expiresAt") or job.get("registerEndDate"),
        "country": country_of(job.get("addressCountry"), job.get("addressCountryShortName")), "state": job.get("addressStateShortName") or job.get("addressState"), "place": job.get("addressCity"),
        "job_type": job.get("jobType"), "workplace_type": job.get("workplaceType"), "open_to_disabled": job.get("handicapped"),
        "description": (parts_txt[0][1] or "")[:20000] or None,
        "sections": {k: v[:8000] for k, v in parts_txt[1:] if v} or None,
        "steps": [s.get("name") for s in (job.get("jobSteps") or []) if isinstance(s, dict) and s.get("name")] or None,
        "contacts_withheld": True,
    }
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Gupy — one career page's published jobs from its own page data (the count it prints beside), and the job page; the street never emitted, no contact. Issue #491.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="every published job of the career page, one request; the page's «N vagas» beside the emitted number")
    s.add_argument("--tenant", required=True, help="the subdomain (farm), the host (farm.gupy.io) or the page's URL")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one job by its page (/jobs/<id>); texts scrubbed, the street withheld")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
