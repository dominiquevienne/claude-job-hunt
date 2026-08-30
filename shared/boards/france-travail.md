# Board adapter — France Travail

France's **public employment service**, ex-Pôle emploi. It publishes its whole
vacancy database through a free REST API, and it is the largest single source of
French ads there is. Employers post to it directly, and a dozen partner boards
feed into it.

It is the French counterpart of `job-room.md`: same institution, same role in a
sweep, and the same reason to run it next to a meta-board — it reaches the SMEs,
the communes, the associations and the staffing agencies that HiringCafe indexes
thinly or not at all.

**Everything here was verified against the live API on 2026-08-30**, with a real
client_id. Where an earlier draft of this file guessed, the guess is recorded at
the bottom with what actually happened — three of its five traps were wrong.

## The finding that decides how this adapter works

**A search that does not name `origineOffre` returns France Travail's own ads
and nothing else.** Measured on department 75:

| Query | Matches |
| :-- | --: |
| `departement=75` | 13 295 |
| `departement=75&origineOffre=1` | 3 079 |
| `departement=75&origineOffre=2` | **10 216** |

The unfiltered search reports 13 295 — and then serves only origine 1. Sampling
the result window at offsets 0, 500, 1500 and 2900 returned **150 origine-1 ads
every time, 600 of 600**. The partner ads, 77% of the board, are not merely
ranked low: they are absent.

And the miss is undetectable from inside. The reachable window is 3 150 rows
(below); department 75 has 3 079 origine-1 ads. **A sweep runs out of origine-1
ads just before it runs out of window**, so it terminates naturally, reports a
complete-looking pass, and has seen 23% of the board.

So `francetravail.py search` **runs both passes by default** and says so on
stderr. `--origine-offre` restricts it to one, deliberately. This is the
`shared/never-fail-silently.md` case in its purest form: HTTP 206, a plausible
count, a clean finish, and three quarters of the data missing.

## No browser — but credentials, which is new here

```
POST https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire
     grant_type=client_credentials & client_id & client_secret
     & scope=api_offresdemploiv2 o2dsoffre
→ {"access_token": "…"}                                    (27 characters)

GET  https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search
       ?departement=75&origineOffre=2&range=0-149
     Authorization: Bearer <token>
→ HTTP 206, {"resultats": [...]}
  Content-Range: offres 0-149/13295
```

`api_offresdemploiv2 o2dsoffre` was the scope that worked; the
`application_<client_id>` variant was not needed.

**This is the only adapter here that needs a secret**, and that changes one
thing: `francetravail.py` reads `FRANCE_TRAVAIL_CLIENT_ID` and
`FRANCE_TRAVAIL_CLIENT_SECRET` **from the environment, and from nowhere else**.
It does not read them from `config.yml` and must never be changed to — that file
is read aloud, pasted into issues and backed up, and an OAuth secret has no
business in it.

Getting the pair is free and self-service; `shared/setup.md` section 5c is the
click path.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/francetravail.py" token
```

## Configuration

```yaml
boards:
  france-travail:
    enabled: true
    departements: ["75", "92", "93"]   # or a commune + radius:
    # commune: "69123"                 # INSEE code, not a postcode
    # distance_km: 20
    publiee_depuis: 7                  # 1, 3, 7, 14 or 31 — nothing else
    type_contrat: ["CDI", "CDD"]       # optional
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `departements` | one of the two | Two-character codes as strings — `"75"`; **`"01"` keeps its leading zero** and works (6 065 offers) |
| `commune` + `distance_km` | one of the two | `commune` is an **INSEE code**, which is not the postcode. `distance_km` defaults to 10 |
| `publiee_depuis` | no | Days, and **only 1, 3, 7, 14 or 31**. Anything else is an HTTP 400 |
| `type_contrat` | no | `CDI`, `CDD`, `MIS` (intérim), `SAI` (saisonnier)… |
| `code_rome` | no | ROME job codes — the precise way to search a trade, and better than keywords |
| `scope` | no | Only if the token call returns `invalid_scope`; the default worked here |

**The credentials are not config keys.** Ask for the departments or the commune;
**`shared/setup.md` section 5c is the click path** — the portal, the
application, the subscription step everyone misses, and the check that proves it
works. Do not improvise that walkthrough here. A board switched on with no
credentials in the environment is skipped with that reason named, like any other
incomplete board.

## Building a search

Every row below was exercised on 2026-08-30.

| `search.*` config | API parameter | Verified |
| :-- | :-- | :-- |
| `keywords` | `motsCles` | yes |
| `location` (area) | `departement`, `region` | 75 → 13 295, 01 → 6 065 |
| `location` (point) | `commune` (INSEE) + `distance` (km) | Lyon `69123` → 9 031 |
| `posted_within` | `publieeDepuis` — 1, 3, 7, 14, 31 only | yes; `5` → 400 |
| — | `typeContrat` — `CDI`, `CDD`, `MIS`, `SAI` | yes |
| — | `codeROME` | yes |
| — | `experience` — `1` <1 an, `2` 1–3 ans, `3` >3 ans | yes |
| — | `qualification` — `0` non-cadre, `9` cadre | yes |
| — | `tempsPlein` — boolean | yes |
| — | `origineOffre` — `1` own, `2` partners | **load-bearing; see above** |
| — | `sort` — `0`, `1`, `2` all accepted (206) | effect not characterised |
| pagination | `range=<start>-<end>` | yes, with two hard limits |

**There is no salary filter.** `salaire.libelle` is on the response as free text
(740 of 900 ads), never as a search parameter, so minimum-pay screening happens
after the fetch, in `shared/scoring-rubric.md`.

## The ad id and its URL

The id is the offer's own reference — `213CNGF` on France Travail's own ads,
`6437418` on partner ads. Rebuild the page from it:

```
https://candidat.francetravail.fr/offres/recherche/detail/<id>
```

In the ledger: `france-travail:<id>`.

## Reading one ad — which you do not need to do

```bash
python3 .../francetravail.py ad <id>
```

**The detail endpoint returns exactly what the search already gave you.** Same
37 keys, and the description byte-identical on 6 of 6 ads compared (133, 1 074,
2 852, 3 656, 1 653 and 1 397 characters). So unlike `job-room.md` trap 8, the
per-ad read buys nothing: **score straight from the search payload** and spend
the request budget on more pages instead.

The command stays, for reading one ad by id outside a sweep.

## Traps

**1. The unfiltered search is a 77% silent loss.** Documented at the top,
because it changes the adapter's design rather than merely warning about it.

**2. `range` has two separate limits, and the API states both.** Start must be
≤ 3000 — *"La position de début doit être inférieure ou égale à 3000."* — and a
page may span at most 150 — *"La plage de résultats demandée est trop
importante."* So **the first 3 150 hits of a search are all you can ever
reach**, per origine. `3000-3149` works; `3100-3149` does not, despite being
smaller and ending at the same row. Paris has 13 295 offers and you may read
6 300 of them, 3 150 per origine. The script stops at the start limit and says
the sweep is truncated; the fix is a narrower query, never more pages.

**3. `commune` is an INSEE code, and a wrong one fails in two different ways.**
A code that does not exist is a loud 400 — `commune=75001`, the Paris 1er
*postcode*, returns *"Valeur du paramètre « commune » incorrecte."* But a
postcode that happens to also be a real INSEE code somewhere else is **silently
accepted and searches the wrong city**: `commune=13001` is the Marseille 1er
postcode *and* the INSEE code for Aix-en-Provence, and it returns Aix's 2 359
offers instead of Marseille's 3 181. There is no error and no clue. Resolve
INSEE codes from a gazetteer, never from a postcode.

**4. `commune` alone is a 10 km radius, not a commune.** Measured on Paris:
bare `commune=75056` → 25 676, `distance=0` → 9 709, `5` → 11 804, `10` →
25 676, `30` → 51 822. The API's implicit default is 10 km, so a "commune"
search quietly includes the whole ring around it. The script pins `distance=10`
explicitly so the radius is the caller's choice rather than an unstated default.

**5. Paris arrondissement codes are not distinguished.** `75056` (the aggregate),
`75101` and `75120` all return **9 709** at `distance=0` — they resolve to the
same Paris. Do not build per-arrondissement searches; they are the same search.
Lyon `69123` and Marseille `13055` likewise work as aggregates.

**6. HTTP 206 is the success case.** Every non-empty search answered
`206 Partial Content`, never 200, with the true total in
`Content-Range: offres 0-149/13295`. Code that treats anything but 200 as an
error throws away every page.

**7. Zero results is `204` with an empty body**, and `Content-Range: */0`. A
client doing `body["resultats"]` crashes on the one response that means
*"nothing here"*. The script reports it as zero with the reason.

**8. A missing offer is also a 204, not a 404.** `GET /offres/9999999` — a
well-formed id that does not exist — returns 204 with no body; only a
*malformed* id gets a 400 (*"Le format de l'id de l'offre recherchée est
incorrect."*). So on the detail endpoint 204 means **gone**, and the script
exits 3 for `discarded`. The same status code means "empty result" on search
and "deleted" on detail; do not share one handler between them.

**9. The employer is usually named — but not on partner ads.** `entreprise.nom`
was absent on **50 of 900** ads overall (5.6%), and on **34 of 150** partner ads
(23%). None of the 50 carried a company description either, so when the name is
missing there is nothing else in the record identifying the employer. This is
still far better than the agency boards, where the employer is never named: the
ledger's employer dedup works on 94% of this board.

**10. `origineOffre.urlOrigine` is not an external URL.** On all 1 050 ads
sampled, across both origines, it pointed back to
`candidat.francetravail.fr/offres/recherche/detail/<id>` — the France Travail
page itself. It is not a link to the partner's copy and it is worthless as a
dedup key. **The card does not expose it.**

**11. What does name the source is `partenaires[].nom`.** On 150 partner ads
from department 75: BEETWEEN 38, METEOJOB 30, PMEJOB 17, DIRECTEMPLOI 15,
CRECHEMPLOI 11, TALENTPLUG 7, COOKORICO 5, WE_RECRUIT 4, GOJOB 3, JOBINLIVE 3.
The card carries it as `partner`, with `partner_url`.

**And on Meteojob, that link carries the ad's own id**, so the duplicate is
exactly identifiable rather than merely suspected:
`https://www.meteojob.com/jobs/56420784?utm_source=pole-emploi&…`. The card
therefore sets `duplicate_of: meteojob:<id>` — 20 of 60 partner ads in one
measured page. When it is set and the ledger already holds that row, this is the
same posting: record it `discarded` naming the row, and do **not** apply the
fuzzy employer-name check from `skills/job-scan/SKILL.md`, which is for cases
where no such key exists.

The other partners publish a tracked link with no usable id, and get **no key
rather than a guess**. `DUPLICATE_HOSTS` in `francetravail.py` is the map, and
only boards with an adapter here belong in it — a key pointing at a row nothing
writes is worse than none.

**Sweep Meteojob directly as well as through this feed.** Its own ads name the
employer on every posting; here 23% of partner ads name nobody (trap 9). See
`meteojob.md` — and note it caps at 20 ads per search, so the two are
complementary rather than redundant.

**12. The apply URL lives in `contact.urlPostulation`, and only on France
Travail's own ads.** Present on 36 of 150 origine-1 ads, pointing at the
employer's real ATS — `jobs.ashbyhq.com`, `*.teamtailor.com`,
`job.mytalentplug.com`, `tnl2.jometer.com`. Partner ads carry `contact: {}`.
The card exposes it as `apply_url` / `apply_host`; an `ashbyhq.com` host there
is an ad this plugin can already read through `ashby.md`.

**13. Volume is not demand.** Not measured here — the equivalent of
`job-room.md`'s "one agency supplied a third of the board" was not checked, and
with a dozen partner feeds it is worth checking before reading any count as a
market signal.

## Applying

There is no in-site apply flow to drive, and **the plugin does not create
accounts and does not fill credential fields.** Hand the user `apply_url` when
there is one, the France Travail page otherwise, with their documents. Many ads
are answered by email or phone; `contact` carries that, and it goes to the user,
never into an automated send.

## Pace, and the note on access

**The API publishes its own rate limit in response headers:**
`X-Ratelimit-Burst-Capacity-Clientidlimiter: 10` with a replenish rate of 10 per
second, alongside a default limiter at 100. A sweep is a few dozen requests and
sits far below that; the script treats a `429` as a stop, never as a retry loop.
Since the detail endpoint adds nothing (above), a sweep costs one request per
page and no per-ad reads.

These are public vacancy data published by a public employment service whose
stated purpose is getting people into work, read through the interface that
service built for the purpose, under the user's own registered application. Keep
the pace human.

## What the first draft got wrong

Kept as a record, because the pattern repeats: every wrong claim came from
generalising a plausible mechanism one step past what anyone had observed.

| Claimed, unverified | Measured |
| :-- | :-- |
| The ceiling is 1 150 rows (`range` to `1000-1149`) | **3 150**, and the rule is *start ≤ 3000*, not an end index |
| Paris/Lyon/Marseille aggregate INSEE codes are refused; use arrondissements | **All three work.** Arrondissement codes are not even distinguished — 75056, 75101 and 75120 return the same 9 709 |
| A wrong commune code is the classic silent zero | **A non-existent one is a loud 400.** The silent failure is a *valid* code for the wrong town |
| `urlOrigine` points at the partner's copy and is a dedup key | It points back at France Travail on every ad sampled. `partenaires[].nom` is the real signal |
| Reading the detail endpoint is worth one request per ad | It returns byte-identical content, 6 of 6 |
| The employer is "routinely absent" | Absent on 5.6% overall — the employer is named on 94% of the board |

Two of its predictions held: 206 as the success case, and 204 for an empty
result. One thing nobody predicted — the origine split — turned out to be the
only finding that changed the code.
