#!/usr/bin/env python3
"""Fetch job ads from emploi-territorial.fr — France's territorial civil service.

The portal of the centres de gestion: communes, departments, regions, CCAS,
intercommunalités. **26 613 posts** nationally on the day this was written —
the jobs of French local government, which no private board carries.

Server-rendered, no JSON and no JSON-LD, so this parses HTML. What makes that
safe: the rows are built from explicit **`label` / `valeur` pairs**
(*"Employeur :"*, *"Grade(s) :"*) and the two dates live in `data-tooltip`
attributes as real dates, not as "expire dans 29 jours".

Search is a **session**: the filter is POSTed once, then pages are fetched by
number and the server remembers the criteria. So a cookie jar is not optional.

  GET  /rechercher                     → results page 1, sets the session
  POST /rechercher                     → applies the filter
  POST /recherche_emploi_mobilite/     → page=N&ajax=1, one page of rows

**`/exportoffres/` is disallowed by robots.txt and is never used**, even though
the site's own JavaScript builds URLs for it. It is the bulk export; this
adapter reads the pages a candidate reads.

Usage:
  emploiterritorial.py search --departement 69 --pages 3
  emploiterritorial.py search --departement 69 --departement 01
  emploiterritorial.py search --pages 2          # the whole country

Output: one JSON object per line.
"""

import argparse
import gzip
import html as html_mod
import http.cookiejar
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _robots import allowed as robots_allowed

BASE = "https://www.emploi-territorial.fr"
SEARCH = BASE + "/rechercher"
PAGE = BASE + "/recherche_emploi_mobilite/"
AD = BASE + "/offre/{}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

ROW_RE = re.compile(r"<tr[^>]*>.*?</tr>", re.S)
LINK_RE = re.compile(r"href='(/offre/(o\d+)-[^']*)'")
TITLE_RE = re.compile(
    r"<a[^>]*lien-details-offre[^>]*>(.*?)</a>", re.S)
REF_RE = re.compile(r"class='[^']*numOf[^']*'>\s*([A-Z0-9]+)\s*<")
TOTAL_RE = re.compile(r'value="(\d+)"\s+id="nb-offres"')
# "Employeur :" and its value are two spans, label then valeur. The value is
# not plain text — the collectivité is wrapped in a link containing an icon
# span — so neither `[^<]+` nor a non-greedy `</span>` works: the first gives
# whitespace, the second stops at the inner tag. Both produce a field that is
# present and empty, on every ad. The value span is therefore sliced with a
# depth counter, in `span_value`.
LABEL_RE = re.compile(
    r"<span class='label'>\s*<em>([^<]+)</em>\s*</span>", re.S)
VALUE_OPEN_RE = re.compile(r"<span class='valeur[^']*'>")
SPAN_TAG_RE = re.compile(r"<(/?)span\b", re.I)
TOOLTIP_RE = re.compile(r'data-tooltip="([^"]+)"')
DATE_RE = re.compile(r"(\d{2}/\d{2}/\d{4})")

LABELS = {"employeur": "employer", "grade(s)": "grade", "grade": "grade"}


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def _robots_gate(url, tag, exit_code=7):
    """Ask before fetching — per host and **per path**. Issues #100, #101.

    `verdict()` answers *is this host closed in one block*. **A site that
    refuses its ad path while leaving its root open passes that and refuses
    every advertisement** — `empleate.gob.hn` does exactly that, closing
    `/Vacantes/` to `User-agent: *` with `/` absent.

    It sits **inside the fetch function**, so every request is covered rather
    than the first one, and a refusal **stops the command** with exit 7 and the
    module's own words. **This adapter decides nothing about what a refusal
    means** — deciding is what turns a check into a decoration.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc:
        return None
    a = robots_allowed(parts.netloc, parts.path or "/")
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", exit_code)
    if a.get("requested_host") and a["host"] != a["requested_host"]:
        print(f"[hellowork] robots.txt for {a['requested_host']} was read from "
              f"{a['host']} — a redirect crossed hosts. A platform that has "
              f"been renamed reaches an adapter this way before it reaches it "
              f"as a rename.", file=__import__("sys").stderr)
    return a



def opener():
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def call(op, url, data=None, ajax=False):
    _robots_gate(url, 'emploi-territorial')
    body = urllib.parse.urlencode(data, doseq=True).encode() if data else None
    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Accept-Encoding": "gzip",
    }
    if data:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if ajax:
        # Only the pagination call is an AJAX call. Sending this header on the
        # filter POST makes the server answer with a bare fragment instead of
        # the results page — which still contains ads, so it looks fine, but
        # the total count is missing and the sweep loses its bound.
        headers["X-Requested-With"] = "XMLHttpRequest"
    try:
        with op.open(urllib.request.Request(url, data=body, headers=headers),
                     timeout=60) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding", "").lower() == "gzip":
                raw = gzip.decompress(raw)
            return raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        die(f"emploi-territorial returned HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network shape varies by platform
        die(f"could not reach emploi-territorial: {e}")


def span_value(row, start):
    """Text of the `valeur` span beginning at `start`, nesting respected."""
    m = VALUE_OPEN_RE.search(row, start)
    if not m:
        return None
    depth, pos = 1, m.end()
    for t in SPAN_TAG_RE.finditer(row, m.end()):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return strip(row[m.end():t.start()])
        pos = t.end()
    return strip(row[m.end():pos])


def strip(markup):
    txt = re.sub(r"<[^>]+>", " ", markup or "")
    return re.sub(r"\s+", " ", html_mod.unescape(txt)).strip()


def dept_code(v):
    """`69` → `069`. The form's own values are three digits, zero-padded.

    A two-digit code is accepted by the server and matches nothing: the search
    comes back with **0 results and no error**, which reads as "no jobs in the
    Rhône" rather than "wrong code". Corsica is 02A / 02B.
    """
    v = str(v).strip().upper()
    if re.fullmatch(r"\d{1,3}", v):
        return v.zfill(3)
    if re.fullmatch(r"2[AB]", v):
        return "0" + v
    return v


def card(row):
    m = LINK_RE.search(row)
    if not m:
        return None
    path, ident = m.group(1), m.group(2)
    # A row renders twice — desktop and a mobile duplicate — so every field
    # appears twice. Everything below takes the first match only.
    title = TITLE_RE.search(row)
    ref = REF_RE.search(row)
    out = {
        "id": ident,
        "ledger_id": f"emploi-territorial:{ident}",
        "url": BASE + path,
        # The department is the first three digits of the id: o050… is Manche.
        "departement": ident[1:4],
        "reference": ref.group(1) if ref else None,
        "title": strip(title.group(1)) if title else None,
    }
    for lm in LABEL_RE.finditer(row):
        key = LABELS.get(lm.group(1).strip().rstrip(":").strip().lower())
        if key and not out.get(key):
            out[key] = span_value(row, lm.end())
    # The visible text says "publié aujourd'hui" and "expire dans 29 jours";
    # the tooltips carry the actual dates. Take the dates.
    for tip in TOOLTIP_RE.findall(row):
        tip = html_mod.unescape(tip)
        d = DATE_RE.search(tip)
        if not d:
            continue
        if "limite" in tip.lower() and "closes" not in out:
            out["closes"] = d.group(1)
        elif "publi" in tip.lower() and "published" not in out:
            out["published"] = d.group(1)
    out.setdefault("employer", None)
    out.setdefault("grade", None)
    out.setdefault("published", None)
    # A real closing date, stated by the employer — not `datePosted` plus a
    # constant, as on meteojob.md (+60) and hellowork.md (+30).
    out.setdefault("closes", None)
    return out


def rows_of(page):
    return [r for r in ROW_RE.findall(page) if "/offre/o" in r]


def cmd_search(a):
    op = opener()
    page = call(op, SEARCH)
    if a.departement:
        codes = [dept_code(d) for d in a.departement]
        page = call(op, SEARCH, {"search_offre_form[searchdept][]": codes,
                                 "btn_rechercher": ""})
        print(f"[emploi-territorial] filtered on {', '.join(codes)}",
              file=sys.stderr)
    total = TOTAL_RE.search(page)
    total = int(total.group(1)) if total else None
    print(f"[emploi-territorial] {total if total is not None else '?'} posts "
          "match", file=sys.stderr)
    if total == 0:
        print("[emploi-territorial] zero — check the department code before "
              "believing it: the form takes three digits (069, not 69) and an "
              "unknown value returns an empty board with no error",
              file=sys.stderr)
        return
    seen, n = set(), 1
    while True:
        fresh = 0
        for r in rows_of(page):
            c = card(r)
            if not c or c["id"] in seen:
                continue
            seen.add(c["id"])
            print(json.dumps(c, ensure_ascii=False))
            fresh += 1
        if not fresh:
            break
        if total is not None and len(seen) >= total:
            break
        if n >= a.pages:
            print(f"[emploi-territorial] stopping after {n} page(s); "
                  f"{len(seen)} of {total} collected. Raise --pages, or "
                  "narrow with --departement — the whole country is over a "
                  "thousand pages", file=sys.stderr)
            break
        n += 1
        time.sleep(a.delay)
        page = call(op, PAGE, {"page": n, "ajax": 1}, ajax=True)
    print(f"[emploi-territorial] {len(seen)} cards returned of {total}",
          file=sys.stderr)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="list posts")
    s.add_argument("--departement", action="append",
                   help="department code, repeatable. `69` is padded to `069`")
    s.add_argument("--pages", type=int, default=5,
                   help="pages of 20 to read (default 5)")
    s.add_argument("--delay", type=float, default=1.0)
    s.set_defaults(func=cmd_search)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
