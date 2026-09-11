#!/usr/bin/env python3
"""Read one host's robots.txt before sweeping it — because on a per-tenant ATS
the policy belongs to the tenant, not to the platform.

**Measured 2026-09-02, and this is why the module exists.** Three Teamtailor
tenants, same platform, same product:

    investengine.teamtailor.com  Content-Signal: search=yes, ai-train=no, ai-input=yes
    oatly.teamtailor.com         Content-Signal: search=yes, ai-train=no, ai-input=yes
    polestar.teamtailor.com      Content-Signal: search=no,  ai-train=no, ai-input=no
    normative.teamtailor.com     Content-Signal: search=no,  ai-train=no, ai-input=no

`teamtailor.md` records the first line **as the platform's policy**. Two of the
four tenants say the opposite, and `ai-input=no` is a tenant asking not to be
read into an AI system — which is what this plugin does, on a user's behalf.

No script in this repository read a tenant's `robots.txt` at runtime before
this one. The policy was read once by a person, written into a board file, and
applied to every tenant of the family afterwards.

**Where this matters and where it does not.** Greenhouse, Lever, Ashby and
Workable serve every tenant from one API host — `boards-api.greenhouse.io`,
`api.lever.co`, `api.ashbyhq.com`, `apply.workable.com` — so one file governs
the family and reading it once is right. Teamtailor, Workday, Taleez,
Personio, umantis, SuccessFactors, Oracle Cloud and iCIMS give each tenant its
own hostname, so each tenant can answer differently, and two of six iCIMS
hosts sampled served `Disallow: /` outright.

Use `verdict(host)` and act on it. It fetches once per host per process.

**`sweep` AND `allowed` HAVE THREE VALUES, NOT TWO** — `True`, `False` and
`None` for *the rules could not be read*. That is issue #118, and it was the
worst defect this module has had:

    nea.gov.kh                  allowed=True   "no rules were read"
    barbadosjobregister.gov.bb  allowed=True   "no rules were read"

`nea.gov.kh` serves Cloudflare's managed block with `User-agent: ClaudeBot /
Disallow: /` — **it closes everything to this project by name**. The module
answered *yes* to it, not because it misread the file but **because it never
got the file**: a timed-out request produced `state: unreadable`, and the
reason said so honestly while the boolean said `True`.

**Measured on the same host within the hour**: when the fetch succeeded,
`allowed: False`, group `claudebot`. When it timed out, `allowed: True`.
**The permission was a function of the network, not of the policy.**

That is #72's pattern on the most sensitive object in the repository: *the
value and its validity travel separately, and only the value crosses the
function*. The value was "no rule matched"; the state was "I could not look";
the caller read the boolean.

**`None` is the fix and it is a small one, because `None` is falsy.** A caller
that writes `if not v["sweep"]: refuse` fails closed, and so does one that
writes `if v["sweep"]: fetch`. **Both naive readings become the safe one**,
which is the only kind of default worth relying on across sixty adapters.

The states a fetch can end in, and they are not interchangeable:

    read         the rules are here
    absent       404 — no file published. **Not a refusal**, and this is the
                 one case where silence really is permission
    refused      403/429/451 — **the host answered, and it said no.**
                 `barbadosjobregister.gov.bb` returns 403 and thirty bytes of
                 "Request is Blocked by Firewall". A server that says
                 *blocked* has replied. Neither a permission nor an absence.
                 **This departs from RFC 9309 on purpose — see below**
    unauthenticated
                 401 — **a credential is demanded for everything, the rules
                 file included.** No file was read and none is presumed:
                 an absence of rules, `certain: False`. Owner's decision of
                 2026-09-09, #201 — see below. **401 and only 401.**
    unreachable  timeout, DNS, TLS, a persistent 5xx, **or a 2xx that is
                 not 200** — unknown, and the only honest answer is that we
                 do not know
    unrecognised 200 with something that is not a rules file — **an open
                 door**, because the host answered and wrote no rule. Still
                 `certain: False`: a body nobody could recognise establishes
                 nothing, and this is a policy applied to that absence, not
                 an absence established

**AND A BODY WE DID NOT RECOGNISE IS NOT AN ABSENCE OF RULES.** Until #128 a
`Content-Type` containing `text/plain` skipped the body check entirely, so
`maliemploi.org`'s Apache *"Access forbidden! / Error 403"* page — served
under that label — was parsed as rules, yielded no `Disallow`, and came back
`allowed: True`, `group: *`, **`certain: True`**. A group invented out of an
error page and then certified.

**The issue read it as the verdict depending on body size**: 976 bytes
accepted, a 5 132-byte React shell rejected. **It is not the size.** The short
one was labelled `text/plain` and never examined; the long one was labelled
`text/html` and was. **The header decided and the body never got a look.**

`certain` exists to say *this is an established absence of rules*. **A guard
that errs by doubting is repairable; a guard that errs by asserting gets
itself believed.**

**That `certain` survives the decision that opened `unrecognised`.** What
changed is the conduct applied to a body without rules, not what is known
about it — the two are separable, and #128 exists because they were once
merged. **A verdict of `allowed: True` with `certain: False` is the honest
shape here**: we are proceeding on a policy, not on a finding, and anything
reading this module can tell the two apart.

**A 404 AND A 202 WITH AN EMPTY BODY ARE NOT THE SAME FACT**, and they shared
a verdict until #125. `algerie.tanqeeb.com` answers **HTTP 202 with zero
bytes**; that landed in `unreadable`, `unreadable` was read as an absence, and
the guard returned `allowed: True` giving the reason *"a 404 is an absence"* —
**a status that never occurred, quoted as the justification.**

A `202 Accepted` says the request was taken and processing is not finished. It
is not a representation of `robots.txt`, and an empty body states nothing. **A
404 is knowledge — the host looked and there is no file.** The three-valued
output added in #118 was right; this branch was not using it.

**And it is the operator, not Algeria.** The Algerian host is the one that
produced the fix; it is not the one that has the behaviour. Four country
subdomains answer identically **and so does the bare apex `tanqeeb.com`**, which
is not a country, so a per-country explanation is ruled out. Measured
2026-09-05, #155, and written up in `shared/boards/tanqeeb.md` — **a dated
observation, not a property of the site.**

**Every reason now quotes the status and the byte count actually observed.** A
silent verdict invites suspicion; **a falsely-motivated one reads like a
verification**, which is worse.

**THE 403 RULE IS A DELIBERATE DEPARTURE FROM RFC 9309, AND SAYING SO IS PART
OF THE FIX.** §2.3.1.3 is explicit: on a status in the 400-499 range a crawler
"MAY access any resources", *as if no robots.txt existed*. **By the letter, a
403 means open.** This module refuses instead, because the letter answers a
question about file availability and a firewall answering *blocked* is
answering a different one — and the cost of being wrong is not symmetric. The
5xx rule is followed as written: unreachable means refuse.

**AND 401 IS BROUGHT BACK TO THE LETTER — owner's decision of 2026-09-09,
#201, applied 2026-09-11.** *«&nbsp;quand le robots.txt nous renvoie une 401,
il faut considérer qu'il s'agit d'une absence de règles et donc, une porte
ouverte au scan&nbsp;».* `api.ashbyhq.com` is the case: an API gateway that
demands a token on every path and makes no exception for `/robots.txt`.
**There is no rules file behind that 401 — there is an authentication in
front of everything**, and a 401 there says nothing about whether the
operator refuses this project. So 401 lands in `unauthenticated`: an open
door with `certain: False`, because nothing was read. **The departure
narrows by one code and keeps the other three**: 403 is a wall that
answered, 429 is «&nbsp;slow down&nbsp;» — opening it would restart a scan
on a host that just said so — and 451 is a legal demand, not a question of
file availability. *A 404 is knowledge; a 401 is ignorance, and ignorance
does not forbid.* A future session reading `refused` without 401 is reading
a decision, not a bug.

**But that departure has a price, and it was measured the day it shipped.**
Two Chilean government portals, the same CloudFront-over-S3 static hosting,
**neither publishing a robots.txt**:

    www.trabajaenelestado.cl/robots.txt   403, 111 bytes of S3 `AccessDenied`
    www.practicasparachile.cl/robots.txt  200, 16 kB of the site's own SPA

**Same absence, opposite verdicts** — refused and permitted — decided by
whether the distribution has a custom error page. On object storage a 403 is
routinely what a *missing key* returns, because listing is not granted; there
is no 404 to give. So `refused` names when a 403 carries a storage-layer error
document, and the sentence says the file may simply not exist. **It still
refuses**: this module does not get to conclude *absent* from a body that
resembles an absence, and `shared/plausible-and-false.md` is about exactly that
inference. It hands a person something to decide with.
"""

import datetime
import hashlib
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from _provenance import vendor_headers

import _tls
import _ua

from _ua import UA

# Keyed on the host **that answered**, never on the string a caller typed —
# see `verdict()`. `_ALIAS` maps what was asked to what answered, so a repeat
# of the same request costs nothing and a different spelling that lands on the
# same host reuses the verdict rather than re-reading the file.
_CACHE = {}
_ALIAS = {}


# The directives a rules file is made of. One of these, at the start of a
# line, is what a `robots.txt` looks like from the inside.
_DIRECTIVE = re.compile(
    r"(?im)^\s*(user-agent|disallow|allow|sitemap|crawl-delay|host|"
    r"content-signal)\s*:")


# A refusal written in prose, not in directives. **Words that mean "you may
# not", never words that mean "it did not work"** — the distinction is the
# whole predicate, and `empleate.gob.es` is why: its error page says *"no ha
# sido posible procesar la operación… inténtelo de nuevo más tarde"*, which is
# a transient failure and the opposite of a refusal.
_REFUSAL_WORDS = re.compile(
    r"access (?:is )?(?:forbidden|denied|restricted)"
    r"|forbidden\b"
    r"|not authori[sz]ed|unauthori[sz]ed"
    r"|permission denied"
    r"|you (?:are|do) not have permission"
    r"|acc[èe]s (?:interdit|refus[ée]|non autoris[ée])"
    r"|zugriff verweigert|nicht erlaubt"
    r"|acceso denegado|prohibido"
    r"|accesso negato|vietato",
    re.I)

# The status a refusal announces about itself. Required alongside the words on
# the short forms, because "forbidden" alone appears in prose that forbids
# nothing. **401 left this set with #201 (2026-09-11)**: a 401 on the rules
# file is an absence of rules, so a 200 body that merely quotes one cannot
# corroborate a refusal either — the same code cannot open the door as a
# status and close it as a word.
_REFUSAL_STATUS = re.compile(r"\b(403|451)\b")


def _looks_like_refusal(body):
    """A body that says *no* without saying it in directives.

    **This exists because `unrecognised` now opens the door.** Since the
    owner's decision of 2026-09-04, a readable 200 carrying no directive is
    treated as an absence of rules — an open door. `maliemploi.org` served an
    Apache error page as its `robots.txt`:

        <title>403 Forbidden</title> … <h1>Access forbidden!</h1><p>Error 403</p>

    **That is in the letter of the decision and outside its spirit.** The
    reasoning quoted was about a host that expressed *nothing*; this one
    expresses a refusal in words, and only its HTTP status lies. #138.

    TWO BOUNDS, AND BOTH ARE MEASURED RATHER THAN IMAGINED:

    **It must not catch an application shell.** `malibaara.com` serves the
    same React shell for `/robots.txt` as for everything else — 5 132 bytes,
    **116 characters of visible text**, *"You need to enable JavaScript to run
    this app."* It carries no refusal word, so it fails here naturally rather
    than by an exclusion list — **a predicate that must name its exceptions
    has not found its rule.**

    **It must not rest on the word `robots`.** `empleate.gob.es`'s error page
    carries `<META NAME='ROBOTS' CONTENT='NOINDEX,NOFOLLOW'>`; a predicate
    searching for that word would be searching for its own answer. Nothing
    here reads it. And that page fails for a second reason worth stating: it
    says *"try again later"*, which is a failure, not a refusal. **Words that
    mean "you may not", never words that mean "it did not work".**

    Returns True only when the body both *names* a refusal and *is* one — the
    status corroborates on the short server templates, and an unambiguous
    phrase stands alone.
    """
    text = body or ""
    if not _REFUSAL_WORDS.search(text):
        return False
    # `403 Forbidden` in a page that also offers a login is still a refusal;
    # `forbidden` inside an article about forbidden characters is not, and the
    # status is what separates them on the bodies measured here.
    if _REFUSAL_STATUS.search(text[:2000]):
        return True
    return bool(re.search(r"access (?:is )?(?:forbidden|denied)"
                          r"|permission denied|acc[èe]s (?:interdit|refus[ée])",
                          text, re.I))


def _looks_like_rules(body):
    """Decide from the body when the server declined to declare a type.

    **The first line settles it and the size corroborates.** Real files
    measured here run 58 to a few hundred bytes and open on a directive; the
    impostors open on `<` and run to 126 015. Markup is checked first because
    a login page can perfectly well contain the word `sitemap`.
    """
    head = (body or "")[:400].lstrip().lower()
    if head.startswith(("<!doctype", "<html", "<?xml", "<")):
        return False
    return bool(_DIRECTIVE.search(body or ""))


# **The body is a property of the host, the verdict is a property of the host
# *and* the agents.** `_CACHE` keys on both, so asking the same file about two
# tokens fetched it twice — and once `allowed()` began consulting `identity()`,
# an ordinary call became three requests for one document. A test counting
# requests caught it. *A cache keyed more finely than the thing it caches
# fetches the same bytes once per key.*
# **The memo lives in `_CACHE`, not beside it.** A second cache was added here
# once and nothing cleared it: 65 tests failed because one case's stub body
# outlived its case. Anything a test must be able to forget goes in the dict
# tests already clear.
_FETCH = "\0fetch"


def _fetch(host):
    """Read one host's file, and report **which host actually answered**.

    `urllib` follows redirects, and a redirect can cross hosts: `ss.ge` sends
    a jobs path to `jobs.ss.ge`, which publishes a **different** rules file —
    62 bytes of `Allow: /` against the apex's 478 bytes of named refusals.
    Returning only the body would hand the caller the right rules under the
    wrong name. Issue #99.
    """
    if (host, _FETCH) in _CACHE:
        return _CACHE[(host, _FETCH)]
    url = f"https://{host}/robots.txt"
    for attempt, timeout in enumerate(_TIMEOUTS, start=1):
        got = _fetch_once(url, host, timeout)
        # **Stamped here, not at each exit.** `_fetch_once` returns from ten
        # places; dating them one by one is a fix per call site, and the
        # eleventh would ship undated. This is the one point they all pass.
        got["read_at"] = _read_at()
        got["attempts"] = attempt
        # **Only an unknown is worth asking again.** `absent`, `refused` and
        # `unreadable` are answers; repeating a question a host has already
        # answered is not diligence, it is load.
        if (got["state"] != "unreachable"
                or not got.get("transient", True)
                or attempt == len(_TIMEOUTS)):
            _CACHE[(host, _FETCH)] = got
            return got
        # Spaced, and jittered so a sweep of many hosts does not retry in
        # lockstep. A slow host used to be a permissive host (#118); it is now
        # a host we wait for, and then decline to guess about.
        time.sleep(_BACKOFF[attempt - 1] * (1 + random.random() * 0.3))
    raise AssertionError("unreachable")


# Three attempts, widening. **The point is not to defeat a firewall — it is
# that a hiccup must not decide a consent question.** Worst case is about a
# minute and a half, once per host per process, against a permission that
# would otherwise be granted by a dropped packet.
_TIMEOUTS = (15, 25, 40)
_BACKOFF = (1.5, 4.0)


def wire_url(url):
    """The address as it goes on the wire: percent-encoded where it must be.

    **`urllib` encodes the request line as ASCII and raises on anything else**,
    so a path carrying `ž`, `é` or `ñ` kills the caller before a byte leaves —
    no HTTP status, no record, a traceback.

    **This lives here because it has now been written THREE times.**
    `adecco.py:100` carried it from 2026-09-03 (*"`côtes-darmor`, `drôme`"*);
    `bin/fetch-body.py` got it on 2026-09-08 after 368 of 423 Montenegrin
    advertisements — 87 % of a board — proved unreachable; and the adapter
    written for that same board hit it again an hour later, because **99
    adapters build their own `urllib.request.Request`**. *A fix at the call
    site does not reach the next call site, and the next one is not found by
    re-reading.*

    **It only acts when it must.** An ASCII path and query come back
    byte-identical, so nothing already working can change — and because
    encoding produces ASCII, applying it twice is a no-op.

    **`%` is kept in `safe`**: a first draft used `quote()`'s default, which
    escapes `%` and turned `%C5%BE` into `%25C5%25BE`. *The bench said so
    before the claim reached the code.*

    And a purely ASCII address is returned **unchanged rather than rebuilt**,
    because a `urlsplit`/`urlunsplit` round trip drops a trailing empty `?` or
    `#`. *Found by mutation: without that early return every other case stayed
    green, since the inner conditions already spare an ascii path.*
    """
    parts = urllib.parse.urlsplit(url)
    if parts.path.isascii() and parts.query.isascii():
        return url
    path = (parts.path if parts.path.isascii()
            else urllib.parse.quote(parts.path, safe="/%"))
    query = (parts.query if parts.query.isascii()
             else urllib.parse.quote(parts.query, safe="=&%"))
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, path, query, parts.fragment))


def full_path(parts):
    """The path **and its query**, as the rules see it.

    `urlsplit` separates them and every guard call but one dropped the second
    half — 54 call sites of 55 asked about `/jobs/boise-id` and then fetched
    `/jobs/boise-id?page=1`. **Those are different questions and `hiringcafe`
    answers them differently**: the first is permitted, the second is refused
    by `Disallow: /*?page=*`, written by hand in both the `?` and `&` form.

    A request went out to that refused path on 2026-09-07 because of this.

    **Every `Disallow` aimed at a query was invisible to this repository**, and
    invisible in the safe-looking direction: the guard returned *permitted* for
    a path the host refuses, and a false permission leaves no trace at all —
    the fetch succeeds, the body is real, nothing looks wrong.

    The one call site that was right, `vieclam24h.py`, is also the one whose
    test exercises a URL carrying a query. *That is the whole difference.*
    """
    path = parts.path or "/"
    return f"{path}?{parts.query}" if parts.query else path


def rules_fingerprint(host):
    """Identify the rules file that decided, without asking for it again.

    Reads what `_fetch` already holds for this host in this process — **no new
    request leaves.** A refusal in the rules has no remote body of its own to
    fingerprint: the request never went out. What can be fingerprinted is the
    file that refused it, and that is what a later reader needs in order to
    tell *the host changed its mind* from *we asked a different question*.

    Carries `final_url` separately because a redirect can cross hosts: `ss.ge`
    sends to `jobs.ss.ge`, which publishes different rules. **A record naming
    only the host asked would attribute one file to another.**
    """
    got = _CACHE.get((host, _FETCH))
    if got is None:
        # **It does not fetch to fill this in.** The caller is on a refusal
        # path; a record is not worth a request, and a guard in this
        # repository counts every request that leaves after a refusal.
        return {"url": f"https://{host}/robots.txt",
                "state": "not-read-in-this-process"}
    body = got.get("body")
    return {
        "url": f"https://{host}/robots.txt",
        # **A host, and named as one.** `_fetch` reports *which host
        # answered*, not a URL; a key called `final_url` holding `ss.ge`
        # would be read as an address by everything downstream.
        "final_host": got.get("final"),
        "state": got.get("state"),
        "status": got.get("status"),
        "bytes": got.get("bytes"),
        "md5": (hashlib.md5(body.encode("utf-8")).hexdigest()
                if isinstance(body, str) else None),
        # **Who answered, and on a rules refusal it is all there is.** When
        # `/robots.txt` itself returns 403 there is no file to fingerprint:
        # `bytes` and `md5` are correctly `None`, and without this the record
        # cannot say whether the host is the tenth carrying a vendor's default
        # or an editor who decided. The response carried these headers; the
        # record used to drop them.
        "vendor": got.get("vendor") or {},
        "read_at": got.get("read_at"),
    }


def _read_at():
    """When the rules were read, in UTC, to the second.

    **A rules refusal is dated by the file that decided it.** Without this the
    only date such a record could carry is the moment somebody thought to
    write it down, which is a fact about us and not about the host.
    """
    return datetime.datetime.now(datetime.timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def _fetch_once(url, host, timeout):
    """Wrapper: **who answered, stamped once for ten exits.**

    A rules refusal is where the question *vendor or editor?* is sharpest and
    where nothing else can be measured — a 403 on `/robots.txt` leaves no file
    to fingerprint, so `bytes` and `md5` are correctly `None` and the headers
    are the only evidence there is. **The response carried them; the record
    threw them away.**

    `_read_once` returns from ten places. Stamping each is a fix per call site
    and the eleventh ships bare, so the headers are captured where a response
    exists — two points — and applied where every return passes.
    """
    seen = {}
    got = _read_once(url, host, timeout, seen)
    if seen.get("vendor"):
        got.setdefault("vendor", seen["vendor"])
    return got


def _read_once(url, host, timeout, seen):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        # **The guard has to reach the file before it can read it.** Two hosts
        # send their leaf without the issuing intermediate, so verification
        # fails here first and the rules become unreadable for a reason that
        # has nothing to do with rules. `_tls` returns `None` for every other
        # host, which means "use the default". Issue #104.
        with urllib.request.urlopen(req, timeout=timeout,
                                    context=_tls.context_for(host)) as r:
            final = urllib.parse.urlsplit(r.geturl()).netloc or host
            ctype = r.headers.get("Content-Type")
            # **`len()` of a decoded string counts characters, and every
            # message below calls the number `bytes`.** On an all-ASCII rules
            # file the two coincide, which is why this survived: the pages the
            # guard reads are usually `robots.txt`. It shows on anything else
            # — `empleate.gob.es` returns an 8 456-byte error page carrying six
            # multi-byte sequences and the guard announced "8 450 bytes".
            # **A wrong unit is worse than no unit**: it invites comparing two
            # numbers that are not the same quantity, which is exactly what
            # happened when a direct read and this message were set side by
            # side and the difference was published as the site changing size.
            # Issue #130.
            seen["vendor"] = vendor_headers(r.headers)
            raw = r.read()
            nbytes = len(raw)
            body = raw.decode("utf-8", "replace")
            status = r.getcode()
            # **A 2xx that is not 200 is not the document.** `202 Accepted`
            # means the request was taken and processing is not finished — it
            # is not a representation of `robots.txt`, and neither is `204`.
            # `algerie.tanqeeb.com` answers **202 with zero bytes**, which
            # used to land in `unreadable` and be reported as *"a 404 is an
            # absence"*: a status that never occurred, quoted as the reason.
            # **A 404 says there are no rules. A 202 with an empty body says
            # nothing at all**, and the two must not share a verdict. #125.
            if status != 200:
                return {"state": "unreachable", "final": final,
                        "status": status, "bytes": nbytes,
                        "why": f"HTTP {status} with a {nbytes}-byte body — "
                               f"a 2xx that is not 200 is not the document, "
                               f"and an empty body states nothing. **This is "
                               f"not an absence**: a 404 would say there are "
                               f"no rules, and this says only that something "
                               f"answered."}
            # A robots.txt that is not text/plain is not a robots.txt — see
            # shared/robots-policy.md. 126 KB of sign-in HTML answered 200 on
            # my.indeed.com, and an Angular shell did the same on kemnaker.
            #
            # **But an absent header is not a declaration of HTML.** The
            # original test was `"text/plain" not in ctype` with `ctype`
            # defaulting to `""`, so a server that declares nothing was
            # rejected without its file being looked at:
            # `hukoomi.gov.qa` serves a valid 468-byte robots.txt with **no
            # `Content-Type` at all** and the plugin called it unreadable.
            # Same asymmetry this module already applies one level up — an
            # absent robots.txt is not a refusal — pushed one level down:
            # **an absence of metadata is not negative metadata.** Issue #96.
            if ctype is None:
                if _looks_like_rules(body):
                    return {"state": "read", "body": body, "final": final,
                            "status": status, "bytes": nbytes,
                            "why": "no Content-Type; the body is a rules "
                                   "file"}
                return {"state": "unreadable", "final": final,
                        "status": status, "bytes": nbytes,
                        "why": f"HTTP {status}, no Content-Type, and the "
                               f"{nbytes} bytes are not a rules file "
                               f"either"}
            # **The body decides, and the header does not.** Until #128 a
            # `Content-Type` containing `text/plain` skipped the body check
            # entirely, so an Apache *"Access forbidden! / Error 403"* page
            # served under that label was parsed as rules, yielded no
            # `Disallow`, and became `allowed: True` with `group: *` and
            # **`certain: True`** — a group invented out of an error page and
            # then certified.
            #
            # The issue read it as the verdict depending on body size: 976
            # bytes accepted, a 5 132-byte React shell rejected. **It is not
            # the size** — the short one was labelled `text/plain` and never
            # examined, the long one was labelled `text/html` and was. Same
            # defect, one branch earlier.
            if not _looks_like_rules(body) and _looks_like_refusal(body):
                # **Asked before `unrecognised`, because since 2026-09-04
                # that conclusion opens the door.** A body that says
                # `Access forbidden! Error 403` expressed a refusal; only its
                # HTTP status says otherwise, and reading it as an absence of
                # rules is the letter of that decision against its spirit.
                # #138.
                return {"state": "refused-in-prose", "final": final,
                        "status": status, "bytes": nbytes,
                        "why": f"HTTP {status}, Content-Type {ctype!r}, "
                               f"{nbytes} bytes, **no directive line — and a "
                               f"refusal written in words**. The host served "
                               f"something that says no while its status says "
                               f"200. **This is not an absence of rules and "
                               f"not a permission**: it is a refusal this "
                               f"module cannot quote as a rule, so it stops "
                               f"and asks for the file to be read by hand."}
            if not _looks_like_rules(body):
                return {"state": "unrecognised", "final": final,
                        "status": status, "bytes": nbytes,
                        "why": f"HTTP {status}, Content-Type {ctype!r}, "
                               f"{nbytes} bytes, and **no `User-agent`, "
                               f"`Disallow` or `Allow` line anywhere in it** "
                               f"— this is not a rules file, whatever it is "
                               f"labelled. A body nobody could recognise is "
                               f"not an absence of rules."}
            return {"state": "read", "body": body, "final": final,
                    "status": status, "bytes": nbytes}
    except urllib.error.HTTPError as e:
        # **At the top of the handler, not in front of one of its exits.** A
        # 403 on `/robots.txt` leaves nothing else to measure — no body to
        # fingerprint, no rules to read — so the headers are the whole
        # evidence, and they must survive whichever branch this takes.
        seen["vendor"] = vendor_headers(e.headers)
        if e.code in (404, 410):
            return {"state": "absent", "status": e.code,
                    "why": f"HTTP {e.code} — no robots.txt published. **This "
                           f"is knowledge**: the host looked and there is no "
                           f"file, which is not the same as a host that did "
                           f"not answer with one."}
        if e.code in (401,):
            # **A credential demanded for everything is not a rule about
            # us.** Owner's decision of 2026-09-09, #201: a 401 on
            # `/robots.txt` is an absence of rules — RFC 9309 §2.3.1.3 as
            # written, on this one code. `api.ashbyhq.com` is the case: an
            # API gateway that wants a token on every path. Nothing was read,
            # so the verdict opens on `certain: False`, not on the 404's
            # `certain: True`. **One-member tuple on purpose**, so the guard
            # that checks the status sets for overlap sees this one too.
            return {"state": "unauthenticated", "status": e.code,
                    "why": f"HTTP {e.code} — the host demands a credential "
                           f"for its rules file, as it does for everything. "
                           f"**No rules file was read and none is presumed**: "
                           f"there is no policy behind this status, there is "
                           f"an authentication in front of every path."}
        if e.code in (403, 429, 451):
            # **The host answered, and it answered no.** Measured on
            # `barbadosjobregister.gov.bb`: 403 and thirty bytes, "Request is
            # Blocked by Firewall". This used to be filed under `unreadable`,
            # whose reason reads *absence of a file is not a refusal* — true
            # of a 404 and false here. Issue #118.
            return {"state": "refused",
                    # **The code, because 403, 429 and 451 are three facts.**
                    # A refusal record read `status: null` beside
                    # `state: refused`, so nothing said whether the host was
                    # blocking us, rate-limiting us, or citing a legal demand.
                    "status": e.code,
                    "why": f"HTTP {e.code} — the host refuses to serve its "
                           f"rules file" + _storage_note(e)}
        # **A 4xx is an answer; a 5xx may be an incident.** The retry is not
        # unconditional — it fires only on `unreachable` — but every status
        # outside the six named above landed there, so a host answering 400
        # was asked the same question three times. It had already replied.
        # Retrying a definitive answer multiplies by the number of
        # indeterminate hosts and tells us nothing new.
        #
        # **The verdict does not change**: a 400 is still `unreachable`, still
        # an unknown, and an unknown is still not probed. Only the number of
        # times we ask changes.
        return {"state": "unreachable", "why": f"HTTP {e.code}",
                "transient": e.code >= 500 or e.code == 408}
    except (urllib.error.URLError, OSError) as e:
        return {"state": "unreachable", "why": str(e)}


def _storage_note(err):
    """Does this 403 look like object storage refusing a **missing** key?

    **A hint for a person, never a conclusion for the module.** On S3 and the
    CDNs in front of it a missing object answers 403 rather than 404, because
    listing the bucket is not granted — so a static site with no robots.txt
    can answer 403 where the identical site with a custom error page answers
    200. Measured on two Chilean government portals the day the 403 rule
    shipped.

    The verdict does not change. **Concluding "absent" from a body that
    resembles an absence is the inference this repository keeps catching**,
    and one error document is not a fact about consent.
    """
    try:
        head_raw = err.read(400)
        head = head_raw.decode("utf-8", "replace")
    except Exception:  # noqa: BLE001 - a body we cannot read tells us nothing
        return ""
    if "AccessDenied" not in head and "NoSuchKey" not in head:
        return ""
    return (". **The body is an object-storage error document** "
            f"({len(head_raw)} bytes, `AccessDenied`/`NoSuchKey`), and on S3 a "
            f"*missing* file answers 403 rather than 404 — so this host may "
            f"simply publish no robots.txt. **That is a hint, not a "
            f"finding**: the refusal stands, because an absence inferred "
            f"from a body that resembles one is not an absence. Read the "
            f"file by hand and record what you saw")


def siblings(host):
    """Does the apex/`www` twin publish a **different rules file**?

    **A diagnostic, run once when a board is written — not on every sweep**,
    and the measurement is why. Across 55 comparable hosts already known to
    this repository, 2026-09-03:

        raw md5 difference          5 of 55
        two real rules files        2 of 55   — flatchr.io, jobindex.dk

    **Three of the five were not two rules files at all**: `job-room.ch`'s
    apex redirects to its home page, `job.id`'s `www` answers 59 KB of HTML,
    and `digitalrecruiters.com` sends both forms to `www.cegid.com`. Comparing
    bytes without asking whether a rules file came back inflated the finding
    by more than double — **the very guard this module applies is the one that
    ad-hoc comparison skips**.

    **So two requests on every host to catch four per cent is disproportionate,
    and the four per cent is not harmless:** `jobindex.dk` serves **47 bytes of
    `User-agent: * / Disallow: /`** on the apex and 4 218 bytes of detailed
    permissions on the `www`. An adapter written against the `www` never sees
    the refusal. Issue #98.
    """
    h = host[4:] if host.startswith("www.") else host
    pair = {}
    for name in (h, "www." + h):
        got = _fetch(name)
        pair[name] = {
            "state": got["state"],
            "final": got.get("final"),
            # **The fetch already measured this correctly**; recomputing it
            # from the decoded string here would reintroduce #130 one level up.
            "bytes": got.get("bytes"),
            "is_rules_file": got["state"] == "read",
            "why": got.get("why"),
        }
    a, b = pair[h], pair["www." + h]
    out = {"pair": pair, "comparable": a["is_rules_file"] and b["is_rules_file"],
           "differ": None, "sweep": {}}
    for name in pair:
        v = verdict(name)
        out["sweep"][name] = v["sweep"]
    if out["comparable"]:
        fa = _fetch(h).get("body") or ""
        fb = _fetch("www." + h).get("body") or ""
        out["differ"] = fa.strip() != fb.strip()
    # **The one that matters is a disagreement about permission**, not about
    # bytes: two files can differ in a comment and agree on everything.
    out["sweep_disagrees"] = len(set(out["sweep"].values())) > 1
    return out



class Partial(dict):
    """A verdict-derived mapping that **refuses to be silent about what it
    does not carry**.

    `allowed()` returns a subset of what `verdict()` builds. Reading a field it
    dropped used to give `None`, and **a `.get()` on a key never carried is
    indiscernible from a key carried whose value is legitimately `None`.**

    That cost twice in one day. `crawl_delay` was missing, so
    `allowed(...).get("crawl_delay")` said *this host asked for nothing* about
    a host asking for ten seconds. Then `group_conflict` was found missing one
    key further along — and that one is worse, because it reports **whether the
    verdict itself is reliable**: a caller saw a clean boolean and never
    learned that two records contradict each other about us.

    **Filling the list case by case repairs instances and leaves the form.**
    The next field added to `verdict()` and forgotten here would fail exactly
    the same way, in silence, in the direction that costs — and a hand-kept
    list is precisely what this defect has already walked through once.

    So absence is loud. A key this mapping knows `verdict()` builds, and does
    not carry, raises on both `[...]` and `.get(...)`. A key nobody knows stays
    an ordinary miss: `.get()` returns its default, because inventing an error
    for an unknown name would break every caller probing for optional keys.
    """

    __slots__ = ("_known",)

    def __init__(self, *a, known=(), **kw):
        super().__init__(*a, **kw)
        self._known = frozenset(known)

    def _complain(self, key):
        return KeyError(
            f"{key!r} is built by `verdict()` and not carried by `allowed()`. "
            f"**This is not `None` — it is a field nobody passed on.** Read it "
            f"from `verdict(host)`, or add it to `CARRY` if a caller needs it "
            f"at the gate. *Returning `None` here is how a host asking for ten "
            f"seconds came back as a host asking for nothing.*")

    def __missing__(self, key):
        if key in self._known:
            raise self._complain(key)
        raise KeyError(key)

    def get(self, key, default=None):
        if key not in self and key in self._known:
            raise self._complain(key)
        return super().get(key, default)


def verdict(host, agents=None):
    """What this host says about being read.

    Returns a dict with **`sweep`, which is `True`, `False` or `None`**,
    `reason`, and the raw signals. `None` means the rules could not be read —
    see the module header and #118. It is falsy, so a caller that never heard
    of the third state still fails closed.

    Conservative in one direction only: a blanket `Disallow: /` for the group
    that binds us, a `Content-Signal` saying `ai-input=no`, or **a host that
    answered 403 to its own rules file**, returns `sweep: False`. An **absent**
    file still returns True with the reason named — that is the one silence
    that really is permission, and this module must not invent a refusal from
    a 404.

    **That claim used to be false in the one place it mattered.** The
    `Content-Signal` was read with `re.search`, which stops at the first
    occurrence — so on a file carrying two, a refusal in the second was never
    seen and the module returned `sweep: True`. **The error went towards
    permitted, on the only signal here that expresses a refusal of consent.**
    Every occurrence is read now, restrictions are unioned, and a file that
    contradicts itself says so in `content_signal_conflict` instead of being
    summarised by whichever line the CDN happened to inject first. Issue #98.

    `host` is the host that **answered**; `requested_host` is what the caller
    asked for. They differ whenever a redirect crossed hosts, and the file
    read is the answering host's — see the cache note below. Issue #99.
    """
    # **Keyed on the host that answered, not on the string that was typed.**
    # `urllib` follows redirects across hosts, so `verdict("ss.ge")` from one
    # caller and from another aiming at a path that lands on `jobs.ss.ge`
    # would share one entry — and those two hosts publish different files.
    # `_ALIAS` remembers what a spelling resolved to, so a repeat costs
    # nothing. **A spelling never seen before still costs one request**: there
    # is no way to learn a redirect without following it, and this fixes the
    # verdict being reused, not the fetch. Issue #99.
    # `OUR_AGENTS` is defined below this function, so the default is resolved
    # here rather than at definition time.
    # **`OUR_AGENTS` stays the default HERE, and that is not an oversight.**
    #
    # `verdict()` reports *what this file says about us* — six names a site
    # may use, including four we never send. That reporting is what
    # `ARefusedNameIsNotAlwaysANameWeSend` exists for, and narrowing this
    # default to the one token we present destroyed it: twelve cases went red
    # because the module could no longer say *this host names `anthropic-ai`
    # and we never send that*.
    #
    # **Reading and deciding are two questions.** `allowed()` decides and is
    # aligned to the token as of 2026-09-07; `verdict()` reads. The
    # consequence is named rather than hidden: `verdict(host)["sweep"]` is
    # still the union answer, so a caller using it to decide a sweep gets the
    # conservative one. That is a real gap and it is written down, not a
    # coincidence that happens to be safe.
    agents = tuple(agents) if agents else OUR_AGENTS
    # **The cache key carries the agents.** Since 2026-09-05 this function is
    # asked the same host under one token and then the other, and a key of the
    # host alone would hand the second caller the first one's verdict — the
    # exact shape of a silent wrong answer, and it would have arrived with a
    # correct-looking reason attached.
    key = (agents,)
    if (host, key) in _ALIAS:
        return _CACHE[(_ALIAS[(host, key)], key)]
    got = _fetch(host)
    final = got.get("final") or host
    if (final, key) in _CACHE:
        _ALIAS[(host, key)] = final
        return _CACHE[(final, key)]

    def _note(result):
        """Say which host these rules came from, on **every** way out.

        This note used to be written into `reason` right after the dict was
        built — and **four of the five branches below overwrite `reason` a few
        lines later**, so it survived only in the one case that happens not to
        set it, which is the most permissive case of all. The verdict was named
        for one host and computed on another, and nothing in its output said
        so: `iqjscout.com` came back `allowed=True` on rules read from
        `yadanoo.com`, and then answered 403. **A false yes leaves no more
        trace than a false no.**

        Prefixed here instead, where nothing downstream can clobber it.
        """
        if final == host:
            return result
        head = (f"**These rules were read from {final!r}, not from {host!r}** "
                f"— the request was redirected, and the two hosts do not "
                f"necessarily publish the same file.")
        result["reason"] = (f"{head} What follows is a verdict about "
                            f"{final!r}.\n  " + result["reason"]
                            if result.get("reason") else head)
        return result

    def _keep(result):
        _note(result)
        _CACHE[(final, key)] = result
        _ALIAS[(host, key)] = final
        return result

    out = {"host": final, "requested_host": host, "sweep": True,
           "reason": None, "content_signal": None, "crawl_delay": None,
           "ignored": [], "sitemaps": [], "state": got["state"],
           "attempts": got.get("attempts"), "certain": True,
           "status": got.get("status"), "bytes": got.get("bytes")}
    if got["state"] == "refused":
        # **A reply, not a silence.** `barbadosjobregister.gov.bb` answers 403
        # with "Request is Blocked by Firewall": a host that will not serve
        # the document setting out what may be read has not granted anything,
        # and a host blocking this request will block the next one. Issue #118.
        out["sweep"] = False
        out["reason"] = (
            f"{got.get('why')}. **This is not an absent file and not an "
            f"unreadable one — the host replied, and the reply was no.** "
            f"Nothing here permits a sweep. Not swept.\n"
            f"  **And since #120 this plugin declares `{_ua.TOKEN}`, so the "
            f"refusal may be a wall reacting to that rather than a policy the "
            f"operator wrote.** Measured on `emploi.batiactu.com` the day the "
            f"declaration shipped: 289 bytes of `robots.txt` to a browser "
            f"string, 403 to ours. **This module will not find out by asking "
            f"again under another name** — `shared/robots-policy.md`: do not "
            f"rotate, do not retry with another agent string. Read the file "
            f"by hand in the user's own browser and record what it says.")
        return _keep(out)
    if got["state"] == "refused-in-prose":
        # **Not `unrecognised`, which opens; not `refused`, which is a 403.**
        # The host answered, and what it answered was no — in prose. `sweep`
        # is False because it said no; `certain` is False because it said so
        # in words this module cannot parse into a rule.
        out["sweep"] = False
        out["certain"] = False
        out["reason"] = (
            f"{got.get('why')} **A refusal in prose is still a refusal.** "
            f"Read the file by hand and record what it says; if it turns out "
            f"to be a server fault rather than a policy, that is a fact worth "
            f"writing down, and it is not one this module may assume.")
        return _note(out)
    if got["state"] == "unrecognised":
        # **A body that says nothing does not say no.** The host answered, the
        # answer was readable, and it expressed no rule — so there is nothing
        # to obey, and refusing lends it a wish it never wrote. The owner's
        # reasoning, quoted: *"l'absence de règle est une porte ouverte.
        # Rappel : le fichier robots.txt est un souhait de l'hôte (qui bien
        # souvent est autogénéré et non vérifié)"*.
        #
        # **This is the counterpart of a rule this repository already applies
        # in the other direction**: `robots-policy.md` holds that a CMS
        # default binds even when nobody meant it — Honduras, whose file is
        # copied from Google's documentation. If an unmeant refusal binds,
        # an unwritten one cannot.
        #
        # **`certain` stays False, and that is not a detail.** #128's whole
        # point is that a body we could not recognise *establishes* nothing;
        # what changed is the conduct applied to that absence, not the
        # epistemics of it. Setting `certain: True` here would re-create the
        # seventh defect — a group invented out of an error page and then
        # certified — through the front door.
        out["sweep"] = True
        out["certain"] = False
        out["reason"] = (
            f"{got.get('why')} **The host answered and expressed no rule, so "
            f"there is none to obey** — an absence of rules is an open door, "
            f"and a `robots.txt` is a wish, often generated and never read by "
            f"anyone. **This is a policy applied to an absence, not an "
            f"absence established**: `certain` stays false. It is emphatically "
            f"*not* \u201cwe proceed when we do not know\u201d — a fetch that "
            f"failed and a 403 both still stop this module cold.")
        return _note(out)
    if got["state"] == "unauthenticated":
        # **#201, 2026-09-09.** An open door, like `unrecognised`, and for a
        # kindred reason: the host expressed no rule. `certain` is False
        # because nothing was read — this is a policy applied to an
        # absence, not an absence established, and the 404's `certain: True`
        # does not travel here. **The scope is 401 and only 401**: 403, 429
        # and 451 are still `refused` above, and a test pins each code to
        # its state by name.
        out["sweep"] = True
        out["certain"] = False
        out["reason"] = (
            f"{got.get('why')} **An absence of rules is an open door** — "
            f"owner's decision of 2026-09-09 (#201), and RFC 9309 §2.3.1.3 "
            f"as written on this one code. `certain` stays false: a 404 is "
            f"knowledge, a 401 is ignorance, and ignorance does not forbid.")
        return _keep(out)
    if got["state"] == "unreachable":
        # **The third state, and the reason this module was rewritten.** Not
        # a refusal and emphatically not a permission: `nea.gov.kh` closes
        # everything to `ClaudeBot` by name and used to be swept whenever the
        # request timed out. **A host we could not reach is a host we know
        # nothing about.** Issue #118.
        out["sweep"] = None
        out["certain"] = False
        out["reason"] = (
            f"robots.txt could not be read after {got.get('attempts')} "
            f"attempt(s): {got.get('why')}. **This is an unknown, not a "
            f"permission and not a refusal.** A host that names this project "
            f"and closes everything to it looks exactly like this from here "
            f"— it did, on `nea.gov.kh`. Retry later, or read the file by "
            f"hand and record what it says." + _resolver_note(got.get("why")))
        # **Deliberately not cached.** Caching a transient failure poisons a
        # whole run with an unknown that a second request would have resolved;
        # the three attempts above have already paid for patience.
        return _note(out)
    if got["state"] != "read":
        # What is left is `absent` and `unreadable`, and they are not equally
        # solid. **An absence is knowledge**: no file, no rules, nothing to
        # respect. A body that is not a rules file is not — a login wall says
        # nothing about consent, so the verdict stands but `certain` does not.
        out["certain"] = got["state"] == "absent"
        out["reason"] = f"robots.txt {got['state']}: {got.get('why')}"
        return _keep(out)

    body = got["body"]
    # **Every occurrence, not the first.** `re.search` stops at one, and which
    # one comes first is an accident of injection order — a file can carry the
    # origin's signal and a CDN's. Measured on `www.mtss.go.cr`: two
    # `Content-Signal` lines that disagree, one permitting `use=reference` and
    # one silent about it. **There is no resolution rule for this convention**,
    # so nothing is arbitrated: the restrictions are unioned and the
    # disagreement is reported. Issue #98.
    signals = [m.group(1).strip() for m in
               re.finditer(r"(?im)^\s*Content-Signal\s*:\s*(.+)$", body)]
    if signals:
        out["content_signal"] = signals
        out["content_signal_conflict"] = len(set(signals)) > 1
        refusing = [x for x in signals
                    if re.search(r"ai-input\s*=\s*no", x, re.I)]
        if refusing:
            out["sweep"] = False
            more = (f" The file declares {len(signals)} `Content-Signal` "
                    f"lines and they do not agree; **a refusal in any of them "
                    f"is a refusal**, because no convention says which wins."
                    if out["content_signal_conflict"] else "")
            out["reason"] = (f"this host publishes `Content-Signal: "
                             f"{refusing[0]}`. `ai-input=no` is the operator "
                             f"asking that its content not be read into an AI "
                             f"system, which is what a sweep does. Not "
                             f"swept.{more}")
            return _keep(out)

    # **The group that binds us, which may not be `*`.** Until #116 this read
    # `*` and never consulted a record naming this project — so a file that
    # opened `*` and closed `ClaudeBot` was reported open, and the error went
    # towards permitted on the one kind of file that addresses us by name.
    token, dis, allow, matched = group_for(body, agents)
    out["crawl_delay"] = delay_for(body, agents)
    out["sitemaps"] = sitemaps_for(body)
    out["ignored"] = ignored_for(body)
    # **An empty `Disallow:` is not a refused path — it is how a file says
    # *nothing is closed*.** `_match_len` has known that since #101, and a
    # test pins it; `verdict()` did not, and counted the empty string as a
    # rule. `employtt.gov.tt` publishes 26 bytes — `User-agent: *` and a bare
    # `Disallow:` — and the sentence came out "**this host refuses 1 path(s)
    # to `*` ... : **" with nothing after the colon. The permission was right
    # and the account of it was wrong, on the most permissive file there is.
    dis = [d for d in dis if d]
    out["disallow"] = dis
    out["allow"] = allow
    out["group"] = token
    out["groups"] = matched
    out["group_conflict"] = _records_disagree(body, matched)
    # **#180.** Carried so a caller sees what the file says and no group
    # claims, without re-parsing the body it never receives.
    out["orphan_rules"] = orphan_rules(body)
    out["has_star_group"] = bool(_groups_named(body, ("*",)))
    # **Every agent token the file names**, so a reason can say whose rules
    # these are instead of asserting there are none. `kariera.mk` names
    # `Googlebot-Image` and nothing else: no `*`, no record for us — and the
    # first draft of the #180 message called that "no `User-agent:` line",
    # which was false three times in one sentence.
    out["agents_named"] = sorted(
        {a for agents, _r in _groups(body) for a in agents if a})
    if "/" in dis:
        # **`sweep` follows the resolution at the root, not the bare presence
        # of `Disallow: /`.** #153.
        #
        # A group carrying both `Allow: /` and `Disallow: /` resolves — by the
        # tie rule this module already applies in `allowed()` — to *everything
        # permitted*. Reporting `sweep: False` there made one file give two
        # opposite answers: `allowed(host, path)` said yes to every path while
        # `verdict()` said the host could not be swept. **An incoherence
        # between two of our own answers is worse than either choice**, and the
        # conservative one was indistinguishable from an oversight because no
        # line said it was a choice.
        #
        # The distinction this preserves: a whitelist — `Allow: /*/jobs/`
        # beside `Disallow: /`, as `bebee.com` publishes — still reports
        # `sweep: False`, because `/` itself is refused and there is no list to
        # sweep. Only the self-contradicting group changes, and
        # `northcyprus.cv` is the case that showed it.
        root_a = max((_match_len(a, "/") for a in allow), default=-1)
        root_d = max((_match_len(d, "/") for d in dis), default=-1)
        out["sweep"] = root_a >= root_d >= 0
        if out["sweep"]:
            out["reason"] = (
                f"`{final}` carries both `Allow: /` and `Disallow: /` for "
                f"`User-agent: {token}`. **The tie goes to `Allow`** — the rule "
                f"this module applies to every other path — so every path is "
                f"permitted and the host sweeps. *A file that contradicts "
                f"itself is read the same way here as anywhere else, rather "
                f"than being treated as unreliable in one place and resolved "
                f"in another.*"
                + _named_note(matched, out.get("group_conflict")))
        elif allow:
            # **`sweep: False` never meant "no path is open", and saying so
            # was half the defect.** A group carrying `Allow:` lines beside
            # `Disallow: /` is a whitelist: sweeping blindly stays refused,
            # because there is no list of what may be fetched — but the named
            # families are open, and `allowed(host, path)` is the question that
            # gets a real answer. Issue #152.
            fams = ", ".join(f"`{a}`" for a in allow[:6])
            more = f" and {len(allow) - 6} more" if len(allow) > 6 else ""
            out["reason"] = (
                f"`{final}` closes the site to `User-agent: {token}` "
                f"**except {len(allow)} named path famil"
                f"{'y' if len(allow) == 1 else 'ies'}**: {fams}{more}. "
                f"**This is a whitelist, not a wall** — a blind sweep has no "
                f"list to sweep and stays refused, but ask `allowed(host, "
                f"path)` before concluding that any particular path is closed."
                + _named_note(matched, out.get("group_conflict")))
        else:
            out["reason"] = (
                (f"this host closes everything to `User-agent: {token}` — "
                 f"**a refusal that names this project**, not a general "
                 f"policy. Not swept." + _fetch_note(token)
                 if token != "*" else
                 "this host's robots.txt is `User-agent: * / Disallow: /` — "
                 "everything closed, evenly. Not swept.")
                + _named_note(matched, out.get("group_conflict")))
    elif dis:
        # **`sweep` answers "is this host closed in one block". It cannot
        # answer for a path, and it must not look as though it does.**
        # `empleate.gob.hn` refuses `/Vacantes/` and `/Candidatos/` to `*` —
        # the vacancies themselves — while `"/"` is absent, so `sweep` is
        # True and used to be the whole answer. Issue #101.
        out["reason"] = (
            f"this host refuses {len(dis)} path(s) to `{token}` and not the "
            f"site as a whole: {', '.join(dis[:4])}. **`sweep: True` means it "
            f"is not closed in one block; it does not mean the path you want "
            f"is open.** Call `allowed(host, path)` before fetching one."
            + _named_note(matched, out.get("group_conflict")))
    elif matched:
        # **The third formulation, and it had no words at all.** A host that
        # names this project and permits it left `reason` at `None` —
        # indistinguishable from a file where nothing matched. They are not
        # the same fact: `taleez.com` writes `User-agent: ClaudeBot / Allow:
        # /` under a `*` group that refuses twelve paths. **That is explicit
        # consent, not the absence of a refusal**, and it is also the reason
        # those twelve refusals do not apply here — which is worth saying
        # before someone later "corrects" an adapter into obeying them.
        # Issue #117.
        star_dis = _star_group(body)[0]
        others = (f" The `*` group refuses {len(star_dis)} path(s) — "
                  f"{', '.join(star_dis[:3])} — and **those do not bind us**, "
                  f"because a record naming us takes precedence over `*`."
                  if star_dis else "")
        out["reason"] = (
            f"this host **names this project and permits it**: "
            f"`User-agent: {token}` with no `Disallow`. That is consent "
            f"written down, not silence.{others}"
            + _named_note(matched, out.get("group_conflict")))
    return _keep(out)


# **Our own tokens, declared here and nowhere else.** A module that decides
# consent must not depend on a user-agent string assembled somewhere else: an
# adapter that changes its `UA` would silently change which rules bind. These
# are the names this project is addressed by, gathered from the files that name
# them — `linkedin.com` refuses `Claude-User` by name, Cloudflare's managed
# block names `ClaudeBot`. Issue #116.
# **The two tokens this project can actually present as.** The other names in
# `OUR_AGENTS` are names a site may use *about* us; these are the two a request
# can carry. The distinction matters since the owner's decision of 2026-09-05.
FETCH_TOKENS = ("claudebot", "claude-user")


OUR_AGENTS = ("claudebot", "claude-web", "claude-user", "claude-searchbot",
              "anthropicbot", "anthropic-ai")


def _groups(body):
    """Every record in the file: `(agents, [(kind, value), …])`.

    Consecutive `User-agent` lines form one record; a record ends at the first
    `User-agent` that follows a directive.
    """
    out, agents, rules = [], set(), []
    for line in (body or "").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        k, _, v = line.partition(":")
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            if rules:                       # a directive closed the last one
                out.append((agents, rules))
                agents, rules = set(), []
            agents.add(v.lower())
        elif k in ("disallow", "allow"):
            rules.append((k, v))
        elif k == "crawl-delay":
            # **A directive, not a remark.** `ejob.az` names `ClaudeBot` to
            # give it `Crawl-delay: 5` and forbids it nothing — named,
            # allowed, conditioned. Dropping it here made the delay
            # unreadable to every caller, so the one host that had asked for
            # one was answered at whatever rate the caller happened to use.
            rules.append((k, v))
    if agents or rules:
        out.append((agents, rules))
    return out


def _named_note(matched, conflict):
    """What to add when more than one record of ours applies. Issue #117."""
    if len(matched) < 2:
        return ""
    names = ", ".join(f"`{n}`" for n in matched)
    if not conflict:
        return (f" The file names {len(matched)} of this project's tokens "
                f"({names}) and says the same thing to each.")
    return (f" **The file names {len(matched)} of this project's tokens "
            f"({names}) and does not answer them alike.** The refusals of all "
            f"of them apply and only the permissions common to all of them "
            f"do: a permission one record grants and another withholds is not "
            f"one this project has.")


def _records_disagree(body, matched):
    """Do the records naming us say different things?

    **Worth reporting rather than smoothing over.** `www.linkedin.com` refuses
    this project in four records and permits it in a fifth; a caller that only
    ever sees the merged answer cannot tell that from a file where every
    record agrees. Issue #117.
    """
    if len(matched) < 2:
        return False
    seen = set()
    for n in matched:
        d, a = [], []
        for names, rules in _groups(body):
            if n not in names:
                continue
            for kind, value in rules:
                (d if kind == "disallow" else a).append(value)
        seen.add((tuple(sorted(set(d))), tuple(sorted(set(a)))))
    return len(seen) > 1


# **A name that does not resolve here has not been shown to be gone.** This
# module inherits the system resolver, so a resolution failure is a fact about
# *tool + resolver*, not about the host. Reported by another session on
# 2026-09-05: `skillingpakistan.gov.pk` came back unresolvable, and the reading
# went to "the host has disappeared" — with a dissociation that seemed to prove
# it, two control hosts resolving and the target not.
#
#     via 1.1.1.1   skillingpakistan.gov.pk   NOERROR   A = 203.124.43.206
#     via 8.8.8.8   skillingpakistan.gov.pk   SERVFAIL
#                   jobs.gov.pk               SERVFAIL   <- not specific to it
#
# **The host was alive.** The message was accurate and was still read as a
# statement about the world, so the sentence that was missing is added here
# rather than left to the reader.
_RESOLUTION = ("nodename nor servname", "name or service not known",
               "temporary failure in name resolution", "getaddrinfo",
               "servfail", "nxdomain")


def _resolver_note(why):
    if not any(k in (why or "").lower() for k in _RESOLUTION):
        return ""
    return (" **This one is a DNS failure, and DNS is the resolver's answer, "
            "not the host's.** Check the name against a second resolver before "
            "concluding anything about the host — a host that resolves "
            "elsewhere is reachable and this verdict is about the path here. "
            "There is deliberately no flag to override it: a name that resolves "
            "on a second resolver simply runs again.")


def _fetch_note(token):
    """Whether the refused group names a token a request from here can carry.

    **A name for this project is not the same as a name we send.** `OUR_AGENTS`
    holds six; `FETCH_TOKENS` holds the two a request can present as. A file
    that refuses `anthropic-ai` and names nothing else has written a refusal
    this project is bound by under our restrictive reading — and has *not*
    named either token we could arrive with.

    The distinction was invisible until 2026-09-05, when `albaniajobs.al` came
    back as `a refusal that names this project` and the sentence was copied
    onto a country page as *the one refusal actually written by an editor*.
    True as written, and it reads as though the editor had shut the door on us
    by name. **The verdict was right and the sentence it handed over was not**,
    which is the failure mode a reason line exists to prevent.

    This changes no verdict. `allowed()` stays restrictive, because whether a
    refusal aimed at a sibling name binds us is the owner's arbitration and not
    this module's — see `nos-agents-lecture-restrictive.md`. It changes only
    what the refusal is reported to say.
    """
    if token in FETCH_TOKENS:
        return (f" **`{token}` is one of the two tokens a request from here can "
                f"present**, so this refusal names an agent we would arrive as.")
    return (f" **`{token}` is a name for this project that this project never "
            f"sends.** The two tokens a request can carry are "
            f"`{'` and `'.join(FETCH_TOKENS)}`, and neither is named here — so "
            f"the refusal binds us by our restrictive reading, not by the "
            f"editor having named an agent we could arrive as. "
            f"`identity()` says which token the rules leave open.")


# **What the parser acts on.** `_DIRECTIVE` above lists what a rules file is
# made of — seven names — and `_groups()` keeps four of them. That gap was
# silent: a host declaring `Sitemap:` got the same verdict, with the same
# fields, as a host declaring nothing, and **a `.get()` on a field never
# parsed returns `None` for ever, which reads exactly like a host that asked
# for nothing.** Measured 2026-09-05 on 187 rules bodies held across three
# sessions: `sitemap` in 82 (43.9 %), `host` in 3, `clean-param` in 1.
_ACTED_ON = ("user-agent", "disallow", "allow", "crawl-delay",
             "sitemap")


def ignored_for(body):
    """Directives present in `body` that this module does not act on.

    **Names the gap rather than closing it.** Whether to obey `Clean-param` or
    to read a declared `Sitemap` is a decision; being unable to see that the
    host wrote one is a defect. This separates the two, which from outside read
    identically — *a directive we ignore for want of parsing it* and *a
    directive we see and choose not to follow* produce the same silence.

    `content-signal` is excluded: it is read, by `verdict()`, elsewhere.
    """
    present = {m.group(1).lower() for m in re.finditer(
        r"(?im)^\s*([A-Za-z][A-Za-z0-9_-]*)\s*:", body or "")}
    return sorted(present - set(_ACTED_ON) - {"content-signal"})


def sitemaps_for(body):
    """The sitemaps a host declares, **as written**, in file order.

    **`Sitemap` is not a group member** (RFC 9309 §2.2.1): it belongs to no
    `User-agent` record and applies to every client. So it is read straight
    from the file and never filed under a token — putting it under the record
    that happens to precede it would invent an addressee the host did not name.

    **The URLs come back exactly as the host wrote them, host included.** A
    declaration may point at another host and *that is the useful case*:
    `merojob.com` declares its sitemaps on `sg.merojob.com`, and a path like
    `sitemap-job_post-1.xml.gz` is covered by no verdict taken at the root.
    Rewriting these to the host whose `robots.txt` was read would erase exactly
    the information worth having.

    **Reading a declaration authorises nothing.** The guard is still taken on
    the exact URL, host included, before any fetch — `allowed(host, path)` on
    what this returns, in a separate turn from the retrieval. This function
    makes no request and must not be read as permission.

    Measured 2026-09-05 on 187 rules bodies held across three sessions: **82
    declare at least one sitemap, 43.9 %**, and until today not one of those
    declarations was read. A session wanting a sitemap was reduced to trying
    `/sitemap.xml` or doing nothing, while the host was saying where it is.
    """
    out, seen = [], set()
    for line in (body or "").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        k, _, v = line.partition(":")
        if k.strip().lower() != "sitemap":
            continue
        v = v.strip()
        if not v or v in seen:
            continue
        seen.add(v)
        out.append(v)
    return out


def delay_for(body, agents=OUR_AGENTS):
    """The `Crawl-delay` that binds us, in seconds, or `None`.

    **The maximum across every record that names us**, and the `*` record only
    when no record names us — the same shape as the rest of this module: where
    records disagree, the reading that asks less of the host wins. A record
    naming us with no delay does not cancel one set by another record naming
    us; it simply contributes nothing.
    """
    ours, star = [], []
    for names, rules in _groups(body):
        vals = [v for k, v in rules if k == "crawl-delay"]
        if not vals:
            continue
        for raw in vals:
            try:
                d = float(raw)
            except ValueError:
                continue
            if d <= 0:
                continue
            (ours if names & set(agents) else
             star if "*" in names else []).append(d)
    pool = ours or star
    return max(pool) if pool else None


def group_for(body, agents=OUR_AGENTS):
    """The rules that bind **us** — across *every* record that names us.

    **This is the half `verdict()` never looked at.** It evaluated `*` and
    never consulted the group that names us — so on a file reading

        User-agent: *
        Allow: /
        …
        User-agent: ClaudeBot
        Disallow: /

    it answered *allowed*, **on the one category of file that addresses us
    explicitly**. And the error went towards permitted. Issue #116.

    **THE FIRST FIX PICKED THE LONGEST TOKEN, AND THAT WAS WRONG TOO.**
    Measured across 70 hosts, 2026-09-03: three name a token of ours, and
    **`www.linkedin.com` names five and does not answer them alike** —
    `ClaudeBot`, `Claude-Web`, `Claude-User` and `anthropic-ai` all get
    `Disallow: /`, while `Claude-SearchBot` gets a path list and no blanket
    refusal. `claude-searchbot` is the longest of the five, so the module
    selected **the one permissive record out of five refusals** and answered
    `sweep: True` on a host that closes itself to this project by name, four
    times over. **The fifth defect in this module, and the fifth going towards
    permitted.**

    RFC 9309 assumes a crawler has one product token. **This project answers to
    six**, and which one it is depends on what it is doing — so there is no
    honest way to pick one record and discard the others. **So none are
    discarded**: the disallows of every matching record are unioned, and an
    `Allow` survives only if *every* matching record grants it. A permission
    one record gives and another withholds is not a permission this project
    has.

    Returns `(token, disallow, allow, groups)` — the token so the caller can
    say who was refused. *"Refused to `ClaudeBot`"* and *"refused to `*`"* are
    not the same fact: the first is aimed at us, the second is a policy.
    `groups` is every token of ours the file names, so a caller can say when
    they disagreed.
    """
    want = {a.lower() for a in agents}
    matched = []
    for names, _rules in _groups(body):
        for n in names:
            if n in want and n not in matched:
                matched.append(n)
    if not matched:
        # **`"*"` and "nothing applies" were the same answer, and they are two
        # facts.** This returned `"*"` whether or not a `*` record existed: on
        # a file reading `User-agent: ClaudeBot / Allow: /*/jobs/ / Disallow: /`
        # — no catch-all at all — `claude-user` came back permitted by matching
        # **nothing**, reported as permitted by `*`.
        #
        # No caller could tell the difference, because the module did not. *The
        # site authorises us* and *the site says nothing about us* are not the
        # same permission, and a token permitted by silence must not outrank a
        # token the file addresses by name. `None` says which one this is.
        #
        # Same family as a field never carried reading as `None`, one layer
        # down and worse: **that was an absence that looked like an answer;
        # this is an answer that covered two facts, and it does not look like a
        # hole.**
        star = [(names, rules) for names, rules in _groups(body)
                if "*" in names]
        if not star:
            return None, [], [], []
        dis, allow = [], []
        for _names, rules in star:
            for kind, value in rules:
                (dis if kind == "disallow" else allow).append(value)
        return "*", dis, allow, []

    per = {}
    for names, rules in _groups(body):
        for n in names:
            if n not in want:
                continue
            d, a = per.setdefault(n, ([], []))
            for kind, value in rules:
                (d if kind == "disallow" else a).append(value)

    dis = []
    for n in matched:
        for value in per[n][0]:
            if value not in dis:
                dis.append(value)
    # **Every record must grant it.** An `Allow` present in one and absent
    # from another is exactly the LinkedIn shape, and taking the union there
    # would resurrect the defect one level down.
    allow = [v for v in per[matched[0]][1]
             if all(v in per[n][1] for n in matched)]
    # The token to name in a sentence: the shortest is the plainest, and where
    # the records agree it makes no difference which is quoted.
    token = sorted(matched, key=len)[0]
    return token, dis, allow, matched


def _groups_named(body, names):
    """Records whose agent set contains any of `names`. Presence, not rules —
    a `*` group with nothing in it still exists, and `_star_group()` returning
    `[]` cannot tell that apart from no `*` group at all."""
    want = {n.lower() for n in names}
    return [r for agents, r in _groups(body) if agents & want]


def orphan_rules(body):
    """`Disallow`/`Allow` lines that sit above any `User-agent:` line.

    **They bind nobody.** RFC 9309 §2.2.1 makes a group start at its
    `User-agent` line, so a directive written before the first one belongs to
    no group and the common parsers ignore it — as this module does.

    **But ignoring it silently is how `allowed: True` came to be reported with
    the words "no `Disallow` matches this path in `*`" on a file that is
    nothing but seven `Disallow` lines and has no `*` group at all.**
    `ihararejobs.com` refuses `/admin/`, `/candidate/` and `/vacancy/apply/`
    that way. The value is defensible; the sentence was false in both halves.
    Issue #180.

    Returns `[(kind, value), …]` as written, so a caller can show the operator
    what it decided not to obey.
    """
    for agents, rules in _groups(body):
        if not agents:
            return [(k, v) for k, v in rules if k in ("disallow", "allow")]
        # A record with agents means the file has groups; anything orphaned
        # can only come first, so the search stops here.
        break
    return []


def _star_group(body):
    """The `Disallow` and `Allow` rules that bind `*`, as written.

    **Consecutive `User-agent` lines form one group**, and the previous
    version overwrote the agent on each of them — so

        User-agent: *
        User-agent: Googlebot
        Disallow: /x

    lost the `*` rule entirely, and **the error went towards permitted.** It
    is the mirror of the defect that produced 41 false positives out of 143
    files elsewhere on the same day by reading those runs as separate groups:
    **the same ignorance of the grammar, erring in opposite directions
    depending on which way it is misread.** Issue #101.

    **Repeated `*` records merge** rather than the first winning — RFC 9309 —
    which this repository measured on eight consecutive `User-agent: *`
    groups.
    """
    dis, allow = [], []
    for names, rules in _groups(body):
        if "*" not in names:
            continue
        for kind, value in rules:
            (dis if kind == "disallow" else allow).append(value)
    return dis, allow


def _match_len(pattern, path):
    """How many characters of `path` a robots pattern matches, or -1.

    Prefix matching with `*` and `$`, which is what the specification asks of
    a rule and all this needs. An **empty `Disallow:`** matches nothing — it
    is the way a file says *nothing is closed* — so it returns -1 rather than
    matching everything at length zero.
    """
    if pattern == "":
        return -1
    rx = re.escape(pattern).replace(r"\*", ".*")
    if rx.endswith(r"\$"):
        rx = rx[:-2] + "$"
    m = re.match(rx, path)
    return len(m.group(0)) if m else -1


# **`Claude-User` first, and the order is the decision.** This project is
# driven by a person's request and that is the token which says so; `ClaudeBot`
# is the fallback for a host that refuses the first by name and permits the
# second. Same order as `identity()`, which is the point of the alignment.
PREFERRED_TOKENS = ("claude-user", "claudebot")


def _token_agents(host, path):
    """The token a request would actually carry, as a one-element tuple.

    Asks each token its own question and takes the first permitted one. When
    **neither** is permitted it returns both, so the caller gets a refusal
    with a real rule behind it rather than a silent `None`.

    **This chooses; it does not retry.** `shared/robots-policy.md` forbids
    rotating agents *after* a refusal and that is untouched: the choice is
    made from the rules, before any request for content leaves, and a 403
    received under the chosen token stays a refusal.
    """
    for tok in PREFERRED_TOKENS:
        if allowed(host, path, agents=(tok,))["allowed"]:
            return (tok,)
    return FETCH_TOKENS


def allowed(host, path, agents=None):
    """May `path` be fetched on `host`? **Longest match wins, `Allow` on a tie.**

    `verdict()` answers *is this host closed in one block*. **A path needs its
    own question**, and until #101 there was no way to ask it: the `*` group's
    rules were computed and thrown away.

    Returns a dict, never a bare bool, because *why* matters as much as *no*:
    `allowed`, `rule` (the directive that decided), `kind`, and the host that
    actually answered.

    **`allowed` is `True`, `False` or `None`** — `None` when the rules could
    not be read. It used to be `True` there, and the reason underneath said
    *no rules were read*: honest about the state, wrong about the permission,
    and it is the boolean that callers act on. Issue #118.
    """
    # **The fields a caller cannot re-derive, carried across.**
    #
    # `allowed()` dropped twelve of the eighteen `verdict()` builds, and one of
    # them is `crawl_delay`. So `allowed(host, path).get("crawl_delay")`
    # returned `None` on `www.hays.fr` two minutes after `verdict()` returned
    # `10.0` for the same host — **two components, one field, two answers.**
    #
    # And the failure is silent in the direction that costs: *a `.get()` on a
    # field never carried returns `None` for ever, which reads exactly like a
    # host that asked for nothing.* A caller reading the rate through the guard
    # rather than through `bin/fetch-body.py` would not wait on a host that
    # asked for ten seconds. **This module wrote that sentence about its own
    # parser this morning and left the same hole one function away.**
    #
    # Only what a caller cannot compute from what it already has: the rate, the
    # declarations, and what was read but not acted on.
    # **What a caller needs at the gate — and `need` is the word, because the
    # first version of this comment said `what a caller cannot recompute` and
    # that is not what it selects.** None of the seven left behind is
    # computable from what `allowed()` returns either: `status`, `attempts`,
    # `bytes`, `disallow`, `allow`, `groups` and `group_conflict` would all
    # take a second request. *A rule that does not select what it claims to
    # select will not protect the next field added* — the same family as a
    # guard that covers the wording of a fix instead of the behaviour.
    #
    # These five are what a caller decides with at the moment it decides: the
    # rate to keep, the declarations to follow, what was read and not acted
    # on, and how the file was obtained. The rest is evidence about the
    # verdict, and belongs to whoever is auditing the verdict.
    CARRY = ("crawl_delay", "sitemaps", "ignored", "content_signal", "state",
             "group_conflict")

    def _carry(result):
        out = Partial(result, known=set(v))
        for k in CARRY:
            out.setdefault(k, v.get(k))
        return out

    def _named(result):
        """Prefix the host these rules actually came from.

        **`verdict()` already says it; this is the function adapters print.**
        Every `gate()` in this repository dies or notes with `a["reason"]` and
        nothing else, so a note that lives only in the verdict is a note nobody
        reads. It reached the caller before today **only when the answer was
        no** — and a `True` computed on another host is the dangerous one:
        `iqjscout.com` answered `allowed=True` from `yadanoo.com`'s rules and
        then 403. *A false yes leaves no more trace than a false no.*
        """
        if result.get("host") and result.get("requested_host") \
                and result["host"] != result["requested_host"]:
            head = (f"**These rules were read from {result['host']!r}, not "
                    f"from {result['requested_host']!r}** — the request was "
                    f"redirected, so this verdict is about "
                    f"{result['host']!r}.")
            result["reason"] = (head + "\n  " + result["reason"]
                                if result.get("reason") else head)
        return result

    # **Decided per token, by the owner on 2026-09-07.**
    #
    # A group naming `ClaudeBot` to refuse it does **not** bind `Claude-User`.
    # They are two distinct tokens; the group that names one does not apply to
    # the other, and that is the standard semantics of the file. Until today
    # this default unioned six names we might be *called*, so a host that
    # closed `ClaudeBot` and left `*` open was reported closed under a token it
    # never mentioned. Thirteen boards sat behind that.
    #
    # **The pilot session recommended the opposite** — that a host which names
    # us to refuse us has said no, whichever token carries the request — and
    # the decision was taken against that advice, in full view of it. It is
    # recorded in `CLAUDE.md` §2 quater. *This comment exists so that a future
    # session reads a decision here and not a bug*: the guard that asserted
    # the old reading was replaced, not deleted, for the same reason.
    #
    # **`OUR_AGENTS` keeps its job.** Six names a site may use *about* us is
    # still the right set for reading what a file says; it was never the right
    # set for deciding what a request may carry, and those are two questions.
    if agents is None:
        agents = _token_agents(host, path)
    else:
        agents = tuple(agents)
    v = verdict(host, agents)
    out = {"host": v["host"], "requested_host": v.get("requested_host"),
           "path": path, "allowed": True, "rule": None, "kind": None,
           "group": v.get("group"), "sweep": v["sweep"],
           "certain": v.get("certain", True)}
    if v["sweep"] is None:
        out.update(allowed=None, kind="unknown", certain=False)
        out["reason"] = v["reason"]
        return _named(_carry(out))
    if not v["sweep"]:
        # **A `Disallow: /` beside `Allow:` lines is a whitelist, not a wall**,
        # and this early return read it as a wall. `bebee.com` opens six path
        # families to `User-agent: ClaudeBot` and closes the rest; the module
        # answered *this host closes everything* and the longest-match code
        # below — which implements the rule this function's own docstring
        # promises — was unreachable in **exactly** the case where `Allow`
        # lines mean anything. Issue #152.
        #
        # **A false refusal is the invisible direction.** A false *yes*
        # eventually produces a 403 somebody sees; a false *no* makes us not
        # fetch, record the host as closed, and move on. Nothing in the result
        # says a door was open. It is the mirror of #101, which was found only
        # because it produced a refused fetch.
        #
        # The short-circuit stays wherever there is nothing to match against:
        # a refusal, an unreadable file, a group with no `Allow` at all.
        if not (v["state"] == "read" and v.get("allow")):
            out.update(allowed=False, kind="host-closed", rule="/")
            out["reason"] = v["reason"]
            return out
    if v["state"] != "read":
        # **Name what happened, not what would have been convenient.** This
        # branch used to read *"a 404 is an absence"* whatever the state was,
        # so `algerie.tanqeeb.com` — HTTP 202, zero bytes — was permitted with
        # a citation of a status it never returned. **A silent verdict invites
        # suspicion; a verdict that gives a false reason reads like a
        # verification.** Issue #125.
        out["certain"] = v["state"] == "absent"
        seen = (f"HTTP {v['status']}" if v.get("status") else "no HTTP status")
        if v.get("bytes") is not None:
            seen += f", {v['bytes']} bytes"
        out["reason"] = (
            f"no rules were read — the host answered {seen} and the state is "
            f"`{v['state']}`. "
            + ("**A 404 is knowledge**: there is no file, so there are no "
               "rules, and that is not a refusal."
               if v["state"] == "absent" else
               "**The host answered and wrote no rule**, so there is none to "
               "obey — an absence of rules is an open door. `certain` is "
               "false because this is a policy applied to an absence, not an "
               "absence established."
               if v["state"] == "unrecognised" else
               "**A 401 on the rules file is an absence of rules** (#201, "
               "2026-09-09): the host demands a credential for every path and "
               "has written no rule. An open door, `certain` false — nothing "
               "was read, and ignorance does not forbid."
               if v["state"] == "unauthenticated" else
               "**That is not an absence and not a permission** — a file that "
               "cannot be read says nothing either way. Proceed at a human "
               "pace and say so, or read it by hand."))
        return _named(_carry(out))
    best_d = max(((_match_len(p, path), p) for p in v.get("disallow") or []),
                 default=(-1, None))
    best_a = max(((_match_len(p, path), p) for p in v.get("allow") or []),
                 default=(-1, None))
    if best_d[0] < 0:
        # **Name the group, because "no rule matched" means two things.** In
        # the `*` group it is the general policy leaving this path alone; in a
        # record that names us it is this operator having written a rule about
        # this project and put nothing in our way. Issue #117.
        g = v.get("group")
        orphans = v.get("orphan_rules") or []
        # **#180, decided 2026-09-07: a malformed refusal is still an
        # intention.** This repository judges intention, not syntax — «a
        # refusal written in the rules is an intention; we do not get round it
        # by any route». Seven `Disallow:` aimed at `/admin/`, `/candidate/`
        # and `/vacancy/apply/` say what the operator wants whatever the file's
        # state.
        #
        # **The verdict is `None`, not `False`.** Inventing a refusal would be
        # as wrong as inventing a permission; we do not know which agents these
        # bind. `None` is the third state this module already has, it is
        # falsy, and a caller that has never heard of it fails closed.
        #
        # **And it is per PATH, not per host.** The intention concerns the
        # paths written down. Returning `None` for every path would close a
        # board on directives that never mentioned it — `ihararejobs.com`
        # refuses seven paths and serves its inventory from two others it
        # never names.
        o_dis = max(((_match_len(pat, path), pat)
                     for k, pat in orphans if k == "disallow" and pat),
                    default=(-1, None))
        o_allow = max(((_match_len(pat, path), pat)
                       for k, pat in orphans if k == "allow" and pat),
                      default=(-1, None))
        if o_dis[0] >= 0 and o_allow[0] < o_dis[0]:
            out.update(allowed=None, certain=False, rule=o_dis[1],
                       kind="orphan-disallow")
            out["reason"] = (
                f"**INDETERMINATE.** `{v['host']}` writes "
                f"`Disallow: {o_dis[1]}`, which matches this path — but the "
                f"file contains **no `User-agent:` line at all**, so that "
                f"directive belongs to no group and binds no named agent "
                f"(RFC 9309 §2.2.1). *We cannot establish that it is aimed at "
                f"us, and we will not read it as permission either*: the "
                f"operator wrote a refusal for this path. "
                f"{len(orphans)} directive(s) sit above any group here. "
                f"An indeterminate is not probed.")
            return _named(_carry(out))
        named = v.get("agents_named") or []
        if not g and not v.get("has_star_group") and named:
            # **The file has groups; none of them is ours and none is `*`.**
            # Distinct from a file with no groups at all, and the difference
            # is not cosmetic: here an operator wrote rules and addressed them
            # to somebody else, which is a decision about that crawler and
            # silence about us.
            shown = ", ".join(f"`{n}`" for n in named[:4])
            out["reason"] = (
                f"`{v['host']}` addresses its rules to {len(named)} named "
                f"agent(s) — {shown}"
                + (", …" if len(named) > 4 else "")
                + " — and declares **no `*` group and no record for this "
                  "project**. Nothing here binds us: this is silence towards "
                  "us, not a permission written for us.")
            return _named(_carry(out))
        if not g and not v.get("has_star_group"):
            # **#180. There was no group, and the sentence used to invent
            # one.** `v.get("group") or "*"` turned «nothing matched» into
            # «the `*` group says nothing», which on `ihararejobs.com` — seven
            # `Disallow` lines and not one `User-agent:` — was false in both
            # halves at once. Ignoring an orphaned directive is defensible;
            # reporting it as an absent one is not.
            shown = ", ".join(f"`{k.title()}: {val}`" for k, val in orphans[:3])
            out["reason"] = (
                f"`{v['host']}` declares **no group at all** — this file "
                f"contains no `User-agent:` line, so there is no record for "
                f"this path to match, and none for `*` either."
                + (f" **It does carry {len(orphans)} directive(s) above any "
                   f"`User-agent:` line** — {shown}"
                   + (", …" if len(orphans) > 3 else "")
                   + ". Those bind no agent under RFC 9309 §2.2.1 and are "
                     "not applied here, but the operator wrote them: treat "
                     "them as an intention before fetching those paths."
                   if orphans else
                   " The file is empty of directives as well as of groups."))
            return _named(_carry(out))
        g = g or "*"
        out["reason"] = (
            f"no `Disallow` matches this path in `{g}` — "
            + ("the group that **names this project**, so this is a decision "
               "about us and not a policy we happen to fall under."
               if g != "*" else "the group that applies to everyone, this "
                                "project included."))
        return _named(_carry(out))
    # A tie goes to `Allow`: the specification's rule, and the direction that
    # respects an operator who wrote both.
    if best_a[0] >= best_d[0]:
        out.update(rule=best_a[1], kind="allow")
        out["reason"] = (f"`Allow: {best_a[1]}` matches at least as much of "
                         f"this path as `Disallow: {best_d[1]}`.")
        return _named(_carry(out))
    token = v.get("group") or "*"
    out.update(allowed=False, rule=best_d[1], kind="disallow", group=token)
    out["reason"] = (
        f"`{v['host']}` refuses this path to `User-agent: {token}` — "
        f"`Disallow: {best_d[1]}`. "
        + (f"**That group names this project**, so this refusal is aimed at "
           f"us and not at crawlers in general."
           if token != "*" else
           f"**This is a refusal aimed at everyone, not at a named "
           f"crawler**, and the intention behind it does not change its "
           f"effect."))
    return _named(_carry(out))


def _main():
    import argparse
    import json
    import sys
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("host")
    p.add_argument("--siblings", action="store_true",
                   help="also read the apex/www twin and compare — a "
                        "diagnostic for writing a board card, not for a sweep")
    a = p.parse_args()
    v = verdict(a.host)
    print(json.dumps(v, ensure_ascii=False, indent=1))
    if v["sweep"] is None:
        print("[robots] **the rules could not be read, so there is no "
              "answer** — not a permission. Exit 8.", file=sys.stderr)
        return 8
    if a.siblings:
        sib = siblings(a.host)
        print(json.dumps(sib, ensure_ascii=False, indent=1))
        if sib["sweep_disagrees"]:
            print("[robots] **the two forms disagree about whether this host "
                  "may be swept.** The more restrictive one was written by "
                  "the same operator; do not pick the convenient one.",
                  file=sys.stderr)
        elif sib["differ"]:
            print("[robots] the two forms publish different files that agree "
                  "on the sweep. Record which host the adapter reads.",
                  file=sys.stderr)
    return 0 if v["sweep"] else 7


if __name__ == "__main__":
    raise SystemExit(_main())


def identity(host, path="/"):
    """Which of our two tokens may fetch `path`, or none — decided per token.

    **The owner's decision of 2026-09-05 replaces the restrictive reading.**
    Until then this module unioned the refusals of every record naming us: a
    host that opened `Claude-User` and closed `ClaudeBot` was reported closed,
    and the arbitration was left to a person. It is now made here:

    | the rules say | what this returns |
    | :-- | :-- |
    | `ClaudeBot` **or** `Claude-User` permitted | that token — ordinary HTTP |
    | both refused | `None` — the caller drives the browser |

    **This chooses; it does not retry.** `shared/robots-policy.md` forbids
    rotating agents *after* a refusal, and that stands: the identity is
    settled from the rules before any request for content is made, and a
    refusal received under the chosen token is a refusal, not an invitation to
    try the other one.

    Returns a dict: `token`, `state` (`"http"` or `"browser"`), `per_token`
    with each token's own verdict, and `reason`. **`token` is `None` in the
    browser branch and the caller must look at `state`** — a falsy token is
    not "unknown".

    **`certain` travels from the underlying verdicts.** When the rules could
    not be read, no token is permitted and the state is not `browser` either:
    an unknown is not a refusal, and `state` reads `"unknown"`.
    """
    per, permitted = {}, []
    unknown = 0
    for tok in FETCH_TOKENS:
        a = allowed(host, path, agents=(tok,))
        per[tok] = {"allowed": a["allowed"], "rule": a["rule"],
                    "group": a.get("group"), "certain": a.get("certain")}
        if a["allowed"] is None:
            unknown += 1
        elif a["allowed"]:
            permitted.append(tok)
    out = {"host": host, "path": path, "per_token": per, "token": None}
    if permitted:
        # `Claude-User` first when both are open: this project is driven by a
        # person's request, and that is the token which says so.
        out["token"] = ("claude-user" if "claude-user" in permitted
                        else permitted[0])
        out["state"] = "http"
        out["reason"] = (
            f"`{out['token']}` may fetch this path"
            + (f" (`{FETCH_TOKENS[0] if out['token'] == FETCH_TOKENS[1] else FETCH_TOKENS[1]}` "
               f"may not)" if len(permitted) == 1 else "")
            + ". Ordinary HTTP, no browser.")
        return out
    if unknown == len(FETCH_TOKENS):
        out["state"] = "unknown"
        out["reason"] = ("the rules could not be read for either token. "
                         "**An unknown is not a refusal**, and it is not the "
                         "browser branch either — retry, or read the file by "
                         "hand.")
        return out
    out["state"] = "browser"
    out["reason"] = (
        "both `ClaudeBot` and `Claude-User` are refused this path, so the "
        "ordinary route is closed. **The browser branch applies** — drive it "
        "with the plugin rather than presenting a third identity.")
    return out

