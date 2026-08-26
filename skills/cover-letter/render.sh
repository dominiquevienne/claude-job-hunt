#!/usr/bin/env bash
# Render a markdown document to a clean A4 PDF via pandoc + xelatex.
# xelatex is used for robust UTF-8 / French-accent handling.
# Usage: render.sh <input.md> <output.pdf> [letter]
#   Pass "letter" as the 3rd arg for the roomier cover-letter geometry.
set -euo pipefail

IN="$1"
OUT="$2"
KIND="${3:-}"

# Make the toolchain findable regardless of how the shell was started:
#  - MacTeX normally exposes xelatex via /Library/TeX/texbin (a symlink farm set
#    up by its TeXDist package) and adds it to the PATH through /etc/paths.d/TeX,
#    which only a fresh login shell picks up. The `mactex-no-gui` cask does NOT
#    create that farm at all, leaving the binaries only under
#    /usr/local/texlive/<year>/bin/<arch>/ — so resolve that directly too.
#  - Homebrew's bin is likewise absent from a bare PATH on Apple Silicon.
PATH="$PATH:/Library/TeX/texbin:/opt/homebrew/bin:/usr/local/bin"
for texbin in /usr/local/texlive/*/bin/*/; do
  [ -x "$texbin/xelatex" ] && PATH="$PATH:${texbin%/}"
done
export PATH

if ! command -v pandoc >/dev/null 2>&1; then
  echo "ERROR: pandoc not found. Install:" >&2
  echo "  macOS:   brew install pandoc" >&2
  echo "  Debian:  sudo apt install -y pandoc" >&2
  echo "  Windows: winget install --id JohnMacFarlane.Pandoc -e" >&2
  exit 3
fi
if ! command -v xelatex >/dev/null 2>&1; then
  echo "ERROR: xelatex not found. Install:" >&2
  echo "  macOS:   brew install --cask mactex-no-gui font-noto-sans" >&2
  echo "  Debian:  sudo apt install -y --no-install-recommends texlive-latex-base texlive-latex-recommended texlive-fonts-recommended texlive-xetex fonts-noto-core" >&2
  echo "  Windows: winget install --id MiKTeX.MiKTeX -e   (allow it to install packages on first use)" >&2
  exit 3
fi

# Both templates do \setmainfont{Noto Sans}; without it xelatex aborts.
#
# There is no portable way to ask "is this font installed": fc-list exists on
# Linux and only on macOS if fontconfig was installed, and Windows has neither.
# So try fc-list first, then look in each platform's font directories. Matching
# is loose on purpose — Homebrew ships the variable font as
# "NotoSans[wdth,wght].ttf" (no dash) while other packagers ship static faces.
font_found=0
if fc-list 2>/dev/null | grep -qi "noto sans"; then
  font_found=1
else
  for d in ~/Library/Fonts /Library/Fonts /System/Library/Fonts \
           ~/.local/share/fonts ~/.fonts /usr/share/fonts /usr/local/share/fonts \
           "$(cygpath -W 2>/dev/null || echo /c/Windows)/Fonts" \
           "${LOCALAPPDATA:-}/Microsoft/Windows/Fonts"; do
    [ -d "$d" ] || continue
    if ls "$d" 2>/dev/null | grep -qi "^notosans"; then font_found=1; break; fi
  done
fi
if [ "$font_found" -eq 0 ]; then
  echo "WARNING: the 'Noto Sans' family may be missing — xelatex will abort if so." >&2
  echo "  macOS:   brew install --cask font-noto-sans" >&2
  echo "  Debian:  sudo apt install -y fonts-noto-core" >&2
  echo "  Windows: download Noto Sans from Google Fonts, select the .ttf files," >&2
  echo "           right-click -> Install for all users" >&2
fi

# Geometry differs: resumes are dense (target 1 page), letters are roomier.
DIR="$(cd "$(dirname "$0")" && pwd)"
EXTRA=()
if [ "$KIND" = "letter" ]; then
  GEOM="top=2.4cm,bottom=2.4cm,left=2.2cm,right=2.2cm"
  FONTSIZE="11pt"
  [ -f "$DIR/letter-template.tex" ] && EXTRA+=(--template="$DIR/letter-template.tex")
else
  GEOM="top=1.9cm,bottom=1.9cm,left=2cm,right=2cm"
  # \documentclass only accepts 10/11/12pt — "10.5pt" was silently dropped with
  # a "Unused global option" warning, so the resume rendered at plain 10pt. The
  # intended 10.5pt now comes from Scale=1.05 on the main font in the template.
  FONTSIZE="10pt"
  # Polished single-column resume template (Noto Sans, colored section rules).
  # Shift headings so ## -> \section (styled rule) and ### -> \subsection (job title).
  [ -f "$DIR/resume-template.tex" ] && EXTRA+=(--template="$DIR/resume-template.tex" --shift-heading-level-by=-1)
fi

# French typography: put a non-breaking space (U+00A0) before high punctuation
# (: ; ! ?) so it never wraps to a new line. Only matches an existing ASCII space
# before the mark, so English text (no space before ':') is left untouched, and
# URLs/times (no space before ':') are unaffected.
# mktemp --suffix= is GNU-only (BSD/macOS mktemp rejects it), so build the .md
# name inside a temp *directory* instead — `mktemp -d` is portable, and pandoc
# still sees the .md extension it needs to pick the markdown reader.
TMPDIR_SRC="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_SRC"' EXIT
SRC="$TMPDIR_SRC/src.md"
perl -CSD -pe 's/ ([:;!?])/\x{00A0}$1/g' "$IN" > "$SRC"

pandoc "$SRC" -o "$OUT" \
  --pdf-engine=xelatex \
  -V geometry:a4paper \
  -V geometry:"$GEOM" \
  -V fontsize="$FONTSIZE" \
  -V colorlinks=true \
  ${EXTRA[@]+"${EXTRA[@]}"}

# ---- PDF weight -----------------------------------------------------------
# Do NOT post-process with Ghostscript. `gs -dPDFSETTINGS=/ebook` shrinks a
# letter from ~169 kB to ~22 kB, but it re-encodes the fonts and loses the
# ToUnicode mapping for ligatures. The page looks identical while the extracted
# text silently rots: "qualifications" -> "quali cations", "mobile-first" ->
# "mobile- rst". For an ATS-parsed CV that is fatal — and it is invisible until
# a parser, not a human, reads the file.
#
# If a PDF is heavy, the cause is almost always the signature image, not the
# text. A 1600 px signature costs ~200 kB for a 2.2 cm render; stored at 320 px
# it is still ~370 dpi at that size and takes a signed letter to about 45 kB
# with the text completely untouched. Keep the original scan under another name
# and resize the copy (`sips -Z 320 signature.png` on macOS, `magick ... -resize`
# elsewhere) if the rendered signature ever needs more detail.

echo "Wrote $OUT"

# Open the generated PDF in the default viewer (detached, non-blocking).
# macOS ships `open`; Linux desktops ship `xdg-open` (with setsid to detach);
# on Windows the script runs under Git Bash, where the opener is cmd's `start`
# — reached as `cmd //c start` because Git Bash would otherwise rewrite the
# single slash into a path. The empty "" is start's title argument: without it,
# start treats a quoted path AS the title and opens nothing.
case "$(uname -s)" in
  Darwin)
    command -v open >/dev/null 2>&1 && open "$OUT" >/dev/null 2>&1 &
    ;;
  MINGW*|MSYS*|CYGWIN*)
    command -v cmd >/dev/null 2>&1 && cmd //c start "" "$(cygpath -w "$OUT" 2>/dev/null || echo "$OUT")" >/dev/null 2>&1 &
    ;;
  *)
    if command -v xdg-open >/dev/null 2>&1; then
      setsid xdg-open "$OUT" >/dev/null 2>&1 < /dev/null &
    fi
    ;;
esac
