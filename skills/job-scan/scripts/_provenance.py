#!/usr/bin/env python3
"""A fetched body is written with its provenance, or it is not written. — #158

    from _provenance import save, load, audit

    save(path, body, url=…, status=200, agent=UA)   # body + sidecar
    body, prov = load(path)                          # refuses an orphan body
    audit(directory)                                 # names the orphans

WHY THIS EXISTS, AND WHAT IT COST

On 2026-09-05 a recount of the Cloudflare managed default found **28 bodies
identical to the byte**. Eighteen could be attributed. **Ten could not, and
eight of those are unrecoverable** — not difficult, unrecoverable:

    the managed default contains no reference to the host serving it.
    No `Sitemap:`, no canonical, no name. Twenty-eight identical files.

**The filename was the only place the host existed, and it had been
abbreviated.** `sl_rb` meant Somaliland. The obvious repair — look at sibling
files sharing the country prefix — answers *Sierra Leone*, because
`sl_ad_real.html` and its neighbours are Sierra Leonean. **The instrument is
refuted on the single case where its answer could be checked**, which is the
only reason anyone knows it is wrong.

So the rule is not *name your files better*. It is:

    **provenance never lives in the filename.**

A name is one string, it is shortened under pressure, it collides across
countries, and nothing about it can be validated. This module puts provenance
in a sidecar next to the body, where it can be read back, counted, and missed
loudly.

WHAT IS RECORDED, AND WHY EACH FIELD IS THERE

    url        the exact URL, host included    a guard is taken per path, and
                                               a sitemap can live on a host the
                                               guard never saw
    status     the HTTP code                   **a readable body is not an
                                               answer**: a 403 page once entered
                                               a fingerprint table as "5 587
                                               bytes of robots.txt", md5 included
    fetched_at UTC, to the second              a behaviour observed once is
                                               dated, never a property of a site
    bytes      len() of the RAW body           and it says `bytes`, because
                                               characters and bytes were once
                                               published as one quantity
    md5        of the RAW body                 a md5 of a *stripped* body differs
                                               too — three files "changed
                                               overnight" and it was one
                                               trailing newline
    agent      the identity actually sent      a tool's identity appears nowhere
                                               in its output; it is verified,
                                               never observed

**`bytes` and `md5` are of the bytes as received.** No strip, no newline
normalisation, no decode. That is the whole point of recording them.

WHAT MAKES THIS A GUARD RATHER THAN A CONVENTION

`save()` takes url, status and agent as **keyword-only arguments with no
defaults** — omitting one is a `TypeError` at the call, not a blank field
discovered later. `load()` **refuses** a body whose sidecar is missing rather
than returning it. And `audit()` reports orphans by name **with their count**,
so a run that silently narrowed its own scope cannot come back green:
*a guard green on a denominator it shrank itself proves nothing.*
"""

import datetime
import hashlib
import json
import os

SUFFIX = ".provenance.json"


def sidecar_for(path):
    return str(path) + SUFFIX


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def describe(body, *, url, status, agent, fetched_at=None, **extra):
    """The provenance record for `body`, without writing anything.

    `body` must be `bytes`. A `str` would make `bytes` a character count, which
    is the confusion this record exists to settle, so it is refused rather than
    encoded on the caller's behalf.
    """
    if not isinstance(body, (bytes, bytearray)):
        raise TypeError(
            f"body must be bytes, got {type(body).__name__} — encoding it here "
            f"would make `bytes` a character count, which is the exact "
            f"confusion this record exists to settle.")
    body = bytes(body)
    rec = {
        "url": url,
        "status": status,
        "agent": agent,
        "fetched_at": fetched_at or _now(),
        "bytes": len(body),
        "md5": hashlib.md5(body).hexdigest(),
    }
    rec.update(extra)
    return rec


def save(path, body, *, url, status, agent, fetched_at=None, **extra):
    """Write the body and its sidecar. Returns the provenance record.

    The three keyword arguments have **no defaults on purpose**: a call that
    forgets one fails where it is written, rather than producing a file that
    looks complete and is unattributable a day later.
    """
    rec = describe(body, url=url, status=status, agent=agent,
                   fetched_at=fetched_at, **extra)
    path = str(path)
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "wb") as f:
        f.write(bytes(body))
    with open(sidecar_for(path), "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    return rec


def load(path):
    """`(body, provenance)` — **refuses a body with no sidecar.**

    Returning it with `None` would let a caller carry an unattributable body
    exactly as far as the ten files that prompted this module.
    """
    path = str(path)
    side = sidecar_for(path)
    if not os.path.exists(side):
        raise FileNotFoundError(
            f"{path} has no {SUFFIX} beside it. **The body is unattributable "
            f"and this module will not hand it over**: eight files were lost "
            f"this way on 2026-09-05, and the loss was invisible until "
            f"somebody asked which host each came from.")
    with open(side, encoding="utf-8") as f:
        rec = json.load(f)
    if rec.get("body_kept") is False:
        # **A deliberate absence, not a missing file.** A refusal leaves its
        # record and not its twenty-five bytes; saying so beats letting
        # `open()` raise a bare *no such file*, which reads like the loss this
        # module exists to prevent.
        raise FileNotFoundError(
            f"{path} was never written: the record says `body_kept: false`. "
            f"This is a fetch that happened and returned HTTP "
            f"{rec.get('status')} — the body was not kept on purpose. Read the "
            f"record beside it.")
    with open(path, "rb") as f:
        body = f.read()
    return body, rec


def verify(path):
    """Does the body on disk still match its recorded md5 and length?"""
    body, rec = load(path)
    return {
        "path": path,
        "matches": (hashlib.md5(body).hexdigest() == rec.get("md5")
                    and len(body) == rec.get("bytes")),
        "recorded": {"bytes": rec.get("bytes"), "md5": rec.get("md5")},
        "found": {"bytes": len(body), "md5": hashlib.md5(body).hexdigest()},
    }


def audit(root, suffixes=(".txt", ".xml", ".html", ".json", ".bin")):
    """Which bodies under `root` have no provenance beside them.

    Returns **the counts as well as the names** — `of`, `with_provenance`,
    `orphans` — so a caller can check the denominator this walked rather than
    trust a verdict computed over whatever it happened to find.
    """
    root = str(root)
    seen, orphans = [], []
    for base, _dirs, files in os.walk(root):
        for name in files:
            if name.endswith(SUFFIX):
                continue
            if suffixes and not name.endswith(tuple(suffixes)):
                continue
            p = os.path.join(base, name)
            seen.append(p)
            if not os.path.exists(sidecar_for(p)):
                orphans.append(p)
    return {
        "root": root,
        "of": len(seen),
        "with_provenance": len(seen) - len(orphans),
        "orphans": sorted(orphans),
        "orphan_count": len(orphans),
    }

def record(path, body, *, url, status, agent, fetched_at=None, **extra):
    """Write the provenance of a fetch **whose body is not kept.**

    A refusal has no body worth storing — twenty-five bytes of *Your request
    was blocked* — but it is the measurement that most needs a record, and it
    was the only one never getting one.

    **`bin/fetch-body.py` returned on a non-2xx before it saved anything.** An
    audit of seventy records held on 2026-09-07 found **seventy carrying status
    200 and not one refusal.** That is the wrong way round: *a 200 can be
    re-checked whenever you like, because the body is there to re-read. A
    refusal is taken once, has no body to keep, and it is the one that decides
    a country has no board.*

    It leaves the same sidecar, with `body_kept: false` and the figures of what
    did arrive, so an audit sees a fetch that happened and a body deliberately
    not stored — **which is a different fact from a body nobody attributed.**
    """
    rec = describe(body, url=url, status=status, agent=agent,
                   fetched_at=fetched_at, body_kept=False, **extra)
    path = str(path)
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(sidecar_for(path), "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    return rec


RULES_REFUSAL = "rules-refusal"


def rules_refusal(path, *, decision, rules, token, url=None, decided_at=None,
                  **extra):
    """Record a refusal **taken from the rules, before anything left.**

    `record()` above covers the transport: a request went out and an edge
    answered 403. This covers the other one, and they are not the same
    measurement — that is what the three exit codes separate, and merging them
    would lose it:

        exit 2   the transport refused a path the rules PERMIT
        exit 7   the RULES refuse this path — no request was made

    **The majority class had no trace at all.** `emploi.batiactu.com` closed
    with exit 7 and left nothing behind, and under the current `allowed()`
    every one of the thirteen blocked hosts closes exactly that way. *The
    measurement that shuts a board without a single packet leaving was the one
    nobody could re-read.*

    **A rules refusal has no remote body to fingerprint.** There is no status,
    no bytes, no vendor header, because there was no response: inventing those
    fields would make it look like a transport record with empty values. What
    it carries instead is **the file that decided** (`rules`, from
    `_robots.rules_fingerprint`), **the rule that bit** (`decision["rule"]` and
    its `kind`), **the group that applied**, and **the token we would have
    presented** — which matters precisely where a file names one of our two
    and is silent about the other.

    `token` is what the request WOULD have carried, not a name a site uses
    about us. The two are different sets and confusing them has already
    produced a wrong sentence under a right verdict.
    """
    rec = {
        "kind": RULES_REFUSAL,
        # **No `status` key at all.** Not `null`: absent. A reader scanning for
        # a status finds nothing rather than a value that could be mistaken
        # for a response that never happened.
        # **A path is called a path.** `decision["path"]` is
        # `/jobs/boise-id?page=1`, not an address; a key named `url` holding it
        # is read as one downstream, which is the mislabel `final_host` had an
        # hour earlier in the same delivery.
        "path": decision.get("path"),
        "url": url,
        "host": decision.get("host"),
        "requested_host": decision.get("requested_host"),
        "rule": decision.get("rule"),
        "rule_kind": decision.get("kind"),
        "group": decision.get("group"),
        "certain": decision.get("certain"),
        "rules_state": decision.get("state"),
        "token": token,
        "rules": dict(rules or {}),
        "decided_at": decided_at or _now(),
        "body_kept": False,
    }
    rec.update(extra)
    path = str(path)
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(sidecar_for(path), "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    return rec


def transport_failure(path, *, url, error, agent, attempted_at=None,
                      **extra):
    """Record a request that never got an answer — **with its NATURE.**

    A refusal has a status; this has none, and the temptation is to write
    `null` and move on. **That is what happened on 2026-09-07**: a sweep
    recorded `code: null` for twenty-two of twenty-three URLs and discarded
    the exception, so the file could not say whether the host had refused,
    timed out, reset the connection or failed to resolve.

    > *A record that cannot say why is why a card cannot say what.*

    The four are different facts and they lead to different conduct: a refusal
    is the host's answer, a timeout may be ours, a reset is often a rate
    limit, and a DNS failure is not about the host at all. **`kind` carries
    the exception's class and `detail` its message**, so the distinction
    survives the process that saw it.
    """
    rec = {
        "kind": "transport-failure",
        "url": url,
        "error": type(error).__name__ if isinstance(error, BaseException)
                 else "unknown",
        "detail": str(error)[:300],
        "agent": agent,
        # No `status`, no `bytes`, no `md5`: nothing answered. **Absent, not
        # `null`** — the same rule the rules-refusal record follows.
        "attempted_at": attempted_at or _now(),
        "body_kept": False,
    }
    rec.update(extra)
    path = str(path)
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(sidecar_for(path), "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    return rec


def refusals(root):
    """Every record under `root` for a fetch that was not a 2xx.

    **The count that matters is this one, not the count of well-formed
    records.** A tree holding no refusal at all passes any check that only
    inspects the records present.
    """
    out = []
    for base, _dirs, files in os.walk(str(root)):
        for name in files:
            if not name.endswith(SUFFIX):
                continue
            try:
                with open(os.path.join(base, name), encoding="utf-8") as f:
                    rec = json.load(f)
            except Exception:                                   # noqa: BLE001
                continue
            # **Both refusals, and a rules refusal has no status.** Testing
            # only the status would have kept reporting zero on the class
            # that closes boards — the very hole this pair was written for.
            refused = rec.get("kind") in (RULES_REFUSAL,
                                          "transport-failure") or (
                isinstance(rec.get("status"), int)
                and not 200 <= rec["status"] < 300)
            if refused:
                out.append((os.path.join(base, name), rec))
    return sorted(out)


# **The headers that name infrastructure, and only those.**
#
# A refusal record carried status, bytes, md5, identity, time and rate — and no
# header at all. So *"the same 25-byte body"* was all it could say, and 25
# bytes is short and generic: the shared `robots.txt` fingerprint carried its
# weight over **1 836 bytes**, where a string that long does not recur by
# chance. **A very short standard sentence is *expected* to be shared**, and
# two vendors emitting it independently would look identical.
#
# `server` and `cf-ray` turn *same string* into *same vendor, named*.
#
# **An allowlist, not the whole set.** Response headers carry `set-cookie` and
# other things that have no business in a record we keep, compare and publish.
# These six name who answered and nothing about who asked.
VENDOR_HEADERS = ("server", "cf-ray", "via", "x-served-by", "x-cache",
                  "x-amz-cf-pop")


def vendor_headers(headers):
    """The infrastructure-naming headers present, lowercased, or `{}`."""
    if not headers:
        return {}
    out = {}
    for h in VENDOR_HEADERS:
        try:
            v = headers.get(h)
        except Exception:                                       # noqa: BLE001
            v = None
        if v:
            out[h] = str(v)[:120]
    return out
