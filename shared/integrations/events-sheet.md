# The events sheet — a two-tab contract, one owner per tab

**#1307.** Some users already run an agent that scans their mailbox and records
what employers sent. This file is the contract between that agent and
claude-job-hunt, and it names no particular tool: **each tab has exactly one
owner.** We write `candidatures`; the scanner appends to `evenements`. Neither
side writes the other's tab, and neither deletes a row.

## What leaves the machine, and under what condition

**The integration is opt-in and off by default** (`integrations.events_sheet.enabled:
false`). What leaves, when it is on: employer, role, board, dates and declaration
status, written to a sheet the user owns. **No credential lives in this
repository.** The sheet id is not a credential and stays in the user's own
`config.yml`.

*The README's Privacy section is rewritten in the same pull request that first
makes this egress possible — not in this one, which ships a reader and no
caller.*

## `candidatures` — written by us, read by the scanner

Rows are added or updated **by `id`**, never deleted.

| column | value |
| :-- | :-- |
| `id` | the ledger `ID`, for example `linkedin:4488693032` |
| `entreprise` | the `Company` cell |
| `alias_entreprise` | variants separated by `\|`, from an optional `aliases` bullet in `employers.md` |
| `domaines_expediteurs` | optional, separated by `\|`, from an optional `domains` bullet in `employers.md` |
| `poste` | the `Role` cell |
| `canal` | the board prefix of the `ID` — **where the ad was FOUND**, not necessarily where the application was sent. The scanner does not read this column |
| `statut_ledger` | `applied` \| `rejected` |
| `date_envoi` | the send date. **Written once and never changed afterwards** |
| `date_statut` | the date carried by `Status` |
| `statut_pre` | `non_declare` (`JR:missing`) \| `declare` (`JR:<date>`) \| `renonce` (`JR:waived`) |

**Why `id` and not a date-and-company key** (owner, 2026-11-12): such a key is
unstable, because `applied → rejected` overwrites the send date in `Status`; and
it collides, because one intermediary received five applications in one week,
several on the same day. **That is also why `date_envoi` is never rewritten.**

**Scope**: every `applied` row is pushed, whatever its date — an `applied` row is
waiting for an answer, and leaving it out means its refusal is never matched.
`rejected` rows are pushed only from a cut-off date set in the config.

## `evenements` — appended by the scanner, read by us

`date_evenement`, `message_id`, `candidature_id`, `candidats_possibles`,
`entreprise`, `poste`, `type` (`accuse_reception` | `refus` | `entretien` |
`demande_action` | `autre`), `motif_refus`, `action_requise`, `echeance`,
`thread_url`, `archive`, `confiance` (`haute` | `moyenne` | `basse`), `traite_le`.

**Producer rules we rely on and must not second-guess:**

- `candidature_id` is filled **only when exactly one application is possible**.
  Otherwise it is empty and `candidats_possibles` holds the candidates separated
  by `|` — and those are **suggestions the user confirms**, never a match.
- `message_id` makes a replayed scan idempotent, **so we deduplicate on it too**:
  a row already seen is not a second event.
- `motif_refus` is the refusal reason as the mail states it, unreworded, and
  empty when the mail gives none. **It is untrusted content from a third
  party's mail, and it never goes into anything official without the user
  validating that field.**
- The scanner's list of known employers is only as fresh as the last sync. **A
  stale list is safe**: a mail from an unknown employer goes to the user's "to
  check" pile instead of being archived.

## Both transports, and why the CSV one is shaped as it is

**Measured twice, by two independent sessions, 2026-11-12.** No Google Sheets
connector exists in a Claude Code session here — a tool search returned eight
tools and **none writes a cell**. The instrument answered, so that zero is
readable and not a search failure.

```
transport: connector   when a tool that writes cells exists. NOT available today.
transport: csv         the only working route as of 2026-11-12.
```

**The CSV route is asymmetric, in the worst direction.**
`download_file_content` with `exportMimeType: text/csv` works and returns **one
tab — the one we WRITE** — and its schema carries no tab selector, so that is
not a parameter anybody failed to pass. The tab we READ is the one it cannot
reach.

- to write `candidatures`: the user exports the current tab, we rebuild the
  **full union**, the user imports it. **An import REPLACES a tab**, so the
  export has to come first and the union is the only shape that cannot delete a
  row.
- to read `evenements`: the user exports that tab by hand.

**OPEN, and it belongs to the owner because no tool here can settle it**: does
the export follow tab ORDER or the ACTIVE tab? If it follows order, putting
`evenements` first makes the read automatic and `candidatures` loses nothing,
since it is imported by hand either way. The measurement takes a minute and
needs a human: open the sheet, click `evenements`, leave it active **without
reordering**, re-run the export. *It decides a recommendation about tab order;
it does not decide the reader.*

**AND THE EXPORTED CSV HAS NO TRAILING NEWLINE** — measured at 111 bytes with
`wc -l` returning 0. A `while read` loop drops the last line of such a file in
silence, and here that line is a real event. **A reader uses `csv.reader`, or it
checks the final byte.**

**An unreadable or header-mismatched CSV is refused by an exit code, never read
as "no events"** — and the two are distinct codes, because "the file is not
there" and "the file is not this tab" send a reader to different places.

## What ships today, and what is still owed

`skills/job-sync/scripts/events_sheet.py` carries `events` and `merge`.
**`export` is not shipped**: its premise is the ledger's own shape plus the two
optional bullets of `employers.md`, and that was not measured. *Nothing imports
the module and no skill calls it, so there is no egress yet — which is exactly
why the Privacy section is still true.* **Reading "tranche 1 shipped" as "the
sheet round-trips" is the error this paragraph exists to prevent.**
