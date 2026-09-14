# Board measurement — Oikotie Työpaikat (`tyopaikat.oikotie.fi`, Finland): the board has closed — the root serves one page that says so in writing, «Oikotie Työpaikat on sulkeutunut», and links only the property sites of the group

<!-- verified: 2026-09-14 -->

<!-- hosts: tyopaikat.oikotie.fi -->
<!-- script: none -->
<!-- countries: FI -->
<!-- content: measured · **the board is closed, and the page says so**: `https://tyopaikat.oikotie.fi/` answers 200, 17 499 B, `md5 c48048a9e001` twice (02:01:0x UTC, the same to the byte as the country page's read of 2026-09-13 17:01) — a Vite SPA shell saved from `localhost:5173` whose rendered body reads «Oikotie Työpaikat on sulkeutunut. Suuret kiitokset kaikille työnhakijoille, yrityksille ja kumppaneille näistä upeista vuosista.» («Oikotie Työpaikat has closed. Many thanks to all job-seekers, companies and partners for these wonderful years»), then the group's property links (asunnot, toimitilat, Tori, Qasa …); the client bundle (175 107 B) names no data route; `/robots.txt` is a 301 to the same shell (an absence of rules since #283); `www.oikotie.fi/tyopaikat` is a 301 to `/404`; `www.oikotie.fi/` a 301 to `asunnot.oikotie.fi` — read by the declared client · 2026-09-14 -->
<!-- witness: none — there is no list and no count; the measurement is the closure notice itself, read twice at the same fingerprint · 2026-09-14 -->
<!-- route: none · the board no longer exists — its only page is a closure notice; there is nothing for a script or a browser to render (#404: a script that yields nothing does not count) · 2026-09-14 -->

**Sanoma's Oikotie Työpaikat — for years Finland's second private
generalist — has closed, and its host says so on its only page.** Issue
#375, opened under #291 on a root read in 200 that the country page of
2026-08-31 had taken for «a SPA shell». Measured 2026-09-14 02:01 UTC by
the declared client, the guard on the exact path.

## What the host serves

```
GET https://tyopaikat.oikotie.fi/robots.txt      301 → https://tyopaikat.oikotie.fi/   (no rules file: an absence, open, `certain` false — #283)
GET https://tyopaikat.oikotie.fi/                200, 17 499 B, md5 c48048a9e001 — twice, the same byte for byte; and the same as 2026-09-13 17:01 UTC
    <!-- saved from url=(0022)http://localhost:5173/ -->   a Vite dev page saved and deployed as the site
    <div id="app"> … Oikotie Työpaikat on sulkeutunut … Suuret kiitokset kaikille työnhakijoille, yrityksille ja kumppaneille näistä upeista vuosista …
    links: asunnot.oikotie.fi, toimitilat.oikotie.fi, tori.fi, qasa.fi, autovex.fi … — not one job address
GET https://tyopaikat.oikotie.fi/index_files/client   200, 175 107 B — the bundle: Vite's own URLs, no API route
GET https://www.oikotie.fi/tyopaikat             301 → https://www.oikotie.fi/404
GET https://www.oikotie.fi/                      301 → https://asunnot.oikotie.fi/
```

The 200 that opened the issue was the closure notice: **the SPA that
the country page expected to query has no data route because it has no
data** — the shell is rendered once, from a saved dev page, and says
the board is gone. The page also carries the group's terms («Säännöllinen,
järjestelmällinen tai jatkuva tietojen kerääminen … ei ole sallittua ilman
Oikotien antamaa kirjallista lupaa» — systematic collection without
written permission is not allowed), which would have bounded an adapter
had there been one.

## What replaces it for a Finnish search

The market's private generalist is Duunitori (`duunitori.md`, shipped),
the public service Työmarkkinatori (`tyomarkkinatori.md`, under the
user's own `override_robots` key), the municipalities Kuntarekry and the
State Valtiolle (`kuntarekry.md`, `valtiolle.md`). Nothing of Oikotie
Työpaikat's inventory is served anywhere on the host.

## What would reopen this card

- **A list on `tyopaikat.oikotie.fi`** — the root serving anything but
  the closure notice (its `md5 c48048a9e001` changing would be the
  first sign).
- **A successor named by the group** — the page names none; Vend's
  other Finnish sites are property, cars and classifieds.

## 2026-09-14 — measured, no adapter

Route none: the board is closed and says so. No script (#404), no
browser route — there is nothing to render. The card names the one
observation that would reopen it.
