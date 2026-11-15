#!/usr/bin/env python3
"""Locate and load the `evenements` reader — the ONE place that resolves it.

Two scripts in this directory consume the events tab: `list_applications.py`
for its state column (issue #1307 tranche 2) and `jobroom_sync.py` for its
`prefill` proposals (tranche 3). Both need the SAME reader, for the same
reason, and that reason is a refusal rather than a convenience:

    an unreadable or header-mismatched CSV leaves with its own exit code,
    and is NEVER read as «this sheet holds no event»

A second resolution would not be a second copy of a path — it would be a
second place where that refusal can be lost, one hand at a time. So the
resolution lives here once, and both callers go through it.
"""

from __future__ import annotations

import os

# `skills/job-sync/scripts/events_sheet.py`, relative to THIS file and never to
# the working directory, so the behaviour does not depend on where the caller
# was invoked from.
_REL = (os.pardir, os.pardir, "job-sync", "scripts", "events_sheet.py")

MODULE_NAME = "events_sheet_1307"


def path() -> str:
    """Where the reader is expected to be. Resolved, not guessed."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, *_REL))


def load(flag: str = "--events"):
    """Import the reader, or refuse by NAMING what is missing.

    The failure mode this guards against is the quiet one: a caller that
    cannot find the reader and reimplements a three-line CSV parse would get
    a listing that renders perfectly and silently drops the refusal.
    """
    p = path()
    if not os.path.exists(p):
        raise SystemExit(
            f"error: {flag} needs {p}, which is not there. The reader is "
            f"shipped with the job-sync skill (issue #1307 tranche 1); "
            f"refusing rather than reading the sheet with a second reader")
    import importlib.util
    spec = importlib.util.spec_from_file_location(MODULE_NAME, p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
