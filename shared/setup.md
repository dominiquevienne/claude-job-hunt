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

### Then four questions, and they are closed on purpose

Use `AskUserQuestion` — one call, all four, each with the consequence stated in
the option text so nobody is choosing blind.

| # | Question | Options | What it decides |
| :-- | :-- | :-- | :-- |
| 1 | **Chercher dans la continuité de ce profil, ou autre chose ?** | Continuité · Élargir aux métiers adjacents · Reconversion, autre métier · Peu importe, je regarde ce qui passe | The search queries in step 5, the scoring rubric's treatment of gaps, **and whether the CV is a target or just a history** |
| 2 | **Mobilité géographique ?** | Rester dans ma région · Ailleurs dans le pays · Un autre pays · Full remote, le lieu m'est égal | Which country's boards exist at all, and whether the commute limit from step 3 still applies |
| 3 | **Quels pays / régions ?** *(only if 2 ≠ "rester")* | Free text, or a country list | The board shortlist, and the language check below |
| 4 | **Quels types de contrat acceptez-vous ?** | CDI / permanent · CDD, mission, projet · Intérim · Freelance / indépendant · Alternance, stage, premier emploi | Whether the **agency boards** are worth enabling at all, and which sector boards apply |

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
| **Wants LinkedIn / Easy Apply** | LinkedIn | Needs their own Chrome and their own logged-in session — say so before enabling, not after |

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

| Board | Needs |
| :-- | :-- |
| Workday | The employers they would work for. **No login, no browser.** Where the large Swiss employers are — Swisscom, Swiss Life, Roche, Lindt. Each board needs three coordinates (host, tenant, site); resolve them with `workday.py resolve "<employer>"`, and ask which site when an employer runs several |
| Solique | The employers they would work for, **as tenant names** — the path segment of any of their ad URLs (`iss`, `ktzh`, `manor`). **No login, no browser.** Warn them that some tenants only serve a truncated listing: the adapter says so per run, and the count is not the size of the board |
| SAP SuccessFactors | The employers they would work for, **as careers domains** — `jobs.<employer>.ch`, `www.carrieres-<employer>.com`. **No login, no browser.** Never guess the site's locale: one the tenant does not publish returns an empty board with no error at all. `successfactors.py locale --host <host>` reads the right one |
| umantis | The employers they would work for, **as careers URLs** — `recruitingapp-<n>.umantis.com` or the employer's own `jobs.<employer>.com`. **No login, no browser.** Unlike the other ATS boards there is no resolver: HiringCafe indexes no umantis ad, so a tenant cannot be looked up from a name. Ask for the URL; never guess a tenant number, because a wrong one serves the vendor's marketing page and looks like an employer with nothing open |
| La Bonne Alternance | The **departments** they would work in, **exactly two characters** — `69`, `2A`. **No browser, no login, but a free API key**: an account at api.apprentissage.beta.gouv.fr, three minutes, and the token goes in `LBA_API_KEY` in their environment — never in config.yml. Offer it **only** for apprenticeship or work-study, and tell them the best part: it also returns companies that take apprentices without posting an ad. Warn that a sandbox key returns unusable apply links for those companies |
| Emploi Territorial | The **departments** they would work in — written any way, `69` or `069`. **No login, no browser, no key.** French local government: communes, départements, régions, CCAS. Offer it to anyone open to the fonction publique territoriale, and say the deadline is real — these ads close on a stated date. Without a department the sweep is the whole country, over 1 300 pages |
| Cegid Talentsoft | The employers they would work for, **as careers host labels** — `businessfrance-recrute`, `groupeadp-recrute`. **`place-ep-recrute` is `choisirleservicepublic.gouv.fr`**, the state's public-service portal: offer it to anyone open to the fonction publique, and warn that its 51 708 posts are not a board to read whole. **No login, no browser, no key.** Ministries, airports, energy, large agencies. No directory exists, so ask for the URL; a wrong label does not 404, it fails to resolve. Worth saying: the listing already carries the address and the date, so a scan is useful without opening a single ad |
| DigitalRecruiters | The employers they would work for, **as careers hostnames** — `recrutement.monoprix.fr`. **No login, no browser, no key.** French retail, franchise networks and large service groups; the biggest boards of any ATS here. No directory exists — the site is on the employer's own domain, so ask for the URL. Warn them the listing has no description or date, and that reading the ads is deliberately paced |
| Softy | The employers they would work for, **as careers URLs** — `<tenant>.softy.pro`. **No login to scan, but it needs their own Chrome** with the extension connected. Say why, because it is not a limitation: the site asks AI crawlers not to read it, so the sweep goes through their session instead. Warn them an ad can span several towns and the listing shows only the first |
| Flatchr | The employers they would work for, **as careers URLs** — `<tenant>.flatchr.io`. **No login, no browser, no key**, and no detail option: one request returns the ads with their full text. Like Taleez there is **no resolver** — its sitemap belongs to the marketing site and lists no vacancies at all — so ask for the URL and never guess a tenant |
| Taleez | The employers they would work for, **as careers URLs** — `<tenant>.taleez.com`. **No login, no browser, no key.** The French SME/ETI ATS, and like umantis there is **no resolver**: no directory, no cross-tenant search, and the sitemaps carry no job URLs. Ask for the URL and never guess a tenant. Warn them the listing has **no description**, so reading the ads costs one request each |
| Greenhouse / Lever / Ashby / SmartRecruiters | A list of **employers** they would actually work for. **No login, no browser.** These answer "is my target employer hiring?", never "who is hiring near me?" — a user with nobody in mind gains nothing, so offer them only when the user names employers. Resolve each tenant token with `ats.py resolve "<employer>"`; never ask the user to guess it. **On SmartRecruiters that resolution is not optional**: a wrong tenant answers `200` with zero postings there, so a guessed token looks exactly like an employer with nothing open |
| France Travail | Their **departments** (`"75"`, `"69"` — strings, leading zero kept) or an **INSEE commune code** plus a radius. **No login, no browser** — but the only board here that needs an API key, free from francetravail.io. Walk them through it with section 5c; do not ask for the key before they have enabled the board. France only |
| job-room.ch | The cantons they would work in (official uppercase codes), or a point and a radius of at least 10 km. **No login, no browser.** Switzerland only. Reaches the SMEs, foundations and staffing agencies HiringCafe misses |
| HiringCafe | Their ISO-2 country code. **No login, no browser, no extension** — it is plain HTTP, and the only sweep that works without Chrome. Worldwide; thin in emerging markets, and blind to the Swiss ATS (Refline, Ostendis, Umantis) |
| LinkedIn | Their own profile URL, and they must be logged in themselves, in the Chrome the Claude extension is connected to |
| jobup.ch | Nothing — **no login needed to scan.** Swiss ads, French-speaking Switzerland |
| randstad.ch | Nothing — **no login, no browser.** The staffing agency's Swiss board, ~985 ads nationwide. The employer is never named. Note for Romandie users: its structured data is absent on Geneva-area ads, which the adapter handles but which makes those ads slightly thinner |
| persigo.ch | Nothing — **no login, no browser.** A staffing agency, mostly central Switzerland, trades and technical roles. Warn them of two things: the employer is never named, and the board keeps ads for over a year with no date on the listing — so a large result count is not a large number of current openings |
| sozialinfo.ch | Nothing — **no login, no browser.** Switzerland's social sector. Worth offering to anyone in social work, care, education or the public sector; pointless otherwise. Unlike the agency boards it names the employer, and every ad carries a postcode the ORP form wants |
| fachkraft.ch / sta.jobs | Nothing — **no login, no browser.** Swiss trades and industry. **Offer `www.fachkraft.ch` and nothing else**: it is the umbrella for sta.jobs and stellenpartner.ch, which add no ads and double every row. Warn them the employer is never named |
| Michael Page | Their country domain — `www.michaelpage.ch`, `.fr`, `.de`, `.co.uk` … **No default**: guessing it searches the wrong market. **No login, no browser.** Warn them the employer is never named on this board, so they cannot research the company before applying, and the ledger cannot dedup it against the employer's own ATS |
| Cadremploi | A **list of `motscles` / `ville` searches**, `ville` written `<slug>-<code postal>` — `paris-75`, `lyon-69`. **No login to scan, but it needs their own Chrome** with the extension connected, because the site blocks scripted access outright. Say that before enabling it: it is the only French board here that cannot run headless |
| Figaro Emploi | A **list of searches**, each one a `departement` (`69`), a `ville` (`lyon-69000`) or a `region` (`fr-ara`), optionally narrowed by a `metier` slug. **No login to scan, but it needs their own Chrome** with the extension connected — Cloudflare blocks scripted access, exactly as on Cadremploi. Mention it when they ask for **Keljob**: that is this board now |
| Jobology | A **list of `site` / `metier` searches**, optionally a `region`. The `site` is one of nine sector boards — ask which sector fits them: santé (`jobvitae.fr`), distribution (`distrijob.fr`), transport (`jobtransport.com`), tourisme-hôtellerie (`clicandtour.fr`), énergie, maritime, sport, environnement, supply chain. **No browser, no account.** Slugs are the site's own vocabulary — `jobology.py metiers --site <site>` lists them, and a wrong one returns an empty board with no error |
| Batiactu | A **list of searches**, each a `region` (21 slugs, the **pre-2016** map — `aquitaine`, not `nouvelle-aquitaine`) or a `metier`, plus `departements` — which they should almost always give, because the site's own region filter matches the employer's name and returns jobs anywhere in France. **No browser, no compte.** Offer it only for BTP, construction and building trades |
| ANEFA | A **list of `departements`**, written as the real numbers — `29`, `2A`, `971` — the adapter translates them. **No browser, no compte.** Offer it for farm, seasonal and rural work. Warn them of one thing: **the ads name no employer**, so a letter goes to a farm the ad describes without naming |
| Welcome to the Jungle | Nothing to configure for discovery — but it **needs their own Chrome** with the extension connected to read the ads, because every page answers an anti-bot challenge that their browser passes and a script does not. Ask which **companies** or which **date window** they want: the board is 88 222 ads and the useful narrowing is `--company` and `--since`. Warn them that `/fr/` is a language, not a country — the country is only known once an ad is read |
| Adecco France | A **narrowing** — `ville` (free, matches the URL slug), `region` (the department spelled out, but it costs a fetch per candidate) or `since`. **No browser, no compte.** Tell them what it is before enabling: 13 293 interim and CDI ads with a salary on two in three, but **the employer is always Adecco** — the client company is described and never named, so no pre-application research and no dedup key |
| Randstad France | A **list of `ville`**, spelled as in the URL — it is reliable here and free. `departement` works too but costs a fetch per candidate. **No browser, no compte.** Same warning as Adecco: **the employer is Randstad France on every ad**, the client is never named. Note for them: this is *not* `randstad.ch`, which the plugin also covers |
| Crit | A **`since` date** above all — its URLs are UUIDs, so the date is the only filter that costs nothing, and it is a real per-ad date. `departements` works but reads every ad to find them (60 read for 1 kept, measured). **No browser, no compte.** Worth telling them: it is the only French board here that gives a **real salary range on every ad**, and the employer is the local Crit branch rather than the client |
| Hays France | A **list of `lieu`**, written as in the URL — `paris`, `loire-atlantique`. It is free and it is the only geography: **this board has no postcode at all**. **No browser, no compte.** Offer it for cadres, finance, audit, IT and engineering rather than for production or logistics — and tell them a salary figure appears on about one ad in four, the rest saying « selon profil » |
| Empléate (SEPE) | A **list of `provincia`**, uppercase as the board writes them — `MADRID`, `BARCELONA`, `A CORUÑA` — and a **`desde` date**, which matters more here than on any other board: **8 106 of its 28 099 live ads were posted over a year ago**, the oldest in 2020, and nothing in the ad says so. **No browser, no compte, no clé.** Spain only. Never type a province from memory: run `empleate.py provincias` and offer what the board actually publishes. Two things worth telling them — the employer is named on only 29% of ads (on the regional-office feed, the largest, you apply through an address written inside the text), and it is the cheapest board here, one request per hundred complete ads |
| Oposiciones (Empléate) | A **`comunidad`** more often than a `provincia` — and say why, because it is counter-intuitive: **`provincia: MADRID` returns 42 announcements and not one is in Madrid** (they are Catalan posts from Madrid-seated bodies), while the 50 real Madrid ones carry no province at all. Optionally a `grupo` (`A1`…`E`, `GP1`…`GP5`) and `dias_restantes`. **No browser, no compte, no clé.** Spain only, and only for the public sector. Three things to tell them before enabling it: the board is **Catalan in practice** (1 334 of 1 558 live records come from the Diputació de Barcelona's register, Madrid has 42), there is **no ad text at all** so `cover-letter` cannot write from it — an oposición is answered with a form and a dossier — and the deadline field says "Abierto" on every record ever published, so the adapter computes the real one and hides expired announcements by default |
| Infoempleo | A **list of `lugar`**, written as in the URL — `madrid`, `barcelona`, `vitoria-gasteiz`, and `multiprovincia` for ads spanning several provinces. It is free and it is the only cheap filter: **the sitemap carries no date**, so `desde` costs a fetch per ad. Run `infoempleo.py lugares` and offer the places the board actually uses — a wrong one is an empty board, not an error. **No browser, no compte, no clé.** Spain only, generalist. Tell them the shape of it before enabling: the employer is named on every ad, which sounds better than it is — **32 of 44 are ETTs** and 60 ads carried only 23 distinct employers, so the name is usually the agency and the workplace is described without being named. No postcode on any ad, and a salary on one in five |
| Turijobs | A **list of `ciudad`** as written in the URL — `barcelona`, `islas-baleares`, `madrid` — plus **`pais: ES`**, and say why: the `/es/` sitemap is the Spanish-**language** board, and 10 of 40 ads measured were in Germany, Portugal, France, Italy, Mexico or Andorra. A `desde` date is free too. **No browser, no compte, no clé.** Offer it for hostelería, hotels, kitchens, front desk, spa and housekeeping — not for anything else. Three things worth telling them: it is **the only board here that shows how many people already applied** (médiane 10, jusqu'à 156), it gives a **real postcode** where the other Spanish boards give none, and the employer is the hotel chain itself rather than an agency — Meliá, Barceló, H10. Warn them the salary is almost never a number: two ads in forty state one, whatever the field suggests |
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

## 5c — France Travail: the one board that needs a key, and how to get it

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
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/francetravail.py" token
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
5. **That this is the only one.** Softy, Tecnoempleo, InfoJobs and Leboncoin are
   refused on files of the same kind, and stay refused. A user who hears "we
   override robots.txt" without hearing "once, here, for this reason" has been
   told something false about the plugin.

### The question, and the three answers it can have

`AskUserQuestion`, single select, no default:

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
