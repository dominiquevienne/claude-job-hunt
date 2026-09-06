#!/usr/bin/env bash
# opencode-job-hunt — environment check.
#
# Reports what is present, what is missing, what each missing piece blocks, and
# the exact command to install it on THIS platform. Run it any time:
#
#   bin/doctor.sh
#
# It changes nothing and always exits 0: it is a report, not a gate. The plugin
# degrades honestly without most of these — the point is that you know which
# parts are degraded before you need them, rather than mid-application.
set -uo pipefail   # deliberately NOT -e: a failing probe is a result, not a crash

# ---------------------------------------------------------------- platform ---
case "$(uname -s)" in
  Darwin) PLATFORM=macos ;;
  Linux)  if grep -qi microsoft /proc/version 2>/dev/null; then PLATFORM=wsl; else PLATFORM=linux; fi ;;
  MINGW*|MSYS*|CYGWIN*) PLATFORM=windows ;;
  *) PLATFORM=unknown ;;
esac

PKG=""
case "$PLATFORM" in
  macos)        PKG="brew" ;;
  linux|wsl)    for p in apt dnf pacman zypper; do command -v "$p" >/dev/null 2>&1 && { PKG="$p"; break; }; done ;;
  windows)      command -v winget >/dev/null 2>&1 && PKG="winget" ;;
esac

echo "opencode-job-hunt — environment check"
echo "  platform:        $PLATFORM ($(uname -s), $(uname -m))"
echo "  package manager: ${PKG:-none detected}"
echo "  shell:           ${BASH_VERSION:-unknown}"
echo

MISSING=0
OPTIONAL_MISSING=0

# how_to <tool>  -> prints the install command for this platform
how_to() {
  case "$1:$PLATFORM" in
    pandoc:macos)      echo "brew install pandoc" ;;
    pandoc:windows)    echo "winget install --id JohnMacFarlane.Pandoc -e" ;;
    pandoc:*)          echo "sudo apt install -y pandoc   (dnf/pacman: pandoc)" ;;
    xelatex:macos)     echo "brew install --cask mactex-no-gui   (lighter: basictex)" ;;
    xelatex:windows)   echo "winget install --id MiKTeX.MiKTeX -e   (let it install packages on first use)" ;;
    xelatex:*)         echo "sudo apt install -y texlive-xetex texlive-latex-recommended texlive-fonts-recommended" ;;
    poppler:macos)     echo "brew install poppler" ;;
    poppler:windows)   echo "winget install --id oschwartz10612.Poppler -e   (then add its bin/ to PATH)" ;;
    poppler:*)         echo "sudo apt install -y poppler-utils" ;;
    font:macos)        echo "brew install --cask font-noto-sans" ;;
    font:windows)      echo "download Noto Sans from fonts.google.com, select the .ttf files, right-click -> Install for all users" ;;
    font:*)            echo "sudo apt install -y fonts-noto-core   (then: fc-cache -f)" ;;
    magick:macos)      echo "brew install imagemagick" ;;
    magick:windows)    echo "winget install --id ImageMagick.ImageMagick -e" ;;
    magick:*)          echo "sudo apt install -y imagemagick" ;;
    pillow:macos)      echo "python3 -m pip install --user Pillow" ;;
    pillow:windows)    echo "py -m pip install --user Pillow" ;;
    pillow:*)          echo "sudo apt install -y python3-pil" ;;
    python:macos)      echo "python3 ships with macOS; if it is gone: brew install python" ;;
    python:windows)    echo "winget install --id Python.Python.3.12 -e   (tick 'Add to PATH')" ;;
    python:*)          echo "sudo apt install -y python3" ;;
    *)                 echo "see README.md" ;;
  esac
}

# --- probes -----------------------------------------------------------------
# Real functions, not strings passed through `eval`. Two reasons, both learned
# the hard way: nested quoting inside an eval'd string silently mangles the
# command (a font that was installed reported as missing), and an `exit` inside
# an eval terminates the whole script rather than the probe.
have() { command -v "$1" >/dev/null 2>&1; }

have_font() {
  fc-list 2>/dev/null | grep -qi "noto sans" && return 0
  local d
  for d in ~/Library/Fonts /Library/Fonts /System/Library/Fonts \
           ~/.local/share/fonts ~/.fonts /usr/share/fonts /usr/local/share/fonts \
           "$(cygpath -W 2>/dev/null || echo /c/Windows)/Fonts" \
           "${LOCALAPPDATA:-}/Microsoft/Windows/Fonts"; do
    [ -d "$d" ] || continue
    ls "$d" 2>/dev/null | grep -qi "^notosans" && return 0
  done
  return 1
}

# The HiringCafe sweep is plain HTTP driven by a stdlib-only Python script, so
# an interpreter is enough — no third-party package to install.
have_python() {
  local c
  for c in python3 python py; do
    if command -v "$c" >/dev/null 2>&1 \
       && "$c" -c "import json,urllib.request" >/dev/null 2>&1; then
      return 0
    fi
  done
  return 1
}

have_pillow() {
  local c
  for c in python3 python py; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c "import PIL" >/dev/null 2>&1; then
      return 0
    fi
  done
  return 1
}

# check <label> <probe-fn> <blocks> <how_to-key> <required|optional>
# Plain ASCII markers, no ANSI colour: this has to stay readable in a Git Bash
# console that may not interpret escape sequences.
check() {
  local label="$1" probe="$2" blocks="$3" key="$4" req="$5"
  if "$probe" >/dev/null 2>&1; then
    printf '  [ ok ] %-14s\n' "$label"
  else
    if [ "$req" = required ]; then
      printf '  [MISS] %-14s blocks: %s\n' "$label" "$blocks"
      MISSING=$((MISSING+1))
    else
      printf '  [ -- ] %-14s optional - %s\n' "$label" "$blocks"
      OPTIONAL_MISSING=$((OPTIONAL_MISSING+1))
    fi
    printf '         install: %s\n' "$(how_to "$key")"
  fi
}

probe_pandoc()    { have pandoc; }
probe_xelatex()   { have xelatex; }
probe_pdftotext() { have pdftotext; }
probe_pdfinfo()   { have pdfinfo; }
probe_magick()    { have magick; }

echo "Documents (resume + cover letter as PDF)"
check "pandoc"    probe_pandoc    "PDF rendering — markdown is still written" pandoc  required
check "xelatex"   probe_xelatex   "PDF rendering — markdown is still written" xelatex required
check "Noto Sans" have_font       "PDF rendering - xelatex aborts without it" font    required
echo
echo "Reading your profile"
check "pdftotext" probe_pdftotext "reading your exports; setup cannot validate them" poppler required
check "pdfinfo"   probe_pdfinfo   "page-count checks after rendering"                poppler required
echo
echo "Job boards"
check "Python"    have_python     "the HiringCafe sweep; the other boards are unaffected" python required
echo
echo "Handwritten signature (optional)"
check "magick"    probe_magick    "keying a scanned signature"                       magick  optional
check "Pillow"    have_pillow     "keying a scanned signature"               pillow  optional
echo

# ------------------------------------------------------------- workspace ----
# **Ask the resolver, so the diagnostic sees what a run would see.** Hardcoding
# the old default here would report a path the plugin no longer uses, and would
# report it as fine. Issue #109.
WS="$(python3 "$(dirname "$0")/workspace-path.py" 2>/dev/null || true)"
echo "Workspace"
if [ -z "$WS" ]; then
  echo "  ✗ not resolved — this machine's home has no Documents folder, so"
  echo "    the plugin will ask you where your files should go instead of"
  echo "    creating them somewhere you would not find. Nothing is broken."
  MISSING=$((MISSING+1))
else
echo "  path: $WS"
if [ -n "${JOB_HUNT_HOME:-}" ]; then
  echo "        (from \$JOB_HUNT_HOME)"
fi
if [ -d "$WS" ]; then
  if [ -w "$WS" ]; then echo "  ✓ exists and is writable"; else echo "  ✗ exists but is NOT writable"; MISSING=$((MISSING+1)); fi
  [ -f "$WS/config.yml" ] && echo "  ✓ configured (config.yml present)" \
                          || echo "  ○ not configured yet — the first run will set it up"
else
  parent="$(dirname "$WS")"
  if [ -d "$parent" ] && [ -w "$parent" ]; then
    echo "  ○ does not exist yet — the first run will create it"
  else
    echo "  ✗ cannot be created: $parent is missing or not writable"
    echo "      set JOB_HUNT_HOME to somewhere you can write, e.g."
    echo "        export JOB_HUNT_HOME=\"\$HOME/job-search\""
    MISSING=$((MISSING+1))
  fi
fi
fi

# OneDrive redirection is the classic Windows surprise: $HOME/Documents exists
# but is not the real Documents folder, so files "disappear" between apps.
if [ "$PLATFORM" = "windows" ] && [ -d "$HOME/OneDrive/Documents" ] && [ -z "${JOB_HUNT_HOME:-}" ]; then
  echo "  ! OneDrive redirection detected: \$HOME/OneDrive/Documents exists."
  echo "      Your real Documents folder is probably there, not at \$HOME/Documents."
  echo "      Pin the workspace explicitly so it lands where you expect:"
  echo "        export JOB_HUNT_HOME=\"\$HOME/OneDrive/Documents/job_applications\""
fi
echo

# -------------------------------------------------------------- browser -----
echo "Browser automation (scanning boards, filling application forms)"
echo "  Cannot be probed from a shell. OpenWork provides the browser tools."
echo "  Log in to each board yourself in the OpenWork browser (LinkedIn needs it;"
echo "  jobup.ch does not). The plugin never signs in for you."
echo "  Test it in OpenWork: \"open linkedin.com and tell me if I'm logged in\""
echo "  Browser access is not needed for HiringCafe or other plain-HTTP boards."
echo

# --------------------------------------------------------------- verdict ----
if [ "$MISSING" -eq 0 ] && [ "$OPTIONAL_MISSING" -eq 0 ]; then
  echo "Everything is in place."
elif [ "$MISSING" -eq 0 ]; then
  echo "Ready. $OPTIONAL_MISSING optional item(s) missing — nothing you need is blocked."
else
  echo "$MISSING required item(s) missing. The plugin still runs and will tell you"
  echo "what it cannot do — but installing them now avoids finding out mid-application."
fi
exit 0
