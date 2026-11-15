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

**THE ASYMMETRY IS A PROPERTY OF `text/csv` AND NOT OF THE TRANSPORT —
measured 2026-11-15, #1322. The paragraph below is CITED and bounded, not
rewritten: do not read "the tab we READ is the one it cannot reach" as a fact
about the route.**

```
exportMimeType: text/csv                     ONE tab — the one we WRITE
exportMimeType: …spreadsheetml.sheet (xlsx)  ALL the tabs, in one file
```

*The CSV measurement reproduces this paragraph exactly, so there is no
disagreement to settle: what nobody had exercised is the OTHER export type. An
`.xlsx` is a zip of XML and the standard library reads it, so this costs no new
dependency.* **And the tab is resolved by its NAME through
`xl/_rels/workbook.xml.rels`, never by the index of `xl/worksheets/sheetN.xml`
— on the workbook measured the two COINCIDED, which is exactly why a reader
that assumes the index returns green today and reads the WRONG tab on the first
workbook whose author reordered or deleted a sheet.**

> *cited:* **The CSV route is asymmetric, in the worst direction.**
> `download_file_content` with `exportMimeType: text/csv` works and returns
> **one tab — the one we WRITE** — and its schema carries no tab selector, so
> that is not a parameter anybody failed to pass. The tab we READ is the one it
> cannot reach.

- to write `candidatures`: the user exports the current tab, we rebuild the
  **full union**, the user imports it. **An import REPLACES a tab**, so the
  export has to come first and the union is the only shape that cannot delete a
  row.
- to read `evenements`: the user exports that tab by hand.

**CLOSED AS *SANS OBJET*, and not by an answer — by the measurement above
(#1322).** The question was asked only because the CSV renders one tab; the
xlsx export renders all of them and the reader resolves by name, so tab order
decides nothing and **no recommendation about it is owed**. *The minute of
human time it asked for is not owed either.* The paragraph below is cited:

> *cited:* **OPEN, and it belongs to the owner because no tool here can settle
> it**: does the export follow tab ORDER or the ACTIVE tab? If it follows
> order, putting `evenements` first makes the read automatic and
> `candidatures` loses nothing, since it is imported by hand either way. The
> measurement takes a minute and needs a human: open the sheet, click
> `evenements`, leave it active **without reordering**, re-run the export.

**AND A CONFORMANT WORKBOOK MAY CARRY A THIRD TAB THE CONTRACT DOES NOT
DECLARE** — a producer's own scan journal, header `date_scan, heure,
mails_vus, evenements_ajoutes, archives, a_verifier, alertes_ignorees,
erreurs`. **It belongs to the producer: we do not write it and we do not read
it.** A reader that ITERATES the tabs instead of naming them would take it for
one of ours; the refusal for an absent tab name lists the tabs the workbook
does carry, which is how a reader learns of this one without reading it.

**AND THE EXPORTED CSV HAS NO TRAILING NEWLINE** — measured at 111 bytes with
`wc -l` returning 0. A `while read` loop drops the last line of such a file in
silence, and here that line is a real event. **A reader uses `csv.reader`, or it
checks the final byte.**

**An unreadable or header-mismatched CSV is refused by an exit code, never read
as "no events"** — and the two are distinct codes, because "the file is not
there" and "the file is not this tab" send a reader to different places.

## What ships today, and what is still owed

`skills/job-sync/scripts/events_sheet.py` carries `events`, `merge` **and
`export` (#1322)**. The paragraph below is cited and not rewritten: do not read
its "`export` is not shipped" as current, and do not conclude from "there is no
egress yet" that the Privacy section still describes the code — **it was
rewritten in the same pull request as `export`, which the section above
requires.**

> *cited:* `skills/job-sync/scripts/events_sheet.py` carries `events` and
> `merge`. **`export` is not shipped**: its premise is the ledger's own shape
> plus the two optional bullets of `employers.md`, and that was not measured.
> *Nothing imports the module and no skill calls it, so there is no egress
> yet.* **Reading "tranche 1 shipped" as "the sheet round-trips" is the error
> this paragraph exists to prevent.**

## What `export` derives, and the three things it leaves EMPTY

**It prints to STDOUT and writes nothing else**, so the user's own import is
still the only thing that changes the sheet, and the order stays export →
union → import.

| what | why it is empty rather than derived |
| :-- | :-- |
| `date_envoi` on a row already `rejected` | the contract's own reason for never rewriting that column is that `applied → rejected` **overwrites the send date in `Status`** — so for such a row **the send date is not in the ledger at all**. `merge` then keeps whatever the sheet holds. A date taken from the refusal would be a send date nobody recorded |
| `statut_pre` with no `JR:` marker in the `Note` | the three declared values map FROM that convention, and the ledger has a fourth state: nothing recorded. Folding it onto `non_declare` would claim a declaration state nobody wrote, on the column a declaration reads |
| `canal` on an id with no board prefix | the column says where the ad was FOUND; inventing a board would assert a provenance |

**And `rejected` rows leave only from a cut-off, with NO cut-off meaning none
of them leaves** — the least-egress default, and the run says how many were
held and which flag releases them. *`applied` rows leave whatever their date,
because an `applied` row is waiting for an answer and leaving it out means its
refusal is never matched.*

**The two optional bullets are ABSENT from the shipped `employers.example.md`,
so both alias columns leave empty unless `--employers` names a file that
declares them.** The reader looks for the labels this contract names —
`aliases` and `domains` — and for nothing else: the template's own "Also
trades as" is NOT read as an alias, because putting into an egress a value the
user never declared for it is an interpretation and not a declaration.
