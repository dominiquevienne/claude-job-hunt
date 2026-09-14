# Board measurement — Grafton Slovakia (`www.grafton.sk`): the recruiter's list is a Vue app querying an Elasticsearch index on a third host with a read-only login the page hands every visitor — a credential that is not the user's, not used; the sitemap the rules name is stale (2023-09-05) and its newest job archived — no adapter, and the owner's call named

<!-- verified: 2026-09-14 -->

<!-- hosts: www.grafton.sk, search.skinner.freely.agency -->
<!-- script: none -->
<!-- countries: SK -->
<!-- content: measured · **no live posting reachable without a credential**: `www.grafton.sk/robots.txt` (200, 1 744 B, Drupal's default under `*`, `/search/` and the account pages refused) names `/grafton_sk/sitemap.xml` — an index dated **2023-09-05** (6 pages) whose job rows are 108 `/en/jobs/` rows on page 1 dated 2020–2021, zero job rows on page 6; the listing `/job-search` (200) is a Vue app (`#vue-jobs-app`, `data-domain="grafton_sk"`) whose `data-config` carries the search backend — `https://search.skinner.freely.agency`, index `elasticsearch_index_grafton_grafton`, **and a Basic-auth user and password (`roelastic`) the page hands to every visitor** — and the server renders not one posting; a job page (`/cs/jobs/<slug>`, 200) is server-rendered with labelled fields (Lokalita, Obor, Druh pozice, Mzda, Zveřejněno, Referenční číslo) and a «Kontaktní osoba» block naming the consultant with a `tel:` link — read on two archived ones — read by the declared client, the guard on the exact path, 03:1x–03:2x UTC · 2026-09-14 -->
<!-- witness: none — the count lives in the Elasticsearch answer, behind the credential; the sitemap's rows are dated and archived; the measurement is the set of addresses read, each with its code and size · 2026-09-14 -->
<!-- route: none · fermé toutes voies, navigateur compris — validé par le propriétaire le 14.09.2026 (verbatim : « 5. considérer le site comme totalement fermé (y compris browser) ») — measured: the only live inventory is an Elasticsearch index on a third-party host reached with a login embedded in the page — authenticating with a credential that is not the user's is not a road the plugin takes without the owner's decision; the sitemap is stale and its newest job archived; the job pages are readable one by one but nothing names the live ones · 2026-09-14 -->

**Grafton is Gi Group's recruitment and staffing brand in Central Europe;
its SK front lists its openings through a search backend the plugin
cannot reach without a password — and the rest of what it publishes is
stale.** Issue #348. Measured 2026-09-14 03:1x–03:2x UTC by the declared
client, the guard on the exact path. Profesia, Služby zamestnanosti and Práca za rohom are read; this one is not, and the
card says why.

## What the host serves

```
www.grafton.sk/robots.txt                       200, 1 744 B — Drupal's default under *: Disallow /core/, /profiles/, /admin/, /search/, /user/*; Sitemap: /grafton_sk/sitemap.xml
GET https://www.grafton.sk/grafton_sk/sitemap.xml            200 — Simple XML Sitemap index, 6 pages, lastmod 2023-09-05
GET https://www.grafton.sk/grafton_sk/sitemap.xml?page=N     200 — pages, articles, and /cs|en|sk/jobs/<slug> rows with a per-node lastmod: 108 `/en/jobs/` rows on page 1 dated 2020–2021, zero job rows on page 6
GET https://www.grafton.sk/job-search                              200 — <div id="vue-jobs-app" data-domain="grafton_sk" data-config="{elastic: {url: https://search.skinner.freely.agency, index: elasticsearch_index_grafton_grafton, auth: {user, password}}, …}">; <noscript>job search page doesn't work properly without JavaScript</noscript>; not one posting rendered
the bundle (/sites/default/files/js/js_FsYOBn…js, 932 601 B)   this.elastic(config.elastic.elastic.url).post("/" + index + "/_search", query, {auth: {username, password}})   — the list, the count and the facets all come from there
GET https://www.grafton.cz/cs/jobs/team-leader-vyroby-mzda-az-70-000-kc-motivacni-bonus   200, 69 083 B — the sitemap's newest job: «Tato pozice již není aktuální», Zveřejněno 2026-03-10; fields, salary «50 000 - 60 000 Kč», Kontaktní osoba with tel:
```

**Three facts, and none of them opens a road:**

1. **The list is an Elasticsearch query to a third host, authenticated.**
   The page embeds a read-only user and password and the Vue app sends
   them as Basic auth on every search. Every visitor's browser does this;
   a script doing it would be authenticating with a credential that is
   not the user's — the plugin never logs in, and its API keys are the
   user's own (`~/.<board>.env`). **Whether a login the site hands to
   every visitor counts as the site's permission is the owner's
   decision, not this card's** — named here so the question is not
   re-derived.
2. **The sitemap is stale.** Its index is dated 2023-09-05; the newest job
   row it names answers «archived». Reading its `/jobs/` rows one by one
   would render only what the site has retired.
3. **The job page is readable and complete** — labelled fields, salary,
   the reference number, the description — but nothing readable names
   which pages are live: a script over the sitemap would render nothing
   current (#404).

## What would settle it

- **The owner's decision on the embedded login** — if «the site's own
  read-only search account, handed to every visitor» is deemed the
  site's permission, an adapter posts the Vue app's own query to
  `elasticsearch_index_grafton_grafton` with `domain: grafton_sk` and
  reads `hits.total` as the witness; a `boards.grafton.<…>` key would
  carry the choice, as `override_robots` does elsewhere.
- **A fresh sitemap** — the index's lastmod moving past 2023-09-05.
- **A tab on `/job-search`** — the browser route runs the same app with the
  same credential; it measures the count but does not change the
  question.

## 2026-09-14 — measured, no adapter

Route none, dated and motivated: the live inventory sits behind a
credential the plugin does not use on its own authority, and the open
roads (sitemap, job pages) render only archived postings. The Czech and
Slovak fronts share the backend, the index and the login (`data-domain`
tells them apart) — one decision covers both (`grafton-cz.md`,
`grafton-sk.md`).

## 2026-09-14 04:4x UTC — the owner's decision, and this card's verdict is his

**fermé toutes voies, navigateur compris — validé par le propriétaire le 14.09.2026 (verbatim : « 5. considérer le site comme totalement fermé (y compris browser) »)** — relayed verbatim by the pilot (#348). What was measured above is
unchanged; what changes is who says «closed»: until this line the card
could only say what it had read and that the verdict was the owner's to
give (CLAUDE.md §2 sexies) — he has given it. The `route: none` line
leads with it, dated, so the Atlas and the country page (#404: a card
declaring `route: none` is «non faisable», excluded from the feasible
denominator) read a decision and not a measurement. Closed on every road, the browser included: the live inventory sits behind a credential that is not the user's, and the owner has ruled that no road is taken — this card carries no browser candidacy.
