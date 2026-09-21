#!/usr/bin/env python3
"""Beetween (`<tenant>.jobs.beetween.com`, a French ATS — one career site at a time): the career site's own JSON API — `POST /api/job/list` stating `numFound`, one hundred a page, `GET /api/job/<wid>` — and the advert of the vendor's apply page (`app.beetween.com/WeaselWeb/p/#/apply/job/<wid>`, the address France Travail and FHF relay) through the backend's `jobs/byWid`. Issue #493.

  beetween.py jobs --tenant <name|host|url>
  beetween.py ad --url https://<tenant>.jobs.beetween.com/job/<wid>
  beetween.py ad --url "https://app.beetween.com/WeaselWeb/p/#/apply/job/<wid>/<slug>"

THE TENANT is the subdomain of `jobs.beetween.com` the employer's career
site lives on (`proxiserve`, `welcoop`, `joker-interim`, `comptoir`,
`aismt13`, `voyageursdumonde`), found by the family's signature
`jobs.beetween.com` in a search engine on 2026-09-21 — never composed: an
unknown subdomain answers 404 on `/api/client/information` (exit 3). Some
employers serve the same site under their own host (`welcoop.nos-recrutements.fr`
is what Welcoop's adverts link) — the user may name that host; the API is
the site's own. The vendor's `www`, `app`, `apehi`, `assets`, `emploi`
hosts are not tenants.

THE RULES: `<tenant>.jobs.beetween.com/robots.txt` is 22 bytes —
`User-agent: *`, `Allow: /` — on every site read (md5 f77c87f977e0).
`app.beetween.com/robots.txt` answers the Nuxt shell (4 065 B, the same
for every path), `apehi.beetween.com/robots.txt` a 74 B 404: no rules on
either, `certain: False` and `True` respectively. No Crawl-delay; 2 s
between requests are ours.

THE CAREER SITE, MEASURED 2026-09-21 06:49–06:51 UTC. A Vue application
(`/js/app.<hash>.js`) whose API is `/api` on the same host:
`GET /api/client/information` names the employer (`completeName`
«Comptoir Des Voyages», `website`); `POST /api/job/list` with the JSON
its page sends (`keywords`, `locations`, `contractTypes`, `categories`,
`page`, `rows`) answers `numFound` and `jobs[]` — **`rows` is honoured up
to the whole board** (500 answered all 216 of Proxiserve; the adapter
asks one hundred a page and walks to `numFound`: 100 + 100 + 16 = 216,
216 distinct `wid`; Welcoop 31, Joker Interim 31, Comptoir 0 — an empty
board said so). A job: `id`, `wid` (the ten-character key), `title`,
`descriptionMission`, `descriptionCompany`, `descriptionProfile` (HTML),
`creationDate`, `city`, `region`, `country`, `gpsCoordinates`, `logo`,
`contractType` (CDI, Intérim…), `salaryMin`/`salaryMax`/`salaryUnit`
(MONTH, YEAR), `language`, `url` (the advert's address — on the site's
host or the employer's own), `agency`, `categories`, `frontPageAd`,
`contractDurationValue`/`Unit`. `GET /api/job/<wid>` is the same record
with `salaryCurrency`; an unknown wid answers 500 (exit 6).

THE VENDOR'S APPLY PAGE — the address the aggregators relay
(`france-travail.md`: BEETWEEN first supplier of the partner feed, 38 of
150 Paris ads; `fhf.md`: 6 of 36) — is
`https://app.beetween.com/WeaselWeb/p/#/apply/job/<wid><2 chars>/<slug>`:
a hash route, nothing of it reaches the server. Its page calls
`GET https://apehi.beetween.com/WeaselWeb/api/jobs/byWid/<wid>` (found in
the page's chunk `87ea881.js`: `fetchPost`): `wid`, `recruitmentTitle`,
`description` (HTML), `location` («19000 Tulle, Nouvelle-Aquitaine»),
`company`, `industry`, `locale`, `logoUrl`. `ad --url` takes that address
too and reads the advert there — the employer named where France Travail
does not name it.

WITHHELD: the three texts scrubbed of e-mail addresses and telephone
numbers; the logo never emitted; the application (`/apply/job/`, an
account or a form) never touched; `contacts_withheld` on every record.
The country is the job's own (`country` → ISO2 when named).
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

BOARD, DOMAIN, APP_HOST, API_HOST = "beetween", "jobs.beetween.com", "app.beetween.com", "apehi.beetween.com"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
NOT_TENANTS = {"www", "app", "apehi", "assets", "emploi", "recrutement", "api", "admin"}
ROWS = 100

TENANT_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", re.I)
HOST_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$", re.I)
WID_RE = re.compile(r"^[a-z0-9]{10}$")
APPLY_RE = re.compile(r"/apply/job/([a-z0-9]{10})[a-z0-9]{0,2}(?:/|$)")
COUNTRIES = {"france": "FR", "belgique": "BE", "belgium": "BE", "suisse": "CH", "switzerland": "CH", "luxembourg": "LU", "espagne": "ES", "spain": "ES", "allemagne": "DE", "germany": "DE", "italie": "IT", "italy": "IT", "royaume-uni": "GB", "united kingdom": "GB", "portugal": "PT", "maroc": "MA", "tunisie": "TN", "sénégal": "SN", "senegal": "SN", "côte d'ivoire": "CI", "canada": "CA", "monaco": "MC", "pays-bas": "NL", "netherlands": "NL"}
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?\d[\d\s().\-]{7,}\d(?!\w)")
_PACES = {}
TENANT = {"host": None}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[beetween] {msg}", file=sys.stderr)


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


def request(url, payload=None):
    """(status, body) — this run's host only, the guard first, 2 s apart; `payload` makes it the JSON POST the site's page sends."""
    parts = urllib.parse.urlsplit(url)
    host = parts.netloc.lower()
    if not TENANT["host"] or host != TENANT["host"]:
        die(f"{url}: not this run's Beetween host ({TENANT['host'] or 'none named'}) — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(host, Pace(host, own=2.0)).wait()
    headers = {"User-Agent": UA, "Accept": "application/json", "Accept-Language": "fr,en"}
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(wire_url(url), data=body, headers=headers)
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
    """`proxiserve`, `proxiserve.jobs.beetween.com`, `welcoop.nos-recrutements.fr` or a URL on one of them → the host."""
    s = (arg or "").strip().lower()
    if "://" in s or "/" in s:
        s = urllib.parse.urlsplit(s if "://" in s else "https://" + s).netloc
    if not s:
        die(f"--tenant {arg!r}: name the career site (proxiserve), its host or its URL")
    if "." not in s:
        if not TENANT_RE.match(s) or s in NOT_TENANTS:
            die(f"--tenant {arg!r}: not a career site (the vendor's own hosts are not a board)")
        return f"{s}.{DOMAIN}"
    if not HOST_RE.match(s) or s in (DOMAIN, "www." + DOMAIN, APP_HOST, API_HOST, "beetween.com", "www.beetween.com") or s.endswith(".beetween.com") and not s.endswith("." + DOMAIN):
        die(f"--tenant {arg!r}: not a Beetween career site host (<tenant>.{DOMAIN}, or the employer's own host)")
    if s.endswith("." + DOMAIN):
        sub = s[: -len("." + DOMAIN)]
        if not TENANT_RE.match(sub) or sub in NOT_TENANTS:
            die(f"--tenant {arg!r}: not a career site host")
    return s


def country_of(name):
    return COUNTRIES.get((name or "").strip().lower())


def parse_json(body, url):
    try:
        return json.loads(body)
    except ValueError:
        die(f"{url}: not JSON — the site answered something else (a page, a shell).", EXIT_PARTIAL)


def record(j, host, company):
    wid = j.get("wid")
    mission, comp, prof = (scrub(text(j.get(k))) for k in ("descriptionMission", "descriptionCompany", "descriptionProfile"))
    sal = {k: j.get(k) for k in ("salaryMin", "salaryMax", "salaryUnit", "salaryCurrency") if j.get(k) is not None}
    gps = (j.get("gpsCoordinates") or "").split(",")
    return {
        "source": BOARD, "tenant": host, "ledger_id": f"{BOARD}:{wid}", "id": wid, "site_id": str(j.get("id")) if j.get("id") is not None else None,
        "url": j.get("url") or f"https://{host}/job/{wid}",
        "title": (j.get("title") or "").strip() or None, "company": company, "agency": j.get("agency") or None,
        "posted": j.get("creationDate"), "country": country_of(j.get("country")), "country_name": j.get("country"), "region": j.get("region"), "place": j.get("city"),
        "lat": float(gps[0]) if len(gps) == 2 and re.fullmatch(r"-?\d+(\.\d+)?", gps[0].strip()) else None,
        "lon": float(gps[1]) if len(gps) == 2 and re.fullmatch(r"-?\d+(\.\d+)?", gps[1].strip()) else None,
        "contract_type": j.get("contractType"), "contract_duration": (f"{j['contractDurationValue']} {j['contractDurationUnit']}".strip() if j.get("contractDurationUnit") and str(j.get("contractDurationValue") or "0") != "0" else None),
        "salary": sal or None, "language": j.get("language"), "categories": j.get("categories") or None,
        "description": (mission or "")[:20000] or None,
        "sections": {k: v[:8000] for k, v in (("Entreprise", comp), ("Profil", prof)) if v} or None,
        "contacts_withheld": True,
    }


def status_of(st, url, host):
    if st == 404:
        die(f"{url}: HTTP 404 — {host} is not a Beetween career site, or the page is gone.", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)


def cmd_jobs(a):
    host = tenant_of(a.tenant)
    TENANT["host"] = host
    url = f"https://{host}/api/client/information"
    st, body = request(url)
    status_of(st, url, host)
    client = parse_json(body, url)
    company = (client.get("completeName") or client.get("name") or "").strip() or None if isinstance(client, dict) else None
    seen, out, total = set(), [], None
    for page in range(1, a.max_pages + 1):
        lurl = f"https://{host}/api/job/list"
        st, body = request(lurl, {"keywords": "", "locations": [], "contractTypes": [], "categories": [], "page": page, "rows": ROWS})
        status_of(st, lurl, host)
        j = parse_json(body, lurl)
        if not isinstance(j, dict) or not isinstance(j.get("jobs"), list):
            die(f"{lurl}: no `jobs` list in the answer ({str(j)[:120]}).", EXIT_PARTIAL)
        if isinstance(j.get("numFound"), int):
            total = j["numFound"]
        fresh = [x for x in j["jobs"] if isinstance(x, dict) and x.get("wid") and x["wid"] not in seen]
        if not fresh:
            break
        for x in fresh:
            seen.add(x["wid"])
            out.append(record(x, host, company))
        if total is not None and len(out) >= total:
            break
    else:
        note(f"{a.max_pages} pages read (--max-pages) and the last still had jobs — the walk is truncated.")
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    if total is None:
        note(f"{th(n)} emitted — the site states no numFound.")
    elif n == total:
        note(f"{th(n)} emitted — the site states {th(total)}: equal.")
    else:
        note(f"{th(n)} emitted — the site states {th(total)}: {th(abs(total - n))} " + ("short" if total > n else "more emitted than stated") + ".")


def cmd_ad(a):
    raw = (a.url or "").strip()
    parts = urllib.parse.urlsplit(raw)
    host = parts.netloc.lower()
    if host == APP_HOST:
        m = APPLY_RE.search(parts.fragment or "") or APPLY_RE.search(parts.path or "")
        if not m:
            die(f"{raw!r}: not a Beetween apply address (https://{APP_HOST}/WeaselWeb/p/#/apply/job/<wid>/<slug>)")
        wid = m.group(1)
        TENANT["host"] = API_HOST
        url = f"https://{API_HOST}/WeaselWeb/api/jobs/byWid/{wid}"
        st, body = request(url)
        status_of(st, url, API_HOST)
        j = parse_json(body, url)
        if not isinstance(j, dict) or not j.get("recruitmentTitle"):
            die(f"{url}: no advert in the answer — the advert is gone.", EXIT_PARTIAL)
        r = {
            "source": BOARD, "tenant": None, "ledger_id": f"{BOARD}:{wid}", "id": wid, "url": raw,                                    # the address as relayed — its two-character suffix is the page's, not the wid's
            "title": j["recruitmentTitle"].strip(), "company": (j.get("company") or "").strip() or None, "industry": j.get("industry"),
            "location": j.get("location"), "language": j.get("locale"),
            "description": (scrub(text(j.get("description"))) or "")[:20000] or None, "contacts_withheld": True,
        }
        print(json.dumps(r, ensure_ascii=False))
        return
    m = re.fullmatch(r"/(?:html/)?job/([a-z0-9]{10})/?", parts.path or "")
    if not m:
        die(f"{raw!r}: not a Beetween advert address (https://<career site>/job/<wid>, or the vendor's apply page)")
    host = tenant_of(host)
    TENANT["host"] = host
    wid = m.group(1)
    url = f"https://{host}/api/job/{wid}"
    st, body = request(url)
    if st == 500:
        die(f"{url}: HTTP 500 — the site answers so to a wid it does not have: gone, or another site's.", EXIT_PARTIAL)
    status_of(st, url, host)
    j = parse_json(body, url)
    if not isinstance(j, dict) or not j.get("wid"):
        die(f"{url}: no job in the answer.", EXIT_PARTIAL)
    curl = f"https://{host}/api/client/information"
    st2, cbody = request(curl)
    client = parse_json(cbody, curl) if st2 == 200 else {}
    company = (client.get("completeName") or client.get("name") or "").strip() or None if isinstance(client, dict) else None
    print(json.dumps(record(j, host, company), ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description="Beetween — one career site's jobs through its own JSON API (numFound beside), the advert by its wid on the site or on the vendor's apply page; texts scrubbed, no contact. Issue #493.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("jobs", help="the career site's jobs, one hundred a page to numFound")
    s.add_argument("--tenant", required=True, help="the subdomain (proxiserve), the host (proxiserve.jobs.beetween.com, welcoop.nos-recrutements.fr) or the site's URL")
    s.add_argument("--max-pages", type=int, default=50)
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="one advert: /job/<wid> on a career site, or the vendor's apply page")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
