# Board adapter — HiringCafe

<!-- verified: 2026-09-02 -->

<!-- hosts: hiringcafe.com -->
A **meta-board**: HiringCafe crawls employer career pages across some forty ATS
platforms and republishes them under one search. Worldwide — every country
tested returned local ads (see *Coverage*, below).

**Everything here was verified against the live site on 2026-08-27.** Field
names and enum values rot; re-check before trusting an old note.

**It is not an aggregator in the sense `shared/pipeline-format.md` blocklists.**
Repost farms recycle titles, name no employer and lead nowhere. Every card here
names the employer, carries the ATS it came from and links to that employer's
own application page. **Do not discard these ads as aggregator noise** — they
are employer postings, reached through a different door.

## What makes it different from every other adapter

**It needs no browser.** The `/api/search-jobs` endpoint answers 401, but the
page is server-rendered: the whole result set sits in `__NEXT_DATA__`. So the
adapter is plain HTTP — no Chrome extension, no login, no anti-bot challenge
seen. It is the only sweep that still works when the extension is missing.

Use the script, not hand-rolled requests:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/hiringcafe.py" \
  search --country CH --posted-within week --sort date --pages 3
```

Resolve the interpreter the portable way (`for c in python3 python py; do …`,
see `shared/portability.md`) — the script imports nothing outside the standard
library, on purpose.


## `countries` is not a place of work

**It lists the jurisdictions an employer is willing to hire from**, and on a
remote ad that is **6.5 of them on average** against 1.9 on the rest. It is not
where the work happens, and it is not even where the employer is.

Measured on 200 Ghanaian cards, 2026-09-02 — of the 71 carrying a Gulf state
in `countries`:

| | |
| :-- | --: |
| also carrying a Gulf **city** | **2 of 71 — 3%** |
| carrying **no city at all** | 45 |
| remote | 66 of 71 — **93%** |
| their actual cities | London 4 · San Francisco 4 · New York 3 · Singapore 3 |

Recomputed on `cities` instead, the gap reaches a factor of thirty: Ghana 30%
against **1%**, Tanzania 29% against **1%**, Nigeria 24% against **0%**.

**The risk is not missing an ad — it is presenting one as local when it is
not.** A remote ad open to six jurisdictions including Switzerland **is** worth
finding; that is what this plugin is for. It is simply not a Swiss job, and
**the commute rule has nothing to apply to.**

**What the code does today, checked rather than assumed (2026-09-02):**
`hiringcafe.py` emits `cities` and `countries` as separate raw fields, **the
city filter reads `cities` alone** — a card with an empty `cities` is dropped
by a city filter rather than matched on its country — and **nothing in
`shared/scoring-rubric.md` or either SKILL scores on `countries`.** So this is
a documentation fix, not a code one.

**What it needs from a reader is one distinction**: a card with a country list
and **no city** is *"remote, open to your country"*, never *"a job in your
country"*. They are two different results and confusing them is what produced
the error. Caveat 7 already says the right thing for `cities`; **it matters
more here, because 63% of these cards have no city to fall back on.**

*(A second property, of the instrument rather than the field: these cards are
largely **the same cards** from one country to the next — 68 of the 71 Ghanaian
ones appear in the Tanzanian sample, 65 in the Ugandan. **The thinner a market's
own data, the more of the answer is non-local ads.** So on a small market the
volume returned does not say what is covered; the number of cards carrying a
city in that country does.)*

## Configuration

```yaml
boards:
  hiringcafe:
    enabled: true
    country: "CH"            # ISO-2. Required.
    # Optional, and only as a complete set — see the city trap below:
    city: "Lausanne"
    region: "Vaud"           # canton / state / département
    lat: 46.5197
    lon: 6.6323
    radius: 25
    radius_unit: "miles"     # or "kilometers"
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `country` | yes | **ISO-2 code**, not a name. `CH`, `FR`, `DE` |
| `city` | no | Only with `region`, `lat` and `lon`. Any one missing → **0 results, no error** |
| `region` | with `city` | The `administrative_area_level_1` name |
| `lat` / `lon` | with `city` | The site has no public geocoder, so coordinates are stored once at setup, not looked up per scan |
| `radius` | no | Default 25 |
| `radius_unit` | no | `miles` (default) or `kilometers` |

Ask for the city coordinates at `/job-setup` time, once, and write them down.
**Never invent them**: wrong coordinates return a plausible result set centred
on the wrong place, which is worse than an error.

## Prerequisites

1. **Nothing.** No login, no account, no browser, no extension.
2. Say that plainly when the user enables it — after LinkedIn's requirements it
   sounds like something is missing.

## Building a search

The whole query is one URL parameter, `searchState`, holding JSON:

```
https://hiringcafe.com/?searchState=<url-encoded JSON>&page=<0-based>
```

| `search.*` config | Field in `searchState` | Verified values |
| :-- | :-- | :-- |
| `keywords` | `searchQuery` | free text; accents work. CH baseline 32 540 → `"product manager"` 1 401 |
| `location` | `locations[0]` | see the two shapes below |
| `posted_within` | `dateFetchedPastNDays` | **an enum, not a day count** — table below |
| `remote_only` | `workplaceTypes` | `["Remote"]`. Also `Hybrid`, `Onsite`, `Field` |
| — | `sortBy` | `default` (relevance), `date`, `date_asc`, `compensation_desc` |
| — | `commitmentTypes` | `["Full Time"]`, … |

`posted_within` maps as: `week` → `14`, `month` → `61`, `quarter` → `121` (the
site's own default, so it can be omitted).

| Enum | Window | | Enum | Window |
| --: | :-- | :-- | --: | :-- |
| `-1` | All time | | `29` | Past 3 weeks |
| `2` | Past 24 hours | | `61` | Past month |
| `4` | Past 3 days | | `91` | Past 2 months |
| `14` | Past week | | `121` | Past 3 months (default) |
| `21` | Past 2 weeks | | `750` | Past year |

**The two location shapes, and they are not interchangeable.**

```jsonc
// Country — matched on short_name ONLY. Coordinates are ignored here.
{"formatted_address":"CH","types":["country"],
 "geometry":{"location":{"lat":0,"lon":0}},"id":"user_country",
 "address_components":[{"long_name":"CH","short_name":"CH","types":["country"]}],
 "options":{"flexible_regions":["anywhere_in_continent","anywhere_in_world"]}}

// City — REQUIRES an administrative_area_level_1 component and real coordinates.
{"formatted_address":"Lausanne, CH","types":["locality"],
 "geometry":{"location":{"lat":46.5197,"lon":6.6323}},"id":"lausanne-ch",
 "address_components":[
   {"long_name":"Lausanne","short_name":"Lausanne","types":["locality"]},
   {"long_name":"Vaud","short_name":"Vaud","types":["administrative_area_level_1"]},
   {"long_name":"CH","short_name":"CH","types":["country"]}],
 "options":{"radius":25,"radius_unit":"miles","ignore_radius":false}}
```

Radius, measured live around Lausanne: 6 mi → 993 ads, 25 mi → 2 162,
50 mi → 9 299, 25 km → 1 498, `ignore_radius: true` → 705. Like LinkedIn's
`distance`, this is a net as the crow flies, **not** the commute rule — the
commute filter in `shared/scoring-rubric.md` is what actually discards ads.

## What a card yields

One JSON object per line from `hiringcafe.py search`:

| Field | Use |
| :-- | :-- |
| `id` | the 16-character `requisition_id`. **The ledger key** |
| `ledger_id` | `hiringcafe:<id>`, ready for the pipeline |
| `url` | `https://hiringcafe.com/job/<id>` — see below |
| `title`, `company`, `cities`, `workplace_type`, `commitment`, `seniority` | scoring inputs |
| **`countries`** | **the jurisdictions the employer will hire from — not a workplace.** See below before scoring on it |
| `published_estimate` | HiringCafe's **estimate** of the posting date |
| `ats`, `ats_tenant` | which ATS hosts it, and the employer's tenant on it |
| `apply_url` | the employer's own application URL |
| `collapse_key` | duplicate grouping — the script already dedupes on it |

## The ad id and its URL

The id is `requisition_id`, sixteen alphanumerics. Rebuild the URL from it:

```
https://hiringcafe.com/job/<requisition_id>
```

That answers **308** and redirects to the canonical slug URL. Follow it —
`urllib` needs a handler for 308, which the script installs. **Never build the
slug yourself**: it encodes the title, the company and the city, and a slug that
drifts by one character 404s.

In the ledger the row is `hiringcafe:<requisition_id>`. **Also record
`apply_url`**: it is the employer's own ad, and therefore the one key that
identifies the same posting when it arrives again through another board or
through a future per-ATS adapter. It is the cross-source dedup key the id check
cannot provide.

## Reading one ad

```bash
python3 .../hiringcafe.py ad <requisition_id>
```

Returns the card plus `description` — the employer's full text, converted from
HTML. A gone ad exits **3** with a clear message; record it `discarded`, do not
retry.

## Traps

**1. An unknown field is ignored in silence.** `query`, `q`, `keywords`,
`searchTerm` and `jobTitle` were all accepted and all ignored — the search
returned the *unfiltered* 32 553 ads, not an error. The only keyword field is
`searchQuery`. A typo in a filter name does not fail; it silently widens the
sweep, and the user reads noise as results.

**2. `dateFetchedPastNDays` is an enum, and a wrong value widens the set.**
`=7` returned 41 818 ads against a 32 540 baseline — *more* than no filter at
all. `=2` returned 1 365 and `=14` returned 7 873. Only the table above is
valid; never pass a raw day count.

**3. A city without its region returns 0, not an error.** The same object with
and without the `administrative_area_level_1` component: 2 162 ads versus 0.
Silent zero is this board's characteristic failure — it reads as "no jobs in
your area". The script refuses to build such a search; keep that refusal.

**4. A country code the site does not know returns a small unrelated set.**
`short_name: "ZZ"` returned 124 ads. Not zero, not an error — 124 plausible
looking ads from nowhere in particular.

**5. `company` can be a guess.** `company_attribution: "llm_pick"` means
HiringCafe's model *inferred* the employer from the ad. Treat those names as
provisional: check the `apply_url` host before writing the employer into a
cover letter, and never state an employer to the user on that basis alone.

**6. `published_estimate` is an estimate**, as the field name says — like
jobup's salary estimate. Fine for ordering and for "posted this week"; do not
present it to the user as the employer's publication date.

**7. A card can span several countries.** `cities` is a list, and a Swiss search
legitimately returns an ad listing Chicago, London, Paris *and* Geneva. Score
the location the user could actually work in, and apply the commute rule to
that one.

**8. The same posting appears twice on some ATS.** Observed verbatim: *"Sales
Development Representative"* and *"Copy Of Sales Development Representative"*,
same employer, same `collapse_key`. Dedupe on `collapse_key`, which the script
does.

**9. Cross-board duplicates are guaranteed here, by design.** This board covers
employers that LinkedIn and jobup also carry. The id check cannot see it — run
the employer-name substring check in `skills/job-scan/SKILL.md`, and prefer
`apply_url` when both rows have one.

## Coverage, measured

41 countries sampled on 2026-08-27, one request each, reading `ssrTotalCount`:

| | ads | | | ads |
| :-- | --: | :-- | :-- | --: |
| United States | 3 958 370 | | Switzerland | 32 540 |
| India | 245 616 | | Italy | 31 318 |
| Germany | 232 952 | | Belgium | 24 085 |
| Canada | 213 097 | | Japan | 21 630 |
| United Kingdom | 197 700 | | South Africa | 10 707 |
| France | 130 951 | | Morocco | 3 815 |
| Australia | 87 030 | | Nigeria | 3 178 |
| Netherlands | 58 976 | | Kenya | 2 690 |

**Where it is thin, say so.** In the thinner markets — Kenya, Nigeria, Morocco,
Egypt — roughly half of the first page was remote-from-elsewhere rather than
local. This board is a good default anywhere; it is not a sufficient one
everywhere. In those countries pair it with a national board.

## What it does not cover

**The Swiss ATS are absent.** Across 771 Swiss ads, zero came from Refline,
Ostendis, Umantis or Rexx — the systems that host Swiss SMEs, communes and
clinics. Large employers are well covered (Migros, Swiss Post, the SNB,
Helvetia, Swiss Re, Manor, Lindt & Sprüngli, Siemens, Syngenta, the Canton of
Vaud); small local ones are not. A Swiss user should not read an empty
HiringCafe sweep as an empty market.

## Applying

**There is no in-site apply flow, and that is a feature.** `apply_url` is the
employer's own ATS. Hand the user that URL with their documents, exactly as for
any external ATS. Never attempt the employer's form from here.

## The site throttles by pages asked for, and the sweep now says so

**Measured 2026-09-02 (issue #59), from a Swiss IP:**

| Run | Result |
| :-- | :-- |
| `--country ID --pages 1` | 403, 403, then success on the third attempt |
| **`--country ID --pages 6`** | **8 consecutive attempts, 8 × 403** |
| `--country CH --pages 1` | first try, 30 862 ads |
| `--country FR --pages 1` | first try, 121 503 ads |

All in the same quarter hour, so it is neither a country nor an ISO-code
problem: **the refusal rate tracks how many pages a run asks for.** One page at
a time with 25 s between requests returned **6 pages of 6**.

**So the remedy is waiting, not retrying quickly**, and the adapter now does
three things it did not:

1. **A timed backoff on 403, 429 and 5xx** — four attempts at 20 s, 40 s, 80 s.
   A second-scale retry is useless against this.
2. **`--delay`, default 25 s between pages**, deliberately high. A one-page
   sweep is unaffected; a six-page sweep takes two minutes and works.
3. **A distinct exit code.** `6` means *throttled*: the site refused, and the
   cards already printed are real. `2` still means *broken* — the payload
   shape changed, the search was invalid. They were indistinguishable before,
   and a caller cannot tell a partial pass from a failure without them.

**A truncated sweep never reports a clean finish.** It prints how many pages
of how many were read, says the rest were never fetched, and exits 6:

```
[hiringcafe] THE SWEEP IS PARTIAL: 3 of 6 page(s) read before the site
refused (HTTP 403 after 4 attempts). 118 unique cards were returned and they
are good; the rest were never fetched. Do not report this as a complete pass.
```

That is `shared/never-fail-silently.md` applied in both directions: not a
silent zero, and not a silent success either — the rule is written there as
its point 3b.

**And the pacing works on the case that failed.** Indonesia at `--pages 3`,
the sweep that could not get past three pages of six during the incident,
returned **114 unique cards over 3 pages of 3 asked** with 8 s spacing on
2026-09-02, with no refusal at all.

**Any figure taken from this board must record the pages that came back**, not
the pages that were asked for. A country measured during a throttle rests on a
smaller sample than its wording implies.

## One city, several labels — and the filter that says what it dropped

This board writes the same place several ways inside one result set. Measured
across two countries (issue #65):

| Label | Cards |
| :-- | --: |
| `Kuala Lumpur, Kuala Lumpur` | 58 |
| `Kuala Lumpur, Federal Territory of Kuala Lumpur` | 16 |
| `Kuala Lumpur, Wilayah Persekutuan Kuala Lumpur` | 12 |
| `Hanoi, Hanoi` / `Hanoi, Ha Noi` / **`Hanoi, Hà Nội`** | 19 / 3 / **2** |

Comparing whole strings by equality loses **a fifth to a third of a capital**,
silently. And on Bogotá's 103 cards: whole string 17%, first segment 51%,
**first segment with diacritics folded 100%** — neither condition works alone.

**`--city-filter` applies that comparison to what came back**, which is
different from `--city`, which asks the *site* to search a place. It folds
diacritics, compares the first segment, and **reports what it dropped**:

```
[hiringcafe] --city-filter 'Zurich' kept 2 and dropped 38.
Dropped labels: None ×7, 'Basel, Basel-Stadt, CH' ×4, 'London, England, GB' ×2 …
```

**The two rows it kept were `Zurich, Zurich, CH` and `Zürich, Zurich, CH`** —
the same city with and without the umlaut, on one page of results. An exact
comparison keeps one and loses the other, and says nothing.

The comparison lives in `skills/job-scan/scripts/_locations.py`, shared, not
copied.

## Pace, and one honest note

One request per search page, now spaced by `--delay`. A whole sweep is a few
dozen — keep it that way, sequentially, and it stays indistinguishable from a
person reading.

`robots.txt` disallows `/*?searchState=*` and `/*?page=*`. **Those URLs are not
ours to fetch, and the collection built on them is suspended.**

**Three commands were building that URL, not one.** #123 named
`hiringcafe.py:119`, found by reading this file. `ats.py` and `workday.py`
assembled the same `?searchState=` URL with **their own clients** — and
`pinpoint.py` and `recruitee.py` inherit it by running `hiringcafe.py search`
as a subprocess. Two of the five were on the user's path, in `resolve`, which
greenhouse, lever, ashby, workday and join all use. **Grepping for the file
found one; grepping for the URL found three.**

All three go through `skills/job-scan/scripts/_hiringcafe.py` now, and it
**refuses**: it returns the reason instead of the URL, names the rule, names
the open route, and says no request was made. Exit **7**, and the code
survives the subprocess boundary so a refusal reaches the caller as a refusal.

**The verdict is read from the record, not asked afresh.** A guard call is a
request to the host like any other, and collection here is suspended — so
`_hiringcafe.py` carries the verdict measured 2026-09-03 and says that it is
dated. Re-measuring means lifting the suspension first, which is a decision
rather than a code path.

> **Retracted 2026-09-03.** This file previously argued: *"This adapter is not a
> crawler … The project's position is that this is equivalent to browsing."*
> **That position is withdrawn.** It is the argument this repository refuses
> everywhere else — `shared/robots-policy.md`: *the intent behind a directive
> does not change its effect* — and accepting it here, where it happened to
> serve us, was relaxing a rule at the moment it cost something. The
> `Disallow` binds. It is left visible rather than deleted so that no one
> re-derives it.

**There is a permitted door, and it is documented** — see issue #123. `robots.txt`
allows the six sitemaps and `/job/`, and `/job/<slug>` serves the same
`__NEXT_DATA__` as the refused URL plus a `JobPosting` block. So the data is
reachable without touching a disallowed path.

**Two things that route does not solve, and both must be settled before any
rewrite:**

- **The site answers 403 (`cf-mitigated: challenge`) to a scripted client on
  *every* path, including the ones it allows.** A rewrite onto sitemaps will not
  run without the browser fallback of issue #124 — and that fallback must
  trigger on a *fetch failure*, **never on a refusal**: guard `False` or `None`
  means stop, not open a browser. Otherwise the declared identity becomes the
  appearance of compliance rather than compliance.
- **Nothing already published from the refused route can be recomputed by it.**
  Totals exist only in the search response; per-country proportions need a
  country filter the per-ad route does not have. Those figures can be dated,
  not redone.

**Until both are settled: no requests to this host, on any path.** The permitted
route being documented is not a decision to resume.
