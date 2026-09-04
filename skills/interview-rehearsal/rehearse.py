#!/usr/bin/env python3
"""Draw the interviewers' facets, seal them, and check them back afterwards.

WHY THIS IS A SCRIPT AND NOT A PARAGRAPH OF INSTRUCTIONS

The skill could ask the agent to "draw the facets and remember them". It would
work most of the time, and **the times it did not would be invisible**: a
debrief that reveals facets chosen after the interview reads exactly like one
that reveals facets chosen before it. The candidate has no way to tell, and
neither has anyone reading the transcript later.

So the draw is sealed. `draw` writes the facets to a file **and prints a short
digest of them into the transcript**. `reveal` reads the file back and prints
the same digest. **A set of facets invented after the fact cannot produce a
digest that was already published before the first question**, and anyone
scrolling up can compare two strings.

That is the whole point of this file. It is not encryption and it is not
tamper-proof against someone who wants to cheat; it removes the *accident* —
the honest agent that reconstructs a plausible draw and believes it remembered
one.

WHAT IT DELIBERATELY DOES NOT DO

**It does not decide the facets' meaning, and it does not score anything.**
Drawing is mechanical and belongs here; judging is not and does not. The
percentage is the skill's work, on bases the skill names.

**The facet list is open.** `--facet name=value` accepts anything, and unknown
names are kept verbatim rather than dropped — the "…" in the request is part of
the request.
"""

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import random
import sys

# The facets named in the request, with the values a draw may take. **This is a
# default, not a vocabulary**: `--facet` accepts names that are not here, and
# `--facet name=value` accepts values that are not here either.
FACETS = {
    "technical_depth": ["shallow", "solid", "deep", "expert"],
    "managerial_skill": ["poor", "adequate", "strong"],
    "commercial_instinct": ["absent", "present", "dominant"],
    "warmth": ["cold", "neutral", "warm"],
    # The facet the request singles out, and the one that changes the
    # interview most: it does not change what is asked so much as how a good
    # answer is received.
    "fear_of_replacement": ["none", "latent", "acute"],
    "time_pressure": ["none", "some", "severe"],
    "prepared": ["read nothing", "skimmed the CV", "read everything"],
}

ROLES = ["hiring manager", "future peer", "HR screener", "skip-level"]


def _now():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def digest(payload):
    """Eight hex characters over the canonical form of the draw.

    Short on purpose: it is read by a human comparing two lines in a
    transcript, not by a machine. Collisions do not matter here — nobody is
    searching for one; the failure this prevents is an honest reconstruction,
    which will not match at all.
    """
    canon = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:8]


def _parse_facets(pairs):
    """`name=value` repeated. Unknown names are kept, never dropped."""
    out = {}
    for raw in pairs or []:
        if "=" not in raw:
            sys.exit(f"--facet wants name=value, got {raw!r}")
        name, value = raw.split("=", 1)
        name, value = name.strip(), value.strip()
        if not name or not value:
            sys.exit(f"--facet wants name=value, got {raw!r}")
        out[name] = value
    return out


def cmd_draw(a):
    rng = random.Random(a.seed) if a.seed is not None else random.Random()
    given = _parse_facets(a.facet)

    panel = []
    for i in range(a.interviewers):
        person = {"role": a.role[i] if i < len(a.role or [])
                  else rng.choice(ROLES), "facets": {}}
        for name, values in FACETS.items():
            person["facets"][name] = given.get(name) or rng.choice(values)
        # a facet the caller named that we do not know is still a facet
        for name, value in given.items():
            person["facets"].setdefault(name, value)
        panel.append(person)

    record = {
        "kind": "rehearsal",  # never "interview" — red line 1
        "drawn_at": _now(),
        "seed": a.seed,
        "given": given,
        "role_hint": a.role or [],
        "panel": panel,
    }
    record["digest"] = digest(record["panel"])

    path = pathlib.Path(a.out)
    if path.exists() and not a.force:
        sys.exit(f"{path} already holds a draw. Use a new path, or --force to "
                 f"replace it — but a replaced draw is a new rehearsal, not "
                 f"the same one.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")

    # **What reaches the transcript, and what does not.** The digest and the
    # count, never the facets: printing them here would hand the candidate the
    # answer before the first question.
    print(f"sealed {len(panel)} interviewer(s) — digest {record['digest']}")
    print(f"recorded in {path}")
    print("Do not print the facets before the debrief. Reveal with:")
    print(f"  rehearse.py reveal --file {path}")


def cmd_reveal(a):
    path = pathlib.Path(a.file)
    if not path.exists():
        sys.exit(f"no draw at {path}. **A debrief without a sealed draw cannot "
                 f"reveal anything honestly** — say so plainly rather than "
                 f"describing facets from memory.")
    record = json.loads(path.read_text(encoding="utf-8"))
    recomputed = digest(record["panel"])
    sealed = record.get("digest")
    if recomputed != sealed:
        sys.exit(f"the file has changed since it was sealed: it now hashes to "
                 f"{recomputed}, and it was sealed as {sealed}. Report that, "
                 f"and do not present its contents as the draw.")
    print(json.dumps(record, indent=1, ensure_ascii=False))
    print(f"\ndigest {sealed} — compare it with the line printed at draw time; "
          f"if they match, these are the facets that were played.",
          file=sys.stderr)


def cmd_verify(a):
    """Answer one question — does this file still hash to what it claims."""
    record = json.loads(pathlib.Path(a.file).read_text(encoding="utf-8"))
    ok = digest(record["panel"]) == record.get("digest")
    print(json.dumps({"file": a.file, "sealed": record.get("digest"),
                      "recomputed": digest(record["panel"]), "intact": ok},
                     ensure_ascii=False))
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("draw", help="draw the panel and seal it")
    d.add_argument("--out", required=True,
                   help="where the sealed draw is written")
    d.add_argument("--interviewers", type=int, default=1)
    d.add_argument("--facet", action="append",
                   help="name=value, repeatable; fixes a facet instead of "
                        "drawing it. Unknown names are kept.")
    d.add_argument("--role", action="append",
                   help="role of the nth interviewer; drawn when absent")
    d.add_argument("--seed", type=int,
                   help="reproducible draw. **Recorded in the file**, so a "
                        "seeded rehearsal says so rather than passing for a "
                        "free one.")
    d.add_argument("--force", action="store_true")
    d.set_defaults(func=cmd_draw)

    r = sub.add_parser("reveal", help="read the sealed draw back, for the debrief")
    r.add_argument("--file", required=True)
    r.set_defaults(func=cmd_reveal)

    v = sub.add_parser("verify", help="is this draw still what it was sealed as")
    v.add_argument("--file", required=True)
    v.set_defaults(func=cmd_verify)

    a = p.parse_args()
    sys.exit(a.func(a) or 0)


if __name__ == "__main__":
    main()
