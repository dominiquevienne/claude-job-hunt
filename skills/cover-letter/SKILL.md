---
name: cover-letter
description: Draft a tailored cover letter and a matching ATS-compliant resume for a specific job ad, after scoring the fit and estimating what the role pays for this candidate. Input is the job-ad URL; with no URL, it picks the highest-scoring `todo` ad from the pipeline ledger that job-scan maintains. The user's own profile documents are the source of truth — nothing is invented. Outputs markdown + PDF into a per-application folder, and can optionally fill a LinkedIn Easy Apply form in the user's own Chrome (the user always validates the send). Runs a guided first-time setup if the workspace is not configured yet. Use when the user says "draft a cover letter for <URL>", "apply to this job <URL>", "tailor my resume for <URL>", or invokes it with no argument to take the next pending ad.
user-invocable: true
allowed-tools: Bash(*), Read, WebFetch, Write, Edit, AskUserQuestion, ToolSearch, mcp__claude-in-chrome__*
---

# Tailored cover letter + resume

Given a **job-ad URL**, produce a tailored **cover letter** and a concise
**resume**, both in the **language of the job ad**, as markdown **and** PDF,
saved into a per-application folder.

**The user's real history is the source of truth — never fabricate.** Do not
invent employers, job titles, dates, skills, tools or certifications that are
not in the record. If the ad requires something the user lacks, leave it out of
the documents and flag the gap to them at the end.

**Shared references** — in this plugin, one level above this skill's folder
(`../../shared/…`, or `${CLAUDE_PLUGIN_ROOT}/shared/…`):

| File | When |
| :-- | :-- |
| `shared/never-fail-silently.md` | **Always.** The rule that outranks the others: nothing skipped, partial or guessed goes unreported |
| `shared/prerequisites.md` | Any step whose tool is missing — how to help the user fix it |
| `shared/workspace.md` | Step 0 — locating and loading the user's data |
| `shared/setup.md` | Step 0 — only when the workspace is not configured |
| `shared/interview-debrief.md` | Step 2b — when the user reports back on a meeting instead of preparing one |
| `shared/scoring-rubric.md` | Step 3 — the go/no-go score |
| `shared/salary-estimate.md` | Step 3b — the compensation range, and where it must never go |
| `shared/pipeline-format.md` | Steps 1, 4 and 9 — the ledger |
| `shared/ats-open-check.md` | Step 1b — asking an employer's ATS directly whether the ad is still open |
| `shared/boards/linkedin.md` | Step 8 — before touching the browser |
| `shared/modules/*.md` | Step 4 — only those enabled in `config.yml` |

## 0 — Load the workspace

```bash
JOB_HUNT_HOME="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
test -f "$JOB_HUNT_HOME/config.yml" && cat "$JOB_HUNT_HOME/config.yml"
```

**Then, once, quietly:**

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-.}/bin/version-check.py"
```

**It prints nothing when the workspace is current**, which is the normal case
— no version line, no reassurance. When a newer release exists it prints one
short block naming it and the host commands that fetch it. **Pass it on as it
is and carry on**: updating is the host's action, the plugin changes nothing,
and the user's task is not interrupted for a version number. Cached for a day;
every failure is silence. Issue #79.

**No `config.yml` → first run.** Say so in one line, then follow
`shared/setup.md` in full before drafting anything. A resume written from
guesses is worse than no resume.

## Inputs & sources

Everything the documents may claim comes from the workspace — see
`shared/workspace.md` for the precedence rules:

- **`profile/`** — the user's own exports or CV. The factual record.
- **`candidate.md`** — contact block, target role families, hard blockers,
  standing resume content, and corrections that override a stale export. Read
  it in full, every run. It is authoritative for the YAML headers of both
  documents: never re-derive the contact line from the PDFs when it exists.
- **`repos.md`** (optional) — technologies verified in the user's own
  repositories, with their real depth and an explicit "never claim these" list.
  Exports systematically *understate* the stack, so when this file exists it is
  **not** optional reading. A skill may be claimed when it appears in the
  exports **or** is documented here — and **at the strength stated there, never
  above it**.
- **`job-pipeline.md`** — the ledger (`shared/pipeline-format.md`). Read at the
  start, written back at the end. If it does not exist, skip the lookup and
  don't write a status; creating the ledger is `job-scan`'s job.

**Refreshing the exports.** When the user says they have updated their profile,
run `sync-sources.sh "<Full Name>" "$JOB_HUNT_HOME/profile"` (this skill's
folder). If a needed document is missing from `profile/`, offer to run it — and
if the source is missing too, give the exact export procedure from
`shared/setup.md` step 1 rather than a vague "please export your profile".

## 1 — Parse the job ad

**No URL given → take the next pending ad from the ledger.** Do not stop and
ask which one. Read `job-pipeline.md`, pick the **highest-`Match` row whose
status is `todo`** (ties go to the more recently posted ad), rebuild its URL
from the `ID`, say in one line which ad you picked and why, and carry on. The
go/no-go gate in step 3 is where the user gets their say.

**Read the row's `Note` before picking it — the score alone is not the ranking.**
A `todo` row can carry a verdict its status never received: a blocker found when
the description was read, a standing decision to hold off on that employer, a
pending application at the same company. Ranking on `Match` walks straight past
all of it.

- **The note records a settled blocker** → skip the row, say why in one line,
  and take the next. Offer to correct its status, since a row like that should
  not have been in the `todo` pool (see `job-scan` step 5).
- **The note records an open question** — a contract form to clarify, a
  description never read → the row is still a legitimate pick, but **that
  question is the first thing step 3 puts to the user**, before any drafting.
- **The note records a hold on the employer** — a freeze pending an answer, an
  application already open there → surface it and let the user decide. Do not
  lift a hold they set.

Seen on a real ledger on 2026-08-27: a .NET/C# role whose own note read
*"bloqueur dur … le management seul ne rachète pas un rôle qui exige d'écrire du
.NET"* was proposed as a top pick, on its 57 % and a 30-minute commute.

A provisional score (`~`) still counts for ranking; step 3 replaces it either
way. If **no** row is `todo`, say so, report how many ads are in the file and
when the last scan ran, and offer to run `job-scan` rather than inventing a
target.

When a URL **is** given, use it and ignore the ranking. **Any URL works** — this
skill needs no board adapter and no browser. It is the route for every board on
earth, including the ones `job-scan` cannot sweep.

**If the URL is from a board with no adapter** in `shared/boards/`, note it and
invoke the `board-request` skill *in the background of your reasoning* — it
decides whether the site is really a board and, if so, records what an adapter
would need. Do this **without interrupting the application**: mention it in one
clause at the end, never as a question in the middle. A user who asked for a
cover letter did not ask to file a feature request.

**One board leading to another is the exception — there you ask.** The rule above
is about the URL the *user* handed you, and it stays silent because they did not
ask for a feature request. But when following a board takes you to a **second,
different board** — most often an employer-owned careers site or ATS reached
through an outbound *apply* link (step 1b does this by design) — that is a board
the user never mentioned, and you found it on your own initiative. **Ask them,
with `AskUserQuestion`, whether to file a `board-request` for it, and prefill the
question with everything you already established**: the host, the vendor or "own
ATS", the shape of a vacancy URL, whether the description is served without
authentication, and how you got there. Asking costs one option in a question the
gate is already putting to them; discovering the board a second time, months
later, costs the whole investigation again.

Fold it into the go/no-go gate's `AskUserQuestion` call rather than raising it on
its own — a second, separate prompt is the interruption the rule above exists to
prevent.

**And the third case, which is worth more to the user than either: the adapter
exists and they never switched it on.** `job-scan` could have been sweeping
this board every week; instead they are pasting URLs from it one at a time.
Unlike a `board-request`, which gives them nothing today, this is **one line in
their own config that changes their next scan** — and they have just proved
their interest by handing you an ad from it.

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-.}/skills/job-scan/scripts/board_offer.py" \
    check --board <adapter name>
```

**Offer only on `"state": "absent"`.** A board can be off for three different
reasons and only one of them is an omission:

| State | What it means | Offer? |
| :-- | :-- | :--: |
| **`absent`** | not in `boards:` at all — **nobody ever decided** | **yes** |
| `enabled` | already swept | no |
| `off` | `enabled: false`, no dormancy — *"never probed, never reported, never proposed"* | **no** |
| `dormant` | a measured bet; `dormant.py` owns its re-check date | **no** |

**Re-offering a board somebody switched off on purpose is nagging**, and it
would cost the offer its credibility everywhere else. The script draws that
line; do not redraw it by eye.

**Name what the board needs, in the offer itself.** Offering to enable a board
that fails on its next run for a missing key is worse than saying nothing —
`requires` carries the adapter's own declared settings and `credentials_hint`
the file it expects (`~/.adzuna.env`, say). When `requirements_declared` is
`false`, say **"this adapter does not declare its settings"** rather than
implying there are none: 49 of 67 adapters carry that table, and the other 18
have not been asked.

**Where it goes: one more option in the go/no-go gate's `AskUserQuestion`**, the
same as the second-board case, and for the same reason. Two choices, not three:
*enable it* (you write the `boards:` entry and say what still needs filling in)
or *not now* (nothing is written, and nothing is remembered).

**If they want it never proposed again, the vocabulary already has the word:**
`enabled: false` with no `dormant_since` is the hard off, and the table above
makes this silent from then on. Write it only if they ask for it — no
`declined:` key is invented, because the state already exists and `dormant.py`
already reads it.

Then, in both cases: WebFetch the URL and extract **company**, **role**,
**location**, **language of the ad**, key **responsibilities**, **required
skills**, and any **must-haves**. LinkedIn URLs may 301 to a country host — if
WebFetch reports a cross-host redirect, call it again with the redirect URL. If
the page is gated or empty, ask the user to paste the ad text.

Set **`LANG`** = the ad's language. Everything in the candidate-facing documents
is written in `LANG`, whatever `languages.interface` says.

## 1b — Is the ad still open? Check before you spend anything

**A successful WebFetch is not proof the ad accepts applications.** Boards serve
the full description of a closed ad, and the *"no longer accepting
applications"* banner is rendered client-side — it never reaches the fetched
markdown. The call that just gave you the responsibilities and the must-haves
says nothing about whether anyone is still reading applications.

Two signals put an ad in the at-risk band. Neither is conclusive alone:

- **Age** — roughly three weeks or more since it was posted.
- **Competition** — a high applicant count, say 100 or more.

**And one signal that is conclusive on its own, when it is there: a stated
expiry date in the past.** It needs no request to any ATS — the employer
published it. Look for it before doing anything else:

- **`validThrough`** in a `JobPosting` block on the ad page. Prospective
  (`ohws.prospective.ch`) carries it on every ad, and Solique on several of its
  tenants — see `shared/ats-open-check.md`.
- **A deadline in the ad text**, which boards' structured data often carries
  even when their visible page does not.

**A date in the past is a reason to check, never a substitute for checking.**
Measured 2026-09-02: an ad carrying *"Délai de postulation : 15.08.2026"* was
still being served on **02.09 — eighteen days later** — present among the 32
current roles in its ATS's own API, its page answering 200 with one
`JobPosting` block against zero on a control id. **It had been discarded on
2026-08-27 on exactly the reasoning this paragraph used to prescribe, without a
request.**

So a past deadline **triggers** the verification below. It never replaces it,
and it is never on its own a reason to write `discarded`. A date in the future
is likewise not proof the ad is open — the employer can fill the role early —
but it is a genuine reason to lower the age weighting.

**This was the only place in this file that authorised skipping the check, and
it is the one that failed.** A rule that dispenses with verification is the
only kind that can fail without leaving a trace. Issue #89.

**And a gap you are about to write into the `Note` is proven against
`profile/.text/` first.** This is where the chain starts: a gap asserted here
becomes a received truth downstream — `interview-prep` reads this `Note` and
tells the candidate about themselves minutes before they repeat it to an
employer, **and nobody catches a false negative, because the candidate has no
reason to doubt their own file.** Breaking the chain at the reading end is too
late; it breaks at the writing end. Issues #63 and #50.

**And where a row was already discarded that way, flag it — do not silently
re-open it.** `no-go` and `discarded` record a decision; **the plugin does not
reverse a decision it did not take.** Say the ad appears to be open, and let
the user decide.

When either at-risk signal holds, verify **before drafting**.

> **One rule covers both directions: the employer's ATS decides, and everything
> else is a hint.** A board that keeps serving a description, a deadline that
> has passed, a redirect, a status code — all of them are reasons to ask, and
> none of them is an answer. The two failures measured on 2026-09-02 are
> mirrors of each other: an ad that was **closed and looked open** (a redirect
> to a category page carrying twenty valid `JobPosting` blocks) and an ad that
> was **open and looked closed** (a deadline eighteen days past). Issues #88
> and #89.

1. **Find the employer's own posting, not their careers page.** Take the ad's
   external apply link, or search for the company and role plus their applicant
   tracking system. A closed posting on Factorial, Workday, Greenhouse, Lever or
   SmartRecruiters says so unambiguously — *"This job opening doesn't exist
   anymore"* — where a board keeps serving the description as if nothing
   happened.
1b. **On a board URL, read the status before the body — and never conclude
   "open" from a page reached by a redirect.** JobCloud's boards (jobup,
   jobs.ch) answer with four different states and the body alone separates
   none of them: a **`410`** serves the ad's own text and its own
   `JobPosting` block with `isActive: false`; an **expired** ad **redirects**
   to its trade's category page, which carries **twenty** valid blocks and not
   one mention of the job; a **`404`** means the id never existed; and only a
   plain `200` with no redirect is the ad. `shared/boards/jobup.md` has the
   table. **A check that counts `JobPosting` blocks calls the first one open
   and the second one open too.**

2. **A role missing from the employer's careers page is a strong signal, not a
   weak one**, when that page is listing their other openings. Do not file it as
   a note and carry on. **The clause carries the whole rule: first confirm the
   page actually listed something.** A client-rendered careers site returns a
   navigation shell with no openings at all, for anyone, always — SAP
   SuccessFactors does exactly this — and reading that emptiness as closure
   concludes from a page you never saw. `shared/ats-open-check.md` gives the
   detection rule and the vacancy URL that does answer.
3. **Report the result at the gate as a finding**, naming the route you used. If
   you could not verify, say that in those words — never let silence imply the
   ad is live.

Do not guess a careers-page URL beyond a single attempt; the board's own search
and a web search for the ATS posting are the routes that work.

**When the ad's apply link points at an applicant tracking system, ask it
directly — see `shared/ats-open-check.md`.** One request to the employer's own
vacancy URL settles in seconds what a careers-page search only hints at, and it
answers unauthenticated on the hosts recorded there. Some hosts say *closed* with
a status code (umantis answers `403`); others cannot say it at all (Jobvite,
SAP SuccessFactors and Refline never return an error, so they are usable only to
confirm an ad is **listed**, never to conclude it is gone — on Refline the tell
is a `JobPosting` block that is present or absent, not the status). **Read the host's row before
trusting either direction**, and if the host is not recorded, say you could not
verify rather than guessing.

**Whatever this step turns up, note the host.** Verifying an ad routinely lands
you on a board nobody asked about — an employer-owned careers site, or an ATS
with no adapter in `shared/boards/`. That is the board-to-board case in step 1,
and it is a question for the user at the gate, not a silent note: carry the host,
the vacancy-URL shape and whether the description came back unauthenticated
forward to step 3, and offer the `board-request` there.

**When the ad is closed, stop.** Say so, mark the row `discarded` with the
reason and the date (`shared/pipeline-format.md`), keep the score you have, and
offer the next row. Never draft a dossier for a role nobody can apply to.

Seen on 2026-08-27, and it is the whole reason this step exists. A Senior PHP /
Full-Stack role scored **86 %** — the strongest fit in the pipeline — on a
description WebFetch returned in full. The ad was a month old with **200+
applicants**, and the employer's careers page listed six openings, none of them
technical. That was reported at the gate as a reserve, and the dossier was
written anyway. The role was gone: LinkedIn showed *"No longer accepting
applications"*, and the employer's own ATS posting answered *"This job opening
doesn't exist anymore."* **One request to that URL, before drafting, would have
settled it.** Two earlier ads in the same ledger died the same way at 77 % and
~75 %; this was the first where a full CV and letter were spent on one.

## 2 — Load the candidate

1. `candidate.md` — the contact block and the standing rules.
2. The documents in `profile/`. **If the main profile document is missing**, run
   `sync-sources.sh`; if it is still missing, stop and give the export procedure
   from `shared/setup.md`.
3. `repos.md`, if it exists.

**Then make the record searchable, once:**

```bash
test -d "$JOB_HUNT_HOME/profile/.text" || \
  "${CLAUDE_PLUGIN_ROOT}/skills/cover-letter/sync-sources.sh" "<Full Name>"
```

**`candidate.md` and `repos.md` are not a skills inventory** — the inventory is
in the `profile/` PDFs, and `.text/` is those PDFs as plain text. Step 3 needs
it for every must-have the ad names, in both directions, and doing that from
the PDFs directly is what made the wrong answer cheaper than the right one.
Issue #63.

## 2b — If the user is talking about a meeting, this is not the skill

**A user who says "I have an interview for X" or "I had the interview" is not
asking for a letter.** Hand over to **`interview-prep`**, which covers both
halves: the briefing sheet before, and the debrief after. It exists because the
most useful column of a debrief — which prepared questions came back
unanswered — only exists if one object holds both.

Do not build a sheet here, and do not run the debrief here.

## 3 — Score the fit, then STOP for a go/no-go

**Do not draft anything before this gate.** Writing a tailored application for a
job the user cannot plausibly get wastes their time and their credibility — the
honest answer is sometimes "don't apply".

Score with `shared/scoring-rubric.md`, and read *Before a score is written*
there first — **it is a check with two directions and both are required**:
every must-have the ad names is matched against `profile/.text/`, and every gap
you are about to assert is proven there. One measured session produced both
errors at once: a false GraphQL gap (65% → 80%) and a stated CMS must-have
simply left out of the scoring (63% → 72%).

Then report, **before drafting**:

1. The **ratio**, with its band label.
2. **Two or three sentences** on why — the genuine matches, then the blockers,
   naming the specific unmet must-haves.
3. A clear **recommendation** (apply / apply with caveats / don't apply),
   measured against the user's own `thresholds.apply_from`.
4. **What step 1b established about the ad still being open** — verified live,
   verified closed, or not verified and why. A strong ratio is the case where
   this gets skipped, and it is exactly the case where it costs the most.

## 3b — Estimate what it pays, for this candidate

Part of the same gate, reported in the same breath as the ratio: an evening
spent on an application is spent on the money too, and finding out at the offer
stage is finding out too late.

Follow `shared/salary-estimate.md`. In short: work down its three tiers —
**stated in the ad**, **published by the board**, then **derived** — and say
which one you used. Give a **range, never a point figure**, with its basis in
one line (gross, period, instalments, workload, currency, what is excluded).
Then place the candidate inside that range using the fit ratio you just
computed and what the record shows beyond the ad's asks.

**When you are reasoning from general market knowledge rather than a source you
checked, say so in those words and widen the range.** Never cite a report you
did not read — a plausible figure with a fabricated source is the single most
damaging thing this skill can produce.

If the market or the role is one you cannot credibly assess, **say that and
give no number.** An empty space is a valid answer; a range invented to fill it
is not. Either way it is reported, per `shared/never-fail-silently.md`.

Three lines at the gate, next to the ratio — not instead of it. Flag it only
when it is decision-relevant: below the user's `compensation.floor`, a foreign
employer whose social-security system changes take-home and entitlements, or an
agency posting whose advertised range is the agency's rather than the client's
budget.

Then ask whether to continue, with `AskUserQuestion`. Offer: proceed anyway,
stop, and — where it makes sense — an angle that would change the framing (pitch
a lead role rather than the hands-on one advertised). **Only continue to step 4
once the user says so.** Never soften a bad ratio — or a poor range — to make
the application feel worth writing.

### The right to work, if `work_authorization` is configured

**Check it before drafting, not after** — the cost this exists to prevent is a
complete dossier written for an ad the user cannot take. A London role scored
74%, the best stack match in that ledger; CV, letter and rendered PDFs were
produced, and the user closed it in one sentence: *"pas éligible, permis de
travail UK"*. Issue #82.

If `config.yml` carries `location.work_authorization` and the **employer's**
country is outside it, say so here, in the gate's own question — and say it as
two routes, never as a refusal:

> **Local employment in GB would need sponsorship you have not declared.**
> Invoicing GB from here is a different legal object and may well be open — if
> this employer will work B2B, nothing above blocks it.

**`candidate.md`'s *employment vehicle* section is the question below this
one**, not this one. Local contract, ANOBAG or B2B is a choice among routes
that exist; **this is whether the employed route exists at all**, and without
the right to work the choice of vehicle does not arise.

**Score the ad anyway and show the score.** The number is what tells the user
the job was worth wanting, and it is what makes a B2B approach worth
attempting. **With no `work_authorization` key, this section does not apply** —
say nothing.

**This gate is also where step 1's board questions ride.** It always fires on
the URL path, which is what makes it the only place they may be asked: a
`board-request` for a second board found through an apply link, and — when
`board_offer.py` reported `"state": "absent"` — the offer to enable the board
this ad came from. **One call, whatever it carries.** A separate prompt for
either of them is the interruption step 1 forbids, and the user answering a
go/no-go has not asked to be asked twice.

**On a no-go:** update that ad's row to `no-go <YYYY-MM-DD>` with the reason
in `Note` (one short clause — the unmet must-have, the language, the commute,
the pay). That row is then excluded from future scans, so the reason has to be
readable later. **Write the step-3b range into `Pay`** as well — especially when
money is why the user said no, since that is the row they will want to find
again if the company reposts at a better figure. Append a row if the ad was not
in the file. Then stop.

## 4 — Create the application folder

**First: check for a same-company duplicate. This is not optional.**

```bash
grep -n "<Company>" "$JOB_HUNT_HOME/job-pipeline.md"
```

The ledger is deduplicated by job id, but **the same role republished per
country carries a different id** — the id check will not catch it. If a row
exists for the same company **and a comparable role**, stop and tell the user;
mark the new id `discarded` with the duplicate reason. Only proceed if they
confirm it is genuinely a different position.

**When you suspect a duplicate but cannot confirm one, the user decides — not
you.** Do not proceed on the assumption it is fine, and do not discard on the
assumption it is not: one risks a second application to a single role, the other
throws away a real opportunity, and **the user sees neither**.

Name the suspicion, say what you could not establish and what would settle it,
give your reading labelled as a reading, then ask. The full rule and the case it
was written for — intermediaries whose end client is not named — are in
`shared/pipeline-format.md`.

**Read the description to the end first.** A sector, a named product or a
mission statement usually settles it, and a question you could have answered
yourself is a question worth not asking.

**Never write into a directory that already exists** without checking what is in
it. If `Write` reports *updated* rather than *created*, an earlier dossier is
being overwritten — stop and resolve it.

Then sanitize `<Company>` and `<Role>` (letters, digits, dashes; spaces to
dashes) and **prefix the folder with today's date**:

```
$JOB_HUNT_HOME/<YYYYMMDD>_<Company>-<Role>/
```

Take the date from the environment, not from the ad's publication date — it
records when the dossier was produced.

**Why the prefix.** Every application reuses the same two output filenames, so
with a dozen folders the PDFs are indistinguishable outside their directory —
and the real risk is attaching the wrong CV to an application. The date prefix
sorts them chronologically and identifies each dossier unambiguously, while the
filenames themselves stay clean and ATS-neutral.

Write the parsed ad to `job-ad.md` there (title, company, location, link,
requirements, responsibilities) so the dossier is self-documenting.

Add a **`## Compensation`** section carrying step 3b's range with its tier, its
basis and today's date. That is what makes it re-readable in three weeks, when
an interview reaches the money conversation and the user needs to remember where
the number came from — and whether it was a figure the employer published or one
you derived.

**If a module is enabled** in `config.yml` (`modules.unemployment_declaration`),
read `shared/modules/<name>.md` now and capture what it asks for **while the ad
is still open** — that is the whole point of doing it here rather than weeks
later.

## 5 — Draft the resume (`resume.md`) — tailored, ATS-compliant

Strictly truthful, reordered to foreground what THIS ad wants. Length follows
`documents.resume_length` in `config.yml`. `render.sh` styles it via
`resume-template.tex`.

**ATS compliance is mandatory** — the resume must parse cleanly in applicant
tracking systems:

- **Single column, linear top-to-bottom flow.** No tables, no multi-column
  layouts, no text boxes, no sidebars — parsers read left-to-right, top-to-
  bottom and scramble columns.
- **Standard section headings** the parser recognises, in `LANG`. EN: `Summary`
  / `Experience` / `Skills` / `Education` / `Certifications` / `Languages`.
  FR: `Profil` / `Expérience professionnelle` / `Compétences` / `Formation` /
  `Certifications` / `Langues`. Avoid creative section names.
- **No graphics, icons, logos, photos, charts or rating bars.** Skill levels are
  words, not dots or progress bars.
- **Plain bullets (`-`) and plain text only.** No emoji, no decorative glyphs.
- **Contact details in the body**, not in a page header or footer — parsers
  routinely drop those.
- **Spell out then abbreviate** key terms so both forms are searchable, e.g.
  "Continuous Integration (CI/CD)", "Amazon Web Services (AWS)". Mirror the
  ad's exact keywords wherever they are genuinely true of the user — ATS ranks
  on keyword match.
- **Standard, consistent date format** (`MM/YYYY – MM/YYYY`), `present` for
  current roles.
- **Selectable text** — the pandoc/xelatex pipeline already emits real text.
  Never embed the content as an image.
- Keep job titles, employers and dates on their own clearly-labelled lines so
  the parser can map role → employer → dates.

Structure — name, title and contact go in a **YAML metadata block** (the
template renders the header from them), then the body:

```markdown
---
name: "<Full name>"
jobtitle: "<Target title> · <secondary> · <tertiary>"
contact: "<email>  ·  <phone>  ·  <city, country>  ·  <linkedin>  ·  <github>"
---

## Summary

<2–3 lines rewritten to mirror the ad's role and top requirements, using only
real strengths. Weave in the ad's key keywords where truthful.>

## Skills

- **<Group>:** <skills the ad asks for that the user genuinely has, first>

## Experience

### <Role> — <Company>
*<City> · MM/YYYY – MM/YYYY*

- <achievement-oriented bullet, chosen for relevance to the ad>

### <next role...>
```

Draw on **both** the exports and `repos.md` — omitting what only `repos.md`
records silently under-sells the user. Mirror its **depth wording**: label
prototype-level work as such rather than implying production depth, and give a
`repos.md` project its own `## Projects` entry when the ad makes it relevant.

**Formatting rules the template depends on:**

- The city/date line is a single `*italic*` line.
- **Always leave a blank line between the `*meta*` line and the bullet list**,
  and after each `## heading`. Without it, pandoc folds the bullets into the
  meta paragraph and they render as literal `-` characters.
- Order roles by recency; give the most relevant one or two bullets each. Fold
  the oldest roles into a single italic "Earlier experience (YYYY–YYYY) — …".
- **Never alter titles, employers or dates.**

End with `## Certifications` (real ones, ad-relevant first), `## Education` and
`## Languages` — **working languages only**; a language listed as passive in
`config.yml` never appears here.

Apply anything `candidate.md` records under *standing resume content*.

## 6 — Draft the cover letter (`cover-letter.md`)

Tailored prose in `LANG`, ~250–400 words, honest and specific. Same YAML header
as the resume (rendered by `letter-template.tex`).

```markdown
---
name: "<Full name>"
jobtitle: "<Target title> · <secondary> · <tertiary>"
contact: "<email>  ·  <phone>  ·  <city, country>  ·  <linkedin>"
---

\hfill <City>, <today's date in LANG's convention>

**<Company>**\
<Recipient, or the HR department if unknown>\
<Company city>

**<Subject line: application for <Role>>**

<Salutation appropriate to LANG.>

<Opening: state the role and a genuine hook — what draws the user to this
company and this role.>

<Body 1: map two or three of their REAL, most relevant experiences directly to
the ad's key requirements. Be concrete — only what is true.>

<Body 2: why this company specifically, and the value they bring.>

<Closing: availability, interview interest, courteous sign-off.>

\vspace{45pt}

\hfill <Full name>\hspace{1.5cm}
```

**Formatting notes:** `\hfill` before the date and the signature right-aligns
them; the trailing `\hspace{1.5cm}` keeps the name off the right margin; the
`\vspace{45pt}` leaves room to sign by hand. End recipient-block lines with a
trailing `\` to force line breaks.

**Signature.** If `$JOB_HUNT_HOME/signature.png` exists, replace the `\vspace`
placeholder with the `\includegraphics` block documented in `candidate.md`,
sized by **height** (the image is near-square; a width-based include blows it
out of proportion). If there is no signature file, keep the `\vspace` — a letter
signed by hand after printing is entirely normal.

**No figure of any kind goes in the letter** — not the step 3b estimate, not the
user's expectation, not a rate. That number is theirs to disclose at a moment of
their choosing, and a letter that opens with a price has made the choice for
them. The only exception is an ad that explicitly *requires* a salary
expectation in the application, and then you ask the user for the figure and use
theirs.

Do not claim skills the user does not have; if the ad wants X and they lack it,
omit it or honestly frame adjacent experience — never assert a false
proficiency. `repos.md` is fair game for concrete proof points, but **respect
its confidentiality notes**: work under NDA is described at architecture level
only, with no endpoints, internal names or ticket references.

## 7 — Render to PDF

```bash
./render.sh <folder>/resume.md       <folder>/<Family>_<Given>_<Company>.pdf
./render.sh <folder>/cover-letter.md <folder>/<Family>_<Given>_<Company>_CoverLetter.pdf letter
```

(`render.sh` sits in this skill's folder; the name parts come from
`config.yml` → `candidate`.) It uses pandoc + xelatex and opens each PDF when
it is done. If it reports a missing tool it prints the install command for the
platform — relay it and re-render; the markdown is already saved.

**Always check the page count** — `pdfinfo <file>.pdf | grep Pages`. Do not
trust Spotlight metadata (`mdls`): it serves a stale cache and reports the
*previous* render's count.

- **The letter must be exactly one page.** It overflows easily, and what spills
  is usually the signature block or just the typed name, alone on page 2, which
  looks like a mistake. Verify with `pdftotext -f 2 -l 2 <file> -` — if page 2
  exists at all, trim. **Fix it by cutting the body**, never by shrinking the
  signature or tightening `\vspace`.

  **Diagnose before cutting — the word count is often the wrong culprit.** Read
  what page 1 actually ends with:

  ```bash
  pdftotext -layout -f 1 -l 1 <file>.pdf - | grep . | tail -3
  ```

  - **Page 1 ends mid-body** → the body is genuinely too long. Cut prose.
  - **Page 1 ends on the closing salutation** → the body already fits, and the
    signature block alone is overflowing. You need roughly **four to five lines**
    of room, so cutting ten words will not do it however many times you try.

  **There is no fixed word ceiling — it depends on the recipient block.** Each
  address line costs a line of body. Measured on real letters with a 2.2 cm
  signature:

  | Recipient block | Usable ceiling |
  | :-- | --: |
  | 2 lines (company, country — employer not named) | **~300 words** |
  | 3 lines (company, street, town) | **~285 words** |
  | 4 lines (company, department, street, town) | **~265 words** |

  Roughly 15 words per address line, measured across three real letters.

  A long `jobtitle` in the YAML header costs another line when it wraps.

  Treat those figures as the starting estimate, not the rule: write, render,
  read the tail of page 1, and cut against what you see.
- **The resume follows `documents.resume_length`.** On `generous`, never trim
  substance for pagination; fix only genuine layout faults (orphan headings,
  split entries).

**Never post-process with Ghostscript.** `-dPDFSETTINGS=/ebook` shrinks a letter
from 169 kB to 22 kB, but it re-encodes the fonts and loses the ToUnicode
mapping for ligatures: the page looks identical while the extracted text
silently rots ("qualifications" → "quali cations"). For an ATS-parsed CV that is
fatal. If a PDF is heavy, the cause is almost always an oversized signature
image, not the text.

## 8 — Assisted Easy Apply (optional, LinkedIn only)

**Only on the user's explicit request** — "apply", "send it", "do the Easy
Apply". Never start this on your own: generating the dossier is the default end
of the skill.

This fills the LinkedIn **Easy Apply** form in the user's own Chrome. **You
never submit it alone** — the final send is gated on the user.

**Applies to LinkedIn Easy Apply only.** If the ad's button says *Apply* rather
than *Easy Apply*, it redirects to an external ATS (Workday, Greenhouse,
SmartRecruiters, Taleo…): those need an account, ask bespoke questions and often
gate on a captcha. **Do not attempt them** — open the URL, say which ATS it is,
and say which files to attach.

### 8.1 — Prerequisites and setup

Read `shared/boards/linkedin.md` first. Its prerequisites are not optional:
tell the user that this drives **their own Chrome**, that it requires the
**Claude Chrome extension** installed and connected, and that they must be
**logged in to LinkedIn themselves** before you begin — you work inside their
session and never sign in for them.

Then `tabs_context_mcp{createIfEmpty:true}`, navigate to the job URL,
`computer{wait:4}`, `screenshot`. If the page shows the logged-out layout, stop
and ask them to log in.

### 8.2 — Open the modal and walk its steps

Click *Easy Apply* **exactly once** (see the constraints file for why a second
click destroys the modal), `wait:2`, then loop until the primary button reads
*Submit application*:

1. `read_page` for field refs and button labels.
2. Fill what you can (8.3), upload the PDFs (8.4).
3. `screenshot`, then a real click on *Next* / *Review*, `wait:2`.

The modal is typically 2–5 steps: contact info → resume → work experience →
education → review. **Screenshot each step before advancing** — that is the
record of what was actually filled, and what you show the user at the gate.

If the same step reappears after *Next*, a required field failed validation:
`read_page` again (or `screenshot`, in the SDUI flow described in the
constraints file), find the error text, and fix it — or, if it is a question you
must not answer, stop and hand over.

### 8.3 — Filling fields: truth only, no guessing

`candidate.md` is authoritative for name, email, phone, city, country.

**Never invent an answer.** Screening questions are frequently knock-out
filters, and a wrong answer is a lie told in the user's name:

- **Answerable from the record** (years on a named technology, location, working
  languages, a notice period recorded in `candidate.md`): answer it, and
  **report each one at the gate** with the value used.
- **Not answerable** (salary expectation, work permit status, "why do you want
  to work here", availability date, willingness to relocate): **leave it blank
  and ask the user**. Do not approximate, do not put a placeholder, do not
  answer "yes" to be safe.
  - **Salary expectation in particular: the step 3b estimate does not make this
    answerable.** Show the user the range and what it was based on, then ask for
    *their* number and use that. An estimate you produced is material for their
    decision, never a substitute for it — and a figure typed into a form is a
    commitment made in their name.
- **Radio and checkbox knock-outs** follow the same rule: if the record says `0`
  on it, the honest answer is *No*, even when it fails the filter. Never click
  *Yes* to get past a gate.

Step 3's score already told the user where the gaps are — a screening question
hitting one of them is expected, not a surprise.

### 8.4 — Attaching the PDFs

**Never click a file input or an "Upload" button** — it opens a native picker
you cannot control and the session hangs. Get the input's `ref` with
`read_page`, then `file_upload` with absolute paths.

**Expect to hand the upload to the user** in the SDUI flow, where there is no
`ref` to give `file_upload`. That is a dead end by design: open the folder so
the file is one click away, name the exact button and filename, ask them to
confirm the selection moved, and ask them **not** to click *Next* — you resume
from 8.2 so the remaining steps stay under the gate.

**Two fields carry stale data from previous applications. Check both, every
time — they are the likeliest way to send the wrong document in the user's
name:**

- **The pre-selected CV.** LinkedIn re-proposes the last file uploaded, which
  may not even be a CV — a cover letter sitting in the resume slot, with
  months-old CVs tailored to other employers below it. Expand *Show N more
  resumes* to see the full list before deciding.
- **The free-text "Cover letter" box.** It keeps the text typed for a previous
  ad. Select all, delete, and retype the current letter's body as plain text —
  no LaTeX, no `\vspace`, no `\includegraphics` — ending with a typed name.

That plain-text box is often the **only** route for the letter: many Easy Apply
forms have a single file slot, so the letter PDF never gets attached. Say so
explicitly at the gate rather than letting the user assume both went out.

Where the form offers optional *Headline* and *Summary* fields, fill them from
the resume's own title line and summary — same words, no new claims.

### 8.5 — The gate: the user validates the send

At the review step, **stop**. Show:

- the company and role;
- the attached filenames — and, when the form had a single slot, that the letter
  went in as **text** and its PDF is not attached;
- **every screening question and the exact answer filled in**. When there were
  none, say so in as many words: "no screening questions, nothing was guessed"
  is information, not an absence of it;
- **the compensation range from step 3b, again, with its tier and its basis** —
  and, when the form asked for a figure, **the exact number the user gave, shown
  back to them.** This is the last moment it can be corrected: a salary typed
  into an application is the anchor for every conversation that follows, and it
  cannot be withdrawn. If the field was left blank, say that too, so nobody
  discovers later that the form went out without it;
- anything left blank;
- **any pre-ticked box that acts beyond the application** — LinkedIn ticks
  *Follow <Company>* by default, which makes the user follow it publicly. Never
  silently accept or silently untick it: name it and let them choose.

Then `AskUserQuestion`: **Send** (you click it on their go-ahead) · **I'll click
it myself** (leave the modal untouched; treat the outcome as unconfirmed) ·
**Fix a field** (apply the correction, re-gate) · **Cancel** (close the modal,
change nothing in the ledger).

Never click the final button without an explicit answer, and never reuse an
approval from an earlier ad in the same session — one approval, one application.

### 8.6 — Confirm it actually went out

After the send, `wait:3` + `screenshot`. Only a visible confirmation (*Your
application was sent*, or the card now marked *Applied*) counts. If you cannot
see one — or the user chose to click it themselves and has not confirmed — the
application is **unconfirmed**: write `todo` with a `dossier generated <date>,
send not confirmed` note, and say so plainly. **Never report a send you did not
see land.**

## 9 — Update the ledger, then report

Update the ad's row to `applied <YYYY-MM-DD>` and note the dossier folder in
`Note`. Append the row if it was not there. Keep the deep score from step 3 in
`Match` (it replaces any provisional `~`). Add a `Log` line. If a module is
enabled, honour its ledger marker.

**Write the step-3b range into the `Pay` column**, with its tier letter:
`CHF 115–135k (C)`. That is what makes a month of applications comparable later
— and what tells the user, at a glance, which figures came from an employer and
which you derived. Two rules from `shared/pipeline-format.md`: **never overwrite
a better tier with a worse one** (an `(A)` from the ad outranks a `(C)` you
computed today), and **leave `—` rather than inventing a figure** when step 3b
gave none — then say so in the closing report.

If the ledger predates the `Pay` column, add the column, pad the existing rows
with `—`, and **tell the user you migrated their file.**

**`no-go` means the application never left**, and it is not the same status as
`rejected`, which records an application that went out and came back refused.
Never use one for the other: a count of real applications is `applied` +
`rejected`, and putting a sent application under `no-go` erases it from every
such count. When the user later tells you an employer said no, move that row
from `applied` to `rejected`.

`applied` requires a **confirmed** send: either 8.6 saw the confirmation, or the
user says they sent it. Otherwise write `todo` with a `dossier generated <date>`
note — **documents existing is not an application.**

Then tell the user:

- the folder path and the files;
- a short **fit summary** — which of the ad's key requirements are well matched;
- the **gaps**, so they can decide whether to address them. These are for the
  user, never inserted into the documents;
- an offer to tweak tone, length or emphasis;
- **anything that did not happen**, per `shared/never-fail-silently.md`: a
  document rendered without a page-count check, a PDF that could not be produced
  because a tool is missing, a field left blank on the form, a profile export
  that was absent from the record, the letter that went in as text rather than
  as a PDF. Name each one and what it costs. If nothing was skipped, say that in
  one clause;
- **the "How to apply" block below — always, without being asked.**

### 9.1 — "How to apply": mandatory, every run

A dossier the user cannot act on is unfinished work. **Every run ends with this
block**, whether or not step 8 ran. Never make them come back to ask "so where
do I apply?".

**1. The apply URL, on its own line, in a fenced block** so it is copy-pasteable:

- LinkedIn Easy Apply → the LinkedIn job URL.
- External ATS → **the company's own careers URL**, not the LinkedIn mirror, and
  say which ATS it is so they expect an account and bespoke questions.
- **Verify it when you can.** If WebFetch 403s or the site blocks retrieval, say
  so and give the route you *did* verify. Never present an unverified URL as
  confirmed — mark it explicitly as unverified.

**2. The steps that follow, as a short ordered list** — what the user actually
has to do, in order (sign in → upload CV → answer N questions → salary → submit).
Flag anything to prepare **before** opening the form: written answers, portfolio
links, a salary figure, a notice period. If the process is known to be long (a
vetting funnel, a paid trial, an essay form), say so and give a realistic sense
of the time it takes.

**3. Which files go where** — the exact filenames and the field each belongs in.
Say explicitly when a document will **not** be used, so they do not hunt for a
slot that does not exist.

**4. What only the user can supply** — salary, availability, work-permit status,
free-text motivation answers. Offer to draft any written answers. **Repeat the
step 3b range here**, with its basis, so they have it in front of them when the
form asks for a figure — and say again that the number they give is theirs, not
yours.

If it is a LinkedIn Easy Apply and step 8 was not run, close by offering it:
"I can fill the Easy Apply form — you validate the send."
