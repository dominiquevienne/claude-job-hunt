# Board measurement — Wazifaha (`www.wazifaha.org`, Afghanistan): «Hire & Find Jobs» — **272 adverts emitted against the 272 the list states, over the 16 pages its pager bounds, the last carrying exactly the 2 the arithmetic predicted**; `wazifaha.py` — Afghanistan's first generalist, and the board **clamps past its last page**

<!-- verified: 2026-09-23 -->

<!-- hosts: www.wazifaha.org -->
<!-- script: wazifaha.py -->
<!-- countries: AF -->
<!-- route: http · 272 · 2026-09-23 -->
<!-- content: measured · **272 emitted over 16 pages of 18 against the «Showing 272 active jobs» the list states — they agree, and 272 = 15 × 18 + 2 with the last page carrying 2, tested before a line was written**. `/jobs/` 200 ×2 (168 540 B), 18 cards; `?page=16` 200 (112 438 B) 2 cards; **`?page=17` 200 with the SAME two ids — the site clamps, so a walk that stops on an empty page never terminates**; one advert 200 (95 175 B) with a labelled grid (contract, salary «Competitive», closing date, gender). 118 employers, Kabul 138, Multi Locations 39, Nangarhar 22; 71 adverts state a number of vacancies; **177 of the 272 cards print a gender, never carried (#183)**; 56 employer names are the site's own truncation. Rules open and certain, no Crawl-delay. Exercised 2026-09-23: `jobs --country-code AF` → **272 emitted, they agree, 0 contact leak** · 2026-09-23 -->
<!-- witness: the list's own «Showing 272 active jobs» AND the pager's largest page read on page 1, checked against the rows and against the last page's fill on every unfiltered run · 2026-09-23 -->

**Found by the Afghanistan search of #613 (the private boards beside
`jobs.af`, which the country page already carries), measured 2026-09-17
13:38–13:39 UTC by the declared client, the guard on the exact path first,
`bin/fetch-body.py`, two reads.** The method is written on #613: two
searches (the NGO coordination body's portal, which the first Afghan
portal grew from; and the portals the engine returns by name), no composed
host names. *A measurement, not an adapter.*

```
_robots.allowed('www.wazifaha.org', '/')   open, certain
GET https://www.wazifaha.org/               200 ×2 — the front, /jobs/, /jobs-by-location/<city>, /companies/<slug>
```

The list `/jobs/`, its pager and the ad are the adapter's first line.

## The adapter, 2026-09-24 (measured 2026-09-23)

```
wazifaha.py jobs [--location SLUG] [--since-days N] [--details] [--country-code AF] [--max-pages N]
wazifaha.py locations
```

**272 emitted against the 272 the list states**, over 16 pages of 18, the last
carrying **2** — and 272 = 15 × 18 + 2, so the total, the pager and the fill
agree. The last page's fill was predicted and then checked, before the adapter
was written.

### The board clamps past its last page

`?page=17` answers **200 with page 16's two adverts, the same ids**. *A walk
that stops on an empty page never terminates here*, and one that stops on «a
round without novelty» is right for the wrong reason — it would stop the same
way on a cache, or a filter lost in flight. So the walk is bounded by the
pager's largest number, read on page 1, **and** a repeated page ends it, and the
run says **which of the two fired**.

> **This is the second new shape of the #894 family found in two days, and it is
> the opposite of the first.** Here the board **repeats for ever**, so a walk
> waiting for emptiness never returns. On `e-estekhdam.com`, measured by the
> pages session on 2026-09-23, the pager **crushes**: pages 100, 500 and 5 000
> are identical to the byte, so «nothing new» returns a **round, false number**
> and presents the server's ceiling as the board. *One never returns, the other
> returns a lie.* The rule that survives both: **stop when a page repeats the
> one before it, and say that it repeated** — never present the stopping point
> as the board's end unless something the site states agrees.

### Counted by container, and read by what the site marks

Page 1 carries **eighteen cards and forty-eight distinct advert addresses** —
the sidebar links adverts too. *Counting hrefs would have given 48 against a
stated 272 and a pager of 16, and the three figures would have disagreed for a
reason that has nothing to do with the board.*

**And each card prints its employer twice, with two different truncations** —
«Rahmanzai Logistic, Trading, …» for the narrow screen, «Rahmanzai Logistic,
Trading, Construction, A…» for the wide one. De-duplication kept both, which
slid the province one place along and put a truncated organisation where
«Kabul» belonged, **on 24 of 272 rows**. The place is now the meta item bearing
`fa-location-dot`, the employer the company link's **longest** text, and the
title the `wz-job-name` link — *nothing is taken from where it falls.*

**The name is the site's own truncation on 56 rows** (`employer_truncated:
true`); the full one is recoverable from the company slug, which the record
carries. Saying the name is cut costs nothing and pretending it is whole costs a
reader.

### The criterion follows the object read

**177 of the 272 cards print a gender**, and the advert prints one too. The
repository serves the advert and does not propagate the criterion (#183);
`criteria_withheld: ["gender"]` appears **where the object read carried one** and
`[]` where it did not (#885). *The first draft of this adapter asserted that no
card printed one — a claim made from the two cards its author had looked at, and
false on two thirds of the board.*

**The salary is a labelled field and the telephone rule never touches it** — not
because the afghani is small (the advert read says «Competitive», and whether
any advert prints a figure is not established) but because the lesson of
`myjobsmm.py` the day before generalises: *a rule written for free text does not
belong on a field whose meaning is known.* There it destroyed 113 of 115
salaries; here it was never given the chance.

**WITHHELD:** e-mail addresses everywhere, telephone numbers in free text at nine
digits, `contacts_withheld` on every record, **0 leaks measured on the 272**. The
advert pages are read only with `--details` — 272 requests is a choice, not a
default — and `/accounts/`, `/login`, `/top-up` are refused before the gate.
