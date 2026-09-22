#!/usr/bin/env python3
"""Replant a branch on `origin/main` instead of replaying its commits. — #861

    bin/replant.py <branch> <guard class> <file> [<file>…] [--row "<README row prefix>"]

WHY REPLAYING IS THE WRONG QUESTION TO ASK GIT

Two sessions ship two adapters. Each appends a guard class to the END of
`tests/test_core.py` and adds one row to `shared/boards/README.md`. Whoever
merges second rebases, and git stops on a conflict **at the same two places,
every time**:

    CONFLICT (content): tests/test_core.py
      <<<<<<< HEAD     the other session's class
      =======          mine
      >>>>>>>          — and BOTH belong, one after the other

**It is not a disagreement.** Nothing in either change contradicts the other;
they land at the same offset because a file has only one end. Asking git to
merge two appends asks it to decide something it cannot know.

Measured on 2026-09-22: two branches of one session conflicted this way in one
afternoon (#857 and `732-pscgovvc`), and the pilot reported three more the day
before on another session. The resolution was identical each time — keep both,
in order — and it was done by hand each time.

WHAT THIS DOES INSTEAD

It starts from `origin/main` and puts the branch's work back on top of it:

    the branch's own files   written as they are (an adapter, a card)
    the guard class          re-APPENDED to the end of tests/test_core.py
    the README row           REPLACED, matched by its prefix

No merge is requested, so there is nothing to resolve.

WHAT IT REFUSES, AND WHY EACH REFUSAL EXISTS

* **the class is already on `main`** — the branch was merged already, and
  replanting would append a second copy of a class that is there;
**THE README ROW IS OPTIONAL, AND THIS TOOL'S OWN BRANCH IS WHY.** It ships a
tool and a guard class, and adds no row to a board index — the first version
demanded one, so **the tool could not replant the branch that delivers it**, on
exactly the conflict it exists to remove. A branch that adds no row passes
`--row` not at all; a branch that adds one still gets every refusal below.

* **the README prefix matches zero rows** — the card was renamed, and a row
  silently not replaced is a card that vanishes from the index;
* **the README prefix matches two or more** — the prefix is too short, and
  replacing the wrong row is invisible: both rows look plausible afterwards;
* **`tests/test_core.py` does not end with its `if __name__ == "__main__":`** —
  something else is at the end of that file, and appending blind would bury it.

A BRANCH CUT BEFORE #861 DOES NOT CONTAIN THIS TOOL. Its checkout has no
`bin/replant.py`, and `git checkout -B` replaces the tree before the tool could
be read from it — so run main's copy instead:

    git show origin/main:bin/replant.py > /tmp/replant.py && python3 /tmp/replant.py <branch> …

*Measured 2026-09-22 on #869, the tool's first use outside its own case.*

WHAT IT DOES NOT DO

It does not commit and it does not push. The branch is replanted, the suite is
yours to re-run, and the commit stays a deliberate act — *a tool that committed
for you would push a tree you have not read.*
"""

import argparse
import io
import os
import subprocess
import sys

ANCHOR = '\n\nif __name__ == "__main__":\n    unittest.main(verbosity=2)\n'
TESTS = "tests/test_core.py"
README = "shared/boards/README.md"


def show(ref, path):
    """A file as some ref has it, or None — never an empty string for a missing file."""
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("branch", help="the branch to replant (it is reset onto origin/main)")
    p.add_argument("guard", help="the guard class the branch appends to tests/test_core.py")
    p.add_argument("files", nargs="+", help="the branch's own files (its adapter, its card, a tool)")
    p.add_argument("--row", help="the first characters of the branch's README row, enough to be unique "
                                 "— omit it for a branch that adds no row (a tool, a fix)")
    p.add_argument("--onto", default="origin/main", help="what to replant onto (default origin/main)")
    a = p.parse_args(argv)

    kept = {}
    for f in a.files:
        body = show(a.branch, f)
        if body is None:
            print(f"ERROR: {a.branch} has no {f}", file=sys.stderr)
            return 2
        kept[f] = body

    tests = show(a.branch, TESTS)
    if tests is None or ("class " + a.guard) not in tests:
        print(f"ERROR: {a.branch} does not carry a class named {a.guard} in {TESTS}", file=sys.stderr)
        return 2
    guard = tests[tests.index("class " + a.guard):tests.index(ANCHOR)]

    row = None
    if a.row:
        readme = show(a.branch, README)
        rows = [l for l in (readme or "").splitlines() if l.startswith(a.row)]
        if len(rows) != 1:
            print(f"ERROR: the prefix matches {len(rows)} row(s) of {a.branch}'s {README}; it must match exactly one",
                  file=sys.stderr)
            return 2
        row = rows[0]

    subprocess.run(["git", "fetch", "-q", "origin"], check=True)
    if subprocess.run(["git", "checkout", "-q", "-B", a.branch, a.onto]).returncode:
        return 2

    for f, body in kept.items():
        if os.path.dirname(f):
            os.makedirs(os.path.dirname(f), exist_ok=True)
        with io.open(f, "w", encoding="utf-8") as fh:
            fh.write(body)

    with io.open(TESTS, encoding="utf-8") as fh:
        cur = fh.read()
    if not cur.endswith(ANCHOR):
        print(f"ERROR: {TESTS} on {a.onto} does not end with its `if __name__` block — "
              f"appending would bury whatever is there", file=sys.stderr)
        return 2
    if ("class " + a.guard) in cur:
        print(f"ERROR: {a.guard} is already on {a.onto} — this branch is merged, and replanting "
              f"would append a second copy", file=sys.stderr)
        return 2
    with io.open(TESTS, "w", encoding="utf-8") as fh:
        fh.write(cur[:-len(ANCHOR)] + "\n\n" + guard + ANCHOR)

    if row is not None:
        with io.open(README, encoding="utf-8") as fh:
            cur = fh.read()
        here = [l for l in cur.splitlines() if l.startswith(a.row)]
        if len(here) != 1:
            print(f"ERROR: the prefix matches {len(here)} row(s) of {README} on {a.onto}; "
                  f"zero means the card was renamed, two means the prefix is too short", file=sys.stderr)
            return 2
        with io.open(README, "w", encoding="utf-8") as fh:
            fh.write(cur.replace(here[0], row))

    print(f"replanted {a.branch} on {a.onto}: {len(kept)} file(s), the guard {a.guard}, "
          f"{'the README row' if row is not None else 'no README row (none was asked for)'}.\n"
          f"Nothing is committed — run the suite, then commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
