# Board adapter — France Travail

France's **public employment service**, ex-Pôle emploi. It publishes its whole
vacancy database — around 300 000 live offers — through a free, documented REST
API, and it is the largest single source of French ads there is. Employers post
to it directly, and partner boards syndicate into it.

It is the French counterpart of `job-room.md`: same institution, same role in a
sweep, and the same reason to run it next to a meta-board — it reaches the SMEs,
the communes, the associations and the staffing agencies that HiringCafe indexes
thinly or not at all.

## ⚠ Status: written, **not yet verified against the live API**

**This adapter has never been run with credentials.** Rule 1 in
`shared/boards/README.md` says only document what you have run against the live
site, so this file says, per section, which side of that line it is on. Until
the *Verification* section below is filled in with measured numbers, this board
is **not `enabled: true` material** — treat it as a draft that needs one
session with a real client_id.

**Verified on 2026-08-30, by request, without credentials:**

- `GET https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search`
  answers **`401` with `WWW-Authenticate: Bearer`** and an empty body. The host,
  the path and the auth scheme are real.
- `POST https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire`
  with `grant_type=client_credentials` alone answers **`400`** — it exists and
  parses the form.
- Every guard in `francetravail.py` fires before any network call: missing
  credentials, `--commune 75056`, `--publiee-depuis 5`, `--distance` without
  `--commune`, and a filterless sweep.

**Not verified — every one of these is a claim, not a measurement:** the effect
of each search parameter, the response body's shape, the `Content-Range` header,
the 1 150-hit ceiling, the 204 behaviour, the arrondissement rule, how often
`entreprise.nom` is absent, and every count anywhere in this file. Their source
is the published documentation and a working third-party client, not a run.

## Why it earns a place next to HiringCafe

Untested for France, but the structural argument is the one `job-room.md`
measured for Switzerland: a public employment service carries a layer of
employer — small firms, communes, associations, staffing agencies — that
publishes nowhere an ATS-oriented meta-board can see. HiringCafe's own file
records **130 951 French ads**; France Travail claims around **300 000**. The
overlap is unmeasured and **measuring it is the first job of the verification
session**, not something to assert here.

## No browser — but credentials, which is new here

```
POST https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire
     grant_type=client_credentials & client_id & client_secret
     & scope=api_offresdemploiv2 o2dsoffre
→ {"access_token": "...", "expires_in": 1499}

GET  https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search?departement=75&range=0-49
     Authorization: Bearer <token>
→ {"resultats": [...]}, the match count in the Content-Range header
```

**This is the only adapter here that needs a secret**, and that changes one
thing: `francetravail.py` reads `FRANCE_TRAVAIL_CLIENT_ID` and
`FRANCE_TRAVAIL_CLIENT_SECRET` **from the environment, and from nowhere else**.
It does not read them from `config.yml` and must never be changed to — that file
is read aloud, pasted into issues and backed up, and an OAuth secret has no
business in it.

Getting the pair is free and self-service: an account on
<https://francetravail.io>, an application, then subscribe that application to
*Offres d'emploi v2*.

```bash
export FRANCE_TRAVAIL_CLIENT_ID=…
export FRANCE_TRAVAIL_CLIENT_SECRET=…
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/francetravail.py" token
```

## Configuration

```yaml
boards:
  france-travail:
    enabled: true
    departements: ["75", "92", "93"]   # or a commune + radius:
    # commune: "69381"                 # INSEE code, not a postcode
    # distance_km: 20
    publiee_depuis: 7                  # 1, 3, 7, 14 or 31 — nothing else
    type_contrat: ["CDI", "CDD"]       # optional
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `departements` | one of the two | Two-character codes as strings — `"75"`, and **`"01"` keeps its leading zero** |
| `commune` + `distance_km` | one of the two | `commune` is an **INSEE code**, which is not the postcode; `distance_km` is the radius around it |
| `publiee_depuis` | no | Days, and **only 1, 3, 7, 14 or 31**. Any other value is an HTTP 400 |
| `type_contrat` | no | `CDI`, `CDD`, `MIS` (intérim), `SAI` (saisonnier)… |
| `code_rome` | no | ROME job codes — the precise way to search a trade, and better than keywords |
| `scope` | no | Only when the token call returned `invalid_scope` — the exact string `francetravail.py` printed. Left out, the default `api_offresdemploiv2 o2dsoffre` is used |

**The credentials are not config keys.** Ask for the departements or the
commune; the client_id/secret are obtained and stored separately, and
**`shared/setup.md` section 5c is the click path** — the portal, the
application, the subscription step everyone misses, and the check that proves
it works. Do not improvise that walkthrough here. A board switched on with no credentials in the environment is
skipped with that reason named, like any other incomplete board.

## Building a search

Parameter names below come from a working third-party client, not from a run
here. The **Verified** column is what this repository has measured — currently
nothing.

| `search.*` config | API parameter | Verified |
| :-- | :-- | :-- |
| `keywords` | `motsCles` | no |
| `location` (area) | `departement`, `region` | no |
| `location` (point) | `commune` (INSEE) + `distance` (km) | no |
| `posted_within` | `publieeDepuis` — 1, 3, 7, 14, 31 only | no |
| — | `typeContrat` — `CDI`, `CDD`, `MIS`, `SAI` | no |
| — | `codeROME` — the trade, precisely | no |
| — | `experience` — `1` <1 an, `2` 1–3 ans, `3` >3 ans | no |
| — | `qualification` — `0` non-cadre, `9` cadre | no |
| — | `tempsPlein` — boolean | no |
| — | `origineOffre` — `1` France Travail, `2` partner boards | no |
| pagination | `range=<start>-<end>` | no |

**There is no salary filter.** The field exists on the response
(`salaire.libelle`, free text) but not as a search parameter, so any minimum-pay
screening happens after the fetch, in `shared/scoring-rubric.md`, not in the
query.

## The ad id and its URL

The id is the offer's own reference (`176RSNK` shape). Rebuild the page from it:

```
https://candidat.francetravail.fr/offres/recherche/detail/<id>
```

In the ledger: `france-travail:<id>`.

## Reading one ad

```bash
python3 .../francetravail.py ad <id>
```

`GET /offres/<id>` returns the full record including `description`. A deleted
offer is a 404, which the script reports as exit 3 — record it `discarded`.

## Traps

Each one is a **prediction to be confirmed or deleted** in the verification
session, not an observation. They are written down because each is a specific,
falsifiable claim, and a session that confirms three and deletes two has done
its job.

**1. The API serves only the first 1 150 hits of any search.** `range` runs from
`0-0` to `1000-1149`, 150 rows at most per page. A department-wide sweep matches
far more than that, so **paging to the end is not the same as reading the
board** — past the ceiling the rest is simply unreachable. The script stops at
the offset and says so rather than looping; the fix is a narrower search
(`codeROME`, `publieeDepuis`, one department at a time), never more pages.

**2. `commune` is an INSEE code, and the postcode looks just like one.** `75001`
is a postcode; the INSEE code for Paris 1er is `75101`. A wrong-but-plausible
code is the classic silent zero on this API.

**3. Paris, Lyon and Marseille have no usable aggregate commune code.** `75056`,
`69123` and `13055` are the codes for the cities as a whole and are not what the
search takes — the arrondissement codes are (`75101`–`75120`, `69381`–`69389`,
`13201`–`13216`). The script refuses the three aggregates by name and points at
`--departement`, which does cover the whole city. **This is the trap most likely
to be wrong as stated**: confirm what `75056` actually returns before trusting
the wording.

**4. HTTP 206 is a success, not a partial failure.** A search that does not
return every match answers `206 Partial Content` with the rows in the body and
the true total in `Content-Range: offres 0-149/1247`. Code that treats anything
but 200 as an error throws away a good page.

**5. 204 No Content is a real answer.** Zero matching offers comes back as an
empty body, not as an empty array — so a client that does `body["resultats"]`
crashes on the one response that means *"nothing here"*. The script reports it
as zero results with the reason, never as a failure.

**6. `entreprise.nom` is routinely absent.** France Travail lets an employer
post without naming itself; the ad then carries a description of the company and
no name. That is the same problem the agency boards have — no research before
applying, and **nothing for the ledger's employer dedup to match on**. The card
carries `company: null` and `company_described: true` so the difference is
visible rather than looking like a parsing bug. How often this happens is
unmeasured.

**7. `origineOffre: 2` is a syndicated ad, and the likely duplicate.** Those
carry `urlOrigine` pointing at the board the ad really lives on, and the partner
in `partenaires[].nom`. This is the France Travail analogue of job-room's
`externalUrl`, with the same consequence: a share of what this board returns is
already in the ledger under another adapter's id. Unlike job-room, **no
`duplicate_of` is emitted yet** — the id formats of the French partner boards
are not known here, so the card exposes `external_url` and `external_host` and
leaves the match to the fuzzy employer check in `skills/job-scan/SKILL.md`.
Filling that in is verification work: sweep, count the hosts, and add the ones
worth a key.

**8. The scope string is not settled.** `api_offresdemploiv2 o2dsoffre` is what
the working client uses; some applications additionally require
`application_<client_id>`. The script detects `invalid_scope` on the token call
and tells the user the exact alternative to pass to `--scope`, rather than
failing with an OAuth error nobody can act on.

**9. Volume is not demand.** The `job-room.md` finding — one staffing agency
supplying a third of the board — is the thing to check here too before reading
any count as a market signal. Unmeasured.

## Applying

There is no in-site apply flow to drive, and **the plugin does not create
accounts and does not fill credential fields.** Hand the user `external_url`
when the ad is syndicated, the France Travail page otherwise, with their
documents. Some offers are answered by email or phone rather than a form; the
detail record carries the contact, and it goes to the user, not into an
automated send.

## Pace, and the note on access

One request per page of results, one per ad read; a sweep is a few dozen. The
API is free and documented for exactly this purpose, and its published ceiling
is generous — but the token is per-application and rate limits are enforced with
`429`, which the script treats as a stop, never as a retry loop.

These are public vacancy data published by a public employment service whose
stated purpose is getting people into work, read through the interface that
service built for the purpose, under the user's own registered application. Keep
the pace human.

## Verification — what the first session with credentials must produce

Fill this in, then delete the status banner at the top and move the row in
`shared/boards/README.md` to *Shipped*.

- [ ] A token, and the scope string that actually worked.
- [ ] `Content-Range` on a real response — the header's exact shape.
- [ ] The status codes actually seen: 200 vs 206, and what a zero-result search
      really returns.
- [ ] A count per department the user cares about, dated.
- [ ] What `--commune 75056` returns — confirming or killing trap 3.
- [ ] The share of a 200-ad sample with no `entreprise.nom` (trap 6).
- [ ] The `origineOffre` split and the host distribution of `urlOrigine`
      (trap 7), which is what tells us whether a `duplicate_of` key is worth
      building and against which boards.
- [ ] Whether the detail endpoint returns more description than the search does
      — the question `job-room.md` trap 8 answered with "sometimes, so always
      read it".
