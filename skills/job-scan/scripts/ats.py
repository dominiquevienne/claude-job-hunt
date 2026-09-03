#!/usr/bin/env python3
"""Read one employer's job board directly from its ATS.

Greenhouse, Lever, Ashby and SmartRecruiters each publish the postings of a
given employer as public JSON — the same feed that powers that employer's
careers page. No key, no cookie, no browser. What they do NOT offer is a search
across employers: you ask for one tenant at a time, which is why this is the
adapter family for "I want to work at X", not for discovery.

SmartRecruiters is the odd one of the four: it paginates (100 per page, silently
clamped), it needs a second request per ad for the description, and it is the
only one with server-side filters — see --country.

**join.com is the odd one of the seven.** It publishes no JSON feed at all — it
is a Next.js app, and the whole payload rides in the page's own `__NEXT_DATA__`,
which is a complete state object rather than markup to scrape. It is also the
only provider here that hands the description over **already cut into `intro`,
`tasks`, `requirements`, `benefits` and `outro`** — `requirements` on its own is
what the scoring rubric actually reads. And it is the only one whose money is
stored in **minor units**: `2035` means `20.35`. See `join_money`.

Usage:
  ats.py list --provider greenhouse --tenant elastic [--location Switzerland]
              [--keywords kubernetes] [--posted-within-days 30] [--remote]
  ats.py list --provider smartrecruiters --tenant nexthink --country ch
  ats.py list --provider join --tenant simplee-energy --with-description
  ats.py ad   --provider greenhouse --tenant elastic --id 8148720
  ats.py resolve "Nexthink"        # employer name -> provider + tenant

`resolve` asks HiringCafe, which records the ATS and tenant of every ad it
indexes. It is a lookup aid for setup, not a sweep.
"""

import argparse
import html
import json
import re

from _decode import decode_body
from _ldjson import one
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from _robots import verdict as robots_verdict

UA = "Mozilla/5.0 (compatible; claude-job-hunt/1.x; +personal job search)"
PROVIDERS = ("greenhouse", "lever", "ashby", "smartrecruiters", "workable",
             "teamtailor", "join")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def fetch(url):
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60)
        return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        die(f"{url} returned HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach {urllib.parse.urlparse(url).netloc}: {e}")


def to_text(markup):
    if not markup:
        return ""
    # Greenhouse double-encodes: the JSON string holds "&lt;div&gt;…", so the
    # entities must be resolved BEFORE the tags can be stripped.
    txt = html.unescape(markup)
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", txt)
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", txt)
    txt = re.sub(r"(?i)<li[^>]*>", "- ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", txt).strip()


def fold(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()


# --------------------------------------------------------------- providers --

def greenhouse_list(tenant, want_content, _a=None):
    q = "?content=true" if want_content else ""
    d = fetch(f"https://boards-api.greenhouse.io/v1/boards/{tenant}/jobs{q}")
    if d is None:
        die(f"Greenhouse has no board called {tenant!r} (HTTP 404). Check the "
            "token with: ats.py resolve \"<employer name>\"", code=4)
    return d.get("jobs") or []


def greenhouse_card(tenant, j, with_description=False):
    out = {
        "id": str(j.get("id")),
        "ledger_id": f"greenhouse:{tenant}:{j.get('id')}",
        # absolute_url points at the employer's own careers domain and carries a
        # duplicated gh_jid query. This canonical form redirects to it.
        "url": f"https://job-boards.greenhouse.io/{tenant}/jobs/{j.get('id')}",
        "apply_url": f"https://job-boards.greenhouse.io/{tenant}/jobs/{j.get('id')}#app",
        "title": j.get("title"),
        "company": j.get("company_name") or tenant,
        "tenant": tenant,
        "provider": "greenhouse",
        "location": (j.get("location") or {}).get("name"),
        "published": j.get("first_published") or j.get("updated_at"),
        "updated": j.get("updated_at"),
        "department": ", ".join(d.get("name", "") for d in (j.get("departments") or [])) or None,
        "employment_type": None,
        "remote": None,
    }
    if with_description:
        out["description"] = to_text(j.get("content"))
    return out


def lever_list(tenant, _want_content=True, _a=None):
    """Lever's US and EU hosts are disjoint — a tenant lives on exactly one."""
    for host in ("api.lever.co", "api.eu.lever.co"):
        d = fetch(f"https://{host}/v0/postings/{tenant}?mode=json")
        if d is not None:
            return d
    die(f"Lever has no board called {tenant!r} on either host (both 404). "
        "Check the token with: ats.py resolve \"<employer name>\"", code=4)


def lever_card(tenant, j, with_description=False):
    cat = j.get("categories") or {}
    created = j.get("createdAt")
    published = None
    if created:
        published = datetime.fromtimestamp(created / 1000, timezone.utc).isoformat()
    locations = [cat.get("location")] + list(cat.get("allLocations") or [])
    out = {
        "id": j.get("id"),
        "ledger_id": f"lever:{tenant}:{j.get('id')}",
        "url": j.get("hostedUrl"),
        "apply_url": j.get("applyUrl"),
        "title": j.get("text"),
        "company": tenant,
        "tenant": tenant,
        "provider": "lever",
        "location": " / ".join(dict.fromkeys(x for x in locations if x)) or None,
        "published": published,
        "updated": published,
        "department": cat.get("department"),
        "employment_type": cat.get("commitment"),
        "remote": (j.get("workplaceType") or "").lower() == "remote" or None,
    }
    if with_description:
        # **`descriptionPlain` is the intro, not the posting.** Lever splits an
        # ad across three top-level fields and the adapter read one of them:
        #
        #   description / descriptionPlain   the company blurb and the intro
        #   lists[] {text, content}          every real section
        #   additional / additionalPlain     the closing boilerplate
        #
        # Measured on sonarsource/8490348a, 2026-09-01: 2 435 characters came
        # back and 2 608 more sat in three `lists` sections — *What you will
        # do*, *Experience and qualifications* (six bullets), *Additional
        # comments* — plus 985 in `additional`.
        #
        # **The dropped half is the one the rubric reads.** From the intro the
        # role scored ~60% as a generic engineering-manager post; with its
        # stated qualifications it is an SRE/Cloud Operations role and scores
        # 52% with a hard zero on a must-have. The two numbers describe
        # different jobs, and nothing in the response looked wrong: a valid,
        # self-consistent 200 answering a question nobody asked. Issue #54.
        parts, sections = [], []
        intro = j.get("descriptionPlain") or to_text(j.get("description"))
        if intro:
            parts.append(intro)
        for block in (j.get("lists") or []):
            head = (block.get("text") or "").strip()
            body = to_text(block.get("content"))
            if not body:
                continue
            sections.append(head or "(untitled section)")
            parts.append(f"{head}\n{body}" if head else body)
        closing = j.get("additionalPlain") or to_text(j.get("additional"))
        if closing:
            sections.append("(additional)")
            parts.append(closing)
        out["description"] = "\n\n".join(parts) or None
        # The count carries the caveat: a posting with no sections either has
        # none, or is being read the old way again (#67 — put it in the field,
        # not in prose somebody skips).
        out["description_sections"] = sections
    return out


def ashby_list(tenant, _want_content=True, _a=None):
    d = fetch(f"https://api.ashbyhq.com/posting-api/job-board/{tenant}"
              "?includeCompensation=true")
    if d is None:
        die(f"Ashby has no job board called {tenant!r} (HTTP 404). Check the "
            "token with: ats.py resolve \"<employer name>\"", code=4)
    # isListed=false means the employer pulled it from the public board.
    return [j for j in (d.get("jobs") or []) if j.get("isListed", True)]


def ashby_card(tenant, j, with_description=False):
    locations = [j.get("location")] + [s.get("location") for s in
                                       (j.get("secondaryLocations") or [])]
    out = {
        "id": j.get("id"),
        "ledger_id": f"ashby:{tenant}:{j.get('id')}",
        "url": j.get("jobUrl"),
        "apply_url": j.get("applyUrl"),
        "title": j.get("title"),
        "company": tenant,
        "tenant": tenant,
        "provider": "ashby",
        "location": " / ".join(dict.fromkeys(x for x in locations if x)) or None,
        "published": j.get("publishedAt"),
        "updated": j.get("publishedAt"),
        "department": j.get("department") or j.get("team"),
        "employment_type": j.get("employmentType"),
        "remote": j.get("isRemote"),
    }
    if with_description:
        out["description"] = (j.get("descriptionPlain")
                              or to_text(j.get("descriptionHtml")))
    return out


SR_API = "https://api.smartrecruiters.com/v1/companies"
SR_PAGE = 100        # asking for more is silently clamped, never refused
SR_MAX_PAGES = 30    # 3000 postings; boards this large need --country anyway


def smartrecruiters_list(tenant, _want_content=True, a=None):
    """Paginate the public postings feed. The description is NOT in here."""
    params = {"limit": SR_PAGE}
    # The only server-side filters in this family. country is a LOWERCASE ISO-2
    # code; an unknown one returns zero with HTTP 200, like an empty board.
    if a is not None and getattr(a, "country", None):
        params["country"] = a.country.lower()
    out, total = [], None
    for page in range(SR_MAX_PAGES):
        params["offset"] = page * SR_PAGE
        d = fetch(f"{SR_API}/{tenant}/postings?" + urllib.parse.urlencode(params))
        if d is None:                      # never observed; the API answers 200
            die(f"SmartRecruiters refused the board {tenant!r}", code=4)
        if total is None:
            total = d.get("totalFound") or 0
            if not total:
                # THE trap: a wrong tenant and an employer with nothing open are
                # the same response. There is no endpoint that separates them —
                # /v1/companies/<t> is 404 for valid tenants too, and the careers
                # page answers 200 for anything.
                die(f"SmartRecruiters returned zero postings for {tenant!r} "
                    f"(HTTP 200, totalFound 0). This is EITHER a wrong tenant "
                    f"OR an employer with nothing open — the API cannot tell "
                    f"you which, and neither can their careers page. Confirm "
                    f"the token with: ats.py resolve \"<employer name>\"",
                    code=4)
        batch = d.get("content") or []
        out.extend(batch)
        if len(out) >= total or len(batch) < SR_PAGE:
            break
    if total and len(out) < total:
        print(f"[smartrecruiters:{tenant}] read {len(out)} of {total} postings "
              f"— this board is larger than {SR_MAX_PAGES} pages. Narrow it "
              f"with --country before concluding anything about coverage.",
              file=sys.stderr)
    return out


def smartrecruiters_card(tenant, j, with_description=False):
    loc = j.get("location") or {}
    # The API path is case-insensitive, but the public URL uses the employer's
    # canonical capitalisation ("Nexthink", "SGS"). Take it from the payload
    # rather than echoing whatever the user typed.
    ident = (j.get("company") or {}).get("identifier") or tenant
    pid = str(j.get("id"))
    out = {
        "id": pid,
        "ledger_id": f"smartrecruiters:{tenant.lower()}:{pid}",
        "url": f"https://jobs.smartrecruiters.com/{ident}/{pid}",
        "apply_url": f"https://jobs.smartrecruiters.com/{ident}/{pid}",
        "title": j.get("name"),
        "company": (j.get("company") or {}).get("name") or tenant,
        "tenant": tenant.lower(),
        "provider": "smartrecruiters",
        "location": loc.get("fullLocation") or ", ".join(
            x for x in (loc.get("city"), loc.get("region"),
                        (loc.get("country") or "").upper()) if x) or None,
        "published": j.get("releasedDate"),
        "updated": j.get("releasedDate"),
        "department": (j.get("department") or {}).get("label"),
        "employment_type": (j.get("typeOfEmployment") or {}).get("label"),
        "remote": loc.get("remote"),
        "hybrid": loc.get("hybrid"),
        "ref": j.get("refNumber"),
    }
    if with_description:
        d = fetch(f"{SR_API}/{tenant}/postings/{pid}")
        if d is None:
            out["description"] = ""
        else:
            out["url"] = d.get("postingUrl") or out["url"]
            out["apply_url"] = d.get("applyUrl") or out["apply_url"]
            out["active"] = d.get("active")
            # The ad is split across sections, and `qualifications` — the
            # must-haves the scoring needs most — is NOT in `jobDescription`.
            # Iterate whatever sections exist; some boards add `videos`.
            sections = ((d.get("jobAd") or {}).get("sections") or {})
            parts = []
            for key in ("companyDescription", "jobDescription", "qualifications",
                        "additionalInformation"):
                txt = to_text((sections.get(key) or {}).get("text"))
                if txt:
                    parts.append(txt)
            for key, val in sections.items():
                if key in ("companyDescription", "jobDescription",
                           "qualifications", "additionalInformation"):
                    continue
                txt = to_text((val or {}).get("text"))
                if txt:
                    parts.append(txt)
            out["description"] = "\n\n".join(parts)
    return out


def workable_list(tenant, want_content, _a=None):
    # `details=true` returns the full description with the listing, so the whole
    # board — text included — is one request. Without it the same call returns
    # the same jobs with no description at all.
    q = "?details=true" if want_content else ""
    d = fetch(f"https://apply.workable.com/api/v1/widget/accounts/{tenant}{q}")
    if d is None:
        die(f"Workable has no account called {tenant!r} (HTTP 404). "
            f"If that tenant came from `ats.py resolve`, do not simply run it "
            f"again: resolve reads HiringCafe's `ats_tenant`, and HiringCafe "
            f"sometimes records a label rather than the slug Workable "
            f"answers to — 'inspired_thinking_group_(itg)' 404s here both raw "
            f"and percent-encoded, measured 2026-09-02. Take the slug from "
            f"the employer's own apply.workable.com URL instead.", code=4)
    jobs = d.get("jobs") or []
    for j in jobs:
        # The employer's real name lives on the account, not on the job. Carry
        # it down so the card does not have to fall back to the tenant slug.
        j["_account_name"] = d.get("name")
        # Workable calls the identifier `shortcode`; every other provider here
        # calls it `id`, and `cmd_ad` looks one ad up by that name across all of
        # them. Without this alias `ats.py ad` reports a live posting as pulled.
        j.setdefault("id", j.get("shortcode"))
    return jobs


def workable_card(tenant, j, with_description=False):
    locs = j.get("locations") or []
    # `city` is empty on most remote ads; `locations[]` is the reliable one.
    where = [x for x in (j.get("city"), j.get("state"), j.get("country")) if x]
    if not where and locs:
        first = locs[0]
        where = [x for x in (first.get("city"), first.get("region"),
                             first.get("country")) if x]
    remote = bool(j.get("telecommuting"))
    out = {
        "id": j.get("shortcode"),
        "ledger_id": f"workable:{tenant}:{j.get('shortcode')}",
        "url": j.get("shortlink") or j.get("url"),
        "apply_url": j.get("application_url") or j.get("shortlink"),
        "title": j.get("title"),
        "company": j.get("_account_name") or tenant,
        "tenant": tenant,
        "provider": "workable",
        "location": ", ".join(where) or None,
        # `published_on` is when the ad went live; `created_at` is when it was
        # drafted. They differ by weeks on republished ads, and reading the
        # wrong one is how a fresh vacancy gets scored as stale — measured at
        # six weeks apart on a live posting (created 2026-07-13, published
        # 2026-08-24). `published` is the one that answers "how old is this ad".
        "published": j.get("published_on"),
        "created": j.get("created_at"),
        "updated": None,
        "department": j.get("department") or j.get("function"),
        "employment_type": j.get("employment_type"),
        "remote": remote,
    }
    # A remote ad on Workable is very often remote *within one country only*.
    # The countries are the ad's real eligibility rule — schema.org calls this
    # applicantLocationRequirements — and taking "remote" at face value without
    # them produces a perfect-looking match nobody is allowed to take.
    if remote:
        codes = [x.get("countryCode") for x in locs if x.get("countryCode")]
        names = [x.get("country") for x in locs if x.get("country")]
        if codes or names:
            out["remote_countries"] = codes or None
            out["remote_country_names"] = names or None
    if with_description:
        out["description"] = to_text(j.get("description"))
    return out


def teamtailor_list(tenant, _want_content=True, _a=None):
    # **The policy belongs to the tenant, not to the platform.** Teamtailor
    # gives every customer its own hostname, and they do not answer the same:
    # measured 2026-09-02, investengine and oatly publish
    # `Content-Signal: search=yes, ai-train=no, ai-input=yes` while polestar
    # and normative publish `search=no, ai-train=no, ai-input=no`. This file
    # swept polestar earlier the same day, before anything read its robots.txt
    # — no script in this repository did. See `_robots.py`.
    v = robots_verdict(f"{tenant}.teamtailor.com")
    if not v["sweep"]:
        die(f"{tenant}.teamtailor.com: {v['reason']} Teamtailor lets each "
            f"customer set this, so it is this employer's answer and not the "
            f"platform's.", code=8 if v["sweep"] is None else 7)
    # `<tenant>.teamtailor.com`, NOT the employer's own `careers.<company>.com`
    # vanity host, even though both answer this path. They do not serve the same
    # board: measured on one tenant the same day, the vanity domain was missing
    # every ad published after 13 July and still carried five the platform had
    # dropped — 8 ads on one side, 5 on the other, only 8 of 16 in common. The
    # platform host is the live one; the vanity is a stale mirror.
    d = fetch(f"https://{tenant}.teamtailor.com/jobs.json")
    if d is None:
        die(f"Teamtailor has no board called {tenant!r} (HTTP 404). The tenant "
            "is the subdomain in <tenant>.teamtailor.com — read it off the "
            "employer's careers page.", code=4)
    items = d.get("items") or []
    for i in items:
        i["_feed_title"] = d.get("title")
        # The numeric ad id lives in `_jobposting.identifier.value`; the item's
        # own `id` is a UUID that appears nowhere in any URL, so it cannot be
        # pasted back into a browser. Fall back to the slug when the JobPosting
        # block is absent.
        jp = i.get("_jobposting") or {}
        ident = one(jp.get("identifier")).get("value")
        if ident is None:
            m = re.search(r"/jobs/(\d+)-", i.get("url") or "")
            ident = m.group(1) if m else i.get("id")
        i["id"] = str(ident)
    return items


def teamtailor_card(tenant, j, with_description=False):
    jp = j.get("_jobposting") or {}
    place = (jp.get("jobLocation") or [{}])
    addr = (place[0].get("address") if place else {}) or {}
    where = [addr.get("addressLocality"), addr.get("addressCountry")]
    out = {
        "id": j.get("id"),
        "ledger_id": f"teamtailor:{tenant}:{j.get('id')}",
        "url": j.get("url"),
        # Teamtailor hosts the form on the ad itself; there is no separate
        # apply endpoint to link to.
        "apply_url": j.get("url"),
        "title": j.get("title"),
        "company": one(jp.get("hiringOrganization")).get("name")
                   or j.get("_feed_title") or tenant,
        "tenant": tenant,
        "provider": "teamtailor",
        "location": ", ".join(x for x in where if x) or None,
        "published": j.get("date_published") or jp.get("datePosted"),
        "updated": None,
        "department": None,
        # Measured absent on 16 of 16 ads: Teamtailor's feed publishes no
        # employment type, no salary, no validThrough and no remote flag.
        # Reported as None rather than guessed from the description.
        "employment_type": None,
        "remote": None,
    }
    if addr.get("postalCode") or addr.get("streetAddress"):
        # The employer's postal address, which the job-room-ch module records as
        # the field that goes missing most often. Present on 13 of 16 measured.
        out["address"] = {k: v for k, v in (
            ("street", addr.get("streetAddress")),
            ("postal_code", addr.get("postalCode")),
            ("locality", addr.get("addressLocality")),
            ("region", addr.get("addressRegion")),
            ("country", addr.get("addressCountry"))) if v}
    if with_description:
        out["description"] = to_text(j.get("content_html") or jp.get("description"))
    return out


# ---------------------------------------------------------------- join.com --

JOIN = "https://join.com/companies/{}"
NEXT_DATA_RE = re.compile(r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


def join_state(url):
    """The page's own React state, which is a complete JSON payload.

    join.com is a Next.js app that ships `__NEXT_DATA__` in the HTML, so no
    scraping is involved: the tenant page carries `initialState.jobs` with its
    items, its pagination and its aggregations, and an ad page carries
    `initialState.job` in full. Returns None on 404 — an ad that was pulled.
    """
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            url, headers={"User-Agent": UA, "Accept": "text/html"}), timeout=60)
        page = decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return None
        die(f"{url} returned HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach join.com: {e}")
    m = NEXT_DATA_RE.search(page)
    if not m:
        die("join.com served a page with no __NEXT_DATA__ — the app changed "
            "shape, or this is a Cloudflare interstitial. Report it with the "
            "board-request skill rather than parsing the HTML.", code=2)
    return json.loads(m.group(1))["props"]["pageProps"]["initialState"]


def join_money(amount):
    """`{"currency": "CHF", "amount": 2035}` is **CHF 20.35**, not 2 035.

    join.com stores money in **minor units**. The board renders that ad as
    *"CHF 20.35 bis CHF 25.25 / Stunde"* and its own JSON-LD writes
    `minValue: 20.35`, so the factor of 100 is not a guess — it is confirmed
    twice on the same page.

    Reading the integer raw turns an hourly rate of CHF 20.35 into CHF 2 035,
    which is not an implausible number: it reads as a monthly salary, so it
    would pass every sanity check a human applies to a pay figure. This is the
    single most dangerous field on the board.
    """
    if not isinstance(amount, dict) or amount.get("amount") is None:
        return None
    return {"currency": amount.get("currency"),
            "amount": round(amount["amount"] / 100, 2)}


def join_list(tenant, _want_content=True, _a=None):
    st = join_state(JOIN.format(urllib.parse.quote(tenant)))
    if st is None:
        die(f"join.com has no company page called {tenant!r} (HTTP 404). The "
            "tenant is the slug in join.com/companies/<tenant>, read off the "
            "ad URL — join.com publishes no directory of them.", code=4)
    company = st.get("company") or {}
    jobs, seen = [], set()
    page = st.get("jobs") or {}
    pages = int((page.get("pagination") or {}).get("pageCount") or 1)
    for n in range(1, pages + 1):
        if n > 1:
            nxt = join_state(f"{JOIN.format(urllib.parse.quote(tenant))}?page={n}")
            page = (nxt or {}).get("jobs") or {}
        items = page.get("items") or []
        # **A page past the end repeats the last one.** Measured on an 8-ad
        # tenant with pageCount 2: `?page=3` answered with page 2's two ads
        # again, while `?page=99` answered `page: 98` and no items at all. The
        # loop is bounded by pageCount for that reason, and still dedupes.
        fresh = [i for i in items if i.get("id") not in seen]
        if not fresh:
            break
        seen.update(i["id"] for i in fresh)
        for i in fresh:
            i["_company"] = company
        jobs.extend(fresh)
    return jobs


def join_card(tenant, j, with_description=False):
    company = j.get("_company") or j.get("company") or {}
    city = j.get("city") or {}
    office = j.get("office") or {}
    ocity = office.get("city") or {}
    idp = j.get("idParam") or j.get("id")
    where = [city.get("cityName") or ocity.get("cityName"),
             city.get("countryName") or ocity.get("countryName")]
    url = f"{JOIN.format(urllib.parse.quote(tenant))}/{idp}"
    workplace = j.get("workplaceType")
    out = {
        "id": str(j.get("id")),
        "ledger_id": f"join:{tenant}:{j.get('id')}",
        "url": url,
        # join.com hosts the form on the ad itself.
        "apply_url": url,
        "title": j.get("title"),
        # **The employer's own name, not an inference.** HiringCafe indexes
        # join.com heavily and labels how it got the name — `llm_pick`,
        # `single_deterministic`. On 11 Swiss tenants the two disagreed 5 times,
        # once badly: HiringCafe said "Smile Fahrlehrerausbildung AG" where the
        # tenant's own record says "wab kurs". Neither is authoritative for a
        # human, but only one of them is what the employer wrote.
        "company": company.get("name") or tenant,
        "tenant": tenant,
        "provider": "join",
        "location": ", ".join(x for x in where if x) or None,
        "published": j.get("createdAt"),
        "updated": j.get("updatedAt"),
        "department": (j.get("category") or {}).get("name"),
        "employment_type": one(j.get("employmentType")).get("name"),
        "workplace_type": workplace,
        "remote": workplace == "REMOTE",
        # The ad's own language, which cover-letter needs before it writes a
        # line — this board is DACH-first and mixes de/fr/en on one tenant.
        "language": (j.get("language") or {}).get("locale"),
    }
    if office.get("postalCode") or ocity.get("cityName"):
        out["address"] = {k: v for k, v in (
            ("postal_code", office.get("postalCode")),
            ("locality", ocity.get("cityName")),
            ("region", ocity.get("regionName")),
            ("country", ocity.get("countryName"))) if v}
    if ocity.get("lat") or company.get("lat"):
        out["coordinates"] = {"lat": ocity.get("lat") or company.get("lat"),
                              "lng": ocity.get("lng") or company.get("lng")}
    lo, hi = join_money(j.get("salaryAmountFrom")), join_money(j.get("salaryAmountTo"))
    if lo or hi:
        out["salary"] = {"from": lo, "to": hi, "period": j.get("salaryFrequency")}
    elif (j.get("settings") or {}).get("showSalary"):
        # `showSalary: true` with nothing to show, on 14 of the 15 ads that set
        # it. The flag is the employer's *intent*, not a promise of a figure —
        # never report a salary because it is true.
        out["salary"] = None
        out["salary_flag_without_amount"] = True
    if j.get("contactName") or j.get("contactEmail"):
        # Published in the clear by the employer, on the public ad, for
        # candidates to use. Nothing is de-obfuscated to get it.
        out["contact"] = {k: v for k, v in (("name", j.get("contactName")),
                                            ("email", j.get("contactEmail"))) if v}
    if with_description:
        full = join_state(url)
        job = (full or {}).get("job") or {}
        if job:
            out["status"] = job.get("status")
            out["language"] = (job.get("language") or {}).get("locale") \
                or out.get("language")
            # **The description arrives already cut into its parts.** No other
            # provider here does this: `requirements` is the must-have list on
            # its own, which is exactly what the scoring rubric reads and what
            # every other adapter has to dig out of one prose blob.
            for src, dst in (("intro", "intro"), ("tasks", "tasks"),
                             ("requirements", "requirements"),
                             ("benefits", "benefits"), ("outro", "outro")):
                if job.get(src):
                    out[dst] = job[src]
            out["description"] = job.get("description") or to_text(
                job.get("schemaDescription"))
            for extra in ("contactName", "contactEmail"):
                if job.get(extra):
                    out.setdefault("contact", {})[
                        "name" if extra == "contactName" else "email"] = job[extra]
            lo = join_money(job.get("salaryAmountFrom"))
            hi = join_money(job.get("salaryAmountTo"))
            if lo or hi:
                out["salary"] = {"from": lo, "to": hi,
                                 "period": job.get("salaryFrequency")}
                out.pop("salary_flag_without_amount", None)
    return out


LISTERS = {"greenhouse": greenhouse_list, "lever": lever_list,
           "ashby": ashby_list, "smartrecruiters": smartrecruiters_list,
           "workable": workable_list, "teamtailor": teamtailor_list,
           "join": join_list}
CARDERS = {"greenhouse": greenhouse_card, "lever": lever_card,
           "ashby": ashby_card, "smartrecruiters": smartrecruiters_card,
           "workable": workable_card, "teamtailor": teamtailor_card,
           "join": join_card}


# ----------------------------------------------------------------- filters --

def keep(card, a):
    """Filter locally. Only SmartRecruiters offers a server-side filter
    (--country); everything else is applied here, after the fetch."""
    if a.location:
        hay = fold(card.get("location"))
        if not any(fold(x) in hay for x in a.location):
            if not (a.remote_counts_everywhere and card.get("remote")):
                return False
    if a.keywords:
        hay = fold(card.get("title"))
        if not all(fold(k) in hay for k in a.keywords):
            return False
    if a.remote and not card.get("remote"):
        return False
    if a.posted_within_days and card.get("published"):
        try:
            d = datetime.fromisoformat(card["published"].replace("Z", "+00:00"))
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            if d < datetime.now(timezone.utc) - timedelta(days=a.posted_within_days):
                return False
        except ValueError:
            pass  # an unparseable date is kept, never silently dropped
    return True


# ---------------------------------------------------------------- commands --

def cmd_list(a):
    jobs = LISTERS[a.provider](a.tenant, True, a)
    carder = CARDERS[a.provider]
    kept = 0
    for j in jobs:
        card = carder(a.tenant, j, with_description=a.with_description)
        if keep(card, a):
            print(json.dumps(card, ensure_ascii=False))
            kept += 1
    print(f"[{a.provider}:{a.tenant}] {kept} of {len(jobs)} postings kept",
          file=sys.stderr)
    if jobs and not kept:
        print(f"[{a.provider}:{a.tenant}] the board is not empty — every posting "
              "was filtered out. Check --location against the values this "
              "employer actually uses.", file=sys.stderr)


def cmd_ad(a):
    if a.provider == "greenhouse":
        j = fetch(f"https://boards-api.greenhouse.io/v1/boards/{a.tenant}/jobs/{a.id}")
        if j is None:
            die(f"no Greenhouse posting {a.id} on board {a.tenant} — it was "
                "filled or pulled. Record it as discarded.", code=3)
    elif a.provider == "smartrecruiters":
        j = fetch(f"{SR_API}/{a.tenant}/postings/{a.id}")
        if j is None:
            die(f"no SmartRecruiters posting {a.id} on board {a.tenant} "
                "(HTTP 404) — it was filled or pulled. Record it as "
                "discarded.", code=3)
    elif a.provider == "join":
        # Fetched directly rather than looked up in the board, because **an ad
        # carries two numbers and both address it**. The item's `id` is the
        # stable identity; `idParam`'s numeric prefix is a different number
        # issued when the ad is republished — measured on one tenant as
        # `id 16257505` against `idParam 16620520-…`, three ads out of seven.
        # Either resolves, and the slug is ignored entirely: a wrong slug on a
        # right number still serves the ad. Searching the list for whichever
        # number the user pasted would report a live ad as pulled.
        st = join_state(f"{JOIN.format(urllib.parse.quote(a.tenant))}/{a.id}")
        j = (st or {}).get("job")
        if not j:
            die(f"no join.com ad {a.id} for {a.tenant} — it was filled or "
                "pulled. Record it as discarded.", code=3)
        j["_company"] = j.get("company") or {}
    else:
        j = next((x for x in LISTERS[a.provider](a.tenant, True, a)
                  if str(x.get("id")) == str(a.id)), None)
        if j is None:
            die(f"posting {a.id} is no longer on the {a.provider} board for "
                f"{a.tenant} — it was filled or pulled. Record it as "
                "discarded.", code=3)
    print(json.dumps(CARDERS[a.provider](a.tenant, j, with_description=True),
                     ensure_ascii=False, indent=1))


def cmd_resolve(a):
    """Ask HiringCafe which ATS an employer uses, and under which tenant."""
    # companyNames is the employer filter. searchQuery would search the ad text
    # instead and returns near-nothing for a company name.
    state = {"companyNames": [a.employer]}
    url = "https://hiringcafe.com/?" + urllib.parse.urlencode(
        {"searchState": json.dumps(state, separators=(",", ":"))})
    # HiringCafe throttles by 403 and the refusal is transient — issue #59.
    # `hiringcafe.py` grew a timed backoff on 2026-09-02 and this call did not,
    # which is how one board came to behave differently depending on which
    # script asked. Same site, same remedy: wait, do not retry quickly.
    raw, wait = None, 20.0
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(url, headers={"User-Agent": UA}),
                    timeout=60) as r:
                raw = decode_body(r.read(), r.headers)[0]
            break
        except urllib.error.HTTPError as e:
            if e.code not in (403, 429) and e.code < 500:
                die(f"hiringcafe answered HTTP {e.code} while resolving")
            if attempt == 3:
                die(f"hiringcafe refused three times (HTTP {e.code}) while "
                    f"resolving. It throttles by volume and the refusal "
                    f"passes; try again in a few minutes, or read the tenant "
                    f"out of the employer's own careers URL.", code=6)
            print(f"[ats] hiringcafe HTTP {e.code} — waiting {wait:.0f}s "
                  f"(attempt {attempt} of 3)", file=sys.stderr)
            time.sleep(wait)
            wait *= 2
        except Exception as e:  # noqa: BLE001
            die(f"could not reach hiringcafe to resolve the tenant: {e}")
    m = re.search(r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', raw, re.S)
    if not m:
        die("hiringcafe's page shape changed — resolve by hand instead: open "
            "the employer's careers page and read the tenant out of the URL.")
    hits = (json.loads(m.group(1))["props"]["pageProps"].get("ssrHits") or [])
    supported, other = {}, {}
    for h in hits:
        # HiringCafe's own name for each ATS. `teamtailor` and `join` were
        # missing here long after their adapters shipped, so `resolve` answered
        # "an ATS this script does not cover" about two providers it covers —
        # a wrong answer that read like a limitation.
        src = {"grnhse": "greenhouse", "lever": "lever", "eu_lever": "lever",
               "ashby": "ashby",
               "smartrecruiters": "smartrecruiters",
               "workable": "workable",
               "teamtailor": "teamtailor",
               "join": "join"}.get(h.get("source"))
        name = ((h.get("attributed_org") or {}).get("name")
                or (h.get("enriched_company_data") or {}).get("name") or "?")
        if src:
            supported.setdefault((src, h.get("board_token")), name)
        else:
            other.setdefault((h.get("source"), h.get("board_token")), name)
    for (provider, tenant), name in supported.items():
        print(json.dumps({"provider": provider, "tenant": tenant,
                          "company": name}, ensure_ascii=False))
    if supported:
        return
    if other:
        # Naming the ATS beats "not found": it tells the user why there is no
        # adapter for this employer, and it is a fact rather than a shrug.
        print(f"{a.employer!r} was found, but on an ATS this script does not "
              "cover:", file=sys.stderr)
        for (src, tenant), name in other.items():
            print(f"  {name} -> {src} / {tenant}", file=sys.stderr)
        print("Give cover-letter one of their ad URLs — it needs no adapter.",
              file=sys.stderr)
        sys.exit(1)
    print(f"No board found for {a.employer!r}. The employer may use an ATS "
          "HiringCafe does not index — that is not evidence they are not "
          "hiring. Check their careers page by hand.", file=sys.stderr)
    sys.exit(1)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--provider", required=True, choices=PROVIDERS)
        sp.add_argument("--tenant", required=True)

    li = sub.add_parser("list", help="list an employer's postings")
    common(li)
    li.add_argument("--location", action="append",
                    help="substring match, repeatable, accent-insensitive")
    li.add_argument("--keywords", action="append", help="all must appear in the title")
    li.add_argument("--posted-within-days", type=int)
    li.add_argument("--remote", action="store_true", help="remote postings only")
    li.add_argument("--remote-counts-everywhere", action="store_true",
                    help="keep a remote posting even when it fails --location")
    li.add_argument("--with-description", action="store_true",
                    help="on smartrecruiters this costs ONE EXTRA REQUEST PER "
                         "AD — the list feed carries no description")
    li.add_argument("--country",
                    help="smartrecruiters only: a lowercase ISO-2 code, applied "
                         "SERVER-SIDE. An unknown code returns zero with HTTP "
                         "200, indistinguishable from an empty board")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="read one posting in full")
    common(ad)
    ad.add_argument("--id", required=True)
    ad.set_defaults(func=cmd_ad)

    rs = sub.add_parser("resolve", help="employer name -> provider and tenant")
    rs.add_argument("employer")
    rs.set_defaults(func=cmd_resolve)

    a = p.parse_args()
    if getattr(a, "country", None) and a.provider != "smartrecruiters":
        die(f"--country is a SmartRecruiters server-side filter; {a.provider} "
            f"has no equivalent. Use --location, which filters locally.")
    for f in ("location", "keywords", "remote", "posted_within_days",
              "remote_counts_everywhere", "with_description"):
        if not hasattr(a, f):
            setattr(a, f, None)
    a.func(a)


if __name__ == "__main__":
    main()
