# Board adapter — adecco.com (France)

<!-- hosts: www.adecco.com -->
<!-- script: adecco.py -->
<!-- countries: FR -->

**13 293 French ads** — not the 20 000 the home page advertises. That number is
marketing; this one is counted, from the country sitemap the site's own
`robots.txt` declares.

The largest interim network in France: production, logistics, maintenance,
building trades, driving. **No browser, no account, no key.**

**Everything here was verified against the live site on 2026-09-01.**

## The country is in the filename

```
GET /robots.txt                        → Sitemap: …/jobsindex.xml
GET /jobsindex.xml                     → 59 country sitemaps
GET /sitemap-jobs-france-fr.xml        → 13 293 ads + a per-ad lastmod
GET /fr-fr/offres-emploi/<slug>/<id>   → the ad, JSON-LD JobPosting
```

`robots.txt` closes infrastructure paths — `/data/`, `/sitecore*/`, `/temp/` —
and leaves `/fr-fr/offres-emploi` open. **`sitemap-jobs-france-fr.xml` names
its country in the file name**, which is the cleanest geography in this
repository: nothing to mistake for a locale, unlike `wttj.md`, where `/fr/`
turned out to mean the language.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/adecco.py" \
  search --ville lorient --limit 20
```

## Configuration

```yaml
boards:
  adecco:
    enabled: true
    searches:
      - { ville: "lorient" }
      - { region: "Morbihan" }
    since: "2026-09-01"
    pages: 3
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `ville` | one narrowing | **Free** — matches the URL slug, before any fetch |
| `region` | one narrowing | The department spelled out. **Costs one fetch per candidate** — see trap 1 |
| `since` | one narrowing | On the sitemap's `lastmod`, which is real per ad |
| `pages` | no | 20 ads read each |

Without a narrowing the sweep reads all 13 293 ads one at a time, and the
script refuses rather than starting.

## What the ads are worth, and what they are not

**Every ad names `adecco` as the employer** — on all 17 measured. That is the
nature of an agency board and the terms `michaelpage.md` already ships on:
there is no company to research beforehand and no key to deduplicate against an
employer's own ATS. The client is sometimes described in the body — *"pour l'un
de ses clients spécialisé dans la fabrication de plats préparés"* — and never
named. The adapter emits `company: "adecco"` with
`employer_is_the_agency: true` rather than letting the field pass for a
workplace.

Against that:

| Field | Rate | Example |
| :-- | :-- | :-- |
| `locality` / `region` | every ad | LORIENT / Morbihan |
| **salary** | **11 of 17** | 30 300 – 38 000 Annuel, 12.46 Heure |
| `sector` | every ad | Mécanique Générale, Bâtiment - Travaux Publics |
| `description` | every ad | 3 448 – 6 681 characters, median 4 504 |
| `job_id`, `datePosted`, `validThrough` | every ad | |
| `postalCode` | **never** | the field is there and empty on every ad |

In the ledger: `adecco:<id>`, the number ending the URL.

## Traps

**1. The department in the URL is truncated, and it is ambiguous at scale.**
The slug ends with the department's *last hyphen-separated word*, so
`seine-et-marne` becomes `marne` and `indre-et-loire` becomes `loire`.
Measured across the sitemap:

| Slug ending | Ads | Departments it conflates |
| :-- | --: | :-- |
| `loire` | **1 065** | Loire, Haute-Loire, Indre-et-Loire, Maine-et-Loire, Loire-Atlantique, Saône-et-Loire |
| `garonne` | 407 | Haute-Garonne, Lot-et-Garonne, Tarn-et-Garonne |
| `marne` | 382 | Marne, Haute-Marne, Seine-et-Marne |
| `rhin` | 264 | Bas-Rhin, Haut-Rhin |

So **`--region` reads the department off the ad, never the URL**, and that
costs a fetch per candidate: a Morbihan sweep read 60 ads to keep 1. Use
`--ville`, which matches the commune in the same slug and *is* reliable, or
`--since`, and keep `--region` as a confirmation rather than a search.

**2. A quarter of the URLs carry raw UTF-8.** **3 339 of 13 293** —
`puy-de-dôme`, `côtes-darmor`, `drôme`. Requested as they stand, Python raises
an ascii codec error and a quarter of the board is lost; other clients fail
more quietly. The adapter percent-encodes the path, after which they answer
200.

**3. The sitemap writes `<lastmod>` before `<loc>`.** That is the reverse of
the usual order, and of the sitemaps `wttj.py` reads. A regex written as
`<loc>…<lastmod>` matches **nothing at all** and returns an empty board with no
error — which is how this was found. Each `<url>` block is taken whole and its
tags looked up inside it, in whatever order they come.

**4. `baseSalary` is filled far more often than it is meaningful.** It is on
every ad. It is **0–0 on 6 of 17**, and `maxValue` is **0 on every hourly ad**
— `12.46 → 0 → Heure` is an hourly rate with no ceiling, not a range down to
nothing. Zero is emitted as absent, because a reader handed `12.46 – 0 €` will
print it.

And the currency is not a currency: **`currency: "France "`** on every ad, the
country with a trailing space. Emitted as
`currency_field_holds_a_country` so nobody has to rediscover it.

**5. `employmentType` never carries the schema.org vocabulary.** It is
`"Temps plein"` in French, or the literal four-character string **`"null"`** —
which passes a truthiness test. Emitted as `contract_text`, and `"null"` is
turned into a real absence.

**6. The description arrives escaped twice.** `&#60;div class&#61;&#34;…` is
`<div class="…` written in numeric entities: one unescape yields HTML, and the
tags then have to come out. Passed through raw, a cover letter would be written
from `&#60;strong&#62;`.

### And one thing this board does right

**A retired ad answers `410 Gone`** — not a soft 404, not a 200 with an empty
page. The sitemap does list ads that have since gone, and the site says so
properly, so the sweep skips them and **reports how many** rather than hiding
the gap. After a day of boards answering 2xx for refusals, an honest 410 is
worth naming.

`validThrough` is honest too: **46 to 62 days** after `datePosted` across the
sample, nine of seventeen at 60. A real per-ad date, not the formula
`hellowork.md`, `figaro-emploi.md` and `wttj.md` all publish.

## Applying

Applications go through Adecco, which needs a candidate account. **The plugin
does not create accounts and does not fill credential fields.** Hand the user
the ad URL.

## Pace, and the note on access

One request for the sitemap, then one page load per ad read — `--ville` and
`--since` decide how many that is. `--delay` defaults to 0.6s. Nothing here is
disallowed: the sitemap is the one `robots.txt` advertises, and the ad path is
open.
