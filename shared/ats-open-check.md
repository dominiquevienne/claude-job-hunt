# Is the ad still open? Asking the employer's ATS directly

<!-- verified: 2026-09-02 -->

*Scope of that date: the **Jobvite** section was re-tested on 2026-09-02 and
its signal is gone (below). The umantis, Greenhouse, Lever and remaining
sections still carry their own earlier dates in place and were **not** re-run
in that pass — the header records when the file was last touched against a
live service, not a claim that every section was.*

Used by `cover-letter` **step 1b**, when an ad is in the at-risk band and the
question *"is anyone still reading applications?"* has to be answered before a
dossier is written.

This file is **not** a board adapter and never will be. `shared/boards/*.md`
exists so `job-scan` can **sweep** a board. This exists so step 1b can **ask one
question about one ad**. The two needs look similar and are not: a host can be
useless for sweeping and excellent as an oracle, which is exactly the case for
every entry below.


**Before any of the per-vendor sections: a rules verdict is not an access
verdict, and the two are independent.** A permissive `robots.txt` does not mean
the pages are reachable, an unreachable page does not mean anybody refused, and
one site in the survey **blocks access while expressing no intention at all** —
its file is a CDN template served on three continents. Measured in one day:
**nine `403`s that a real browser denies against two refusals that hold at both
layers.** `shared/robots-policy.md` carries the method; the short form is
**read the rules, then open a real page, and say which client worked.**

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

### Jobvite — **the signal is gone as of 2026-09-02. Do not use this section.**

Re-tested 2026-09-02 with a plain client. **Every request to
`jobs.jobvite.com` answered `200` with the same page** — `<title>Job Seeker
FAQs and Support | Jobvite` — for a fabricated token, for a fabricated
employer, and for three plausible employer listings alike:

```
jobs.jobvite.com/careers/job/oZZZfakefake   200  "Job Seeker FAQs and Support"
jobs.jobvite.com/nonexistent-employer-xyz/… 200  "Job Seeker FAQs and Support"
jobs.jobvite.com/ingram-micro               200  "Job Seeker FAQs and Support"
jobs.jobvite.com/zscaler                    200  "Job Seeker FAQs and Support"
jobs.jobvite.com/blackline                  200  "Job Seeker FAQs and Support"
```

The old table below distinguished `<Employer> Careers - <Job Title>` from a
bare `<Employer> Careers`. **Neither string appears any more**, so the
affirmative reading cannot be obtained on this host by a plain client, and a
tool matching those titles now reads every ad as unknown.

**Closed in the browser, same day.** The layer rule says a complete `200`
carrying a page nobody asked for is *substituted*, and a substituted response
is one a browser may change — so it was opened in Chrome rather than left as
an open question. **Chrome renders exactly what the plain client gets**: the
same support page. The oracle is dead, and that is now a verdict rather than
an unknown.

**And following the redirect by hand corrects the old claim twice over.**
`curl -L` had been hiding the status:

```
GET jobs.jobvite.com/zscaler                     → 302
GET jobs.jobvite.com/nonexistent-employer/job/abc → 302
   both → http://search.jobvite.com/?invalid=1 → the support page
```

So **"Jobvite never returns an error status" is no longer true** — it returns
a `302`, and the operator names the reason in the query string: `invalid=1`.
That redirect is a *better* negative signal than the bare title this section
used to match on, because it is unambiguous and it is the operator's own word.

**The affirmative half remains untested**: no live Jobvite tenant was found
among those tried, so nothing here establishes what a *listed* ad looks like
today. Use the redirect to conclude "not listed"; do not use its absence to
conclude anything.

The table is kept below as the record of what it used to answer.

### Jobvite — the former signal, retired 2026-09-02

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
- **Like Jobvite, it never signals absence with a status code.** **The tell is
  a `JobPosting` block, present or absent** — the same shape as Refline below,
  and it replaces the `<title>` test that used to carry this section.

**Measured on two tenants, two dates, independently** — BCV 2026-08-27, SICPA
2026-09-02:

| Case | HTTP | bytes | `itemtype="…JobPosting"` | lands on |
| :-- | --: | --: | --: | :-- |
| a real vacancy | 200 | 79 854 | **1** | the vacancy |
| an id that never existed | 200 | 42 956 | **0** | `/errorpage/?errortype=Exception` |
| a **wrong slug** with a real id | 200 | 79 854 | **1** | the vacancy |

**Why the block and not the title.** The two tenants do not return the same
shell: BCV answers with its chrome and an empty title slot, SICPA with
`Jobs at SICPA`. **A test on the shape of a title is therefore per tenant; the
block is binary and is not.** The size gap (~80 kB against ~43 kB) is a third,
weaker tell.

**And the URL shape is per tenant too, which cost a false negative.** BCV
serves `/job/<slug>/<id>-<locale>`; SICPA serves `/job/<slug>/<id>/` and sends
the locale form to the error page. With only the first shape, `check` on a
**live** SICPA vacancy answered *unverified* — the wrong shape landed on the
error page, the error page matched the control, and the control test concluded
the requisition did not resolve. **A live advert reported as unresolvable,
plausibly and in silence.** The adapter now tries both shapes and stops at the
one that carries a block.

**The slug is decorative**, confirmed on a second host:
`/job/Zzz-Not-A-Job/<real id>/` serves the whole vacancy. **So the id alone
rebuilds a check URL** — there is no need to keep the slug.

**Two tenants, two dates — not a property of the SuccessFactors family.** These
are two independent deployments of the same vendor, so the repetition
corroborates; it does not generalise.

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

**The block measurement improves the tell and does not widen that conclusion.**
Block present → the advert is being served. Block absent → **the id does not
resolve**, which is still not proof that it closed. What was tested is ids that
never existed, on both tenants; a requisition that really closed has never been
observed here.

**The missing measurement, named rather than assumed:** one tenant where a
recently closed vacancy is known would settle it in a single request. Until
somebody has it, this section stays affirmative-only.

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

### randstad.ch — the 410, and never the markup

- Path: `www.randstad.ch/jobs/<uuid>/`. **The UUID alone rebuilds the URL.**

| Response | Reading |
| :-- | :-- |
| `200` | **Listed** |
| `410` | **Not listed** — this board says gone with a 410, not a 404 |

**Do not use the `JobPosting` block as a test here.** It is present on some ads
and absent on others, and the split follows the *region*: 8 of 8 German-region
ads sampled carried one, 4 of 4 Geneva-area ads did not. Its absence says
nothing about the ad. Swept by `shared/boards/randstad.md`.

### Applifly — it confirms both ways, and only if you keep the query string

- **Recognise it by the path**, not the host: `/job/view-job.php?id=<n>` on an
  employer's own `jobs.<employer>.ch`. **The host never says Applifly.**

| Response | Reading |
| :-- | :-- |
| `200` with an `itemtype=".../JobPosting"` block | **Listed** |
| `3xx` | **Not listed** — an unknown id redirects |
| `200`, ~718 bytes, `document.referrer` in a `<script>` | **Nothing.** Your URL was under-specified — see below |

**The URL must carry `language` and `source`.** Without them the same id
answers `200` with a script that reloads the page with
`?source=<referrer>` — so **a browser always sees the ad and a script never
does**, and the status line says `200` either way. `source`'s value is
irrelevant; its presence is not.

**This is not client-side rendering and it does not need a browser.** The first
reading of this host called it a shell and treated the ad as unverifiable by
its ATS. It is verifiable, at the cost of one query parameter — *decide by
layer*, and the layer is above the browser.

**And do not strip the query string to normalise the URL.** The id is in it,
and so is the parameter that renders the page. Swept by
`shared/boards/applifly.md`.

### The ones already named in step 1b

Factorial, Workday, Greenhouse, Lever and SmartRecruiters close a requisition
with unambiguous prose — *"This job opening doesn't exist anymore"*. Step 1b has
always said so; no table needed, because the page tells you in words.

## The host that cannot confirm, and it is not the same as a host that says no

**This file classifies hosts by what they answer. It had no category for a host
that cannot answer** — and a shell was therefore read the way an unresolved id
is read: as a weak negative. **It is not a weak negative. It is an absence of
signal**, and the two lead to opposite decisions.

| What the ATS returns | About the ad | What 1b does |
| :-- | :-- | :-- |
| A `JobPosting` block, or an unambiguous status | **served** | **corroborated** — two witnesses agree |
| An error shell, no block — *the id does not resolve* | **not proof of closure** (see SuccessFactors above) | second witness, **mute in the negative direction** |
| **A shell for every id, valid or not** | **nothing** | **one witness only — and say so** |
| **A shell because the request was under-specified** | **nothing yet** | **fix the request; this one is ours** |

### The instance is Ostendis, and it was already in this file under the wrong heading

`link.ostendis.com` answers `200` with 1 850 bytes and `<title>` = *Publikation*
— **and a bogus token answers `200` with the same shell.** There is nothing to
match on, in either direction. It sits below under *investigated and rejected*,
which conflates two different judgements: **not worth an adapter** and **cannot
serve as a witness**. The second is what 1b needs and it is what this table now
says.

### Applifly is **not** in this category, and the difference is instructive

It looks identical from one request — `200`, a small body, no block — and it is
the opposite case: **the request was missing a parameter.** With `language` and
`source` the same URL returns the ad, and an unknown id returns `3xx`. **It
confirms in both directions.** The first reading called it client-rendered and
recorded the ad as verified by one witness; it had two.

**So the fourth row is a category about us, not about the host** — a `200` with
no content that our own request produced. It is the third shape of that failure
found in two days, after `curl --compressed` manufacturing a transport error
and `-L` turning a redirect loop into a dead site (`shared/plausible-and-false.md`,
*The flag is part of the measurement*). **Before filing a host as mute, change
one thing in the request and ask again.**

### "One witness" is a state to declare, not a defect to fix

**There is nothing wrong with a single-source verification.** Sometimes the
board is all there is, and the ad is genuinely open. **What is wrong is writing
it the same way as a corroborated one.**

This repository spent two days establishing that a single source repeated looks
like agreement — five country queries served from one pool (#86), a check that
shares its object's blind spot (*blind agreement*). **This is the symmetric
duty: knowing, and saying, when you only have one.**

So step 1b names its witnesses:

> *"verified live — jobup answers 200 with no redirect. **One witness**: the
> employer's ATS could not be asked (Ostendis returns the same shell for any
> id)."*

**Never *"verified"* on its own** when only one source spoke. And note what the
single witness costs here: **jobup is the source #88 established lies by
redirection** when an ad expires. A single witness with a known failure mode is
the weakest verification in this file, and it must read as such.

### What this file does *not* hold

**What an ATS can confirm about an ad is not what a user has decided about an
employer.** A freeze, a "never again", a pay range refused — those are the
user's own facts, they age, and they belong beside `commute.md` in the
workspace, not in a repository file that ships to everybody. This file is
indexed by host and is true for every user of the plugin; that boundary is the
whole reason it can ship.

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
- **Count your witnesses and name them.** *"Verified"* without a number is the
  claim this file cannot support; *"one witness, and it is the board"* is.
- **A `200` with no content is our request until proven otherwise.** Change one
  parameter and ask again before recording a host as mute.
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

### stellenpartner.ch — already covered, do not enable it

Not a separate board: **501 of its 501 distinct slugs also appear on
fachkraft.ch**, and its `-SPxxx` references resolve there too. `fachkraft.md`
sweeps it already. Enabling it alongside would record every ad twice, because
the numeric ids are per-domain. Recorded here so the resemblance to a new board
does not cost anyone a second investigation.

### krippenstellen.ch — a real board, and far too small

10 employers across 11 ads — genuinely multi-employer, childcare sector, and
the employers are named. But `/de/` **is** the whole listing and it carries
**11 ads**. No `JobPosting` block, and the ad page renders only chrome to a
plain fetch; the content arrives by AJAX.

Eleven ads against sozialinfo's 708. The volume does not justify the work.
Revisit only if the board grows.

### okjob.ch — its job-room URLs are not ads

**6 of 6** external URLs sampled led to a *category* page, `<title>` = *"Toutes
les offres d'emploi à &lt;slug&gt;"*, not to a posting — see `job-room.md` trap
6b, where the general lesson is recorded. One employer (OK Job, an agency), no
`JobPosting` anywhere. Nothing here to read as a single ad.

### evergreen-hr.ch — one employer, no listing

An agency, 12 ads in the sweep, no `JobPosting` block, and `/stellen/` answers
`404` — no listing was found at any path tried. Nothing to sweep.

## Investigated, buildable, not built

Recorded so the work is not repeated. All three came out of the same 2 800-ad
job-room sweep, on 2026-08-29.

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
