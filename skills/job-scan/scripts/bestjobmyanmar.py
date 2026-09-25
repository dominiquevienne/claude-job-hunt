#!/usr/bin/env python3
"""BestJobMyanmar (`www.bestjobmyanmar.com`), Myanmar: a small DJ-Classifieds board whose own RSS feed enumerates it, so the walk needs no pager and no guess at component internals. **Three independent readings agree that the board publishes three live adverts** — the HTML listing, a connected tab, and the feed's own `<item>` count. Issue #637.

  bestjobmyanmar.py jobs [--country-code MM] [--max N]     the feed, then one request an advert

WHAT IT IS. A Joomla site running DJ-Classifieds (`com_djclassifieds`), server-rendered — no
`__NEXT_DATA__`, no `data-page`, nothing client-side carrying the list. Myanmar's other routes are
`myjobsmm.py`, `jobnetmm.py` and `myanmargov.py`; this is a fourth and much smaller one.

THE RULES. `www.bestjobmyanmar.com` serves its rules file (`state: read`, `certain: True`) and
writes **no Crawl-delay**; 2 s is ours. The guard is taken on the exact path, query string included.

THE ROUTE, AND WHY IT IS THE FEED. `/jobs` — the path the issue named — answers **HTTP 404**; the
listing lives at `/find-jobs-in-myanmar`, which states no count and carries no pager. The site
publishes its own feed at `/find-jobs-in-myanmar?format=feed&type=rss`, linked from that page, and
its `<item>` count is a figure this adapter does not compute: **it is printed beside the emitted
count, and a mismatch is an error, not a note.** *There is no sitemap (404).*

**A LINK COUNT IS NOT AN ADVERT COUNT HERE.** The same advert is published under two URL shapes on
the same page — `/find-jobs-in-myanmar/ad/sale-51/<slug>-<id>` (canonical, the feed's) and
`/find-jobs-in-myanmar/sale/ad/<slug>-<id>` (the home page's). Counting `/ad/` links gives a number
that looks like an inventory and is not one. The advert's identity is the trailing **id**.

**AND A NUMBER IN A PATH BELONGS TO A NAMESPACE.** `sale-51` is category 51 (Sale); `51` is also
**Bago** in the location select. Same integer, different vocabularies — read from the site's own
`<option>` lists, never inferred from the path.

FIELDS ARE READ BY THE SITE'S OWN LABELS, never by position: every one is a
`<span class="row_label">…</span><span class="row_value">…</span>` pair. Salary, employer name,
workplace, dates, industry, work type.

**WITHHELD — and the two are withheld for different reasons.** *Contacts*: e-mail addresses and
telephone numbers in free text («[e-mail withheld]» / «[telephone withheld]»); the board's «Contact
Now» form is never touched. *A personal criterion*: the board prints **Gender** on some adverts
(«Male»), and #183 says such a criterion is not propagated — it is withheld and **named** in
`criteria_withheld`. **The declaration follows the ADVERT, never the board**: an advert that prints
no gender declares nothing, because a `criteria_withheld` that names what was never there would lie
about our own discretion rather than about the board.

**THE SALARY IS A LABELLED FIELD AND THE TELEPHONE RULE DOES NOT TOUCH IT.** The board writes
«Up To 550,000 Kyats» — six figures, which is exactly the shape a nine-digit telephone rule catches.
That rule destroyed 113 of 115 salaries on another Myanmar board before it was caught by a fixture
holding a real figure. *The danger is not «a salary field»: it is a currency whose ordinary monthly
pay has as many digits as a telephone number.* The e-mail scrub stays; it costs nothing.

`--country-code` STAMPS (no record states a country) and the run says so.

Measured 2026-09-25 07:44–08:0x UTC by the declared client, the guard on the exact path, two reads
of the root: 200, 63 062 B, **md5 f12de9a76dc3 then 41de5c313125 — the root's fingerprint MOVES
between two reads**, so no md5 comparison means anything on this host. `/find-jobs-in-myanmar` 200,
73 726 B, 3 adverts, no count stated, no pager; `/jobs` **404**; `/sitemap.xml` **404**; the feed
200, 3 176 B, **3 items**. A connected tab shows the same three, so nothing is hidden behind
JavaScript. The category select offers exactly three categories (Customer Service 24,
Engineering/Technology 106, Sale 51) under the parent «Jobs» (110) — one advert each.
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

HOST = "www.bestjobmyanmar.com"
FEED = "/find-jobs-in-myanmar?format=feed&type=rss"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# **UNE REGLE ANCREE SUR LE PREFIXE MOBILE LAISSE PASSER LES FIXES — et elle rend
# la garde du salaire INERTE par la meme occasion.** Premier jet : `0?9` en tete,
# donc « 09 765 432 109 » etait pris et « 01 234 5678 » ne l'etait pas ; et comme
# aucun salaire en kyats ne commence par 9, la mutation qui remettait le salaire
# sous la regle du telephone **restait VERTE** — la garde ne pouvait pas echouer
# sur ce qu'elle pretendait surveiller. *Deux defauts d'un seul ancrage : des
# contacts qui fuient, et une garde inerte qui se lit comme une protection.*
# La regle porte donc sur la FORME (sept chiffres et plus, separateurs admis), ce
# qui la met en collision avec les salaires en kyats — et c'est exactement pour ca
# que `money()` existe et qu'il est desormais porteur, pas decoratif.
PHONE_RE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().\-/]{6,}\d(?!\w)")
ITEM_RE = re.compile(r"<item>(.*?)</item>", re.S)
TAG_RE = {k: re.compile(r"<%s>(.*?)</%s>" % (k, k), re.S) for k in ("title", "link", "category", "pubDate", "description")}
CDATA_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.S)
# Le couple que le site pose lui-meme sur CHAQUE champ.
PAIR_RE = re.compile(r'<span class="row_label">(.*?)</span>\s*<span class="row_value[^"]*">(.*?)</span>', re.S)
# **LE SALAIRE EST LE SEUL CHAMP A VALEUR IMBRIQUEE, ET IL SE LIT A PART.**
# Le site ecrit `<span class='price_val'>Up to 550,000</span> <span
# class='price_unit'>Kyats</span>` : `PAIR_RE` s'arrete au premier `</span>` et
# rendait donc « Up to 550,000 » **sans sa monnaie** — un montant sans unite, la
# faute que le depot poursuit partout sur ses compteurs, ici dans la donnee livree.
# *Et le premier correctif etait pire que le defaut* : fermer la valeur sur le
# `</div>` de la ligne faisait traverser les lignes suivantes au motif, si bien que
# le salaire avalait « Name / JinLong Myanmar » et que l'employeur sortait vide.
# **Un motif qui deborde ne rend pas moins, il rend faux, et il abime un AUTRE
# champ que celui qu'on croyait corriger.** On lit donc les deux `<span>` que le
# site pose lui-meme, et rien d'autre.
PRICE_RE = re.compile(r"<span class='price_val'>(.*?)</span>(?:\s*<span class='price_unit'>(.*?)</span>)?", re.S)
# Le conteneur nomme la nature du champ : `row_gender`, `row_industry`, `price_wrap`…
GENDER_RE = re.compile(r'class="[^"]*row_gender[^"]*"', re.S)
ID_RE = re.compile(r"-(\d+)$")
_PACES = {}


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[bestjobmyanmar] {msg}", file=sys.stderr)


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
    a = gate(url)
    _PACES.setdefault(HOST, Pace(HOST, own=2.0)).wait()   # aucun Crawl-delay ecrit : 2 s sont les notres
    req = urllib.request.Request(wire_url(url), headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/rss+xml"})
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
    """Free text: both rules. A title, an employer's name, a description."""
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def money(s):
    """A LABELLED salary: the e-mail scrub only — see the module docstring."""
    return (MAIL_RE.sub("[e-mail withheld]", s).strip() or None) if s else None


def id_of(url):
    m = ID_RE.search(urllib.parse.urlsplit(url or "").path)
    return m.group(1) if m else None


def feed_items(body):
    out = []
    for block in ITEM_RE.findall(body or ""):
        row = {}
        for k, rx in TAG_RE.items():
            m = rx.search(block)
            v = m.group(1) if m else ""
            c = CDATA_RE.search(v)
            row[k] = text(c.group(1) if c else v)
        if row.get("link"):
            out.append(row)
    return out


def fields_of(markup):
    """The advert's labelled pairs, keyed by the label the SITE printed."""
    out = {}
    for lab, val in PAIR_RE.findall(markup or ""):
        k = (text(lab) or "").rstrip(":").strip()
        if k and k not in out:
            out[k] = text(val)
    m = PRICE_RE.search(markup or "")
    if m:
        out["__salary__"] = " ".join(x for x in (text(m.group(1)), text(m.group(2))) if x) or None
    return out


def record(item, f, has_gender, stamp):
    ident = id_of(item["link"])
    withheld = ["gender"] if has_gender else []
    return {
        "source": "bestjobmyanmar", "country": stamp,
        "ledger_id": f"bestjobmyanmar:{ident}", "id": ident,
        "url": item["link"], "title": scrub(item.get("title")),
        "category": item.get("category"),
        "employer": scrub(f.get("Name")),
        "workplace": scrub(f.get("Workplace")),
        "salary": money(f.get("__salary__")),
        "industry": f.get("Industry"),
        "work_type": f.get("Work Type"),
        "posted": f.get("Date Posted"), "updated": f.get("Updated"),
        "published": item.get("pubDate"),
        "description": scrub(item.get("description")),
        "contacts_withheld": True,
        # **Ce que l'ANNONCE portait, jamais ce que le board porte en general.**
        "criteria_withheld": withheld,
    }


def cmd_jobs(a):
    stamp = a.country_code.upper() if a.country_code else None
    url = f"https://{HOST}{FEED}"
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 — the feed the listing links is gone", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    items = feed_items(body)
    stated = body.count("<item>")          # le compte du SITE, pas le mien
    if not items:
        die(f"{url}: 200 but no <item> — the feed changed shape; not an empty board", EXIT_PARTIAL)

    rows, seen, manques = [], set(), 0
    for it in items:
        if a.max and len(rows) >= a.max:
            break
        ident = id_of(it["link"])
        if not ident or ident in seen:
            continue
        seen.add(ident)
        c, page = request(it["link"])
        if c != 200:
            manques += 1
            note(f"{it['link']}: HTTP {c} — advert skipped")
            continue
        rows.append(record(it, fields_of(page), bool(GENDER_RE.search(page)), stamp))

    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

    # **Le compte enonce est imprime a cote de l'emis, et l'ecart est une ERREUR.**
    emis, plafonne = len(rows), bool(a.max and len(rows) >= a.max)
    note(f"{emis} emitted, the site's feed states {stated} item(s)"
         + (f", {manques} advert page(s) unreachable" if manques else "")
         + (" — stopped by --max" if plafonne else ""))
    withheld = sum(1 for r in rows if r["criteria_withheld"])
    if withheld:
        note(f"gender withheld and named on {withheld} of {emis} advert(s) (#183); the rest print none.")
    if stamp:
        note(f"country {stamp} is the user's stamp — no record states one.")
    if not plafonne and not manques and emis != stated:
        die(f"{emis} emitted against {stated} stated by the feed — {abs(stated-emis)} unaccounted", EXIT_PARTIAL)


def main(argv=None):
    p = argparse.ArgumentParser(description="BestJobMyanmar — the board's own RSS feed enumerates it; the stated count is printed beside the emitted one. Issue #637.")
    sub = p.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("jobs", help="the feed, then one request an advert")
    j.add_argument("--country-code", dest="country_code", metavar="ISO2", help="STAMP a country on every record (no record states one)")
    j.add_argument("--max", type=int, default=0, help="stop after N adverts (0 = all the feed names)")
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
