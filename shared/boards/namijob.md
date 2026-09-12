# Board measurement — Namijob.com (Namibia, AfricaWork): refused to our client, served to a browser, 144 stated and 144 walked from page zero

<!-- verified: 2026-09-12 -->

<!-- hosts: www.namijob.com, namijob.com -->
<!-- script: none -->
<!-- countries: NA -->
<!-- content: measured · **144 distinct advertisement addresses** over `/job-vacancies-search-namibia?page=0…5` (5 × 25 + 19; `?page=6` empty), read from a connected browser tab, **and the page states «144 Job ads found» — equal**; a walk from `?page=1` finds 119 — the pager is zero-based · 2026-09-12 -->
<!-- witness: the page's own «144 Job ads found», read on every page and printed beside the distinct count («144 emitted, site states 144 — equal»); the same two traps as `ghanajob.md`, measured the same minute · 2026-09-12 -->
<!-- route: browser · 144 · 2026-09-12 -->

**Namibia's AfricaWork board — the family's template, the family's
refusal, and its own dated reading.** Measured 2026-09-12 12:26–12:29 UTC:
two reads with the declared client, then one Claude-in-Chrome tab, the
guard on the exact path first. *The only board of its country in this
repository.*

## Rules, transport, the door

```
robots.txt        200, 1 836 B — the managed template: `*` open, `ClaudeBot` refused, `Claude-User` not named → allowed True, certain True; identity claude-user
declared client   GET https://www.namijob.com/   403, 25 B, md5 9ccabba20b9f4ec7d18bd6644579e5bf, server cloudflare — twice, 2 s apart, identical
browser tab       /job-vacancies-search-namibia → 200 «Jobs in Namibia | Namijob.com» · no challenge, no interstitial
```

## The listing — zero-based pages, and the site's count met exactly

```
«144 Job ads found» · pager links ?page=1 [2] · ?page=2 [3] · ?page=5 [6]   — the link labelled «2» is ?page=1
fetch ?page=1 … 5      25 × 4 + 19 = 119   («25 short» — the walk skipped page 0)
fetch ?page=0 … 5      25 × 5 + 19 = **144 distinct** /job-vacancies-namibia/<slug>-<id> · ?page=6 → 0     12:28:23 UTC
                       bare path = ?page=0 (25 of 25 shared) · ?page=0 ∩ ?page=1 = 0
                       **144 emitted, site states 144 — equal.**
advertisement id       the trailing number of the address (…-erongo-namibia-265424)
```

*This host is where the zero-based pager was caught: `ghanajob.com` had
just read «25 short» a minute earlier, and the same constant here said
the shortfall was the reader's index.* Both cards start their walk at
zero.

## The advertisement — a JobPosting behind malformed JSON

```
GET /job-vacancies-namibia/branch-manager-electrical-industrial-technical-support-erongo-namibia-265424   200
two ld+json blocks; JSON.parse: «Bad control character in string literal» on both
control characters folded → JobPosting: title «Branch Manager – Electrical, Industrial and Technical Support - Erongo, Namibia» · hiringOrganization HIC AGENCIES
                              datePosted 2026-09-11T14:55:01+01:00 · validThrough 2026-09-20 · description 1 832 chars · jobLocation Erongo, Namibia (addressCountry «Namibia»)
page lines: «Published on 11.09.2026» · Industries · City · Experience level
```

**The JobPosting is there; a strict parser says it is not.** The adapter
folds control characters (or uses `_ldjson.postings`) and reports the
parse failure beside the read.

## The procedure a session follows — this is the adapter (decision of 2026-09-08)

The six steps of `ghanajob.md`, with `namibia` for `ghana` in both paths
— the template is shared, and each host is walked and counted on its own
day: guard → tab → `?page=0, 1, 2 …` until empty → «n emitted, site
states N» → the JobPosting read tolerantly → close.

## What this card does not establish

- **The JobPosting's full field set** (`baseSalary`, `employmentType`)
  — head fields only were read.
- **Whether the count moves within the day** — one read.
- **No script ships.** The route is a browser tab and fetches from it.
