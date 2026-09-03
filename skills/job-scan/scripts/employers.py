#!/usr/bin/env python3
"""What is true of an *employer*, read before an ad of theirs is proposed.

**Issue #94.** The ledger is indexed by advertisement, so a decision about a
company written on one ad's row is found only by luck.

WHAT IT COST, MEASURED 2026-09-02:

    19.08  freeze on an employer declared      → written on one ad's row
    27.08  freeze lifted by the candidate      → written on another ad's row
    02.09  a scan discards three of that
           employer's ads, citing "the freeze
           of 2026-08-19, a standing decision"

**Two live ads were discarded on a decision that no longer existed.** The two
notes sat eighteen rows apart. `SKILL.md` says to read a row's notes before
proposing it, **and that was done — one note was read.** The fact that
cancelled it lived elsewhere, and nothing in the file's structure said to go
and look.

**SO THIS COMMAND EXISTS TO MAKE THE LOOKUP MECHANICAL RATHER THAN HOPED FOR.**
`lookup` returns every standing decision for an employer **with its lifting
date beside it**, so a lifted freeze cannot be read as a live one. A reader who
has to join two facts across eighteen rows will eventually not.

WHAT IT REFUSES TO DO. It never reads the ledger and never reports a score, a
status or an ad. **Two places that say the same thing eventually disagree** —
a wrong percentage in this repository once survived two clean-ups because it
was written in three places. The authority rule is written in
`shared/workspace.md`: **the ledger is authoritative about advertisements, this
file about the employer, and they never speak about the same thing.**

    python3 employers.py lookup --name "Acme SA"
    python3 employers.py list
"""

import argparse
import json
import os
import re
import sys
import unicodedata

JOB_HUNT_HOME = os.environ.get(
    "JOB_HUNT_HOME", os.path.expanduser("~/Documents/job_applications"))
DEFAULT_FILE = os.path.join(JOB_HUNT_HOME, "employers.md")

EXIT_NO_FILE = 0        # absent is not an error: the file is optional

# A row of the standing-decisions table: | from | decision | lifted | why |
ROW = re.compile(r"^\|(?P<cells>.*)\|\s*$")
DATE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

# **One field, three states, and the third is "not asked" rather than neutral.**
# It is read from the header bullets and never from the decisions table: every
# row of that table carries a lifting date, and a preference is not lifted.
PREF = re.compile(r"^\s*-\s*\**preference\**\s*[—:-]\s*(?P<rest>.*)$", re.I)
PREF_VALUES = ("preferred", "excluded")


def fold(s):
    """Compare names without accents or case. `_locations.py` folds the same
    way, and for the same reason: one employer under three spellings."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def sections(text):
    """`## <employer>` to the next `## `, keeping the heading.

    **Only what follows the first `---` rule counts as an employer.** The
    file's own preamble uses `##` headings too, and without this boundary
    *"Authority"* and *"The two rules"* are listed as companies — which is not
    a cosmetic defect: a lookup for an employer whose name happened to collide
    would match a paragraph of prose and report its absence of decisions as
    fact. A file with no `---` is read whole, and says so.
    """
    body = (text or "")
    parts = re.split(r"(?m)^-{3,}\s*$", body, maxsplit=1)
    if len(parts) == 2:
        body = parts[1]
    out, name, buf = [], None, []
    for line in body.splitlines():
        m = re.match(r"^##\s+(?!#)(.*\S)\s*$", line)
        if m:
            if name:
                out.append((name, "\n".join(buf)))
            name, buf = m.group(1).strip(), []
        elif name:
            buf.append(line)
    if name:
        out.append((name, "\n".join(buf)))
    return out


def decisions(body):
    """Every row of a standing-decisions table, lifting date included.

    **A lifted decision is returned, not filtered out.** Dropping it would
    leave the caller with no way to contradict a freeze it remembers.
    """
    out, in_table = [], False
    for line in body.splitlines():
        m = ROW.match(line.strip())
        if not m:
            in_table = False
            continue
        cells = [c.strip() for c in m.group("cells").split("|")]
        if not cells or all(set(c) <= set("-: ") for c in cells if c):
            in_table = True
            continue
        if not in_table:
            # A header row; the separator below it turns the table on.
            continue
        frm = (DATE.search(cells[0]).group(1)
               if len(cells) > 0 and DATE.search(cells[0]) else None)
        lifted = (DATE.search(cells[2]).group(1)
                  if len(cells) > 2 and DATE.search(cells[2]) else None)
        out.append({
            "from": frm,
            "decision": cells[1] if len(cells) > 1 else None,
            "lifted": lifted,
            "why": cells[3] if len(cells) > 3 else None,
            "active": bool(frm) and not lifted,
        })
    return out


def bullets(body):
    """Top-level bullets, **joined across wrapped lines**.

    Both readers below need this. The first version of `undated()` read line
    by line and reported four undated facts in a file where two carried their
    date on the continuation line — a check that cries wolf on a well-kept
    file gets switched off, and then the real ones go unseen.
    """
    out, cur = [], None
    for line in body.splitlines() + [""]:
        s = line.strip()
        if s.startswith("- ") or not s or s.startswith(("#", "|")):
            if cur is not None:
                out.append(re.sub(r"\s+", " ", cur).strip())
            cur = s[2:] if s.startswith("- ") else None
        elif cur is not None:
            cur += " " + s
    return [b for b in out if b]


def preference(body):
    """`preferred`, `excluded`, or None for **never asked**.

    Read from the header bullets only. A preference found inside the standing
    decisions table is a misfiling and is reported as one: everything in that
    table ends, and this does not.
    """
    out = {"value": None, "since": None, "reason": None, "misfiled": False}
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("|") and any(v in s.lower() for v in PREF_VALUES):
            out["misfiled"] = True
    for b in bullets(body):
        m = PREF.match("- " + b)
        if not m:
            continue
        rest = m.group("rest")
        low = rest.lower()
        for v in PREF_VALUES:
            if v in low:
                out["value"] = v
                break
        d = DATE.search(rest)
        out["since"] = d.group(1) if d else None
        # Everything after the first separator that is not the date.
        r = re.split(r"[—·|]", rest)
        out["reason"] = (re.sub(r"\s+", " ", r[-1]).strip(" *_`") or None) \
            if len(r) > 1 else None
        break
    return out


def undated(body):
    """Bullet facts carrying no date. A fact about an employer goes stale."""
    return [b[:140] for b in bullets(body) if not DATE.search(b)]


def cmd_lookup(a):
    path = a.file or DEFAULT_FILE
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        print(json.dumps({"file": path, "exists": False, "matched": None,
                          "note": "no employers.md — nothing is known about "
                                  "any employer, which is not the same as "
                                  "nothing being true. Say so rather than "
                                  "proceeding as if it were checked."}),
              ensure_ascii=False)
        return EXIT_NO_FILE

    want = fold(a.name)
    hits = []
    for name, body in sections(text):
        folded = fold(name)
        # Substring both ways: "Acme" finds "Acme SA", and an ad's
        # "ACME HOLDING SA" finds "Acme". Reported, never silently chosen.
        if want and (want in folded or folded in want):
            d = decisions(body)
            hits.append({
                "employer": name,
                "preference": preference(body),
                "decisions": d,
                "active_decisions": [x for x in d if x["active"]],
                "undated_facts": undated(body),
            })

    out = {"file": path, "exists": True, "query": a.name,
           "matched": [h["employer"] for h in hits], "employers": hits}
    if len(hits) > 1:
        out["warning"] = ("more than one section matched. **Two legal names "
                          "for one employer have already blocked an official "
                          "declaration here** — resolve which one this ad is, "
                          "do not merge them silently.")
    if not hits:
        out["note"] = ("no section for this employer. That is an absence of "
                       "record, not an absence of decisions.")
    active = [x for h in hits for x in h["active_decisions"]]
    if active:
        out["say"] = ("A standing decision is in force and it must reach the "
                      "user before an ad of theirs is proposed.")
    prefs = [h["preference"] for h in hits if h["preference"]["value"]]
    if prefs:
        out["preference_says"] = (
            "**This never touches the score.** A preference changes the "
            "cadence, the effort and the order of work — it is shown beside "
            "the ratio at the gate and never inside it. *'55%, and this is an "
            "employer you favour'* is information; *'68%'* for the same ad is "
            "a lie.")
    if any(h["preference"]["misfiled"] for h in hits):
        out["misfiled_preference"] = (
            "A preference appears in the standing-decisions table. **It does "
            "not belong there**: every row of that table carries a lifting "
            "date and a preference is not lifted — filed there it reads as a "
            "decision nobody ended.")
    if not prefs and hits:
        out["preference_says"] = (
            "**No preference recorded — which means never asked, not "
            "neutral.** Ask once at the go/no-go gate, then never again for "
            "this employer.")
    lifted = [x for h in hits for x in h["decisions"] if x["lifted"]]
    if lifted:
        out["lifted"] = ("Decisions recorded here have been lifted. **A lifted "
                         "decision is not a current one** — do not cite it, "
                         "and do not reinstate it from memory.")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_list(a):
    path = a.file or DEFAULT_FILE
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        print(f"[employers] no {path} — the file is optional and this is not "
              f"an error. `/job-setup` offers to create it.", file=sys.stderr)
        return EXIT_NO_FILE
    for name, body in sections(text):
        d = decisions(body)
        act = sum(1 for x in d if x["active"])
        print(json.dumps({"employer": name,
                          "preference": preference(body)["value"],
                          "decisions": len(d), "active": act,
                          "undated_facts": len(undated(body))},
                         ensure_ascii=False))
    return 0


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", help=f"default {DEFAULT_FILE}")
    sub = p.add_subparsers(dest="cmd", required=True)

    lk = sub.add_parser("lookup", help="everything recorded for one employer")
    lk.add_argument("--name", required=True)
    lk.set_defaults(func=cmd_lookup)

    ls = sub.add_parser("list", help="one line per employer")
    ls.set_defaults(func=cmd_list)

    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
