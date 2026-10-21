#!/usr/bin/env python3
"""`boards.<board>.override_robots` — read from the user's own `config.yml`,
by the adapter that needs it, for one board.

**The consent lives in the config; the code that needs the consent reads it
there.** #206 wrote this for SmartRecruiters inside `ats.py`; #198 needed the
same reading for HiringCafe, and a second copy would be the second adapter's
own way of parsing the same key. So it is one function, and the two adapters
call it with their own board name.

Reading it here, and only this key, is the one exception to «&nbsp;adapters do
not read `config.yml`&nbsp;» (`skills/job-scan/SKILL.md`): the profile is
passed down by the skill; *this is not profile, it is the adapter's own key*.
The workspace is resolved the way `_secrets.py` resolves `credentials.env` —
`bin/workspace-path.py`, never a guessed folder — and the `boards:` block is
parsed by `dormant.read_boards`, the parser this directory already has.

`where` names what was consulted, so a refusal can say «&nbsp;no key at
<path>&nbsp;» rather than «&nbsp;no key&nbsp;»: an absent key and a config that
was never found are two different things to fix. And the refusal that prints
it must quote the SENTENCE — `no boards.<board>.override_robots: true in
<path>` — not only the path: a path alone reads as «&nbsp;file not found&nbsp;»
(`2ce1048`, #206).
"""

import os
import re

# The SAME shapes `dormant.read_boards` matches, because a second convention
# for the same file is a second file. Two spaces for a board, four for its
# keys, six for a block list's items.
_BOARD_RE = re.compile(r"^  ([A-Za-z0-9_-]+):\s*$")
_KEY_RE = re.compile(r"^    ([A-Za-z0-9_-]+):\s*(.*?)\s*$")
_ITEM_RE = re.compile(r"^      -\s+(\S.*?)\s*$")
# A `- ` item that is a `<key>:` is a MAPPING, not a pointer. Measured on the
# owner's own config 2026-10-21: `boards.workday.employers` is six of them,
# and their continuation lines are indented PAST the dash — so a reader that
# took each `- ` for a pointer stopped at the first and reported ONE.
_MAPPING_RE = re.compile(r"^[A-Za-z0-9_-]+\s*:")

__all__ = ["enabled", "board_value", "contact", "threshold"]


def enabled(board):
    """`(on, where)` for `boards.<board>.override_robots: true` — the sentence quoted either way (#206)."""
    v, where = board_value(board, "override_robots")
    path = where.split(" in ", 1)[1] if " in " in where else None
    if v is not None and v.strip().lower() == "true":
        return True, f"boards.{board}.override_robots: true in {path}"
    if path:
        return False, f"no boards.{board}.override_robots: true in {path}"
    return False, where


def board_value(board, key):
    """`(value, where)` for any `boards.<board>.<key>` — the same door, one more key.

    **#337 (2026-09-13): `boards.hh.contact`.** `api.hh.ru` requires a contact
    address on every request and the plugin never fabricates one: the address
    is the user's own, written by the user in their config, read here by the
    one function that opens the config, sent to that host and printed
    nowhere. A second reader in `hh.py` would be the profile creeping into the
    adapters by a second door — the guard in tests/ keeps the door one."""
    from _secrets import _workspace
    ws = _workspace()
    if not ws:
        return None, "no workspace resolved (JOB_HUNT_HOME unset, nothing remembered)"
    path = os.path.join(ws, "config.yml")
    if not os.path.exists(path):
        return None, f"no config.yml at {path}"
    from dormant import read_boards
    try:
        boards = read_boards(path)
    except SystemExit:
        return None, f"{path} could not be read as a job-hunt config (see above)"
    v = str((boards.get(board) or {}).get(key, "")).strip()
    if v:
        return v, f"boards.{board}.{key} in {path}"
    return None, f"no boards.{board}.{key} in {path}"


def contact(board):
    """The user's own contact address for a host that asks who is calling — `(value, where)`, the value for the wire only."""
    return board_value(board, "contact")


def threshold(key):
    """`(text, where)` for a `thresholds.<key>` scalar — THROUGH the one door.

    **The guard `test_only_this_one_adapter_reads_the_config` named four
    files and refused a fifth, and it was right to.** #934 point 2 needs
    `thresholds.stale_after` in `ledger.py`, and the obvious move — build the
    path there — would have widened the door by one exception citing the four
    before it as precedent, *which reads as consistency*. So the DOOR stays
    here and only the MEANING travels: this returns the raw text, and the
    caller decides what a valid value for its own key is. Nothing about a
    delay, a score or a length belongs in this file.

    **Not `read_boards`**: that parser requires a `boards:` block and dies
    without one, which is right for a board key and wrong here — a config
    carrying only `thresholds:` is a config, and a missing block must be an
    absent setting rather than a refusal.

    `where` names what was consulted on every path, including the ones that
    find nothing: a value that came from this file and a value that came from
    a caller's own default read identically otherwise, and that is how a
    figure acquires a provenance it never had.
    """
    from _secrets import _workspace
    ws = _workspace()
    if not ws:
        return None, "no workspace resolved (JOB_HUNT_HOME unset, nothing remembered)"
    path = os.path.join(ws, "config.yml")
    if not os.path.exists(path):
        return None, f"no config.yml at {path}"
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        return None, f"{path} could not be read ({type(exc).__name__})"
    inside = False
    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith((" ", "\t")):
            # `boards:` takes indented keys too, so a reader that matched on
            # the key alone would take it from anywhere in the file — which is
            # how one board's setting silently becomes a global one.
            inside = raw.rstrip() == "thresholds:"
            continue
        if not inside:
            continue
        name, _, val = raw.strip().partition(":")
        if name.strip() != key:
            continue
        val = val.split("#", 1)[0].strip()
        if val:
            return val, f"thresholds.{key}: {val} in {path}"
        return None, f"thresholds.{key} in {path} has no value"
    return None, f"no thresholds.{key} in {path}"


def employers(board):
    """`(pointers, where)` for `boards.<board>.employers` — BOTH list forms.

    **Measured 2026-10-21 by running `dormant.read_boards` on a fixture, not
    by reading it** (#1094 point 4a):

        employers: [scandit, nexthink]    ->  '[scandit, nexthink]'   a STRING
        employers:                        ->  ''        <- the items are SKIPPED
          - swisscom
          - roche

    `read_boards` skips a nested list by design — *«&nbsp;a nested list or map:
    not ours&nbsp;»* — so the block form arrives as a key whose value is empty,
    and `board_value` collapses that into `None` by its `if v:`. Its caller
    then prints **`no boards.<board>.employers in <path>`**: a sentence that
    names the file and denies two employers the file configures. That is the
    false zero of `shared/false-zero-cost.md` at the one place the user cannot
    see it, and it is the shape a migration writes FIRST — nobody writes six
    employers as an inline list.

    So the lines are read here, as `threshold()` reads them, and for a kindred
    reason: that parser cannot answer this question at all, rather than merely
    dying on a config without a `boards:` block. The three returns are not
    interchangeable:

        ([...], where)   the pointers, in file order, duplicates KEPT
        ([],    where)   the key is ABSENT — this board configures no employer
        (None,  where)   a shape that was NOT READ — never an empty list

    The third is the whole point. `[]` says «&nbsp;nothing is configured&nbsp;»
    and `None` says «&nbsp;I could not tell&nbsp;»; a caller that renders them
    alike has published a zero it never measured.
    """
    from _secrets import _workspace
    ws = _workspace()
    if not ws:
        return None, "no workspace resolved (JOB_HUNT_HOME unset, nothing remembered)"
    path = os.path.join(ws, "config.yml")
    if not os.path.exists(path):
        return None, f"no config.yml at {path}"
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        return None, f"{path} could not be read ({type(exc).__name__})"
    return employers_in(lines, board, path)


def employers_in(lines, board, path):
    """The reading itself, on LINES — so every shape can be exercised.

    Taking lines rather than a path is what lets a guard reach the branch that
    matters: a workspace is resolved from the environment, and a test that has
    to build one reaches the easy branches only.
    """
    from dormant import unquote
    at = _employers_line(lines, board)
    if at is None:
        return [], f"no boards.{board}.employers in {path}"
    # A trailing comment is ordinary in this file — and it is the expensive
    # half of it: 302 of its 508 lines are comments saying when a tenant was
    # exercised. `threshold()` strips one the same way, two functions up, so
    # doing it differently here would be a second convention for one file.
    rest = _KEY_RE.match(lines[at]).group(2).split("#", 1)[0].strip()
    if rest:
        if not (rest.startswith("[") and rest.endswith("]")):
            return None, (f"boards.{board}.employers at {path}:{at + 1} carries "
                          f"{rest!r}, which is neither an inline list nor a "
                          f"block list — a shape to fix, NOT an absence")
        items = [unquote(x.strip()) for x in rest[1:-1].split(",") if x.strip()]
        if not items:
            return None, (f"boards.{board}.employers at {path}:{at + 1} is an "
                          f"EMPTY inline list — a key written and left blank "
                          f"is a shape to fix, not a board with no employers")
        return items, (f"boards.{board}.employers in {path} "
                       f"({len(items)} inline)")
    items = []
    for raw in lines[at + 1:]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = _ITEM_RE.match(raw)
        if not m:
            break
        item = unquote(m.group(1).strip())
        if _MAPPING_RE.match(item):
            return None, (f"boards.{board}.employers at {path}:{at + 1} is a "
                          f"block list of MAPPINGS, not of pointers — and its "
                          f"items' own keys are indented past the `- `, so a "
                          f"reader that took each dash for a pointer reports "
                          f"ONE where the file holds several. This is the "
                          f"shape BEFORE #1094 point 4b; it is a migration "
                          f"still owed, NOT an absence of employers")
        items.append(item)
    if not items:
        return None, (f"boards.{board}.employers at {path}:{at + 1} has no "
                      f"value and no `- ` item under it — a key that carries "
                      f"nothing is a shape to fix, not a board with no "
                      f"employers")
    return items, f"boards.{board}.employers in {path} ({len(items)} block)"


def _employers_line(lines, board):
    """The index of `boards.<board>.employers`, or None if the key is absent."""
    inside, here = False, False
    for i, raw in enumerate(lines):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith(" "):
            # `boards:` takes indented keys too, so a reader matching on the
            # key alone would take it from anywhere in the file.
            inside, here = raw.rstrip() == "boards:", False
            continue
        if not inside:
            continue
        m = _BOARD_RE.match(raw)
        if m:
            here = m.group(1) == board
            continue
        if not here:
            continue
        m = _KEY_RE.match(raw)
        if m and m.group(1) == "employers":
            return i
    return None
