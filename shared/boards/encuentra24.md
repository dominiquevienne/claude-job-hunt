# Board adapter — Encuentra24 (twelve countries, one host)

<!-- verified: 2026-09-03 -->

<!-- hosts: www.encuentra24.com -->
<!-- script: encuentra24.py -->
Central American and Caribbean classifieds with a real jobs section. **Not a
country per domain: one host with a country-and-language prefix** —
`/panama-es/`, `/costa-rica-en/` — so there is no host enumeration to do.

**No key, no cookie, no browser.** The ad page carries a full `JobPosting` in
JSON-LD.

**Everything below was verified against the live site on 2026-09-03.**

## `robots.txt` names the countries, and they are not composable

**10 084 bytes, one `User-agent: *` group, no AI agent named anywhere** — open
by absence of a policy rather than by permission. And it declares **twenty-four
prefixes**, one `Disallow` each:

```
chile-en  chile-es  colombia-en  colombia-es  costa-rica-en  costa-rica-es
dominican-en  dominicana-es  el-salvador-en  el-salvador-es  espana-es
guatemala-en  guatemala-es  honduras-en  honduras-es  nicaragua-en
nicaragua-es  panama-en  panama-es  paraguay-en  paraguay-es
puerto-rico-en  puerto-rico-es  spain-en
```

**Read them from the file, never build them.** `dominican-en` sits beside
`dominicana-es`, and `spain-en` beside `espana-es`: **anything that pairs
`<country>-es` with `<country>-en` loses both.** `encuentra24.py prefixes`
re-reads the file every run and says when it has changed.

This is `shared/robots-policy.md`'s *a robots.txt is a source of discovery*
(#74) doing the work an adapter would otherwise do by guessing.

## The two languages are one corpus, and the ledger key must say so

Measured: `panama-es` and `panama-en` return **the same twenty ads**;
`dominicana-es` and `dominican-en` **the same twelve**.

**So the ledger id is keyed on the country, not the prefix** —
`encuentra24:panama:32343238` — because `…:panama-es:…` and `…:panama-en:…`
would put one advertisement in the ledger twice. That is the job-room defect
of the same day arriving by another road.

**The page size differs between them**: 20 ads a page under `-es`, **30**
under `-en`, on the same corpus. Reported rather than assumed; a hard-coded 20
becomes a wrong total.

## Past the last page it serves page one, with `200`

```
pages 1, 2, 3       disjoint — 60 distinct ads
page 50             page 1's twenty ads, exactly
page 500            page 1's twenty ads, exactly
```

Binary search puts Panama's last real page at **30**, about 600 ads.

**An adapter that trusts the status code paginates for ever — and re-emits
page one's ads as new at every page past the end.** So `search` compares every
page against the first and stops when they match. That is `philjobnet.md`'s
rule arriving through a different door: **a page that answered `200` has not
necessarily advanced**, and this site says *"there is no page 31"* by handing
back page 1.

## The pagination is a path, and the site documents it itself

```
GET …/empleos-ofertas-de-trabajos?page=2
    → 308  Location: …/empleos-ofertas-de-trabajos.2?page=2
```

**The redirect is the documentation.** The shape is `<category>.<n>`.

## Three names that look right and are not

**1. `/panama-es/trabajos` and `/panama-es/empleo` both answer `200`** — with
~97 KB titled *"Últimas novedades en Panamá"*, the site's generic latest
listings. Only `empleos` reaches the jobs section, and only
`empleos-ofertas-de-trabajos` reaches the offers.

**2. The category slug is language-specific and is not a translation.**
`empleos-ofertas-de-trabajos` under `-es`, `jobs-work-employ-job-offers` under
`-en`. **`jobs-job-offers` — the obvious guess — redirects to the site root**:
a guessed name that answers, which is worse than one that does not (#72).

**3. The English listing links to ads outside its own category.** Filtering on
the prefix alone returned **30 ids where the Spanish page returned 20**, and
ten of them were not jobs. The category is part of the filter.

## What an ad yields

A `JobPosting` in JSON-LD, server-rendered:

```
title · hiringOrganization · jobLocation (locality, region) · datePosted
employmentType · industry · occupationalCategory · description
qualifications · responsibilities · skills · baseSalary
```

**`baseSalary` is free text, not an amount.** `"Salario más bono $$"` on the
measured ad. The card emits `salary_text` and `salary_is_structured`, and
**nothing computes on it** — this is the shape `never-fail-silently.md`
catalogues as a field that is present, plausible and useless.

## The corpus is classifieds, and the card should not pretend otherwise

Panama's offers include *niñera*, *cocinera*, *asesores de ventas*,
*llanteros*. **This is a general classifieds site with a jobs category**, not a
professional board — which is worth knowing before a scan is scored against it,
and is exactly why the adapter exists rather than not: a market this plugin
would otherwise not reach at all.

**Spain declares its prefixes and its offers category is empty** — `espana-es`
and `spain-en` returned **0 ads each**, measured. Declared is not populated.

## Configuration

```yaml
boards:
  encuentra24:
    enabled: true
    prefixes: [panama-es, costa-rica-es]
    delay: 1.0
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `prefixes` | yes | From `encuentra24.py prefixes`. **One language per country is enough** — the other is the same corpus |
| `pages` | no | The sweep stops on its own when a page repeats page 1 |
| `delay` | no | Seconds between pages, default 1.0 |

No credentials, no login, no browser.

## Zero-shaped answers

**1. Page 31 answering `200` with page 1.** The headline.

**2. `trabajos` and `empleo` answering `200` with the wrong section.**

**3. A guessed English slug that redirects to the root** instead of 404ing.

**4. `baseSalary` present and not a number.**

**5. A bare request answering `403`** — the host sniffs `Accept` and
`Accept-Language`; `robots.txt` refuses nothing here.

**6. Spain's category, populated with nothing.** Declared is not populated.

## Applying

Through the ad URL, in the user's own browser. **The plugin does not create
accounts and does not fill credential fields.**

## Pace

No published limit, no `429` over about 80 requests at 1 s apart. A listing
page is 350–400 kB and an ad ~420 kB, so the sweep is heavy in bytes and
modest in requests: a country is about 30 requests.

## Verification

```bash
S=skills/job-scan/scripts/encuentra24.py
python3 $S prefixes                                  # 24, read from robots.txt
python3 $S search --prefix panama-es --limit 5
python3 $S ad --url "https://www.encuentra24.com/panama-es/empleos-ofertas-de-trabajos/asesores-de-ventas-bilingue/32412571"
```
