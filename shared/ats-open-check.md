# Is the ad still open? Asking the employer's ATS directly

Used by `cover-letter` **step 1b**, when an ad is in the at-risk band and the
question *"is anyone still reading applications?"* has to be answered before a
dossier is written.

This file is **not** a board adapter and never will be. `shared/boards/*.md`
exists so `job-scan` can **sweep** a board. This exists so step 1b can **ask one
question about one ad**. The two needs look similar and are not: a host can be
useless for sweeping and excellent as an oracle, which is exactly the case for
every entry below.

## Why a direct request beats every other route

The board is the least reliable place to ask. A board will happily serve the
full description of a dead ad — the *"no longer accepting applications"* banner
is rendered client-side and never reaches fetched markdown. **The employer's own
applicant tracking system has no reason to lie**: when the requisition closes,
the ATS stops serving it, usually with a status code.

So when an ad's *apply* link points at a host below, **one request settles what
a careers-page search only suggests.**

## The hosts, and exactly what they answer

Match on **status code first, page title second, body text last** — bodies are
localised and get rewritten; status codes do not.

### Haufe / Abacus umantis — a strong, status-code signal

- **Recognise it by the path**, not the host: `/Vacancies/<numeric id>/Description/<segment>`.
  Employers front it either with `recruitingapp-<n>.umantis.com` or a vanity
  domain of their own (`jobs.<employer>.com`), so **the host tells you nothing
  and the path tells you everything.**
- **The trailing segment is per *vacancy*, and must never be guessed.**
  Corrected 2026-08-28: this file previously said the `2` was required and was
  not a view index. It is one, and it varies **inside a single tenant** — on
  BOBST, vacancy 9151 serves at `/2` while 9220, 9221 and 9222 serve at `/3`;
  Swiss TPH serves at `/1`. Every wrong segment answers `200`.
  **Read the segment from the employer's `/Jobs` listing, which links each
  vacancy with a working one** — `skills/job-scan/scripts/umantis.py` does this,
  and `umantis.py check --host … --id …` answers this whole section in one call.

| Response | Reading |
| :-- | :-- |
| **`200`** + a real job title in `<title>` | **Open.** |
| **`403`** | **Not open** — closed, withdrawn, or never existed. Body is localised (*"Invalid permission"* / *"Fehlende Berechtigung"*); **match the 403, not the words.** Confirmed at every segment, so a 403 needs no segment hunt. |
| `404` | Malformed path — you got the URL shape wrong, not an answer about the ad. |
| `200` + **nothing before the `\|`** in `<title>` (`  \| Applicant Management`, `  \| eRecruiting Swiss TPH`) | The tenant's chrome, not a description. **Wrong segment, not a dead ad** — try the ones the listing publishes. What follows the pipe is per-tenant and localised; what is stable is that nothing precedes it. |

**Verified 2026-08-27 on two unrelated tenants, in two locales.** The decisive
case: a vacancy on `recruitingapp-2698.umantis.com` that a search engine had
indexed — so it was open when crawled — answered **403** when requested. That is
a genuinely closed vacancy returning 403, not merely an unknown id.

**The site root is usually gated by SSO. That does not matter** — the direct
vacancy URL answers unauthenticated, which is the whole value.

**umantis now also has a board adapter** (`shared/boards/umantis.md`): it sweeps
one employer at a time, and reaches the Swiss SMEs, communes and institutes that
HiringCafe does not index at all. This section stays as the open/closed oracle;
that file is for listing a board.

### Jobvite — a weak, title-only signal. Affirmative use only.

- Path: `jobs.jobvite.com/<employer>/job/<opaque token>`
- **Jobvite never returns an error status.** Every request below answered `200`.

| Response | Reading |
| :-- | :-- |
| `200` + `<title>` = `<Employer> Careers - <Job Title>` | **Listed.** |
| `200` + `<title>` = `<Employer> Careers` (bare) | Token is unknown or malformed. **Not proof the ad closed.** |
| `200` + Jobvite's own support page | The employer segment is wrong. |

> **What a genuinely *closed* Jobvite vacancy returns is UNVERIFIED.** Only the
> bogus-token state was tested. It may well keep serving the description.
> **So Jobvite is trustworthy in one direction only:** a real job title means
> listed; anything else means *ask another way*, never *the ad is dead*.

### SAP SuccessFactors — affirmative only, and the search page lies

- **Recognise it by the path**, not the host. Employers front it with a vanity
  domain of their own (`jobs.<employer>.ch`), so the host tells you nothing.
  Vacancy path: `/job/<slug>/<id>-<locale>` — e.g.
  `/job/IT-Business-Analyst-domaine-Opérations-de-Marché/31130-fr_FR`.
- Confirm the vendor from the page source: `rmkcdn` (i.e.
  `rmkcdn.successfactors.com`) or `/platform/bootstrap/`.
- **Like Jobvite, it never signals absence with a status code.** The `<title>`
  is the whole signal.

| Response | Reading |
| :-- | :-- |
| **`200`** + a real job title in `<title>` (`<Job Title> Détails du poste \| <Employer>`) | **Listed.** |
| **`200`** + `<title>` opens on its separator, the title slot empty (`` ` Détails du poste \| <Employer>` ``) | The requisition does not resolve. **Not proof the ad closed** — it is the same response an invented id gives. |

**Verified 2026-08-27 on one tenant, with a negative control**: a real
requisition (`31130`) answered `200` / 55 742 B with its title; the same slug
with an invented id (`99999`) answered `200` / 46 424 B with the slot empty. The
≈ 9 kB delta is a second, weaker tell; **the title is the reliable one.**

#### The search page is client-rendered, and that invalidates step 1b's rule 2

`/search/` returns a navigation shell and **nothing else** — zero `/job/` hrefs,
zero job titles, zero occurrences of the search term, for anyone, always.
Measured unauthenticated with a desktop user-agent:

| Request | Result |
| :-- | :-- |
| `/search/?q=&sortColumn=referencedate&sortDirection=desc` | `200`, 66 141 B |
| `/search/?q=&searchResultView=LIST` | `200`, **66 141 B — byte-identical** |
| `/search/?q=<terms>` | `200`, navigation shell only |
| `/search/rss/?q=` | `200`, 65 993 B — **the HTML shell, not a feed** |

**Step 1b treats "the role is missing from the employer's careers page, while
that page lists their other openings" as a strong signal of closure. On this
host that inference is invalid**, because the page lists nothing at all. A
fetched summary saying *"the page does not display actual job listings"* means
*nothing was rendered*, not *the employer has no openings* — and reading it the
second way concludes "closed" from a page that was never read.

`/search/rss/` is the trap inside the trap: the one URL shape that would normally
bypass client rendering is present, answers `200`, and is worthless.

**Detection, before drawing any conclusion:** a `200` of a few tens of kB
containing `rmkcdn` or `/platform/bootstrap/` and **no `/job/` hrefs** is a
client-rendered shell. Two different query strings returning byte-identical
responses is a second, independent tell.

#### Getting the vacancy URL, which is not guessable

The requisition id cannot be derived from the ad, and that is what previously
made this host unverifiable. **jobup publishes it** — the vacancy JSON on a
jobup detail page carries the employer's own posting:

```
"externalUrl":"https://jobs.<employer>.ch/job/<slug>/<id>-fr_FR"
```

So on a jobup ad the working sequence is: read `externalUrl` from the detail
page → request it → look for a non-empty job title in `<title>`. The same page's
`isActive` corroborates independently. See `shared/boards/jobup.md`.

> **What a genuinely *closed* requisition returns is UNVERIFIED.** Only the
> invented-id state was tested, and a closed requisition may well keep serving
> its description. **Affirmative direction only:** a real job title means listed;
> an empty title slot means *ask another way*, never *the ad is dead*.

#### Corrected 2026-08-28: there is an API, and the title test needs a control

Two things in this section were true but incomplete.

**The board is readable without a browser.** The client-rendered `/search/` page
is backed by `POST /services/recruiting/v1/jobs`, which answers unauthenticated.
`skills/job-scan/scripts/successfactors.py` reads it, and
`successfactors.py check --host … --id …` answers this whole section in one
call. See `shared/boards/successfactors.md`.

**The empty title slot is not empty text.** A live requisition reads
`<Job Title> Détails du poste | BCV`; an invented id reads
`  Détails du poste | BCV` — the tenant's chrome is still there. Testing that
*something* precedes the separator therefore passes an invented id. The chrome
phrase is per-tenant **and** per-locale, so it cannot be matched either.
**Compare against a control instead**: fetch an id that cannot exist on the same
tenant; an identical page means the requisition does not resolve.

#### The browser is not the easy fallback here

Rendering the list in the Chrome extension is not the easy fallback it looks
like. Observed 2026-08-20 on this tenant: **the portal only opens in the tab
where the session was authenticated**, and the extension could not join that
tab — a dossier was rendered and then abandoned. Unreadable headless *and*
awkward in the browser is the same host, twice.

### Refline — the cleanest signal here, and readable without a browser

- **Recognise it by the path**: `apply.refline.ch/<tenant>/<id>/pub/1/index.html`.
  The tenant is a six-digit number, the id a short one.
- The vacancy page is **server-rendered** — plain HTTP, no browser, no cookie.

**Two independent tells, and they agree.** Verified 2026-08-29 on **three
unrelated tenants** — 424626 (Möbel Pfister), 891537 and 637921:

| Response | Reading |
| :-- | :-- |
| `200`, a `JobPosting` block in the markup, **and a job title in `<title>`** | **Open.** |
| `200`, **no `JobPosting`**, `<title>` **empty** | The posting does not resolve. |

| | live | invented id |
| :-- | --: | --: |
| bytes | 12 000 – 20 500 | 1 385 – 1 831 |
| `JobPosting` | **1** | **0** |
| `<title>` | the job title | **empty** |

**Match on the `JobPosting` block and the title, not on the size.** The shell is
a different length on every tenant (1 385, 1 573, 1 790 bytes on the three
above), so size is a corroboration and never the test.

Rendered in a browser, the non-resolving page says *"Ce poste n'est plus
disponible. Il se peut que le lien soit invalide ou que le poste ait été
supprimé."* — client-side, so a fetch never sees those words. **That is why the
test is the missing `JobPosting`, not the message.**

> **What a genuinely *closed* posting returns is UNVERIFIED.** Only invented ids
> were tested. The rendered message conflates "invalid link" and "deleted
> posting" in one sentence, so even in a browser it does not separate them.
> **Affirmative direction only.**

**There is no listing, and this will never be a board adapter.** Eight
tenant-level URL shapes were tried; every one returns the same shell with zero
ad links. `apply.refline.ch/<tenant>/pub/1/index.html` is not a list — it is the
vacancy viewer with no id, which is why it renders "no longer available".

**Where the URLs come from:** job-room carries them. HiringCafe indexes no
Refline ad at all (`shared/boards/hiringcafe.md`), so job-room is the route.

### Prospective — the only host that gives a status code AND an expiry date

- **Recognise it by the host and path**: `ohws.prospective.ch/public/v1/jobs/<uuid>`.
- **The path looks like a REST API and is not one.** It serves HTML, and
  `Accept: application/json` answers `301`. Do not chase a JSON endpoint here.
- Unlike every other entry in this file, it is **multi-employer**: 15 distinct
  employers across the 28 ads sampled — Coop, the Swiss Army, the Canton of
  Bern, Psychiatrie St.Gallen.

| Response | Reading |
| :-- | :-- |
| **`200`** + a `JobPosting` block | **Listed.** |
| **`404`** (`<title>` = `Fehlermeldung`) | **Not listed** — unknown or withdrawn. |

**Every ad carries `validThrough`, and that is the point.** Measured 2026-08-29
on eight ads: `JobPosting` **8/8**, `validThrough` **8/8**, a real employer name
in `hiringOrganization` **8/8**.

```json
{"datePosted": "2026-08-28", "validThrough": "2026-09-25",
 "hiringOrganization": {"name": "BâleHotels"}}
```

**A `validThrough` in the past closes the question with no request to anyone** —
the employer published the deadline. This is the *stated application deadline*
that a 2026-08-27 board report flagged as "a first-class step-1b signal,
currently unused"; it arrives here as structured data rather than as prose to
parse. `cover-letter` step 1b now checks it first.

**There is no listing and there will be no adapter**: `/public/v1/jobs` and the
host root both `301` to an S3 bucket. This is an oracle, not a board.

### Solique — trust the 404, not the markup

- **Two ad shapes, and they are not equivalent**:
  `live.solique.ch/<tenant>/job/details/<numeric id>/` is the full page
  (10–19 kB); `live.solique.ch/Microsites/showPublication/<uuid>` is a light one
  (4.5–7 kB).

| Response | Reading |
| :-- | :-- |
| **`200`** on either shape | **Listed.** |
| **`404`** | **Not listed.** Also what a wrong tenant returns. |

> **Corrected 2026-08-29, while building the adapter: the 404 is not universal
> either.** `iss`, `manor` and `ottosag` answer an unknown id with `404`;
> **`ktzh` answers `200` with its own landing page** — 1 112 bytes against
> 23 196 for a real ad. A status-only check reports a non-existent ad as
> **open**, which is exactly what the adapter did on its first run.
>
> **The control is the tenant's landing page.** Fetch `<tenant>/` once and
> compare its `<title>` to the ad page's; equal means the id does not resolve,
> whatever the status was. `solique.py check --tenant … --id …` does this and
> answers this whole section in one call.

**The `404` is the usual test, and the markup is never one.** A `JobPosting` block
is present on some tenants and absent on others — Vebego, ISS, Kanton Zürich and
Manor carry one; Otto's and united-machining do not, and the `Microsites` pages
**never** do. So the presence of structured data says something about the
employer's configuration, not about the ad. Measured across 24 ads and 6 tenants
on 2026-08-29.

Where a `JobPosting` is present it carries `validThrough`, which is worth using
under the rule above — but never rely on it being there.

**The lead recorded here on 2026-08-29 was built the same day, and the caution
that came with it was wrong.** `/iss/` and `/KTZH/` answering `200` with zero ad
links does not mean those tenants cannot be swept — they are AngularJS shells
whose data is one request away, on two *different* JSON routes. All six known
tenants are reachable. See `shared/boards/solique.md`.

### sozialinfo.ch — a JobPosting block, and an expiry date on every ad

- Path: `www.sozialinfo.ch/arbeitsmarkt/stellenportal/<token>/`. **The token
  alone is enough** — the slug in front of it is decorative.
- Server-rendered, unauthenticated.

| Response | Reading |
| :-- | :-- |
| `200` + a `JobPosting` block | **Listed.** |
| `200`, **no `JobPosting`**, `<title>` **empty** | The token does not resolve. |

**The status code is not a test here**: an unknown token answers `200` with a
~300 kB page. The block is the test, as on Refline.

**Every ad carries `validThrough`** (6/6 sampled), so most questions about this
board are settled by the expiry rule above without any request at all. It also
names the hiring employer with a `sameAs` link to their own site — see
`shared/boards/sozialinfo.md`, which sweeps it.

### persigo.ch — a clean 404, and no expiry date at all

- Path: `www.persigo.ch/stelle-finden/stelle/<token>/`, the token six
  alphanumeric characters. **The token alone rebuilds the URL.**

| Response | Reading |
| :-- | :-- |
| `200` + a `JobPosting` block | **Listed** — but read `datePosted`, see below |
| `404` | **Not listed.** |
| `200`, no `JobPosting` | A page-shape change, **not** a dead ad. |

**There is no `validThrough` anywhere on this board**, so the expiry rule above
cannot help, and *listed* is a weaker statement here than elsewhere: **the board
keeps ads for over a year.** Of 14 sampled, 3 were posted in 2025, the oldest
2025-05-23. Always read `datePosted` alongside the verdict —
`persigo.py check` returns both. Swept by `shared/boards/persigo.md`.

### The ones already named in step 1b

Factorial, Workday, Greenhouse, Lever and SmartRecruiters close a requisition
with unambiguous prose — *"This job opening doesn't exist anymore"*. Step 1b has
always said so; no table needed, because the page tells you in words.

## Rules

- **A stated expiry date in the past is the one exception, and it outranks
  everything here.** `validThrough` is the employer's own statement, not an
  inference from a response — so when it is present and past, the ad is closed
  and no host needs asking. Check it before making any request; only Prospective
  guarantees it, but several Solique tenants and other boards' structured data
  carry it too.
- **Never infer closure from a signal not verified for closure.** An unverified
  host earns *"could not verify"*, which is a reportable outcome under
  `shared/never-fail-silently.md` — not a silent assumption either way.
- **Never guess a vacancy id or a URL shape** to manufacture an answer. Probing
  ids to learn a host's *behaviour* is fine and is how this file was written;
  probing them to decide a specific ad's fate is not.
- **Report the route at the gate**, naming host and response: *"verified live —
  employer's umantis posting answers 200 with the job title"* is a finding a
  user can weigh. *"Looks open"* is not.
- **A host that is not listed here is not a failure.** Say you could not verify
  and why, then carry on. Adding a host means testing its **closed** state, not
  just its open one — that is the whole difference between the two entries above.

## Investigated and rejected — do not investigate a third time

A negative result costs as much to establish as a positive one and is worth
exactly as much, because without it the next person repeats the work. Both of
these were reached the same way as Refline: a sweep of **2 800 job-room ads
across all 25 cantons**, on 2026-08-29, harvesting `externalUrl` hosts.

### Ostendis — opaque without a browser, and almost absent

- **1 ad in 2 800.** Path: `link.ostendis.com/publication/<slug>/<opaque token>`.
- The page answers `200` with **1 850 bytes** and `<title>` = `Publikation` — a
  client-rendered shell, no `JobPosting`, no job title.
- **A bogus token also answers `200`**, with the same shell. There is nothing to
  match on.

Neither an adapter nor an oracle: no signal headless, and no volume to justify a
browser route. Revisit only if a user actually hits one, and then in a browser.

### Rexx — nothing to measure

- **0 ads in 2 800.** No tenant was found by probing the usual domain shapes
  (`career.`, `jobs.`, `www.` under `rexx-systems.com`).

This is **not** "it does not work" — it is "no employer in this sample publishes
through it". `shared/boards/hiringcafe.md` names Rexx among the Swiss ATS it
does not index; that remains true, and job-room does not carry it either. Any
future work needs a real tenant URL first, from a user who has one.

## Investigated, buildable, not built

Recorded so the work is not repeated. All three came out of the same 2 800-ad
job-room sweep, on 2026-08-29.

### randstad.ch — blocked on pagination

`/jobs/` serves **29 ads**, an unknown id answers **`410`**, and the ad page
carries a `JobPosting` with `validThrough`. But **`?page=2` returns the same 29**
and no other pagination mechanism was found. Reading an ad is solved; walking
the board is not.

### wigumar.ch — not a board

**One employer** (Wigumar AG), 25 ads in the sweep. `/` and `/stellen/` answer
`200` with **zero** ad links, and every other path tried answers `404`; no
listing was found. This is a single company's own site — the shape of an ATS
tenant, not a board. An unknown ad id answers `404`, so if a user ever lands on
one, that is a usable open/closed signal; nothing more is worth doing.

## Adding a host

One entry costs a handful of requests, and the closed state is the only part
that is hard:

1. Fetch a **known-open** vacancy. Record status and `<title>`.
2. Find a **known-closed** one — the reliable trick is a search engine's index:
   anything indexed was open when crawled, so a stale result is a closed-vacancy
   candidate. Record status and `<title>`.
3. Fetch a **malformed** id and a **wrong tenant**, to learn what "you asked
   wrong" looks like versus "the ad is gone".
4. Repeat on a **second, unrelated tenant** — one employer's configuration is
   not a vendor's behaviour.
5. Write down what you observed and **only** what you observed. A guessed row
   here produces a confident, wrong "this ad is closed" — which costs the user a
   real opportunity, the most expensive mistake this plugin can make.
