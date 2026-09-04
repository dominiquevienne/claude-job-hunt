# Board adapter — La Bonne Alternance

<!-- hosts: api.apprentissage.beta.gouv.fr -->
<!-- script: labonnealternance.py -->
<!-- countries: FR -->

A French state service for **apprenticeship and alternance**, run by the
Mission Apprentissage. One call returns two different things, and the second is
why it is here.

**Everything here was verified against the live API on 2026-08-31**, with a
sandbox key — which turns out to matter (trap 1).

## Companies that hire apprentices without advertising

```
GET /job/v1/search → {"jobs": [...], "recruiters": [...], "warnings": [...]}
```

- **`jobs`** — posted apprenticeship ads, aggregated from other boards.
- **`recruiters`** — **companies that take apprentices and have posted
  nothing.** No other board in this repository carries those, and for
  alternance they are most of the opportunity: a search of the Rhône returned
  **300 ads and 150 such companies**.

The adapter emits both, tagged `kind: "job"` or `kind: "opportunity"`. An
opportunity has no title, no description and no ad URL, because there is no ad
— it has a named company, a SIRET, an address, a size and a sector. That is a
different kind of row and `cover-letter` should treat it as one: a spontaneous
application, not a reply.

## The key, and what a sandbox key costs you

Free and self-service: an account at **https://api.apprentissage.beta.gouv.fr**,
then a token. The adapter reads it from `LBA_API_KEY` in the environment and
**never from `config.yml`**.

```bash
export LBA_API_KEY=…
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/labonnealternance.py" \
  search --departement 69
```

The API's own OpenAPI document is at `/api/documentation/json`, and it says a
**sandbox** key is granted automatically while a **production** key is
requested from support. Read trap 1 before deciding that does not matter.

**The old key-free `/api/v1/jobs` on `labonnealternance.apprentissage.beta.gouv.fr`
is gone** — every shape of it answers 404. Do not restore it from memory.

## Configuration

```yaml
boards:
  labonnealternance:
    enabled: true
    departements: ["69", "01"]
    romes: ["M1805"]        # optional
    jobs_only: false        # keep the companies; they are the point
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `departements` | one of the two | **Exactly two characters** — `69`, `01`, `2A`. See trap 2 |
| `lat` / `lon` / `radius` | one of the two | Radius barely matters; see trap 3 |
| `romes` | no | ROME codes. The strongest narrowing available |
| `jobs_only` | no | Drops the companies. Usually the wrong choice |

Offer it to anyone looking for an apprenticeship or a work-study place, and to
nobody else — every row here is alternance.

## Traps

**1. A sandbox key hands out staging links.** All **150** of the companies
returned in the Rhône carried an `apply.url` on
`labonnealternance-recette.apprentissage.beta.gouv.fr` — the **test
environment**. Passed to a candidate, that is a dead link discovered after the
letter is written. The adapter blanks `url`, keeps the value in `staging_url`
and sets `apply_url_unusable: true`, and the run says how many were affected.
**The posted ads are unaffected** — their apply URLs point at the source board
and are real. If the companies matter, ask support for a production key.

**2. A department code is exactly two characters, and three wrong shapes fail
three different ways — none of them an error.** Measured:

| Passed | Result |
| :-- | :-- |
| `69` | 293 of 300 jobs in the Rhône — **correct** |
| `069` | **0 jobs**, silently |
| `1` | 300 jobs in **13, 14, 17** — a silent prefix match |
| `075` | jobs in **07, the Ardèche** — silently the wrong department |

The last is the worst answer a board has given in this repository: not empty,
not everything, a plausible board from two hundred kilometres away. The script
validates the shape before asking rather than passing it through.

*(Note the opposite convention on `emploi-territorial.md`, where the code is
three digits and two returns zero. Two French public services, two rules, both
silent. Never carry a code format from one board to another.)*

**3. Both lists are capped, and the cap does not move.** Jobs came back at
~300 and companies at exactly **150** for radius 10, 30, 100 **and 200 km**. A
full-looking result is the ceiling, not the market — narrow with `--rome`, not
with a bigger radius, which does nothing. The script says which number is a cap.

**4. Most of the ads are republished from boards this plugin already sweeps.**
In the Rhône: **France Travail 226, Meteojob 38**, Nos Talents Nos Emplois 21,
La Poste 8. But the row carries the source's own id in
`identifier.partner_job_id`, so the duplicate is **exact, not suspected** —
264 of 450 cards came back with a `duplicate_of` such as
`france-travail:212MBDM`. When the ledger already holds that row, this is the
same posting: record it `discarded` naming the row.

Only boards with an adapter here are mapped; the rest get no key rather than a
guess.

**5. `warnings` is part of the response, and is not decoration.** The API
returns a `warnings` array alongside the results. It was empty on every call
measured — which is exactly why it must be printed when it is not.

## The ad id and its URL

The id is La Bonne Alternance's own (`6a7f935f9ef8f4ccc56c4bdd`). In the
ledger: `labonnealternance:<id>`.

There is no canonical page on this service: `apply.url` points at wherever the
ad really lives — `candidat.francetravail.fr`, `www.meteojob.com`,
`www.directemploi.com`, `app.mytalentplug.com`. Hand the user that.

## Applying

The API has a `POST /job/v1/apply` route. **It is not used and should not be**:
this plugin never sends an application on the user's behalf, and a sandbox key
would route it through the test environment anyway. Hand the user the URL with
their documents.

## Pace, and the note on access

One request per search — there is no pagination, only the caps in trap 3. So a
sweep of three departments is three requests, which makes this the cheapest
board here after `taleez.md`.

The site's `robots.txt` closes its own UI search paths and says nothing about
`/api/`; this uses the documented API, under the user's own registered key, at
the volume one person's job search needs.

## Why this adapter does not call the guard — HELD, same class

`api.apprentissage.beta.gouv.fr` answers `/robots.txt` with **145 778 bytes of
its own single-page application** — `text/html`, no directive line anywhere.
Since #128 the guard reads that as `unrecognised`. **What that state means
changed on 2026-09-04**: the owner decided an absence of rules is an open door,
so the verdict is now `allowed: True` with **`certain: False`** — a policy
applied to an absence, not an absence established. An adapter calling the guard
would no longer stop here.

**Which rule covers it: `unrecognised`**, not the API rule — and the
distinction is the whole point. `api.apprentissage.beta.gouv.fr` **answered and
expressed no rule.** It did not refuse. The other three keyed boards
(`api.francetravail.io`, `api.adzuna.com`, `rest.arbeitsagentur.de`) were
explicitly closed and fall under the API rule instead. **A host that refuses
and opens a door beside it is not a host that says nothing.**

*(The 145 778 is a byte count, measured on the wire. Until v1.203.0 the guard
reported `len()` of the decoded string and called it bytes; the same page reads
145 672 characters, and the two were once published as a size that changed
between readings — #130.)*

**Not wired, because it is the same class as `adzuna.md`** — a documented
public API whose host does not serve usable rules — and that class is in
arbitration with the user. **Four boards, one arbitration.**
