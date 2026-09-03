# Board adapter — NEXT (Pakistan, jobs.gov.pk)

<!-- verified: 2026-09-03 -->
<!-- hosts: jobs.gov.pk -->

Pakistan's national employment exchange. **No key, no cookie, no browser, no
endpoint** — one GET returns every advertisement it holds.

```
GET /JobSeeker/SearchJobs?keyword=   → 1 511 advertisements, ~3.5 MB
GET /JobSeeker/ViewJobDetails/<id>?orgId=&jobId=   → one advertisement
```

## 1 506 of 1 511 have closed. Five are live.

That is the number that matters, and the board marks it itself: every card
carries `portal-job-card--live` or `portal-job-card--expired`. **`--live`
returns the five.** Without it the count is accurate and 99.7% of it is dead —
a figure worth saying rather than leaving in a ledger.

## The page's own counter contradicts the page's own cards

| | |
|---|---|
| `/JobSeeker/JobSeekerJobs` header | **1511** total, 1506 expired |
| `/JobSeeker/SearchJobs` header | **5** total, 1506 expired |
| `/JobSeeker/SearchJobs` markup | 1511 cards, 1506 marked expired |

**The same counter label carries different numbers on two pages**, and on the
search page it is not arithmetic — 5 total beside 1 506 expired. The browse
page is the coherent one: 1 506 + 5 = 1 511, matching the rendered cards
exactly.

**So the adapter counts the cards and prints the header beside them**, saying
plainly when they differ instead of choosing the convenient one. Two
measurements of the same quantity are worth having precisely because they can
disagree; **merging them would have hidden this.**

## Fields

Read by class — `portal-job-card__title`, `portal-job-card__org`,
`portal-badge--type` — and the facts by their **label**, because position is
not stable: `Salary` appears on 1 428 cards and `Scale` on 83, so the third
fact is not the same fact twice.

Fill rates over all 1 511, counted on values:

```
Deadline    1 511 / 1 511      Salary    1 428 / 1 511   (94.5%)
Location    1 511 / 1 511      Scale        83 / 1 511    (5.5%)
Vacancies   1 511 / 1 511
```

## The sign-in link is the apply route, not a wall

The five live cards offer *"Sign in to apply"* beside *"View details"*. **The
detail page answers 200 with no wall** — the site's own words are *"Login is
required only to apply."* The adapter reads the public detail URL, **refuses a
`/Account/Login` URL before making any request**, and puts
`apply_needs_sign_in` in the row so the distinction is recorded rather than
remembered.

## Two notes on the host

`robots.txt` is **not a rules file** — the host serves markup for it — so no
rules were read and **none were invented**. `www.jobs.gov.pk` does not resolve.

**It is slow.** The 3.5 MB listing timed out at 30 s and answered at 60 s.
`get()` allows 90 s and says, on failure, that a timeout here is not an empty
board.
