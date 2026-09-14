# Board measurement — Barona (`www.barona.fi` → `www.baronacareers.com`, Finland): the staffing network's postings live on a careers host whose rules open and whose transport answers the 25-byte provider 403 to this client on every path — a browser candidate, not measured (no browser on the day); the marketing site itself lists no posting a client may read

<!-- verified: 2026-09-14 -->

<!-- hosts: www.barona.fi, barona.fi, www.baronacareers.com -->
<!-- script: none -->
<!-- countries: FI -->
<!-- content: measured · **no posting readable over HTTP by this client**: `www.barona.fi` (WordPress; rules 205 B — `Disallow: /wp-json/`, `/?rest_route=`; five sitemaps, none of jobs) serves `/tyopaikat/` (200, 231 002 B) as a page whose job widget is filled client-side and whose empty state says «Kaikki Baronan työpaikat löytyvät Barona Careersista» — the postings are on `www.baronacareers.com`; that host's rules (219 B) open everything but `/ahoy/`, `/api/v1/browse/events/`, `…/jobs/*/viewed` and `?from_apply=`, name `sitemap.xml.gz` and refuse `trovitBot` by name — **and its transport answers 403, 25 B, `md5 9ccabba20b9f4ec7d18bd6644579e5bf` to this client on `/`, `/fi/fi/job`, `/api/v1/browse/jobs` and `/sitemap.xml.gz`, twice on the root at the same fingerprint (02:52–02:53 UTC): the provider's static block seen on ten other hosts, not a challenge and not the editor's page** · 2026-09-14 -->
<!-- witness: none — the marketing site prints no count and the careers host answers nothing this client can read; the measurement is the set of addresses, each with its code, size and md5 · 2026-09-14 · **browser, 2026-09-14 09:1x UTC: `www.baronacareers.com/fi/fi/job` served to a connected tab — a sliding pager of 10 (`?page=N`, no total printed), 29 pages, 283 rows, 277 distinct slugs (6 repeated across adjacent page boundaries on two identical walks — a pager unstable on ties), the site states no count; each ad page carries a JobPosting with `identifier.value` as the key** -->
<!-- route: browser · 277 · 2026-09-14 -->

**Barona is Finland's largest staffing and recruitment group; its
postings are served by its own careers portal, `www.baronacareers.com`,
which refuses this client at the transport with the provider's 25-byte
403 while its rules open the path — the shape the doctrine of
2026-09-07 names a browser candidate.** Issue #377. Measured 2026-09-14
02:51–02:53 UTC by the declared client, the guard on the exact path;
**the browser route is not measured — no browser was attached on the
day — and the card says so rather than guess.**

## What each host serves

```
barona.fi/robots.txt                     301 → www.barona.fi/robots.txt
www.barona.fi/robots.txt                 200, 205 B — Yoast block: User-agent: *: Disallow /wp-json/, /?rest_route=; Sitemap: /sitemap_index.xml
GET https://www.barona.fi/sitemap_index.xml   200, 929 B — page, barona_article, barona_press_release, barona_case, barona_offices: no job sitemap
GET https://www.barona.fi/                200, 299 485 B — the marketing site; 110 links under /tyopaikat/ (sector pages), 12 to www.baronacareers.com
GET https://www.barona.fi/tyopaikat/      200, 231 002 B — a widget configured in the page («loadMoreButtonText», «noJobsFoundWithFiltersBtnUrl»: https://www.baronacareers.com/fi/fi/job), filled client-side; not one posting in the markup
www.baronacareers.com/robots.txt         200, 219 B — User-agent: *: Disallow /*?*from_apply=, /ahoy/, /api/v1/browse/events/, /api/v1/browse/jobs/*/viewed; Sitemap: /sitemap.xml.gz; trovitBot: Disallow /
GET https://www.baronacareers.com/                       403, 25 B, md5 9ccabba20b9f4ec7d18bd6644579e5bf
GET https://www.baronacareers.com/fi/fi/job              403, 25 B, the same
GET https://www.baronacareers.com/api/v1/browse/jobs     403, 25 B, the same   (the browse API the rules leave open)
GET https://www.baronacareers.com/sitemap.xml.gz         403, 25 B, the same
GET https://www.baronacareers.com/  (again)              403, 25 B, the same — a static body, not a rendered challenge
```

**The careers host's rules open the list, the browse API and the
sitemap; its transport refuses this client on all of them with the
provider's static 403** — the fingerprint `9ccabba20b9f` measured on
`jobstore.com`, `www.hays.fr`, `kariera.mk`, `sptojobslink.com`,
`tala-com.com`, `gallito`, `tecoloco`, `vacaturebank.sr`, `emploi.ma`,
`saplic` before it: a provider default, not a decision the editor wrote
on this host. Under the doctrine of 2026-09-07 that is the case for the
browser — and a browser was not available on the day, so the route is
**named, not measured**. The marketing site offers no second road: its
job widget is filled from `/wp-json/` (refused in writing) or from the
careers host (refused at the transport), and its sitemaps carry pages,
articles, press releases, cases and offices, no postings.

## What would settle it

- **A tab on `https://www.baronacareers.com/fi/fi/job`** — if the list
  renders, the route is `browser`; the page's own count (if printed)
  and the `api/v1/browse/jobs` answer from the tab would be the
  witness, as on `cvonline-lt.md`.
- **The provider's block lifting** — the md5 changing on the root would
  be the first sign; the rules already open the path.

## 2026-09-14 — measured, no adapter

No script: nothing is served to this client on either host that a
script could render (#404). The browser candidate is measured below
(`route: browser · 277 · 2026-09-14`). What replaces it for a Finnish search today:
Duunitori (`duunitori.md`), Jobly (`jobly.md`), Kuntarekry and
Valtiolle (`kuntarekry.md`, `valtiolle.md`), Työmarkkinatori
(`tyomarkkinatori.md`) — and Barona's postings appear on some of them
under Barona's name.

## Browser reading, 2026-09-14 09:14–09:21 UTC (#377)

The extension answered this session, so the candidate was measured from
a connected tab — the same path the client is refused on:

```
www.baronacareers.com/fi/fi/job          served — «Avoimet työpaikat», 10 cards a page, a sliding pager «Edellinen 1 2 3 Seuraava» (?page=N), no total printed anywhere on the page
?page=2 … ?page=28                       10 rows each; ?page=29: 3 rows and no «Seuraava»; ?page=30, 35, 40: 0 rows
the walk (twice, identical)              283 rows, 277 distinct slugs; 6 slugs repeated on adjacent pages (3/4, 5/6, 5/6, 16/17, 17/19, 19/20): a pager unstable on ties, the same six both times
the list's JSON-LD                       an ItemList of 10 (`numberOfItems`, name, url /fi/fi/jobs/<slug>) per page
the ad /fi/fi/jobs/<slug>                200, ~93 KB — a JobPosting: identifier {Barona Careers, 97757}, datePosted, validThrough, description, employmentType, educationRequirements, experienceRequirements, industry, skills, hiringOrganization (the client — «Rittal Oy» — or a Barona company), jobLocation with postcode; the page text names the consultant with an e-mail («Lisätietoja tästä työpaikasta antaa …») — never to be emitted
```

**`route: browser · 277 · 2026-09-14`.** The site states no count a
reader can compare to; 277 distinct over 29 pages is the walk's own
figure, and the six boundary repeats say the true number is 277 or a few
more. What an adapter would do from a tab: the `?page=N` walk until
«Seuraava» disappears, the ad's JobPosting by `identifier.value`, the
consultant's line withheld whole. Not written here — a browser adapter is
a procedure a session follows, and the card is what it follows.

