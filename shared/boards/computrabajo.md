# Board adapter — Computrabajo (18 Latin American countries)

**Eighteen national sites, one adapter, and one rule file with no exception.**
`co cl pe mx ar ec ve cr pa gt bo do uy sv hn ni py pr` — every one of them
serves the same 874-byte `robots.txt`, **md5 `cfcbd02061ac…`, identical on all
eighteen**, checked as `text/plain` rather than merely as a status.

That is the most uniform family measured in this repository. SEEK diverges by
a line in Singapore and the Philippines; Indeed diverges by four lines in
Thailand. **Computrabajo diverges nowhere.**

**No key, no cookie, no account, no browser.** Listings and ad pages both
answer plain `curl`. Colombia alone carried **74 399 offers** on the day.

**Everything below was verified against `co.computrabajo.com` on 2026-09-02.**

## The rule file closes the filters and leaves the search open

Every `Disallow` on the listing path names a **query parameter**:

```
/ofertas-de-trabajo/*dis=   *cont=   *pubdate=   *sal=   *by=
/ofertas-de-trabajo/*emp=   *emq=    *ememq=     … and the whole em* family
/hojas-de-vida/*   /curriculums/*   /Ajax/*   /_services/*   /go/*
```

**`q=` is not among them, and neither is `p=`.** So the keyword search and its
pagination are open, and what is closed is the site's own **salary, posting
date, contract type, disability and sort filters**.

That is an unusually precise instruction, and it shapes the adapter: it
searches by keyword, pages, and **filters after the fetch** in
`shared/scoring-rubric.md`. `computrabajo.py` refuses to build any of the
named parameters and quotes the rule when it does.

No AI agent is named anywhere in the file, for or against.

*(`co.computrabajo.com/sitemap.xml` answers **403 in `text/html`, 118 bytes** —
there is no sitemap to work from, and the file declares none.)*

## There is no structured data, so this is DOM extraction

The only `application/ld+json` on a listing page or an ad page is an
`Organization` graph describing Computrabajo itself. **No `JobPosting`,
anywhere.** That is the opposite of `jobs-ch.md`, where the structured block is
what made the browser unnecessary — here the markup is all there is.

The two handles the adapter uses are the most stable the page offers:

| Where | Anchor |
| :-- | :-- |
| Listing card | `<article class="box_offer" data-id="<32-hex>">`, 20 a page |
| Ad body | the container marked `div-link="oferta"` |

They are still markup. Re-verify before trusting an old note, and expect this
file to age faster than an API-backed one.

## What a card carries — measured on 80 cards

| Field | Filled |
| :-- | --: |
| Title, ad URL, 32-hex id | 80/80 |
| Location text | 80/80 |
| Relative date (*Hace 7 horas*, *Ayer*) | 80/80 |
| **Employer name** | **69/80 (86%)** |
| Remote tag | 28/80 (35%) |
| **Salary** | **0/80 — there is none on the card** |

**No date is absolute.** The card says *Hace 7 horas*; there is no timestamp
anywhere on it. The adapter carries `posted_relative` as the localised string
rather than inventing a date from it, because the arithmetic would be a guess
in eighteen locales.

**And no salary is anywhere in the listing.** The site's salary filter is one
of the parameters `robots.txt` closes, so pay is read from the ad text or not
at all. A board with 74 399 Colombian offers and no salary on any card is a
discovery board for this plugin, and the file says so rather than letting a
scorer wait for a field that never comes.

## The employer name and the company page do not always agree

The card's employer link points at a company page whose slug is a different
string from the displayed name on **4 of 80**:

| Displayed | Company page slug |
| :-- | :-- |
| ANDISEG LTDA | compania-andina-de-seguridad-privada-ltda |
| S4L COLOMBIA S.A.S | scala-colombia-sas |
| CARMEDA S.A.S. | strattegi |

Two of those are the same firm written long and short. The third is not
obviously the same firm at all. **So the slug is not an employer key**: the
card carries the displayed name and the company page's own hex id, and dedup
uses those. Reading the slug as the employer would merge and split companies
in ways nobody could audit.

## Pagination ends honestly

`?q=programador&p=<n>` was distinct at pages 2, 5 and 40, and **page 200
answered 200 with a shorter page and no cards at all**. No repeat of the last
page, no error, no fabricated results — the empty page is the end, and it can
be trusted.

Worth saying plainly because two boards shipped this month do the opposite:
JOBBKK repeats its last page for ever, and Kalibrr substitutes an unrelated
set. Computrabajo simply stops.

## Before building on this: it overlaps the Colombian public service

Colombia's public employment service publishes an open API — 262 275 offers,
JSON, no key, the whole corpus reachable, **a salary figure on 83%** — and a
measurement offer by offer through its `DETALLES_PRESTADOR` field, which names
the accredited operator, puts **about 84% of it inside Computrabajo's
inventory**.

**Enabling both in Colombia produces a large duplicate set**, and the ledger
has no shared key to catch it: Computrabajo's id is a 32-hex string of its
own, and no field crosses. The public service's record does carry the origin
URL on every offer, which is the one thread that could tie them.

**So in Colombia, choose.** The public API is the better source on its own
terms — a real salary on 83% against none here — and Computrabajo is the
complement for what it does not carry. Nothing in this file decides that for
the other seventeen countries, where no such measurement exists yet.

## Configuration

```yaml
boards:
  computrabajo:
    enabled: true
    countries: ["co", "mx"]      # any of the eighteen
    searches:
      - keyword: "programador"
      - keyword: "contador"
    pages: 3                     # 20 ads a page
    delay: 1.5
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `countries` | yes | `co cl pe mx ar ec ve cr pa gt bo do uy sv hn ni py pr` |
| `searches` | no | `keyword` becomes `q=`. Without one the sweep is the country's whole listing |
| `pages` | no | 20 ads a page; the sweep stops on the first empty page |
| `delay` | no | Seconds between pages, default 1.5 |

**Filters are not configurable, deliberately.** Salary, posting date, contract
type and sort are the parameters `robots.txt` disallows; ask for them in the
scoring rubric instead.

No credentials, no login, no browser.

## Zero-shaped answers

**1. An employer that is not on the card at all** — 11 of 80. Not an empty
string: no element.

**2. A company page slug that names a different company.** Use the displayed
name and the page id.

**3. A relative date and nothing else.** No timestamp exists to fall back on.

**4. No salary on any card**, and no structured block to look in.

**5. The `Organization` JSON-LD looks like structured data and is not** — a
parser that finds `application/ld+json` and assumes a `JobPosting` gets
Computrabajo's own social links.

**6. `sitemap.xml` is a 403 in `text/html`.** There is nothing to enumerate.

## Applying

The apply flow lives behind `candidato.<cc>.computrabajo.com` and requires an
account. **The plugin does not create accounts and does not fill credential
fields.** Hand the user the ad URL and their documents.

## Pace

No published limit, no `429` seen over about 25 requests at 1.5 s apart. The
pages are ~310 KB, so a sweep is heavier in bytes than in requests — 20 ads a
page is the unit, and there is no larger one.

## Verification

```bash
S=skills/job-scan/scripts/computrabajo.py
python3 $S search --country co --keyword programador --limit 3
python3 $S search --country co --keyword programador --pages 3
python3 $S search --country co --keyword x --sal 2000000   # refuses, quoting robots.txt
```
