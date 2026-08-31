# Board adapter — Jobology (nine sector boards)

Jobology runs **nine French sector job boards** on one platform. They share a
URL contract, a `robots.txt` and a page structure, so one adapter reaches all
nine — the same leverage as `taleez.md`, `flatchr.md` and `digitalrecruiters.md`,
except the tenants here are whole boards rather than employers.

**Everything here was verified against the live sites on 2026-08-31.**

## The nine, and why they matter

| Site | Sector | Ads announced |
| :-- | :-- | --: |
| `distrijob.fr` | Distribution et retail | 22 361 |
| `jobvitae.fr` | Santé, soignant, médical | 17 950 |
| `jobtransport.com` | Transport et logistique | 15 654 |
| `clicandtour.fr` | Tourisme, hôtellerie, restauration | 4 796 |
| `clicandpower.fr` | Énergie | 3 775 |
| `clicandsea.fr` | Maritime et naval | 3 344 |
| `clicandsport.fr` | Sport | 2 411 |
| `clicandearth.fr` | Environnement | 1 916 |
| `supply-chain.fr` | Logistique et supply chain | 460 |
| | **Total** | **72 667** |

This is inventory the generalist boards serve badly: driving, warehouse, retail
floor, care work, kitchens, ships. **It is not a France Travail rerun** — the
ads carry the platform's own identifier, name the employer, and offer a direct
apply. That was checked before the adapter was written, because it is the test
that disqualified the aggregators.

Four families the repository listed as uncovered collapse into this one build:
distribution (Distrijob), transport and logistics (the old Emploi Center),
health (alongside `talentsoft.md` and the FHF, this is the private side), and
hospitality.

*(The "Emploi Center" network these boards used to belong to is gone:
`jobindustrie.com`, `jobbtp.com`, `jobagroalimentaire.com` and
`emploi-center.com` no longer resolve, and `jobtechnique.com` is parked for
sale. Only `jobtransport.com` survived, and Jobology is where it lives now.)*

## Browsing by path, because the query string is closed

The `robots.txt` — identical on all nine — leaves the paths open and closes the
**facet parameters**: `fpos`, `fspos`, `fsec`, `fexp`, `fdate`, `freg`, `fctr`,
`fcsoc`, plus `/*?$`. So the search filters are disallowed and the browse paths
are not, exactly as on `hellowork.md`. **The script refuses any URL containing
`?`.**

```
/emploi/<metier>.aspx                        nationwide
/emploi/<metier>/<region>.aspx               narrowed
/emploi/<metier>[/<region>]/page-<n>.aspx    pagination, 20 ads a page
/offre-emploi/<slug>-<id>.aspx               the ad
```

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/jobology.py" \
  search --site jobvitae.fr --metier infirmier --pages 5
```

Both vocabularies come from the sites themselves, and the script reads them:

```bash
jobology.py sites                                # the nine
jobology.py metiers --site jobvitae.fr           # 271 slugs
jobology.py metiers --site supply-chain.fr       # 72 slugs
jobology.py regions --site jobtransport.com      # 12 slugs
```

Region slugs are readable — `occitanie`, `provence-alpes-cote-azur`,
`ile-de-france`. **Twelve came back, not thirteen: Corse is absent** from the
index, so a Corsican search has no path and must go through a métier sweep
filtered on the postcode.

## Configuration

```yaml
boards:
  jobology:
    enabled: true
    searches:
      - { site: "jobvitae.fr",       metier: "infirmier" }
      - { site: "distrijob.fr",      metier: "vendeur", region: "occitanie" }
      - { site: "jobtransport.com",  metier: "chauffeur-spl" }
    pages: 5
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `searches` | yes | Each needs a `site` and a `metier` |
| `site` | yes | One of the nine. Anything else is refused by name |
| `metier` | yes | A slug the site publishes — check with `metiers` |
| `region` | no | One of the 12 slugs |
| `pages` | no | 20 ads each |

Offer it by sector, not by default: a candidate in tech has nothing to find on
`clicandsea.fr`, and a nurse has everything to find on `jobvitae.fr`.

## What an ad yields

Every ad page carries a JSON-LD `JobPosting`. Measured on 18 ads across four
métiers — **postcode present on 18 of 18**:

| Field | Example |
| :-- | :-- |
| `id` | `3272873`, the number at the end of the URL slug |
| `title` | Conducteur Routier SPL nuit (H/F) |
| `company` | Groupe RAVE, KIMMEL TRANSPORTS, INSTITUT LA TEPPE |
| `locality` / `region` / `postcode` | Rochefort-sur-Nenon / Jura / **39700** |
| `employment_type` | `FULL-TIME`, `PART-TIME`, `TEMPORARY` — read trap 6 |
| `salary_text` | free text, ~78% filled — read trap 7 |
| `published` | `2026-08-30T01:28:52Z` |
| `description` | 2 000–4 000 characters |

In the ledger: `jobology:<site>:<id>` — the site is part of the key, because
the same employer posts to more than one of the nine.

## Traps

**1. Past the last page the site never stops, and never repeats itself
either.** `chauffeur-spl` on Jobtransport has 83 pages; page 83 returned 5 ads.
**Page 84 returned 20. So did page 200. So did page 9999** — all on-topic SPL
ads, 15 or 16 of each set already seen on pages 1–83. There is no empty page
and no 404 to stop on.

**2. And the same URL answers differently on a second call.** Two consecutive
requests for page 1 shared **15 of 20** ads; two for page 9999 also shared 15 of
20. Deep pages are stable — page 40 returned the identical 15 ads in the
identical order both times — so the churn is in the promoted block at the top.

Together these mean **neither "stop when the page is empty" nor "stop when
nothing is new" is sufficient**. The script uses both bounds at once: it stops
on a page with no unseen id **and** never goes past the last page number the
pagination advertises.

**3. A wrong slug is an empty board, not an error.** `/emploi/metier-bidon.aspx`
and `/emploi/chauffeur-spl/region-inexistante.aspx` both answer **200 with zero
ads** — which reads as "nobody is hiring". The script treats zero ads on page 1
as a probable bad slug and says so, naming the `metiers` command.

**4. There are two pagination URL forms and they carry different pages.**
`/emploi/<m>/page-2.aspx` and `/emploi/mc/<m>/page/83.aspx`. The site links the
next page in the first form and the **last** page in the second, and the two
forms served different page-2 content when asked. Reading only the first form
capped `chauffeur-spl` at **2 pages instead of 83** — a sweep that would have
collected 40 ads of roughly 1 645 and reported success. Found by writing the
naive version first; the fixed pattern accepts both.

**5. No listing page states a total.** Every other board here announces a count
to check the sweep against; this one announces it only on the site's home page,
for the whole board. So the only bound is trap 4's page number, and the run
says when it stopped short of it.

**6. `employmentType` is spelled `FULL-TIME`, with a hyphen.** Schema.org's
value is `FULL_TIME` with an underscore. A consumer matching the standard
vocabulary matches nothing — silently, on every ad. Values seen: `FULL-TIME`
13, `TEMPORARY` 3, `PART-TIME` 2.

**7. The salary field is filled far more often than it is informative.**
Present on **14 of 18** ads — a rate `figaro-emploi.md` would envy — but it is
free text, and much of it is not a salary:

```
'38 000 à 45 000 brut annuel + commissions'    '13.5 - 15.5 par heure'
'2200 - 2600 par mois'                         'Selon profil et expérience'
'35000 à 40000 EUR'                            'Selon expérience'
'13ème mois'                                   '2.486.62 EUR brut'
```

Note the last one: a mangled decimal, unparseable as written. The adapter emits
the string as `salary_text` and never a number, because a number is not what is
there. **Do not report a fill rate as a salary rate.**

**8. `validThrough` is `datePosted` + 30 days, on 18 of 18.** A formula, like
`hellowork.md` and `figaro-emploi.md`. Emitted as `valid_through_formula` so it
cannot be mistaken for the real deadline that `emploi-territorial.md` has.

**9. `directApply: true` on every ad measured**, which makes it worth nothing as
a signal.

**10. The employer is named — and two thirds of the time it is an agency.**
Eleven distinct employers across 18 ads, but the mix was Aquila Rh ×7, ADECCO
×2, Manpower, Adéquat Intérim, FED Group, Adsearch, MICHAEL PAGE ADVERTISING —
against four genuine end employers (DUPESSEY CO, KIMMEL TRANSPORTS, GROUPE
HEPPNER, Institut La Teppe). Same caution as `cadremploi.md`: the field is
filled, but what it names is often the intermediary. And `michaelpage.md`
already sweeps one of them directly, so expect duplicates there.

## Applying

`directApply` is claimed on every ad and the apply flow needs an account.
**The plugin does not create accounts and does not fill credential fields.**
Hand the user the ad URL with their documents.

## Pace, and the note on access

One request per page of 20, plus one per ad whose description is read —
`--no-details` skips the second. `--delay` defaults to 0.5s. A métier in one
region is a handful of pages; a métier nationwide can be 83, and nine boards ×
hundreds of métiers is not something to sweep, so the config names searches
rather than sites.

Everything is fetched from the browse paths, never from the facet parameters
the `robots.txt` closes, at the volume one person's job search needs.
