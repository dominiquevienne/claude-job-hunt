# Board adapter — Computrabajo (18 Latin American countries)

<!-- hosts: co.computrabajo.com, cl.computrabajo.com, pe.computrabajo.com, mx.computrabajo.com, ar.computrabajo.com, ec.computrabajo.com, ve.computrabajo.com, cr.computrabajo.com, pa.computrabajo.com, gt.computrabajo.com, bo.computrabajo.com, do.computrabajo.com, uy.computrabajo.com, sv.computrabajo.com, hn.computrabajo.com, ni.computrabajo.com, py.computrabajo.com, pr.computrabajo.com -->
<!-- script: computrabajo.py -->
<!-- verified: 2026-09-02 -->
<!-- countries: CO CL PE MX AR EC VE PA CR GT HN NI SV DO BO PY UY US -->

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

## Seven countries, four measurements, and the corpora are distinct

**The `robots.txt` is identical on all eighteen sites, so it cannot say
anything about the network's shape.** On this board there is nothing to read:
the intersection test is the only instrument. Measured 2026-09-03 across
`ec co pe mx cr pa do`:

| | |
| :-- | :-- |
| Cross-country **id** overlap | **0**, over 21 pairs and 140 ads |
| Cross-country **title + employer** overlap | **0**, over 6 pairs, once blank employers are excluded |

**Seven markets, seven corpora.** That is the **fourth** resolution of *one
platform, many countries* in this repository, and it agrees with none of the
other three: Bumeran gave distinct corpora under a shared filename marker,
Encuentra24 gave **one** corpus under two language prefixes, and hr.ge gave two
identical brands out of six. **A pattern that resolves four ways is not
predictive** — measure it every time.

### Half of every id is the same sixteen characters

```
C49824F7E83E82A4 61373E686DCF3405
1E48827D9AC02D50 61373E686DCF3405
```

**`61373E686DCF3405` is on every id, on all seven countries and on three
different keywords.** So the "32-hex id" is a 16-hex id followed by a
platform-wide constant. It is harmless — the ids stay unique, and the ledger
key needs no country — but **a reader who takes the tail for a site or tenant
marker is reading noise**, and two ads from one country are enough to suggest
that and not enough to refute it.

### And the comparison that found four matches was matching blanks

The first pass of the test above joined on `(title, employer)` and reported
**four cross-country matches**. Every one of them was a pair of ads with **no
employer name**, matching each other on the empty string.

**An empty field equals an empty field.** The employer is absent on **3 of 20
Mexican cards and 14 of 20 Peruvian ones** — 15% against 70% — so a join on
that column produces matches in proportion to how anonymous a market is, and
none of them are real. **Exclude the blanks before comparing, and report how
many you excluded.**

## Pagination ends honestly

`?q=programador&p=<n>` was distinct at pages 2, 5 and 40, and **page 200
answered 200 with a shorter page and no cards at all**. No repeat of the last
page, no error, no fabricated results — the empty page is the end, and it can
be trusted.

Worth saying plainly because two boards shipped this month do the opposite:
JOBBKK repeats its last page for ever, and Kalibrr substitutes an unrelated
set. Computrabajo simply stops.

## In Colombia the public API is not a rival source — it is the salary

Colombia's public employment service publishes an open API: **262 275 offers**
(`total_registros`), JSON, no key, the whole corpus reachable, **a salary
figure on 83%**. Its `DETALLES_PRESTADOR` field names the accredited operator
that carries each offer, and Computrabajo is the operator seen most often.

**An earlier version of this section read that as a reason to choose one
source.** That framing was wrong, and the correction is worth stating because
the numbers say the opposite:

| | Salary figure |
| :-- | --: |
| Computrabajo card | **0 of 80** |
| The public API record | **83%** |

**These are not two sources of the same content. They are the same advert,
seen once without a salary and once with one** — which is an argument *for*
reading both, as **enrichment**, not as a second board.

**The share itself is not established, and the first version of this file
claimed one.** Computrabajo's portion cannot be read off consecutive pages,
because **the corpus is grouped by operator**: measured 2026-09-02, the first
eight pages are 83.5% Computrabajo and **page 900 is 0%** — all Magneto and the
compensation funds. A proportion taken from the start of the index is a
proportion of the start of the index. **What is measured is the join below,
not the share.**

### The join exists, and it costs no request

**Measured 2026-09-02 on 600 records of the public API.** The origin URL is
`DETALLES_PRESTADOR[].URL_DETALLE_VACANTE` — a **list**, not a string, one
entry per accredited operator carrying the offer.

```
DETALLES_PRESTADOR present ....................... 600 of 600
entries with no URL_DETALLE_VACANTE .............. 0
Computrabajo entries ............................. 484
  → decoded to co.computrabajo.com ............... 484
  → ending in a 32-hex identifier ................ 484   (100%)
```

Every Computrabajo URL is a redirector, and **the identifier is already in the
stored string**:

```
https://go.computrabajo.com/go/gom?url=https%3a%2f%2fco.computrabajo.com
  %2fofertas-de-trabajo%2foferta-de-trabajo-de-…-en-madrid-4784707D3318336C61373E686DCF3405
```

Percent-decode the `url=` parameter, take the trailing 32 hex characters, and
that is the adapter's own id — `computrabajo.py search --country co` returns
`89CDDE57D569F7B061373E686DCF3405`, the same shape and the same suffix. **So
`computrabajo:<id>` is reconstructible from the public record by string
parsing, with no HTTP request at all.**

**Look at the shape of the id before you trust its length.** Across 334
identifiers there were **334 distinct first halves and exactly one distinct
second half** (`61373E686DCF3405`). The last sixteen characters are a constant,
not entropy. Compare all 32 — but do not claim that all 32 discriminate.

*(This was measured by reading the stored string before following any link,
which is why it cost nothing: had the URL been followed first, a 200 on the
board's landing page would have looked like a successful resolution. That is
the mistake `curl -L` produced on Jobvite.)*

### Two things that will bite whoever writes the API adapter

**1. The server sends only its leaf certificate.** `openssl s_client` reports
`Verify return code: 21 (unable to verify the first certificate)`, and the
consequence is that **`curl` succeeds where Python's `urllib` fails** — macOS
fetches the missing intermediate, OpenSSL does not. **The obvious repair is to
disable verification, and it is the wrong one**: supply the intermediate
instead. This is the TLS case in `shared/robots-policy.md`, and it looks like a
dead host from one client and a healthy one from another.

**2. `totalPages` overstates the corpus by about 390 pages.** The endpoint
answers `total: 276004` and `totalPages: 5637`, while `total_registros` says
**262 275** — and 262 275 ÷ 50 is 5 245. Page 5 245 returns 50 rows; **pages
5 300, 5 520 and 5 637 return zero, with HTTP 200 and no error.** A sweep that
trusts `totalPages` reads several hundred empty pages and reports a complete
corpus. `total_registros` is the number that matches the data.

### What that changes, and what it does not

**Enabling both sources in Colombia is now a join rather than a duplicate
risk** — the public record's salary can be attached to the Computrabajo row it
belongs to, which is the enrichment the overlap always argued for. **The
adapter does not do it yet**: nothing here has been built, and until it is, the
practical advice stands unchanged — **enable one**. The difference is that the
work is now specified rather than unknown.

Nothing here decides anything for the other seventeen countries, where no such
measurement exists.

*(Reframed 2026-09-02 after the first version had been published, then
completed the same day when the join was measured. The measurement never
changed; what it was taken to mean did — twice.)*

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
