#!/usr/bin/env python3
"""Read one employer's SAP SuccessFactors career site.

SuccessFactors is an ATS, not a board: one employer per host, no search across
employers. Employers front it with a vanity domain of their own
(jobs.<employer>.ch, www.carrieres-<employer>.com), so the host tells you
nothing and the path tells you everything.

TWO ROUTES, AND THE RULES FILE CHOOSES — #202, 2026-09-11.

    api    POST https://<host>/services/recruiting/v1/jobs
           {"locale": "fr_FR", "pageNumber": 0, "keywords": "..."}
           — a public JSON endpoint, no key, no cookie, no browser
    html   GET  https://<host>/search/?q=...&startrow=N   -> the job tiles
           GET  https://<host>/job/<slug>/<id>/           -> one JobPosting
           — taken when `/services/` is refused and `/search/` + `/job/` are not

**`/services/` is refused by 3 tenants of 3** measured 2026-09-11 (`jobs.fr.ch`,
`jobs.bcv.ch`, `jobs.sicpa.com`, each `Disallow: /services/` to `*`), and it was
this adapter's only route: every one of them returned exit 7 and zero rows —
**a zero indistinguishable from an employer with nothing open.**

v1.9.0 recorded that `/search/` "is rendered entirely client-side and lists
nothing to a plain fetch". **That was measured on ONE tenant and written as a
property of the platform.** It is a property of the TENANT, dated: `jobs.bcv.ch`
serves 0 `/job/` links on `/search/` (66 kB shell, 2026-09-09); `jobs.fr.ch`
serves 25 tiles a page and states «133 offres» (378 kB, 2026-09-11). So when
the HTML route returns no tile, the adapter does not print zero — it says that
THIS tenant does not serve its list to a plain client and that `/services/` is
refused to it: an INDETERMINATE, exit 8, a browser route to document.

The locale is the trap on the API route. Get it wrong and the board comes back
EMPTY with no error at all — see `locale`, which reads the right one off the
site. The HTML route does not take one.

Usage:
  successfactors.py locale --host jobs.bcv.ch
  successfactors.py list   --host jobs.bcv.ch [--keywords analyste] [--pages 3]
  successfactors.py ad     --host jobs.bcv.ch --id 31130
  successfactors.py check  --host jobs.bcv.ch --id 31130
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
from _robots import allowed as robots_allowed, full_path
from _robots import verdict as robots_verdict

from _ua import UA
API = "/services/recruiting/v1/jobs"
PAGE = 10          # fixed by the service; pageNumber is 0-indexed
SEARCH = "/search/"
JOB = "/job/"
ROWS = 25          # tiles per /search/ page on the tenants measured; `startrow` is 0-indexed
# One tile per vacancy on the HTML route. `job-id-<id>` and `data-url` sit on
# the same `<li>`. **The path is not always `/job/…`**: a tenant's BRAND
# sub-site prefixes it — `/Police_Cantonale/job/…` on `jobs.fr.ch`, 2 tiles
# of 25 on page 3, 2026-09-11 — and a pattern anchored on `/job/` read 23 of
# the 25 the page itself declared. So: any `data-url` that contains `/job/`,
# and the exact URL is gated before it is fetched.
TILE_RE = re.compile(r'<li class="job-tile job-id-(\d+)[^"]*"[^>]*?data-url="([^"]*/job/[^"]+)"',
                     re.S)
TITLE_RE = re.compile(r'(?s)class="jobTitle-link[^"]*"[^>]*>\s*(.*?)\s*</a>')
# `id="…-section-city-value"` and NOT the bare `section-city-value"`: the
# label `<span>` beside it carries `aria-describedby="…-section-city-value"`,
# and a pattern without the `id=` anchor read the label's text — «Ville» —
# as the value. Caught on the first run, 2026-09-11.
FIELD_RE = re.compile(r'id="job-\d+-[a-z]+-section-([a-z0-9]+)-value"[^>]*>\s*([^<]*?)\s*<')
# The page states its own total, in the tenant's language — «Affichage de 1
# sur 25 parmi 133 offres d'emploi». The label is localised; the three numbers
# are not, and the last is the total. Read as an ANCHOR, printed beside the
# count this adapter extracted — never used in its place.
RESULTS_LABEL_RE = re.compile(r'(?s)id="searchresultslabel"[^>]*>(.*?)</label>')
LOCALE_RE = re.compile(r"locale[=:]\s*['\"]?([a-z]{2}_[A-Z]{2})")
DESC_RE = re.compile(r'(?is)<div[^>]*(?:class|id)="[^"]*joblayouttoken[^"]*"[^>]*>(.*)')


def gate_path(url):
    """Ask on the exact URL, before anything leaves. #176.

    **This module decided on `verdict(host)["sweep"]` and nothing else.**
    `sweep` answers *is this host closed in one block* under `OUR_AGENTS` —
    six names a site may use **about** us, four of which we never send — so
    the owner's decision of 2026-09-07 reached `allowed()` and never reached
    here. **And a sweep verdict is not a path verdict:** `hiringcafe.com`
    answers `sweep: True` above its own reason, *"this host refuses 17
    path(s) to `*`"*.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return
    a = robots_allowed(parts.netloc, full_path(parts))
    # An unknown is not a refusal: `not None` is `True` for both.
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", 8)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", 7)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def get(url):
    gate_path(url)
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=45)
        return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach {urllib.parse.urlsplit(url).netloc}: {e}")


def get_with_url(url):
    """`get`, plus where it landed.

    **The landing URL is half the signal here.** An id that does not resolve is
    redirected to the portal's own error page, and a check that reads only the
    body sees a 200 of the right size and has to guess.
    """
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=45)
        return r.getcode(), decode_body(r.read(), r.headers)[0], r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", getattr(e, "url", url)
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach {urllib.parse.urlsplit(url).netloc}: {e}")


def post(host, body):
    url = f"https://{host}{API}"
    gate_path(url)
    data = json.dumps(body).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            url, data=data,
            headers={"User-Agent": UA, "Content-Type": "application/json"}),
            timeout=60)
        return json.loads(decode_body(r.read(), r.headers)[0])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            die(f"{host} has no SuccessFactors job service at {API} (HTTP 404). "
                f"Check the host — this is not a SuccessFactors career site, or "
                f"it is on a build that predates this endpoint.", code=4)
        die(f"{host} answered HTTP {e.code} on {API}", code=4)
    except Exception as e:  # noqa: BLE001
        die(f"could not reach {host}: {e}")


def to_text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def page_title(markup):
    m = re.search(r"(?is)<title>(.*?)</title>", markup)
    return htmlmod.unescape(m.group(1)).strip() if m else ""


def discover_locale(host):
    """Read the tenant's own locale off /search/.

    Guessing it is the single most expensive mistake on this ATS: a locale the
    tenant does not publish returns an EMPTY board with `error: null`, which is
    indistinguishable from an employer with nothing open.
    """
    status, body = get(f"https://{host}/search/")
    if status != 200:
        return None
    m = LOCALE_RE.search(body)
    return m.group(1) if m else None


def search(host, locale, keywords, page):
    body = {"locale": locale, "pageNumber": page}
    if keywords:
        body["keywords"] = keywords
    return post(host, body)


def refuse_on_error(host, payload, locale):
    """Separate 'this tenant does not serve jobs' from 'nothing matched'."""
    err = payload.get("error")
    if err:
        die(f"{host} answered with an explicit refusal: "
            f"{err.get('code')} / {err.get('message')!r}. The endpoint exists "
            f"but this tenant is not serving jobs through it — that is NOT an "
            f"employer with nothing open. Read their /search/ page in a browser "
            f"instead, and report the board with the board-request skill.",
            code=5)
    if payload.get("totalJobs") in (0, None) and not payload.get("jobSearchResult"):
        found = discover_locale(host)
        if found and found != locale:
            die(f"zero jobs for locale {locale!r}, and this tenant publishes "
                f"{found!r}. A locale the tenant does not use returns an EMPTY "
                f"board with no error — retry with --locale {found}.", code=4)


def card(host, locale, r):
    loc = r.get("filter1") or []
    cat = r.get("filter5") or []
    # The API returns the slug HTML-escaped (`...-d&apos;applications-...`).
    # The slug segment is decorative — /job/x/<id>-<locale> answers 200 just as
    # well — but an escaped one in the ledger is a URL nobody can read.
    slug = htmlmod.unescape(r.get("unifiedUrlTitle") or r.get("urlTitle") or "")
    jid = str(r.get("id"))
    return {
        "id": jid,
        "ledger_id": f"successfactors:{host}:{jid}",
        "url": f"https://{host}/job/{slug}/{jid}-{locale}",
        "title": r.get("unifiedStandardTitle"),
        "company": host,
        "host": host,
        "locale": locale,
        "provider": "successfactors",
        # filter1..filter5 are PER-TENANT facet configuration. On one tenant
        # filter1 is a town and filter5 a business area; another tenant may map
        # them to anything at all. Recorded raw, never renamed.
        "location_raw": ", ".join(loc) or None,
        "category_raw": ", ".join(cat) or None,
        "published": r.get("unifiedStandardStart"),
        "currency": ", ".join(r.get("currency") or []) or None,
        "supported_locales": r.get("supportedLocales"),
    }


# The vacancy URL has **two shapes, and they are per tenant**. BCV serves
# `/job/<slug>/<id>-<locale>`; SICPA serves `/job/<slug>/<id>/` and sends the
# locale form to `/errorpage/?errortype=Exception`. Measured 2026-09-02, and it
# matters more than it looks: with only the first shape, `check` on a LIVE
# SICPA vacancy answered `unverified` — the wrong shape landed on the error
# page, the error page equals the control, and the control test concluded that
# the requisition does not resolve. **A live advert reported as unresolvable,
# plausibly, in silence.** Issue #87.
AD_SHAPES = ("https://{host}/job/{slug}/{jid}-{locale}",
             "https://{host}/job/{slug}/{jid}/")
ERROR_PATH = "/errorpage/"
POSTING_RE = re.compile(r'itemtype="[^"]*JobPosting"', re.I)


def read_ad(host, locale, jid, slug=""):
    """The vacancy page, whichever URL shape this tenant serves.

    Returns `(status, body, url)`. A shape that redirects to the portal's
    error page is not this tenant's shape; the next one is tried.
    """
    last = (0, "", "")
    for shape in AD_SHAPES:
        url = shape.format(host=host, slug=slug or "x", jid=jid, locale=locale)
        status, body, landed = get_with_url(url)
        last = (status, body, landed)
        if status == 200 and ERROR_PATH not in landed and POSTING_RE.search(body):
            return status, body, landed
    return last


def route_for(host):
    """`(route, why)` — `"api"`, `"html"` or `None`, chosen by the rules file,
    path by path. #202.

    **Path by path, because a sweep verdict is not a path verdict** (#176):
    all three tenants measured are `sweep: True` and refuse `/services/`.
    `None` comes with the reason, and the caller says whether it is a refusal
    (every route closed, exit 7) or an unknown (rules unreadable, exit 8).
    """
    api = robots_allowed(host, API)
    if api["allowed"] is None:
        return None, f"the rules could not be read: {api['reason']}"
    if api["allowed"]:
        return "api", f"`{API}` is permitted — the JSON service"
    s = robots_allowed(host, SEARCH)
    j = robots_allowed(host, JOB)
    if s["allowed"] and j["allowed"]:
        return "html", (f"`{API}` is refused (`{api['rule']}`), `{SEARCH}` and "
                        f"`{JOB}` are permitted — the job tiles and each "
                        f"vacancy's JobPosting block")
    closed = [p for p, v in ((API, api), (SEARCH, s), (JOB, j)) if not v["allowed"]]
    return None, (f"every route is closed by the rules: {', '.join(closed)} "
                  f"refused. Nothing here permits a sweep")


def tiles(body):
    """`[(id, path, title, fields)]` for every job tile on a `/search/` page."""
    out, seen = [], set()
    for m in TILE_RE.finditer(body):
        jid, path = m.group(1), m.group(2)
        if jid in seen:
            continue
        seen.add(jid)
        chunk = body[m.start():body.find("</li>", m.start())]
        t = TITLE_RE.search(chunk)
        fields = {}
        for name, value in FIELD_RE.findall(chunk):
            # the tile repeats its fields for desktop and mobile; first wins
            fields.setdefault(name, htmlmod.unescape(value).strip())
        out.append((jid, htmlmod.unescape(path),
                    to_text(t.group(1)) if t else "", fields))
    return out


def stated_total(body):
    """What the page itself says it holds, or `None` — the anchor of #181."""
    m = RESULTS_LABEL_RE.search(body)
    if not m:
        return None
    nums = re.findall(r"\d+", to_text(m.group(1)))
    return int(nums[-1]) if len(nums) >= 3 else None


def card_html(host, jid, path, title, fields):
    """The same shape as `card()`, from a tile instead of a JSON row. The
    facets are PER-TENANT here too (`city`, `dept`, `shifttype`, `customfield5`
    on `jobs.fr.ch`) and are recorded raw under `fields`, never renamed."""
    return {
        "id": jid,
        "ledger_id": f"successfactors:{host}:{jid}",
        "url": f"https://{host}{path}",
        "title": title,
        "company": host,
        "host": host,
        "locale": None,
        "provider": "successfactors",
        "route": "html",
        "location_raw": fields.get("city") or None,
        "category_raw": fields.get("dept") or None,
        "published": None,
        "fields": fields,
    }


def iso_day(value):
    """`Thu Sep 10 02:00:00 UTC 2026` → `2026-09-10`; anything else unchanged.
    The microdata carries Java's default `Date.toString()`, not ISO 8601."""
    from datetime import datetime
    try:
        return datetime.strptime(value, "%a %b %d %H:%M:%S %Z %Y").date().isoformat()
    except (TypeError, ValueError):
        return value


def posting_of(body):
    """The `JobPosting` **microdata** block of a vacancy page — SuccessFactors
    carries no JSON-LD (0 `ld+json` blocks on `jobs.fr.ch`, 2026-09-11)."""
    from _microdata import items
    blocks = items(body, "JobPosting")
    return (blocks[0].get("props") or {}) if blocks else {}


def list_html(a, why):
    """The HTML route: tiles from `/search/`, then — with `--with-description`
    — each vacancy's own `JobPosting`. Three states, not two (#202):
    `n` tiles → cards; **no tile at all → INDETERMINATE, exit 8**, because on
    this route a shell with no tile and a board with nothing open look the
    same to a plain client — and `/services/`, which would have told them
    apart, is refused; the page's own «0 offres» → a real zero."""
    host = a.host
    seen, kept, total, page = set(), 0, None, 0
    rows_read, per_page = 0, []
    for page in range(a.pages):
        q = urllib.parse.urlencode({"q": a.keywords or "", "startrow": page * ROWS})
        status, body = get(f"https://{host}{SEARCH}?{q}")
        if status != 200:
            die(f"{host}{SEARCH} answered HTTP {status} on page {page + 1}", code=4)
        if total is None:
            total = stated_total(body)
        found = tiles(body)
        if not found:
            break
        rows_read += len(found)
        per_page.append(len(found))
        for jid, path, title, fields in found:
            if jid in seen:
                continue
            seen.add(jid)
            out = card_html(host, jid, path, title, fields)
            if a.with_description:
                gate_path(f"https://{host}{path}")      # the exact URL, every time
                st, ad, _ = get_with_url(f"https://{host}{path}")
                props = posting_of(ad) if st == 200 else {}
                out["description"] = (to_text(props.get("description") or "")[:20000]
                                      if props else "")
                out["published"] = iso_day(props.get("datePosted"))
                out["valid_through"] = iso_day(props.get("validThrough"))
            print(json.dumps(out, ensure_ascii=False))
            kept += 1
        if len(found) < ROWS:
            break
    anchor = (f"page states {total}" if total is not None
              else "page states no total")
    if kept == 0:
        if total == 0:
            print(f"[successfactors:{host}] route html — 0 tiles, and the page "
                  f"itself states 0 offers: a real zero for this query.",
                  file=sys.stderr)
            return
        # **The state that was missing** — the false zero of #181 and #202.
        die(f"[successfactors:{host}] route html — {SEARCH} returned no job "
            f"tile ({anchor}). **This is NOT an empty board and NOT a zero**: "
            f"this tenant does not serve its list to a plain client (measured "
            f"on `jobs.bcv.ch`: a 66 kB shell, 0 `/job/` links), and "
            f"`{API}`, which would have listed it, is refused by its rules. "
            f"INDETERMINATE — a browser route for this tenant is to be "
            f"documented, not a count.", code=8)
    # **`rows_read` beside `kept`, and the pages** — a tile seen on two pages
    # is dropped by `seen`, and without this line the drop is invisible: on
    # `jobs.fr.ch` three pages of 25 emitted 73, and only this said why.
    note = (f"[successfactors:{host}] route html — {kept} emitted, {anchor}; "
            f"{rows_read} tiles read on {len(per_page)} page(s) "
            f"({'+'.join(map(str, per_page))}), {rows_read - kept} repeated "
            f"across pages")
    if total is not None and kept < total:
        note += (f" — {total - kept} short" if page + 1 >= a.pages
                 else f" — {total - kept} short, stopped early")
        if page + 1 >= a.pages:
            note += f"; {ROWS} per page, raise --pages to go further"
    print(note, file=sys.stderr)


# ---------------------------------------------------------------- commands --

def cmd_locale(a):
    found = discover_locale(a.host)
    if not found:
        die(f"could not read a locale off https://{a.host}/search/. Either the "
            f"host is not a SuccessFactors career site, or its page shape "
            f"changed — do not guess one: a wrong locale returns an empty "
            f"board with no error.", code=4)
    print(json.dumps({"host": a.host, "locale": found}, ensure_ascii=False))


def cmd_list(a):
    _v = robots_verdict(a.host)
    if not _v["sweep"]:
        die(f"{_v['host']}: {_v['reason']} On SuccessFactors the host belongs to the employer, so this is that employer's "
            f"answer and not the platform's. Issue #73.",
                8 if _v["sweep"] is None else 7)
    route, why = route_for(a.host)
    # **The route is printed, always** — a reader of the log must be able to
    # tell which of the two produced the rows, or refused.
    print(f"[successfactors:{a.host}] route {route or 'none'} — {why}",
          file=sys.stderr)
    if route is None:
        die(f"{a.host}: {why}. On SuccessFactors the host belongs to the "
            f"employer, so this is that employer's answer and not the "
            f"platform's. Issue #73, #202.",
            8 if "could not be read" in why else 7)
    if route == "html":
        return list_html(a, why)
    locale = a.locale or discover_locale(a.host)
    if not locale:
        die(f"no --locale given and none could be read off {a.host}. Run "
            f"`successfactors.py locale --host {a.host}` first; guessing it "
            f"returns an empty board with no error.", code=4)
    first = search(a.host, locale, a.keywords, 0)
    refuse_on_error(a.host, first, locale)
    total = first.get("totalJobs") or 0
    seen, kept = set(), 0
    payload = first
    for page in range(a.pages):
        if page:
            payload = search(a.host, locale, a.keywords, page)
        rows = payload.get("jobSearchResult") or []
        if not rows:
            break
        for entry in rows:
            r = entry.get("response") or {}
            jid = str(r.get("id"))
            if jid in seen:
                continue
            seen.add(jid)
            out = card(a.host, locale, r)
            if a.with_description:
                status, body, _ = read_ad(a.host, locale, jid,
                                          r.get("unifiedUrlTitle") or "")
                m = DESC_RE.search(body) if status == 200 else None
                out["description"] = to_text(m.group(1))[:20000] if m else ""
            print(json.dumps(out, ensure_ascii=False))
            kept += 1
    note = f"[successfactors:{a.host}] route api — {kept} of {total} postings, locale {locale}"
    if kept < total:
        note += f" — {PAGE} per page; raise --pages to go further"
    print(note, file=sys.stderr)
    if total == 0:
        print(f"[successfactors:{a.host}] zero postings, and the service "
              f"answered without an error. With the locale confirmed, that is a "
              f"real zero for this query — not a silent failure.", file=sys.stderr)


CONTROL_ID = "99999999"   # an id no tenant will have issued


def verdict_for(host, locale, jid):
    """Compare the page against a deliberately invented id on the same tenant.

    v1.9.0 recorded that a live and a non-existent requisition BOTH answer 200,
    and that the difference is an empty job-title slot in <title>. What it does
    not say — and what a first attempt gets wrong — is that the empty slot still
    carries the tenant's localised chrome: ` Détails du poste | BCV`. Testing
    that the text before the separator is non-empty therefore passes an invented
    id. The chrome phrase is per-tenant and per-locale, so it cannot be matched
    either.

    One control request settles it without knowing any of that: fetch an id that
    cannot exist, and compare. Same title -> this requisition does not resolve.
    """
    status, body, landed = read_ad(host, locale, jid)
    if status != 200:
        return "unverified", f"HTTP {status}", "", body
    title = page_title(body)

    # **The tell is the `JobPosting` block, not the title.** Measured on two
    # tenants: a live vacancy carries exactly one `itemtype="…JobPosting"`
    # (79 854 B on SICPA), an id that does not resolve carries none (42 956 B,
    # and it redirects to the portal's error page). The block is binary; the
    # title is not — BCV returns its chrome with an empty slot while SICPA
    # returns `Jobs at SICPA`, **so a test on the shape of the title is
    # tenant-specific and this one is not.** SuccessFactors joins Refline in
    # `shared/ats-open-check.md`'s "the tell is a JobPosting block" category.
    if POSTING_RE.search(body):
        return ("open",
                "HTTP 200 and the page carries a JobPosting block — the "
                "advert is being served",
                title, body)
    if ERROR_PATH in landed:
        return ("unverified",
                f"HTTP 200 after a redirect to {landed} — the id does not "
                f"resolve on this tenant. NOT proof it closed: a genuinely "
                f"closed requisition has never been observed on this ATS",
                title, body)

    # No block and no error redirect: fall back to the control comparison,
    # which is what carried this check before the block was measured.
    _, control_body, _ = read_ad(host, locale, CONTROL_ID)
    control = page_title(control_body)
    if control and title.strip() == control.strip():
        return ("unverified",
                "HTTP 200, but the page is identical to the one a deliberately "
                "invented id returns — the requisition does not resolve. NOT "
                "proof it closed: a genuinely closed requisition has never been "
                "observed on this ATS",
                title, body)
    return ("unverified",
            "HTTP 200, no JobPosting block, and the page differs from the "
            "invented-id control — this is neither a served advert nor a "
            "recognised absence. Read the page before concluding anything",
            title, body)


def clean_title(raw, description):
    """Strip the localised chrome the <title> appends after the job title.

    The page title reads `<Job Title> Détails du poste | <Employer>` on a French
    tenant and will read something else on any other — the suffix is not a
    constant to match. The description opens with the job title verbatim, so the
    longest prefix of the title that the description also starts with is the
    title, whatever language the tenant runs in.
    """
    head = raw.split(" | ")[0].strip()
    if not description:
        return head
    words, best = head.split(), head
    for i in range(len(words), 0, -1):
        candidate = " ".join(words[:i])
        if description.startswith(candidate):
            best = candidate
            break
    return best


def cmd_ad(a):
    _v = robots_verdict(a.host)
    if not _v["sweep"]:
        die(f"{_v['host']}: {_v['reason']} On SuccessFactors the host belongs to the employer, so this is that employer's "
            f"answer and not the platform's — and it refuses the content, not just the sweep. Issue #73.",
                8 if _v["sweep"] is None else 7)
    locale = a.locale or discover_locale(a.host) or die(
        f"no locale for {a.host}; run `successfactors.py locale --host {a.host}`",
        code=4)
    verdict, why, title, body = verdict_for(a.host, locale, a.id)
    if verdict != "open":
        die(f"requisition {a.id} on {a.host}: {why}", code=3)
    m = DESC_RE.search(body)
    description = to_text(m.group(1))[:20000] if m else ""
    print(json.dumps({
        "id": a.id,
        "ledger_id": f"successfactors:{a.host}:{a.id}",
        "url": f"https://{a.host}/job/x/{a.id}-{locale}",
        "title": clean_title(title, description),
        "title_raw": title,
        "host": a.host, "locale": locale, "provider": "successfactors",
        "description": description,
    }, ensure_ascii=False, indent=1))


def cmd_check(a):
    _v = robots_verdict(a.host)
    if not _v["sweep"]:
        die(f"{_v['host']}: {_v['reason']} On SuccessFactors the host belongs to the employer, so this is that employer's "
            f"answer and not the platform's — and it refuses the content, not just the sweep. Issue #73.",
                8 if _v["sweep"] is None else 7)
    locale = a.locale or discover_locale(a.host) or die(
        f"no locale for {a.host}", code=4)
    verdict, why, title, _ = verdict_for(a.host, locale, a.id)
    print(json.dumps({"id": a.id, "host": a.host, "locale": locale,
                      "verdict": verdict, "why": why, "title": title,
                      "url": f"https://{a.host}/job/x/{a.id}-{locale}"},
                     ensure_ascii=False))
    sys.exit(0 if verdict == "open" else 1)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def host_arg(sp):
        sp.add_argument("--host", required=True,
                        help="the employer's career-site domain, e.g. jobs.bcv.ch")
        sp.add_argument("--locale", help="e.g. fr_FR. Read off the site when "
                                         "omitted; NEVER guess it")

    lo = sub.add_parser("locale", help="read the tenant's locale off its site")
    lo.add_argument("--host", required=True)
    lo.set_defaults(fn=cmd_locale)

    li = sub.add_parser("list", help="list this employer's postings")
    host_arg(li)
    li.add_argument("--keywords", help="free text, matched by the service")
    li.add_argument("--pages", type=int, default=3,
                    help=f"pages to read, {PAGE} postings each. Default 3")
    li.add_argument("--with-description", action="store_true",
                    help="costs one extra request per posting")
    li.set_defaults(fn=cmd_list)

    ad = sub.add_parser("ad", help="read one posting in full")
    host_arg(ad)
    ad.add_argument("--id", required=True, help="the requisition id, e.g. 31130")
    ad.set_defaults(fn=cmd_ad)

    ck = sub.add_parser("check", help="is this posting still open? (step 1b)")
    host_arg(ck)
    ck.add_argument("--id", required=True)
    ck.set_defaults(fn=cmd_check)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
