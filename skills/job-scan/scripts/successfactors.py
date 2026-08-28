#!/usr/bin/env python3
"""Read one employer's SAP SuccessFactors career site.

SuccessFactors is an ATS, not a board: one employer per host, no search across
employers. Employers front it with a vanity domain of their own
(jobs.<employer>.ch, www.carrieres-<employer>.com), so the host tells you
nothing and the path tells you everything.

v1.9.0 recorded that the /search/ page is rendered entirely client-side and
lists nothing to a plain fetch. That is still true — and it is beside the point,
because the widget is backed by a public JSON endpoint that answers
unauthenticated, with no key, no cookie and NO BROWSER:

    POST https://<host>/services/recruiting/v1/jobs
    {"locale": "fr_FR", "pageNumber": 0, "keywords": "..."}

The locale is the trap. Get it wrong and the board comes back EMPTY with no
error at all — see `locale`, which reads the right one off the site.

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

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
API = "/services/recruiting/v1/jobs"
PAGE = 10          # fixed by the service; pageNumber is 0-indexed
LOCALE_RE = re.compile(r"locale[=:]\s*['\"]?([a-z]{2}_[A-Z]{2})")
DESC_RE = re.compile(r'(?is)<div[^>]*(?:class|id)="[^"]*joblayouttoken[^"]*"[^>]*>(.*)')


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def get(url):
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=45)
        return r.getcode(), r.read().decode("utf8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach {urllib.parse.urlsplit(url).netloc}: {e}")


def post(host, body):
    url = f"https://{host}{API}"
    data = json.dumps(body).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            url, data=data,
            headers={"User-Agent": UA, "Content-Type": "application/json"}),
            timeout=60)
        return json.loads(r.read().decode("utf8", "replace"))
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


def read_ad(host, locale, jid, slug=""):
    """The vacancy page is server-rendered, unlike /search/."""
    status, body = get(f"https://{host}/job/{slug or 'x'}/{jid}-{locale}")
    return status, body


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
                status, body = read_ad(a.host, locale, jid,
                                       r.get("unifiedUrlTitle") or "")
                m = DESC_RE.search(body) if status == 200 else None
                out["description"] = to_text(m.group(1))[:20000] if m else ""
            print(json.dumps(out, ensure_ascii=False))
            kept += 1
    note = f"[successfactors:{a.host}] {kept} of {total} postings, locale {locale}"
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
    status, body = read_ad(host, locale, jid)
    if status != 200:
        return "unverified", f"HTTP {status}", "", body
    title = page_title(body)
    _, control_body = read_ad(host, locale, CONTROL_ID)
    control = page_title(control_body)
    if control and title.strip() == control.strip():
        return ("unverified",
                "HTTP 200, but the page is identical to the one a deliberately "
                "invented id returns — the requisition does not resolve. NOT "
                "proof it closed: a genuinely closed requisition has never been "
                "observed on this ATS",
                title, body)
    return "open", "HTTP 200, and the page differs from the invented-id control", title, body


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
