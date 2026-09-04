# Board adapter — infoempleo.com (Spain)

<!-- hosts: www.infoempleo.com -->
<!-- script: infoempleo.py -->
<!-- countries: ES -->

**7 621 active ads.** The third Spanish adapter here and the first that is not
a public register: `empleate.md` and `oposiciones.md` are both the SEPE's, and
this one is a private generalist board covering the whole country.

**Everything here was verified against the live site on 2026-09-01.**

**The most useful thing this board taught is not the board.** See trap 1 — and
read it before writing any adapter against any site, because the failure it
describes is invisible, intermittent, and survives a spot-check.

## Access

```
GET /robots.txt                     → two Sitemap: lines, one of them empty
GET /sitemap-index.xml              → the real list of eight sitemaps
GET /sitemap-ofertas-activas.xml    → 7 621 ad URLs, ~900 KB, no lastmod
GET /ofertasdetrabajo/<slug>/<place>/<id>/   → the ad, JSON-LD JobPosting
```

`robots.txt` names **no crawler and no AI agent**. Its 73 `Disallow` rules
under `*` close the faceted search (`/trabajo/fecha_*`, `/trabajo/pais_*`), the
training section, the RSS export and `/login/` — and leave `/ofertasdetrabajo/`
entirely open. Only `msnbot` gets a `Crawl-delay`, of 5.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/infoempleo.py" \
  search --lugar madrid --limit 20
```

**No browser, no account, no key.**

## Configuration

```yaml
boards:
  infoempleo:
    enabled: true
    searches:
      - { lugar: "madrid" }
      - { lugar: "barcelona" }
    desde: "2026-09-01"
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `lugar` | recommended | **Free** — matched in the URL before any fetch. 1 201 distinct values; `infoempleo.py lugares` lists them with counts |
| `desde` | no | On `datePosted`, which **costs a fetch per ad**: the sitemap carries no `lastmod` at all |

`multiprovincia` is a real place value, not a placeholder — 146 ads posted
across several provinces at once.

## Traps

**1. `Content-Encoding: deflate`, unsolicited, on a fraction of responses —
and the fraction changes between runs.**

The same URL, same headers, same minute:

```
try1  enc=deflate  raw= 39 057  →  decoded 159 803   ld+json blocks: 4
try2  enc=deflate  raw= 39 057  →  decoded 159 803   ld+json blocks: 4
try3  enc=-        raw=159 579                       ld+json blocks: 4
try4  enc=-        raw=159 579                       ld+json blocks: 4
```

Six of eight came back deflated in one run; two of forty-five in the next. It
is a load-balanced pair of backends and there is no way to ask for one.

**A client that does not decompress gets no error.** It gets 37 111 characters
of mangled bytes that decode cleanly with `errors="replace"`, carry no
`<script>` tag, contain no `JobPosting` string, and read exactly like *an ad
page that has no structured data*. HTTP 200, correct content type, plausible
length, no exception anywhere.

So the failure is **silent, intermittent, and never reproduces on the same
ads**. A spot-check passes. A re-run "fixes" a different subset, which is the
most misleading outcome available: it looks like a flaky site rather than a
broken reader.

| Measured | Ads reporting "no structured data" |
| :-- | --: |
| Body read raw | **5 of 45** |
| Body decompressed | **1 of 45** — and that one is a genuinely expired ad |

This is the gzip trap of `jobindex.dk` and the CDATA trap of `hays-fr.md` with
the property both of those lacked: **it comes and goes.** Those two fail
totally and therefore loudly — 0 of 3 193 is an alarm. This one fails partially
and quietly, which is worse.

Two defences, and the second matters more than the first:

- `get()` always decodes `gzip` and `deflate` (both the zlib-wrapped and the
  raw form are seen), and a body that will not decompress is a hard error
  naming the encoding.
- `card()` treats **zero `ld+json` blocks** — not "no JobPosting" — as a
  failure to read. A live ad page here always carries three or four blocks, so
  zero is an invariant violation rather than a fact about the ad. That check
  catches the next encoding this site invents without needing to know about it.

**2. The previous release's salary lesson, inverted.**

`hays-fr.md` records that the pay sits in `baseSalary.value.value`, as prose,
where four other boards use `minValue` / `maxValue` — and that reading only the
sub-fields reported "no salary" on a board that states one on every ad.

Here:

```json
"baseSalary": {"currency": "EUR",
               "value": {"value": 0.0,
                         "minValue": 22000.0, "maxValue": 30000.0,
                         "unitText": "YEAR"}}
```

`value.value` is **`0.0` on every salaried ad measured — 9 of 9** — and the
figures are in `minValue` / `maxValue`. An adapter written from the most recent
lesson in this repository reports **€0 on every ad that states a salary**, which
is worse than reporting none: zero looks like data.

The rule that survives both boards is the one neither of them teaches on its
own: **read the object, not the sub-field that worked last time.** The literal
`0.0` is emitted as `salary_value_field_literal` so nobody rediscovers it.

**3. `robots.txt` declares a sitemap that is 0 bytes.**

```
Sitemap: https://www.infoempleo.com/sitemap-index.xml
Sitemap: https://www.infoempleo.com/sitemap-ofertas-activas-recientes.xml   ← 200, 0 bytes
```

The second is **absent from `sitemap-index.xml`** and returns `200`,
`text/plain`, **zero bytes** on every request. It is also the one whose name
sounds most useful — *active offers, recent*.

Taking the sitemap list from `robots.txt` is the correct, standard thing to do,
and several adapters here do it. On this site it is a coin flip between the
whole board and nothing. The adapter reads `/sitemap-index.xml` and names this
file in its error message, so an empty result points at the cause instead of
looking like a dead board.

**And zero URLs is never reported as an empty board.** `<loc>` is read with the
tolerant pattern that also accepts the CDATA wrapper `hays-fr.md` documents —
infoempleo does not use it today (7 621 `<url>`, 7 621 `<loc>`, no CDATA), so
that is insurance against a change nobody would announce. Behind it sits the
check that actually generalises: **zero `<loc>` inside a non-zero number of
`<url>` blocks is impossible in a valid sitemap**, so it is reported as a
reading fault rather than an empty board. That arithmetic, not the code, is
what exposed the CDATA trap on Hays. `<lastmod>` cannot play the same role —
the spec makes it optional, so its absence proves nothing. See issue #55.

## What the record carries

Measured on 45 ads sampled at random from the sitemap, read with the body
decompressed.

| Field | Coverage | Note |
| :-- | --: | :-- |
| `title`, `description` | 44/44 | Median **1 264 characters**; only 1 under 300 |
| `hiringOrganization` | **44/44** | Always named — but see below |
| `datePosted` | 44/44 | Real per ad |
| `validThrough` | **44/44** | 20 to 283 days after posting — genuinely per ad, not a formula, and **none had already passed** |
| `employmentType`, `workHours` | 44/44 | `FULL_TIME` / `PART_TIME` / `OTHER`, and `Completa` / `Parcial` |
| `experienceRequirements` | 44/44 | Prose — "Al menos 2 años de experiencia" |
| `industry`, `occupationalCategory` | 44/44 | Real sectors and job families |
| `addressRegion` (province) | 43/44 | |
| `addressLocality` (town) | 39/44 | |
| `baseSalary` | **9/44** | 20%. See trap 2 |
| `postalCode` | **0/44** | Absent on every ad, exactly as on `hays-fr.md` |

**`qualifications` is a copy of `industry`** — identical on 18 of 18 measured.
It carries the sector name, not a qualification. The card emits
`qualifications_field_duplicates_industry` rather than a field that would read
as requirements.

**`jobLocation` is a dict on most ads and a list on the multi-site ones** — 1
of 44. An adapter written against the first twenty ads assumes a dict and
either crashes or silently drops the location on the rest.

### It is a generalist board by coverage and an agency board by content

The employer is named on every ad, which reads like an advantage over
`adecco.md` or `crit.md`. Then you count them: **60 ads carried only 23
distinct employers**, and the four largest — all staffing agencies — account
for 36 of the 60.

| Employer | Ads in 60 |
| :-- | --: |
| HOSPITALITY CONNECTION BARCELONA SL | 11 |
| ANANDA GESTION ETT | 9 |
| IMAN TEMPORING ETT, S.L. | 8 |
| GRUPO CRIT | 8 |
| EULEN Flexiplán, MANPOWER ESPAÑA, PACTO ETT, Areajob Spain ETT | 7 |

32 of 44 employers in the other sample were *ETTs* — *empresas de trabajo
temporal*. So the name in `hiringOrganization` is usually the intermediary, and
the workplace is described without being named. **The same caveat as the interim
boards applies, and it is easy to miss here** precisely because the field is
filled: no pre-application research, and no dedup key against the employer's own
ATS.

Worth knowing for the ledger: `GRUPO CRIT` and `MICHAEL PAGE` both appear, and
this plugin has adapters for both groups' own boards. Ads reachable twice get
two ledger rows, because the ids are per-board.

### Age

`datePosted` runs back to **February 2025** — 9 of 44 are over a year old. Unlike
`empleate.md`, that is not staleness: `validThrough` is filled on every ad and
none had expired, so a year-old ad here is a long-running vacancy rather than a
corpse. `--desde` is available but costs a fetch per ad; `validThrough` is the
field to trust.

## Not covered, and why

**InfoJobs** — Spain's largest private board, and a different company from this
one despite the similar name. Read again on 2026-09-01: its `robots.txt` runs
24 groups and names **twelve** AI agents, each in its own group with a bare
`Disallow: /` — `GPTBot`, `ClaudeBot`, `Claude-SearchBot`, `Claude-User`,
`PerplexityBot`, `Perplexity-User`, `Google-Extended`, `CCBot`,
`Meta-ExternalAgent`, `Meta-ExternalFetcher`, `Bytespider`,
`Applebot-Extended`. `Claude-User` is treated exactly as `ClaudeBot`; there is
no class distinction to read into it. The documented API at
`developer.infojobs.net` remains the only route. See `shared/robots-policy.md`.

**Tecnoempleo** — named Anthropic agents, ruled out; its ads reach us through
`empleate.md` instead.

**jobfluent.com** names `ClaudeBot`, `GPTBot`, `CCBot` and `Bytespider` but not
`Claude-User`. That distinction is real and worth recording, but the board is
small; it is noted here rather than built.

## Verification

```bash
S=skills/job-scan/scripts/infoempleo.py
python3 $S lugares --limit 5      # madrid 536, barcelona 345, sevilla 162 …
python3 $S search --lugar madrid --limit 4
```

The encoding trap is the one to re-check after any change, and it will not
show up in a single run. Fetch one ad eight times and count:

```bash
for i in $(seq 8); do
  curl -s -o /dev/null -D- "https://www.infoempleo.com/ofertasdetrabajo/\
tecnicoa-de-rrhh-sustitucion-maternidad/santander/3174173/" | grep -i content-encoding
done
```

Some of those eight will say `deflate` and some will say nothing. Both must
yield four `ld+json` blocks after `get()`.
