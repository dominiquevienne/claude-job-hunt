#!/usr/bin/env python3
"""events_sheet — the CSV half of the two-tab events sheet. #1307, tranche 1.

**THIS SHIPS THE TABS WE *READ* AND *REBUILD*, AND NOT THE ONE WE DERIVE FROM
THE LEDGER.** `export` is deliberately absent: its premise is the ledger's own
shape plus the two optional bullets of `employers.md`, and neither was measured
when this was written. *A chain left open on a DECLARED dependency is a debt,
not an error — what would be false is reading «tranche 1 shipped» as «the sheet
round-trips».* Nothing imports this module yet, and no skill calls it: there is
no egress here, so the README's Privacy section stays true until the shipping
tranche rewrites it in its own PR.

**WHY CSV AT ALL, measured twice by two sessions on 2026-11-12 and recorded in
the issue's thread.** No Google Sheets connector exists in a Claude Code session
here: a tool search returned eight tools — Drive `update_file`, `create_file`,
`read_file_content`, `share_file`, `search_files`, two Calendar, one Gmail — and
**none writes a cell**. The instrument answered, so that zero is readable and
not a search failure.

> **Writing `candidatures` cannot be automated at all today.** A CSV import
> *replaces* a tab, so rebuilding the FULL union with the tab's current content
> is not an optimisation: it is the only shape that cannot delete a row.

**AND THE EXPORT IS ASYMMETRIC IN THE WORST DIRECTION.**
`download_file_content` with `text/csv` works and returns **one** tab — the one
we WRITE — and its schema carries no tab selector, so that is not a parameter
anybody failed to pass. The tab we READ is the one it cannot reach. *Whether
the export follows tab ORDER or the ACTIVE tab is still open, needs a human,
and belongs to the owner; it decides a recommendation about tab order and it
does not decide anything here.*

**THE EXPORTED CSV HAS NO TRAILING NEWLINE** — 111 bytes, `wc -l` returns 0. A
`while read` loop drops the last line of such a file in silence, and here that
line is a real event. `csv.reader` is used for that reason, and the bench
carries a fixture with no final newline so the choice is exercised rather than
asserted.

**AN UNREADABLE OR HEADER-MISMATCHED CSV IS REFUSED BY AN EXIT CODE, NEVER READ
AS «no events».** The two failures are distinct codes, because «the file is not
there» and «the file is not this tab» send a reader to different places. *And a
code is taken WITHOUT A PIPE: the exit of a pipeline is the exit of the pipe.*

**«Pas de donnée» IS NOT THE ONLY SENTINEL A SHEET WRITES, so the floor is
POSITIVE**: a cell is a value when it passes a test, never because it is missing
from a list of refusals. A list of refusals bets that the problem has been
enumerated, and the next sentinel arrives spelled differently.

**AND AN UNKNOWN `type` OR `confiance` IS NAMED AND NEVER COERCED.** When a sort
has a default case, the default is the one that fails VISIBLY: mapping an
unknown type onto `autre` would make a producer's new event kind look like a
deliberate «other», and nothing in the output would say otherwise.

    events_sheet.py events --csv evenements.csv
    events_sheet.py merge  --current candidatures.csv --new rows.csv

*The contract itself lives in `shared/integrations/events-sheet.md`; each tab
has one owner, and this module never writes the tab it reads.*
"""

import argparse
import csv
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

EXIT_BROKEN = 2
EXIT_UNREADABLE = 4      # the file is not there, or not readable text
EXIT_HEADER = 5          # the file is readable and is NOT this tab

#  The two contracts, in the order the sheet carries them. They are LITERALS
#  here so that a header check compares against the agreement and never against
#  whatever the file happens to hold.
CANDIDATURES = ("id", "entreprise", "alias_entreprise", "domaines_expediteurs",
                "poste", "canal", "statut_ledger", "date_envoi", "date_statut",
                "statut_pre")
EVENEMENTS = ("date_evenement", "message_id", "candidature_id",
              "candidats_possibles", "entreprise", "poste", "type",
              "motif_refus", "action_requise", "echeance", "thread_url",
              "archive", "confiance", "traite_le")

TYPES = ("accuse_reception", "refus", "entretien", "demande_action", "autre")
CONFIANCES = ("haute", "moyenne", "basse")

#  A POSITIVE floor. The first alternative is the one measured on a real sheet
#  export; the others are DECLARED inert on that corpus and exist because the
#  next sentinel arrives spelled differently, not because they protected
#  anything we saw.
SENTINEL = re.compile(
    r"^\s*(?:pas\s+de\s+donn[ée]es?|n/?a|aucune?|-{1,3}|null|none|undefined"
    r"|\$undefined)\s*$", re.I)

#  An ISO date, optionally followed by a time. A cell that does not match is not
#  ordered against the others: it is reported under its own name.
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:[ T].*)?$")


class SheetRefused(Exception):
    """The file is not the tab this reader was given."""

    def __init__(self, message, code=EXIT_HEADER):
        super().__init__(message)
        self.code = code


def die(msg, code=EXIT_BROKEN):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[events_sheet] {msg}", file=sys.stderr)


def declared(value):
    """`(value, state)` — a POSITIVE floor, run on the RAW cell.

    Three states and not two: `if x` conflates «absent», «present but empty»
    and «the sheet wrote a sentinel there», and the one that costs is the third
    — a column holding «Pas de donnée» has deposited nothing, and reading it as
    a value is how a record comes to claim something nobody wrote.
    """
    if value is None:
        return None, "absent"
    if isinstance(value, str):
        if not value.strip():
            return None, "present but empty"
        if SENTINEL.match(value):
            return None, "sentinel"
        return value.strip(), "declared"
    return value, "declared"


def read_tab(path, header):
    """Rows of one tab, in SHEET ORDER, or a refusal with its own exit code.

    The header is compared to the contract and the complaint NAMES what it got:
    «not this tab» and «this tab with a column renamed» are different repairs.
    """
    try:
        with io.open(path, encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.reader(fh))
    except OSError as e:
        raise SheetRefused(f"{path}: {type(e).__name__}: {e}", EXIT_UNREADABLE)
    except UnicodeDecodeError as e:
        raise SheetRefused(f"{path}: not readable as UTF-8 text: {e}",
                           EXIT_UNREADABLE)
    if not rows:
        raise SheetRefused(
            f"{path}: zero lines. An empty FILE is not an empty TAB — a tab "
            f"carries its header row even with no data, so this is a refusal "
            f"and never «no rows»")
    got = tuple(c.strip() for c in rows[0])
    if got != tuple(header):
        missing = [c for c in header if c not in got]
        extra = [c for c in got if c not in header]
        detail = []
        if missing:
            detail.append("missing " + ", ".join(missing))
        if extra:
            detail.append("unexpected " + ", ".join(extra))
        if not detail:
            detail.append("same columns in a different ORDER")
        raise SheetRefused(
            f"{path}: header is not the contract — {'; '.join(detail)}. "
            f"Refused rather than read as «no rows»")
    out = []
    for n, raw in enumerate(rows[1:], start=2):
        if len(raw) != len(header):
            raise SheetRefused(
                f"{path}: line {n} carries {len(raw)} cell(s) for "
                f"{len(header)} column(s). A short row would silently shift "
                f"every field after it")
        out.append({k: raw[i] for i, k in enumerate(header)})
    return out


def date_of(row):
    """The ISO date prefix of `date_evenement`, or `None` — never a guess."""
    value, _state = declared(row.get("date_evenement"))
    if value is None:
        return None
    m = DATE_RE.match(value)
    return m.group(1) if m else None


def events(path):
    """Latest event per application, plus everything that has no single one.

    Three things are measured rather than assumed. **Deduplication is by
    `message_id`** — a replayed scan is idempotent on the producer's side and
    must be on ours. **«Latest» is by `date_evenement`, and ties keep the order
    in the sheet**, which is why the rows are never sorted: a stable scan of the
    sheet order cannot reorder a tie. **And a row whose date does not parse is
    not ordered against the others**: it leaves under its own name, because
    comparing it would put an unknown instant somewhere precise.
    """
    rows = read_tab(path, EVENEMENTS)
    seen, twice = set(), 0
    latest, sans_date, sans_candidature, inconnus = {}, [], [], []
    for row in rows:
        mid, _s = declared(row.get("message_id"))
        if mid is not None:
            if mid in seen:
                twice += 1
                continue
            seen.add(mid)
        kind, _s = declared(row.get("type"))
        if kind is not None and kind not in TYPES:
            inconnus.append({"type": kind, "message_id": mid})
        conf, _s = declared(row.get("confiance"))
        if conf is not None and conf not in CONFIANCES:
            inconnus.append({"confiance": conf, "message_id": mid})
        when = date_of(row)
        cid, _s = declared(row.get("candidature_id"))
        record = {
            "date_evenement": when,
            "message_id": mid,
            "candidature_id": cid,
            "type": kind,
            "confiance": conf,
            "a_confirmer": conf != "haute",
            "thread_url": declared(row.get("thread_url"))[0],
            "motif_refus": declared(row.get("motif_refus"))[0],
            "motif_refus_non_fiable": declared(row.get("motif_refus"))[0] is not None,
            "action_requise": declared(row.get("action_requise"))[0],
            "echeance": declared(row.get("echeance"))[0],
        }
        if when is None:
            sans_date.append(record)
            continue
        if cid is None:
            possibles, _s = declared(row.get("candidats_possibles"))
            record["candidats_possibles"] = (
                [p.strip() for p in possibles.split("|") if p.strip()]
                if possibles else [])
            sans_candidature.append(record)
            continue
        held = latest.get(cid)
        #  STRICTLY greater: on a tie the row already held wins, which is the
        #  sheet's own order, and the scan never sorts.
        if held is None or when > held["date_evenement"]:
            latest[cid] = record
    return {
        "dernier_par_candidature": latest,
        "sans_candidature": sans_candidature,
        "sans_date_lisible": sans_date,
        "valeurs_inconnues": inconnus,
        "lus": len(rows),
        "doublons_message_id": twice,
    }


def merge(current, new):
    """The union of the tab's current content with our rows — by `id`.

    A CSV import REPLACES the tab, so this is the only shape that cannot delete
    a row: anything the sheet holds and we do not know about is carried through
    untouched. **And `date_envoi` is never rewritten**: the owner's decision 1
    says a send date must survive `applied → rejected`, which is exactly the
    update that would overwrite it.
    """
    held = read_tab(current, CANDIDATURES)
    mine = read_tab(new, CANDIDATURES)
    order, rows = [], {}
    for row in held:
        rid, _s = declared(row.get("id"))
        if rid is None:
            raise SheetRefused(
                f"{current}: a row carries no `id`. The union keys on it, so a "
                f"row without one would be dropped or duplicated in silence")
        if rid not in rows:
            order.append(rid)
        rows[rid] = dict(row)
    kept_dates, added, updated = 0, 0, 0
    for row in mine:
        rid, _s = declared(row.get("id"))
        if rid is None:
            raise SheetRefused(f"{new}: a row carries no `id`")
        if rid not in rows:
            order.append(rid)
            rows[rid] = dict(row)
            added += 1
            continue
        before = rows[rid]
        merged = dict(row)
        envoi, _s = declared(before.get("date_envoi"))
        if envoi is not None:
            merged["date_envoi"] = before["date_envoi"]
            if declared(row.get("date_envoi"))[0] != envoi:
                kept_dates += 1
        rows[rid] = merged
        updated += 1
    return ([rows[r] for r in order],
            {"tenues": len(held), "miennes": len(mine), "ajoutees": added,
             "mises_a_jour": updated, "dates_envoi_conservees": kept_dates,
             "supprimees": 0})


# ---------------------------------------------------------------- commands

def cmd_events(a):
    state = events(a.csv)
    json.dump(state, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    note(f"{state['lus']} row(s) read, {state['doublons_message_id']} dropped "
         f"as a replayed `message_id`")
    note(f"{len(state['dernier_par_candidature'])} application(s) carry an "
         f"event, {len(state['sans_candidature'])} event(s) name no single "
         f"application, {len(state['sans_date_lisible'])} carry no readable "
         f"date")
    bas = sum(1 for r in state["dernier_par_candidature"].values()
              if r["a_confirmer"])
    note(f"{bas} of them below `haute`: they are SUGGESTIONS and nothing is "
         f"applied without a yes")
    if state["valeurs_inconnues"]:
        note(f"{len(state['valeurs_inconnues'])} cell(s) carry a value this "
             f"contract does not list — NAMED and never coerced onto `autre`")


def cmd_merge(a):
    rows, counts = merge(a.current, a.new)
    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(CANDIDATURES)
    for row in rows:
        w.writerow([row.get(c, "") for c in CANDIDATURES])
    note(f"{counts['tenues']} held + {counts['miennes']} mine -> {len(rows)} "
         f"row(s): {counts['ajoutees']} added, {counts['mises_a_jour']} "
         f"updated, {counts['supprimees']} deleted")
    if counts["dates_envoi_conservees"]:
        note(f"{counts['dates_envoi_conservees']} `date_envoi` kept as the "
             f"sheet already had it — a send date is written once")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    s = p.add_subparsers(dest="cmd", required=True)

    pe = s.add_parser("events", help="latest event per application")
    pe.add_argument("--csv", required=True)
    pe.set_defaults(fn=cmd_events)

    pm = s.add_parser("merge", help="union with the tab's current content")
    pm.add_argument("--current", required=True)
    pm.add_argument("--new", required=True)
    pm.set_defaults(fn=cmd_merge)

    a = p.parse_args()
    try:
        a.fn(a)
    except SheetRefused as e:
        die(str(e), e.code)


if __name__ == "__main__":
    main()
