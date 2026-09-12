# Board measurement — Rwandajob.com (`www.rwandajob.com`, Rwanda, AfricaWork): refused to our client, served to a browser, 84 stated and 84 walked from page zero

<!-- verified: 2026-09-12 -->

<!-- hosts: www.rwandajob.com, rwandajob.com -->
<!-- script: none -->
<!-- countries: RW -->
<!-- content: measured · **84 distinct advertisement addresses** over `/job-vacancies-search-rwanda?page=0…` (25 + 25 + 25 + 9; the next page empty), read from a connected browser tab, **and the page states «84 Job ads found» — equal**; the pager is zero-based, as on `ghanajob.md` and `namijob.md` · 2026-09-12 -->
<!-- witness: the page's own «84 Job ads found», read on every page of the walk and printed beside the distinct count («84 emitted, site states 84 — equal») · 2026-09-12 -->

**Rwanda's AfricaWork board — the family's managed template, the family's
25-byte refusal to the declared client, and its own dated reading.**
Measured 2026-09-12 12:35–12:40 UTC: two reads with the declared client,
then one Claude-in-Chrome tab, the guard on the exact path first. *One of
four hosts read in the same six minutes — Sierra Leone, Rwanda, Gabon,
Côte d'Ivoire — each walked and counted on its own; the template is
shared, the numbers are not.*

## Rules, transport, the door

```
robots.txt        200, 1 836 B — the managed template: `*` open, `ClaudeBot` refused, `Claude-User` not named → allowed True, certain True; identity claude-user
declared client   GET https://www.rwandajob.com/   403, 25 B, md5 9ccabba20b9f4ec7d18bd6644579e5bf, server cloudflare — twice, 2 s apart, identical
browser tab       / → 200 «Job Vacancies and Recruitment in Rwanda | Rwandajob.com» · no challenge, no interstitial
```

## The listing — the site's count met exactly, from page zero

```
/job-vacancies-search-rwanda              «84 Job ads found» · 25 cards a page · pager zero-based (the link labelled «2» is ?page=1)
fetch ?page=0 …  25 + 25 + 25 + 9 → **84 distinct /job-vacancies-rwanda/<slug>-<id>** · the next page → 0 cards
                 **84 emitted, site states 84 — equal.**
advertisement id the trailing number of the address (…-kigali-153365)
```

## The advertisement

```
GET /job-vacancies-rwanda/national-sales-manager-kigali-153365    200 — two ld+json blocks; the first a JobPosting (datePosted 2026-09-11T15:55:01+02:00)
JSON.parse rejects both blocks («Bad control character in string literal») — read tolerantly, as `ghanajob.md` says; never «no JobPosting»
```

## The procedure a session follows — this is the adapter (decision of 2026-09-08)

The six steps of `ghanajob.md` with this host's two paths — `/job-vacancies-search-rwanda` for
the listing, `/job-vacancies-rwanda/<slug>-<id>` for the advertisement: guard → tab →
`?page=0, 1, 2 …` until empty, 1.5 s apart → **«n emitted, site states
N»** → the JobPosting read tolerantly → close.

## What this card does not establish

- **The JobPosting's full field set** — head fields only.
- **Whether the count moves within the day** — one read.
- **No script ships.** The route is a browser tab and fetches from it.
