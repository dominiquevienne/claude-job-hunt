#!/usr/bin/env python3
"""Count and read `<loc>` elements — the one reader, because there were
thirteen.

**Issue #55 measured the cost.** `hays.fr` wraps its URLs:

    <loc>
          <![CDATA[ https://www.hays.fr/description-emploi/… ]]>
    </loc>

The usual `<loc>\\s*([^<\\s]+)` matches **nothing at all** here — the first
non-space character after the tag is `<`. On a **valid, 200-OK, 2.37 MB**
sitemap it returns **zero URLs**: a board that appears to publish nothing.

**What exposed it was arithmetic, not the code**: the same file yielded 3 193
`<lastmod>` and 0 `<loc>`. A sitemap with dates and no URLs is impossible.
Had it carried neither, nothing would have said a word.

**AND THE FIX WAS PASTED INSTEAD OF SHARED, WHICH IS WHY THIS FILE EXISTS.**
Audited 2026-09-03: **13 scripts read `<loc>`. Seven carry the corrected
pattern — five of them with the same comment block copied verbatim — and five
still carry the naive one.** #55 fixed four adapters and left the rest, because
there was nowhere for the fix to live. *Two places that say the same thing
eventually disagree*; thirteen places is not a style problem, it is a defect
generator.

THREE WAYS A POPULATED SITEMAP READS AS EMPTY, and this handles all three:

- **CDATA**, above.
- **The whole file on one line.** `grep -c '<loc>'` counts **lines**, not
  elements: a 91-URL sitemap served without newlines is reported as **1**.
  Measured on a government sitemap, 2026-09-03.
- **A namespace prefix** — `<ns:loc>`, `<sitemap:loc>` — which a pattern
  anchored on `<loc>` misses entirely.

WHAT IT DOES NOT DO: it is not an XML parser, and deliberately. These files are
routinely served with a wrong content type, truncated, or gzipped-and-labelled-
text; a strict parser raises where a reader should return what is there and say
what it could not read. `count_says` is the sentence for that.

    from _sitemap import locs, count_says
    urls = locs(body)
    if not urls:
        note(count_says(body))
"""

import gzip
import re

__all__ = ["LOC_RE", "locs", "count", "count_says", "maybe_gunzip"]

# `<loc>` or `<ns:loc>`, CDATA-wrapped or not, across newlines, and not
# requiring `</loc>` to follow the URL directly — that extra strictness is what
# made one of the four readers in #55 the tightest, failing even on a merely
# pretty-printed file.
LOC_RE = re.compile(
    r"<(?:[A-Za-z0-9_.-]+:)?loc\s*>\s*(?:<!\[CDATA\[)?\s*"
    r"([^\s<\]]+)", re.I)

_LASTMOD_RE = re.compile(r"<(?:[A-Za-z0-9_.-]+:)?lastmod\s*>", re.I)
_URL_RE = re.compile(r"<(?:[A-Za-z0-9_.-]+:)?url\s*>", re.I)
_SITEMAP_RE = re.compile(r"<(?:[A-Za-z0-9_.-]+:)?sitemap\s*>", re.I)


def maybe_gunzip(raw):
    """Decompress if these are gzip's magic bytes, whatever the header said.

    `jobindex.dk` serves `application/x-gzip` at `/sitemap.gz` and a reader
    that trusts the content type gets 286 bytes and 0 `<loc>`; decompressed it
    is 906 bytes and five sub-sitemaps.
    """
    if isinstance(raw, bytes) and raw[:2] == b"\x1f\x8b":
        try:
            return gzip.decompress(raw)
        except OSError:
            return raw
    return raw


def _text(body):
    body = maybe_gunzip(body)
    if isinstance(body, bytes):
        return body.decode("utf-8", "replace")
    return body or ""


def locs(body, contains=None):
    """Every URL, in document order. `contains` filters on a substring."""
    urls = LOC_RE.findall(_text(body))
    if contains:
        urls = [u for u in urls if contains in u]
    return urls


def count(body):
    """`{"locs": n, "urls": n, "sitemaps": n, "lastmods": n}` — the four
    numbers that let a caller check itself.

    **`urls` and `locs` should be equal in a `<urlset>`.** They are printed
    together because that inequality is what caught the CDATA bug, and a reader
    that reports one number cannot notice it.
    """
    t = _text(body)
    return {
        "locs": len(LOC_RE.findall(t)),
        "urls": len(_URL_RE.findall(t)),
        "sitemaps": len(_SITEMAP_RE.findall(t)),
        "lastmods": len(_LASTMOD_RE.findall(t)),
        "bytes": len(t),
        "lines": t.count("\n") + 1 if t else 0,
    }


def count_says(body):
    """The sentence to print when the count looks wrong or is zero.

    **Never "this sitemap is empty".** A zero here has four causes and only one
    of them is an empty sitemap.
    """
    c = count(body)
    if c["bytes"] == 0:
        return ("the sitemap body is empty — nothing was read, which says "
                "nothing about what the site publishes.")
    if c["locs"] == 0 and (c["urls"] or c["lastmods"]):
        return (f"**0 `<loc>` against {c['urls']} `<url>` and "
                f"{c['lastmods']} `<lastmod>` in {c['bytes']} bytes — that is "
                f"impossible, so the reader is wrong, not the file.** A "
                f"sitemap with dates and no URLs does not exist. Check for "
                f"CDATA, a namespace prefix, or gzip served as text.")
    if c["locs"] == 0:
        return (f"**0 `<loc>` in {c['bytes']} bytes.** That is not "
                f"established as an empty sitemap: CDATA wrapping, a "
                f"namespace prefix and gzip-served-as-text all read the same "
                f"way. Compare against `<url>` and `<lastmod>` before "
                f"concluding.")
    if c["lines"] == 1 and c["locs"] > 1:
        return (f"{c['locs']} `<loc>` on a single line — `grep -c` would "
                f"report 1. Count elements, never lines.")
    if c["urls"] and c["locs"] != c["urls"]:
        return (f"{c['locs']} `<loc>` against {c['urls']} `<url>`. **They "
                f"should be equal in a urlset**; the difference is the part "
                f"nobody is reading.")
    return f"{c['locs']} `<loc>`, {c['urls']} `<url>`, {c['bytes']} bytes."


def _main():
    import argparse
    import json
    import sys
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", help="a sitemap on disk; omit to read stdin")
    p.add_argument("--contains")
    p.add_argument("--print", action="store_true", dest="print_urls")
    a = p.parse_args()
    raw = (open(a.file, "rb").read() if a.file
           else sys.stdin.buffer.read())
    print(json.dumps(count(raw), ensure_ascii=False))
    print(f"[sitemap] {count_says(raw)}", file=sys.stderr)
    if a.print_urls:
        for u in locs(raw, a.contains):
            print(u)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
