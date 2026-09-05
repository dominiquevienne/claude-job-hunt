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
