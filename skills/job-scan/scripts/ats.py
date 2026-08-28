#!/usr/bin/env python3
"""Read one employer's job board directly from its ATS.

Greenhouse, Lever and Ashby each publish the postings of a given employer as
public JSON — the same feed that powers that employer's careers page. No key,
no cookie, no browser. What they do NOT offer is a search across employers:
you ask for one tenant at a time, which is why this is the adapter family for
"I want to work at X", not for discovery.

Usage:
  ats.py list --provider greenhouse --tenant elastic [--location Switzerland]
              [--keywords kubernetes] [--posted-within-days 30] [--remote]
  ats.py ad   --provider greenhouse --tenant elastic --id 8148720
  ats.py resolve "Nexthink"        # employer name -> provider + tenant

`resolve` asks HiringCafe, which records the ATS and tenant of every ad it
indexes. It is a lookup aid for setup, not a sweep.
"""

import argparse
import html
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

UA = "Mozilla/5.0 (compatible; claude-job-hunt/1.x; +personal job search)"
PROVIDERS = ("greenhouse", "lever", "ashby")


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

def greenhouse_list(tenant, want_content):
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


def lever_list(tenant, _want_content=True):
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
        out["description"] = (j.get("descriptionPlain")
                              or to_text(j.get("description")))
    return out


def ashby_list(tenant, _want_content=True):
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


LISTERS = {"greenhouse": greenhouse_list, "lever": lever_list, "ashby": ashby_list}
CARDERS = {"greenhouse": greenhouse_card, "lever": lever_card, "ashby": ashby_card}


# ----------------------------------------------------------------- filters --

def keep(card, a):
    """Filter locally. None of the three APIs offers a server-side search."""
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
    jobs = LISTERS[a.provider](a.tenant, True)
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
    else:
        j = next((x for x in LISTERS[a.provider](a.tenant, True)
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
    try:
        raw = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}),
            timeout=60).read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        die(f"could not reach hiringcafe to resolve the tenant: {e}")
    m = re.search(r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', raw, re.S)
    if not m:
        die("hiringcafe's page shape changed — resolve by hand instead: open "
            "the employer's careers page and read the tenant out of the URL.")
    hits = (json.loads(m.group(1))["props"]["pageProps"].get("ssrHits") or [])
    supported, other = {}, {}
    for h in hits:
        src = {"grnhse": "greenhouse", "lever": "lever", "eu_lever": "lever",
               "ashby": "ashby"}.get(h.get("source"))
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
    li.add_argument("--with-description", action="store_true")
    li.set_defaults(func=cmd_list)

    ad = sub.add_parser("ad", help="read one posting in full")
    common(ad)
    ad.add_argument("--id", required=True)
    ad.set_defaults(func=cmd_ad)

    rs = sub.add_parser("resolve", help="employer name -> provider and tenant")
    rs.add_argument("employer")
    rs.set_defaults(func=cmd_resolve)

    a = p.parse_args()
    for f in ("location", "keywords", "remote", "posted_within_days",
              "remote_counts_everywhere", "with_description"):
        if not hasattr(a, f):
            setattr(a, f, None)
    a.func(a)


if __name__ == "__main__":
    main()
