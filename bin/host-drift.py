#!/usr/bin/env python3
"""Which board cards name a host that no longer answers for itself.

**A board that has been bought reaches us as a redirect long before it reaches
us as a rename.** Nobody sends an announcement; the infrastructure moves at
once. Four cases turned up in four hours on 2026-09-03, all by the same
mechanism — since #99 a verdict names the host that **answered** rather than
the string that was asked for, so a cross-host redirect stopped being
swallowed:

    my.indeed.com          → secure.indeed.com
    jobs.recruitee.com     → careers.tellent.com      Recruitee is Tellent
    talent-soft.com        → www.cegid.com            Talentsoft is Cegid
    digitalrecruiters.com  → www.cegid.com            the same, twice

**None of them was known here.** And `talentsoft` is the one that bites:
`www.cegid.com` answers 268 KB of HTML, so its `robots.txt` comes back
`unreadable` — **and an `unreadable` reads as a server accident, not as an
acquisition.**

The consequence goes past the name: **a card describing the access policy of
`talent-soft.com` describes a host that no longer serves anything.** The rules
that apply are the receiving platform's, and nobody has read them.

**AND A REDIRECT CAN BE INTERMITTENT, SO READ THE TWO OUTCOMES DIFFERENTLY.**
`my.indeed.com` sent this repository to `secure.indeed.com` in the afternoon
and answered under its own name an hour later. **One observation of drift is a
finding; one observation of no drift is not a clearance** — which is this
repository's rule on independent measurements, turned on the tool that applies
it.

THIS IS A MAINTENANCE DIAGNOSTIC, NOT A RUNTIME CHECK. Four cases in four
hours does not mean four a day; it means **an unexamined backlog empties fast
the first time.** Run it when cards are reviewed.

**AND IT READS A DECLARED FIELD, NEVER PROSE.** `bin/adapter-age.sh` carries
the reason: it once took any date it could find in a file and reported a board
1 384 days stale because the file quoted a date it had measured. *A script that
reads "any date" has no field, it has a heuristic.* The same trap caught the
first draft of this one — extracting hosts from module constants pulled `jobs`
out of a regex literal, a host that is not a host. So:

    <!-- hosts: www.example.com, api.example.com -->

near the top of a board card, beside `<!-- verified: -->`. **A card without one
is reported UNDECLARED — not skipped, and not guessed at.** The absence of a
declaration is not a clean bill; it is the backlog, made visible.

    python3 bin/host-drift.py            # every card
    python3 bin/host-drift.py --drift    # only the ones that moved
"""

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "job-scan", "scripts"))

HOSTS_RE = re.compile(r"(?im)^<!--\s*hosts:\s*(.+?)\s*-->\s*$")


def declared(path):
    with open(path, encoding="utf-8") as f:
        head = f.read(4000)
    m = HOSTS_RE.search(head)
    if not m:
        return None
    return [h.strip().lower() for h in m.group(1).split(",") if h.strip()]


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--drift", action="store_true",
                   help="print only cards whose host has moved")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    try:
        from _robots import verdict
    except ImportError:
        print("ERROR: _robots.py not importable from "
              "skills/job-scan/scripts.", file=sys.stderr)
        return 2

    rows, undeclared = [], []
    for card in sorted(glob.glob(os.path.join(ROOT, "shared", "boards",
                                              "*.md"))):
        name = os.path.basename(card)[:-3]
        if name == "README":
            continue
        hosts = declared(card)
        if hosts is None:
            undeclared.append(name)
            continue
        for h in hosts:
            v = verdict(h)
            answered = v["host"].lower()
            moved = answered != h
            # **`www.` in front of the same name is not an acquisition**, and
            # reporting it as one is how a check gets switched off. Compare
            # what is left after stripping a leading `www.`; anything else is
            # a different operator until shown otherwise.
            same_site = (answered.removeprefix("www.")
                         == h.removeprefix("www."))
            rows.append({
                "card": name, "declared": h, "answered": v["host"],
                "moved": moved, "kind": (None if not moved else
                                         "www" if same_site else "platform"),
                "state": v["state"],
                "sweep": v["sweep"],
                # **The state that matters when they differ is the second
                # host's**, because that is the file that applies.
                "reason": v.get("reason"),
            })

    drift = [r for r in rows if r["moved"] and r["kind"] == "platform"]
    cosmetic = [r for r in rows if r["kind"] == "www"]
    mute = [r for r in rows if not r["moved"] and r["state"] != "read"]
    shown = (drift + cosmetic) if a.drift else rows
    if a.json:
        print(json.dumps({"rows": shown, "undeclared": undeclared},
                         ensure_ascii=False, indent=1))
    else:
        for r in shown:
            flag = {"platform": "MOVED", "www": "www  "}.get(
                r["kind"], "     ")
            print(f"{flag} {r['card']:22} {r['declared']:34} -> "
                  f"{r['answered']:34} {r['state']}")
        if undeclared:
            print(f"\nUNDECLARED ({len(undeclared)}): "
                  f"{', '.join(undeclared)}")
            print("   A card with no `<!-- hosts: -->` header is not clean — "
                  "it is unexamined. Adding one is the work.")
    if cosmetic:
        print(f"\n{len(cosmetic)} card(s) differ only by a leading `www.` — "
              f"the same site, not a change of operator. Listed and not "
              f"raised: a check that cries wolf gets switched off.",
              file=sys.stderr)
    if mute:
        print(f"\n{len(mute)} card(s) answer under their own name and cannot "
              f"be read: "
              + ", ".join(f"{r['card']} ({r['state']})" for r in mute)
              + ". **Not drift — but an `unreadable` is not a clean state "
                "either.**", file=sys.stderr)
    if drift:
        print(f"\n{len(drift)} card(s) name a host that answers under another "
              f"name. **The rules that apply are the receiving host's**, and "
              f"a card describing the first describes a host that no longer "
              f"serves anything.", file=sys.stderr)
        for r in drift:
            if r["state"] != "read":
                print(f"   {r['card']}: {r['answered']} answers "
                      f"`{r['state']}` — **that reads as a server accident "
                      f"and it is an acquisition.**", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
