#!/usr/bin/env python3
"""Decode a response with the charset it declares, not the one we assume.

**`decode("utf-8", "replace")` is this repository's house pattern — 32 of its
adapters use it — and on a Latin-1 site it corrupts every accented character
without failing.** That is the shape `shared/plausible-and-false.md` catalogues,
arriving in the transport layer: **`errors="replace"` cannot raise, so it
produces plausible text with holes in it.**

MEASURED ON `bne.gob.cl`, Chile's national employment service, 2026-09-03:

    Content-Type: text/html;charset=ISO-8859-1
    <meta charset="windows-1252">
    bytes: b'Pudahuel \xa1Comisiones'

    decoded as utf-8    →  "Pudahuel �Comisiones"
    decoded as cp1252   →  "Pudahuel ¡Comisiones"

**Eight of eight sampled ads lost between 37 and 93 characters** under UTF-8,
and none under cp1252. On a Spanish-language board that is most of the text
that carries meaning.

**And the site declares its encoding twice, differently** — `ISO-8859-1` in the
header, `windows-1252` in the markup. They agree on these bytes and they are
not the same declaration; **neither is UTF-8**, which is the only thing a
reader needed to notice.

WHAT THIS DOES, IN ORDER:

1. The HTTP header's charset, when the server states one.
2. A `<meta charset>` or `<meta http-equiv>` in the first 2 kB, when it does
   not — the markup's own claim. **An XML prolog counts as markup too**:
   `<?xml version="1.0" encoding="ISO-8859-1"?>` is how a sitemap declares
   itself, and this repository reads sitemaps on almost every board.
3. UTF-8, **strictly**, which either succeeds or tells us it is not UTF-8.
4. cp1252 as the last resort, because it maps every byte and therefore never
   raises: **the fallback is chosen for being total, not for being right**, and
   the caller is told which one was used.

    from _decode import decode_body
    text, enc = decode_body(raw, response.headers)
"""

import gzip
import re
import zlib
import sys

__all__ = ["decode_body", "decode_body_readable", "charset_of", "decompress_body",
           "looks_mojibake"]

# **Once per process.** A sweep of four thousand advertisements on a broken
# host would otherwise print four thousand lines, and a warning that scrolls
# is a warning nobody reads.
_WARNED = set()


def _warn_once(message):
    if message[:60] in _WARNED:
        return
    _WARNED.add(message[:60])
    print(f"[decode] {message}", file=sys.stderr)

# `<?xml … encoding="…"?>`, which must be the very first thing in the file.
# A sitemap is the one document this repository reads on nearly every board,
# and it declares its encoding here rather than in a `<meta>`.
_PROLOG = re.compile(rb"""^\s*<\?xml[^>]*?encoding\s*=\s*["']([\w\-]+)["']""",
                     re.I)

_META = re.compile(
    rb"""<meta[^>]+charset\s*=\s*["']?\s*([a-zA-Z0-9_\-]+)"""
    rb"""|<meta[^>]+content\s*=\s*["'][^"']*charset\s*=\s*([a-zA-Z0-9_\-]+)""",
    re.I)


def charset_of(headers=None, raw=b""):
    """What the response says it is — header first, then the markup.

    Returns `(name, where)` with `where` in `header` / `xml` / `meta` /
    `None`, so a
    caller can report **which claim it followed** rather than only the result.
    """
    if headers is not None:
        try:
            cs = headers.get_content_charset()
        except AttributeError:
            cs = None
        if not cs:
            ct = (headers.get("Content-Type") or "") if hasattr(
                headers, "get") else ""
            m = re.search(r"charset=([a-zA-Z0-9_\-]+)", ct, re.I)
            cs = m.group(1) if m else None
        if cs:
            return cs.lower(), "header"
    head = raw[:2048] if isinstance(raw, bytes) else b""
    m = _PROLOG.match(head)
    if m:
        return m.group(1).decode("ascii", "ignore").lower(), "xml"
    m = _META.search(head)
    if m:
        return (m.group(1) or m.group(2)).decode("ascii", "ignore").lower(), \
            "meta"
    return None, None


def decode_body(raw, headers=None):
    """`(text, encoding_used)` — never a silent replacement.

    **Strict first, then a total fallback.** `errors="replace"` on a guessed
    encoding is what hides the problem; here a wrong guess *fails* and the next
    candidate is tried, and only the final fallback is lossless-by-construction
    rather than correct-by-evidence.
    """
    if isinstance(raw, str):
        return raw, "str"
    declared, _where = charset_of(headers, raw)
    tried = []
    for name in (declared, "utf-8", "cp1252"):
        if not name or name in tried:
            continue
        tried.append(name)
        try:
            return raw.decode(name), name
        except (UnicodeDecodeError, LookupError):
            continue
    # Nothing decoded strictly. **And saying so in the second value was not
    # enough**: measured 2026-09-03, **60 of 61 call sites discard it with
    # `[0]`** and nothing anywhere tests for `"utf-8/replace"`. A signal that
    # exists and is never read is the shape this repository met four times in
    # one day — `absent_reason` parsing differently from the reader, an empty
    # `external_host` asserting *no host*, `certain` on a body nobody
    # recognised. **So this one speaks.**
    text = raw.decode("utf-8", "replace")
    lost = text.count("\ufffd")
    if lost:
        _warn_once(
            f"{lost} character(s) of {len(raw)} bytes could not be decoded by "
            f"any candidate and were replaced. **The text now contains U+FFFD "
            f"and reads as ordinary text to everything downstream** — a "
            f"half-replaced title is indistinguishable from a correct one. "
            f"Tried: {', '.join(tried)}. The declaration was "
            f"{declared or 'absent'}; if it names an encoding this "
            f"repository did not try, that is the fix.")
    return text, "utf-8/replace"


# **The last resort is total, not right — and this module says so, which puts an obligation on
# the caller that the caller had no clean way to meet.** `decode_body` reports the codec it used
# precisely so a caller can act on it; the only action available was to decode by hand, which
# `TheLossyFallbackSpeaks` forbids across every adapter and is right to. So the arbitration lives
# HERE, where decoding is owned, and `decode_body` itself is UNCHANGED: no existing call site
# moves.
#
# MEASURED ON `jobpaw.com`, Haiti's generalist board, 2026-11-03:
#
#     <meta charset="UTF-8">                       the document's own claim
#     1 169 653 characters, FIVE of them not UTF-8  0.00043 %
#
#     decoded as cp1252         ->  "PubliÃ© 13 aoÃ»t 2026"      28 adverts of mojibake
#     decoded as utf-8/replace  ->  "Publié 13 août 2026"        five U+FFFD, the rest intact
#
# **cp1252 wins the strict loop because it maps every byte and therefore never raises** — the
# very property the docstring above calls total rather than right. Five bad bytes are enough to
# lose every accent on a page.

# The repository's own mojibake control: the PART of the UTF-8 lead bytes that are followed by a
# continuation byte. A PART and not a density, so it does not move with the composition of the
# text; `0/0` — a well-decoded page with no Latin-1 range at all — reads NOT mojibake.
_LEAD = re.compile(r"[\u00c0-\u00ff]")
_PAIR = re.compile(r"[\u00c0-\u00ef][\u0080-\u00bf]")
_UTF8_NAMES = ("utf-8", "utf8", "utf_8")


def looks_mojibake(text, threshold=0.5):
    """Does this reading look like UTF-8 bytes shown through a Latin-1 lens?"""
    lead = len(_LEAD.findall(text or ""))
    return (len(_PAIR.findall(text or "")) / lead) > threshold if lead else False


def decode_body_readable(raw, headers=None):
    """`(text, encoding_used)` — `decode_body`, then ARBITRATED on readability.

    Use this when a board is known to declare UTF-8 and serve a few bytes that are not.
    It changes the result in exactly one case: the strict loop fell to the total fallback
    **and** the document declared a UTF-8 family encoding **and** the lossy UTF-8 reading
    is the one this module's own control prefers. Everything else is `decode_body`.

    **The other direction is the one `decode_body` exists for and it must not move**: a
    genuinely Latin-1 board — `bne.gob.cl` lost between 37 and 93 characters an advert
    under UTF-8 — reads as `cp1252` here too, because its cp1252 text is not mojibake.
    """
    if isinstance(raw, str):
        return raw, "str"
    text, enc = decode_body(raw, headers)
    if enc != "cp1252":
        return text, enc
    declared, _where = charset_of(headers, raw)
    if (declared or "").replace("_", "-").lower() not in ("utf-8", "utf8"):
        return text, enc
    other = raw.decode("utf-8", "replace")
    if looks_mojibake(text) and not looks_mojibake(other):
        lost = other.count("\ufffd")
        _warn_once(
            f"the document declares {declared} and {lost} byte(s) of {len(raw)} are not, so "
            f"the strict loop fell to cp1252 — TOTAL, not right. Re-read as utf-8/replace, "
            f"which this module's own control prefers; {lost} character(s) are U+FFFD and the "
            f"rest is intact. **cp1252 never raises, which is why it won.**")
        return other, "utf-8/replace (arbitrated)"
    return text, enc

def decompress_body(raw, headers=None):
    """`bytes` as the origin wrote them, whatever transfer coding carried them.

    **A no-op when there is no `Content-Encoding`**, so it is safe to wrap any
    read, and that is why nothing already calling `decode_body` has to change.

    WHY IT EXISTS, AND IT IS A *CACHE* FACT AND NOT A SIZE FACT — #1260,
    measured 2026-11-04. `jobup.py` asked for `Accept-Encoding: identity` so
    that one body would have one size rather than two (#71). Both of its hosts
    answer `Vary: Accept-Encoding`, so their CDN keys its cache **per encoding
    variant**, and on THAT host nothing ever refreshed the `identity` entry.
    **The failure mode is not "identity versus gzip" though**, measured the same
    day: jobs.ch serves its own `identity` variant from cache FRESH TO THE
    SECOND. What bites is a HIT on a long-lived entry, and which keys carry one
    depends on their own traffic — so changing the encoding moves us to a better
    keyspace rather than repairing anything. Measured on ten listing keys at
    one edge POP: **eight `identity` hits at `Age` 51.6 h**, each to a tenth of
    an hour, so a single snapshot written at a single instant — our own sweep
    of two days earlier. **Against that, eight of the ten gzip reads were
    MISSES** — the origin's own answer, so today's data, and silent on whether
    anything keeps that variant warm; of the two gzip HITS, one was our own
    write of fifteen minutes earlier and establishes nothing, and **the only
    uncontaminated witness is a single HIT at `Age` 11.5 h** on a key we had
    never requested in gzip. One specimen, declared as one.

    **And the two variants carry the same content:** on the two keys our sweeps
    had NOT populated, `identity` and gzip returned stated totals equal to the
    unit (160/160 and 132/132) and the same newest date. So the reserve of #71
    is honoured by DECOMPRESSING and measuring the result — never by sitting on
    a variant that real traffic never touches.

    **An unknown coding RAISES rather than returning the compressed bytes.**
    Handed back as they are, they reach `decode_body`, which reads them as a
    charset problem and warns about mojibake: a cause named one layer away from
    where it lives. Only gzip and deflate are decodable here — the standard
    library has no brotli — so nothing may ask for `br`.
    """
    if isinstance(raw, str) or not raw:
        return raw
    enc = ""
    if headers is not None:
        try:
            enc = (headers.get("Content-Encoding") or "").strip().lower()
        except AttributeError:          # something without `.get`, or None
            enc = ""
    if not enc or enc == "identity":
        return raw
    # The LAST coding applied is the first to undo, which is why this reads the
    # tail of the list and not its head.
    parts = [p.strip() for p in enc.split(",") if p.strip()]
    if parts and parts[-1] in ("gzip", "x-gzip"):
        return gzip.decompress(raw)
    if parts and parts[-1] == "deflate":
        try:
            return zlib.decompress(raw)
        except zlib.error:              # raw deflate, without the zlib wrapper
            return zlib.decompress(raw, -zlib.MAX_WBITS)
    raise ValueError(
        f"Content-Encoding: {enc!r} — this module decodes gzip and deflate and "
        f"nothing else, and it refuses rather than hand back bytes that would "
        f"be read as a charset fault one layer down.")
