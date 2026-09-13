#!/usr/bin/env python3
"""HeadHunter (`api.hh.ru`) — one file for the hh network's five fronts (hh.ru RU, hh.kz KZ, hh.uz UZ, rabota.by BY, zarplata.ru RU), through the public JSON API its specification documents; the API's `found` printed beside every walk; the contact the API requires comes from the user's own config and never leaves this adapter in any text. Issue #337.

  hh.py search --area 16 [--text TEXT] [--pages N] [--limit N]
  hh.py ad --id <vacancy id>

THE ROUTE IS THE API, AND THE API ASKS WHO IS CALLING. `api.hh.ru` publishes
no rules file (404 — an absence, a knowledge) and its OpenAPI specification
requires a `User-Agent: MyApp/1.0 (contact address)` or `HH-User-Agent` on
every request; without one it answers 403. **The plugin never fabricates an
address.** The contact is the user's own, read from `boards.hh.contact` in
the workspace's `config.yml` — the same way `_override.py` reads
`override_robots`: workspace → config.yml → the `boards:` block — and sent
as `HH-User-Agent: claude-job-hunt/<version> (<contact>)` beside our own
`User-Agent`. **Without the key this adapter requests nothing and exits 7**
saying what to write. **With it the address goes to `api.hh.ru` and
nowhere else**: not to stdout, not to stderr, not to a card, a test, a
commit or a message — `setup.md` tells the user so before they set it.
Owner's decision of 2026-09-13 (#337): the form of the key, and one request
per area as the exercise.

THE COUNT. `/vacancies?area=<id>&per_page=<n>&page=<p>` answers `{found,
pages, per_page, page, items[]}`; `found` is the site's own figure for the
area and is printed beside every walk. `per_page` ≤ 100, and the API pages
to 2 000 results per query (page × per_page — its own window); the note
says where the window ends. Areas: **16 Belarus, 40 Kazakhstan, 97
Uzbekistan, 113 Russia** — the network's own ids, one front each;
`countries: RU KZ BY UZ`. Measured on the day with the owner's key: one
request per area (see the card).

THE ITEM: id, name, employer {id, name}, area {name}, salary {from, to,
currency, gross}, published_at, schedule, experience, employment,
snippet {requirement, responsibility}, alternate_url (the front's page),
professional_roles. THE VACANCY (`/vacancies/<id>`): description (HTML),
key_skills, and a `contacts` object the adapter DROPS whole — recruiters'
names, e-mails and telephones — and lists as dropped.
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

BOARD = "hh"
HOST = "api.hh.ru"
BASE = f"https://{HOST}"
AREAS = {"113": ("RU", "hh.ru"), "40": ("KZ", "hh.kz"), "97": ("UZ", "hh.uz"), "16": ("BY", "rabota.by")}
PAGE_SIZE = 100
WINDOW = 2000           # the API's own depth (page × per_page)

EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[hh] {msg}", file=sys.stderr)


def contact():
    """`boards.hh.contact` from the user's own config.yml — `(value, where)`, through `_override.py`, the one door to the config; the value is sent to the API and printed nowhere."""
    from _override import contact as _contact
    return _contact(BOARD)


def version():
    m = re.search(r"claude-job-hunt/([\d.]+)", UA)
    return m.group(1) if m else "0"


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


_PACE = Pace(HOST, own=1.0)   # no rules file, no Crawl-delay; 1 s is ours


def request(url):
    """One API request, with the user's contact in `HH-User-Agent` — and the contact in no message this function raises."""
    who, where = contact()
    if not who:
        die(f"{HOST} requires a contact address on every request (its OpenAPI specification: `HH-User-Agent: MyApp/1.0 (address)`), "
            f"and this plugin never fabricates one. **Nothing was requested.** Write your own address in your workspace: "
            f"`boards:` → `hh:` → `contact: \"claude-job-hunt (you@example.org)\"` — consulted: {where}. "
            f"See shared/setup.md: the address is sent to api.hh.ru on every request and to nothing else.", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url), headers={"User-Agent": UA, "HH-User-Agent": f"claude-job-hunt/{version()} ({who})", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup or "")
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</h\d>", "\n", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    out = re.sub(r"[ \t]+", " ", htmlmod.unescape(markup))
    return re.sub(r"(?:\s*\n\s*)+", "\n", out).strip()


def th(n):
    return f"{n:,}".replace(",", " ")


def api(url):
    code, body = request(url)
    if code == 403:
        die(f"{url}: HTTP 403 — the API refuses this request (a contact it does not accept, or a block); stopped, no retry.", EXIT_REFUSED)
    if code == 429:
        die(f"{url}: HTTP 429 — the API asks to slow down; stopped, no retry.", EXIT_REFUSED)
    if code == 404:
        return 404, None
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    try:
        return 200, json.loads(body)
    except ValueError:
        die(f"{url}: not JSON ({len(body)} characters)", EXIT_PARTIAL)


def row(it, area):
    iso, front = AREAS.get(str(area), (None, None))
    emp = it.get("employer") if isinstance(it.get("employer"), dict) else {}
    sal = it.get("salary") if isinstance(it.get("salary"), dict) else {}
    ar = it.get("area") if isinstance(it.get("area"), dict) else {}
    snip = it.get("snippet") if isinstance(it.get("snippet"), dict) else {}
    lab = lambda k: (it.get(k) or {}).get("name") if isinstance(it.get(k), dict) else None
    return {
        "source": BOARD, "country": iso, "front": front, "ledger_id": f"{BOARD}:{it.get('id')}", "id": str(it.get("id")),
        "url": it.get("alternate_url") or f"https://hh.ru/vacancy/{it.get('id')}",
        "title": it.get("name"), "employer": emp.get("name"), "employer_id": str(emp.get("id")) if emp.get("id") else None,
        "city": ar.get("name"), "published": it.get("published_at"),
        "salary_min": sal.get("from"), "salary_max": sal.get("to"), "salary_currency": sal.get("currency"),
        # the API states the period nowhere on the item — its salaries are monthly by the network's convention, and «read as» is not «stated»
        "salary_unit": None, "salary_unit_stated": False, "salary_gross": sal.get("gross"),
        "schedule": lab("schedule"), "experience": lab("experience"), "employment": lab("employment"),
        "roles": [r.get("name") for r in (it.get("professional_roles") or []) if isinstance(r, dict) and r.get("name")],
        "requirement": text(snip.get("requirement")) or None, "responsibility": text(snip.get("responsibility")) or None,
        "language": "ru",
    }


def cmd_search(a):
    if str(a.area) not in AREAS:
        die(f"--area {a.area}: not one of the network's country areas — {', '.join(f'{k} {v[0]}' for k, v in AREAS.items())}")
    rows, seen, page, found = [], set(), 0, None
    while True:
        q = {"area": a.area, "per_page": PAGE_SIZE, "page": page}
        if a.text:
            q["text"] = a.text
        code, j = api(f"{BASE}/vacancies?" + urllib.parse.urlencode(q))
        if code != 200 or not isinstance(j, dict) or "found" not in j:
            die(f"{BASE}/vacancies: no `found` in the answer — not the API's response shape.", EXIT_PARTIAL)
        if found is None:
            found = j.get("found")
        items = [it for it in (j.get("items") or []) if isinstance(it, dict)]
        new = 0
        for it in items:
            if not it.get("id") or str(it["id"]) in seen:
                continue
            seen.add(str(it["id"]))
            rows.append(row(it, a.area))
            new += 1
        if not items or new == 0 or len(rows) >= (found or 0):
            break
        if a.pages and page + 1 >= a.pages:
            break
        if a.limit and len(rows) >= a.limit:
            break
        if (page + 1) * PAGE_SIZE >= WINDOW:
            note(f"the API's window ends at {th(WINDOW)} results: {th(len(rows))} read, the site states {th(found)} — narrow with --text to read the rest.")
            break
        page += 1
    emitted = rows[:a.limit] if a.limit else rows
    for r in emitted:
        print(json.dumps(r, ensure_ascii=False))
    n = len(emitted)
    walked = page + 1
    iso, front = AREAS[str(a.area)]
    where = f"(area {a.area} {iso}, {front}" + (f", text={a.text!r}" if a.text else "") + ")"
    bounded = (a.pages and walked >= a.pages and (found or 0) > walked * PAGE_SIZE) or (a.limit and a.limit < (found or 0))
    if bounded:
        note(f"{th(n)} emitted of the {th(found)} the site states {where} — {walked} page(s) of {PAGE_SIZE} walked by request (--pages/--limit), not a shortfall.")
    elif n == found:
        note(f"{th(n)} emitted over {walked} page(s), site states {th(found)} {where} — equal.")
    else:
        note(f"{th(n)} emitted over {walked} page(s), site states {th(found)} {where} — {th(abs((found or 0) - n))} " + ("short" if (found or 0) > n else "more emitted than the site states") + ".")


def cmd_ad(a):
    ident = str(a.id).strip()
    if not ident.isdigit():
        die(f"{a.id!r}: not a vacancy id")
    code, j = api(f"{BASE}/vacancies/{ident}")
    if code == 404 or not isinstance(j, dict):
        die(f"{BASE}/vacancies/{ident}: HTTP 404", EXIT_GONE)
    area_id = str((j.get("area") or {}).get("id", "")) if isinstance(j.get("area"), dict) else ""
    r = row(j, area_id)
    r["country"] = r["country"] or None
    # **No contact leaves this adapter**: the vacancy's `contacts` (name, e-mail, phones) and anything named like one is dropped and listed
    dropped = sorted(k for k in j if re.search(r"contact|phone|email", k, re.I))
    r.update({"description": text(j.get("description"))[:20000] or None,
              "key_skills": [k.get("name") for k in (j.get("key_skills") or []) if isinstance(k, dict) and k.get("name")],
              "contact_dropped": dropped})
    print(json.dumps(r, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="HeadHunter's five fronts through api.hh.ru — the user's own contact in HH-User-Agent (never printed), `found` beside every walk, 2 000-deep window, contacts of a vacancy dropped. Issue #337.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="one area (16 BY · 40 KZ · 97 UZ · 113 RU), 100 a page, 1 s apart; the site's `found` beside the count")
    s.add_argument("--area", required=True)
    s.add_argument("--text")
    s.add_argument("--pages", type=int)
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("ad", help="one vacancy by id — description and key skills; `contacts` dropped and listed")
    d.add_argument("--id", required=True)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
