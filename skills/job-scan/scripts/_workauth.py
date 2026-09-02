#!/usr/bin/env python3
"""May this person be employed in that country — and if not, is the other route
still open?

**Issue #82.** `shared/scoring-rubric.md` has listed *"Work authorization the
candidate lacks"* among the zeros that cap a score since long before this file.
**Nothing ever asked the user for it.** The rule existed; the input did not.

WHAT IT COST, MEASURED 2026-09-02. `linkedin:4460638365` — Software Engineer
(PHP), London — scored **74% in depth, the best stack match in the whole
ledger**. A complete dossier was produced: CV, letter, rendered PDFs, page
count verified. The user closed it in one sentence: *"pas éligible pour le
poste (permis de travail UK)"*. It never went out, and the next `todo` row was
another foreign post.

**THIS IS NOT A DISCARD, AND THAT IS THE WHOLE DESIGN.** The rubric drops an
out-of-range commute *before scoring*, for a good reason: a body cannot be in
two places. **The right to work has a different shape** — being employed in
London and invoicing London from Switzerland are two different legal objects,
and the second stays open without any permit. An implementation that silently
dropped these ads would destroy real opportunities and do it invisibly, which
is the failure `shared/never-fail-silently.md` exists to prevent.

**So the verdict is never a flat no.** It is *local employment excluded,
service provision perhaps open* — and the score is still computed and still
shown, because the score is what tells somebody the job was worth wanting.

TWO THINGS THIS DELIBERATELY DOES NOT KNOW:

- **Nothing about the person beyond one list of countries.** Not nationality,
  not permit type, not status, not history. `location.work_authorization` is
  the places they can work without sponsorship, and that is an answer, not a
  file.
- **Nothing about the law.** It expands `EU`/`EFTA`/`EEA` into country codes
  and compares lists. **It gives no legal advice and decides nothing**: the
  user declares where they may work, and the user decides what to do about an
  ad that falls outside it.

AND THE TRAP THAT WILL KEEP CATCHING PEOPLE: **a remote post with a British
employer is still British employment.** The country that matters is the
employer's, not the desk's. The measured case advertised "hybrid and remote
working arrangements available" and the ledger had already been corrected to
`(Remote)` that morning — the plugin noticed the word and still stopped at the
place of work instead of climbing to the right to work there.

    from _workauth import verdict
    v = verdict("GB", cfg["location"].get("work_authorization"))
    if v["flag"]:
        note(v["text"])
"""

__all__ = ["ZONES", "expand", "verdict"]

# Zone names a user may write instead of listing members. Codes are ISO 3166-1
# alpha-2, upper case.
ZONES = {
    "EU": ("AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE",
           "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT",
           "RO", "SK", "SI", "ES", "SE"),
    "EFTA": ("CH", "IS", "LI", "NO"),
    # The EEA is the EU plus Iceland, Liechtenstein and Norway — Switzerland is
    # in EFTA and not in the EEA. Written out because getting it wrong by one
    # country is exactly the kind of quiet error this file is about.
    "EEA": ("AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE",
            "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT",
            "RO", "SK", "SI", "ES", "SE", "IS", "LI", "NO"),
}


def expand(entries):
    """`["CH", "EU"]` → the set of country codes it stands for.

    An entry that is neither a zone nor a two-letter code is returned in the
    `unknown` set rather than dropped: a value the user wrote and this file
    could not read must be visible, not silently ignored.
    """
    codes, unknown = set(), set()
    for raw in entries or ():
        e = str(raw).strip().upper()
        if not e:
            continue
        if e in ZONES:
            codes.update(ZONES[e])
        elif len(e) == 2 and e.isalpha():
            codes.add(e)
        else:
            unknown.add(str(raw).strip())
    return codes, unknown


def verdict(employer_country, allowed):
    """Is employment in `employer_country` open to this person?

    `flag` is True only when the answer is a confident no. **Silence is the
    default**: no configured list, or a country nobody could determine, says
    nothing at all — a user who skipped the setup question gets exactly
    today's behaviour, not a nag.
    """
    country = (employer_country or "").strip().upper()
    codes, unknown = expand(allowed)
    out = {"country": country or None, "flag": False, "status": None,
           "text": None, "unreadable_entries": sorted(unknown)}

    if not allowed:
        out["status"] = "not-configured"
        return out                      # silent: the question was never asked
    if not country or len(country) != 2 or not country.isalpha():
        out["status"] = "country-unknown"
        return out                      # silent: guessing here helps nobody
    if country in codes:
        out["status"] = "authorised"
        return out                      # silent: nothing to say

    out.update(
        flag=True,
        status="employment-excluded",
        text=(
            f"**{country} is not in your `work_authorization`, so a local "
            f"employment contract there needs sponsorship you have not said "
            f"you have — and that is a stop on the employed route, not on the "
            f"ad.** Invoicing {country} from where you are is a different "
            f"legal object and it may well be open: if the employer will work "
            f"B2B, nothing here blocks it. **A remote post does not change "
            f"this by itself** — a remote job with a {country} employer is "
            f"still {country} employment. This is your call and your "
            f"paperwork; the plugin only noticed the mismatch."
        ),
    )
    return out


def _main():
    """A small CLI so a skill can ask without an inline `python3 -c`."""
    import argparse
    import json
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--country", required=True,
                   help="the EMPLOYER's ISO-2 country, not the desk's")
    p.add_argument("--allowed", default="",
                   help="config.yml's location.work_authorization, comma "
                        "separated (`CH,EU`). Empty means not configured, "
                        "and nothing is ever flagged")
    a = p.parse_args()
    allowed = [x for x in (a.allowed or "").split(",") if x.strip()]
    v = verdict(a.country, allowed or None)
    if v["unreadable_entries"]:
        print(f"[workauth] not read as a country or a zone, and ignored "
              f"rather than guessed at: {', '.join(v['unreadable_entries'])}",
              file=__import__("sys").stderr)
    print(json.dumps(v, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
