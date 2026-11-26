"""One reading of the `## Ads` table of `job-pipeline.md`, for `job-report`.

**Issue #1182.** The ledger had THREE readers in the tracked tree, each with
its own row splitter: `ledger.py` in `job-scan`, and `list_applications.py`
and `jobroom_sync.py` here. The two here agreed with `ledger.py` on the real
ledger of 2026-10-22 — `ad_rows: 2823` against `total_rows: 2823` — and they
agreed **by coincidence**, not by construction:

    widths by section      ## Ads {9: 2824}      ## Log {4: 5}

`ledger.py` bounds itself to `## Ads`; the two here read every line of the
file that starts with `|`, keeping the header they found in `## Ads`. The only
non-conformant table in that ledger lives in `## Log` and happens to carry
**four** cells, so it fails their width test and is dropped. Give `## Log` a
nine-column table and its rows become applications — in the two readers whose
number goes into an unemployment-office declaration, and not in the third.

**And a row whose width does not match was lost in silence**, which is the one
failure `_warn` exists to prevent and the one it could not see: the rows were
dropped in `load_rows`, so they never reached `meta`. Its docstring already
carried the argument — *"A count is the one output where an omission is
invisible: the result looks exactly as legitimate whether or not rows were
dropped along the way."*

    a row SHORTER than the header    dropped by `continue`, absent from the
                                     numerator AND the denominator
    a row LONGER than the header     truncated by `cells[: len(columns)]`, so
                                     every column after a stray `|` is shifted
                                     and the status read can be wrong

`ledger.py` tests `!=` and says so, naming the row: *"their columns are
shifted and their status cannot be trusted"*. This module takes the same
verdict — a row of the wrong width is not read — and **counts both
directions**, so `_warn` can print what did not make it into the number.

**Measured, none of the three branches fires on the real ledger**: every row
of `## Ads` carries nine cells and nothing outside it is nine wide. The
branches are declared dead on that corpus rather than presented as live. A
defect behind a path that SUCCEEDS waits for the path to change, and this path
is a count sent to an authority.

**Residue, declared:** `ledger.py` stays a separate copy. Unifying all three
would need a cross-skill import, a pattern this repository has nowhere — all
26 `_*.py` helpers are imported from their own directory — so that is an
architecture decision and not a fix.

**AND THAT RESIDUE IS PERIMED ON ITS SECOND CLAUSE — the pattern it calls
absent EXISTS, twice, and one of the two predates this file.** Measured on the
tracked tree, 2026-11-15: `_secrets.py` resolves `bin/workspace-path.py`, and
`_events_reader.py` resolves `job-sync`'s events reader (#1307 tranche 1). The
paragraph above is CITED and not rewritten: do not read its "a pattern this
repository has nowhere" as true, and do not conclude from "26 helpers" that the
count is still 26 — it is 29, and a count written inside the object it counts
perishes at the next write.

*What the residue got RIGHT does not move: `ledger.py` is still a separate
copy, and unifying it is still an architecture decision. What changes is that
the ARGUMENT against it was the pattern's absence, and the pattern is here.*

**SO THIS MODULE IS NOW THE SINGLE POINT FOR TWO CONSUMERS AND ONE MORE
DIRECTION.** Alongside the reading, it carries the ledger's HEADER CONTRACT and
the normalisation of a row's `Status` and `Note` cells, because those were
**byte-identical copies in two files** — `HEADER_ALIASES` in `jobroom_sync.py`
and in `list_applications.py`, the same twelve keys in the same order — and
four copies of one rule are lost one at a time. `job-sync` reaches them through
its own single resolver, for `export` (#1322).
"""

from __future__ import annotations

import re

SEP_RE = re.compile(r"^:?-{2,}:?$")


def split_row(line: str) -> list[str]:
    """Split a markdown table row, honouring \\| escapes inside cells."""
    body = line.strip().strip("|")
    cells, buf, i = [], "", 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body) and body[i + 1] == "|":
            buf += "|"
            i += 2
            continue
        if ch == "|":
            cells.append(buf.strip())
            buf = ""
            i += 1
            continue
        buf += ch
        i += 1
    cells.append(buf.strip())
    return cells


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(SEP_RE.match(c) for c in cells if c)


def ads_table(text: str, path: str) -> tuple[list[str], list[str]]:
    """The header cells and the row lines of `## Ads`, and nothing else.

    The boundary is the one `skills/job-scan/scripts/ledger.py` uses: from the
    `## Ads` heading to the next `## ` heading that is not `Ads`.
    """
    m = re.search(r"^## Ads\s*$", text, re.M)
    if not m:
        raise SystemExit(
            f"error: {path} has no `## Ads` heading — is this a "
            f"job-pipeline.md? `shared/pipeline-format.md` declares it, and "
            f"`ledger.py` refuses the file for the same reason.")
    end = re.search(r"^## (?!Ads)", text[m.start() + 1:], re.M)
    seg = (text[m.start(): m.start() + 1 + end.start()] if end
           else text[m.start():])
    lines = [l for l in seg.split("\n") if l.strip().startswith("|")]
    if not lines:
        raise SystemExit(
            f"error: {path}: `## Ads` carries no table row. **A reading "
            f"failure and an empty ledger are not the same thing** — the "
            f"section is {len(seg)} characters long.")
    return split_row(lines[0]), [l for l in lines[1:]
                                 if not is_separator(split_row(l))]


def load(path: str, header_aliases: dict[str, str]) -> tuple[list[dict],
                                                             dict[str, int]]:
    """`(rows, skipped)` — the rows of `## Ads`, and what did not make it.

    `skipped` names the direction, because the two are different defects: a
    short row is a cell missing, a long row is an unescaped `|` shifting every
    column after it. Neither is read, and both are counted so the caller can
    say so.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        raise SystemExit(f"error: pipeline file not found: {path}")

    head, lines = ads_table(text, path)
    columns = [header_aliases.get(c.strip().lower(), c.strip().lower())
               for c in head]
    skipped = {"short": 0, "long": 0, "no_status_column": 0}
    rows: list[dict] = []
    for line in lines:
        cells = split_row(line)
        if len(cells) < len(columns):
            skipped["short"] += 1
            continue
        if len(cells) > len(columns):
            skipped["long"] += 1
            continue
        if "statut" not in columns:
            skipped["no_status_column"] += 1
            continue
        rows.append(dict(zip(columns, cells)))
    return rows, skipped


# ---------------------------------------------------------------------------
# The ledger's HEADER CONTRACT, and the normalisation of one row
# ---------------------------------------------------------------------------
#  These were written out twice, identically, in `jobroom_sync.py` and
#  `list_applications.py`, and a third consumer — `events_sheet.py export`,
#  #1322 — would have made three. The copies AGREED, which is exactly why
#  nothing ever rang: a divergence is what a copy announces, and an agreement
#  is what it hides until one hand edits one of them.

HEADER_ALIASES = {
    "id": "id",
    "role": "poste", "poste": "poste",
    "company": "societe", "société": "societe", "societe": "societe",
    "location / mode": "lieu", "lieu / mode": "lieu", "lieu": "lieu",
    "posted": "publiee", "publiée": "publiee", "publiee": "publiee",
    "match": "match",
    "pay": "pay",
    "status": "statut", "statut": "statut",
    "note": "note",
}

#  Statuses that mean an application actually LEFT. `no-go` never did, and
#  `todo`/`discarded` carry no date — none of them belong in a declaration,
#  and none of them belong in the sheet either.
SENT_KINDS = {"applied", "rejected", "postulé", "postule", "refusé", "refuse"}

STATUS_RE = re.compile(
    r"^(?P<kind>[\w'’-]+(?:\s+[\w'’-]+)*?)(?:\s+le)?\s+"
    r"(?P<date>\d{4}-\d{2}-\d{2})\s*$"
)
JR_DECLARED_RE = re.compile(r"JR:(\d{4}-\d{2}-\d{2})")
JR_MISSING_RE = re.compile(r"JR:missing")
#  A third state the vocabulary needed: `JR:missing` is "not declared yet" and
#  `JR:<date>` is "declared"; neither covers an application the candidate has
#  decided, deliberately, never to declare.
JR_WAIVED_RE = re.compile(r"JR:waived(?:\s+(\d{4}-\d{2}-\d{2}))?")
#  A fourth state, issue #1332: `JR:<date>` dates the DECLARATION, and nothing
#  said that the RESULT was later corrected in job-room. A refusal entered
#  there satisfied «refused after declared» forever, so `plan` re-proposed it
#  at every session. `JR:result <date>` is the day the negative answer was
#  entered; the date is REQUIRED, because the test compares it to the refusal.
JR_RESULT_RE = re.compile(r"JR:result\s+(\d{4}-\d{2}-\d{2})")


def annotate(row: dict) -> dict:
    """Add `date`, `kind` and the four `jr_*` fields to a loaded row.

    **The row is annotated IN PLACE and returned**, so a caller that keeps its
    own list keeps the same dicts. `kind` falls back to the whole cell folded
    to lower case when no date can be read, which is what makes `sent()` false
    for it rather than raising: a status nobody can parse is not an
    application that left, and it is not an error either.
    """
    m = STATUS_RE.match(row.get("statut") or "")
    row["date"] = m.group("date") if m else None
    row["kind"] = (m.group("kind").lower() if m
                   else (row.get("statut") or "").lower())
    note = row.get("note", "")
    row["jr_missing"] = bool(JR_MISSING_RE.search(note))
    jr = JR_DECLARED_RE.search(note)
    row["jr_declared"] = jr.group(1) if jr else None
    w = JR_WAIVED_RE.search(note)
    row["jr_waived"] = (w.group(1) or True) if w else None
    r = JR_RESULT_RE.search(note)
    row["jr_result"] = r.group(1) if r else None
    return row


def sent(row: dict) -> bool:
    """Whether this row is an application that LEFT — date AND a sent kind.

    Both terms are needed and the AND is the point: a `rejected` with no date
    is a cell nobody can read, and a dated `todo` never left.
    """
    return bool(row.get("date")) and row.get("kind") in SENT_KINDS


def skipped_lines(skipped: dict[str, int]) -> list[str]:
    """The warning lines for `skipped`, empty when nothing was dropped.

    **An omission that announces itself is the whole point** — and a warning
    that fires on every run is no better than one that never fires, so this
    returns nothing when there is nothing to say.
    """
    out = []
    if skipped.get("short"):
        out.append(
            f"  ! {skipped['short']} row(s) of `## Ads` have FEWER cells than "
            f"the header, so they")
        out.append(
            "    were not counted — their status cannot be trusted; fix the "
            "table")
    if skipped.get("long"):
        out.append(
            f"  ! {skipped['long']} row(s) of `## Ads` have MORE cells than "
            f"the header — an unescaped")
        out.append(
            "    `|` shifts every column after it, so they were not counted "
            "either")
    if skipped.get("no_status_column"):
        out.append(
            f"  ! the `## Ads` header carries no status column, so all "
            f"{skipped['no_status_column']} row(s)")
        out.append(
            "    were dropped — this is not «no applications», it is a "
            "header that cannot be read")
    return out
