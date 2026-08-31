# Board adapters

`job-scan` is board-agnostic: it owns the scoring, the ledger and the reporting,
and each adapter owns one site. Thirty-nine ship today, each verified against
the live site — count the rows below rather than trusting this sentence, which
has gone stale before.

## Which boards are available

| Board | File | Status |
| :-- | :-- | :-- |
| HiringCafe | `hiringcafe.md` | **Shipped.** Worldwide meta-board over ~40 ATS. Search sweep and description reading, **with no browser and no login** — plain HTTP. No apply flow to support: every ad links to the employer's own ATS |
| job-room.ch | `job-room.md` | **Shipped.** Switzerland's public employment service portal (SECO). Public REST API — **no browser, no login**. Reaches the Swiss SMEs and foundations HiringCafe misses; heavily overlaps jobup, and says exactly which row each duplicate is |
| Greenhouse | `greenhouse.md` | **Shipped.** One employer at a time, by tenant token. Public JSON, **no browser**. Targeting, not discovery |
| Lever | `lever.md` | **Shipped.** Same family. Two disjoint hosts (US / EU) — the wrong one looks exactly like a missing employer |
| Ashby | `ashby.md` | **Shipped.** Same family. Multi-city postings hide their other locations in `secondaryLocations` |
| Solique | `solique.md` | **Shipped.** One employer at a time, by tenant. **No browser.** Three different architectures behind one host — two JSON routes and a truncatable HTML one; the adapter says which answered and how complete it was |
| SAP SuccessFactors | `successfactors.md` | **Shipped.** One employer at a time, by host. Public JSON, **no browser** — the client-rendered `/search/` page is backed by an endpoint that answers unauthenticated. A locale the tenant does not publish empties the board **with no error** |
| SmartRecruiters | `smartrecruiters.md` | **Shipped.** Same family, and the one `ats.py resolve` used to name and then stop at. The only one where a wrong tenant is **indistinguishable** from an employer with nothing open |
| Workable | `workable.md` | **Shipped.** Same family, by tenant. **No browser.** One request returns the employer's whole board *with descriptions*. Publishes the residency rule behind a remote ad — `remote` alone is a trap — and distinguishes `published_on` from `created_at`, which aggregators confuse |
| Teamtailor | `teamtailor.md` | **Shipped.** Same family, by tenant. **No browser.** Whole board in one JSON Feed request, descriptions included. Publishes the employer's **full postal address** — the field a PRE misses most — but no salary, contract type or expiry. Read `<tenant>.teamtailor.com`: the employer's own `careers.` host is a **stale mirror** |
| SwissDevJobs | `swissdevjobs.md` | **Shipped.** A real multi-employer board, **no browser**. Whole board in one request. **A salary on 169 of 170 ads** — the only board here where the money is known before applying — and coordinates on 170 of 170, so `--near` filters by real distance. Carries **no description**, and is overwhelmingly German-speaking Switzerland: 2 of 170 ads in Suisse romande |
| Free-Work | `freework.md` | **Shipped.** French IT, permanent **and** contract, **no browser**. Public JSON API; `robots.txt` allows it explicitly. The only board here carrying a **contractor day rate**, and one of the very few with a real **`expiredAt`**. Three traps documented: `searchKeywords` is the only keyword parameter that filters, the page number never runs out, and the numeric id 404s — the slug is the key |
| FHF Emploi | `fhf.md` | **Shipped.** France's public hospitals and medico-social sector — CHUs, EHPADs, USLDs — **no browser, no account, no key**. The employer is always the hospital itself. **A full postal address on 36 of 36 sampled ads**, the field a PRE misses most, and a named contact on half. Its first page was served **four days stale from the edge cache**, announcing 345 ads more than the board held, so every request carries a cache-buster. The site's own `department[]` and `contract[]` field names return an empty board as GET parameters; the scalars work. Also a **listing for Beetween and a tenant directory for Softy**: 17 of 36 ads link out to an ATS, with the employer named here and anonymous there |
| JOIN | `join.md` | **Shipped.** One employer at a time, by tenant. **No browser, no account, no key** — but no JSON feed either: it is a Next.js app and the whole payload rides in the page's own `__NEXT_DATA__`. **The largest ATS family in Switzerland** — 108 of 223 HiringCafe cards, ahead of Workday. The only provider here that hands the description over **already split into `intro` / `tasks` / `requirements` / `benefits`**, and the only one whose money is in **minor units**: `2035` means `20.35`, an error that reads like a monthly salary. `showSalary` is true on 15 of 22 ads and an amount is present on 1. An ad carries **two numbers and both address it**; the stable one is the ledger key. **No search exists** — `/jobs` is a login and the declared job sitemap answers 403 |
| Workday | `workday.md` | **Shipped.** One employer at a time, by host + tenant + site. Public JSON, **no browser**. Where the large Swiss employers are |
| Haufe / Abacus umantis | `umantis.md` | **Shipped.** One employer at a time, by host. Public HTML, **no browser**. The Swiss SMEs, communes, clinics and institutes **HiringCafe does not index at all**. No tenant resolution exists — the user supplies the careers URL |
| LinkedIn | `linkedin.md` | **Shipped.** Search sweep, description reading, assisted Easy Apply |
| jobup.ch | `jobup.md` | **Shipped.** Search sweep and description reading. No login needed to scan; the in-site apply flow is *not* supported |
| randstad.ch | `randstad.md` | **Shipped.** A staffing **agency** board, **no browser**, 985 ads over 33 pages. Pagination is a **path segment** (`/jobs/page-2/`), and past the last page it silently repeats page 1 — the stop condition is that repeat |
| persigo.ch | `persigo.md` | **Shipped.** A staffing **agency** board, **no browser**, whole board (890 ads) in one request. **No `validThrough` and no date on the listing**, and it keeps ads for over a year — freshness needs `--with-detail` |
| sozialinfo.ch | `sozialinfo.md` | **Shipped.** Switzerland's social-sector portal — a genuine multi-employer board, **no browser**, whole board in one request. **The only board here that names the employer**, so the ledger's employer dedup works on it |
| fachkraft.ch | `fachkraft.md` | **Shipped.** A staffing **agency** board — the whole listing in one request (~3 500 ads), **no browser**. The umbrella for sta.jobs and stellenpartner.ch, whose numeric ids are disjoint from its own; the `<n>-STAxx` / `-SPxxx` reference is the only key that crosses |
| Michael Page | `michaelpage.md` | **Shipped.** A recruitment **agency** board — one search across many employers, country-scoped, **no browser**. The employer is described and **never named**, so no dedup key crosses to their own ATS |
| jobs.ch | `jobs-ch.md` | **Shipped.** jobup's German-language sibling on the same platform — **and the same ad ids**, so an ad on both boards is one row, matched by UUID. Three times the national volume, thinner in Romandie: it does not replace jobup |
| Indeed | `indeed.md` | **Shipped.** Search sweep and description reading, country-scoped. **Serves anti-bot challenges** — the user solves them, never the plugin |
| France Travail | `france-travail.md` | **Shipped.** France's public employment service (ex-Pôle emploi) — **no browser**, but the only adapter here that needs an API key, free from francetravail.io. A search that does not name `origineOffre` returns France Travail's own ads and **silently omits the partner ads that are 77% of the board**, finishing early enough to look complete — so the sweep runs both passes |
| Meteojob | `meteojob.md` | **Shipped.** French generalist board, **no browser, no account**. Its robots.txt opens exactly one door — `Allow: /jobs?*` against a blanket `Disallow: /*?` — and pages 2+ live behind the disallowed API, so **one search is 20 ads and there is no second page**: a targeted probe, not a sweep. Names the employer on every ad, unlike its France Travail feed |
| HelloWork | `hellowork.md` | **Shipped.** France's largest private generalist board — the SMEs and the regions. **No browser, no account.** The most restrictive robots.txt here: `Disallow: /*?` with **no** search carve-out, and the sitemap it advertises answers 403. What is open is its path-based facet system, so coverage is a **facet list** — `facets` enumerates the ones each sector publishes. Richest `JobPosting` of any board: skills as a list, experience in months, a real remote flag |
| APEC | `apec.md` | **Shipped.** France's executive employment agency — 77 023 ads, **no browser, no key, no cookie**. The only French board here with **no pagination ceiling**: `startIndex` walked to 76 900 and still returned disjoint ads. But `texteOffre` is a fixed 283-character teaser and the detail endpoint sits behind a DataDome captcha, so it is **triage, not ad text** — with a salary on every single ad, which no other board manages |
| Cadremploi | `cadremploi.md` | **Shipped — browser only.** The other French cadre board. Cloudflare answers **403 to every scripted request, `robots.txt` included**, so there is no script and cannot be one; it runs in the user's own Chrome like `linkedin.md`. Its location parameter has a decoy that is accepted and ignored, and its card list drifts out of the search area with nothing marking where |
| Figaro Emploi | `figaro-emploi.md` | **Shipped — browser only.** Large French generalist, **244 815 ads**; `keljob.com` redirects here and answers `410` on its retired paths. Cloudflare answers **403 to every scripted request, `robots.txt` included** — same edge as `cadremploi.md`, same group. Sweeps the **allowed browse hierarchy** (`/d/fr-69/m/<metier>`, 28 855 of them) and never `/recherche/offres-emploi` or `/services/search/jobs`, both of which robots.txt closes. Counts are exact — no cap. Its JSON-LD is **emptier than its HTML**: hollow `baseSalary`, and CDI and CDD both arrive as `FULL_TIME` |
| Jobology | `jobology.md` | **Shipped.** One contract, **nine French sector boards** — Distrijob, Jobvitae, Jobtransport, Clicandtour, Clicandpower, Clicandsea, Clicandsport, Clicandearth, Supply-Chain — **72 667 ads**, **no browser**. Browses by path because the `robots.txt` closes the facet parameters. Its pagination **never ends**: page 9999 answers with twenty on-topic ads, and the same URL answers differently twice, so the sweep needs two bounds at once. A wrong slug is an empty board with no error |
| Taleez | `taleez.md` | **Shipped.** A French ATS for SMEs and ETI — the counterpart of `umantis` on the French side, and the family `README` called the biggest blind spot left. **No browser, no key**: one unauthenticated request returns a tenant's whole careers site, 412 ads for one of them. **No tenant directory exists**, so the user supplies the careers URL. The listing carries no description at all |
| Flatchr | `flatchr.md` | **Shipped.** The other French SME/ETI ATS, next to Taleez. **No browser, no key**, and **one request per employer is the whole sweep**: the careers site is Next.js and the job list is server-rendered with the descriptions in it — 55 fields per ad, the richest listing here. No tenant directory; its sitemap is the marketing site's and carries zero vacancies |
| Softy | `softy.md` | **Shipped — browser only, by choice.** The third French SME/ETI ATS, after Taleez and Flatchr. Its robots.txt allows `*` everything and then **disallows the AI agents by name, Anthropic's twice** — so the sweep runs in the user's own Chrome rather than as a script. An ad can span seven towns and the page shows one: the rest live in a tooltip that only a **real hover** opens |
| DigitalRecruiters | `digitalrecruiters.md` | **Shipped.** The Cegid-owned ATS of French retail and franchise networks — **948 ads on the tenant sampled**, the most per employer here. **No browser, no key.** Careers sites are white-labelled on the employer's own domain, so the tenant key is the hostname and no directory exists. `job_ad_id` is **not unique** — one posting across five towns shares it — so the ledger keys on the composite id |
| Cegid Talentsoft | `talentsoft.md` | **Shipped**, verified on two tenants. The last of the five French ATS — and **`choisirleservicepublic.gouv.fr` is one of them** (`place-ep-recrute`, 51 708 posts), so the state portal needs no board of its own. The listing's fields mean different things per tenant, so the parser labels only what it can identify and hands the rest back unnamed — ministries, airports, energy, large agencies. **No browser, no key.** Server-rendered ASP.NET with no JSON and no JSON-LD, but the ad pages carry Talentsoft's **field model as element ids**, which outlive any restyling. A **full street address on the listing**, and a location rule that must not assume a French postcode |
| Emploi Territorial | `emploi-territorial.md` | **Shipped.** France's **territorial** civil service — communes, departments, regions, CCAS. 26 613 posts, carried by no private board. **No browser, no key.** Search is a *session*, not a URL: the filter is POSTed once and the server remembers it. Publishes a **real closing date**, unlike the boards that print `datePosted` plus a constant |
| La Bonne Alternance | `labonnealternance.md` | **Shipped.** French state API for **apprenticeship**. **No browser**, one free self-service key. Returns posted ads *and* **companies that take apprentices without advertising** — 150 of them in the Rhône, which no other board here carries. A **sandbox key hands out staging apply URLs**, and the department code takes exactly two characters: `069`, `1` and `075` each fail differently and silently |
| *your board here* | — | See *Writing an adapter* below |

## When a shipped adapter stops working

Boards redesign, and an adapter that was verified against the live site stops
matching it. **That is a bug in the plugin, not in the user's setup, and it is
reported upstream** — invoke `board-request` in its broken-adapter mode
(section 2b). `job-scan` does this on its own when a sweep fails.

The reason it goes upstream rather than getting patched locally: the installed
plugin lives in a cache directory that the next update overwrites, and the site
changed for every user, not just this one. **One issue fixes it for everybody;
a local edit fixes it for nobody, twice.**

## Without any adapter, the plugin still works

`cover-letter <ad URL>` needs no adapter and no browser: give it a URL from any
board on earth — or paste the ad text when the page is gated — and it scores the
fit, gates on go/no-go, and writes the resume and letter. It is the full
workflow minus the automatic sweep.

So the answer to *"can it do <board X>?"* is never a flat no. It is: *"not
automatically yet — give me an ad URL from it and I'll do everything else."*

## Nothing is enabled by default

**An unconfigured workspace scans no board at all.** Scanning drives the user's
own browser, in their own logged-in session, under their own account — so it
only ever touches a site they explicitly switched on.

Each board is enabled *and configured* in `config.yml`:

```yaml
boards:
  linkedin:
    enabled: true
    profile_url: "https://www.linkedin.com/in/adalovelace"
```

Four states, four different behaviours — never improvise a fifth:

| State | What `job-scan` does |
| :-- | :-- |
| No board enabled | Scans nothing. Says so, lists the adapters available, and offers `/job-setup boards` |
| Enabled but a required setting is empty | Skips that board, names the missing key, and offers to fill it. **Never half-runs** |
| Enabled and complete | Sweeps it |
| **Dormant** — `enabled: false` **plus** the four `dormant_*` keys | Does not sweep it, and says nothing about it — **until its `recheck_after` date passes**, when it offers one cheap yield re-check. See below |

`enabled: false` **with no `dormant_since` is a hard off**: never swept, never
probed, never mentioned. That state predates dormancy and keeps its meaning
exactly — a user who said no to a board is not asked again.

## The fourth state: dormant, or "wrong month, not wrong board"

**A board can come back empty for two completely different reasons**, and until
this state existed the config could only record one of them.

- *This board does not serve this candidate.* sozialinfo.ch carries social-work
  ads; a backend engineer will still be finding none of them in five years.
- *This board serves this candidate and had nothing open that week.* On
  2026-08-30, `jobs.bobst.com` — BOBST, **25 minutes** from that user's home,
  on an adapter that worked perfectly — had ten vacancies, and all ten were
  apprenticeships and internships.

Both produce the same zero, and switching both off the same way throws the
second one away permanently. **Dormancy is the state for a board whose zero is
about timing, and it is the user's own measured evidence that puts it there.**

```yaml
boards:
  umantis:
    enabled: false
    dormant_since: "2026-08-30"
    dormant_reason: "the 10 vacancies on jobs.bobst.com are all apprenticeships"
    recheck_after: "2026-11-28"
    recheck_count: 0
    employers: ["jobs.bobst.com"]
```

| Key | Meaning |
| :-- | :-- |
| `dormant_since` | When the run that measured the zero happened. **Its presence is what makes the board dormant rather than off** |
| `dormant_reason` | The measurement, in one line — counts, not adjectives. This is what the user reads months later when deciding, and *"nothing relevant"* tells them nothing |
| `recheck_after` | The date `job-scan` may offer a re-check. Required: a dormant board with no date never comes back, which is a hard off wearing dormancy's clothes |
| `recheck_count` | How many re-checks have already found nothing. Drives the back-off |

**Its own configuration is kept, not deleted.** The tenant list, the domain, the
cantons — waking a board must be one line changed, not a setup interview
repeated.

`skills/job-scan/scripts/dormant.py` reads these back:

```bash
dormant.py list --config "$JOB_HUNT_HOME/config.yml"   # all dormant boards
dormant.py due  --config "$JOB_HUNT_HOME/config.yml"   # only those now due
dormant.py next --count 0                              # the next date to write
```

**Do the date arithmetic with `dormant.py`, not by hand.** *"Is 2026-11-28 in
the past?"* is exactly the question a language model answers confidently and
wrongly, and both wrong answers are bad: one nags the user about a board they
just parked, the other buries it forever.

### The back-off, and why there is one

A re-check that finds nothing pushes the next one out: **90 days → 180 → 365,
then 365 forever.** A board that is genuinely wrong for this candidate therefore
costs one decision this quarter, one next spring, and then roughly one a year —
while a board that comes good is still caught within a season.

Without the back-off this feature becomes a recurring chore, and a recurring
chore gets switched off wholesale — taking the BOBST case down with it.

### What a re-check is, and what it is not

**A yield check, not a scan.** One listing call at the adapter's cheapest
setting, capped. **No descriptions are opened, no scoring is done beyond
title-and-location screening, and nothing whatsoever is written to the ledger.**
A re-check that quietly turned into a sweep would make dormancy expensive, which
is the one thing it must not be.

**Never re-check a browser board silently.** LinkedIn, jobup, jobs.ch and Indeed
drive the user's own Chrome under their own account; for those, dormancy expiry
means *offering* the re-check and waiting for a yes — never running one because
a date passed.

**A re-check that fails is not a re-check that found nothing**, and the two must
never be reported the same way. A dormant board whose probe errors, 404s or hits
a login wall goes to `board-request` in its broken-adapter mode like any other
failure — its dormancy says the board was *empty*, and that claim is now
unverified rather than confirmed.

A board named in `config.yml` with no adapter file is an error, not a fallback:
the skill says so and skips it rather than improvising selectors against a site
nobody has tested. **Guessing at a board's DOM produces a scan that silently
returns nothing, or worse, returns the wrong ads** — and the user has no way to
tell.

## What the skill expects from an adapter

The skill is board-agnostic. It asks each adapter for five things and does the
scoring, the ledger and the reporting itself.

| Contract | What the adapter must document |
| :-- | :-- |
| **0. Its config keys** | Everything it needs under `boards.<name>` in `config.yml`, which of those are **required**, and what to ask the user to obtain each one. An adapter that reads an undocumented key is a bug |
| **1. Prerequisites** | Whether it needs the browser, whether the user must be logged in, and what to say to them before starting |
| **2. Search** | How to build a search URL from `keywords`, `location`, `posted_within` and `remote_only`; how to extract the result cards; what a card yields (**a stable id**, title, company, location, work mode, posting age) |
| **3. Description** | How to open one ad and extract its full text |
| **4. Ad URL** | How to rebuild a canonical ad URL **from the id** — never by scraping a URL out of the page |
| **5. Its zero-shaped answers** | Every way this board says *no* while answering `200`, and every way it says *yes* while answering an error. **This is not optional and not a nicety**: it is the failure mode every adapter built so far has turned up, and an adapter that documents only the happy path hands the next reader a zero with no way to read it. See *HTTP 200 is not a yes* in `shared/never-fail-silently.md` |

Optionally, a sixth: **assisted application**, if the board has an in-site apply
flow. It must follow the same gate as LinkedIn's — the user validates every
send, and nothing is reported as sent without a visible confirmation.

The **id is the load-bearing part**. It is the ledger's dedup key, so it must be
stable across visits and rebuildable into a URL. A board with no stable per-ad
id needs a documented composite key (company + title + posting date) and a note
saying it will occasionally miss a duplicate.

## Writing an adapter

Copy the shape of `linkedin.md`. It is not a spec document — it is a field
report, and that is what makes it useful. Write down:

- the **constraints you hit**, and what happens when you ignore them
  (virtualized lists, hidden-tab throttling, synthetic clicks that do nothing,
  endpoints that return an error code instead of data);
- the **selectors and snippets that actually worked**, verbatim;
- the **traps**: geocoding that lies, aggregator reposts, stale form fields,
  anything that produced a wrong result once;
- what the board does about **rate limiting**, and the pace that stays under it.

Two rules for anything added here:

1. **Only document what you have run against the live site.** An adapter that
   describes a plausible DOM is worse than no adapter.
2. **Date what you verified**, and say when a selector was last confirmed.
   Boards change their markup; a dated note lets the next person tell a broken
   adapter from a broken assumption.

3. **When you re-verify a file in part, date the part you did not touch.** A
   header saying *"re-verified 2026-08-28"* over sections nobody re-ran makes
   the file read as fresh when half of it is not — and `bin/adapter-age.sh`
   reports each file by its **oldest** standing date, so an undated old section
   is invisible to it. `linkedin.md` carries the worked example: its Easy Apply
   sections say in their own heading that they date from 2026-08-26 and were
   deliberately left out, because exercising them means driving a real
   application on the user's real account.

## Which adapters are due for re-verification

```
bin/adapter-age.sh [days]      # default 30
```

Reads the dates back out of every file here plus `shared/ats-open-check.md`,
sorts by the oldest claim still standing, and flags anything past the threshold
— or carrying no date at all, which is worse than stale because nothing says
when it was true. A file whose heading says it was **never verified against the
live site** is pulled out of the age ranking entirely and listed under its own
`[ !! ]` — a draft is not a stale adapter, and its drafting date is not a
verification date. It changes nothing and always exits 0: **a stale adapter is
not a broken one, it is one nobody has re-run.**

Re-verifying means *running* the adapter against the live site, not re-reading
it. That distinction is the whole point: every defect found on 2026-08-28 —
umantis's per-vacancy segment, the unanchored `externalUrl`, LinkedIn's
`^with verification` anchor — was a rule generalised one step past what had been
observed, and **none of them were visible on re-reading.**

## ATS hosts — not boards, but useful for a different question

`shared/ats-open-check.md` records hosts that answer *"is this ad still open?"*
in one unauthenticated request — Haufe/Abacus umantis, Jobvite, SAP
SuccessFactors, Refline, Prospective, Solique, and the ATSs already named in
`cover-letter` step 1b. It also records which hosts publish a **stated expiry
date**, which answers the question without any request at all.

**Those are deliberately not adapters, and adding one here would be a mistake.**
An adapter exists so `job-scan` can **sweep many employers**; an ATS host serves
**one employer per tenant** and has no cross-employer search, so there is nothing
to sweep. What it does have is an authoritative answer about a single ad, which
is what step 1b needs and what a board is worst at providing.

Keep the two apart: **sweepable board → an adapter here. Employer ATS → a row in
`shared/ats-open-check.md`.** That file also records the hosts investigated and
**rejected**, with why — a negative costs as much to establish as a positive and
saves the next person from repeating it. When a `board-request` turns out to be an ATS, that
file is where its findings belong.

## Reading a robots.txt, and the one case that overrides it

The sections below decide individual boards. **The rule they are decided by
lives in `shared/robots-policy.md`** — four questions, answered in the board's
own file before any code, and a default of *obey* that four of the five cases
land on. Read it before concluding anything about a board that names AI agents;
the answer stopped being binary at `leboncoin`, and the file records why.

The one board decided the other way is the Austrian **AMS**, whose `robots.txt`
grants `LinkedInBot` the employer pages and refuses every other agent. That
override is **opt-in and off by default** (`override_robots: true`), it must
announce itself in the run's output, and its full reasoning — including the
open-data check that came back empty rather than negative — is in the policy
file, not here.

## Investigated and closed — leboncoin.fr

**Verified 2026-08-31, from `robots.txt` alone** — once the rule was read,
nothing else on the site was fetched.

Leboncoin is the largest French audience with no adapter, and it will not get
one. Its `robots.txt` **declares no `User-agent: *` group at all**, and opens
with a prose statement rather than a rule:

> *"It's forbidden to use search robots or other automatic methods to access
> Leboncoin.fr. Access is only permitted with special permission from
> Leboncoin.fr."*

Everything after that is the list of exceptions they have granted — and it is
the most considered file this repository has read, because it **splits AI
agents into three classes**:

| Group | Agents | Treatment |
| :-- | :-- | :-- |
| AI **search / retrieval** | `Claude-User`, `Claude-SearchBot`, `ChatGPT-User`, `Perplexity-User`, `Applebot`… | Allowed, **except `/recherche`** |
| AI **training** | `ClaudeBot`, `anthropic-ai`, `GPTBot`, `CCBot`, `Google-Extended` | Allowed, **except `/recherche` and `/ad/`** |
| `Bytespider` | — | `Disallow: /` |

**`Claude-User` is precisely the class this plugin falls into**: a fetch a
person asked for, on their own behalf. Leboncoin permits it — and still closes
`/recherche`, which is the results page, which is the sweep.

That is not an obstacle to route around, it is a considered position: *read an
ad a human pointed you at; do not harvest our search results.* **A browser
adapter changes nothing here** — what is refused is not the access, it is the
sweeping. `cadremploi.md` uses a browser because a script is blocked; nothing
of the kind applies.

**What remains true and useful:** individual ad pages are not disallowed to the
retrieval class. That is exactly the `cover-letter <URL>` case — the user finds
an ad, hands over the link, and the plugin does everything else. It needs no
adapter and works today.

**Worth carrying to other adapters:** this is the first site here to
distinguish *user-initiated retrieval* from *training crawls*, and to allow the
first while refusing the second on the pages that matter. `softy.md` banned
every AI agent outright; `taleez.md` allowed `ClaudeBot` explicitly. When a
`robots.txt` names AI agents, read which class it is talking about before
concluding anything — the answer is no longer binary.

## Investigated and closed — Monster

**Verified 2026-08-31, live.** Monster gets no French adapter, and the reason is
not access: **there is no French job board left to adapt.** Monster still
exists, still calls itself a job board, and still answers to `monster.fr` — the
name is the only thing that survived.

### `monster.fr` is a CV advert

Every path on the domain answers `301` to **one** destination, discarding the
path and the query with it:

| Asked | Sent to |
| :-- | :-- |
| `www.monster.fr/emploi/recherche?q=developpeur` | `www.monster.com/fr/` |
| `www.monster.fr/emploi/annonce/12345` | `www.monster.com/fr/` |
| `www.monster.fr/entreprises/` | `www.monster.com/fr/` |
| `jobview.monster.fr/...`, `job-openings.monster.fr/...` | `www.monster.com/` |

And `www.monster.com/fr/` is not a job board. Its `<title>` is **"Monster et
monCVparfait CV designer"**, its body sells a CV builder, and it contains **no
search form and not one link to a job** — the only outbound links are to
`moncvparfait.fr`, the affiliate. The footer's language switcher confirms it is
not a French accident: **every non-US locale points at a CV page** —
`fr`, `de`, `es`, `it`, `nl`, `se` at `/xx/`, and Canada, Ireland and the United
Kingdom at `/resume/`. The US board is the only board.

**This matters to `cover-letter <URL>` even with no adapter.** An old Monster
France link does not 404 and does not say *"offre expirée"*. It returns **200**
and a CV advertisement — a page with a title, prose and a call to action, which
is exactly the shape a fetch-and-summarise step mistakes for an ad. If a user
hands over a `monster.fr` URL, say the ad is gone; do not describe the page.

### The US board accepts a French location and answers with Mississippi

This is worth recording in full, because it is the most convincing wrong answer
any board in this repository has given.

`www.monster.com/jobs/search` accepts `where=` without validating it. Measured:

| Searched | Header echoed back | What came back |
| :-- | :-- | :-- |
| `q=engineer&where=Lyon, France` | *"Engineer Jobs in Lyon, France"* | 7 ads: **Lyon, MS**, Clarksdale MS, West Helena AR |
| `q=ingénieur&where=France` | *"Ingénieur Jobs in France"* | Huntsville AL, Boise ID, Houston TX, Kassel DE |
| `q=developpeur&where=Paris, France` | *"Developpeur Jobs in Paris, France"* | **1 ad**, Sabattus, **Maine** |
| `q=Paris, France` (empty `where`) | *"…Jobs in **Remote**"* | Palo Alto CA, and **France, ID** |

It matched **Lyon, Mississippi** — a Delta town of a few hundred people — and
returned its neighbours within 30 miles. `France` was dropped. An empty `where`
silently became `Remote`. Nothing errored, nothing warned, and the page kept
repeating the French location back in its own heading while serving Arkansas.

A handful of genuinely European rows are in the index (*"Systems Engineer,
Territory South (Lyon Based) France"*, a Kassel ad in German) — but they surface
because their **title** contains the word, never because the location filter
found them. There is no French inventory to sweep, only French words in US ads.

### A browser adapter does not rescue this one

`indeed.md`, `cadremploi.md` and `softy.md` each use the user's own Chrome
because a script is blocked. Monster is blocked too — **DataDome** guards every
page and the underlying API alike:

```
POST https://appsapi.monster.io/jobs-svx-service/v2/monster/search-jobs/samsearch/en-US?apikey=…
```

From a script that answers `403` with a **`geo.captcha-delivery.com` URL**, and
this plugin does not solve CAPTCHAs. From inside the browser it answers
normally — so the browser route is *technically* open, exactly as it was for
Indeed.

**It is still the wrong build**, and the distinction is the point: for Indeed
the browser buys access to French ads. Here it would buy access to
**Mississippi**. The blocker is not the wall, it is the inventory. Note also
that the locale is a path segment (`…/samsearch/en-US`) — `fr-FR` and `fr` were
tried and are not a way in.

### What would reopen this

A French Monster job board coming back — a `monster.fr` that serves its own
search again, or a `www.monster.com/fr/jobs/…` that returns French locations.
Re-check by asking one question, which takes ten seconds and no adapter:

```bash
curl -sI 'https://www.monster.fr/emploi/recherche?q=x' | grep -i location
```

While that answers `https://www.monster.com/fr/`, there is nothing here. Until
then Monster is a brand licensed onto a CV builder in France, and the honest
answer to *"can it scan Monster?"* is **"Monster no longer publishes French
jobs"** — not *"not yet"*, which invites the user to wait for something that is
not coming.

## Investigated and not built — Beetween

**Verified 2026-08-31.** Beetween is the fifth French ATS name on the list, and
the only one of the five investigated that **cannot have a platform adapter** —
for a reason worth writing down, because it is not a wall, it is an absence.

The other four each have one contract that holds across every customer:
Taleez's `/api/careez`, Flatchr's `__NEXT_DATA__`, Talentsoft's `fld*` element
ids, DigitalRecruiters' single API keyed by hostname. **Beetween has none.** It
sells careers sites *"from basic to fully customised"*, and its own —
`recrutement.beetween.fr` — is a bespoke **WordPress + Elementor** build whose
pages call no Beetween service at all: the only host they talk to is their own.

What was established:

- Ads live at `/poste/<id>-<slug>/` **on that site**, and the ad page carries a
  standard schema.org `JobPosting` — description, `baseSalary`, `datePosted`,
  education and experience requirements.
- **The sitemap contains no ads** — only posts, pages, categories and tags — so
  there is no enumeration route even on that one site.
- The single hosted-looking domain found in the markup,
  `<tenant>.nous-recrutons.fr`, answers **403 in a real browser as well as to a
  script**. Not bot protection: that host is not served publicly.
- No Beetween *customer* careers site was found to verify against.

An adapter written now would be an adapter for **one WordPress theme**, and
would break on the next customer. Rule 1 forbids shipping that.

### There *is* a platform surface — and it still does not make a board

Followed up 2026-08-31, from the France Travail partner links: **79 BEETWEEN
ads across four departments all pointed at one host**,
`app.beetween.com/WeaselWeb/p/#/apply/job/<id>/<slug>`. So Beetween does have a
shared surface after all — the customer careers sites vary, the *apply* pages
do not.

Three things about it, all measured:

- It is a **hash-route Vue SPA**. The shell is 1.3 KB with no data and no
  JSON-LD, so plain HTTP gets nothing.
- Its backend is `https://apehi.beetween.com` — read out of
  `window.__NUXT__.config.backendApiBaseUrl` — and it answers unauthenticated:
  `/WeaselWeb/api/publicoffer/detail` returns a **RESTEasy 404**, which is a
  live backend rejecting a wrong path, not a refusal. The exact call was not
  established.
- **It is a detail surface, not a listing.** One ad at a time, keyed by ad id.
  No per-tenant index was found on that host.

So even fully reverse-engineered, Beetween would not be a board: **France
Travail would still be doing the enumerating**, and Beetween would only add the
employer's name and the full ad text to rows the partner feed already carries
anonymously. Real, but modest — and resting on an undocumented internal
application API with no contract and no versioning.

**Two routes remain, and neither is blocked:** finish reverse-engineering
`apehi.beetween.com`, or read the SPA in the user's own browser as
`cadremploi.md` does. Both were left unbuilt deliberately: the value is small
and the foundation is unstable.

**What would change that:** one working Beetween *customer* careers URL with a
real listing on it. That puts Beetween back in the shape of every other ATS
here — a per-tenant adapter — and most plausibly a `JobPosting` reader, since
schema.org is identical whoever emits it.

**And Beetween ads already reach the ledger.** It is the **largest single
supplier** of France Travail's partner feed — 38 of 150 sampled Paris partner
ads, ahead of METEOJOB — so `france-travail.md` with `origineOffre=2` carries
them today, without the employer being named.

## Investigated, buildable, not built

**jobeo.ch** — a staffing-agency board (Adecco and others), verified 2026-08-29
over the same job-room sweep that produced `fachkraft.md`.

What is established: the listing lives at **`/jobsearch/offers`** (also `/jobs`)
and serves **20 ads per page**; every ad page carries a `JobPosting` block whose
`hiringOrganization` is the agency, with a **GUID** as `identifier`. There is
**no `validThrough`**.

What is not: pagination was never exercised, and it is unclear which of the slug
or the GUID is the stable key — so the ledger contract cannot be met yet.

One trap already worth knowing: **`/candidat/offres/` — the path job-room
publishes in its `externalUrl` — answers `200` with a "Page non trouvée" page.**
The ad URLs under it work; the directory itself does not.

Built when someone needs it; the remaining work is one session, not a project.

## Boards without an adapter

The user can still apply to an ad from any board: `cover-letter` takes a URL,
and falls back to asking for pasted ad text when the page is gated. It is only
the *scan* — the automated sweep that fills the ledger — that needs an adapter.

So a reasonable answer to "can it do <board X>?" is: *"not automatically yet;
give me an ad URL from it and I'll do everything else."* Say that, rather than
attempting a scan that has never worked.

**Two boards are exceptions, and "not yet" is the wrong answer for both.**
Leboncoin has declined the sweep on purpose, and **Monster no longer publishes
French jobs at all** — telling either user to wait invites them to wait for
something that is not coming. Read their sections above and say what is
actually true.
