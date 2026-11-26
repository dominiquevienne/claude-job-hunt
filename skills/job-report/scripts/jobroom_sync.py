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

import _events_reader
import _ledger_table

JOB_HUNT_HOME = os.environ.get(
    "JOB_HUNT_HOME", os.path.expanduser("~/Documents/job_applications")
)
DEFAULT_PIPELINE = os.path.join(JOB_HUNT_HOME, "job-pipeline.md")
DEFAULT_STATE = os.path.join(JOB_HUNT_HOME, ".jobroom-sync.json")

# The header contract and the `Status`/`Note` normalisation live in
# `_ledger_table` since #1322: they were byte-identical here and in
# `list_applications.py`, and `events_sheet.py export` would have made a third
# copy. **The names stay bound here** — a caller that reads
# `jobroom_sync.STATUS_RE` keeps working, and it now reads the ONE object.
SENT_KINDS = _ledger_table.SENT_KINDS
STATUS_RE = _ledger_table.STATUS_RE
JR_DECLARED_RE = _ledger_table.JR_DECLARED_RE
JR_MISSING_RE = _ledger_table.JR_MISSING_RE
JR_WAIVED_RE = _ledger_table.JR_WAIVED_RE
JR_RESULT_RE = _ledger_table.JR_RESULT_RE
HEADER_ALIASES = _ledger_table.HEADER_ALIASES


# --------------------------------------------------------------------------
# ledger
# --------------------------------------------------------------------------



def load_rows(path: str) -> tuple[list[dict], dict[str, int]]:
    """`(rows, skipped)` — see `_ledger_table`, issue #1182.

    The reading is shared with `list_applications.py`: bounded to `## Ads`
    with the boundary `ledger.py` uses, and counting the rows whose width does
    not match rather than dropping them in silence. This file had its own
    near-identical copy, and the two agreed with `ledger.py` by coincidence.
    """
    rows, skipped = _ledger_table.load(path, HEADER_ALIASES)
    return [_ledger_table.annotate(row) for row in rows], skipped



def sent(row: dict) -> bool:
    """Delegates to `_ledger_table.sent` — same reason as `load_rows`."""
    return _ledger_table.sent(row)


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

def build_plan(rows: list[dict], state: dict,
               skipped: dict[str, int] | None = None,
               periods=None, today: str | None = None) -> dict:
    """Split the ledger into what job-room is missing and what it has wrong.

    `to_enter`  — sent, and never declared.
    `to_update` — declared, but the employer answered *after* the declaration,
                  so job-room still shows the old result.

    The second one is the case a `jr_missing` count can never surface: the row
    IS declared, so it does not miss anything; what is stale is the outcome
    recorded next to it. It needs no new field — the ledger already dates both
    the status (`rejected 2026-08-20`) and the declaration (`JR:2026-08-18`),
    and the comparison between the two is the whole test.

    **Two refusals leave `to_update`, and neither is hidden** (issue #1332).
    On a real ledger the list held 56 rows and 0 of them were actionable:

    `result_recorded` — the note carries `JR:result <date>` on or after the
                  refusal: the answer is already entered in job-room. Without
                  this marker a corrected row satisfied «refused after
                  declared» forever, and the list only ever grew.
    `frozen`      — the row is declared in a period job-room has already
                  TRANSMITTED, read from `periods` exactly as `prefill` reads
                  it. A transmitted period cannot be edited by anyone, so the
                  row is SAID and not proposed.

    `periods` is `None` when no listing was supplied. That is NOT «no period is
    transmitted»: `plan["periodes"]["consulte"]` says the gate was not
    consulted, and every `to_update` row carries `periode_transmise: None`.
    """
    today = today or dt.date.today().isoformat()
    gate = periods_gate(periods, today)
    to_enter, to_update, waived = [], [], []
    result_recorded, frozen = [], []
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
            # **On a `rejected` row this date is the employer's ANSWER, not
            # the day the application went out.** `applied -> rejected` is a
            # legitimate transition in `shared/pipeline-format.md`, and it
            # overwrites the send date — which is the one the PRE form asks
            # for ("the day the send is confirmed"). An application sent on
            # 20 August and refused on 2 September would otherwise be declared
            # in the September period, while August transmits on a fixed date.
            #
            # The send date is not recoverable from the row, so this does not
            # invent one: it says the date cannot be used as a send date and
            # leaves the answer to the person who sent it.
            "date_is_answer": r["kind"] in ("rejected", "refusé", "refuse"),
        }
        if r["jr_waived"]:
            # Counted as an application, never proposed for entry again. It is
            # listed, not hidden: a decision that silently removes a row from
            # view is indistinguishable from a row that was lost.
            item["waived_on"] = r["jr_waived"] if r["jr_waived"] is not True else None
            waived.append(item)
        elif r["jr_missing"] or not r["jr_declared"]:
            to_enter.append(item)
        elif r["kind"] in ("rejected", "refusé", "refuse") and r["date"] > r["jr_declared"]:
            item["expected_result"] = "Réponse négative"
            res = r.get("jr_result")
            if res and res >= r["date"]:
                item["result_recorded_on"] = res
                result_recorded.append(item)
                continue
            if res:
                # Entered BEFORE the refusal it would have to describe: that
                # entry cannot be this answer, so the row stays to do — and
                # says why, rather than reading as a marker nobody wrote.
                item["result_recorded_on"] = res
            verdict, periode = period_of(gate, r["jr_declared"])
            item["periode_transmise"] = verdict
            item["periode"] = periode["label"] if periode else None
            (frozen if verdict else to_update).append(item)
    return {
        "last_sync": state.get("last_sync"),
        "to_enter": to_enter,
        "to_update": to_update,
        "waived": waived,
        "result_recorded": result_recorded,
        "frozen": frozen,
        "periodes": gate,
        "counts": {"to_enter": len(to_enter), "to_update": len(to_update),
                   "waived": len(waived),
                   "result_recorded": len(result_recorded),
                   "frozen": len(frozen)},
        # Rows of `## Ads` the reading refused, by direction. A PRE is an
        # official declaration: «Both errors are invisible in a row count, so
        # neither is left to judgement here» — and a row dropped in silence
        # was exactly that. Issue #1182.
        "skipped": skipped or {},
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


# The period listing carries three things the check needs and used not to
# read: which periods exist, how many entries job-room itself says each holds,
# and when each one leaves the user's hands. Issue #49 and issue #51.
#
# **Measured in French, on a real page, 2026-09-01.** job-room also serves DE,
# IT and EN, and the labels there have NOT been measured — so the parser is
# label-agnostic wherever it can be (a heading is a word plus a year; a count
# is a label followed by digits; a date is dd.mm.yyyy) and says `language:
# "unrecognised"` rather than guessing when the French words are absent.
MONTH_RE = re.compile(r"^([A-Za-zÀ-ÿ]{3,12})\s+(\d{4})$")
COUNT_RE = re.compile(r"^[^:]{1,40}:\s*(\d+)\s*$")
DATE_RE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
# French, measured. Anything else is reported as an unclassified date rather
# than assumed to be one kind or the other — the difference between "it leaves
# on its own" and "you must send it" is not a detail to guess at.
AUTO_RE = re.compile(r"automatique", re.I)
MANUAL_RE = re.compile(r"manuelle", re.I)
COUNT_LABEL_FR = "nombre saisi"


def parse_periods(text: str) -> list[dict]:
    """Every control period on the listing, with its count and its deadline.

    A period block starts at a `<Month> <Year>` heading and runs to the next
    one. Inside it:

        Nombre saisi: 48
        Transmission automatique le 06.09.2026 à 00 h 00

    `count` is what job-room says the period holds — **the number that tells a
    genuinely empty period from a listing this script failed to read**, which
    used to be the same condition (issue #49).

    `deadline` is the date after which a mistake stops being correctable
    (issue #51). It is on the page; it was simply never read.
    """
    lines = [l.strip() for l in text.splitlines()]
    starts = [i for i, l in enumerate(lines) if MONTH_RE.match(l)]
    out = []
    for n, i in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        block = lines[i:end]
        month, year = MONTH_RE.match(lines[i]).groups()
        count, count_seen, deadline, kind, lang = None, None, None, None, "fr"
        for l in block[1:]:
            m = COUNT_RE.match(l)
            if m and count is None:
                count = int(m.group(1))
                count_seen = l
                if COUNT_LABEL_FR not in l.lower():
                    lang = "unrecognised"
            d = DATE_RE.search(l)
            if d and deadline is None:
                y, mo, dd = d.group(3), d.group(2), d.group(1)
                deadline = f"{y}-{mo}-{dd}"
                kind = ("automatic" if AUTO_RE.search(l) else
                        "manual" if MANUAL_RE.search(l) else "unclassified")
                if kind == "unclassified":
                    lang = "unrecognised"
        # The line above a period sometimes qualifies it — "AVANT chômage" on
        # the measured page, which is the user's own period name — and
        # sometimes it is page chrome. **This script does not claim to know
        # which**, so it reports it as the line above and lets the reader
        # judge. Calling it a qualifier would be a small invented fact on a
        # page about official declarations.
        above = lines[i - 1] if i and lines[i - 1] and not MONTH_RE.match(lines[i - 1]) \
            and not COUNT_RE.match(lines[i - 1]) else None
        out.append({
            "label": f"{month} {year}",
            "line_above": above,
            "count": count,
            "count_line": count_seen,
            "deadline": deadline,
            "deadline_kind": kind,
            "language": lang,
        })
    return out


def run_check(plan: dict, text: str) -> dict:
    existing = parse_jobroom_text(text)
    periods = parse_periods(text)
    declared = sum(p["count"] for p in periods if p["count"] is not None)
    counted = [p for p in periods if p["count"] is not None]

    # **Three outcomes, not two.** "I could not read the page" and "the period
    # is legitimately empty" used to be the same condition — zero entries
    # parsed — so the first entry of every month was unreachable through the
    # documented path (issue #49). job-room states its own count on every
    # period, and reconciling the two numbers separates them.
    if not counted:
        return {
            "usable": False,
            "reason": (
                "no control period could be read from this text — no `<Month> "
                "<Year>` heading with a count under it. **This is a failure to "
                "read the page, not an empty period**: an empty period still "
                "prints its heading and `Nombre saisi: 0`. Capture the listing "
                "again with get_page_text (never read_page — the list is "
                "virtualised) and check it is the /work-efforts page."
            ),
            "existing_count": 0,
            "periods": periods,
        }
    if declared != len(existing):
        return {
            "usable": False,
            "reason": (
                f"job-room says these periods hold {declared} entr(y/ies) and "
                f"{len(existing)} could be read from the text. **A partial "
                f"capture is exactly what this refusal is for** — five rows of "
                f"forty-eight parse perfectly well and would clear duplicates "
                f"that are plainly there. NOTHING is written. Re-capture with "
                f"get_page_text and make the two numbers agree."
            ),
            "existing_count": len(existing),
            "declared_count": declared,
            "periods": periods,
        }
    if declared == 0:
        # Positive evidence of emptiness: a period was read and it says zero.
        return {
            "usable": True,
            "empty_period": True,
            "existing_count": 0,
            "declared_count": 0,
            "periods": periods,
            "safe_to_enter": list(plan["to_enter"]),
            "blocked_as_duplicate": [],
            "counts": {"safe": len(plan["to_enter"]), "blocked": 0},
            "note": (
                "the period is genuinely empty — job-room says so itself "
                "(count 0) and the listing was read. No duplicate is possible, "
                "so every planned entry is safe."
            ),
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
        "empty_period": False,
        "existing_count": len(existing),
        "declared_count": declared,
        "periods": periods,
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
    for line in _ledger_table.skipped_lines(plan.get("skipped") or {}):
        print(line)
    print()
    print(f"to declare ({len(plan['to_enter'])}):")
    for i in plan["to_enter"] or []:
        flag = "  <- NOT the send date" if i.get("date_is_answer") else ""
        print(f"  · {i['status_date']}  {i['company'][:44]:44}  {i['role'][:46]}{flag}")
    answered = [i for i in plan["to_enter"] or [] if i.get("date_is_answer")]
    if answered:
        print()
        print(f"  ** {len(answered)} of these carry the employer's ANSWER date, "
              f"not the day they were sent.** `applied -> rejected` overwrites")
        print("     the send date, and the PRE form asks for the send. Ask the")
        print("     user for it — do not declare these on the date shown, and do")
        print("     not guess: an application sent in August and refused in")
        print("     September would land in the wrong period.")
    if not plan["to_enter"]:
        print("  (none)")
    print()
    print(f"result changed since declaration ({len(plan['to_update'])}):")
    for i in plan["to_update"] or []:
        # `->`, not U+2192: a Windows pipe is cp1252 and has no arrow, so the
        # first refusal in this list ended `plan` in `UnicodeEncodeError`
        # (#1332, red on windows-latest only — the class of #232).
        print(f"  · declared {i['declared']} -> {i['status']} {i['status_date']}")
        print(f"      {i['company'][:44]:44}  {i['role'][:46]}")
        print(f"      job-room should read: {i['expected_result']}")
        if i.get("result_recorded_on"):
            print(f"      (`JR:result {i['result_recorded_on']}` predates this "
                  f"refusal — it cannot be this answer)")
    if not plan["to_update"]:
        print("  (none)")
    gate = plan.get("periodes") or {}
    if plan["to_update"] and not gate.get("consulte"):
        print("  ** transmitted-period gate NOT consulted — pass --jobroom-text "
              "<period listing>.")
        print("     A row declared in a transmitted period cannot be edited; "
              "without the")
        print("     listing this list cannot tell those apart, and does not "
              "pretend to. **")
    if plan.get("frozen"):
        print()
        print(f"refused in a TRANSMITTED period ({len(plan['frozen'])}) — "
              "cannot be edited, by anyone:")
        for i in plan["frozen"]:
            print(f"  · declared {i['declared']} ({i.get('periode')}) -> "
                  f"{i['status']} {i['status_date']}  {i['company'][:36]}")
    if plan.get("result_recorded"):
        print()
        print(f"result already entered in job-room ({len(plan['result_recorded'])})"
              " — `JR:result <date>`:")
        for i in plan["result_recorded"]:
            print(f"  · {i['status']} {i['status_date']}, entered "
                  f"{i['result_recorded_on']}  {i['company'][:36]}")
    if plan.get("waived"):
        print()
        print(f"deliberately not declared ({len(plan['waived'])}) — still counted "
              "as applications:")
        for i in plan["waived"]:
            on = f" (decided {i['waived_on']})" if i.get("waived_on") else ""
            print(f"  · {i['status_date']}  {i['company'][:40]:40} "
                  f"{i['role'][:38]}{on}")


def print_periods(periods: list[dict]) -> None:
    """The deadline is printed whenever a period is touched — issue #51.

    It is the one date that separates a mistake somebody can still fix from a
    false declaration, and it was on the page all along.
    """
    if not periods:
        return
    print("periods on this listing:")
    for p in periods:
        n = "?" if p["count"] is None else p["count"]
        print(f"  · {p['label']}: {n} entr(y/ies) saved")
        if p.get("line_above"):
            print(f"      line above it on the page: {p['line_above']!r} "
                  f"(may be the period's own name, may be page chrome)")
        if p["deadline"] and p["deadline_kind"] == "automatic":
            print(f"      transmitted automatically on {p['deadline']} — "
                  f"REVIEW THE PERIOD BEFORE THEN")
        elif p["deadline"] and p["deadline_kind"] == "manual":
            print(f"      manual transmission possible from {p['deadline']} — "
                  f"the user sends it, nobody else")
        elif p["deadline"]:
            print(f"      a date is stated ({p['deadline']}) and this script "
                  f"could not tell automatic from manual — read the line "
                  f"yourself: {p['count_line'] or 'see the page'}")
        else:
            print("      no transmission date could be read on this period")
        if p["language"] == "unrecognised":
            print("      (the French labels were not found — this period was "
                  "read structurally, so check the numbers against the page)")
    print()


def print_check(res: dict) -> None:
    if not res["usable"]:
        print("REFUSED — nothing may be written.")
        print(f"  {res['reason']}")
        print()
        print_periods(res.get("periods") or [])
        return
    print_periods(res.get("periods") or [])
    if res.get("empty_period"):
        print(f"job-room entries read: 0 — {res['note']}")
    else:
        print(f"job-room entries read: {res['existing_count']} "
              f"(job-room itself says {res.get('declared_count')})")
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

# --------------------------------------------------------------------------
# prefill — propose what job-room's form should read, and save nothing
# --------------------------------------------------------------------------

# Measured on job-room (2026-11-12): the *Motif* field appears only once
# *Réponse négative* has been chosen, and it is mandatory and capped at 250
# characters. The cap is the page's, not ours, so a longer motif is NAMED and
# never shortened here: trimming a third party's words inside an official
# declaration would publish a sentence nobody wrote.
MOTIF_MAX = 250

# The form's result values this command is allowed to propose. *Engagement* is
# deliberately absent: no mail event establishes a hire, and a declaration that
# claims one is the one error on this form that is not merely inaccurate.
RESULTAT_EN_SUSPENS = "En suspens"
RESULTAT_NEGATIF = "Réponse négative"
CASE_ENTRETIEN = "Entretien d'embauche"

# Event type -> what the form should read. `autre` and `accuse_reception` and
# `demande_action` are listed EXPLICITLY rather than falling into a default:
# a type this contract does not declare must leave under its own name, and a
# fourth branch that swallows it would coerce an unknown onto *En suspens*.
MAPPING = {
    "refus": {"resultat": RESULTAT_NEGATIF, "motif_requis": True},
    "entretien": {"resultat": RESULTAT_EN_SUSPENS, "case": CASE_ENTRETIEN},
    "accuse_reception": {"resultat": RESULTAT_EN_SUSPENS},
    "demande_action": {"resultat": RESULTAT_EN_SUSPENS},
    "autre": {"resultat": RESULTAT_EN_SUSPENS},
}


def _index_rows(plan: dict, rows: list[dict]) -> dict:
    """Every SENT ledger row by id, carrying the plan bucket it fell into.

    The plan only lists what is still to DO, so a row that is declared and has
    not moved since falls into none of its three buckets. Indexing the plan
    alone would make that row indistinguishable from an id the ledger has
    never carried — and those two need opposite answers: one says «your record
    is behind the mail», the other says «this event names something unknown».
    Sending the user to hunt for an id their own file holds is the expensive
    half, so the index starts at the rows.
    """
    out = {}
    for r in rows:
        if not sent(r) or not r.get("id"):
            continue
        out[r["id"]] = {
            "id": r["id"],
            "company": r.get("societe", ""),
            "role": r.get("poste", ""),
            "status": r["kind"],
            "status_date": r["date"],
            "declared": r["jr_declared"],
            "bucket": "declared",
        }
    for bucket in ("to_enter", "to_update", "waived"):
        for item in plan.get(bucket) or []:
            if item.get("id"):
                out[item["id"]] = dict(out.get(item["id"], {}), **item)
                out[item["id"]]["bucket"] = bucket
    return out


# The twelve French month words, folded through `norm` so an accent or a
# capital cannot change the answer. `parse_periods` already reads this page in
# French — its count label and its «automatique» are French too — so this adds
# no assumption that was not already measured. What it does NOT do is guess:
# a label this table does not hold leaves the period UNMATCHED, under that
# name, rather than being placed somewhere plausible.
MOIS_FR = {norm(m): n + 1 for n, m in enumerate(
    ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
     "août", "septembre", "octobre", "novembre", "décembre"])}


def period_month(label: str):
    """`(year, month)` for a period label, or `None` when the word is unknown."""
    m = MONTH_RE.match((label or "").strip())
    if not m:
        return None
    n = MOIS_FR.get(norm(m.group(1)))
    return (int(m.group(2)), n) if n else None


def periods_gate(periods, today: str) -> dict:
    """Which control periods can no longer be edited, from the page's own dates.

    **A period's deadline is when it TRANSMITS, not the span it covers.** The
    October period transmits on 6 November, so a row declared on 3 November
    belongs to November and is still editable. Comparing a declaration date
    against the latest passed deadline conflates the two and marks live rows as
    frozen — the restrictive direction, which nobody audits.

    So the match is on the MONTH, and only when the label's month word is one
    this page's language gives us. `periods` is `None` when the listing was not
    supplied: that is NOT «every period is open», it is «this gate was not
    consulted», and it leaves under that name. An absent verdict is not a pass.
    """
    if periods is None:
        return {"consulte": False, "par_mois": {}, "transmises": [],
                "non_reconnues": []}
    par_mois, transmises, non_reconnues = {}, [], []
    for p in periods:
        ym = period_month(p.get("label", ""))
        passee = bool(p.get("deadline")) and p["deadline"] < today
        resume = {"label": p.get("label"), "deadline": p.get("deadline"),
                  "deadline_kind": p.get("deadline_kind"), "transmise": passee}
        if ym is None:
            non_reconnues.append(resume)
            continue
        par_mois[f"{ym[0]:04d}-{ym[1]:02d}"] = resume
        if passee:
            transmises.append(resume)
    return {"consulte": True, "par_mois": par_mois, "transmises": transmises,
            "non_reconnues": non_reconnues}


def period_of(gate: dict, declared):
    """`(verdict, period)` for a declaration date — three outcomes, never two.

    `None` is «not established», and it covers both «the gate was not
    consulted» and «the listing carries no period for that month». Folding
    either one into `False` would read as «editable, checked».
    """
    if not gate.get("consulte") or not declared:
        return None, None
    p = gate["par_mois"].get(declared[:7])
    if p is None:
        return None, None
    return bool(p["transmise"]), p


def build_prefill(plan: dict, ev: dict, rows: list[dict],
                  periods=None, today=None) -> dict:
    """Turn the latest event per application into form proposals — only that.

    Four things decide, and three of them REFUSE:

    * **The ledger goes first.** A `refus` event sitting on a row the ledger
      still calls `applied` means our own record has not absorbed the mail
      yet. Declaring *Réponse négative* on that strength would put an official
      declaration ahead of the user's own file, so nothing is proposed and the
      ledger is named as the thing to update.
    * **A row that is not declared yet has no field to prefill.** It belongs to
      `plan`, not here, and saying so is not the same as having nothing to say.
    * **A `waived` row is never proposed again** — that decision was taken.
    * **Below `haute` confidence nothing is applied without an explicit yes**,
      and the proposal carries its source so the user can go and look.
    """
    today = today or dt.date.today().isoformat()
    gate = periods_gate(periods, today)
    par_id = _index_rows(plan, rows)

    props, hors_registre, non_declarees, deja_renoncees, retard_registre = \
        [], [], [], [], []

    for cid, e in sorted((ev.get("dernier_par_candidature") or {}).items()):
        item = par_id.get(cid)
        source = {"thread_url": e.get("thread_url"),
                  "confiance": e.get("confiance"),
                  "date_evenement": e.get("date_evenement"),
                  "message_id": e.get("message_id")}
        if item is None:
            # Named, one per line, never counted: an event aimed at an id the
            # ledger does not carry is a question, not a statistic.
            hors_registre.append({"candidature_id": cid, **source,
                                  "type": e.get("type")})
            continue
        base = {"id": cid, "company": item.get("company", ""),
                "role": item.get("role", ""), "type": e.get("type"),
                "source": source,
                "confirmation_explicite_requise": bool(e.get("a_confirmer"))}
        if item["bucket"] == "waived":
            deja_renoncees.append(base)
            continue
        if item["bucket"] == "to_enter":
            non_declarees.append(base)
            continue
        regle = MAPPING.get(e.get("type"))
        if regle is None:
            # An unknown or absent type is NOT coerced onto `autre`.
            hors_registre.append({"candidature_id": cid, **source,
                                  "type": e.get("type"),
                                  "raison": "type absent du contrat"})
            continue
        if e.get("type") == "refus" and item.get("status") not in (
                "rejected", "refusé", "refuse"):
            retard_registre.append(dict(base, statut_ledger=item.get("status")))
            continue

        motif = e.get("motif_refus")
        prop = dict(base)
        prop["resultat"] = regle["resultat"]
        if regle.get("case"):
            prop["case_a_cocher"] = regle["case"]
        if regle.get("motif_requis"):
            prop["motif_requis"] = True
            prop["motif"] = motif
            # The sheet's own wording, from a third party's mail. It is never
            # written into an official field without the user reading it.
            prop["motif_non_fiable"] = motif is not None
            prop["motif_a_ecrire_par_le_candidat"] = motif is None
            prop["motif_longueur"] = len(motif) if motif else 0
            prop["motif_trop_long"] = bool(motif) and len(motif) > MOTIF_MAX
        declared = item.get("declared")
        prop["declared"] = declared
        verdict, periode = period_of(gate, declared)
        prop["periode_transmise"] = verdict
        prop["periode"] = periode["label"] if periode else None
        props.append(prop)

    return {
        "propositions": props,
        "retard_registre": retard_registre,
        "non_declarees": non_declarees,
        "deja_renoncees": deja_renoncees,
        "hors_registre": hors_registre,
        "sans_candidature": ev.get("sans_candidature") or [],
        "valeurs_inconnues": ev.get("valeurs_inconnues") or [],
        "periodes": gate,
        "counts": {
            "propositions": len(props),
            "retard_registre": len(retard_registre),
            "non_declarees": len(non_declarees),
            "deja_renoncees": len(deja_renoncees),
            "hors_registre": len(hors_registre),
            "sans_candidature": len(ev.get("sans_candidature") or []),
        },
        # Said on every run, in the output itself, because a command that
        # proposes form values is exactly where a reader stops assuming.
        "rien_n_est_sauve": True,
        "periode_jamais_transmise": True,
    }


def print_prefill(pre: dict) -> None:
    print("prefill — PROPOSALS ONLY. Nothing here is saved, no field is")
    print("written without the user validating it, and the period is NEVER")
    print("transmitted by this command.")
    print()
    g = pre["periodes"]
    if not g["consulte"]:
        print("control periods: NOT CONSULTED (no --jobroom-text). This is not")
        print("  «every period is open» — a period already transmitted cannot be")
        print("  edited, and nothing here checked whether one is.")
    else:
        if g["transmises"]:
            print(f"control periods already transmitted ({len(g['transmises'])}) "
                  f"— they can no longer be edited:")
            for p in g["transmises"]:
                print(f"  · {p['label']}  transmitted {p['deadline']} "
                      f"({p['deadline_kind']})")
        else:
            print("control periods: none of them has passed its transmission "
                  "date.")
        for p in g["non_reconnues"]:
            print(f"  · {p['label']!r}: month word not recognised — rows of that "
                  f"month are reported as NOT ESTABLISHED, never as editable")
    print()

    print(f"proposals ({len(pre['propositions'])}):")
    for p in pre["propositions"]:
        print(f"  · {p['company'][:40]:40} {p['role'][:38]}")
        print(f"      event {p['type']} on {p['source']['date_evenement']} "
              f"— confidence {p['source']['confiance']}")
        print(f"      Résultat -> {p['resultat']}")
        if p.get("case_a_cocher"):
            print(f"      tick     -> {p['case_a_cocher']}")
        if p.get("motif_requis"):
            if p.get("motif_a_ecrire_par_le_candidat"):
                print("      Motif    -> MANDATORY and the sheet gives none: "
                      "the user writes it")
            else:
                print(f"      Motif    -> proposed from the mail "
                      f"({p['motif_longueur']}/{MOTIF_MAX} chars) — "
                      f"UNTRUSTED third-party text, read it before saving")
                print(f"                  {p['motif'][:72]}")
                if p.get("motif_trop_long"):
                    print(f"      ** too long for the field by "
                          f"{p['motif_longueur'] - MOTIF_MAX} characters. It is "
                          f"NOT shortened here: trimming someone else's words")
                    print("         inside a declaration publishes a sentence "
                          "nobody wrote. **")
        if p.get("confirmation_explicite_requise"):
            print("      ** confidence below `haute`: this is a SUGGESTION and "
                  "needs an explicit yes **")
        if p.get("periode_transmise") is True:
            print(f"      ** its period ({p.get('periode')}) is already "
                  f"transmitted — a transmitted period cannot be edited, so "
                  f"this is SAID and not proposed **")
        elif p.get("periode_transmise") is None:
            print("      (period not established: the listing was not supplied, "
                  "or carries no period for that month)")
        if p["source"].get("thread_url"):
            print(f"      source: {p['source']['thread_url']}")
    if not pre["propositions"]:
        print("  (none)")

    for key, title in (
        ("retard_registre",
         "the LEDGER is behind — update it first, nothing proposed"),
        ("non_declarees",
         "not declared in job-room yet — these belong to `plan`, not here"),
        ("deja_renoncees",
         "deliberately not declared (`JR:waived`) — never proposed again"),
        ("hors_registre",
         "events the ledger does not carry, or a type this contract does not "
         "declare"),
    ):
        rows = pre.get(key) or []
        if not rows:
            continue
        print()
        print(f"{title} ({len(rows)}):")
        for r in rows:
            who = (f"{r.get('company', '')[:36]:36} {r.get('role', '')[:30]}"
                   if r.get("company") else r.get("candidature_id", ""))
            extra = ""
            if key == "retard_registre":
                extra = f"  ledger says `{r.get('statut_ledger')}`"
            if key == "hors_registre":
                extra = f"  type {r.get('type')!r}"
            print(f"  · {who}{extra}")

    if pre["sans_candidature"]:
        print()
        print(f"events naming no single application "
              f"({len(pre['sans_candidature'])}) — SUGGESTIONS the user "
              f"confirms:")
        for r in pre["sans_candidature"]:
            cands = ", ".join(r.get("candidats_possibles") or []) or "(none)"
            print(f"  · {r.get('date_evenement')} {r.get('type')}  "
                  f"possible: {cands}")

    if pre["valeurs_inconnues"]:
        print()
        print(f"cells carrying a value this contract does not list "
              f"({len(pre['valeurs_inconnues'])}) — NAMED, never coerced:")
        for r in pre["valeurs_inconnues"]:
            print(f"  · {r}")


def _read_text(path):
    """`-` is stdin; anything else is a file, closed on the way out (#210)."""
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=DEFAULT_PIPELINE,
                    help=f"pipeline file (default: {DEFAULT_PIPELINE})")
    ap.add_argument("--state", default=DEFAULT_STATE,
                    help=f"sync state file (default: {DEFAULT_STATE})")
    ap.add_argument("--format", choices=("table", "json"), default="table")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("plan", help="what to declare, and what to correct")
    pl.add_argument("--jobroom-text", default=None,
                    help="file holding the job-room period listing "
                         "(get_page_text output; use '-' for stdin). With it, "
                         "refusals declared in a TRANSMITTED period leave "
                         "`to_update` for `frozen`; without it the gate is NOT "
                         "consulted, and the output says so")

    c = sub.add_parser("check", help="refuse anything already in job-room")
    c.add_argument("--jobroom-text", required=True,
                   help="file holding the job-room period listing (get_page_text output; "
                        "use '-' for stdin)")

    d = sub.add_parser("periods",
                       help="the control periods and their transmission dates")
    d.add_argument("--jobroom-text", required=True,
                   help="file holding the job-room period listing "
                        "(get_page_text output; use '-' for stdin)")

    f = sub.add_parser("prefill",
                       help="propose what job-room's form should read, from "
                            "the events tab — and save nothing")
    f.add_argument("--events", required=True,
                   help="CSV export of the `evenements` tab (issue #1307)")
    f.add_argument("--jobroom-text", default=None,
                   help="file holding the job-room period listing "
                        "(get_page_text output; use '-' for stdin). Without "
                        "it the transmitted-period gate is NOT consulted, and "
                        "the output says so rather than implying it is open")

    m = sub.add_parser("mark-synced", help="record that job-room is now up to date")
    m.add_argument("--entries", type=int, default=None,
                   help="number of entries the period holds after the session")

    args = ap.parse_args()
    state = read_state(args.state)

    if args.cmd == "plan":
        rows, skipped = load_rows(args.file)
        periods = None
        if args.jobroom_text:
            periods = parse_periods(_read_text(args.jobroom_text))
            if not periods:
                # The same refusal `periods` and `prefill` make: no period
                # read is a page this script could not read, not an open board.
                print("error: --jobroom-text carried no readable control "
                      "period. That is a page this script could not read, "
                      "not a board with nothing on it", file=sys.stderr)
                return 2
        plan = build_plan(rows, state, skipped, periods)
        print(json.dumps(plan, indent=2, ensure_ascii=False)) if args.format == "json" else print_plan(plan)
        return 0

    if args.cmd == "check":
        rows, skipped = load_rows(args.file)
        plan = build_plan(rows, state, skipped)
        text = _read_text(args.jobroom_text)
        res = run_check(plan, text)
        print(json.dumps(res, indent=2, ensure_ascii=False)) if args.format == "json" else print_check(res)
        # Exit 2 when the listing could not be read: a caller that ignores the
        # output still cannot mistake this for "verified, nothing found".
        return 0 if res["usable"] else 2

    if args.cmd == "periods":
        text = _read_text(args.jobroom_text)
        periods = parse_periods(text)
        if args.format == "json":
            print(json.dumps(periods, indent=2, ensure_ascii=False))
        else:
            print_periods(periods)
        # No period read is a failure to read the page, not an empty board.
        return 0 if periods else 2

    if args.cmd == "prefill":
        rows, skipped = load_rows(args.file)
        plan = build_plan(rows, state, skipped)
        reader = _events_reader.load("--events")
        try:
            ev = reader.events(args.events)
        except reader.SheetRefused as e:
            # The reader's own codes travel out: «not there» (4) and «not this
            # tab» (5) are different repairs, and NEITHER of them is «this
            # sheet holds no event». A proposal list is exactly where that
            # degradation would be invisible — it would simply be empty.
            print(f"error: --events {args.events}: {e}", file=sys.stderr)
            return e.code
        periods = None
        if args.jobroom_text:
            periods = parse_periods(_read_text(args.jobroom_text))
            if not periods:
                # Reading no period is a failure to read the page, never an
                # empty board — the same refusal `periods` already makes.
                print("error: --jobroom-text carried no readable control "
                      "period. That is a page this script could not read, "
                      "not a board with nothing on it", file=sys.stderr)
                return 2
        pre = build_prefill(plan, ev, rows, periods)
        if args.format == "json":
            print(json.dumps(pre, indent=2, ensure_ascii=False))
        else:
            print_prefill(pre)
        return 0

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
