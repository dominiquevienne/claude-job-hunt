# Board adapter — Empléate, public sector (oposiciones)

<!-- hosts: empleate.gob.es -->

**1 558 live announcements**, ~3 438 posts, from the second Solr index behind
`empleate.gob.es`. Spanish public-sector recruitment: *oposiciones*, *bolsas de
trabajo*, *convocatorias* — the competitive examinations and standing lists
that fill civil-service and public-body jobs.

`empleate.md` covers the same host's private index and is a **different board**
in almost every respect. Read this file rather than assuming its sibling
applies; the two endpoints disagree about the one thing that matters most, and
neither announces which contract it is honouring.

**Everything here was verified against the live index on 2026-09-01.**

**The most useful thing this board taught is not the board.** See trap 1.

## Status on 2026-09-04 — **the board is dark, and the remaining cause is a decision**

**Do not read a zero from this adapter as a market.** It returns nothing today,
and it stops before it reaches the index.

`https://empleate.gob.es/robots.txt` answers **HTTP 200, `Content-Type:
text/html`, ~8 456 bytes** — the SEPE error page, `<title>SEPE</title>`, *"Si el
problema persiste, póngase en contacto con nosotros"*. It is not a rules file
and it is not an absence of one. `_robots.py`'s `unrecognised` state (#128)
refuses to guess in either direction, so **both adapters on this host exit
refused**, this one and its sibling.

Three things measured on 2026-09-04 that say what it is:

| observation | reading |
| :-- | :-- |
| three consecutive reads, **identical length, three different md5s** | the body is generated per request — a fixed document does not do this |
| the same length under `Claude-User` and under a browser token | **not** UA-conditional; this is not a bot wall, and must not be reported as one |
| the page carries `<META NAME='ROBOTS' CONTENT='NOINDEX,NOFOLLOW'>` | the word *robots* is present with no directive behind it — a parser matching on the word alone would read this as rules |

**What has been repaired, and what has not.** The TLS half is fixed: this host
sends its leaf without the issuing intermediate, `empleate.py` was given
`_tls.context_for` and **this adapter was not**, though both read the same host.
Measured: bare stdlib gives `CERTIFICATE_VERIFY_FAILED — unable to get local
issuer certificate`, the same URL through `_tls` gives HTTP 200. Fixed in
v1.202.0, and a test now binds every reader of a `_tls.HOSTS` host to the
module.

**That repair lights nothing on its own**, and it was made anyway: a known
defect is not held back because its fix is not sufficient, and when the
remaining question is answered there will be one step left instead of two.

**The remaining cause is not a bug.** What to do about a host whose
`/robots.txt` is an error page is a policy decision — treat it as absent, treat
it as refusal, record a hand-read exception — and the guard deliberately
declines to take it. **Nobody should wire around this to make the board return
rows.** Tracked in #104.

## Access

```
GET /empleate/open/publicoffersearch/selectBuscador   → Solr, open, no key
     ?q=*&wt=json&rows=100&fq=speStateId:1
https://empleate.gob.es/empleo/#/trabajoPublico?search=<id>   → the ad
```

Same `robots.txt` as the sibling: nine lines, `Allow: /`, six logged-in paths
closed, no crawler and no AI agent named. Nothing to weigh.

**There is no per-ad page on `empleate.gob.es` for a public offer.** The card
links straight out to the source. The URL above is the site's own share link
for these records — read out of its `getOfferLink` / `FBshareOffer` pair, where
EURES, SNE, WEB and MISOS ads get `#/oferta/<id>` and everything in this index
gets the search page pinned to the id. It is not invented, and it resolves:
`q=<id>` returns exactly that record.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/oposiciones.py" \
  search --provincia BARCELONA --grupo A1
```

**No browser, no account, no key.**

## Configuration

```yaml
boards:
  oposiciones:
    enabled: true
    searches:
      - { provincia: "BARCELONA", grupo: "A1" }
      - { comunidad: "MADRID" }
    dias_restantes: 7
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `provincia` | see trap 3 | **Not always the post's province.** `oposiciones.py provincias` |
| `comunidad` | recommended | Often the more reliable of the two. See trap 3 |
| `grupo` | no | Civil-service group — `A1`…`E` (funcionario), `GP1`…`GP5` (laboral). `oposiciones.py grupos` |
| `acceso` | no | `Ingreso libre`, `Interinidad`, `Contratación fija`, `Estatutaria`. `oposiciones.py accesos` |
| `personal` | no | `Personal Funcionario`, `Personal Laboral`, … |
| `ambito` | no | `Local`, `Autonómico`, `Nacional`, `Internacional` |
| `organismo` | no | Phrase in the hiring body's name. `oposiciones.py organismos` |
| `dias_restantes` | recommended | Keep only what is still open in N days — a dossier takes time to assemble |
| `incluir_cerradas` | no | Keep expired announcements, marked. Off by default |

## Traps

**1. The field that names the deadline is a constant.**

```
facet estadoPlazoF over the whole index  →  Abierto: 76050
```

`estadoPlazoF` reads **"Abierto" on all 76 050 records** — on the 74 492 the
same index marks `Inactiva`, on announcements that closed in 2025, on
everything. It is not a status. It is a string that is always there.

On a board of competitive examinations that is the whole object: nobody applies
to an oposición they cannot enter. And the arithmetic is not academic —

```
live (speStateId:1)                                 1 558
  … deadline still in the future                    1 060
  … deadline ALREADY PASSED                           498   ← all "Abierto"
```

**498 of the 1 558 live announcements — 32% — have an application window that
has already shut**, and the board stamps every one of them open.

So the state is **computed from `fechaPresentacion` and never read from
`estadoPlazo`**. The adapter excludes closed announcements by default, says so
in the run, and offers `--incluir-cerradas` to see them marked. The literal
field is still emitted as `deadline_status_field_literal` so nobody
rediscovers it.

*(`fechaFinPublicacionFormateada` is identical to `fechaPresentacion` on 500 of
500 measured — there is no second, later date to fall back on.)*

**2. The sibling adapter's base filter returns an empty board here.**

```
publicoffersearch   fq=checkVisible:1   →      0   echoed back unchanged
publicoffersearch   fq=speStateId:1     →  1 558
publicoffersearch   no fq               → 76 050   (74 492 of them inactive)
```

`empleate.md`'s trap 1 is that the server **injects** `(speStateId:1 OR
speStateId:4)` whenever a request carries any `fq`, so `checkVisible:1` is sent
purely to trigger the injection.

**This endpoint injects nothing, and has no `checkVisible` field at all.** The
same clause is echoed back untouched and matches zero documents. Two adjacent
endpoints on one host, opposite contracts, no announcement of which is which —
and the failure modes are mirror images: on the sibling, forgetting the filter
gives you four times the board; here it gives you **forty-nine times** the
board, 98% of it dead.

The live filter is ours to supply, so the adapter adds it, refuses an `fq`
mentioning `checkVisible`, and asserts `speStateId:1` in the echoed parameters
on every response.

*(The divergence runs the other way too: `fq=comunidadF:CASTILLA LEON`,
unquoted, answers `FAIL!` on the sibling and 1 509 here. Quote values on both.)*

**3. `--provincia MADRID` returns 42 jobs and none of them are in Madrid.**

Across all 1 558 live records, **42 carry a province and a region that cannot
both be true** — and it is not a scattering of typos. All 42 are:

```
provinciaF: MADRID    comunidadF: CATALUÑA
```

Catalan posts advertised by nationally-seated bodies — Ineco, Tragsatec, a
ministry — where CIDO has filled `provinciaF` with **the hiring organisation's
seat** rather than the post's location. The titles say Barcelona and Girona.

Meanwhile the **50 real Madrid-region announcements carry no province at all**,
so a province filter misses every one of them.

| Filter | Returns | Actually in Madrid |
| :-- | --: | --: |
| `--provincia MADRID` | 42 | **0** |
| `--comunidad MADRID` | 50 | 50 |

This is the trap a user actually hits: a full-looking result set of jobs 600 km
away. The adapter warns on `--provincia MADRID` by name before it queries, and
flags any record whose province and region disagree.

## What the board is, and is not

**It is not national in practice.** 1 334 of the 1 558 live records come from
**CIDO**, the Diputació de Barcelona's register, and **1 291 of the 1 391 that
carry a province are Catalan**:

| Province | Live |
| :-- | --: |
| Barcelona | 965 |
| Tarragona | 161 |
| Girona | 104 |
| Lleida | 61 |
| Madrid *(see trap 3)* | 42 |
| Illes Balears | 12 |
| Valencia | 12 |

The index is national; what is *live* in it is Catalan local government. Offer
it accordingly, and say so rather than letting a user in Seville conclude the
Spanish public sector is not hiring.

**There is no ad text.** `contenido` is one line — median **118 characters**,
longest 289, and never a copy of the title. What the record carries is the
title, the hiring body, the group, the access route and the dates. The notice
itself is on `cido.diba.cat` or `administracion.gob.es`.

**`cover-letter` therefore has nothing to read on this board**, and the adapter
says so on every record with `has_full_text: false`. That is a property of the
source, not a gap to paper over: an oposición is answered with a form and a
documented dossier, not with a letter written from a 118-character summary.

## What the record does carry

Measured on all 1 558 live records, and by field on 300.

| Field | Coverage | Note |
| :-- | --: | :-- |
| `organismo` (hiring body) | **300/300** | Named on every record — against 29% on the private board |
| `fechaPresentacion` | **1 558/1 558** | The deadline. The only honest state on this board |
| `grupoF` | 300/300 | A1–E funcionario, GP1–GP5 laboral — a real qualification signal |
| `tipoAccesoF` | 300/300 | Contratación temporal 29 630, Interinidad 14 366, Contratación fija 14 094, Ingreso libre 13 458 *(whole index)* |
| `ambitoGeograficoF` | 300/300 | Autonómico, Local, Nacional, Internacional |
| `educacionF` | 300/300 | |
| `localizacion` | 300/300 | `lat,lon` |
| `provinciaF` | 265/300 | **See trap 3** |
| `trabajosOfertados` | 237/300 | Posts offered; 0 on the rest |
| `contenido` | 285/300 | One line — see above |

**The home page's counter counts posts, not announcements.**
`open/home/getTotalJobsOfferedPublic` returns `3.441`, and the sum of
`trabajosOfertados` over the live set is **3 438** — a match. So 1 558
announcements offer roughly 3 438 plazas. The same relation explains the
private board's `55.300` against its 28 099 ads: neither figure is an ad count.

## The links out, and why they stay links

`url` is on every record, pointing to the source notice:

| Host | Share of 300 | `robots.txt` |
| :-- | --: | :-- |
| `cido.diba.cat` | 250 | **none published** — the request is refused outright |
| `administracion.gob.es` | 50 | Allows all bots, but **`Crawl-delay: 60` and `Visit-time: 0100-0645` GMT** |

Neither host refuses us, so this is not `empleate.md`'s Tecnoempleo case. But
`administracion.gob.es` asks for one request a minute inside a 5¾-hour
overnight window, and **no unattended sweep here could honour that**.

So the same rule applies for a different reason: **the ad URL emitted is always
`empleate.gob.es`**, the source link is carried as `source_url` with its
constraint spelled out in `source_url_fetch_constraints`, and it is there for
the user to click, not for a script to follow. See *When a refused board's ads
reach us through an open one* in `shared/robots-policy.md` — this is the
neighbouring case, where the door is open but only on stated terms.

## Freshness

Unlike the private board, the live set here is genuinely current: 690 of 1 558
were posted in the last 30 days, 1 153 in the last 90, and only 198 are over a
year old. **The staleness on this board is in the deadline, not the posting
date** — which is exactly why trap 1 matters and `--desde` matters less.

## Verification

```bash
S=skills/job-scan/scripts/oposiciones.py
python3 $S provincias                      # Barcelona 965 … Madrid 42
python3 $S grupos                          # GP1 563, A1 200 …
python3 $S search --provincia BARCELONA --grupo A1 --limit 3
python3 $S search --provincia MADRID --incluir-cerradas --limit 200
    # → warns before querying, then flags 42 of 42 as geographically incoherent
```

The guards are worth exercising after any change; both failures are silent at
the network layer:

```python
solr("checkVisible:1")                            # → dies, the sibling's habit
check_live_filter({"fq": "provinciaF:MADRID"}, "")  # → dies, no live filter
```
