# Board adapter — Mero Rojgari (Nepal)

<!-- verified: 2026-09-07 -->

<!-- hosts: merorojgari.com -->
<!-- host-forms: merorojgari.com -->
<!-- host-forms-basis: read — `merorojgari.py:BASE` is a literal and the nine children are numbered from it, no host substituted · 2026-09-07 -->
<!-- script: merorojgari.py -->
<!-- countries: NP -->
<!-- content: measured · 583 advertisements counted in 3 of the 9 `job_listing-sitemap*.xml` (200 + 200 + 183), all 583 under `/job/`; on a sample spread across the files, 3 of 3 that carry a `JobPosting` are LIVE and 1 of 4 carries none · 2026-09-07 -->
<!-- witness: none found — the site serves no total, and the index's nine files carry a `lastmod` that is EARLIER than the advertisements they list · 2026-09-07 -->

**Nepal's largest listing, and the third of its four boards to get an adapter.**

*The country page of 2026-09-04 calls it an archive of 1 766. That figure is not
re-counted here and does not appear in this card's `content:` line, which
carries only what was measured on 2026-09-07.*

## "Archive" is a description, and the measurement refutes it

**Every one of the nine `job_listing-sitemap*.xml` carries `lastmod
2026-07-20` — forty-nine days before this card — and the entries inside stop
there too.** *That reads as a board that died in July.*

**It did not.** Four advertisements sampled **across** the files:

```
file 1, entry 0     posted 2026-07-31   validThrough 2026-11-28   LIVE
file 1, entry 150   posted 2026-07-21   validThrough 2026-11-18   LIVE
file 5, entry 100   posted 2026-05-31   validThrough 2026-09-28   LIVE
file 9, entry 90    no `JobPosting` at all, on 98 591 characters of text
```

**And `--file 1 --fetch --live --limit 4` keeps 4 of 4, expiring in late
November.**

> **The sitemap stopped regenerating and the advertisements did not stop
> living. The stock and the flow classify in opposite directions here.**

**Every advertisement is posted LATER than the sitemap entry that lists it** —
2026-07-31 under an entry dated 2026-07-20. *So `--since` refuses without
`--fetch`: filtering on the listing would drop advertisements that qualify.*

**One of the four carries no `JobPosting`.** *Those are counted and reported,
never dropped in silence — a number that quietly drops a quarter is
indistinguishable from one that had nothing to drop.*

## The path decides, as on both neighbours

```
advertisements   /job/<slug>/    200 of 200 · 200 of 200 · 183 of 183
```

**Neither the filename nor the `lastmod` was trusted.** *`merojob.md` records
why a filename is not a predicate — its tender file is a sibling of its jobs
file — and why `lastmod` does not generalise: there it separates facets from
content but not tenders from jobs, since both regenerate. Here it does not even
separate the ad from its own listing. **The path has now decided on three
Nepali boards out of three.***

## Nine files, date-windowed, newest first

```
file 1   2026-07-17 -> 2026-07-20      file 5   2026-05-24 -> 2026-05-27
file 9   2026-04-21 -> 2026-04-24
```

**`--file N` reads one window**, so the recent end is reachable without opening
1 766 pages — *about half an hour at one second apart, and the adapter says so
before it starts.*

**`--limit` takes the head of what was selected**, which is the newest inside
file 1 and the oldest inside file 9. *It warns on every run: on `merojob.com`
the same flag returned five expired advertisements and made a live board look
dead.*

## What this card does not establish

- **the total was not counted.** *583 in three files of nine; 1 766 is the
  figure the country page of 2026-09-04 carries and it is not re-measured here.*
- **no rate.** *The live/expired split is 3 of 3 and then 4 of 4 on the most
  recent window — a sample, not a census, and the head of file 1 is its best
  case by construction.*
- **nothing about the fourth Nepali board.** *`jobsnepal.com` REFUSES as of
  2026-09-07 — `allowed=False`, `certain`.*
