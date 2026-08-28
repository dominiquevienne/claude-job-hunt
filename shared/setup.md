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
├── signature.png               # optional
├── profile/                    # the user's source documents
└── job-pipeline.md             # the shared ledger
```

Resolve the workspace in every command, never hardcode it:

```bash
JOB_HUNT_HOME="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
```

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

Ask in batches with `AskUserQuestion` where the options are closed (work modes,
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
`AskUserQuestion`:

### Route A — LinkedIn exports (best, and what the skills are tuned for)

Five files. The first is one click; the other four are browser prints. Give the
user this block verbatim, with `<handle>` replaced by their own LinkedIn handle
once known:

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
"${CLAUDE_PLUGIN_ROOT}/skills/cover-letter/sync-sources.sh" "<Full Name>" "$JOB_HUNT_HOME/profile"
```

The script looks in Downloads and on the Desktop, accepts both naming shapes
LinkedIn produces, and reports one line per file: `✓ found` or `– missing`.

### Route B — an existing CV

Any PDF or DOCX. Ask for the **absolute path**, copy it to
`$JOB_HUNT_HOME/profile/`, and extract the history from it. Say plainly that a
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
| The file exists | `test -f` | Which name was looked for, in which two folders, and that the export probably landed elsewhere — ask them to drag it into Downloads, or give the absolute path instead |
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
2. **Maximum one-way commute**, in minutes (`AskUserQuestion`: 30 / 60 / 90 /
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

## 5 — Target roles and the search sweep

**Propose, then confirm.** Read the skills and experience gathered in step 1 and
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

List what exists in `shared/boards/`, with what each one needs:

| Board | Needs |
| :-- | :-- |
| job-room.ch | The cantons they would work in (official uppercase codes), or a point and a radius of at least 10 km. **No login, no browser.** Switzerland only. Reaches the SMEs, foundations and staffing agencies HiringCafe misses |
| HiringCafe | Their ISO-2 country code. **No login, no browser, no extension** — it is plain HTTP, and the only sweep that works without Chrome. Worldwide; thin in emerging markets, and blind to the Swiss ATS (Refline, Ostendis, Umantis) |
| LinkedIn | Their own profile URL, and they must be logged in themselves, in the Chrome the Claude extension is connected to |
| jobup.ch | Nothing — **no login needed to scan.** Swiss ads, French-speaking Switzerland |

For HiringCafe, a **city** search needs the region name *and* the coordinates as
a complete set — the site has no public geocoder, and a partial location returns
zero ads with no error. Either collect all four (`city`, `region`, `lat`, `lon`)
or configure `country` alone. **Never invent coordinates**: wrong ones return a
plausible result set centred on the wrong place.

Multi-select which to enable, then **collect each one's required settings
immediately** — a board switched on with an empty required key is skipped at
scan time, which reads as a bug. Read the adapter's own *Configuration* section
for the exact keys and how the user obtains each one.

Say clearly what happens if they enable none: `job-scan` will tell them there is
nothing to sweep, **and `cover-letter <ad URL>` still does the whole job for any
ad from any board.** Enabling a board is an optimisation, not a prerequisite.

If the user names a board that has no adapter, do not promise one and do not
improvise: hand it to the `board-request` skill, which records what an adapter
would need.

## 6 — Thresholds and document preferences

- **Apply-from threshold** (`AskUserQuestion`: 70 selective / 55 broad / 40
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
"${CLAUDE_PLUGIN_ROOT}/skills/cover-letter/make-signature.sh" <scan.pdf|scan.png> "$JOB_HUNT_HOME/signature.png"
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
