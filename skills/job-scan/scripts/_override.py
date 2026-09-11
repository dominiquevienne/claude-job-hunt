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

__all__ = ["enabled"]


def enabled(board):
    """`(on, where)` for `boards.<board>.override_robots: true`."""
    from _secrets import _workspace
    ws = _workspace()
    if not ws:
        return False, ("no workspace resolved (JOB_HUNT_HOME unset, nothing "
                       "remembered)")
    path = os.path.join(ws, "config.yml")
    if not os.path.exists(path):
        return False, f"no config.yml at {path}"
    from dormant import read_boards
    try:
        boards = read_boards(path)
    except SystemExit:            # `read_boards` dies on a shape it cannot read
        return False, f"{path} could not be read as a job-hunt config (see above)"
    block = boards.get(board) or {}
    if str(block.get("override_robots", "")).strip().lower() == "true":
        return True, f"boards.{board}.override_robots: true in {path}"
    return False, f"no boards.{board}.override_robots: true in {path}"
