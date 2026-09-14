# Board adapter — StartupJobs (`www.startupjobs.cz`, Czechia): the tech and start-up board, read through its offers sitemap (392 ids on 2026-09-14) and each offer page's own server-rendered state — because the listing's API lives on `back.startupjobs.cz`, which refuses everything in writing; no count stated on a page this client may read, and the adapter says so

<!-- verified: 2026-09-14 -->

<!-- hosts: www.startupjobs.cz, startupjobs.cz, back.startupjobs.cz -->
<!-- script: startupjobs.py -->
<!-- host-forms: www.startupjobs.cz -->
<!-- host-forms-basis: read — the sitemap's rows and the page's canonical are on `www.startupjobs.cz`; `startupjobs.py` names it as a literal, and names `back.startupjobs.cz` only to refuse it before the rules are even asked · 2026-09-14 -->
<!-- countries: CZ -->
<!-- content: measured · **`sitemap/offers.xml` (200, 48 488 B) names 392 `/nabidka/<id>/<slug>` offers, no lastmod (414 on 2026-09-01); the listing `/nabidky` (200, 150 886 B) is a Nuxt page that renders no offer on the server — its list is fetched from `https://back.startupjobs.cz` (`apiSearchOffers…` queries, `baseUrl` in the page's own state), whose rules are `User-agent: * / Disallow: /`: refused in writing, never sent; the offer page (200, 152 689 B) is server-rendered with the whole offer object in its `__NUXT_DATA__` payload (54 144 characters, the `apiOffersIdGet` query) — company, salary «75 000–112 000 CZK monthly», locations, collaborations, seniorities, skills, languages, 25 benefits, description; 3 read live by request** — read by the declared client, the guard on the exact path (`www.` rules 143 B: `Allow: /`, `/admin/` and `/superadmin/` refused); **the offer object carries no contact field; the text is scrubbed of e-mail addresses and Czech numbers all the same; the employer's `externalLink` is emitted and never fetched** · 2026-09-14 -->
<!-- witness: none the site states on a page this client may read — the listing's count is on the refused host; the adapter prints the sitemap's row count as the inventory and never as the site's statement, counts the offers gone since the sitemap, and exits 6 on a page without an offer block · 2026-09-14 -->

**StartupJobs is the Czech tech and start-up board — Applifting, CDN77,
scale-ups and studios — a segment Jobs.cz, Prace.cz and the Úřad práce
carry only diluted: 392 offers named by its sitemap on the day.** Issue
#354. Measured 2026-09-14 02:45–02:48 UTC by the declared client, the
guard on the exact path before each request.

## Two hosts, one of which says no

```
www.startupjobs.cz/robots.txt              200, 143 B — User-agent: *: Allow: /, Allow: /admin/onboarding, Disallow: /admin/, /superadmin/; Sitemap: /sitemap_index.xml
back.startupjobs.cz/robots.txt             200 — User-agent: * / Disallow: /         ← the API host: everything refused in writing
GET https://www.startupjobs.cz/sitemap_index.xml   200, 601 B — blog, categories, companies, offers, quiz-fields
GET https://www.startupjobs.cz/sitemap/offers.xml  200, 48 488 B — 392 <loc> https://www.startupjobs.cz/nabidka/<id>/<slug>, no lastmod
GET https://www.startupjobs.cz/nabidky             200, 150 886 B — «Nabídky práce», not one /nabidka/ link: the list is fetched client-side from back.startupjobs.cz
GET https://www.startupjobs.cz/nabidka/24290/fullstack-agentic-engineer   200, 152 689 B — the text rendered; __NUXT_DATA__ carries the offer object (query apiOffersIdGet, baseUrl back.startupjobs.cz, path.id 24290)
```

**The page calls `back.startupjobs.cz` for its list and for the offer;
that host's rules refuse everything, and the adapter never sends a
request there — `gate()` refuses the host before the rules are even
asked (exit 7).** What the adapter reads is what `www.` serves: the
offers sitemap, and the offer page whose payload already holds the
object the API would have answered. The listing's count — «N nabídek»
— is the API's and is not read: **the note prints the sitemap's 392 as
the inventory and never as the site's statement.**

## The three commands

```
startupjobs.py sitemap
[startupjobs] 392 offer id(s) in the offers sitemap (0 other rows set aside) — the site states no count on a page this client may read (its count is on back.startupjobs.cz, refused in writing): the sitemap is the inventory, not the site's statement.
startupjobs.py list --limit 3
[startupjobs] 3 offer(s) read from their pages, 0 gone since the sitemap, of the 392 the offers sitemap names — 3 read by request (--limit), not a shortfall; the site states no count this client may read.
startupjobs.py ad --url https://www.startupjobs.cz/nabidka/24290/fullstack-agentic-engineer
{"id": "24290", "title": "🤖Fullstack Agentic Engineer", "employer": "Applifting", "employer_type": "start", "employer_areas": ["Technologie", "Zakázkový vývoj", "Umělá inteligence"], "field": "Vývoj",
 "locations": [{"name": "Praha, Česko", "place": "Praha", "region": "Hlavní město Praha", "country": "Česko", "type": "place"}], "collaborations": ["hybrid", "onsite", "employment", "freelance"], "shifts_hours_month": [160], "seniorities": ["medior", "senior"],
 "salary_min": 75000, "salary_max": 112000, "salary_currency": "CZK", "salary_unit": "monthly", "salary_unit_stated": true, "skills": [{"name": "JavaScript", "type": "required"}, …], "languages": [{"name": "angličtina", "level": 2}, …], "benefits": ["13. a 14. plat", …],
 "created": "2020-06-22", "updated": "2026-09-13", "promoted_since": "2026-09-13", "status": "published", "external_link": null, "summary": "…", "description": "…", "contacts_withheld": true}
```

`sitemap` is two requests; `list` reads the first N offers of the
sitemap from their pages (20 unless `--limit`, 2 s apart) and counts
the ones gone since the sitemap was written; `ad` reads one. **The
payload is devalue's flat array — every value an index, `Reactive` and
`Ref` wrappers around the object — unwrapped by the adapter; a page
without the offer block exits 6.** The record is the object's own
fields, Czech text first: `name`, `company` (name, slug, `type`
start/scale/corporate, areas, verified), `salary` with its `measure` (a
period — `salary_unit_stated` true only with a figure), `locations`
(place, region, country, `type` place/remote), `collaborations`,
`shifts` (hours a month), `seniorities`, `skills` (required /
nice-to-have), `languages` (level), `benefits`, the field, the three
dates, `status`, `externalLink` — **the employer's own application page,
emitted and never fetched** —, `descriptionShort` and `description`
(HTML → text). **No contact field exists in the object; description and
summary are scrubbed of e-mail addresses and Czech telephone numbers all
the same; `contacts_withheld` on every record.**

## Configuration

```yaml
boards:
  startupjobs:
    enabled: true
    limit: 50             # list: offers read from their pages, 2 s apart
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `limit` | no | 20 by default; the sitemap named 392 on the day |

No credentials, no browser, no login. `sitemap` is two requests; `list`
is two plus one an offer.

## What is not established

- **The site's own count** — on the refused host; not read. The sitemap's
  392 against the country page's 414 of 2026-09-01 is two readings of
  the same file, not a statement.
- **The order of `offers.xml`** — the first rows on the day were 2020
  ids (long-running offers re-promoted); no lastmod to sort by.
- **Filters** — the site's search is the refused API; `list` reads the
  sitemap in its order.
- **The English front** (`www.startupjobs.com`, the same tenant per the
  page's site config) — not read; the object carries `en` texts beside
  `cs` and the adapter takes the Czech.

## 2026-09-14 — shipped

`sitemap`: 392 ids; `list --limit 3`: three offers read from their
pages, salaries and locations resolved, no address or number in the
output; `ad`: one. Three tests; six mutations on a detached worktree
(`python3 -B`), six red — the refused-host guard dropped, a wrapper not
unwrapped, a repeated id counted twice, the salary period taken as
stated without a value, the e-mail not scrubbed, a gone offer counted
as read.
