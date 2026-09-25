#!/usr/bin/env python3
"""MyanmarJobLink (`www.myanmarjoblink.com`), Myanmar: a generalist whose LIST carries every field, so the whole board is 27 requests and not 405. The pager is a sliding window that also names its last page — the bound is read from page 1 only. Issue #639.

  myanmarjoblink.py jobs [--country-code MM] [--max-pages N]    1 request a page

WHAT IT IS. Myanmar's fifth route here, after `myjobsmm.py`, `jobnetmm.py`, `myanmargov.py`,
`bestjobmyanmar.py` and `myworldmm.py`. Many of its employers are recruitment agencies, which the
board names openly — unlike MyWorld, nothing is anonymised.

THE RULES. `www.myanmarjoblink.com` serves its rules file (`state: read`, `certain: True`) and
writes **no Crawl-delay**; 2 s are ours. **It declares no sitemap and `/sitemap.xml` answers 404**,
so there is no published enumerator and the list must be walked. The guard is on the exact path.

**THE BOUND IS READ FROM PAGE 1, AND ONLY FROM PAGE 1.** The pager on page 1 names `2 3 4 5 6` and
**27** — a sliding window that also carries its last page. Read on every page, the window would
follow the walk instead of bounding it. *Page 1 holds 15 adverts, so the board is between
26 × 15 + 1 = 391 and 27 × 15 = 405, and the last page's count pins it.* The run prints the emitted
count, the pages walked and the bound the site named.

**A FEATURED ADVERT IS AN ADVERT.** The items are `<li class="job_listing clearfix">` **and**
`<li class="job_listing clearfix job_position_featured">`. Anchoring on the exact class silently
drops every featured one — the defect that cost 33 adverts of 3 232 on Wazifaha, invisible because
what remains still looks like a board. The pattern matches the stable prefix.

**THE TITLE CARRIES THE REFERENCE, and they are separated by the reference's own shape** — the
anchor reads «&nbsp;Junior Accountant&nbsp;&nbsp;&nbsp;JO-59112&nbsp;», so `JO-\\d+` is lifted out and
the rest is the title. *Splitting on whitespace would cut a two-word title in half.*

**WITHHELD:** e-mail addresses and telephone numbers in free text. **The salary is a labelled field
and the telephone rule does not touch it** — this is Myanmar, where an ordinary monthly figure has
as many digits as a telephone number.

`--country-code` STAMPS; the board writes its own places («&nbsp;Hlaingtharya , Yangon&nbsp;»).

Measured 2026-09-25 18:3x UTC by the declared client, the guard on the exact path: `/find-jobs`
200, 159 415 B, **15 distinct adverts**, pager naming 27; `/sitemap.xml` **404**; no
`__NEXT_DATA__`, no `JobPosting` — server-rendered throughout.
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

HOST = "www.myanmarjoblink.com"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
# **Le prefixe stable, jamais la classe exacte : `job_position_featured` s'y ajoute.**
ITEM_RE = re.compile(r'<li class="job_listing[^"]*">(.*?)</li>', re.S)
DETAIL_RE = re.compile(r'href="[^"]*?/find-jobs/detail/(\d+)"')
TITLE_RE = re.compile(r'<h3><a href="[^"]*?/find-jobs/detail/\d+">(.*?)</a>', re.S)
COMPANY_RE = re.compile(r'<a href="[^"]*?/companies/detail/\d+"[^>]*><strong>(.*?)</strong>', re.S)
# **LE MEME CHAMP EST PORTE PAR DEUX BALISES SELON L'ITEM — mesure du 25.09.2026.**
# `<span class="fprize">` sur les annonces ordinaires, `<p class="fprize">` sur
# d'autres. Ancrer sur la BALISE rendait `salary` et `place` nuls **sur toutes les
# lignes**, en silence : la sortie restait un JSON complet et bien forme, avec deux
# champs vides qui se lisaient comme «&nbsp;le board ne publie pas de salaire&nbsp;».
# *C'est la variance `job_position_featured` une couche plus bas.* **On lit par la
# CLASSE que le site pose, jamais par la balise qui la porte.**
SALARY_RE = re.compile(r'<(?:p|span) class="fprize">\s*<b>Salary</b>\s*:\s*(.*?)</(?:p|span)>', re.S)
PLACE_RE = re.compile(r'<(?:p|span) class="Place">(.*?)</(?:p|span)>', re.S)
EXCERPT_RE = re.compile(r'<(?:p|span) class="only-mobile-show">(.*?)</(?:p|span)>', re.S)
POSTED_RE = re.compile(r"Posted\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})")
PAGE_RE = re.compile(r"/find-jobs/page/(\d+)")
REF_RE = re.compile(r"\bJO-\d+\b")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[myanmarjoblink] {msg}", file=sys.stderr)


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
    if parts.scheme != "https" or parts.netloc != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", markup or "")
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def money(s):
    """A LABELLED salary: the e-mail scrub only — a Myanmar figure has a telephone's digits."""
    return (MAIL_RE.sub("[e-mail withheld]", s).strip() or None) if s else None


def titre_et_ref(brut):
    """«Junior Accountant   JO-59112» → («Junior Accountant», «JO-59112»).

    Le decoupage se fait sur la FORME de la reference, jamais sur l'espace : un
    titre de deux mots serait coupe en deux.
    """
    t = text(brut) or ""
    m = REF_RE.search(t)
    if not m:
        return (t or None, None)
    return (t[:m.start()].strip() or None, m.group(0))


def items_of(markup):
    out = []
    for block in ITEM_RE.findall(markup or ""):
        d = DETAIL_RE.search(block)
        if not d:
            continue
        titre, ref = titre_et_ref((TITLE_RE.search(block) or [None, ""])[1] if TITLE_RE.search(block) else "")
        c = COMPANY_RE.search(block)
        s = SALARY_RE.search(block)
        p = PLACE_RE.search(block)
        e = EXCERPT_RE.search(block)
        dt = POSTED_RE.search(block)
        out.append({
            "id": d.group(1), "title": titre, "reference": ref,
            "employer": text(c.group(1)) if c else None,
            "salary": text(s.group(1)) if s else None,
            # le lieu tient sur une ligne : le site l'ecrit «Mingaladon ,\n Yangon»
            "place": " ".join((text(p.group(1)) or "").split()) or None if p else None,
            "excerpt": text(e.group(1)) if e else None,
            "posted": dt.group(1) if dt else None,
        })
    return out


def record(it, stamp):
    return {
        "source": "myanmarjoblink", "country": stamp,
        "ledger_id": f"myanmarjoblink:{it['id']}", "id": it["id"],
        "url": f"https://{HOST}/find-jobs/detail/{it['id']}",
        "reference": it["reference"],
        "title": scrub(it["title"]), "employer": scrub(it["employer"]),
        "salary": money(it["salary"]),
        "place": it["place"], "posted": it["posted"],
        "excerpt": scrub(it["excerpt"]),
        "contacts_withheld": True,
    }


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    rows, seen, borne, page = [], set(), None, 0
    while True:
        page += 1
        url = f"https://{HOST}/find-jobs" + (f"/page/{page}" if page > 1 else "")
        code, body = request(url)
        if code == 404:
            die(f"{url}: HTTP 404", EXIT_GONE)
        if code != 200:
            die(f"{url}: HTTP {code}", EXIT_PARTIAL)
        if page == 1:
            # **La borne se lit ICI et nulle part ailleurs.** Le pager glisse : lu a
            # chaque page il suivrait la marche au lieu de la borner.
            nums = [int(n) for n in PAGE_RE.findall(body)]
            borne = max(nums) if nums else None
            if "job_listing" not in body:
                die(f"{url}: 200 without a single job_listing — the list changed shape", EXIT_PARTIAL)
        found = items_of(body)
        if not found:
            break
        neufs = 0
        for it in found:
            if it["id"] in seen:
                continue
            seen.add(it["id"])
            rows.append(record(it, stamp))
            neufs += 1
        if not neufs:
            die(f"page {page} repeats the previous page's adverts — the walk ended at {len(rows)}", EXIT_PARTIAL)
        if a.max_pages and page >= a.max_pages:
            break
        if borne and page >= borne:
            break

    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    plafonne = bool(a.max_pages and page >= a.max_pages)
    note(f"{len(rows)} emitted over {page} page(s); the pager on page 1 named {borne} as its last"
         + (" — stopped by --max-pages" if plafonne else ""))
    if borne and not plafonne and page == borne:
        note(f"the walk reached the bound the site named; {len(rows)} sits in [{(borne-1)*15+1}, {borne*15}] if every page holds 15.")
    if stamp:
        note(f"country {stamp} is the user's stamp.")


def main(argv=None):
    p = argparse.ArgumentParser(description="MyanmarJobLink — the list carries every field, so the board is one request a page; the bound is read from page 1 only. Issue #639.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the list, 1 request a page")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record")
    j.add_argument("--max-pages", dest="max_pages", type=int, default=0, help="stop after N pages (0 = the bound page 1 names)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
