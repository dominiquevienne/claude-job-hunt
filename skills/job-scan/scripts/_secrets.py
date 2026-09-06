#!/usr/bin/env python3
"""Credentials: the environment first, then a file in the user's workspace.

**"From the environment, and from nowhere else" is unworkable outside a
terminal.** In an app-hosted shell the environment may reset between calls, so an exported variable
does not survive from one to the next — `set -a; . ~/.adzuna.env; set +a` is
not merely tedious there, it **cannot work**. Issue #110.

**So a second place, and never a replacement.** The environment still wins; the
file is what a person can create once and keep.

    <workspace>/credentials.env          # or ~/.<name>.env, still read

**The security rule does not move**, and it is the reason this is a file and
not a config key:

- **Never in `config.yml`** — that file is read aloud, pasted into issues and
  backed up.
- **Never in git** — the workspace is the user's data directory, not a
  repository.
- **Never pasted into the conversation.** The plugin does not type secrets.

**And the message when a key is missing must say what to do where it is being
read.** Prescribing `export` and `chmod 600` to somebody who has no shell is
not help; neither is prescribing a file to somebody who is holding a terminal.
`missing_note()` gives both, and says which is which.

    from _secrets import get
    app_id = get("ADZUNA_APP_ID")

Format: `KEY=value` a line, `#` comments, optional `export ` prefix, quotes
stripped. **It is not a shell**: nothing is evaluated, nothing is expanded.
"""

import os
import re

__all__ = ["get", "load", "missing_note", "candidate_files", "Masked"]


class Masked(dict):
    """A mapping of secrets whose `repr` shows lengths and never values.

    **Written after printing one.** Diagnosing this module meant printing what
    it returned, and a real API key — a JWT carrying the user's e-mail — went
    to a terminal.

    **And this guard would not have stopped that one**, which is worth saying
    plainly: the leak was `print(get(...))`, and `get()` has to return the
    value because a caller needs it. What this closes is the *other* accident,
    the one a plain `dict` invites — printing or logging the whole container,
    putting it in an error message, pasting it into an issue. **The rest is
    the caller's discipline, and it was mine.**
    """

    def __repr__(self):
        inner = ", ".join(f"{k!r}: <{len(v)} chars>" for k, v in self.items())
        return "Masked({" + inner + "})"

    __str__ = __repr__

_LINE = re.compile(r"""^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$""")
_CACHE = {}


def _resolver():
    """`bin/workspace-path.py`, imported rather than reimplemented.

    **This function used to be a copy of that cascade with its two guards
    left out**, and those two were the whole point of #109: it took
    `JOB_HUNT_HOME`, else `<home>/Documents/job_applications` the moment
    `Documents` merely *existed*, and it could not be handed the folder the
    user had named. In a sandboxed app session `$HOME` can be the sandbox's — so a `Documents`
    inside it satisfied that test and the credentials were read from a path
    the person will never see. **A silent success, which is the failure #109
    was opened against.**

    The file name has a hyphen, so it is loaded by path.
    """
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "..", "..", "..", "bin", "workspace-path.py")
    path = os.path.normpath(path)
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location("_workspace_path", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Where the old, weaker cascade would have looked. Kept for one purpose only:
# telling somebody whose keys are sitting there that they are no longer being
# read, and naming the file.
def _legacy_workspace():
    docs = os.path.join(os.path.expanduser("~"), "Documents")
    return os.path.join(docs, "job_applications") if os.path.isdir(docs) \
        else None


def _workspace(prefer=None):
    """The user's workspace, resolved the way the files are resolved.

    Returns `None` when nothing is established — **and refusing to guess is
    the point.** `bin/workspace-path.py` exits 3 with a question in that case
    rather than inventing a directory in a container and reporting success.
    """
    mod = _resolver()
    if mod is None:                      # a checkout without bin/, tests aside
        env = os.environ.get("JOB_HUNT_HOME")
        return os.path.abspath(os.path.expanduser(env)) if env else None
    path, _source, _ask = mod.resolve(prefer)
    return path


def candidate_files(name=None):
    """Where a credential may live, in the order they are read.

    The workspace file first because it is the one a person can create without
    a shell; `~/.<name>.env` after it, because that convention is documented
    and in use and **removing it would break the terminal path**.
    """
    out = []
    ws = _workspace()
    if ws:
        out.append(os.path.join(ws, "credentials.env"))
    home = os.path.expanduser("~")
    if name:
        out.append(os.path.join(home, f".{name}.env"))
    return out


def stranded_note(name=None):
    """A sentence when the strict cascade settles nothing **and** a readable
    `credentials.env` is sitting where the old one would have looked.

    **The hardening can stop finding a file that was being found.** Somebody
    whose keys are in `~/Documents/job_applications/credentials.env` on a
    `Documents` that is not writable was served by the old cascade and is not
    served by this one: their setup works this evening and not after the
    release, without their having touched anything.

    `shared/never-fail-silently.md` is exactly this case. The refusal stands —
    guessing is what #109 removed — but it does not stand quietly, and the
    sentence names the file so the person can see what is no longer read.
    """
    if _workspace() is not None:
        return None
    legacy = _legacy_workspace()
    if not legacy:
        return None
    f = os.path.join(legacy, "credentials.env")
    if not (os.path.isfile(f) and os.access(f, os.R_OK)):
        return None
    return (
        f"**`{f}` exists and is no longer being read.**\n"
        f"  This plugin now resolves your workspace the way it resolves every "
        f"other file it writes, and that resolution has settled nothing here: "
        f"`~/Documents` is not writable, which usually means this home folder "
        f"is not yours. **It will not guess**, because guessing is how "
        f"credentials came to be read from inside a container.\n"
        f"  **Your keys are not lost.** Tell the plugin which folder is yours, "
        f"or set `JOB_HUNT_HOME`, and that file is read again.")


def load(name=None):
    """Every key found, file by file. Earlier files win."""
    key = name or ""
    if key in _CACHE:
        return _CACHE[key]
    found = {}
    for path in candidate_files(name):
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        for line in text.splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = _LINE.match(line)
            if not m:
                continue
            k, v = m.group(1), m.group(2).strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            found.setdefault(k, v)
    found = Masked(found)
    _CACHE[key] = found
    return found


def get(var, name=None):
    """**The environment first, then the file.** Never the other way round."""
    v = os.environ.get(var)
    if v:
        return v
    return load(name).get(var)


def missing_note(vars_, name, where, how):
    """What to do, said for both places the message can be read.

    `where` is a human name for the service, `how` a one-line pointer to the
    page that issues the key. **Both routes are given because the reader's
    situation is unknown**, and prescribing a shell command to somebody
    without a shell is not help.
    """
    # **The stranded file goes first, because it changes what the reader
    # should do.** Somebody whose keys are sitting in the old place does not
    # need to be told how to obtain a key — they have one, and it is no longer
    # being read. A note nobody prints is a signal nobody reads, so this is
    # said here rather than left for a caller to remember.
    stranded = stranded_note(name)
    joined = " and ".join(f"`{v}`" for v in vars_)
    ws = _workspace()
    target = os.path.join(ws, "credentials.env") if ws else \
        "<your workspace>/credentials.env"
    # **The indentation has to be inside the join, not in front of it.**
    # An f-string indents only the first line of what it interpolates; every
    # later one starts at column 0 and falls out of the block. A single
    # credential never showed it — the two that do are `ADZUNA_APP_ID` /
    # `ADZUNA_APP_KEY` and France Travail's pair, **the two messages whose
    # whole point is that both values are needed.**
    lines = "\n".join(f"        {v}=…" for v in vars_)
    return (
        (stranded + "\n\n" if stranded else "")
        + f"{joined} not found — neither in the environment nor in a "
        f"credentials file.\n\n"
        f"**In the app**, put them in a file the plugin will find, one per "
        f"line:\n"
        f"    {target}\n"
        f"{lines}\n\n"
        f"**In a terminal**, either that file or the older convention:\n"
        f"    set -a; . ~/.{name}.env; set +a\n\n"
        f"A key for {where} is free and self-service: {how} — **the plugin "
        f"does not create accounts, and never types a secret.** Do not put it "
        f"in `config.yml`: that file is read aloud, pasted into issues and "
        f"backed up."
    )
