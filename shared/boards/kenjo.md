# Board measurement — Kenjo (a Spanish/DACH ATS, one tenant at a time): every employer's career site lives on `<tenant>.kenjo.io`, and every such host writes `User-agent: * / Disallow: /` — the whole tenant host refused in writing, the vendor's own `www.kenjo.io` open; no route crosses a written refusal, and nothing permitted shows the request shape to write the adapter from — the user's own key is the exit (#403), and it needs a first keyed read (#487)

<!-- verified: 2026-09-21 -->

<!-- hosts: doctorlycareer.kenjo.io, -ofertas-de-empleo.kenjo.io, www.kenjo.io -->
<!-- script: none -->
<!-- countries: * -->
<!-- content: measured · **rules read twice on each host, 2026-09-21 09:04 UTC, the declared client. `doctorlycareer.kenjo.io/robots.txt` and `-ofertas-de-empleo.kenjo.io/robots.txt` (200, 26 B ×2 each, md5 f71d20196d4c on both hosts, both reads): `User-agent: * / Disallow: /` — the tenant host closed evenly, `_robots.allowed` → `host-closed`, certain; `www.kenjo.io/robots.txt` (200, 66 B ×2, md5 948706223ba5): `User-agent: * / Allow: /` and a sitemap — the vendor's marketing site, not a board. Nothing of a tenant's list or ad was read: the guard refuses the root before the transport, and the plugin does not sound a written refusal. The vendor's help centre names the form (`https://<subdomain>.kenjo.io/`, «Set up a Career site with Kenjo»); the article's own address answers 404 today** · 2026-09-21 -->
<!-- witness: none reachable by a permitted path — the list lives on the refused tenant host · 2026-09-21 -->

**Issue #487 (opened under #406, the ATS families). The premise of 13.09
(`www.kenjo.io` open, «rien de connu ne bloque») concerns the vendor's
marketing site; measured 2026-09-21: the family's tenant hosts —
`<tenant>.kenjo.io`, the form the vendor's help centre documents — write
`User-agent: * / Disallow: /` (the same 26 bytes on the two tenants named
by a search engine, twice each).** Rank: the pilot's order of 2026-09-21
06:13 UTC — #479 → #488 after the dated controls; GO of 09:04 UTC.

## What was read, and what was not

The tenants' file, as written (26 bytes, both hosts, both reads):

```
User-agent: *
Disallow: /
```

```
GET https://doctorlycareer.kenjo.io/robots.txt        200 ×2 — 26 B, md5 f71d20196d4c — the file above
GET https://-ofertas-de-empleo.kenjo.io/robots.txt    200 ×2 — the same 26 bytes
GET https://www.kenjo.io/robots.txt                   200 ×2 — 66 B — User-agent: * / Allow: / + a sitemap (the vendor's site)
_robots.allowed("doctorlycareer.kenjo.io", "/")       allowed False, kind host-closed, certain True — «everything closed, evenly. Not swept.»
```

**Nothing else was fetched.** A `Disallow: /` written to `*` is a refusal
by every route — the plain client and a tab alike (bound 1 of the
2026-09-07 decision): the plugin neither reads the list under it nor
opens a tab on it. The refusal is the host's, not a provider's: two
tenants, the same bytes, and the vendor's own site open beside them.

## Why no adapter, and what would change it

An adapter needs the list's request shape — the page, its markup or the
call it makes — and every byte of it lives under the refusal. Unlike UKG
Pro (where a permitted route showed the shape and the card carries an
`override:` line), **nothing permitted shows Kenjo's**, so there is
nothing to write from. The exit is the one the owner generalised on
2026-09-13 (#403): the user's own `boards.kenjo.override_robots: true`,
set by the user, never by `job-setup` — and its first keyed read is what
would tell the shape and let the adapter be written. Until then: no
route, no script, the issue `blocked` with this measurement.

Same form as Webcruiter (#465) and, for the «nothing to write from» half,
HRlink (#473).
