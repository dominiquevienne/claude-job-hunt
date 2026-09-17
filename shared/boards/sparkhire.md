# Board adapter — SparkHire Recruit, ex-Comeet (an ATS, one tenant at a time): the tenant's careers page on `www.comeet.com` carries its `company_uid` and public careers token, and the page fills its list by the careers API on `www.comeet.co` — replayed with the page's own parameters; `sparkhire.py`, the application address never emitted

<!-- verified: 2026-09-16 -->

<!-- hosts: www.comeet.com, www.comeet.co -->
<!-- host-forms: www.comeet.com, www.comeet.co -->
<!-- host-forms-basis: read — `sparkhire.py` names both hosts as literals (`PAGE_HOST` for the tenant page, `API_HOST` for the careers API), refuses any other host before the gate; the tenant is a path (`/jobs/<slug>/<uid>`), never a subdomain, so the host forms are closed · 2026-09-16 -->
<!-- script: sparkhire.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants with positions and one without, 2026-09-16 22:26–22:28 UTC. Rules: both hosts publish the same file (1 261 B) — `*` refused `?s=`, `/category/`, `/tag/`, `/wp-admin/`, `utm` and `src` URLs, nothing under `/jobs/` or `/careers-api/`; no Crawl-delay. The tenant page `/jobs/<slug>/<uid>` (200; 293 973 B for Quantum Machines, 811 176 B for CommIT, 118 566 B for Spark Hire's own) is AngularJS with no position in its markup and `COMPANY_DATA = {"company_uid": "D6.000", "token": "6D02…", "slug": …}`; the API the page calls, `www.comeet.co/careers-api/2.0/company/<uid>/positions?token=<token>&details=true`, answers a JSON list: Quantum Machines 51 positions (232 918 B; IL 16, US 16, DK 6, JP 3, DE 3, NL 3, KR, SG, HU 1, one without a country), CommIT 158 (IL 47, PL 22, UA 20, 15 without a country; `employment_type` «Full-time» 93, «full time» 15, None 41 — the tenant's own labels), Spark Hire `[]` — a tenant with no open position answers an empty list with 200; each position carries uid, name, department, location (name, city, state, country), employment_type, experience_level, workplace_type, time_updated, url_active_page (the employer's page — one careers URL for every CommIT position), url_comeet_hosted_page (per position), details (Description, Requirements, Preferred Skills as HTML), and `email` / `email_alias` (the application address on applynow.io), referrals_reward, linkedin_job_posting_id; no count stated anywhere — the list is the board** · 2026-09-16 -->
<!-- witness: none — the API's list is the board; `sparkhire.py jobs` prints its length as the count and says no count is stated anywhere · 2026-09-16 -->
<!-- route: http · 209 · 2026-09-16 -->

**Issue #452 (opened under #406, the ATS families). Measured 2026-09-16
22:26–22:28 UTC by the declared client, the guard on the exact path, on
three tenants — Spark Hire's own (`spark-hire/30.005`, no position),
Quantum Machines (`quantummachines/D6.000`, 51), CommIT (`comm-it/76.008`,
158): two with positions, as the README's two-tenant rule asks.** Rank: the
pilot's order of 2026-09-16 23:4x, the first ATS family after the boards.

## What SparkHire is, and where its tenants live

Comeet was an Israeli ATS; Spark Hire bought it in 2023 and calls it Spark
Hire Recruit. **The hosted careers pages are still on `www.comeet.com/jobs/
<slug>/<uid>`** (the employer's own site usually frames or links them — Spark
Hire's `/careers/` links to `comeet.com/jobs/spark-hire/30.005/`), **and the
API on `www.comeet.co/careers-api/2.0/`.** The user names the tenant as the
careers URL spells it: `quantummachines/D6.000`. A tenant found on an
employer's domain is the same page: its source carries the same
`COMPANY_DATA`, and the `www.comeet.com` address for it is
`/jobs/<slug>/<uid>`.

## The route — a call the page makes, replayed with the page's own parameters

```
GET https://www.comeet.com/jobs/quantummachines/D6.000                                    200 — COMPANY_DATA: company_uid D6.000, token 6D02…
GET https://www.comeet.co/careers-api/2.0/company/D6.000/positions?token=6D02…&details=true  200 — 51 positions, JSON
GET https://www.comeet.co/careers-api/2.0/company/D6.000/positions/13.05B?token=6D02…        200 — one position (the `ad` command)
GET https://www.comeet.com/jobs/spark-hire/30.005 → …/company/30.005/positions?token=…       200 — `[]`: «0 positions — the tenant publishes none today», not an error
GET https://www.comeet.com/jobs/lemonade | jfrog | fiverr | riskified | gong                  404 — a guessed slug is not a tenant; the uid is part of the address
```

**The token is the tenant's public careers key, printed in every visitor's
page** — the same shape as StaffPoint's `Next-Action` id and Eezy's GraphQL
text (the pilot's judgment of 2026-09-14): the plugin replays the URL the
page calls, with the parameters the page carries, and nothing else. The
adapter checks that the page's `company_uid` is the address's (exit 6
otherwise) and refuses any host but the two (exit 7).

## What the adapter emits, and withholds

`jobs --tenant <slug>/<uid> [--country-code ISO2]` (two requests): id (the
position uid), url (the hosted page, per position), employer_url (the
employer's own page — may be one careers URL for all), title, company,
department, place, region, location (the site's own label), employment_type,
experience_level, workplace_type (Hybrid / Remote / On-site), updated, and
`details` as a map of the tenant's section names to scrubbed text. `ad
--url`: one position through the API's `positions/<uid>`.

**Withheld:** `email` and `email_alias` — the position's application
address (`<slug>.<uid>@applynow.io`) — never emitted, not even as a key; the
details scrubbed of e-mail addresses and telephone numbers; the referral
reward («4,000$» on Quantum Machines) and the LinkedIn posting id not
emitted; `contacts_withheld` on every record; the application (a form on
the hosted page) never touched.

## Tests and mutations

`AnATSWhoseTenantPageCarriesItsOwnCareersTokenAndWhoseAPIListsThePositionsWithTheirApplicationAddress`,
both ways on fixtures (the page's token, the API's list with a position
without details, the country filter, the empty tenant, the page without
COMPANY_DATA, the uid mismatch, a 404 tenant, a malformed tenant, another
host refused, the ad). Mutation bench on a detached copy, `python3 -B`, 6 /
6 red: the token regex broken · the application address emitted · the
details not scrubbed · the country filter dropped · the uid check dropped ·
the empty list made an error.
