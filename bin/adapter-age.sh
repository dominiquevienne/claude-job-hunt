#!/usr/bin/env bash
# claude-job-hunt — which adapters are due for re-verification.
#
# Every file in shared/boards/ carries the date it was last checked against the
# live site, because shared/boards/README.md requires it: "Date what you
# verified, and say when a selector was last confirmed. Boards change their
# markup; a dated note lets the next person tell a broken adapter from a broken
# assumption."
#
# This reads those dates back and sorts by the OLDEST claim still standing:
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

  dates="$(grep -oE '20[0-9]{2}-[0-9]{2}-[0-9]{2}' "$f" | sort -u)"
  if [ -z "$dates" ]; then
    UNDATED="$UNDATED$f
"
    continue
  fi
  oldest="$(echo "$dates" | head -1)"
  newest="$(echo "$dates" | tail -1)"
  count="$(echo "$dates" | wc -l | tr -d ' ')"
  ROWS="$ROWS$oldest $newest $count $f
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
  # A file re-verified in part still carries its old claims; say so.
  if [ "$oldest" != "$newest" ]; then
    note="$note; $count distinct dates, newest $newest — parts of this file are older than its header"
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
  echo "No date at all — worse than stale, because nothing says when it was true:"
  echo "$UNDATED" | grep -v '^$' | while read -r f; do
    echo "  [ !! ] $(basename "$f" .md)"
  done
fi

echo
echo "Re-verifying means running the adapter against the live site and updating"
echo "its date — not re-reading it. Every defect found on 2026-08-28 was a rule"
echo "generalised one step past what had been observed, and none of them were"
echo "visible on re-reading. When a board has genuinely changed, that is a bug"
echo "in the plugin: report it upstream with the board-request skill."
exit 0
