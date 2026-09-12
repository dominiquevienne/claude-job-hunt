# Board measurement — Ghanajob.com (Ghana, AfricaWork): refused to our client, served to a browser, 262 stated and 262 walked once the pager is read from zero

<!-- verified: 2026-09-12 -->

<!-- hosts: www.ghanajob.com, ghanajob.com -->
<!-- script: none -->
<!-- countries: GH -->
<!-- content: measured · **262 distinct advertisement addresses** over the 11 pages of `/job-vacancies-search-ghana?page=0…10` (10 × 25 + 12; `?page=11` empty), read from a connected browser tab, **and the page states «262 Job ads found» — equal**; a first walk that started at `?page=1` found 237 and reported «25 short» — the pager is zero-based and `?page=1` is the SECOND page · 2026-09-12 -->
<!-- witness: the page's own «262 Job ads found», read on every page of the walk and printed beside the distinct count («262 emitted, site states 262 — equal»); the 25 the first walk missed were page 0 · 2026-09-12 -->
<!-- route: browser · 262 · 2026-09-12 -->

**Ghana's AfricaWork board — the same managed rules template, the same
25-byte refusal to the declared client, the same Cloudflare front as its
seven siblings, and a reading of its own rather than a verdict copied
from them.** Measured 2026-09-12 12:22–12:30 UTC: two reads with the
declared client, then one Claude-in-Chrome tab, the guard on the exact
path first. *Two of this card's first findings were wrong in the same
way — the reader's, not the site's — and both are kept below, corrected,
because the next AfricaWork host will present the same two traps.*

## Rules, transport, the door

```
robots.txt        200, 1 836 B — the managed template: `*` open, `ClaudeBot` refused, `Claude-User` not named → allowed True, certain True; identity claude-user
declared client   GET https://www.ghanajob.com/   403, 25 B, md5 9ccabba20b9f4ec7d18bd6644579e5bf, server cloudflare — twice, 2 s apart, identical
browser tab       / → 200 «Job Vacancies and Recruitment in Ghana | Ghanajob.com» · no challenge, no interstitial
```

**Borne 0 held**: family (1) of `robots-policy.md`, the refusal goes to the
declared client and to nobody else.

## The listing — the pager counts from zero, and a walk from one is 25 short

```
GET /job-vacancies-search-ghana            «262 Job ads found» · 25 cards · pager links ?page=1 [2] · ?page=2 [3] · … ?page=10 [11]
fetch ?page=1 … 10                         25 × 9 + 12 = 237 → «237 emitted, site states 262 — 25 short»      12:23 UTC  <- WRONG START
fetch ?page=0 … 10                         25 × 10 + 12 = **262 distinct** /job-vacancies-ghana/<slug>-<id> · ?page=11 → 0    12:29 UTC
                                           **262 emitted, site states 262 — equal.**
card                                       title – city · employer · the first lines of the body
advertisement id                           the trailing number of the address (…-kumasi-255659)
```

**The pager's link labelled «2» points at `?page=1`; the first page is
`?page=0` (and the bare path).** *A walk that starts at `?page=1` skips
the first page, comes up exactly one page short, and the shortfall reads
as a site defect — «expired but still counted», «a ten-page cap» — when it
is the reader's index.* Measured the same minute on `namijob.com`
(144 stated, 119 from `?page=1`, 144 from `?page=0`): **the constant 25
across two hosts was the tell.** The adapter starts at zero.

## The advertisement — a JobPosting that a strict JSON parser rejects

```
GET /job-vacancies-ghana/senior-health-safety-officer-kumasi-255659    200, 62 454 B
two <script type="application/ld+json"> blocks — the first a JobPosting (datePosted 2026-09-11T13:55:01+00:00, title, hiringOrganization SAT INTERNATIONAL, validThrough 2026-09-29, description…)
JSON.parse on either block: SyntaxError «Bad control character in string literal» — raw control characters inside the description string
labelled lines in the page: «Published on 11.09.2026» · Industries · Job category · City : Kumasi · Experience level : 5 to 10 years – more than 10
```

**The block is there and it is a JobPosting; a strict parser says «no
JobPosting» and that sentence stood in this card's first version.** *The
same trap on `namijob.com`: two blocks, both rejected, a JobPosting once
control characters are folded.* The adapter reads the block with a
tolerant parser (`_ldjson.postings`, or control characters folded to
spaces first) and reports the parse failure beside the read, never «none».

## The procedure a session follows — this is the adapter (decision of 2026-09-08)

1. guard `www.ghanajob.com` on `/job-vacancies-search-ghana` and on
   `/job-vacancies-ghana/…` before anything;
2. `navigate https://www.ghanajob.com/job-vacancies-search-ghana` in the
   session's own tab; read «N Job ads found» — **N is the site's count**;
3. from the tab, `fetch('/job-vacancies-search-ghana?page=P')` for
   **P = 0, 1, 2, …** until a page carries no card, 1.5 s apart; collect
   the distinct `/job-vacancies-ghana/<slug>-<id>` addresses; the id is
   the trailing number;
4. print **«n emitted, site states N — equal / k short»** — on the day,
   «262 emitted, site states 262 — equal»; a shortfall of exactly one
   page's worth means the walk started at 1;
5. one advertisement page for the body: the JSON-LD JobPosting, parsed
   tolerantly (control characters), else the labelled lines;
6. close the tab.

## What this card does not establish

- **Whether the siblings behave the same** — `namijob.com` did on both
  traps the same minute; the other six carry their own dated readings,
  and the family shares a template, not a verdict.
- **The description's full field set** — the JobPosting was read by its
  head fields only; `baseSalary`, `employmentType`, `jobLocation` were
  not extracted here.
- **No script ships.** The route is a browser tab and fetches from it.
