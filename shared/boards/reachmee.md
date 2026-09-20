# Board adapter — ReachMee (Talentech's Swedish ATS, one tenant at a time): the employer's list at `web<NNN>.reachmee.com/ext/<instance>/<customer>/main?site=&lang=&validator=` is one server-rendered table with the tenant's own columns — no page, no count stated, the table is the board — and the job page carries the advert with a contact section that is withheld; `reachmee.py`

<!-- verified: 2026-09-20 -->

<!-- hosts: web103.reachmee.com, web106.reachmee.com -->
<!-- host-forms: web103.reachmee.com, web106.reachmee.com -->
<!-- host-forms-basis: read — `reachmee.py:HOST_RE` accepts any `web<digits>.reachmee.com` the list's address names (the two seen in the search engine: 103 and 106), one per run, every other host refused before the gate; the tenant is a path and a query (`/ext/<instance>/<customer>/main?site=&validator=`), never a subdomain · 2026-09-20 -->
<!-- script: reachmee.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants with jobs, 2026-09-20 14:0x UTC, the declared client, the guard on the exact path first, each list read twice. Rules: `web103.reachmee.com/robots.txt` 404 (nginx) — no file, no rules. The list (200): Linköping University `ext/I011/853/main?site=6&lang=SE&validator=c5f7…` 32 390 B ×2 same md5, Sodexo `ext/I019/731/main?site=6&validator=44e1…` 18 640 B ×2 same md5 — `<table id='jobsTable'>` with `<th id='col-N'>` labels the tenant chose (Linköping: Anställningar, Sista ans.dag, Anställningsform, Diarienummer, Ort, Affärsområde, Erfarenhetsområde; Sodexo: Tjänst, Ort, Sista ansökningsdagen, Län, Yrkesområde — the same ids across tenants: col-1 title, col-6 date, col-9 town, col-8 county, col-17 form, col-3 reference), one `<tr>` per job, the title linked to `…/job?site=&lang=&validator=&job_id=<id>`, the date cell carrying a hidden sort key and a mobile label; 43 jobs / 23 jobs; no pager, no count on the page («JavaScript måste vara påslaget» in a noscript, the table is served regardless). The job page `…/job?…&job_id=29920` (200, 15 694 B): `h1#jobad-heading`, `p.extid` (the town, «Referensnummer LiU-2026-04136»), `div.jobad-body` (HTML), `section.contact` with `contact-person` blocks (name, position, telephone, e-mail — two on this page), a login to apply; no JobPosting. `reachmee.py jobs` live: Linköping 43 emitted, Sodexo 23, «the table is the board: no count is stated anywhere»** · 2026-09-20 -->
<!-- witness: none — no count is stated on the page; `reachmee.py jobs` prints the table's length and says so · 2026-09-20 -->
<!-- route: http · 66 · 2026-09-20 -->

**Issue #470 (opened under #406, the ATS families). The premise of 13.09
(`www.reachmee.com` → `talentech.com`) concerns the vendor's site; the
tenants live on `web103` / `web106.reachmee.com` and were found by the
signature `reachmee.com/ext/…/main?site=` in a search engine on 2026-09-20
(Linköping University, Sodexo, ESV, FMV, Sweco, BDX, SiS, Atea, PTS); two
measured twice, as the README's two-tenant rule asks.** Rank: the pilot's
order of 2026-09-20 12:5x, after #469.

## What ReachMee is, and where its tenants live

ReachMee (Talentech, Stockholm) is a Swedish ATS used by agencies,
universities and companies. The employer's site links its list on
`web<NNN>.reachmee.com/ext/<instance>/<customer>/main?site=<n>&lang=SE&validator=<hash>`;
**the `validator` is the tenant's public list key, printed in every
visitor's address** — the SparkHire shape (#452): the plugin replays the
address the employer publishes, and nothing else. **The user names the
tenant by that address**, as the employer's site links it; a composed
address without its validator is refused before any request.

## The route — one table, one request

```
GET https://web103.reachmee.com/ext/I011/853/main?site=6&lang=SE&validator=c5f7…            200 — #jobsTable, 43 rows, no count, no pager
GET https://web103.reachmee.com/ext/I011/853/job?site=6&lang=SE&validator=c5f7…&job_id=29920  200 — the job (the `ad` command)
```

**No count is stated anywhere on the page**, so `jobs` prints the table's
length and says so; a page without the table (a wrong validator or site)
dies with 6. The job address is rebuilt from its four parameters —
tracking such as `rmref=` dropped. Two seconds between requests are ours.

## What the adapter emits, and withholds

`jobs --tenant "<list address>" [--country-code]`: id, url, title, place
(town), region (county, when the tenant shows it), closes, employment_type,
reference, and `fields` — the tenant's own column labels and values. **The
list states towns and counties, not countries: `--country-code` stamps the
rows and the note says so.** `ad --url`: title, place, reference,
description (scrubbed), `contact_section_withheld`.

**Withheld:** the job page's contact section (names, positions,
telephones, e-mails); e-mail addresses and telephone numbers in the advert;
the application (a login); `contacts_withheld` on every record.

## Tests and mutations

`AnATSWhoseListAddressCarriesItsOwnValidatorAndRendersOneTableWithTheTenantsColumnsAndNoCount`,
both ways on fixtures (the address replayed as given, the columns mapped by
id and kept by label, a repeated job_id, the sort key and the mobile label
not read as values, the stamp, the empty table, a page without the table,
a 404, the ad with the contact section withheld and the prose scrubbed and
balanced across nested divs, tracking dropped, bad addresses, other hosts
refused, composed tenants refused). Mutation bench on a detached copy,
`python3 -B`, 10 / 10 red: duplicate ids emitted · a missing table read as
empty · the columns not mapped · the sort key read as a value · the mobile
label read as a value · the description not scrubbed · a nested div ending
the advert · tracking kept in the job address · another host sent · the
validator not required.
