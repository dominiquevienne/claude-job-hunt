# Board adapter — Bundesagentur für Arbeit (Germany)

<!-- hosts: jobsuche.api.bund.dev, rest.arbeitsagentur.de -->

**994 348 live ads.** Germany's federal employment agency, through the API the
German state documents at `jobsuche.api.bund.dev`.

It is the fourth national public employment service here after `job-room.md`
(CH), `france-travail.md` (FR) and `empleate.md` (ES), **the first German
adapter of any kind**, and **thirty-five times** the largest board this
repository previously held.

**Everything here was verified against the live API on 2026-09-01.**

**The most useful thing this board taught is not the board.** See *You cannot
read this board*, which is the whole design.

## Access

```
GET jobsuche.api.bund.dev/openapi.yaml          → the state's own specification
GET /pc/v6/jobs?wo=…&size=100&page=…            → the list, header X-API-Key
GET /pc/v4/jobdetails/{base64(referenznummer)}  → the ad text
```

Base: `https://rest.arbeitsagentur.de/jobboerse/jobsuche-service`

**No browser, no account, and the key is printed in the specification.** The
OpenAPI description says, in its own words: *"Die Authentifizierung
funktioniert über die clientId: `jobboerse-jobsuche`"*, passed as `X-API-Key`.
Nothing here is a credential belonging to anybody — it is the identifier the
operator publishes for third parties, in the German government's own API
directory, `bund.dev`.

`arbeitsagentur.de/robots.txt` is four lines and opens everything —
`Disallow:` empty, `Allow: /`, three sitemaps. **No crawler and no AI agent is
named.** Question 1 of `shared/robots-policy.md` does not arise; question 2 —
*is there a sanctioned door?* — is answered by the state publishing one.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/arbeitsagentur.py" \
  read --wo Berlin --seit 7
```

**A stale path in the same specification is dead.** The spec offers
`/pc/v6/jobs` *and* `/pc/v4/app/jobs`; the second answers **403 with a
one-byte body**, which reads exactly like a rejected key. Every third-party
write-up still shows v4. The adapter names this in its 403 handler so an hour
is not lost hunting for a key that was never the problem.

## You cannot read this board

```
page=100, size=100   →  200, 100 ads
page=101             →  400
```

**The reachable window is 10 000 ads per query. The board is 994 348.**

A query answers with `maxErgebnisse: 45901` for Berlin and will hand over
10 000 of them. No parameter lifts the ceiling. So **the number this API
reports is not the number it will give you**, and an adapter that pages until
the pages run out reports a complete sweep of Berlin having read 22% of it —
a clean, plausible, wrong result, with a large and confident count attached.

This adapter therefore checks every count against the ceiling **before it
pages**, and **refuses** a query it cannot deliver whole rather than
truncating it:

```
$ arbeitsagentur.py search --wo Berlin
ERROR: this query matches 45901 ads and the API will only ever return 10000
of them — 35901 are unreachable, and no parameter lifts the ceiling
(page 101 answers HTTP 400).
```

`--limit N` takes the first N knowingly; that is a decision the user makes,
not one the adapter makes for them.

### Slicing until it fits — measured

| Query | Matches | |
| :-- | --: | :-- |
| *(no filter)* | 994 346 | unreachable |
| `--wo Berlin` | 45 901 | unreachable |
| `--wo Berlin --seit 7` | **8 786** | fits |
| `--wo Berlin --seit 1` | **3 114** | fits |
| `--wo Berlin --was Entwickler` | **173** | fits |
| `--berufsfeld Informatik` | **10 002** | **misses by two** |
| `--berufsfeld Informatik --seit 7` | **1 775** | fits |

**`berufsfeld=Informatik` is the one to remember: 10 002 against a ceiling of
10 000.** It looks like it fits. Run `arbeitsagentur.py count` before a sweep
— it prints `fits_under_ceiling` and the exact overflow.

The recipe that works is **a place plus a recency window**: `--seit 7` for a
weekly sweep, `--seit 1` for a daily re-scan. `--seit` takes 0–100 days.

## Configuration

```yaml
boards:
  arbeitsagentur:
    enabled: true
    searches:
      - { wo: "Berlin", seit: 7 }
      - { wo: "München", seit: 7 }
      - { berufsfeld: "Informatik", seit: 7 }
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `wo` | recommended | Place — a city, or a postcode. Pair it with `seit` |
| `seit` | **effectively yes** | Days since publication, 0–100. **The filter that makes a city fit** |
| `was` | no | Free text in the title |
| `berufsfeld` | no | Occupational field — `Informatik`, `Pflege` |
| `arbeitgeber` | no | Employer name |
| `umkreis` | no | Radius in km around `wo` |

## What it carries that nothing else here does

**`istArbeitnehmerUeberlassung` — the ad's own declaration that the work is
*Leiharbeit*, hired out through a temp agency.** True on **15 of 40**.

Every agency board in this repository — `adecco.md`, `randstad-fr.md`,
`crit.md`, `infoempleo.md` — leaves the reader to infer that from the
employer's name, and `infoempleo.md` records the consequence: a filled
employer field that names an intermediary is *less* honest than an empty one,
because nothing flags it. **Here the publisher states it, because German law
makes them.** `istPrivateArbeitsvermittlung` (5 of 40) marks private placement
the same way.

**`allianzpartnerName`, on 40 of 40**, names the channel the ad came in
through: `arbeitsagentur.de` on 8 of 40 — posted directly — and a partner on
the other 32 (`talent360 GmbH` 16, `HOGAPAGE Media GmbH` 6, `Hays AG` 3). The
board states how much of itself is syndicated, which no other board here does.

**`quereinstiegGeeignet`** — *suitable for a career changer* — on 20 of 200.
For a user in reconversion that is the single most useful flag on any board in
this plugin, and it is set by the employer.

Both `ist…` flags and `allianzpartnerName` are **detail-only**: they cost one
request per ad. That is what `read` spends and `search` does not.

## What the record carries

Listing measured on 200 ads Germany-wide; detail on 40 across six cities and
26 distinct employers.

| Field | Coverage | Note |
| :-- | --: | :-- |
| `firma` (employer) | **200/200** | Always named |
| `adresse.ort`, `region`, `land` | 200/200 | |
| `adresse.plz` | **192/200** | A real postcode — the field a PRE/ORP form wants |
| `adresse.strasse` | 81/200 | The full street on two ads in five |
| coordinates | 200/200 | |
| `datumErsteVeroeffentlichung`, `aenderungsdatum` | 200/200 | Real per-ad dates |
| `eintrittszeitraum.von` (start date) | 200/200 | |
| `vertragsdauer` | 200/200 | `UNBEFRISTET` 150, `KEINE_ANGABE` 43, `BEFRISTET` 7 |
| `gehaltsspanneVon` / `Bis` | **69/200** | A real range on a third of ads |
| `quereinstiegGeeignet` | 20/200 | |
| `chiffrenummer` | 38/200 | An anonymised ad — applied to through the agency |
| `externeURL` | 26/200 | An off-site apply link |
| `homeofficemoeglich` | 8/200 | Remote is essentially not stated here |
| **`stellenangebotsBeschreibung`** | **40/40**, detail | Median **2 589 characters**, 39 of 40 over 300 |

**The salary figures are usually an hourly rate.** `verguetungsangabe` is
`STUNDENLOHN` on 94 of 200 and `JAHRESGEHALT` on 7, so `gehaltsspanneVon:
18.5` means €18.50 an hour. Read as a monthly or annual figure it is absurd by
three orders of magnitude — the same class of error as `join.md`'s minor
units, where `2035` means `20.35`. The card carries `salary_kind` next to the
numbers for exactly this reason.

`verguetungsangabe` is `KEINE_ANGABEN` on 97 of 200, so a little under half the
board says something about pay and a third gives a range.

## Ad kinds — it is not only jobs

`stellenangebotsart` across 200: **`ARBEIT` 179, `AUSBILDUNG` 18,
`SELBSTAENDIGKEIT` 2, `PRAKTIKUM_TRAINEE` 1.**

*Ausbildung* is the German dual apprenticeship — a three-year training
contract, not a job, and `cover-letter` should treat it the way
`labonnealternance.md` treats French apprenticeship. The card carries
`offer_kind` and every run prints the split, so a sweep that is a fifth
apprenticeships says so.

## Verification

```bash
S=skills/job-scan/scripts/arbeitsagentur.py
python3 $S count  --wo Berlin                 # 45 901, fits_under_ceiling false
python3 $S count  --wo Berlin --seit 7        # 8 786,  true
python3 $S search --wo Berlin --seit 1 --limit 3
python3 $S read   --wo München --seit 3 --limit 3   # + description, temp flags
```

The refusal is the behaviour to re-check after any change, because its failure
mode is a large confident number:

```bash
python3 $S search --wo Berlin      # → must ERROR, not return 10 000 quietly
```
