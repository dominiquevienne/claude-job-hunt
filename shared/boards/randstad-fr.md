# Board adapter — randstad.fr

<!-- hosts: www.randstad.fr -->

**6 755 ads** — the second French interim network here, after `adecco.md`. Half
its sibling's volume, and **better data on every axis that matters**.

**Everything here was verified against the live site on 2026-09-01.**

Not to be confused with `randstad.md`, which is `randstad.ch`: a different
site, a different structure, and the Swiss adapter does not apply here.

## Better than its sibling, field by field

| | `adecco.md` | this one |
| :-- | :-- | :-- |
| `postalCode` | **empty on every ad** | **on every ad** |
| town in the URL | truncated department, unusable | **matches the ad, 22 of 22** |
| `currency` | `"France "` — a country | **`EUR`** |
| `employmentType` | *"Temps plein"* or the string `"null"` | **`CONTRACTOR`** — the schema.org vocabulary |
| `validThrough` | a date, 46–62 days out | **absent, and honestly so** |
| `identifier` | absent | on every ad |
| description | median 4 504 characters | median 1 938 |

Only the last line favours Adecco. Everything else here is what the schema
asks for, spelled the way it asks.

**And the one thing they share:** `hiringOrganization` is **`Randstad France`**
on every ad. The client is described in the body and never named, so there is
no company to research before applying and no key to deduplicate against an
employer's own ATS. That is what an agency board is, and the terms
`michaelpage.md` and `adecco.md` already ship on.

## Access

```
GET /robots.txt                       → Sitemap: //www.randstad.fr/sitemaps/sitemap.xml
GET /sitemaps/sitemap.xml             → 32 sitemaps, 3 of job details
GET /sitemaps/jobs/sitemap-jobdetails.xml           5 000 ads
GET /sitemaps/jobs/sitemap-jobdetails-2.xml         1 719
GET /sitemaps/jobs/sitemap-jobdetails-internal.xml     36
GET /emploi/<poste>_<ville>_<ref>/    → the ad
```

`robots.txt` carries **93 `Disallow` rules** — faceted search
(`/emploi/*/cdi/`, `/emploi/*/interim/`, `/*/km-`, `/*/postcode-`), the CMS,
and the apply paths (`/*/apply/`, `/*/postuler/`). **None of them touches the
ad detail path**, which is what this adapter reads, and the apply paths are
never requested.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/randstadfr.py" \
  search --ville royan
```

**No browser, no account, no key.**

## Configuration

```yaml
boards:
  randstad-fr:
    enabled: true
    searches:
      - { ville: "royan" }
      - { ville: "lyon" }
    departements: ["33"]
    since: "2026-09-01"
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `ville` | strongly recommended | **Free** — the town is in the URL and it is reliable. See trap 2 |
| `departement` | no | Two characters, read off the ad's postcode. **Costs a fetch per candidate** |
| `since` | no | On `lastmod`, which is batched — see trap 3 |
| `max_read` | no | Stops a department sweep walking the whole sitemap. Default 120 |

## Traps

**1. The `ld+json` script tag uses single quotes.** This one nearly shipped
broken. The site writes:

```html
<script type='application/ld+json'>
```

A pattern requiring `type="application/ld+json"` matches **nothing**, and the
adapter then reports `json_ld: false` on **every ad** — a total parsing failure
wearing the face of *"this board publishes no structured data"*. It was caught
by running the adapter against one ad and finding a row with four keys in it.

Two things follow, and the second is the more useful:

- Match the attribute, not the punctuation around it. Quote style is not a
  contract.
- **When a page contains `JobPosting` and the parser finds none, that is a
  broken reader, not a board without structured data.** The adapter now checks
  exactly that and exits with an error naming the markup, rather than emitting
  a row that says the ad had nothing in it.

**2. The town in the URL is reliable — unlike Adecco's.** `<poste>_<ville>_<ref>`,
and on 22 of 22 the URL's town and the ad's `addressLocality` were the same
place once accents and apostrophes are folded away: `aire-sur-ladour` for
*Aire-sur-l'Adour*, `pleudihen-sur-rance` for *Pleudihen-sur-Rance*.

So `--ville` filters **before any fetch and costs nothing**, where
`adecco.md`'s equivalent could not be trusted at all. Use it. The department is
a different matter: it is only on the ad, so `--departement` reads from the top
of the sitemap until it finds matches — which is why there is a `--max-read`
cap, and why a run that finds nothing says how many it read and what to do
instead.

**3. `lastmod` is batched, not per ad.** **535 distinct values across 5 000
URLs** — roughly nine ads to a timestamp. That places it between
`figaro-emploi.md`, where 30 000 entries share one build stamp and the field is
worthless, and `wttj.md`, where 7 691 values in 10 000 make it a genuine per-ad
date. Here it is real enough to skip a re-scan with `--since`, and too coarse
to date an ad.

**4. `maxValue` is 0 on every hourly ad.** `14 → 0 → HOUR` is an hourly rate
with no ceiling given, not a range down to nothing — the same shape as
`adecco.md`. Zero is emitted as absent, because a reader handed `14 – 0 €` will
print it. Measured: `HOUR` on 20 of 22 ads, `MONTH` on one, `YEAR` on one.

**5. `employmentType` is `CONTRACTOR` on 21 of 22.** That is correct
schema.org and it is also nearly uniform, so it carries almost no information:
interim work is `CONTRACTOR` whatever the assignment. Do not filter on it
expecting to separate CDI from mission — the distinction is in the description.

## The ad id and its URL

The id is the URL's last segment, `etancheur-fh_royan_001-at2-0006111_01c`,
and the ad also carries its own `identifier` — `001-AT2-0006111_01C`, the
agency's reference. In the ledger: `randstad-fr:<slug>`.

## Applying

`/*/apply/` and `/*/postuler/` are disallowed and never requested.
Applications go through Randstad, which needs a candidate account. **The plugin
does not create accounts and does not fill credential fields.** Hand the user
the ad URL.

## Pace, and the note on access

Three sitemap requests, then one page load per ad read. `--ville` decides how
many that is; `--delay` defaults to 0.6s and `--max-read` to 120. Everything is
fetched from paths the `robots.txt` leaves open, and the sitemaps are the ones
it advertises.
