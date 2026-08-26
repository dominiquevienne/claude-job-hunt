# Missing prerequisites — help, don't report

**A missing tool is not an error message, it is a task.** When something the
user needs is absent, never stop at "pandoc is not installed". Take them
through it:

1. **Name what is missing** and, in one line, **what it blocks** — not what it
   is. "Without `pandoc` I can write your resume but not turn it into a PDF."
2. **Give the exact command for their platform**, already filled in.
3. **Offer to run it** — ask first, always. It modifies their machine.
4. **Verify afterwards**, with the check command, and say so.
5. **If they decline, or it fails, take the fallback** and say plainly what is
   degraded. Never dead-end, and never silently produce less than was asked
   for.

Check prerequisites **when a step needs them**, not all at once at the start.
A user who only wants a scan should never be asked to install LaTeX.

Platform differences, and the traps that come with them, are catalogued once in
[`shared/portability.md`](portability.md) — read it before writing any shell.

## Detecting the platform

```bash
case "$(uname -s)" in
  Darwin) PLATFORM=macos ;;
  Linux)  grep -qi microsoft /proc/version 2>/dev/null && PLATFORM=wsl || PLATFORM=linux ;;
  MINGW*|MSYS*|CYGWIN*) PLATFORM=windows ;;
  *) PLATFORM=unknown ;;
esac
echo "$PLATFORM"
```

On Linux, pick the package manager the same way — `apt`, `dnf`, `pacman` —
rather than assuming Debian.

## The table

| Tool | Check | Blocks | Install |
| :-- | :-- | :-- | :-- |
| `pandoc` | `pandoc --version` | PDF rendering | macOS `brew install pandoc` · Debian `sudo apt install -y pandoc` · Fedora `sudo dnf install -y pandoc` · Arch `sudo pacman -S pandoc` · Windows `winget install --id JohnMacFarlane.Pandoc -e` |
| `xelatex` | `xelatex --version` | PDF rendering | macOS `brew install --cask mactex-no-gui` · Debian `sudo apt install -y texlive-xetex texlive-latex-recommended texlive-fonts-recommended` · Windows `winget install --id MiKTeX.MiKTeX -e` |
| Noto Sans | `fc-list \| grep -i "noto sans"` | PDF rendering (the templates set it) | macOS `brew install --cask font-noto-sans` · Debian `sudo apt install -y fonts-noto-core` · Windows: download from Google Fonts, select the `.ttf` files, right-click → *Install for all users* |
| `pdftotext`, `pdfinfo` | `pdftotext -v` | Reading profile exports, page-count checks | macOS `brew install poppler` · Debian `sudo apt install -y poppler-utils` · Windows `winget install --id oschwartz10612.Poppler -e` |
| `magick` + Pillow | `magick -version` | Signature image only | macOS `brew install imagemagick && python3 -m pip install --user Pillow` · Debian `sudo apt install -y imagemagick python3-pil` · Windows `winget install --id ImageMagick.ImageMagick -e` then `py -m pip install --user Pillow` |
| Homebrew (macOS) | `brew --version` | Everything above, on macOS | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` — then follow its "Next steps", which set the `PATH` |
| Claude Chrome extension | ask Claude to open a tab | All browser automation | Cannot be installed from a shell — see below |

## Rules when installing for the user

- **Ask before running anything that changes their system.** One question, with
  the command visible. A `sudo` command especially: show it, explain it, and
  let them run it themselves if they prefer.
- **Never run an installer in the background** and report success from the exit
  code alone. Verify with the check command.
- **A fresh shell is often needed.** Homebrew on Apple Silicon and MacTeX both
  add to the `PATH` in ways an already-open shell does not see. If the check
  still fails right after a successful install, say *that* — it is the usual
  cause, and it looks like a failed install to everyone the first time.
- **MiKTeX installs packages on demand** during the first render. Warn the user
  before it happens, so the prompt is expected rather than alarming.
- **Never disable a check to move on.** A resume rendered without Noto Sans is
  not a resume rendered.

## The Chrome extension is different

It cannot be installed from a shell, and it needs three things the user must do
themselves. Give them as a numbered list, not a sentence:

1. Install the **Claude extension for Chrome** — <https://claude.com/chrome>.
2. **Sign in to it** with the same account.
3. **Grant it permission for the site** you are about to use (`linkedin.com`,
   and any board or portal the run touches). The extension asks per site; a
   scan cannot read one page without it.

Then ask the user to confirm, and re-test by opening a tab. Until they confirm,
**do not retry the browser tools in a loop** — it fails identically every time.

If they cannot or will not install it, say what still works without a browser:
`cover-letter` accepts an ad URL, and falls back to pasted ad text when the page
is gated. That is a complete, useful workflow — it just is not automated.

## Being logged in is a prerequisite too

The browser tools work **inside the user's own session**. Before any run that
touches a logged-in site, ask them to log in themselves and confirm — and if a
page comes back showing the signed-out layout, name it, give the URL, and wait.

Never try to work around a login wall, never fill a credential field, and never
offer to sign in on their behalf.
