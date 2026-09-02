#!/usr/bin/env bash
# claude-job-hunt — which adapters are due for re-verification.
#
# THE FIELD IS A CONTRACT; A DATE IN THE PROSE IS A GUESS. This script used to
# read every date it could find in a file and take the oldest as a verification
# date. On 2026-09-02 it reported jobbkk as 1 384 days stale, because
# jobbkk.md quotes `created_at: 2022-11-17` — a date this repository MEASURED
# on a live ad, to document a board that refreshes ancient postings.
#
# That is issue #67 turned on our own tooling: a value that is present, well
# formed, and does not mean what the reader thinks. Five board files had
# documented that pattern before it caught the tool that looks for it.
# **A script that reads "any date" has no field — it has a heuristic.**
#
# So the source of truth is one explicit header line, near the top of a file:
#
#     <!-- verified: 2026-09-02 -->
#
# A file without one is reported UNDECLARED, not due: the absence of a header
# is not an age, and guessing is what caused this. The migration is
# incremental — every file touched by ordinary work gains the line — with the
# good side effect that recording a verification becomes deliberate rather
# than a by-product of having quoted a date somewhere.
#
# This reads those headers back and sorts by the oldest:
#
#   bin/adapter-age.sh [days]      # default 30
#
# It changes nothing and always exits 0: it is a report, not a gate. A stale
# adapter is not a broken one — it is one nobody has re-run. The only way to
# find out is to run it, which is what the report is for.
set -uo pipefail   # deliberately NOT -e: a file with no date is a result

DAYS="${1:-30}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

case "$DAYS" in
  ''|*[!0-9]*) echo "usage: bin/adapter-age.sh [days]   (a whole number; default 30)" >&2; exit 0 ;;
esac

# --------------------------------------------------------------- portable ---
# BSD date (macOS) and GNU date disagree on everything except -u +%s.
to_epoch() {
  if date -j -f "%Y-%m-%d" "$1" "+%s" >/dev/null 2>&1; then
    date -j -f "%Y-%m-%d" "$1" "+%s"                 # BSD
  else
    date -d "$1" "+%s" 2>/dev/null                   # GNU
  fi
}
TODAY_EPOCH="$(date "+%s")"

age_days() {   # $1 = YYYY-MM-DD
  local e; e="$(to_epoch "$1")"
  [ -z "$e" ] && { echo "?"; return; }
  echo $(( (TODAY_EPOCH - e) / 86400 ))
}

echo "claude-job-hunt — adapter re-verification report"
echo "  today:     $(date '+%Y-%m-%d')"
echo "  threshold: $DAYS day$([ "$DAYS" = 1 ] || echo s)"
echo

# Collect "<oldest> <newest> <count> <path>" per file, then sort by oldest.
ROWS=""
UNDATED=""
UNVERIFIED=""
for f in "$ROOT"/shared/boards/*.md "$ROOT"/shared/ats-open-check.md; do
  [ -f "$f" ] || continue
  case "$(basename "$f")" in README.md) continue ;; esac

  # An adapter written but never run carries a date — the day it was drafted —
  # and without this check the report calls it fresh, which is the exact
  # misreading the file's own banner exists to prevent.
  if grep -qiE '^#{2,3} .*not yet verified against the live' "$f"; then
    UNVERIFIED="$UNVERIFIED$f
"
    continue
  fi

  # The declared field, and nothing else, sets the age.
  declared="$(grep -oE '<!--[[:space:]]*verified:[[:space:]]*20[0-9]{2}-[0-9]{2}-[0-9]{2}' "$f" \
              | grep -oE '20[0-9]{2}-[0-9]{2}-[0-9]{2}' | sort -u | head -1)"
  if [ -z "$declared" ]; then
    UNDATED="$UNDATED$f
"
    continue
  fi
  # Dates in the body are still worth a note — a section may have outrun the
  # header — but they never set the age. They are data, not metadata.
  prose="$(grep -oE '20[0-9]{2}-[0-9]{2}-[0-9]{2}' "$f" | sort -u)"
  newest="$(echo "$prose" | tail -1)"
  count="$(echo "$prose" | wc -l | tr -d ' ')"
  ROWS="$ROWS$declared $newest $count $f
"
done

printf '%-6s %-22s %-12s %6s   %s\n' "" "ADAPTER" "OLDEST AGE" "" "NOTE"
echo "$ROWS" | grep -v '^$' | sort | while read -r oldest newest count f; do
  name="$(basename "$f" .md)"
  a="$(age_days "$oldest")"
  if [ "$a" = "?" ]; then
    mark="[ ?? ]"; note="unparseable date $oldest"
  elif [ "$a" -gt "$DAYS" ]; then
    mark="[ due ]"; note="older than $DAYS day$([ "$DAYS" = 1 ] || echo s) — re-run it against the live site"
  else
    mark="[ ok  ]"; note="fresh"
  fi
  # A body mentioning dates later than the declared one is worth a glance: a
  # section may have been re-verified while the header was not — or the file
  # may simply quote measured data, which is legitimate and common.
  if [ "$newest" \> "$oldest" ]; then
    note="$note; body mentions $count date(s), latest $newest — check whether a section outran the header"
  fi
  printf '%s %-22s %-12s %5sd   %s\n' "$mark" "$name" "$oldest" "$a" "$note"
done

if [ -n "$UNVERIFIED" ]; then
  echo
  echo "Never run against the live site — a draft, not a stale adapter. Its own"
  echo "file lists what one session with real access has to measure:"
  echo "$UNVERIFIED" | grep -v '^$' | while read -r f; do
    echo "  [ !! ] $(basename "$f" .md)"
  done
fi

if [ -n "$UNDATED" ]; then
  echo
  echo "UNDECLARED — no <!-- verified: YYYY-MM-DD --> header. Not stale and not"
  echo "fresh: unknown. Add the line next time you touch the file, carrying the"
  echo "date you actually re-ran it against the live site:"
  echo "$UNDATED" | grep -v '^$' | while read -r f; do
    echo "  [ !! ] $(basename "$f" .md)"
  done
fi

echo
echo "Re-verifying means running the adapter against the live site and updating"
echo "its <!-- verified: --> header — not re-reading it. Every defect found on 2026-08-28 was a rule"
echo "generalised one step past what had been observed, and none of them were"
echo "visible on re-reading. When a board has genuinely changed, that is a bug"
echo "in the plugin: report it upstream with the board-request skill."
exit 0
