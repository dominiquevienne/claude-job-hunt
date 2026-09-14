# Board adapter — Úřad práce ČR (`up.gov.cz`, Czechia): the public employment service's whole register through the Ministry's open-data file — 39 887 postings, 101 207 positions in one daily file; the portal's own search behind a written `Disallow: */rest/*`, never sent; the contact person every record carries never emitted

<!-- verified: 2026-09-14 -->

<!-- hosts: up.gov.cz, data.mpsv.cz -->
<!-- script: uradprace.py -->
<!-- host-forms: data.mpsv.cz, up.gov.cz -->
<!-- host-forms-basis: read — the open-data page `data.mpsv.cz/web/data/volna-mista-za-celou-cr` names the file and the code lists on `data.mpsv.cz/od/soubory/…`; the portal's `config.json` names `https://up.gov.cz/volna-mista-v-cr` as `cs.volnaMista.urlVolnaMista`, and the adapter builds the record's address on it (the app's own hash route, never fetched) · 2026-09-14 -->
<!-- countries: CZ -->
<!-- content: measured · **`volna-mista.json` carries 39 887 postings (`polozky`) whose `pocetMist` sum to 101 207 positions, `Last-Modified: Sun, 13 Sep 2026 20:07:40 GMT`, 189 957 345 B in one request** — read by the declared client, the guard on each exact path (`data.mpsv.cz` rules open, certain, no Crawl-delay; `up.gov.cz` 191 B: `*` refuses `*/rest/*`, `/fas/*`, `/cas/*`, the notice boards — and the search component POSTs `/security-provider/rest/token` then `/volna-mista/rest/volna-mista/dto/query`, both refused); 36 915 published with the employer, 2 950 EU-wide, 22 anonymous (`anosp`); 31 002 places are an establishment's address, 6 515 a municipality, 1 992 districts, 179 a free address, 72 the whole country; the operator's own press figure «99 274 volných pracovních míst» at the end of August (`up.gov.cz/nezamestnanost-v-cesku-srpen-2026`) is the same grandeur; **every record carries `prvniKontaktSeZamestnavatelem` — name, e-mail, telephone — never emitted; 12 926 descriptions carried an e-mail and 8 956 a telephone, scrubbed; one profession WAS an e-mail address, scrubbed too** · 2026-09-14 01:11 UTC -->
<!-- witness: the file's own `Last-Modified` and its two figures — postings in `polozky`, positions summed from `pocetMist` — printed on every run; a body shorter than `Content-Length` exits 6 (a short file, never a smaller register); the operator's monthly press figure (99 274 positions at the end of August 2026 against 101 207 summed on 13 September) is the outside witness, read by hand, not fetched by the adapter · 2026-09-14 -->

**The Czech public employment service (Úřad práce ČR) keeps the
country's register of vacancies — 39 887 postings for 101 207 positions
on the day, the largest Czech inventory measured, of which easy-prace.cz
republishes 24 546 (`easyprace.md`).** Issue #350. Measured 2026-09-14
01:04–01:14 UTC by the declared client, the guard on the exact path before
each request.

## The portal says no in writing — and the Ministry publishes the register

```
up.gov.cz/robots.txt                        200, 191 B — JoobleBot and SemrushBot: Disallow: /; *: Disallow: */rest/*, /fas/*, /cas/*, /uredni-deska, /uredni-deska-mpsv
GET https://up.gov.cz/                      200, 1 649 626 B — a Nuxt site; the vacancies signpost is /volna-mista-v-cr
GET https://up.gov.cz/volna-mista-v-cr      200, 1 216 076 B — «Volná místa - hledání»: the server renders the chrome and NOT ONE vacancy;
                                            the body is <volna-mista-app options='{"mode": "default"}'> from /app/volna-mista/src/volna-mista-app.js (2 813 950 B)
the app's data calls, read in that script:   POST /security-provider/rest/token  →  POST /volna-mista/rest/volna-mista/dto/query   — both `*/rest/*`: REFUSED IN WRITING
www.uradprace.cz (the former host)          TLS fails on its rules file — an absence since #283 — and it is the same application; not used
```

**A written `Disallow` is honoured by every route, browser included; the
adapter never sends those two requests and has no `ad` command.** What
the same operator publishes for exactly this purpose is the open-data set
**«Volná místa za celou ČR»** on `data.mpsv.cz` (rules open, certain):

```
GET https://data.mpsv.cz/web/data/volna-mista-za-celou-cr        200 — «Opendatová sada 1x denně»; the export is the vacancies the ÚP ČR approved for the JPŘ PSV portal
GET https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json   200, 189 957 345 B, Last-Modified Sun, 13 Sep 2026 20:07:40 GMT — {"polozky": [39 887]}, no compression, Accept-Ranges: bytes
GET https://data.mpsv.cz/od/soubory/ciselniky/kraje.json           200, 2 004 B — 14 regions      (Kraj/19 = Hlavní město Praha …)
GET https://data.mpsv.cz/od/soubory/ciselniky/okresy.json          200, 12 786 B — 78 districts   (Okres/9999 → Kraj/19 …)
GET https://data.mpsv.cz/od/soubory/ciselniky/obce.json            200, 900 386 B — 6 258 municipalities (Obec/554782 = Praha → Okres/9999 …)
GET https://data.mpsv.cz/od/soubory/ciselniky/cz-isco.json         200, 813 597 B — 1 995 CZ-ISCO codes
```

**One file is the whole register** — nothing paged, nothing walked,
nothing to be short of. The adapter reads the five files (five requests,
2 s apart — its own pace, the host writes none), checks the bytes received
against `Content-Length` and **exits 6 on a short body rather than count a
truncated file**, and prints the file's own figures:

```
uradprace.py list --cache ~/.cache/uradprace
[uradprace] 39 887 posting(s) in the file (Last-Modified: Sun, 13 Sep 2026 20:07:40 GMT), 101 207 position(s) summed — one file is the whole register, nothing paged.
[uradprace] 39 887 emitted, 101 207 position(s).
[uradprace] the contact person every record carries (name, e-mail, telephone) is never emitted; descriptions scrubbed; the portal's own search is behind a written Disallow (*/rest/*) and is never sent — there is no `ad` command.
```

`--cache DIR` keeps the five files and reuses them for 24 hours — the
portal's own `config.json` says `vm.cache.hours = 24` and the set is
daily; the note then says «the cached copy». Filters are applied to the
file after the read and **resolved against the published lists**:
`--kraj 19` or `--kraj kralovehradecky` (a code or a name, accents
optional; 8 ICT postings in Královéhradecký kraj with `--isco 25` on the
day), `--okres kolin` (30 changed since 10 September), `--obec brno
--profese kuchar` (95), `--changed-since 2026-09-10`, `--limit N`. **A name
that matches nothing — or several entries — is an error (exit 2), never
an empty market.**

## The record

```
{"portalId": 67292464, "referencniCislo": "35039080790", "pozadovanaProfese": {"cs": "Doplňovači zboží"}, "profeseCzIsco": {"id": "CzIsco/93340"},
 "zamestnavatel": {"ico": "28408624", "nazev": "Thi Le Nguyen"}, "pocetMist": 2, "mesicniMzdaOd": 22500, "mesicniMzdaDo": 25000, "typMzdy": {"id": "TypMzdy/mesic"}, "pocetHodinTydne": 40,
 "mistoVykonuPrace": {"typMistaVykonuPrace": {"id": "TypMistaVykonuPrace/adrprov"}, "pracoviste": [{"nazev": "Cuřínova sídlo", "email": null, "telefon": null, "adresa": {"psc": "14200", "kraj": {"id": "Kraj/19"}, "okres": {"id": "Okres/9999"}, "obec": {"id": "Obec/554782"}, "ulice": {"nazev": "Cuřínova"}, "cisloDomovni": 590, "cisloOrientacni": "14"}}]},
 "zverejnovat": {"id": "ZverejnovatVpm/ano"}, "smennost": {"id": "Smennost/pruznaPd"}, "upresnujiciInformace": {"cs": "…"}, "datumVlozeni": "2026-09-08T00:00:00.000Z", "datumZmeny": "2026-09-13T23:12:44.473Z",
 "prvniKontaktSeZamestnavatelem": {"komuSeHlasit": {"jmeno": "…", "prijmeni": "…", "email": "…", "telefon": null}, "kdeSeHlasit": {…}}}
```

One record per posting: `id` (`portalId`; the address
`https://up.gov.cz/volna-mista-v-cr#/volna-mista-detail/<portalId>` is
the app's own hash route, emitted and never fetched), `reference`, title
(`pozadovanaProfese`), `isco_code` and its name, **employer name and IČO
— null with `employer_withheld` on the 22 records published «bez uvedení
informací o zaměstnavateli» (`anosp`), whose place is withheld with them,
as the set's own page says**, `positions`, the place as the set types it
— an establishment (`workplace_name`, `street`, `postal_code`), a
municipality, districts, a free `address_text`, «celá ČR» — with
`municipality`, `districts` and `region` resolved through the lists
(municipality → district → region when the address names only the
municipality; 1 090 establishments name neither and keep their postal
code), salary bounds with `salary_unit` month/hour from `typMzdy` (a
period, so `salary_unit_stated` is true; 2 425 hourly), hours a week,
shift, contract types, minimum education, suitability, benefits,
languages, skills, start/end, posted/changed/expires, the card and agency
flags, `up_office`, and `description` (`upresnujiciInformace`) scrubbed
of e-mail addresses and Czech telephone numbers. **The contact person
(`prvniKontaktSeZamestnavatelem`: name, e-mail, telephone, where to
report) and the establishment's `email`/`telefon` are never emitted;
`contacts_withheld` on every record.** The small lists (shift, education,
contract, benefit, skill) are emitted as the set's own codes (`jednoSm`,
`zaklPraktSkol`, `plny`, `premie` …), not resolved.

## Configuration

```yaml
boards:
  uradprace:
    enabled: true
    cache: ~/.cache/uradprace     # optional — keeps the 190 MB file 24 h; the set is daily
    kraj: 19                      # optional — a region code or name
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `cache` | no | a directory; five files, reused under 24 h |
| `kraj` / `okres` / `obec` / `isco` / `profese` | no | filters, applied after the read |

No credentials, no browser, no login. A run is five requests and 190 MB;
with `--cache` the second run of the day is none.

## What is not established

- **Whether the portal's search shows what the file carries** — the
  search is refused in writing and was not sent; the file's page says the
  export IS what the portal publishes (approved, count > 0, within the
  publication window). Not compared.
- **The English/Russian/Ukrainian fronts** (`/en/vacancies-search-3` …)
  — the same component; not read.
- **The 1 090 establishments without a municipality** — postal code
  only; a postcode list is not among the four lists read.
- **`www.uradprace.cz`** — the former host, TLS-broken on its rules file
  on the day; the same application, not used.

## 2026-09-14 — shipped

`list`: 39 887 of 39 887 postings, 101 207 positions; the whole output
scanned — zero e-mail addresses left (13 400 withheld marks), zero
telephone numbers (9 582), zero `komuSeHlasit`. Three tests; six
mutations on a detached worktree (`python3 -B`), six red — the
description not scrubbed, the anonymous flag not honoured, the district
not derived from the municipality, the hourly unit mapped to month, the
short-body check relaxed, `--changed-since` made exclusive.
