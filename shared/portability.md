# Portability — Windows, macOS, Linux

**The whole plugin must work on all three.** Not "mostly", not "with a bit of
adaptation": a user on Windows gets the same behaviour as a user on macOS, or
the plugin tells them exactly what is different and why.

This file is the single source of truth for platform differences. Read it before
writing any shell, and before assuming a command exists.

## One implementation, not three

There are no `.ps1` or `.cmd` equivalents of the `.sh` scripts, and there should
not be. Claude Code runs shell commands through **Git Bash** on native Windows
and through a normal shell in WSL, on macOS and on Linux — so a portable `.sh`
file is the *only* format that is literally the same code everywhere.

The reason to care is not elegance. The scripts carry safety-critical logic —
the ownership check that stops a stranger's CV being adopted, the page-count
discipline, the refusal to compress a PDF. A second implementation in another
language means two versions of those rules, and the one that drifts is the one
nobody runs. For a plugin whose entire value is "never silently wrong", an
unmaintained fork of the safety logic is a liability, not a feature.

So: **make the shell portable; never fork it.**

## What is verified, and what is not

Say this honestly, in the README and to users — it is the same rule the board
adapters follow.

| Platform | Status |
| :-- | :-- |
| macOS (Apple Silicon) | **Verified.** Scripts, PDF rendering, signature keying and the board adapters were run end to end |
| Linux / WSL2 | Written for it, **not run by the author.** The shell is standard and the packages are named in the README |
| Windows (Git Bash) | Written for it, **not run by the author.** The platform-specific paths below were handled deliberately, not incidentally |

`bin/doctor.sh` exists so that this is checkable in five seconds by whoever gets
there first, rather than being a claim.

## The differences that actually bite

Each of these was a real defect, found by running the code.

| Trap | Why it breaks | The portable form |
| :-- | :-- | :-- |
| **Opening a file** | `open` is macOS, `xdg-open` is Linux, Windows has neither | `case "$(uname -s)"` → `open` / `cmd //c start "" "$(cygpath -w …)"` / `setsid xdg-open`. The `//c` is deliberate: Git Bash rewrites a single `/c` into a path |
| **Python** | Windows has no `python3` on the PATH — it is `python` or the `py` launcher | Resolve it: `for c in python3 python py; do …` — and check the *library* imports too, not just that an interpreter exists |
| **`file(1)`** | Git for Windows does not ship it | Read the magic bytes: `head -c 5 "$f"` = `%PDF-`. More reliable anyway |
| **`fc-list`** | Linux only; on macOS only with fontconfig; never on Windows | Try `fc-list`, then fall back to listing each platform's font directories, including `$(cygpath -W)/Fonts` |
| **Desktop / Documents paths** | Windows with OneDrive Backup redirects them to `$HOME/OneDrive/…` — the default on many machines | Probe both, keep every directory that exists, print which ones were searched. Let `JOB_HUNT_HOME`, `JOB_HUNT_DOWNLOADS`, `JOB_HUNT_DESKTOP` override |
| **ANSI colour** | Not guaranteed in a Git Bash console | Plain ASCII markers (`[ ok ]`, `[MISS]`) in anything a user reads |
| **`xdg-user-dir`** | Linux only | `xdg-user-dir DOWNLOAD 2>/dev/null || echo "$HOME/Downloads"` |

## Two shell traps that are not about platforms, and cost more

Both were found in this repository's own scripts, and both fail **silently**,
which is why they get their own section.

**`set -e` plus a function whose last command legitimately fails.** A helper
ending in `[ -d "$1" ] && arr+=("$1")` returns 1 whenever the directory is
absent — and `set -e` then kills the script with no output at all. A missing
OneDrive folder, i.e. every Mac and every Linux box, was enough to abort a run
before it printed a line. **End such functions with `return 0`.**

**`set -o pipefail` plus a truncating reader.** `producer | head -c 200` makes
`head` close the pipe, the producer takes SIGPIPE, the pipeline returns 141, and
`set -e` kills the script. It only fires when the producer is still writing —
i.e. on *large* inputs — so it passes every small test and then drops half of a
real user's data. **Extract once into a variable and slice in-shell**, or bound
the work at the source (`pdftotext -l 3`, not `| head -150`).

## Rules for anything added later

1. **No new dependency without all three install commands.** If you cannot name
   the Windows one, the dependency is not ready.
2. **Probe, do not assume.** `command -v` before use; a fallback or a clear
   message after.
3. **Never hardcode a path outside `$HOME`** or a user-relocatable variable.
4. **Bound work at the source rather than truncating a pipe.**
5. **End predicate-style helpers with `return 0`.**
6. **Test what you can, and state what you did not test.** Claiming a platform
   works because the code "should" work is the same failure as an adapter
   describing a DOM nobody loaded.
