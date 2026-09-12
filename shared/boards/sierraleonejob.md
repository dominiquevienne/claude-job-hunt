# Board measurement — Sierraleonejob.com (`www.sierraleonejob.com`, Sierra Leone, AfricaWork): refused to our client, served to a browser, 52 stated and 52 walked from page zero

<!-- verified: 2026-09-12 -->

<!-- hosts: www.sierraleonejob.com, sierraleonejob.com -->
<!-- script: none -->
<!-- countries: SL -->
<!-- content: measured · **52 distinct advertisement addresses** over `/job-vacancies-search-sierra-leone?page=0…` (25 + 25 + 2; the next page empty), read from a connected browser tab, **and the page states «52 Job ads found» — equal**; the pager is zero-based, as on `ghanajob.md` and `namijob.md` · 2026-09-12 -->
<!-- witness: the page's own «52 Job ads found», read on every page of the walk and printed beside the distinct count («52 emitted, site states 52 — equal») · 2026-09-12 -->
<!-- route: browser · 52 · 2026-09-12 -->

**Sierra Leone's AfricaWork board — the family's managed template, the family's
25-byte refusal to the declared client, and its own dated reading.**
Measured 2026-09-12 12:35–12:40 UTC: two reads with the declared client,
then one Claude-in-Chrome tab, the guard on the exact path first. *One of
four hosts read in the same six minutes — Sierra Leone, Rwanda, Gabon,
Côte d'Ivoire — each walked and counted on its own; the template is
shared, the numbers are not.*

## Rules, transport, the door

```
robots.txt        200, 1 836 B — the managed template: `*` open, `ClaudeBot` refused, `Claude-User` not named → allowed True, certain True; identity claude-user
declared client   GET https://www.sierraleonejob.com/   403, 25 B, md5 9ccabba20b9f4ec7d18bd6644579e5bf, server cloudflare — twice, 2 s apart, identical
browser tab       / → 200 «Job Vacancies and Recruitment in Sierra Leone | Sierraleonejob.com» · no challenge, no interstitial
```

## The listing — the site's count met exactly, from page zero

```
/job-vacancies-search-sierra-leone              «52 Job ads found» · 25 cards a page · pager zero-based (the link labelled «2» is ?page=1)
fetch ?page=0 …  25 + 25 + 2 → **52 distinct /job-vacancies-sierra-leone/<slug>-<id>** · the next page → 0 cards
                 **52 emitted, site states 52 — equal.**
advertisement id the trailing number of the address (…-home-70039)
```

## The advertisement

```
GET /job-vacancies-sierra-leone/manager-work-home-70039    200 — two ld+json blocks; the first a JobPosting (datePosted 2026-09-11T13:55:01+00:00, validThrough 2026-09-25)
JSON.parse rejects both blocks («Bad control character in string literal») — read tolerantly, as `ghanajob.md` says; never «no JobPosting»
```

## The procedure a session follows — this is the adapter (decision of 2026-09-08)

The six steps of `ghanajob.md` with this host's two paths — `/job-vacancies-search-sierra-leone` for
the listing, `/job-vacancies-sierra-leone/<slug>-<id>` for the advertisement: guard → tab →
`?page=0, 1, 2 …` until empty, 1.5 s apart → **«n emitted, site states
N»** → the JobPosting read tolerantly → close.

## What this card does not establish

- **The JobPosting's full field set** — head fields only.
- **Whether the count moves within the day** — one read.
- **No script ships.** The route is a browser tab and fetches from it.
