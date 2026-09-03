#!/usr/bin/env python3
"""Is the installed plugin behind the published one? Say so once a day, or
say nothing.

**The host does not tell anybody.** Measured 2026-09-02 on a real install:
`claude plugin list` prints

    claude-job-hunt@claude-job-hunt
      Version: 1.85.1

with no indication that 1.90.0 exists. The marketplace clone the host keeps at
`~/.claude/plugins/marketplaces/<name>/` is a git checkout of `main`, and it
sat at `chore: release 1.85.1` — **five releases behind, and nothing said so.**
That is the whole case for this file (issue #79).

WHY `/releases/latest` AND NOT A TAG OR A FILE. The maintainer decided it, and
the reason is worth keeping next to the code: a release is **the version the
author deliberately published**. A tag can be pushed before the release is
ready, and `plugin.json` on the default branch changes when the bump commit
lands, which may precede the tag. Both would tell somebody to update to
something that does not exist yet.

*(The repository has 118 tags and 117 releases. The one gap is `v1.0.0`, tagged
in the same second as `v1.1.0` during the initial bootstrap, before the release
practice began 21 seconds later. It is not a process that drops releases.)*

WHAT THIS NEVER DOES, and the list is the point:

- **It never updates anything.** The plugin is installed through a marketplace
  and updating is the host's action. This prints what exists and the command
  that gets it. It fetches nothing, writes no plugin file and restarts nothing
  — and it never phrases itself so a reader could think it did.
- **It never speaks when there is nothing to say.** Up to date prints nothing:
  not a version, not a reassurance. A "you are up to date" line is a
  notification whose information content is zero.
- **It never tells a contributor to downgrade.** Anyone working on the
  repository runs a version newer than the last release. Remote must be
  strictly greater than local, or this is silent.
- **It never fails loudly.** No network, a 403, a rate limit, a timeout, a
  malformed answer: all silent. **A version check that breaks a job scan is a
  worse bug than the one it fixes.**
- **It never runs on its own.** There is no startup hook. It is called at the
  beginning of a skill invocation — when the plugin is in use, which is the
  moment the information is worth anything — and never in the hundreds of
  sessions that have nothing to do with a job hunt.

Unauthenticated GitHub allows 60 requests an hour per IP, shared by everybody
behind it, so the answer is cached for a day.

    version-check.py            # silent unless there is news
    version-check.py --json     # the state, for a caller that wants it
    version-check.py --force    # ignore the cache (for testing this file)
"""

import argparse
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request

RELEASES = "https://api.github.com/repos/dominiquevienne/claude-job-hunt/releases/latest"
TTL = 24 * 3600
HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "..", ".claude-plugin", "plugin.json")


def cache_path():
    home = os.environ.get("JOB_HUNT_HOME",
                          os.path.expanduser("~/Documents/job_applications"))
    if os.path.isdir(home):
        return os.path.join(home, ".version-check.json")
    return os.path.join(tempfile.gettempdir(), "claude-job-hunt-version.json")


def parse(v):
    """`v1.85.1` → (1, 85, 1), or None.

    **Numbers, never strings.** A string sort puts `v1.10.0` before `v1.9.0`,
    and this repository is long past the version where that starts lying.
    """
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", (v or "").strip())
    return tuple(int(x) for x in m.groups()) if m else None


def installed():
    try:
        with open(MANIFEST, encoding="utf-8") as fh:
            return json.load(fh).get("version")
    except (OSError, ValueError):
        return None


def cached():
    try:
        with open(cache_path(), encoding="utf-8") as fh:
            c = json.load(fh)
        if time.time() - c.get("at", 0) < TTL:
            return c.get("latest")
    except (OSError, ValueError):
        pass
    return None


def remember(latest):
    try:
        with open(cache_path(), "w", encoding="utf-8") as fh:
            json.dump({"latest": latest, "at": time.time()}, fh)
    except OSError:
        pass          # a cache that cannot be written is not worth a word


def published():
    """The latest release tag, or None. **Every failure is None.**"""
    req = urllib.request.Request(RELEASES, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "claude-job-hunt-version-check",
    })
    try:
        with urllib.request.urlopen(req, timeout=6) as r:
            return json.load(r).get("tag_name")
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return None


def state(force=False):
    local = installed()
    latest = None if force else cached()
    fetched = False
    if latest is None:
        latest = published()
        fetched = True
        if latest:
            remember(latest)
    lv, rv = parse(local), parse(latest)
    behind = bool(lv and rv and rv > lv)
    return {
        "installed": local,
        "latest": latest,
        "behind": behind,
        # Named rather than implied: a contributor running a build newer than
        # the last release must never be told to go backwards.
        "ahead_of_release": bool(lv and rv and lv > rv),
        "checked_now": fetched,
        "reason": (None if latest else
                   "the release could not be read — no network, a rate limit, "
                   "or GitHub said no. Nothing is wrong with the plugin."),
    }


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--print-version", action="store_true",
                   dest="print_version",
                   help="print the running version and nothing else, always. "
                        "For a run report: a board failure observed on stale "
                        "code is not evidence about the board (issue #78)")
    p.add_argument("--json", action="store_true", help="print the state and exit")
    p.add_argument("--force", action="store_true", help="ignore the cache")
    a = p.parse_args()
    if a.print_version:
        # **Always prints, unlike everything else here.** #79 asks for silence
        # about *updates*; #78 asks a run to say which code produced it. Those
        # are different sentences and only the first one is a notification.
        print(installed() or "unknown")
        return 0
    s = state(a.force)
    if a.json:
        print(json.dumps(s, ensure_ascii=False))
        return 0
    if not s["behind"]:
        return 0          # **silence is the normal case**
    latest = (s["latest"] or "").lstrip("v")
    print(f"claude-job-hunt {latest} is out; this workspace runs "
          f"{s['installed']}.")
    # **Say it for where it is being read.** Two slash-style CLI commands are
    # Claude Code's syntax and exist nowhere else; prescribing them to somebody
    # in an app is directions to a door that is not there. Name the action
    # first, then give the terminal form as the terminal form. Issue #112.
    print("  Updating is the host's action, not the plugin's — it installs "
          "plugins and it updates them.")
    print("  **In an app:** update `claude-job-hunt` from wherever you "
          "installed it, through the plugin or marketplace view.")
    print("  **In the Claude Code terminal:** two commands, in this order —")
    print("      claude plugin marketplace update claude-job-hunt")
    print("      claude plugin update claude-job-hunt")
    # **Both lines, in this order, and the first is the one people miss.**
    # The host keeps two caches: the marketplace clone it reads to learn what
    # exists, and the plugin cache that is installed. `plugin update` compares
    # the installed version against the clone — so while the clone is stale it
    # finds nothing newer and does nothing, correctly and silently, which
    # looks exactly like a broken plugin. README.md § Updating records that;
    # this file measured the stale half on 2026-09-02, with the clone sitting
    # at `chore: release 1.85.1` five releases after the fact.
    print("  A restart applies it. **Nothing has been changed for you**, and "
          "nothing here is broken: this is a version number, not a fault.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
