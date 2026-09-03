# Board adapter — BNE (Chile, Bolsa Nacional de Empleo)

<!-- verified: 2026-09-03 -->
<!-- hosts: www.bne.gob.cl, bne.cl -->

Chile's national employment service. **No key, no cookie, no browser** — the
*search* renders client-side and **the advertisement pages do not**: each
carries a `JobPosting` in JSON-LD.

**7 928 advertisements**, from one request.

## The sitemap is nothing but ads, and that is unusual here

```
GET /sitemap.xml   → 7 928 <loc>, all /oferta/<id>
```

**7 928 of 7 928 are advertisements.** No employer pages, no search landings —
so this file needs no filtering.

**That is worth stating because it is the exception.** `hr.ge` publishes 39 247
`<loc>` of which **1 062** are ads; Vieclam24h's index is mostly occupation and
province families. **The habit of filtering is what protects against those**,
and a board where it turns out to be unnecessary is not a reason to drop it.

## The board is not UTF-8, and `errors="replace"` is why nobody would notice

```
Content-Type: text/html;charset=ISO-8859-1
<meta charset="windows-1252">
bytes:  b'Pudahuel \xa1Comisiones'

decoded as utf-8    →  "Pudahuel <?>Comisiones"
decoded as cp1252   →  "Pudahuel ¡Comisiones"
```

**Eight of eight sampled advertisements lost between 37 and 93 characters**
under UTF-8, and none under the declared charset. On a Spanish-language board
that is most of the text that carries meaning.

**And `decode("utf-8", "replace")` is this repository's house pattern — 32 of
its adapters use it, and not one reads the declared charset.** It has not bitten
before because every board measured so far served UTF-8. **`errors="replace"`
cannot fail**: it produces plausible text with holes, which is
`shared/plausible-and-false.md`'s class arriving in the transport layer.

`skills/job-scan/scripts/_decode.py` follows the header, then the markup's own
`<meta>`, then **strict** UTF-8, and only then a total fallback — **and it
returns which one it used**, so a run that had to guess says so.

**The site declares its encoding twice, differently** — `ISO-8859-1` in the
header, `windows-1252` in the markup. They agree on these bytes; they are not
the same declaration, and **neither is UTF-8**, which is the only thing a
reader needed to notice.

## Two domains, one site, and the file points at the other one

`bne.cl` and `bne.gob.cl` serve **the same 67 bytes** — md5 `7d46f6463cb7…`,
`User-agent: * / Allow: /` — and **both declare their sitemap on
`www.bne.gob.cl`**. `bne.cl` itself redirects to `www.bne.cl`.

**So the host you type is not the host that answers**, which is what
`_robots.py` has keyed its cache on since #99: the verdict comes back naming
`www.bne.cl`, one entry for both spellings, and nothing here records a host by
hand.

## The search is not a route

`/ofertas` answers `200` with 122 kB and **zero `/oferta/` links** — the
results arrive client-side. Its own pagination URL
(`numPaginaRecuperar`, `numResultadosPorPagina`, taken from the page itself)
returns the same empty shell.

**So `search` in this adapter is a scan, and it says so before it starts:** it
reads advertisements one by one up to `--read`, and reports **both numbers** —
matches, and how many were read out of 7 928. A zero from it is a statement
about the ads that were read and **not about Chile**.

## What a card yields — measured on 25 read in order

| Field | Filled |
| :-- | --: |
| `title`, `company`, `location_text` | **25/25** |
| `posted` (`datePosted`) | 25/25 |
| `valid_through` (`validThrough`) | 25/25 |
| Past `validThrough` and still listed | **0/25** |
| Replacement characters in any field | **0/25** |

**`validThrough` on every ad is worth more here than the fill rate suggests.**
`shared/ats-open-check.md` makes a stated expiry the one signal that outranks
every inference about whether an ad is open — and this board publishes it on
all of them.

**Zero expired of 25 is measured and is not a property**: 25 of 7 928, read in
sitemap order rather than sampled across it.

## Configuration

```yaml
boards:
  bnecl:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `read` | no | How many ads a `search` may read. **There is no query to send** |

No credentials, no login, no browser.

## Zero-shaped answers

**1. A page decoded as UTF-8 that "works".** 37 to 93 characters gone per ad,
no error, no warning.

**2. Two charset declarations that disagree**, neither of them UTF-8.

**3. `/ofertas` answering 200 with no advertisement in it.**

**4. A `search` that reads 40 of 7 928 and returns nothing.** That is a
statement about 40 ads.

**5. A sitemap that happens to need no filtering** — and the next one will.

## Applying

Through the ad URL, in the user's own browser. **The plugin does not create
accounts and does not fill credential fields.**

## Pace

One request for the whole board. Reading advertisements is one request each at
~50 kB, so a scan is deliberate and bounded by `--read`, default 40.

## Verification

```bash
S=skills/job-scan/scripts/bnecl.py
python3 $S sitemap --limit 5              # 7 928, all advertisements
python3 $S ad --id 2026-082609            # accents intact, encoding reported
python3 $S search --keyword vendedor --read 8 --limit 2
```
