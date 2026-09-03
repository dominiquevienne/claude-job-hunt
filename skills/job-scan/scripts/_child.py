#!/usr/bin/env python3
"""Run another of this repository's scripts, and **read its exit code.**

**Two adapters shelled out to `hiringcafe.py`; one checked and one did not**,
and the one that did carried the reason in its own message:

    An empty tenant list from a failed sweep would read exactly like a
    provider nobody uses.

`recruitee.py` did not, and on 2026-09-03 — the day `hiringcafe.py search`
started refusing by design — it printed **"0 tenants seen in HiringCafe's GB
cards"** and exited 0. **A refusal presented as a measurement**, in the shape
this repository has now met a dozen times: something returned, so it reads as
having been counted.

`subprocess.run` does not raise on a non-zero exit. **`capture_output=True`
then reading only `.stdout` is the whole defect**: the child's diagnosis goes
to `.stderr`, which nobody looked at, and an empty `.stdout` parses to an
empty result perfectly well.

**The child's exit code travels.** 7 (refused) and 8 (the rules could not be
read) mean something to a caller, and flattening them into the parent's
generic failure would lose the one distinction the guard exists to draw.
"""

import subprocess

__all__ = ["run"]

# Codes whose meaning survives being passed upward. Everything else becomes
# the parent's own "broken", because a child's 2 is not the parent's 2.
MEANINGFUL = (7, 8)


def run(cmd, die, tag, timeout=300, broken=2):
    """`stdout` of a successful child, or `die` with the child's own words.

    `die(message, code)` is the caller's — each adapter keeps its own exit
    conventions and its own prefix.
    """
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout)
    except Exception as exc:  # noqa: BLE001 - report, never swallow
        die(f"could not run {tag}: {exc}", broken)
        raise                                   # unreachable; `die` exits
    if r.returncode != 0:
        code = r.returncode if r.returncode in MEANINGFUL else broken
        die(f"{tag} exited {r.returncode}. **Its own message, which is the "
            f"one that matters:**\n  {(r.stderr or '').strip()[:600]}\n"
            f"**Nothing is reported from this run.** An empty result from a "
            f"failed child reads exactly like a real absence — a provider "
            f"nobody uses, a market with no jobs — and the two are not the "
            f"same fact.", code)
        raise
    return r.stdout
