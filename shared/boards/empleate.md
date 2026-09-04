# Board adapter — empleate.gob.es (SEPE, Spain)

<!-- hosts: empleate.gob.es -->

**28 099 live ads.** The first Spanish board in this repository, and the third
national public employment service after `job-room.md` (Switzerland) and
`france-travail.md` (France).

**One request returns 100 complete ads, full text included.** There is no
per-ad fetch and no detail endpoint to call: the search response *is* the ad.
That makes this the cheapest board here per ad — a 2 000-ad sweep is 20
requests.

**Everything here was verified against the live index on 2026-09-01.**

**The most useful thing this board taught is not the board.** See trap 1.


## Status on 2026-09-04 — **the board is dark, and the remaining cause is a decision**

**Do not read a zero from this adapter as a market.** It returns nothing today,
and it stops before it reaches the index.

`https://empleate.gob.es/robots.txt` answers **HTTP 200, `Content-Type:
text/html`, 8 456 bytes** — the SEPE error page, `<title>SEPE</title>`, *"Si el
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

**What has been repaired, and what has not.** This adapter's TLS was fixed in
v1.184.0 — the host sends its leaf without the issuing intermediate, and
`_tls.context_for` supplies the one its own AIA names. **Its sibling
`oposiciones.py` read the same host and never got that**, which went unnoticed
for a day because the robots refusal stops both adapters before the TLS path is
ever reached: the broken call site could not fail loudly. Repaired in v1.202.0,
and a test now binds every reader of a `_tls.HOSTS` host to the module rather
than leaving the wiring per-adapter.

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
GET /robots.txt                                → Allow: /, six private paths closed
GET /empleate/open/offersearch/selectBuscador  → Solr, open, no key
     ?q=*&wt=json&rows=100&fq=checkVisible:1
https://empleate.gob.es/empleo/#/oferta/<id>   → the ad, for a human
```

`robots.txt` is nine lines. `User-agent: *` / `Allow: /`, then six
`Disallow:` paths that are all logged-in areas — `/empleo/perfil/`,
`/empleo/empresas/`, the saved-and-applied lists. **No crawler is named, no AI
agent is named, and the API path is not mentioned.** Question 1 of
`shared/robots-policy.md` does not arise; there is nothing to weigh.

The site is an AngularJS 1.x front end over Solr, and `open/offersearch/` is
what its own search box calls. `open/master/*` publishes the code tables —
`modalities`, `contracttypes`, `provinces` — so nothing here is guessed from a
value seen in the data.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/empleate.py" \
  search --provincia MADRID --desde 2026-09-01
```

**No browser, no account, no key.**

## Configuration

```yaml
boards:
  empleate:
    enabled: true
    searches:
      - { provincia: "MADRID" }
      - { provincia: "BARCELONA", categoria: "INFORMÁTICA/TELECOMUNICACIONES" }
    desde: "2026-09-01"
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `provincia` | recommended | Uppercase, as the board writes it. **List them with `empleate.py provincias`** — never type one from memory |
| `comunidad` | no | The 19 autonomous communities. `empleate.py comunidades` |
| `categoria` | no | 23 categories. `empleate.py categorias` |
| `texto` | no | A phrase matched in the title |
| `desde` | **effectively yes** | See *Age*. Without it, three ads in ten are over a year old |
| `fuente` / `sin_fuente` | no | Keep or drop one of the thirteen feeds. `empleate.py fuentes` |

Geography is free — it is a filter on the index, not a fetch per ad — so
unlike `crit.md` or `adecco.md` there is no cost to narrowing.

## Traps

**1. Omit `fq` and the endpoint returns 131 510 ads, four fifths of them
dead.**

```
?q=*&rows=0&wt=json                    → numFound 131510
?q=*&rows=0&wt=json&fq=checkVisible:1  → numFound  28099
```

The server injects the live filter `(speStateId:1 OR speStateId:4)` **only when
the request already carries an `fq` of its own** — you can watch it happen in
`responseHeader.params.fq`, which comes back rewritten. Send no `fq` and it
applies none, and hands over the entire index: **103 411 expired and withdrawn
ads**, HTTP 200, well-formed JSON, indistinguishable in shape from the real
board.

`checkVisible:1` narrows nothing on its own — 28 099 with it and without it.
**Its only job is to exist**, so that the injection fires. That is the whole
trick, and it is worth stating plainly because the instinct on an open Solr
endpoint is the opposite one: to send no filter and get everything.

*The adapter therefore checks the echoed `fq` on every single response and
treats its absence as fatal.* Nothing downstream could tell 131 510 from
28 099 — both look like a board.

**2. `FAIL!` is an HTTP 200 with `Content-type: application/json`.**

```
fq=comunidadF:CASTILLA LEON              → 200, application/json, body: FAIL!
fq=comunidadF:"CASTILLA LEON"            → 200, 2 130 ads
fq=checkVisible:1 AND speStateId:1       → 200, application/json, body: FAIL!
```

Five bytes, not JSON, on a success status with a JSON content type. It is how
the endpoint rejects an `fq` its validator dislikes: **an unquoted value
containing a space**, or **any clause naming `speStateId` alongside another**
(the server passes those through unvalidated instead of rewriting them, then
its own parser refuses the result).

A client that wraps `json.loads` in a `try` and treats the failure as "no
results" reports an empty board on a working endpoint. Quote every value,
never send `speStateId`, and make a non-JSON body an error rather than a zero.

**3. `rows` is capped at 100, silently.**

```
?rows=1000  →  responseHeader.params.rows = "100",  100 docs
```

No error, no warning; the echoed parameter is the only sign. A client that
asks for 1 000, receives 100 and pages `start += 1000` reads **one tenth of
the board** and reports a complete sweep. Page by the number of documents
actually returned.

**4. `url:"#"` matches all 28 099 ads.**

The 9 819 SNE records store the literal string `"#"` in `url`. In a Solr text
field `#` tokenises to nothing, so the clause has no terms and matches every
document. `url:http*` gives the honest count: **19 945 of 28 099 carry a real
off-site URL**.

This is the inverse of the usual sitemap failure — `hays-fr.md`'s CDATA `<loc>`
returns zero from a full file. Here a filter that reads as precise quietly
returns the whole index. Both are the same lesson: check a filter's count
against something you already know.

## Age — "live" means "not withdrawn"

| Posted | Live ads |
| :-- | --: |
| Last 7 days | 3 382 |
| Last 30 days | 8 951 |
| Last 90 days | 15 734 |
| **Over 1 year ago** | **8 106** |
| **Over 3 years ago** | **4 326** |

The oldest ad still flagged live is from **July 2020**. Nothing in the record
marks these as stale — no `validThrough`, no expiry — and `speState` says
`Activa` on all of them.

**So `--desde` is a correctness control on this board, not an optimisation.**
The adapter reports, on every run, how many of the ads it returned are over a
year old, and says so in the run's own output.

## What the record carries

Measured on 28 099 live ads, and by feed on 100 ads from each of the nine
largest.

| Field | Coverage | Note |
| :-- | --: | :-- |
| `titulo`, `contenido` | 28 099 | Description is HTML; median 598 characters, but see below |
| `provinciaF` | 26 110 | 1 989 have none — mostly remote and syndicated |
| `ciudadF` | 25 459 | |
| `cp` (postcode) | 9 432 | `ciudad` is a municipal code, not a postcode |
| `localizacion` | ~85% | `lat,lon` as a string |
| `salarioMin` / `salarioMax` | **5 303** | Always a pair when present. **19%** — better than most French boards here |
| `creador` (employer) | **8 010** | **29%.** See below |
| `fechaCreacionPortal` | 28 099 | A real per-ad date |
| `modality` | 2 309 useful | 25 790 are "No informado" |

**The employer is missing on 71% of the board.** `creador` is filled on the
COGITI, TECNO_EMPLEO and WEB feeds and empty on SNE, INSERTIA,
CASTILLA_Y_LEON, GESTIONANDOTE, HACESFALTA and PORTALENTO. On SNE ads — 9 819,
the largest feed — there is no employer field at all: the application route is
an office reference or an email written inside the description text. Say that
to the user rather than reporting a blank company.

**Description length is a property of the feed, not of the board.** Medians
across 100 ads each: TECNO_EMPLEO 2 233, HACESFALTA 1 723, INSERTIA 1 648,
COGITI 801, SNE 604, GESTIONANDOTE 396, CASTILLA_Y_LEON 383, WEB 367,
**PORTALENTO 76**. A run that returns mostly PORTALENTO returns titles.

**`modality` does not tell you whether a job is remote.** 25 790 of 28 099 are
"No informado" and the whole index holds **110** ads flagged teletrabajo, a
distancia or mixto. Remote work has to be read out of the text.

### The salary comma is ambiguous, and both readings occur

```
salarioMin  16200,00   →  €16 200,00     comma is the decimal separator
salarioMin  19,500     →  €19 500        comma is the thousands separator
```

Both notations, same field, same index. Applying the Spanish rule everywhere
turns `19,500` into **€19.50 a year**; applying the English rule everywhere
turns `16200,00` into **€1 620 000**. Wrong by a factor of a thousand in
either direction, and a salary is exactly the field a user acts on.

The separator is disambiguated by what follows it — **two digits is a decimal,
three is a thousands mark** — and anything matching neither is returned
unparsed rather than guessed. The adapter emits `salary_read_as` saying which
rule it applied, alongside the raw string.

*(Also seen at the source: `14725,34` with a maximum of `148000`. A data error
on the board, not a parsing question — it is emitted as read.)*

## Thirteen feeds, and one of them is a board this plugin will not read

`entitytype` is the feed. Empléate is an aggregator with a direct-application
channel bolted on, not a single board:

| Feed | Live ads | Off-site `url` |
| :-- | --: | :-- |
| SNE (regional employment services) | 9 819 | none (`#`) |
| INSERTIA | 7 235 | insertia.net |
| COGITI (engineering colleges) | 3 285 | proempleoingenieros.es, enginyersbcn.cat |
| **TECNO_EMPLEO** | **2 436** | **tecnoempleo.com** |
| WEB (Empléate's own, direct application) | 2 319 | none |
| CASTILLA_Y_LEON | 880 | empleo.jcyl.es |
| GESTIONANDOTE | 826 | gestionandote.com |
| HACESFALTA (third sector) | 584 | hacesfalta.org |
| PORTALENTO (disability employment) | 526 | portalento.es |
| NAVARRA, GALICIA, GASTROEMPLEO, MERCADIS | 189 | their own |

**Tecnoempleo is the board `shared/robots-policy.md` closed the door on** — its
`robots.txt` names six Anthropic agents with `Disallow: /`, and the verdict
recorded there is *"Obey. No adapter, and there will not be one."* Its ads are
2 436 of the 28 099 here, complete with the longest descriptions on the board.

**Reading them here is not reading tecnoempleo.com.** This is a Spanish public
register, fed by the party that owns the ads, served from a host that invites
us in. `robots.txt` governs access to a server, not the onward publication of
content by a third party the operator chose to supply.

**But the record's `url` field points straight back at that host** — and if the
adapter emitted it as *the* ad URL, `cover-letter <URL>` would then go and
fetch a host that has refused us, on the user's own address. That is the trap,
and it is a live one:

- the ad URL emitted is **always** `https://empleate.gob.es/empleo/#/oferta/<id>`;
- the partner link is carried separately as `source_url`, with
  `source_url_do_not_fetch: true` on the refused hosts;
- the full text is in the record, so nothing is lost by not following it.

`empleate.py fuentes` prints the flag per feed, so the next host to appear in
that list is visible rather than assumed.

## The other index — now `oposiciones.md`

`open/publicoffersearch/selectBuscador` is a second, separate index of Spanish
public-sector announcements — *oposiciones*, *bolsas de trabajo*,
convocatorias. It ships as its own adapter, `oposiciones.md`, because it is a
different board rather than a flag on this one: no ad text, a statutory
deadline instead of a posting date, and a geography that is Catalan in
practice.

**Correction to what this file first said.** It described that index as
"76 050 public-sector announcements". 76 050 is the record count; **1 558 are
live** — confirmed independently by the site's own
`open/publicoffersearch/countActive`, which returns exactly that. The other
74 492 are marked `Inactiva`. The raw figure was quoted here as though it were
a board, and it is not; `oposiciones.md` has the measured version.

Two things there are worth reading even if Spain's public sector is not the
user's market. The endpoint **injects no live filter at all**, so the base
clause this file relies on returns *zero* rather than everything. And its
`estadoPlazoF` field reads "Abierto" on all 76 050 records, including 498 live
announcements whose deadline has already passed.

Not covered, and for a different reason: **InfoJobs**, Spain's largest
private board. `shared/robots-policy.md` records the verdict — it names
`ClaudeBot`, `Claude-SearchBot` and `Claude-User`, publishes a documented API
at `developer.infojobs.net`, and the API is the only route.

## Verification

```bash
S=skills/job-scan/scripts/empleate.py
python3 $S provincias | head -5          # BARCELONA 5108, MADRID 4107 …
python3 $S fuentes                       # thirteen feeds, host_refuses_us flags
python3 $S search --provincia MADRID --desde 2026-09-01 --limit 3
```

The three guards are worth exercising after any change, because all three
failures are silent at the network layer:

```python
solr("speStateId:1 AND checkVisible:1")         # → dies, does not send it
check_live_filter({"fq": "checkVisible:1"}, "")  # → dies, filter not injected
solr("comunidadF:CASTILLA LEON")                # → dies on the FAIL! body
```

## Stopped 2026-09-03: this host no longer serves a rules file

`empleate.gob.es/robots.txt` and `www.empleate.gob.es/robots.txt` both return
**8 456 bytes of an SEPE error page** — `Content-Type: text/html`, `<title>SEPE
</title>`, and **zero `User-agent`, `Disallow` or `Allow` lines anywhere in
it**.

**This figure read 8 450 until 2026-09-04, and 8 450 was never a byte count.**
It came from the guard's own message, which measured `len()` of a *decoded
string* and called the result `bytes`; this page carries six multi-byte
sequences, so it under-reported by exactly six. Corrected in v1.203.0 (#130).
**The number is the same page, not a page that changed size** — and the two
readings were briefly published as evidence that it did.

This card previously recorded *"`Allow: /`, six private paths closed"*, so the
file was real when it was written. **The site drifted; the reading did not.**

**The adapter now stops with exit 8** — the rules could not be read, and #128
established that **a body nobody could recognise is not an absence of rules**.
Before that fix this host was `unreadable` and *permitted*, which is how a
board came to be swept on the strength of somebody's home page.

**Fixing #128 cost this board, and that is the trade the fix was for.** The
alternative was a guard that reads an error page as an empty `*` group and
marks it certain. The route back is not code:

- the file may return — one request tells you, and the adapter says so on
  every run rather than failing quietly;
- or the operator can be told, since a `robots.txt` that answers with the
  home page is very plausibly a misconfiguration.

**What must not happen is a special case for this host.** The measurement is
the same one that protects every other board.
