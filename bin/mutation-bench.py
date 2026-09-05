#!/usr/bin/env python3
"""Run a mutation sweep **on a copy**, never in the shared tree. — #167

    bin/mutation-bench.py mutations.json --out results.jsonl

WHY IT DOES NOT RUN WHERE YOU ARE

On 2026-09-05 a sweep ran in the shared working tree. Two other sessions were
working in it. Two things went wrong and only the second was foreseen:

  * a mutation was live for **eight minutes** because the first run was killed
    at a timeout and its `finally` never executed. **A `finally` does not
    survive the death of its process**, and the announcement that "each
    mutation restores itself" promised a guarantee the mechanism does not give;
  * the second run then started from that dirty tree **believing it was
    clean**, because nothing checked.

One session spent a quarter of an hour dismantling its own conclusions against
file mtimes to work out which of its measurements had been taken under a
mutation. **The result of the sweep was worth less than that.**

So: a throwaway `git worktree`, and the shared tree is never written to.

THREE THINGS THE DAY TAUGHT, BUILT IN

**Cleanliness is checked, not promised** — at the start, because the second run
began dirty, and at the end, because a bench that leaves residue has failed
even if every mutation reported correctly. A dirty tree at either end is a
failure *of the bench*.

**Results are written and flushed after every mutation.** The sweep that died
lost all twenty-four, and four survived only because a human remembered them.

**And every mutation is classified.** *A silent mutation moves a **threshold**
without changing a **form**.* The bench knows which it made, because it knows
what it substituted: a numeric constant, or an element dropped from a tuple, is
silent; an `if False:` is not.

WHY THE CLASSIFICATION IS THE POINT

`FETCH_TOKENS` with `claude-user` removed **breaks nothing**. The code reads
the real file, extracts the real `Crawl-delay`, and returns a fully
circumstantial refusal — no exception, no absurd value, **a plausible and
specific verdict that is wrong in a known direction**. A measurement taken
under it would have revived a thesis refuted the day before, with output more
detailed than the measurement that killed it.

So the number worth reading is not how many mutations went red. It is **the
share of silent mutations that went red, per file**. A file where they go red
is guarded on its values. A file where they pass is guarded on its shapes —
and `_robots.py`, whose guard would not have noticed `FETCH_TOKENS`
amputated, is the specimen.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

NUMERIC = re.compile(r"^-?\d+(?:\.\d+)?$")


def classify(before, after):
    """`silent` when a threshold moved without a form changing."""
    b, a = before.strip(), after.strip()
    if NUMERIC.search(b.rsplit("=", 1)[-1].strip()) and \
            NUMERIC.search(a.rsplit("=", 1)[-1].strip()):
        return "silent"
    if b.count(",") > a.count(",") and "(" in b and "(" in a:
        return "silent"          # an element dropped from a tuple or call
    if re.search(r"\bif (False|True)\b", a) or "pass" in a.split():
        return "structural"
    if len(a) < len(b) // 2:
        return "structural"
    return "silent" if b.replace(" ", "")[:8] == a.replace(" ", "")[:8] \
        else "structural"


def run(cmd, cwd, timeout):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, ""
    return r.returncode, r.stderr


def dirty(cwd):
    r = subprocess.run(["git", "status", "--porcelain"], cwd=cwd,
                       capture_output=True, text=True)
    return [l for l in r.stdout.splitlines() if l.strip()]


def scrub(cwd):
    """Undo everything a run left behind — **including what it wrote.**

    Restoring the source is not restoring the tree. A mutation that removed
    the *where do I write this* check made the tool save a body to a file
    literally named `None`, and the source restore left it there. **The next
    mutation then ran against a tree the previous one had changed**, and
    nothing in either result said so.

    A bench that promises a clean tree has to check the tree, not the files it
    remembers touching.
    """
    subprocess.run(["git", "checkout", "--", "."], cwd=cwd,
                   capture_output=True)
    subprocess.run(["git", "clean", "-fdq"], cwd=cwd, capture_output=True)


def read_results(path):
    """Rows from a bench file, **or a refusal if it is not finished.**

    Without the marker, any count taken from this file is a lower bound
    wearing the clothes of a total.
    """
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    if not rows or not rows[-1].get("done"):
        raise ValueError(
            f"{path} has no completion marker: it is still being written, or "
            f"the bench died. **Any count from it is a lower bound, not a "
            f"total** — 23 rows were once read as the result of 24 mutations.")
    return rows[:-1], rows[-1]["n"]


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mutations", help="JSON list of [tag, path, before, after]")
    p.add_argument("--out", required=True, help="JSONL, written as it goes")
    p.add_argument("--test", default="python3 -m unittest discover -s tests")
    p.add_argument("--timeout", type=float, default=90)
    a = p.parse_args()

    repo = os.getcwd()
    # **Refuse to start from a dirty tree.** The second run of 2026-09-05
    # started from one and did not know.
    d = dirty(repo)
    if d:
        print("ERROR: the tree is dirty before the bench starts — a sweep "
              "cannot tell its own residue from someone's work:\n  "
              + "\n  ".join(d), file=sys.stderr)
        return 2

    muts = json.load(open(a.mutations, encoding="utf-8"))
    work = tempfile.mkdtemp(prefix="mutation-bench-")
    tree = os.path.join(work, "t")
    code, err = run(["git", "worktree", "add", "--detach", tree, "HEAD"],
                    repo, 120)
    if code != 0:
        print(f"ERROR: could not make a worktree: {err}", file=sys.stderr)
        return 2
    print(f"[bench] copy at {tree} — the shared tree is not written to",
          file=sys.stderr)

    try:
        base_code, base_err = run(a.test.split(), tree, a.timeout)
        if base_code != 0:
            print(f"ERROR: the copy is red before any mutation:\n{base_err[-600:]}",
                  file=sys.stderr)
            return 2
        out = open(a.out, "w", encoding="utf-8")
        counts = {}
        for tag, path, before, after in muts:
            f = os.path.join(tree, path)
            src = open(f, encoding="utf-8").read()
            kind = classify(before, after)
            if before not in src:
                row = {"tag": tag, "file": path, "kind": kind,
                       "state": "anchor-absent", "classes": []}
            else:
                open(f, "w", encoding="utf-8").write(src.replace(before, after, 1))
                code, err = run(a.test.split(), tree, a.timeout)
                open(f, "w", encoding="utf-8").write(src)
                # **Between two mutations, not only after the last one.**
                left = dirty(tree)
                scrub(tree)
                if left:
                    row_extra = [l.strip() for l in left]
                else:
                    row_extra = []
                classes = sorted(set(re.findall(
                    r"^(?:FAIL|ERROR): \S+ \(\w+\.(\w+)\.", err, re.M)))
                row = {"tag": tag, "file": path, "kind": kind,
                       "state": ("timeout" if code is None else
                                 "red" if code != 0 else "GREEN"),
                       "classes": classes,
                       "left_behind": row_extra,
                       "before": before[:70], "after": after[:70]}
            # **Written and flushed now.** The sweep that died lost all
            # twenty-four of its results at once.
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            os.fsync(out.fileno())
            k = (row["file"], kind, row["state"])
            counts[k] = counts.get(k, 0) + 1
            print(f"[bench] {row['state']:12} {kind:10} {path}", file=sys.stderr)
        # **The last line says how many there were.** A reader that counted
        # this file while it was being written got 23 for 24 mutations — a
        # figure that was not wrong, only one second stale, with nothing in
        # the file saying so. *An unexplained gap invites an explanation, and
        # an explanation found for a gap that does not exist is a false thesis
        # no re-reading overturns.*
        out.write(json.dumps({"done": True, "n": len(muts)}) + "\n")
        out.flush()
        os.fsync(out.fileno())
        out.close()

        # **Cleanliness is a verdict, not a promise.**
        left = dirty(tree)
        if left:
            print("BENCH FAILED: the copy is dirty at the end — a restore did "
                  "not happen:\n  " + "\n  ".join(left), file=sys.stderr)
            return 3
        print("\n[bench] silent mutations that survived, by file — "
              "**the number worth reading**", file=sys.stderr)
        for (fpath, kind, state), n in sorted(counts.items()):
            if kind == "silent" and state == "GREEN":
                print(f"    {n:3}  {fpath}", file=sys.stderr)
        return 0
    finally:
        run(["git", "worktree", "remove", "--force", tree], repo, 120)
        shutil.rmtree(work, ignore_errors=True)
        after = dirty(repo)
        if after:
            print("BENCH FAILED: the SHARED tree is dirty after the run:\n  "
                  + "\n  ".join(after), file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
