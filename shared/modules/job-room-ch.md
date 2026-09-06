# Module — Switzerland: ORP job-search evidence (`job-room.ch`)

Enabled with `modules.unemployment_declaration: "job-room-ch"` in `config.yml`.
When it is `none`, ignore this file entirely.

Registered jobseekers in Switzerland must report their applications to their ORP
as **preuves de recherche personnelle d'emploi (PRE)**, monthly, on
<https://www.job-room.ch>. This module captures the fields that form demands
**while the ad is still open**, because hunting them down three weeks later
costs far more than noting them now.

---

## Responsibility — state this every time the module produces data

> **You are solely responsible for what you submit to your ORP.** This module is
> a **submission aid**: it collects and pre-fills information. It does not
> replace your own check, and it carries no authority over what your ORP
> accepts.
>
> **Read every field before you send it.** A declaration to an unemployment
> office is an official statement with real consequences — an incorrect or
> incomplete one can affect your entitlement. Nothing here is legal or
> administrative advice, and the plugin's authors accept no liability for a
> declaration made with its help.
>
> If a field is uncertain, leave it to the user. **Never invent a value on an
> official form** — not a postcode, not a date, not a company address.

Say this to the user **the first time the module is enabled**, and repeat the
short form — *"check every field before you submit; you are the one signing
this"* — each time the module produces PRE data or fills the form.

---

## Capturing the fields — during the dossier step, not later

Write a `## Job-room data (PRE)` block at the end of the dossier's `job-ad.md`:

| Job-room field | Required | Where to find it |
| :-- | :-- | :-- |
| Application date | yes | the day the send is confirmed — **and on a `rejected` row the ledger no longer holds it, see below** |
| **Company** — exact legal name | yes | the ad. For a recruitment agency, the declarable employer is **the agency**, not the unnamed end client |
| Street and number | no | the ad, the site footer, or the commercial register |
| Country | yes (Switzerland by default) | the ad |
| **Postcode / town** | **yes** | the ad. **This is the field that is missing most often**: an ad saying only "Vaud" or "remote" is not enough — find the registered office (commercial register, contact page) and record it here |
| Contact person, email, phone | no | the ad |
| **Job title** | yes | the ad's exact wording |
| **Link to the online form** | yes, as soon as the application is electronic | the full ad URL — a truncated identifier is unusable |
| Occupancy rate | yes | full time / part time, per the ad |

**When the ad came from the `job-room` sweep, some of this arrives already
filled — but less of it than you would expect.** Measured on 100 fresh VD/GE
ads on 2026-08-28: the employer name is always present, **postcode and town on
39**, **street and number on 7**, an AVAM number on **2**. So the adapter is a
head start on the postcode field, not a way to skip it. Everything still gets
read before it goes on the form, and a missing town is still asked for, never
inferred. See `shared/boards/job-room.md`.

Two traps seen in real use:

- **A recruitment agency whose end client is not named** leaves the town
  unfindable. Ask the user for it rather than inventing a postcode on an
  official form.
- **A remote role with a foreign employer** requires changing the country, which
  turns the postcode/town field into two free-text fields.

Rows that reach `applied` **or `rejected`** carry a job-room marker at the head
of their `Note` — `` `JR:YYYY-MM-DD` `` once declared, or `` **`JR:missing`** ``
while it is not. A quick audit the user can run themselves:

```bash
grep -E '^\| ' "$JOB_HUNT_HOME/job-pipeline.md" | grep -c 'JR:missing'
```

It should fall to zero after every session of applications — the PRE is
transmitted to the ORP on a fixed date, and an application not entered before
that transmission does not count as evidence.

**The `grep -E '^\| '` prefix is not optional, and this is why.** A bare
`grep -c 'JR:missing' job-pipeline.md` counts *every* occurrence in the file,
including the `Log` section — and the log is exactly where the marker gets
discussed, so the count inflates as soon as anyone writes about it. Observed on
a real ledger on 2026-08-27: the bare command returned **8** where the true
number of undeclared applications was **3**. Restricting to table rows is what
makes the number mean what it says.

This affects only the manual command. `job-report` parses the table properly and
its `jr_missing` figure was never wrong.

**`rejected` is included deliberately.** An application the employer turned down
still went out, and it is exactly the kind that gets forgotten in a declaration.
**Never strip that marker** when updating a row: it is how the user sees, at a
glance, which applications are still undeclared.

### A third state: `` `JR:waived YYYY-MM-DD` ``

`JR:missing` means *not declared yet*. `` `JR:<date>` `` means *declared*. Some
applications are neither: the user has decided, deliberately, **never** to
declare this one — most often because a field the form demands cannot be
recovered.

Without a marker for that, such a row is re-proposed at every session forever,
and the only way to silence it is to delete the evidence of a real application.
So it gets its own state:

```
**`JR:waived 2026-08-31`** — decision of <date>: not to be declared. Reason: …
```

Three rules, and they are the point of the marker:

- **The application still counts.** It went out; it stays in `applied` +
  `rejected` and in every volume figure. Only its PRE entry is abandoned.
- **Record the reason in the same note.** A waiver whose motive is lost reads,
  months later, exactly like an oversight.
- **`plan` lists it, it does not hide it.** A decision that silently removes a
  row from view is indistinguishable from a row that was lost.

Only the user decides this. Never waive a row to make a count come out clean.

**The `job-report` skill surfaces this automatically.** It counts `JR:missing`
rows over the whole ledger and reports them with any period report — because a
period report is exactly the moment the user is thinking about their
declaration, and a total that hides an undeclared application is worse than no
total.

---

### A `rejected` row does not carry the date this form asks for

**`applied → rejected` is a legitimate transition, and it overwrites the send
date with the employer's answer.** The form asks for the send. So an
application that went out on 20 August and was refused on 2 September appears
in the plan dated **2 September** — and declaring it there **puts it in the
wrong period**, while August transmits on a fixed date.

**`plan` flags those rows** — `<- NOT the send date` — and it **does not invent
a send date**, because the ledger no longer has one. **Ask the user when it
went out**, and enter that. A guess here is a false entry in an official
declaration.

*(Found on 2026-09-03 while checking whether a wrinkle in `job-report
--interviews` was local to that view. It was not: the same set of statuses is
right for asking **whether** an application left and wrong for asking
**when**.)*

## Work out what job-room actually needs — `jobroom_sync.py plan`

**Never reconstruct this by reading the whole period by eye.** A period holds
tens of entries (17 to 64 a month on a real account), and re-deriving the delta
each session is both slow and the moment mistakes enter.

```bash
python3 "<job-report skill>/scripts/jobroom_sync.py" plan
```

It reads the ledger and splits it in two:

- **`to declare`** — sent (`applied` / `rejected`) and never declared.
- **`result changed since declaration`** — declared, but the employer answered
  *afterwards*, so job-room still shows the old result.

**The second list is the one no count can surface.** Those rows are declared, so
they miss nothing; what is stale is the outcome recorded beside them. It needs
no new field: the ledger already dates the status (`rejected 2026-08-20`) and
the declaration (`JR:2026-08-18`), and comparing the two *is* the test. A row
whose refusal is later than its declaration still reads *En suspens* in
job-room.

`mark-synced` records when the period was last brought up to date:

```bash
python3 "<…>/jobroom_sync.py" mark-synced --entries <count shown by job-room>
```

It writes `$JOB_HUNT_HOME/.jobroom-sync.json`. The timestamp is context for the
user, **not** a permission to skip the check below.

---

## The duplicate check is not optional — `jobroom_sync.py check`

**RULE: nothing is written into a PRE until the period has been read and the
candidate row has been rapproché against it.** Two entries for one application
is an inaccurate official declaration; a missing one is a search that does not
count. Both are invisible in a row count.

```bash
# capture the complete period listing with browser_eval, then:
python3 "<…>/jobroom_sync.py" check --jobroom-text listing.txt
```

Output is three lists — `safe to enter`, `BLOCKED as duplicate`, and the
employers already present under **another** role. **Enter only what it calls
safe.**

**If the listing cannot be read, it refuses and exits `2`.** An
unrecognised text is never read as "verified, no duplicate found": that is the
one outcome the check exists to prevent, and it is the reason the refusal is an
exit code rather than a printed remark.

**An empty period is not that case, and used to be treated as it.** The check
recognised entries only by their `Postulation du …` markers, so *"I could not
read the page"* and *"this period is legitimately empty"* were the same
condition — and **the first entry of every month was unreachable through the
documented path** (issue #49). job-room states its own count on every period,
so the two numbers are now reconciled and there are three outcomes:

| job-room says | rows read | verdict |
| --: | --: | :-- |
| `0` | 0 | **genuinely empty** — safe to enter, no duplicate is possible |
| `n > 0` | `n` | listing read; run the duplicate check |
| `n > 0` | `0` or `≠ n` | **refused** — the capture is partial |
| *no period at all* | — | **refused** — this is not the listing |

The third row is stricter than what it replaces: five rows of forty-eight parse
perfectly well and used to clear duplicates that were plainly there.

### Feed it complete page text, never only the visible rows

**The job-room list is virtualised.** A visible `browser_snapshot` can return
only the rows currently on screen — **5 exposed out of 48** on a measured run —
so a check built on it sees almost nothing and clears entries that are plainly
there. Use `browser_eval` to extract the complete period text. The script
rejects visible-row-shaped input rather than trusting it.

Complete page text does **not** carry the state of the radio buttons, so it cannot
tell you the *Résultat de l'offre de service*. That is what `plan`'s second list
is for; the two are complementary and neither replaces the other.

### The key is employer + job title, never the employer alone

Measured on one real session — 48 existing entries, 11 to add — matching on the
employer alone would have discarded **four genuine applications**:

| Already in job-room | About to be entered |
| :-- | :-- |
| an intermediary with 1 role | 2 further, different roles |
| an employer with 2 roles | 1 further, different role |
| an agency under one reference | a different reference |

The reverse error — matching too loosely — creates the duplicate. So the script
normalises case, accents and punctuation and nothing else: no stemming, no
dropping "senior", no collapsing "PHP/Symfony". Fusing two real roles at one
employer is how an application disappears.

**When it is still ambiguous, the user decides — not the agent.** Do not write,
do not discard: name the doubt and ask.

---

## Optional — assisted filling of the job-room form

Only on the user's explicit request. This is **assistance, never submission on
their behalf**.

### Prerequisites — say both out loud before starting

1. **OpenWork's native browser must be available.** This step
   drives the user's own browser. If it is unavailable, say so plainly and fall back to handing them the
   captured values to type in themselves — which is a perfectly good outcome.
2. **The user must log in to job-room.ch first, themselves.** It is an
   authenticated space tied to their AVS number and their ORP file. The plugin
   works *inside their existing session*: it never signs in for them, never
   handles their credentials, and never touches their account settings. Ask
   them to log in and confirm before anything is opened:
   *"open <https://www.job-room.ch> in OpenWork's browser, log in, and tell me when you're
   in — I work in your session and I won't sign in for you."*

If the page comes back logged out, name it, give the URL, and wait. Do not try
to work around the login.

### Filling

**Order of operations, and it is not negotiable:**

1. `plan` — what the period is missing, and what it has wrong.
2. Open the period and capture the complete listing with `browser_eval`.
3. `check` — and enter **only** the rows it calls safe.
4. Fill the form.

Then fill **only** the fields captured above, and follow the same rules as any
other form in this plugin: truth only, no guessing, leave unknown fields blank
and ask.

**Reaching step 4 without step 3 is a bug, not a shortcut.** No delta, no
timestamp and no "I just looked at the list" replaces it — a saisie made
manually by the user between two sessions appears in no state file.

### The gate — saving a row is not declaring a period

**job-room separates two acts, and so must this module.** Captured live on
2026-09-01 from the period listing:

| Act | What it is | Whose |
| :-- | :-- | :-- |
| **Sauvegarder** an entry | one line added to an **open, still-editable** period. Reversible, correctable and deletable right up to the deadline | a data-entry step — **the plugin may do it** |
| **Transmission** of the period | the **official declaration reaching the ORP** — automatic at a stated date, or manual from one | **the user's, irreducibly** |

`Nombre saisi: 48` on a period that has not been transmitted is the proof:
forty-eight rows saved, nothing declared.

**So save the row.** Once the fields have been captured from the ad, `check`
has cleared it and the values have been shown, the write is the plugin's to
make. The August 2026 period held 48 entries; a rule that hands each one back
as a manual click returns most of the module's value to the user as work, and
the forty-eighth save is not reviewed more carefully than the first — it is
reviewed less. *(Issue #51, open across thirty-six releases.)*

**And never touch the transmission.** Do not trigger a manual one, do not
confirm one, do not offer to. **Never describe a period as *declared* because
entries were saved into it** — that sentence would be false in the one place
where a false sentence costs the user an official declaration.

### After saving: say what was written, where, and by when

**The gate moves to the period.** The review that protects a declaration is the
whole period read before its deadline, not each row at the moment of typing —
so after saving, the module owes the user three things:

```bash
# re-capture the complete listing with browser_eval, then:
python3 "<…>/jobroom_sync.py" periods --jobroom-text listing.txt
```

1. **What was written** — every field and its exact value, and what was left
   blank and why.
2. **Which period it went into**, with job-room's own count.
3. **That period's deadline, always.** *"48 entries in Août 2026; automatic
   transmission 06.09.2026 at 00:00 — review the period before then."*

**The deadline is the one date that separates a correctable mistake from a
false declaration**, and it is printed on the page already. Report it whenever
a period is touched, even when nothing was written.

### What stays the human's, whatever the automation

- **The transmission.** Always.
- **Any field where the answer is the user's judgement about themselves** — the
  **sought occupation rate** above all. What an insured person declares there
  bears on their fitness for placement, and it is not the plugin's to decide.
- **A value that is not on the ad.** No invented postcode, no guessed legal
  name — the existing rules on that do not move.

### Confirming the write, and only then the marker

The write is verifiable, so verify it rather than assuming it: re-capture the
listing and check that job-room's own count rose by the number of rows saved.
`check` refuses when its two numbers disagree, which is the same test.

Only then update the ledger row marker to `` `JR:YYYY-MM-DD` ``. An
unconfirmed write stays `` **`JR:missing`** ``: the value of that marker is
that it never lies. **And it means *saved into the period*, never
*transmitted*** — those are different facts and the ledger records the one it
can verify.

### After

Then record the synchronisation, so the next session starts from the delta
rather than from the whole period:

```bash
python3 "<…>/jobroom_sync.py" mark-synced --entries <count job-room now shows>
```

**Only after the write has been confirmed against job-room's own count**, for
the same reason as the marker: a timestamp written for rows that did not land
makes the next run skip exactly the ones that still need attention.
