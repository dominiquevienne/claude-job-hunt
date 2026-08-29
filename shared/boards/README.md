# Board adapters

`job-scan` is board-agnostic: it owns the scoring, the ledger and the reporting,
and each adapter owns one site. Sixteen ship today, each verified against the live
site.

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
| Workday | `workday.md` | **Shipped.** One employer at a time, by host + tenant + site. Public JSON, **no browser**. Where the large Swiss employers are |
| Haufe / Abacus umantis | `umantis.md` | **Shipped.** One employer at a time, by host. Public HTML, **no browser**. The Swiss SMEs, communes, clinics and institutes **HiringCafe does not index at all**. No tenant resolution exists — the user supplies the careers URL |
| LinkedIn | `linkedin.md` | **Shipped.** Search sweep, description reading, assisted Easy Apply |
| jobup.ch | `jobup.md` | **Shipped.** Search sweep and description reading. No login needed to scan; the in-site apply flow is *not* supported |
| fachkraft.ch / sta.jobs | `fachkraft.md` | **Shipped.** A staffing **agency** board — the whole listing in one request (~3 500 ads), **no browser**. One board on two domains whose numeric ids are disjoint; the `<n>-STAxx` reference is the only key that crosses |
| Michael Page | `michaelpage.md` | **Shipped.** A recruitment **agency** board — one search across many employers, country-scoped, **no browser**. The employer is described and **never named**, so no dedup key crosses to their own ATS |
| jobs.ch | `jobs-ch.md` | **Shipped.** jobup's German-language sibling on the same platform — **and the same ad ids**, so an ad on both boards is one row, matched by UUID. Three times the national volume, thinner in Romandie: it does not replace jobup |
| Indeed | `indeed.md` | **Shipped.** Search sweep and description reading, country-scoped. **Serves anti-bot challenges** — the user solves them, never the plugin |
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

Three states, three different behaviours — never improvise a fourth:

| State | What `job-scan` does |
| :-- | :-- |
| No board enabled | Scans nothing. Says so, lists the adapters available, and offers `/job-setup boards` |
| Enabled but a required setting is empty | Skips that board, names the missing key, and offers to fill it. **Never half-runs** |
| Enabled and complete | Sweeps it |

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
when it was true. It changes nothing and always exits 0: **a stale adapter is
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
