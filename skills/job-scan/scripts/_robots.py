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
    refused      401/403/429/451 — **the host answered, and it said no.**
                 `barbadosjobregister.gov.bb` returns 403 and thirty bytes of
                 "Request is Blocked by Firewall". A server that says
                 *blocked* has replied. Neither a permission nor an absence.
                 **This departs from RFC 9309 on purpose — see below**
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

import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request

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
# nothing.
_REFUSAL_STATUS = re.compile(r"\b(401|403|451)\b")


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


def _fetch(host):
    """Read one host's file, and report **which host actually answered**.

    `urllib` follows redirects, and a redirect can cross hosts: `ss.ge` sends
    a jobs path to `jobs.ss.ge`, which publishes a **different** rules file —
    62 bytes of `Allow: /` against the apex's 478 bytes of named refusals.
    Returning only the body would hand the caller the right rules under the
    wrong name. Issue #99.
    """
    url = f"https://{host}/robots.txt"
    for attempt, timeout in enumerate(_TIMEOUTS, start=1):
        got = _fetch_once(url, host, timeout)
        got["attempts"] = attempt
        # **Only an unknown is worth asking again.** `absent`, `refused` and
        # `unreadable` are answers; repeating a question a host has already
        # answered is not diligence, it is load.
        if got["state"] != "unreachable" or attempt == len(_TIMEOUTS):
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


def _fetch_once(url, host, timeout):
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
        if e.code in (404, 410):
            return {"state": "absent", "status": e.code,
                    "why": f"HTTP {e.code} — no robots.txt published. **This "
                           f"is knowledge**: the host looked and there is no "
                           f"file, which is not the same as a host that did "
                           f"not answer with one."}
        if e.code in (401, 403, 429, 451):
            # **The host answered, and it answered no.** Measured on
            # `barbadosjobregister.gov.bb`: 403 and thirty bytes, "Request is
            # Blocked by Firewall". This used to be filed under `unreadable`,
            # whose reason reads *absence of a file is not a refusal* — true
            # of a 404 and false here. Issue #118.
            return {"state": "refused",
                    "why": f"HTTP {e.code} — the host refuses to serve its "
                           f"rules file" + _storage_note(e)}
        return {"state": "unreachable", "why": f"HTTP {e.code}"}
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

    def _keep(result):
        _CACHE[(final, key)] = result
        _ALIAS[(host, key)] = final
        return result

    out = {"host": final, "requested_host": host, "sweep": True,
           "reason": None, "content_signal": None, "crawl_delay": None,
           "state": got["state"],
           "attempts": got.get("attempts"), "certain": True,
           "status": got.get("status"), "bytes": got.get("bytes")}
    if final != host:
        out["reason"] = (f"read from {final!r}, not {host!r} — the request "
                         f"was redirected, and the two hosts do not "
                         f"necessarily publish the same file.")
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
        return out
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
        return out
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
            f"hand and record what it says.")
        # **Deliberately not cached.** Caching a transient failure poisons a
        # whole run with an unknown that a second request would have resolved;
        # the three attempts above have already paid for patience.
        return out
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
        dis, allow = [], []
        for names, rules in _groups(body):
            if "*" not in names:
                continue
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
    agents = tuple(agents) if agents else OUR_AGENTS
    v = verdict(host, agents)
    out = {"host": v["host"], "requested_host": v.get("requested_host"),
           "path": path, "allowed": True, "rule": None, "kind": None,
           "group": v.get("group"), "sweep": v["sweep"],
           "certain": v.get("certain", True)}
    if v["sweep"] is None:
        out.update(allowed=None, kind="unknown", certain=False)
        out["reason"] = v["reason"]
        return out
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
               "**That is not an absence and not a permission** — a file that "
               "cannot be read says nothing either way. Proceed at a human "
               "pace and say so, or read it by hand."))
        return out
    best_d = max(((_match_len(p, path), p) for p in v.get("disallow") or []),
                 default=(-1, None))
    best_a = max(((_match_len(p, path), p) for p in v.get("allow") or []),
                 default=(-1, None))
    if best_d[0] < 0:
        # **Name the group, because "no rule matched" means two things.** In
        # the `*` group it is the general policy leaving this path alone; in a
        # record that names us it is this operator having written a rule about
        # this project and put nothing in our way. Issue #117.
        g = v.get("group") or "*"
        out["reason"] = (
            f"no `Disallow` matches this path in `{g}` — "
            + ("the group that **names this project**, so this is a decision "
               "about us and not a policy we happen to fall under."
               if g != "*" else "the group that applies to everyone, this "
                                "project included."))
        return out
    # A tie goes to `Allow`: the specification's rule, and the direction that
    # respects an operator who wrote both.
    if best_a[0] >= best_d[0]:
        out.update(rule=best_a[1], kind="allow")
        out["reason"] = (f"`Allow: {best_a[1]}` matches at least as much of "
                         f"this path as `Disallow: {best_d[1]}`.")
        return out
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
    return out


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

