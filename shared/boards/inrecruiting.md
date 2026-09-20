# Board adapter — Inrecruiting, ex-Intervieweb (Zucchetti's Italian ATS, one tenant at a time): the employer's career page on `<tenant>.intervieweb.it` or `inrecruiting.intervieweb.it/<Company>/` carries the URL of its own list call (with a CSRF pair) and its section id; the list is POSTed there page by page and answers HTML inside JSON — no count stated; the job page carries a JobPosting; `inrecruiting.py`, the street never emitted

<!-- verified: 2026-09-20 -->

<!-- hosts: inrecruiting.intervieweb.it, berner.intervieweb.it -->
<!-- host-forms: inrecruiting.intervieweb.it, {tenant}.intervieweb.it -->
<!-- host-forms-basis: read — `inrecruiting.py:DOMAIN`: the shared host with the company as a path, or the tenant as a subdomain (`tenant_of` takes the career page's own address), one host per run, every other host refused before the gate; the vendor's `www.in-recruiting.com` (refused the declared client on 13.09) is not a board · 2026-09-20 -->
<!-- script: inrecruiting.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants — one with vacancies, one without —, 2026-09-20 14:5x–15:0x UTC, the declared client, the guard on the exact path first, the shared host's page read twice. Rules: `inrecruiting.intervieweb.it/robots.txt` (200, 165 B): `LinkedInBot` and `*` both `Allow: *` / `Disallow: /*access*` / `/*recoveryForm*`; `berner.intervieweb.it/robots.txt` 404 with the app's own «404 Error» page — no rules; no Crawl-delay. The career page (200; Julia Service `/juliaservice/it/career` 379 901 B ×2 — md5 405cf4b25e56 / 5cbdcf7a7d58, a token moves —; Berner `/it/career/` 398 969 B) is server-rendered with the first page of cards (Julia: 5–6 `div.row.vacancy__render`) and holds `<input id="url-for-announces" value="…/app.php?opmode=guest&module=newcareer&ajax=1&IdAzienda=<id>&CSRFToken=<t>&CSRFHash=<h>">` and a script POSTing `act1=vacancyListCareer&section=<id>&order=&page=&country=&region=&function=&project=&text=&division=&company=` there; replayed with the page's session cookie (`PHPSESSID`): Julia `{success: true, data: <html>}` 24 243 B with 6 cards — title link `/juliaservice/jobs/<slug-id>/it/`, `subtitle__informations[title=Sede]` «Ascoli Piceno Italia», `[title=Professione/Funzione]`, `vacancy__description` (an excerpt), «Invia candidatura» —; Berner 453 B, «Nessun annuncio disponibile»; no count anywhere, no pager markup on 6 cards (`researchAnnounces(page)` exists in the script); the job page `/juliaservice/jobs/addettao-…-553887/it/` (200, 354 487 B) carries one schema.org JobPosting (title, datePosted, validThrough, hiringOrganization «JULIA SERVICE SRL», jobLocation.address with streetAddress «Via L. Luciani», addressLocality, addressRegion, addressCountry «IT», description as HTML). `inrecruiting.py jobs` live: Julia 6 emitted, «no count is stated by the site: the walk stopped when a page brought nothing new»; Berner 0, «Nessun annuncio disponibile»** · 2026-09-20 -->
<!-- witness: none — no count is stated by the page or the list call; `inrecruiting.py jobs` walks until a page brings nothing new and says so · 2026-09-20 -->
<!-- route: http · 6 · 2026-09-20 -->

**Issue #476 (opened under #406, the ATS families). The premise of 13.09
(`www.in-recruiting.com` refusing the client) concerns the vendor's site; the tenants live
on `intervieweb.it` — Inrecruiting's former name — and were found by the
signature `…intervieweb.it/<lang>/career` in a search engine on 2026-09-20
(Julia Service, ORBYTA, Berner, Tecnica Group, Begear, Compagnia di San
Paolo, 4FUN, Fiamm Components, Inrecruiting's own); two measured, one
with vacancies.** Rank: the pilot's order of 2026-09-20 12:5x, after #475.

## What Inrecruiting is, and where its tenants live

Inrecruiting (Turin; Zucchetti since 2019) is Italy's Intervieweb: the
career page («Lavora con noi») lives on `<tenant>.intervieweb.it/<lang>/career/`
or on the shared `inrecruiting.intervieweb.it/<Company>/<lang>/career`; a
job at `…/jobs/<slug-id>/<lang>/`. **The user names the tenant by the
career page's own address** — two shapes exist, a composed one is refused.

## The route — the page's own list call, replayed with its parameters

```
GET  https://inrecruiting.intervieweb.it/juliaservice/it/career                                  200 — url-for-announces (IdAzienda, CSRFToken, CSRFHash), section
POST https://inrecruiting.intervieweb.it/app.php?opmode=guest&module=newcareer&ajax=1&IdAzienda=…  200 — {success: true, data: 6 cards}   (page 1)
POST …  (page 2)                                                                                 200 — the same cards: the end
GET  https://inrecruiting.intervieweb.it/juliaservice/jobs/addettao-…-553887/it/                200 — the JobPosting (the `ad` command)
POST https://berner.intervieweb.it/app.php?…                                                     200 — «Nessun annuncio disponibile»: 0 emitted, not an error
```

The CSRF pair and the session are the page's own for this visit — read
from the page, replayed on the list call, never composed; a list URL that
names another host is refused. **No count is stated**: the walk asks the
next page until a page brings nothing new and says so; `--max-pages`
bounds it, a ceiling of 200 pages is the adapter's own. Two seconds
between requests are ours.

## What the adapter emits, and withholds

`jobs --tenant "<career address>" [--country-code ISO2] [--max-pages N]`:
id (the slug with its number), url, title, place (the card's «Sede»),
function, `fields` (the card's labelled informations), summary (the
excerpt, scrubbed). **The list states a place, no country code;
`--country-code` stamps the rows and says so.** `ad --url`: title,
company, place, region, country, posted, closes, description (scrubbed).

**Withheld:** the street of the workplace; e-mail addresses and telephone
numbers in the texts; the application never touched; `contacts_withheld`
on every record.

## Tests and mutations

`AnATSWhoseCareerPageCarriesItsOwnListCallURLWithACSRFPairAndAnswersHTMLInsideJSONWithNoCount`,
both ways on fixtures (the page's own URL, section, session headers
replayed page by page until nothing new; the cards' title, place,
function and fields; the screen-reader labels not read as values; the
excerpt scrubbed; the empty tenant; the bounded walk; a list URL on
another host refused; a page without the URL or the section; a non-JSON
answer; a 404; the ad's JobPosting with the street withheld; bad
addresses; other hosts refused; composed tenants refused). Mutation bench
on a detached copy, `python3 -B`, 10 / 10 red: the list URL composed ·
another host's list replayed · the section not sent · the walk stopping
after the first page · the summary not scrubbed · the screen-reader label
read as a value · the empty tenant read as an error · the street emitted ·
the ad not scrubbed · a composed tenant accepted.
