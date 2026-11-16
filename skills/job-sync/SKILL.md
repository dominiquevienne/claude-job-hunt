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

## The two matching columns — rules, and they are PERMANENT

**Decided by the owner on 2026-11-15, and they bind every run of this command,
not one batch.** The outside agent uses the `candidatures` tab as a WHITE LIST
to recognise a recruiter's mail. With `alias_entreprise` and
`domaines_expediteurs` empty it can only compare the full company name, which
fails the moment the name carries a parenthesis or the mail comes from an
agency. **So a row this command creates carries both columns at INSERTION, or
it carries a declared blank.**

**Separator: `|`, no stray space.**

### `alias_entreprise` — short forms and variants

The names under which the company can appear in a mail or a sender name.

- **Strip the qualifiers**: `(client : …)`, `(partenaire non nommé)`,
  `(groupe X)`, `(division …)`.
- `Sword Group (client : Lombard Odier…)` → `Sword|Sword Group`
- `Banque Cantonale Vaudoise (division Retail)` → `BCV|Banque Cantonale Vaudoise`
- **NEVER the final client's name as an alias of the agency.** A mail from
  Lombard Odier would then be read as a mail from Sword, which is the one
  mistake this column can make that makes the white list worse than empty.

### `domaines_expediteurs` — the company's OWN domains only

Lower case, no `@`, no needless subdomain.

- **NEVER a platform or a shared ATS domain** — `linkedin.com`, `indeed.com`,
  `jobs.ch`, `job-room.ch`, `jobgether.com`, `greenhouse.io`, `lever.co`,
  `workday`, `smartrecruiters`, `teamtailor` and their kind. One of those would
  make ANY mail look like a reply to an application, which is the failure that
  destroys the list rather than weakening it.
- **A domain goes in only if it is CERTAIN** — the company's official site, or a
  domain seen in an application mail already received.
- **In doubt, leave it EMPTY.** A blank is better than a false domain, and the
  asymmetry is the whole reason: a blank costs one unmatched mail, a false
  domain mislabels every mail from that domain forever.

### Before inserting a row

1. **Look for the company in the tab FIRST.** If it is already there, REUSE its
   existing alias and domain values instead of recomputing them — two rows for
   one company must carry the same two cells, and a recomputation is how they
   drift apart.
2. **Never change the alias or domain of a row that already carries them**
   without asking the owner. They may have been corrected by hand, and this
   command cannot tell a correction from an older guess.
   **`merge` and `push` ENFORCE this** since #1329: those two columns are
   `SHEET_OWNED`, the sheet wins on both, an empty ledger cell is COUNTED
   («N alias/domain cell(s) KEPT») and a value that DIFFERS is NAMED on
   stderr, one line per cell, for the owner to arbitrate. Before the fix the
   union wrote a blank over 123 of the tab's 212 rows and reported
   `0 deleted`: a cell emptied is not a row deleted, and no row count sees it.
3. A company that appears twice — the tab has such pairs — gets the SAME alias
   and domains on both rows.

### The control line, at the end of every sync

**`merge` and `push` print it themselves** — `control_line()` — so an agent
cannot forget to compute it. It is printed even when nothing was inserted,
because a sync that inserted nothing and a sync that forgot the columns read
the same otherwise:

```
CONTROLE : N ligne(s) apres union | A avec alias | D avec domaine | N-D sans domaine
```

**And it counts the UNION, not the rows inserted** (#1329). Counted on the
inserted rows only, it reads identically whether the rows the tab already
carried kept their two cells or had them blanked — which is the exact defect
it would have had to catch.

**And name the blanks out loud** — « N lignes sans domaine » — rather than
leaving the owner to find them in the sheet. A column that is empty by DECISION
and a column that is empty by OMISSION look identical there.

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
