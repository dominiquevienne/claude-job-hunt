# Board adapter — crit-job.com

**16 175 ads** — the largest French interim board here, ahead of `adecco.md`
(13 293) and more than twice `randstad-fr.md` (6 755). **No browser, no
account, no key.**

**Everything here was verified against the live site on 2026-09-01.**

## Two things it does better than any French board in this repository

**The salary.** A **minimum *and* a maximum, in euros, on every one of the 20
ads measured** — `14–15 HOUR`, `20 000–30 000 YEAR`. Adecco and Randstad both
write a minimum and leave the maximum at zero on hourly work; Figaro Emploi
publishes an empty `MonetaryAmount`; Jobology writes a sentence. This one
writes two numbers.

**The dates.** `lastmod` is **13 893 distinct values across 16 175 ads** — the
best ratio in the repository, ahead of `wttj.md`'s 7 691 in 10 000 and against
`figaro-emploi.md`'s single build stamp on 30 000. It is a real per-ad date and
`--since` genuinely narrows.

That second point matters more here than anywhere else, because **the URL is a
UUID** — `/offres/0004e776-912c-40bc-8ea7-e2959b8ab81e` — with no town and no
department in it. `--since` is the *only* narrowing that costs nothing.

```
GET /robots.txt          → Sitemap: …/offres/sitemap.xml
GET /offres/sitemap.xml  → 16 175 ads + lastmod
GET /offres/<uuid>       → the ad
```

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/crit.py" \
  search --since 2026-09-01 --limit 40
```

## Configuration

```yaml
boards:
  crit:
    enabled: true
    since: "2026-09-01"
    departements: ["30", "62"]
    max_read: 150
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `since` | strongly recommended | **The only free filter.** 1 901 of 16 175 in the last two days |
| `departements` | no | Two characters, on the ad's postcode — **costs a fetch each** |
| `max_read` | no | Caps a department sweep. Default 150 |

## What an ad yields

Measured on 20 ads:

| Field | Rate | Example |
| :-- | :-- | :-- |
| `locality` / `postcode` | **every ad** | Aigues-Mortes / 30220 |
| **`salary_min` and `salary_max`** | **every ad** | 14–15 HOUR EUR, 20 000–30 000 YEAR |
| `occupational_category` | every ad | *Installation, Maintenance & Réparation*, *BTP & second œuvre* |
| `company` | every ad | **CRIT LUNEL**, CRIT ARRAS BTP — the local branch |
| `description` | every ad | 381–1 401 characters, median 556 |
| **`profile`** | every ad | 274–407 characters — **and it is not in the JSON-LD**, see trap 1 |
| `valid_through` | **never** | and that is the honest answer |

**The employer is the local branch**, not just "Crit": 15 distinct names across
20 ads — CRIT LUNEL, CRIT CHAUMONT, CRIT ARRAS BTP. That is more than
`adecco.md`'s flat `adecco` gives you, since the branch says roughly where the
assignment is run from. It is still the agency: the client is described in the
body — *"nous recherchons pour notre client"* — and never named.

In the ledger: `crit:<uuid>`.

## Traps

**1. Half the ad is outside the JSON-LD.** The structured `description` covers
*"Description du poste"* only. **"Profil recherché" is a sibling section in the
page**, worth another 274 to 407 characters, and an adapter reading JSON-LD
alone silently drops the requirements — which is the half a candidate needs to
judge whether to apply.

It is taken from the DOM, anchored on the **heading's text**:

```html
<h2 class="MuiTypography-root MuiTypography-h2 css-aocjcp">Profil recherché</h2>
<p class="MuiTypography-root MuiTypography-body1 css-1nm1tyc">…</p>
```

`css-aocjcp` and `css-1nm1tyc` are **Emotion build hashes** and change on every
deploy. Selecting on them works today and rots on the next release — the same
lesson as the Vue `data-v-*` attributes on `figaro-emploi.md`. The heading text
is the stable handle.

**2. `addressCountry` is the country's *name*.** `"France"`, where every other
board in this repository writes `"FR"`. A check written `== "FR"` matches
nothing, on every ad. Emitted as `country_name` so the field says what it holds.

**3. `employmentType` is `OTHER` on 14 of 20.** A valid schema.org value
carrying no information at all. The rest were `FULL_TIME` (5) and `TEMPORARY`
(1) — and interim work landing under `FULL_TIME` is not a distinction to rely
on either. **Do not filter on it.** `occupational_category` is the field that
actually sorts these ads.

**4. `jobStartDate` is prose.** *"Dès que possible"* on 19 of 20; one ad
carried `24/08/2026`. Present on every ad and parseable on almost none — a
field filled far more often than it is a date.

**5. There is no cheap geography.** The URL is a UUID, so unlike
`randstad-fr.md` — where the town in the slug is reliable and free —
`--departement` has to read each ad to see its postcode. Measured: **60 ads
read to keep 1** in the Gard. Narrow with `--since` first, and the run reports
how many it read and why it stopped rather than returning a silent zero.

**6. `directApply: true` on every ad**, which makes it worth nothing as a
signal.

## Applying

Applications go through Crit, which needs a candidate account. **The plugin
does not create accounts and does not fill credential fields.** Hand the user
the ad URL, the branch name, and the salary — which here is a real range.

## Pace, and the note on access

One request for the sitemap, then one page load per ad read. `--since` decides
how many that is; `--delay` defaults to 0.5s and `--max-read` to 150. The
sitemap is the one `robots.txt` advertises and the ad path is open.
