# Board adapter — GLMIS (Ghana)

<!-- verified: 2026-09-08 -->

<!-- hosts: www.glmis.gov.gh, glmis.gov.gh -->
<!-- hosts-source: NOT composed, and the provenance is weaker than usual — see below · 2026-09-07 -->
<!-- script: glmis.py -->
<!-- countries: GH -->
<!-- content: measured · **10 advertisements, and the adapter itself calls it a suspected cap** — the unfiltered listing returns exactly ten and so does `jobTypeId=1`, and the site has no pagination · 2026-09-08 -->
<!-- witness: none found — the page states no total, and the id range is evidence of more rather than a count of them · 2026-09-07 -->

**Ghana had a country page and zero adapters.** `melr-gh.md`, its only card,
was measured on 2026-09-07 and **is not a board**: its single employment route
answers 404. *It names GLMIS in prose and gives no address for it.*

## How this hostname was obtained, and why that matters here

**It was not composed.** `glmis.gov.gh` is exactly what an acronym would
suggest, which is what makes the provenance worth writing down rather than
assuming.

```
searched            "GLMIS Ghana Labour Market Information System … vacancies"
index returned      https://www.glmis.gov.gh/                    title « GLMIS | … »
                    https://www.glmis.gov.gh/Identity/Account/…  title « Sign In | … »
Ghanaian Times      FETCHED — names NO address, checked verbatim
moi.gov.gh          unreachable (connection refused)
newsghana.com.gh    HTTP 403
```

**A search engine's summary claimed the address came from those articles. It
does not.** *Fetching the one reachable article showed it carries no URL at
all* — **so the summary attributed to a source what the index knew from its
own crawl.** A search summary is not a source, and the difference was one
fetch.

**What actually names the host is the index, carrying the pages' own
`<title>` on two distinct paths** — and then the host itself, which is the
strongest confirmation available: fetching `/` returns
`<title>GLMIS | Ghana Labour Market Information System</title>`.

*This is weaker than a third party naming it in prose, and it is written as
such. It is not composition: the string was read, not built.*

## Measured 2026-09-07

```
GET /                          200 · 200 682 o · no redirect
                               « GLMIS | Ghana Labour Market Information System »
GET /robots.txt                404 — an ABSENCE, which is knowledge
GET /Jobs/Joblistings          200 · 154 214 o
                               10 links to /JobPostings/JobDetails/<id>
                               10 distinct ids, 5407 … 5424
                               no <table>, no pagination marker, no ld+json
GET /JobPostings/JobDetails/5424   200 · 108 618 o — a real vacancy
```

**Ten is what one request yields, not the board's size.** *The ids span 5407
to 5424 — eighteen numbers for ten advertisements shown — so the id space is
denser than the page.* **No pagination marker was found in the markup**, and
the site is an ASP.NET application with 47 `<script>` blocks: paging may be
driven by a POST or by script, and **that has not been established.**

*A count of links is not a count of advertisements, so one was opened:*

```
« in DUBAI is Hiring for Indoor Cleaners »   employer NABS RECRUITM…
Posted 3 days ago · Apply · Job Description
```

**It is a vacancy, and it is an overseas placement recruited from Ghana** —
which is consistent with `countries` listing recruitment jurisdictions rather
than workplaces. *A card counting this as a Ghanaian workplace would be wrong
in a way the field is designed to prevent.*

## Shipped 2026-09-07 — `glmis.py`, and no total is stated

**There is no pagination, and that was established before any count.**

```
markup searched for   pagination · pager · page-link · PageNumber
                      pageIndex · LoadMore · data-page · next
found                 none, on any of them
the listing is        <form method="get" id="jobFilterForm"
                            action="/Jobs/Joblistings">
```

**So reach comes from the form's own filters, and the module composes
nothing** — neither a page number nor an advertisement id. *The ids run
2312…5424; enumerating them would be composition of exactly the kind that
naming this host from its acronym would have been.*

### The sweep, and its per-facet yield

```
(no filter)        10 returned · 10 new
Full-time (1)      10 returned ·  1 new
Part-time (2)       0 returned ·  0 new     <- a real empty facet
Contract (3)        1 returned ·  0 new
Temporary (4)       1 returned ·  1 new
Internship (5)      0 returned ·  0 new
Volunteer (6)       0 returned ·  0 new
                   ------------------------
12 distinct over 7 requests · ids 2312 … 5424 · 0 unreadable
```

**Two queries returned exactly ten — the same number the unfiltered view
returns — so a per-query cap of ten is not ruled out**, and more may sit
behind those two. **This is a union, not a total, and none is stated.**

*A filtered query surfaced id 2312, which the unfiltered listing does not
show: the id space is far denser than what is published.*

### The filter values are declared, and an unknown one is refused

Every value comes from the form's own `<select>`: six job types, three
workplace types, sixteen regions, twenty-two subsectors. **A value the module
does not know is refused rather than sent** — submitting an unknown id would
be composing a facet.

*`regionStateId` and `subSectorId` are accepted as single filters and
deliberately not swept: each extra dimension multiplies requests on a host
that publishes about a dozen advertisements.*

### What is parsed, and what is deliberately not split

`id`, `title`, `subsector`, and `job_type` / `workplace` **matched against the
declared vocabularies rather than inferred**. The employer and the place sit
side by side in the card with no markup between them, so **they travel whole
as `card_text` rather than being split at a guessed boundary.**

**`--strict` prints every card the parser could not read**, one per line. On
2026-09-07 that number is nought of twelve — *and it is printed rather than
assumed, because a narrow extractor does not return less, it returns false.*

## What an adapter would face

**No structured data at all**: `ld+json` is absent from the root, the listing
and the advertisement. `JobPosting` appears nine times on the homepage **and
every one of them is a path segment** — `/JobPostings/JobDetails/…` — not a
schema type. *A counter that matched the word would have reported nine.*

**So the parsing would be HTML**, and the first thing to establish is how the
listing pages beyond the first are requested. **Until that is known, no total
can be stated and none is stated here.**
