# Board adapter — Jobs.af (Afghanistan): refused to our client, and its own API states the count

<!-- verified: 2026-09-08 -->

<!-- hosts: jobs.af, api.jobs.af -->
<!-- script: none -->
<!-- countries: AF -->
<!-- content: measured · 242 advertisements, the number the site's own API states in `meta.totalItems` and the UI repeats as `Active Jobs (242)`; the pager closes on it exactly — 24 pages of 10 plus a last page of 2 · 2026-09-08 -->
<!-- witness: 242, and it is the site's number rather than my reader's — an extraction that broke would still be told 242 -->

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

## What this card does not claim

**No script ships, and `script: none` says so.** The route is the browser that
`job-scan` already drives; what is established here is the recipe, the field
list and the count, not a Python adapter.

**Nothing here was applied to.** *The advertisements carry `submissionThroughout`
values such as `link`, and no application path was exercised.*

**The 242 is today's flux.** *It is `totalItems` on 2026-09-08, and one
advertisement in the first page was published at 04:51 UTC that morning — this
board moves within the day, and the number is a reading rather than a
property.*
