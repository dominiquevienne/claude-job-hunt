# Board measurement — Zangia (`www.zangia.mn`, Mongolia): the country's generalist, **7 945 adverts emitted on 2026-09-23 against the 7 945 it states**, ninety a page; `zangia.py` — the list page is a Next.js shell and the adverts come from the JSON its own bundle calls, whose envelope **restates its total as ZERO past the last page**

<!-- verified: 2026-09-23 -->

<!-- hosts: www.zangia.mn, zangia.mn, new-api.zangia.mn -->
<!-- script: zangia.py -->
<!-- countries: MN -->
<!-- content: measured · **`jobs --all` emitted 7 945 adverts over 89 pages of 90 against the 7 945 the board states — equal, and 7 945 distinct codes.** The list at `/job/list` is a Next.js App Router SHELL (47 512 B, no card, no count, an RSC payload carrying neither); the adverts come from `https://new-api.zangia.mn/api/jobs/search`, the axios `baseURL` carried in the fifty-four `_next/static` chunks — and the page's `preconnect` names `cdn.zangia.mn` and `lib.zangia.mn`, NEITHER of which answers the question. **Past the last page the envelope restates its total as ZERO**: page 89 of 89 answers 25 items and `meta.total: 7945`, page 90 answers none and `{"total": 0, "page": 0, "limit": 0, "totalPages": 0}` — so a walk that refreshes its witness each round ends holding zero and prints «7 945 emitted — the site states 0: 7 945 short», an exact walk accused of over-reading. The total is read on page ONE and never again. **A second witness PARTITIONS the board**: the ten job-level facets come to 93+3 127+454+2 676+255+938+171+128+66+37 = **7 945**, the stated total exactly, which says every advert carries exactly one level and that the total agrees with a decomposition computed apart from it (`zangia.py levels`). Read by the declared client, 2026-09-23 16:0x–17:0x UTC, the guard on each exact path: both hosts answer **404 on `/robots.txt`** — no file, so no rules, open and `certain: True`, no `Crawl-delay`. **84 of the 90 rows of page one carry the recruiter's telephone in `contact`** — dropped whole, never scrubbed into a placeholder; `lat`/`lng` pin a workplace more precisely than a street and are never read. The criteria the board prints about a PERSON (`age_requires` on 2 605 of the 7 945, `for_hbi`, `is_retired`) are not carried (#183), and its own facets give them back as QUESTIONS — `--type 45plus` 412, `--type disability` 11, `--type isRemote` 21, `--type part_time` 55. A walk of 89 requests met a connection reset on the 49th, so the rows are written as they are read and a cut walk keeps them and says it is short. Exercised: `jobs --all` → **7 945 emitted, the site states 7 945** ; `levels` → **7 945 = 7 945** · 2026-09-23 -->
<!-- witness: the envelope's own `meta.total` (7 945), AND — because a total that agrees with itself is not a check — the ten job-level counts, which sum to it exactly · 2026-09-23 -->
<!-- route: http · 7945 · 2026-09-23 -->

**Found by the Mongolia search of #603 (a country never searched), issue #660;
measured 2026-09-17, 2026-09-22 and 2026-09-23 by the declared client, the
guard on the exact path first.** The country's largest board by every account
read.

## The shell says nothing, and the bundle says everything

```
GET /job/list                          200, 47 512 B — no card, no count
                                       54 chunks, 31 __next_f.push, no advert data
the page preconnects to                cdn.zangia.mn, lib.zangia.mn
the data is at                         new-api.zangia.mn/api   <- named by neither
```

A `preconnect` names a host the page will open early. **It does not name the
host that holds the answer**, and following it here would have cost two
measurements on hosts that serve images and libraries.

## A 404 on a chunk is a stale hash, not a refusal

The route chunk named by a copy of the shell taken **2026-09-22 17:07 UTC** —
`page-3b033792772fb37e.js` — answered **404** on 2026-09-23, with and without
its parentheses percent-encoded. The shell re-read a minute later named
`page-c18b61710934368a.js`, which answered **200**: the site had redeployed
between the two reads.

> A bundle is addressed by a content hash, so **yesterday's copy of a page
> points at addresses that no longer exist** — and the 404 they earn is
> indistinguishable from a host that has closed its door.

Re-read the shell in the same session as the chunk.

## The total that turns to zero

```
page 89 of 89    25 items   meta.total 7945     <- the last real page
page 90          no item    {"total": 0, "page": 0, "limit": 0, "totalPages": 0}
```

Nothing in that envelope marks it as past-the-end: it has the shape of a real
one. **A walk that re-reads its witness each round therefore finishes holding
zero**, and the witness then accuses an exact walk of over-reading — the
failure mode is a red exit on a green measurement, which is the kind nobody
re-opens. The total and the last page are read on page one and never again,
and the guard `AnEnvelopeThatRestatesItsTotalAsZeroWhenItIsPastTheEnd` holds
it.

## The second witness, and why a partition is a proof

`meta.total` travels in the same answer as the adverts it counts: *a sum that
matches its source is not a check.* The ten job-level facets are a different
question, asked ten times:

```
1:93  2:3 127  3:454  4:2 676  5:255  6:938  7:171  8:128  9:66  10:37   = 7 945
the board states                                                           7 945
```

**Landing exactly on an independently stated total is what makes it a proof
and not a coincidence.** It says every advert carries exactly one level — none
counted twice, none without one — and that the total is not a stored claim.
An excess would mean the facets overlap; a shortfall, that some adverts carry
no level, and then the walk and the total would be counting different
populations. `zangia.py levels` prints the ten and exits 6 with the gap named
in either direction.

## The loss this walk cannot prevent, and how it becomes visible

The list is ordered by `sort_time`, which is **not** the posting date (`time`
is): it moves when an employer raises an advert. One raised in the middle of a
nine-minute walk jumps to page one, behind the reader, and pushes an unread
advert across a page boundary. **Nothing in the answer says so.** The dedup by
`code` stops it being counted twice, and the emitted-against-stated line is
what makes the loss visible — which is why that line is printed even on a
bounded read. On 2026-09-23 the walk lost none: 7 945 distinct codes.

## What is never emitted

| field | why |
| :-- | :-- |
| `contact` | **the recruiter's telephone, on 84 of 90 rows of page one** — dropped whole, not masked |
| `lat`, `lng` | they pin a workplace more precisely than a street |
| `logo` | the employer's mark |
| `id`, `company_id`, `profession_id`, `addr_id`, … | the board's internal identifiers |
| `hits`, `applies`, `shares` | the board's own traffic counters |
| `age_requires`, `for_hbi`, `is_retired` | criteria about a PERSON (#183) — asked for by facet instead |

The telephone pattern takes the three shapes the board's own column holds — a
mobile (`99112233`), an Ulaanbaatar landline (`11317798`), a service line
(`1800-1600`) — and leaves the pay: **opening its first digit to `[1-9]` eats
`12000000`, a salary in tugriks**, and the mutation bench names that value when
it does.

And because the two routes do not carry the same keys — the search answer holds
all three criteria, `/api/jobs/<code>` holds only `for_hbi` — an **absent** key
goes in `criteria_unknown` rather than letting `criteria_withheld: []` say *the
board prints no criterion here* when the truth is *this route does not say*.
That is #885 turned around: there a row claimed a withholding that never
happened; here an empty list would claim a knowledge nobody has.

## Invocation

```
zangia.py jobs [--pages N | --all] [--type T] [--query Q] [--from FILE]
zangia.py ad --url https://www.zangia.mn/job/_<code> | --code <code>
zangia.py types
zangia.py levels
```

The advert address carries an **underscore** — `/job/_1jd5q7pvwy`, read out of
the bundle (`href:"/job/_".concat(t.code)`) — and `ad` refuses an address
without it. `limit` is honoured beyond the client's own (200 answers 200, 40
pages), and the walk asks 90 all the same: the value the site's own page sends.
