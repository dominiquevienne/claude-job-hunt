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

## Why no adapter tonight

**No `JobPosting`, no `ld+json` at all** — so HTML anchors, as on
`zaposli.me`. **And the useful set is 109 of about 12 570**, so an adapter must
either find a status filter or read the `Expired` marker per advertisement:
*reading the whole listing to keep 0.9 % of it is not a design, and which of the
two it should be was not measured here.*

**That is the open question, and it is one request away** — *whether `/en/jobs`
accepts a status parameter.* It was not asked because the budget that remained
was better spent stating what is established than starting what would not
finish.

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
