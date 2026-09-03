#!/usr/bin/env python3
"""Ask, once a month, what the candidate has done since last time — and stay
quiet the rest of the time.

**Issue #42.** A candidate's file ages in silence. Nothing in this plugin ever
asks *"have you done anything new?"*, and that is the only way an achievement
that exists in no export ever gets into the record.

THE CASE. On 2026-08-31 a passing question — *does the plugin itself appear in
`repos.md`?* — turned up **no**. It was a public MIT repository, 125 commits,
35 adapters, 7 814 lines of dependency-free Python, written in five days
**during the job search**, and it was the best evidence for a practice the
dossier already claimed on ten times thinner grounds. The file had been reread
and enriched several times in those five days. **Nobody thought to ask.** A
candidate does not spontaneously declare what they have just done: to them it
is the present, not a CV line.

**AND THIS IS NOT A DEVELOPER'S PROBLEM.** `repos.md` is an artefact of one
trade. The reflex is to implement a reminder that scans git repositories, and
that is missing the point entirely — a cabinetmaker delivered three kitchens, a
nurse qualified in palliative care, a project manager finished a migration, a
graphic designer redid a client's identity. **None of that is detectable, and
only the question makes it exist.** So this file holds a schedule and nothing
else: it never looks at the disk, and `where` refuses to name a file that does
not exist in this workspace.

WHAT IT STORES, AND WHAT IT DELIBERATELY DOES NOT. `$JOB_HUNT_HOME/
.achievements.json` holds **when the question was last asked** and whether
anything came of it. **Never the answer itself** — that belongs in the
candidate's own files, after they have approved the wording, because a badly
phrased achievement in `repos.md` propagates into every CV generated
afterwards.

    python3 achievements.py due            # is it time? JSON, and exit 0
    python3 achievements.py where          # which files this workspace has
    python3 achievements.py asked --outcome none|recorded|paused
"""

import argparse
import datetime as dt
import json
import os
import sys

JOB_HUNT_HOME = os.environ.get(
    "JOB_HUNT_HOME", os.path.expanduser("~/Documents/job_applications"))
STATE = os.path.join(JOB_HUNT_HOME, ".achievements.json")

EVERY_DAYS = 30

# Where an achievement can go, in the order a router should consider them, with
# what each is for. **`repos.md` is one entry among several and never the
# default** — see the header.
DESTINATIONS = (
    ("candidate.md", "the default for every trade: a qualification, a "
                     "responsibility, a delivery, a piece of volunteering"),
    ("repos.md", "software work with a repository, and nothing else"),
    ("profile/", "a document that speaks for itself — a certificate, a "
                 "portfolio page, an attestation"),
)


def today():
    return dt.date.today()


def load():
    try:
        with open(STATE, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except FileNotFoundError:
        return {}
    except (ValueError, OSError) as e:
        # A corrupt state file must not silence the question for ever, and must
        # not be repaired quietly either.
        print(f"[achievements] {STATE} did not parse ({e}) — treating it as "
              f"never asked. Delete it if that is wrong.", file=sys.stderr)
        return {}


def save(d):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, STATE)


def cmd_due(a):
    st = load()
    out = {"due": False, "last_asked": st.get("last_asked"),
           "every_days": a.every_days, "days_since": None,
           "paused": bool(st.get("paused")), "reason": None}

    if st.get("paused"):
        out["reason"] = ("the candidate asked to stop being asked. **Do not "
                         "ask again** — they turn it back on themselves.")
        print(json.dumps(out, ensure_ascii=False))
        return 0

    last = st.get("last_asked")
    if not last:
        out.update(due=True, reason=(
            "never asked. The first time is the one that pays: a dossier that "
            "has been reread several times is exactly the one nobody thought "
            "to ask about."))
        print(json.dumps(out, ensure_ascii=False))
        return 0

    try:
        d = dt.date.fromisoformat(last)
    except ValueError:
        out.update(due=True, reason=f"`last_asked` is not a date ({last!r}).")
        print(json.dumps(out, ensure_ascii=False))
        return 0

    days = (today() - d).days
    out["days_since"] = days
    if days >= a.every_days:
        out.update(due=True, reason=(
            f"{days} days since the last time, and the interval is "
            f"{a.every_days}."))
    else:
        out["reason"] = (
            f"asked {days} days ago. **A question asked too often is ignored, "
            f"then resented, then switched off** — so it waits.")
    print(json.dumps(out, ensure_ascii=False))
    return 0


def cmd_where(a):
    """What this workspace actually has. Never an assumption about the trade."""
    rows = []
    for name, what in DESTINATIONS:
        path = os.path.join(JOB_HUNT_HOME, name)
        rows.append({"name": name, "purpose": what,
                     "exists": os.path.exists(path), "path": path})
    print(json.dumps({"home": JOB_HUNT_HOME, "destinations": rows},
                     ensure_ascii=False, indent=2))
    if not any(r["exists"] for r in rows):
        print("[achievements] this workspace has none of the destinations — "
              "run `/job-setup` before recording anything.", file=sys.stderr)
    missing = [r["name"] for r in rows if not r["exists"]]
    if missing:
        print(f"[achievements] absent here, and **do not create one to have "
              f"somewhere to put a trade it does not fit**: "
              f"{', '.join(missing)}", file=sys.stderr)
    return 0


def cmd_asked(a):
    st = load()
    st["last_asked"] = (a.date or today().isoformat())
    st["last_outcome"] = a.outcome
    st["asked_count"] = int(st.get("asked_count") or 0) + 1
    if a.outcome == "paused":
        st["paused"] = True
    elif a.outcome in ("none", "recorded"):
        st.pop("paused", None)
    if a.outcome == "recorded":
        st["last_recorded"] = st["last_asked"]
    save(st)
    # The state carries dates and outcomes, never the achievement itself.
    print(json.dumps({k: st[k] for k in sorted(st)}, ensure_ascii=False))
    if a.outcome == "none":
        print("[achievements] recorded as asked. **A 'no' is a complete "
              "answer** — do not follow up, and do not ask again before the "
              "interval is up.", file=sys.stderr)
    return 0


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("due", help="is it time to ask?")
    d.add_argument("--every-days", type=int, default=EVERY_DAYS)
    d.set_defaults(func=cmd_due)

    w = sub.add_parser("where", help="which destination files exist here")
    w.set_defaults(func=cmd_where)

    a_ = sub.add_parser("asked", help="record that the question was put")
    a_.add_argument("--outcome", required=True,
                    choices=["none", "recorded", "paused"],
                    help="none = they had nothing; recorded = something was "
                         "written, with their approval; paused = they asked "
                         "not to be asked again")
    a_.add_argument("--date", help="ISO date, default today")
    a_.set_defaults(func=cmd_asked)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
