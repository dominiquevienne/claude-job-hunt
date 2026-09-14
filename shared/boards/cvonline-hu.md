# Board adapter — CVOnline Hungary (`www.cvonline.hu`, Alma Career): the Finnish Jobly template on a Hungarian board, by `jobly.py --host cvonline-hu` — «5 681 ÁLLÁS VÁR» stated on 2026-09-14, the same ten seconds asked and honoured, the same card, panes and sitemap index; the employer's template body read and scrubbed

<!-- verified: 2026-09-14 -->

<!-- hosts: www.cvonline.hu, cvonline.hu -->
<!-- script: jobly.py -->
<!-- host-forms: www.cvonline.hu -->
<!-- host-forms-basis: read — every card's `about` path, sitemap row and pager link is on `www.cvonline.hu`; `jobly.py` names the host in `BOARDS["cvonline-hu"]` and builds every address on it; the ad's address is matched against the board's own shape (`/hu/allas/<slug>-<id>`, `/hu/<tier>/allas/…`) · 2026-09-14 -->
<!-- countries: HU -->
<!-- content: measured · **`/hu/allashirdetesek` states «5 681 ÁLLÁS VÁR, JELENTKEZZ MÉG MA!» in its `<h1>` (200, 174 282 B, 02:2x UTC), 20 `<article id="node-<id>">` cards a page, 284 pages counted from zero; `/hu/sitemap.xml` (200, 404 B) names two files, `?page=1` 926 867 B / 5 000 rows — 4 685 `/hu/allas/`, 162 `/hu/lite/`, 77 `/hu/premium/`, 53 `/hu/freemium/`, 14 `/hu/master/`, 6 `/hu/basic/`, 2 `/hu/standard/` (the ad under a tier prefix), lastmod 2021-11 … 2026-09-13; 40 read in 2 pages** — read by the declared client, the guard on the exact path, ten seconds apart as the rules ask (Drupal's default file, 2 189 B, `Crawl-delay: 10`, refusing `/search/` and the account pages — the same file as Jobly's, without the `apply-external` line); the ad (60 726 B) carries the same JSON-LD JobPosting as Jobly (`employmentType` and `jobLocation` as lists, an empty `baseSalary` in HUF), the same region and employment-type panes, «Frissítés dátuma: 14.09.2026», and its body in `recruiter_job_template` — the employer's own template — rather than the node's body field; **the body is scrubbed of Hungarian telephone numbers and e-mail addresses; the «Jelentkezem» link (`/hu/node/<id>/apply-external`) is never followed** · 2026-09-14 -->
<!-- witness: the listing's own «N ÁLLÁS VÁR», printed beside every walk of the list and beside the sitemap's count, never merged; a page serving page 1's cards again exits 6, as does a 200 page without one card · 2026-09-14 -->

**CVOnline Hungary is Alma Career's Hungarian board — 5 681 open
advertisements stated on the day, beside Profession.hu (`profession.md`)
and Állásportál (`allasportal.md`) — and it runs on the very template of
Alma's Finnish Jobly (`jobly.md`): one script, `--host cvonline-hu`.**
Issue #362. Measured 2026-09-14 02:27–02:31 UTC by the declared client,
the guard on the exact path before each request, ten seconds between
requests because the host asks for ten.

## The same template, named per board

```
www.cvonline.hu/robots.txt                    200, 2 189 B — Drupal's default under *: Crawl-delay: 10; Disallow /search/, /user/login/ … (Jobly's file without the apply-external line)
GET https://www.cvonline.hu/hu/allashirdetesek    200, 174 282 B — <h1>5 681 ÁLLÁS VÁR, JELENTKEZZ MÉG MA!</h1>; 20 <article id="node-<id>" about="/hu/allas/<slug>-<id>"> cards; pager ?page=1 … ?page=284
GET https://www.cvonline.hu/hu/sitemap.xml        200, 404 B — two files, lastmod 2026-09-13T22:10Z
GET https://www.cvonline.hu/hu/sitemap.xml?page=1  200, 926 867 B — 5 000 rows: /hu/allas/ 4 685, /hu/lite/allas/ 162, /hu/premium/allas/ 77, /hu/freemium/ 53, /hu/master/ 14, /hu/basic/ 6, /hu/standard/ 2
GET https://www.cvonline.hu/hu/allas/metro-muszaki-ugyeletes-1965816   200, 60 726 B — JSON-LD JobPosting; panes; <div class="recruiter_job_template"><div class="markup">…; «Frissítés dátuma: 14.09.2026»; Jelentkezem → /hu/node/1965816/apply-external
```

| named per board | Jobly (`jobly`) | CVOnline Hungary (`cvonline-hu`) |
| :-- | :-- | :-- |
| host · country · language | `www.jobly.fi` · FI · fi | `www.cvonline.hu` · HU · hu |
| the listing | `/tyopaikat` | `/hu/allashirdetesek` |
| the count | «meillä on 12 737 avointa työpaikkaa» | «5 681 ÁLLÁS VÁR» in the `<h1>` |
| the ad's address | `/tyopaikka/<slug>-<id>` | `/hu/allas/<slug>-<id>`, `/hu/<tier>/allas/<slug>-<id>` |
| the sitemap index | `/sitemap.xml` | `/hu/sitemap.xml` |
| the body | `field--name-body` | `recruiter_job_template` › `markup` |
| the date on the page | «Julkaistu» | «Frissítés dátuma:» |

Everything else is one code path: the `<article id="node-<id>">` card
with its title, date, employer, location and terms; the pager counted
from zero with the guard against a pager that does not page; the region
and employment-type panes; the JSON-LD JobPosting with its lists; the
sitemap index in files; `Crawl-delay: 10` honoured through `_pace.Pace`.
**A card whose address is not the board's ad shape — a company page, a
tier without the slug — is not a card; `source` and `ledger_id` carry
the board's key; `ad --url` reads the board off the address and refuses
any other host before a request.**

```
jobly.py list --host cvonline-hu --pages 2
[jobly] 40 emitted over 2 page(s) of 20, the listing states 5 681 — walked by request (--pages/--limit), 10 s a page as the host asks; not a shortfall.
jobly.py ad --url https://www.cvonline.hu/hu/allas/metro-muszaki-ugyeletes-1965816
{"source": "cvonline-hu", "country": "HU", "id": "1965816", "title": "Metró műszaki ügyeletes", "employer": "BKV Zrt.", "employment_type": ["FULL_TIME"], "employment_type_term": "Teljes munkaidős", "locations": ["Budapest"], "category": "Szakmunka / fizikai munka", "posted": "2026-09-14", "valid_through": "2026-11-13", "description": "…", "contacts_withheld": true}
```

**The body is the employer's template** — a banner image, the
employer's own headings, the tasks, the requirements, and often the way
to apply («fényképes önéletrajz beküldésével», a telephone to be called
back on): scrubbed of Hungarian telephone numbers (`+36`, `06`) and
e-mail addresses, like Jobly's Finnish ones; `contacts_withheld` on every
record; the «Jelentkezem» link is an application action and is never
followed.

## Configuration

```yaml
boards:
  cvonline-hu:
    enabled: true
    host: cvonline-hu     # jobly.py's board key
    pages: 5              # 20 a page, ten seconds a page
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `host` | yes | `cvonline-hu` (or `www.cvonline.hu`) |
| `pages` | no | 5 by default; the listing had 284 on the day |

No credentials, no browser, no login. `sitemap` is four requests (40 s);
`list` one a page; `ad` one.

## What is not established

- **The sitemap's total** — the first file's 5 000 rows were read on the
  day and the second was not; `sitemap` reads both and prints the count
  against the listing's.
- **The tiers** — `/hu/premium/`, `/hu/lite/` … prefix the same ad
  shape; whether a tier changes the page's markup was not seen (the one
  ad read was plain `/hu/allas/`).
- **The English front** (`/en/`) — not read.
- **Whether every body is a template** — one ad read; the node's body
  field is tried first, the template second, and a page with neither
  exits 6.

## 2026-09-14 — shipped

`list`: 40 in 2 pages against 5 681 stated, every card with an employer,
a date and a location, `source` `cvonline-hu` on all; `ad`: one, the
template body read, no number or address in the output. Two tests; six
mutations on a detached worktree (`python3 -B`), six red — the host's
listing path not used, the key not on the record, the card's address not
checked against the board's ad shape, the template body not read, the
Hungarian number not scrubbed, the unknown host accepted.
