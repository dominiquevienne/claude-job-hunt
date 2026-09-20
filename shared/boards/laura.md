# Board adapter — LAURA Rekrytointi (a Finnish ATS, one tenant at a time): the employer's careers site on `<tenant>.rekrytointi.com` serves its open-jobs list as a server-rendered table with its count in the page, and a subdomain that is no tenant answers 200 with the vendor's own site; `laura.py`, the session token never emitted

<!-- verified: 2026-09-20 -->

<!-- hosts: tuni.rekrytointi.com, finnlines.rekrytointi.com, pingviini.rekrytointi.com, laurarekrytointi.rekrytointi.com -->
<!-- host-forms: {tenant}.rekrytointi.com -->
<!-- host-forms-basis: read — `laura.py:DOMAIN` with the tenant as its subdomain (`tenant_of`), one per run, every other host refused before the gate; the vendor's `laura.fi` is not a board · 2026-09-20 -->
<!-- script: laura.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants with jobs and one former tenant, 2026-09-20 13:2x UTC, the declared client, the guard on the exact path first, each list read twice. Rules (`tuni.rekrytointi.com/robots.txt`, the same file on the three): `Amazonbot`, `meta-externalagent`, `ClaudeBot`, `SemrushBot` refused `/`; `Yandex` and `AhrefsBot` refused `/list/` with Crawl-delay 2 and `Clean-param: rspvt`; `User-agent: *` refused `/list/` only — the list lives under `/paikat/`, `Claude-User` is not named (the decision of 2026-09-07: the `*` group applies), no Crawl-delay for `*`. The list `/paikat/index.php?o=A_LOJ&list=1` (200): Tampere University `tuni` 37 768 B ×2, same md5, «Avoimia työpaikkoja: 20», 20 rows (columns Name, ApplyEndDate, Department); Finnlines 27 655 B ×2, same md5, «16», 16 rows (Name, ApplyEndDate; `lang=en` gives «Open jobs: 16» and English labels); `pingviini` 76 260 B ×2, same md5 — the vendor's marketing page (title «Valitse sujuvampi rekrytointi Lauran avulla – Laura.fi»), no list: a subdomain that is no tenant is served 200, so the adapter checks for the list's markup. Rows are `<tr class='odd'|'even'>` with `<td class='col_<Column>'><a href='/paikat/index.php?jid=<id>&key=&o=A_RJ&rspvt=<session>'>`, the page's «direct link» being `?jid=<id>&o=A_RJ`; no pager seen. The job page `?o=A_RJ&jid=3160` (200, 56 843 B): `<h1>`, `job_description` (HTML, «Lisätietoja» with the contact's name and e-mail — the address scrubbed), `job_start_end_times` (start 2026-08-28 15:15, end 2026-09-20 23:59), the employer's name in the logo's alt («Tampereen yliopisto»), the application at `?o=A_A` (an account); no JobPosting. `laura.py jobs` live: tuni 20 emitted, states 20; finnlines 16 = 16; pingviini exit 6** · 2026-09-20 -->
<!-- witness: the page's own `result_count` («Avoimia työpaikkoja: N» / «Open jobs: N») — `laura.py jobs` prints it beside the emitted count · 2026-09-20 -->
<!-- route: http · 36 · 2026-09-20 -->

**Issue #466 (opened under #406, the ATS families). Tenants found by the
family's signature `rekrytointi.com/paikat/index.php?o=A_LOJ` in a search
engine on 2026-09-20 — `tuni` (20), `finnlines` (16), `fca`, `rtkpalvelu`,
`laurarekrytointi` (the vendor's own, 1) — two with jobs measured, as the
README's two-tenant rule asks; `pingviini`, listed by the engine, is no
tenant any more.** Rank: the pilot's order of 2026-09-20 12:5x, after #465.

## What LAURA is, and where its tenants live

LAURA Rekrytointi (Laura Rekrytointi Oy, Helsinki) is a Finnish ATS whose
candidate side is `<tenant>.rekrytointi.com/paikat/` — a PHP application
with `o=` actions: `A_LOJ` the open-jobs list (`list=` the tenant's list
id, `lang=` fi / en / se), `A_RJ` a job, `A_A` the application, `A_L` the
login. **The user names the tenant by its subdomain** (`tuni`), its host or
the list's URL. The employer's own site links to it.

## The route — one server-rendered table

```
GET https://tuni.rekrytointi.com/paikat/index.php?o=A_LOJ&list=1       200 — «Avoimia työpaikkoja: 20», 20 rows
GET https://tuni.rekrytointi.com/paikat/index.php?o=A_RJ&jid=3160      200 — the job (the `ad` command)
GET https://pingviini.rekrytointi.com/paikat/index.php?o=A_LOJ&list=1  200 — laura.fi's marketing page: not a tenant, exit 6
```

**`rspvt` is a session token** — every link on the page carries one, the
tenants' own rules mark it `Clean-param` — and the adapter neither emits
nor replays it: the job's address is rebuilt as the page's «direct link»
spells it. No pager was seen on either tenant (20 of 20, 16 of 16); a list
shorter than its count is reported short, not walked blind. Two seconds
between requests are ours.

## What the adapter emits, and withholds

`jobs --tenant <name> [--list N] [--lang] [--country-code]`: id, url,
title, department, closes, place (when the tenant shows a location
column), and `fields` — the tenant's own column labels («Hakuaika
päättyy», «Tiedekunta/Yksikkö») and values. **The list states no country;
`--country-code` stamps the rows and the count line says so.** `ad --url`:
title, company (from the logo), posted and closes (the application
period), language, description (scrubbed).

**Withheld:** e-mail addresses and telephone numbers in the description
(the «Lisätietoja» contact); the session token; the application never
touched; `contacts_withheld` on every record.

## Tests and mutations

`AnATSWhoseTenantSubdomainServesAServerRenderedTableWithItsCountAndWhoseNonTenantsAnswerWithTheVendorsSite`,
both ways on fixtures (the count and the labels, the address without the
token, `--list`/`--lang`, the vendor's site as a non-tenant, a short list,
the empty list, a 404, the ad's period and employer and scrubbed contact, a
non-LAURA page, bad addresses, other hosts refused, bad tenants). Mutation
bench on a detached copy, `python3 -B`, 7 / 7 red: the session token kept
in the address · the vendor's site read as an empty list · the count
ignored · the labels not the tenant's · the description not scrubbed ·
another host sent · the country stamp dropped.
