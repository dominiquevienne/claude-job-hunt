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

import _ledger_table

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






# `IV:2026-09-02 phone`, `IV:2026-09-11 on-site` — repeatable, the qualifier
# optional and short. The date is the meeting's, never the application's.
IV_RE = re.compile(r"\bIV:(\d{4}-\d{2}-\d{2})(?:\s+([A-Za-z][\w -]{0,18}))?")



# --- #1307 tranche 2: the state a mailbox scanner found -----------------------
# The event vocabulary is the contract's (`shared/integrations/events-sheet.md`)
# and the five state words are the ones issue #1307 fixes. `autre` is the
# producer's own «other», DECLARED by the contract — it is not our default.
EVENT_STATES = {
    "accuse_reception": "acknowledged",
    "refus": "refused",
    "entretien": "interview",
    "demande_action": "action required",
    "autre": "other",
}

# What the LEDGER says, in the SAME words — otherwise the two cannot be
# compared at all, and a column that mixes them carries no provenance.
LEDGER_STATES = {
    "applied": "sent", "postulé": "sent",
    "rejected": "refused", "refusé": "refused",
}

# Which pairs cannot both describe the current state. **This is a declared
# JUDGEMENT, not a measurement**: an acknowledgement, an interview or a
# request for action on a row the ledger calls `sent` is PROGRESS on an
# application that did leave, so it contradicts nothing. What cannot both be
# true is a refusal on a row still `sent` (the ledger is behind), and any
# later move on a row the ledger already calls `refused` (the refusal is not
# the last word). Everything outside this set is reported as a state and
# never as a disagreement.
INCOMPATIBLE = frozenset({
    ("sent", "refused"),
    ("refused", "acknowledged"),
    ("refused", "interview"),
    ("refused", "action required"),
})


def _events_module():
    """`skills/job-sync/scripts/events_sheet.py`, by PATH and never re-derived.

    The reader is imported rather than reimplemented because the rule that
    matters is the one a second reader loses: an unreadable or
    header-mismatched CSV is REFUSED with its own exit code, never read as
    «no events». The path is resolved against THIS file and not the working
    directory, so the flag behaves the same wherever it is called from.
    """
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.normpath(os.path.join(
        here, os.pardir, os.pardir, "job-sync", "scripts", "events_sheet.py"))
    if not os.path.exists(p):
        raise SystemExit(
            f"error: --events needs {p}, which is not there. The reader is "
            f"shipped with the job-sync skill (issue #1307 tranche 1); "
            f"refusing rather than reading the sheet with a second reader")
    spec = importlib.util.spec_from_file_location("events_sheet_1307", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def attach_events(rows, path):
    """Hang each application's latest event onto its ledger row.

    Returns everything the caller must be TOLD, because a state column is a
    place where an omission is invisible: a row with no event and a row whose
    event we failed to attach render identically unless the counts are shown.
    """
    mod = _events_module()
    try:
        got = mod.events(path)
    except mod.SheetRefused as e:
        # The reader's codes are the point: «not there» (4) and «not this tab»
        # (5) are different repairs, and NEITHER of them is «this sheet holds
        # no event». The code travels out instead of degrading to an empty
        # list — which is exactly what a state column would hide.
        print(f"error: --events {path}: {e}", file=sys.stderr)
        raise SystemExit(e.code)

    latest = got["dernier_par_candidature"]
    attached = 0
    to_confirm = 0
    divergences = []
    for row in rows:
        # The ledger's own statement first, so a row with no event still
        # carries a state — and carries WHERE it comes from.
        row["etat"] = LEDGER_STATES.get(row["kind"])
        row["etat_source"] = "ledger" if row["etat"] else None
        row["a_confirmer"] = False
        row["divergence"] = None
        ev = latest.get(row.get("id"))
        if ev is None:
            continue
        attached += 1
        kind = ev.get("type")
        if kind is None:
            etat = "? event carries no type"
        elif kind in EVENT_STATES:
            etat = EVENT_STATES[kind]
        else:
            # When a sort has a default, take the one that fails VISIBLY:
            # folding an unknown kind onto `sent` would make a producer's new
            # event look like a row nothing has happened to.
            etat = f"? unknown event type: {kind}"
        ledger_etat = row["etat"]
        row["etat"] = etat
        row["etat_source"] = "evenement"
        row["evenement"] = ev
        if ev.get("a_confirmer"):
            to_confirm += 1
            row["a_confirmer"] = True
        if (ledger_etat, etat) in INCOMPATIBLE:
            row["divergence"] = (
                f"the ledger says {ledger_etat}, the event says {etat}")
            divergences.append({
                "id": row.get("id"), "ledger": ledger_etat, "evenement": etat,
                "date_evenement": ev.get("date_evenement"),
                "thread_url": ev.get("thread_url"),
                "confiance": ev.get("confiance"),
            })

    # Ids the sheet carries that NO ledger row matches. Their MEMBERS are
    # printed and never only their count: a count does not say which ones
    # are missing, and these are applications someone believes we sent.
    connus = {r.get("id") for r in rows}
    orphelins = sorted(i for i in latest if i not in connus)
    return {
        "file": path,
        "lus": got["lus"],
        "doublons_message_id": got["doublons_message_id"],
        "attaches": attached,
        "a_confirmer": to_confirm,
        "divergences": divergences,
        "orphelins": orphelins,
        "sans_candidature": got["sans_candidature"],
        "sans_date_lisible": got["sans_date_lisible"],
        "valeurs_inconnues": got["valeurs_inconnues"],
    }


def _warn_events(ev: dict) -> None:
    """What the sheet said that the column cannot show."""
    print()
    print(f"  events: {ev['lus']} row(s) read from {ev['file']}, "
          f"{ev['attaches']} attached to an application")
    if ev["doublons_message_id"]:
        print(f"  ! {ev['doublons_message_id']} replayed message_id(s) counted once")
    if ev["a_confirmer"]:
        print(f"  ! {ev['a_confirmer']} event(s) below `haute` confidence — marked")
        print("    [to confirm]: they propose, they do not establish")
    for d in ev["divergences"]:
        print(f"  ! DIVERGENCE {d['id']}: {d['ledger']} in the ledger, "
              f"{d['evenement']} in the sheet ({d['date_evenement']})")
        print("    nothing is applied to the ledger here — /job-sync proposes the edit")
    for o in ev["orphelins"]:
        print(f"  ! the sheet carries an event for {o}, which this ledger "
              f"does not know")
    if ev["sans_candidature"]:
        print(f"  ! {len(ev['sans_candidature'])} event(s) name no single "
              f"application — SUGGESTIONS to confirm, never matches:")
        for s in ev["sans_candidature"][:5]:
            print(f"      {s.get('date_evenement')} {s.get('type')} -> "
                  f"{' | '.join(s.get('candidats_possibles') or []) or '(none)'}")
    if ev["sans_date_lisible"]:
        print(f"  ! {len(ev['sans_date_lisible'])} event(s) carry no readable "
              f"date, so they are not ordered against the others")
    for u in ev["valeurs_inconnues"]:
        print(f"  ! value the contract does not declare: {u}")


def load_rows(path: str) -> tuple[list[dict], dict[str, int]]:
    """`(rows, skipped)` — see `_ledger_table`, issue #1182.

    The reading itself lives in `_ledger_table`: bounded to `## Ads` with the
    same boundary `ledger.py` uses, and counting the rows whose width does not
    match instead of dropping them in silence. What stays here is the part
    that is this script's own — the derived fields it adds to each row.
    """
    rows, skipped = _ledger_table.load(path, HEADER_ALIASES)
    out = []
    for row in rows:
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
        out.append(row)
    return out, skipped



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
    for line in _ledger_table.skipped_lines(meta.get("skipped") or {}):
        print(line)
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
    if meta.get("events") is not None:
        _warn_events(meta["events"])


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
    ap.add_argument(
        "--events", metavar="CSV",
        help="the `evenements` tab exported as CSV. Adds a state column "
             "(sent / acknowledged / interview / refused / action required) "
             "and flags any event below `haute` confidence. An unreadable or "
             "header-mismatched file is REFUSED with its own exit code, never "
             "read as «no events»")
    args = ap.parse_args()

    start = parse_date(args.start) if args.start else today.replace(day=1)
    end = parse_date(args.end) if args.end else today
    if start > end:
        raise SystemExit(f"error: --from {start} is after --to {end}")

    wanted = None
    if args.status.strip().lower() != "all":
        wanted = {s.strip().lower() for s in args.status.split(",") if s.strip()}

    rows, skipped = load_rows(args.file)

    events_meta = None
    if args.events:
        if args.interviews:
            # Silently ignoring a flag is the invisible failure; the interview
            # report filters on the MEETING date and has no state column.
            raise SystemExit(
                "error: --events does not apply to --interviews (that report "
                "filters on the meeting date). Run them separately")
        events_meta = attach_events(rows, args.events)

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
        # Rows of `## Ads` whose width does not match the header, by
        # DIRECTION: a short row is a cell missing, a long one is an
        # unescaped `|` shifting every column after it. Neither is read.
        # They used to vanish before `meta` existed for them. Issue #1182.
        "skipped": skipped,
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

    if events_meta is not None:
        meta["events"] = events_meta

    if args.format == "json":
        print(json.dumps({"meta": meta, "applications": kept}, ensure_ascii=False, indent=2))
        return 0

    if args.format == "md":
        print(f"## Applications from {start} to {end} — {len(kept)}")
        print()
        if kept and events_meta is not None:
            print("| Date | Role | Company | Status | State | Link |")
            print("| :-- | :-- | :-- | :-- | :-- | :-- |")
            for r in kept:
                etat = r.get("etat") or "?"
                if r.get("etat_source") == "evenement":
                    etat += " (event)"
                if r.get("a_confirmer"):
                    etat += " [to confirm]"
                if r.get("divergence"):
                    etat += " **DIVERGENCE**"
                print(f"| {r['date']} | {r['poste']} | {r['societe']} "
                      f"| {r['statut']} | {etat} | {r['url']} |")
        elif kept:
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
        if events_meta is not None:
            etat = r.get("etat") or "?"
            marks = []
            if r.get("etat_source") == "evenement":
                marks.append("from the sheet")
            if r.get("a_confirmer"):
                marks.append("to confirm")
            if r.get("divergence"):
                marks.append(r["divergence"])
            suffix = ("   (" + "; ".join(marks) + ")") if marks else ""
            print(f"              state: {etat}{suffix}")
        if r["url"]:
            print(f"              {r['url']}")
        else:
            print("              (no ad URL: the id cannot be resolved to a board)")
    _warn(meta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
