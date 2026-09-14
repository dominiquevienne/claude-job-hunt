# Board adapter — Randstad Czechia (`www.randstad.cz`): the French platform's front by `randstadfr.py --host cz` — 348 advertisements in the board's own-language job-detail files on 2026-09-14 (344 public, 4 internal), the English copies set aside; the agency as employer on every ad; the consultant the description names withheld

<!-- verified: 2026-09-14 -->

<!-- hosts: www.randstad.cz -->
<!-- script: randstadfr.py -->
<!-- host-forms: www.randstad.cz -->
<!-- host-forms-basis: read — the sitemap index and every row are on `www.randstad.cz`; `randstadfr.py` names the host in `BOARDS["cz"]` and rewires its index on it before any request · 2026-09-14 -->
<!-- countries: CZ -->
<!-- content: measured · **`/sitemaps/sitemap.xml` (200) names 24 files: 5 job files (jobdetails, jobdetails-internal, joblistings and 13 sector listings) in Czech under sitemaps/jobs/, the same three under sitemaps/jobs/en/; the board's own-language `sitemap-jobdetails.xml` carries 344 `/jobs/<slug>_<town>_t-<n>/` rows (281 distinct lastmod for 344 rows) and `sitemap-jobdetails-internal.xml` 4 under `/pridejte-se-k-nam/volna-mista/` — 348 read as the inventory; the `/en/` files carry the same ads again and are set aside and said** — read by the declared client, the guard on the exact path (the rules, `*` open on the sitemaps and the ads, name the index); the ad (200, ~300 KB) carries the platform's JobPosting — `hiringOrganization` Randstad, `identifier.value` `t-10682`, locality and region, `employmentType`, `baseSalary` «40 000–45 000 CZK MONTH» on an internal one, «0» on the sample, `datePosted`, `validThrough`, `industry`; **the page and the description name the consultant with e-mail and telephone — the description is scrubbed, the page's contact block never read** · 2026-09-14 -->
<!-- witness: none the site states — the platform prints no count; the sitemaps' row count is the inventory, printed on every run beside the ads read; a job-detail file that parses to zero rows exits 2 (a read failure, never an empty board) · 2026-09-14 -->

**Randstad Czechia is the staffing network's national front on Randstad's global
platform — the very stack `randstadfr.py` reads for France: one script,
`--host cz`.** Issue #357. Measured 2026-09-14 02:5x UTC by the
declared client, the guard on the exact path before each request.
Beside Jobs.cz (`jobscz.md`), Prace.cz (`pracecz.md`), the Úřad práce (`uradprace.md`), StartupJobs (`startupjobs.md`), it is the interim
network's own inventory, the client employer never named.

## The same platform, named per board

```
www.randstad.cz/robots.txt                          200 — the platform's file; Sitemap: /sitemaps/sitemap.xml
GET https://www.randstad.cz/sitemaps/sitemap.xml    200 — 24 files: 5 job files (jobdetails, jobdetails-internal, joblistings and 13 sector listings) in Czech under sitemaps/jobs/, the same three under sitemaps/jobs/en/
GET https://www.randstad.cz/sitemaps/jobs/sitemap-jobdetails.xml            200 — 344 rows /jobs/<slug>_<town>_t-<n>/
GET https://www.randstad.cz/sitemaps/jobs/sitemap-jobdetails-internal.xml   200 — 4 row(s) /pridejte-se-k-nam/volna-mista/… — Randstad's own vacancies
GET https://www.randstad.cz/sitemaps/jobs/en/sitemap-jobdetails.xml              the same 344 ads in English — set aside, never read twice
GET https://www.randstad.cz/jobs/ridicka-vzv_mosnov_t-10682/   200 — <script type='application/ld+json'> JobPosting: hiringOrganization Randstad, identifier t-10682, baseSalary in CZK
```

| named per board | France (`fr`, default) | Czechia (`cz`) | Hungary (`hu`) |
| :-- | :-- | :-- | :-- |
| host · country | `www.randstad.fr` · FR | `www.randstad.cz` · CZ | `www.randstad.hu` · HU |
| the job-detail files read | every `jobdetails` file | `sitemaps/jobs/` (Czech) — `/en/` set aside | `sitemaps/jobs/hu/` — `/en/` set aside |
| the language asked for | fr | cs | hu |
| `source` / ledger key | `randstad-fr` | `randstad-cz` | `randstad-hu` |

Everything else is one code path: the index, the job-detail files with
their batched `lastmod`, `discover` (the rows, free) and `search` (the
ads read, `--ville` on the URL's town, `--since`, `--limit`,
`--max-read`), the JobPosting read through `_ldjson` (the platform
writes the script tag with single quotes), the agency flagged as the
employer, a zero salary read as none. **`--departement` is the French
postcode and is refused on this front.** The `-internal` file's rows
are read and carry `internal: true` — Randstad recruiting for itself.

```
randstadfr.py search --host cz --limit 3
[randstad-cz] 2 job-detail file(s) in another language set aside — the same ads twice: en/sitemap-jobdetails-internal.xml, en/sitemap-jobdetails.xml
[randstad-cz] 348 ads in the sitemaps
[randstad-cz] 3 ads returned, 3 read
```

## The consultant in the description

**The description names the consultant — «Kapcsolattartó / Information:
<name> - <e-mail> - <telephone>» on the Hungarian ads, the contact block
on the Czech page — and the record emits it scrubbed of e-mail addresses
and French, Czech and Hungarian telephone shapes; `contacts_withheld`
on every record. This is a correction for the French front too, which
emitted the description as written until this day.** The client
employer is described and never named — `employer_is_the_agency` on
every record, as on `randstad-fr.md`.

## Configuration

```yaml
boards:
  randstad-cz:
    enabled: true
    host: cz
    limit: 50             # search: ads read from their pages
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `host` | yes | `cz` (or `www.randstad.cz`) |
| `ville` / `since` / `limit` | no | as on the French front; one of them is required by `search` |

No credentials, no browser, no login. `discover` is three requests;
`search` adds one an ad, 0.6 s apart.

## What is not established

- **A count the site states** — the platform prints none the client
  reads; the sitemap's rows are the inventory.
- **Whether the `/en/` copies ever differ** — same ids, same count on
  the day; set aside, not compared row by row.
- **The joblistings sitemaps** — sector listing pages, not ads; not read.
- **The salary figures' scale** — the site writes what the site writes
  (a Hungarian minimum of «600» a month); emitted as written, not
  interpreted.

## 2026-09-14 — shipped

`discover`: 348 rows; `search --limit 3`: three ads read, the consultant's
address and number scrubbed, none in the output. Two tests for the hosts;
six mutations on a detached worktree (`python3 -B`), six red — the
other-language files read too, the key not on the record, the internal
flag not carried, the scrub dropped, the unknown host accepted,
`--departement` allowed on the Czech front.
