# Board adapter — turijobs.com (Spain, hospitality)

<!-- hosts: www.turijobs.com -->
<!-- siblings: turijobs.com 2026-09-04 agree -->
<!-- script: turijobs.py -->
<!-- countries: ES -->

**2 863 active ads** in tourism and hospitality — hotels, kitchens, front
desk, spa, housekeeping. The fourth Spanish adapter here and **the first
sector board**: `empleate.md` and `oposiciones.md` are the SEPE's registers,
`infoempleo.md` is a generalist. Tourism is the sector the generalists cover
worst in Spain, and this is where the chains post directly.

**Everything here was verified against the live site on 2026-09-01.**

## Access

```
GET /robots.txt                             → nine Sitemap: lines, one per locale
GET /es/sitemap/index.xml                   → nine files
GET /es/sitemap/active-offers.xml           → 2 863 ads, a real lastmod on each
GET /es/oferta-trabajo/<city>/<slug>/<id>   → the ad, inside __NEXT_DATA__
```

**No browser, no account, no key.**

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/turijobs.py" \
  search --ciudad barcelona --pais ES
```

### `robots.txt` — allowed, and worth reading carefully anyway

23 groups, **no crawler and no AI agent named**. The ad path and the sitemaps
are open. What the `*` group closes is duplicate-language URLs — each locale
disallows the paths belonging to the *other* languages and leaves its own
open:

```
Disallow: /es/anuncio    Disallow: /en/oferta     Disallow: /es/job
Disallow: /es/offerte    Disallow: /pt-pt/oferta  Disallow: /*.aspx
```

`/es/oferta-trabajo/…` — the Spanish ad path — matches none of them. Checked
rule by rule against a real ad URL, not by trusting a parser; see the trap
below for why that distinction mattered here.

**On Python 3.13 and earlier, `urllib.robotparser` reports ALLOW on paths
this file explicitly closes.** Two independent defects, both erring towards
permission — and **both fixed in 3.14**:

| Interpreter | wildcard honoured | rule after a blank line kept |
| :-- | :-- | :-- |
| 3.9.6 (`/usr/bin/python3`, macOS) | no | no |
| 3.13.5 | no | no |
| 3.14.6 | **yes** | **yes** |

*(3.9.6 and 3.14.6 measured here; 3.13.5 measured by a sibling session, which
is what turned a flat claim into a version boundary. The first draft of this
file stated the defect without the bound — it was true on the interpreter it
was measured on and false on the next one.)*

**That makes it worse, not better.** Every script here starts
`#!/usr/bin/env python3`, so the interpreter is the user's, and on macOS
`/usr/bin/python3` is still 3.9.6. The defects:

```python
>>> rp.parse(["User-agent: *", "Disallow: /*.aspx"])
>>> rp.can_fetch("*", "https://h/x.aspx")
True                       # the rule is stored as "/%2A.aspx" — the
                           # wildcard is percent-encoded and can never match

>>> rp.parse(["User-agent: *", "Disallow: /a", "", "Disallow: /b"])
>>> rp.can_fetch("*", "https://h/a"), rp.can_fetch("*", "https://h/b")
(False, True)              # a blank line ends the record; the rules after it
                           # belong to no agent and are silently dropped
```

This file has a blank line before its 25 locale rules, and it uses `*` in
`/*.aspx` and `*/admin/`. So on a pre-3.14 interpreter a `robotparser` check
drops **every rule that matters** and answers ALLOW to `/es/anuncio`,
`/en/oferta` and `/x.aspx` alike.

**It does not change the verdict here** — the ad path is allowed under a
strict, correct reading too, which is the only reason this adapter exists. But
a robots check that returns ALLOW because it silently discarded the rules is
not a check. Neighbouring cases are in issue #53.

## Configuration

```yaml
boards:
  turijobs:
    enabled: true
    searches:
      - { ciudad: "barcelona", pais: "ES" }
      - { ciudad: "islas-baleares", pais: "ES" }
    desde: "2026-09-01"
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `ciudad` | recommended | **Free** — read from the URL before any fetch. 127 values; `turijobs.py ciudades` lists them |
| `desde` | recommended | **Free** — on `lastmod`, which is genuinely per ad: **2 506 distinct values across 2 863** |
| `pais` | recommended | ISO-2. **Costs a fetch per ad** — the country is inside the ad. See below |

Both free filters are real here, which is unusual: `infoempleo.md` has the
place but no date, `crit.md` the date but no place.

## What it has that nothing else here does

**`applies` — the number of people who have already applied.** Median 10, up
to 156, present on 39 of 40. No other board in this repository publishes it,
and it answers a question a candidate otherwise cannot ask: is this a queue of
three or of a hundred and thirty.

It is emitted as `applicants_so_far`. Treat it as the board's own counter, not
a verified figure — but it is the board's own counter, which is more than a
guess.

**A real postcode on 38 of 40**, where `infoempleo.md` and `hays-fr.md` have
none at all. Only 3 of those are a `<province>000` placeholder, and the card
flags them (`postcode_looks_like_placeholder`). Plus coordinates on 40 of 40,
the employer's own street address, sector and careers URL.

## Traps

**1. The salary field reads three different ways and only one is true.**

| Reading | Count | Would report |
| :-- | --: | :-- |
| `salary` object is present | **40 of 40** | "100% state a salary" |
| `salaryVisible: true` | **27 of 40** | "67% state a salary" |
| `salaryMin` or `salaryMax` **> 0** | **2 of 40** | **5%** |

`salary` is never absent — it is an object on every ad, so a presence check
reports total coverage. `salaryVisible` is true on two thirds, and **25 of
those 27 carry `salaryMin: 0, salaryMax: 0`**. `salaryType` says `YEAR` on 26
ads, of which two state an amount: the *unit* is filled in where there is no
number.

This is `infoempleo.md`'s `value: 0.0` one level worse. There the zero sat in a
sub-field; here the whole object is present **and** a boolean asserts it is
visible. Only `> 0` is a salary. Both flags are kept on the card so that an ad
with no figure but `salary_marked_visible: true` is explicable rather than
mysterious.

**2. The employer is named on every ad, and not where you would look.**

```
company.name            0 of 35     ← the field every JSON-LD board here uses
company.brandName      35 of 35     ← Meliá, Barceló, Catalonia Hotels, H10
company.enterpriseName 35 of 35     ← differs from brandName on 6 of 35
```

**`company.name` does not exist in the payload at all.** A reader that asks
for it gets `None` on a board that names the employer on every single ad —
the third instance in the Spanish series of *the field with the expected name
is empty and the data is under a different one*, after `empleate.md`'s
`baseSalary` and `infoempleo.md`'s `value.value`.

And these are the **real employers**, not agencies: the opposite of
`infoempleo.md`, where 32 of 44 were ETTs. The concentration is in the chains
instead — 16 distinct employers across 35 ads, Meliá alone 15. `features`
states the employer *type* (`Cadena hotelera`, `Empresa de selección / ETT`),
so on this board you can tell which you are looking at.

**3. A locale is not a country, at two and a half times `wttj.md`'s rate.**

The `/es/` sitemap is the **Spanish-language** board, not the Spanish one.
Across 40 sampled ads: **Spain 30, Germany 4, Portugal 3, France 1, Italy 1,
Mexico 1** — and Andorra turns up in the city list as `canillo`. Ten of forty
outside Spain.

`--pais ES` filters on the ad's own `countryISO`. It costs a fetch per ad,
because the country is inside the ad and not in the URL; every run reports the
split it saw either way.

**4. The ad is 0.9% of the page.**

The median ad page is **706 000 characters** and the ad inside it is **6 290**.
The rest is the i18n bundle plus `relatedOffers` and `companyOffers` — two
other ad lists shipped with every ad. Nothing can be done about it from the
outside; it is stated so that a sweep's cost is not a surprise, and it is why
`--ciudad` and `--desde` matter more here than on a cheaper board.

## What the record carries

The whole ad is in `props.pageProps.offerData.offerDetail` of `__NEXT_DATA__`
— the same shape as `join.md`. There is **no JSON-LD JobPosting**: the page's
single `ld+json` block is a `BreadcrumbList`, so a JSON-LD reader finds
nothing and reports the ad as unreadable. Measured on 25 ads, that reader
scored **0 of 25**.

| Field | Coverage | Note |
| :-- | --: | :-- |
| `title`, `description` | 25/25 | Median **1 486 characters**, up to 6 563 |
| `company.brandName` | 35/35 | See trap 2 |
| `location.zipCode` | 38/40 | Real postcodes |
| `location.latitude/longitude` | 40/40 | |
| `applies` | 39/40 | The applicant count |
| `publicationDate`, `updatingDate`, `expiringDate` | 25/25 | All three, per ad |
| `requirements` | 25/25 | **A dict**, not prose: `DEGREE` and `EXP_YEARS` always, `LANGUAGES` and `WORK_PERMIT` on 2 |
| `features` | 25/25 | Education, experience band, contract, working time, job family, employer type |
| `additionalRequirements` | 9/25 | A string |
| `benefits`, `assignments`, `skills`, `preferences` | **0/25** | Present in the payload, empty on every ad measured |

Four fields exist and are never filled. They are read anyway, so the day they
start carrying something it is one line — and reported as absent rather than
quietly dropped.

**`ownerName` is a natural person** — the recruiter who posted the ad, filled
on 40 of 40 with names like *Marta Pérez Fernández*. It is not the employer, it
is not needed to decide or to apply, and `shared/robots-policy.md` is explicit
that nothing here licenses personal data. **It is read and deliberately not
emitted.**

The description's markup is machine-written: every paragraph carries an inline
`style` with a generated font name (`__IBMPlexSans_873584`) that changes on
every build. Stripped entirely.

## Verification

```bash
S=skills/job-scan/scripts/turijobs.py
python3 $S ciudades --limit 5        # barcelona 395, islas-baleares 374 …
python3 $S search --ciudad barcelona --pais ES --limit 3
python3 $S search --desde 2026-09-01 --limit 12   # reports the country split
```

The guards, all of which fail silently at the network layer if removed:

```python
entries()                       # N <url> blocks, 0 <loc> → reading fault (#55)
card(url_with_no_next_data)     # → dies: the ad IS __NEXT_DATA__
money({"salaryVisible": True, "salaryMin": 0})   # → (None, None, None, True)
```
