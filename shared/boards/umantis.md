# Board adapter — Haufe / Abacus umantis

**An ATS, not a board**, in the same family as Workday, Greenhouse, Lever and
Ashby: one employer per tenant, no search across employers. It earns an adapter
for the reason those did — it answers *"is my target employer hiring?"* — and it
matters in Switzerland for a reason they do not: **HiringCafe indexes none of
it.** Zero of 771 Swiss ads came from umantis (`hiringcafe.md`), so the SMEs,
communes, clinics and institutes that run on it are invisible to every sweep
that ships today.

Read by `skills/job-scan/scripts/umantis.py`. Public HTML, **no key, no cookie,
no browser** — except on the tenants noted in trap 3.

**Verified 2026-08-28** against three live tenants: BOBST (`jobs.bobst.com`,
10 vacancies), Swiss TPH (`recruitingapp-2698.umantis.com`, 2) and Kanton
St. Gallen (`recruitingapp-2800.umantis.com`).

## The two paths, and the SSO that does not matter

```
https://<host>/Jobs                                  the listing
https://<host>/Vacancies/<id>/Description/<segment>  one vacancy, full text
```

`<host>` is either `recruitingapp-<n>.umantis.com` or a vanity domain the
employer owns (`jobs.bobst.com`). **The host tells you nothing; the path tells
you everything.**

**The site root is often gated by SAML SSO — and that is irrelevant.** BOBST's
root 302s to `sso.umantis.com`, while `/Jobs` and every vacancy under it answer
`200` unauthenticated, with the complete description: 1 274 to 5 950 characters
of text across the five vacancies measured.

## The trap that governs the whole adapter

**The trailing segment is per *vacancy*, not per tenant, and it must never be
guessed.** Measured on BOBST, one tenant, four vacancies:

| Vacancy | `/1` | `/2` | `/3` |
| :-- | :-- | :-- | :-- |
| 9151 | shell | **the job** | shell |
| 9220 | shell | shell | **the job** |
| 9221 | shell | shell | **the job** |
| 9222 | shell | shell | **the job** |

Swiss TPH serves its vacancies at `/1`, and answers with the shell at `/2`.
**Every one of those wrong segments returns HTTP `200`.** Nothing in the status
code says you asked wrongly.

**The discriminator is the `<title>`, and specifically what precedes the
separator:**

| `<title>` | Reading |
| :-- | :-- |
| `Apprenti employé-e de commerce CFC` | the vacancy |
| `  \| Applicant Management` | the tenant's chrome — **wrong segment** |
| `  \| eRecruiting Swiss TPH` | the same thing, on a tenant that renamed it |

What follows the pipe is per-tenant and localised; **what is stable is that
nothing precedes it.** The script tests `title.startswith("|")`.

**So: read the segment from `/Jobs`, which links each vacancy with one that
works.** `umantis.py ad --id <n>` consults the listing before falling back to
probing `1…5`, and refuses rather than reporting an empty description.

> This corrects `shared/ats-open-check.md` as shipped in v1.5.0, which said the
> trailing `2` is required and is *not* a view index. It is one, it varies per
> vacancy, and hardcoding `2` returns the shell on three of BOBST's four current
> vacancies and on every Swiss TPH vacancy.

## Closed vacancies say so, with a status code

**`403` is the answer, and it is reliable** — the one thing a board never gives
you. Confirmed 2026-08-28 on two unrelated tenants and **at every segment**: an
unknown or withdrawn id answers `403`, not `404` and not a 200 with a banner.

| Response | Reading |
| :-- | :-- |
| `200` + a job title in `<title>` | **Open.** |
| `403` | **Not open** — closed, withdrawn, or never existed. |
| `200` + empty title slot on every segment tried | **Not an answer.** Wrong URL, not a dead ad. |

`umantis.py check --host … --id …` returns this as a verdict and exits `0` when
open, `1` otherwise. That is what `cover-letter` step 1b wants.

## Traps

**1. An unallocated tenant number answers `200` with the vendor's own
marketing page.** `recruitingapp-1000` and `recruitingapp-2000` both returned
*"Abacus Umantis – Die HR-Suite für DACH-Mittelständler"* with zero vacancies.
A wrong host therefore looks exactly like an employer with nothing open. The
script matches the vendor title and refuses; **never report that as an empty
board.** Non-existent numbers fail DNS instead, which is at least honest.

**2. Some vacancies are live but unlisted.** BOBST's `9151` — the Product Owner
role this plugin first met through a jobup ad — answers `200` with its full
description at `/2`, and does **not** appear in `/Jobs`. So the listing is not
the whole board, and an id that is absent from it is not evidence the ad closed.
Same shape as Ashby's `isListed: false`.

**3. Some tenants render their listing client-side, and then `/Jobs` carries no
vacancies at all.** Kanton St. Gallen returns `200` and 64 kB of chrome with
zero `/Vacancies/` links; its rows arrive from a `connectortable` widget, and
following that widget's own pagination parameters (`?tc<id>=p2`) still returns
none. **This is not an empty board.** The script detects the widget and says so
with its own exit code rather than printing nothing. Read such a tenant in the
browser, or reach a vacancy directly if you already have its id — `ad` and
`check` still work there, because the vacancy path does not depend on the
listing.

**4. There is no server-side search.** The whole board comes back — 2 to 10
vacancies on the tenants measured — and `--search` filters titles locally. When
that keeps nothing the script says *"the board is not empty; every vacancy was
filtered out"*, because zero results and zero matches are different facts.

**5. No structured data.** No JSON-LD, no microdata, no `JobPosting` markup.
Title and description come from the HTML, and there is no reliable posting date
or location field — do not invent one for the ledger.

## The one thing this family cannot do here: find the tenant

Workday, Greenhouse, Lever and Ashby all resolve an employer name to a tenant
through HiringCafe. **That route does not exist for umantis**, by the same
measurement that justifies the adapter: HiringCafe indexes none of it.

So `umantis.py` has **no `resolve` command**, deliberately. The host arrives:

- from the user, who names the employer's careers site;
- or from an `externalUrl` on a jobup, jobs.ch or job-room row — which is
  exactly how this ATS was first met (`shared/boards/jobup.md`);
- or from a web search for the employer plus *"umantis"* or *"/Vacancies/"*.

**Recognise it by the path**, `/Vacancies/<id>/Description/<n>`, never by the
host. Say *"give me their careers URL"* rather than guessing a tenant number:
the guess lands on the vendor's marketing page and looks like an answer.

## The ledger

```
umantis:<host>:<id>          e.g. umantis:jobs.bobst.com:9151
```

The host is part of the key for the reason it is on the other ATS boards: this
platform hosts one board per employer, and the id alone cannot rebuild a URL.
The segment is **not** in the key — it is a property of the page, recoverable
from the listing, and putting it in the key would freeze a value that the
employer can change when they add a language.

## Applying

umantis runs its own application flow, behind the vendor's account creation.
**The plugin does not create accounts and does not fill credential fields** —
hand the user the vacancy URL and their documents, as for any external ATS.

## Pace

Boards are small and requests are cheap. One `/Jobs` per employer per run, plus
one request per vacancy read, is the whole cost.
