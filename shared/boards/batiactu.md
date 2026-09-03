# Board adapter — emploi.batiactu.com

<!-- hosts: emploi.batiactu.com -->

**9 984 offres** of French construction and public works — the largest sector
this repository had no coverage for at all. `jobology.md` reaches transport,
distribution, health and hospitality; its BTP board is one of the domains that
died with the Emploi Center network.

**Everything here was verified against the live site on 2026-08-31.**

## Search is closed; browsing is open

The `robots.txt` is 289 bytes and closes five things, of which one matters:

```
Disallow: /offre-emploi-recherche.php*      ← the search page
Disallow: /cv-ecrire-modifier.php*
Disallow: /identification.php*
```

No sitemap is declared, no AI agent is named. The browse paths are open, and
they are what this adapter uses:

```
/offre-emploi-BTP/localisation/<region>       21 regions
/offre-emploi-BTP/metier/<metier>             24 trades
…?page=<n>                                    20 ads a page
/offre-emploi/<slug>-<id>.php                 the ad
```

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/batiactu.py" \
  search --region ile-de-france --departement 75 --departement 92 --pages 5
```

**No browser, no account, no key.** Listings are byte-stable between calls, and
the pagination is honest — see the good news at the end of the traps.

## Configuration

```yaml
boards:
  batiactu:
    enabled: true
    searches:
      - { region: "ile-de-france", departements: ["75","92","93"] }
      - { region: "rhone-alpes",   departements: ["69"] }
      - { metier: "architecte" }
    pages: 5
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `searches` | yes | Each entry takes `region` **or** `metier`, never both |
| `region` | one of two | One of 21 slugs. **The pre-2016 map** — see trap 6 |
| `metier` | one of two | Trade slug, e.g. `architecte` |
| `departements` | strongly recommended | **The only location filter that works.** See trap 1 |
| `pages` | no | 20 ads each |

Offer it to anyone in construction, public works, building engineering or
building trades — and to nobody else. Every ad here is BTP.

## What an ad yields

From the JSON-LD `JobPosting` on the ad page. Measured across 50 ads in five
regions:

| Field | Example |
| :-- | :-- |
| `id` | `927922`, the number ending the URL slug |
| `title` | Conducteur de Travaux / Principal F/H |
| `company` | Eurovia, Vinci Energies, Actual Group, Domino Rh |
| `locality` / `postcode` | Livry-Gargan / 93190 |
| **`lat` / `lon`** | 48.917667 / 2.5345 — **on every ad** |
| `salary_min` / `max` / `unit` | 35000.00 / 42000.00 / YEAR — on ~20% |
| `published` | 22/07/2026, emitted ISO |
| `description` | ~3 700 characters, the full text |

**Coordinates on every ad is rare** — no other board here publishes them — and
they are correct: 21 distinct pairs across 32 ads, each matching its commune.
With the postcode they are the location to trust. The `streetAddress` is not
(trap 2).

In the ledger: `batiactu:<id>`.

## Traps

**1. The region is not a location — it is the employer's name.** This is the
one that matters. Of 24 ads taken from the **Île-de-France** pages:

| Postcode | Commune | Actual region |
| :-- | :-- | :-- |
| 45430 | Chécy | Centre-Val de Loire |
| 89190 | Pont-sur-Vanne | Bourgogne |
| 61500 | Chailloué | Normandie |
| 80120 | Rue | Picardie |
| 50400 | Granville ×2 | Normandie |
| 27220 | Saint-Laurent-des-Bois | Normandie |

**Eight of twenty-four, a third of the page, were somewhere else** — Granville
is 340 km from Paris. All eight were Eurovia, whose posting entity is called
*"Eurovia Délégation Île-de-France Normandie"*: the filter matched the
**company's name**, not the job's address.

Nothing errors, nothing warns, and the ads are real BTP ads — they are simply
not where you asked. So the region is a way to page through the board, never a
way to know where the work is. **`--departement` filters on the postcode after
the fact**, and the run reports how many it dropped so the number is never
mistaken for a fault.

**2. `streetAddress` is the employer's head office, not the job site.**
*"20 rue Thierry Sabine"* — Eurovia's — came back on ads in **twenty different
communes**, from Paris to Précy-sur-Marne. Joined to `addressLocality` it
composes an address that does not exist. The adapter emits it as
`employer_street` so it cannot be read as the workplace, and keeps
`locality`, `postcode` and the coordinates, which are the job's and are right.

A well-formed `PostalAddress` with three fields from the job and one from the
company — and the wrong one is the most precise-looking.

**3. An unknown region slug returns twenty ads.**
`/localisation/region-qui-nexiste-pas` answers **200 with twenty plausible BTP
ads** and a title that echoes the slug back: *"Toutes les offres d'emploi BTP :
region-qui-nexiste-pas"*. A typo does not empty the board, it silently changes
it. The script checks the slug against the site's own list first.

**4. `/offre-emploi-BTP/ville/<x>` is accepted and ignored.** It looks like a
fourth axis and it is not: `/ville/paris` returns the **national** board, its
title reading *"…: France"*. Never build a search on it.

**5. Two pagination forms that look right serve page 1 for ever.**
`?page=2` is the only one that works. `/localisation/<r>/page/2` and
`/localisation/<r>/2` both answer 200 with **page 1 again** — same first ad —
so a sweep built on either re-reads the same twenty ads until it gives up.

And the site's own pagination links cannot be followed: they are built by
concatenation and come out malformed, pointing at a **different region** —
`…/ile-de-france/ville/ville/…/localisation/midi-pyrenees?page=2` on the
Île-de-France page. The adapter counts pages itself and follows none of them.

**6. The regions are the pre-2016 map.** Aquitaine, Limousin, Picardie,
Languedoc-Roussillon, Midi-Pyrénées — 21 of them. There is no
`nouvelle-aquitaine` and no `hauts-de-france`, and asking for one lands in
trap 3 rather than an error.

**7. A short first page is not a short board.** `bretagne` returns **2 ads on
page 1** and **20 on each of pages 2, 3, 4 and 5**. It is not a cache artefact
— a cache-busting parameter returns the same two. Any sweep that stops when a
page comes back short stops on Bretagne having seen 2 of several hundred ads.
The adapter stops only on a page with **no ads at all**.

**8. The advertised total is national, on every page.** *"9 984 offres"* is
printed on the Île-de-France page, the Corse page and the home page alike. It
is not the filtered count and cannot be used to check a sweep.

**9. `industry` holds the company name.** On 24 of 24 ads, `industry` was
`"Eurovia"`, `"Actual Group"` — the employer, not a sector. The field is
emitted as `industry_field_holds_company_name` rather than dropped, so nobody
rediscovers it.

**10. Some ads are France Travail republished, and say so in the wrong
field.** Ads came back with `hiringOrganization` = **"Pole Emploi"**. On those,
the employer is not named at all and the row duplicates `france-travail.md`,
which this plugin already sweeps. The adapter flags them
`from_france_travail: true` rather than passing off the aggregator as the
employer.

**11. `validThrough` is a default on most ads, not a formula and not a
deadline.** 90 days after `datePosted` on 14 of 24 — but the other ten came
back at 123, 168, 181, 182, 182, 243, 246, 252, 257 and 258 days. Neither a
constant like `hellowork.md` (+30) nor a real limit like
`emploi-territorial.md`. Emitted as `valid_through`, believed as neither.

**12. A few employers dominate.** Three distinct employers across 24
Île-de-France ads, Eurovia holding 21 of them; six across 26 ads taken from
five other regions (Actual Group 8, Domino Rh 7, Eurovia 7). Actual Group and
Domino Rh are staffing agencies. **9 984 ads is not 9 984 employers**, and a
region sweep can come back as one company's recruitment plan.

### And the good news, which is rarer

**The pagination is exact and it terminates.** Provence-Alpes-Côte d'Azur:
pages 1–120 gave 20 each, page 121 gave **8**, page 122 gave **zero** — and so
did 200 and 9999. Corse: 20 then 15 then zero. No cap, no ceiling, no
plausible-looking page past the end, unlike `jobology.md` and `free-work.md`.
**And the listings are stable**: the same URL fetched twice returned the same
twenty ads in the same order.

## Applying

Applications go through the site, which needs an account
(`/identification.php`, disallowed and never touched). **The plugin does not
create accounts and does not fill credential fields.** Hand the user the ad URL
with their documents.

## Pace, and the note on access

One request per page of 20, plus one per ad read — `--no-details` skips the
second, at the cost of `--departement`, since the postcode lives on the ad page.
`--delay` defaults to 0.5s. A region is a few dozen pages at most; the whole
board is about 500, which is not something to sweep in one go.

Everything is fetched from the browse paths, never from the search page the
`robots.txt` closes.

## Refused since the plugin declared `Claude-User` — and the body does not say why

Measured 2026-09-03, after #120. **This board now fails at the gate**, because
`emploi.batiactu.com` returns 403 for its own `robots.txt`.

```
robots.txt, browser string   200, 289 bytes   (measured in the same minute)
robots.txt, our declaration  403, 18 887 bytes
```

**So the response is conditional on the agent string.** What it is not is
identifiable as a bot wall. The 403 body was tested against every marker this
repository has measured on a real wall, and **none matches**:

```
Attention Required (bayt.com, 5 507 b)             no
cf-mitigated header (hiringcafe.com)               no
Sucuri / Imperva / Incapsula                       no
"Request is Blocked by Firewall"
        (barbadosjobregister.gov.bb, 30 b)         no
captcha / robot / bot                              no
```

What it says instead, under `Server: Apache` with no CDN header at all:

> **sorry, site under maintenance** — We'll be back soon…

**A maintenance page is not a consent decision, and it is not proof of a
wall.** So the strict default holds: **the verdict stays `False`, the board is
not swept, and no exception was written.** A 403 becomes *a wall* only on
positive proof in the body — a board is gained by showing the refusal was not
one, never by failing to show that it was.

**And the degraded mode does not apply here.** #124's trigger is a fetch
failure on a host that *permits*; the guard says `False`, so the browser is
not reached for. That is the rule working, not a gap in it.

**What remains available is what any visitor has**: the site opens normally in
a browser, and reading it there is the user's own access, not the plugin's.
The other route is to write to the operator — a 403 on `robots.txt`,
conditional on the user-agent and carrying a maintenance page, is very
plausibly a misconfiguration they would want to know about.

**Not verified, and deliberately:** whether the same body is served to other
agent strings today. `robots-policy.md` forbids retrying under another name,
and that holds when the retry would suit us.
