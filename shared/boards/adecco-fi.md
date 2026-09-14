# Board adapter — Adecco Finland (`www.adecco.fi` → `www.adecco.com`): the French platform's country file by `adecco.py --host fi` — 74 advertisements in `sitemap-jobs-finland-fi.xml` on 2026-09-14, the agency as employer on every ad, the consultant the description names withheld

<!-- verified: 2026-09-14 -->

<!-- hosts: www.adecco.fi, www.adecco.com -->
<!-- script: adecco.py -->
<!-- host-forms: www.adecco.com -->
<!-- host-forms-basis: read — `www.adecco.fi/` answers 301 to `www.adecco.com/fi-fi`, and every sitemap row is on `www.adecco.com`; `adecco.py` names the country's file in `BOARDS["fi"]` · 2026-09-14 -->
<!-- countries: FI -->
<!-- content: measured · **`jobsindex.xml` on `www.adecco.com` names `sitemap-jobs-finland-fi.xml` — 74 `/fi-fi/avoimet-tyopaikat/<slug>/<id>` rows, 66 distinct lastmod (200, 14 583 B)** — read by the declared client, the guard on the exact path (`www.adecco.fi/robots.txt` answers 404 — an absence, certain; the platform's file on `www.adecco.com` names `jobsindex.xml`); the ad (200, ~370 KB) carries the platform's JobPosting — `hiringOrganization` the agency (`adeccocms` / `adecco`), `jobId`, `country` FI, `addressLocality`, `employmentType` in the site's words, `datePosted`, «null» strings and zero salaries as on the French front; **the description names the consultant with e-mail and telephone («sanna…@adecco.fi» in the description on the sample) — scrubbed; `contacts_withheld` on every record** · 2026-09-14 -->
<!-- witness: none the site states — the platform prints no count a client reads (the home page's figure is marketing, as `adecco.md` says); the country file's row count is the inventory, printed on every run beside the ads read; a file that parses to zero rows exits 2 (a read failure, never an empty board) · 2026-09-14 -->

**Adecco Finland is the staffing network's national front on Adecco's global
platform — the very stack `adecco.py` reads for France: one script,
`--host fi`.** Issue #380. Measured 2026-09-14 03:1x UTC by the declared
client, the guard on the exact path before each request. beside Duunitori (`duunitori.md`), Jobly (`jobly.md`) and the public boards,
it is the interim network's own inventory, the client employer never
named.

## The same platform, one country file each

```
www.adecco.fi/robots.txt                         404 — no rules file on the country host (an absence, certain)
GET https://www.adecco.fi/                       301 → https://www.adecco.com/fi-fi
www.adecco.com/robots.txt                Sitemap: …/jobsindex.xml — 59 country files
GET https://www.adecco.com/jobsindex.xml               names sitemap-jobs-finland-fi.xml (beside sitemap-jobs-france-fr.xml …)
GET https://www.adecco.com/sitemap-jobs-finland-fi.xml   200, 14 583 B — 74 rows /fi-fi/avoimet-tyopaikat/<slug>/<id>, <lastmod> before <loc> as on the French file
GET https://www.adecco.com/fi-fi/avoimet-tyopaikat/avoin-hakemus-kainuun-alueelle-kajaani/00061763   200 — JobPosting: hiringOrganization the agency, country FI
```

| named per board | France (`fr`, default) | Norway (`no`) | Finland (`fi`) |
| :-- | :-- | :-- | :-- |
| the country file | `sitemap-jobs-france-fr.xml` | `sitemap-jobs-norway-nb.xml` | `sitemap-jobs-finland-fi.xml` |
| the language asked for | fr | nb | fi |
| `source` / ledger key | `adecco` | `adecco-no` | `adecco-fi` |
| rows on the day | 13 293 (2026-09-01) | 189 | 74 |

Everything else is one code path: `discover` (the rows, with the batched
`lastmod`) and `search` (the ads read, `--ville` on the slug, `--since`,
`--all`, `--limit`), the JobPosting read through `_ldjson`, the agency
flagged as the employer, «null» strings and zero salaries read as none,
a WAF challenge died on rather than read. **`--region` is the French
department spelled out and is refused on this front** (`--ville` or
`--all`). `--host` takes the code, the country or the hostname.

```
adecco.py search --host fi --all --limit 2
[adecco-fi] 74 ads in the Finland sitemap
[adecco-fi] 2 kept, 2 ads read
```

## The consultant in the description

**The description names the consultant — name, e-mail, telephone — on
the ads read; the record emits it scrubbed of e-mail addresses and
French, Norwegian and Finnish telephone shapes; `contacts_withheld` on
every record. This is a correction for the French front too, which
emitted the description as written until this day.** The client
employer is described and never named — `employer_is_the_agency` on
every record, as on `adecco.md`.

## Configuration

```yaml
boards:
  adecco-fi:
    enabled: true
    host: fi
    limit: 50             # search --all: ads read from their pages
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `host` | yes | `fi` (or `www.adecco.fi`) |
| `ville` / `since` / `limit` | no | as on the French front |

No credentials, no browser, no login. `discover` is one request; `search`
adds one an ad, 0.6 s apart.

## What is not established

- **A count the site states** — none a client reads; the country file's
  rows are the inventory.
- **How stale the file is** — the Norwegian sample's `datePosted` was
  2025-06-30 for a row the file still lists; `lastmod` is batched, and
  a retired ad answers 410 (counted as gone by `search`).
- **The sector field** — `industryTypeTitle` is «null» on the ads read.
- **The other 56 country files** of `jobsindex.xml` — one `BOARDS` entry
  each away; not measured.

## 2026-09-14 — shipped

`discover`: 74 rows; `search --all --limit 2`: two ads read, the
consultant's address and number scrubbed, none in the output. One test
for the two hosts; six mutations on a detached worktree (`python3 -B`),
six red — the sitemap not rewired per board, the key not on the record,
the scrub dropped, the hostname form not accepted, the unknown host
accepted, `--region` allowed on the Norwegian front.
