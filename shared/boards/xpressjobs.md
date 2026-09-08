# Board adapter — XpressJobs (Sri Lanka): shipped, and its own total counts slots

<!-- verified: 2026-09-08 -->

<!-- hosts: xpress.jobs -->
<!-- script: xpressjobs.py -->
<!-- host-forms: xpress.jobs -->
<!-- host-forms-basis: read — `xpressjobs.py:BASE`, a single literal; no tenant and no second host · 2026-09-08 -->
<!-- countries: LK -->
<!-- hosts-source: `xpressjobs.lk` named on Sri Lanka's country page 2026-09-02; it redirects, and the guard reports the rules as read from `xpress.jobs` · 2026-09-08 -->
<!-- content: measured · **2 761 distinct advertisements** read over 219 pages of `/api/jobs/searchJobs` on 2026-09-08. The board's own `recordCount` says **4 364**, and that figure counts ROW SLOTS: the pager served exactly 4 364 of them and **1 603 were repeats**. The two agree on slots and neither counts the board · 2026-09-08 -->
<!-- witness: `recordCount`, the board's own field, carried on every row — but it attests SLOTS and not advertisements, and this card says so rather than quoting it as a total · 2026-09-08 -->

**Sri Lanka's country page listed this host as *«à instruire»* on 2026-09-02.
It is instructed: open, reachable, and not readable over HTTP.**

## The host named on the country page is not the host that answers

```
guard on xpressjobs.lk  ->  "These rules were read from 'xpress.jobs', not from …"
```

**The board has moved domain**, and the guard said whose rules it had actually
read rather than reporting them as the requested host's. *That is the
behaviour `shared/robots-policy.md` requires — «the rules that apply are the
receiving host's» — working before anything was fetched.*

Everything below is `xpress.jobs`.

## The rules are as open as a rules file gets

```
# https://www.robotstxt.org/robotstxt.html
User-agent: *
Disallow:
```

**Seventy bytes, one empty `Disallow`.** *An empty `Disallow:` is how a file
says nothing is closed* — not a refused path, which is a distinction this
repository has had to make before, on a 26-byte file that was reported as
refusing one path.

## The sitemap has 8 815 URLs and not one advertisement

```
/Organization/<id>/<slug>   8 725     employer profiles
/jobs/sector/<sector>          ~40     category pages
/Organization/<id>/jobs          4     per-employer job lists
/Jobs · /jobs/cvless · static     …     the rest
                            -----
                            8 815     lastmod on 0 of them
```

**Counting `<loc>` here would report a very large board where the file
contains no advertisement at all** — not 16.6 times too large, as on
`myjobsfiji`, but a number with no relation to the quantity.

*And nothing carries a `lastmod`*, so the file says nothing about freshness
either.

## Every route returns the same 1 766-byte shell

```
/Jobs                          1 766 o · no payload carrier · JobPosting 0
/jobs/sector/banking           1 766 o · idem
/Organization/10389/jobs       1 766 o · idem
<body><noscript>You need to enable JavaScript to run this app.</noscript>
       <div id="root"></div></body>
```

**Checked for payload carriers, not assumed from the size** — `data-page`,
`__NEXT_DATA__`, `application/json`, `__INITIAL_STATE__`: none present.

*That control exists because it was got wrong:* `portaljob-madagascar` was
filed as serving nothing when it serves its whole page in a `data-page`
attribute. **Here the check was run and the shell really is empty.**

### And the endpoint is not statically extractable

The bundle is 4.3 MB minified. It names `api/` paths for images and CVs —
`api/vacancy/getJobDescriptionImage?`, `api/candidate/cv?` — but the base is
**computed at runtime**:

```js
zs = Na() + "api/"
```

*The search endpoint is assembled from minified identifiers.* **Finding it
would mean executing the bundle, not reading it**, and this card does not
guess a path the site never writes down.

## What this is, and what it is not

**Not refused** — the rules are the most permissive form there is, and every
request returned 200. **Not absent** — the site is live and says it serves
over 12 000 organisations. **Not an anti-robot challenge** — nothing was
posed.

> **The object is simply not on the wire.** *A client-side application that
> computes its own API base is unreadable by this repository's HTTP route, and
> that is a property of the site's architecture rather than of its policy.*

**Sri Lanka stays uncovered by a national adapter.** *The country page records
that `hiring.cafe` carries 25 cards with a Sri Lankan city and that an existing
adapter reaches them; this card says nothing about those and does not count
them.*

**The other named hosts, from the country page and not re-measured here:**
`topjobs.lk` answers `/robots.txt` with 1.13 MB of home page and returns the
same body for an invented URL; `jobsnet.lk` serves a self-signed certificate
issued for `ln2.ceynet.asia`; `labourdept.gov.lk` is broken while
`labourmin.gov.lk` renders. `ikman.lk` — classifieds with a jobs section —
remains genuinely uninstructed, and its rules file **explicitly allows nine AI
agents including `ClaudeBot` and `anthropic-ai`**, with a comment saying so.

## The advertisements are behind an API the site's own front end calls

**This card said `indeterminate` because every route returns the same
1 766-byte shell.** *That was true, and it stayed true of the routes: an
employer page (`/Organization/85/ceylon-tours`) and a sector page
(`/jobs/sector/accounting`) both return that identical shell — two more route
families, same answer.*

**The listing is a JSON API**, found by loading one page in a browser and
reading the requests it made:

```
/api/jobs/searchJobs?page=1&pageSize=20&keyword=&locations=&sectors=
      &jobTypes=&careerLevels=&sortBy=SortedCreateDate+DESC
      &byCVLess=false&byWalkIn=false
/api/jobs/allSectors     /api/home/locations     /api/jobs/searchFilterOptions
```

> **The browser was used to DISCOVER the path and not to read the board.**
> *`robots.txt` permits `/api/jobs/searchJobs` — `allowed=True`, `certain=True`
> — so the reading itself goes through the ordinary guarded fetcher.*

**And the path was not in the bundle.** *4 317 800 bytes of React, and a search
for `/api/` strings returns nothing: the URL is assembled at run time.* **Six
routes and a full bundle read said «&nbsp;not here&nbsp;»; one page load said
where.**

## The count, and its anchor is not ours

```
recordCount declared on every item, page 1     4 354
recordCount declared on page 218               4 356
pagination      217 full pages x 20 + 16   =   4 356
page 400                                       0 items, no overlap with page 1
```

**Two independent computations agree**: the board's own field and the
arithmetic of its pagination. *That is the external anchor issue #181 asks for
— a number that does not come from our own reader.*

**And it moved by two between two requests**, minutes apart. *A live stock, not
an archive: `expireDayCountDown` is 14 on the three advertisements sampled.*

## What is still not established

- **no advertisement page was opened** — the fields above are the listing API's;
- **the 8 725 `/Organization/` sitemap entries were not crossed** against the
  employers in the API, so how much of the employer corpus is hiring is unknown;
- **no adapter**, and the API's parameters (`sectors`, `locations`,
  `careerLevels`) were not exercised beyond the unfiltered query.


## 2026-09-08 — shipped, and the number the board states is not the number of jobs

**`xpressjobs.py search` reads the API 5a found.** *The browser discovered the
path; it does not read the board.* **Every fetch goes through the ordinary
guarded fetcher**, and `robots.txt` permits `/api/jobs/searchJobs`.

```
219 pages read          2 761 distinct advertisements
recordCount             4 364
slots served            4 364        218 x 20 + 4
duplicate rows          1 603        skipped by jobId
```

> **`recordCount` counts the row slots the pager will serve, not distinct
> advertisements.** *It agrees with `218 × 20 + 4` because both count slots.*
> **Neither of them counts the board.**

**The earlier reading of this pair as "two independent counts that agree" was
wrong, and it was mine.** *They are not independent: the pager's arithmetic and
the declared total measure the same thing.* **37 % of the rows served are
repeats**, and only reading every page and keying on `jobId` reveals it — *the
first 500 rows carried 15 duplicates, 3 %, which would have passed for noise.*

### Two defects the exercise found in this adapter, and both are recorded

**It paced too fast.** *At 1.5 s a full sweep took HTTP 400 at the 26th
request, 51 seconds in — about 30 a minute. Page 26 fetched alone straight
afterwards returned its 20 rows, so the refusal was a RATE and not a page.*
**The spacing is now 3 s, and it is a measured margin rather than a chosen
one.**

**And its duplicate counter was inert.** *It printed `kept − len(seen_ids)`,
and both grow in the same branch, so it was zero by construction* — **it
reported "0 duplicates" across a sweep that skipped 1 603.** Duplicates are now
counted where they are skipped.

### What the adapter emits, and what it does not

**No `url`.** *The API carries no address field, every HTML route answers 200
with the same 1 766-byte shell, and a composed address would look right and
resolve to nothing.* **`jobId` is emitted instead** — the site's own identifier,
and the ledger key.

**No per-advertisement endpoint**, because none was verified. *`overview` is a
summary of about 120 characters, not the description.*

**A truncated sweep says so.** *On an HTTP failure mid-sweep the run reports
`{n} advertisements, not the board, which declares {recordCount}` and exits
PARTIAL — without it, a rate limit at page 26 leaves 485 rows on stdout that
look like a result.*
