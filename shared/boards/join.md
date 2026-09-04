# Board adapter — join.com

<!-- hosts: join.com -->
<!-- script: ats.py -->
<!-- countries: * -->

One employer at a time, by tenant. **No browser, no account, no key.**

JOIN (JOIN Solutions AG, Pfäffikon SZ) is the ATS of European SMB hiring —
20 000+ companies across the DACH region, France and Spain. On the plugin's own
home market it is **the largest ATS family there is**: 108 of 223 Swiss
HiringCafe cards, 48 %, ahead of Workday. It had no adapter for fifteen country
pages.

**Everything below was measured against the live site on 2026-08-31.**

## Configuration

```yaml
boards:
  join:
    enabled: true
```

## Usage

```bash
ats.py resolve "BaXian"                                  # employer -> tenant
ats.py list --provider join --tenant simplee-energy
ats.py list --provider join --tenant baxian-group --with-description
ats.py ad   --provider join --tenant hebu-shop --id 16646156
```

## There is no search. Say so before anyone asks.

`join.com/jobs` redirects to a **login**; `/companies`, `/de/jobs` and `/search`
all answer 404. The declared job sitemap —
`join.com/companies/sitemap-jobs-index.xml`, listed in the site's own
`robots.txt` — answers **403 from Cloudflare**.

So this is a targeting adapter, not a discovery one: *"I want to work at X"*.
Discovery of join.com ads goes through HiringCafe, which indexes them heavily.

`robots.txt` is otherwise among the most permissive this plugin reads: it
disallows only `/*/lp/`, names `ClaudeBot`, `Claude-User` and `Claude-SearchBot`
in a group that is **allowed**, and publishes an `/llms.txt` index. The 403 on
the sitemap sits oddly beside that, and is treated as what it is — a closed
door, whatever the invitation says elsewhere.

## No JSON feed. A complete state object instead.

join.com is a Next.js app and ships `__NEXT_DATA__` in every page:

| Page | What it carries |
| :-- | :-- |
| `/companies/<tenant>` | `initialState.jobs` — `items`, `pagination`, `aggregations`; `initialState.company` |
| `/companies/<tenant>/<id>-<slug>` | `initialState.job` — the ad in full |

This is not scraping. `pagination` gives `total` and `pageCount`, so the sweep
is exact and terminates by construction rather than by guessing an end.

## The field that will hurt you: money is in minor units

```json
"salaryAmountFrom": {"currency": "CHF", "amount": 2035}
```

That ad renders as **"CHF 20.35 bis CHF 25.25 / Stunde"** and its own JSON-LD
writes `minValue: 20.35`. The factor of 100 is confirmed twice on the same page.

**Read the integer raw and an hourly rate of CHF 20.35 becomes CHF 2 035** — a
number that reads perfectly well as a monthly salary and would pass any sanity
check a human applies to a pay figure. `join_money` divides by 100.

**And a flag that promises what it does not deliver.** `settings.showSalary` was
`true` on **15 of 22** sampled ads; an actual amount was present on **1**. The
flag is the employer's intent, not a figure. The card reports
`salary_flag_without_amount` and no salary, rather than inventing one.

## An ad carries two numbers, and both address it

```
item id      16257505      <- stable identity
item idParam 16620520-customer-excellence-…   <- reissued on republish
```

Three of seven ads on one tenant had a different number in each. **Either
resolves, and the slug is ignored entirely** — a wrong slug on a right number
still serves the ad. So:

- `ledger_id` is `join:<tenant>:<job.id>` — the stable one.
- `ats.py ad` fetches the URL directly instead of searching the board, because a
  user pastes whichever number the browser showed them. Looking one up in the
  list would report a live ad as pulled.

## Pagination, and the page past the end

`perPage` is 5. Bounded by `pageCount`, because past the end the board **repeats
the last page**: on an 8-ad tenant with `pageCount: 2`, `?page=3` returned page
2's two ads again while `?page=99` answered `page: 98` with nothing. The loop
dedupes on id as well, so neither shape can inflate a count.

## The description arrives already cut into its parts

No other provider in `ats.py` does this:

| Field | What it is |
| :-- | :-- |
| `intro` | the pitch |
| `tasks` | what the job does |
| **`requirements`** | **the must-haves, on their own** |
| `benefits` | what they offer |
| `outro` | the sign-off |

Markdown, not HTML. **`requirements` alone is what `shared/scoring-rubric.md`
actually reads** — everywhere else it has to be dug out of one prose blob, and
the marketing bleeds into the must-haves. Present on 20 of 22 sampled ads.

## Also on the card

| Field | Coverage on 22 sampled |
| :-- | --: |
| `contact` — name **and** email, in the clear | 20 |
| `coordinates` | 22 |
| `language` — the ad's own locale | 22 |
| `address` — postcode, town, region | 16 |
| `status` (`ONLINE`) | 22 |

The contact is published by the employer on the public ad for candidates to use;
nothing is de-obfuscated to get it, unlike `fhf.md`.

`language` earns its place: this board is DACH-first and mixes `de-de`, `fr-fr`
and `en-*` **within one tenant**, and `cover-letter` sets `LANG` from the ad
before it writes a line.

## What it adds over HiringCafe, measured

HiringCafe already indexes join.com — so the honest question is what a direct
read buys. Its card for a join ad carries **no description at all**, a
`published_estimate`, and a company name it labels as inferred:
`llm_pick`, `single_deterministic`, `invalid_fallback_canonical`.

On 11 Swiss tenants the two names disagreed **5 times**:

| HiringCafe | join.com |
| :-- | :-- |
| `Smile Fahrlehrerausbildung AG` | `wab kurs` |
| `simplee` | `simplee AG` |
| `Vitality Spitex GmbH` | `Vitality-Spitex` |
| `Mensch und Maschine` | `Mensch und Maschine Schweiz AG` |
| `Agnostic Intelligence` | `Agnostic Intelligence AG` |

Neither is authoritative for a human, and the first row shows join's value can be
a careless tenant name. But **only one of the two is what the employer wrote**,
and the ledger's employer dedup keys on it. Where they disagree, the plugin now
holds both.

## Exit codes

| Code | Meaning |
| :-- | :-- |
| `4` | no company page for that tenant (HTTP 404) |
| `3` | `ad` on an id that 404s — filled or pulled |
| `2` | a page with no `__NEXT_DATA__` — the app changed shape, or Cloudflare interposed |

The `2` is deliberate: when the state object is gone, the adapter **stops**
rather than falling back to parsing HTML. A scraper improvised against a
Cloudflare interstitial is how a board starts returning confident nonsense.

## Finding tenants

**There is no directory, and no resolver on join.com.** Two routes:

1. `ats.py resolve "<employer>"` — asks HiringCafe, which records `join` and the
   tenant on every ad it indexes. This is how most tenants will be found.
2. Read it off an ad URL: `join.com/companies/<tenant>/…`.
