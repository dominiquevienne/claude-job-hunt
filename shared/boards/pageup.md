# Board adapter — PageUp (an Australian ATS — universities, the public sector, Compass Group; US campuses too; one tenant at a time) on its classic careers site: `careers.pageuppeople.com/<id>/cw/<lang>/listing/` — or the same paths on the employer's own host — a server-rendered table paged by its own «More Jobs» link whose count is what REMAINS after the page (shown + remaining = the stated total: Compass Group 651, Virginia Tech 297, 2026-09-21); `pageup.py`, the apply gateway never touched; the newer «careersite» product measured and not covered

<!-- verified: 2026-09-21 -->

<!-- hosts: careers.pageuppeople.com -->
<!-- host-forms: careers.pageuppeople.com/{id}/cw/{lang}/ · {employer-host}/cw/{lang}/ -->
<!-- host-forms-basis: read — `pageup.py:tenant_of`: a bare id is `careers.pageuppeople.com/<id>/cw/en/`; an address on any host with `/cw/<lang>/listing/` is its own tenant (host, id prefix, locale); one host per run, every other host refused before the gate; `secure.pageuppeople.com` / `secure.dc2.pageuppeople.com` (the application gateway), `www.` and `static.` never tenants, never sent · 2026-09-21 -->
<!-- script: pageup.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants with positions on the classic site, one on the newer product, and an unknown id, 2026-09-21 09:05–09:10 UTC, the declared client, the guard on the exact path. The issue's 403 (873 B, 2026-09-13) was the VENDOR's marketing root `www.pageuppeople.com` — the careers host answers 200. Rules (`careers.pageuppeople.com/robots.txt`, BOM + 33 lines): `*` refuses the test and admin paths (`/admin`, `/awake`, `/uat`, `/*/uat/`, `/*/staging/`…), nothing of `/<id>/cw/`; no Crawl-delay. Compass Group `/541/cw/en/listing/` (200, 89 670 B): the `#search-results-content` table — `a.job-link` `/541/cw/en/job/<no>/<slug>`, `span.location`, `span.close-date time[datetime]`, a `tr.summary` teaser under each row — fifteen rows, then `<a class="more-link" href="…?page=2&page-items=15">More Jobs <span class="count">636</span>`: **the count is the REMAINDER — 15 + 636 = 651; page 2 (15 rows) says 621 = 651 − 30; `page-items=100` shows 100 and says 551 = 651 − 100.** `pageup.py jobs --tenant 541` live 09:08 UTC: **651 emitted over 7 pages of 100 — the site states 651: equal** (651 distinct numbers, every row with a place, 54 with a closing date, Perth 45 / Melbourne CBD 42 / Sydney CBD 40); Virginia Tech `/968/cw/en-us/listing/` (20 a page by default, two columns — no Closes cell): **297 emitted over 3 pages = 297 stated** (Blacksburg 225). SA Power Networks 511 REDIRECTS to `careers.sapowernetworks.com.au/jobs/search` — the newer «careersite» product (Rails/Turbo cards, ten a page, no stated count read, also on `<hash>.careersite.pageuppeople.com/cw/en/listing/`): NOT this adapter (exit 6 «not the classic careers site»), a second form to build. `/999999/cw/en/listing/` 404 (exit 3). The advert (`/541/cw/en/job/725443/…`, 24 108 B): `#job-content` — `h2`, `.job-externalJobNo`, `.work-type`, `.location`, `.categories`, `#job-details` (HTML), «Advertised:» `.open-date time` 2026-09-21T08:30:00Z, «Applications close:» `.close-date time`, `og:site_name` «Compass Group»; no JobPosting; the apply and employee-referral links go to `secure.dc2.pageuppeople.com/apply/541/gateway/…` (never emitted, never touched); an unknown job number answers 200 with «Sorry, we can't provide additional information about this job right now» and an empty `#job-content` (exit 3)** · 2026-09-21 -->
<!-- witness: the page's own «More Jobs» remainder — `pageup.py jobs` reads the first page's rows plus its remainder as the stated total and prints it beside the emitted count («651 emitted … the site states 651 … equal»; «short» is exit 6) · 2026-09-21 -->
<!-- route: http · 948 · 2026-09-21 -->

```
pageup.py jobs --tenant 541 --country-code AU                                   # careers.pageuppeople.com/541/cw/en/listing/?page=N&page-items=100
pageup.py jobs --tenant https://careers.pageuppeople.com/968/cw/en-us/listing/ --page-items 20
pageup.py ad --url https://careers.pageuppeople.com/541/cw/en/job/725443/karratha-locals-hospitality-all-rounders
```

**The count is a remainder, not a total.** The «More Jobs» link says how
many jobs are left after the page it sits on — 636 under fifteen rows, 551
under a hundred. The adapter adds the first page's rows to it and calls that
the stated total (651 both ways), then follows the link's own `page` and
`page-items` to the end; the page size 100 is ours (the site's default is
15 or 20) and the output says over how many pages of what size it walked.
The 948 of the route line are Compass 651 + Virginia Tech 297.

**Two products under one name.** The classic `cw` site is this adapter. The
newer «careersite» (SA Power Networks, the `<hash>.careersite.pageuppeople.com`
hosts) is a different application — cards, no table, no remainder read; the
adapter names it and exits 6 rather than emitting nothing in silence. A
second adapter, or a second mode, is due for it.

**Withheld:** the application gateway links, the texts scrubbed of e-mail
addresses and telephones, `contacts_withheld` on every record, the country
stamped from `--country-code` (the site names none) and said.

**Guard** `AClassicCareersSiteWhoseMoreJobsCountIsWhatRemainsAfterThePage` in
`tests/test_core.py` — both ways (the walk by the link and the count against
shown + remaining, short → 6, a repeated number once, a page of repeats, a
two-column tenant on its own host and locale, the summary row on its own job,
`--page-items` sent, `--country-code` said, the careersite shape → 6, an
unknown id → 3, the advert's fields, dates, employer and scrubbed
description, the gateway absent, an unknown job number → 3, bad addresses
and the gateway hosts refused, another host refused before the gate).
Mutation bench 2026-09-21: 11 mutations, 11 red.
