# Board adapter — softgarden (an ATS, one tenant at a time): the tenant's «Karriere Board» on `<tenant>.softgarden.io/<lang>/vacancies` renders its whole list in the page — the page's own id list is the count — and each ad carries one JobPosting; `softgarden.py`, the widget and API routes refused in writing never asked, the contact footer and street never emitted

<!-- verified: 2026-09-21 -->

<!-- hosts: gruen.softgarden.io, infodas.softgarden.io, host.softgarden.io -->
<!-- host-forms: {tenant}.softgarden.io -->
<!-- host-forms-basis: read — `softgarden.py:101` (`host_of`: `--tenant` is REQUIRED, a subdomain, a host or an address on it, resolved to `<tenant>.softgarden.io`; the vendor's own subdomains refused, `softgarden.py:67`; `request()` refuses any other host before the gate) · 2026-09-21 -->
<!-- script: softgarden.py -->
<!-- countries: * -->
<!-- content: measured · **three tenants with positions and one unknown subdomain, 2026-09-21 07:06–07:09 UTC, the declared client, the guard on the exact path, two reads each. Rules: every tenant publishes the same 273-byte file — `*` refused `/just-hire/`, `/hrFrontend/`, `/hrManagement/`, `/hrd/`, `/hrc/`, `/api/`, `/strategy-board/`, `/apply/`, `/apply-choice*`, `/rest/`, `/*/widgets/`, `/wicket/bookmarkable/`; no Crawl-delay — so the widget address the search engines index (`/de/widgets/jobs`) is a refused route, never asked; the root redirects to `/de/vacancies`, open. The board page (200; HOST GmbH 34 396 B ×2 identical, GRÜN 53 756 / 56 040 B, INFODAS 52 961 B) is a Wicket page whose search is client-side (`jobSearchLive.js` filters, orders and pages the cards already in the DOM, 10 a screen; nothing fetched): `var complete_job_id_list = jobs_selected = [ids]` names every position — **HOST 7, INFODAS 22, GRÜN 31** — and each `matchElement` card carries `matchValue` cells named by the tenant's columns (`title` with the link `../job/<id>/<slug>?jobDbPVId=<n>&l=de`, `ProjectGeoLocationCity`, `sg_company_id`, `audience`, `date` dd.mm.yy, `jobcategory`); no JobPosting on the list. The ad `/job/66860360/…?jobDbPVId=…&l=de` (200 ×2, 40 471 B, identical) carries one JobPosting — title, description HTML, datePosted / validThrough with an offset (validThrough two years out), employmentType `["FULL_TIME"]`, hiringOrganization with a logo, jobLocation with streetAddress «-», postalCode, locality, region, country as a name («Deutschland»), baseSalary 0–0 — and a «Kontakt» footer with a name and an e-mail. `zzz-not-a-tenant-2026.softgarden.io/de/vacancies` 404 «Unknown subdomain.» Exercised: `jobs --tenant gruen --country-code de` → 31 emitted, the page's list names 31 (1 request, the stamp said); INFODAS by its widget address → 22 (the widget never asked); the ad → the posting, the footer's e-mail withheld** · 2026-09-21 -->
<!-- witness: the page's own `complete_job_id_list` (7 / 22 / 31), printed beside the emitted count on every run, with the ids named without a card and the cards not in the list · 2026-09-21 -->
<!-- route: http · 31 · 2026-09-21 -->

**Issue #480 (opened under #406, the ATS families). Measured 2026-09-21
07:06–07:09 UTC by the declared client, the guard on the exact path, on
three tenants named by the family's signature (`softgarden.io/jobs` in a
search engine): INFODAS (22), GRÜN Software Group (31), HOST GmbH (7).**
Rank: the pilot's order of 2026-09-21 06:13 UTC — #479 → #488 after the
dated controls.

## What softgarden is, and where its tenants live

softgarden e-recruiting GmbH (Berlin) sells applicant tracking, multiposting
and feedback tools; the employer's «Karriere Board» is hosted on
`<tenant>.softgarden.io` (a company page on `softgarden.career.softgarden.de`
exists too — not this route). **The user names the tenant** by its subdomain
(`gruen`), its host, or any address on it — the widget address a search
engine gives, `infodas.softgarden.io/de/widgets/jobs`, names the tenant and
nothing more: `/*/widgets/` is refused in writing.

## The route — the board page, whole

```
GET https://gruen.softgarden.io/de/vacancies                       200 — complete_job_id_list = [31 ids]; 31 matchElement cards
GET https://host.softgarden.io/                                    200 → /de/vacancies (7)
GET https://gruen.softgarden.io/job/66860360/…?jobDbPVId=285261432&l=de   200 — one JobPosting (the `ad` command); the ad lives at /job/, not /de/job/ (404)
GET https://zzz-not-a-tenant-2026.softgarden.io/de/vacancies       404 «Unknown subdomain.» — not a tenant, exit 3
```

One request for the whole board: the page's search, paging and «N
Stellenanzeigen gefunden» are computed in the browser over the cards the
server already rendered, so the plugin reads what the browser would show
without running its script. The adapter emits the ids the page names, in
its order, then any card the list does not name — and says both counts.
`--country-code` **stamps**: the cards carry no country (the ad carries a
name), and the run says the code is the user's.

## What the adapter emits, and withholds

`jobs --tenant <tenant> [--lang de] [--country-code ISO2]`: id, url (the
card's own link, `jobDbPVId` and `l` kept), title, company
(`sg_company_id`), place, audience, category, published (dd.mm.yy →
ISO) — each as the tenant's columns give it, None otherwise. `ad --url`:
the page's JobPosting — title, company, place, region, `country_name`
(the name the posting gives; `country` only when it is a code),
employment_type, published, expires, description (text, scrubbed).

**Withheld:** the «Kontakt» footer (a name and an e-mail) never read into a
record; the JobPosting's `streetAddress`, `postalCode`, `logo` and its 0–0
`baseSalary` never emitted; every e-mail address and telephone in the text
replaced by «[e-mail withheld]» / «[telephone withheld]» — a date («ab
01.10.2026») is left alone; `contacts_withheld` on every record; the
application (`jobdb.softgarden.de/…/applyonline`, `/apply/` refused in
writing) never touched.

## Tests and mutations

`AnATSWhoseBoardIsRenderedWholeInItsPageAndWhoseWidgetRouteIsRefusedInWriting`,
both ways on fixtures (the id list and the cards, an id without a card and
a card without an id, the widget address resolved to the board, the stamp
said, the empty board, the unknown subdomain, a page without the list, the
vendor's hosts and another host refused, the ad with its footer and street,
the ad gone or changed, a foreign query dropped from the ad address).
Mutation bench on a detached copy, `python3 -B` — see the PR.
