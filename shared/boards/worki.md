# Board adapter — Worki (`www.worki.sk`, SK): the board the old public labour-market guide (istp.sk) redirects to — a server-rendered listing that states its count («Zobraziť 623 pracovných ponúk» on 2026-09-14) and pages by path, a jobs sitemap of the same ids, and a labelled ad page cut before «Kontaktná osoba»; the state's portal republishes 537 of the 623

<!-- verified: 2026-09-14 -->

<!-- hosts: www.worki.sk -->
<!-- script: worki.py -->
<!-- host-forms: www.worki.sk -->
<!-- host-forms-basis: read — every card link, sitemap row and employer link is on `www.worki.sk`; `worki.py` names the host as a literal and refuses an ad address on any other · 2026-09-14 -->
<!-- countries: SK -->
<!-- content: measured · **`/ponuka-prace` (200, 342 025 B) is server-rendered: the filter button prints the site's own count («Zobraziť 623 pracovných ponúk»), twenty cards follow in `#offers`, the pager links `/ponuka-prace/2` … `/32`; a card carries the ad link `/ponuka-prace/<employer-slug>/<id>-<slug>`, a «TOP» badge (270 of 623), the title, the employer with its `/zoznam-zamestnavatelov/<id>` link, the place line, the contract line (402 «Pracovný pomer na dobu neurčitú», 69 fixed-term, 66 «Práca na živnosť»), the salary line as printed («od 150 € do 2 000 € za mesiac»; 524 monthly, 64 hourly, 35 «Neuvedená mzda»; one in CZK) and the freshness («Aktualizované dnes / včera / <date>»). 623 emitted in 32 pages, 623 stated — equal. `/sitemap.xml` is an index of three files; `sitemap.jobs.xml` names the same 623 ids with a `lastmod` that is the file's generation time (06:00 local on every row — never emitted as a date). The ad `/ponuka-prace/<employer>/<id>-<slug>` (200, 239 358 B, no JSON-LD) is a labelled page: a facts block («Miesto výkonu práce» with the street address and notes, «Dátum nástupu», «Dátum pridania ponuky» with its update, «Druh pracovného pomeru», «Mzda (v hrubom)» with the site's note, «Počet voľných pracovných miest»), the «Údaje o pracovnom mieste» sections (Náplň práce, Informácie o výberovom procese, Pracovný režim, Pracovné miesto vhodné aj pre, Ponúkané výhody), the «Požiadavky na zamestnanca» sections (vzdelanie, prax, digitálne zručnosti, vodičské oprávnenie, spôsobilosti, ďalšie požiadavky), the employer's public record (Obchodné meno, IČO, Adresa, Internetová stránka, Charakteristika spoločnosti)** — read by the declared client, the guard on the exact path (the rules, 200 B: `*` `Disallow: /organization`, `/admin`, `/*/pracovna-ponuka/*/poslat-zivotopis*`, `/pracovna-ponuka/*/poslat-zivotopis*`, `/nelmio/csp/report*`; no Crawl-delay, 2 s ours; the refused paths never sent, exit 7); **«Kontaktná osoba» — a name and a telephone — and «Podobné pracovné ponuky» cut before reading; every text scrubbed of e-mail addresses and Slovak telephone numbers (the ad read carried the employer's own e-mail in its selection-process text); `contacts_withheld` on every record; the CV form never touched. The state's portal (`sluzbyzamestnanosti.md`, `zdrojPonuky=WRK`) republishes 537 of these 623 — all 537 in the sitemap, 0 outside it, 86 only here — with title, employer, place and salary and a link out: the direct read adds the 86 and every ad's body (04:2x UTC)** · 2026-09-14 -->
<!-- witness: the listing's own «Zobraziť N pracovných ponúk» — printed beside every walk («623 emitted in 32 page(s), the site states 623 — equal»); a page without the count or without a card exits 6, a page serving page 1's cards again exits 6 — a changed template, never an empty market; the root's «1818 pracovných ponúk» is another figure and is not read · 2026-09-14 -->

**Worki is the board the old public labour-market guide istp.sk redirects to —
623 advertisements stated on the day, 402 open-ended contracts, salary printed
on 585, «TOP» on 270; the state's portal republishes 537 of them.** Issue #344.
Measured 2026-09-14 04:2x UTC by the declared client, the guard on the exact
path before each request, two seconds apart.

## Three readings that agree, and one that does not

```
www.worki.sk/robots.txt                  200, 200 B — User-agent: *: Disallow /organization, /admin, /*/pracovna-ponuka/*/poslat-zivotopis*, /pracovna-ponuka/*/poslat-zivotopis*, /nelmio/csp/report*; Sitemap /sitemap.xml
GET /                                    200, 174 816 B — «U nás nájdeš 1818 pracovných ponúk»: not the listing's figure, not read
GET /ponuka-prace                        200, 342 025 B — «Zobraziť 623 pracovných ponúk», 20 cards, pager /ponuka-prace/2 … /32
GET /ponuka-prace/2 … /32                200 — 20 cards each, the 32nd 3: 623 distinct ids
GET /sitemap.xml → sitemap.jobs.xml      200 — 623 /ponuka-prace/<employer>/<id>-<slug> rows, lastmod = the file's generation time
sluzbyzamestnanosti.gov.sk/search/ponuky?zdrojPonuky=WRK   200 — countVPM 537, 537 rows, 537 ids ⊂ the 623
GET /ponuka-prace/<employer>/<id>-<slug> 200, 239 358 B — the labelled page, cut before «Kontaktná osoba»
```

The listing, the sitemap and the walk agree at 623; the root's «1818» is a
different figure (positions, or a marketing count) and is left alone. The
state's portal (`sluzbyzamestnanosti.md`) republishes 537 with a link out —
title, employer, place, salary — so the direct read adds 86 advertisements
and, on every one, the body: tasks, selection process, regime, benefits,
requirements, the employer's register record.

## The record, and what is withheld

The card's own lines, the salary as printed (a floor, a ceiling, one figure,
its currency, its period — `salary_unit_stated` only when a figure and a
period are both there), and on the ad the facts, the sections and the
employer's public record. **«Kontaktná osoba» — a name and a telephone — is
cut before reading, and so is «Podobné pracovné ponuky»; the texts are
scrubbed; the CV form, refused in writing, is never sent.**

## Running it

```
python3 skills/job-scan/scripts/worki.py list                 # 623 rows, 32 requests, ~65 s
python3 skills/job-scan/scripts/worki.py list --pages 2
python3 skills/job-scan/scripts/worki.py sitemap              # the 623 ids, 2 requests
python3 skills/job-scan/scripts/worki.py ad --url https://www.worki.sk/ponuka-prace/<employer>/<id>-<slug>
```

Exit codes: 0 all read · 3 the ad is gone · 6 a 200 without the count, a
card or the ad's header, or a pager that repeats (a changed template, never
an empty market) · 7 a refused path. No key, no browser, no login.
