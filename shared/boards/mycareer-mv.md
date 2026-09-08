# MyCareer — the Maldives government's employment service

<!-- verified: 2026-09-08 -->

<!-- hosts: mycareer.gov.mv, jobcenter.mv -->
<!-- script: mycareer.py -->
<!-- countries: MV -->
<!-- content: measured · 107 distinct live advertisements read by `mycareer.py list` from the site's own active filter in 13 pages, against about 12 570 in the unfiltered archive back to 2019-11-17 · 2026-09-08 -->
<!-- witness: served by the site — its home page states «&nbsp;109 Active Jobs&nbsp;» and its filtered paginator declares 13 pages. **Both are the same host**, so this corroborates the site with itself; the adapter's own walk returned 109 rows and 107 distinct addresses · 2026-09-08 -->
<!-- hosts-source: `jobcenter.mv`, named by the country page of 2026-09-03, redirects here · 2026-09-08 -->

**The country page of 2026-09-03 concluded this service did not exist.**

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/mycareer.py" list
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/mycareer.py" list --fetch --limit 20
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/mycareer.py" ad \
    --url https://mycareer.gov.mv/en/jobs/carpenter
```

## Two conclusions of that page are false, and neither was wrong when written

> *«&nbsp;Aucun site d'État maldivien lisible ne nomme de service d'emploi.&nbsp;»*
> *«&nbsp;`jobcenter.mv` … on ne saura pas ce qu'elle est.&nbsp;»*

```
2026-09-03   jobcenter.mv   allowed=False — «closes everything to User-agent: claudebot»
2026-09-08   jobcenter.mv   allowed=True, certain, group `*`
             and it REDIRECTS to mycareer.gov.mv — a .gov.mv host
```

**The host did not change. The rule did.** *On 2026-09-07 the repository's owner
decided that a refusal naming `ClaudeBot` does not bind `Claude-User`.* **The
door that was «&nbsp;the only way to know, and it is forbidden&nbsp;» opened, and
behind it was the service the page had looked for.** *Second host in two days
freed by that decision, after `jobsiniraq.github.io` — and both were found by
accident, because a country was being revisited for another reason.*

## Two quantities, and the site publishes both

```
/en/jobs                       1 397 pages   ~12 570   the archive, back to 2019-11-17
/en/jobs?filter[active]=1         13 pages       107   distinct live advertisements
home page counter                              109     «Active Jobs»
```

> **Counting the unfiltered listing would overstate the live Maldivian market by
> a factor of a hundred**, and nothing on the page says so, because both numbers
> are true of what they measure.

## The heuristic that looked right, and the two pages that broke it

**Each dead advertisement carries a `badge-expired` on its card, and the listing
is roughly newest-first**, so «&nbsp;read in order, stop at the first
badge&nbsp;» seems to follow:

```
page 1      VVVVVVVVV        page 12     XXXXVXXXX
page 2      VVVVVVVVV        page 13     VVXXXVVXX
page 700    XXXXXXXXX        page 1397   XXXXXXXX
```

**Live advertisements sit behind dead ones** — the order is by posting date and
expiry is a per-advertisement deadline, so the two do not agree. *Stopping at
the first badge ends on page 12 and loses the five live advertisements after
it.*

> **Pages 1 and 2 confirmed the heuristic, and they are adjacent — which is
> exactly why they were not a sample. Adjacency is the condition under which
> two different orderings coincide**, so a rule about ordering checked on
> neighbours is checked on nothing.

**The pages that refute it are 12 and 13**, and they were read because a
reviewer asked for spread pages rather than the next one.

## Why the site's own filter is trusted

**Exercised in both directions, 2026-09-08:**

```
filter[active]=1     9 cards   0 expired   7 shared with unfiltered page 1
filter[expired]=1    9 cards   9 expired   0 shared with either
```

**Zero overlap, and the inverse filter returns the complement it names.** *A
filter tested only on the side one wants is not tested.*

## The total agreed with the site and hid two duplicates

**The 13-page walk returns 109 rows and 107 distinct addresses**, and 109 is
exactly what the home page prints.

```
page 1, positions 8 and 9   =   page 2, positions 1 and 2
hr-officer-28 · admin-1     — same pair on two separate runs
```

**A step of seven inside a window of nine, at that one boundary**: no other
page pair in the thirteen repeats an address, and the *unfiltered* pages 1 and 2
share none at all. **So the agreement between our 109 and the site's 109 is not
a check — both may be counting the same rows twice.** *`mycareer.py` prints
`rows_read` and `found` side by side and names each duplicate with the pages it
came from, so a paginator drifting under a new posting stays distinguishable
from a board that lists one advertisement twice.*

## What the adapter reads, and what it costs

**Title, employer, town, salary and employment type all sit on the listing
card**, each counted one-per-card across pages 1, 2, 12, 13, 700 and 1397.
**So the whole live market costs 13 requests, not 109.**

- `employment_type` is **optional and known to be** — 3 of 8 cards on page 1397
  publish none, so its absence is the board's choice, not a defect;
- `--fetch` opens each advertisement for `posted` and `deadline`, which the card
  does not carry — *`carpenter` returns `2019-11-17 → 2019-12-17`, `expired`*;
- `--since` **refuses without `--fetch`** and exits 8: the dates are not on the
  card, and a filter that silently kept everything would be worse than none;
- `--archive` walks the 1 397 pages instead of the 13, and says so in its output.

**No `JobPosting` and no `ld+json` exist anywhere on this site**, so every field
is an HTML anchor and every missing required one is named on stderr.

## A correction, made the same night

**The first version of this card said the design question «&nbsp;was not
measured here&nbsp;», that it was «&nbsp;one request away&nbsp;», and that the
budget was why. All three were wrong**, and the answer cost no request at all:

| | first version, 04:30 | measured, 05:05 |
| :-- | :-- | :-- |
| status filter | unknown | **the site publishes one** — `filter[active]` |
| expiry read from | *«&nbsp;per advertisement&nbsp;»*, 12 570 fetches | **the listing card** |
| why unmeasured | *«&nbsp;the budget&nbsp;»* | **the files were already on disk**, at 14&nbsp;% / 52&nbsp;% |

**The three listings that answered it had been fetched an hour earlier to count
pages, and were on disk while the card called the question open.** *Second
instance of `la-donnee-etait-la-la-question-manquait`.*

## Access

`mycareer.gov.mv` answers `read` and permits `/`, `/en/jobs`, the paginated and
filtered forms, and the advertisement paths — `allowed=True`, `certain=True`,
group `*`, measured 2026-09-08. **`gov.mv` itself is `unreachable`** —
`allowed=None`, and an indeterminate is not sounded.

## What this card does not establish

- **nothing about the Dhivehi side** — `/dv` exists, permits, and was not read;
- **the 109 were not reconciled with the 107**: whether the site's counter
  double-counts the same pair, or counts something else, was not measured;
- **nothing about `presidency.gov.mv`**, which answers `unrecognised` with
  `certain=False`.
