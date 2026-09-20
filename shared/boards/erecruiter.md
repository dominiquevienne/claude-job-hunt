# Board adapter — eRecruiter (Poland's most used ATS, one tenant at a time): the employer's career site on `<tenant>.pracujunas.pl` carries in its own page data the keyed feed it renders — `offers.erecruiter.pl/skk/company/<id>/offers.json?hash=` — replayed as the page carries it; the feed is the board (no count stated); the offer page on `skk.erecruiter.pl` for `ad`; `erecruiter.py`, the form, the GDPR clause and the coordinates never emitted

<!-- verified: 2026-09-20 -->

<!-- hosts: zabka.pracujunas.pl, dkms.pracujunas.pl, viessmann.pracujunas.pl, hopi.pracujunas.pl, steico.pracujunas.pl, kaczmarekelectric.pracujunas.pl, offers.erecruiter.pl, skk.erecruiter.pl -->
<!-- host-forms: {tenant}.pracujunas.pl, offers.erecruiter.pl, skk.erecruiter.pl -->
<!-- host-forms-basis: read — `erecruiter.py:SITE_DOMAIN` with the tenant as its subdomain (`tenant_of`), `FEED_HOST` and `AD_HOST` as literals; one tenant per run, every other host refused before the gate; `system.erecruiter.pl` (the application form the issue named) is never requested · 2026-09-20 -->
<!-- script: erecruiter.py -->
<!-- countries: * -->
<!-- content: measured · **six tenants — three with offers, one without —, 2026-09-20 14:1x–14:2x UTC, the declared client, the guard on the exact path first, the sites read twice. Rules: `zabka.pracujunas.pl/robots.txt` (200, 1 248 B) is Cloudflare's content-signal comment block with no directive (open, `certain: False`); `offers.erecruiter.pl` and `skk.erecruiter.pl` publish no rules file (404). The career site (200; Żabka 19 735 B ×2 same md5, Viessmann 21 677 B ×2, DKMS 19 717 B ×2) is a Next.js shell — «powered by eRecruiter» in the footer — whose `__NEXT_DATA__.props.pageProps.companyData` carries `companyName` (the numeric id, 18802512), `companyDisplayName`, `subDomainName`, `regions` (Image, Text, OffersList, SpontaneousApplication) and **`offersLink`: `https://offers.erecruiter.pl/skk/company/18802512/offers.json?hash=24F0…` — the tenant's public feed key, printed in the page**; the feed (200; Żabka 402 404 B ×2 — md5 6761ece02477 / 6aaab08a644d, the items' order moves; DKMS 5 518 B; Viessmann 11 B, `{"jobs":[]}`) answers `{jobs: [...]}`: Żabka 25 items for 18 offers (`jobOfferId`, one item per `jobOfferRegionId`), DKMS 1, HOPI 8, STEICO 11, Kaczmarek Electric 5; `page=`, `take=`, `skip=`, `offset=` on the feed are ignored (measured on Żabka: 25 either way) — whether the feed caps is not established (no tenant above 25 seen), and the page renders the same feed; the item: url (`skk.erecruiter.pl/Offer.aspx?oid=&ejoId=&ejorId=&comId=`), urlWithLayout, title, publishDate, expiryDate, company, partnership, location (towns, comma-separated), referencenumber, country {isoCode «PL»}, region {name}, departments, additionalFields, branches, applicationLink (`system.erecruiter.pl/FormTemplates/RecruitmentForm.aspx?webid=`), companyDescription, requirements, opportunities, notes, clause (the GDPR text), experience, positionDescription (HTML), lastModificationDate, uniqueId, geolocations, compensationPackage {salaryRanges, benefits}; five e-mail addresses in Żabka's texts. The offer page `skk.erecruiter.pl/Offer.aspx?oid=4952907&…` (200, 17 434 B): `p.offComp`, `h1`, `#divWorkplace`, `#divRegionName`, sections `#divJobDescription` / `#divRequirements` with `h2` and `div.desc`; no JobPosting. `erecruiter.py jobs` live: Żabka 25 emitted (18 offers), Viessmann 0, «the feed is the board»** · 2026-09-20 -->
<!-- witness: none — no count is stated by the page or the feed; `erecruiter.py jobs` prints the feed's length (items and offers) and says so · 2026-09-20 -->
<!-- route: http · 25 · 2026-09-20 -->

**Issue #471 (opened under #406, the ATS families). The signature the
issue named — `system.erecruiter.pl/FormTemplates/…` — is the application
form, one per job, no list; the lists live on the employers' career sites
built by eRecruiter's Career Sites Builder on `<tenant>.pracujunas.pl`,
found by that signature in a search engine on 2026-09-20 (Żabka, DKMS,
Viessmann, HOPI, STEICO, Kaczmarek Electric, Ministerstwo Cyfryzacji,
Saltus, Ryłko); three with offers measured, as the README's two-tenant
rule asks.** Rank: the pilot's order of 2026-09-20 12:5x, after #470.

## What eRecruiter is, and where its tenants live

eRecruiter (eRecruitment Solutions, Grupa Pracuj, Warsaw) is Poland's most
used ATS (2 300 companies). Its Career Sites Builder hosts the employer's
career page on **`<tenant>.pracujunas.pl`** («pracuj u nas», work with us);
the page renders the offers from a feed on `offers.erecruiter.pl` and links
each offer to its page on `skk.erecruiter.pl` and its form on
`system.erecruiter.pl`. Career Site PRO tenants and the JavaScript widget
live on the employers' own domains and are not covered. **The user names
the tenant by its subdomain**, its host or the site's URL.

## The route — the page's own feed link, replayed as given

```
GET https://zabka.pracujunas.pl/                                                              200 — __NEXT_DATA__ … offersLink
GET https://offers.erecruiter.pl/skk/company/18802512/offers.json?hash=24F0…                 200 — {"jobs": [25]}
GET https://skk.erecruiter.pl/Offer.aspx?oid=4952907&ejoId=812866&ejorId=550752&comId=18802512  200 — the offer (the `ad` command)
GET https://viessmann.pracujunas.pl/ → its feed                                               200 — {"jobs": []}: 0 emitted, not an error
```

**The feed's `hash` is the tenant's public key, printed in every visitor's
page** — the SparkHire shape (#452): the adapter reads the page, takes the
link as it is, refuses a link of another shape (exit 6), and requests the
feed once. **No count is stated anywhere**, so `jobs` prints the feed's
length — items and distinct offers — and says the feed is the board. Two
seconds between requests are ours.

## What the adapter emits, and withholds

`jobs --tenant <name> [--country-code ISO2]`: id (the region item),
offer_id, url (the offer page), title, company, brand, place (the towns),
region, country (the feed's `isoCode`; an item without one is stamped with
`--country-code`, said aloud), departments, reference, published, closes,
updated, salary_ranges, benefits, description (the position, scrubbed),
sections (requirements, opportunities, notes, companyDescription,
experience — scrubbed). `ad --url`: title, company, place, region,
description and the page's sections by their own headings.

**Withheld:** the application form (`applicationLink`, the layout key
`cfg=`), the GDPR clause, the workplace coordinates; e-mail addresses and
telephone numbers in the texts; `contacts_withheld` on every record.

## Tests and mutations

`AnATSWhoseCareerSiteCarriesItsOwnKeyedFeedLinkAndWhoseFeedListsAnOfferOncePerRegion`,
both ways on fixtures (the feed link replayed as the page carries it, one
row per region item and the offers counted, a repeated item, the country
and the stamp with a foreign item filtered, the form / clause /
coordinates absent, the texts scrubbed, the empty feed, a page without
`companyData`, a feed link of another shape, a non-eRecruiter page, a 404,
the offer page's sections and scrubbing, the layout key dropped, bad
addresses, other hosts refused, bad tenants). Mutation bench on a detached
copy, `python3 -B`, 10 / 10 red: the feed link composed · the feed shape
not checked · region items collapsed to offers · the form link emitted ·
the clause emitted · the texts not scrubbed · the country filter dropped ·
missing company data read as empty · the layout key kept · the ad's
sections not scrubbed.
