# Board measurement — HRlink (a Polish ATS): its public side is the advert and the form on `ats.hrlink.pl` (`/advc/<base64>` naming an `advertisement_id`, `?module=aplikacja&fix=<client>&id_ogloszenie=`), one per job; the tenant's list — the «zakładka kariera» — is a page HRlink builds on each client's own site, so no list host is nameable by signature; no adapter until a client's career tab is named (#473)

<!-- verified: 2026-09-20 -->

<!-- hosts: ats.hrlink.pl, www.hrlink.pl -->
<!-- script: none -->
<!-- countries: * -->
<!-- content: measured · **2026-09-20 14:2x–14:3x UTC, the declared client, the guard on the exact path first. Rules: `ats.hrlink.pl/robots.txt` answers 404 with the app's own «404 Not Found» page (2 470 B) — no rules; `hrlink.pl` open on 13.09 (the vendor's site, a TLS certificate for another name on the apex). What a search engine names on `ats.hrlink.pl`: adverts `/advc/<base64>` (the base64 decodes to `4129-173-8219-{"advertisement_id":10232,"country_id":1,"advertisement_template_id":70,"form_template_id":25}-13755`) and application forms `/?module=aplikacja&page=kandydat&fix=<client id>&id_ogloszenie=<n>&id_reg=<n>…` (clients `fix=2195`, `1192`, `2538`, `1647`, `1710`); the one advert found (`advertisement_id` 10232, «Stażysta Data Mining») answers 404 «Wystąpił nieoczekiwany błąd» (2 470 B) — gone. No list address: HRlink's own site says the «zakładka Kariera» (the list of a client's offers) is prepared by HRlink for each client «adapted to the client's website» — it lives on the client's domain, in the client's markup; `kariera.hrlink.pl` is a parked hosting page. Nothing on `ats.hrlink.pl` enumerates a client's adverts** · 2026-09-20 -->
<!-- witness: none — no list was found to count · 2026-09-20 -->

**Issue #473 (opened under #406, the ATS families). The premise of 13.09
(a TLS certificate for another name on `hrlink.pl`) concerns the vendor's
apex; measured 2026-09-20: the family's public host is `ats.hrlink.pl`,
open, and it serves adverts and forms one by one — no tenant list.**
Rank: the pilot's order of 2026-09-20 12:5x, after #472.

## What HRlink is, and where its tenants live

HRlink (Szczecin) is one of Poland's two leading ATS. Its multiposting
pushes adverts to job boards (Pracuj.pl, OLX…); its own public pages are
the advert (`ats.hrlink.pl/advc/<base64>`) and the application form
(`ats.hrlink.pl/?module=aplikacja&fix=<client>&id_ogloszenie=<n>…`, the
`fix` parameter being the client). **The list of a client's offers is a
«zakładka Kariera» HRlink builds into the client's own website** — bespoke
markup on the client's domain — and nothing on `ats.hrlink.pl` enumerates
it.

## Why there is no adapter yet

The README's rule for an ATS family asks for a tenant named by the
family's signature and a list to walk. Here the signature names adverts
and forms, not lists; the lists are the clients' own pages, each in its own
shape. An adapter that reads `ats.hrlink.pl/advc/<base64>` would give
`ad` and nothing to enumerate — a route to single pages, not a board.

**What lifts it:** a client's career tab named (a URL on a client's domain
whose list links to `ats.hrlink.pl/advc/…` or `?module=aplikacja&fix=`),
read twice, so the list's shape can be measured; or a list endpoint on
`ats.hrlink.pl` (a `fix=`-keyed page) found by someone who uses the
system. Until then #473 says so and stays `blocked` (waiting for an
event).
