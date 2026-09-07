# Board adapter — GLMIS (Ghana)

<!-- verified: 2026-09-07 -->

<!-- hosts: www.glmis.gov.gh, glmis.gov.gh -->
<!-- hosts-source: NOT composed, and the provenance is weaker than usual — see below · 2026-09-07 -->
<!-- script: none -->
<!-- countries: GH -->
<!-- content: measured · 10 advertisements rendered server-side on `/Jobs/Joblistings`, ids 5407–5424; no pagination marker found, so 10 is one request's yield and NOT the board's size · 2026-09-07 -->
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

## What an adapter would face

**No structured data at all**: `ld+json` is absent from the root, the listing
and the advertisement. `JobPosting` appears nine times on the homepage **and
every one of them is a path segment** — `/JobPostings/JobDetails/…` — not a
schema type. *A counter that matched the word would have reported nine.*

**So the parsing would be HTML**, and the first thing to establish is how the
listing pages beyond the first are requested. **Until that is known, no total
can be stated and none is stated here.**
