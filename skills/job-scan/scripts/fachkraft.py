#!/usr/bin/env python3
"""Read the fachkraft.ch / sta.jobs board.

**One board, several brand domains.** www.fachkraft.ch is the umbrella: it
serves the listings of www.sta.jobs (`-STAxx` references) and
www.stellenpartner.ch (`-SPxxx`) as well as its own. Sweep fachkraft.ch and
nothing else — a brand domain adds no ads and doubles every row.

It is a staffing AGENCY board: `hiringOrganization` is STA Personal AG on every
ad, and the client employer is never named. Same shape as michaelpage.md.

The whole board arrives in one request — ~3 500 ads on fachkraft.ch, ~1 800 on
sta.jobs — because the page ships every card in its markup and only reveals 20
at a time client-side. There is nothing to paginate.

Usage:
  fachkraft.py list  [--domain www.fachkraft.ch] [--canton LU] [--search cnc]
                     [--with-ref]
  fachkraft.py ad    --slug polymechaniker-in-rapperswil-jona-dauerstelle-295702
  fachkraft.py check --ref 19868-STAZH
  fachkraft.py resolve --ref 19868-STAZH      # portable ref -> canonical slug
"""

import argparse
import html as htmlmod
import json
import re
import sys
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
# fachkraft.ch is the umbrella and serves every brand's references; the
# others are subsets. Sweep the first, and use the rest only to resolve or
# check a reference that arrived from elsewhere.
DOMAINS = ("www.fachkraft.ch", "www.sta.jobs", "www.stellenpartner.ch")
CARD = re.compile(r'<li class="ff-job-entry"(.*?)</li>', re.S)
ATTR = re.compile(r'data-(canton|jobtype|sector|job-id)="([^"]*)"')
HREF = re.compile(r'href="https://(?:www\.fachkraft\.ch|www\.sta\.jobs)/stellen/([^"/]+)/"')
FIELD = re.compile(r'ff-job-entry__(title|description|start-date|type|region)[^>]*>(.*?)</', re.S)
REF = re.compile(r"\b(\d+-STA[A-Z]{2})\b")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def get(url):
    """Return (status, final_url, body). 410 is this board's 'gone'."""
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90)
        return r.getcode(), r.geturl(), r.read().decode("utf8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach {urllib.parse_urlsplit(url).netloc if False else url}: {e}")


def to_text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", htmlmod.unescape(markup)).strip()


def label(chunk, name):
    """The card puts its label in a <span> before the value; drop the label."""
    m = re.search(r'ff-job-entry__%s[^>]*>(.*?)</div>' % name, chunk, re.S)
    if not m:
        return None
    txt = re.sub(r"(?is)<span[^>]*>.*?</span>", " ", m.group(1))
    return to_text(txt) or None


def cards(domain, body):
    out = []
    for chunk in CARD.findall(body):
        slugs = HREF.findall(chunk)
        if not slugs:
            continue
        slug = slugs[0]
        m = re.search(r"-(\d{4,})$", slug)
        title = re.search(r'ff-job-entry__title.*?<a[^>]*>(.*?)</a>', chunk, re.S)
        attrs = dict(ATTR.findall(chunk))
        out.append({
            "slug": slug,
            "id": m.group(1) if m else slug,
            "url": f"https://{domain}/stellen/{slug}/",
            "title": to_text(title.group(1)) if title else None,
            "canton": attrs.get("canton"),
            "region": label(chunk, "region"),
            "contract": label(chunk, "type"),
            "start": label(chunk, "start-date"),
            "teaser": label(chunk, "description"),
        })
    return out


def ledger_row(domain, c, ref=None):
    row = {
        # The portable key is the STA reference: the per-domain numeric id is
        # NOT shared — 0 of 3 534 fachkraft ids appear among sta.jobs's 1 835,
        # for the same underlying jobs.
        "id": ref or c["id"],
        "ledger_id": f"fachkraft:{ref}" if ref else f"fachkraft:{domain}:{c['id']}",
        "portable_key": bool(ref),
        "url": c["url"],
        "title": c["title"],
        # The agency, never the client. The employer is not named on this board.
        "company": None,
        "employer_named": False,
        "agency": "STA Personal AG",
        "provider": "fachkraft",
        "domain": domain,
        "canton": c.get("canton"),
        "region": c.get("region"),
        "contract": c.get("contract"),
        "start": c.get("start"),
        "teaser": c.get("teaser"),
    }
    if ref:
        row["sta_ref"] = ref
    return row


def ad_ref(domain, slug):
    """One request: the ad page carries its portable <n>-STAxx reference."""
    status, _final, body = get(f"https://{domain}/stellen/{slug}/")
    if status != 200:
        return None, status, ""
    m = REF.search(body)
    return (m.group(1) if m else None), status, body


# ---------------------------------------------------------------- commands --

def cmd_list(a):
    status, _final, body = get(f"https://{a.domain}/stellen/")
    if status != 200:
        die(f"{a.domain} answered HTTP {status} on /stellen/", code=4)
    rows = cards(a.domain, body)
    if not rows:
        die(f"{a.domain} served /stellen/ with no cards. The listing ships every "
            f"ad in its markup, so zero cards is a page-shape change, not an "
            f"empty board — report it with the board-request skill.", code=5)
    kept = 0
    for c in rows:
        if a.canton and (c.get("canton") or "").upper() != a.canton.upper():
            continue
        hay = " ".join(x for x in (c.get("title"), c.get("teaser")) if x).lower()
        if a.search and a.search.lower() not in hay:
            continue
        ref = None
        if a.with_ref:
            ref, _st, _b = ad_ref(a.domain, c["slug"])
        print(json.dumps(ledger_row(a.domain, c, ref), ensure_ascii=False))
        kept += 1
    note = f"[fachkraft:{a.domain}] {kept} of {len(rows)} ads on the board"
    if not a.with_ref:
        note += (" — keys are DOMAIN-SCOPED without --with-ref: the numeric id "
                 "differs between fachkraft.ch and sta.jobs for the same job, "
                 "so these rows will not match a job-room row or the other "
                 "domain. --with-ref costs one request per kept ad and fixes it")
    print(note, file=sys.stderr)
    if a.search and not kept:
        print(f"[fachkraft:{a.domain}] the board is not empty — all {len(rows)} "
              f"ads were filtered out.", file=sys.stderr)


def cmd_ad(a):
    ref, status, body = ad_ref(a.domain, a.slug)
    if status == 410:
        die(f"ad {a.slug!r} is gone (HTTP 410 — this board uses 410, not 404). "
            f"Record it as discarded.", code=3)
    if status != 200:
        die(f"{a.domain} answered HTTP {status} for {a.slug!r}", code=4)
    # <title> carries the site's own suffix ("- fachkraft.ch - Jobs für
    # Handwerker"); the JobPosting block carries the job title alone.
    m = re.search(r'"title"\s*:\s*"((?:[^"\\]|\\.)*)"', body) \
        or re.search(r"(?is)<title>(.*?)</title>", body)
    valid = re.search(r'"validThrough"\s*:\s*"([^"]+)"', body)
    print(json.dumps({
        "id": ref or a.slug,
        "ledger_id": f"fachkraft:{ref}" if ref else f"fachkraft:{a.domain}:{a.slug}",
        "sta_ref": ref,
        "url": f"https://{a.domain}/stellen/{a.slug}/",
        "title": htmlmod.unescape(m.group(1)).strip() if m else None,
        "company": None, "employer_named": False, "agency": "STA Personal AG",
        "provider": "fachkraft", "domain": a.domain,
        "valid_through": valid.group(1) if valid else None,
        "description": to_text(body)[:20000],
    }, ensure_ascii=False, indent=1))


def cmd_resolve(a):
    """A portable <n>-STAxx reference redirects to that domain's canonical slug."""
    status, final, _body = get(f"https://{a.domain}/stellen/{a.ref}/")
    if status == 410:
        die(f"reference {a.ref!r} is gone (HTTP 410). Record it as discarded.",
            code=3)
    if status != 200:
        die(f"{a.domain} answered HTTP {status} for reference {a.ref!r}", code=4)
    slug = final.rstrip("/").rsplit("/", 1)[-1]
    print(json.dumps({"ref": a.ref, "domain": a.domain, "slug": slug,
                      "url": final, "ledger_id": f"fachkraft:{a.ref}"},
                     ensure_ascii=False))


def cmd_check(a):
    status, final, body = get(f"https://{a.domain}/stellen/{a.ref}/")
    if status == 410:
        verdict, why = "closed", "HTTP 410 Gone — this board says so explicitly"
    elif status == 200:
        verdict, why = "open", "HTTP 200, redirected to the canonical ad"
    else:
        verdict, why = "unverified", f"HTTP {status}"
    valid = re.search(r'"validThrough"\s*:\s*"([^"]+)"', body or "")
    print(json.dumps({"ref": a.ref, "domain": a.domain, "verdict": verdict,
                      "why": why, "valid_through": valid.group(1) if valid else None,
                      "url": final}, ensure_ascii=False))
    sys.exit(0 if verdict == "open" else 1)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def dom(sp):
        sp.add_argument("--domain", default=DOMAINS[0], choices=DOMAINS,
                        help="fachkraft.ch is the umbrella and the one to sweep; "
                             "the others are subsets, useful only for resolving "
                             "or checking a reference that came from elsewhere")

    li = sub.add_parser("list", help="the whole board, in one request")
    dom(li)
    li.add_argument("--canton", help="two-letter code as the card carries it, e.g. LU")
    li.add_argument("--search", help="matched against title and teaser, locally")
    li.add_argument("--with-ref", action="store_true",
                    help="fetch each kept ad's portable <n>-STAxx reference — "
                         "one request per ad, and the only way to get a key "
                         "that matches across the two domains")
    li.set_defaults(fn=cmd_list)

    ad = sub.add_parser("ad", help="read one ad in full")
    dom(ad)
    ad.add_argument("--slug", required=True, help="the canonical path segment")
    ad.set_defaults(fn=cmd_ad)

    rs = sub.add_parser("resolve", help="portable reference -> canonical slug")
    dom(rs)
    rs.add_argument("--ref", required=True, help="e.g. 19868-STAZH")
    rs.set_defaults(fn=cmd_resolve)

    ck = sub.add_parser("check", help="is this ad still open? (step 1b)")
    dom(ck)
    ck.add_argument("--ref", required=True)
    ck.set_defaults(fn=cmd_check)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
