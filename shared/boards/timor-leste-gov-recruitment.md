# Board measurement — Government of Timor-Leste — Recruitment (`timor-leste.gov.tl/?cat=44`, Timor-Leste): the Government's WordPress category of recruitment notices, served to the declared client, **25 entries over three pages on 2026-09-21** (each a dated document, 24 PDFs and one image, with the editor's summary), the walk ending on the first page the category does not fill; `timorlestegov.py` — the documents are named, never downloaded

<!-- verified: 2026-09-21 -->

<!-- hosts: timor-leste.gov.tl, timorleste-jobs.tenderwell.app -->
<!-- script: timorlestegov.py -->
<!-- countries: TL -->
<!-- content: measured · **the category walked by the declared client, 2026-09-21 13:38–13:40 UTC, the guard on the exact path, two reads of page 1 and one of each other page: `/?cat=44&lang=en` 200 ×2 (33 435 B, md5 d20470a82dd2 / f5bdc419f9d7 — an agenda block moves) carries **10 entries**; `&page=2` 200 (31 657 B) 10; `&page=3` 200 (25 137 B) 5; `&page=4` 200 (19 110 B) **0 — the walk's end**. **25 entries, and the category states no count anywhere** (its pager only names the next pages). Each entry is a `div.docs_img` + `div.docs_details`: `span.date` («01 of July of 2026», and Portuguese months on older ones — «20 of Outubro of 2022»), `a.title` pointing at the **document itself** (24 of 25 PDFs under `/wp-content/uploads/`, one JPEG), the summary the editor wrote, `#file_size`. What the category holds is what the government filed under it: calls for judges, consultants and project staff, and the odd tender or contest — dated 2022 to 2026-07-01. The four-post reading of 2026-09-18 was the page before its pager was followed. Exercised: `jobs --country-code tl` → **25 entries over 3 pages, «page 4 carried none — the walk's end» said**** · 2026-09-21 -->
<!-- witness: none — the category states no count; `timorlestegov.py jobs` prints the entries read, the pages walked and how the walk ended · 2026-09-21 -->
<!-- route: http · 25 · 2026-09-21 -->

**Found by the Timor-Leste search of #612 (a country never searched),
measured 2026-09-18 06:33–06:36 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #612: one search naming the national portals, the Government's
recruitment page and the UN aggregators (UNjobs, UNjobnet — global, left
aside), no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('timor-leste.gov.tl', '/?cat=44&lang=en')   open, certain
GET https://timor-leste.gov.tl/?cat=44&lang=en             200 ×2 — WordPress «Recruitment», four posts
GET https://timorleste-jobs.tenderwell.app/                 404, 19 B ×2 — nothing at the root
```

**The public entry found**: the Government's own recruitment notices —
few, on the portal. Whether the category pages by `paged=N` and what a
post carries are the adapter's first line; a national employment service
portal was not found by this search.

## The adapter — `timorlestegov.py` (#685, 2026-09-21)

```
GET /?cat=44&lang=en            200 — 10 entries, the pager naming pages 2 and 3
GET /?cat=44&lang=en&page=2     200 — 10
GET /?cat=44&lang=en&page=3     200 — 5
GET /?cat=44&lang=en&page=4     200 — 0 entries: the walk's end
```

**The end of the walk is a page the category does not fill**, not a count:
nothing on the site states one, and the run says «page 4 carried none — the
walk's end» beside the entries read. A page repeating the previous page's
documents ends it too (exit 6) — the other way a pager can lie.

**The key is the document's own file name** (`C27BC53D6ECA87895.pdf`): the
portal repeats no id, and two calls can share a title word for word (two of
the 25 do). **The documents are never downloaded** — the record names the
address the category publishes, with the date, the editor's summary and the
file size as written.

**Withheld:** e-mail addresses and telephone numbers in the summaries;
`contacts_withheld` on every record. `--lang` picks the portal's language
(`en`, `pt`, `tt`; the entries are often Portuguese whatever the interface
says, and the run does not translate). `--country-code` stamps and says so.

**Tests and mutations.**
`AGovernmentCategoryWhoseEntriesAreDocumentsAndWhoseEndIsAnEmptyPage`, both
ways on fixtures (the empty page ending the walk and not counted as a page
of entries, a Portuguese date, the repeating page, a page that is not the
category, a 404, an empty first page, `--max-pages`, a bad `--lang`, the
`www.` host refused). Mutation bench on a detached copy, `python3 -B` — see
the PR.

