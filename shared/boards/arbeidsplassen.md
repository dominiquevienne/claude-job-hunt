# Board adapter — NAV Arbeidsplassen (`arbeidsplassen.nav.no`, Norway): the public employment service, a sitemap and an unkeyed API that agree to five, a window at 10 000, and a contact section that never leaves

<!-- verified: 2026-09-13 -->

<!-- hosts: arbeidsplassen.nav.no -->
<!-- script: arbeidsplassen.py -->
<!-- host-forms: arbeidsplassen.nav.no -->
<!-- host-forms-basis: read — `arbeidsplassen.py:HOST`, a single literal; the site writes no `www.` and every `<loc>` and API address carries the bare host · 2026-09-13 -->
<!-- countries: NO -->
<!-- content: measured · **13 615 distinct advertisement uuids in the declared sitemap (`/stillinger/sitemap.xml`, every one with a `<lastmod>`) and «hits.total 13 620» stated by the search API the same minute — 5 apart, a live board between two reads**; `arbeidsplassen.py sitemap` 17:35 UTC; `search --q python --pages 1`: 58 emitted, site states 58 — equal; the API's `positioncount.sum` 27 406 is a headcount, printed and never compared; `from` is capped at 10 000 («Pagination depth exceeds maximum allowed window»); rules `*` open, everything, no Crawl-delay; a 429 after ~200 reads measured on 2026-08-31 by the country page · 2026-09-13 -->
<!-- witness: the API's own `hits.total.value`, read on every walk and printed beside the emitted count («58 emitted over 1 page(s), site states 58 (q=python) — equal»), and beside the sitemap's distinct count («13 615 in the sitemap, the API states 13 620 — 5 more in the API»); the headcount named as such · 2026-09-13 -->

**Norway's public employment service — the country's largest inventory,
half of it FINN.no's through the door the State opens — and the first
Norwegian adapter that is a script (`karrierestart.md` is a browser
route).** Issue #365. Measured 2026-09-13 17:32–17:36 UTC by the declared
client, the guard on the exact path first (`*`, `Disallow:` empty:
everything open, `certain: True`).

## Rules and the two routes the site writes

```
robots.txt                          200, 76 B — `User-agent: *` / `Disallow:` (empty) / `Sitemap: https://arbeidsplassen.nav.no/sitemap.xml`; no Crawl-delay
GET /sitemap.xml                    200 — an index of two: /sitemaps/innhold/sitemap.xml (content) and /stillinger/sitemap.xml (advertisements)
GET /stillinger/sitemap.xml         200 — 13 616 <loc>: /stillinger and 13 615 /stillinger/stilling/<uuid>, each with <lastmod> (2026-04-08 … 2026-09-13), changefreq weekly
GET /stillinger/api/search?size=25&from=0        200, 80 066 B — Elasticsearch: hits.total.value 13 620 (relation eq), 25 hits, aggregations (counties, occupations, positioncount.sum 27 406 …)
GET …?size=100&from=0                            200 — 100 hits (size up to 100)
GET …?q=python&size=25&from=0                    200 — total 58   ·   …?county=VESTLAND   total 1 656
GET …?size=25&from=10000                         200, 59 B — {"error":"Pagination depth exceeds maximum allowed window"}
GET /stillinger/stilling/<uuid>                  200, 134 064 B — Next.js, no JSON-LD; <dt>/<dd> list and <h2> sections; the ad JSON (with contactList) embedded in the RSC payload
GET /stillinger/api/stilling/<uuid>              200, 67 830 B — an HTML shell titled «Arbeidsplassen.no», not the ad
```

**The API is unkeyed and the page calls it** — the search page's own
requests, under the rules' `*` open; the doctrine of 2026-09-04 (#100)
applies and the identity is still sent. **`from` stops at 10 000**: a
filterless walk reaches 10 000 of 13 620 and the adapter says where the
window ends and to narrow with `--county`/`--municipal`/`--q`. **A 429
stops the run without a retry** (exit 7) — the country page measured one
after ~200 reads on 2026-08-31; 1 s spacing is the adapter's own.

## Two figures, five apart — and a third that is not a count

```
arbeidsplassen.py sitemap --limit 2
[arbeidsplassen] **13 615 distinct advertisement uuid(s)** in the sitemap, 0 without <lastmod>; 2 emitted (--limit 2).
[arbeidsplassen] 13 615 in the sitemap, the API states 13 620 — 5 more in the API; a live board between two reads, and the sitemap is rebuilt on its own clock.

arbeidsplassen.py search --q python --pages 1
[arbeidsplassen] 58 emitted over 1 page(s), site states 58 (q=python) — equal.
[arbeidsplassen] the API also states 92 POSITIONS (positioncount.sum) — a headcount, not advertisements; printed, never compared.
```

The sitemap's `<lastmod>` is the advertisement's own date (`--since`
filters on it); the API's `published` is the listing date. **`positioncount
.sum` (27 406 for the whole board) counts POSITIONS** — one advertisement
for three drivers is three — the `karrierestart.md` distinction; it is
printed with its name and never set against the count.

## The hit, and where the rest is

The search hit: title, employer (`businessName`, `employer.name` —
upper-case on one, cased on the other), the first location's county,
municipal, city and country (**the street address in `locationList` is a
premises' address and is not emitted**), published, expires,
`properties.applicationdue` («Snarest» or a date), remote, workLanguage,
education, experience, occupations (STYRK level 1 / 2), categories,
**`source` — FINN, IMPORTAPI, Stillingsregistrering, EURES: the door the
advertisement came through, emitted as `listed_via`, not the employer**.
No engagement type, extent, position count or description in the hit.

The advertisement page (`ad`): `<dt>/<dd>` — Oppstart, Stillingstittel,
Type ansettelse («Fast, heltid 100%»), Arbeidstid, Sektor, Stillingsnummer,
Sist endret, Hentet fra, Referanse — and the `<h2>` sections Om jobben,
Hva vi ser etter, Arbeidsoppgaver, Vi tilbyr, Om bedriften, Annonsedata.
**«Kontaktperson for stillingen» is dropped whole and named in
`contact_dropped`**: the page embeds `contactList` with the contact's
name, e-mail and telephone, and none of it leaves the adapter (checked on
the live page: 0 occurrences of the name, the address, the number in the
output). «Nettsted» (the employer's site) is dropped from `fields` too.
Read in full on one (`4ff26012…`).

## Configuration

```yaml
boards:
  arbeidsplassen:
    enabled: true
    county: ""        # optional — VESTLAND, OSLO … the API's own upper-case names
    q: ""             # optional
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `county`, `municipal`, `q` | no | narrow the API; a filterless walk ends at the 10 000 window |

No credentials, no browser. `sitemap` is two requests (~2 MB of XML +
one API call); `search` is one per 100 at 1 s; `ad` is one.

## What is not established

- **How the 429 falls** — ~200 reads on 2026-08-31 (the country page's
  measure); 12 requests on the 13th were all answered; the adapter stops
  on the first.
- **Whether `municipal`/`county` values must be upper-case** — VESTLAND
  answered; lower-case not tried.
- **The 5 between the file and the API** — a live board; which five is
  not read.
- **The other sitemap** (`/sitemaps/innhold/`) — content pages, not read.

## 2026-09-13 — shipped

`sitemap --limit 2`: 13 615 distinct, the API states 13 620. `search --q
python --pages 1`: 58 / 58 — equal. `ad` on one, contact section dropped.
Four tests; six mutations on a detached worktree (`python3 -B`), six red
— the window guard dropped, the 429 branch dropped, the headcount compared
as a count, the uuid dedup dropped, «Kontaktperson» kept, `--since`
inverted.
