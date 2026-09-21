# Board adapter — SeamlessHiring (SeamlessHR's ATS — Nigeria, Botswana, West and Southern Africa; one tenant at a time): the careers portal `<tenant>.seamlesshiring.com` is a login shell, but its own job API `/v2/jobs/job-list` answers the declared client without a session and states its `total` (Letshego 15, Golden Oil 6, 2026-09-21); `seamlesshiring.py`, the recruiters' contacts and the tenant's API key — which the API hands out — never emitted

<!-- verified: 2026-09-21 -->

<!-- hosts: letshego.seamlesshiring.com, goldenoiltd.seamlesshiring.com, coronationgroup.seamlesshiring.com, mgas.seamlesshiring.com -->
<!-- host-forms: {tenant}.seamlesshiring.com -->
<!-- host-forms-basis: read — `seamlesshiring.py:DOMAIN` with the tenant as its subdomain (`tenant_of`: a name, a host or an address on it); one host per run, the vendor's own hosts (`seamlesshiring.com`, `cdn.`, `seamlesshr.com`) never tenants, every other host refused before the gate · 2026-09-21 -->
<!-- script: seamlesshiring.py -->
<!-- countries: * -->
<!-- content: measured · **four tenants, 2026-09-21 07:47–07:52 UTC, the declared client, the guard on the exact path. The issue (#494) named `<entreprise>.seamlesshr.com/careers`; the product's careers portals live on `<tenant>.seamlesshiring.com` (found by search: coronationgroup, letshego, goldenoiltd, mgas). Rules: `User-agent: * / Disallow:` on the tenant hosts — nothing refused, no Crawl-delay. The root (8 935 B) is a Vue login shell («Welcome to X's job portal»; `cdn.seamlesshiring.com/js/app.js`, 15.5 MB) — no job in it; `/jobs` 404. Read in the bundle: `JobModel.viewJobsListing` → `GET /v2/jobs/job-list` with params, `getJob` → `GET v2/jobs/find/<id>`, axios base `/`, the candidate route `/jobs/view/:id` redirecting to `/job/view/<id>`. `job-list` answers the plain client, no cookie, no token: `{status_code: 200, data: {jobs: {current_page, data, last_page, per_page: 20, total, next_page_url}, subsidiaries}}` — `seamlesshiring.py jobs` live 07:51–07:52 UTC: **Letshego 15 emitted = 15 stated, Golden Oil 6 = 6, Coronation 0 = 0, M-Gas 0 = 0**; `find/10845` the same record; `find/1` `{"message": {"message": "Job not found", "status_code": 404}}` (exit 3); an unknown subdomain does not resolve (exit 3, «not a tenant»); `/job/view/10845` 200, 71 553 B, «Portfolio Analyst | Letshego Holdings Limited» in the title — the public advert address. The record: title, summary, details and experience (HTML), location / city / location_details.name, `country_id` (a number — the API names no country), post_date, expiry_date, closing_date, job_type, work_style, position, job_level, qualification, remuneration min/max + currency_id when `show_remuneration` is 1 (Golden Oil: 200 000–300 000, currency 74), is_private, status, company.name, specializations. **And the API gives what the page does not show: `company.phone`, `company.email`, `company.address`, `company.api_key` (the tenant's own key), `users[]` (the recruiters' names and e-mails), `fields`/`form_structure` (the application form), `scoring_criteria`, `auto_screening_json`, `sentiment_analysis`** — none emitted** · 2026-09-21 -->
<!-- witness: the API's own `total` — `seamlesshiring.py jobs` walks twenty a page to `last_page` and prints it beside the emitted count («15 emitted from letshego.seamlesshiring.com — the site states 15: equal»; «short» is exit 6) · 2026-09-21 -->
<!-- route: http · 21 · 2026-09-21 -->

```
seamlesshiring.py jobs --tenant letshego --country-code BW     # /v2/jobs/job-list?page=N to last_page; «15 emitted — the site states 15: equal»
seamlesshiring.py ad --url https://goldenoiltd.seamlesshiring.com/job/view/10848
```

**A tenant is named, never guessed.** The issue's `<entreprise>.seamlesshr.com/careers`
form does not exist on the product; the portals are `<tenant>.seamlesshiring.com`
and the tenant comes from the user's configuration (a name, a host, or an
advert address on it). The vendor's own hosts are refused as tenants; a name
that does not resolve is «not a tenant» (3), never an empty board.

**The country is stamped, not read.** The API carries `country_id` (29,
393…) and no name; `--country-code` stamps every row and the run says so.
The 21 of the route line are Letshego 15 + Golden Oil 6, the two tenants with
adverts on 2026-09-21.

**Withheld — more than usual, because the API leaks more than usual.** The
company block carries the recruiter's telephone, e-mail, street and the
tenant's API key; `users` the recruiters' names and e-mails; the form and the
screening rules travel with every record. The adapter keeps the advert and
its dates, scrubs the texts of e-mails and telephones, never emits the logo,
and sets `contacts_withheld` on every record. *The key is the vendor's
matter to fix; this repository neither prints nor stores it.*

**Guard** `ATenantPortalWhoseLoginShellHidesAJobApiThatStatesItsTotalAndLeaksItsRecruiters`
in `tests/test_core.py` — both ways (the walk to `last_page` against `total`,
short → 6, a repeated id once, a page of repeats stopping the walk, the
vendor's hosts and any other refused before the gate, an unknown tenant, a
login shell answering HTML → 6, `--country-code` stamped and said, the
salary only when shown, the advert by its public address, «Job not found» →
3, bad addresses, and nothing from the contact and screening blocks in any
row). Mutation bench 2026-09-21: 10 mutations, 10 red.
