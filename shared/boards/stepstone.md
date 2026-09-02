# Board adapter — StepStone

**One platform, nine domains, six inventories, six countries.** Totaljobs,
Jobsite, Caterer, IrishJobs, NIJobs and StepStone DE/AT/BE/NL are the same
application: the same JavaScript bundle, the same markup contract, the same ad
schema. They are told apart by one number.

It is the widest single adapter here — Germany, Austria, Belgium, the
Netherlands, the United Kingdom and Ireland, which are six of the countries
with the thinnest coverage in the atlas — and it is the first adapter in this
repository whose main risk is not a missing ad but **a page full of ads that do
not match the search**.

**Everything below was verified against the live sites on 2026-09-02**, with no
account and no key.

## The identity, established rather than assumed

All nine serve `client-bundle.js?v=4.107.0`, the same Genesis design system
(`data-genesis-element` on every node), the same `window.__PRELOADED_STATE__`,
the same `VISITOR_ID` cookie and the same Akamai front. The result cards carry
`data-at="job-item"` / `job-item-title` / `job-item-company-name` /
`job-item-location` / `job-item-timeago` on every domain, 25 per page on every
domain. The ad pages carry `job-ad-header`, `apply-now-section`,
`job-ad-company-card` and **one JSON-LD `JobPosting`** on every domain.

What differs is `siteId`, in `__PRELOADED_STATE__.header`:

| Domain | `siteId` | Country | Ad URL grammar | Inventory |
| :-- | --: | :-- | :-- | :-- |
| `cwjobs.co.uk` | 2 | GB | — **not a board**, see below | uk |
| `totaljobs.com` | 4 | GB | `/job/<slug>/<employer>-job<id>` | uk |
| `jobsite.co.uk` | 7 | GB | same | uk |
| `caterer.com` | 10 | GB | same | uk |
| `stepstone.de` | 250 | DE | `/stellenangebote--<title>-<city>-<employer>--<id>-inline.html` | de |
| `stepstone.at` | 255 | AT | `/stellenangebote--…-inline.html` | at |
| `stepstone.be` | 260 | BE | `/jobs--…-inline.html` | be |
| `stepstone.nl` | 270 | NL | `/banen--…-inline.html` | nl |
| `nijobs.com` | 300 | GB-NIR | `/job/<slug>/<employer>-job<id>` | ie |
| `irishjobs.ie` | 301 | IE | same | ie |

Checked and **outside** the family: `stepstone.fr` redirects to the group's
corporate site and is not a board; `stepstone.lu` redirects to `en.jobs.lu`,
which is a different platform; `milkround.co.uk` did not answer.

**Six inventories, not nine.** Ad ids were tried across domains, and they do not
travel:

| Tried | Result |
| :-- | :-- |
| A Jobsite card id on `totaljobs.com` | **200, the same ad** — Jobsite is Totaljobs |
| A Caterer card id on `totaljobs.com` | **200** — Caterer is Totaljobs |
| An IrishJobs id on `nijobs.com`, and the reverse | **200 both ways** — one island-of-Ireland inventory |
| An IrishJobs id, a NIJobs id on `totaljobs.com` | **404** — Ireland is not the UK board |
| A `stepstone.de` id on `stepstone.at` | **404** |
| A `stepstone.be` id on `stepstone.nl`, and the reverse | **404** |

So the ledger sees `uk` (four skins), `ie` (two skins), and DE, AT, BE, NL one
each. **Enabling two skins of one inventory is a duplicate generator**, and the
card carries `inventory` so the ledger can say so.

## The transport failure, which comes first because it has no status code

A request to this platform can fail **with no HTTP status at all**:

```
curl … https://www.totaljobs.com/job/…-job107921946
  → curl: (92) HTTP/2 stream 1 was not closed cleanly: INTERNAL_ERROR (err 2)
curl --http1.1 … https://www.irishjobs.ie/jobs/chef?page=6
  → curl: (56) Recv failure: Operation timed out
```

Not a 429, not a 403, not a page. Two shapes were seen, and they are different:

1. **Cold ad requests over HTTP/2 fail** while the result list answers 200 on
   the same connection settings. Fetching a result list first — which leaves
   `VISITOR_ID`, `_abck` and `bm_sz` in the jar — then replaying the ad with a
   `Referer` returned **200 on 5 of 5**. Forcing HTTP/1.1 also worked, cold.
2. **Any host goes quiet after a burst.** `irishjobs.ie` served `?page=3`
   normally, then timed out on pages 6, 7 and 12 in a row a minute later,
   including a page that certainly exists (that search has 150 results, six
   pages). The silence is the rate limit; there is no 429 to read.

`stepstone.py` therefore uses `urllib`, which speaks **HTTP/1.1 only** and never
meets shape 1, warms the host before reading an ad, paces at 2 s by default, and
on a statusless failure **retries exactly once after 15 s, then stops and says
the sweep is incomplete**. This is `shared/never-fail-silently.md`: a client
that reads "no status" as a blip retries for ever and reports nothing.

## The count on the page is not the count of ads that match

Every result list carries its own analytics blob,
`data-atx-onpageview-payload`, and that blob breaks the headline total down by
*extension* — the platform's own word for the ads it added to a thin result:

| Site, search | reported | `main` | `semantic` | `regional` |
| :-- | --: | --: | --: | --: |
| stepstone.nl, *software developer* | 26 | **1** | 25 | 0 |
| stepstone.be, *software developer* | 607 | 110 | **497** | 0 |
| stepstone.at, *softwareentwickler* | 519 | 248 | **271** | 0 |
| totaljobs, *software developer* **in London** | 1 862 | 1 065 | 1 | **796** |
| stepstone.de, *softwareentwickler* | 4 962 | 4 892 | 70 | 0 |
| totaljobs, *software developer* | 3 786 | 3 785 | 1 | 0 |
| irishjobs, *software developer* | 408 | 408 | 0 | 0 |

**`stepstone.nl` holds one Dutch ad for "software developer" and serves a full
page of 25 cards.** Nothing in the visible list marks the other 24: same card,
same markup, same position in the flow. A sweep that scores what it is given
scores 25 ads as Dutch software-developer vacancies, and the one real match is
diluted 1 in 26.

The padding is worst exactly where the board is thinnest — the small national
sites — and negligible on the big ones. **Adding a location adds a third
axis**: `regional` is ads outside the place asked for, 796 of 1 862 on London.

The payload gives counts, **not per-card attribution**, so an adapter cannot
filter the padding out; it can only refuse to hide it. `count` and `search`
print the split on stderr and name the share that is not a literal match, and
`count` returns `literal_matches` next to `reported`. Read `main`.

## The depth is a per-site field, not a platform constant

Every site's own `robots.txt`, read 2026-09-02. There are **four regimes**, by
two different mechanisms:

| Site | The rule in its `*` group | Pages open |
| :-- | :-- | --: |
| `totaljobs.com` | `Disallow: /jobs*?page=*`, then `Allow: /jobs/*?page=2$` … `page=5$` | **5** |
| `cwjobs.co.uk` | the same `Disallow`, and **the `Allow` lines for 2–5 are commented out** (dated 04/03/25) | 1 |
| `jobsite.co.uk` | `Disallow: /*?page=*`, `/*page=*`; its `Allow` commented out | 1 |
| `caterer.com`, `irishjobs.ie`, `nijobs.com` | `Allow: /*?q*&page=` **outranks** `Disallow: /*&page=` — the longer rule wins | result set |
| `stepstone.de/at/be/nl` | `Disallow: /*?*` (any query string), reopened by `Allow: /jobs/*?q=*`, closed again by `Disallow: /jobs/*?q*&*` | 1 |

The StepStone four are the strictest and by a different route: they never
mention `page=`. They forbid **any** query string, reopen a single-parameter
`q=` search, and the `&` in `?q=x&page=2` puts it back under the ban. Their
path-only URLs carry no query and stay open, which is why the script builds
`/jobs/<keyword>/in-<place>` rather than a query — verified equivalent:
`/vacatures/accountant` and `/vacatures/?q=accountant` return the same 3 cards.

So **coverage on this platform is a number of searches, not a depth**. At 25
cards a page that is 25 ads per search on five sites, 125 on Totaljobs, and the
whole result set on Caterer, IrishJobs and NIJobs.

`Amazonbot` is banned on Totaljobs, CWJobs and Caterer. **No AI agent is named
anywhere, for or against**, on any of the nine. Apex and `www` are identical
everywhere (every apex 301s to `www`, byte-identical files). No `Sitemap:` line
on any of them.

## CWJobs is not a board

`cwjobs.co.uk/jobs/software-developer` answers 200 with 25 ordinary-looking
cards. **50 of 50 card links across two searches point at
`https://www.totaljobs.com/job/…`; 0 point at `cwjobs.co.uk`**, and its ids
resolve on Totaljobs. It is a filtered front end onto the Totaljobs inventory —
a tech vertical, the way Caterer is a hospitality vertical, except that Caterer
at least serves the ad on its own domain.

`stepstone.py --site cwjobs` exits 2 with that measurement rather than
sweeping. Enabling it would add nothing and duplicate everything.

## Configuration

```yaml
boards:
  stepstone:
    enabled: true
    sites: ["stepstone-de", "irishjobs"]   # required; one or more
    searches:                              # required; each is one sweep
      - keyword: "softwareentwickler"
        location: "Berlin"                 # optional
      - keyword: "product manager"
    pages: 1                               # optional; capped per site
    delay: 2.0                             # optional; seconds. Do not lower
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `sites` | yes | Any of `totaljobs`, `jobsite`, `caterer`, `irishjobs`, `nijobs`, `stepstone-de`, `stepstone-at`, `stepstone-be`, `stepstone-nl`. **`cwjobs` is refused** |
| `searches` | yes | A bare result list is the whole board, and this platform pads a result list. The script refuses a search with neither `keyword` nor `location` |
| `pages` | no | Above a site's robots ceiling the script errors rather than fetching |
| `delay` | no | Default 2.0 s. The platform goes silent under a burst, without a 429 |

**Two skins of one inventory is a configuration mistake**, not a wider sweep:
`totaljobs` + `jobsite`, or `irishjobs` + `nijobs`, return the same ads under
two ledger keys. Pick the general one — `totaljobs`, `irishjobs` — unless the
vertical is the point (`caterer` for hospitality).

No credentials, no login, no browser.

## Search, and what a card yields

```
GET https://www.stepstone.de/jobs/softwareentwickler
GET https://www.stepstone.de/jobs/softwareentwickler/in-berlin
GET https://www.totaljobs.com/jobs/chef?page=2        # where robots allows it
```

The keyword and the place are slugified into the path. The card is an
`<article id="job-item-<id>">` and yields, verbatim from `data-at` attributes:
**id, title, company, location text, salary text, posting age**, plus a
work-from-home marker. Company and location are nested inside an icon span —
anchoring on the first `</span>` returns nothing, so the parse walks the tag
depth.

The id is the ledger key: `totaljobs:107921946`, `stepstone-de:14330848`.

## The ad URL is rebuilt from the id, and the slug is decorative

```
https://www.totaljobs.com/job/x/y-job107921946              → 200
https://www.stepstone.de/stellenangebote--x--14330848-inline.html → 200
```

Both answer with the real ad. **Never scrape the URL out of the card** — and on
Jobsite you cannot anyway: all 25 card links are `href="/tp-out"`, a redirect
stub, and `jobsite.co.uk/robots.txt` **disallows `/tp-out`**. The id is in the
card's `id` attribute, and rebuilding from it is the only route that is both
possible and permitted.

## Reading one ad

Every ad carries one JSON-LD `JobPosting`. Across **108 ads read on nine
sites**, it gave:

| Field | Coverage |
| :-- | :-- |
| `description`, full text | 108/108 — median 1 152 to 5 223 characters depending on the site |
| `validThrough` | **108/108** — a real expiry date, which most boards here do not have |
| `datePosted`, `employmentType`, `hiringOrganization.name`, `jobLocation` | 108/108 |
| `baseSalary` | **11/12 on Totaljobs; 0/12 on Caterer, IrishJobs, NIJobs and all four StepStone sites** |

So the ad is worth reading for its text and its expiry, and — outside Totaljobs
— it is **not** where the salary is.

## Salary: measured, because a field that is present is not a field that is filled

Salary was counted on **the cards**, four searches per site, ~100 cards each:

| Site | Cards with a salary element | Of those, carrying a figure |
| :-- | --: | --: |
| totaljobs | 98/104 | **89 (91%)** |
| jobsite | 100/104 | 88 (88%) |
| caterer | 91/104 | 79 (87%) |
| nijobs | 99/103 | 80 (81%) |
| **irishjobs** | 100/104 | **27 (27%)** |
| stepstone.de / .at / .be / .nl | **0 of 104 each** | — |

Two different absences, and they must not be handled the same way:

- **On the four StepStone sites the element is not rendered at all.** There is
  no salary on the card and none in the JSON-LD. For DE, AT, BE and NL this
  board tells you nothing about pay, and `shared/scoring-rubric.md` has to work
  without it.
- **On IrishJobs the field is filled with a string that means empty**:
  `€ Not Disclosed`, 73 of 100 cards. Totaljobs has its own vocabulary —
  `Unspecified`, `Competitive`, `Negotiable`. A parser that tests for a
  non-empty salary string reads 100% coverage on a board that discloses 27%.

The card therefore carries `salary_text` **and** `salary_disclosed`:
`false` when the field is present and says nothing, `null` when there is no
field at all. They are different facts.

## Zero-shaped answers

**1. No HTTP status at all.** Both shapes above. Retry once, slowly; then say
the sweep is truncated. Never loop.

**2. A 200 result list padded with ads that do not match.** The headline count
and the cards agree with each other and both overstate the board. Only the
analytics payload dissents. Documented at the top because it changes what a
result means, not merely how to fetch it.

**3. A keyword slug that nobody uses answers 200 with a plausible title.**
`stepstone.nl/vacatures/kok` → *"Kok Jobs en vacatures | Stepstone"*, **1
card**; `/vacatures/verpleegkundige` → 1 card. There is no 404 for a term the
board has nothing for, and the page looks like a small market rather than a bad
search. Compare `main` against `total` before believing either.

**4. CWJobs: 25 cards, none of them its own.** Covered above.

**5. Jobsite: 25 cards, no ad URL in the page.** `href="/tp-out"`, which its
own robots.txt disallows. Rebuild from the id.

**6. A 404 on an ad means gone**, and it is how the cross-domain id tests came
back — a well-formed id from the wrong inventory 404s cleanly.

**7. An ad with no JSON-LD.** Not seen once in 108, which is exactly why the
script treats it as a signal to re-verify this file rather than a row to skip
quietly.

## Applying

There is no in-site apply flow driven here. `directApply` was `true` on the ads
sampled, meaning the platform hosts the application form; the plugin hands the
user the ad URL and their documents, and **the user applies themselves**. No
account is created and no credential field is filled.

## Pace

No rate limit is published and there is no `429` — the platform simply stops
answering, and comes back later. 2 s between requests held for a run of about
160 requests across ten hosts; a burst on one host went silent within a dozen.
Keep `delay` at or above 2.0, and prefer more searches on more days over more
pages in one run.

## Verification

```bash
S=skills/job-scan/scripts/stepstone.py
python3 $S count  --site stepstone-nl --keyword "software developer"   # 26 reported, 1 literal
python3 $S count  --site totaljobs --keyword "software developer" --location london
python3 $S search --site stepstone-de --keyword softwareentwickler --limit 3
python3 $S search --site irishjobs --keyword "software developer" --limit 4  # € Not Disclosed
python3 $S ad     --site stepstone-de --id 14330848
python3 $S search --site cwjobs --keyword x        # refuses, with the measurement
python3 $S search --site jobsite --keyword chef --pages 3   # refuses, robots ceiling
```
