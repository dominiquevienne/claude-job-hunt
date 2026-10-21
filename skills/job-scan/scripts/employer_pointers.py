#!/usr/bin/env python3
"""The config names the EMPLOYER; the shared registry gives the coordinates.

**Issue #1094 point 4a, and it is the prerequisite of 4b rather than a part of
it.** The owner asked, on 2026-10-07, for «&nbsp;une meilleure méthode pour
config.yml afin d'utiliser des pointeurs et non une redondance
d'informations&nbsp;», then «&nbsp;migre mon config.yml&nbsp;». The registry was
opened and the resolver written; **measured on 2026-10-21, the only referent
of that resolver was its own guard.** Migrating the config to pointers before
anything resolved them would have turned a configuration that works into a
configuration nothing can read — so this is the thing that reads them.

WHAT IT DOES. For one board, it takes the employer pointers the user's own
`config.yml` carries, resolves each through `shared/employer-ats.md`, and
prints the command that would sweep that employer — or says, pointer by
pointer, why it could not.

    python3 employer_pointers.py plan --board workday

WHY THE REFUSALS MATTER MORE THAN THE ANSWERS. A wrong tenant answers **200
with zero ads** (`shared/boards/smartrecruiters.md`), so every failure in this
chain has a shape the user cannot tell from an employer who is not hiring.
Four configured employers once returned `0` each because a consent had to be
re-transmitted by prose and no step carried it (`skills/job-scan/SKILL.md`).
A *pointer* re-transmitted by prose is lost the same way. So nothing here ever
renders an absence it did not measure:

    exit 0   every pointer resolved — or the board configures none, said so
    exit 1   a pointer did NOT resolve: the sentence names which, and why
    exit 2   the pointer LIST could not be read at all — INDETERMINATE

**Exit 2 is not exit 1.** `[]` says «&nbsp;nothing is configured&nbsp;» and an
unreadable shape says «&nbsp;I could not tell&nbsp;»; a caller that renders them
alike has published a zero it never measured, which is the whole of
`shared/false-zero-cost.md`.

WHAT IT REFUSES TO DO. It never opens `config.yml` — the door is
`_override.py` and it stays one door (#206, #198, and the guard that kept it
at one). It never retypes an argument string or a sub-command: both are
DERIVED from the registry row, by the rule the registry's own format already
states for `args`. And it launches nothing: it prints the command, and the
step that owns the sweep runs it.
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import argparse
import json
import sys

import os
import re

import _employer_ats
import _override

HERE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "shared", "boards"))

# The card's own declaration of which script serves the board. It is the same
# line the adapter count is taken from, so reading it here adds no second
# convention.
_SCRIPT_RE = re.compile(r"<!--\s*script:\s*([A-Za-z0-9_-]+)\.py\s*-->")
_PROVIDER_RE = re.compile(r"--provider\s+([A-Za-z0-9_-]+)")


def family_of(board, cards=None):
    """`(family, where)` — the registry `family` for a CONFIG board key.

    **They are not the same thing, and assuming they were is a defect the
    owner's own config exposes.** The registry defines `family` as «&nbsp;the
    adapter's filename without `.py`&nbsp;»; his config indexes by BOARD. The
    two differ wherever one adapter serves several boards — measured
    2026-10-21: `ashby`, `greenhouse`, `lever`, `smartrecruiters` and
    `workable` are five board keys served by **one** family, `ats`.

    The mapping is not derived and not guessed: every card declares it in the
    `<!-- script: -->` line this repository already counts adapters by. A
    board with no card, or a card declaring no script, resolves to nothing and
    the sentence says which of the two it was.
    """
    path = os.path.join(cards or CARDS, f"{board}.md")
    if not os.path.exists(path):
        return None, (f"no card at {path} — the board\u2192family mapping is "
                      f"DECLARED by the card's `<!-- script: -->` line and is "
                      f"not derivable from the board name")
    with open(path, encoding="utf-8") as fh:
        m = _SCRIPT_RE.search(fh.read())
    if not m:
        return None, f"{path} declares no `<!-- script: -->` line"
    return m.group(1), f"declared by {path}"


def plan(board, registry=None, lines=None, path=None, cards=None):
    """`(rows, where)` — one row per pointer, or `(None, why)` if unreadable.

    `lines`/`path` stand in for the config so that a guard can reach the
    branches that matter: a workspace is resolved from the environment, and a
    test that must build one reaches the easy branches only.
    """
    if lines is None:
        pointers, where = _override.employers(board)
    else:
        pointers, where = _override.employers_in(lines, board, path or "<lines>")
    if pointers is None:
        return None, where
    family, fwhere = family_of(board, cards)
    if family is None:
        return None, fwhere
    out = []
    for pointer in pointers:
        row, why = _employer_ats.resolve(family, pointer, registry)
        if row is None:
            out.append({"identifier": pointer, "command": None, "why": why})
            continue
        command, why = _employer_ats.command(row)
        item = {"identifier": pointer, "command": command, "why": why,
                "state": row["state"], "checked": row["checked"]}
        # **A disagreement between the two must be SEEN, not resolved in
        # silence.** Point 3's own constraint: a local override stays possible
        # and it is visible. The registry is authoritative about the
        # coordinates, so the command is its own — but a pointer filed under
        # `boards.greenhouse` whose row says `--provider smartrecruiters`
        # would otherwise sweep a provider the config never named.
        said = _PROVIDER_RE.search(row["args"] or "")
        if said and said.group(1).lower() != board.lower():
            item["note"] = (f"the config files this pointer under "
                            f"`boards.{board}`; the registry says "
                            f"`--provider {said.group(1)}` and the registry "
                            f"decides the coordinates")
        out.append(item)
    return out, where


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("plan", help="the sweep commands for one board's "
                                     "configured employers")
    pl.add_argument("--board", required=True,
                    help="the `boards.<board>` key, which is the registry's "
                         "`family` — the adapter's filename without `.py`")
    pl.add_argument("--registry", help="override the shared registry's path")
    a = ap.parse_args(argv)

    rows, where = plan(a.board, a.registry)
    print(json.dumps({"board": a.board, "where": where, "pointers": rows},
                     ensure_ascii=False, indent=1))
    if rows is None:
        print(f"INDETERMINATE: {where}", file=sys.stderr)
        return 2
    unresolved = [r for r in rows if not r["command"]]
    for r in unresolved:
        print(f"UNKNOWN {a.board}/{r['identifier']}: {r['why']}",
              file=sys.stderr)
    return 1 if unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
