# Board measurement — HireLebanese (`www.hirelebanese.com`, Lebanon): «Find Jobs / Browse Jobs / Advanced Job Search» — **the route is found and it is a plain GET: `searchresults.aspx?…&pg=N` states «Job Posts 1 - 50 of 3210 Results Found» and its own Last link ends at page 65**, with the browse page carrying the site's counts by location, by sector and by company; rules open, no adapter yet

<!-- verified: 2026-09-22 -->

<!-- hosts: www.hirelebanese.com -->
<!-- script: none -->
<!-- countries: LB -->
<!-- content: measured · **2026-09-22, two reads of each route by the declared client, the guard on the exact path, no Crawl-delay written: `/jseeker/findjobhome.aspx` 200 ×2, 110 865 B, md5 25e3856878b4 identical — the Browse page, 42 advert links and THREE facet blocks carrying the site's own counts (by location: Lebanon 1951, Lebanon - Beirut 901, Tripoli 63, Bekaa 34, Saidon 12, and non-Lebanese ones — Iraq 30, Congo 29, Ghana 26, Ivory Coast 12, Angola 7; by sector: Other 445, Sales 417, Accounting/Finance 396, Engineering 219, Restaurant/Food 214; by company). Every facet link is a plain GET `../searchresults.aspx?resume=1&top=0&category=&company=&country=N`. `searchresults.aspx?resume=1&top=0&category=&company=&country=` 200 ×2, 39 583 B, md5 5dab6fb7a558 identical — **50 adverts and «Job Posts 1 - 50 of 3210 Results Found»**, the pager a GET `…&pg=N` whose own Last link is **pg=65** (50 × 65 = 3 250 ≥ 3 210). Each advert is a `div.panel.jobs-margin`: the title linking `jobdetails.aspx?id=N`, «employer - country», «Posted at Sep 22, 2026», and an excerpt. No POST and no ViewState are needed for the walk — the search FORM uses them, the browse route does not** · 2026-09-22 -->
<!-- witness: the results page's own «Job Posts 1 - 50 of 3210 Results Found» and its Last link at pg=65; and the browse page's counts by location, by sector and by company · 2026-09-22 -->

**Found by the Lebanon search of #609 (a country never searched), measured
2026-09-17 13:53–13:55 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads, two public resolvers on a DNS
negative.** The method is written on #609: one search naming the boards,
the National Employment Office (ILO and UNESCWA name its e-labour
exchange at `neo.gov.lb`) and the regional aggregators (Bayt — already
`bayt.md`; Naukrigulf, Tanqeeb — regional, left aside), no composed host
names. *A measurement, not an adapter.*

```
_robots.allowed('www.hirelebanese.com', '/jobsearch.aspx')   open, certain
GET https://www.hirelebanese.com/jobsearch.aspx               200 ×2, identical — a WebForms search form, /jseeker/findjobhome.aspx to browse
```

**The search is a POST with a ViewState** — not a URL the plugin replays;
whether «Browse Jobs» lists by GET is the adapter's first line (its
`adapter` issue).

## The route, found 2026-09-22 — and what the next session should not assume

**The walk is a GET.** `searchresults.aspx?order=date&keywords=&category=&type=&duration=&country=&state=&city=&emp=&pg=N` is what the page's own «Next» and «Last» links carry, 50 adverts a page, **65 pages**. The card's earlier note — «an ASP.NET WebForms board, a search by POST» — describes the **search form** at `/jobsearch.aspx`, which is not the road to the board: the browse route needs neither a POST nor a `__VIEWSTATE`.

**Three witnesses, and none of them is ours.** The results page states its total *and* its window («1 - 50 of 3210»), so a walk can be checked at every page rather than once at the end; and the browse page states counts **by location, by sector and by company**, which is the discriminant a total cannot be — *an extraction that drops five rows and doubles five others still states 3 210.*

> **But the location counts must NOT be summed.** They carry «Lebanon (1951)» *and* «Lebanon - Beirut (901)», «Lebanon - Tripoli (63)», «Lebanon - Bekaa (34)», «Lebanon - Saidon (12)» side by side, **and whether the sub-entries are inside the 1 951 or beside it is not established.** Adding them would be the subordination trap this repository has already paid for: two true numbers and a false relation between their denominators. *The next session settles it by asking the site — `country=` for one and the other — before writing any comparison.*

**And the board is not only Lebanese.** Its own location facets name Iraq (30), Congo (29), Ghana (26), Ivory Coast (12), Angola (7) and a dozen more, so `--country-code` must STAMP and the country a record carries is the one the row prints («employer - country»), never one we assume from the host.

*Measured, not built: this is the first line of #657 done, deposited so it is not rediscovered. No adapter was written — the session that took it stopped at its budget floor and said so.*
