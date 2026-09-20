# Board adapter — Traffit (a Polish ATS, one tenant at a time): the employer's career page on `<tenant>.traffit.com/career/` fills its list by `GET /public/an/list/?limit=&offset=&page=` — the call its own widget makes — whose answer states `count`; the advert page is server-rendered; `traffit.py`, the form, the coordinates and the unlabelled custom fields never emitted

<!-- verified: 2026-09-20 -->

<!-- hosts: scalo.traffit.com, vercom.traffit.com -->
<!-- host-forms: {tenant}.traffit.com -->
<!-- host-forms-basis: read — `traffit.py:DOMAIN` with the tenant as its subdomain (`tenant_of`), one per run, every other host refused before the gate; the vendor's `traffit.com` and its CDN `cdn3.traffit.com` are not boards · 2026-09-20 -->
<!-- script: traffit.py -->
<!-- countries: * -->
<!-- content: measured · **two tenants with adverts, 2026-09-20 14:2x UTC, the declared client, the guard on the exact path first, each page and list read twice. Rules: `scalo.traffit.com/robots.txt` answers 404 with the app's own page — no rules. The career page `/career/` (200; Scalo 12 116 B ×2 same md5, Vercom 881 189 B ×2 same md5) is a server-rendered shell with an «Otwarte rekrutacje» section filled by `/public/an/generateJs/` (200, 65 269 B — the list widget, read once): it builds `request = {obj: {}, filter: [], limit, offset: 0, page: 1}` (`careerPageJobPostLimit` 10) and GETs `<site>public/an/list/` with the object flattened to a query string; the answer (200; Scalo 94 563 B ×2 same md5, Vercom 95 118 B ×2 same md5) is `{count, items[]}` — Scalo **235** stated, Vercom 7; `limit=50` honoured (50 items, 448 710 B), `offset=10&page=2` advances (other ids); the item: advertId, advertPublishId, recruitmentId, nrRef, name, title («(11882) QA/Test Lead», the id prefixed), url (`/public/an/<hash>?source=career_page`), applicationForm (`/public/form/a/<id>`), validStart / validEnd (epoch), language, confidential, remote, job {id, experienceLevel[]}, description / requirements / responsibilities / benefits (HTML), locations[] (locality, region1..3, country, iso, postcode, latitude, longitude), geolocation, headerPhoto, `_vacStatus`, and custom fields under 32-hex keys with no label («Regular/Senior», «Hybrydowo», «do 115 PLN/h», «B2B» on Scalo — a rate and a contract type the key does not name); no e-mail address in Scalo's 235. The advert page `/public/an/6c60…` (200, 136 458 B): `h1.advert-data__name`, five `article.main__article > div.article__content` (nested divs), the apply button to `/public/form/a/<id>`; no JobPosting. `traffit.py jobs` live: Scalo 235 emitted, states 235, 5 calls of 50; Vercom 7 = 7** · 2026-09-20 -->
<!-- witness: the answer's own `count` — `traffit.py jobs` prints it beside the emitted number on every walk · 2026-09-20 -->
<!-- route: http · 242 · 2026-09-20 -->

**Issue #472 (opened under #406, the ATS families). Tenants found by the
signature `<tenant>.traffit.com/career/` in a search engine on 2026-09-20
(Scalo, Vercom, IT LeasingTeam `itlt`, `welove`, `cloud_recruitment`,
IT Performance, Edugo, Traffit's own); two with adverts measured twice, as
the README's two-tenant rule asks — Scalo is a recruitment agency's board
(235).** Rank: the pilot's order of 2026-09-20 12:5x, after #471.

## What Traffit is, and where its tenants live

Traffit (Gdańsk) is a Polish ATS (800+ clients) whose career pages live on
`<tenant>.traffit.com/career/`, the adverts on `/public/an/<hash>`, the
forms on `/public/form/a/<id>`. **The user names the tenant by its
subdomain**, its host or the career page's URL.

## The route — the widget's own call, replayed with its parameters

```
GET https://scalo.traffit.com/public/an/list/?limit=50&offset=0&page=1     200 — {count: 235, items: [50]}
GET …?limit=50&offset=200&page=5                                           200 — the last 35
GET https://scalo.traffit.com/public/an/6c60388dc0503557f220236254a6d70f386c306646513d3d   200 — the advert (the `ad` command)
GET https://vercom.traffit.com/public/an/list/?limit=50&offset=0&page=1    200 — {count: 7, items: [7]}
```

`count` is the witness, printed beside the emitted number; the walk is
bounded by the stated count's last call, a call that repeats dies with 6;
a subdomain that is no tenant answers the app's page instead of JSON (exit
6). Two seconds between requests are ours.

## What the adapter emits, and withholds

`jobs --tenant <name> [--country-code ISO2] [--max-pages N]`: id
(advertId), recruitment_id, reference, url (the advert page, tracking
dropped), title, place · region · country (the first location's locality,
region1 and `iso`; an advert without a location is stamped with
`--country-code`, said aloud), locations, remote, experience_level,
language, published / closes / updated (from epochs, UTC dates),
description (scrubbed), sections (requirements, responsibilities,
benefits — scrubbed). `ad --url`: title and the page's articles, balanced
across nested divs, scrubbed.

**Withheld:** the application form, the header photo, the workplace's
postcode and coordinates, the custom fields under hashed keys (no label —
a rate or a contract type may be among them, but nothing says which);
e-mail addresses and telephone numbers in the texts; `contacts_withheld`
on every record.

## Tests and mutations

`AnATSWhoseCareerPageWidgetListsAdvertsByLimitOffsetAndPageAndStatesTheCountWithUnlabelledCustomFields`,
both ways on fixtures (the walk 50 by offset and page to the stated 56,
the dates, the locations without postcode and coordinates, the hashed
fields and the form absent, the texts scrubbed, tracking dropped, the
country filter and the stamp, the bounded walk, a repeating call, the
empty tenant, a non-JSON answer, a 404, the advert page's articles read
balanced and scrubbed, bad addresses, other hosts refused, bad tenants).
Mutation bench on a detached copy, `python3 -B`, 10 / 10 red: the offset
not advancing · a repeat tolerated · the coordinates emitted · the form
emitted · the description not scrubbed · tracking kept · the country
filter dropped · dates left raw · a nested div ending the article · the ad
not scrubbed.
