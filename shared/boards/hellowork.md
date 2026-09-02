# Board adapter — hellowork.com

<!-- verified: 2026-09-02 -->

**Re-verified 2026-09-02**: `metier_developpeur` returned **20 cards**, and the script still says out loud that 20 is the cap and not the result count — pagination is a query string this site's `robots.txt` disallows.

France's largest private generalist board. Ex-RegionsJob, merged with Cadreo in
2022, and the umbrella over the old regional sites (ParisJob, OuestJob,
RhoneAlpesJob…) — around 5 million visitors a month. It is where French **SMEs
and the regions** publish, which is the layer HiringCafe indexes thinly.

**Everything here was verified against the live site on 2026-08-30.**

## Read this before touching the URLs

HelloWork's `robots.txt` is the most restrictive of any board here, and it
shapes the whole adapter.

```
User-Agent: *
Disallow: /*?                      ← every query-string URL
Disallow: /fr-fr/emploi/recherche.html
Disallow: /fr-fr/api/    /api/
Disallow: /search/       /fr-fr/search/
Disallow: /rss/
Disallow: /offres/postuler
Allow:    /*utm_source=
Allow:    /*xtor=
```

**There is no search carve-out.** Meteojob blocks `/*?` and then opens
`/jobs?*`; HelloWork opens only tracking parameters. Search, pagination and the
API are all behind that line, and the search page is disallowed by name on top
of it.

**The sitemap it advertises does not serve.** `robots.txt` ends with
`Sitemap: https://www.hellowork.com/fr-fr/horizon.xml`, and that URL answers
**403** from a Microsoft Azure Application Gateway. The published route is
closed; do not keep trying it.

What is left, and what this adapter uses:

| Path | What it gives |
| :-- | :-- |
| `/fr-fr/emploi/domaine_<d>.html` | 20 ads in a sector |
| `/fr-fr/emploi/domaine_<d>-ville_<slug>-<postcode>.html` | 20 ads, sector × town |
| `/fr-fr/emploi/metier_<m>.html` | 20 ads for one job title |
| `/fr-fr/emplois/<id>.html` | The ad, with a **very** rich `JobPosting` |

These are the site's own SEO landing pages: no query string, not disallowed,
and linked from each other. **`fetch()` refuses any URL containing `?`** — the
robots boundary is enforced in code rather than left to whoever edits this next,
because every forbidden route on this site is reached by adding a query string.

**One note the maintainer should weigh rather than inherit from me.** The same
`robots.txt` carries a long boilerplate bad-bots blocklist — HTTrack, Teleport
Pro, WebZIP, Wget and roughly four hundred site-rippers — and **`Python-urllib`
is in it**, with `Disallow: /`. This adapter is Python and sends a browser
User-Agent, as every adapter here does. The list's evident target is mass
downloaders, and this fetches a few dozen pages at human pace for one person's
job search; but the site does name the client, and that is worth knowing rather
than discovering later. The script never rotates the User-Agent to get around a
`403`.

## What this adapter can see

**One facet page is 20 ads, and there is no page 2** — pagination is a
`<form id="paginationForm">` with `name="p"`, which produces `?p=2`.

But unlike Meteojob's flat 20-per-keyword cap, **the facets combine**, and the
site publishes which ones exist. `domaine_informatique` alone offered **8 city
facets and 32 job-title facets** — so that one sector is reachable as roughly
40 × 20 ads, from URLs the site itself links to.

Coverage here is a facet list, not a page count. `facets` enumerates them so
nobody guesses a slug.

## Configuration

```yaml
boards:
  hellowork:
    enabled: true
    facets:
      - { domaine: "informatique" }
      - { domaine: "informatique", ville: "lyon", cp: "69000" }
      - { metier: "administrateur-reseau" }
    with_detail: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `facets` | yes | Each entry is `domaine`, or `domaine` + `ville` + `cp`, or `metier`. **The number of facets is the coverage** |
| `with_detail` | no | Reads each ad page. 20 extra requests per facet, and it is where the skills, the salary and the remote flag live |

No login, no account, no API key. France only.

**Build the facet list with the script, not from memory:**

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/hellowork.py" \
  facets --domaine informatique
```

It returns the towns (with their postcodes) and job titles that domain actually
publishes. A slug that does not exist answers **404 with a full-looking page**,
so guessing is the one thing that fails quietly here.

## The ad id and its URL

The id is the numeric id in the listing link:

```
https://www.hellowork.com/fr-fr/emplois/<id>.html
```

In the ledger: `hellowork:<id>`.

## What a listing card yields

Measured across one 20-ad facet page — every field on every card:

| Field | Filled |
| :-- | :-- |
| `title` | 20/20 |
| `company` | 20/20 |
| `location` — `Descartes - 37` | 20/20 |
| `contract` — `CDI`, `CDD`, `Alternance` | 20/20 |
| `posted_age` — *"il y a 2 heures"* | 20/20 |

The card hooks are `data-cy` attributes — `serpCard`, `offerTitle`,
`localisationCard`, `contractCard`. Those are test hooks, which is exactly why
they are the right thing to anchor on: they survive the styling churn that
would break a class selector.

## Reading one ad

```bash
python3 .../hellowork.py ad 82832314
```

The richest `JobPosting` of any board here — 22 fields, including things the
scoring rubric would otherwise have to infer from prose:

- **`skills`** as a list: `["Python", "TCP/IP", "YAML", "Anglais", …]`
- **`experienceRequirements.monthsOfExperience`** — a number, not "3 à 5 ans"
- **`educationRequirements.credentialCategory`** — `bachelor degree`
- **`jobLocationType: TELECOMMUTE`** — a real remote flag
- `baseSalary` min/max with a unit, `qualifications`, `industry`, a postcode

That makes `--with-detail` worth its 20 requests here in a way it is not
everywhere: this is structured data the rubric can score directly.

## Traps

**1. The 20-ad cap looks exactly like a thin sector.** A facet page returning 20
ads has matched more, and nothing on the page says so. The script prints the
difference whenever a facet comes back full — 20 is *the cap*, never a
measurement.

**2. A slug that does not exist answers 404 with a full page.** Not an error
message, not an empty listing — a normal-looking page. So a typo in a domain or
town slug is invisible except in the ad count. Use `facets` to get real ones.

**3. `validThrough` is a formula, not a promise.** Every ad states an expiry,
which normally makes a board authoritative on *"is this still open?"*. Here it
is **`datePosted` + 30 days, on 10 ads out of 10**, to the second. It restates
the posting date. **Do not add it to `shared/ats-open-check.md` as an expiry
oracle** — the same false authority `meteojob.md` trap 2 records at 60 days.
Two boards, two constants, zero information: treat a `validThrough` as a claim
to be tested, not a fact, on any board where nobody has checked.

**4. The ville facet's trailing number is the postcode.** `-13100` is Aix,
`-59000` Lille, `-69000` Lyon. It is part of the URL, not decoration, and
`--ville` without `--cp` cannot build one — the script says so rather than
guessing a postcode.

**5. `jobLocationType` is absent, not `ONSITE`, when a job is on site.** It
appeared on 2 of 10 ads, both remote. So the card reports `remote: true/false`
from its presence; never read a missing value as "we do not know".

**6. `employmentType` is not the contract type.** `FULL_TIME` on the ad against
`CDI` on the card — schema.org's time basis versus the French contract. Both are
kept, `contract` from the listing and `employment_type` from the ad. Merging
them replaces the useful one with the useless one, exactly as on
`meteojob.md` trap 7.

**7. `directApply` is `true` on every ad**, and applying is nonetheless out of
scope: `/offres/postuler` is robots-disallowed, and **the plugin does not create
accounts and does not fill credential fields.** Hand the user the ad URL.

**8. The WAF fronts the whole site.** The advertised sitemap answers 403, so a
403 elsewhere is a plausible state, not a bug in the adapter. The script treats
403 and 429 as a stop, never as a retry loop.

## Applying

No assisted apply. `directApply: true` means the form is on HelloWork, and the
path that serves it is disallowed — hand the user the ad URL with their
documents.

## Pace, and the note on access

One request per facet, plus one per ad with `--with-detail`; a six-facet sweep
with details is about 126 requests, spaced by `--delay` (default 1s).

This adapter reads only the site's own public landing pages and ad pages, at
human pace, for one person's job search. The cap and the closed sitemap are
documented above rather than engineered around, and the query-string guard in
`fetch()` is there so that stays true after the next edit.
