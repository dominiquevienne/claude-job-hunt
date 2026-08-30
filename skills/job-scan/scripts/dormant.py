#!/usr/bin/env python3
"""Which dormant boards are due for a yield re-check?

A board goes **dormant** when a real run showed it carries nothing for this
candidate — not when it broke, and not when the user never wanted it. The
difference matters: a board that is merely off should never be mentioned again,
while a dormant one is a bet that could come good. `jobs.bobst.com` is the case
that produced this file: BOBST is 25 minutes from the candidate and runs on an
adapter that works, and on 2026-08-30 its ten open vacancies were *all*
apprenticeships. Wrong month, not wrong board.

Dormancy is four flat keys under `boards.<name>` in the user's `config.yml`,
alongside `enabled: false`:

    boards:
      umantis:
        enabled: false
        dormant_since: "2026-08-30"
        dormant_reason: "10 vacances, toutes des apprentissages et des stages"
        recheck_after: "2026-11-30"
        recheck_count: 0

**`enabled: false` with no `dormant_since` is a hard off.** It is never probed,
never reported and never proposed — that state predates this file and keeps its
meaning exactly. Dormancy is opt-in, and only the user (or a run that measured
a zero) may write it.

    dormant.py list  --config <path>          # every dormant board, due or not
    dormant.py due   --config <path>          # only those whose date has passed
    dormant.py next  --count <n>              # the next re-check date to write

Output: one JSON object per line, or nothing at all when nothing is due —
which is the common case and is not an error.

**Every failure here is loud.** A config this cannot parse exits non-zero and
says which line defeated it, because the silent failure available to a tool
like this one is to report "nothing due" for a file it never understood, and
that reads exactly like a healthy workspace.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys

# The back-off. A dormant board that keeps coming back empty must not keep
# costing the user a decision every quarter forever, so each re-check that
# changes nothing pushes the next one further out.
BACKOFF_DAYS = [90, 180, 365]


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def parse_date(s, where):
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        die(f"{where}: {s!r} is not a YYYY-MM-DD date")


# ----------------------------------------------------------------- parsing ---
# Deliberately NOT a YAML parser. It reads exactly one block — `boards:` — and
# only the flat scalar keys inside each board, which is all dormancy uses. Any
# shape it does not recognise is an error, never a shrug: see the module
# docstring on why "nothing due" is the dangerous answer here.
#
# PyYAML is not assumed. It is absent on a stock macOS python3, and a plugin
# that needs a pip install before it can read its own config has moved the
# failure rather than handled it.

BOARD_RE = re.compile(r"^  ([A-Za-z0-9_-]+):\s*$")
KEY_RE = re.compile(r"^    ([A-Za-z0-9_-]+):\s*(.*?)\s*$")


def unquote(v):
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def read_boards(path):
    if not os.path.exists(path):
        die(f"no config at {path}")
    lines = open(path, encoding="utf-8").read().splitlines()

    start = None
    for i, line in enumerate(lines):
        if line.rstrip() == "boards:":
            start = i + 1
            break
    if start is None:
        die(f"{path} has no `boards:` block — is this a job-hunt config.yml?")

    boards, name = {}, None
    for i in range(start, len(lines)):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith("  "):          # de-indented: the block is over
            break
        m = BOARD_RE.match(raw)
        if m:
            name = m.group(1)
            # Last-wins is what a YAML parser would do here, and it is the wrong
            # answer for this file: a board accidentally listed twice would lose
            # its dormancy to the copy that has none, silently, and the board
            # would simply never come back. Caught while testing this script.
            if name in boards:
                die(f"{path}:{i+1}: board `{name}` is declared twice "
                    f"(already at line {boards[name]['_line']}). The second "
                    f"declaration would silently replace the first — including "
                    f"its dormancy. Merge them")
            boards[name] = {"_line": i + 1}
            continue
        m = KEY_RE.match(raw)
        if m:
            if name is None:
                die(f"{path}:{i+1}: a key before any board name — {raw.strip()!r}")
            boards[name][m.group(1)] = unquote(m.group(2))
            continue
        if raw.startswith("      ") or raw.lstrip().startswith("- "):
            continue                          # a nested list or map: not ours
        die(f"{path}:{i+1}: cannot read this line inside `boards:` — {raw.strip()!r}")
    return boards


# -------------------------------------------------------------- dormancy ---

def dormant_rows(path, today):
    rows = []
    for name, b in sorted(read_boards(path).items()):
        since = b.get("dormant_since")
        if not since:
            continue                          # enabled, or a hard off
        if b.get("enabled", "").lower() == "true":
            die(f"{path}:{b['_line']}: board `{name}` is both enabled and dormant. "
                f"Dormancy means off — remove `dormant_since` to wake it, or set "
                f"`enabled: false`. Refusing to guess which was meant")
        after = b.get("recheck_after")
        if not after:
            die(f"{path}:{b['_line']}: board `{name}` has `dormant_since` but no "
                f"`recheck_after`. A dormant board with no date is one that never "
                f"comes back, which is a hard off wearing dormancy's clothes")
        d_since = parse_date(since, f"{path}:{b['_line']} dormant_since")
        d_after = parse_date(after, f"{path}:{b['_line']} recheck_after")
        try:
            count = int(b.get("recheck_count", "0"))
        except ValueError:
            die(f"{path}:{b['_line']}: recheck_count must be a whole number")
        rows.append({
            "board": name,
            "dormant_since": d_since.isoformat(),
            "dormant_reason": b.get("dormant_reason", ""),
            "recheck_after": d_after.isoformat(),
            "recheck_count": count,
            "days_until_due": (d_after - today).days,
            "due": d_after <= today,
            "config_line": b["_line"],
            "next_recheck_if_still_empty": next_date(today, count + 1).isoformat(),
        })
    return rows


def next_date(today, count):
    step = BACKOFF_DAYS[min(count, len(BACKOFF_DAYS) - 1)]
    return today + dt.timedelta(days=step)


# ------------------------------------------------------------------- main ---

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    default_cfg = os.path.join(
        os.environ.get("JOB_HUNT_HOME",
                       os.path.expanduser("~/Documents/job_applications")),
        "config.yml")

    for c in ("list", "due"):
        p = sub.add_parser(c, help=f"{c} dormant boards")
        p.add_argument("--config", default=default_cfg)
        p.add_argument("--today", help="override today, for testing (YYYY-MM-DD)")

    p = sub.add_parser("next", help="the date to write after a re-check found nothing")
    p.add_argument("--count", type=int, default=0,
                   help="the board's current recheck_count (before this re-check)")
    p.add_argument("--today", help="override today, for testing (YYYY-MM-DD)")

    a = ap.parse_args()
    today = parse_date(a.today, "--today") if a.today else dt.date.today()

    if a.cmd == "next":
        print(json.dumps({"recheck_after": next_date(today, a.count + 1).isoformat(),
                          "recheck_count": a.count + 1}))
        return

    rows = dormant_rows(a.config, today)
    if a.cmd == "due":
        rows = [r for r in rows if r["due"]]
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

    n_dormant = len(dormant_rows(a.config, today))
    if a.cmd == "due":
        print(f"[dormant] {len(rows)} due of {n_dormant} dormant board(s)",
              file=sys.stderr)
    else:
        print(f"[dormant] {n_dormant} dormant board(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
