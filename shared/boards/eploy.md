# Board adapter — Eploy (a UK ATS, one tenant at a time): the tenant's careers site on its own domain renders `/vacancies/vacancy-search-results.aspx?view=list` server-side, 12 a page, the count in the page's title, and the pages beyond the first by the pager's WebForms postback — replayed with the page's own hidden fields and cookies; the vacancy page carries a JobPosting; `eploy.py`, streets and postcodes never emitted

<!-- verified: 2026-09-20 -->

<!-- hosts: jobs.le.ac.uk, jobs.manchester.gov.uk, careers.nhsprofessionals.nhs.uk, careers.eploy.com -->
<!-- host-forms: jobs.le.ac.uk, jobs.manchester.gov.uk, careers.nhsprofessionals.nhs.uk -->
<!-- host-forms-basis: read — the tenant is the employer's own host (`eploy.py:tenant_of`, any host the user names, one per run, every other refused before the gate); the family has no shared host, its signature is the path `/vacancies/vacancy-search-results.aspx` with `$Eploy(` and `aspnetForm` in the page, checked on the answer (exit 6 otherwise); the three named are the tenants measured · 2026-09-20 -->
<!-- script: eploy.py -->
<!-- countries: * -->
<!-- content: measured · **three tenants with vacancies and one without, 2026-09-20 12:4x–13:1x UTC, the declared client, the guard on the exact path first, the root read twice per host. Rules: `jobs.le.ac.uk`, `jobs.manchester.gov.uk`, `careers.nhsprofessionals.nhs.uk` — no Disallow on `/vacancies/`, no Crawl-delay; `jobs.digital.nhs.uk` no longer resolves (two public resolvers). The list `/vacancies/vacancy-search-results.aspx?view=list` is server-rendered (200; Leicester 274 005 B, Manchester 494 552 B, NHSP 279 898 B): `<title>17 Vacancies - University of Leicester</title>` / «82 Vacancies - Manchester City Council» / «3 Vacancies - NHS Professionals» state the count, `careers.eploy.com` (Eploy's own, 221 694 B) states «0 Vacancies» and «Your search returned no results»; cards `<div id="…VacancyListView_ctlNN_pnlList" class="vsr-job">` with `<h2 class="vsr-job__title"><a href="<id>/<slug>.html">`, fields as `div_<Field>_<id>` items whose labels the tenant chooses (Leicester: Location, School/Division, Vacancy terms, Salary details, Hours per week, Advert closes; Manchester: Vacancy Type, All Locations with the school's street and postcode; NHSP: All Locations, Position, Advertising Salary, End Date, Vacancy Type), `More Info` to the same page, `vacancy-apply.aspx?VacancyID=` (an account); 12 a page; page 2 and on by `__doPostBack('ctl00$ContentContainer$ctlNN$VacancyPager','2')` — a POST of the form with every hidden field (`__VIEWSTATE`, `__VIEWSTATEGENERATOR`, `__EVENTVALIDATION`, `__VIEWSTATEENCRYPTED`, `hiddenPostAction`…), the selects' values and the session's cookies: without them the server answers page 1 again, with them `<span class="cpb">2</span>` and the next 5 (Leicester); `eploy.py jobs` live: Leicester 17 emitted, states 17, 2 pages; Manchester 82 = 82, 7 pages; NHSP 3 = 3. The vacancy page `/vacancies/13948/director-of-marketing.html` (200, 176 651 B) carries one schema.org JobPosting in a list — title, datePosted, validThrough, employmentType, skills, industry, hiringOrganization, jobLocation (streetAddress «University Road», postalCode «LE1 7RH», locality, region, country «United Kingdom»), baseSalary («Competitive»), description (HTML, a contact address in it — scrubbed)** · 2026-09-20 -->
<!-- witness: the page's title («N Vacancies») and its hero — `eploy.py jobs` prints it beside the emitted count on every walk · 2026-09-20 -->
<!-- route: http · 102 · 2026-09-20 -->

**Issue #464 (opened under #406, the ATS families). Tenants found by the
family's signature on 2026-09-20 — `careers.nhsprofessionals.nhs.uk` (3),
`careers.eploy.com` (0), `jobs.manchester.gov.uk` (82), `jobs.le.ac.uk`
(17), `jobs.digital.nhs.uk` (no longer resolves) — three with vacancies, as
the README's two-tenant rule asks; measured by the declared client, the
guard on the exact path first.** Rank: the pilot's order of 2026-09-20
12:5x, after #463.

## What Eploy is, and where its tenants live

Eploy is a British ATS (Eploy Ltd, Kidderminster) whose careers sites run
on the employer's own domain — a university, a council, an NHS body — with
the same WebForms application behind: `/vacancies/vacancy-search-results.aspx`
for the list, `/vacancies/<id>/<slug>.html` for a vacancy,
`/vacancies/vacancy-apply.aspx?VacancyID=<id>` to apply (an account). **The
user names the tenant by its host** (`jobs.le.ac.uk`) or its URL; the
adapter reads that host and refuses every other before the gate.

## The route — a server-rendered list, a postback pager

```
GET  https://jobs.le.ac.uk/vacancies/vacancy-search-results.aspx?view=list                 200 — 12 cards, «17 Vacancies», the pager's __doPostBack('…VacancyPager','2')
POST https://jobs.le.ac.uk/vacancies/vacancy-search-results.aspx?view=list  (the form + cookies)  200 — page 2: cpb 2, 5 cards
GET  https://jobs.le.ac.uk/vacancies/13948/director-of-marketing.html                        200 — the JobPosting (the `ad` command)
GET  https://careers.eploy.com/vacancies/vacancy-search-results.aspx?view=list               200 — «0 Vacancies», «no results»: 0 emitted, states 0, not an error
```

**The pager is a postback, and it wants the whole page back.** The form's
hidden fields carry the server's view state and its event validation for
that very page; a POST with the event alone is answered with page 1, and the
adapter reads the current page from `<span class="cpb">` and dies with 6
when the answer is the page it was sent from. The first page's cookies are
kept for the walk (one jar per run). Two seconds between requests are ours;
a tenant's `Crawl-delay` is read by `Pace`.

## What the adapter emits, and withholds

`jobs --tenant <host> [--country-code ISO2] [--max-pages N]`: id, url, title,
place · site (the location trimmed of streets and postcodes — «Pear Tree
High School, Worcester Road, Cheadle Hulme, Stockport, SK8 5NW» gives site
«Pear Tree High School», place «Stockport»), salary, hours_per_week,
vacancy_type, closes, division, and `fields` — the tenant's own labels and
values, the address fields left out. **The list states no country:
`--country-code` stamps the rows with the country the user names for that
tenant, and the count line says so.** `ad --url`: the JobPosting — title,
company, country (from `addressCountry`), place, region, posted, closes,
employment_type, salary, skills, industry, description (scrubbed).

**Withheld:** the street and the postcode of a workplace, in the list (the
label trimmed) and in the ad (`streetAddress`, `postalCode` not read out);
descriptions scrubbed of e-mail addresses and telephone numbers (Leicester's
posting names a contact address); the application never touched;
`contacts_withheld` on every record.

## Tests and mutations

`AnATSWhoseTenantSiteRendersItsListAndPagesByAWebFormsPostbackThatNeedsThePagesOwnFieldsAndCookies`,
both ways on fixtures (the postback's fields, event and Referer; the walk
to the stated count; a postback answered with its own page; the empty
tenant; the bounded walk; a page without the count; a non-Eploy page; the
address trimmed, a street as the last segment, a validator's message; the
country stamp; the ad with the street and postcode withheld and the
description scrubbed; another host refused; bad tenants refused before a
request). Mutation bench on a detached copy, `python3 -B`, 9 / 9 red: the
view state not carried · the selects not carried · the `cpb` check dropped
· the postcode kept · the street segment kept · the validator's message kept
· the description not scrubbed · the street read out in the ad · the stated
count ignored.
