#!/usr/bin/env python3
"""Read only what the decision needs out of `job-pipeline.md`.

**Issue #77 asked whether the ledger should be split by month. Measured, the
answer is no — it should stop being read whole.**

MEASURED ON ONE REAL LEDGER, 2026-09-02:

    job-pipeline.md ........ 499 320 bytes   2 926 lines
      header ...............  14 426   (3 %)
      ## Ads ............... 283 918  (57 %)    474 ad rows
      ## Log ............... 200 976  (40 %)  2 233 lines

    inside ## Ads, by column:
      Note ................. 211 892 bytes — **78.5 %** of all cell content
      Role .................  16 895
      ID ...................  11 921
      everything else ......  25 000 or so

    status: discarded 314 · no-go 91 · applied 46 · todo 17 · rejected 6
            → closed 411 of 474 = 87 %

**The step that reads this file does so to build one thing: the exclusion set,
the ids never to propose again.** That needs `ID` and `Status`, which is
**16 531 bytes — 3.3 % of the file.** The other 96.7 % is read into context on
every scan and decides nothing: `## Log` is a history nothing consults, and
`Note` is prose written for the person, never parsed.

So the fix is not a new file layout. **It is to stop reading 96.7 % of one.**
No format change, no migration, no new file — and `shared/pipeline-format.md`
stays the contract it is.

WHY A SCRIPT AND NOT AN `awk` ONE-LINER: **ten of the 474 rows contain `\\|`,
an escaped pipe inside a cell.** Splitting a row on `|` mis-aligns exactly
those ten and silently shifts every column after the escape — it produced a
row whose status read `42` while writing this. A ledger tool that corrupts 2 %
of rows without saying so is worse than no tool, and this is precisely the risk
the issue names for any migration.

    ledger.py index                 id, status and match — the exclusion set
    ledger.py rows --status todo    the full rows a run will edit in place
    ledger.py count                 rows and section sizes
    ledger.py verify --before N     refuse a write that lost a row

Exit codes: 2 unreadable, 5 a row count that went down.
"""

import argparse
import json
import os
import re
import sys

DEFAULT = os.path.join(
    os.environ.get("JOB_HUNT_HOME",
                   os.path.expanduser("~/Documents/job_applications")),
    "job-pipeline.md")
SEP = re.compile(r"^\|[\s:|-]+\|$")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[ledger] {msg}", file=sys.stderr)


def cells(line):
    """Split a markdown row on real column breaks only.

    **`\\|` is an escaped pipe, not a break.** Ten rows of 474 carry one, and a
    naive split shifts every column after it — the kind of corruption that
    reads as data rather than as an error.
    """
    holed = line.replace("\\|", "\x00")
    return [c.replace("\x00", "\\|").strip() for c in holed.strip("|").split("|")]


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as e:
        die(f"{path}: {e}")


def ads_table(text, path):
    m = re.search(r"^## Ads\s*$", text, re.M)
    if not m:
        die(f"{path} has no `## Ads` heading — is this a job-pipeline.md?")
    end = re.search(r"^## (?!Ads)", text[m.start() + 1:], re.M)
    seg = text[m.start(): m.start() + 1 + end.start()] if end else text[m.start():]
    lines = [l for l in seg.split("\n") if l.startswith("|")]
    if not lines:
        die(f"{path}: `## Ads` carries no table row. **This is a reading "
            f"failure or an empty ledger, and they are not the same** — the "
            f"section is {len(seg)} characters long.")
    cols = cells(lines[0])
    rows = [l for l in lines[1:] if not SEP.match(l)]
    return cols, rows


def parsed(cols, rows, path):
    out, ragged = [], 0
    for r in rows:
        c = cells(r)
        if len(c) != len(cols):
            ragged += 1
        out.append(dict(zip(cols, c)))
    if ragged:
        # Loud, because a shifted row means a wrong status, and a wrong status
        # means an ad proposed again or one silently buried.
        note(f"{ragged} of {len(rows)} row(s) do not have {len(cols)} cells. "
             f"Their columns are shifted and their status cannot be trusted — "
             f"fix the table before relying on this index. ({path})")
    return out


def status_of(row):
    """`applied 2026-09-01` → `applied`. The vocabulary is fixed and English."""
    s = (row.get("Status") or "").strip()
    return s.split()[0].lower() if s else ""


def cmd_index(a):
    text = read(a.file)
    cols, rows = ads_table(text, a.file)
    data = parsed(cols, rows, a.file)
    closed = {"applied", "rejected", "no-go", "discarded"}
    kept = 0
    for d in data:
        st = status_of(d)
        if a.excluded_only and st not in closed:
            continue
        print(json.dumps({"id": d.get("ID", ""), "status": st,
                          "match": d.get("Match", "")}, ensure_ascii=False))
        kept += 1
    whole = len(text.encode())
    note(f"{kept} row(s) of {len(rows)}. The ledger is {whole} bytes; this "
         f"index is what the exclusion set actually needs. Issue #77.")


def cmd_rows(a):
    """The full rows a run will edit — `todo` by default, 17 of 474 here."""
    text = read(a.file)
    cols, rows = ads_table(text, a.file)
    n = 0
    for r, d in zip(rows, parsed(cols, rows, a.file)):
        if a.status and status_of(d) != a.status:
            continue
        print(r)
        n += 1
    note(f"{n} row(s) with status {a.status!r} of {len(rows)}.")


FU_RE = re.compile(r"\bFU:(\d{4})-(\d{2})-(\d{2})\b")


def cmd_due(a):
    """Rows carrying a follow-up date that has arrived.

    **The one thing a chat transcript cannot keep.** An interview ends with
    *"we will reply by the end of next week"* and a promise to present the file
    internally; a week later the date has passed and nothing knows. `FU:` is
    that date on the row, and this is the reading of it. Issue #69.
    """
    import datetime as dt
    text = read(a.file)
    cols, rows = ads_table(text, a.file)
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    n = 0
    for r, d in zip(rows, parsed(cols, rows, a.file)):
        m = FU_RE.search(r)
        if not m:
            continue
        when = dt.date(*map(int, m.groups()))
        if (when - today).days > a.within:
            continue
        n += 1
        print(json.dumps({
            "id": d.get("ID", ""), "company": d.get("Company", ""),
            "role": d.get("Role", ""), "status": status_of(d),
            "follow_up": when.isoformat(),
            "days": (when - today).days,
            "state": "overdue" if when < today else "due",
        }, ensure_ascii=False))
    if n == 0:
        note(f"no follow-up falls within {a.within} day(s) of {today}. "
             f"**That is an answer, not a clean run**: a row only appears here "
             f"if somebody wrote `FU:` on it after a meeting.")
    else:
        note(f"{n} follow-up(s) due by {today} + {a.within} day(s).")


def fingerprint(path):
    """`<mtime_ns>:<size>` — enough to notice somebody else wrote."""
    st = os.stat(path)
    return f"{st.st_mtime_ns}:{st.st_size}"


def cmd_stamp(a):
    """Take a fingerprint before reading; check it before writing.

    **`read it first, write it last, and never lose a row` is correct for one
    session and is the row-loss mechanism when two run.** The second writer's
    copy was read before the first writer's save, so its write drops every row
    the first one added — no error, no warning, and the file stays
    syntactically perfect. Issue #56.

    This is not hypothetical on this machine: three live sessions were counted
    on 2026-09-01 against one `$JOB_HUNT_HOME`, and the ledger was rewritten
    about fifteen times in one of them.

    **Detect, do not prevent.** No lock file, no daemon, nothing to clean up —
    a lock nobody releases is worse than the problem. A changed fingerprint
    means *re-read, re-apply, and say it happened*, which turns a silent loss
    into a visible retry.

        S=$(ledger.py stamp)          # before reading
        …                             # do the work
        ledger.py stamp --expect "$S" # before writing; exit 5 if it moved
    """
    if not os.path.exists(a.file):
        die(f"{a.file}: no such file", 2)
    now = fingerprint(a.file)
    if not a.expect:
        print(now)
        return
    if now == a.expect:
        note(f"unchanged since it was read ({now}).")
        return
    die(f"**{a.file} changed under you.** It was {a.expect} when you read it "
        f"and it is {now} now — another session has written to it since. "
        f"**Do not write your copy**: it does not contain their rows, and "
        f"writing it would drop them silently. Re-read the file, re-apply "
        f"your changes, and tell the user this happened.", 5)


def cmd_count(a):
    text = read(a.file)
    cols, rows = ads_table(text, a.file)
    heads = [(m.start(), m.group(0).strip())
             for m in re.finditer(r"^#{1,3} .*$", text, re.M)] + [(len(text), "")]
    sections = {t: len(text[s:e].encode())
                for (s, t), (e, _) in zip(heads, heads[1:])}
    print(json.dumps({"file": a.file, "bytes": len(text.encode()),
                      "ad_rows": len(rows), "columns": cols,
                      "sections": sections}, ensure_ascii=False))


def cmd_verify(a):
    """The invariant, as a check rather than as a sentence.

    `shared/pipeline-format.md` opens with *read it first, write it last, and
    never lose a row*. This is that, after the write.
    """
    text = read(a.file)
    _cols, rows = ads_table(text, a.file)
    if len(rows) < a.before:
        die(f"{a.file} now has {len(rows)} ad row(s) and had {a.before} before "
            f"the write. **{a.before - len(rows)} row(s) were lost.** Restore "
            f"the file from the copy taken before the run and do not write "
            f"again until the merge is fixed.", 5)
    note(f"{len(rows)} row(s), was {a.before} — nothing lost "
         f"({len(rows) - a.before} added).")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn, h in (("index", cmd_index, "id, status and match only"),
                        ("rows", cmd_rows, "whole rows, by status"),
                        ("count", cmd_count, "rows and section sizes"),
                        ("due", cmd_due, "follow-up dates that have arrived"),
                        ("stamp", cmd_stamp,
                         "fingerprint before reading, check before writing"),
                        ("verify", cmd_verify, "refuse a write that lost a row")):
        c = sub.add_parser(name, help=h)
        c.add_argument("--file", default=DEFAULT)
        if name == "index":
            c.add_argument("--excluded-only", action="store_true",
                           dest="excluded_only",
                           help="only the statuses that exclude an ad")
        if name == "rows":
            c.add_argument("--status", default="todo")
        if name == "due":
            c.add_argument("--within", type=int, default=3,
                           help="days ahead to include (default 3)")
            c.add_argument("--today", help="YYYY-MM-DD, for testing")
        if name == "stamp":
            c.add_argument("--expect",
                           help="the fingerprint taken before reading. Exits 5 "
                                "if the file moved since")
        if name == "verify":
            c.add_argument("--before", type=int, required=True)
        c.set_defaults(func=fn)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
