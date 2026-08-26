# claude-job-hunt

Two [Claude Code](https://claude.com/claude-code) skills that run a job search
end to end, honestly.

- **`job-scan`** — sweeps the job boards you switch on, in *your own* Chrome,
  scores every ad against your real profile, and keeps a ledger so the same ad
  is never proposed twice. Ships with adapters for **LinkedIn** and
  **jobup.ch**; no board is enabled until you enable it.
- **`cover-letter`** — takes one ad, from **any board**, and produces a
  tailored, ATS-compliant resume and cover letter as markdown and PDF, after
  telling you whether the job is actually worth applying to **and roughly what
  it pays for someone with your record**. Needs no adapter and no browser: a URL
  is enough.

The unusual part is what it *refuses* to do: it will not claim a skill you do
not have, will not answer a screening question by guessing, will not report an
application as sent unless it saw the confirmation, and will tell you not to
apply when the fit is poor. A job search runs on your credibility; the tool
treats that as the thing to protect.

**And it never fails silently.** Anything skipped, partial, capped or guessed is
in the output of the run that did it — counted as *n of m*, with the reason and
the fix. A job search is invisible work with delayed feedback; you find out
weeks later, from a silence, that something did not happen. That is the failure
mode this plugin is built against. See
[`shared/never-fail-silently.md`](shared/never-fail-silently.md).

---

## Table of contents

- [What you need](#what-you-need)
- [Install — Linux](#install--linux)
- [Install — macOS](#install--macos)
- [Install — Windows](#install--windows)
- [Check that it works](#check-that-it-works)
- [Platform support](#platform-support)
- [First run](#first-run)
- [What it creates](#what-it-creates)
- [Job boards](#job-boards)
- [Configuration](#configuration)
- [Privacy](#privacy)
- [Optional modules](#optional-modules)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## What you need

Nothing here is unusual, but **all of it is needed for the full workflow**. The
plugin degrades honestly: without the browser it still writes your documents,
without LaTeX it still writes the markdown. It just tells you what it cannot do
instead of failing halfway.

**You do not have to install this list up front.** Start the plugin and it
checks each tool at the moment it needs one — then names what is missing, says
what it blocks, gives you the exact command for your platform, and offers to run
it. This section is here for anyone who would rather do it in one pass.

| # | Requirement | Needed for | Without it |
| :-- | :-- | :-- | :-- |
| 1 | **Claude Code**, recent version | everything | — |
| 2 | **A profile to work from** — a LinkedIn account you can export, or an existing CV | the factual record every document is checked against | The plugin cannot work; it will not invent a career |
| 3 | **Google Chrome** + the **[Claude extension for Chrome](https://claude.com/chrome)**, connected, with site permission granted for your job board | scanning ads, filling application forms | Documents still work; nothing opens or fills automatically. You give an ad URL, or paste the text |
| 3b | **Being logged in to the board yourself**, in that Chrome — LinkedIn requires it, jobup.ch does not | scanning LinkedIn, Easy Apply | The plugin works *inside* your session and never signs in for you |
| 4 | **`pandoc`** | markdown → PDF | No PDFs. The markdown is still written and you can convert it yourself |
| 5 | **A LaTeX engine with `xelatex`** (TeX Live, MacTeX or MiKTeX) | the PDF layout | Same as above — `render.sh` prints the install command and stops |
| 6 | **The Noto Sans font family** | both PDF templates set it as the main font | `xelatex` aborts with a font error |
| 7 | **`poppler`** — provides `pdftotext` and `pdfinfo` | reading your profile exports, checking page counts | Setup cannot validate your exports, and page-count checks are skipped |
| 8 | **ImageMagick** + **Python 3** with **Pillow** | *optional* — turning a scanned signature into a transparent PNG | No signature image; the letter leaves blank space to sign by hand |
| 9 | **~50 MB of disk** in your home directory | the workspace: your profile, the ledger, one folder per application | — |

**On the browser parts.** They work *inside your own logged-in session*. You log
in yourself, in your own Chrome; the plugin never handles your credentials,
never signs in for you, and never submits anything without asking you first.

---

## Install — Linux

Tested on Debian/Ubuntu. For Fedora or Arch, substitute your package manager —
the package names are close.

### 1. System packages

```bash
sudo apt update
sudo apt install -y \
  pandoc \
  poppler-utils \
  fonts-noto-core \
  texlive-latex-base texlive-latex-recommended texlive-fonts-recommended texlive-xetex
```

Optional, only if you want a handwritten signature on your letters:

```bash
sudo apt install -y imagemagick python3-pil
```

<details>
<summary>Fedora / RHEL</summary>

```bash
sudo dnf install -y pandoc poppler-utils google-noto-sans-fonts \
  texlive-scheme-basic texlive-xetex texlive-collection-fontsrecommended
sudo dnf install -y ImageMagick python3-pillow   # optional
```
</details>

<details>
<summary>Arch</summary>

```bash
sudo pacman -S --needed pandoc poppler noto-fonts \
  texlive-basic texlive-xetex texlive-fontsrecommended
sudo pacman -S --needed imagemagick python-pillow   # optional
```
</details>

### 2. Chrome and the Claude extension

1. Install Google Chrome if you do not have it.
2. Install the **[Claude extension for Chrome](https://claude.com/chrome)** and
   sign in to it.
3. **Grant it permission for your job board's domain** (`linkedin.com`). The
   extension asks per site; without that permission the scan cannot read a
   single page.
4. **Log in to the job board in that Chrome**, as yourself. Keep it logged in.

### 3. The plugin

In Claude Code:

```
/plugin marketplace add dominiquevienne/claude-job-hunt
/plugin install claude-job-hunt@claude-job-hunt
```

### 4. Fonts

If `fc-list | grep -i "noto sans"` returns nothing after step 1, install the
family manually from <https://fonts.google.com/noto/specimen/Noto+Sans> into
`~/.local/share/fonts/`, then run `fc-cache -f`.

Then go to [Check that it works](#check-that-it-works).

---

## Install — macOS

### 1. Homebrew

If you do not have it:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the "Next steps" it prints — on Apple Silicon it tells you to add
`/opt/homebrew/bin` to your `PATH`, and nothing works until you do.

### 2. System packages

```bash
brew install pandoc poppler
brew install --cask mactex-no-gui font-noto-sans
```

`mactex-no-gui` is a large download (~2 GB) — it is the full TeX distribution
without the GUI applications. A lighter alternative is BasicTeX plus the
packages the templates need:

```bash
brew install --cask basictex
sudo tlmgr update --self
sudo tlmgr install fontspec xcolor geometry titlesec enumitem parskip
```

Optional, only for a handwritten signature:

```bash
brew install imagemagick
python3 -m pip install --user Pillow
```

### 3. Make `xelatex` findable

MacTeX puts its binaries in `/Library/TeX/texbin` and adds them to the `PATH`
through `/etc/paths.d/TeX`, which **only a fresh login shell picks up**. Open a
new terminal after installing, or:

```bash
eval "$(/usr/libexec/path_helper)"
```

`render.sh` also probes the usual locations itself, so this rarely bites — but
if you see "xelatex not found" straight after installing, this is why.

### 4. Chrome and the Claude extension

1. Install Google Chrome.
2. Install the **[Claude extension for Chrome](https://claude.com/chrome)** and
   sign in to it.
3. **Grant it permission for `linkedin.com`** — the extension asks per site.
4. **Log in to LinkedIn in that Chrome**, as yourself.

### 5. The plugin

In Claude Code:

```
/plugin marketplace add dominiquevienne/claude-job-hunt
/plugin install claude-job-hunt@claude-job-hunt
```

Then go to [Check that it works](#check-that-it-works).

---

## Install — Windows

The plugin's helper scripts are `bash` scripts, so Windows needs a bash. There
are two routes; **WSL2 is the one to pick unless you have a reason not to.**

### Route A — WSL2 (recommended)

**1. Install WSL2 with Ubuntu.** In PowerShell, as Administrator:

```powershell
wsl --install -d Ubuntu
```

Reboot when asked, then open **Ubuntu** from the Start menu and create your
Linux user.

**2. Install Claude Code inside WSL**, following the official instructions for
Linux. From here on, run Claude Code from the Ubuntu shell, not PowerShell.

**3. Install the system packages** — the same as
[Install — Linux](#install--linux) step 1, run inside Ubuntu.

**4. Chrome and the extension stay on Windows.** Install Chrome and the
**[Claude extension](https://claude.com/chrome)** in Windows as usual, grant it
permission for `linkedin.com`, and log in there.

> **Caveat worth knowing before you count on it.** Claude Code runs inside WSL
> while Chrome runs on Windows — two different environments. Whether the
> extension connects across that boundary depends on your setup and on the
> version of Claude Code. **Test it first** (see
> [Check that it works](#check-that-it-works), step 4). If it does not connect,
> everything except browser automation still works: you paste the ad text and
> the plugin writes your documents. If browser automation matters to you, use
> Route B.

**5. Where to keep your workspace.** Keep it inside the Linux filesystem
(`~/Documents/job_applications`), not under `/mnt/c/`. Cross-filesystem access
is slow and mangles permissions. To reach your files from Windows Explorer, use
the `\\wsl$\Ubuntu\home\<you>\` path.

### Route B — native Windows

Claude Code runs on Windows directly, and uses **Git Bash** for shell commands.
Everything works provided the tools are on your `PATH`.

**1. Git for Windows** (this is what provides Git Bash):

```powershell
winget install --id Git.Git -e
```

**2. The document toolchain:**

```powershell
winget install --id JohnMacFarlane.Pandoc -e
winget install --id MiKTeX.MiKTeX -e
winget install --id oschwartz10612.Poppler -e
```

MiKTeX installs packages on demand the first time a document needs them —
**allow it when it asks**, or the first render fails with a missing-package
error.

Poppler is not always on the `PATH` after install. Check with
`pdftotext -v` in Git Bash; if it is missing, add its `bin` folder to your
`PATH` environment variable and reopen the shell.

**3. The Noto Sans font.** Download
[Noto Sans](https://fonts.google.com/noto/specimen/Noto+Sans), select all the
`.ttf` files, right-click → **Install for all users**. The PDF templates set it
as the main font and `xelatex` aborts without it.

**4. Optional — signature support:**

```powershell
winget install --id ImageMagick.ImageMagick -e
winget install --id Python.Python.3.12 -e
py -m pip install --user Pillow
```

**5. Chrome and the Claude extension** — install Chrome, install the
**[Claude extension](https://claude.com/chrome)**, grant it permission for
`linkedin.com`, and log in.

**6. The plugin**, in Claude Code:

```
/plugin marketplace add dominiquevienne/claude-job-hunt
/plugin install claude-job-hunt@claude-job-hunt
```

**Known rough edges on native Windows.** Paths with spaces (`C:\Users\Ada
Lovelace\`) occasionally trip shell quoting; if a script fails oddly, that is
the first thing to suspect. The workspace defaults to
`~/Documents/job_applications`, which Git Bash resolves under your Windows user
profile — that is fine.

---

## Check that it works

**The short way — one command**, in the shell Claude Code uses (Git Bash on
native Windows, Ubuntu in WSL, your terminal elsewhere):

```bash
bin/doctor.sh
```

It detects your platform, checks every tool, and for anything missing tells you
what it blocks and the exact install command **for that platform**. It changes
nothing and always exits 0 — it is a report, not a gate.

<details>
<summary>The long way, if you would rather check by hand</summary>

Four checks:

```bash
# 1. The document toolchain
pandoc --version | head -1
xelatex --version | head -1
pdftotext -v            # prints to stderr; that is normal

# 2. The font
fc-list 2>/dev/null | grep -i "noto sans" | head -3
#   macOS without fontconfig: ls ~/Library/Fonts /Library/Fonts | grep -i noto
#   Windows: check the Fonts control panel for "Noto Sans"

# 3. The workspace location the plugin will use
echo "${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
```

**4. The browser.** In Claude Code, ask: *"open a tab on linkedin.com and tell
me whether I'm logged in."* You should get an answer about the page. If Claude
reports no connected browser, the extension is not installed, not signed in, or
has no permission for that site.

</details>

Any of these can fail and you can still use the plugin — you will just be told
what is unavailable, and offered the manual route.

## Platform support

**The whole plugin is written to run identically on Windows, macOS and Linux.**
There is one implementation — portable `bash` — because Claude Code runs shell
commands through Git Bash on Windows, and duplicating the safety-critical logic
into PowerShell would create a second version that drifts. The reasoning, and
the platform traps that were handled, are in
[`shared/portability.md`](shared/portability.md).

What that means in practice, stated honestly:

| Platform | Status |
| :-- | :-- |
| **macOS** (Apple Silicon) | **Verified** — scripts, PDF rendering, signature keying and both board adapters run end to end |
| **Linux / WSL2** | Written for it, **not yet run by the author**. Standard shell, packages named above |
| **Windows** (Git Bash) | Written for it, **not yet run by the author**. The specific traps — no `python3`, no `file`, no `fc-list`, OneDrive-redirected folders, `start` instead of `open` — are all handled deliberately |

`bin/doctor.sh` is there so you can settle it in five seconds rather than trust
the table. **If something is broken on your platform, that is a bug worth an
issue** — it is meant to work, and a report is the fastest way there.

One Windows note worth acting on before you start: if OneDrive Backup is on,
your real Documents folder is under `$HOME/OneDrive/Documents`, so pin the
workspace explicitly and avoid hunting for files later:

```bash
export JOB_HUNT_HOME="$HOME/OneDrive/Documents/job_applications"
```

`doctor.sh` detects that case and tells you.

---

## First run

Just use it. The first invocation of either skill notices there is no
configuration and walks you through setup — about five minutes, most of it
spent locating your LinkedIn exports. **Every question comes with the exact URL
or command that produces the answer**, and anything that does not look right
comes back with the reason and the fix rather than a shrug.

```
/job-scan                        # sweep the boards you enabled, fill the ledger
/cover-letter <job ad URL>       # one ad from any board, start to finish
/cover-letter                    # takes the best pending ad from the ledger
/job-setup                       # change any of it, later
/job-setup boards                # enable or configure a board
/board-request <board URL>       # note a board that has no adapter yet
```

You will be asked for, in this order: your profile documents, your contact
details (pre-filled from those documents — you confirm rather than type), your
home base and how far you will commute, your working languages, the searches to
run, how selective to be, and which optional modules you want.

---

## What it creates

Everything lives in **your workspace**, outside the plugin, so updating or
removing the plugin never touches your data:

```
~/Documents/job_applications/        # or wherever $JOB_HUNT_HOME points
├── config.yml                       # settings
├── candidate.md                     # your identity, target roles, hard blockers
├── commute.md                       # travel times you validated (optional)
├── repos.md                         # what your own code proves (optional)
├── signature.png                    # optional
├── profile/                         # your LinkedIn exports or CV
├── job-pipeline.md                  # the ledger — every ad, once
└── 20260826_Acme-Senior-Engineer/   # one folder per application
    ├── job-ad.md
    ├── resume.md  →  Lovelace_Ada_Acme.pdf
    └── cover-letter.md  →  Lovelace_Ada_Acme_CoverLetter.pdf
```

Plain files. Read them, edit them, grep them, back them up, delete them.

---

## Job boards

| Board | Sweep | Login to scan | Notes |
| :-- | :-- | :-- | :-- |
| **LinkedIn** | yes | **yes**, in your own Chrome | Also drives Easy Apply forms — you always validate the send |
| **jobup.ch** | yes | no | French-speaking Switzerland. Ads carry a full street address, which few boards do |
| Anything else | not yet | — | `cover-letter <URL>` still does the whole job |

**No board is enabled until you enable it.** Scanning drives your own browser
under your own account, so it never touches a site you did not switch on. Turn
one on with `/job-setup boards`.

**Using a board that has no adapter changes nothing for you** — hand
`cover-letter` the ad URL and it scores the fit and writes both documents as
usual. The only thing you lose is the automatic sweep. When you do that, the
plugin notes what an adapter for that board would need; the report is saved in
your workspace, and it is yours to post as an issue if you want it built.

## Configuration

`config.yml` holds the machine-readable settings — see
[`templates/config.example.yml`](templates/config.example.yml), which documents
every key. `candidate.md` holds the prose the config cannot: your target role
families, the blockers you do not want re-litigated every week, and corrections
that override a stale export.

Edit either by hand, or run `/job-setup` to change one section conversationally.

To put the workspace somewhere else, set `JOB_HUNT_HOME` in your shell profile:

```bash
export JOB_HUNT_HOME="$HOME/work/job-search"
```

---

## Privacy

**Nothing is uploaded anywhere by this plugin.** Your profile, your contact
details and your applications stay in your workspace on your machine. The
browser automation acts in your own Chrome session; the job board sees you, as
usual, and no third party is involved.

There is exactly **one** thing that can ever leave your machine, and only if you
ask for it: a **board request** — a short report saying that some job board has
no adapter yet and what one would need. It is written to your workspace first,
shown to you in full, and submitted as a GitHub issue **under your own account**
only after you say yes. It contains the board's URL, one example ad URL, and
notes on the site's structure — no part of your profile, name or application.
The example ad URL is the one detail that says something about you, so the
plugin offers to strip it before submitting.

What Claude reads, it reads to write your documents — the same way it reads any
file you point it at. If that matters for a particular document, keep it out of
`profile/`.

**Never commit your workspace to a public repository.** It contains your
address, your phone number and your employment history. This repo's
`.gitignore` refuses those filenames as a safety net, but the workspace lives
outside the repo precisely so the question does not arise.

---

## Optional modules

Country-specific add-ons, off by default, in `shared/modules/`:

- **`job-room-ch`** — Switzerland: captures the fields the ORP's *preuve de
  recherche d'emploi* form on job-room.ch requires, while the ad is still open,
  and can help fill the form in your own logged-in session.

Modules that touch an official declaration carry an explicit notice:
**they assist, they do not replace your own check.** You are solely responsible
for anything you submit — read every field before you send it. Nothing here is
legal or administrative advice.

Adding a module for your country is the most useful contribution you can make.

---

## Troubleshooting

| Symptom | Cause | Fix |
| :-- | :-- | :-- |
| `ERROR: pandoc not found` / `xelatex not found` | Not installed, or not on the `PATH` of the shell Claude Code uses | Reinstall per your platform above, then open a **new** terminal. On macOS see [Make `xelatex` findable](#3-make-xelatex-findable) |
| `xelatex` aborts on a font error | Noto Sans missing | Install the family, then `fc-cache -f` on Linux |
| MiKTeX asks to install a package mid-render | Normal on first use | Allow it; it happens once |
| "No connected browser" | Extension missing, signed out, or no permission for the site | Install/sign in to the Claude Chrome extension and grant permission for `linkedin.com` |
| The scan says LinkedIn is showing the signed-out page | You are not logged in **in that Chrome** | Log in yourself, then tell Claude to continue. It will not sign in for you |
| The scan only ever sees ~7 ads per search | Expected — the results list is virtualized and the automated tab is hidden | Run more, narrower searches. See [`shared/boards/linkedin.md`](shared/boards/linkedin.md) |
| `sync-sources.sh` reports "missing" for files you exported | They landed somewhere other than Downloads or the Desktop | Move them there, or set `JOB_HUNT_DOWNLOADS` / `JOB_HUNT_DESKTOP` |
| An export has "no selectable text" | It was saved as an image, or via *Save page as* instead of *Print → Save as PDF* | Re-print it from the browser |
| A resume is missing jobs | The detail page was printed before it finished loading | Scroll the LinkedIn page to the bottom, re-print, re-run `sync-sources.sh` |
| PDFs are huge | An oversized signature image, not the text | Resize `signature.png`. **Never** compress the PDF with Ghostscript — it silently corrupts the extracted text an ATS reads |

---

## Contributing

**A new board adapter is the most useful contribution.** The contract is in
[`shared/boards/README.md`](shared/boards/README.md), and `linkedin.md` /
`jobup.md` are the worked examples. One rule above all: **document only what you
ran against the live site, and date it.** An adapter describing a plausible DOM
is worse than no adapter — it fails silently, and the user has no way to tell.

**All three platforms are in scope for every change.** One portable `bash`
implementation, no PowerShell fork — the reasoning and the traps are in
[`shared/portability.md`](shared/portability.md). No new dependency lands
without its Windows, macOS and Linux install commands.

Issues and pull requests welcome. Two rules:

1. **No personal data in a commit**, ever — not yours, not an example person's
   real details. The `templates/*.example.*` files describe a fictional person;
   keep it that way.
2. **Do not add a shortcut that guesses.** Most of the value in these skills is
   the refusals: unopened descriptions marked provisional, unanswerable
   questions left blank, unconfirmed sends never recorded as sent. A change
   that makes the tool smoother by making it less honest will be declined.

## Licence

MIT — see [LICENSE](LICENSE).
