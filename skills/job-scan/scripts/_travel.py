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
    # **A travel word next to a stated amount is a requirement** — issue #207:
    # *"You will travel two weeks per year"* was not even seen as a question,
    # because every phrasing above is a verb of willingness and this one is a
    # plain statement. The amount is what makes it an ask and not the
    # industry: *"travel allowance CHF 500 per month"* is caught earlier by
    # `_NOT_A_REQUIREMENT`, and *"international travel: confirmed available"*
    # — the plugin's own prose — carries no quantity.
    r"(?:will|may|must|should|have to|need to|required to|able to)\s+travel",
    r"(?:occasional|regular|frequent|extensive|some|light|moderate|minimal)"
    r"\s+travel",
    r"travel(?:l?ing)?\b[^.\n]{0,25}?\b(?:QTY)",
    r"(?:QTY)\s+(?:of\s+)?(?:business\s+|international\s+|domestic\s+)?"
    r"travel",
    r"d[ée]placements?\b[^.\n]{0,40}?\b(?:QTY)",
    r"(?:QTY)[^.\n]{0,20}?\bd[ée]placements?",
    r"(?:dienst)?reisen?\b[^.\n]{0,40}?\b(?:QTY)",
    r"reiset[äa]tigkeit",
    r"(?:QTY)[^.\n]{0,20}?\b(?:dienst)?reisen\b",
)

# Matched but *not* a requirement. Measured, not imagined: three of the
# eleven corpus hits were the first of these.
_NOT_A_REQUIREMENT = (
    r"travel\s*/\s*property", r"hospitality\s*/\s*travel",
    r"travel (?:industry|sector|domain|platform|tech)",
    r"travel expenses?", r"travel allowance", r"travel reimburse",
    r"frais de d[ée]placement", r"indemnit[ée] de d[ée]placement",
    r"prime mobilit[ée]",
    r"reisekosten", r"reisebranche", r"reiseindustrie",
)

# ---------------------------------------------------------------------------
# A quantity, in digits OR in words — issue #207.
#
# The first version required `\d+` and the adjacency `weeks per year`, so
# *"twice a year, for company events for up to two weeks each"* was read as
# *"without saying how much"*. **A number written in letters is invisible to
# a pattern that looks for digits** — the same defect that hid six dead Atlas
# counters spelled *"cent quatre-vingt-quatre"* from `grep '\b18[0-9]\b'`.
# ---------------------------------------------------------------------------

_WORDS = {
    # English
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "a": 1, "an": 1, "a couple of": 2, "couple of": 2,
    # French
    "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5,
    "sept": 7, "huit": 8, "neuf": 9, "dix": 10, "onze": 11, "douze": 12,
    # German
    "ein": 1, "eine": 1, "einen": 1, "einer": 1, "zwei": 2, "drei": 3,
    "vier": 4, "fünf": 5, "fuenf": 5, "sechs": 6, "sieben": 7, "acht": 8,
    "zehn": 10, "elf": 11, "zwölf": 12, "zwoelf": 12,
}
_FREQ_WORDS = {
    "once": 1, "twice": 2, "thrice": 3,
    "einmal": 1, "zweimal": 2, "dreimal": 3, "viermal": 4,
}
_VAGUE = ("a few", "several", "quelques", "plusieurs", "einige", "mehrere")

_NUM = (r"(?P<num>\d+(?:[.,]\d+)?(?:\s*[-–—]\s*\d+(?:[.,]\d+)?)?|"
        + "|".join(sorted(map(re.escape, list(_WORDS) + list(_VAGUE)),
                          key=len, reverse=True)) + r")")
_FREQ = (r"(?P<freq>" + "|".join(_FREQ_WORDS) + r"|"
         r"(?:\d+|" + "|".join(k for k in _WORDS if " " not in k) + r")"
         r"\s*(?:times|fois|x|×|-?mal|\s+mal))")
_UNIT = (r"(?P<unit>weeks?|semaines?|wochen?|fortnights?|quinzaines?|"
         r"days?|jours?|tage?n?|months?|mois|monate?n?)")
_PERIOD = (r"(?:per|a|an|/|par|pro|im|je)\s*(?P<period>year|yr|annum|an|"
           r"ann[ée]e|jahr|month|mois|monat|quarter|trimestre|quartal)"
           r"|(?P<period_adv>yearly|annually|monthly|quarterly|j[äa]hrlich|"
           r"monatlich|quartalsweise|par an|par mois)")
_QUAL = (r"(?:(?P<qual>up to|jusqu'[àa]|bis zu|max(?:imum|\.)?|approx"
         r"(?:imately|\.)?|about|around|roughly|environ|ca\.?|etwa|"
         r"rund)\s+)?")

_UNIT_WEEKS = {"week": 1, "semaine": 1, "woche": 1, "fortnight": 2,
               "quinzaine": 2, "day": 1 / 5, "jour": 1 / 5, "tag": 1 / 5,
               "month": 4, "mois": 4, "monat": 4}
_PERIOD_PER_YEAR = {"year": 1, "yr": 1, "annum": 1, "an": 1, "année": 1,
                    "annee": 1, "jahr": 1, "yearly": 1, "annually": 1,
                    "jährlich": 1, "jahrlich": 1, "par an": 1,
                    "month": 12, "mois": 12, "monat": 12, "monthly": 12,
                    "monatlich": 12, "par mois": 12,
                    "quarter": 4, "trimestre": 4, "quartal": 4,
                    "quarterly": 4, "quartalsweise": 4}

# `QTY` inside `_ASKS` is expanded here: anything that reads as an amount.
_QTY = (r"(?:\d+(?:[.,]\d+)?\s*%|" + _NUM[len("(?P<num>"):-1] +
        r")\s*(?:%|" + _UNIT[len("(?P<unit>"):-1] + r"|"
        + _FREQ[len("(?P<freq>"):-1] + r")|" + _FREQ[len("(?P<freq>"):-1])
_ASKS = tuple(p.replace("QTY", _QTY) for p in _ASKS)

_RE_UNIT_PER_PERIOD = re.compile(
    _QUAL + _NUM + r"\s*" + _UNIT + r"\s*(?:(?:of|de|d')\s*(?:business\s+)?"
    r"(?:travel|d[ée]placements?|reisen)\s*)?(?:" + _PERIOD + ")")
_RE_FREQ_PER_PERIOD = re.compile(_QUAL + _FREQ + r"\s*(?:" + _PERIOD + ")")
_RE_UNIT_EACH = re.compile(
    _QUAL + _NUM + r"\s*" + _UNIT + r"\s*(?:each|at a time|chacun[e]?s?|"
    r"[àa] chaque fois|jeweils|pro reise|per trip)")
_RE_PERCENT = re.compile(
    _QUAL + r"(?P<num>\d+(?:[.,]\d+)?(?:\s*[-–—]\s*\d+)?)\s*(?:%|percent|"
    r"pour ?cent|prozent)(?:\s*(?:of (?:the |your )?time|du temps|der zeit|"
    r"travel|reiset[äa]tigkeit|d[ée]placements?))?")


def _number(word):
    """`"3-4"` → `(3, 4)`, `"twice"` → `(2, 2)`, `"a few"` → `None`."""
    word = re.sub(r"\s+", " ", word.strip().lower())
    if word in _VAGUE:
        return None
    if word in _FREQ_WORDS:
        return (_FREQ_WORDS[word], _FREQ_WORDS[word])
    if word in _WORDS:
        return (_WORDS[word], _WORDS[word])
    m = re.match(r"(\d+(?:[.,]\d+)?)(?:\s*[-–—]\s*(\d+(?:[.,]\d+)?))?$", word)
    if m:
        lo = float(m.group(1).replace(",", "."))
        hi = float(m.group(2).replace(",", ".")) if m.group(2) else lo
        return (lo, hi)
    m = re.match(r"(\d+|\w+)\s*(?:times|fois|x|×|-?mal|\s+mal)$", word)
    if m:
        return _number(m.group(1))
    return None


def _fmt(lo, hi):
    f = lambda v: str(int(v)) if float(v).is_integer() else f"{v:.1f}"
    return f(lo) if lo == hi else f"{f(lo)}–{f(hi)}"


def _weeks_per_year(n, unit, period):
    """`(lo, hi)` of weeks a year, or `None` when it cannot be computed."""
    if n is None:
        return None
    # by prefix, never by stripping a suffix: `(?:s|n|en)$` turned `wochen`
    # into `woch` because `en` matches one character earlier than `n`
    u = next((v for k, v in sorted(_UNIT_WEEKS.items(), key=lambda kv: -len(kv[0]))
              if unit.lower().startswith(k)), None)
    k = _PERIOD_PER_YEAR.get((period or "year").lower())
    if u is None or k is None:
        return None
    return (n[0] * u * k, n[1] * u * k)


def quantity(low):
    """`(degree, amount)` for a sentence that states how much travel, else
    `None`. `amount` is a normalised string — *"4 weeks/year"*,
    *"up to 3–4 weeks/year"*, *"20% of time"* — or `None` when the words are
    vague (*"a few weeks a year"*) but a degree is still stated.

    **`"twice a year … two weeks each"` is a product**, 2 × 2 = 4, and the
    two halves may be twenty words apart: the frequency and the duration are
    matched independently in the same sentence, never as one expression.
    """
    m = _RE_PERCENT.search(low)
    if m:
        n = _number(m.group("num"))
        qual = (m.group("qual") + " ") if m.group("qual") else ""
        return ("percent-of-time",
                f"{qual}{_fmt(*n)}% of time" if n else None)
    m = _RE_UNIT_PER_PERIOD.search(low)
    if m:
        n = _number(m.group("num"))
        period = m.group("period") or m.group("period_adv")
        w = _weeks_per_year(n, m.group("unit"), period)
        qual = (m.group("qual") + " ") if m.group("qual") else ""
        return ("weeks-per-year", f"{qual}{_fmt(*w)} weeks/year" if w else None)
    f = _RE_FREQ_PER_PERIOD.search(low)
    if f:
        times = _number(f.group("freq"))
        period = f.group("period") or f.group("period_adv")
        k = _PERIOD_PER_YEAR.get((period or "year").lower())
        e = _RE_UNIT_EACH.search(low)
        if e and times and k:
            n = _number(e.group("num"))
            w = _weeks_per_year(n, e.group("unit"), None)
            qual = (e.group("qual") or f.group("qual") or "")
            qual = qual + " " if qual else ""
            if w:
                return ("weeks-per-year",
                        f"{qual}{_fmt(w[0] * times[0] * k, w[1] * times[1] * k)}"
                        f" weeks/year ({_fmt(*times)} × {_fmt(*n)} "
                        f"{e.group('unit')} per {period or 'year'})")
        if times and k:
            qual = (f.group("qual") + " ") if f.group("qual") else ""
            return ("times-per-year",
                    f"{qual}{_fmt(times[0] * k, times[1] * k)} times/year")
        return ("times-per-year", None)
    return None


# A degree, when the advertisement states one and `quantity()` found no
# amount: the vague words, measured in the corpus.
_DEGREE = (
    (r"limited basis|occasionnels?|gelegentlich|occasional", "limited"),
    (r"frequent|r[ée]guliers?|regelm[äa]ssig|regular", "frequent"),
    (r"probables?|possibles?|m[öo]glich", "possible"),
)


def _quote(sent, low):
    """The 200 characters that carry the ask **and** the amount — never the
    head of the sentence. Issue #207: a bullet list flattened onto one line
    is one "sentence", and `sent[:200]` quoted *"Debug and fix issues…"* for
    an ask that sat 300 characters further on."""
    if len(sent) <= 200:
        return sent
    spans = [m.span() for p in _ASKS for m in [re.search(p, low)] if m]
    for rx in (_RE_PERCENT, _RE_UNIT_PER_PERIOD, _RE_FREQ_PER_PERIOD,
               _RE_UNIT_EACH):
        m = rx.search(low)
        if m:
            spans.append(m.span())
    if not spans:
        return sent[:200]
    lo = min(s for s, _e in spans)
    hi = max(e for _s, e in spans)
    if hi - lo > 190:
        hi = lo + 190
    start = max(0, lo - max(10, (200 - (hi - lo)) // 2))
    start = min(start, max(0, len(sent) - 200))
    piece = sent[start:start + 200]
    return ("…" if start else "") + piece + ("…" if start + 200 < len(sent)
                                             else "")


def _sentences(text):
    # a bullet list flattened onto one line — ` - Debug … - Mentor … ` — is
    # split at its markers, so each item is judged and quoted on its own
    # and `ca. 2x pro Jahr` is not two sentences: the abbreviations that
    # precede an amount do not end one
    return [s.strip() for s in re.split(
        r"(?<!\bca\.)(?<!\benv\.)(?<!\bmax\.)(?<!approx\.)(?<!\bmin\.)"
        r"(?<=[.!?])\s+|\n|\s+[-–—•·▪]\s+(?=[A-ZÀ-Ý])", text or "")
            if s.strip()]


def requirement(text):
    """What this advertisement asks about travel, quoted.

    `{"asks": bool, "degree": str|None, "amount": str|None, "quotes": [str]}`
    — and a sentence that names an industry, a product or a benefit is not an
    ask. `amount` is the stated quantity normalised (*"4 weeks/year"*), in
    digits whatever the advertisement wrote; #207.
    """
    out = {"asks": False, "degree": None, "amount": None, "quotes": []}
    for sent in _sentences(text):
        low = sent.lower()
        if any(re.search(p, low) for p in _NOT_A_REQUIREMENT):
            continue
        if not any(re.search(p, low) for p in _ASKS):
            continue
        out["asks"] = True
        out["quotes"].append(_quote(sent, low))
        if out["degree"] is None or out["amount"] is None:
            q = quantity(low)
            if q:
                out["degree"], out["amount"] = q
                continue
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
    if degree and req.get("amount"):
        degree = f"{degree}, {req['amount']}"
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
        print(json.dumps({**v, "degree": req["degree"],
                          "amount": req["amount"]}, ensure_ascii=False))
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
