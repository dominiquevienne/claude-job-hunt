# Board adapter — meteojob.com

<!-- verified: 2026-09-02 -->

<!-- hosts: www.meteojob.com -->
**Re-verified 2026-09-02**: one search still returns **exactly 20 ads and no second page**, with the run stating that this is the ceiling rather than the market.

A French generalist board, around 2 million visitors a month. It also **feeds
France Travail**: 30 of 150 sampled partner ads in Paris came from Meteojob
(`france-travail.md` trap 11), so some of this board already reaches the ledger
by that route.

**Everything here was verified against the live site on 2026-08-30.**

## What this adapter can see, and what it cannot

**One search returns 20 ads. There is no second page.** That is not a
configuration choice, it is the whole envelope the site permits — see the next
section. So this adapter is a **targeted probe, not a sweep**: several narrow
searches, 20 ads each, rather than one broad pass over the board.

Offer it on that basis. A user who expects jobup-scale volume from it will
conclude the plugin is broken; a user who is told it returns the 20 freshest
matches per query gets what it actually is.

## robots.txt decides the design

```
Disallow: /api/
Disallow: /jobsearch/api/
Disallow: /jobads/
Disallow: /*?
Allow:    /jobs?*
```

The site blocks every query-string URL, then **carves out exactly one
exception**: `/jobs?*`. That is not an accident — it is the site owner saying
which door is open. So the adapter uses two paths and nothing else:

| Path | What it gives |
| :-- | :-- |
| `/jobs?what=…&where=…` | 20 result cards, **server-rendered** — no browser, no login |
| `/jobs/<id>` | The ad, with a full `JobPosting` block |

**Pages 2+ exist only behind `/jobsearch/api/`, which is disallowed.** The
pagination widget in the HTML is Angular — `<a role="button">` with **no
`href`** — and every page parameter tried on the allowed path was ignored:
`p`, `page`, `offset`, `start`, `from`, `pageNumber`, `pn`, `index`, `debut`,
`pageIndex`, `num` all returned the same 20 ids.

**Do not add a call to `/jobsearch/api/` to lift the 20-ad cap.** The cap is the
price of using the door that was left open. More coverage comes from more
searches, narrower ones — not from the forbidden endpoint.

## Configuration

```yaml
boards:
  meteojob:
    enabled: true
    searches:
      - { what: "infirmier",   where: "Lyon" }
      - { what: "développeur", where: "Paris" }
    with_detail: true      # +20 requests per search, buys the description
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `searches` | yes | A list of `what` / `where` pairs. **At least one of the two per entry**; both empty is the site's generic front page, not a search |
| `with_detail` | no | Reads each ad page for the description. 20 extra requests per search — worth it, since the listing card carries no description at all |

No login, no account, no API key. France only.

Because one search is 20 ads, **the number of configured searches is the
coverage**. When setting this board up, build the list from the user's target
roles *and* their commute towns, rather than one broad query per role.

## Building a search

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/meteojob.py" \
  search --what "infirmier" --where "Lyon" --with-detail
```

| `search.*` config | Parameter | Verified |
| :-- | :-- | :-- |
| `keywords` | `what` | `infirmier` + `Lyon` → 20 cards, all in 69 |
| `location` | `where` | Town name; the cards came back Lyon, Villeurbanne, Feyzin, Vaulx-en-Velin, Tassin, Vourles — so it is a **catchment**, not an exact-town filter |
| `posted_within` | — | **Not supported.** The card states an age in words (*"Il y a 4 jours"*), which is all there is |
| `remote_only` | — | Not supported on the allowed path |

## What a listing card yields

Measured across one 20-ad search:

| Field | Filled |
| :-- | :-- |
| `title` | 20/20 |
| `company` | **20/20** |
| `location` | 20/20 |
| `contract` — `CDI`, `CDD`, `Intérim` | 20/20 |
| `salary` — as displayed, e.g. `27 000 € - 33 000 € par an` | 17/20 |
| `posted_age` — *"Il y a 4 jours"* | 20/20 |

**What that age measures.** A relative label is the age of **this listing**, and on a re-listed ad that is the age of the re-listing, not of the ad. **This board publishes no absolute date at all** — the file already says `posted_within` is unsupported for that reason — so `posted_age` orders ads and dates none of them. Never write a date derived from it into the ledger — an empty date is a question, a wrong one is an answer (issue #84, measured on jobup: seven weeks out, and it changed which ad topped a ranking).


**The employer is named on every ad** — 20/20 on the listing, 12/12 on the ad
pages read in full. That is the reason to sweep Meteojob directly rather than
relying on its France Travail feed, where 23% of partner ads carry no employer
name at all. The ledger's employer dedup works here.

## The ad id and its URL

The id is the numeric id in the listing link. Rebuild the page from it:

```
https://www.meteojob.com/jobs/<id>
```

In the ledger: `meteojob:<id>`.

## Reading one ad

```bash
python3 .../meteojob.py ad <id>
```

The page carries two `application/ld+json` blocks — a `BreadcrumbList` and a
`JobPosting`. The `JobPosting` is the record: `title`, `datePosted`,
`validThrough`, `employmentType`, `hiringOrganization`, `jobLocation` with a
**postcode**, `baseSalary`, `industry`, `occupationalCategory`, `identifier`,
`directApply`, and the full `description`.

The postcode comes free, in the shape the ORP's PRE form wants — see
`shared/modules/job-room-ch.md`, for the users who need it.

## Traps

**1. The 20-ad cap looks exactly like a small market.** A search returning 20
ads has almost certainly matched more, and nothing in the page says so. The
script prints the difference explicitly whenever a search comes back full — a
count of 20 is *the cap*, never a measurement.

**2. `validThrough` is a formula, not a promise.** Every ad publishes an expiry
date, which normally makes a board an authority on *"is this still open?"* —
`shared/ats-open-check.md` treats a stated `validThrough` as exactly that. Here
it is **`datePosted` + 60 days, on 12 ads out of 12**, to the second. It carries
no information the posting date does not, and **must not be added to
`ats-open-check.md` as an expiry oracle.** To know whether a Meteojob ad is
still open, fetch it: a withdrawn one is gone (trap 3).

**3. A withdrawn ad answers `410 Gone`, not `404`.** Handling only 404 turns a
normal, expected outcome into a hard error. The script treats both as
`discarded`, exit 3.

**4. Identical requests return different ad sets.** The same URL fetched three
times gave the same 20 ids twice and a different set on the third. So a repeat
run legitimately surfaces ads the previous one never saw — good for coverage,
and it means **a count from this board is never stable** and two runs are not
comparable.

**5. Every tag carries an Angular build hash.** The markup is littered with
`_ngcontent-candidate-front-c752671492`, and that number changes on every
front-end deploy. **Never anchor a selector on it.** The adapter matches
`<article class="… cc-job-offer-list-item__card">` and the ad-id-keyed
`id="<id>-job-locations"`, both of which survived across the session's fetches.

**6. The location badge's text starts with the icon's name.** Its first child is
`<mat-icon>place</mat-icon>`, and `place` is the ligature, not a town — a naive
capture yields `"place"` for every ad on the board, which looks like data. The
icon element is removed before the tags are stripped.

**7. `employmentType` is not the contract type.** The `JobPosting` field is
schema.org's time-basis vocabulary — `FULL_TIME` on all 12 ads sampled — while
the listing card carries the French `CDI` / `CDD` / `Intérim`. They are
different facts, so the card keeps both: `contract` from the listing,
`employment_type` from the ad. Merging them into one field silently replaces
the useful one with the useless one.

**8. The salary is usually a range with no period.** `baseSalary.value` normally
carries `minValue` / `maxValue` rather than `value`, and **`unitText` was absent
on 5 of 6 ads** — so `30000–40000` states no period at all. Do not infer "per
year" from the magnitude; the card reports `salary_min`, `salary_max` and a
`salary_unit` that is often `null`, plus the listing's own display string, which
does say *"par an"* when the site knows.

**9. A search with no matches and a markup change look identical** — no cards,
no message, HTTP 200. The script says so rather than reporting zero as a fact.

**10. Much of this board is staffing agencies.** ADECCO MEDICAL and ADSEARCH
between them supplied most of one 20-ad healthcare search. The employer is
named — but the named employer is the agency, not the workplace, exactly as on
`randstad.md` and `fachkraft.md`. Read `company` accordingly before telling the
user who is hiring.

## Applying

`directApply` was `false` on every ad sampled: applying happens off Meteojob, on
the employer's or the agency's own site. There is no in-site apply flow to
drive, and **the plugin does not create accounts and does not fill credential
fields** — hand the user the ad URL with their documents.

## Pace, and the note on access

One request per search, plus one per ad with `--with-detail`, so a configured
sweep of six searches is about 126 requests. The script sleeps between ad reads
(`--delay`, default 1s). **`403` and `429` are treated as a stop**, never as a
retry loop, and the User-Agent is never rotated to get around one.

This adapter reads only the paths the site's own robots.txt leaves open, at
human pace, for one person's job search. The cap that comes with that is
documented above rather than engineered around — which is the whole point.
