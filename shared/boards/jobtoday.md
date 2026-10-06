# Board measurement — JobToday (`jobtoday.com`, Spain/UK/US): hourly and shift work — **every one of the 48 adverts on a facet page names an individual: a hiring manager's name, photograph and LAST-ONLINE timestamp, plus precise coordinates — and the payload contains zero e-mail and no contact-shaped field at all**, so a contact-pattern rule reports nothing withheld on a board that ships a person per advert; and the declared sitemap's 168 854 Spanish URLs are a facet cross-product containing not one advert

<!-- verified: 2026-10-06 -->

<!-- hosts: jobtoday.com, www.jobtoday.com -->
<!-- script: jobtoday.py -->
<!-- countries: ES GB US -->
<!-- host-forms-basis: read — `jobtoday.com` and `www.jobtoday.com` serve the SAME 204 B rules file (md5 9d6b7ad7e77d, `state: read`, `certain: True`); the apex resolves to a different address on each public resolver (54.228.177.143 against 18.202.67.183) because it sits behind a multi-address front, which is not a disagreement · 2026-10-05 -->
<!-- content: measured · **ADAPTER DELIVERED 2026-10-06 (#1005), and exercising the host added TWO withheld fields the issue did not name.** The route of 2026-10-05 holds: `/es/trabajos/<city>` serves a Next.js `__NEXT_DATA__` whose job records are reached by the TYPE of their items and never by a section index — on this reading sections 0 and 1 were empty and the 48 jobs sat in section 2, which is a fact about the page and not the host. **The items are ENVELOPES, `{type, payload}`, so the advert's own keys are one level down**, and `pagination` sits at `props.pageProps.pagination` and NOT under `feed` — 20 page descriptors, a reach of about 960 per facet and not a count. **WHAT MEASURING ADDED TO THE OWNER'S LIST: `addressInfo` carries no `city`, `region` or `town` at all — its keys are `countryCode`, `ghash`, `itemId`, `coordinates`, `display`, `type` — so a first row read `addressInfo.city` and emitted NULL on 48 of 48; a field empty everywhere is a reading defect until proven otherwise. The town-level string is the advert's own `address` (district, city, region, country, no street). And two further location fields are withheld on the owner's own rule without a new question: `addressInfo.display.fullName` is a STREET ADDRESS — «36 Avenida de Monforte de Lemos, Fuencarral-El Pardo, 28029, Madrid, MD, España», more precise than the coordinates the issue DID name — and `addressInfo.itemId` equals `ghash` on every record measured (both `539940`), the same geohash under a second name. An issue names the specimen; the class is measured.** **THE PERSON, RE-MEASURED: `company.hiringManager` is present on 48 of 48 with `name`, `image` and `lastOnline` all 48 of 48 — and the name the board publishes is a FIRST NAME PLUS AN INITIAL on 48 of 48 («Alejandro C.», «SANTIAGO L.»), so the host already abbreviates what the owner decided to keep.** Kept: `name`. Dropped: `image`, `lastOnline`, `coordinates`, `ghash`, `display`, `itemId` — named per RECORD and derived from presence, so a record carrying none declares none. **AND THE CONTACT-PATTERN TRAP IS CONFIRMED FROM BOTH ENDS: zero key matches phone, email or tel, while a plain e-mail regex over the page returns SEVEN matches of which NOT ONE is a contact — a Sentry DSN, an obfuscated token, and the filename `share-pict-1200x630@2x.jpg`. It invents matches where there is nothing and misses the person who is there.** SALARY, re-measured: present on 24 of 48 and `isValid` on 21, periods MONTHLY 19 and YEARLY 2 — against 28 / 26 and MONTHLY 14 / YEARLY 9 / HOURLY 3 the day before, on a board whose freshest advert was 597 seconds old at this reading: **the rates are a reading, not a property of the host.** Exercised end to end with `jobtoday.py list --city madrid --pages 1 --limit 3`, 200 on 408 414 B, md5 7ca1f4db72dc, as `Claude-User`, both host forms `allowed=True state=read certain=True` · 2026-10-06 -->
<!-- content: measured · **48 adverts arrive per facet page and every one of the 48 names a PERSON: `company.hiringManager` is present on 48 of 48 and carries `name`, `image` and `lastOnline`, while `addressInfo.coordinates` gives `lat`/`lng` and `ghash` on 48 of 48 — and the same payload holds ZERO e-mail address and not one key matching phone, email or tel. So an expurgation rule written around contact shapes finds nothing here and would record «nothing withheld» on a board that ships a named individual, their photograph and their presence timestamp with every advert; that is the mirror of declaring a withholding nobody deposited, and it is worse, because the honest-looking output is the silent one. THE DECLARED ENUMERATOR CONTAINS NO ADVERT: `robots.txt` declares TWO sitemaps and they enumerate DIFFERENT KINDS of object — `/sitemap.xml` (63 196 B) holds 478 `<loc>` for 477 distinct and they are BLOG POSTS, while `/sitemaps/sitemap_index.xml` (4 610 B) is a real index of 32 `Positions` children split by country (us 16; gb 12; es 4). The four Spanish children total 168 921 `<loc>` for 168 854 distinct, are PAIRWISE DISJOINT (all 67 duplicates lie within files, none across them), and every one of the 168 854 has exactly three segments, begins `/es/trabajos`, and carries NO identifier — no four-digit run, no UUID. They are a cross product of 6 714 categories or employers by 1 306 cities, 8 768 484 theoretical cells at 1.9 % density. A count of `<loc>` is not a count of adverts, and here it is a count of generated landing pages. WHERE THE ADVERTS ARE: a facet page such as `/es/trabajos/madrid` (403 511 B) ships a Next.js `__NEXT_DATA__` of 173 205 B whose `feed.sections[2].items` holds 48 records of `type: job`, each keyed by `key` (48 of 48 present and distinct) and addressed by `canonicalUrl` of the form `/es/trabajo/<role>-<key>` — SINGULAR `trabajo`, one letter from the plural the facets use. NO TOTAL EXISTS ANYWHERE IN THE PAYLOAD: `pagination.pages` carries 20 entries and the page's own title states «1000+ ofertas», a FLOOR and not a count, so about 960 adverts are reachable per facet and the board's size is not established. THE SALARY IS STRUCTURED AND THE BOARD FLAGS ITS OWN VALIDITY: the field is present on 28 of 48 and `isValid` is true on 26, so `if x` would count 28; the 26 valid ones all carry `currencyCode: EUR`, both `from` and `to`, and a `period` that is MONTHLY on 14, YEARLY on 9 and HOURLY on 3 — three periods on one page, so a figure without its period means nothing — and the 2 invalid ones carry no amount at all, which is what makes honouring `isValid` cost nothing. FRESHNESS: `postedSecondsAgo` spans 73 seconds to 2 172 758 seconds, about 603 hours. METHOD: guard on each host form and each exact path in turns distinct from the retrievals, `bin/fetch-body.py` throughout, no `Crawl-delay` written so the 2 s of our own pace apply** · 2026-10-05 -->

<!-- witness: none — the payload carries NO integer total; `pagination.pages` has 20 entries and the page title says «1000+ ofertas de trabajo en Madrid», which is a floor. 168 854 is the count of Spanish facet URLs in the declared sitemap and is NOT a count of adverts; 48 is the adverts on one page and 20 the reachable pages, so about 960 per facet is a reach and not an inventory · 2026-10-05 -->

## Measured 2026-10-05 — 48 adverts a page, each naming a person, and 168 854 sitemap URLs that are not adverts

```
robots.txt              204 o   md5 9d6b7ad7e77d, read, certain
  groupe *                      UN seul refus : /*_ext_*     aucun Crawl-delay -> 2 s a nous
  nommes refuses                DataForSeoBot · Yandex  ->  Disallow: /
  aucun jeton de ce projet nomme
  DEUX sitemaps declares
/sitemap.xml         63 196 o   478 loc / 477 distincts  ->  des BILLETS DE BLOG
/sitemaps/sitemap_index.xml     INDEX de 32 enfants « Positions »
                                us 16 · gb 12 · es 4
                                32 lastmod, UNE valeur : 2026-10-05 (date de BUILD)
les 4 enfants es                50 000 + 50 000 + 50 000 + 18 921 = 168 921 loc
  union distincte               168 854     (67 doublons, TOUS internes aux fichiers)
  les quatre entre eux          DISJOINTS, mesure par les MEMBRES
  structure                     3 segments exactement, tous /es/trabajos…
  identifiant                   AUCUN : 0 suite de 4 chiffres, 0 UUID
  produit croise                6 714 categories x 1 306 villes = 8 768 484
  densite                       1,9 %   ->  des pages d'atterrissage, pas des annonces
/es/trabajos/madrid 403 511 o   Next.js, __NEXT_DATA__ 173 205 o
  feed.sections[2].items        48 enregistrements, type « job » 48/48
  key                           48/48 presents, 48 distincts   <- L'IDENTIFIANT
  canonicalUrl                  /es/trabajo/<role>-<key>   (trabajo SINGULIER)
  pagination.pages              20     ->  ~960 atteignables par facette
  total entier                  AUCUN dans la charge ; le titre dit « 1000+ » = PLANCHER
  salary                        present 28/48, isValid 26/48
    des 26 valides              EUR 26/26, from+to 26/26
    period                      MONTHLY 14 · YEARLY 9 · HOURLY 3
    des 2 invalides             0 portent un montant
  company.hiringManager         48/48 — name, image, lastOnline
  addressInfo.coordinates       48/48 — lat, lng   ·   ghash 48/48
  courriels · cles de contact   0 · AUCUNE
  postedSecondsAgo              73 s  ->  2 172 758 s (603,5 h)
```

**Found by the Spain pass of #949.** *The sitemap index names exactly three countries, so this card
declares `ES GB US` rather than a single country or a wildcard.*

### Every advert names a person, and no contact-shaped rule can see it

**`company.hiringManager` is present on 48 of 48**, carrying `name`, `image` and **`lastOnline`**.
*So each advert ships an individual's name, a link to their photograph, and a timestamp of when
they were last active on the platform.* **And `addressInfo` gives `lat`/`lng` and a `ghash` on 48
of 48** — a precise position per advert, which this repository already treats as not-to-be-emitted
since Batiactu.

**Meanwhile the payload holds zero e-mail addresses and not one key matching `phone`, `email` or
`tel`.** *Measured, not assumed.*

> **So a rule written around contact SHAPES — an `@`, a run of digits — finds nothing on this
> board and reports «&nbsp;nothing withheld&nbsp;», while the records carry a named person, their
> picture and their presence.** *That is the mirror of `declarer-avoir-retenu-ce-que-personne-na-depose`,
> and it is the worse half: there we over-claimed a discretion we had not exercised, here the
> output would be silent and the omission invisible.* **A withholding rule is named by FIELD here,
> never by pattern**: `company.hiringManager` whole, `addressInfo.coordinates`, `ghash`, and the
> manager's `image` URL.

*And `lastOnline` deserves its own line: it is not a contact at all, it is an activity trace about
a third party, and nothing in our doctrine names it yet.*

### The two declared sitemaps enumerate different KINDS of object

| declared sitemap | what it holds |
| :-- | :-- |
| `/sitemap.xml` | 478 `<loc>`, 477 distinct — **blog posts** (`/gb/blog/…`) |
| `/sitemaps/sitemap_index.xml` | an **index** of 32 `Positions` children, split by country |

> **The two-enumerator discipline usually asks «&nbsp;do their MEMBERS overlap&nbsp;»; here the prior
> question bites first — do they enumerate the same KIND of thing at all?** *They do not.* **A
> reading that compared the two cardinals — 478 against 32 — and took the larger would walk 478
> articles and emit zero adverts.**

### And the enumerator that does name jobs still contains no advert

**168 921 `<loc>` across the four Spanish children, 168 854 distinct, the four PAIRWISE DISJOINT**
— *all 67 duplicates lie within individual files, none across them, measured by the members and not
by the sizes.*

**Every one of the 168 854 has exactly three segments, begins `/es/trabajos`, and carries no
identifier at all.** *They are the cross product of 6 714 categories or employers by 1 306 cities —
8 768 484 theoretical cells, 1.9 % of them generated.*

**So the board's own declared enumerator contains not one advert**, and 168 854 is a count of
landing pages. *«&nbsp;A count of `<loc>` is not a count of adverts&nbsp;» has been a line here since
6 932 URLs yielded zero; this is the same fact at twenty-four times the scale, and the sitemap is
the one the host declares.*

**And its `lastmod` cannot date anything either**: all 168 921 carry 2026-10-05, the day of the
reading, exactly as the index's 32 do — *a build stamp, the same shape `hosco.md` carries.*

### What the board states, and what it does not

**There is no integer total anywhere in the payload.** *`pagination.pages` holds 20 entries and the
page's own title reads «&nbsp;1000+ ofertas de trabajo en Madrid&nbsp;».* **A floor, not a count** — the
OLX shape — **so about 960 adverts are reachable per facet and the board's size is not
established.**

*The reach is per FACET, and there are 168 854 of them with 1.9 % density, so «&nbsp;how many adverts
does this board hold&nbsp;» is not answered by any reading taken here and none is offered.*

### The salary is structured, and the board flags its own validity

**Present on 28 of 48, `isValid` true on 26** — *so `if x` would count 28, and the field is one more
specimen of «&nbsp;present is not filled&nbsp;».*

**The 26 valid ones are complete**: `currencyCode: EUR` on 26 of 26, both `from` and `to` on 26 of
26, and a `period` that is **MONTHLY on 14, YEARLY on 9 and HOURLY on 3**. *Three periods on a
single page, so a figure carried without its period is meaningless here — and `SalaryCarriesItsUnit`
is satisfied by the board's own structure rather than by a default borrowed from its client.*

**And the two invalid ones carry no amount at all.** *Which is what settles the question of whether
to honour `isValid` or second-guess it: honouring it discards nothing, and guessing would be the
only way to be wrong.*

### What an adapter would do

```
route   : http — no key, no account, no form. A facet page ships its own state.
          2 s pace (no Crawl-delay written). `/*_ext_*` is the one refused path.
walk    : the facets from the DECLARED position sitemaps (168 854 for Spain
          alone), then ?page=N to the 20 the pagination names — ~960 a facet.
          NEVER present 168 854 as an advert count; it counts landing pages.
keyed by: `key` (48/48 distinct). Address adverts by `canonicalUrl`,
          /es/trabajo/<role>-<key> — SINGULAR, one letter from the facet form.
carries : role, companyName, address (the display line), description,
          employmentType, createDate, postedSecondsAgo, and the salary WHEN
          `isValid` — with its currency AND its period, which varies per advert
no count: the board states a FLOOR («1000+»), never a total. Say so rather than
          emitting ~960 as if it were an inventory.
NEVER   : `company.hiringManager` in any part — name, image, lastOnline — nor
          `addressInfo.coordinates`, nor `ghash`. These are named by FIELD
          because no contact pattern matches them: the payload holds zero
          e-mail and no phone-shaped key, so a pattern rule would withhold
          nothing and say so.
```

### What this card does NOT say

**It does not say how many adverts the board holds, in Spain or anywhere.** *168 854 is facets, 48
is one page, 20 is the pager's reach, and «&nbsp;1000+&nbsp;» is the board's own floor — none of the four
is an inventory.* **And the field rates come from ONE facet page of 48 records**: salary filled on
28 and valid on 26, `hiringManager` on 48 of 48, coordinates on 48 of 48. *A second facet and a
second country would be the first thing to measure, and nothing here is offered as a board-wide
rate.*

**Measured 2026-10-05 by the declared client, the guard taken on each host form and each exact path
in a turn distinct from the retrieval, `bin/fetch-body.py` throughout, DNS on two public resolvers.**
*No value of any personal field was printed at any point — only counts.* *A measurement, not an
adapter.*

```
_robots.verdict('jobtoday.com')    state: read, certain: True, 204 B, 1 Disallow, crawl_delay None
GET /robots.txt                    200, 204 B, md5 9d6b7ad7e77d
GET /sitemap.xml                   200, 63 196 B, 478 <loc> — blog
GET /sitemaps/sitemap_index.xml    200, 4 610 B, 32 Positions children (us 16, gb 12, es 4)
GET /sitemaps/JobToday_Sitemap_Positions_es_{0,1,2,3}.xml   200 x4, union 168 854
GET /es/trabajos/madrid            200, 403 511 B, __NEXT_DATA__ 173 205 B, 48 items, 20 pages
```
