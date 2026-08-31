#!/usr/bin/env python3
"""Work out what job-room still needs, and refuse to write a duplicate into it.

Two jobs, deliberately in one script because they share the ledger parsing and
because doing only the first one is unsafe:

  plan   what to declare, and what to correct — the delta, not the whole board
  check  does this candidate row already exist in job-room? — the hard gate

A PRE (preuve de recherche d'emploi) is an official declaration to an
unemployment office. Two entries for one application is an inaccurate
declaration; a missing one is a search that does not count. Both errors are
invisible in a row count, so neither is left to judgement here.

The script never talks to job-room: that space is authenticated and lives in
the user's own browser. `check` is fed the page text the caller already has.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import unicodedata

JOB_HUNT_HOME = os.environ.get(
    "JOB_HUNT_HOME", os.path.expanduser("~/Documents/job_applications")
)
DEFAULT_PIPELINE = os.path.join(JOB_HUNT_HOME, "job-pipeline.md")
DEFAULT_STATE = os.path.join(JOB_HUNT_HOME, ".jobroom-sync.json")

# Statuses that mean an application actually left. `no-go` never did, and
# `todo`/`discarded` carry no date — none of them belong in a declaration.
SENT_KINDS = {"applied", "rejected", "postulé", "postule", "refusé", "refuse"}

STATUS_RE = re.compile(
    r"^(?P<kind>[\w'’-]+(?:\s+[\w'’-]+)*?)(?:\s+le)?\s+(?P<date>\d{4}-\d{2}-\d{2})\s*$"
)
JR_DECLARED_RE = re.compile(r"JR:(\d{4}-\d{2}-\d{2})")
JR_MISSING_RE = re.compile(r"JR:missing")

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


# --------------------------------------------------------------------------
# ledger
# --------------------------------------------------------------------------

def split_row(line: str) -> list[str]:
    """Split a markdown table row, honouring \\| escapes inside cells."""
    out, cell, i = [], [], 0
    body = line.strip().strip("|")
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body) and body[i + 1] == "|":
            cell.append("|")
            i += 2
            continue
        if ch == "|":
            out.append("".join(cell).strip())
            cell = []
            i += 1
            continue
        cell.append(ch)
        i += 1
    out.append("".join(cell).strip())
    return out


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
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if cells and cells[0].strip().lower() == "id":
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
        note = row.get("note", "")
        row["jr_missing"] = bool(JR_MISSING_RE.search(note))
        jr = JR_DECLARED_RE.search(note)
        row["jr_declared"] = jr.group(1) if jr else None
        rows.append(row)
    if columns is None:
        raise SystemExit(f"error: no table header found in {path}")
    return rows


def sent(row: dict) -> bool:
    return bool(row["date"]) and row["kind"] in SENT_KINDS


# --------------------------------------------------------------------------
# matching key
# --------------------------------------------------------------------------

def norm(text: str) -> str:
    """Fold a label to something comparable across two systems.

    Deliberately conservative: case, accents, punctuation and runs of
    whitespace go; words do not. Anything cleverer (stemming, dropping
    'senior', collapsing 'PHP/Symfony') risks fusing two genuinely different
    roles at the same employer, which is how a real application disappears.
    """
    if not text:
        return ""
    text = re.sub(r"\*\*|__|`|\[\[|\]\]", " ", text)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def key(company: str, role: str) -> tuple[str, str]:
    return (norm(company), norm(role))


# --------------------------------------------------------------------------
# state
# --------------------------------------------------------------------------

def read_state(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_state(path: str, data: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)


# --------------------------------------------------------------------------
# plan
# --------------------------------------------------------------------------

def build_plan(rows: list[dict], state: dict) -> dict:
    """Split the ledger into what job-room is missing and what it has wrong.

    `to_enter`  — sent, and never declared.
    `to_update` — declared, but the employer answered *after* the declaration,
                  so job-room still shows the old result.

    The second one is the case a `jr_missing` count can never surface: the row
    IS declared, so it does not miss anything; what is stale is the outcome
    recorded next to it. It needs no new field — the ledger already dates both
    the status (`rejected 2026-08-20`) and the declaration (`JR:2026-08-18`),
    and the comparison between the two is the whole test.
    """
    to_enter, to_update = [], []
    for r in rows:
        if not sent(r):
            continue
        item = {
            "id": r.get("id", ""),
            "company": r.get("societe", ""),
            "role": r.get("poste", ""),
            "status": r["kind"],
            "status_date": r["date"],
            "declared": r["jr_declared"],
        }
        if r["jr_missing"] or not r["jr_declared"]:
            to_enter.append(item)
        elif r["kind"] in ("rejected", "refusé", "refuse") and r["date"] > r["jr_declared"]:
            item["expected_result"] = "Réponse négative"
            to_update.append(item)
    return {
        "last_sync": state.get("last_sync"),
        "to_enter": to_enter,
        "to_update": to_update,
        "counts": {"to_enter": len(to_enter), "to_update": len(to_update)},
    }


# --------------------------------------------------------------------------
# check — the hard gate
# --------------------------------------------------------------------------

def parse_jobroom_text(text: str) -> list[dict]:
    """Pull (company, role) pairs out of the job-room period listing.

    The listing renders each entry as three consecutive lines:

        Postulation du 26.08.2026
        Darwin Partners SA
        Service Delivery Manager / Coordinateur Applicatif IT

    That shape is what `get_page_text` returns. `read_page` must NOT be used as
    the source: the list is virtualised and exposes only the visible rows (5 of
    48 measured), so a check built on it would see almost nothing and report
    "no duplicate" for entries that are plainly there.
    """
    lines = [l.strip() for l in text.splitlines()]
    entries = []
    marker = re.compile(r"^Postulation du (\d{2})\.(\d{2})\.(\d{4})$", re.IGNORECASE)
    for i, line in enumerate(lines):
        m = marker.match(line)
        if not m:
            continue
        rest = [l for l in lines[i + 1: i + 6] if l]
        if len(rest) < 2:
            continue
        d, mo, y = m.groups()
        entries.append({
            "date": f"{y}-{mo}-{d}",
            "company": rest[0],
            "role": rest[1],
        })
    return entries


def run_check(plan: dict, text: str) -> dict:
    existing = parse_jobroom_text(text)
    if not existing:
        return {
            "usable": False,
            "reason": (
                "no entry could be read from the job-room text. Either the period is "
                "genuinely empty or the text is not the listing. Either way NOTHING is "
                "written: an unverified write is the one outcome this check exists to "
                "prevent."
            ),
            "existing_count": 0,
        }

    index: dict[tuple[str, str], dict] = {}
    for e in existing:
        index.setdefault(key(e["company"], e["role"]), e)

    safe, blocked = [], []
    for item in plan["to_enter"]:
        k = key(item["company"], item["role"])
        hit = index.get(k)
        if hit:
            blocked.append({**item, "duplicate_of": hit})
        else:
            same_company = [
                e for e in existing if norm(e["company"]) == k[0]
            ]
            entry = dict(item)
            if same_company:
                # Not a duplicate — but the employer is already there under
                # another role. Surfaced so a human can confirm the distinction
                # rather than discover it afterwards.
                entry["same_company_other_roles"] = [e["role"] for e in same_company]
            safe.append(entry)

    return {
        "usable": True,
        "existing_count": len(existing),
        "safe_to_enter": safe,
        "blocked_as_duplicate": blocked,
        "counts": {"safe": len(safe), "blocked": len(blocked)},
    }


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def print_plan(plan: dict) -> None:
    ls = plan["last_sync"] or "never"
    print(f"last job-room sync: {ls}")
    print()
    print(f"to declare ({len(plan['to_enter'])}):")
    for i in plan["to_enter"] or []:
        print(f"  · {i['status_date']}  {i['company'][:44]:44}  {i['role'][:46]}")
    if not plan["to_enter"]:
        print("  (none)")
    print()
    print(f"result changed since declaration ({len(plan['to_update'])}):")
    for i in plan["to_update"] or []:
        print(f"  · declared {i['declared']} → {i['status']} {i['status_date']}")
        print(f"      {i['company'][:44]:44}  {i['role'][:46]}")
        print(f"      job-room should read: {i['expected_result']}")
    if not plan["to_update"]:
        print("  (none)")


def print_check(res: dict) -> None:
    if not res["usable"]:
        print("REFUSED — nothing may be written.")
        print(f"  {res['reason']}")
        return
    print(f"job-room entries read: {res['existing_count']}")
    print()
    print(f"safe to enter ({len(res['safe_to_enter'])}):")
    for i in res["safe_to_enter"]:
        print(f"  · {i['company'][:44]:44}  {i['role'][:46]}")
        if i.get("same_company_other_roles"):
            print(f"      note: employer already present with "
                  f"{len(i['same_company_other_roles'])} other role(s) — distinct, not a duplicate")
            for r in i["same_company_other_roles"][:4]:
                print(f"        · {r[:66]}")
    if not res["safe_to_enter"]:
        print("  (none)")
    print()
    print(f"BLOCKED as duplicate ({len(res['blocked_as_duplicate'])}):")
    for i in res["blocked_as_duplicate"]:
        print(f"  · {i['company'][:44]:44}  {i['role'][:46]}")
        print(f"      already in job-room, declared for {i['duplicate_of']['date']}")
    if not res["blocked_as_duplicate"]:
        print("  (none)")


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=DEFAULT_PIPELINE,
                    help=f"pipeline file (default: {DEFAULT_PIPELINE})")
    ap.add_argument("--state", default=DEFAULT_STATE,
                    help=f"sync state file (default: {DEFAULT_STATE})")
    ap.add_argument("--format", choices=("table", "json"), default="table")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("plan", help="what to declare, and what to correct")

    c = sub.add_parser("check", help="refuse anything already in job-room")
    c.add_argument("--jobroom-text", required=True,
                   help="file holding the job-room period listing (get_page_text output; "
                        "use '-' for stdin)")

    m = sub.add_parser("mark-synced", help="record that job-room is now up to date")
    m.add_argument("--entries", type=int, default=None,
                   help="number of entries the period holds after the session")

    args = ap.parse_args()
    state = read_state(args.state)

    if args.cmd == "plan":
        plan = build_plan(load_rows(args.file), state)
        print(json.dumps(plan, indent=2, ensure_ascii=False)) if args.format == "json" else print_plan(plan)
        return 0

    if args.cmd == "check":
        plan = build_plan(load_rows(args.file), state)
        text = sys.stdin.read() if args.jobroom_text == "-" else \
            open(args.jobroom_text, encoding="utf-8").read()
        res = run_check(plan, text)
        print(json.dumps(res, indent=2, ensure_ascii=False)) if args.format == "json" else print_check(res)
        # Exit 2 when the listing could not be read: a caller that ignores the
        # output still cannot mistake this for "verified, nothing found".
        return 0 if res["usable"] else 2

    if args.cmd == "mark-synced":
        state["last_sync"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
        if args.entries is not None:
            state["entries_at_sync"] = args.entries
        write_state(args.state, state)
        print(f"recorded: {state['last_sync']}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
