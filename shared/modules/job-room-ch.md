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
| Application date | yes | the day the send is confirmed |
| **Company** — exact legal name | yes | the ad. For a recruitment agency, the declarable employer is **the agency**, not the unnamed end client |
| Street and number | no | the ad, the site footer, or the commercial register |
| Country | yes (Switzerland by default) | the ad |
| **Postcode / town** | **yes** | the ad. **This is the field that is missing most often**: an ad saying only "Vaud" or "remote" is not enough — find the registered office (commercial register, contact page) and record it here |
| Contact person, email, phone | no | the ad |
| **Job title** | yes | the ad's exact wording |
| **Link to the online form** | yes, as soon as the application is electronic | the full ad URL — a truncated identifier is unusable |
| Occupancy rate | yes | full time / part time, per the ad |

Two traps seen in real use:

- **A recruitment agency whose end client is not named** leaves the town
  unfindable. Ask the user for it rather than inventing a postcode on an
  official form.
- **A remote role with a foreign employer** requires changing the country, which
  turns the postcode/town field into two free-text fields.

Rows that reach `applied` **or `rejected`** carry a job-room marker at the head
of their `Note` — `` `JR:YYYY-MM-DD` `` once declared, or `` **`JR:missing`** ``
while it is not.

**`rejected` is included deliberately.** An application the employer turned down
still went out, and it is exactly the kind that gets forgotten in a declaration.
**Never strip that marker** when updating a row: it is how the user sees, at a
glance, which applications are still undeclared.

---

## Optional — assisted filling of the job-room form

Only on the user's explicit request. This is **assistance, never submission on
their behalf**.

### Prerequisites — say both out loud before starting

1. **The Claude Chrome extension must be installed and connected.** This step
   drives the user's own browser; without the extension there is no browser at
   all. If it is missing, say so plainly and fall back to handing them the
   captured values to type in themselves — which is a perfectly good outcome.
2. **The user must log in to job-room.ch first, themselves.** It is an
   authenticated space tied to their AVS number and their ORP file. The plugin
   works *inside their existing session*: it never signs in for them, never
   handles their credentials, and never touches their account settings. Ask
   them to log in and confirm before anything is opened:
   *"open <https://www.job-room.ch> in Chrome, log in, and tell me when you're
   in — I work in your session and I won't sign in for you."*

If the page comes back logged out, name it, give the URL, and wait. Do not try
to work around the login.

### Filling

Navigate to the PRE form, fill **only** the fields captured above, and follow
the same rules as any other form in this plugin: truth only, no guessing, leave
unknown fields blank and ask.

### The gate — the user submits, always

**Never click the final submit button.** At the end:

1. Show every field and the exact value placed in it.
2. Show what was **left blank** and why.
3. Repeat the short responsibility line.
4. Tell the user the form is ready **on screen** and that it is theirs to check
   and submit.

Then stop. Unlike a job application — where the user may delegate the click —
an official declaration is submitted by the person it belongs to. Do not offer
to press it.

### After

Only once the user confirms the declaration went through, update the ledger row
marker to `` `JR:YYYY-MM-DD` ``. An unconfirmed submission stays
`` **`JR:missing`** ``: the value of that marker is that it never lies.
