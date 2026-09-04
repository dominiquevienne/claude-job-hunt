# Board adapter — hays.fr

<!-- hosts: www.hays.fr -->
<!-- script: hays.py -->

**3 193 ads** from the job sitemap the site's `robots.txt` declares. Smaller
than `crit.md` (16 175), `adecco.md` (13 293) and `randstad-fr.md` (6 755), and
a **different population**: qualified profiles — finance, audit, IT,
engineering, construction management — where the other three carry production,
logistics and warehouse work.

**Everything here was verified against the live site on 2026-09-01.**

**The most useful thing this board taught is not the board.** See trap 1.

## Access

```
GET /robots.txt                        → Sitemap: …/sitemap/fr-FR/job-sitemap.xml
GET /sitemap/fr-FR/job-sitemap.xml     → 3 193 ads + per-ad lastmod
GET /description-emploi/<slug>_<id>    → the ad, JSON-LD JobPosting
```

`robots.txt` is 6 KB and **26 user-agent groups**. Eighteen of them are a bare
`Disallow: /` — and every one is a named scraper or SEO bot: `OmniExplorer_Bot`,
`trovitBot`, `ScoutJet`, `seoscanners`, `spbot`, `Feedly/1.0`. **No AI agent is
named anywhere**, and the `*` group's 55 rules close faceted search, the client
portal and `/*.php` — not the ad path and not the sitemap.

*(Worth checking that structure before concluding anything: a naive grep for
`Disallow: /` in this file returns eighteen hits and reads like a closed door.
Parse by group.)*

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/hays.py" \
  search --lieu paris --limit 20
```

**No browser, no account, no key.**

## Configuration

```yaml
boards:
  hays-fr:
    enabled: true
    searches:
      - { lieu: "paris" }
      - { lieu: "loire-atlantique" }
    since: "2026-09-01"
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `lieu` | recommended | **Free** — matched in the URL slug before any fetch. 149 of 3 193 for `paris` |
| `since` | no | On `lastmod`, which is real per ad: 2 962 distinct values in 3 193 |

Offer it for qualified and managerial profiles. For warehouse, driving or
production work the other three interim boards carry far more.

## Traps

**1. The `<loc>` elements are wrapped in CDATA, and every naive extractor
returns zero.**

```xml
<urlset xmlns="…"><url>
  <loc>
        <![CDATA[ https://www.hays.fr/description-emploi/…_1453408 ]]>
  </loc>
```

The naive pattern `<loc>\s*([^<\s]+)` matches **nothing at all**, because the
first non-space character after the tag is `<`. On a **2.37 MB, valid, HTTP
200** sitemap it yields **0 of 3 193 URLs**: a board that appears to publish
nothing.

It was carried by `adecco.py`, `crit.py`, `randstadfr.py` and `wttj.py`, and
all four now read both forms — issue #55.

*(This paragraph used to say "the pattern used on **six** other boards". That
number was wrong when it was written, and it was then relayed into an issue and
a second session's count before anyone re-derived it. **Name the files, not a
count**: a filename can be checked against any commit by whoever reads it, a
bare integer against none, and the integer goes stale at the next adapter while
still reading as fact.)*

**What exposed it was arithmetic, not the code.** The same file gave **3 193
`<lastmod>` and 0 `<loc>`**. A sitemap with dates and no URLs is impossible, so
the reader was wrong rather than the file. Had it carried neither — a sitemap
with no dates either — *"Hays publishes an empty sitemap"* would have been
written down and published.

**The invariant that generalises keys on `<url>`, not `<lastmod>`.** Zero
`<loc>` inside a non-zero number of `<url>` blocks cannot occur in a valid
sitemap, so it is a reading fault and must be reported as one. `<lastmod>` is
**optional** in the sitemaps.org schema — a valid file may carry none — so a
check against it raises a false positive on perfectly healthy sitemaps. Every
sitemap reader here now makes that comparison before reporting a count.

The form to use, here and everywhere:

```
<loc>\s*(?:<!\[CDATA\[)?\s*([^\s\]<]+)
```

*(This is the same species as the gzip trap on `jobindex.dk` one level down:
the file decompresses, parses, validates — and still yields nothing.)*

**2. The pay is in `baseSalary.value.value`, as prose — not in `minValue` /
`maxValue`.** `adecco.md`, `randstad-fr.md` and `crit.md` all put their figures
in the sub-fields, so that is where this adapter's first draft looked, and it
reported **"no salary, 0 of 12"** on a board that states one on **every ad**.
The error was mine and it is the reason this trap is written down: *looking in
the sub-field the last four boards used is not the same as looking at the
object.*

Measured properly across 22 ads: **a figure on 5, prose on 17** —
`36k€ à 42k€`, `26000 € à 32000 €` against `Selon profil`, `Selon expérience`,
`Fixe + Variable + Avantages`. Emitted verbatim as `salary_text`, never parsed.
`incentiveCompensation` repeats the same string.

**3. `postalCode` is the literal string `"NA"`.** On 22 of 22. A field that is
present, typed, populated — and holds "not available" as data. The adapter
emits `postcode: null` and keeps the raw value in `postcode_field_literal` so
nobody rediscovers it. **There is no postcode on this board**, which means no
department filtering: `--lieu` on the slug is the only geography.

**4. `addressLocality` and `addressRegion` carry the same string** — identical
on 22 of 22 — and that string is a **town, a department or a region depending
on the ad**: `Paris`, `Loire-Atlantique`, `Nord Pas-de-Calais`,
`Moselle - Thionville`. Not a granularity that can be assumed, and `region`
adds nothing. Emitted as `location_text` rather than as a city.

**5. `validThrough` is `datePosted` + 90 days.** Measured at 89, 90 or 91
across 14 ads — a formula, like `hellowork.md` (+30), `figaro-emploi.md` and
`wttj.md` (+90). Emitted as `valid_through_formula`.

**6. The employer is `Hays`** on every ad — a specialist recruiter, so the
client is described and never named. Same terms as `michaelpage.md`,
`adecco.md`, `randstad-fr.md` and `crit.md`.

### The honest summary

Seven of the 3 193 sitemap entries are pre-2026 and **answer `410 Gone`**,
which is honest and which the sweep counts. The rest are current: 3 186 dated
2026. Descriptions run to a median of **2 086 characters**, and `industry`
carries real sectors — *Cabinet d'Audit et d'Expertise comptable*, *Industrie
& Production*, *Aviation & Aérospacial*.

Against that: no postcode, a salary figure one time in four, and a location
field of unpredictable granularity. **This is the thinnest of the five agency
boards here**, and it was built knowing that.

## Applying

Applications go through Hays, which needs a candidate account. **The plugin
does not create accounts and does not fill credential fields.** Hand the user
the ad URL.

## Pace, and the note on access

One request for the sitemap, then one page load per ad read. `--lieu` and
`--since` decide how many; `--delay` defaults to 0.5s. Nothing used here is
disallowed to the `*` group.
