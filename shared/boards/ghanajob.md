# Board measurement — Ghanajob.com (Ghana, AfricaWork): refused to our client, served to a browser, and a listing that states 262 while its ten pages carry 237

<!-- verified: 2026-09-12 -->

<!-- hosts: www.ghanajob.com, ghanajob.com -->
<!-- script: none -->
<!-- countries: GH -->
<!-- content: measured · **237 distinct advertisement addresses** over the 10 pages of `/job-vacancies-search-ghana` (9 × 25 + 12; page 11 empty), read from a connected browser tab, **against «262 Job ads found» stated by the page — 25 short**, exactly one page's worth, unexplained; the site's counter is the anchor and the walk is the reader · 2026-09-12 -->
<!-- witness: the page's own «262 Job ads found», read on every page of the walk and printed beside the distinct count («237 emitted, site states 262 — 25 short»); the 25 do not appear on any page the pager exposes · 2026-09-12 -->

**Ghana's AfricaWork board — the same managed rules template, the same
25-byte refusal to the declared client, the same Cloudflare front as its
seven siblings, and a reading of its own rather than a verdict copied
from them.** Measured 2026-09-12 12:22–12:24 UTC: two reads with the
declared client, then one Claude-in-Chrome tab, the guard on the exact
path first.

## Rules, transport, the door

```
robots.txt        200, 1 836 B — the managed template: `*` open, `ClaudeBot` refused, `Claude-User` not named → allowed True, certain True; identity claude-user
declared client   GET https://www.ghanajob.com/   403, 25 B, md5 9ccabba20b9f4ec7d18bd6644579e5bf, server cloudflare — twice, 2 s apart, identical
browser tab       / → 200 «Job Vacancies and Recruitment in Ghana | Ghanajob.com» · no challenge, no interstitial
```

**Borne 0 held**: family (1) of `robots-policy.md`, the refusal goes to the
declared client and to nobody else.

## The listing — the site's count, and a walk that stops one page early

```
GET /job-vacancies-search-ghana            «262 Job ads found» · 25 cards · pager ?page=1 … 10
fetch ?page=1 … 10 from the tab            25 × 9 + 12 = 237 distinct /job-vacancies-ghana/<slug>-<id> · page 11 → 0 cards   12:23:43 UTC
                                           **237 emitted, site states 262 — 25 short.**
card                                       title – city · employer · the first lines of the body
advertisement id                           the trailing number of the address (…-kumasi-255659)
```

**The counter says 262 and the pager exposes 237** — the gap is exactly
twenty-five, one page, and nothing on the pages says which twenty-five or
why. *Two readings fit and neither is established: the counter includes
advertisements the listing no longer shows (expired but still counted),
or the pager caps at ten pages and the eleventh is unreachable by
`?page=11` (which returned a page with no cards, not an error).* **Either
way the site's number is the anchor and 237 is what a reader can reach;
the adapter prints both and names the gap.**

## The advertisement

```
GET /job-vacancies-ghana/senior-health-safety-officer-kumasi-255659    200, 62 454 B
«Published on 11.09.2026» · Industries · Job category · City : Kumasi · Experience level : 5 to 10 years – more than 10 · body
no JSON-LD, no JobPosting
```

## The procedure a session follows — this is the adapter (decision of 2026-09-08)

1. guard `www.ghanajob.com` on `/job-vacancies-search-ghana` and on
   `/job-vacancies-ghana/…` before anything;
2. `navigate https://www.ghanajob.com/job-vacancies-search-ghana` in the
   session's own tab; read «N Job ads found» — **N is the site's count**;
3. from the tab, `fetch('/job-vacancies-search-ghana?page=P')` for P = 1,
   2, … until a page carries no card, 1.5 s apart; collect the distinct
   `/job-vacancies-ghana/<slug>-<id>` addresses; the id is the trailing
   number;
4. print **«n emitted, site states N — equal / k short»** — on the day,
   «237 emitted, site states 262 — 25 short»;
5. one advertisement page for the body when wanted (published date,
   city, industry, experience level in labelled lines; no JobPosting);
6. close the tab.

## What this card does not establish

- **Which 25 the counter counts and the pager does not** — not
  determinable from the pages; a sort or a filter (`?sort=`, region) was
  not exercised.
- **Whether the siblings behave the same** — this card reads one host;
  `algeriejob.md`, `3amal.md` and the others carry their own dated
  readings, and the family shares a template, not a verdict.
- **No script ships.** The route is a browser tab and fetches from it.
