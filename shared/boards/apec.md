# Board adapter — apec.fr

<!-- verified: 2026-09-02 -->

<!-- hosts: www.apec.fr -->
<!-- script: apec.py -->
**Re-verified 2026-09-02**: a `--mots-cles developpeur` search returned **50 cards of 3 286 matching**, and every card still carries a teaser rather than the ad — the constraint this file is built on.

The **Association pour l'emploi des cadres** — France's public-interest agency
for management and senior professional roles, and the reference board for that
segment. **77 023 ads** nationally on the day this was written; 6 063 in Paris,
4 951 in the Rhône.

**Everything here was verified against the live API on 2026-08-30.**

## The friendliest board here, and the one that gives least

Two facts decide how this adapter is used, and they pull in opposite
directions.

**Its robots.txt is wide open.** No `Disallow` at all — the file's own comment
is *"All robots will spider the domain"* — and it advertises four sitemaps.
After HelloWork, that is a striking difference: nothing here has to be worked
around, because nothing is closed.

**And the description is not reachable.** `texteOffre` is a **fixed
283-character teaser**, cut mid-sentence, identical in length on all 300 ads
sampled. The full text lives behind a detail endpoint that answers `403` with a
**DataDome captcha** URL. The plugin does not solve captchas — `indeed.md` sets
that rule and it holds here.

So this is **the best triage board in France and not a source of ad text**. What
it gives per ad is unusually good for screening: title, employer, location,
**salary on every single ad**, contract type, sector, coordinates and a
publication timestamp. What it cannot give is the ad itself.

Say that when offering it. A user who expects `cover-letter` to work from a
scan of this board will hit the paste-the-text fallback and think something
broke.

## No browser, no key, no cookie

```
POST https://www.apec.fr/cms/webservices/rechercheOffre
     content-type: application/json
     {"typeClient":"CADRE","activeFiltre":true,
      "sorts":[{"type":"DATE","direction":"DESCENDING"}],
      "pagination":{"range":100,"startIndex":0},
      "lieux":["75"]}
→ {"resultats":[…], "offreFilters":[…], "totalCount":6063}
```

Unauthenticated, no account, no browser.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/apec.py" \
  search --lieux 75 --lieux 92 --mots-cles "data engineer" --pages 3
```

## Pagination is unlimited, which is unique here

`startIndex` was walked to **76 900** and still returned 100 **disjoint** ads;
77 100 returned zero. Every other French board in this repository truncates —
France Travail at 3 150, Meteojob and HelloWork at 20 per page with no page 2.
**The APEC hands over its entire board.**

That changes how it is swept: not "as many narrow searches as possible", but one
broad search paged through. Be deliberate about how far you page, because
nothing stops you at 77 000 ads.

## Configuration

```yaml
boards:
  apec:
    enabled: true
    lieux: ["75", "92", "93"]      # department codes, as strings
    mots_cles: ["data engineer"]   # optional
    types_contrat: ["101888"]      # optional, ids — see `filters`
    pages: 5                       # 100 ads per page
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `lieux` | recommended | **Department codes as strings** — `"75"`, `"69"`. Also `799` (France) and `102099` (abroad). An unknown value is a loud 400 |
| `mots_cles` | no | Free text |
| `types_contrat`, `fonctions`, `teletravail`, `experience`, `secteurs` | no | **Numeric ids.** The API publishes no labels for them — get them from `filters` |
| `pages` | no | 100 ads each, and there is no ceiling |

No login, no account, no API key. France, plus a small abroad bucket (351 ads).

## The id space, and how to verify one

**There is no public referential.** `/cms/webservices/referentiel*` is a 404 in
every form tried, and the API returns bare numeric ids with no labels anywhere.

What it does return is `offreFilters`: every facet, with a **count per id**. And
those counts are the oracle. Each filter name in this adapter was confirmed by
passing an id and checking the total came back equal to the count the facet
claimed:

| Filter | Id | Facet count | Total when passed |
| :-- | :-- | --: | --: |
| `typesContrat` | 101888 | 70 948 | **70 948** |
| `typesTeletravail` | 20765 | 10 135 | **10 135** |
| `niveauxExperience` | 20043 | 50 325 | **50 325** |
| `fonctions` | 101828 | 16 859 | **16 859** |

```bash
python3 .../apec.py filters --lieux 69
```

That is the id catalogue for a given search. Use the same check before trusting
any id: pass it, compare the total to the count.

## The ad id and its URL

The id is `id` — `numeroOffre` is the same number with a `W` suffix, so it adds
nothing as a key. Rebuild the page from it:

```
https://www.apec.fr/candidat/recherche-emploi.html/emploi/detail-offre/<id>
```

In the ledger: `apec:<id>`.

## Traps

**1. `texteOffre` is a teaser, not the ad.** 283 characters, exactly, on 300 of
300 sampled — it stops mid-sentence. The card names the field `teaser`, never
`description`, and carries `full_text_available: false`, precisely so nothing
downstream scores it as if it were the posting.

**2. The detail endpoint is behind a captcha.**
`/cms/webservices/offre/public/detail/<id>` answers `403` with a
`geo.captcha-delivery.com` URL. **Do not route around it**, and do not rotate
the User-Agent: the script stops with that reason named.

**3. The ad page does not prerender, even for Googlebot.** It is a 12 KB
Angular shell with no `JobPosting` block, and fetching it with a Googlebot
User-Agent returns the same 12 KB. That is worth knowing because the site
advertises a `sitemap_seo4ajax.xml`, which suggests prerendering exists — it
does not reach ad pages. **There is no scraping route to the description
either.**

**4. `range` over 100 is silently downgraded to 20.** Not refused, not capped —
`range: 200` returns twenty ads and a normal `200`. A sweep asking for big
pages would quietly collect a fifth of what it thinks. The script clamps to 100
and says so.

**5. `salaireMinimum` is accepted and silently ignored.** `salaireMinimum: 60`
returned the unfiltered 77 023. The field exists, the API does not reject it,
and it does nothing — so this adapter does not expose it. Filter pay after the
fetch; `salaireTexte` is on every ad.

**6. `datePublication` is a 500, not a filter.** The site's own UI has a
period facet (`PERIOD_FILTERING`), but that parameter name makes the API throw.
Some wrong names here fail loudly and some are ignored (trap 5), so **neither
outcome proves a parameter is real** — only the count check does.

**7. A confidential ad has a filled employer field containing no employer.**
`nomCommercial` was non-empty on 300 of 300 ads — but 10 of them read
`ZZ_Confidentiel`, with `offreConfidentielle: true`. Passed through naively,
that sentinel reaches the ledger looking like a company. The card sets
`company: null` and `confidential: true` instead.

**8. An unknown filter value is a loud 400** — with a Java deserialization
message quoting the value. That is the good case: on this board a wrong id
fails, it does not silently return everything. Trap 5 is the exception, which is
why it is written down.

**9. Salary is on every ad, as free text.** `salaireTexte` was filled 300/300 —
`"80 - 120 k€ brut annuel"`. No other board here comes close, and it is the one
field that makes a 283-character teaser worth scoring at all. It is prose, not a
number: parse it defensively.

## Applying

There is no in-site apply flow to drive, and **the plugin does not create
accounts and does not fill credential fields.** Hand the user the ad URL with
their documents.

Because the full text is unreachable, `cover-letter <URL>` on an APEC ad will
fall back to asking the user to paste the ad text — the documented behaviour for
any gated page. Tell them that when the row is proposed, not after they click.

## Pace, and the note on access

One request per page of 100. A five-page sweep is five requests, which is the
cheapest coverage of any board here — but the board is 77 000 ads and nothing
stops a caller from paging through all of it, so the pages are spaced
(`--delay`, default 1s) and the sweep is bounded by configuration rather than by
the server.

A `403` carrying a captcha URL is treated as a stop. `robots.txt` disallows
nothing, and this reads the search interface the site's own front end uses,
unauthenticated, a handful of times, for one person's job search. Keep the pace
human anyway.
