# Board adapter — lagriculture-recrute.org (ANEFA)

<!-- hosts: www.lagriculture-recrute.org -->

**2 818 offres** of French agricultural work — harvests, vineyards, livestock,
market gardening, farm machinery. The ANEFA is the sector's own employment
association, like the FHF is for hospitals, and this is the one place these ads
are gathered: no generalist board here carries the seasonal ones in any useful
number.

**Everything here was verified against the live site on 2026-09-01.**

## Fields no other board in this repository has

Present on **every one of the 47 ads measured** across three departments:

```
Hébergement possible        Oui / Non   + free-text details
Repas sur place possible    Oui / Non   + free-text details
Type d'agriculture          Conventionnelle / Bio
Caces · CertiPhyto · Permis the certificates a farm asks for
```

For someone driving 300 km for six weeks of picking, whether there is a bed is
the question that decides, ahead of the pay. **Measured, it is "Oui" on about
one ad in eleven** — 4 of 47 — and that is exactly why the field earns its
place: knowing it is *Non* before setting off is worth as much as knowing it is
*Oui*. Meals on site came back "Oui" on 8 of 47.

`CDD saisonnier` is a first-class contract value here, not a footnote: 10 of 20
ads in the Gironde.

## No robots.txt, and no employer either

There is **no `robots.txt`**: the apex `301`s every path to the `www` home
(losing the path, as `monster.fr` does), and `www/robots.txt` is a genuine
`404`. Nothing is declared, nothing is closed. No sitemap either.

**And there is no employer field.** Not empty — absent. The farm appears in the
description prose when it appears at all: *"Ferme légumière familiale implantée
à Santec, spécialisés dans la culture de vieux légumes de saison"* names no
company. The adapter emits `company: null` rather than lifting a guess out of
the prose. For `cover-letter` this means the letter is addressed to a farm the
ad does not name — say so rather than inventing one.

## Search

```
GET /rechercher/offres
    ?offer_search[geography][type]=department
    &offer_search[geography][department]=<internal id>
    &page=<n>                                        20 ads a page
```

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/anefa.py" \
  search --departement 29 --pages 5
```

The form carries a CSRF token (`offer_search[_token]`). **It is not required** —
tested with and without, same result — so the adapter does not fetch one.

No browser, no account, no key.

## Configuration

```yaml
boards:
  anefa:
    enabled: true
    departements: ["29", "33", "84"]
    pages: 5
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `departements` | recommended | **The real numbers** — `29`, `2A`, `971`. The adapter maps them; see trap 1 |
| `pages` | no | 20 ads each |

Without a department the sweep is the whole board — 141 pages. Offer this board
to anyone open to farm work, seasonal work or rural jobs, and to nobody else.

## Traps

**1. The department parameter is not the department number, and getting it
wrong returns a full page of ads in the wrong department.** The values are an
ordinal over a list in which **Corsica takes two slots where the numbering has
one**:

| Department | id | |
| :-- | :-- | :-- |
| 01 … 19 | 1 … 19 | identity |
| **2A** | **20** | |
| **2B** | **21** | the second slot |
| 21 (Côte-d'Or) | **22** | and from here, **id = department + 1** |
| 28 | 29 | |
| **29** (Finistère) | **30** | |
| 95 | 96 | |
| 971 | 97 | different again overseas |

Measured: `department=29` returns **24 ads, all of them in the Eure-et-Loir
(28)** — Magny, Arcisses, Mignières — 400 km from the Finistère and every one a
genuine French farm job. The correct id, `30`, returns **200 ads, all in the
Finistère**. Nothing errors. Both answers look right.

**The map is read from the site's own `<select>` on every run and never
computed.** A formula would work today and rot the day a department is added.

*(That makes four conventions in this repository, no two alike:
`emploi-territorial.md` wants three zero-padded digits, `labonnealternance.md`
wants exactly two characters, `batiactu.md` has no department axis at all and
uses pre-2016 region slugs, and this one wants an ordinal that drifts. Never
carry a code format from one board to another.)*

**2. There are two ways to get the whole board while believing you filtered.**

- Pass the department value **without** `[geography][type]=department` and the
  filter is dropped in silence: 2 818 ads come back.
- Pass an id the site does not know — `999` — and the same thing happens: 2 818,
  no error.

So an unfiltered sweep and a mistyped filter are indistinguishable by their
result. The adapter always sends both parameters and refuses a department that
is not in the live map.

**3. The salary is free text and often absent.** When present it reads
*"Durée du travail: 39h hebdomadaire; Taux horaire brut: entre …"* — a sentence,
not an amount. Emitted as `salary_text`, never parsed into a figure.

**4. Field names are the site's, misspellings included.** `Permi souhaité`
(one `s`), and `Détails concernant l\`hébergement` with a **backtick** where an
apostrophe belongs. They are matched exactly as the site writes them; anything
labelled that the adapter does not name is passed through in `other_fields`
rather than dropped.

### The good news

**The pagination is exact and it terminates.** 140 pages of 20, then 18 —
2 818, the announced total to the unit. Page 142 comes back with no ads *and no
total*, and so do pages 200 and 9999. Third board in a row to behave, after
`batiactu.md` and against `jobology.md` and `free-work.md`.

## The ad id and its URL

```
https://www.lagriculture-recrute.org/rechercher/offres/67683
```

In the ledger: `anefa:<id>`. The ad also carries its own `reference` —
`OFR-067683-29`, whose middle is the id and whose tail is the **real**
department number, which is a useful cross-check on trap 1.

## Applying

The apply flow needs a candidate account (*Espace candidat*); there is no
public apply link on the ad page. **The plugin does not create accounts and
does not fill credential fields.** Hand the user the ad URL with their
documents — and with the housing and meals answers, which is what this board is
for.

## Pace, and the note on access

One request per page of 20, plus one per ad read — `--no-details` skips the
second. `--delay` defaults to 0.5s. A department is a handful of pages; the
whole board is 141, which is a sweep to run once and then filter, not to repeat.
Nothing here is disallowed, because the site declares nothing at all.
