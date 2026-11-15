#!/usr/bin/env python3
"""Locate and load the readers `job-sync` does not own — the ONE place.

`events_sheet.py export` (#1322) derives the `candidatures` tab from two
objects that belong to other skills: the ledger's `## Ads` table, read by
`job-report`, and the optional `aliases` / `domains` bullets of
`employers.md`, read by `job-scan`. **Neither is reimplemented here**, and the
resolution lives in one file for the same reason `_events_reader.py` exists in
the other direction: a second resolution is not a second copy of a path, it is
a second place where a REFUSAL can be lost, one hand at a time.

The two refusals are different, and that is why they are named separately
rather than described as one:

    the ledger      a row whose width does not match the header is NOT read,
                    and BOTH directions are counted — a short row is a cell
                    missing, a long row is a stray `|` shifting every column
                    after it, and a count sent to an authority cannot carry
                    either in silence
    employers.md    an employer section is only what follows the first `---`
                    rule, and a bullet is joined across its wrapped lines —
                    without the first, the file's own preamble headings are
                    read as companies; without the second, a bullet that
                    wrapped loses everything after its first line

**The direction is what this file is one of.** `_events_reader.py` resolves
`job-report → job-sync`; this resolves `job-sync → elsewhere`. Both exist, and
`_secrets.py` resolved `job-scan → bin` before either of them, so the
"pattern this repository has nowhere" that `_ledger_table.py` recorded as a
residue is no longer absent — its paragraph is cited there and not rewritten.

*`employers.md` is OPTIONAL and so are both of its bullets: the contract lets
`alias_entreprise` and `domaines_expediteurs` be empty, and an absent file is
not an error here. What is NOT optional is that an employers file which EXISTS
and cannot be read leaves by a refusal rather than as "this employer declares
no alias".*
"""

from __future__ import annotations

import os

#  Resolved relative to THIS file and never to the working directory, so the
#  behaviour does not depend on where the caller was invoked from.
_LEDGER_REL = (os.pardir, os.pardir, "job-report", "scripts",
               "_ledger_table.py")
_EMPLOYERS_REL = (os.pardir, os.pardir, "job-scan", "scripts", "employers.py")

LEDGER_MODULE = "ledger_table_1322"
EMPLOYERS_MODULE = "employers_1322"


def _path(rel) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, *rel))


def ledger_path() -> str:
    """Where the ledger reader is expected to be. Resolved, not guessed."""
    return _path(_LEDGER_REL)


def employers_path() -> str:
    """Where the employers reader is expected to be."""
    return _path(_EMPLOYERS_REL)


def _load(path: str, module_name: str, flag: str, why: str,
          siblings: bool = False):
    """Import a module by path, or refuse by NAMING what is missing.

    The failure mode this guards against is the quiet one: a caller that
    cannot find the reader and writes a three-line parse of its own would get
    output that renders perfectly and has dropped the refusal.

    **`siblings` is MEASURED and not assumed, and the two readers differ.**
    `_ledger_table.py` imports nothing of ours, so it loads with `sys.path`
    untouched; `employers.py` does `import _console`, so loading it with a
    bare spec raises `ModuleNotFoundError` — which reads like a missing
    package when it is a missing search path (CLAUDE.md records the same
    confusion for `python3 -I`). So its directory is put on the path **for the
    duration of the exec and removed afterwards**, and APPENDED rather than
    inserted: that directory holds dozens of modules, among them `ledger.py`
    and `_withheld.py`, and leaving it on the path would let a LATER import
    anywhere in the process resolve to a third skill's file instead of
    failing. A borrowed search path is given back.
    """
    if not os.path.exists(path):
        raise SystemExit(
            f"error: {flag} needs {path}, which is not there. {why} "
            f"Refusing rather than reading it with a second reader")
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    here = os.path.dirname(path)
    added = siblings and here not in sys.path
    if added:
        sys.path.append(here)
    try:
        spec.loader.exec_module(mod)
    finally:
        if added and sys.path and sys.path[-1] == here:
            sys.path.remove(here)
    return mod


def ledger(flag: str = "--pipeline"):
    """The `job-report` ledger reader — `load`, `annotate`, `sent`, aliases.

    **It imports nothing of ours**, which is why no `sys.path` is touched here
    and why this direction does not close a cycle with `_events_reader.py`:
    that one resolves `events_sheet.py`, and `events_sheet.py` resolves this
    file, which resolves a module with no sibling import at all.
    """
    return _load(ledger_path(), LEDGER_MODULE, flag,
                 "The ledger table reader is shipped with the job-report "
                 "skill (issue #1182).")


def employers(flag: str = "--employers"):
    """The `job-scan` employers reader — `sections` and `bullets`."""
    return _load(employers_path(), EMPLOYERS_MODULE, flag,
                 "The employers reader is shipped with the job-scan skill.",
                 siblings=True)
