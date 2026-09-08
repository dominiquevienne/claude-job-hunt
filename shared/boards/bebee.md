# Board adapter — beBee (a platform, and jobs are one section of six)

<!-- verified: 2026-09-08 -->

<!-- hosts: bebee.com -->
<!-- script: bebee.py -->
<!-- countries: CH -->
<!-- content: measured · the sitemap index `robots.txt` declares moved from 3 407 children and 2 102 job files in the morning to 3 799 and 2 494 in the afternoon of the same day — **this index moves within a day**, so a single reading of it is a moment and not a size; the Swiss country held 9 numbered files carrying 432 533 addresses under `/ch/jobs/` (8 x 50 000 + 32 533) spanning 2026-03-27 to 2026-09-07, and its `delta-` files went from 4 to 10 across the same day · 2026-09-08 -->
<!-- witness: none — nothing was fetched beyond the homepage and `robots.txt`, and the homepage carries no inventory to corroborate -->

**This is not a job board. It is a platform whose navigation names six
products, and jobs are one of them.**

```
/ch/jobs        /ch/people       /ch/services
/ch/academy     /ch/cv-builder   /ch/blog
```

**`countries:` lists the sections its own navigation names** — `/ch`, `/es`,
`/gb`, `/fr`, `/de`, `/pt`, `/it`. *That is what the page declares, not a
measurement of where its advertisements are.*

## Why it is `indeterminate` and not `open`

**It answers `200` and serves half a megabyte, and that is nearly all
application code.** *104 links in 575 457 bytes, no `__NEXT_DATA__`, **zero
`JobPosting`**, one `Organization` in `ld+json` and nothing else.*

> **A title that says "Jobs" is not an advertisement, and a count of links is
> not a count of advertisements.**

**The share of the site that is job advertisements is not measurable from this
body**, and this card does not estimate it. *Reading `/ch/jobs` would be a
second measurement, and it has not been made.*

**Its `robots.txt` names `ClaudeBot` at `Disallow: /` and never names
`Claude-User`**, which the `*` group leaves open — so the transport serves us.
**It was filed for two days in a population of nineteen said to "refuse at
transport". It never refused.**

## `/ch/people` is a directory of persons, and it is not read

**Nothing here enumerates people, and nothing should.**

> **"The rules permit it" is not a reason to read something.**

*This repository has left candidate sitemaps unread on `jobs.am`, `busy.az`,
`afriqueemplois` and the fabricated network's nodes for the same reason.* **A
platform that carries advertisements beside profiles does not turn its profiles
into fair game because its advertisements are fair game.**

## What would change this card

**One reading of `/ch/jobs`** — enough to say whether advertisements are
enumerable there, and how many. **Until that is done, `beBee` is neither
disqualified nor qualifiable**, and it must not be counted as coverage for any
of the seven countries above.

*The distinction this repository keeps: `jobstore.md` is refused,
`tanqeeb.md` is unreadable at the rules layer, `portaljob-madagascar.md`
serves an empty shell, and this one serves a real site whose job share nobody
has measured. Four different facts that a single "no" would flatten.*

## The advertisements were in the sitemap index all along — 2026-09-08

**This card said `indeterminate` because the markup carried no enumerable
list.** *That was true of the markup, and it was read as a statement about the
board.* **`robots.txt` declares `Sitemap: https://bebee.com/sitemaps`, and that
index is the list.**

```
/sitemaps                     3 407 children
   /sitemaps/jobs/            2 102 files over 99 countries   us 1185 · de 76 · ca 66 · fr 54 · ch 13
/sitemaps/jobs/ch             50 000 <loc>, all under /ch/jobs/
/sitemaps/jobs/ch/9           32 533 <loc>          intersection with file 1: 0
```

**Guard taken on each path: `allowed=True`, `certain=True`.**

> **And the asymmetry matters: the paginated search is closed and the sitemap
> is not.** `robots.txt` refuses `/*?*page=`, `/*?*q=`, `/*?*sort=` and
> `/*?*location=`. *A refusal on one path is not a refusal on the host* — the
> mirror of `un-403-sur-un-sitemap-nest-pas-un-board-ferme`.

## What the addresses are, checked and not assumed

**Three sampled from the Swiss file, spread across it, all three real:**

```
datePosted 2026-09-07  validThrough 2026-11-13  addressCountry "CH"   Aarau
datePosted 2026-09-03  validThrough 2026-11-02  addressCountry "CH"   IOM
                                                                      Zollikon/ZH
```

**Two `JobPosting` blocks per page, `validThrough` in the future, and
`<lastmod>` equal to `datePosted` on 2 of 2** — so the sitemap date is the
posting date on this board and not a regeneration stamp.

## The number is real and it is NOT a count of Swiss vacancies

```
file 1   2026-09-02 .. 09-07   50 000 addresses over SIX days
file 9   2026-03-27 .. 07-15   32 533, the tail
```

**Fifty thousand in six days is about 8 300 a day for Switzerland**, and the
whole set spans five and a half months. **No Swiss labour market produces
that.**

> **BeBee is an aggregator: it republishes other boards' postings.** *The first
> address sampled names `Equal.Jobs` — itself a Swiss board — as the source.*
> **So 432 533 counts republished postings, not distinct vacancies, and the
> duplicate rate against the origin boards was not measured here.**

**This card therefore publishes the address count and refuses the market
reading.** *`un-compte-de-loc-nest-pas-un-compte-dannonces`, on the largest
figure this repository has met — and a large number attracts no suspicion,
which is exactly why it needed one.*

## What is still not established

- **the duplicate rate against origin boards** — the one measurement that would
  turn 432 533 into a market figure, and it needs the origin boards;
- **the four `delta-` files** beside the nine numbered ones were not read;
- **the other 98 countries** were not opened; `us` alone declares 1 185 files;
- **no adapter.** *The route is now known and permitted, which is the whole
  change here.*

## Built 2026-09-08 — `bebee.py`

```bash
S=skills/job-scan/scripts/bebee.py
python3 $S countries                              # 2 494 job files over 99 countries
python3 $S list --country ch --limit 5            # one file, no total claimed
python3 $S list --country ch --limit 3 --fetch    # with dates, locality, poster
python3 $S ad --url https://bebee.com/ch/jobs/<slug>
```

**Plain HTTP — no key, no cookie, no browser.** *The route is the sitemap index
`robots.txt` declares, and the paginated search stays closed: `/*?*page=`,
`/*?*q=`, `/*?*sort=` and `/*?*location=` are disallowed and this adapter never
reaches for them.*

### The anchor is the file's own length, printed beside our count

```
50000 <loc> in this file: 50000 advertisement(s)
```

**The left number is counted before anything is parsed.** *No empty board and
no broken reader can produce that sentence with a number on both sides* — the
form issue #181 asks for, and the same one `ihararejobs` prints.

**And no total is ever claimed from a bounded run.** *Reading one file of nine
prints «&nbsp;1 of 9 numbered files read on purpose — no total for `ch` is
claimed by this run&nbsp;»*, because a partial walk does not answer «&nbsp;how
many are there&nbsp;».

### The `--limit` ceiling is the caller's, not a shortfall

*The first version printed «&nbsp;5 distinct&nbsp;» against 50 000 `<loc>` when
`--limit 5` was on — a ceiling the caller asked for, reading as a catastrophic
gap.* **The summary is now computed before the truncation, and the limit says
so on its own line.** `rocken.py` carried the same defect for one commit.

### The poster is sometimes the origin BOARD

```
Equal.Jobs                     <- a Swiss job board, republished here
MAAG Group                     <- a real employer
GWG Gemeinnützige Wohnbau…     <- a real employer
```

**Three advertisements, and the field means two different things.** *So it is
emitted as `poster` and never as `employer`* — the same conclusion `rocken.md`
and `jobeo-ch.md` reach from opposite specimens.

### The index moves, and the delta files are counted rather than merged

```
2026-09-08 morning   3 407 <loc> in the index · 2 102 job files · ch: 9 + 4 delta
2026-09-08 afternoon 3 799 <loc>              · 2 494 job files · ch: 9 + 10 delta
```

**The `delta-` files are incremental updates and this adapter does NOT read
them**, but it counts them and prints the count. *Merging them silently would
make a run's denominator unreproducible.*

### Still not established, and not guessed

- **the duplicate rate against the origin boards.** *`Equal.Jobs` appearing as a
  poster is the reason the question exists.* **A duplicate is established by
  employer, title and city together — never by a date two publishers set
  separately** — and this adapter neither measures nor assumes it;
- **`countries: CH`** because Switzerland is the only country exercised. *The
  index declares 99, `us` alone holds 1 191 files, and none was read.*
