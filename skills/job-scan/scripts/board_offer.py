#!/usr/bin/env python3
"""May we offer to switch this board on? — the four states of a board in
someone's `config.yml`, and the only one that is an omission.

**Issue #80.** `cover-letter` handles a pasted URL from a board with *no*
adapter (file a `board-request`, silently). It says nothing about the more
useful case: **the adapter exists and works, and the board is simply not in the
user's config.** They go on pasting URLs one at a time from a board `job-scan`
could sweep for them every week.

**But three of the four states are deliberate, and re-offering them is
nagging.** `skills/job-scan/scripts/dormant.py` already draws the line this
depends on:

    absent from `boards:`          nobody ever decided — **this is the offer**
    enabled: true                  already swept; nothing to offer
    enabled: false, no dormancy    a HARD OFF. "never probed, never reported
                                   and never proposed" — dormant.py's words
    enabled: false + dormant_since a bet that could come good, and dormant.py
                                   owns its re-check date. Not this skill's
                                   business, and re-offering it every time a
                                   URL is pasted would nag the user out of
                                   trusting the offer at all

**A decline has somewhere to live already**: `enabled: false` with no
`dormant_since` is the hard off, and it silences this permanently. That is why
no `declined:` key is invented here — the vocabulary already has the word.

WHAT THE OFFER MUST SAY. Offering a board that will fail on its next run for a
missing setting is worse than silence, so this reports the adapter's **own**
declared requirements — the `| Key | Required |` table in
`shared/boards/<board>.md` — and says plainly when an adapter declares none
rather than implying it needs nothing. Measured 2026-09-02: **49 of 67
adapters carry that table**, and 10 mention credentials in an `~/.<board>.env`
file.

    board_offer.py check --board jobup
    board_offer.py check --board adzuna --config ~/Documents/job_applications/config.yml

One JSON object on stdout. `offer` is the answer; `reason` is why, in words
meant to be shown to nobody but the person reading this code.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOARDS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "shared", "boards"))
DEFAULT_CONFIG = os.path.join(
    os.environ.get("JOB_HUNT_HOME",
                   os.path.expanduser("~/Documents/job_applications")),
    "config.yml")

sys.path.insert(0, HERE)
from dormant import read_boards          # noqa: E402  the config parser lives there

REQ_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*yes\s*\|(.*)$", re.M)
CREDS = re.compile(r"~/\.[a-z0-9_-]+\.env|APP_ID|APP_KEY|API key", re.I)


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def adapter_path(board):
    # `README.md` sits in the same directory and is the index, not a board.
    # A check on it would report an offerable adapter that cannot be enabled.
    if board.lower() in ("readme",):
        return None
    p = os.path.join(BOARDS, f"{board}.md")
    return p if os.path.exists(p) else None


def requirements(path):
    """What the adapter's own Configuration table says it needs.

    Returns `(keys, credentials_line, declared)`. **`declared` is False when
    the adapter has no such table** — 18 of 67 do not — and the caller must
    say "this adapter does not declare its settings" rather than "it needs
    nothing". The two are not the same sentence.
    """
    text = open(path, encoding="utf-8").read()
    if "| Key | Required" not in text:
        return [], None, False
    keys = [{"key": m.group(1), "note": m.group(2).strip(" |")}
            for m in REQ_ROW.finditer(text)
            if m.group(1) != "enabled"]
    # Prefer the concrete file name (`~/.adzuna.env`) over a variable name:
    # it is the thing the person has to create, and the adapter's page
    # documents it. The variable is what they put inside it.
    env = re.search(r"~/\.[a-z0-9_-]+\.env", text)
    hit = env or CREDS.search(text)
    return keys, (hit.group(0) if hit else None), True


def cmd_check(a):
    path = adapter_path(a.board)
    out = {"board": a.board, "adapter": None, "state": None, "offer": False,
           "reason": None, "requires": [], "requirements_declared": None,
           "credentials_hint": None}
    if path is None:
        out["state"] = "no-adapter"
        out["reason"] = ("no `shared/boards/%s.md`. This is the board-request "
                         "path and it stays silent — a user who asked for a "
                         "cover letter did not ask to file a feature request."
                         % a.board)
        print(json.dumps(out, ensure_ascii=False))
        return
    out["adapter"] = os.path.relpath(path, os.path.join(HERE, "..", "..", ".."))

    if not os.path.exists(a.config):
        out["state"] = "no-config"
        out["reason"] = (f"no config at {a.config} — this is a first run, and "
                         f"`shared/setup.md` owns it. Do not offer one board "
                         f"to somebody who has no workspace yet.")
        print(json.dumps(out, ensure_ascii=False))
        return

    boards = read_boards(a.config)
    row = boards.get(a.board)
    if row is None:
        keys, creds, declared = requirements(path)
        out.update(state="absent", offer=True, requires=keys,
                   requirements_declared=declared, credentials_hint=creds,
                   reason="not in `boards:` at all — nobody ever decided "
                          "about this board, which is the one state that is "
                          "an omission rather than a choice.")
        print(json.dumps(out, ensure_ascii=False))
        return

    enabled = str(row.get("enabled", "")).strip().lower() in ("true", "yes")
    if enabled:
        out.update(state="enabled",
                   reason="already enabled; `job-scan` sweeps it. Nothing to "
                          "offer.")
    elif row.get("dormant_since"):
        out.update(state="dormant",
                   reason=f"dormant since {row['dormant_since']} — a measured "
                          f"bet, and `dormant.py` owns its re-check date "
                          f"({row.get('recheck_after', 'unset')}). Re-offering "
                          f"it on every pasted URL would nag.")
    else:
        out.update(state="off",
                   reason="`enabled: false` with no dormancy is a hard off: "
                          "never probed, never reported, never proposed. The "
                          "user decided, and this is where a previous decline "
                          "would have been written.")
    print(json.dumps(out, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="may we offer to enable this board?")
    c.add_argument("--board", required=True,
                   help="the adapter's name, i.e. `shared/boards/<name>.md`")
    c.add_argument("--config", default=DEFAULT_CONFIG)
    c.set_defaults(func=cmd_check)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
