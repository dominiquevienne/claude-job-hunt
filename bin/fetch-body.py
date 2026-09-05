#!/usr/bin/env python3
"""Fetch one URL and write the body **with its provenance**. — #158

    bin/fetch-body.py https://host.example/robots.txt -o scratch/h.txt
    bin/fetch-body.py https://host.example/sitemap.xml -o s.xml --allow-refusal

**Use this instead of an ad-hoc script.** That is the whole point: the bodies
lost on 2026-09-05 were not written by any adapter — *no adapter in this
repository writes a fetched body to disk at all* — they were written by
one-off scripts in a scratchpad, and every one of them is now unattributable.
An audit of one session's scratchpad the same day: **365 bodies, 0 with
provenance.**

WHAT THIS DOES THAT AN AD-HOC SCRIPT KEEPS FORGETTING

**1. It asks the guard on the exact URL, host included.** Not the root. A
sitemap can live on a host the guard has never seen — `merojob.com` declares
its own on `sg.merojob.com` — and a path declared somewhere other than
`/sitemap.xml` is covered by no verdict taken at the root.

**2. It declares this project's identity.** `_ua.UA`, never a browser string.
A tool's identity appears nowhere in its output, so it is verified rather than
observed — and one draft script sent Chrome for a whole day while the module
beside it declared itself properly.

**3. It tests the HTTP code, and records it either way.** A readable body is
not an answer: a 403 page once entered a fingerprint table as *"5 587 bytes of
robots.txt"*, md5 included, and that false success then invented a cause for
itself that took four measurements to demolish. Here a non-200 is written
**with its status in the record** and reported on stderr; nothing is silently
promoted to a success.

**4. It honours `Crawl-delay` when the host sets one.** `ejob.az` names
`ClaudeBot` to give it `Crawl-delay: 5` and forbids it nothing — named,
allowed, conditioned.

WHAT IT REFUSES

A path the rules refuse is **not fetched**, and there is no flag for that.
`--allow-refusal` is about the *HTTP* status: it lets a 4xx/5xx body be saved
for study, which is legitimate and was never the problem — the problem was
calling it a success.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "job-scan", "scripts"))

from _provenance import save          # noqa: E402
import _tls                           # noqa: E402
from _robots import allowed, verdict  # noqa: E402
from _ua import UA                    # noqa: E402

EXIT_HTTP, EXIT_REFUSED, EXIT_UNKNOWN = 2, 7, 8


def decoded(body, encoding):
    """`(body, encoding_or_None)` — the bytes a reader would see.

    **A record of compressed bytes describes the transfer, not the document.**
    `apec.fr` answers gzip without being asked: 14 171 bytes on the wire for a
    65 551-byte page. Two things follow, and the second is the heavy one.

    A `grep` over such a body returns **no match and no error** — a negative
    manufactured by an encoding, and one was published as *"apec serves no
    total"* before it was caught.

    And an md5 taken there compares transfers. **Two identical responses
    compressed differently give different `bytes` and different `md5` for the
    same document** — a third road to the false *"the file changed"*, after
    this morning's stripped trailing newline and a render stamp.

    So the record describes the decoded body, and **names the encoding it
    undid** rather than silently erasing it: `encoded_bytes` keeps what came
    off the wire, because a transfer size is a real fact about a host and the
    point is to stop the two being one number.
    """
    if not encoding or encoding == "identity":
        return body, None
    try:
        if encoding in ("gzip", "x-gzip"):
            import gzip
            return gzip.decompress(body), encoding
        if encoding == "deflate":
            import zlib
            try:
                return zlib.decompress(body), encoding
            except zlib.error:
                return zlib.decompress(body, -zlib.MAX_WBITS), encoding
        # **`br` is not decoded here, and it is named rather than ignored.**
        # There is no brotli in the standard library and this plugin installs
        # nothing — the repository's own dependency guard caught the import
        # that tried. A caller gets the bytes with the encoding that defeated
        # us attached, which is the honest answer: *undecodable is not
        # unencoded*.
    except Exception:                                       # noqa: BLE001
        # **Undecodable is not the same as unencoded.** The record must not
        # claim a decoded body it does not have; the caller is told which
        # encoding defeated it.
        return body, f"{encoding} (not decoded)"
    return body, f"{encoding} (unknown)"


def shown_token():
    """The name to print for our identity — **not the first word of `UA`.**

    `UA` begins `Mozilla/5.0 (compatible; Claude-User; …)`, which is the
    ordinary convention and is correct on the wire. But `UA.split("/")[0]`
    reports **"Mozilla"**, and this repository has already spent a day on a
    tool that announced a browser: an operator reading that line, or a session
    reading its own output, would see exactly the defect it is meant to
    disprove. *A tool's identity appears nowhere in its output — it is
    verified, never observed*, and a summary line is output like any other.
    """
    m = re.search(r"(Claude-[A-Za-z-]+|ClaudeBot)", UA)
    return m.group(1) if m else UA


def main():
    # **Nothing here reads standard input, and it is closed anyway.**
    #
    # A shell loop feeding this tool a list of hosts processed seven of eight,
    # and this tool was the suspect. It did not reproduce on any of three exit
    # paths, and the real cause was found the same day and is not here:
    #
    #     the list file had no trailing newline, and `while read` returns
    #     non-zero at such an end-of-file *after assigning the variables*,
    #     so the loop exits and the last line is read and thrown away.
    #
    #     sans_nl.txt  41 bytes  wc -l=2  iterations=2
    #     avec_nl.txt  42 bytes  wc -l=3  iterations=3
    #
    # **One byte, one iteration fewer.** And the check that seemed obvious —
    # count output rows against input rows — is inert against it: `wc -l`
    # counts newlines, so both sides agree on the wrong number. Write lists as
    # `"\n".join(...) + "\n"`, or read them with
    # `while read -r x || [ -n "$x" ]`.
    #
    # Closing stdin stays because the documented use of this tool *is* a loop,
    # and a tool used that way should not be able to become the suspect again.
    try:
        sys.stdin.close()
    except Exception:                                      # noqa: BLE001
        pass
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url")
    p.add_argument("--sitemaps", action="store_true",
                   help="list the sitemaps this host declares, and stop. Reads "
                        "only robots.txt, writes nothing unless -o is given, "
                        "and fetches none of what it finds")
    p.add_argument("-o", "--out",
                   help="where the body goes; the provenance goes beside it")
    p.add_argument("--allow-refusal", action="store_true",
                   help="save a non-200 body too — with its status recorded, "
                        "which is the point")
    p.add_argument("--timeout", type=float, default=45)
    p.add_argument("--json", action="store_true",
                   help="emit the provenance record on stdout instead of the "
                        "path — so a caller need not parse prose or re-read a "
                        "file it just wrote")
    a = p.parse_args()

    if not a.sitemaps and not a.out:
        print("ERROR: -o is required unless --sitemaps", file=sys.stderr)
        return EXIT_HTTP
    parts = urllib.parse.urlsplit(a.url)
    if not parts.netloc:
        print(f"ERROR: {a.url} has no host", file=sys.stderr)
        return EXIT_HTTP

    # **The guard is taken on the exact path, in this order, before anything
    # leaves.** Not on the root, and not after.
    g = allowed(parts.netloc, parts.path or "/")
    if g["allowed"] is None:
        print(f"ERROR: {a.url}: {g['reason']}", file=sys.stderr)
        return EXIT_UNKNOWN
    if not g["allowed"]:
        print(f"REFUSED: {a.url}: {g['reason']}", file=sys.stderr)
        return EXIT_REFUSED

    if a.sitemaps:
        # **Only the declaration, and nothing it names.** A session wanting a
        # sitemap could compose `/sitemap.xml` or do nothing, while 82 of 187
        # rules bodies say where theirs is. Reading that answer authorises no
        # fetch: whatever comes back still has its own guard to pass, on its
        # own host — `merojob.com` declares its sitemaps on `sg.merojob.com`.
        v = verdict(parts.netloc) or {}
        maps = v.get("sitemaps") or []
        if a.json:
            print(json.dumps({"host": parts.netloc, "sitemaps": maps},
                             ensure_ascii=False))
        else:
            for u in maps:
                print(u)
        if not maps:
            print(f"[fetch-body] {parts.netloc} declares no sitemap. **That is "
                  f"not permission to guess one** — 43.9 % of hosts declare, "
                  f"and the rest have not told us.", file=sys.stderr)
        return 0

    delay = (verdict(parts.netloc) or {}).get("crawl_delay")
    if delay:
        print(f"[fetch-body] the host asks for {delay}s between requests; "
              f"waiting", file=sys.stderr)
        time.sleep(float(delay))

    # **The same TLS chain the guard uses, or this tool cannot reach a host
    # the guard has already read.** `empleate.gob.es` omits the intermediate
    # its certificate needs; `_tls` supplies it. Until 2026-09-05 the guard
    # imported `_tls` and this tool did not, so it failed
    # `CERTIFICATE_VERIFY_FAILED` **in the same minute the guard declared the
    # host readable at 8 456 bytes** — and `CLAUDE.md` names this tool as the
    # only way to fetch. An asymmetry between the guard and the fetcher makes
    # that rule inapplicable on exactly the hosts that need it most.
    #
    # `context_for` returns `None` for every host but one, and `None` means
    # *use the default*. **Verification stays whole**: `verify=False` is never
    # the alternative, which is the whole point of that module.
    ctx = _tls.context_for(parts.netloc)
    req = urllib.request.Request(a.url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=a.timeout,
                                    context=ctx) as r:
            status, body, landed = r.getcode(), r.read(), r.geturl()
            enc = (r.headers.get("Content-Encoding") or "").strip().lower()
    except urllib.error.HTTPError as e:
        status, body, landed = e.code, e.read(), e.geturl()
        enc = (e.headers.get("Content-Encoding") or "").strip().lower()
    except (urllib.error.URLError, OSError) as e:
        print(f"ERROR: {a.url}: {e}", file=sys.stderr)
        return EXIT_HTTP

    if status != 200 and not a.allow_refusal:
        # **Not saved, and said out loud.** The failure this prevents is the
        # opposite one: saving it and calling it a body.
        print(f"ERROR: {a.url}: HTTP {status}, {len(body)} bytes not saved. "
              f"**A readable body is not an answer — the code decides.** Pass "
              f"--allow-refusal to keep it; its status travels in the record.",
              file=sys.stderr)
        return EXIT_HTTP

    # **The rate a measurement was taken at belongs in the record.** It was
    # announced on stderr and lost, and it is a fact about our own conduct
    # rather than about the body: a later reader could not tell whether a
    # host's `Crawl-delay` had been honoured. `None` when the host sets none —
    # which is a different fact from "we did not look".
    # **Where the body actually came from, when that is not where it was
    # asked for.** `iqjscout.com` redirects to `yadanoo.com`, and a guard that
    # concluded on the second while being named for the first said so nowhere.
    # A record that keeps only the requested URL cannot answer *which host is
    # this body's* — the question the whole record exists for.
    wire = len(body)
    body, undone = decoded(body, enc)
    rec = save(a.out, body, url=a.url, status=status, agent=UA,
               crawl_delay_s=delay,
               final_url=(landed if landed and landed != a.url else None),
               content_encoding=undone,
               encoded_bytes=(wire if undone else None))
    print(f"[fetch-body] {a.out} — HTTP {rec['status']}, {rec['bytes']} bytes, "
          f"md5 {rec['md5'][:12]}, as {shown_token()}, "
          f"{rec['fetched_at']}", file=sys.stderr)
    if a.json:
        print(json.dumps(rec, ensure_ascii=False, sort_keys=True))
    else:
        print(a.out)
    return 0 if status == 200 else EXIT_HTTP


if __name__ == "__main__":
    sys.exit(main())
