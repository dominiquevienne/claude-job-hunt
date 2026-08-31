---
name: job-scan
description: Sweep the job boards the user has enabled (HiringCafe, job-room.ch, France Travail, Workday, Greenhouse, Lever, Ashby, SmartRecruiters, Workable, Teamtailor, SwissDevJobs, SuccessFactors, Solique, umantis, Taleez, Flatchr, Michael Page, fachkraft.ch, sozialinfo.ch, persigo.ch, randstad.ch, Meteojob, HelloWork, APEC, Cadremploi, LinkedIn, jobup.ch, jobs.ch, Indeed) in their own Chrome, score each ad against their real profile, and maintain the shared pipeline ledger at $JOB_HUNT_HOME/job-pipeline.md. Ads already in the ledger are skipped, so each run only surfaces what is new. No board is scanned until it is explicitly enabled. Runs a guided first-time setup if the workspace is not configured yet. Use when the user says "scan LinkedIn", "scan jobup", "find me some jobs", "look for roles that fit me", "refresh my job list", or before running the cover-letter skill.
user-invocable: true
allowed-tools: Bash(*), Read, Write, Edit, AskUserQuestion, ToolSearch, mcp__claude-in-chrome__*
---

# Job scan → pipeline ledger

Sweep a job board in the user's logged-in Chrome, score each ad against their
real profile, and write the results into the **ledger** that the `cover-letter`
skill reads and updates.

**Shared references — read the ones a step points to, not all of them up front.**
They live in this plugin, one level above this skill's folder
(`../../shared/…`, or `${CLAUDE_PLUGIN_ROOT}/shared/…`):

| File | When |
| :-- | :-- |
| `shared/never-fail-silently.md` | **Always.** The rule that outranks the others: nothing skipped, partial or guessed goes unreported |
| `shared/workspace.md` | Step 0 — locating and loading the user's data |
| `shared/setup.md` | Step 0 — only when the workspace is not configured |
| `shared/prerequisites.md` | Any step whose tool is missing — how to help the user fix it |
| `shared/boards/README.md` | Step 2 — which boards are supported and what an adapter owes the skill |
| `shared/boards/<board>.md` | Steps 2–4 — the adapter for each board enabled under `boards:` in `config.yml` |
| `shared/scoring-rubric.md` | Step 5 — scoring, and the commute filter |
| `shared/pipeline-format.md` | Steps 0 and 6 — the ledger's format and merge rules |
| `shared/modules/*.md` | Step 6 — only those enabled in `config.yml` |

**When a board with an adapter fails to sweep, invoke the `board-request` skill**
(broken-adapter mode, its section 2b) before the run ends — the fix belongs
upstream, where it reaches every user, not in a local workaround that the next
plugin update overwrites.

**When a prerequisite is missing at any point, do not stop at saying so.**
Follow `shared/prerequisites.md`: name what it blocks, give the exact command
for the user's platform, offer to run it, verify, and fall back gracefully if
they decline.

## 0 — Load the workspace, then the ledger (always first)

```bash
JOB_HUNT_HOME="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
test -f "$JOB_HUNT_HOME/config.yml" && cat "$JOB_HUNT_HOME/config.yml"
cat "$JOB_HUNT_HOME/job-pipeline.md" 2>/dev/null
```

**No `config.yml` → this is a first run.** Say so in one line, then follow
`shared/setup.md` in full before scanning anything. Do not improvise a profile
and do not scan with defaults: a scan built on guesses produces a ledger the
user has to clean by hand.

**No ledger file** → create it from `templates/job-pipeline.example.md`.

Then build the **exclusion set**: every `ID` in the ledger whose status is
`applied`, `rejected`, `no-go` or `discarded`. Those are never proposed again.
Rows still `todo` stay in the file and get refreshed in place rather than
duplicated.

**Build a second index at the same time: company name → existing rows.** The id
check alone is not enough, because **the same ad carries a different id on every
board**, and boards rename the employer as they please. Keep the company strings
from the ledger to hand; step 3 matches new cards against them.

## 1 — Load the candidate

```bash
# -l 3 = first 3 pages. Do not pipe into `head`: it is the same SIGPIPE trap
# that silently truncated sync-sources.sh, and page count is what you want here.
for f in "$JOB_HUNT_HOME"/profile/*.pdf; do pdftotext -layout -l 3 "$f" -; done
cat "$JOB_HUNT_HOME/candidate.md"
cat "$JOB_HUNT_HOME/repos.md" 2>/dev/null
cat "$JOB_HUNT_HOME/commute.md" 2>/dev/null
```

What matters for scoring: core stack, seniority, leadership history, working
languages, and home base. `candidate.md` also carries the **hard blockers** and
the current **search posture** — read them before deciding what counts as a good
ad, not afterwards.

Home base and the commute limit come from `config.yml` (`location.home_base`,
`location.max_commute_minutes`). Every distance in this skill is measured from
there.

## 2 — Resolve the boards, then set up the browser

`config.yml` → `boards` says which job boards may be swept. **Nothing is
enabled by default and an unconfigured workspace scans nothing** — scanning
drives the user's own browser under their own account, so it only ever touches
a site they explicitly switched on.

**No board enabled → do not scan anything.** Say so in one line, list the
adapters that exist (`shared/boards/`), say what each needs, and offer to
enable one now (`/job-setup boards`). Do not pick a default, and do not scan
"just LinkedIn since it's the common one".

Then give the user the route that works right now, because there is one:
*"you can also just hand me an ad URL from any board — `/cover-letter <URL>` —
and I'll score it and write the documents without any of this."* Never leave
them at a dead end because a board is not configured.

For each board that *is* enabled, read its adapter — `shared/boards/<board>.md`
— **before the first browser call.** The adapter owns its config keys, the URL
recipe, the card extraction, the description reading and the ad-URL rebuild;
this skill owns the scoring, the ledger and the reporting.

- **Enabled but a required setting is empty** → skip that board, name the
  missing key, say how to obtain it, and offer to fill it now. **Never
  half-run** a board on a guessed value.
- **Enabled with no adapter file** → skip it and say so plainly: *"there is no
  adapter for <board> yet, so I can't sweep it automatically — give me an ad
  URL from it and `cover-letter` will do the rest."* Guessing at an untested
  site's markup returns nothing, or the wrong ads, with no way for the user to
  tell. See `shared/boards/README.md`.
- **Adapter present but the board fails anyway** — the search page loads and
  nothing extracts, a selector no longer matches, a login wall or consent gate
  appeared, the URL recipe 404s → **skip that board, keep sweeping the others,
  and invoke the `board-request` skill in its broken-adapter mode (its section
  2b) before the run ends.** Capture the symptom while the browser is still on
  the page; a failure reconstructed afterwards is a guess.

  **A board that broke for this user broke for everyone.** Working around it
  locally is half the job — the issue is what turns one broken scan into a fix
  that ships to every user on the next plugin update. `board-request` handles
  the duplicate check, the privacy pass on search URLs and page dumps, and the
  submission; do not hand-roll any of it here.

  Do **not** file for an anti-bot challenge that the adapter already documents
  as expected (`indeed.md` does), for a logged-out session, or for a search that
  genuinely has no results. Section 2b's table separates the three.

### 2a — Dormant boards: the ones switched off on evidence, not on principle

**Run this once, at the same time as reading `config.yml`:**

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/dormant.py" due \
  --config "$JOB_HUNT_HOME/config.yml"
```

It prints one JSON object per board whose re-check date has passed, and usually
prints nothing at all — which is the normal case and is not an error.

**Never work out those dates yourself.** *"Has 2026-11-28 passed?"* is the kind
of question that gets answered confidently and wrongly, and both wrong answers
cost the user something: one nags them about a board they parked last week, the
other silently buries a board that was worth another look.

A board is **dormant**, not off, when `config.yml` carries `dormant_since`
alongside `enabled: false` — see *The fourth state* in `shared/boards/README.md`
for the shape and the reasoning. **A bare `enabled: false` is a hard off: do not
probe it, do not report it, do not mention it.** The user said no.

For each board the script reports as due:

1. **Run one yield check — not a sweep.** One listing call at the adapter's
   cheapest setting, capped. **No descriptions, no scoring beyond title and
   location, and nothing written to the ledger.** A dormant board must stay
   cheap; a re-check that turns into a full sweep is how this feature ends up
   switched off wholesale.
2. **Never probe a browser board on your own.** LinkedIn, jobup, jobs.ch and
   Indeed run in the user's own Chrome under their own account. For those, a
   passed date means *offering* the re-check and waiting for a yes.
3. **Report it as a measurement, next to the one that put it to sleep** — counts
   against counts, so the user is comparing like with like:

   > **umantis (dormant since 2026-08-30)** — parked because the 10 vacancies on
   > `jobs.bobst.com` were all apprenticeships. Today: 14 vacancies, **3 engineering
   > roles**, one *Software Engineer Full Stack* at Mex (~25 min). Wake it up?

4. **Then let the user decide, and write their answer back:**

   | Answer | What to write in `config.yml` |
   | :-- | :-- |
   | Wake it | `enabled: true`, and **remove all four `dormant_*` keys**. Its own configuration was kept, so this is one line plus a deletion — never a fresh setup interview |
   | Leave it asleep | Set `recheck_after` and `recheck_count` to what `dormant.py next --count <current>` returns. The back-off is 90 → 180 → 365 days |
   | Never again | Delete the four `dormant_*` keys and leave `enabled: false`. That is the hard off, and it is silent from then on |

   **Ask before writing, and ask once.** If the user does not answer this run,
   leave the config untouched — an unanswered question is not a snooze, and
   pushing the date out on their silence loses the very signal they were asked
   about.

**A probe that fails is not a probe that found nothing.** Dormancy records that
a board was *empty*; an error, a 404 or a login wall leaves that claim
unverified, not confirmed. Treat it as any other board failure — `board-request`
in its broken-adapter mode — and say plainly in the report that the re-check did
not happen, rather than letting a silent failure read as another empty quarter.

Then the adapter's **prerequisites block**, which is not optional: the user must
be told that this drives their own Chrome, that it needs the Claude Chrome
extension installed and connected, and that they must be logged in to the board
themselves first. If the extension is absent, follow `shared/prerequisites.md`
— help them install it, and offer the no-browser route meanwhile.

**Read that block rather than assuming it.** Most adapters do not drive the
browser at all. `hiringcafe.md`, `job-room.md`, `france-travail.md`, `apec.md`,
`meteojob.md`, `hellowork.md` and the ATS family (`workday.md`,
`greenhouse.md`, `lever.md`, `ashby.md`, `workable.md`, `teamtailor.md`, `swissdevjobs.md`, `taleez.md`, `flatchr.md`) are plain HTTP and need no extension,
no login and no Chrome. Only `linkedin.md`, `jobup.md`, `jobs-ch.md`,
`indeed.md` and `cadremploi.md` need the user's own browser — and of those,
only LinkedIn needs them logged in. Announcing requirements a board does not have costs the user a
setup they did not need — and when the extension really is missing, HiringCafe
is a sweep that still runs, not just a fallback to `cover-letter`.

The adapter's constraint table is the difference between a scan that works and
forty wasted round-trips. Read it; do not improvise around it.

## 3 — Run the searches

Take the sweep from `config.yml` → `search.queries`. Each entry becomes one
search on each configured board, built with that adapter's URL recipe from
`keywords`, `location`, `posted_within` and `remote_only`.

Quoting a keyword (`keywords: '"Laravel"'`) makes most boards match it strictly
— four results instead of six hundred of noise. Unquoted keywords are matched
very loosely, so **always sanity-check the titles**.

For each search: `navigate` → wait → extract the cards with the adapter's
snippet.

If the user asked for a different perimeter than the configured one, use theirs
for this run — and offer to save it into `config.yml` if they want it to stick.

### Filter out the noise before spending clicks

Record as `discarded`, **with the reason**, so they are never re-proposed (the
full list is in `shared/pipeline-format.md`):

- Aggregators and repost farms, plus anything in `search.blocklist`.
- Ads whose stack is explicitly foreign to the candidate.
- Anything breaching the commute filter below.
- Anything already in the exclusion set from step 0.
- **Anything the company index from step 0 matches to an existing row for a
  comparable role** — see below.

### Cross-board duplicates: the id check will not catch them

The same ad on two boards has two ids, so **the id check cannot see it**. The
only signal available at scan time is the employer's name — and it must be
matched **as a substring, in both directions**, never as an exact cell:

```bash
grep -n "<Company>" "$JOB_HUNT_HOME/job-pipeline.md"
```

Boards write the same employer differently, and an exact match fails on either
side of the difference. Both of these were observed on one real scan, on
2026-08-27:

| Board's string | Ledger's string | Why exact matching failed |
| :-- | :-- | :-- |
| `Université de Lausanne` | `Université de Lausanne — Centre informatique (DCSR)` | the ledger's is **longer** — the board omits the department |
| `Infomaniak Network SA` | `Infomaniak` | the ledger's is **shorter** — the board adds the legal form |

Three duplicates slipped through that scan, including one for an ad the ledger
had already scored in depth two weeks earlier and one the user had explicitly
frozen. All three were caught later at `cover-letter`'s own duplicate gate —
after the scan had reported them as new finds.

**When a match comes back, do not silently discard it either.** Check whether it
is genuinely the same position: same company *and* comparable role. If it is,
record the new id as `discarded` naming the row it duplicates. If the roles
differ, keep it and say so in `Note` — the same employer advertising two real
openings is normal.

**And when you cannot tell, keep the row and record the doubt** — do not discard
on a suspicion. Write what you suspect and what would settle it into `Note`, and
raise it in the run's report. The decision belongs to the user, and step 7 will
put it to them; a row quietly discarded on a maybe is an opportunity they never
hear about. See *When you suspect a duplicate but cannot confirm one* in
`shared/pipeline-format.md`.

**Read the matched row's `Note` before moving on.** It may carry a standing
decision — a freeze on that employer, a pending application, a reason the
company was set aside — that outranks the score on the new card.

### The commute filter

**An ad requiring physical presence further than `max_commute_minutes` from the
home base is discarded, whatever its score.** Apply it *before* spending clicks
on the description — the card already carries the location and the work mode.
The full rule, including how hybrid and remote-with-distant-HQ are treated and
the two traps that catch everyone, is in `shared/scoring-rubric.md`.

Use `commute.md` for travel times rather than guessing. If it does not exist,
estimate — and offer to generate it once, since the same guesses recur every
week.

When a row already in the ledger breaches the rule, flip it to `discarded` with
the reason on the next run — but **never rewrite an `applied`, `rejected` or
`no-go` row**, those record what actually happened.

## 4 — Read the descriptions of the survivors

The description is only readable through a **real click** on the card — see
`shared/boards/linkedin.md` for the click-by-coordinates procedure and the
extraction snippet. Several clicks on one search page chain in a single
`browser_batch`: one screenshot, then three to six descriptions.

Confirm the extracted title matches the ad you meant to open; the list re-orders
between visits.

## 5 — Score each ad

Use `shared/scoring-rubric.md` — the **same rubric the `cover-letter` skill
uses**, so the numbers stay comparable end to end.

Mark a score **provisional (`~`)** when it comes from the card only, because the
description was not opened. Never present a provisional score as if the ad had
been read.

### A hard blocker found here changes the status, not just the `Note`

Step 3 discards ads whose stack is foreign to the candidate — but it works from
the **card**, before any description is open. When the blocker only becomes
visible in the description you just read, **the row is `discarded`, with the
reason. It does not stay `todo` carrying a warning.**

This is not bookkeeping pedantry. **Both selection paths rank on `Match` alone** —
step 7 here, and `cover-letter` step 1 — so a `todo` row scoring 57 % is proposed
ahead of a clean 52 % one, whatever its `Note` says. A verdict written in a note
and not carried into the status will be ignored, because **the status is what
gets read and the note is what gets skipped.**

Observed on a real ledger on 2026-08-27: two rows — a .NET/C# team lead at 57 %
and a .NET/Azure integration role at 35 % — had been read weeks earlier, had
`bloqueur dur` written in their own notes, and were still `todo`. The 57 % one
was then proposed to the user as a top pick, on its score and its excellent
commute, by a run that had just finished writing the rule about reading notes.

So, at this step:

- **Hard blocker** (the ad's primary backend language, a required certification
  or spoken language the record lacks, whatever `candidate.md` lists) → status
  `discarded`, reason in `Note`, and say so in the report. Do not score it into
  the shortlist.
- **Partial gap** → keep it `todo` and score it honestly. That is what the score
  is for.
- **An open question rather than a verdict** — a contract form to clarify, a
  description not yet read — stays `todo`, and the `Note` says what has to be
  answered *before* drafting. This is the one case where a note may legitimately
  carry the word "blocker" on a `todo` row, and it reads as a question, not a
  conclusion.

## 6 — Write the ledger

Merge, don't overwrite — the rules are in `shared/pipeline-format.md`. Keep
every existing row, refresh `todo` rows in place, append the new ones, sort by
match descending within each status group, and append one `Log` line.

**The `Pay` column: record only what the board published.** Some boards attach a
figure to the ad — jobup does — and when the adapter extracts one, put it in
`Pay` with its tier letter (`(A)` if it is the employer's own range, `(B)` if it
is the board's estimate). **Never derive a figure here:** estimating per ad
across a whole sweep is expensive and would fill the ledger with
low-confidence numbers wearing the same clothes as real ones. Leave `—`;
`cover-letter` fills it properly at step 3b when the user picks the ad.

If a module is enabled in `config.yml` (`modules.unemployment_declaration`),
read `shared/modules/<name>.md` and honour what it asks of the ledger — some
modules add a marker to the `Note` column that must never be stripped.

Then report: how many ads were scanned, how many are new, the top matches with
their scores, and **what was discarded and why**. The discards matter — they are
what the user does not have to look at again.

**Then the accounting, per `shared/never-fail-silently.md`.** Give the counts as
*n of m*, never as a bare total: searches run of searches planned, descriptions
read of ads shortlisted, boards swept of boards enabled. Close with the "not
done this run" block whenever anything was skipped, capped or scored
provisionally — a board skipped for a missing key, a search cut short by
throttling, ads scored from the card alone. **A run that ends with nothing new
still owes the user the zero and the reason for it.**

### A board that swept fine and yielded nothing: offer dormancy, don't just say it

**When a board completed its sweep and produced no kept row, say so with the
counts — and then offer to park it.** *"randstad: 18 ads, 4 in range, 0 kept"*
is a fact the user cannot act on; the offer is what turns it into a decision.

The offer has three doors, and the middle one is the point of this whole
mechanism:

| Offer | When it is the right one |
| :-- | :-- |
| **Leave it on** | One empty run is thin evidence. A board swept for the first time, or one whose queries were narrow this run, has not been measured yet |
| **Make it dormant** | The zero looks structural *for now* — but the board is geographically or technically plausible, so a later look is worth one question a quarter. Write the four `dormant_*` keys, with the **counts** in `dormant_reason` |
| **Switch it off** | The board serves a different trade entirely, and no month will change that. `enabled: false`, no `dormant_*` keys, silent from then on |

**Put the counts in `dormant_reason`, never an adjective.** *"nothing
relevant"* tells the user nothing three months later; *"10 vacancies, all
apprenticeships"* lets them decide in one read — and it is what the re-check
compares against.

**Two boards with the same zero can deserve different doors, and usually do.**
On a real run on 2026-08-30: sozialinfo returned 687 ads with 1 in range —
social-sector work, a trade the candidate will still not be in next year.
umantis returned 10, all of them apprenticeships, from an employer **25 minutes
away** on an adapter that worked perfectly. Identical zeros; the second is
timing and the first is not. Reading them the same way is how the good bet gets
thrown out with the bad one.

**A board that failed is named in that block with its issue URL**, or with the
fact that no issue was filed and why — the user declined, `gh` was unavailable,
a duplicate was already open. *"jobup returned nothing"* on its own is the
silent failure this whole rule exists to refuse: the user cannot tell a broken
adapter from an empty market, and those call for opposite reactions.

## 7 — Hand off to `cover-letter`

Propose the top `todo` rows in match order. When the user picks one, invoke the
`cover-letter` skill with the ad URL rebuilt from the `ID`; it re-scores the ad
in depth, gates on go/no-go, and writes the resulting status back into the
ledger.

**Read each row's `Note` before proposing it — match order is not the whole
ranking.** The rows you are about to recommend include ones written weeks ago by
earlier runs, and a `todo` row can carry a verdict its status never received: a
blocker found when its description was read, a hold on that employer, an
application already open there.

A row whose note settles the matter does not belong in the list — skip it, and
offer to correct its status. A row whose note raises an **open question** belongs
in the list, with the question named next to the score, because that question is
what `cover-letter` must resolve before drafting.

**Never present a row on its score and its commute alone.** That is exactly how a
.NET/C# role whose own note read *"bloqueur dur"* was recommended as a top pick
on a real ledger on 2026-08-27 — by a run that had, hours earlier, written the
rule about reading notes.
