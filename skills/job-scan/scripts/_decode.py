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
   not — the markup's own claim.
3. UTF-8, **strictly**, which either succeeds or tells us it is not UTF-8.
4. cp1252 as the last resort, because it maps every byte and therefore never
   raises: **the fallback is chosen for being total, not for being right**, and
   the caller is told which one was used.

    from _decode import decode_body
    text, enc = decode_body(raw, response.headers)
"""

import re

__all__ = ["decode_body", "charset_of"]

_META = re.compile(
    rb"""<meta[^>]+charset\s*=\s*["']?\s*([a-zA-Z0-9_\-]+)"""
    rb"""|<meta[^>]+content\s*=\s*["'][^"']*charset\s*=\s*([a-zA-Z0-9_\-]+)""",
    re.I)


def charset_of(headers=None, raw=b""):
    """What the response says it is — header first, then the markup.

    Returns `(name, where)` with `where` in `header` / `meta` / `None`, so a
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
    m = _META.search(raw[:2048] if isinstance(raw, bytes) else b"")
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
    # Nothing decoded strictly. Say so in the second value rather than
    # returning text that looks fine.
    return raw.decode("utf-8", "replace"), "utf-8/replace"
