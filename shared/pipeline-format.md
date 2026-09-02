# The pipeline ledger

`$JOB_HUNT_HOME/job-pipeline.md` is the memory of the whole workflow.
`job-scan` fills it, `cover-letter` reads it and writes outcomes back.

**Read it first, write it last, and never lose a row.** It is the only thing
preventing an ad the user already applied to — or already rejected — from being
proposed again next week.

## Format

```markdown
# Job pipeline — <Full name>

Shared file: `job-scan` fills it and uses it to skip ads already seen;
`cover-letter` reads it and writes the outcome of each application back.

Statuses: `todo` · `applied YYYY-MM-DD` · `rejected YYYY-MM-DD` ·
`no-go YYYY-MM-DD` · `discarded`

- `applied` — sent, no answer yet.
- `rejected` — sent, and **the employer said no**.
- `no-go` — the candidate decided **not to apply** after the gate.
- `discarded` — noise or out of scope, never proposed again.

**An application that went out stays countable: `applied` + `rejected`.**

Pay: gross range, full-time equivalent. `(A)` stated in the ad · `(B)` board
estimate · `(C)` derived · `—` not established.

Last scan: YYYY-MM-DD

## Ads

| ID | Role | Company | Location / mode | Posted | Match | Pay | Status | Note |
| :-- | :-- | :-- | :-- | :-- | --: | :-- | :-- | :-- |
| linkedin:4430721631 | Tech Lead PHP | Acme | Bristol · on-site | 2026-07 | 85 % | GBP 75–90k (A) | applied 2026-07-28 | Stack and location ideal |
| linkedin:4434970873 | Senior Backend Engineer, PHP | Globex | UK · remote | 2026-07 | ~78 % | — | todo | Provisional — description not read |

## Log

- 2026-08-04 — initial scan: 8 searches, 26 ads kept, 12 descriptions read.
```

- **`ID`** is the job board's own job id — the dedup key. Rebuild the ad URL
  from it with the adapter's recipe; **never scrape a URL** out of the page
  (see `shared/boards/linkedin.md`).
  - **Always prefix it with the board**, and **always write the id in full**:

    ```
    linkedin:4430721631
    jobup:4302da20-da24-449c-af7b-2e7577ce45a8
    indeed:c8a3978553801746
    hiringcafe:bs8vw0v4viy4i6se
    job-room:f9673db9-86b5-4792-a360-ba1c7907bb35
    greenhouse:elastic:8098185
    lever:caseware:0dcbf482-60a0-4fd2-9d8f-9945f18d419d
    workday:swisscom:SwisscomExternalCareers:R-0006153
    umantis:jobs.bobst.com:9151
    smartrecruiters:nexthink:744000145952849
    michaelpage:www.michaelpage.ch:jn-072026-7075230
    successfactors:jobs.bcv.ch:31130
    solique:iss:4061853
    fachkraft:19868-STAZH
    sozialinfo:TA94iHqG
    persigo:00G6LE
    randstad:aefa6056-8e23-4d6d-b22e-d2b4c9ef9047
    ```

    **The ATS boards carry the employer in the key**, as
    `<provider>:<tenant>:<id>`. That is not decoration: those platforms host
    one board per employer, and the id alone cannot rebuild a URL without
    knowing whose board it came from.

  - **A job-room row that names a duplicate names it exactly.** Roughly a
    third of its Romandie ads are syndicated from jobup, and the card carries
    `duplicate_of` — `jobup:<uuid>`, lifted from the ad's own external URL.
    That is a certainty, not the substring guess the employer-name check makes:
    discard the new row naming the one it duplicates.

  - **jobup and jobs.ch share one id space, and that is the one exception to
    "the prefix decides".** They are the two faces of JobCloud, and an ad
    published on both carries the **same UUID** on both — verified 2026-08-28 on
    two ads, one of which jobup serves under a machine-translated title while
    jobs.ch keeps the employer's own. So the titles disagree, the employer names
    match, and **only the UUID proves it is one posting**.

    Before writing a `jobs.ch:<uuid>` row, look for `jobup:<uuid>`, and the
    reverse. When the bare UUID already appears under the other prefix this is
    the same ad: discard the new row naming the one it duplicates, with the
    certainty an exact key gives — and do **not** fall back to the fuzzy
    employer-name check, which is for when no such key exists.

    This is what makes enabling both boards safe, and enabling both is the point:
    neither contains the other.

  - **A HiringCafe row also keeps its `apply_url`**, in `Note`. The id
    identifies the ad *on HiringCafe*; the `apply_url` identifies the same
    posting on the employer's own ATS, which is where it will turn up again —
    through another board, or through a future per-ATS adapter. It is the only
    key that survives the crossing.

    **A jobup row keeps its `externalUrl` the same way**, for the same reason —
    it is the employer's own posting, published in the ad's vacancy JSON
    (`shared/boards/jobup.md`). On hosts whose requisition id cannot be derived
    from the ad, it is the only route to an open/closed check at all.

    **No board is the default**, and a bare id is not valid. Two boards already
    ship and ids are not unique across them, so an unprefixed id is a guess
    about which site it came from — a guess that gets silently wrong the day a
    third adapter arrives, and that makes an ad URL impossible to rebuild
    without one.

  - **Never abbreviate an id to make the column narrower.** The id's whole job
    is to rebuild the ad URL; a shortened one cannot, and the row becomes a
    dead end that still *looks* fine. jobup ids are 36-character UUIDs and this
    is where it bites: `jobup:4302da20` renders a blank page, while
    `jobup:4302da20-da24-449c-af7b-2e7577ce45a8` opens the ad.

    Seen on a real ledger on 2026-08-27: **all 55 jobup rows** carried only the
    first 8 characters of their UUID, so not one of them was reconstructible.
    36 were recovered by re-harvesting ids from jobup search results and joining
    on the prefix; **19 were lost for good**, their ads having expired out of
    the index. Recovery is possible but slow, and it only works while the ad is
    still listed — so write the id in full the first time.

    Markdown tables do not need narrow cells. Let the column be wide.
  - A ledger written before this convention has bare numeric ids. Migrate them
    to `linkedin:<id>` in one pass and **say you did it**, rather than carrying
    two conventions and re-deciding on every row.
  - **`—` is a legitimate id** for an application reconstructed after the fact —
    from a mailbox, from memory — where the ad is gone. Such a row cannot be
    deduplicated, so say so in `Note`. It still belongs in the ledger: an
    application that happened counts whether or not its ad still exists.
- **`Posted`** is when the ad was **published**, and only ever that. **Never
  fill it from a card's relative label** — *"Il y a 3 semaines"*, *"Posted 30+
  Days Ago"* — because on a re-listed ad that is the age of the re-listing, and
  nothing on the card says so. Take the board's absolute date where one exists
  (`info-publication` on jobup, `startDate` on Workday, `refreshed` on JOBBKK,
  which names both) and **leave the cell empty where none does**.

  **Two ads tied at 62% were separated by this column on 2026-09-02**, and the
  date that won was seven weeks wrong — `2026-09-01` written from a card whose
  ad was really published `2026-07-14`. The older ad topped the ranking, and
  the ranking decides what gets drafted. **An empty date is a question; a wrong
  one is an answer.** Issue #84.

- **`Match`** carries a `~` prefix while the score is provisional — read from
  the card only. `cover-letter` replaces it with the deep score.
- **`Pay`** is the compensation range for the ad, with the **tier letter that
  says where it came from** — see `shared/salary-estimate.md`. Compact and
  comparable: `CHF 115–135k (C)`, gross, full-time equivalent, currency named.
  This column is what lets the user sort a month of applications by what they
  actually pay, and see at a glance which figures are the employer's and which
  are guesses.
  - **`job-scan` fills it only when a board publishes a figure** — jobup does.
    It never derives one: estimating per ad across a whole sweep is expensive
    and would fill the ledger with low-confidence numbers.
  - **`cover-letter` fills it at step 9**, from its step-3b estimate.
  - **Never overwrite a better tier with a worse one.** An `(A)` from the ad
    outranks a `(B)` board estimate, which outranks a `(C)` derivation. A later
    run that only has a `(C)` leaves an existing `(A)` alone.
  - `—` means not established. **Leave it at `—` rather than inventing a
    figure**, and say at the end of the run that it stayed empty and why.
- **`Note`** is what makes the file useful three weeks later: the reason for a
  low score, for a rejection, or the dossier folder for an application. One
  short clause, not a paragraph.
- **`Location`**: record the **town**, not just the region. `UK · remote` is
  unusable for an unemployment-office declaration (see `shared/modules/`) and
  for judging a commute. When the ad gives only a region or "remote", say so
  explicitly in `Note` (`town to be established`) so the gap is visible before
  it blocks something.

The status vocabulary is **fixed and English** — it is parsed. The `Note`
column, the log and everything you say to the user follow the user's
`languages.interface` setting.

## Merge rules

- **Merge, never overwrite.** Keep every existing row, refresh `todo` rows in
  place (age, status, score), and **insert** new ones where their match puts
  them within their status group. The table stays sorted by match descending
  within each status group — by insertion, not by re-sorting.

  **Never re-emit the whole table to sort it.** On a real ledger that is 474
  rows and 283 918 bytes, rewritten to place a handful of new ones; it is the
  most expensive operation in the whole skill and the likeliest way to lose a
  row. Issue #77.

- **Read the columns you decide on, not the file.** The exclusion set needs
  `ID` and `Status` — 16 531 bytes of a 499 320-byte ledger, **3.3%**. `## Log`
  is 40% of that file and nothing reads it to decide anything; the `Note`
  column is 78.5% of the ads table and is prose for the person, never parsed.
  `skills/job-scan/scripts/ledger.py` reads the narrow view, and it knows that
  **`\|` inside a cell is an escaped pipe rather than a column break** — ten
  of those 474 rows carry one, and splitting on `|` shifts their columns and
  corrupts their status silently.
- **Never rewrite an `applied`, `rejected` or `no-go` row.** Those record what
  actually happened. A later scan may add to the note; it may not change the
  verdict. The one legitimate transition is `applied` → `rejected`, when the
  employer's answer arrives.
- **Build the exclusion set first**, from every row whose status is `applied`,
  `rejected`, `no-go` or `discarded`. Those ads are never proposed again.
- **Append one `Log` line per run** — date, what was searched, what came back.
- **Never strip a `` `WA:<CC>` `` marker.** It records that the employer sits
  outside `location.work_authorization` — *local employment excluded, service
  provision perhaps open* — and it is a route note, never a verdict: it does
  not change a status and it is not a reason to skip a row. Issue #82.

### A ledger written before the `Pay` column existed

Older files have eight columns, not nine. Add the header cell, pad every
existing row with `—`, and **tell the user you migrated their file** — one line,
naming the column added. A ledger silently rewritten under someone is exactly
the failure `shared/never-fail-silently.md` forbids, even when the rewrite is
harmless.

Do not backfill the old rows with derived figures: an application sent in March
was decided on what was known in March, and a number invented today would read
as though it had been.

## `rejected` and `no-go` are not the same event, and the difference is load-bearing

Both end the story of an ad, so it is tempting to collapse them. Do not.

A **`rejected`** row is a **real application**: it went out, it counts toward
the volume the candidate can report, it belongs in any unemployment-office
evidence, and it documents the market's answer. A **`no-go`** row never left the
machine.

Collapse them and every count based on "applied" silently loses the
applications that were turned down — which is precisely the population a
jobseeker is asked about most often. This is not hypothetical: the distinction
was added to a real ledger only after an application that had been refused
stopped appearing in any count, and went undeclared to the unemployment office
as a result.

So when the user reports an employer's answer, move the row from `applied` to
`rejected` — never to `no-go`, and never back to `discarded`.

## Deduplication has a blind spot: the same role, republished

The ledger is keyed by job id, but **the same role republished per country
carries a different id**, so the id check will not catch it. Before creating a
dossier, grep the ledger for the company name:

```bash
grep -n "<Company>" "$JOB_HUNT_HOME/job-pipeline.md"
```

If a row exists for the same company **and a comparable role**, stop and tell
the user: applying twice to one role through regional postings adds nothing and
reads as careless in a shared applicant-tracking system. Mark the new id
`discarded` with the duplicate reason, and only proceed if the user confirms it
is genuinely a different position.

### When you suspect a duplicate but cannot confirm one

**Say so, and let the user decide. Never resolve the doubt yourself in either
direction.**

Silently proceeding risks a second application to one role. Silently discarding
loses a real opportunity — and the user never learns it existed. Both failures
are invisible to them, which is exactly what
`shared/never-fail-silently.md` forbids.

So when the evidence is genuinely ambiguous:

1. **Name the suspicion and its basis** — same intermediary, same location, same
   role family, overlapping dates.
2. **Say precisely what you could not establish**, and what would settle it.
3. **Give your reading**, if you have one, labelled as a reading rather than a
   finding.
4. **Ask, and abide by the answer.** The decision to apply is the user's.

The case this rule was written for: **recruitment intermediaries whose end
client is not named.** Two ads from the same platform, both "based in
Switzerland", both for unnamed employers, are unresolvable by company name — the
company on both rows is the intermediary. They may be one client or two, and the
id check cannot tell. Seen on 2026-08-27, where two such ads turned out to have
entirely different end clients, established only by reading each description to
the end.

**A detail deep in the description often settles it** — a named product, a
sector, a mission statement, a customer count. Read for that before asking, so
the question you put to the user is the one you genuinely could not answer.

## Noise to discard on sight

Record these as `discarded` **with the reason**, so they are never re-proposed:

- **Aggregator and repost farms** — recycled titles, absurd hourly ranges,
  "EMEA (Remote)" with no employer named, posted hours ago, no real company
  behind them. Seed the user's `search.blocklist` with the ones they meet;
  they are regional and they change names often.
- Ads whose stack is explicitly foreign to the candidate.
- Anything already in the exclusion set.
- Anything breaching the commute rule (see `shared/scoring-rubric.md`).
- **Ads that have closed or expired** — see below, because the status is not
  obvious and the row keeps more than the reason.

A `discarded` row still costs one line and saves the same click every week
forever. Write the reason down — "no employer named, aggregator" — because in a
month nobody remembers why.

## An ad that closed is `discarded`, and it keeps its score

A closed or expired ad is **not** a `no-go`: the user decided nothing. It is not
`rejected` either — no application went out to be refused. It is `discarded`,
with the reason and the date in `Note`, so no later scan proposes it again.

Two things stay on the row, and both are easy to throw away by accident:

- **The score**, including a deep one computed minutes before the discovery. It
  cost real work and it describes a real fit. If the role is reposted, having
  the number already there turns a fresh scoring session into a lookup.
- **The dossier folder, when one was written** — and say in the note that it is
  reusable. Employers republish: the same role under a new id is common enough
  that the ledger's whole deduplication blind spot is built around it. A repost
  is exactly where a finished CV, a letter, a sourced pay range and a cleared
  blocker are worth having in hand.

Record whether the **employer** is still alive and hiring, because that is what
decides if the dossier is worth keeping warm. Two rows from one real ledger, three
weeks apart: one company's ad was closed and its domain was parked for sale at a
registrar — nothing will be reposted there. The other closed a single role while
running six other openings across 16 countries — that one is worth watching, and
its 86 % dossier was kept for the repost.

**Verifying closure is `cover-letter` step 1b's job**, before a dossier is
written rather than after.
