#!/usr/bin/env python3
"""List job applications from the pipeline file within a date range.

Reads the markdown table in ~/Documents/job_applications/job-pipeline.md and
keeps the rows whose status carries a date inside [from, to].

Defaults: from = 1st of the current month, to = today.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

JOB_HUNT_HOME = os.environ.get(
    "JOB_HUNT_HOME", os.path.expanduser("~/Documents/job_applications")
)
DEFAULT_PIPELINE = os.path.join(JOB_HUNT_HOME, "job-pipeline.md")

# The statuses that mean an application actually left. `no-go` never did, and
# `todo`/`discarded` carry no date — the same set the ledger's own format fixes.
SENT_KINDS = ("applied", "rejected", "postulé", "refusé")

# "applied 2026-08-04", "rejected 2026-08-04", "no-go 2026-08-04".
# The date is what we filter on. The older French form ("postulé le 2026-08-04")
# is still accepted so a ledger that has not been migrated keeps working.
STATUS_RE = re.compile(
    r"^(?P<kind>[\w'’-]+(?:\s+[\w'’-]+)*?)(?:\s+le)?\s+(?P<date>\d{4}-\d{2}-\d{2})\s*$"
)

# Column names are read from the table header, not hardcoded: a column inserted
# in the middle (Pay, 2026-08-26) used to shift every field silently and made
# the Status cell read the wrong value. Only these two are required.
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

# An ad id is prefixed by its board ("linkedin:123", "jobup:<uuid>"). A bare
# numeric id is a pre-migration LinkedIn row.
AD_URL = {
    "linkedin": "https://www.linkedin.com/jobs/view/{id}/",
    "jobup": "https://www.jobup.ch/fr/emplois/detail/{id}/",
    "indeed": "https://www.indeed.com/viewjob?jk={id}",
}


def ad_url(raw_id: str) -> str:
    """Rebuild the ad URL from a possibly board-prefixed id."""
    if not raw_id or raw_id == "—":
        return ""
    board, _, ident = raw_id.partition(":")
    if not ident:                       # bare id: legacy LinkedIn row
        board, ident = "linkedin", raw_id
    tpl = AD_URL.get(board.lower())
    return tpl.format(id=ident) if tpl else ""


def parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        raise SystemExit(f"error: invalid date {value!r} (expected YYYY-MM-DD)")


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
    return all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c)


# `IV:2026-09-02 phone`, `IV:2026-09-11 on-site` — repeatable, the qualifier
# optional and short. The date is the meeting's, never the application's.
IV_RE = re.compile(r"\bIV:(\d{4}-\d{2}-\d{2})(?:\s+([A-Za-z][\w -]{0,18}))?")


def load_rows(path: str) -> list[dict]:
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except FileNotFoundError:
        raise SystemExit(f"error: pipeline file not found: {path}")

    rows, columns = [], None
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = split_row(stripped)
        if is_separator(cells):
            continue
        if cells and cells[0].strip().lower() == "id":          # header row
            columns = [HEADER_ALIASES.get(c.strip().lower(), c.strip().lower()) for c in cells]
            continue
        if columns is None or len(cells) < len(columns):
            continue
        row = dict(zip(columns, cells[: len(columns)]))
        if "statut" not in row:
            continue
        m = STATUS_RE.match(row["statut"])
        row["date"] = m.group("date") if m else None
        row["kind"] = m.group("kind").lower() if m else row["statut"].lower()
        row["url"] = ad_url(row.get("id", ""))
        row["jr_missing"] = "JR:missing" in row.get("note", "")
        # **`IV:` is the third use of a convention, not a second convention.**
        # `JR:` records a declaration, `FU:` a promised date, `IV:` a meeting
        # that happened — all three live in the Note, none of them touches the
        # status, and no run strips any of them. Issue #52.
        row["interviews"] = [
            {"date": m.group(1), "kind": (m.group(2) or "").strip() or None}
            for m in IV_RE.finditer(row.get("note", ""))
        ]
        rows.append(row)
    if columns is None:
        raise SystemExit(f"error: no table header found in {path} (expected a row starting with '| ID |')")
    return rows


def report_interviews(rows, start, end, args) -> int:
    """Applications that reached a meeting — the outcome metric.

    **Volume sent is an effort metric; interviews obtained is the outcome
    one**, and until `IV:` existed the ledger could count the first and not the
    second. An `applied` row that produced a meeting looked exactly like one
    sent into silence three weeks ago.

    **Two numbers, two denominators, both named** — because they answer
    different questions and averaging them would answer neither:

    * meetings that *happened* in the window, whenever the application went
      out;
    * applications *sent* in the window that have since produced one — which
      is systematically low near the end of a window, since an application
      sent yesterday has had a day to bear fruit.
    """
    with_iv = [r for r in rows if r["interviews"]]
    in_window = [
        r for r in with_iv
        if any(start <= dt.date.fromisoformat(iv["date"]) <= end
               for iv in r["interviews"])
    ]
    # **Only `applied` rows here, and the reason is in the ledger's own
    # format**: `applied → rejected` is a legitimate transition, so a
    # `rejected` row's date is the employer's *answer*, not the day the
    # application left — the send date is overwritten and gone. Counting those
    # as "sent in the window" would date an application by the day it was
    # refused. `SENT_KINDS` is still right for the main report, which counts
    # applications that left at all; it is wrong for a denominator about *when*
    # they left.
    sent = [r for r in rows
            if r["date"] and r["kind"] in ("applied", "postulé")
            and start <= dt.date.fromisoformat(r["date"]) <= end]
    sent_with_iv = [r for r in sent if r["interviews"]]

    if args.format == "json":
        print(json.dumps({
            "meta": {"from": start.isoformat(), "to": end.isoformat(),
                     "meetings_in_window": len(in_window),
                     "applications_sent_in_window": len(sent),
                     "of_those_with_a_meeting": len(sent_with_iv),
                     "rows_with_any_interview": len(with_iv)},
            "applications": in_window,
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"Interviews between {start} and {end}")
    print()
    if not in_window:
        print("  No meeting recorded in this window.")
        print()
        print("  **Which of the two silences this is matters**: a row only "
              "appears here if somebody wrote an `IV:` marker on it after a "
              "meeting. No marker is not the same fact as no meeting.")
        if with_iv:
            print(f"  ({len(with_iv)} row(s) in the ledger carry an interview "
                  f"marker outside this window.)")
        return 0

    for r in sorted(in_window, key=lambda x: x["interviews"][0]["date"]):
        meetings = ", ".join(
            f"{iv['date']}{' ' + iv['kind'] if iv['kind'] else ''}"
            for iv in r["interviews"])
        print(f"  {r['societe']} — {r['poste']}")
        print(f"      {r['statut']}   ·   met: {meetings}")
        if r["url"]:
            print(f"      {r['url']}")
    print()
    print(f"  {len(in_window)} application(s) had a meeting in this window.")
    print(f"  Of the {len(sent)} application(s) still marked `applied` and "
          f"dated between {start} and {end}, {len(sent_with_iv)} has/have "
          f"produced a meeting so far.")
    print("  **Those two numbers have different denominators and neither is a "
          "conversion rate**: a meeting here may belong to an application sent "
          "months ago, an application sent yesterday has had a day — and a row "
          "that reached `rejected` carries the employer's answer date, not the "
          "day it was sent, so it is left out of the second number rather than "
          "dated wrongly.")
    return 0


def _warn(meta: dict) -> None:
    """Print everything that did NOT make it into the number.

    A count is the one output where an omission is invisible: the result looks
    exactly as legitimate whether or not rows were dropped along the way.
    """
    if meta["unparsed_status"]:
        print()
        print(f"  ! {len(meta['unparsed_status'])} status value(s) not understood, so those rows")
        print("    were not counted:", ", ".join(repr(s) for s in meta["unparsed_status"][:5]))
    if meta["no_url"]:
        print(f"  ! {meta['no_url']} counted row(s) have no reconstructible ad URL")
    if meta["legacy_french"]:
        print(f"  ! {meta['legacy_french']} row(s) still use the old French status vocabulary")
        print("    — they were counted, but the ledger is worth migrating")
    if meta["jr_missing"]:
        print(f"  ! {meta['jr_missing']} application(s) carry JR:missing — sent but not yet")
        print("    declared to the unemployment office (whole ledger, not just this period)")


def main() -> int:
    today = dt.date.today()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from", dest="start", help="start date YYYY-MM-DD (default: 1st of current month)")
    ap.add_argument("--to", dest="end", help="end date YYYY-MM-DD (default: today)")
    ap.add_argument(
        "--status",
        default="applied,rejected",
        help=(
            "comma-separated status kinds to keep, or 'all' "
            "(default: applied,rejected — BOTH are applications that were actually "
            "sent; counting 'applied' alone silently drops every application an "
            "employer turned down)"
        ),
    )
    ap.add_argument("--file", default=DEFAULT_PIPELINE, help=f"pipeline file (default: {DEFAULT_PIPELINE})")
    ap.add_argument("--format", choices=("table", "json", "md"), default="table")
    ap.add_argument(
        "--interviews", action="store_true",
        help="applications that reached an interview. Filters on the MEETING "
             "date, not the application date — the question is 'how many of "
             "my applications led to a meeting?', and the two dates are "
             "different facts")
    args = ap.parse_args()

    start = parse_date(args.start) if args.start else today.replace(day=1)
    end = parse_date(args.end) if args.end else today
    if start > end:
        raise SystemExit(f"error: --from {start} is after --to {end}")

    wanted = None
    if args.status.strip().lower() != "all":
        wanted = {s.strip().lower() for s in args.status.split(",") if s.strip()}

    rows = load_rows(args.file)

    if args.interviews:
        return report_interviews(rows, start, end, args)

    kept = []
    for row in rows:
        if not row["date"]:
            continue
        if wanted is not None and row["kind"] not in wanted:
            continue
        d = dt.date.fromisoformat(row["date"])
        if start <= d <= end:
            kept.append(row)
    kept.sort(key=lambda r: (r["date"], r["societe"]))

    # Everything the caller must be told about, so a clean-looking number is
    # never mistaken for a complete one. See shared/never-fail-silently.md.
    dated = [r for r in rows if r["date"]]
    meta = {
        "from": start.isoformat(),
        "to": end.isoformat(),
        "status": args.status,
        "count": len(kept),
        "total_rows": len(rows),
        "dated_rows": len(dated),
        # A status that carries no date and is not one of the dateless kinds:
        # something the ledger says that this script does not understand.
        "unparsed_status": sorted(
            {r["statut"] for r in rows
             if not r["date"] and r["kind"] not in ("todo", "discarded", "")}
        ),
        # Counted, but the ad cannot be linked to (id "—", or an unknown board).
        "no_url": sum(1 for r in kept if not r["url"]),
        # Applications not yet declared to an unemployment office, over the
        # whole ledger — not just this period, because that is the real gap.
        "jr_missing": sum(1 for r in rows if r.get("jr_missing")),
        # Legacy French vocabulary still present: worth migrating.
        "legacy_french": sum(
            1 for r in rows
            if r["kind"] in ("postulé", "refusé", "refus employeur", "à traiter", "écarté")
        ),
    }

    if args.format == "json":
        print(json.dumps({"meta": meta, "applications": kept}, ensure_ascii=False, indent=2))
        return 0

    if args.format == "md":
        print(f"## Applications from {start} to {end} — {len(kept)}")
        print()
        if kept:
            print("| Date | Role | Company | Status | Link |")
            print("| :-- | :-- | :-- | :-- | :-- |")
            for r in kept:
                print(f"| {r['date']} | {r['poste']} | {r['societe']} | {r['statut']} | {r['url']} |")
        else:
            print("_No application in this period._")
        return 0

    print(f"Period: {start} -> {end}   status: {args.status}   ({len(kept)}/{len(rows)} rows)")
    if not kept:
        print("No application in this period.")
        _warn(meta)
        return 0
    width_c = max(len(r["societe"]) for r in kept)
    width_p = max(len(r["poste"]) for r in kept)
    for r in kept:
        print(f"  {r['date']}  {r['societe']:<{width_c}}  {r['poste']:<{width_p}}  {r['statut']}")
        if r["url"]:
            print(f"              {r['url']}")
        else:
            print("              (no ad URL: the id cannot be resolved to a board)")
    _warn(meta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
