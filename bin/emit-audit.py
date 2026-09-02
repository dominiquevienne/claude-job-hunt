#!/usr/bin/env python3
"""Does every adapter enumerate the fields it emits?

**Issue #75. Name what you emit, not what you drop.** A deny-list is a bet that
the problem was enumerated correctly; an allow-list is a bet that the *need*
was. The two failure modes are not symmetric:

- an allow-list that is too narrow produces **a missing field** — visible,
  reported, fixed in one line;
- a deny-list that is too narrow produces **a leak** — invisible, persistent,
  and found by somebody else.

The same asymmetry as `_robots.py` passing on an unreadable file and as #67
putting the caveat in the field name: **when two errors are possible, prefer
the one that announces itself.**

The case that produced the rule: `vieclam24h`'s ad record carries 110 fields,
including a named recruiter's phone, email and address **and the board's own
account manager**. Dropping `employer_info` by name — the obvious fix — would
have left four of the five contact fields behind.

WHAT THIS CHECKS, AND WHAT IT CANNOT. It resolves each `json.dumps(...)` that
reaches stdout back to the expression that built it, following one local
assignment and one function call, and asks whether the result is a **dict
written out key by key**. It reports three verdicts:

    enumerated   every emit site resolves to a dict with named keys
    allow-list   the same, and the keys come from a named tuple (KEEP)
    unresolved   this tool could not follow it — **read it yourself**

**`unresolved` is not `leaking`.** It means the analysis stopped, and saying
otherwise would be the plausible-false-number this repository keeps catching:
a first version of this file called 80 sites suspicious, of which nearly all
were `c = card(...)` one line above.

    bin/emit-audit.py            # one line per adapter
    bin/emit-audit.py --detail   # every site this tool could not resolve
"""

import argparse
import ast
import glob
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.normpath(os.path.join(HERE, "..", "skills", "job-scan", "scripts"))
# Not adapters: helpers and workspace tools emit their own reports.
SKIP = {"dormant.py", "ledger.py", "board_offer.py"}

# **Read by hand on 2026-09-02, because the tool stops before them and an
# unread file must not be reported as a clean one.** Each entry says what the
# emit site turned out to be. Re-read them when the adapter changes shape.
HAND_CHECKED = {
    "ats.py": "seven `<provider>_card` builders reached through the CARDERS "
              "dispatch table; each one is `out = {…literal…}` plus named "
              "optional keys",
    "francetravail.py": "`referentiel` dumps a public reference taxonomy, not "
                        "an ad card — a passthrough of the board's own code "
                        "lists, deliberately",
    "philjobnet.py": "`cards()` appends a literal dict per card",
    "solique.py": "rows come from the listing parser, which builds a literal "
                  "dict per row",
    "stepstone.py": "`cards()` builds a literal dict per card",
    "talentsoft.py": "`ad_detail()` writes only keys named in the AD_FIELDS "
                     "and SECTIONS constants — an allow-list in another shape. "
                     "**But see `other_fields`**: the one emitted field in this "
                     "repository whose content is not enumerable. It carries "
                     "unlabelled fragments of the card's visible text, capped "
                     "at MAX_FIELDS, because this board's rows vary by tenant "
                     "and a wrong label is worse than an unnamed string",
}


def literal(node):
    """A dict written key by key, with no `**` splat."""
    return isinstance(node, ast.Dict) and all(k is not None for k in node.keys)


def allow_list(node):
    """`{k: item.get(k) for k in KEEP}` — the strongest form there is.

    The field set is a named constant, so a field the board adds tomorrow
    cannot appear in the output. `vieclam24h` is why this exists: its record
    carries 110 fields and the card emits sixteen.
    """
    return (isinstance(node, ast.DictComp)
            and len(node.generators) == 1
            and isinstance(node.generators[0].iter, ast.Name)
            and node.generators[0].iter.id.isupper())


def loop_source(fn, name, lineno):
    """`for row in rows:` → what put things in `rows`.

    Cards very often reach `print` through a list: built by a comprehension,
    or appended to in a loop. Without this step the tool stops on six adapters
    that enumerate their fields perfectly well.
    """
    for n in ast.walk(fn) if fn else ():
        if not (isinstance(n, ast.For) and isinstance(n.target, ast.Name)
                and n.target.id == name):
            continue
        it = n.iter
        if isinstance(it, ast.Subscript):
            it = it.value
        if isinstance(it, ast.IfExp):
            it = it.body
        if isinstance(it, ast.Subscript):
            it = it.value
        if not isinstance(it, ast.Name):
            return None
        out = []
        for m in ast.walk(fn):
            if (isinstance(m, ast.Call) and isinstance(m.func, ast.Attribute)
                    and m.func.attr == "append" and m.args
                    and isinstance(m.func.value, ast.Name)
                    and m.func.value.id == it.id):
                out.append(m.args[0])
            if isinstance(m, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == it.id for t in m.targets):
                if isinstance(m.value, ast.ListComp):
                    out.append(m.value.elt)
        return out or None
    return None


def enclosing(tree, lineno):
    best = None
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if n.lineno <= lineno <= (n.end_lineno or n.lineno):
                if best is None or n.lineno > best.lineno:
                    best = n
    return best


def last_assign(fn, name, before):
    """The last `name = <expr>` above `before` inside `fn`."""
    found = None
    for n in ast.walk(fn) if fn else ():
        if isinstance(n, ast.Assign) and n.lineno < before:
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    if found is None or n.lineno > found.lineno:
                        found = n
    return found.value if found else None


def resolve(expr, tree, fn, lineno, depth=0):
    """`enumerated`, `splat`, or None when the analysis stops."""
    if depth > 4 or expr is None:
        return None
    if literal(expr):
        return "enumerated"
    if allow_list(expr):
        return "allow-list"
    if isinstance(expr, ast.Dict):
        return "splat"                      # a `**` merge: bounded by both sides
    if isinstance(expr, ast.Name):
        direct = last_assign(fn, expr.id, lineno)
        if direct is not None:
            return resolve(direct, tree, fn, lineno, depth + 1)
        sources = loop_source(fn, expr.id, lineno)
        if sources:
            got = {resolve(e, tree, fn, lineno, depth + 1) for e in sources}
            got.discard(None) if len(got) > 1 else None
            if got == {"enumerated"} or got == {"allow-list"}:
                return got.pop()
            return None
        return None
    if isinstance(expr, ast.IfExp):
        a = resolve(expr.body, tree, fn, lineno, depth + 1)
        b = resolve(expr.orelse, tree, fn, lineno, depth + 1)
        return a if a == b else None
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name):
        target = next((n for n in ast.walk(tree)
                       if isinstance(n, ast.FunctionDef) and n.name == expr.func.id),
                      None)
        if target is None:
            return None
        verdicts = set()
        for r in [n for n in ast.walk(target)
                  if isinstance(n, ast.Return) and n.value is not None]:
            if isinstance(r.value, ast.Constant) and r.value.value is None:
                continue                    # "not found" is not a card
            verdicts.add(resolve(r.value, tree, target, r.lineno, depth + 1))
        if verdicts in ({"enumerated"}, {"allow-list"}):
            return verdicts.pop()
        if verdicts and None not in verdicts:
            return "splat"
        return None
    return None


def emit_sites(tree):
    """Only `print(json.dumps(...))` that reaches stdout.

    **A first version counted every `json.dumps` in the file** and flagged the
    request bodies four adapters POST to their API — outbound payloads the
    caller wrote, not cards. Counting them made the tool report a problem where
    there was none, which is the failure this whole repository keeps catching.
    """
    for call in ast.walk(tree):
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                and call.func.id == "print" and call.args):
            continue
        if any(k.arg == "file" for k in call.keywords):
            continue                        # stderr is commentary, not a card
        for arg in call.args:
            if (isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute)
                    and arg.func.attr == "dumps" and arg.args):
                yield arg


def audit(path):
    src = io.open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    sites, unresolved = 0, []
    for node in emit_sites(tree):
        sites += 1
        fn = enclosing(tree, node.lineno)
        v = resolve(node.args[0], tree, fn, node.lineno)
        if v is None:
            unresolved.append(node.lineno)
    allow = "KEEP" in src and "for k in KEEP" in src
    return sites, unresolved, allow


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--detail", action="store_true",
                   help="list the sites this tool could not follow")
    a = p.parse_args()
    total = clean = 0
    stuck = []
    for f in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))):
        name = os.path.basename(f)
        if name.startswith("_") or name in SKIP:
            continue
        total += 1
        sites, unresolved, allow = audit(f)
        verdict = ("allow-list" if allow and not unresolved else
                   "enumerated" if not unresolved else
                   f"unresolved ({len(unresolved)} of {sites})")
        if not unresolved:
            clean += 1
        elif name in HAND_CHECKED:
            clean += 1
            verdict = "enumerated (read by hand — see HAND_CHECKED)"
        else:
            stuck.append((name, unresolved))
        print(f"  {name:<24} {sites:>2} emit site(s)  {verdict}")
    print(f"\n{clean} of {total} adapters enumerate every field they emit "
          f"({len(HAND_CHECKED)} of them read by hand, dated in this file).")
    if stuck:
        print(f"{len(stuck)} could not be followed by this tool — **that is not "
              f"a leak, it is an unread file.** Read them:")
        for name, lines in stuck:
            print(f"  {name}: line(s) {', '.join(map(str, lines))}")
        if a.detail:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
