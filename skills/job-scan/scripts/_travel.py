#!/usr/bin/env python3
"""Business travel asked by an advertisement — **a degree, never a fact.**

`_licence.py` answers *does the candidate hold category B*, and the answer is
yes or no. **This one cannot be built that way**, and the corpus says why.

MEASURED ON THE WORKSPACE CORPUS, 2026-09-04 — 49 advertisements:

    mention a travel word            8   (16%)
    sentences matched               11
      … a real requirement           5
      … the employer's industry      3   "hospitality/travel/property domain"
      … a benefit                    1   "prime mobilité douce" — a cycling
                                         allowance, the opposite of business
                                         travel
      … the plugin's own prose       1   "International travel: confirmed
                                         available by the candidate"

**Six of eleven matches were not a requirement**, which is why this is a
whitelist of phrasings and never a `grep` for the word. Issue #137, and the
precedent is #91: `permis` also names a residence permit, and the fix was the
same.

**The last false positive is the one to keep in mind.** A run writes its own
analysis into the workspace, and the next read finds *"International travel:
confirmed available"* in a file it produced itself. `_licence.py` records the
identical trap. **A detector that reads its own output agrees with itself.**

AND EVERY TRUE MATCH WAS A DEGREE:

    "Ability to travel 3–4 weeks per year to meet teammates in person"
    "Willingness to travel internationally on a limited basis"
    "des déplacements inter-sites sont probables"

**None of them is satisfiable by a yes.** A candidate who will travel three
weeks a year and one who will travel monthly both answer *"yes, I travel"* —
so the useful record is what the advertisement asks, quoted, and what the user
said they will do, not a boolean either side.

**And this never blocks.** `_licence.py`'s `blocker` already means *say it
before a dossier is spent*, never *discard*; here even that is too strong. A
travel requirement is a thing to raise at the gate, and an advertisement is
never set aside for it.
"""

import re

# Phrasings measured in the corpus, plus the German and French forms the same
# boards use. A requirement, never the industry and never a benefit.
_ASKS = (
    r"ability to travel",
    r"willing(?:ness)? to travel",
    r"travel commitment",
    r"expected to travel",
    r"requires? travel",
    r"travel required",
    r"prepared to travel",
    r"open to travel",
    # **`déplacements inter-sites sont probables` has a word in between**,
    # and the first version required them adjacent — it dropped a real French
    # requirement from the corpus while keeping all three English ones.
    r"d[ée]placements?\b[^.\n]{0,40}?\b(?:probables?|fr[ée]quents?|"
    r"r[ée]guliers?|occasionnels?|[àa]\s+pr[ée]voir|possibles?|"
    r"attendus?|n[ée]cessaires?)",
    r"disponibilit[ée]\s+(?:pour|[àa])\s+(?:des\s+)?d[ée]placements?",
    r"reisebereitschaft",
    r"dienstreisen?\s+(?:erforderlich|m[öo]glich)",
)

# Matched but *not* a requirement. Measured, not imagined: three of the
# eleven corpus hits were the first of these.
_NOT_A_REQUIREMENT = (
    r"travel\s*/\s*property", r"hospitality\s*/\s*travel",
    r"travel (?:industry|sector|domain|platform|tech)",
    r"travel expenses?", r"travel allowance", r"travel reimburse",
    r"frais de d[ée]placement", r"indemnit[ée] de d[ée]placement",
    r"prime mobilit[ée]",
)

# A degree, when the advertisement states one.
_DEGREE = (
    (r"(\d+\s*[-–—]\s*\d+|\d+)\s*(?:weeks?|semaines?|wochen)\s*"
     r"(?:per|a|/|par|pro)\s*(?:year|an|jahr)", "weeks-per-year"),
    (r"(\d+)\s*%\s*(?:of (?:the )?time|du temps)", "percent-of-time"),
    (r"limited basis|occasionnels?|gelegentlich", "limited"),
    (r"frequent|r[ée]guliers?|regelm[äa]ssig", "frequent"),
    (r"probables?|possibles?|m[öo]glich", "possible"),
)


def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", text or "")
            if s.strip()]


def requirement(text):
    """What this advertisement asks about travel, quoted.

    `{"asks": bool, "degree": str|None, "quotes": [str]}` — and a sentence
    that names an industry, a product or a benefit is not an ask.
    """
    out = {"asks": False, "degree": None, "quotes": []}
    for sent in _sentences(text):
        low = sent.lower()
        if any(re.search(p, low) for p in _NOT_A_REQUIREMENT):
            continue
        if not any(re.search(p, low) for p in _ASKS):
            continue
        out["asks"] = True
        out["quotes"].append(sent[:200])
        if out["degree"] is None:
            for pattern, name in _DEGREE:
                if re.search(pattern, low):
                    out["degree"] = name
                    break
    return out


def verdict(req, declared=None):
    """`{ask, blocker, status, text, quotes}` — **`blocker` is always False.**

    `declared` is what the user said they will do, from configuration: `None`
    when they have not said, otherwise a free string such as `"none"`,
    `"occasional"` or `"a few weeks a year"`. **It is deliberately not a
    boolean**: the advertisements ask for degrees, so a yes/no answer cannot
    meet them.
    """
    out = {"ask": False, "blocker": False, "status": "nothing-asked",
           "text": None, "quotes": req.get("quotes", [])}
    if not req.get("asks"):
        return out
    degree = req.get("degree")
    if declared is None:
        out.update(ask=True, status="asked-user-silent", text=(
            "This advertisement asks about business travel"
            + (f" and states a degree ({degree})" if degree else
               " without saying how much")
            + ". **Nothing in the workspace says what you will do**, so this "
              "is a question for the gate, not a reason to set the ad aside."))
        return out
    out.update(ask=True, status="asked-user-answered", text=(
        f"This advertisement asks about business travel"
        + (f" ({degree})" if degree else "")
        + f"; you have recorded {declared!r}. **Compare the two before "
          f"spending a dossier** — a degree is not met by a yes."))
    return out


def _main():
    """`--file <ad>` and an optional `--declared <phrase>`.

    **The doctrine in both `SKILL.md` files promises this invocation**, and it
    did not exist when that was written — the same defect this repository
    checks for in board cards, committed in the turn that documented it. The
    card guard reads `shared/boards/`, not a skill.
    """
    import argparse
    import json
    import sys

    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--file", required=True,
                   help="the advertisement's text, or - for stdin")
    p.add_argument("--declared",
                   help="what the user recorded in location.travel")
    p.add_argument("--json", action="store_true", dest="as_json")
    a = p.parse_args()

    text = (sys.stdin.read() if a.file == "-"
            else open(a.file, encoding="utf-8", errors="replace").read())
    req = requirement(text)
    v = verdict(req, a.declared)
    if a.as_json:
        print(json.dumps({**v, "degree": req["degree"]}, ensure_ascii=False))
        return 0
    if not v["ask"]:
        print("[travel] this advertisement asks nothing about business "
              "travel.", file=sys.stderr)
        return 0
    print(f"[travel] {v['text']}", file=sys.stderr)
    for q in v["quotes"]:
        print(f"  · {q}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
