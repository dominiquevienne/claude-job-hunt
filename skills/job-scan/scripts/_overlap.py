#!/usr/bin/env python3
"""Do two boards carry the same advertisements under two country names?

  _overlap.py --a liberia.txt --b sierraleone.txt
  _overlap.py --a liberia.txt --b sierraleone.txt --json

Two files of job titles, one per line. Returns a recovery rate **and the two
controls that say whether the rate means anything**, computed in the same draw.

WHY THIS IS A SCRIPT AND NOT A PARAGRAPH

On 2026-09-03 and 04 this comparison, run by hand across sessions, found a
network of thirty-one African hosts publishing one another's advertisements
under thirty-one country names. **Nothing in the shape of those sites betrays
them** — clean sitemaps, plausible dates, real cities, credible titles,
hundreds of advertisements each. Only the comparison between countries does.

It lived in messages. An adapter written for any one of them would serve
fabricated advertisements to a candidate, and the check that would have caught
it was not something the repository could run.

THREE THINGS IT DOES BECAUSE THE MANUAL RUNS GOT THEM WRONG

**1. The comparison key never contains a country name.** A key that carries the
country returns 0.0 % on every pair — a perfectly clean negative that is
entirely false, because the one token guaranteed to differ is doing all the
work. `_PLACES` is stripped before anything is compared, and
`--show-key` prints what survived so the exclusion can be audited rather than
trusted.

**Cities are a different matter and the module does not pretend otherwise.**
Countries are enumerable; the cities of the world are not. `mombasa` survives
into the key, and a test says so on purpose — a promise of completeness that
cannot be kept is worse than a stated limit.

**2. The controls are in the draw, never upstream.** Every run computes:

  - a **positive control**: A against a corpus that has copied half of A
    verbatim. It must find roughly that half. **If it does not, the instrument
    is broken and the run says so instead of reporting a rate.**

    The first version compared two halves of A with each other and returned
    0.0 % — correctly, since two halves hold different advertisements. **A
    control that cannot come out high on a corpus that is copying is not a
    control**, and running it was what showed that; no amount of re-reading
    would have.
  - a **negative control**: A against a corpus built by reshuffling its own
    words. Same vocabulary, no shared advertisements, so it must come out low.

  It was a positive control that refuted this method the first time, not a
  re-reading. A control run beforehand and remembered is not a control.

**3. It reports the composition, not only the quotient.** `shared: 41 of 240`
survives being quoted; `17 %` does not, because the number a reader needs to
check it has already been divided away.

WHAT IT MEASURED WHEN IT WAS FIRST RUN, AND IT IS WEAKER THAN THE METHOD CLAIMED

Measured 2026-09-05 on real corpora — three nodes of the network (452, 346 and
488 advertisements), one Chadian board (25) and one Fijian board (217):

    pair                                   exact keys   vocabulary
    network × network                      0.0–1.2 %      53–61 %
    network × Fiji      (English, apart)       0.9 %        35.4 %
    network × Chad      (French, apart)        0.0 %        20.3 %

**The exact-key rate separates nothing.** Two nodes of one network that publish
each other's advertisements score the same as two boards on different
continents. Whatever the manual runs compared, it was not this.

**The vocabulary rate does separate — and it is badly confounded by language.**
The gap that matters is 35 % against 53 %, not 20 % against 60 %: most of the
apparent signal in the first comparison was English against French. **A
same-language control is not optional here; without one the number measures a
dictionary.**

So this ships as an instrument that reports two rates with their controls and
**claims no threshold**. The 17 % figure that circulated in messages does not
reproduce under either statistic, and is not repeated here.

WHAT IT DOES NOT DO

**It does not decide that a board is fabricated.** It returns a rate with its
denominators and its controls; the conclusion is a human's, on evidence that
includes the rate and never rests on it alone. Two boards of one honest
operator can share advertisements openly, and a franchise is not a fraud.

**And it says nothing about corpora that label in different languages.**
Measured in Armenia on 2026-09-04: three boards writing in transliterated
Armenian, in English and in percent-encoded Armenian returned 0.3 %, which
does not separate *independent* from *written differently*. `verdict()` reports
`out-of-domain` when the two corpora share almost no vocabulary at all — the
state that has every appearance of a result and is not one.
"""

import argparse
import json
import random
import re
import sys
import unicodedata

# Place names are stripped before comparison. **The list is not the point** —
# the point is that a key containing the country decides the answer by itself.
# `--show-key` exists so this exclusion is auditable rather than believed.
_PLACES = {
    "afrique", "africa", "african", "algerie", "algeria", "angola", "benin",
    "botswana", "burkina", "burundi", "cameroun", "cameroon", "congo", "coast",
    "cote", "djibouti", "egypt", "egypte", "eritrea", "erythree", "eswatini",
    "ethiopia", "ethiopie", "gabon", "gambia", "gambie", "ghana", "guinea",
    "guinee", "ivoire", "kenya", "lesotho", "liberia", "libya", "libye",
    "madagascar", "malawi", "mali", "maroc", "mauritania", "mauritanie",
    "mauritius", "maurice", "morocco", "mozambique", "namibia", "namibie",
    "niger", "nigeria", "rwanda", "senegal", "seychelles", "sierra", "leone",
    "somalia", "somalie", "somaliland", "sudan", "soudan", "swaziland",
    "tanzania", "tanzanie", "tchad", "chad", "togo", "tunisia", "tunisie",
    "uganda", "ouganda", "zambia", "zambie", "zimbabwe",
    # capitals and large cities seen in this corpus
    "abuja", "accra", "addis", "abeba", "alger", "asmara", "bamako", "bangui",
    "banjul", "bissau", "brazzaville", "bujumbura", "cairo", "caire", "conakry",
    "dakar", "dar", "salaam", "djamena", "douala", "freetown", "gaborone",
    "harare", "johannesburg", "kampala", "khartoum", "kigali", "kinshasa",
    "lagos", "libreville", "lilongwe", "lome", "luanda", "lusaka", "malabo",
    "maputo", "maseru", "mbabane", "mogadishu", "monrovia", "nairobi",
    "niamey", "nouakchott", "ouagadougou", "porto", "novo", "pretoria",
    "rabat", "tripoli", "tunis", "windhoek", "yaounde", "juba", "praia",
}

# Words that carry no information about which advertisement this is.
_NOISE = {
    "a", "an", "and", "at", "de", "des", "du", "el", "en", "et", "for", "in",
    "la", "le", "les", "of", "on", "or", "the", "to", "un", "une", "with",
    "job", "jobs", "emploi", "emplois", "poste", "postes", "vacancy",
    "vacancies", "offre", "offres", "recrutement", "recruitment", "hiring",
}

_WORD = re.compile(r"[a-z0-9]+")


def fold(s):
    """Lowercase, strip accents. `Abéché` and `Abeche` are one token."""
    n = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in n if not unicodedata.combining(c))


def key(label):
    """The comparable form of one label: a frozenset of informative words.

    **Place names are removed here and nowhere else**, so there is exactly one
    place to audit and exactly one place to get it wrong.
    """
    words = {w for w in _WORD.findall(fold(label)) if len(w) > 2}
    return frozenset(words - _PLACES - _NOISE)


def keys_of(labels):
    out = []
    for l in labels:
        k = key(l)
        if k:
            out.append(k)
    return out


def rate(a, b):
    """Share of the smaller corpus whose key also appears in the other.

    **The smaller corpus is the denominator on purpose.** Against a corpus a
    hundred times larger, a Jaccard index is small whatever the truth, and a
    board that copies everything from a big neighbour would read as
    independent.
    """
    if not a or not b:
        return {"shared": 0, "of": 0, "rate": None,
                "why": "one corpus is empty after keying"}
    sa, sb = set(a), set(b)
    small, big = (sa, sb) if len(sa) <= len(sb) else (sb, sa)
    shared = len(small & big)
    return {"shared": shared, "of": len(small),
            "rate": round(100.0 * shared / len(small), 1)}


def _shuffled(keys, rng):
    """A corpus with the same vocabulary and no shared advertisements."""
    pool = [w for k in keys for w in k]
    rng.shuffle(pool)
    out, i = [], 0
    for k in keys:
        out.append(frozenset(pool[i:i + len(k)]))
        i += len(k)
    return out


def verdict(a_labels, b_labels, seed=7):
    """The rate, and the two controls that say whether it means anything."""
    rng = random.Random(seed)
    a, b = keys_of(a_labels), keys_of(b_labels)
    observed = rate(a, b)

    # **The positive control must simulate the phenomenon, not the source.**
    # The first version split A in two halves and compared them — and returned
    # 0.0 %, correctly: two halves of one corpus hold *different*
    # advertisements, and this sieve compares advertisements, not styles. A
    # control that cannot come out high on a corpus that is copying is not a
    # control, and it refused every run in the same breath as it refuted
    # itself.
    #
    # So the control is a corpus that *has copied*: half of A's own entries,
    # verbatim, mixed with half drawn from A's reshuffled vocabulary. The sieve
    # must find roughly the copied half.
    half = len(a) // 2
    if half >= 5:
        planted = a[:half] + _shuffled(a[half:], rng)
        positive = rate(a, planted)
    else:
        positive = {"shared": 0, "of": 0, "rate": None,
                    "why": f"corpus A has {len(a)} usable labels, too few "
                           f"to plant a control in"}
    negative = rate(a, _shuffled(a, rng))

    out = {"observed": observed, "control_positive": positive,
           "control_negative": negative,
           "a_labels": len(a_labels), "a_usable": len(a),
           "b_labels": len(b_labels), "b_usable": len(b)}

    # **The instrument's own scope, checked in the same run.**
    vocab_a = {w for k in a for w in k}
    vocab_b = {w for k in b for w in k}
    shared_vocab = len(vocab_a & vocab_b)
    smaller = min(len(vocab_a), len(vocab_b)) or 1
    out["shared_vocabulary"] = round(100.0 * shared_vocab / smaller, 1)

    if positive["rate"] is None:
        out["state"] = "out-of-domain"
        out["reason"] = (f"the positive control could not run: "
                         f"{positive.get('why')}. **A rate without a control "
                         f"that could have failed is not a measurement.**")
    elif positive["rate"] < 20.0:
        out["state"] = "out-of-domain"
        out["reason"] = (
            f"the positive control returned {positive['rate']} % — A against "
            f"a corpus that copied half of A verbatim. **The instrument cannot "
            f"see copying it planted itself**, so it cannot see real copying, "
            f"and the observed {observed['rate']} % says nothing. "
            f"Titles here may be too varied, too short, or in more "
            f"than one language.")
    elif out["shared_vocabulary"] < 5.0:
        out["state"] = "out-of-domain"
        out["reason"] = (
            f"the two corpora share {out['shared_vocabulary']} % of their "
            f"vocabulary. **This does not separate *independent* from "
            f"*written in different languages*** — measured in Armenia on "
            f"2026-09-04, where three boards label in transliterated Armenian, "
            f"English and percent-encoded Armenian.")
    else:
        out["state"] = "measured"
        out["reason"] = (
            f"positive control {positive['rate']} %, negative control "
            f"{negative['rate']} %, observed {observed['rate']} % "
            f"({observed['shared']} of {observed['of']}). "
            f"**The conclusion is yours**: this is a rate with its controls, "
            f"not a verdict about a board.")
    return out


def _read(path):
    if path == "-":
        return [l.strip() for l in sys.stdin if l.strip()]
    with open(path, encoding="utf-8") as fh:
        return [l.strip() for l in fh if l.strip()]


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--a", required=True, help="labels, one per line, or -")
    p.add_argument("--b", required=True)
    p.add_argument("--seed", type=int, default=7,
                   help="the negative control's shuffle; recorded in the output")
    p.add_argument("--show-key", action="store_true",
                   help="print the first keys, to audit what the place-name "
                        "exclusion left behind")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    la, lb = _read(a.a), _read(a.b)
    if a.show_key:
        for l in la[:8]:
            print(f"  {l[:52]:54s} → {sorted(key(l))}", file=sys.stderr)
    v = verdict(la, lb, seed=a.seed)
    v["seed"] = a.seed
    if a.json:
        print(json.dumps(v, ensure_ascii=False, indent=1))
        return
    o, cp, cn = v["observed"], v["control_positive"], v["control_negative"]
    print(f"state              {v['state']}")
    print(f"observed           {o['shared']} of {o['of']}"
          f"   ({o['rate']} %)")
    print(f"control positive   {cp['shared']} of {cp['of']}"
          f"   ({cp['rate']} %)   A against a corpus that copied half of A"
          f" — must be high")
    print(f"control negative   {cn['shared']} of {cn['of']}"
          f"   ({cn['rate']} %)   A against its own words reshuffled — must be low")
    print(f"shared vocabulary  {v['shared_vocabulary']} %"
          f"   — the discriminating one, and language-confounded:"
          f" compare only same-language corpora")
    print(f"\n{v['reason']}")


if __name__ == "__main__":
    main()
