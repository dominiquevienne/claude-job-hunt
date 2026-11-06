#!/usr/bin/env python3
"""JobSyria (`jobsyria.org`) — the Syrian NGO and humanitarian board, **read through the API its own bundle declares**, because the root is not the enumerator. Issue #1278.

  jobsyria.py list [--max N] [--with-closed]   the adverts the API enumerates, newest first
  jobsyria.py ad --code <code>                 one advert's full record, body included

THE ROUTE WAS NOT GUESSED: THE BUNDLE DECLARES IT. Measured 2026-11-06, the guard on each
exact URL in a turn distinct from the retrieval, one token (`claude-user`), every body
retrieved by `bin/fetch-body.py`, which writes its provenance:

    jobsyria.org/main.fa349d6e6f8df30c.js   976 908 B  ->  apiUrl, baseUrl: api.jobsyria.org/api/
    jobsyria.org/runtime.b49b437fd075e66e.js  5 477 B  ->  the chunk map, 91 chunks
    jobsyria.org/common.deaf22ae30d4e7c5.js  14 107 B  ->  `jobs`, `jobs?size=`, `jobs/show/`

`main.js` carries only `jobs/filters`: the list page is a LAZY chunk, so an adapter built on
the main bundle alone would have concluded there is no list endpoint. The route config names
six chunks for the public shell, all six were guarded and read, and the endpoints are in
`common`. **This is `CLAUDE.md` §3 bis — establish on which host the route lives, from the
bundle — carried one level further, to WHICH FILE of the bundle.**

`allowed=True`, `state=read`, `certain=True`, group `*`, **`rule=None`** on
`api.jobsyria.org/api/jobs`, `/api/jobs/show/<code>` and `/api/jobs/filters`, and on every
`jobsyria.org` asset above: the rules are LUES and write no rule on these paths. **No
`Crawl-delay` for any agent, so 3 s is ours.**

THE ENUMERATOR IS HONOURED, AND THAT IS MEASURED RATHER THAN ASSUMED. `api/jobs?page=P&size=20`
is a Laravel paginator whose `meta` states its own arithmetic, and the discriminant is the
page PAST the end — a parameter that is ignored returns page 1, which reads exactly like a
short board:

    page 1    20 records   current_page 1     from 1     to 20     total 6493   last_page 325
    page 325  13 records   current_page 325   from 6481  to 6493   -> 324 x 20 + 13 = 6493
    page 326   0 records   current_page 326   from None  to None   -> EMPTY, and ZERO overlap
                                                                      with page 1: HONOURED

**THE BOARD STATES TWO TOTALS AND THEY DIFFER BY 45. Neither is our extraction, and they do
not answer the same question.** `api/home` -> `counters.jobs = 6538`, read 19:35:58Z;
`api/jobs` -> `meta.total = 6493`, read 19:33:43Z, two minutes apart. **The witness printed
beside what we emit is `meta.total`, because it is the count the LIST honours** — 325 pages
of 20 that sum to it exactly. `counters.jobs` is named and never used as a denominator: 45
adverts the list does not serve, and WHY is NOT established (drafts, hidden, deleted — from
here they look alike). A ratio built on 6538 would be plausible and false.

**THE LIST SERVES CLOSED ADVERTS, AND PAGE 1 CANNOT SHOW IT.** This is the measurement that
decides the adapter's shape, taken on a SPREAD sample — pages 1, 81, 163, 244, 325 — never
the newest:

    page   1   20 records   status = open   x20       page 244  20 records  status = closed x20
    page  81   20 records   status = open   x20       page 325  13 records  status = closed x13
    page 163   20 records   status = closed x20
    ------------------------------------------------------------------------------------------
    the spread sample: 93 records, 40 `open` and 53 `closed`   -> 43 % open

*Page 1 alone says 100 % open.* An adapter written on it would emit expired vacancies into a
job ledger as live ones — `CLAUDE.md` §4, «un taux pris sur la page 1 n'est pas un taux de
board», on a field that decides whether a record is applicable at all. So `list` emits
`status == "open"` ONLY, `--with-closed` lifts it, and the run PRINTS how many were skipped.
**The discriminant is the `status` FIELD and never the position**: the list is newest-first by
id (page 1 first id 6693, page 325 first id 13), so the open ones happen to cluster at the
front today, and nothing guarantees it tomorrow.

**AND `status` IS NOT A FRESHNESS SIGNAL EITHER -- THAT IS A SECOND AND INDEPENDENT REASON,
found by RUNNING the adapter and not by reading it.** On the same 93 records, against
2026-11-06:

    status    deadline PAST    deadline to come
    closed         53                 0
    open           23 <----           17        -> only 17 of 93 are open AND not expired

Advert 4984 is `status: open` with `deadline: 2026-01-04`, ten months past; adverts 6674-6676
are `open` on page 1 with `deadline: 2026-11-04`, two days past. **So a filter on `status`
alone leaves 58 % of what it keeps expired**, and the two facts are carried and counted apart:
`--with-closed` lifts the first, `--with-expired` the second, and the run prints each with its
own reason. *An ABSENT deadline is never read as an expiry; none of the 93 lacked one, so that
branch is exercised by the suite rather than by the board.*

THE LIST CARRIES EVERYTHING EXCEPT THE BODY, so `list` costs one request per 20 adverts and
not one per advert. Measured on the 93: every record carries `id · code · title · client ·
cities · category · types · published_at · deadline · status · views · monthly_salary ·
application_method · application_link · permanent_link`, and its `translations` carry only
`title`. **`jobs/show/<code>` is what adds `description`, `responsibilities`, `requirements`,
`how_to_apply` and `is_auto_translation`** — its `data.job` has the same keys as a list
record, so the body is the whole difference.

**AND `show` TAKES THE CODE, NOT THE ID.** `jobs/show/6693` returns **404** while
`jobs/show/pFjNxp0Fcq1793862313` returns 200 — and the record says so itself:
`permanent_link` is `www.jobsyria.org/jobs/details/<code>`. A chemin that works masks the one
that does not: the id is right there in the record and would have been the natural argument.

WHAT THE RECORD CARRIES, on 20 full records read across the whole range (pages 1, 81, 163,
244, 325 — first, quarter, median, last of each):

    description / responsibilities / requirements   filled on 19, 20, 20 of 20
    how_to_apply                                    filled on  0 of 20  <- in the schema, never used
    is_auto_translation                             False on 20 of 20   <- no machine translation here
    translations                                    14 `en`, 6 `ar` (the NON-primary language)
    monthly_salary                                  EMPTY on 93 of 93
    application_method                              `link` on 93 of 93

**THE CONTACTS ARE IN ONE FIELD AND THE REDACTION IS PER LINK, NOT PER FIELD.** Zero e-mail,
zero telephone and zero messaging host in the prose of those 20 records — a measured fact with
a denominator, not a protection — and the exposure is entirely in `application_link`: 26 hrefs
across 20 adverts, of which **2 are `mailto:`** that reach a person.

    id 3290  4 hrefs:  europass.europa.eu/create-europass-cv      <- a legitimate route
                       mailto:echo-administration.amman@…         <- reaches a PERSON
                       ec.europa.eu/echo/…/field-network_en       <- a legitimate route
                       ec.europa.eu/echo/…/privacy_statement…     <- a legitimate route
    id 4984  1 href:   mailto:hr.syria@giz.de                     <- reaches a PERSON, and NOTHING else

**Dropping the field because one href is a `mailto:` would destroy three routes the candidate
needs** — the over-redaction that is the one defect whose output does not differ from a
well-conducted discretion. So each href is judged on its own, and the CAUSE travels beside the
name through `reached_a_person`, because `application_link` is ONE name for THREE causes and
only two of them are contacts (`_withheld`, #1238).

**AND `apply_url` IS EMITTED ONLY WHEN EXACTLY ONE http ROUTE SURVIVES.** Measured: 17 of 20
adverts leave exactly one, 1 leaves none (the `mailto:`-only advert), and 2 leave three and
four. When several survive, WHICH of them is the application route is not established — 9 of
20 fields are prose with reference links inside — so the field is ABSENT rather than guessed,
and `application_text` carries the scrubbed prose with every surviving link in it.

THE PHONE PATTERN IS ANCHORED ON THE DIALLING CODE, NEVER ON A DIGIT COUNT, and it is tried in
BOTH directions — because a digit-count rule on a currency is how 113 of 115 salaries were
once destroyed, and the Syrian pound is written in millions. 13 of 13 caught, 20 of 20 left
intact, **Arabic-Indic digits in both columns**:

    CAUGHT   +963 944 123 456 · 00963944123456 · 0944123456 · +963-11-123-456 · 0932 456 789
             ٠٩٤٤١٢٣٤٥٦ · +٩٦٣ ٩٤٤ ١٢٣ ٤٥٦ · 094.412.3456 · 0944<nbsp>123<nbsp>456
    INTACT   1 500 000 SYP · 250 000 SYP par mois · ٢٥٠ ٠٠٠ ل.س · salaire 850000 SYP
             USD 2,500 · article 123 456 789 du code · ISO 9001 · 0.9442 · 963 postes
             reference 2024/963/11 · budget 1 500 000 000 · version 0.9.4 · 2 000 postes

*Residue DECLARED, twice over: `monthly_salary` is empty on 93 of 93, so no salary in this
corpus can collide with the rule — the protection is EXERCISED by the controls above and not
by the board. And the prose carries no contact at all today, so the scrub's green says «there
was nothing there», never «I looked and it is safe».*

**FOUR SURFACES THIS ADAPTER NEVER ASKS, and the reason is per path rather than per prefix.**
The bundle declares them all; `list` and `ad` cannot reach them, and the suite exercises the
refusal directly, because a guard nobody can reach and nobody tests is inert:

    jobs/submit/<id>            acts FOR a person — an application is the candidate's own
    jobs/offsite_applied/<id>   reports an application as made
    jobs/report/<id>            reports an advert in someone's name
    jobs/recommended[/<id>]     bound to a signed-in user
    admin/reports/*             an administration surface that is not ours
    profile/profile · auth/*    someone's account
    tenders                     291 PUBLIC TENDERS — a SEPARATE population, not vacancies

*`tenders` is not refused by the rules and it is not a vacancy: `counters.tenders = 291`, the
board declares it apart, and an adapter that emitted them would write public procurement into
a job register. It is out of SCOPE, which is a different thing from refused, and the guard
says which.*
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import datetime
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
from _withheld import withheld_a_contact

HOST = "api.jobsyria.org"            # the API host the BUNDLE declares, not the apex
SITE = "www.jobsyria.org"            # where `permanent_link` points, never requested
BASE = f"https://{HOST}/api/"
PAGE = 20                            # the `size` measured honoured; `per_page` agrees
DEFAULT_MAX = 40
EXIT_BROKEN, EXIT_GONE, EXIT_PARTIAL = 2, 3, 6
EXIT_REFUSED, EXIT_UNKNOWN = 7, 8

MAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# **ANCHORED on the dialling code, or on the leading 0 of the local form — NEVER on a
# digit count.** The Syrian pound is written in millions, so a length rule on digits
# would eat salaries; `\d` already spans Arabic-Indic digits in Python, but the ANCHORS
# are literals and must carry both scripts, which is why `0` and `963` appear twice.
_D = r"[0-9٠-٩]"
_SEP = r"[\s \-/.]?"
PHONE_RE = re.compile(
    rf"(?:\+|00|٠٠)\s?[9٩][6٦][3٣](?:{_SEP}{_D}){{8,10}}"
    rf"|(?<![0-9٠-٩.,])[0٠](?:{_SEP}{_D}){{9}}(?![0-9٠-٩.,])")

HREF_RE = re.compile(r"""href\s*=\s*["']([^"']+)["']""", re.I)
# **The anchor is rendered as «text (url)» BEFORE the markup is stripped**, or the
# surviving route is lost with the tags and only the link TEXT remains -- which is
# what the field exists to preserve.
A_RE = re.compile(r"""<a\b[^>]*?href\s*=\s*["']([^"']+)["'][^>]*>(.*?)</a\s*>""",
                  re.S | re.I)
HOSTNAME_RE = re.compile(r"[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+")
SCHEMES_FOR_A_PERSON = ("mailto", "tel", "sms", "callto", "whatsapp", "viber", "skype")
MESSAGING = ("wa.me", "api.whatsapp.com", "web.whatsapp.com", "whatsapp.com",
             "t.me", "telegram.me", "telegram.org", "m.me", "messenger.com")
CODE_RE = re.compile(r"[A-Za-z0-9]{8,40}")

# **NEVER ASKED, and the reason is PER PATH.** The first five act for a person or belong to
# someone's account; `tenders` is a separate population and not a vacancy. `list` and `ad`
# cannot reach any of them, so this is defence in depth for a future caller -- and the suite
# exercises it directly, a guard nobody can reach being inert and its green saying nothing.
NEVER_ASKED = (
    (re.compile(r"^/api/jobs/(?:submit|offsite_applied|report)(?:/|$)"),
     "acts FOR a person -- applying, or reporting, is the candidate's own act"),
    (re.compile(r"^/api/jobs/recommended(?:/|$)"),
     "bound to a signed-in user"),
    (re.compile(r"^/api/(?:admin|profile|auth)(?:/|$)"),
     "an account or an administration surface that is not ours"),
    (re.compile(r"^/api/tenders(?:/|$)"),
     "291 PUBLIC TENDERS, a population the board declares apart -- out of SCOPE, which is "
     "not the same as refused: emitting them would write procurement into a job register"),
)

_PACE = Pace(HOST, own=3.0)   # no Crawl-delay written for any agent; 3 s is ours


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[jobsyria] {msg}", file=sys.stderr)


def th(n):
    return f"{n:,}".replace(",", " ")


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
    for motif, pourquoi in NEVER_ASKED:
        if motif.search(parts.path):
            die(f"{url}: never asked -- {pourquoi}", EXIT_REFUSED)
    if parts.netloc and parts.netloc != HOST:
        die(f"{url}: only `{HOST}` is asked -- the route lives on the API host the bundle "
            f"declares, and `{SITE}` serves a shell whose root is not the enumerator",
            EXIT_REFUSED)
    gate(url)
    _PACE.wait()
    req = urllib.request.Request(wire_url(url),
                                 headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            # `decode_body` reads the DECLARATION and SPEAKS on a real replacement; a
            # hand-rolled lossy decode is the probe that cannot go red (#115). **And the
            # guard for it reads the OCTETS of this file**, so naming that form here --
            # even inside a comment, even to forbid it -- reddens the suite: the motif
            # cannot tell a citation from a call, and it is right not to try.
            return r.getcode(), decode_body(r.read(), r.headers)[0]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError) as e:
        die(f"{url}: {type(e).__name__}: {e}")


def fetch(url, quoi):
    """The envelope is `{locale, success, message, data}` and **`success: false` is the API
    REFUSING, not the board being empty** -- it exits 6 rather than printing nothing."""
    code, body = request(url)
    if code == 404:
        die(f"{url}: HTTP 404 -- no such advert; `show` takes the CODE and not the id, and "
            f"the id returns exactly this", EXIT_GONE)
    if code != 200:
        die(f"{url}: HTTP {code}", EXIT_PARTIAL)
    try:
        d = json.loads(body)
    except ValueError as e:
        die(f"{url}: 200 and {len(body)} characters that are not JSON -- {e}; {quoi} "
            f"unreadable, which is not an empty board", EXIT_PARTIAL)
    if not isinstance(d, dict) or "data" not in d:
        die(f"{url}: 200, JSON, and no `data` -- the envelope changed", EXIT_PARTIAL)
    if d.get("success") is False:
        die(f"{url}: the API answered `success: false` ({d.get('message')!r}) -- a REFUSAL, "
            f"not an empty board", EXIT_PARTIAL)
    return d["data"]


def txt(markup):
    if not markup:
        return None
    t = re.sub(r"<br\s*/?>|</p>|</li>|</div>|</h[1-6]>|</tr>", "\n", str(markup))
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip()).strip() or None


def scrub(s):
    """Returns (text, what was ACTUALLY removed) -- the witness is DERIVED, never asserted.

    Zero e-mail and zero telephone in the prose of the 20 records read across the whole
    range, so this returns an empty list on that corpus: its green says «there was nothing
    there», never «I looked and it is safe»."""
    if not s:
        return None, []
    taken = []
    if MAIL_RE.search(s):
        taken.append("email")
        s = MAIL_RE.sub("[e-mail withheld]", s)
    if PHONE_RE.search(s):
        taken.append("telephone")
        s = PHONE_RE.sub("[telephone withheld]", s)
    return (s.strip() or None), taken


def a_person(href):
    """Does this address open a conversation with someone?

    The test is NOT whether it is social: a form, a careers page or a privacy statement is
    where the job is described, so it stays; `mailto:`, `tel:` and a messaging host are how
    you reach a person, so they go. And an address we cannot read as an address is not
    emitted either -- publishing a link nobody can follow is worse than saying there was one.
    """
    parts = urllib.parse.urlsplit(href.strip())
    if parts.scheme in SCHEMES_FOR_A_PERSON:
        return True, True                       # dropped, and it reached a person
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return True, False                      # not an address: nobody is reached
    host = parts.netloc.lower().split("@")[-1].split(":")[0]
    if not HOSTNAME_RE.fullmatch(host):
        return True, False
    if host.startswith("www."):
        host = host[4:]
    if host in MESSAGING:
        return True, True
    return False, False


def application(raw):
    """(text, apply_url, what was withheld, whether that reached a person, how many routes).

    **Judged PER HREF.** One advert of the 20 carries four links of which three are
    legitimate routes and one is a `mailto:`; dropping the field would destroy the three.
    And `apply_url` is emitted only when EXACTLY ONE http route survives -- 17 of 20 -- because
    when several do, which one is the application route is not established, 9 of 20 fields
    being prose with reference links inside."""
    raw = (raw or "").strip()
    if not raw:
        return None, None, None, False, 0
    gardes, etat = [], {"drop": False, "reached": False}

    def anchor(m):
        href, dedans = m.group(1).strip(), (txt(m.group(2)) or "").strip()
        jete, person = a_person(href)
        if jete:
            etat["drop"] = True
            etat["reached"] = etat["reached"] or person
            return f" {dedans} [{'link withheld' if person else 'unusable link'}] "
        gardes.append(href)
        # the URL goes INTO the text: stripping the markup would otherwise keep only
        # «Europass» and lose the route the candidate needs
        return f" {dedans} ({href}) " if dedans and dedans != href else f" {href} "
    raw = A_RE.sub(anchor, raw)
    # an `href` outside an anchor the pattern could pair -- judged the same way, and the
    # count below is of ROUTES and never of attributes
    for href in HREF_RE.findall(raw):
        jete, person = a_person(href)
        if jete:
            etat["drop"] = True
            etat["reached"] = etat["reached"] or person
            raw = raw.replace(href, "[link withheld]" if person else "[unusable link]")
        elif href.strip() not in gardes:
            gardes.append(href.strip())
    corps, _pris = scrub(txt(raw))
    url = gardes[0] if len(gardes) == 1 else None
    return (corps, url, ("application_link" if etat["drop"] else None),
            etat["reached"], len(gardes))


def label(o):
    return (o or {}).get("name") or None


def record(j, detail=False):
    """`detail` says whether the BODY was read -- `list` never claims one it did not fetch."""
    withheld = []
    tr = j.get("translations") or {}
    alt = next(iter(tr.values()), {}) or {}
    corps, pris_c = scrub(txt(alt.get("description")))
    taches, pris_t = scrub(txt(alt.get("responsibilities")))
    exig, pris_e = scrub(txt(alt.get("requirements")))
    comment, pris_h = scrub(txt(alt.get("how_to_apply")))
    app_text, app_url, drop, reached, n_routes = application(j.get("application_link"))
    for n in (pris_c + pris_t + pris_e + pris_h):
        if n not in withheld:
            withheld.append(n)
    if drop and drop not in withheld:
        withheld.append(drop)
    code = j.get("code")
    r = {
        "source": "jobsyria", "country": "SY",
        "ledger_id": f"jobsyria:{code or j.get('id')}",
        "id": j.get("id"), "code": code,
        "url": (j.get("permanent_link") or (f"https://{SITE}/jobs/details/{code}" if code else None)),
        "title": (j.get("title") or "").strip() or None,
        "employer": label(j.get("client")),
        "cities": [label(c) for c in (j.get("cities") or []) if label(c)] or None,
        "category": label(j.get("category")),
        "employment_type": [label(t) for t in (j.get("types") or []) if label(t)] or None,
        "published": (j.get("published_at") or "")[:10] or None,
        "deadline": (j.get("deadline") or "")[:10] or None,
        "status": j.get("status") or None,
        "views": j.get("views"),
        "application_method": j.get("application_method") or None,
        "application_text": app_text,
        "alt_language": alt.get("language") or None,
        # **False on 20 of 20 measured** -- carried because a machine translation is not the
        # employer's words, and the flag is the only thing that would say so.
        "auto_translation": bool(alt.get("is_auto_translation")) if alt else None,
        "description": corps, "responsibilities": taches, "requirements": exig,
        "how_to_apply": comment,
        "detail_read": bool(detail),
        "withheld_fields": withheld or None,
        "language": "ar",
    }
    if app_url:
        r["apply_url"] = app_url
    elif n_routes > 1:
        # the routes are IN `application_text`; which one applies is not established
        r["apply_routes_several"] = n_routes
    salaire = (j.get("monthly_salary") or "").strip()
    if salaire:
        r["monthly_salary"] = salaire
    # The key is ABSENT when nothing that reaches a person left the record. `application_link`
    # is ONE name for THREE causes and only two are contacts, so the CAUSE travels beside it
    # (`_withheld`, #1238); an `else` branch would break the in-suite mutation.
    if withheld_a_contact(r["withheld_fields"], reached_a_person=reached):
        r["contacts_withheld"] = True
    return r


def page(n):
    d = fetch(f"{BASE}jobs?page={n}&size={PAGE}", "the advert list")
    inner = d.get("data")
    meta = d.get("meta") or {}
    if not isinstance(inner, list):
        die(f"{BASE}jobs?page={n}: 200 and `data.data` is {type(inner).__name__}, not a "
            f"list -- the paginator changed", EXIT_PARTIAL)
    return inner, meta


def cmd_list(a):
    borne = a.max if a.max else DEFAULT_MAX
    rows, closed, expire, n_pages, meta = [], 0, 0, 0, {}
    auj = datetime.date.today().isoformat()
    p = 1
    while len(rows) < borne:
        brut, meta = page(p)
        n_pages += 1
        if not brut:
            if p == 1:
                die(f"{BASE}jobs?page=1: 200 and an EMPTY first page while the board states "
                    f"`meta.total = {meta.get('total')}` -- a reading fault and an empty "
                    f"board look alike from here. INDETERMINATE.", EXIT_PARTIAL)
            break                                  # past the end: an empty page IS the answer
        for j in brut:
            # **TWO INDEPENDENT REASONS, counted apart.** The board's own `status` is not a
            # freshness signal: 23 of the 40 `open` records in the spread sample of 93 have a
            # deadline already past. An ABSENT deadline is never an expiry.
            if (j.get("status") or "") != "open" and not a.with_closed:
                closed += 1
                continue
            dl = (j.get("deadline") or "")[:10]
            if dl and dl < auj and not a.with_expired:
                expire += 1
                continue
            rows.append(record(j, detail=False))
            if len(rows) >= borne:
                break
        if p >= (meta.get("last_page") or p):
            break
        p += 1
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    total = meta.get("total")
    note(f"{th(len(rows))} emitted from {n_pages} page(s) of {PAGE} -- walked BY REQUEST "
         f"(--max {borne}), not a shortfall. The board states `meta.total = {th(total)}` over "
         f"{meta.get('last_page')} pages, and that is the count the LIST honours; `api/home` "
         f"states `counters.jobs` separately and the two differ -- the second is never used as "
         f"a denominator here.")
    if not a.with_closed:
        note(f"{th(closed)} record(s) skipped as `status != open`. **The list serves closed "
             f"adverts**: a spread sample of 93 over pages 1/81/163/244/325 was 40 open and 53 "
             f"closed, where page 1 alone reads 100 % open. --with-closed emits them.")
    if not a.with_expired:
        note(f"{th(expire)} further record(s) skipped as their `deadline` is before {auj}. "
             f"**This is a SECOND and independent reason**: the board's `status` does not "
             f"track the deadline -- 23 of the 40 `open` records in that same sample were "
             f"already past theirs, so filtering on `status` alone leaves 58 % expired. "
             f"--with-expired emits them, and an ABSENT deadline is never an expiry.")
    nw = sum(1 for r in rows if r.get("contacts_withheld"))
    nr = sum(1 for r in rows if r.get("apply_url"))
    note(f"a contact was removed from {nw} of {th(len(rows))}; `withheld_fields` names what "
         f"was actually taken, and `application_link` is judged PER HREF so a legitimate route "
         f"survives beside a withheld `mailto:`. {nr} carry `apply_url` (exactly one http "
         f"route survived); where several did, the field is ABSENT and the routes are in "
         f"`application_text`. No body was read: `detail_read` is false on all -- the list "
         f"carries no description, `ad --code` does.")
    note("the tenders population, the application and the admin surfaces were never asked.")


def cmd_ad(a):
    code = a.code.strip()
    if not CODE_RE.fullmatch(code):
        die(f"{a.code!r}: not an advert code. `show` takes the CODE -- the form "
            f"`pFjNxp0Fcq1793862313` that `permanent_link` carries -- and the numeric id "
            f"returns 404")
    d = fetch(f"{BASE}jobs/show/{urllib.parse.quote(code)}", "an advert")
    j = d.get("job")
    if not isinstance(j, dict) or not j:
        die(f"{BASE}jobs/show/{code}: 200 and no `data.job` -- the envelope changed",
            EXIT_PARTIAL)
    r = record(j, detail=True)
    if not r["title"] and not r["description"]:
        die(f"{BASE}jobs/show/{code}: 200 and neither a title nor a description -- the shape "
            f"changed", EXIT_PARTIAL)
    print(json.dumps(r, ensure_ascii=False))
    quoi = [k for k in ("description", "responsibilities", "requirements", "how_to_apply")
            if r.get(k)]
    note(f"{code}: read from `jobs/show/<code>`; body fields present: {quoi or 'none'}; "
         + (f"withheld {', '.join(r['withheld_fields'])}" if r["withheld_fields"]
            else "nothing to withhold")
         + f"; status {r['status']!r}; the application route was never followed.")


def main():
    p = argparse.ArgumentParser(
        description="JobSyria -- the API its own bundle declares enumerates the board; the "
                    "root is not the enumerator, and the list serves CLOSED adverts too. "
                    "Issue #1278.")
    sub = p.add_subparsers(dest="cmd", required=True)
    l_ = sub.add_parser("list", help=f"the newest adverts the API enumerates -- {DEFAULT_MAX} unless --max")
    l_.add_argument("--max", type=int, help=f"how many records to emit ({PAGE} per request, 3 s apart)")
    l_.add_argument("--with-closed", action="store_true",
                    help="emit `status != open` adverts too (53 of a spread sample of 93 are closed)")
    l_.add_argument("--with-expired", action="store_true",
                    help="emit adverts whose deadline has passed (23 of the 40 `open` in that sample)")
    l_.set_defaults(fn=cmd_list)
    ad = sub.add_parser("ad", help="one advert's full record, body included")
    ad.add_argument("--code", required=True, help="the advert CODE, not its numeric id")
    ad.set_defaults(fn=cmd_ad)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
