#!/usr/bin/env python3
"""Save a profile page's text straight into `profile/.text/` — no print dialog.

**Printing five pages to PDF is the first place people stop, and the repository
says so.** `README.md` names it as the abandonment point, and three things make
it expensive:

- **The truncation is silent.** A page that was not scrolled to the bottom
  prints a valid, incomplete PDF. No error, a poorer record, and a resume
  missing jobs.
- **The print dialog is a real wall.** It is a native window; no automation
  crosses it, here or anywhere.
- **And the PDF is not what is used.** Only the *text* is consumed downstream,
  from `profile/.text/`. The PDF is an imposed intermediate whose useful
  content is extracted afterwards. Issue #111.

So the nominal route is inverted: **read the pages in the user's own browser,
in their own session, and save the text.** Same content, no printing, no
dialog — **and the truncation disappears, because nothing depends on a manual
scroll any more.**

    python3 save-profile-text.py experience --stdin < text
    python3 save-profile-text.py skills --from-file /tmp/skills.txt

The name is one of the five the pipeline knows, so a `.text/` written this way
is indistinguishable from one built by `sync-sources.sh`, and every downstream
check — `grep -ril '<term>' profile/.text/` — works unchanged.

**LOGGING IN FOR THE USER IS OUT OF SCOPE AND STAYS OUT.** The reading happens
in *their* browser with *their* session, which is already how the LinkedIn
adapter is designed and what `shared/robots-policy.md` records: LinkedIn
refuses this project by name, including the user-driven agent.
"""

import argparse
import os
import re
import sys

NAMES = ("profile", "experience", "projects", "certifications", "skills")

# Short is not an error and long is not proof, but a page that yielded almost
# nothing is worth saying out loud rather than saving quietly — that is the
# truncation this route exists to remove, and it must not come back as a
# silent success in a new shape.
THIN = 400


def workspace():
    env = os.environ.get("JOB_HUNT_HOME")
    if env:
        return os.path.abspath(os.path.expanduser(env))
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    try:
        sys.path.insert(0, os.path.join(root, "bin"))
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "wp", os.path.join(root, "bin", "workspace-path.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        path, _source, _ask = m.resolve()
        return path
    except Exception:                                  # noqa: BLE001
        return None


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("name", choices=NAMES,
                   help="which of the five sections this text is")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--stdin", action="store_true")
    src.add_argument("--from-file")
    p.add_argument("--dest", help="a profile/ directory; default the workspace")
    a = p.parse_args()

    text = (sys.stdin.read() if a.stdin
            else open(a.from_file, encoding="utf-8", errors="replace").read())
    # Collapse the runs of blank lines a page dump carries, keep the lines.
    text = re.sub(r"\n{3,}", "\n\n", text.replace("\r\n", "\n")).strip()

    dest = a.dest
    if not dest:
        ws = workspace()
        if not ws:
            print("ERROR: no workspace. Name one with JOB_HUNT_HOME, or pass "
                  "--dest — see shared/workspace.md.", file=sys.stderr)
            return 2
        dest = os.path.join(ws, "profile")
    out = os.path.join(dest, ".text")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, f"{a.name}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text + "\n")

    print(path)
    print(f"[profile] {len(text)} characters saved as {a.name}.txt — "
          f"**no PDF, no print dialog.**", file=sys.stderr)
    if len(text) < THIN:
        print(f"[profile] **that is thin for a profile section** ({len(text)} "
              f"characters). It may be a page that had not finished loading, "
              f"or a section the person genuinely has little in. **Say which "
              f"you think it is rather than saving it silently** — a short "
              f"record and a truncated one look identical afterwards.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
