#!/usr/bin/env python3
"""`shared/employer-ats.md` resolved — the config names the KEY, the registry
gives the arguments and the justification (#1094 point 3).

**The redundancy was never inside anyone's `config.yml`&nbsp;: it is between
the config and what the repository could know.** Each entry repeated the
coordinates — `host` + `tenant` + `site` — that a registry holds once. So a
pointer is `(family, identifier)`, which the user's config ALREADY writes:
`family` is the board name, `identifier` is the bare token under its
`employers:` block, and `tenant_offer.employers_of` already parses both.

**The pointer is NOT the employer label.** The registry's own format table
says `employer_label` is «&nbsp;a human label, NOT unique and never a
key&nbsp;», so resolving on it would resolve the wrong row the day two
employers share a name. The key is `(family, identifier)`, and that is what
its guard asserts unique.

Three things this module refuses to do, each because #1094 § 3 named it:

1. **An unresolved pointer renders UNKNOWN and SAYS SO — never zero, never an
   empty argument string.** `launchd` taught the repository that a missing
   tool answers UNKNOWN and not a count of zero; here the same shape costs one
   extra return value. `where` names what was consulted, the way `_override`
   does it, so a refusal reads «&nbsp;no row for ats/docker in <path>&nbsp;»
   rather than «&nbsp;no row&nbsp;»: a key that is absent and a registry that
   was never found are two different things to fix.
2. **A local override stays possible, by name, and it is VISIBLE.** `resolve`
   takes `local=` and, when it is given, returns it while naming BOTH it and
   what the registry would have said. A silent override is how a registry
   starts being wrong without anybody learning it.
3. **It returns the JUSTIFICATION with the values.** `checked` and
   `verified_by` travel in the row, because 302 of the 508 lines of a real
   `config.yml` are the comments that say when a tenant was last exercised and
   which one answers falsely. *A migration that keeps only the values destroys
   the work while looking like it is tidying it.*

**And the parsing detail is load-bearing, not cosmetic — measured 2026-10-21 on
`origin/main`: 21 / 21 identifiers and 21 / 21 `args` cells are wrapped in
backticks, where a `config.yml` writes the identifier BARE.** Comparing the two
raw forms returns a false zero on EVERY present row, with no error at all —
«&nbsp;a same string has several forms, and a pattern right on one returns zero
on the other&nbsp;». So every cell is unwrapped on the way out, and the guard
mutates that unwrapping in both directions.

*The file holds THREE tables under the same seven-column header — 24
seven-column lines are 3 headers and 21 entries — so a row filter that drops
only the first header counts two headers as rows. The symptom is that `family`
answers `family`.*
"""

import _console  # noqa: F401  (patches argparse's writer -- see #1166)
import io
import os
import re

__all__ = ["REGISTRY", "FIELDS", "rows", "resolve", "search"]

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "shared", "employer-ats.md"))

FIELDS = ("family", "identifier", "args", "employer_label",
          "state", "checked", "verified_by")

_SEP = re.compile(r"^\|[\s:|-]+\|$")


def _cell(raw):
    """A cell as the registry writes it, unwrapped — see the docstring.

    **Only a cell wrapped ENTIRELY in backticks is unwrapped.** `strip("`")`
    removes a SET OF CHARACTERS, not a wrapper, and `verified_by` is the cell
    that proves the difference: it reads «&nbsp;`cmd` -> **61**, first
    *title*&nbsp;», so the opening backtick goes and the closing one — which is
    in the MIDDLE — stays, leaving an orphan. Same family as
    `lstrip("www.")`, which corrupts `www.willhaben.at` into `illhaben.at`
    and leaves most hosts alone, so the tool looks like it works. Found by
    RUNNING the resolver, not by re-reading it.
    """
    c = raw.strip()
    if len(c) > 1 and c.startswith("`") and c.endswith("`"):
        c = c[1:-1].strip()
    return c


def rows(path=None):
    """`(rows, where)` — `rows` is None when the registry could not be read.

    None and `[]` are different answers and this returns both: a registry that
    is absent is not a registry that holds nothing.
    """
    path = REGISTRY if path is None else path
    if not os.path.exists(path):
        return None, f"no registry at {path}"
    try:
        with io.open(path, encoding="utf-8") as fh:
            texte = fh.read()
    except OSError as exc:
        return None, f"registry at {path} could not be read ({exc})"
    out = []
    for ligne in texte.splitlines():
        if not ligne.startswith("|") or ligne.count("|") != len(FIELDS) + 1:
            continue
        if _SEP.match(ligne):
            continue
        cells = [_cell(c) for c in ligne.strip("|").split("|")]
        if cells[0] == FIELDS[0]:          # one of the THREE headers
            continue
        out.append(dict(zip(FIELDS, cells)))
    return out, f"{len(out)} row(s) in {path}"


def resolve(family, identifier, path=None, local=None):
    """`(row, where)` for the pointer `(family, identifier)`.

    `row` is None whenever nothing was resolved, and `where` says WHICH of the
    reasons it was. `local` overrides, and the sentence names both.
    """
    # the SAME unwrapping as a cell, and for the same reason — the idiom this
    # module exists to refuse must not survive in the module that refuses it
    key = (str(family).strip().lower(), _cell(str(identifier)).lower())
    found, where = rows(path)
    if found is None:
        if local is not None:
            return dict(local), f"local override for {key[0]}/{key[1]} — and {where}"
        return None, where
    path = REGISTRY if path is None else path
    hit = [r for r in found
           if (r["family"].lower(), r["identifier"].lower()) == key]
    if local is not None:
        said = hit[0]["args"] if hit else None
        quoi = f"the registry says {said!r}" if hit else "the registry has no row"
        return dict(local), (f"local override for {key[0]}/{key[1]} — "
                             f"{quoi} in {path}")
    if not hit:
        return None, f"no row for {key[0]}/{key[1]} in {path}"
    if len(hit) > 1:
        return None, (f"{len(hit)} rows for {key[0]}/{key[1]} in {path} — "
                      f"the key must be unique, so this resolves to nothing")
    row = hit[0]
    if not row["args"]:
        return None, (f"the row for {key[0]}/{key[1]} in {path} carries no "
                      f"args — an empty argument string is not 'no arguments "
                      f"needed', it is a malformed row")
    return dict(row), f"{key[0]}/{key[1]} in {path}"

def search(name, path=None):
    """`(matches, where)` — every row whose `employer_label` holds `name`.

    The registry's key is `(family, identifier)` and an employer NAME is not a
    key, so answering a name is a SEARCH and it returns N rows. The three
    answers are kept apart: None is « I could not read the registry »,
    `[]` is « the registry holds no row for this name », and NEITHER is
    « this employer has no ATS ». Conflating the last two would publish a
    zero nobody measured, at the one place a user cannot see it.

    The match is DECLARED rather than clever: case-folded substring on
    `employer_label` alone, which is the one field whose purpose is the human
    name. It is NOT accent-folded — `Societe` will not find `Société` — and
    that limit is written here because its cost is to MISS a row, which the
    caller's sentence then names, never to invent one.
    """
    found, where = rows(path)
    if found is None:
        return None, where
    path = REGISTRY if path is None else path
    needle = str(name).strip().casefold()
    # A POSITIVE floor on our own pattern: `"" in anything` is True, so an
    # empty name would match EVERY row and the caller would read that as a
    # resolved employer. Refusing to judge is not the same answer as finding
    # nothing, so this is None and not `[]`.
    if not needle:
        return None, (f"an empty name is not a search — refusing to match "
                      f"all {len(found)} row(s) in {path}")
    hit = [dict(r) for r in found
           if needle in r["employer_label"].casefold()]
    return hit, (f"{len(hit)} row(s) for {name!r} among {len(found)} "
                 f"in {path}")


# The witness is prose, so the sub-command is EXTRACTED from it and the script
# it names must be the family itself — a witness that happens to mention
# another adapter would otherwise hand back that adapter's sub-command.
_WITNESS_RE = re.compile(r"\b([A-Za-z0-9_]+)\.py\s+([a-z][a-z-]*)\b")


def subcommand(row):
    """`(sub, where)` — the sub-command, DERIVED from the witness.

    **The format rule already says `args` is «&nbsp;DERIVED from
    `verified_by`, never retyped&nbsp;». The sub-command is the other half of
    the same command, and no column holds it.** Measured 2026-10-21 over the
    21 rows: `ats`→`list` ×11, `workday`→`list` ×6, `successfactors`→`list`,
    `umantis`→`list`, `recruitee`→**`jobs`**, `oraclecloud`→**`sites`**. So it
    is NOT one word for the whole registry, and a caller that assumed `list`
    would hand two families a sub-command they do not have.

    `None` whenever it cannot be derived, and the sentence says so. A command
    emitted without its sub-command would be the worst of the three outcomes:
    it would look launchable.
    """
    fam = str(row.get("family", "")).strip().lower()
    ident = _cell(str(row.get("identifier", "")))
    witness = _cell(str(row.get("verified_by", "")))
    for script, sub in _WITNESS_RE.findall(witness):
        if script.lower() == fam:
            return sub, f"derived from verified_by ({script}.py {sub})"
    return None, (f"the witness for {fam}/{ident} names no "
                  f"`{fam}.py <sub-command>`, so the command cannot be "
                  f"derived — and a retyped sub-command is not a witness")


def command(row):
    """`(cmd, where)` — the launchable command for a resolved row, or None.

    The row's own `args` are taken verbatim: they are asserted to PARSE in
    that adapter's `argparse` by the guard the registry already carries, and
    retyping them here would be the one thing the format forbids.
    """
    sub, where = subcommand(row)
    if sub is None:
        return None, where
    return f"{row['family']}.py {sub} {row['args']}", where


def main(argv=None):
    import argparse
    import json
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("resolve", help="resolve one (family, identifier)")
    r.add_argument("--family", required=True)
    r.add_argument("--identifier", required=True)
    r.add_argument("--registry")
    l = sub.add_parser("rows", help="every row the registry holds")
    l.add_argument("--registry")
    a = ap.parse_args(argv)
    if a.cmd == "rows":
        found, where = rows(a.registry)
        print(json.dumps({"rows": found, "where": where},
                         ensure_ascii=False, indent=2))
        return 0 if found else 1
    row, where = resolve(a.family, a.identifier, a.registry)
    print(json.dumps({"row": row, "where": where},
                     ensure_ascii=False, indent=2))
    return 0 if row else 1


if __name__ == "__main__":
    raise SystemExit(main())
