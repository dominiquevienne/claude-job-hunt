# Board adapter — Jobs.af (Afghanistan): refused to our client, and its own API states the count

<!-- verified: 2026-09-12 -->

<!-- hosts: jobs.af, api.jobs.af -->
<!-- script: none -->
<!-- countries: AF -->
<!-- content: measured · 292 distinct advertisement ids read through the page's own API from a browser tab (3 pages of 100: 100 + 100 + 92), **and `meta.totalItems` states 292, the UI repeats `Active Jobs (292)` — equal**; the browser route, walked end to end · 2026-09-12 -->
<!-- witness: the site's own `meta.totalItems` and the UI counter, read in the same minute as the walk and printed beside the distinct count («292 emitted, site states 292 — equal»); 242 on 2026-09-08 by the same two anchors — the board moves within the day · 2026-09-12 -->

**No `host-forms:` is declared, because no script ships to reach a form** —
the same reason `kariera-mk.md` gives. *Both hosts are named in `hosts:`
above, and the second one comes from the page's own network trace rather than
from a literal in code.*

**The first card for Afghanistan.** *No card in this repository declared `AF`
before this one, so the country's status was not "measured and empty": it was
never asked.*

## Both hosts refuse our declared client, with the vendor default

```
GET https://jobs.af/                                     403   25 bytes
GET https://api.jobs.af/public/jobs?itemsPerPage=10&page=1
                                                         403   25 bytes
body   "Your request was blocked."   md5 9ccabba20b9f4ec7d18bd6644579e5bf
```

**Read twice on the API host, same md5 both times**, so the fingerprint is
comparable rather than carrying a per-request element. *This is the body shared
across unrelated hosts that `shared/robots-policy.md` records: a vendor
default, not this operator's words.*

**The rules, by contrast, permit.** `jobs.af` carries a `*` group and no
`Disallow` touching our paths; the guard was taken on `/`, `/public/job` and a
real advertisement path before anything was fetched.

**`api.jobs.af` is the honest gap in that sentence.** Its `/robots.txt`
answers **HTTP 200 with 1 248 bytes that are not a rules file** — the module
reports `state: unrecognised` and permits by absence. *No rules were read
there; "permitted" means "nothing forbade", which is a weaker claim than the
apex's.*

## The browser is served, and the API answers from the page's own origin

**The refusal is aimed at the client.** The same API that returns 403 to our
declared HTTP client returns `200` and JSON when the page itself calls it.

```
GET https://api.jobs.af/public/jobs?itemsPerPage=<n>&page=<n>
envelope   { data: [...], meta: { currentPage, itemsPerPage,
                                  totalItems, totalPages, filters, sorts } }
filters    filter[expiryDate]=$lt:<date>;$gt:<date>      (the "Expiring" tab)
```

**29 fields per advertisement**, and they are real fields rather than prose:
`id`, `title`, `slug`, `reference`, `numberOfVacancies`, `educationLevel`,
`salaryType`, `salaryGrade`, `minimumSalary`, `maximumSalary`, `fixedSalary`,
`currency`, `workType`, `contractType`, `probationPeriod`, `isExtendable`,
`gender`, `language`, `publishDate`, `expiryDate`, `submissionThroughout`,
`company`, `country`, `provinces`, `functionalAreas`, and three UI flags.

*Advertisement pages are `/public/job/<slug>`.*

## The count is the site's, not mine — which is the whole point

**`meta.totalItems` is 242, and the UI counter says `Active Jobs (242)`.**

```
page  1   -> 10 items      totalItems 242, totalPages 25
page 12   -> 10 items
page 24   -> 10 items
page 25   ->  2 items      24 x 10 + 2 = 242
```

**The pager's arithmetic closes on the declared total**, and the 32 items drawn
from those four pages carry 32 distinct ids — *no overlap between pages, though
that is checked on four pages and not on twenty-five.*

> **This is the discriminant #181 asks for.** *If my extraction stopped
> working, `meta.totalItems` would still say 242 — so "the board is empty" and
> "I read nothing" would not produce the same output here.* **`kariera.mk` has
> no such number and its card says so; this host has one.**

**And a sum that closes is not a duplicate check.** *`24 x 10 + 2 = 242` would
hold just as well if pages repeated items;* the id comparison is what rules
that out, on the four pages where it was done.

## The constraint that costs a session if it is not written down

**A cold load of `https://jobs.af/public/job` renders NOTHING** — zero cards,
and the counter itself reads `Active Jobs (0)`.

**The same URL reached by clicking `View All` from the home page renders
normally**, counter at 242. *The listing hydrates through client-side
navigation and not on a direct hit.*

**`Active Jobs (0)` is the dangerous half.** *A page that renders no cards
invites a second look; a page that states a count of zero looks like an
answer* — and it is the same shape as a probe taken before a page has
finished, which reads exactly like an empty site.

**Scrolling adds nothing and there is no pagination control in the DOM**: ten
cards, five scrolls, still ten. **The 242 are reachable only through the API
above**, which is why this card records the endpoint rather than a scroll
recipe.

## 2026-09-12 — the browser route, MEASURED end to end (#222)

**11:50–11:52 UTC, Claude in Chrome connected, one tab, nothing applied to.**
The guard first, on the exact paths: `jobs.af/` open (`*`, certain),
**`jobs.af/jobs` refused by a written `Disallow: /jobs`** — not a path this
route touches (the listing is `/public/job`, the pages `/public/job/<slug>`) —
and `api.jobs.af` permitted by absence (`allowed True, certain False`, as
on the 8th). `www.tala-com.com`, first in the #222 order, could not be
measured — its name is out of the zone (see its card).

```
navigate https://jobs.af/                      renders; «Active Jobs (292)» in the page's own text
fetch api.jobs.af/public/jobs?itemsPerPage=10&page=1   200 — meta.totalItems 292, totalPages 30
fetch …?itemsPerPage=100&page=1..3             200 · 100 + 100 + 92 rows, totalPages 3
                                               **292 distinct ids — 292 emitted, site states 292 — equal.**  11:51:31 UTC
click «View Field Officer – Mobile Money»      /public/job/field-officer-mobile-money-16 — one JobPosting in JSON-LD
                                               (title, hiringOrganization, datePosted, validThrough, description 2 142 chars, addressCountry Afghanistan)
the page's own calls, read from performance entries:
  api.jobs.af/public/jobs/promoted · api.jobs.af/public/jobs/<slug> · api.jobs.af/public/jobs/<slug>/similar
fetch api.jobs.af/public/jobs/field-officer-mobile-money-16   200 — 41 keys: the listing's 29 plus jobRequirements,
  roleSummary, minimum/maximumExperience, contractDuration, nationality, submissionEmail, submissionLink,
  travelRequired, announcementType, isLegacy, attachments   (numberOfVacancies 50, salaryType as_per_company_scale)
```

**The procedure a session follows — this is the adapter, at the same title
as a script (decision of 2026-09-08):**

1. guard `jobs.af` `/` and `/public/job/<slug>`, and `api.jobs.af` on the
   exact path, before anything — `/jobs` is refused and is never the route;
2. `navigate https://jobs.af/` in the session's own tab (a cold load of
   `/public/job` renders nothing — the 8th's finding, unchanged);
3. from that tab, `fetch('https://api.jobs.af/public/jobs?itemsPerPage=100&page=N')`
   for N = 1 … `meta.totalPages`, 1.5 s apart, collecting `data[].id`;
   print **«n emitted, site states meta.totalItems»** — equal, or k short;
4. one advertisement: `fetch('https://api.jobs.af/public/jobs/<slug>')`, or
   the page `/public/job/<slug>` for its JSON-LD; the ad URL is rebuilt from
   the slug, never scraped;
5. close the tab.

*Four API requests and one page for the whole board on the day.* **The
count is the site's on both ends** — the API's `meta.totalItems` and the
UI's `Active Jobs (n)` — and on 2026-09-12 they agreed with each other and
with the walk. **292 on the 12th against 242 on the 8th**: fifty more in
four days, by the same two anchors; this is a flux, not a drift in the
reader.

## What this card does not claim

**No script ships, and `script: none` says so.** The route is the browser that
`job-scan` already drives; what is established here is the recipe, the field
list and the count, not a Python adapter.

**Nothing here was applied to.** *The advertisements carry `submissionThroughout`
values such as `link`, and no application path was exercised.*

**The 242 was the 8th's flux, the 292 the 12th's.** *It is `totalItems` on the day, and one
advertisement in the first page was published at 04:51 UTC that morning — this
board moves within the day, and the number is a reading rather than a
property.*
