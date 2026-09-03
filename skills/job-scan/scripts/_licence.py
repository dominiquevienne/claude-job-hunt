#!/usr/bin/env python3
"""Does this ad require a driving licence or a vehicle — and did anybody ever
ask the candidate?

**Issue #91, and it is #82 on a different field.** `shared/scoring-rubric.md`
knows how to treat a stated must-have; **nothing collected this one.** The rule
existed, the value did not.

THE CASE, 2026-09-03. A Meanquest `Chef de projet IT` ad lists, at the same
height as everything else:

    **Permis de conduire obligatoire**

Not "an asset", not "a plus" — in a list where ITIL *is* explicitly only a
plus. Searched `candidate.md`, `repos.md` and five profile PDFs: **nothing**.
Not the licence, not the category, not a vehicle. The run wrote *"to verify
before drafting"* into the ledger, which was the right reaction and **turns a
stable fact into a question re-asked at every ad**.

TWO FIELDS, NEVER ONE. *Permis B* is the legal capacity to drive; *"véhicule
personnel indispensable"* is having a car. Ads ask for one, the other, or both,
and a single boolean loses the distinction that decides field roles.

**ABSENT FROM THE FILE IS NOT NO.** A false *"they don't have it"* costs an ad
wrongly dropped; a false *"they have it"* costs an interview. Both are real and
they land in different places — so while the field is unset this produces a
**question at the go/no-go gate and never an automatic discard.** Three states,
not two: held, declared not held, never asked.

WHY THE DETECTION IS THE HARD HALF, MEASURED ON 45 ADS AND ONE WORKSPACE:

- **`permis` alone is worthless.** Of 13 `permis <word>` matches in one
  workspace: **7 driving licence, 5 work permit** — the #82 object, an entirely
  different field — **and 1 the ordinary French past participle** (*"seule la
  recherche a permis de conclure"*). Six of thirteen are not this.
- **`permis` is also a prefix of `permission`.** A stem match hits *"gestion
  des permissions"* in a backend ad about file sharing.
- **`permis B` is the Swiss residence permit**, not driving category B, and on
  a Swiss board that is the commoner reading by far. So a bare category letter
  is **never** read as a licence here: it raises a question instead.
- **Bare `vehicle` is a false friend in this repository's own vocabulary.**
  *"The employment vehicle"* — B2B versus local employment — appears in **5 of
  45 ad files and 0 of them is a car.**

**So the matcher is an allow-list of phrases, never a stem**, for the same
reason `vieclam24h.py` emits an allow-list: the narrow version fails visibly
and the broad version fails silently.

AND RUN IT ON THE AD, NOT ON THE FILE. All five `vehicle` false positives were
in the plugin's own analysis prose, not in the employer's words. A corpus that
mixes the ad with what we wrote about it cannot validate a detector.

    from _licence import requirement, verdict
    r = requirement(ad_text)
    v = verdict(r, cfg["location"].get("driving_licence"),
                cfg["location"].get("own_vehicle"))
    if v["ask"]:
        note(v["text"])
"""

import re

__all__ = ["requirement", "verdict"]

# **An allow-list of phrases.** Each is a form somebody actually writes for a
# driving licence. Nothing here matches a bare `permis`, a bare category
# letter, or the stem of `permission`.
LICENCE = (
    r"permis\s+de\s+conduire",
    r"permis\s+de\s+conduite",
    r"driv(?:er'?s|ing)\s+licen[cs]e",
    r"driver\s+licen[cs]e",
    r"f[üu]hrerschein",
    r"fahrausweis",                     # the Swiss German form
    r"fahrerlaubnis",
    r"patente\s+di\s+guida",
    r"carnet\s+de\s+conducir",
    r"permiso\s+de\s+conducir",
    r"carta\s+de\s+condu[çc][ãa]o",
    r"rijbewijs",
    r"k[oö]rkort",
)

# A car, not a metaphor. `vehicle` on its own is excluded on measurement:
# 5 of 45 ad files carry "employment vehicle" and none of them is a car.
VEHICLE = (
    r"v[ée]hicule\s+(?:personnel|priv[ée]|de\s+fonction|propre)",
    r"v[ée]hicule\s+(?:indispensable|obligatoire|requis|exig[ée])",
    r"propre\s+v[ée]hicule",
    r"own\s+(?:car|vehicle|transport)",
    r"personal\s+(?:car|vehicle)",
    r"eigene[sn]?\s+(?:fahrzeug|auto)",
    r"eigener\s+pkw",
    r"mezzo\s+proprio",
    r"veh[íi]culo\s+propio",
)

# The ambiguous forms: a category letter with no verb. In Switzerland `permis
# B` is a residence permit and `permis C` a settlement permit, so this is NOT
# resolved by pattern — it becomes a question.
AMBIGUOUS = (
    r"permis\s+[A-F]\d?\b(?!\w)",
    r"cat[ée]gorie\s+[A-F]\d?\b(?!\w)",
)

MANDATORY = (
    r"obligatoire", r"exig[ée]e?s?\b", r"requis(?:e|es)?\b", r"indispensable",
    r"imp[ée]ratif", r"n[ée]cessaire", r"must\b", r"required\b",
    r"mandatory", r"essential", r"erforderlich", r"vorausgesetzt",
    r"zwingend", r"obbligatori[oa]", r"imprescindible",
)

OPTIONAL = (
    r"un\s+atout", r"un\s+plus", r"souhait[ée]e?\b", r"appr[ée]ci[ée]e?\b",
    r"de\s+pr[ée]f[ée]rence", r"id[ée]alement",
    r"an\s+asset", r"a\s+plus\b", r"preferred", r"nice\s+to\s+have",
    r"desirable", r"von\s+vorteil", r"w[üu]nschenswert", r"gradito",
    r"valorado",
)

NEGATED = (
    r"non\s+requis", r"pas\s+(?:de\s+)?(?:permis|besoin)",
    r"not\s+required", r"no\s+(?:driv\w+\s+)?licen[cs]e\s+(?:is\s+)?required",
    r"nicht\s+erforderlich",
)

# How far from the phrase we look for the qualifier. One clause, not one page:
# a wider window picks up the next bullet's "obligatoire" and calls a nice-to-
# have a must-have.
WINDOW = 90


def _find(text, patterns):
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m
    return None


def _strength(text, at):
    """mandatory / optional / unqualified, read in the phrase's own clause."""
    lo = max(0, at.start() - WINDOW)
    near = text[lo:at.end() + WINDOW]
    if _find(near, NEGATED):
        return "negated"
    m_req, m_opt = _find(near, MANDATORY), _find(near, OPTIONAL)
    if m_req and m_opt:
        # Both words in one clause: say so rather than picking. Guessing here
        # is the failure this file exists to avoid.
        return "conflicting"
    if m_req:
        return "mandatory"
    if m_opt:
        return "optional"
    return "unqualified"


def requirement(text):
    """What the ad asks for. Never an opinion about the candidate."""
    t = text or ""
    out = {"licence": None, "vehicle": None, "ambiguous": [], "quotes": {}}

    m = _find(t, LICENCE)
    if m:
        out["licence"] = _strength(t, m)
        out["quotes"]["licence"] = _quote(t, m)
    m = _find(t, VEHICLE)
    if m:
        out["vehicle"] = _strength(t, m)
        out["quotes"]["vehicle"] = _quote(t, m)
    for p in AMBIGUOUS:
        for m in re.finditer(p, t, re.I):
            out["ambiguous"].append(_quote(t, m))
    return out


def _quote(t, m):
    lo, hi = max(0, m.start() - 60), min(len(t), m.end() + 60)
    return re.sub(r"\s+", " ", t[lo:hi]).strip()


def verdict(req, licence_held=None, vehicle_held=None):
    """What to say, given what the ad asks and what the user declared.

    `licence_held` is `location.driving_licence` — a list of categories, `[]`
    for *declared none*, and **`None` when the key is absent**, which is not
    the same thing. `vehicle_held` is `location.own_vehicle`: `True`, `False`,
    or `None` for never asked.

    Returns `ask` (put a question at the gate), `blocker` (the ad states it as
    a must-have and the user declared they do not have it) and a `text` for the
    user. **`blocker` never means discard** — it means say it before a dossier
    is spent.
    """
    out = {"ask": False, "blocker": False, "status": "nothing-asked",
           "text": None, "quotes": req.get("quotes", {})}

    lic, veh = req.get("licence"), req.get("vehicle")
    wanted = [k for k, v in (("licence", lic), ("vehicle", veh))
              if v in ("mandatory", "unqualified", "conflicting")]
    softly = [k for k, v in (("licence", lic), ("vehicle", veh))
              if v == "optional"]

    if req.get("ambiguous") and not lic:
        # `permis B` with no verb. In Switzerland that is the residence
        # permit far more often than driving category B — so this asks, and
        # under no circumstances asserts.
        out.update(ask=True, status="ambiguous", text=(
            "The ad names a permit by letter and nothing says which permit. "
            "**In Switzerland `permis B` is a residence permit, not driving "
            "category B**, and the two are different fields — read the "
            "sentence before treating it as either: "
            + " · ".join(req["ambiguous"][:2])))
        return out

    if not wanted and not softly:
        return out                       # the ad asks for neither: silence

    held = {
        "licence": None if licence_held is None else bool(licence_held),
        "vehicle": None if vehicle_held is None else bool(vehicle_held),
    }
    unknown = [k for k in wanted if held[k] is None]
    missing = [k for k in wanted if held[k] is False]

    label = {"licence": "a driving licence", "vehicle": "a personal vehicle"}
    quoted = " · ".join(req["quotes"].get(k, "") for k in wanted if
                        req["quotes"].get(k))

    if missing:
        out.update(ask=True, blocker=True, status="declared-absent", text=(
            f"**The ad states {' and '.join(label[k] for k in missing)} as a "
            f"requirement, and you have declared you do not have "
            f"{'them' if len(missing) > 1 else 'it'}.** That is a stated "
            f"must-have, and unlike the right to work it has no second route: "
            f"a licence required is a licence required. **The ad is not "
            f"removed** — the score still says whether it was worth wanting — "
            f"but this belongs at the gate before a dossier is spent. "
            f"Quoted: {quoted}"))
        return out

    if unknown:
        out.update(ask=True, status="never-asked", text=(
            f"**The ad asks for {' and '.join(label[k] for k in unknown)} and "
            f"nothing in your workspace answers.** Absent from the file is "
            f"not a no, so this is a question and not a discard — and it is a "
            f"stable fact worth recording once rather than re-asking at every "
            f"ad: `location.driving_licence` and `location.own_vehicle` in "
            f"`config.yml`. Quoted: {quoted}"))
        return out

    if softly:
        # Mentioned as a plus. Silent either way — but do not call it
        # *satisfied* when the user declared they do not have it: a status
        # that overstates is the same defect as a score that overstates.
        out["status"] = ("optional-unknown"
                         if any(held[k] is None for k in softly)
                         else "optional-held" if all(held[k] for k in softly)
                         else "optional-not-held")
        return out

    out["status"] = "satisfied"
    return out


def _main():
    import argparse
    import json
    import sys
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", help="the AD's own text — not the analysis")
    p.add_argument("--text", default="")
    p.add_argument("--licence", default=None,
                   help="config location.driving_licence, comma separated. "
                        "Omit for 'never asked'; pass '' for 'declared none'")
    p.add_argument("--vehicle", default=None,
                   choices=["yes", "no"],
                   help="config location.own_vehicle. Omit for 'never asked'")
    a = p.parse_args()
    text = open(a.file, encoding="utf-8", errors="replace").read() \
        if a.file else a.text
    lic = None if a.licence is None else [
        x.strip() for x in a.licence.split(",") if x.strip()]
    veh = None if a.vehicle is None else (a.vehicle == "yes")
    r = requirement(text)
    v = verdict(r, lic, veh)
    print(json.dumps({"requirement": r, "verdict": v}, ensure_ascii=False,
                     indent=2))
    return 0 if not v["blocker"] else 0     # never an error: it is a question


if __name__ == "__main__":
    raise SystemExit(_main())
