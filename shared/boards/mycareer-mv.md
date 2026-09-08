# Assessed, adapter not built — MyCareer (Maldives, government)

<!-- verified: 2026-09-08 -->

<!-- hosts: mycareer.gov.mv, jobcenter.mv -->
<!-- script: none -->
<!-- countries: MV -->
<!-- content: measured · about 12 570 advertisements listed at `/en/jobs`, 9 a page over 1 397 pages, reaching back to 2019-11-17; the site states 109 ACTIVE and the two numbers are different quantities · 2026-09-08 -->
<!-- witness: served by the site — its home page states «&nbsp;109 Active Jobs&nbsp;», «&nbsp;4 655 Employers&nbsp;», «&nbsp;63 298 Registered Users&nbsp;». **Both figures come from the same host**, so this corroborates the site with itself · 2026-09-08 -->
<!-- hosts-source: `jobcenter.mv`, named by the country page of 2026-09-03, redirects here · 2026-09-08 -->

**The Maldives' government employment service, and the country page of
2026-09-03 concluded it did not exist.**

## Two conclusions of that page are now false, and neither was wrong when written

> *«&nbsp;Aucun site d'État maldivien lisible ne nomme de service d'emploi.&nbsp;»*
> *«&nbsp;`jobcenter.mv` … on ne saura pas ce qu'elle est.&nbsp;»*

```
2026-09-03   jobcenter.mv   allowed=False — «closes everything to User-agent: claudebot»
2026-09-08   jobcenter.mv   allowed=True, certain, group `*`
             and it REDIRECTS to mycareer.gov.mv — a .gov.mv host
```

**The host did not change. The rule did.** *On 2026-09-07 the repository's owner
decided that a refusal naming `ClaudeBot` does not bind `Claude-User`: they are
two tokens, and the group naming the first does not apply to the second.*

**So the door that was «&nbsp;the only way to know, and it is forbidden&nbsp;»
opened**, and behind it is the state service the page had looked for. *The
second host was discoverable the moment the first was fetched — the guard names
it in its own reason: «&nbsp;these rules were read from `mycareer.gov.mv`, not
from `jobcenter.mv`&nbsp;».*

**This is the second host in two days freed by that decision**, after
`jobsiniraq.github.io` on 2026-09-08. *Neither was re-measured because anything
was suspected: both came up because a country was revisited.*

## Two numbers, and the site publishes both

```
the listing   9 ads a page x 1 397 pages ~= 12 570   back to 2019-11-17
the home page                            109 ACTIVE
```

**The listing is the archive; 109 is the current stock.** *And the pages carry
the difference explicitly:*

```
/en/jobs/accountant-80   Published 7 September 2026    no marker
/en/jobs/carpenter       Published 17 November 2019    EXPIRED
```

> **A count of listed advertisements here would overstate the live market by a
> factor of a hundred**, and the paginator is honest — page 1397 serves eight
> real advertisements, none shared with page 1.

*This is the stock-and-flow inversion this repository already records, with the
unusual feature that **the publisher states both quantities itself**.*

## Why no adapter tonight — and a correction, made the same night

**The first version of this card said the design choice «&nbsp;was not measured
here&nbsp;», that the open question was «&nbsp;one request away&nbsp;», and that it
was not asked because the budget was better spent elsewhere. All three were
wrong**, and the correction cost no request at all:

| | first version, 2026-09-08 04:30 | corrected, 2026-09-08 05:05 |
| :-- | :-- | :-- |
| the status filter | *«&nbsp;whether `/en/jobs` accepts a status parameter&nbsp;»*, unknown | **the site publishes one** — `chk-filter-expired`, a checkbox in the listing's own filter panel |
| where expiry is read | *«&nbsp;per advertisement&nbsp;»*, so 12 570 fetches | **from the listing** — `<span class="badge badge-expired">` sits on the card of each expired advertisement |
| why it wasn't measured | *«&nbsp;the budget that remained&nbsp;»* | **the files were already on disk**, and the budget was 14&nbsp;% / 52&nbsp;% |

**The reason matters more than the fact: nothing new was fetched.** *The three
listings that answered the question had been fetched an hour earlier to count
pages, and were sitting in the scratchpad while the card declared the question
open.* **A held file answers no question you do not put to it** —
`la-donnee-etait-la-la-question-manquait`, and this is the second instance.

## What the listing actually gives

```
page 1      9 advertisements   0 expiry badges
page 2      9 advertisements   0 expiry badges
page 1397   8 advertisements   8 expiry badges     <- all of them
```

**Negative control, on the two advertisement pages** — the badge pattern must
find nothing on a live advertisement and something on a dead one:

```
/en/jobs/accountant-80   published 2026-09-07   badge x0
/en/jobs/carpenter       published 2019-11-17   badge x1
```

**So the listing is newest-first and carries the status itself.** *An adapter
reads pages in order and stops at the first badge — about 12 pages for the 109
active advertisements, not 1 397.* **That is a small adapter, and this card was
wrong to imply otherwise.**

**It is still not built.** *Anchors, not `ld+json` — there is no `JobPosting`
anywhere on this site — and the four anchors have not been counted unique on
three pages, which is what this repository requires of an HTML adapter before
one is written.* **That is the remaining work, and it is measurement, not
design.**

## Access

`mycareer.gov.mv` answers `read` and permits `/`, `/en/jobs`, `/en/jobs?page=N`
and the advertisement paths — `allowed=True`, `certain=True`, group `*`,
measured 2026-09-08. **`gov.mv` itself remains unreachable** — `allowed=None`,
connection refused, and an indeterminate is not sounded.

## What this card does not establish

- **the 109 were not enumerated**, and no advertisement was counted as active
  other than by the absence of an `Expired` marker on one page;
- **nothing about the Dhivehi side** — `/dv` exists, permits, and was not read;
- **nothing about `presidency.gov.mv`**, which answers `unrecognised` with
  `certain=False`, and whose 2026-09-03 reading found no employment link.
