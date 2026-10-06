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


# **The mirror of `VENDOR_HEADERS`, and it is the harder direction.** — #999
#
# Those six name *who answered* and nothing about who asked. What follows names
# *what was asked* and nothing about who asked it — and that is new in this
# module, because until a POST existed every request was fully described by its
# URL, and a URL is composed by us.
#
# **A request body is the first thing here that can carry a candidate's own
# search**: their trade, their city, the employer they are chasing. The
# provenance sidecar sits in the repository's reach, and the repository is
# public.
#
# So the rule is not *be careful with the body*. It is:
#
#     **the SCHEMA is recorded and the VALUES are not.**
#
# Field names are the board's form, not the candidate's answer. Lengths and a
# count describe the shape of what went out. **And the digest is taken over the
# NAMES, never over the body** — which is the half that looks like a redaction
# and is not: `q=plombier` has a dozen bits of entropy, so an md5 of a search
# body is a dictionary lookup away from the term it was meant to hide. *A digest
# of a low-entropy secret is not a redaction, and naming it `sent_md5` would be
# the `withheld_fields` lie in a new place: a claim of discretion we would not
# have.*
#
# **The assumption, stated rather than left implicit:** a field NAME belongs to
# the board. That is true of a form POST and it is what this treats as safe; a
# name is still capped and elided past the cap, because the assumption is an
# assumption.

# **A field that is PRESENT is not a field that is FILLED, and `if x` cannot
# tell them apart.** The literal strings below are values that real boards
# store: measured 2026-10-02, `email` arrived true on 10 ads and real on 4,
# `number_Of_vacancy` true on 11 and real on 2, because the sentinel was the
# four-character string `"undefined"`. A summary that counted those as values
# would report a candidate's details withheld where the candidate typed
# nothing.
# **AND A DENY-LIST OF SENTINELS IS DEFEATED BY ONE CHARACTER — #1007.** The
# tuple below was the floor, and it was a list of strings to REJECT: so
# `"$undefined"` — a real stored value, measured by `cd` — folded to nothing in
# it and counted as a value. *A deny-list bets you enumerated the problem; the
# problem here is a sentinel someone else spells.*
#
# So the floor is POSITIVE and it judges the value's CORE, not its text: strip
# everything that is not a letter or a digit, lower-case it, and ask whether
# what remains IS a placeholder word. One extra character no longer matters.
#
#     "$undefined"  -> "undefined"          placeholder   (the specimen)
#     "N/A" / "n/a" -> "na"                 placeholder   (the old list MISSED it)
#     "(null)"      -> "null"               placeholder
#     "--"          -> ""                   placeholder
#     "undefined behaviour in C" -> "undefinedbehaviourinc"   A VALUE
#     "0"           -> "0"                  A VALUE — see below
#
# **`0` and `false` are NOT placeholders**, deliberately: they are what a count
# of zero and a boolean false look like, and a floor that ate them would drop
# real data to avoid a sentinel. *The cost of that choice is that a board using
# the string `"0"` as its own sentinel is not caught — written here so the next
# session widens it on a MEASUREMENT rather than on a hunch.*
PLACEHOLDER_WORDS = frozenset((
    "undefined", "null", "none", "nil", "nan", "na", "unknown", "tbd",
    "empty", "blank", "unspecified",
))

# Kept so an older caller still resolves, and so a grep for it lands here.
UNVALUED = ("", "undefined", "null", "none", "nil", "nan", "-")

SENT_NAME_CAP = 64
SENT_FIELD_CAP = 60


def _core(v):
    """A value's alphanumeric core, folded — `$undefined` becomes `undefined`.

    *Written with `str.isalnum` and not `re`, because this module does not
    import `re` and the first version did: it PARSED, and raised `NameError`
    the moment it ran. Found by calling it on the null case, which is the only
    way that species shows — §4 ter's fourth, «la garde qui lève».*

    And `isalnum` keeps non-Latin letters, so a Cyrillic or Greek value has a
    core and survives the floor instead of folding to nothing.
    """
    return "".join(c for c in str(v).strip().lower() if c.isalnum())


def placeholder(v):
    """True when the value is a placeholder, judged on its CORE.

    A container is never a placeholder: an empty one is ABSENT, and a filled
    one is a value whose shape we do not read here.
    """
    if isinstance(v, (dict, list, tuple, set)):
        return False
    c = _core(v)
    return c == "" or c in PLACEHOLDER_WORDS


def valued(v):
    """**The POSITIVE floor**: a value is anything that is not a placeholder."""
    return not placeholder(v)


def _valued(v):
    """The old name, now answering through the positive floor."""
    return valued(v)


# **THE TRI-STATE THAT MAKES A SILENT OUTPUT READABLE — #1007.**
#
# A board that hands over a person and a board that hands over nothing both
# produce an EMPTY list of withheld fields, and nothing in the output separates
# them. *That is the recorded defect taken from its worse end: there the output
# ASSERTED a discretion we had not exercised, which is a lie one can check;
# here the output is SILENT, and there is no claim to check.*
#
# So the answer is not a better list of withheld names — it is to emit what was
# LOOKED FOR beside what was dropped:
#
#     inspected   every field name the adapter asked about        <- the PROOF we looked
#     withheld    those present and carrying a real value
#     absent      those we asked about and the board did not send
#     placeheld   present, but holding a placeholder
#
# **`withheld: []` with a non-empty `inspected` means «we looked and the board
# sent nothing».** An adapter that emits no `inspected` at all is then visibly
# a different thing from one that emits an empty `withheld` — which is the
# whole point, and it is why `inspected` is NOT optional.
def third_party(record, fields):
    """Classify the third-party fields an adapter declares it inspects.

    `fields` is an iterable of dotted paths («company.hiringManager.image») or
    of segment tuples. The VALUE side is never returned: only names.
    """
    inspected, withheld, absent, placeheld = [], [], [], []
    for path in fields:
        segs = tuple(path.split(".")) if isinstance(path, str) else tuple(path)
        name = ".".join(segs)
        inspected.append(name)
        cur = record
        for seg in segs:
            cur = cur.get(seg) if isinstance(cur, dict) else None
            if cur is None:
                break
        if cur is None or (isinstance(cur, (dict, list, tuple, set)) and not cur):
            absent.append(name)
        elif placeholder(cur):
            placeheld.append(name)
        else:
            withheld.append(name)
    return {
        "third_party_inspected": inspected,
        "third_party_withheld": withheld,
        "third_party_absent": absent,
        "third_party_placeholder": placeheld,
    }


def _cap(name):
    name = str(name)
    if len(name) <= SENT_NAME_CAP:
        return name
    # A name past the cap is not printed: the assumption that a name is the
    # board's schema is weakest exactly where the name is long and odd.
    return f"<elided, {len(name)} chars>"


def sent_summary(raw, *, content_type=None):
    """What may be recorded about a request body. **Schema, never values.**

    `raw` must be `bytes` — the same refusal `describe()` makes, for the same
    reason: a `str` would make `sent_bytes` a character count.

    Returns keys prefixed `sent_`, all of them safe to publish:

        sent_bytes          length of the body as sent
        sent_content_type   what we declared it as
        sent_parsed         "form" · "json" · None when it could not be read
        sent_fields         the names, sorted            — the board's schema
        sent_field_count
        sent_valued_fields  the names that carried a value under the floor
        sent_value_lengths  {name: [len, …]}             — shape, not content
        sent_schema_md5     md5 over the NAMES only      — comparable, inert
        sent_values         present ONLY when something was actually withheld

    **That last line is the `withheld_fields` lesson.** A record that says
    *values withheld* on a body where every field was empty would be lying
    about our own discretion, in the one direction no guard outside this file
    can check — the sidecar reads the same either way. So the sentence is
    derived from the measured set and is **absent** when that set is empty.

    A body this cannot parse — multipart, binary, a content type we were not
    told — yields `sent_parsed: None` and no field names at all. *Guessing
    field boundaries out of bytes we do not understand is how a value ends up
    recorded as a name.*
    """
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError(
            f"raw must be bytes, got {type(raw).__name__} — encoding it here "
            f"would make `sent_bytes` a character count, the same confusion "
            f"`describe()` refuses.")
    raw = bytes(raw)
    ct = (content_type or "").split(";")[0].strip().lower()
    out = {"sent_bytes": len(raw), "sent_content_type": content_type or None}

    pairs, parsed = [], None
    if ct == "application/x-www-form-urlencoded":
        try:
            import urllib.parse
            pairs = urllib.parse.parse_qsl(raw.decode("utf-8"),
                                           keep_blank_values=True)
            parsed = "form"
        except Exception:                                       # noqa: BLE001
            parsed = None
    elif ct == "application/json":
        try:
            doc = json.loads(raw.decode("utf-8"))
            if isinstance(doc, dict):
                pairs = [(k, v) for k, v in doc.items()]
                parsed = "json"
        except Exception:                                       # noqa: BLE001
            parsed = None

    out["sent_parsed"] = parsed
    if parsed is None:
        # **No names invented from bytes we could not read.** The size and the
        # declared type are facts; a field list would not be.
        return out

    lengths, valued = {}, []
    for k, v in pairs[:SENT_FIELD_CAP]:
        name = _cap(k)
        lengths.setdefault(name, []).append(len(str(v)))
        if _valued(v) and name not in valued:
            valued.append(name)
    names = sorted(lengths)
    out["sent_fields"] = names
    out["sent_field_count"] = len(pairs)
    out["sent_value_lengths"] = lengths
    out["sent_valued_fields"] = sorted(valued)
    out["sent_schema_md5"] = hashlib.md5(
        "\n".join(names).encode("utf-8")).hexdigest()
    if len(pairs) > SENT_FIELD_CAP:
        out["sent_fields_truncated"] = len(pairs) - SENT_FIELD_CAP
    if valued:
        out["sent_values"] = (
            f"{len(valued)} field(s) carried a value and it is NOT recorded "
            f"here — a request body can hold the candidate's own search terms, "
            f"and this file is within the repository's reach. Names, lengths "
            f"and a digest OF THE NAMES are above; there is no digest of the "
            f"body, because an md5 of `q=<one word>` is a dictionary lookup.")
    return out
