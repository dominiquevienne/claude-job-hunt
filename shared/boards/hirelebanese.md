# Board measurement — HireLebanese (`www.hirelebanese.com`, Lebanon): «Find Jobs / Browse Jobs / Advanced Job Search» — an ASP.NET WebForms board (ViewState, a search by POST) whose search page is served to the declared client (52 KB, identical twice), rules open; no count stated; no adapter yet, the browse route to measure

<!-- verified: 2026-09-17 -->

<!-- hosts: www.hirelebanese.com -->
<!-- script: none -->
<!-- countries: LB -->
<!-- content: measured · **`/jobsearch.aspx` (200, 51 957 B, md5 57dbdf6d6d93 identical on two reads) is a WebForms search form — keywords, a category list, `__VIEWSTATE` — with no card in its markup, a «Browse Jobs» page at `/jseeker/findjobhome.aspx`; no count stated, no JobPosting; `_robots.allowed('www.hirelebanese.com','/jobsearch.aspx')` → open, certain; the browse page and the ad not read** · 2026-09-17 -->
<!-- witness: none — the search form states no count · 2026-09-17 -->

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
