#!/usr/bin/env bash
# Collect the user's LinkedIn PDF exports from Downloads/Desktop into the
# workspace's profile/ directory, so the skills always read from one stable
# place. Re-run whenever the exports are refreshed.
#
# Usage: sync-sources.sh "<Full Name>" [destination-dir]
#        destination defaults to $JOB_HUNT_HOME/profile
#
# Every file is checked, not just copied: a file that is not a PDF, or a PDF
# with no selectable text, is worse than a missing one — it silently produces a
# resume with holes in it. Failures are reported with the reason and the fix.
set -euo pipefail

JOB_HUNT_HOME="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
CANDIDATE="${1:-}"
DEST="${2:-$JOB_HUNT_HOME/profile}"

if [ -z "$CANDIDATE" ]; then
  cat >&2 <<'USAGE'
usage: sync-sources.sh "<Full Name>" [destination-dir]

The name is required: exports are matched against it so that another person's
PDF sitting in the same Downloads folder is never picked up by mistake.
USAGE
  exit 2
fi

mkdir -p "$DEST"

# The longest word of the candidate's name, used to check that an export really
# belongs to them (see the ownership check below). The longest token is chosen
# rather than "the surname" because name order is not universal — it lands on a
# given name or a family name, and either one anchors the file to this person.
ANCHOR="$(printf '%s\n' $CANDIDATE | awk '{ if (length($0) > length(m)) m = $0 } END { print m }')"
if [ "${#ANCHOR}" -lt 3 ]; then
  echo "ERROR: '$CANDIDATE' gives no usable anchor (need a word of 3+ letters)." >&2
  exit 2
fi

# The source folders. On macOS and Linux the on-disk names stay English even
# when the desktop displays them translated, so $HOME/Downloads is right.
#
# Windows is the exception that breaks the assumption: with OneDrive Backup
# enabled — the default on many machines — Desktop and Documents are REDIRECTED
# to $HOME/OneDrive/Desktop, while Downloads usually stays put. Looking only at
# $HOME/Desktop there finds nothing, and the user is told their export is
# missing while it sits in plain sight on their desktop. Probe both, keep every
# directory that exists, and say which ones were searched.
SEARCH_DIRS=()
# NOTE the trailing `return 0`. Without it the function inherits the exit status
# of its last command — 1 whenever the directory does not exist — and under
# `set -e` that kills the script. A missing OneDrive folder, i.e. every Mac and
# every Linux box, was enough to abort the whole run before printing a line.
add_dir() { [ -d "$1" ] && SEARCH_DIRS+=("$1"); return 0; }

if [ -n "${JOB_HUNT_DOWNLOADS:-}" ]; then add_dir "$JOB_HUNT_DOWNLOADS"; else
  add_dir "$(xdg-user-dir DOWNLOAD 2>/dev/null || echo "$HOME/Downloads")"
  add_dir "$HOME/OneDrive/Downloads"
fi
if [ -n "${JOB_HUNT_DESKTOP:-}" ]; then add_dir "$JOB_HUNT_DESKTOP"; else
  add_dir "$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
  add_dir "$HOME/OneDrive/Desktop"
  add_dir "$HOME/OneDrive/Bureau"
fi

if [ ${#SEARCH_DIRS[@]} -eq 0 ]; then
  echo "ERROR: neither a Downloads nor a Desktop folder was found under $HOME." >&2
  echo "  Point the script at the right places:" >&2
  echo "    JOB_HUNT_DOWNLOADS=/path/to/downloads JOB_HUNT_DESKTOP=/path/to/desktop \\" >&2
  echo "      sync-sources.sh \"$CANDIDATE\"" >&2
  exit 2
fi

MISSING=()
SUSPECT=()
UNVERIFIED=()

# LinkedIn exports arrive under two very different names depending on how they
# were produced, and either may land in Downloads or on the Desktop:
#   - "Save to PDF" / a manual rename  ->  projects.pdf
#   - the browser's "Print to PDF"     ->  "<Name> _ LinkedIn - Projects.pdf"
# Either may also carry a " (1)" suffix when the browser avoids an overwrite.
# Match both shapes case-insensitively, and keep the most recently modified hit
# so a fresh export always wins over a stale one.
copy() {  # $1 = canonical dest name, $2 = LinkedIn section label,
          # $3 = "bare" to also accept the sectionless "<Name> _ LinkedIn.pdf"
  local name="$1" section="$2" bare="${3:-}" newest="" src
  local extra=()
  [ "$bare" = "bare" ] && extra=(-o -iname "${CANDIDATE} _ LinkedIn.pdf" \
                                 -o -iname "${CANDIDATE} _ LinkedIn (*).pdf")
  while IFS= read -r src; do
    [ -n "$src" ] || continue
    if [ -z "$newest" ] || [ "$src" -nt "$newest" ]; then newest="$src"; fi
  done < <(
    find "${SEARCH_DIRS[@]}" -maxdepth 1 -type f \
      \( -iname "$name" \
      -o -iname "${name%.pdf} (*).pdf" \
      -o -iname "*LinkedIn - ${section}.pdf" \
      -o -iname "*LinkedIn - ${section} (*).pdf" \
      ${extra[@]+"${extra[@]}"} \) 2>/dev/null
  )

  if [ -z "$newest" ]; then
    echo "  – missing: $name"
    MISSING+=("$name|$section")
    return
  fi

  cp -f "$newest" "$DEST/$name"

  # --- validate ------------------------------------------------------------
  # Is it really a PDF? `file` is not guaranteed to exist — Git for Windows does
  # not ship it — so read the magic bytes directly, which is both portable and
  # more reliable than a description string. `head -c` is safe here: it reads a
  # regular file, so there is no producer to kill with SIGPIPE.
  local magic kind text
  magic="$(LC_ALL=C head -c 5 "$DEST/$name" 2>/dev/null || true)"
  if [ "$magic" != "%PDF-" ]; then
    kind="$(file -b "$DEST/$name" 2>/dev/null || echo "not a PDF")"
    rm -f "$DEST/$name"
    echo "  ! $name is not a PDF — it is: $kind"
    echo "      Source: $newest"
    echo "      Re-print the page with 'Save as PDF' as the DESTINATION,"
    echo "      not 'Save page as…' (which saves an HTML file)."
    SUSPECT+=("$name"); return
  fi

  if command -v pdftotext >/dev/null 2>&1; then
    # Extract ONCE, then inspect in-shell. Do not pipe into `head`/`head -c`
    # here: under `set -o pipefail` a truncating reader closes the pipe, the
    # producer takes SIGPIPE, the command substitution returns 141, and `set -e`
    # kills the whole script with no output at all. It only fires on PDFs large
    # enough for the producer to still be writing — i.e. on long careers — so it
    # looks like "it works for me" right up until it silently drops half the
    # user's history.
    text="$(pdftotext -layout "$DEST/$name" - 2>/dev/null || true)"
    if [ "${#text}" -lt 40 ]; then
      echo "  ! $name has no selectable text (it is an image, e.g. a scan or screenshot)"
      echo "      Nothing can be read from it. Print the page from the browser"
      echo "      instead of photographing the screen."
      SUSPECT+=("$name"); return
    fi

    # --- whose export is this? ------------------------------------------------
    # The canonical names ("experience.pdf", "skills.pdf") say nothing about who
    # they belong to, so a same-named export left in Downloads by someone else —
    # or an old one from a previous occupant of the machine — would be adopted
    # silently as the factual record, and every resume built from it would carry
    # a stranger's career.
    #
    # Two independent anchors, either one is enough:
    #   - the SOURCE FILENAME carries the name ("<Name> _ LinkedIn - Skills.pdf")
    #   - the TEXT carries it (the browser's print header, "<Name> | LinkedIn")
    # Neither is reliable alone. A "Save to PDF" is renamed to a generic name;
    # a "Print to PDF" made with page headers turned off contains the name
    # nowhere in its text — verified on a real export, where the newest file had
    # zero occurrences of its owner's name.
    if printf '%s' "$newest" | grep -qiF -- "$ANCHOR" \
       || printf '%s' "$text"  | grep -qiF -- "$ANCHOR"; then
      : # anchored to this person
    elif [ "$name" = "Profile.pdf" ]; then
      # The backbone of the record, and the one export that always carries the
      # name — "Save to PDF" writes it into the document itself. If it is absent
      # here, this is somebody else's file, and building a CV out of a stranger's
      # career is the worst thing this tool could do. Refuse it.
      rm -f "$DEST/$name"
      echo "  ! $name never mentions '$ANCHOR' — this is not your profile export"
      echo "      Source: $newest"
      echo "      NOT kept. A same-named export belonging to someone else is the"
      echo "      one way this tool could build a CV out of another person's"
      echo "      career, so it is refused rather than guessed."
      echo "      Fix: move or rename that file, export your own profile"
      echo "      (More → Save to PDF), and re-run."
      SUSPECT+=("$name"); return
    else
      # A detail page with no anchor: possibly theirs (printed without headers),
      # possibly a stranger's. A script cannot tell, and silently discarding a
      # legitimate export is as damaging as adopting a foreign one. Keep it,
      # and make the doubt impossible to miss.
      UNVERIFIED+=("$name")
      echo "  ? $name  (from $newest)"
      echo "      Kept, but ownership UNVERIFIED: '$ANCHOR' appears neither in"
      echo "      the filename nor in the text. That is normal for a page"
      echo "      printed with browser headers off — and it is also what someone"
      echo "      else's export looks like. Open it and confirm it is yours."
      return
    fi
  else
    echo "  ? $name kept WITHOUT the ownership check (pdftotext is missing) —"
    echo "      verify it is your own export before relying on it."
  fi

  echo "  ✓ $name  (from $newest)"
}

echo "Collecting exports for '$CANDIDATE'"
for d in "${SEARCH_DIRS[@]}"; do echo "  looking in: $d"; done
echo "  writing to: $DEST"
echo

copy "Profile.pdf"        "Profile" bare
copy "experience.pdf"     "Experience"
copy "projects.pdf"       "Projects"
copy "certifications.pdf" "Certifications"
copy "skills.pdf"         "Skills"

if ! command -v pdftotext >/dev/null 2>&1; then
  echo
  echo "NOTE: pdftotext is not installed, so the text of each PDF could not be"
  echo "      verified. Install it to catch image-only exports early:"
  echo "        macOS:  brew install poppler"
  echo "        Debian: sudo apt install -y poppler-utils"
fi

if [ ${#UNVERIFIED[@]} -gt 0 ]; then
  echo
  echo "UNVERIFIED (${#UNVERIFIED[@]}): ${UNVERIFIED[*]}"
  echo "  Kept, but nothing proves these are yours. Open each one before"
  echo "  relying on it — everything written from them is stated as fact in"
  echo "  your name. Re-printing the page with browser headers ON puts your"
  echo "  name in the file and removes the doubt for good."
fi

if [ ${#MISSING[@]} -gt 0 ] || [ ${#SUSPECT[@]} -gt 0 ]; then
  cat <<'HOWTO'

------------------------------------------------------------------------------
How to produce the exports
------------------------------------------------------------------------------
1. The whole profile — one click:
   open your LinkedIn profile → the "More" button under your header
   → "Save to PDF". It lands in your Downloads folder.

2. The four detail pages — open each URL, then print it to PDF
   (Cmd/Ctrl + P → Destination: Save as PDF), keeping the suggested name:

     https://www.linkedin.com/in/<your-handle>/details/experience/
     https://www.linkedin.com/in/<your-handle>/details/projects/
     https://www.linkedin.com/in/<your-handle>/details/certifications/
     https://www.linkedin.com/in/<your-handle>/details/skills/

   SCROLL EACH PAGE TO THE BOTTOM BEFORE PRINTING. They load more entries as
   you scroll; printing early silently truncates your history, and the resume
   that follows will simply be missing jobs.

Then re-run this script. Files already collected are left alone unless a newer
export is found.

Missing detail pages are workable — the skills continue with a smaller record.
A missing Profile.pdf is not: it is the backbone of the factual record.
HOWTO
fi

echo
echo "Done. The skills read from $DEST"
