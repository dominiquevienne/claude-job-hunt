#!/usr/bin/env python3
"""Melli Kar (`mellikar.com`, «ملی کار», Iran): an ASP.NET WebForms board whose category pages carry their adverts in a `Repeater` and hand out the next eighteen by POSTBACK — and **whose list RESETS itself to its first slice, twice in eight rounds measured**, so «a round with nothing new» is NOT the end. Issue #631.

  mellikar.py categories                      # the eight the home page states, with their counts
  mellikar.py jobs --category manual-worker [--rounds N | --all]
  mellikar.py ad --url https://mellikar.com/jobs/category/<slug>   (the advert has no address of its own)

**THE RESET IS THE WHOLE DIFFICULTY, AND IT HAS NO SYMPTOM.** Measured 2026-09-23
15:4x–15:5x UTC on `/jobs/category/manual-worker`:

    GET     18 cumul
    POST1 page=  18 nouv=  0 cumul=  18 vs=9368o   <-- nothing new
    POST2 page=  36 nouv= 18 cumul=  36 vs=14080o
    POST3..7  +18 each round                cumul= 126 vs=37996o
    POST8 page=  18 nouv=  0 cumul= 126 vs=9368o   <-- nothing new

A round that brings nothing new returns **the first eighteen again, with a
`__VIEWSTATE` back at its starting size** — the server has dropped the
accumulation. The next round resumes. **The rule every other adapter here uses
— stop when a round brings nothing new — would have emitted 18 of the 5 358
this category states, with exit 0, no error and nothing to re-read.** So a
barren round is treated as a RESET and replayed; only `MAX_RESETS` consecutive
ones stop the walk, and they are said.

THE PAGE ACCUMULATES, SO THE WALK IS QUADRATIC IN BYTES. Each postback returns
everything read so far: 111 KB at the GET, 424 KB at the fourth round, and the
`__VIEWSTATE` grows from 9 to 38 KB. Walking one category of 5 358 would need
~298 rounds whose last response is ~21 MB, over a gigabyte in all — for one
category of eight. **`--rounds` is therefore the default (three), and the
output says it is a bounded read.**

THE POSTBACK CARRIES THE THREE STATE FIELDS AND NOTHING ELSE. Echoing the whole
form — every `hidden`, every `select` — answers **500**. Echoing
`__VIEWSTATE`, `__VIEWSTATEGENERATOR`, `__EVENTVALIDATION` plus the button
answers 200 and appends. *Sending more is not being more faithful.*

THE CATEGORY IS KEPT. The page's `<title>` changes after the first postback
(«جدیدترین آگهی استخدامی» — the newest adverts), which looks like the filter
being dropped; it is not. Every appended row carries the same `HideDaste`, and
the walk checks it: a row of another category is counted and NAMED, never
emitted silently.

WHAT THE HOME PAGE STATES, AND WHAT IT CLAIMS. «امروز **بیش از** 70000 شغل» is
«MORE THAN 70 000» — an advertising claim, not a count, and the site says so in
its own word. The eight per-category figures («۵۳۵۸ موقعیت باز») ARE counts:
they moved between 2026-09-17 and 2026-09-23 (5316→5358, 3822→3858,
1875→1881), so they are computed. They are the witness, and they live on the
HOME page — a category page states nothing.

A FIELD NAME THAT LIES. `lblEnteshar` means «publication», and it carries the
CONTRACT («تمام وقت» — full time). It is read for what it holds, not for what
it is called.

THE SALARY IS BEHIND A LOGIN — «برای مشاهده حقوق وارد شوید» («log in to see the
salary»). It is DECLARED (`salary_behind_login`) rather than left absent: *a
field a site hides is not a field the site does not have.* No account is
created, ever.

THE RULES (read 2026-09-23): `mellikar.com` answers a `robots.txt` with no
directive that matches — open, `certain: True`, no `Crawl-delay`, one sitemap.

WITHHELD: e-mail addresses and telephone numbers in every text (Persian digits
included) — **the home page carries the operator's own address and two numbers,
which are never emitted**; the employer's logo; the application route; the
site's internal ids beyond the advert's own. Country IR.
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

BOARD, HOST, COUNTRY = "mellikar", "mellikar.com", "IR"
BASE = f"https://{HOST}"
HOME = BASE + "/"
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8
SLICE = 18
MAX_ROUNDS = 400
MAX_STALLS = 2       # rounds without the page growing before calling it the end
STATE_FIELDS = ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION")
LOADMORE = "ctl00$ContentPlaceHolder1$btnLoadMore"
FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
# the home page writes its category links RELATIVE and its city links absolute — both forms are read
CAT_RE = re.compile(r'<a href="(?:https://mellikar\.com)?/jobs/category/([a-z0-9-]+)"[^>]*>(.*?)</a>', re.S)
COUNT_RE = re.compile(r"\(\s*([\d۰-۹٠-٩,،]+)\s*موقعیت\s*باز\s*\)")
ITEM_RE = re.compile(r'Repeater1\$ctl(\d+)\$(HideAgahiID|HideDaste|hideKarfarmaID|HideShahr)"[^>]*value="([^"]*)"')
LABEL_RE = re.compile(r'id="ContentPlaceHolder1_Repeater1_(\w+?)_(\d+)"[^>]*>(.*?)</(?:span|div|p|li|a)>', re.S)
MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<![\w/$€])\+?[\d۰-۹][\d۰-۹\s().\-]{7,}[\d۰-۹](?!\w)")
LOGIN_SALARY = "برای مشاهده حقوق"
_PACE = Pace(HOST, own=2.0)


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[mellikar] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


def fa_int(s):
    """A count the site writes in Persian or Latin digits. «بیش از 70000» is not passed here: it is a
    claim, and the caller never treats it as a number."""
    if not s:
        return None
    d = re.sub(r"[^0-9]", "", s.translate(FA_DIGITS))
    return int(d) if d else None


def gate(url):
    parts = urllib.parse.urlsplit(url)
    a = robots_allowed(parts.netloc, full_path(parts))
    if a["allowed"] is None:
        die(f"{url}: {a['reason']}", EXIT_UNKNOWN)
    if not a["allowed"]:
        die(f"{url}: {a['reason']}", EXIT_REFUSED)
    return a


def request(url, form=None):
    """(status, text) — this host only, the guard first, 2 s apart. `form` makes it a POST."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower() != HOST:
        die(f"{url}: not {HOST} — never sent", EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    headers = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "fa,en"}
    data = None
    if form is not None:
        data = urllib.parse.urlencode(form, encoding="utf-8").encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(wire_url(url), data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def text(markup):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", markup or "", flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>", "\n", t)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ").replace("‌", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    if not s:
        return None
    s = MAIL_RE.sub("[e-mail withheld]", s)
    return PHONE_RE.sub("[telephone withheld]", s).strip() or None


def status_of(st, url):
    if st == 404:
        die(f"{url}: HTTP 404", EXIT_GONE)
    if st in (403, 429):
        die(f"{url}: HTTP {st} — the operator answering directly; stopped, no retry, no other agent, no browser (robots-policy.md).", EXIT_REFUSED)
    if st == 500:
        die(f"{url}: HTTP 500 — the postback was refused. This board answers 500 when the whole form is echoed; "
            f"only {', '.join(STATE_FIELDS)} and the button are sent.", EXIT_PARTIAL)
    if st != 200:
        die(f"{url}: HTTP {st}", EXIT_PARTIAL)


def state_of(body):
    out = {}
    for n in STATE_FIELDS:
        m = re.search(rf'name="{n}"[^>]*value="([^"]*)"', body or "")
        if m:
            out[n] = htmlmod.unescape(m.group(1))
    return out


def items(body):
    """The Repeater's rows, by index: the site's own ids plus the labels beside them."""
    hid, lab = {}, {}
    for idx, field, value in ITEM_RE.findall(body or ""):
        hid.setdefault(idx.lstrip("0") or "0", {})[field] = htmlmod.unescape(value)
    for name, idx, inner in LABEL_RE.findall(body or ""):
        lab.setdefault(idx, {})[name] = text(inner)
    out = []
    for idx in sorted(hid, key=lambda x: int(x)):
        h, l = hid[idx], lab.get(idx, {})
        if not h.get("HideAgahiID"):
            continue
        # `lblName2` is the title with the job family appended — «وسط کار تولیدی کارگر» is the advert
        # «وسط کار تولیدی» plus «کارگر», which `lblShoghl` holds on its own.
        title, family = l.get("lblName2"), l.get("lblShoghl")
        if title and family and title.endswith(family):
            title = title[: -len(family)].strip() or title
        out.append({"id": h["HideAgahiID"], "category_code": h.get("HideDaste"),
                    "employer_code": h.get("hideKarfarmaID"), "city_code": h.get("HideShahr"),
                    "title": title, "family": family, "place": l.get("lblCity"),
                    # **the field called «publication» holds the CONTRACT** — read for what it holds
                    "contract_as_written": l.get("lblEnteshar"),
                    "salary_raw": l.get("mablaghLi2")})
    return out


def row(c, slug):
    behind = bool(c["salary_raw"] and LOGIN_SALARY in c["salary_raw"])
    return {"source": BOARD, "country": COUNTRY, "ledger_id": f"{BOARD}:{c['id']}", "id": c["id"],
            "url": f"{BASE}/jobs/category/{slug}", "category": slug,
            "title": scrub(c["title"]), "place": scrub(c["place"]),
            "family_as_written": c["family"], "contract_as_written": c["contract_as_written"],
            # *a field a site hides is not a field the site does not have* — said, not left absent
            "salary_behind_login": behind,
            "salary_as_written": None if behind else scrub(c["salary_raw"]),
            "contacts_withheld": True}


def cmd_categories(a):
    st, body = request(HOME)
    status_of(st, HOME)
    seen, out = set(), []
    for slug, inner in CAT_RE.findall(body):
        if slug in seen:
            continue
        seen.add(slug)
        tail = body[body.index(f'/jobs/category/{slug}"'):][:600]
        m = COUNT_RE.search(tail)
        # The tile's text is the name AND the count beneath it. Cutting on the first line break works
        # on the real page, where the two sit in sibling blocks — and NOT on a tile whose count shares
        # the line. The count is removed by what it IS, not by where it happens to fall.
        label = COUNT_RE.sub("", text(inner) or "").strip(" \n()") or None
        out.append({"category": slug, "label": label, "stated": fa_int(m.group(1)) if m else None})
    if not out:
        die(f"{HOME}: no category tile in the answer — the home page changed shape.", EXIT_PARTIAL)
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    withc = [r for r in out if r["stated"] is not None]
    note(f"{th(len(out))} categories, {th(len(withc))} of them stating a count — the eight «موقعیت باز» figures are "
         f"the site's own and they MOVE (5 316→5 358 between 2026-09-17 and 09-23), so they are computed. "
         f"The «بیش از 70000 شغل» of the front is «MORE THAN 70 000»: a claim, never a count.")


def stated_for(slug):
    st, body = request(HOME)
    status_of(st, HOME)
    for s, _inner in CAT_RE.findall(body):
        if s == slug:
            tail = body[body.index(f'/jobs/category/{slug}"'):][:600]
            m = COUNT_RE.search(tail)
            return fa_int(m.group(1)) if m else None
    return None


def cmd_jobs(a):
    slug = a.category
    url = f"{BASE}/jobs/category/{slug}"
    stated = None if a.no_witness else stated_for(slug)
    st, body = request(url)
    status_of(st, url)
    rows = items(body)
    if not rows:
        die(f"{url}: no Repeater row in the answer — not a category page, or the page changed shape.", EXIT_PARTIAL)
    seen, out, other = [], [], 0
    code0 = rows[0]["category_code"]

    def take(cs):
        nonlocal other
        new = 0
        for c in cs:
            if c["id"] in seen:
                continue
            if c["category_code"] != code0:
                other += 1
                continue
            seen.append(c["id"])
            out.append(row(c, slug))
            new += 1
        return new

    take(rows)
    state = state_of(body)
    rounds, resets, consecutive, last_len = 0, 0, 0, len(rows)
    limit = MAX_ROUNDS if a.all_rounds else max(1, a.rounds or 3)
    while rounds < limit and LOADMORE.split("$")[-1] in body:
        form = dict(state)
        form["__EVENTTARGET"] = ""
        form["__EVENTARGUMENT"] = ""
        form[LOADMORE] = ""
        st, body = request(url, form)
        status_of(st, url)
        rounds += 1
        got = items(body)
        new = take(got)
        # **«Nothing new» is ambiguous in THREE ways here, and only one of them is the end.** Measured on
        # «sewing» 2026-09-23: the list reset at round 7, and rounds 8 and 9 also brought nothing new —
        # not because the list was over, but because the server was CLIMBING BACK through rows already
        # seen (18, then 36, then 54…). A rule counting NEW rows stops mid-climb and loses the rest.
        # The rule that separates the three is the page's OWN row count: it grows on every good round,
        # falls back to the first slice on a reset, and stops growing only at the end.
        page_len = len(got)
        if page_len < last_len and page_len <= SLICE and len(seen) > SLICE:
            # **A reset is a FALL, not a stall** — the count drops back to the first slice. Writing this
            # branch as a growth (which is what it looks like from the far side of the reset) sent the
            # walk through the stall counter instead, and the guard caught it.
            resets += 1
            consecutive = 0
            note(f"round {rounds}: the list RESET to its first slice ({page_len}) — the server dropped the accumulation; climbing back.")
        elif page_len > last_len:
            consecutive = 0
        else:
            consecutive += 1
            note(f"round {rounds}: the page did not grow ({page_len} rows, {th(new)} new) — {consecutive}/{MAX_STALLS}.")
            if consecutive >= MAX_STALLS:
                note(f"round {rounds}: {MAX_STALLS} rounds without growth — the list is over, or the board stopped serving it.")
                break
        last_len = page_len
        state = state_of(body)
        if stated and len(seen) >= stated:
            break
    for r in out:
        print(json.dumps(r, ensure_ascii=False))
    n = len(out)
    bounded = not a.all_rounds
    note(f"{th(n)} emitted for «{slug}» over {th(rounds)} postback(s) of {SLICE} — the site states "
         + (f"{th(stated)} for this category" if stated is not None else "no count for this category")
         + (f": equal." if stated == n else (f"; {th(abs(stated - n))} short." if stated is not None and not bounded else ""))
         + (f"; a BOUNDED read (--rounds {limit}), not the category — the page ACCUMULATES, so a full walk is quadratic in bytes" if bounded else "")
         + (f"; {th(resets)} reset(s) climbed back through" if resets else ""))
    if other:
        note(f"{th(other)} row(s) of another category appeared and were NOT emitted — the postback is supposed to keep the filter.")
    if stated is not None and not bounded and n != stated:
        sys.exit(EXIT_PARTIAL)


def cmd_ad(a):
    die("Melli Kar gives an advert no address of its own: the rows live in a Repeater and open by "
        "`__doPostBack`, so there is nothing to fetch. Use `jobs --category <slug>`; the record carries "
        "the site's own advert id.", EXIT_PARTIAL)


def main(argv=None):
    p = argparse.ArgumentParser(description="Melli Kar (Iran) — a WebForms board walked by postback, whose list RESETS itself; a barren round is replayed, never taken for the end. Issue #631.")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("categories", help="the categories the home page states, with their counts")
    c.set_defaults(fn=cmd_categories)
    s = sub.add_parser("jobs", help="one category, eighteen a postback; «N emitted — the site states M»")
    s.add_argument("--category", required=True, help="a slug from `categories`, e.g. manual-worker")
    s.add_argument("--rounds", type=int, help="how many postbacks (default 3 — a bounded read, said in the output)")
    s.add_argument("--all", dest="all_rounds", action="store_true", help="walk the category out; the page accumulates, so this is expensive and the docstring says how much")
    s.add_argument("--no-witness", action="store_true", help="skip the home page read that fetches the stated count")
    s.set_defaults(fn=cmd_jobs)
    d = sub.add_parser("ad", help="refused, with the reason: an advert has no address of its own here")
    d.add_argument("--url", required=False)
    d.set_defaults(fn=cmd_ad)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
