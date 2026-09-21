# Board adapter — rexx systems (an ATS, one tenant at a time): the tenant's portal on `<tenant>-portal.rexx-recruitment.com` lists its positions on `/stellenangebote.html?start=N` (a table or cards, a pager 100 apart) and each ad carries one JobPosting with four text sections; `rexx.py`, the street, the postal code and the session id never emitted

<!-- verified: 2026-09-21 -->

<!-- hosts: stadtfrankfurt-portal.rexx-recruitment.com, msig-portal.rexx-recruitment.com, codesys-portal.rexx-recruitment.com -->
<!-- host-forms: {tenant}.rexx-recruitment.com -->
<!-- host-forms-basis: read — `rexx.py:110` (`host_of`: `--tenant` is REQUIRED, a portal subdomain with or without `-portal`, a host or an address on it, resolved to `<tenant>-portal.rexx-recruitment.com`; the vendor's own subdomains refused, `rexx.py:68`; `request()` refuses any other host before the gate — a tenant's custom domain in the links is rewritten to the portal host, never sent to) · 2026-09-21 -->
<!-- script: rexx.py -->
<!-- countries: * -->
<!-- content: measured · **three tenants with positions, 2026-09-21 07:22–07:24 UTC, the declared client, the guard on the exact path, two reads each. Rules: every portal publishes the same 382-byte file — seventeen HTTP libraries named by their default tokens (wget, python-requests, python-urllib, Go-http-client, Java, libwww-perl, PHP/, LWP::Simple, okhttp, axios, http-client, aiohttp, Scrapy, Httpie, PycURL, node-fetch, node-superagent) and refused `/`; no `*` group, no other name, no Crawl-delay — the plugin's declared token is not named and no group binds it (`_robots.allowed`: open, certain): the file refuses default library identities, not a declared agent. The list `/stellenangebote.html` (200; Stadt Frankfurt 83 205 B, MSIG 31 283 B, CODESYS 24 427 B — Frankfurt's md5 moving, a session id in every link) renders in one of two layouts: a table `#joboffers.real_table` whose `<th>` links name the columns by `order[field]` (stellenbezeichnung, standort_bez, taetigkeiten, valid_until — Frankfurt: **100 rows on `start=0`, 4 on `start=100`, the `#joblist_navigator` pager's `nav_next` empty on the last page; «00.00.0000» for no deadline**), or cards `.joboffer_container` (title link, `.job_standort`, `.job_details_second` — **MSIG 5, CODESYS 6**, no pager); the ad's address `/<slug>-<lang>-j<id>.html`; Frankfurt's links carry its own host `stadtfrankfurtjobs.de` and `?sid=<32 hex>`. No count stated anywhere, no JobPosting on the list. The ad (200 ×2, MSIG 191 421 B; Frankfurt 79 296 B on the portal host) carries one JobPosting — title, description, responsibilities, qualifications, jobBenefits (HTML, entity-escaped; Frankfurt's double-encoded: «&Atilde;&frac14;» for «ü», «&acirc;&#128;&#130;» for U+2002), datePosted, validThrough, employmentType, hiringOrganization (logo empty), jobLocation with streetAddress and postalCode, addressCountry «DE». Exercised: `jobs --tenant stadtfrankfurt --country-code de` → 104 emitted over 2 pages (the stamp said); MSIG by its list address → 5; the MSIG ad → the posting's four sections** · 2026-09-21 -->
<!-- witness: none — no count is stated anywhere; `rexx.py jobs` prints the emitted count with the pages walked and says the pager was followed to its end · 2026-09-21 -->
<!-- route: http · 104 · 2026-09-21 -->

**Issue #482 (opened under #406, the ATS families). Measured 2026-09-21
07:22–07:24 UTC by the declared client, the guard on the exact path, on
three tenants named by the family's signature (`rexx-recruitment.com` in a
search engine): Stadt Frankfurt (104), CODESYS (6), MSIG Europe (5).**
Rank: the pilot's order of 2026-09-21 06:13 UTC — #479 → #488 after the
dated controls.

## What rexx is, and where its tenants live

rexx systems (Hamburg) sells an HR suite; its recruiting portal is hosted
on `<tenant>-portal.rexx-recruitment.com` — a city administration, an
insurer, a software house, an agency network, a cultural institute. A
tenant often frames the portal under its own domain
(`stadtfrankfurtjobs.de`); the portal's links then carry that domain and
a `?sid=` session id. **The user names the tenant** by its portal
subdomain (`stadtfrankfurt`, `msig-portal`), its host, or any address on
the portal; the adapter sends only to the portal host and rewrites the
links to it.

## The rules — a file that names libraries, not agents

The file refuses seventeen HTTP libraries by their **default** tokens —
what a script sends when it declares nothing — and writes no `*` group.
The plugin declares its own token on every request; the file does not
name it and no group applies. `_robots.allowed` answers open and certain,
and this card says why: the rule is read as written, and what it forbids
is anonymity, which the plugin never uses.

## The route — the list walked, the ad read

```
GET https://stadtfrankfurt-portal.rexx-recruitment.com/stellenangebote.html             200 — a table, 100 rows; nav_next → ?start=100
GET https://stadtfrankfurt-portal.rexx-recruitment.com/stellenangebote.html?start=100   200 — 4 rows; nav_next empty
GET https://msig-portal.rexx-recruitment.com/stellenangebote.html                       200 — 5 cards; no pager
GET https://msig-portal.rexx-recruitment.com/Underwriter-Casualty-mwd-de-j560.html      200 — one JobPosting (the `ad` command)
```

Two layouts, one record: the table's columns are read by the `<th>`
links' `order[field]` (`stellenbezeichnung` → title, `standort_bez` →
location, `taetigkeiten` → level, `valid_until` → deadline), the cards by
their classes (`job_standort` → place, `job_details_second` → level). The
pager's `nav_next` is followed until empty; a page whose ids repeat the
previous one ends the walk (exit 6). No count is stated anywhere: the run
prints «N emitted over P page(s)» and says the pager was followed to its
end. `--country-code` **stamps** on the list (it states no country) and
says so; on the ad it filters on the posting's own country.

## What the adapter emits, and withholds

`jobs --tenant <tenant> [--country-code ISO2] [--max-pages N]`: id, url
(on the portal host, no session id), title, lang (from the address),
place, location, department, level, deadline (dd.mm.yyyy → ISO;
«00.00.0000» → none). `ad --url`: the page's JobPosting — title, company,
place, region, country, employment_type, published, expires, and
`sections` (description, responsibilities, qualifications, benefits) as
text, scrubbed, the double-encoding repaired run by run («Ã¼» → «ü»,
«â€‚» → U+2002) only where the run reads as UTF-8 after re-encoding.

**Withheld:** `streetAddress` and `postalCode`; the session id; every
e-mail address and telephone in the texts replaced by «[e-mail withheld]»
/ «[telephone withheld]» — a date («bis 25.10.2026») is left alone;
`contacts_withheld` on every record; the application (a form on the
portal) never touched.

## Tests and mutations

`AnATSWhosePortalListsInATableOrCardsAndWhoseLinksCarryASessionIdAndACustomHost`,
both ways on fixtures (the table over two pages with a session id and a
custom host in every link, the «00.00.0000» deadline, the cards in `de`
and `en`, the stamp said, `--max-pages`, the empty list, the repeating
page, a page that is not a portal, the unknown portal, the vendor's hosts,
the custom host and another host refused, the ad with its street, its
telephone and e-mail, its double-encoding, the country filter on the ad,
the ad gone or changed). Mutation bench on a detached copy, `python3 -B`
— see the PR.
