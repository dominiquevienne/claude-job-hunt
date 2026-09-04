# Board adapter — job.am (Armenia)

<!-- verified: 2026-09-04 -->

<!-- hosts: job.am -->
<!-- script: jobam.py -->
<!-- countries: AM -->
<!-- content: measured · rolling window read in full, 15 of 15 randomly sampled pages parsed · 2026-09-04 -->

**Rank 1 in Armenia refuses us, so this is the country's readable market.**

```
jobam.py list --since 2026-08-20 --fetch
jobam.py ad --slug shinararutyun-78613
```

## The sitemap is a rolling thirty-day window, and that is not a size

```
https://job.am/sitemap/jobs.xml
  2026-09-04 22:38 UTC · 449 518 o · 1 185 <loc> · 1 185 distinct · 0 duplicates
  25 dates, 2026-08-06 → 2026-09-04 — exactly thirty calendar days
```

Another session read the same file at **20:46 UTC**: **1 231 entries over 26
dates, 2026-08-05 → 2026-09-04** — thirty-one days.

**Between the two readings the window rolled and took 2026-08-05 entire.**

**The day that fell carried 34, not the 47.4 an average day carries — and the
average describes nothing here.** The distribution is bimodal: twenty-two
working days hold 1 179 entries (36 to 85 each), and eight weekend days hold
six between them. A mean taken across both falls between the two populations
and resembles neither. *Comparing a gap of 46 to that mean was a summary
standing in for a value that was in the file.*

Aligning the two readings day by day: **34 from the window, seven more from
ordinary expiry on the three oldest surviving days**, and five unaccounted at
the time of writing. **The window explains most of the gap, not all of it**, and
advertisements also drop out from inside it.

**The signature distinguishes this from ordinary trading.** A board that gains
and loses advertisements changes its counts throughout; **a retention window
loses its oldest day whole.** So `1 185` is not the size of the board — it is
what the board keeps, and the adapter reports the window's bounds with the
count so the two are never confused.

**And there is no second file to check it against.** `hellojob.az` publishes
`vacancies` beside `expired-vacancies`, a closed partition whose total is
conserved when advertisements move between them — so any other cause breaks
the sum. Here `jobs`, `companies` and `blog` do not exchange members: **the
partition is open, the conservation argument is unavailable, and saying so is
part of the measurement rather than a caveat on it.**

## Fields, on fifteen advertisements drawn at random

| field | rate |
| :-- | :-- |
| title · employer · posted · valid_through · city · region | 15/15 |
| description | 15/15 |
| `baseSalary` | 0/15 — never present |

**Fifteen distinct employers on fifteen advertisements**, so the file is not one
poster's batch. The sample is `random.sample`: on `jobsbotswana.info` a
contiguous slice from the tail gave a rate two and a half times the truth.

**`employmentType` is Armenian free text, not the schema.org vocabulary** —
`Լրիվ դրույք` on fourteen, `Լրիվ դրույք, Կես դրույք` on one. It carries real
information in a vocabulary the field name does not promise, so it is emitted
as **`employment_type_text`**. A caller filtering on `FULL_TIME` would get
nothing and would not be told why.

*Three boards, three verdicts on one field in one night: `keejob` returns
`OTHER` on every advertisement and it is dropped; `jobsbotswana` returns the
real enum and it is emitted; here it is free text and it is renamed. **What a
field is worth is a property of the board, not of the schema.***

## A schema variant that only running found

`addressCountry` reads `"AM"` on some advertisements and
`{"@type": "Country", "name": …}` on others. Assuming the string form raised
`AttributeError` on the very first fetch. **The variant was in the data before
it was in the code** — which is the ordinary case, and the reason an adapter is
run rather than reasoned about.

## Access and cost

`robots.txt` reads, the host sweeps, 36 `Disallow` rules and none on the paths
used here — asked per path. `list` without `--fetch` costs one request; with it,
one per advertisement, bounded by `--since` and `--limit`.
