#!/usr/bin/env python3
"""Where the user's files go — resolved, and **said out loud before anything is
written there.**

**`$HOME` is not necessarily the user's folder outside a terminal.** In a
sandboxed app session it can belong to the sandbox, so a resume, a cover letter,
a PDF and the ledger land somewhere the person will never find in their file
manager. Issue #109.

**And the expensive failure is not a crash, it is a silent success.** The scan
runs, the letters are written, the ledger fills. Nothing errors. `README.md`
promises *"Plain files. Read them, edit them, back them up"* — **in a container
that sentence becomes false, and nothing says so.**

THE CASCADE, in order, and each step is evidence rather than a guess:

1. **`--prefer <path>`** — a folder the user named or connected. The caller
    passes it; this file never invents one.
2. **`JOB_HUNT_HOME`** — the explicit override, unchanged. The terminal path
    keeps working exactly as it did.
3. **`<home>/Documents/job_applications`**, *if `<home>/Documents` exists and
    is writable.* On a Mac or a Linux desktop it does, which is why nothing
    changes there.
4. **Nothing.** No fallback is invented. The script exits `3` with the
    sentence to put to the person:

        I'll put your job-search files in <suggestion>. Is that where you
        want them?

**Step 4 is the whole point.** The previous behaviour was to default into
`$HOME/Documents/job_applications` whether or not `Documents` existed —
**creating a directory in a container and reporting success.** Refusing to
guess is what turns an invisible failure into one question.

    python3 bin/workspace-path.py                 # resolve, or ask
    python3 bin/workspace-path.py --prefer ~/Docs/Job
    python3 bin/workspace-path.py --json
"""

import argparse
import json
import os
import sys

FOLDER = "job_applications"
EXIT_ASK = 3


def _home():
    return os.path.expanduser("~")


def _writable_dir(path):
    return os.path.isdir(path) and os.access(path, os.W_OK)


def resolve(prefer=None):
    """`(path, source, ask)` — `ask` is a sentence when nothing is settled."""
    home = _home()
    if prefer:
        p = os.path.abspath(os.path.expanduser(prefer))
        return p, "the folder you named", None
    env = os.environ.get("JOB_HUNT_HOME")
    if env:
        return os.path.abspath(os.path.expanduser(env)), "JOB_HUNT_HOME", None
    docs = os.path.join(home, "Documents")
    if _writable_dir(docs):
        return os.path.join(docs, FOLDER), "your Documents folder", None
    # **Nothing established.** `$HOME` exists in a container too, so its
    # existence proves nothing; `Documents` not being there is the evidence
    # that this `$HOME` is not the person's.
    suggestion = os.path.join(docs, FOLDER)
    return None, None, (
        f"I could not tell where your files should go: this machine's home "
        f"folder has no `Documents` in it, which usually means it is not "
        f"yours. **Tell me a folder and I will use it** — or say the word and "
        f"I will create `{suggestion}`.")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--prefer", help="a folder the user named or connected")
    p.add_argument("--json", action="store_true", dest="as_json")
    p.add_argument("--create", action="store_true",
                   help="create it — only after the user has agreed")
    a = p.parse_args()

    path, source, ask = resolve(a.prefer)
    if a.as_json:
        print(json.dumps({"path": path, "source": source, "ask": ask},
                         ensure_ascii=False))
    elif path:
        print(path)
    if ask:
        print(f"[workspace] {ask}", file=sys.stderr)
        return EXIT_ASK
    if a.create:
        os.makedirs(path, exist_ok=True)
    if not a.as_json:
        # **Say where, in words, before anything is written.** A path printed
        # on stdout is for the shell; this line is for the person.
        print(f"[workspace] your job-search files go in {path} "
              f"({source}). Say so now if that is not where you want them.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
