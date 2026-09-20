# Board adapter — Varbi (a Swedish ATS, one tenant at a time): the employer's site on `<tenant>.varbi.com` renders every open job in one table — no page, no count stated, the table is the board — and the job page carries the advert with a «quick info» table whose contact and union rows are withheld; `varbi.py`

<!-- verified: 2026-09-20 -->

<!-- hosts: su.varbi.com, solna.varbi.com, regionstockholm.varbi.com -->
<!-- host-forms: {tenant}.varbi.com -->
<!-- host-forms-basis: read — `varbi.py:DOMAIN` with the tenant as its subdomain (`tenant_of`), one per run, every other host refused before the gate; the vendor's `varbi.com` (0 bytes in 200 on `/` and `/robots.txt`, 13.09) and `career.varbi.com` are not boards · 2026-09-20 -->
<!-- script: varbi.py -->
<!-- countries: * -->
<!-- content: measured · **three tenants with jobs, 2026-09-20 13:5x–14:0x UTC, the declared client, the guard on the exact path first, two lists read twice. Rules (`su.varbi.com/robots.txt`, 272 B, the same on `solna`): seven named crawlers refused `/` (SemrushBot, SemrushBot-SA, Teoma, Gigabot, Robozilla, dotbot, AhrefsBot), nothing written for `*`, no Crawl-delay. The tenant's root is the list (200; Stockholm University `su` 181 907 B ×2 — md5 31235648a634 / be3d71b2c77f, a token moves —, Solna Stad `solna` 116 487 B ×2, Region Stockholm `regionstockholm` 738 064 B): `<table id="table-position">` with one `<tr>` per job — `td.pos-title` (a link to `/se/what:job/jobID:<id>/`), `pos-town`, `pos-subcompany`, `pos-ends` — su 66 rows / 66 ids, solna 16 / 16, regionstockholm 476 ids in one page; no pager, no count anywhere on the page (`what:findjob` is a filter form over the same table); `/en/` is the English path. The job page `/se/what:job/jobID:969973/` (200, 106 620 B): `<h1>`, `div.job-desc` (HTML), `table.quick-info` rows `quick-info-<key>` — type-of-employment, hours, pay, number-of-positions, working-hours, town, county, country («Sverige»), reference-number, published, ends — and `quick-info-union-representative` (a `contactList` of unions with telephones and e-mails; the contact persons' row is the same shape), the apply button to `what:login/…/apply:1` (an account); no JobPosting. `varbi.py jobs` live: su 66 emitted, solna 16, «the table is the board: no count is stated anywhere»** · 2026-09-20 -->
<!-- witness: none — no count is stated on the page; `varbi.py jobs` prints the table's length and says so · 2026-09-20 -->
<!-- route: http · 82 · 2026-09-20 -->

**Issue #469 (opened under #406, the ATS families). The premise of 13.09
(`varbi.com` 0 bytes in 200) concerns the vendor's apex; the tenants live
on `<tenant>.varbi.com` and are open — found by the signature in a search
engine on 2026-09-20 (`su`, `solna`, `regionstockholm`, `regionostergotland`,
`arbetsformedlingen`, `vgregion`, `lansstyrelsen`); two measured twice and
a third once, as the README's two-tenant rule asks.** Rank: the pilot's
order of 2026-09-20 12:5x, after #468.

## What Varbi is, and where its tenants live

Varbi (Trollhättan) is a Swedish ATS used by universities, regions,
municipalities and agencies (Arbetsförmedlingen, Region Stockholm, Stockholm
University). The employer's site is `<tenant>.varbi.com`: the root lists the
jobs, `/<lang>/what:job/jobID:<id>/` is a job, `what:login/…/apply:1` the
application. **The user names the tenant by its subdomain**, its host or
the site's URL.

## The route — one table, one request

```
GET https://su.varbi.com/                                 200 — #table-position, 66 rows, no count, no pager
GET https://su.varbi.com/se/what:job/jobID:969973/        200 — the job (the `ad` command)
GET https://regionstockholm.varbi.com/                    200 — 476 ids in one page
```

**No count is stated anywhere on the page**, so `jobs` prints the table's
length as the count and says so — the same form as SparkHire (#452),
where the list is the board; a page without the table dies with 6 (the
vendor's apex answers 0 bytes in 200). Two seconds between requests are
ours; the rules write no Crawl-delay.

## What the adapter emits, and withholds

`jobs --tenant <name> [--lang se|en] [--country-code]`: id, url, title,
place (the town), department, closes. **The list states towns, not
countries: `--country-code` stamps the rows and the note says so.** `ad
--url`: title, place, region (county), country (from the quick info's
«Land» — «Sverige» → SE), employment_type, extent, pay, positions,
working_hours, reference, published, closes, `fields` (the tenant's own
labels), description (scrubbed), `people_rows_withheld` (which rows were
dropped).

**Withheld:** the quick info's contact and union-representative rows —
names, telephones, e-mails — never emitted (the row keys are listed
instead); e-mail addresses and telephone numbers in the description; the
application never touched; `contacts_withheld` on every record.

## Tests and mutations

`AnATSWhoseTenantSiteRendersEveryJobInOneTableWithNoCountAndWhoseJobPageListsTheContactsInItsQuickInfo`,
both ways on fixtures (the table read once, its length as the count with
the note, a repeated id, the stamp, the `/en/` path, the empty table, a
page without the table, a 404, the ad's quick info with the people rows
withheld and the description scrubbed and balanced across nested divs, a
gone job, bad addresses, other hosts refused, bad tenants). Mutation
bench on a detached copy, `python3 -B`, 8 / 8 red: duplicate ids emitted ·
a missing table read as empty · the people rows emitted · the description
not scrubbed · a nested div ending the advert · the country not mapped ·
the language path ignored · another host sent.
