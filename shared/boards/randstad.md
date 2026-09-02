# Board adapter — randstad.ch

<!-- verified: 2026-09-02 -->

**Re-verified 2026-09-02**: **1 068 ads over 36 pages**, against the 1 059 recorded on 2026-08-29 — the page count is unchanged and the board drifted by nine.

A staffing **agency** board, like `michaelpage.md`, `fachkraft.md` and
`persigo.md`: `hiringOrganization` is *Randstad* and **the client employer is
never named**.

Server-rendered HTML. **No key, no cookie, no browser.**

Read by `skills/job-scan/scripts/randstad.py`.

**Verified 2026-08-29**: 33 pages walked, **985 unique ads, zero duplicates
across pages**.

## Pagination is a path segment, and that is why this went unbuilt

```
https://www.randstad.ch/jobs/page-2/     ← works, 30 ads
https://www.randstad.ch/jobs/?page=2     ← returns page 1, verbatim
```

The query-parameter form does not fail: it **silently serves page 1**. A first
investigation concluded "there is no pagination" from exactly that, and the
board sat on the shelf for it. The links are in the listing's own markup —
`/jobs/page-2/` through `/jobs/page-20/` — and reading them settles it in one
look.

## There is no end marker either

Past the last page the site serves **page 1 again**: HTTP `200`, a full set of
30 cards, no 404 and no empty page. `page-50` and `page-200` both returned
page 1's exact ad set.

**So the stop condition is "this page is page 1"**, which is what `list` uses —
it compares each page's id set against the first and stops when they match. The
`--max-pages` flag is a safety budget, not the board size.

Measured: **33 real pages, the 33rd partial at 25 ads, 985 unique in total**,
and `page-34` was the first repeat.

## The structured data is missing exactly where Romandie is

A `JobPosting` block is on **some** ads and not others, and on the 12 sampled the
split followed the region without exception:

| Region | `JobPosting` |
| :-- | :-- |
| Rorschach, Dietikon, Luzern, Hägendorf, St. Gallen, Basel, Olten ×2 | **8 of 8 have it** |
| Les Acacias, Genf ×3 | **4 of 4 lack it** |

So on this board the block **tracks the region, not the ad's state** — and it is
absent precisely where a Romandie user is looking. Two consequences:

- **`check` never uses it.** The `410` is the test (see below); a missing block
  is reported as `has_jobposting: false` and explicitly called *not a signal*.
- **`ad` does not need it.** The description comes from
  `data-locator-id="jobdetails_description_jobdescription"`, which is present on
  every ad, and the title falls back to `<title>` split on `" Job in "`.

`validThrough` therefore exists only on the ads that carry the block.

## Traps

**1. The id is a UUID, not a number.** The path is `<slug>_<city>_<uuid>`; a
pattern ending in `_\d+` matches nothing and reads as an empty listing. **The
UUID alone rebuilds the URL** — `/jobs/<uuid>/` redirects to the canonical slug —
so it is the ledger key:

```
randstad:<uuid>       e.g. randstad:aefa6056-8e23-4d6d-b22e-d2b4c9ef9047
```

**2. Each ad appears twice per card**, once on the title link and once on the
button. Deduplicate on the id, not on the number of links.

**3. The description container must be bounded.** An unbounded slice from
`jobdetails_description_jobdescription` runs into the neighbouring sections and
returns **17 000 characters** of page furniture as "the ad"; stopping at
`jobdetails_description_jobdetailsaccordions` gives the real 800–1 600.

**4. Gone is `410`, not `404`** — as on `fachkraft.md`. A 404-only check treats a
dead ad as unreachable rather than closed.

## Is it still open?

| Response | Reading |
| :-- | :-- |
| `200` | **Listed** — whether or not a `JobPosting` block is there |
| `410` | **Not listed** |

## Applying

Through the agency, and through a consultant. The plugin does not create
accounts and does not fill credential fields — hand the user the ad URL and
their documents, and tell them the employer's identity usually arrives only
after contact.

## Pace

A full walk is 33 requests. `--with-detail` adds one per kept ad, so filter with
`--search` and `--place` first — the listing card already carries a 600-character
teaser to filter on.
