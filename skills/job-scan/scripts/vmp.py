#!/usr/bin/env python3
"""Virtuális Munkaerőpiac Portál (`vmp.munka.hu`) — Hungary's public employment service, through the GET search its own form posts; the site lists a search only when it is small enough and STATES THE COUNT when it refuses to list — that refusal is the board's own figure. Issue #358.

  vmp.py search [--kategoria 13] [--helyseg Budapest] [--kulcsszo TEXT] [--isk CODE] [--pages N] [--limit N]
  vmp.py categories
  vmp.py ad --url <https://vmp.munka.hu/allas/reszletek/<id>>

THE ROUTE IS THE FORM — `GET /allas/talalatok?kulcsszo=&helyseg=&kategoria=&tipus=allas`,
paged by `&oldal=N&sorrend=2&irany=ASC`, 50 rows a page. **The site lists
a result set only when it is small enough**: unfiltered it answers «A
lista túl sok elemet tartalmaz (1806), kérjük, szűkítse az eredményt» —
too many elements, narrow the search — and **that sentence carries the
board's own count** (1 806 on 2026-09-13 18:19 UTC; 1 799 for the letter
«a»; 435 for category 7; 203 for category 3 — refused; 141 for
Budapest and 4 for category 14 — listed). The threshold sits between 141
and 203 and is the site's; the adapter never guesses it: a listed search
is walked and compared to its «(N találat)», a refused one prints the
site's N and exits 6 with the word «narrow». `categories` asks the 25
categories one by one and prints each count, listed or refused, and
their sum beside the unfiltered 1 806 — a sum of categories is an upper
bound, not the board's size (an advertisement may sit in two).

NO RULES FILE (404 — an absence, a knowledge), no Crawl-delay; 2 s is
ours — **and after 14 requests in four minutes at that pace the host
answered 404 on every path, the root included** (18:23 UTC, a 546-byte
«A megadott cím nem található» page): a rate limit rendered as
not-found is the likeliest reading, and the adapter says so on a 404
rather than reporting a page gone. Spacing is 5 s since. THE ROW: the FEOR code and occupation (the site's title), the
education required, the workplace (city and district), and «Bejelentkezés
után látható» where the employer's name would be — **the employer is
shown to members only and the plugin never logs in**; `employer` is null
with the reason. THE DETAIL PAGE (`/allas/reszletek/<id>`, open) adds the
monthly gross salary («Felajánlott havi bruttó kereset (Ft)» — the unit
IS stated: monthly, gross, HUF), the headcount («Alkalmazni kívánt
létszám»), the validity dates, hours, schedule, education, the
description («Megjegyzés») — and the workplace as a street address, cut
here to the city and district. The employer's details are behind the
login there too. No contact is on either page.
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

HOST = "vmp.munka.hu"
BASE = f"https://{HOST}"
SEARCH = f"{BASE}/allas/talalatok"
DETAIL_RE = re.compile(r"^https://vmp\.munka\.hu/allas/reszletek/(\d+)/?$")
PAGE_SIZE = 50
FOUND_RE = re.compile(r"\((\d+) találat\)")
TOO_MANY_RE = re.compile(r"túl sok elemet tartalmaz \((\d+)\)")
ROW_RE = re.compile(r'<tr>\s*<td><a href="/allas/reszletek/(\d+)">(.*?)</a></td>\s*<td><a[^>]*>(.*?)</a></td>\s*<td><a[^>]*>(.*?)</a></td>\s*<td>(.*?)</td>', re.S)
LOGIN_NOTE = "Bejelentkezés után látható"
CATEGORIES = {1: "Alapítvány / Non-profit / Egyház", 2: "Államigazgatás / Közigazgatás", 3: "Asszisztencia / Adminisztráció / Ügyfélkapcsolat", 4: "Bank / Biztosítás / Pénzintézet",
              5: "Biztonság / Honvédelem / Biztonságtechnika", 6: "Egészségügy / Szociális ellátás", 7: "Egyéb foglalkozások", 8: "Energetika / Villamosság", 9: "Építés / Ingatlan",
              10: "Gyógyszeripar / Vegyipar", 11: "Humán erőforrás", 12: "Idegenforgalom / Vendéglátás", 13: "IT / Informatika / Telekommunikáció", 14: "Jog / Jogi tanácsadás",
              15: "Kereskedelem / Értékesítés / Szolgáltatás", 16: "Kultúra / Művészet / Szórakoztatás / Sport", 17: "Marketing / Reklám / Média / PR", 18: "Mezőgazdaság / Környezettudomány",
              19: "Műszaki / Mérnök", 20: "Oktatás / Képzés", 21: "Pénzügy / Számvitel / Kontrolling", 22: "Szakmunka / fizikai munka", 23: "Szervezés / Menedzsment / Cégvezetés",
              24: "Termelés / Gyártás / Szállítás", 25: "Tudomány / Kutatás, fejlesztés"}

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[vmp] {msg}", file=sys.stderr)


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=5.0)   # no rules file, no Crawl-delay; 5 s is ours — 2 s drew a 404-on-everything after 14 requests (2026-09-13)


def get(url):
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "hu"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</td>|</th>|</tr>|</li>|</h\d>|</dt>|</dd>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def figures(body):
    """(listed count, refused count) — the site states one of the two on every answer, or neither on an empty one."""
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", body or ""))
    f = FOUND_RE.search(t)
    m = TOO_MANY_RE.search(t)
    return (int(f.group(1)) if f else None, int(m.group(1)) if m else None)


def rows(body):
    out = []
    for m in ROW_RE.finditer(body or ""):
        ident, occ, edu, place, emp = m.groups()
        occ = text(occ)
        code = re.match(r"(\d{4}) - (.+)", occ)
        emp_t = text(emp)
        out.append({"source": "vmp", "country": "HU", "ledger_id": f"vmp:{ident}", "id": ident, "url": f"{BASE}/allas/reszletek/{ident}",
                    "title": code.group(2) if code else occ or None, "feor": code.group(1) if code else None,
                    "employer": None if LOGIN_NOTE in emp_t or not emp_t else emp_t,
                    "employer_hidden": (f"login required — the site prints «{LOGIN_NOTE}»" if LOGIN_NOTE in emp_t else None),
                    "education": text(edu) or None, "workplace": text(place) or None, "language": "hu"})
    return out


def query(a, page=1):
    q = {"tipus": "allas"}
    for k in ("kulcsszo", "helyseg", "kategoria", "isk"):
        v = getattr(a, k, None)
        if v:
            q[k] = v
    if page > 1:
        q.update({"oldal": page, "sorrend": 2, "irany": "ASC"})
    return SEARCH + "?" + urllib.parse.urlencode(q)


def cmd_search(a):
    code, body = get(query(a))
    if code != 200:
        # **A 404 on the search page has been a block from here**: on 2026-09-13 18:23 UTC, after 14 requests
        # in four minutes at 2 s, the host answered 404 with a 546-byte «A megadott cím nem található» page on
        # every path, the root included — the shape of a rate limit rendered as not-found. Not a verdict.
        die(f"{query(a)}: HTTP {code}" + (" — the host answered 404 to the root as well after a burst on 2026-09-13; a block rendered as 404 is not excluded: wait, and try the root first." if code == 404 else ""), EXIT_PARTIAL)
    found, too_many = figures(body)
    if too_many is not None:
        note(f"the site states {th(too_many)} for this search and refuses to list it («A lista túl sok elemet tartalmaz») — narrow with --kategoria/--helyseg/--kulcsszo/--isk; {th(too_many)} is the site's own count, not the adapter's.")
        sys.exit(EXIT_PARTIAL)
    if found is None:
        if not rows(body):
            die(f"{query(a)}: neither «(N találat)» nor «túl sok» on the page ({len(body)} characters) — not the results page as read.", EXIT_PARTIAL)
        die(f"{query(a)}: rows on the page and no «(N találat)» — the count line changed; a walk without it is not compared.", EXIT_PARTIAL)
    out, seen, page = [], set(), 1
    while True:
        new = 0
        for r in rows(body):
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            out.append(r)
            new += 1
        if new == 0 or len(out) >= found:
            break
        if a.pages and page >= a.pages:
            break
        if a.limit and len(out) >= a.limit:
            break
        page += 1
        code, body = get(query(a, page))
        if code != 200:
            die(f"{query(a, page)}: HTTP {code} — {th(len(out))} read before it; a partial walk is not a count.", EXIT_PARTIAL)
    emitted = out[:a.limit] if a.limit else out
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    where = ", ".join(f"{k}={getattr(a, k)}" for k in ("kulcsszo", "helyseg", "kategoria", "isk") if getattr(a, k, None)) or "no filter"
    bounded = (a.pages and page >= a.pages and found > page * PAGE_SIZE) or (a.limit and a.limit < found)
    if bounded:
        note(f"{th(n)} emitted of the {th(found)} the site states ({where}) — {page} page(s) of {PAGE_SIZE} walked by request (--pages/--limit), not a shortfall.")
    elif n == found:
        note(f"{th(n)} emitted over {page} page(s), site states {th(found)} ({where}) — equal.")
    else:
        note(f"{th(n)} emitted over {page} page(s), site states {th(found)} ({where}) — {th(abs(found - n))} " + ("short" if found > n else "more emitted than the site states") + ".")
    note(f"the employer's name is behind a login on every row — never read; `employer` is null on {sum(1 for r in emitted if r['employer'] is None)} of {th(n)}.")


def cmd_categories(a):
    """Each of the 25 categories asked once: its count as the site states it, listed or refused."""
    code, body = get(SEARCH + "?tipus=allas")
    whole = figures(body)[1] if code == 200 else None
    total, listed = 0, 0
    for k in sorted(CATEGORIES):
        code, body = get(f"{SEARCH}?kategoria={k}&tipus=allas")
        if code != 200:
            die(f"category {k}: HTTP {code}", EXIT_PARTIAL)
        found, too_many = figures(body)
        n = found if found is not None else too_many
        state = "listed" if found is not None else ("refused" if too_many is not None else "silent")
        if n is None:
            n = 0
        total += n
        listed += 1 if found is not None else 0
        print(json.dumps({"kategoria": k, "name": CATEGORIES[k], "count": n, "state": state}, ensure_ascii=False))
    note(f"{th(total)} summed over 25 categories ({listed} listed, {25 - listed} refused with their count) — a sum of categories, an upper bound; "
         + (f"the site states {th(whole)} unfiltered." if whole is not None else "the unfiltered search stated no count this run."))


def cmd_ad(a):
    m = DETAIL_RE.match((a.url or "").strip())
    if not m:
        die(f"{a.url}: not a detail address — expected {BASE}/allas/reszletek/<id>")
    ident = m.group(1)
    code, body = get(a.url)
    if code in (404, 410):
        die(f"{a.url}: HTTP {code}", EXIT_GONE)
    if code != 200:
        die(f"{a.url}: HTTP {code}. **A readable body is not an answer — the code decides.**")
    t = text(body[body.find("<body"):] if "<body" in body else body)
    lines = [l.strip() for l in t.split("\n") if l.strip()]
    if "Alapadatok" not in lines:
        die(f"{a.url}: not the detail page ({len(body)} characters) — no «Alapadatok» section.", EXIT_PARTIAL)

    def after(label, n=1):
        for i, l in enumerate(lines):
            if l == label:
                v = lines[i + 1:i + 1 + n]
                return " ".join(v).strip() if v else None
        return None
    head = next((l for l in lines if re.search(r"\(\d{6,8}\)$", l)), None)
    hm = re.match(r"(.+?)\s*\((\d+)\)$", head or "")
    sal = after("Felajánlott havi bruttó kereset (Ft)")
    sm = re.match(r"([\d\s]+)\s*-\s*([\d\s]+)", sal or "")
    lo = int(re.sub(r"\D", "", sm.group(1))) if sm else None
    hi = int(re.sub(r"\D", "", sm.group(2))) if sm else None
    place = after("Munkavégzés helye") or ""
    city = re.match(r"(?:\d{4}\s+)?([^\d,]+?(?:\s+\d{1,2}\.\s*ker\.)?)(?:\s+[A-ZÁÉÍÓÖŐÚÜŰ]\S*\s+(?:út|utca|u\.|tér|körút|sor|köz)\b.*)?$", place)
    headcount = after("Alkalmazni kívánt létszám")
    hc = re.match(r"(\d+)\s*fő", headcount or "")
    validity = after("Érvényesség időtartama")
    vm = re.match(r"(\d{4}\.\d{2}\.\d{2})\s*-\s*(\d{4}\.\d{2}\.\d{2})?", validity or "")
    # the description sits under «Megjegyzés» and runs to the validity line
    desc = None
    if "Megjegyzés" in lines:
        i = lines.index("Megjegyzés")
        j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("Érvényesség")), len(lines))
        desc = "\n".join(lines[i + 1:j]).strip() or None
    print(json.dumps({
        "source": "vmp", "country": "HU", "ledger_id": f"vmp:{ident}", "id": ident, "url": a.url,
        "title": hm.group(1).strip() if hm else after("Munkakör (FEOR)"), "reference": hm.group(2) if hm else None,
        "occupation": after("Munkakör (FEOR)"), "occupation_supplement": after("Munkakör kiegészítése"),
        "employer": None, "employer_hidden": "login required — the site prints «A foglalkoztató részletes adatainak megjelenítéséhez kérjük jelentkezzen be!»",
        "workplace": (city.group(1).strip() if city else place.split(",")[0]) or None,
        "salary_currency": "HUF" if sm else None, "salary_min": lo, "salary_max": hi if hi else None,
        "salary_unit": "MONTH" if sm else None, "salary_gross": True if sm else None, "salary_unit_stated": bool(sm),
        "headcount": int(hc.group(1)) if hc else None,
        "valid_from": vm.group(1) if vm else None, "valid_through": vm.group(2) if vm and vm.group(2) else None,
        "hours": after("Teljes/rész munkaidő (óra)"), "schedule": after("Munkarend"),
        "education": after("Elvárt iskolai végzettség"), "experience": after("Gyakorlati idő"),
        "description": (desc or "")[:20000] or None, "language": "hu",
    }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Virtuális Munkaerőpiac — Hungary's public employment service through its own GET search; a listed search is walked against «(N találat)», a refused one prints the site's «túl sok (N)» and stops; the employer stays behind the login. Issue #358.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="one search, 50 a page, 2 s apart; the site lists it or states its count and refuses")
    s.add_argument("--kulcsszo", help="free word")
    s.add_argument("--helyseg", help="county or city, as the site spells it (Budapest)")
    s.add_argument("--kategoria", help="category 1–25 (see `categories`)")
    s.add_argument("--isk", help="education code as the detailed form numbers them")
    s.add_argument("--pages", type=int)
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_search)
    c = sub.add_parser("categories", help="the 25 categories, each count as the site states it (listed or refused), and their sum beside the unfiltered count — 26 requests")
    c.set_defaults(fn=cmd_categories)
    d = sub.add_parser("ad", help="one detail page — salary (monthly gross HUF, stated), headcount, validity, hours, description; the employer behind the login")
    d.add_argument("--url", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
