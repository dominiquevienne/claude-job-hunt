# Board measurement — Hosco (`www.hosco.com`): the hospitality industry's board, worldwide — **the board states 3 689 jobs in its own page data and serves 10 a page over an HTTP route that needs no key**, with a real `posted_date` per advert and a salary that names its currency AND its period; but **every advert's `url` field points at `web-hoscov2.web.svc.cluster.local`**, an internal cluster name that cannot resolve, and the declared sitemap enumerates job FACETS while no advert sitemap exists at all

<!-- verified: 2026-10-05 -->

<!-- hosts: www.hosco.com, hosco.com -->
<!-- script: none -->
<!-- countries: * -->
<!-- host-forms-basis: read — `hosco.com` and `www.hosco.com` serve the SAME 931 B rules file (md5 0695af992a50, `state: read`, `certain: True`); the addresses differ per public resolver (172.67.71.209 against 104.26.2.159) because the host sits behind a multi-edge CDN, which is not a disagreement · 2026-10-05 -->
<!-- content: measured · **3 689 jobs are stated by the board itself and 10 arrive per page: `/en/jobs` (552 026 B) ships a Next.js `__NEXT_DATA__` of 110 413 B whose `props.pageProps.initialState.jobDirectory.search` carries `count: 3689` and a `results` list of 10 — a figure that does NOT come from our extraction. THE HOST SETS ITS OWN RATE AND IT IS NOT OURS: the `*` group writes `Crawl-delay: 10`, and the file's own comment names ClaudeBot among the agents known to respect it, so ten seconds apply and not the two seconds of our courtesy; 3 689 at 10 a page is 369 pages, about an hour of walking, which is a cost to state before anyone starts. EVERY ADVERT URL IS WRITTEN ON AN UNRESOLVABLE HOST: the `url` field reads `https://web-hoscov2.web.svc.cluster.local/en/job/<slug>` on 10 of 10 records — a Kubernetes internal service name, reserved by construction and never publicly resolvable — while the page's own 31 `/en/job/...` hrefs give the real form, so an adapter builds `https://www.hosco.com/en/job/<slug>` from `slug` and never follows `url`. WHAT THE DECLARED SITEMAP DOES AND DOES NOT ENUMERATE: `/sitemap.xml` is an index of 14 children; companies and schools each get both a per-entity sitemap and a directory sitemap, and jobs get ONLY `sitemap-en-jobs-directorypages.xml` — 213 `<loc>` for 211 distinct, `/en/jobs/management` appearing three times, and `sitemap-en-jobs-jobpages.xml` answers 404 with a 95 532 B HTML body, measured rather than inferred from the index. Its 213 `lastmod` carry ONE distinct value, 2026-10-05, the day of reading: a build stamp that cannot date anything. THE FIELDS, on the ten records read: `pay_range` is PRESENT on 10 and FILLED on 3, so `if x` would count ten; the three filled ones all name currency and period (`$18-$20 USD per hour`), and one uses EN DASH U+2013 where another uses ASCII hyphen, so a split on `-` alone would miss one of the three; `posted_date` gives 10 dates and 6 distinct values spanning 2026-09-20 to 2026-10-02, so freshness is measurable per advert even though the enumerator cannot date anything; `company` and `owner` agree on 10 of 10; and there is NO contact field at all, zero e-mail and zero telephone in the records. WHAT THE RULES REFUSE, which binds every route: the `*` group closes `/_next/data/`, `*/fruitsalad/`, `*/candidates/`, `*/edit/`, `/*/newsfeed/status/*`, `/*/company/*/albums*`, `/*/member/*`, `/*/directory/members` and `/*/members*` — the people-facing paths — and seven named crawlers are refused outright while no token of this project is named anywhere. METHOD: guard on each host form and each exact path in turns distinct from the retrievals, `bin/fetch-body.py` throughout, the 404 kept only under `--allow-refusal` so its status travels in its record** · 2026-10-05 -->

<!-- witness: the board states its own total in its page data — `jobDirectory.search.count = 3689` on 2026-10-05, read from `__NEXT_DATA__` and not from any count of ours; the listing's JSON-LD carries only `BreadcrumbList` and `SearchResultsPage`, so there is no `ItemList` whose `numberOfItems` could be mistaken for a board total · 2026-10-05 -->

## Measured 2026-10-05 — the board states 3 689, serves 10 a page, and writes every advert URL on a host that cannot resolve

```
robots.txt              931 o   md5 0695af992a50, read, certain
  groupe *                      Crawl-delay: 10   <- l'allure de L'HOTE, pas la notre
                                son propre commentaire nomme ClaudeBot comme la respectant
  9 refus a *                   /_next/data/ · */fruitsalad/ · */candidates/ · */edit/
                                /*/newsfeed/status/* · /*/company/*/albums*
                                /*/member/* · /*/directory/members · /*/members*
  7 robots nommes               AhrefsBot SemrushBot Sogou Seekport PetalBot
                                Bytespider Barkrowler  ->  Disallow: /
  aucun jeton de ce projet nomme nulle part
/sitemap.xml          1 799 o   INDEX de 14 enfants
  jobs                          directorypages SEULEMENT — aucun jobpages
  companies · schools           les DEUX formes, par entite ET annuaire
  jobs-jobpages.xml             404 avec 95 532 o de HTML  (mesure, pas deduit)
  jobs-directorypages.xml      31 721 o, 213 <loc> / 211 distincts
                                /en/jobs/management x3
                                213 lastmod, UNE seule valeur : 2026-10-05
/en/jobs             552 026 o  Next.js, __NEXT_DATA__ 110 413 o
  search.count                  3 689        <- le board l'annonce LUI-MEME
  search.results                10 par page  ->  369 pages a 10 s = ~1 h
  url (10/10)                   web-hoscov2.web.svc.cluster.local   NE RESOUT PAS
  slug                          royal-caribbean-group/bar-supervisor
  hrefs /en/job/... du HTML     31, la forme REELLE
  pay_range                     present 10/10, REMPLI 3/10
  posted_date                   10 dates, 6 distinctes, 2026-09-20 -> 2026-10-02
  company == owner              10/10
  contacts                      AUCUN champ, 0 courriel, 0 telephone
```

**Found by the Spain pass of #949, and it is not a Spanish board.** *Its own filter list
enumerates **212 countries** with ISO codes and place identifiers, Spain being one entry among
them, so `countries: *` is what this card declares.* **Declaring `ES` would have made a country
ratio move by misdescribing the board**, and the Spain page keeps it as what it is: a worldwide
hospitality board with six Spanish city facets (`barcelona`, `girona`, `ibiza`, `madrid`, `palma`,
`sevilla`). *There is no country-level `/en/jobs/in/spain`, so a Spain-only count is not available
in one request and none is claimed here.*

### The host sets the rate, and it names us as one who respects it

**`Crawl-delay: 10` under `User-agent: *`** — and the file carries a comment of its own saying the
directive is *"Known to be respected by: Bingbot, Yandex, ClaudeBot (Anthropic), and most compliant
SEO/AI bots"*.

> **So the two seconds of our own courtesy are not the figure here: ten is.** *The rules name us
> among those expected to honour it, which makes the delay an expectation and not a hint* — and
> `Crawl-delay` has been a directive and not a remark in this repository since `ejob.az`.

**The cost follows from it and belongs in the card rather than in a surprise:** *3 689 stated at 10
a page is 369 pages, and 369 pages at ten seconds is about an hour of walking.* **A board whose
total is known in advance lets that cost be stated before anyone starts.**

### Every advert URL is written on a host that cannot resolve — and the real one is next to it

**`url` reads `https://web-hoscov2.web.svc.cluster.local/en/job/<slug>` on 10 of 10 records.**
*`svc.cluster.local` is Kubernetes' internal service domain: it is not merely unregistered, it is
reserved for cluster-internal resolution and cannot answer a public query by construction.*

**The real address is beside it:** *the same page carries 31 `href="/en/job/..."` links, and `slug`
holds `royal-caribbean-group/bar-supervisor`.* **So an adapter composes
`https://www.hosco.com/en/job/<slug>` and never follows `url`.**

> *This is the Emprego Xunta shape — `speg15.xunta.gal`, a host the sitemap named and no resolver
> knew — and it is a cleaner specimen: there the leaked name was merely absent from DNS, here it is
> a reserved internal domain.* **Two boards in one pass whose own enumerator addresses an
> unreachable host, and in both the correct path was already present in the same payload.**

### The declared sitemap enumerates facets, and the asymmetry is the tell

| child | per-entity sitemap | directory sitemap |
| :-- | :-- | :-- |
| companies | `companypages` ✓ | `directorypages` ✓ |
| schools | `schoolpages` ✓ | `directorypages` ✓ |
| **jobs** | **none** | `directorypages` ✓ |

**The index names job DIRECTORY pages and no advert at all** — 66 `/en/jobs/in/<place>`, 33
`/en/jobs/at/<employer>`, and department facets. *The asymmetry is readable from the index alone,
before a single child is fetched: two of the three families get both forms and jobs get one.*

**And the missing one was measured, not assumed:** `sitemap-en-jobs-jobpages.xml` **answers 404
with a 95 532 B HTML body** — the site's own page under a 404 code, which `fetch-body.py` refused
to save as content. *A readable body is not an answer; the code decides.*

**Two defects of the file itself**: *213 `<loc>` for 211 distinct — `/en/jobs/management` appears
**three times*** — and **213 `lastmod` carrying a single distinct value, 2026-10-05, the day of the
reading**.

> **A `lastmod` on 100 % of rows, all identical and equal to today, is a BUILD stamp.** *It is the
> most complete-looking and least informative form this field takes* — and it is the fifth distinct
> way an offers sitemap has failed to be a witness in this campaign: **Manfred** spans six years,
> **Portalento** carries none at all, **Feina Activa** declares one that 404s, **Emprego Xunta**
> serves an undeclared one naming an unresolvable host, and **Hosco** stamps every row with the day
> it was generated.

*The record repairs it:* **`posted_date` gives 6 distinct values over 2026-09-20 → 2026-10-02 on
ten adverts.** *So freshness is measurable per advert while the enumerator cannot date anything —
the Portalento shape, on a different field.*

### `pay_range` is present on ten and filled on three

**`if x` would count ten.** *This is the live form of the rule this repository paid for: a field
PRESENT is not a field FILLED, and `withheld_fields` written on truthiness claims a discretion
nobody exercised.*

**And the three that are filled name their unit completely** — `$18-$20 USD per hour`,
`$18 USD per hour`, `$22–$24 USD per hour`: *currency and period, on the figure itself.* **That
satisfies `SalaryCarriesItsUnit` without any default having to be borrowed from the board's
client**, which is rare enough here to record.

**One of the three uses EN DASH U+2013 where another uses ASCII HYPHEN-MINUS.** *Same board, same
field, same page.* **A range split on `-` alone would silently drop one of three** — *the "a string
has several forms at the point of call" trap, measured rather than imagined, and the character is
what it is regardless of how small the sample is.*

### What an adapter would do

```
route   : http — no key, no account, no form. `/en/jobs` ships the page's own
          state; the paging parameter is to be established on the second page,
          which this measurement did not take.
RATE    : 10 s, written by the host under `*`. Not 2 s. State the ~1 h for a
          full walk before starting it, and bound it with --max-pages.
witness : `jobDirectory.search.count` — the board's own total. Print
          «N emitted, the board states 3689» so a shortfall is visible.
address : compose https://www.hosco.com/en/job/<slug>. NEVER the `url` field:
          it names an internal cluster host on every record.
carries : title, company, displayed_location, excerpt, posted_date, types,
          and pay_range WHEN FILLED — floored, never on truthiness (3 of 10)
          and split on an EN DASH as well as a hyphen
NEVER   : the refused paths — `*/candidates/`, `*/member/*`, `*/members*`,
          `*/directory/members` are closed in writing to `*`, so they are closed
          by every route. The records carry no contact to withhold, which is
          worth asserting rather than assuming on a wider sample.
```

### What this card does NOT say

**It does not say 3 689 adverts were read, nor that the fields above hold beyond ten records.** *Ten
is the first page; `pay_range` filled on 3 of 10 and `company == owner` on 10 of 10 are observations
on that page and not rates for the board.* **And one of the two employers on it — «&nbsp;International
Recruitment Exchange Services&nbsp;», on 3 of the 10 — is a recruitment agency naming itself**, which
is not the Portalento defect (where the placer occupied the employer field on every advert) but is
the same question, to be measured on a sample before an adapter emits an employer.

**Measured 2026-10-05 by the declared client, the guard taken on each host form and each exact path
in a turn distinct from the retrieval, `bin/fetch-body.py` throughout at the host's written 10 s,
DNS on two public resolvers.** *A measurement, not an adapter.*

```
_robots.verdict('www.hosco.com')   state: read, certain: True, crawl_delay: 10.0, group '*'
GET /robots.txt                    200, 931 B, md5 0695af992a50
GET /sitemap.xml                   200, 1 799 B, index of 14
GET /sitemaps/sitemap-en-jobs-directorypages.xml   200, 213 <loc>, 211 distinct
GET /sitemaps/sitemap-en-jobs-jobpages.xml         404, 95 532 B  (not saved as content)
GET /en/jobs                       200, 552 026 B, __NEXT_DATA__ 110 413 B, count 3689
```
