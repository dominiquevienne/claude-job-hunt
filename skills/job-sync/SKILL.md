---
name: job-sync
description: Push the application ledger to the Google Sheet the user owns, so an agent that reads their mailbox can tell which companies and which applications a reply belongs to. Proposes the union first and writes nothing without an explicit yes. Use when the user asks to "synchroniser la feuille", "mettre à jour le Sheet", "envoyer mes candidatures dans la feuille", "sync the sheet", or asks why an assistant reading their mail does not know about an application.
user-invocable: true
allowed-tools: Bash(*), Read
---

# Sheet sync

Writes the `candidatures` tab of a spreadsheet **the user owns** from the
ledger that `job-scan` and `cover-letter` maintain, and reads back the
`evenements` tab that an outside agent fills.

**Why this exists.** The ledger lives on the user's machine; an assistant that
sorts their mail does not. The sheet is the only bridge between the two, and
the `candidatures` tab is the side that carries what the user applied to.
*Decided by the owner on 2026-11-15, who also refused the shape this used to
have — « il n'est pas envisageable d'exporter... puis potentiellement importer
la feuille... NO go » — so nothing here asks them to export or import
anything.*

## Before anything: the switch, and what it does not protect

`integrations.events_sheet.enabled` in the user's own `config.yml` is the
declared gate. **Read it, and stop if it is not `true`:**

```bash
CFG="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}/config.yml"
python3 - "$CFG" <<'PY'
import io, re, sys
try:
    text = io.open(sys.argv[1], encoding="utf-8").read()
except OSError as exc:
    print("CONFIG ABSENTE: %s" % exc); raise SystemExit(1)
#  read the two scalars under `integrations.events_sheet` without a YAML
#  parser: this skill is a procedure, not an adapter, and the repository keeps
#  exactly one code path that opens the config.
block = re.search(r'(?ms)^integrations:\s*$(.*?)(?=^\S|\Z)', text)
if not block:
    print("PAS DE SECTION integrations: la synchro est DESACTIVEE par defaut")
    raise SystemExit(2)
sub = block.group(1)
on = re.search(r'^\s+enabled:\s*(\S+)', sub, re.M)
sid = re.search(r'^\s+sheet_id:\s*["\']?([A-Za-z0-9_-]{20,})', sub, re.M)
print("enabled  :", on.group(1) if on else "(absent)")
print("sheet_id :", "present" if sid else "(absent)")
if not on or on.group(1).strip().lower() != "true":
    raise SystemExit(2)
if not sid:
    raise SystemExit(3)
PY
```

**Exit 2 means the user has not turned it on** — say so and stop; do not pass
`--sheet` from memory to work around it. **Exit 3 means the switch is on and
the id is missing**: ask for the id once and tell the user to write it in
`config.yml` under `integrations.events_sheet.sheet_id`, because an id typed
into a command is an id nobody can audit tomorrow.

> **AND SAY WHAT THIS SWITCH IS WORTH.** It is read HERE, in a procedure, and
> **not** by the transport: a direct `events_sheet.py push --apply` does not
> consult it. So it gates this command and not the script, and the gate that
> actually holds is the second one below — nothing is written without an
> explicit yes. *Declaring that is the point: a flag described as a protection
> it does not provide is worse than no flag.*

## The sync

**Propose, then write — never both in one breath.**

```bash
cd <the repository>
python3 skills/job-sync/scripts/events_sheet.py push \
  --sheet <the sheet_id from config.yml> \
  --pipeline "${JOB_HUNT_HOME:-$HOME/Documents/job_applications}/job-pipeline.md" \
  --employers "${JOB_HUNT_HOME:-$HOME/Documents/job_applications}/employers.md"
```

Without `--apply` this **writes nothing**: it prints the union it would write
and the counts on stderr. Show the user the counts — how many rows the tab
holds, how many the ledger gives, how many would be added or updated — and
**wait for a yes.** Then run the same line with `--apply` appended.

**The union is the whole safety property.** It never deletes and the write
never clears, so no row the sheet holds can be dropped — including rows the
outside agent put there. A deletion count other than zero is a defect to
report, not a plan to carry out.

## Read the counts out loud, because three of them surprise the user

- **`rejected` rows are HELD BACK by default.** The ledger overwrites the send
  date with the refusal date, so a rejected row has no send date left to give.
  `--rejected-from <YYYY-MM-DD>` releases them from that date. Say how many are
  held; do not release them without being asked.
- **`alias_entreprise` and `domaines_expediteurs` leave EMPTY** unless
  `employers.md` carries the optional `aliases` and `domains` bullets. The
  contract allows it. **It is also the half that matters for matching mail**, so
  name it rather than letting the user discover that the two columns are blank.
- **`canal` is empty on an id with no board prefix**, and `statut_pre` is empty
  when no `JR:` marker was recorded — which is a fourth state the three
  declared values do not cover.

## The other direction

`events` reads the tab the outside agent fills, from a CSV or an `.xlsx`
export of it:

```bash
python3 skills/job-sync/scripts/events_sheet.py events --csv <the export>
```

It **proposes** the latest event per application and applies nothing. Anything
below `haute` confidence is a suggestion; `/job-report --events` is what shows
them next to the ledger.

## What this command refuses to do

It does not create a spreadsheet, does not share one, does not widen who can
read it, and never prints the credential, the token or the service-account
address. **The credential is the user's**: it is read from
`~/.job-sync-sa.json` (or `$JOB_SYNC_SA_KEY`) and from nowhere else, and an
absent credential is not an error — it is what "not set up" looks like.

*Measured 2026-11-15: the transport signs its token with `openssl` rather than
a Python library, because this repository asserts that no module imports
outside the standard library. Where FIFOs exist the private key never touches a
file; on Windows it goes through a 0600 file removed in a `finally`, which is
the weaker path and is declared as such in `_sheets.py`.*
