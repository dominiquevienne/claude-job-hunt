# First-run setup — building the user's workspace

This is the shared onboarding procedure. Both skills call it when the workspace
is not configured, and `/job-setup` calls it on demand.

**Output:** a configured workspace the two skills read from. Nothing is written
inside the plugin — the plugin is replaceable, the workspace is the user's.

```
$JOB_HUNT_HOME/                 # default: ~/Documents/job_applications
├── config.yml                  # machine-readable settings
├── candidate.md                # prose: identity, target roles, blockers, contact
├── commute.md                  # travel times from home base (optional)
├── repos.md                    # evidence from the user's own code (optional)
├── employers.md                # what is true of an employer, not of an ad (optional)
├── signature.png               # optional
├── profile/                    # the user's source documents
└── job-pipeline.md             # the shared ledger
```

Resolve the workspace in every command, never hardcode it:

```bash
JOB_HUNT_HOME="$(python3 "${JOB_HUNT_ROOT}/bin/workspace-path.py")"
```

**And if it exits `3`, ask before creating anything.** Outside a terminal
`$HOME` belongs to a container, and the old default wrote there and reported
success. The script prints the sentence to put to the user; `shared/workspace.md`
has the cascade. Issue #109.

---

## The prime directive — never ask for a value without saying how to get it

Setup is where users abandon a tool. Every single request in this procedure
must carry, in the same message:

1. **What you need**, in one line, in plain words.
2. **Where it comes from** — the **exact URL** and the **exact click path**
   (menu → item → button), or the exact shell command. Never "export your
   profile" — the user does not know which of five LinkedIn menus you mean.
3. **What you will do with it**, when it is personal data.

And when what you receive is not what you expected, **never** answer with a bare
"that didn't work" or silently carry on degraded. Always give, in this order:

1. **What was expected** — the concrete shape (a PDF, a town name, a number).
2. **What was actually received** — quote it, or name the file and what it
   turned out to be. The user cannot fix a problem you keep to yourself.
3. **Why it does not work** — one sentence of cause, not a stack trace.
4. **The procedure to fix it** — numbered steps, with the URL again. Assume the
   user has forgotten the instruction from two messages ago.
5. **A way forward that is not "fix it"** — skip this input, supply it another
   way, or continue without it and revisit later. Setup must never dead-end.

Ask in batches with `question` where the options are closed (work modes,
thresholds, modules). Use plain questions for free text (name, home town).

---

## 0 — Announce, then get consent to write

Tell the user, before anything:

- what the workspace is and **where** it will be created (the resolved path);
- that their profile documents will be **copied into it**, and that it all stays
  **on their machine** — nothing is uploaded anywhere by this plugin;
- that the folder is theirs: readable, editable, deletable at any time;
- roughly how long this takes (about 5 minutes, most of it locating exports).

If `$JOB_HUNT_HOME/config.yml` already exists, this is a **re-configuration**:
read it, show the current values, and ask which section to change rather than
re-asking everything. Never overwrite an existing config without showing what
is in it first.

**When `/job-setup` was given an argument, go straight to that section** and
leave the rest of the config untouched. The named sections:

| Argument | Section | Use it when |
| :-- | :-- | :-- |
| `profile` | 1 | New CV, new export, a career step to add |
| `contact` | 2 | Address, phone, `signature`, `repos` |
| `commute` | 3 | Moved, or changed what commute they will accept |
| `languages` | 4 | A language became working rather than passive |
| `searches` | 5 | The queries return junk, or the target role moved |
| `orientation` | **4b** | **What they are looking for changed** — widening the geography, a reconversion, opening up to intérim. This is the one that re-picks the boards |
| `boards` | 5b | Adding or pruning a board without redoing the interview |
| `thresholds` | 6 | Too much noise, or too little getting through |
| `modules` | 7 | Turning unemployment-office declaration on or off |

An argument you do not recognise is not a reason to re-run everything: say which
sections exist and let the user pick.

```bash
JOB_HUNT_HOME="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
mkdir -p "$JOB_HUNT_HOME/profile"
echo "Workspace: $JOB_HUNT_HOME"
```

---

## 1 — The factual record: where the user's history comes from

This is the single most important input: **every claim in every document the
plugin produces is checked against these files.** Without them the skill cannot
work, and it must not invent a career.

Offer three routes, in this order, and let the user pick with
`question`:

### Route A — read the pages in the user's own browser

**This is the nominal route, and it used to be the fallback.** Printing five
pages to PDF is the first place people stop — `README.md` says so — and three
things made it expensive:

- **The truncation was silent.** A page not scrolled to the bottom prints a
  valid, incomplete PDF: no error, a poorer record, and a resume missing jobs.
- **The print dialog is a real wall.** A native window; no automation crosses
  it, here or anywhere.
- **And the PDF was never what is used.** Only the text is consumed, from
  `profile/.text/`. The PDF was an imposed intermediate whose useful content
  gets extracted afterwards. Issue #111.

**So: open each page in the user's browser, take its text, save it.** Same
content, no printing, no dialog — **and the truncation disappears, because
nothing depends on a manual scroll.**

**In their browser, with their session. Never log in for them**, and never
fetch these URLs from a script: `shared/robots-policy.md` records that
LinkedIn refuses this project by name, the user-driven agent included. What is
being read is a page the person is looking at.

Ask them to open their profile, then for each of the five sections:

| Section | Page |
| :-- | :-- |
| `profile` | `linkedin.com/in/<handle>/` |
| `experience` | `linkedin.com/in/<handle>/details/experience/` |
| `projects` | `linkedin.com/in/<handle>/details/projects/` |
| `certifications` | `linkedin.com/in/<handle>/details/certifications/` |
| `skills` | `linkedin.com/in/<handle>/details/skills/` |

Read the page's text, then save it under the name the pipeline knows:

```bash
python3 "${JOB_HUNT_ROOT}/skills/cover-letter/save-profile-text.py" \
  experience --stdin <<'TEXT'
…the page text…
TEXT
```

**A `.text/` written this way is indistinguishable from one `sync-sources.sh`
built**, so every downstream check works unchanged —
`grep -ril '<term>' profile/.text/`.

**The script says when a section came back thin**, and that warning is the
truncation risk in its new shape: *a short record and a truncated one look
identical afterwards*, so say which you think it is rather than saving it
quietly.

### Route A-bis — the five PDFs, when the browser is not available

**The old nominal route, kept because it works and some people prefer it.**
Give the user this block verbatim, with `<handle>` replaced by their own
LinkedIn handle once known:

> **1. The whole profile** — one click:
> open <https://www.linkedin.com/in/> your profile → the **More** button under
> your header → **Save to PDF**. It lands in your Downloads folder.
>
> **2–5. The four detail pages** — open each URL, then print it to PDF
> (`Cmd/Ctrl + P` → *Destination: Save as PDF*), keeping the suggested name:
>
> - `https://www.linkedin.com/in/<handle>/details/experience/`
> - `https://www.linkedin.com/in/<handle>/details/projects/`
> - `https://www.linkedin.com/in/<handle>/details/certifications/`
> - `https://www.linkedin.com/in/<handle>/details/skills/`
>
> **Scroll each page to the bottom before printing.** They load more entries as
> you scroll; printing early silently truncates your history, and the skill will
> then write a resume that is missing jobs.

Then collect them:

```bash
"${JOB_HUNT_ROOT}/skills/cover-letter/sync-sources.sh" "<Full Name>" "$JOB_HUNT_HOME/profile"
```

**It also writes `profile/.text/`** — every PDF as plain text. That is not a convenience: the skills check a claimed skill against the record before scoring, and while that check cost a PDF extraction it was skipped in favour of grepping `candidate.md`, which is not an inventory. A candidate was told Confluence was not in their file; it is, with eight experiences behind it. Issue #63.

The script looks in Downloads and on the Desktop, accepts both naming shapes
LinkedIn produces, and reports one line per file: `✓ found` or `– missing`.

### Route B — an existing CV

Any PDF or DOCX. **Do not ask for an absolute path.** It was the fallback for
the most important step and it was harder than the thing it was rescuing —
*"give me the absolute path"* asks for a notion, where the step it backs up
asks for a click. Issue #111.

**Ask to be shown the file**, in this order:

1. **A file dropped into the conversation** — the shortest route, and the one
   that works everywhere.
2. **What is already in the workspace or a connected folder.** List what you
   find and let them pick: `ls "$JOB_HUNT_HOME"/*.pdf "$JOB_HUNT_HOME"/*.docx`,
   plus wherever they have said their documents live.
3. **A path, if they offer one** — accept it, do not require it, and accept a
   relative one or a `~` as readily as an absolute one.

Then copy it to `$JOB_HUNT_HOME/profile/` and extract the history from it. Say plainly that a
CV is a *summary*: it will under-represent the user's stack compared with the
LinkedIn exports, and they can add Route A later with `/job-setup`.

### Route C — dictate it

No documents at all. Interview the user: current role, previous roles with dates
and employers, education, certifications, core skills. Write it into
`candidate.md` and tell them it is now the source of truth, so it must be kept
accurate.

### Validating what arrived — the four checks

Run all four on every file, and apply the prime directive on any failure:

| Check | Command | If it fails, tell the user |
| :-- | :-- | :-- |
| The file exists | `test -f` | Which name was looked for, in which folders, and that the export probably landed elsewhere — **ask them to drop it into the conversation, or name where it is.** A path is accepted, not required |
| It is really a PDF | `file <f>` | What it turned out to be (an HTML page saved instead of printed, a `.webarchive`, a zero-byte file), and to redo the print with *Save as PDF* as the **destination**, not *Save page as* |
| It has selectable text | `pdftotext -layout <f> - \| head` | That it came out as an image (a scan or a screenshot), so nothing can be read from it, and to re-print from the browser rather than photographing the screen |
| It is the right section | the extracted text contains the section heading | Which section the file actually contains — users routinely print `experience` twice — and give the URL of the missing one again |

If `pdftotext` is not installed, say so with the install command rather than
reporting a corrupt file:
`brew install poppler` (macOS) · `sudo apt install -y poppler-utils` (Debian).

**Never proceed past a missing whole-profile document.** Missing *detail* pages
are a degraded but workable state: continue, and record in `candidate.md` which
ones are absent so later runs know the record is incomplete.

---

## 2 — Identity and contact: propose, don't interrogate

Read what you just collected and **fill the contact block yourself**, then ask
the user to confirm or correct it. Typing an address into a chat prompt is the
most tedious part of any setup — do not make them do it.

Extract: full name, email, phone, city and country, LinkedIn URL, GitHub or
portfolio URL if present. Show them as a list and ask one question: *"correct as
is, or what should change?"*

Anything missing from the documents (a phone number is often absent from a
LinkedIn PDF) is asked for individually, with a reason: *"the cover letter
header needs a phone number — LinkedIn's export doesn't include one."*

Derive `family_name` / `given_name` for the output filenames and **show the
resulting filename** so the user can object:
*"your files will be named `Lovelace_Ada_Acme.pdf` — right family name?"*
Names do not split reliably: never guess silently on a multi-part or
particle-bearing name (`van der Berg`, `García Márquez`), ask.

---

## 3 — Geography: home base, commute, work modes

Four questions, then a generated table.

1. **Home base.** *"Where should commutes be measured from? A town plus region,
   e.g. 'Bristol, England' — precise enough to estimate travel times."*
2. **Maximum one-way commute**, in minutes (`question`: 30 / 60 / 90 /
   remote only). Explain what it does: an ad demanding regular presence beyond
   it is discarded **whatever its score**, because no stack fit buys back a
   commute that cannot be made.
3. **Work modes accepted** (multi-select: on-site / hybrid / remote). Point out
   the trap: *hybrid still means regular days on site*, so hybrid inherits the
   commute limit; a *remote* role with a distant head office does not.
4. **Search perimeter** — the location strings the job board understands.
   Propose them from the home base and let the user edit.

Then **generate `commute.md`**: the main employment centres within and just
beyond their limit, with estimated one-way drive times from the home base, as
two columns (within / beyond). Present it and ask them to correct it — they
know their own region better than any estimate. This file replaces guessing at
scan time, which is where a wrong guess costs a real opportunity.

Write, at the top of that file, that the times are **estimates the user
validated**, with the date — so a later run knows they were confirmed, not
invented.

**Then offer `employers.md`, and offer it rather than assume it.** It is the
fifth workspace file and it holds what the ledger structurally cannot: a fact
about a *company* rather than about an advertisement — the exact legal name, the
address an official declaration expects, standing decisions with their lifting
dates, which ATS they run.

```bash
cp "${JOB_HUNT_ROOT}/templates/employers.example.md" \
   "$JOB_HUNT_HOME/employers.md"
```

**Say what it is for in one sentence and let them decline.** A user with no
standing decisions and one employer does not need it yet; a user who has ever
said *"not this company again"* does.

**And say the rule that comes with it**, because a second place to look is only
safe if the authority is settled: **the ledger is authoritative about
advertisements, this file about the employer, and they never speak about the
same thing.** No score and no application status go in it; ledger rows are
**referenced**, never copied. `shared/workspace.md` carries the incident that
established it — two live ads discarded on a freeze that had been lifted eight
days earlier, because the two notes sat eighteen rows apart. Issue #94.

**One country changes what happens later in this flow.** If the home base, the
commute table or the search perimeter reaches **Austria**, note it now and run
**section 5d** when you get to the boards. AMS is the largest source of Austrian
vacancies and the only board in this plugin that asks the user to take a
position rather than supply a value — raising it at the geography step is too
early, and not raising it at all leaves the biggest Austrian gap unexplained.

---

## 4 — Languages

Two lists, and the distinction matters more than users expect:

- **Working languages** — can write, interview and negotiate in it.
- **Passive languages** — understands, gets by, but is not professional.

Explain the consequence before asking: a language on the *passive* list is
scored `0` when an ad requires it, treated as a **hard blocker rather than a
gap**, and **kept out of the resume** — because employers writing "good German"
mean something the user does not have, and claiming it produces an interview
that fails in its first two minutes.

Then ask for the **interface language** — the language of the conversation and
of anything the ad does not dictate. State clearly that the resume and cover
letter always follow **the language of the ad**, whatever this setting says.

---

## 4b — Orientation: what they are looking for, which is not what they have done

**Run this before step 5, and re-run it on its own with `/job-setup orientation`.**
It is the step that turns a pile of CV facts into a *search*, and it exists
because the two are not the same thing: **step 1 reads what the user has done;
this step asks what they want next**, and step 5 cannot draft a single query
until it knows. Skipping it and inferring the search from
the CV quietly assumes the answer is "more of the same" — which for anyone
changing trade, changing country, or leaving a field they are tired of is the
wrong sweep, every run, for months.

It also does the thing that makes 5b bearable. Twenty adapters is too long a
list to hand someone cold; four answers here cut it to the three or four boards
that can actually serve them, with a reason attached to each.

### First, say back what you read — then let them correct it

Draft a profile from step 1's documents and **show it before asking anything**:

> Voici ce que je lis dans votre dossier — corrigez-moi :
> **Métier** — ingénieur logiciel backend, 12 ans, dont 4 en encadrement
> **Secteurs** — fintech, industrie
> **Base** — Lausanne (VD), Suisse
> **Langues de travail** — français, anglais
> **Contrats** — CDI, salarié

Five lines, no more. The point is a correction, not a portrait: a wrong trade or
a wrong seniority here propagates into every search query and every board
choice, and it is far cheaper to fix now than after a scan.

**Never present an inference as a fact.** If the documents were thin, say which
line you are unsure about and mark it — `Secteurs — fintech (déduit d'un seul
poste)`. A user corrects a hedged line; they skim past a confident one.

### Then six questions, and they are closed on purpose

Use `question` — one call, all six, each with the consequence stated in
the option text so nobody is choosing blind.

| # | Question | Options | What it decides |
| :-- | :-- | :-- | :-- |
| 1 | **Chercher dans la continuité de ce profil, ou autre chose ?** | Continuité · Élargir aux métiers adjacents · Reconversion, autre métier · Peu importe, je regarde ce qui passe | The search queries in step 5, the scoring rubric's treatment of gaps, **and whether the CV is a target or just a history** |
| 2 | **Mobilité géographique ?** | Rester dans ma région · Ailleurs dans le pays · Un autre pays · Full remote, le lieu m'est égal | Which country's boards exist at all, and whether the commute limit from step 3 still applies |
| 3 | **Quels pays / régions ?** *(only if 2 ≠ "rester")* | Free text, or a country list | The board shortlist, and the language check below |
| 4 | **Quels types de contrat acceptez-vous ?** | CDI / permanent · CDD, mission, projet · Intérim · Freelance / indépendant · Alternance, stage, premier emploi | Whether the **agency boards** are worth enabling at all, and which sector boards apply |

| 5 | **Où pouvez-vous travailler sans parrainage ?** *(offer a default built from `home_base` — for a Swiss base, `CH` + `EU`)* | The default · Add or remove countries · **Passer** | Whether an ad from elsewhere carries one sentence at the gate — see below |

| 6 | **Permis de conduire, et disposez-vous d'un véhicule ?** | Permis + véhicule · Permis, pas de véhicule · Ni l'un ni l'autre · **Passer** | Whether an ad stating a licence as a must-have is answered once or re-asked every week — see below |

**Question 5 asks for one list and nothing else.** Countries and zones where
the person needs no sponsorship, written to `location.work_authorization`.
**Never their nationality, their permit type or their status**: the plugin
needs the answer to one question, not an immigration file, and a `config.yml`
gets read aloud and pasted into issues.

**Offer a default rather than an empty box** — `home_base` gives the country,
and for an EU or EFTA base the zone usually follows. **And let them skip it**:
somebody who declines gets exactly the previous behaviour, with nothing ever
flagged. It is one question, asked once, not a gate to get through.

**Say what it buys, because it does not restrict anything.** An ad from outside
the list is still scanned, still scored and still shown; what changes is one
sentence at the go/no-go gate saying that a *local employment contract* there
would need sponsorship, while invoicing that country from here is a different
legal object and may well be open. **The plugin gives no legal advice and
decides nothing** — it noticed a mismatch between two lists.

*(This exists because a London role scored 74%, the best stack match in the
whole ledger, and a complete dossier — CV, letter, rendered PDFs — was produced
before the user closed it in one sentence: "pas éligible, permis de travail
UK". Issue #82.)*

**Question 6 is two fields, not one, and it is the same failure as question 5
on another value.** `location.driving_licence` takes the categories held —
`["B"]`, or `[]` for none — and `location.own_vehicle` is a boolean. **Ads ask
for one, the other, or both**: *permis B* is the legal capacity to drive,
*"véhicule personnel indispensable"* is having a car, and a single checkbox
loses the distinction that decides field roles. **Ask for the category when
they have one**, because ads name it (B, BE, C1, D).

**And "Passer" is a real answer here.** With both keys absent, an ad that
states a licence still raises a **question at the go/no-go gate** — it does not
go silent, and it never discards. That is the difference from question 5: there
silence costs nothing because the ad is scored anyway; here a stated must-have
that nobody can answer is what produced the issue.

**Absent from the file is not no**, and the asymmetry is why: a wrong "they do
not have it" drops an ad silently, a wrong "they have it" fails in the room.

*(This exists because an ESN ad printed "Permis de conduire obligatoire" in a
list where ITIL was explicitly only *"un plus"*, and `candidate.md`, `repos.md`
and five profile PDFs answered nothing at all. The run flagged it correctly and
by hand — which is a stable fact turned into a weekly question. Issue #91.)*

### Asking question 6 later, without redoing the onboarding

**An existing `config.yml` has neither key**, and nobody should re-run setup to
add two lines. When `_licence.py` returns `never-asked` at a gate, **ask there,
once, and offer to write it**:

```yaml
location:
  driving_licence: ["B"]     # [] if none
  own_vehicle: true
```

**Write it only on an explicit yes**, and confirm what was written. A user who
declines is not asked again in that run — and the ad still gets its question,
which is what the gate was for.

**Question 1 is the one people answer too fast.** If they pick *reconversion* or
*élargir*, say plainly what changes: the searches stop being built from their
stack, the scoring rubric's "missing skill" penalty has to be relaxed or the
whole market scores badly, and the boards keyed to their old sector come off the
list. Record the answer in `candidate.md` as a first-class target, the way
step 5 will for "roles with no hands-on work" — otherwise every later run
re-derives the old profile from the same documents and quietly undoes this.

**Question 2 has a trap worth naming out loud.** *Un autre pays* is not only a
board change. Ask, in the same breath: do they have the **right to work** there,
and do they have a **working language** for it from step 4? A user with passive
German sweeping Zurich gets a full pipeline and no interviews — and the plugin
will have produced that outcome enthusiastically. Record the answer; do not
guess it from a passport or a surname.

### Then propose the boards, do not list them

Turn the four answers into a **shortlist with a reason each**, and present that
instead of the full table in 5b. The user edits a proposal far more readily than
they build a selection.

| Signal from the answers | Boards to propose | Boards to leave out, and say why |
| :-- | :-- | :-- |
| **Anywhere / any profile** | HiringCafe — worldwide, no browser, no account, the one sweep that works everywhere | — |
| **Country = Switzerland** | job-room.ch, jobup.ch (Romandie) or jobs.ch (Suisse alémanique), randstad.ch | France Travail — French offers only |
| **Country = France** | France Travail *(see 5c, and say it is unverified)*, Indeed `fr.indeed.com`, Michael Page `.fr` | Every `.ch` board — they carry no French ads at all |
| **Country not covered by any adapter** | HiringCafe, LinkedIn, Indeed on that country's domain | Say plainly that the national boards there have no adapter, and that `cover-letter <URL>` still handles any ad from them |
| **Names specific employers** | Workday, Greenhouse, Lever, Ashby, SmartRecruiters, SuccessFactors, Solique, umantis — resolved per employer | Offer these **only** when employers were named. They answer *"is X hiring?"*, never *"who is hiring near me?"*, and a user with nobody in mind gains nothing |
| **Accepts intérim / mission** | The agency boards for that country — randstad.ch, persigo.ch, fachkraft.ch, Michael Page | Leave them out otherwise: they are volume the user has already said no to, and the employer is never named |
| **Sector = social, care, education** | sozialinfo.ch (CH) | — |
| **Sector = trades, industry, technical** | fachkraft.ch (CH), persigo.ch (CH) | — |
| **Reconversion (Q1)** | Broad boards only — HiringCafe, the national one, LinkedIn | **Drop the sector boards keyed to the old trade.** This is the case where a sector board is actively harmful: it fills the pipeline with exactly the work they are leaving |
| **Wants LinkedIn / Easy Apply** | LinkedIn | Needs their own logged-in browser session — say so before enabling, not after |

Present it as: *"d'après vos réponses, je propose ces quatre — voici pourquoi
chacune, et voici celles que j'ai écartées."* **Naming the exclusions matters as
much as the selection**: a user who sees that jobs.ch was left out *because they
said Romandie* trusts the shortlist; one who just gets four boards wonders what
they are missing.

Carry the answers into step 5 — they decide how the queries are built — then
into 5b, which collects the settings for each board they kept.

### Re-running this later

`/job-setup orientation` re-runs exactly this step against the existing
workspace. It is the right command for the three things that actually change
mid-search:

- **they decide to widen or narrow** — "je ne trouve rien en local, j'ouvre à
  toute la France";
- **a board came back empty for a season** — that is the dormancy decision in
  5b, not a reason to redo the whole interview;
- **the profile itself changed** — a new qualification, a first job in a new
  trade.

**Keep every board's own configuration when re-running.** Tenants, domains,
cantons, departments: a board dropped from the shortlist goes to `enabled:
false`, it does not lose its settings. Re-enabling must be one line changed, not
this interview repeated — the same rule as *Turning a board off* below.

---

## 5 — Target roles and the search sweep

**Propose, then confirm.** Read the skills and experience gathered in step 1,
**and the orientation answers from 4b** — a user who said *reconversion* gets
queries built from the trade they are moving to, not the one on their CV — then
draft:

- the **target role families** — often more than one (hands-on senior engineer
  *and* team lead, for instance). Ask explicitly whether roles with **no
  hands-on work** are acceptable; if they are, record it in `candidate.md` as a
  first-class target so scoring never treats "this role has no coding" as a gap.
- the **core stack** the user actually wants to work in;
- a **hard-blocker rule** worth stating up front: is a primary backend language
  with no production experience behind it a blocker, or negotiable? Ads write
  "or willingness to learn" freely; the user's answer decides whether that
  clause is taken at face value. Record the decision, not the assumption.
- **6 to 8 search queries** built from the above, mixing strict-quoted stack
  searches, role-title searches and a remote-only sweep.

Show the queries as a list, say what each one is *for*, and let the user cut or
add. Warn that unquoted keywords match very loosely on most boards, so quoting
is the difference between four relevant results and six hundred junk ones.

Seed `search.blocklist` with the aggregator and repost farms listed in
`shared/pipeline-format.md`, and say that it is theirs to extend.

---

## 5b — Enable the job boards (nothing is on by default)

**`job-scan` sweeps nothing until a board is switched on**, and that is
deliberate: scanning drives the user's own browser under their own account. Say
that when you ask — it explains why they are being asked at all.

**Step 4b has already produced a shortlist.** This table is the reference for
what each board on it needs — not a menu to read out. Show the full list only if
the user asks what else exists.

**And ask in their language, not the column's.** The *Needs* column is the
board's vocabulary — tenant, slug, facet, ISO-2, an INSEE commune code that is
not a postcode, a pre-2016 region map, a city *and* its coordinates. **Seven
developer notions to answer "where do you want to work?"** Issue #113.

**The resolvers already exist**; the design is fine and it was the writing that
exposed the plumbing. So:

| Ask this | Then resolve it |
| :-- | :-- |
| *"Which towns or areas would you actually work in?"* | Into cantons, departments, regions, ISO-2 — each board's own shape |
| *"Which employers would you like to work for?"* | Into tenants and careers hosts, with the adapter's `resolve` where it has one |
| *"What kind of work?"* | Into the board's facets or occupation codes, and **check how much of the index they classify before trusting one** |

**Never read a code out and never ask for one.** If a value cannot be resolved,
say what you tried and what you need — *"I could not find a commune code for
that name; is it the one in <department>?"* — rather than asking for the code
itself.

| Board | Needs |
| :-- | :-- |
| Workday | The employers they would work for. **No login, no browser.** Where the large Swiss employers are — Swisscom, Swiss Life, Roche, Lindt. Each board needs three coordinates (host, tenant, site); resolve them with `workday.py resolve "<employer>"`, and ask which site when an employer runs several |
| Solique | The employers they would work for, **as tenant names** — the path segment of any of their ad URLs (`iss`, `ktzh`, `manor`). **No login, no browser.** Warn them that some tenants only serve a truncated listing: the adapter says so per run, and the count is not the size of the board |
| SAP SuccessFactors | The employers they would work for, **as careers domains** — `jobs.<employer>.ch`, `www.carrieres-<employer>.com`. **No login, no browser.** Never guess the site's locale: one the tenant does not publish returns an empty board with no error at all. `successfactors.py locale --host <host>` reads the right one |
| umantis | The employers they would work for, **as careers URLs** — `recruitingapp-<n>.umantis.com` or the employer's own `jobs.<employer>.com`. **No login, no browser.** Unlike the other ATS boards there is no resolver: HiringCafe indexes no umantis ad, so a tenant cannot be looked up from a name. Ask for the URL; never guess a tenant number, because a wrong one serves the vendor's marketing page and looks like an employer with nothing open |
| La Bonne Alternance | The **departments** they would work in, **exactly two characters** — `69`, `2A`. **No browser, no login, but a free API key**: an account at api.apprentissage.beta.gouv.fr, three minutes, and the token goes in `LBA_API_KEY` — **in the credentials file of §5b-bis, which needs no shell**, never in config.yml. Offer it **only** for apprenticeship or work-study, and tell them the best part: it also returns companies that take apprentices without posting an ad. Warn that a sandbox key returns unusable apply links for those companies |
| Emploi Territorial | The **departments** they would work in — written any way, `69` or `069`. **No login, no browser, no key.** French local government: communes, départements, régions, CCAS. Offer it to anyone open to the fonction publique territoriale, and say the deadline is real — these ads close on a stated date. Without a department the sweep is the whole country, over 1 300 pages |
| Cegid Talentsoft | The employers they would work for, **as careers host labels** — `businessfrance-recrute`, `groupeadp-recrute`. **`place-ep-recrute` is `choisirleservicepublic.gouv.fr`**, the state's public-service portal: offer it to anyone open to the fonction publique, and warn that its 51 708 posts are not a board to read whole. **No login, no browser, no key.** Ministries, airports, energy, large agencies. No directory exists, so ask for the URL; a wrong label does not 404, it fails to resolve. Worth saying: the listing already carries the address and the date, so a scan is useful without opening a single ad |
| DigitalRecruiters | The employers they would work for, **as careers hostnames** — `recrutement.monoprix.fr`. **No login, no browser, no key.** French retail, franchise networks and large service groups; the biggest boards of any ATS here. No directory exists — the site is on the employer's own domain, so ask for the URL. Warn them the listing has no description or date, and that reading the ads is deliberately paced |
| Softy | The employers they would work for, **as careers URLs** — `<tenant>.softy.pro`. **No login to scan, but it needs their own browser session**. Say why, because it is not a limitation: the site asks AI crawlers not to read it, so the sweep goes through their session instead. Warn them an ad can span several towns and the listing shows only the first |
| Flatchr | The employers they would work for, **as careers URLs** — `<tenant>.flatchr.io`. **No login, no browser, no key**, and no detail option: one request returns the ads with their full text. Like Taleez there is **no resolver** — its sitemap belongs to the marketing site and lists no vacancies at all — so ask for the URL and never guess a tenant |
| Taleez | The employers they would work for, **as careers URLs** — `<tenant>.taleez.com`. **No login, no browser, no key.** The French SME/ETI ATS, and like umantis there is **no resolver**: no directory, no cross-tenant search, and the sitemaps carry no job URLs. Ask for the URL and never guess a tenant. Warn them the listing has **no description**, so reading the ads costs one request each |
| Greenhouse / Lever / Ashby / SmartRecruiters | A list of **employers** they would actually work for. **No login, no browser.** These answer "is my target employer hiring?", never "who is hiring near me?" — a user with nobody in mind gains nothing, so offer them only when the user names employers. Resolve each tenant token with `ats.py resolve "<employer>"`; never ask the user to guess it. **On SmartRecruiters that resolution is not optional**: a wrong tenant answers `200` with zero postings there, so a guessed token looks exactly like an employer with nothing open |
| France Travail | Their **departments** (`"75"`, `"69"` — strings, leading zero kept) or an **INSEE commune code** plus a radius. **No login, no browser** — but it needs an API key, free from francetravail.io. Walk them through it with section 5c; do not ask for the key before they have enabled the board. France only |
| job-room.ch | The cantons they would work in (official uppercase codes), or a point and a radius of at least 10 km. **No login, no browser.** Switzerland only. Reaches the SMEs, foundations and staffing agencies HiringCafe misses |
| Adzuna | Their ISO-2 country, from the nineteen it serves. **No login, no browser** — but it needs a free key from developer.adzuna.com, and its budget is the smallest here: **250 calls a day for every country together**. Walk them through it with section 5e |
| HiringCafe | Their ISO-2 country code. **No login, no browser** — it is plain HTTP, and the only sweep that works without a browser. Worldwide; thin in emerging markets, and blind to the Swiss ATS (Refline, Ostendis, Umantis) |
| LinkedIn | Their own profile URL, and they must be logged in themselves in the OpenWork browser session |
| jobup.ch | Nothing — **no login needed to scan.** Swiss ads, French-speaking Switzerland |
| randstad.ch | Nothing — **no login, no browser.** The staffing agency's Swiss board, ~985 ads nationwide. The employer is never named. Note for Romandie users: its structured data is absent on Geneva-area ads, which the adapter handles but which makes those ads slightly thinner |
| persigo.ch | Nothing — **no login, no browser.** A staffing agency, mostly central Switzerland, trades and technical roles. Warn them of two things: the employer is never named, and the board keeps ads for over a year with no date on the listing — so a large result count is not a large number of current openings |
| sozialinfo.ch | Nothing — **no login, no browser.** Switzerland's social sector. Worth offering to anyone in social work, care, education or the public sector; pointless otherwise. Unlike the agency boards it names the employer, and every ad carries a postcode the ORP form wants |
| fachkraft.ch / sta.jobs | Nothing — **no login, no browser.** Swiss trades and industry. **Offer `www.fachkraft.ch` and nothing else**: it is the umbrella for sta.jobs and stellenpartner.ch, which add no ads and double every row. Warn them the employer is never named |
| Michael Page | Their country domain — `www.michaelpage.ch`, `.fr`, `.de`, `.co.uk` … **No default**: guessing it searches the wrong market. **No login, no browser.** Warn them the employer is never named on this board, so they cannot research the company before applying, and the ledger cannot dedup it against the employer's own ATS |
| Cadremploi | A **list of `motscles` / `ville` searches**, `ville` written `<slug>-<code postal>` — `paris-75`, `lyon-69`. **No login to scan, but it needs their own browser session**, because the site blocks scripted access outright. Say that before enabling it: it is the only French board here that cannot run headless |
| Figaro Emploi | A **list of searches**, each one a `departement` (`69`), a `ville` (`lyon-69000`) or a `region` (`fr-ara`), optionally narrowed by a `metier` slug. **No login to scan, but it needs their own browser session** — Cloudflare blocks scripted access, exactly as on Cadremploi. Mention it when they ask for **Keljob**: that is this board now |
| Jobology | A **list of `site` / `metier` searches**, optionally a `region`. The `site` is one of nine sector boards — ask which sector fits them: santé (`jobvitae.fr`), distribution (`distrijob.fr`), transport (`jobtransport.com`), tourisme-hôtellerie (`clicandtour.fr`), énergie, maritime, sport, environnement, supply chain. **No browser, no account.** Slugs are the site's own vocabulary — `jobology.py metiers --site <site>` lists them, and a wrong one returns an empty board with no error |
| Batiactu | A **list of searches**, each a `region` (21 slugs, the **pre-2016** map — `aquitaine`, not `nouvelle-aquitaine`) or a `metier`, plus `departements` — which they should almost always give, because the site's own region filter matches the employer's name and returns jobs anywhere in France. **No browser, no compte.** Offer it only for BTP, construction and building trades |
| ANEFA | A **list of `departements`**, written as the real numbers — `29`, `2A`, `971` — the adapter translates them. **No browser, no compte.** Offer it for farm, seasonal and rural work. Warn them of one thing: **the ads name no employer**, so a letter goes to a farm the ad describes without naming |
| Welcome to the Jungle | Nothing to configure for discovery — but it **needs their own browser session** to read the ads, because every page answers an anti-bot challenge that their browser passes and a script does not. Ask which **companies** or which **date window** they want: the board is 88 222 ads and the useful narrowing is `--company` and `--since`. Warn them that `/fr/` is a language, not a country — the country is only known once an ad is read |
| Adecco France | A **narrowing** — `ville` (free, matches the URL slug), `region` (the department spelled out, but it costs a fetch per candidate) or `since`. **No browser, no compte.** Tell them what it is before enabling: 13 293 interim and CDI ads with a salary on two in three, but **the employer is always Adecco** — the client company is described and never named, so no pre-application research and no dedup key |
| Randstad France | A **list of `ville`**, spelled as in the URL — it is reliable here and free. `departement` works too but costs a fetch per candidate. **No browser, no compte.** Same warning as Adecco: **the employer is Randstad France on every ad**, the client is never named. Note for them: this is *not* `randstad.ch`, which the plugin also covers |
| Crit | A **`since` date** above all — its URLs are UUIDs, so the date is the only filter that costs nothing, and it is a real per-ad date. `departements` works but reads every ad to find them (60 read for 1 kept, measured). **No browser, no compte.** Worth telling them: it is the only French board here that gives a **real salary range on every ad**, and the employer is the local Crit branch rather than the client |
| Hays France | A **list of `lieu`**, written as in the URL — `paris`, `loire-atlantique`. It is free and it is the only geography: **this board has no postcode at all**. **No browser, no compte.** Offer it for cadres, finance, audit, IT and engineering rather than for production or logistics — and tell them a salary figure appears on about one ad in four, the rest saying « selon profil » |
| Empléate (SEPE) | A **list of `provincia`**, uppercase as the board writes them — `MADRID`, `BARCELONA`, `A CORUÑA` — and a **`desde` date**, which matters more here than on any other board: **8 106 of its 28 099 live ads were posted over a year ago**, the oldest in 2020, and nothing in the ad says so. **No browser, no compte, no clé.** Spain only. Never type a province from memory: run `empleate.py provincias` and offer what the board actually publishes. Two things worth telling them — the employer is named on only 29% of ads (on the regional-office feed, the largest, you apply through an address written inside the text), and it is the cheapest board here, one request per hundred complete ads |
| Oposiciones (Empléate) | A **`comunidad`** more often than a `provincia` — and say why, because it is counter-intuitive: **`provincia: MADRID` returns 42 announcements and not one is in Madrid** (they are Catalan posts from Madrid-seated bodies), while the 50 real Madrid ones carry no province at all. Optionally a `grupo` (`A1`…`E`, `GP1`…`GP5`) and `dias_restantes`. **No browser, no compte, no clé.** Spain only, and only for the public sector. Three things to tell them before enabling it: the board is **Catalan in practice** (1 334 of 1 558 live records come from the Diputació de Barcelona's register, Madrid has 42), there is **no ad text at all** so `cover-letter` cannot write from it — an oposición is answered with a form and a dossier — and the deadline field says "Abierto" on every record ever published, so the adapter computes the real one and hides expired announcements by default |
| Infoempleo | A **list of `lugar`**, written as in the URL — `madrid`, `barcelona`, `vitoria-gasteiz`, and `multiprovincia` for ads spanning several provinces. It is free and it is the only cheap filter: **the sitemap carries no date**, so `desde` costs a fetch per ad. Run `infoempleo.py lugares` and offer the places the board actually uses — a wrong one is an empty board, not an error. **No browser, no compte, no clé.** Spain only, generalist. Tell them the shape of it before enabling: the employer is named on every ad, which sounds better than it is — **32 of 44 are ETTs** and 60 ads carried only 23 distinct employers, so the name is usually the agency and the workplace is described without being named. No postcode on any ad, and a salary on one in five |
| Turijobs | A **list of `ciudad`** as written in the URL — `barcelona`, `islas-baleares`, `madrid` — plus **`pais: ES`**, and say why: the `/es/` sitemap is the Spanish-**language** board, and 10 of 40 ads measured were in Germany, Portugal, France, Italy, Mexico or Andorra. A `desde` date is free too. **No browser, no compte, no clé.** Offer it for hostelería, hotels, kitchens, front desk, spa and housekeeping — not for anything else. Three things worth telling them: it is **the only board here that shows how many people already applied** (médiane 10, jusqu'à 156), it gives a **real postcode** where the other Spanish boards give none, and the employer is the hotel chain itself rather than an agency — Meliá, Barceló, H10. Warn them the salary is almost never a number: two ads in forty state one, whatever the field suggests |
| Bundesagentur für Arbeit | A **list of `wo` + `seit` pairs** — a city and a recency window — and say why the second is not optional: **the API returns at most 10 000 ads per query while reporting the real total**, so `Berlin` alone matches 45 901 and delivers 10 000. `wo: Berlin, seit: 7` is 8 786 and fits. **No browser, no compte, no clé.** Germany only, and it is the largest board in the plugin by a factor of thirty-five. Three things worth telling them: it names the employer on every ad, gives a **real postcode** on 192 of 200, and is the only board here that says outright whether the job is **Leiharbeit** — temp-agency work — because German law makes the employer declare it. Warn them the salary figures are usually an **hourly** rate, and that about one ad in ten is an *Ausbildung*, an apprenticeship rather than a job |
| JobsIreland | A **list of `location`** (free text — `Dublin` is 1 209 of 4 934) and, above all, **`kind: job`**. Say why, because it is the whole board: **more than half of what JobsIreland publishes is not employment** — 135 of the 250 newest ads are Community Employment Scheme placements, a state work-placement for long-term unemployed people entered through an Intreo office and paid on a social-welfare rate, not a post you apply to. Nothing on the ad says so in words. **No browser, no compte, no clé.** Ireland only. Worth adding: it gives a real **Eircode** on 195 of 251 ads, and a closing date on every one, but no salary and no description at all |
| Platsbanken | A **`kommun` or `region` code paired with a `sedan` date** — and say why the pair is not optional: **one query reaches 2 100 ads out of 39 865**, so Stockholm alone (6 371) overflows and Stockholm + one day (751) fits. **No browser, no compte, no clé du tout** — c'est un produit d'open data de l'État suédois. Sweden only. Three things worth telling them: every ad carries an **application deadline** and most a postcode and coordinates; the employer's **legal registration number** is on 293 of 300, which no other board here gives; and the salary field states the *type* of pay on every ad and the *amount* on none — so do not read "salary_type present" as "salary known" |
| Personio | The employers they would work for, **as careers URLs** — `<tenant>.jobs.personio.de`. **No login, no browser, no key**, and one request returns the employer's whole board with full descriptions. It is **the ATS most German, Austrian and Swiss SMEs use**, so offer it to anyone naming a DACH employer. Like umantis and Taleez there is **no resolver** — no directory, no cross-tenant search — so ask for the URL and never guess a tenant: a wrong one answers a 404 page, not an error. **Never pass a language**: asking for French returns every position with its description emptied, same count and same ids, and the adapter refuses rather than handing over blank ads. Warn them there is no salary and no closing date in the feed |
| Recruitee | The employers they would work for, **as tenant names or careers URLs** — `gmk` or `gmk.recruitee.com`. **No login, no browser, no key**, and one request returns the employer's whole board with descriptions. A European ATS — Netherlands, Belgium, Germany, Poland. There is **no directory**, but unlike SmartRecruiters a wrong tenant is *distinguishable*: it answers a JSON 404 rather than an empty board. `recruitee.py tenants --country NL` lists the tenants HiringCafe happens to have indexed, which is a hint rather than a census. Worth telling them: it states a **real salary on more than half the ads**, and the figure is usually **monthly** — reading it as annual is wrong by twelve |
| Pinpoint | The employers they would work for, **as tenant names or careers URLs**. **No login, no browser, no key**, and one request returns the whole board with descriptions already split — `key_responsibilities` is on every posting, which is what the scoring actually reads. There is **no directory**, but `pinpoint.py tenants --country <ISO2>` lists the tenants HiringCafe has labelled, which is a hint rather than a census. Worth telling them: about half the postings state a real salary range, the postcode is on four in five, and the ad key is the **posting** id — the provider also publishes a `jobs.json` whose ids look similar and are a different entity |
| Oracle Recruiting Cloud | The employers they would work for, **as careers hostnames** — `ecwl.fa.us2.oraclecloud.com`. **No login, no browser, no key**, and the whole board is readable with no cap. It is the most widespread ATS the plugin covers: measured present in twelve of twelve markets sampled. There is **no directory** — take the host from a careers URL; a host that is not a tenant answers the Oracle login page rather than an error, and the adapter says so. Warn them the listing carries **no description at all** — reading the ads costs one request each — and that the employer's own fields (department, job family, legal employer) were null on every row of the tenant measured |
| APEC | The **department codes** they would work in, as strings — `"75"`, `"69"`. **No login, no browser, no key.** Offer it to anyone in a cadre or senior role, and say the two things up front: it is the only French board that can be paged end to end, and it gives a **283-character teaser instead of the ad**, so `cover-letter` will ask them to paste the text. Any other filter is a numeric id with no public label — get them from `apec.py filters`, never from memory |
| HelloWork | A **list of facets** — a sector, optionally narrowed by town, or a job title. One facet is 20 ads and there is no page 2, so the facet list *is* the coverage. **Never ask them to type a slug**: run `hellowork.py facets --domaine <secteur>` and offer the towns and job titles the site actually publishes, because a slug that does not exist answers 404 with a full-looking page. **No login, no browser.** France only |
| Meteojob | A **list of `what` / `where` searches**, because one search is 20 ads and there is no page 2 — so the number of searches *is* the coverage. Build it from their target roles crossed with their commute towns, not one broad query per role. **No login, no browser.** France only. Tell them the cap up front: someone expecting a full board sweep will read 20 ads as a broken adapter |
| jobs.ch | Nothing — **no login needed to scan.** The same platform as jobup, German-speaking Switzerland. Offer it alongside jobup rather than instead of it: nationally it is ~3× the board, in Romandie it is thinner. Shared ad ids mean the ledger never doubles a row. **No French UI** — `de` or `en` only |

For HiringCafe, a **city** search needs the region name *and* the coordinates as
a complete set — the site has no public geocoder, and a partial location returns
zero ads with no error. Either collect all four (`city`, `region`, `lat`, `lon`)
or configure `country` alone. **Never invent coordinates**: wrong ones return a
plausible result set centred on the wrong place.

Multi-select which to enable, then **collect each one's required settings
immediately** — a board switched on with an empty required key is skipped at
scan time, which reads as a bug. Read the adapter's own *Configuration* section
for the exact keys and how the user obtains each one.

## 5b-bis — Where a key lives, and it is one answer for three boards

**Read this before 5c, 5e and La Bonne Alternance.** Three boards need a
credential the user creates, and **they take it in the same place**. It used to
be written once per board, in three shapes; the shapes were not the same and
two of them were older than the code.

**There is one place to put a credential, and the other two are terminal-only
fallbacks the code still reads.** Do not offer them side by side: an
installation built on either works until the day the person opens the same
plugin somewhere without a shell, and then stops, having changed nothing.

| where | in a terminal | outside one |
| :-- | :-- | :-- |
| **`<workspace>/credentials.env`** | works | **works — the only one that does** |
| `export` in the environment | works | **no**: the shell is reset between calls, so an exported variable does not survive from one to the next (#110) |
| `~/.<board>.env` | works | **no**: `$HOME` is a container's, not the person's folder (#109) |

**So the instruction is single**: the folder the user names or connects, then
`credentials.env` inside it. The two fallbacks stay in the code because
removing them would break every terminal install that has one — **they are not
a second answer to give.**

```
<workspace>/credentials.env
    FRANCE_TRAVAIL_CLIENT_ID=…
    FRANCE_TRAVAIL_CLIENT_SECRET=…
    ADZUNA_APP_ID=…
    ADZUNA_APP_KEY=…
    LBA_API_KEY=…
```

**The scripts read that file themselves** — `_secrets.py`, in this order: the
environment, then `<workspace>/credentials.env`, then the older
`~/.<board>.env`. **Nothing has to be sourced, and no shell is required.** A
user working in an app creates that one file and is done.

**Give them the resolved path, never `<workspace>`.** It is the one announced
in step 0, and if that was a different conversation, resolve it again rather
than asking them to remember:

```bash
JOB_HUNT_HOME="$(python3 "${JOB_HUNT_ROOT}/bin/workspace-path.py")"
echo "$JOB_HUNT_HOME/credentials.env"
```

**A placeholder is where this section fails a reader who has no shell.** The
adapters print the absolute path in their own missing-key message — which means
that without this line, **the surest way to learn where the file goes is to run
a sweep and let it fail.**

**The environment still wins**, so nothing changes for a terminal. And the
security rule does not move: **never in `config.yml`** — read aloud, pasted
into issues, backed up — **never in git**, and **never pasted into the
conversation.** The workspace is the user's data directory, not a repository.

**Telling somebody with no shell to run `export` is not help** — and that is
why the answer above does not depend on asking. The file route is prescribed
to everyone because it is the only one that holds in both places; a person with
a terminal loses nothing by using it, and the adapters' own messages still name
both routes for anyone who already has a key in the older place.

**And the resolution can settle nothing, on purpose.** If `Documents` is not
writable — which usually means the home folder is not the person's —
`workspace-path.py` exits **3** with a question instead of inventing a
directory. **Ask it, and use the folder they name.** Since v1.223.0 the
credential reader follows that same cascade, so the answer they give is the
answer the keys are read from.

**If they already had keys in the old default, the run says so and names the
file.** Nothing is lost; the folder simply has to be named once.

**Every shell command in 5c and 5e is bash**: `export`, `chmod 600` and
`set -a; . file; set +a` are bash, not PowerShell. On Windows that means WSL or
Git Bash — `README.md` documents both routes and this file does not repeat
them. **Say which shell you are asking for before you ask**: a Windows user
reading this page on its own runs these in PowerShell and gets errors that name
nothing.

**What is measured here, and what is not.** The failure behaviour below was
**measured on this repository on 2026-09-04**. The two "no" cells in the table
above are **not** — they are established by issues #109 and #110, from the
code and its history, and **nobody has run this plugin under CoWork to watch
`$HOME` resolve or an `export` survive.** The instruction is built on that
reasoning, and an onboarding is followed without being re-read, so it says
which of its claims were watched and which were argued.

**And a wrong key does not hide.** Measured 2026-09-04 on `adzuna` and
`labonnealternance`: a missing key and a wrong one both exit non-zero with
**nothing on `stdout`** and a message that names the cause. **Neither produces
an empty board** — so a board that comes back empty is a market, not a
credential.

**Then confirm it, because *"it did not fail"* is not *"it is set"*.** Somebody
who has just pasted two values into a file has seen nothing at all. One command
per board, and each says what it proves:

| board | check | what a good answer looks like |
| :-- | :-- | :-- |
| France Travail | `francetravail.py token` | `{"ok": true, …}` — §5c has the four outcomes |
| Adzuna | `adzuna.py count --country <cc> --what <term>` | a `matches` number, and it **announces its own cost**: *1 call of the 250/day* |
| La Bonne Alternance | `labonnealternance.py search --departement <dd>` | ads and recruiters — **there is no cheap check here**, the search is the check |

**`adzuna.py count` is the one to know**: a single call, under a second, and it
is the reason not to verify Adzuna with a `search`.

## 5c — France Travail: a key the user creates, and how to get it

**Skip this section entirely unless the user enabled `france-travail`.**

Every other board here needs nothing, or a URL. This one needs an OAuth
client_id and client_secret. They are free, self-service, and take about three
minutes — but the user will not find the path on their own, so walk them
through it. Do not ask for "your France Travail credentials" and stop there;
that is exactly the failure the prime directive is about.

**Say what it is, before asking.** France Travail publishes its vacancy
database through an API meant for exactly this kind of reuse. The key identifies
the application, not the person: it is **not** a France Travail *candidate*
account, it is not linked to their file as a jobseeker, and creating one tells
nobody they are looking. Users who are registered with France Travail often
assume the opposite, and the assumption stops them.

### The click path — give it in full, in one message

1. Go to **<https://francetravail.io>** and select **Inscription** (top right).
   Any email address works; this is a developer portal, separate from
   `francetravail.fr`.
2. Confirm the address, then sign in.
3. Open **Mes applications** → **Créer une application**. The name is free text
   — suggest `recherche-emploi-perso`. A description of one line is enough.
4. In that application, open the API catalogue and **subscribe it to
   « Offres d'emploi v2 »**. This is the step people miss: an application with
   no subscription authenticates fine and then returns `401` on every search.
5. The application page now shows an **Identifiant client** and a **Clé
   secrète**. The secret is shown in full — copy it now.

### Storing it — the plugin never types it

**Do not ask the user to paste the secret into the conversation, and never
write it into `config.yml`.** That file is read aloud, copied into issues and
backed up; a secret does not belong in it, and `francetravail.py` deliberately
cannot read one from there.

**Where the value goes is the same answer for all three boards, and it is in
§5b-bis.** Send them there rather than repeating it: France Travail, Adzuna and
La Bonne Alternance share one file.

Give them these two lines and ask them to run them **themselves**, with the `!`
prefix so the shell is theirs:

```bash
export FRANCE_TRAVAIL_CLIENT_ID='<identifiant client>'
export FRANCE_TRAVAIL_CLIENT_SECRET='<clé secrète>'
```

That lasts for one shell. For it to survive a reboot, the same two lines go in
their shell profile — `~/.zshrc` on macOS, `~/.bashrc` on most Linux. **Offer
to append them, do not just do it**: a shell profile is the user's, and an edit
they did not expect is worse than a manual paste. If they prefer, they append it
themselves and you say nothing further.

### Then check it, and say what the check proved

```bash
python3 "${JOB_HUNT_ROOT}/skills/job-scan/scripts/francetravail.py" token
```

Run this before finishing setup. A board that is switched on and unverified
turns into a failed sweep three days later, when nobody remembers this
conversation.

| What comes back | What it means | What to say |
| :-- | :-- | :-- |
| `{"ok": true, …}` | Credentials and subscription both good | Confirm it, and move on |
| `set FRANCE_TRAVAIL_CLIENT_ID…` | The exports did not reach this shell | They ran them in a different terminal, or in a subshell. Re-run both in the same session |
| `rejected the credentials (HTTP 400/401)` | Wrong id/secret, **or** step 4 was skipped | Send them back to the application page: check the subscription to « Offres d'emploi v2 » first, the secret second |
| `refused the scope` | Their application wants the id in the scope | The script prints the exact `--scope` string to use. Record it in `config.yml` as `scope:` so the sweep reuses it |

### If they stop partway

**Do not leave the board enabled with no key.** Two honest ways out, and the
user picks:

- Leave `france-travail` enabled and finish the rest of setup. `job-scan` will
  skip it each run, naming the missing credentials — visible, not silent.
- Set `enabled: false` with `dormant_since`, `dormant_reason: "clé API
  francetravail.io non créée"` and a `recheck_after` 90 days out. It comes back
  once, later, instead of being lost.

Both are fine. Guessing which one they meant is not.

---

### Turning a board *off* has two meanings — ask which one

When the user switches a board off, or when `/job-setup boards` is run to prune
a list that has grown, **do not assume they mean "never again".** Two different
intentions produce the same request, and `config.yml` can record both:

- **Off for good** — the board serves a trade they are not in. `enabled: false`,
  nothing else. Silent from then on, and never mentioned again.
- **Dormant** — it came back empty, but it is plausible: right region, right
  kind of employer, an adapter that worked. Write `enabled: false` **plus** the
  four `dormant_*` keys, and `job-scan` offers one cheap re-check per quarter
  instead of losing the board. See *The fourth state* in `shared/boards/README.md`.

**Keep the board's own configuration either way** — tenants, domains, cantons.
Waking a dormant board must be one line changed, not this interview repeated.

Dormancy is only honest when it carries the measurement that justified it:
`dormant_reason` takes **counts, not adjectives**. *"10 vacancies, all
apprenticeships"* is a reason; *"not relevant"* is a shrug the user cannot
re-read in three months.

Say clearly what happens if they enable none: `job-scan` will tell them there is
nothing to sweep, **and `cover-letter <ad URL>` still does the whole job for any
ad from any board.** Enabling a board is an optimisation, not a prerequisite.

If the user names a board that has no adapter, do not promise one and do not
improvise: hand it to the `board-request` skill, which records what an adapter
would need. **AMS is the one documented exception** — a board with no adapter
and a decision already taken. See 5d.

## 5d — AMS (Austria): a decision to take, not a value to fetch

**Run this section only when Austria is in scope** — flagged at step 3, or
Austria named as a target country. Skip it entirely otherwise; nobody outside
Austria needs to hear any of it.

**Check first whether the adapter exists** — `shared/boards/ams.md` and
`skills/job-scan/scripts/ams.py`. The two states read very differently and
blurring them is the failure this section exists to prevent:

| State | What this step is |
| :-- | :-- |
| **No adapter** (the state today) | An **advisory**. Explain, record their stance, configure nothing. `job-scan` sweeps no AMS ad whatever they answer, and you say so |
| **Adapter present** | A real enable step. Pre-fill from the recorded stance, confirm it in one question, and **do not run the explanation again** |

### Why this board gets a section instead of a table row

Every board in 5b asks *can we*. This one asks *should we*, and the answer is
the user's, not yours. So give them the facts and let them decide — **do not
present it as a recommended setting and never pre-tick it.**

Say this, in one message, in this order:

1. **What AMS is.** Austria's federal public employment service, and the largest
   single source of Austrian vacancies — the equivalent of France Travail.
2. **What its `robots.txt` says.** Quote it; it is four lines and it convinces
   better than any summary:

   ```
   user-agent: LinkedInBot     Allow: /public/emps/    Disallow:
   user-agent: *               Allow: /public/emps/$   Disallow: /public/emps/
   ```

   `LinkedInBot` gets the employer pages entire. Everyone else gets that exact
   index page — the `$` — and nothing beneath it.
3. **What this project decided, and on what ground.** Not that the obstacle is
   inconvenient: that a publicly funded body has granted machine access to one
   privately held platform and refused it to every other actor, free or paid,
   closed or open-source. The rule it was decided by — four questions, and a
   default of *obey* that every other case lands on — is in
   `shared/robots-policy.md`. Offer the file; do not paraphrase it into a slogan.
4. **What it costs them, not us.** The realistic failure is AMS blocking the
   address the requests come from — **theirs** — which costs them their own
   ordinary use of the site. Say it plainly and early.
5. **That there are two, and which.** AMS and SmartRecruiters (5f), and no
   others. Softy, Tecnoempleo, InfoJobs and Leboncoin are refused on files of
   the same kind, and stay refused. A user who hears "we override robots.txt"
   without hearing "twice, here and here, for this reason" has been told
   something false about the plugin. **Do not say "the only one" — it stopped
   being true on 2026-09-03.**

### The question, and the three answers it can have

`question`, single select, no default:

- **Enable it** — they accept the override for their own workspace.
- **Leave it off** — a hard no.
- **Decide later** — recorded as undecided.

### Recording it — and why not as a board

**With no adapter, write nothing under `boards:`.** A board switched on with no
adapter behind it is skipped at scan time and reads as a bug; an entry the
scanner does not recognise is worse. `shared/boards/README.md` lists four board
states and says never to improvise a fifth — this is not one of them. Record it
outside that structure:

```yaml
pending_decisions:
  ams:
    stance: opt_in          # opt_in | declined | undecided
    decided_on: 2026-08-31
    basis: shared/robots-policy.md
```

**Once the adapter ships**, that stance becomes an ordinary board block — plus
the key the policy requires:

```yaml
boards:
  ams:
    enabled: true
    override_robots: true   # absent or false → skipped, and the skip is reported
```

**`enabled: true` without `override_robots` is not half-configured, it is the
safe state.** Never write one without the other on the user's behalf, and never
infer the override from `enabled` — that inference is the whole thing this
design exists to prevent.

### If they decline

`stance: declined`, and that is a **hard off**: never swept, never probed, never
mentioned — including when the adapter ships. **Not dormancy**: dormancy means
*wrong month, not wrong board*, and a refusal on principle is neither. The only
thing that reopens it is the user asking.

### What to say before moving on, whatever they answered

**Do not promise them the `cover-letter <URL>` fallback here.** It is the honest
answer on Leboncoin, whose file permits the fetch and refuses only the sweep.
AMS is not that shape: its `Disallow` is **path-based and applies to everyone**,
so an ad page under `/public/emps/` is covered by the same rule as the listing.
**Whether AMS ad URLs live under that path has not been established** — the
index page is the only thing this project has fetched there — and settling it is
part of building the adapter, not something to assume in a setup conversation.

So say the true thing: today AMS is not swept, and if they have an AMS ad in
hand, **pasting its text into `cover-letter` works and raises no question at
all.**

## 5e — Adzuna: a second key, and the smallest budget here

**It was missing from this guide entirely.** `adzuna.py` documents its own
convention and a user following these pages never learned the adapter existed
or that it needed a key — they found out by running it and reading the error.
Issue #106.

**Say what it is.** Adzuna aggregates vacancies across nineteen countries and
publishes them through a developer API. The key identifies the application, not
the person, and creating one tells no employer anything.

### The click path

1. Go to **<https://developer.adzuna.com>** and register. Any email works.
2. The dashboard shows an **Application ID** and an **Application Key**. Both
   are needed; neither is a password.

### Storing it — a file, not the config, and not the conversation

**Do not ask the user to paste the key into the conversation, and never write
it into `config.yml`.** Same reason as 5c: that file is read aloud, pasted into
issues and backed up.

**Both values go in the file of §5b-bis**, one per line, and nothing else is
needed:

```
<workspace>/credentials.env
    ADZUNA_APP_ID=…
    ADZUNA_APP_KEY=…
```

**`adzuna.py` reads that file itself** — no `export`, no sourcing, no shell.
That is the route to give by default, and the only one that works in an app.

**In a terminal, the older convention still works** and is worth offering to
anyone who already keeps keys that way — `~/.adzuna.env`, sourced into the
shell that runs the sweep:

```bash
printf 'ADZUNA_APP_ID=%s\nADZUNA_APP_KEY=%s\n' '<app id>' '<app key>' \
  > ~/.adzuna.env
chmod 600 ~/.adzuna.env
set -a; . ~/.adzuna.env; set +a
```

**That last line is the one people lose** — which is why it is the fallback and
not the instruction. A shell that has not sourced it gets the adapter's own
message naming both variables and both routes, which is the intended behaviour
and not a failure.

### The budget is the constraint, and it is small

**250 calls a day, for all nineteen countries together.** That is not a rate
limit to pace around; it is a daily ceiling. Say it while enabling the board,
because a user who configures five countries has divided it by five.

*(And nothing measured through Adzuna goes into a country page or the Atlas —
a separate rule, recorded where those are written.)*

## 5f — SmartRecruiters: the second override, and the adapter already exists

**Run this whenever SmartRecruiters is in scope** — it is a global ATS, so
that is most workspaces, unlike AMS which only matters for Austria.

**This is the "adapter present" state of 5d's table, not the advisory one.**
`ats.py` reads SmartRecruiters today, so the answer decides whether a working
board keeps working. Do not run 5d's explanation again if it has already been
given; give the facts below once and ask.

### What to say, in this order

1. **What it is.** One of the large applicant-tracking systems; the postings of
   any employer using it, through `api.smartrecruiters.com`.
2. **What its `robots.txt` says.** Seventy-two bytes, and quoting them is
   better than any summary:

   ```
   User-agent: LinkedInBot     Allow: /v1/companies/
   User-agent: *               Disallow: /
   ```

   **The same shape as AMS**: opened to one privately held platform, closed to
   everyone else — free or paid, closed or open-source.
3. **What it costs them, not us.** The realistic failure is SmartRecruiters
   blocking the address the requests come from — **theirs**. Say it plainly
   and early, exactly as in 5d.
4. **That there are two overrides in the plugin, and this is the second.**
   Greenhouse, Workable and Lever publish files of the same kind that permit
   and are read with none of this; Softy, Tecnoempleo, InfoJobs and Leboncoin
   are refused and stay refused. **The override does not generalise, and
   saying so is part of the offer.**
5. **What was got wrong first**, if they ask why the file argues with itself:
   an `llms.txt` was cited as an invitation addressed to AI agents. It sits on
   other hosts, one copy is generated by an SEO plugin, and it indexes
   marketing and documentation pages. **The most specific declaration for the
   API host is its own file, and it refuses.** `shared/boards/smartrecruiters.md`
   carries the retraction.

### The question, and the three answers it can have

`question`, single select, **no default and nothing pre-ticked**:

- **Enable it** — they accept the override for their own workspace.
- **Leave it off** — a hard no. The board is skipped and says so on every run
  that reaches it; it is never raised again.
- **Decide later** — recorded as undecided, and the board stays skipped.

### Recording it

**The adapter exists, so this is a real board entry**, unlike AMS:

```yaml
boards:
  smartrecruiters:
    enabled: true
    override_robots: true    # absent or false → skipped, with the reason
```

**`enabled: true` without `override_robots` must report the skip and say why**
— `never-fail-silently.md`. That is what `ats.py` does: exit 7, naming the
rule, saying the key is missing and what it would cost.

**And the run says it out loud, once, every time:**

> `[smartrecruiters] robots.txt override ACTIVE — api.smartrecruiters.com
> disallows everything to all agents but LinkedInBot. You enabled this, and
> the address that gets blocked is yours.`

## 6 — Thresholds and document preferences

- **Apply-from threshold** (`question`: 70 selective / 55 broad / 40
  urgent). Frame it honestly: a lower threshold means more applications and more
  rejections, and it is the right setting when time or income is short. This
  number is a **default, not a rule** — every application still passes a
  go/no-go gate where the user decides.
- **Resume length**: one page strict, or up to three pages with nothing cut.
- **Compensation estimate**: on by default. Explain what it is before asking —
  at the go/no-go gate, an estimate of what the role pays and where they would
  land in it, always as a range with its source. Then ask for their **currency**
  and, optionally, a **floor**. Say plainly what the floor does and does not do:
  a range below it is flagged once, and never turned into a recommendation
  against applying — circumstances decide that, not a number. Say too that the
  estimate never enters their resume, their letter, or a salary field on a form.
- **Signature**: offer it, do not require it (step 7).

---

## 7 — Optional modules

Offer each one, explain what it costs and what it gives, and default to *off*.

**Unemployment-office declaration.** Ask whether the user must report their job
search to an unemployment office. If yes and a module exists for their country
(`shared/modules/`), enable it in `config.yml`; if no module exists, say so
plainly and record the fields their office asks for in `candidate.md` so nothing
is lost. Every such module carries a responsibility notice — read it out at the
moment it is enabled, not just when it is used.

**Handwritten signature.** If the user wants one on their cover letters:

```bash
"${JOB_HUNT_ROOT}/skills/cover-letter/make-signature.sh" <scan.pdf|scan.png> "$JOB_HUNT_HOME/signature.png"
```

Tell them how to produce the input: sign a **blank white sheet** with a dark
pen, photograph or scan it flat in good light, and give the path. The script
keys out the paper and writes a transparent PNG. Without a signature file the
letter simply leaves blank space to sign by hand — which is a perfectly normal
outcome, not a failure.

**Local repository evidence.** Explain the problem it solves: profile exports
systematically *understate* the stack, and whole technologies backed by real
authored code are often missing from them. Offer to inspect repositories the
user names — manifests, file counts, commit authorship — and write `repos.md`:
what is genuinely there, **at what depth**, and what must never be claimed.

Two rules to state while offering it, because they are what make the file
trustworthy:

- It records **depth**, not just presence: a prototype is labelled a prototype.
  The scoring reads it literally, so an inflated line here corrupts every score.
- It must carry a **confidentiality note** for anything belonging to an
  employer. Work under NDA can support a claim at architecture level and must
  never surface endpoints, internal names or ticket references in a document
  sent to a third party.

---

## 8 — Write, verify, and hand over

Write `config.yml` (from `templates/config.example.yml`) and `candidate.md`
(from `templates/candidate.example.md`), create the ledger from
`templates/job-pipeline.example.md` if it does not exist, then **verify**:

```bash
ls -la "$JOB_HUNT_HOME" "$JOB_HUNT_HOME/profile"
```

Report to the user:

- the workspace path and what is in it, file by file, one line each;
- **which optional pieces are absent and what each one costs** — "no `repos.md`,
  so scoring sees only what your exports declare";
- how to change any of it: edit the file directly, or run `/job-setup`;
- **one concrete next step**, not a menu: *"run `/job-scan` to fill the pipeline,
  or `/cover-letter <ad URL>` if you already have an ad in mind."*

Never end setup with a wall of configuration and no next action.
