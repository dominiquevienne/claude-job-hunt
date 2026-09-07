#!/usr/bin/env python3
"""Where the user's files go — resolved, and **said out loud before anything is
written there.**

**`$HOME` is not the user's folder outside a terminal.** In CoWork it is a
container's, so a resume, a cover letter, a PDF and the ledger land somewhere
the person will never find in their file manager. Issue #109.

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


def config_path():
    """Where a remembered answer lives. **Honours `XDG_CONFIG_HOME`.**

    Chosen by the owner on 2026-09-07, from four candidates, and this is the
    one that is portable and that a person can find and edit without us.
    """
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(_home(), ".config")
    return os.path.join(base, "claude-job-hunt", "config.yml")


def from_config(path=None):
    """The workspace this machine has been told to use, or `None`.

    **It reads; it never creates.** Writing into somebody's configuration
    directory because a tool ran is a side effect, not a feature — the file's
    absence is the ordinary case and not an error. `--remember` is the one
    thing that writes, and only after the person has named a folder.

    Parsed by hand, one key. `dormant.py` settled that idiom for the
    workspace's own `config.yml`: *a tool that needs a pip install before it
    can read its own config has moved the problem, not solved it.* This file
    holds one line, and an unreadable one is treated as absent rather than
    fatal — **the cascade below it still works, and refusing to start because
    of a stray character in an optional file would be worse than the
    problem.**
    """
    path = path or config_path()
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.split("#", 1)[0].rstrip()
                if not line or line[0].isspace():
                    continue
                key, sep, value = line.partition(":")
                if sep and key.strip() == "workspace":
                    value = value.strip().strip("'\"")
                    if value:
                        return os.path.abspath(os.path.expanduser(value))
    except OSError:
        return None
    return None


def remember(path, config=None):
    """Write the named folder down, so the question is asked once.

    **Called only from `--remember`.** Returns the file it wrote.
    """
    config = config or config_path()
    os.makedirs(os.path.dirname(config), exist_ok=True)
    with open(config, "w", encoding="utf-8") as fh:
        fh.write("# Written by claude-job-hunt. Delete this file to be asked "
                 "again.\n")
        fh.write(f"workspace: {path}\n")
    return config


def resolve(prefer=None):
    """`(path, source, ask)` — `ask` is a sentence when nothing is settled.

    **The order was set by the owner on 2026-09-07:**

        prefer=           the answer being given right now, this turn
        JOB_HUNT_HOME     the environment, when there is one
        config.yml        what the person told us once
        ~/Documents       the last guess, and only if it is writable
        (nothing)         a question, never an invented directory

    `prefer` sits above the environment because it is not a stored source at
    all: it is what the person is saying as we ask. The three below it are
    the ones that persist, and their order is the decision.
    """
    home = _home()
    if prefer:
        p = os.path.abspath(os.path.expanduser(prefer))
        return p, "the folder you named", None
    env = os.environ.get("JOB_HUNT_HOME")
    if env:
        return os.path.abspath(os.path.expanduser(env)), "JOB_HUNT_HOME", None
    saved = from_config()
    if saved:
        return saved, "the folder you named earlier", None
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
    p.add_argument("--remember", action="store_true",
                   help="write the folder down so the question is asked once "
                        "— only after the user has named one. Nothing else "
                        "here writes to the configuration directory.")
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
    if a.remember:
        # **The only write, and it is opt-in.** Reading must never create:
        # a tool that puts a file in someone's configuration directory
        # because it ran has had a side effect, not a feature.
        written = remember(path)
        print(f"[workspace] remembered in {written} — delete that file to be "
              f"asked again.", file=sys.stderr)
    if not a.as_json:
        # **Say where, in words, before anything is written.** A path printed
        # on stdout is for the shell; this line is for the person.
        print(f"[workspace] your job-search files go in {path} "
              f"({source}). Say so now if that is not where you want them.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
