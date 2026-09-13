# Board measurement — Intermediair (`www.intermediair.nl`, Netherlands): DPG Media's second board on the same template as Nationale Vacaturebank — 2 495 in a fresh sitemap, 19 of 20 served, a `--host` away from an adapter

<!-- verified: 2026-09-13 -->

<!-- hosts: www.intermediair.nl, intermediair.nl -->
<!-- script: none -->
<!-- countries: NL -->
<!-- content: measured · **2 495 distinct advertisement uuids in the declared sitemap (`/cdn/sitemaps/vacature.xml` → one file, index lastmod 2026-09-13T15:21:17Z, no `<lastmod>` per entry) — and of 20 drawn at random, 19 served with a JobPosting whose validThrough is 2026-09-26 … 2026-11-11, 1 answered 404**; `bin/fetch-body.py` and a 20-page sample by the declared client, 16:16–16:17 UTC; the site states no figure by HTTP — the same DPG template as `nationalevacaturebank.md`, the search refused in writing to `*` · 2026-09-13 -->
<!-- witness: the sample — 19 of 20 served open, the index's lastmod an hour before the read; no stated figure to compare, and none copied from a tab (the extension did not reach this host on 2026-09-13) · 2026-09-13 -->

**No `host-forms:` is declared, because no script ships to reach a form**
— the pages and every `<loc>` carry `www.`; the sitemap index sends its one
file to the apex `intermediair.nl`, and the guard was taken there on the
exact path (`allowed('intermediair.nl', '/cdn/sitemaps/vacature/vacature-1.xml')`
→ True, certain). The adapter that ships declares both.

**The sister board of Nationale Vacaturebank, same group, same rules
file to the line, same sitemap layout, same JobPosting — measured by the
declared client on 2026-09-13 16:15–16:17 UTC, the guard on the exact
path first, and served on every path read.** Not built: per #291 an
adapter has its issue before its first line; this card is the measure
that issue cites.

## Rules — the same file as `www.nationalevacaturebank.nl`

```
robots.txt   200, 3 735 B — `User-agent: *`: Disallow /vacature/zoeken?* · /vacature/uitgebreid-zoeken · /vacatures/*?page= · /vacatures/*?*&page= · (accounts, apply, cv, utm/gclid variants …)
             `User-agent: ClaudeBot`: Disallow /          <- `Claude-User` under `*` (2026-09-07)
             AdsBot-Google, AdsBot-Google-Mobile, Twitterbot: Allow /vacature/zoeken?*
             nine `Sitemap:` lines — /cdn/sitemaps/vacature.xml is the advertisements; the others are landing pages (topics, dco-titel, werkgever, plaats, salary, gemeente, trefwoorden)
identity("/vacature/<uuid>/<slug>")   http, claude-user — certain: True
```

**Every queried or paginated listing is refused to `*`** — as on the
sister host, the search is never taken, and the route is the sitemap.

## Transport and the sample

```
GET /cdn/sitemaps/vacature.xml                              200, 3xx B — ONE <sitemap>, ONE <loc>, lastmod 2026-09-13T15:21:17Z, the file on the apex host
GET intermediair.nl/cdn/sitemaps/vacature/vacature-1.xml    200 — 2 495 <loc>, all /vacature/<uuid>/<slug> on www., 2 495 distinct uuids, no <lastmod>
20 drawn at random (seed 13), 1.5 s apart, 16:16–16:17 UTC:  19 → 200 with a JobPosting, validThrough 2026-09-26 … 2026-11-11 (all ahead)  ·  1 → 404
```

A JobPosting per served page, the sister's shape: title, datePosted,
validThrough, employmentType (a list — `["FULL_TIME", "PART_TIME"]` on the
one read in full), hiringOrganization, jobLocation {locality, region, NL,
postalCode}, baseSalary {EUR, 6000–8000, MONTH}, industry, directApply.

**The difference from the sister is the freshness**: 1 gone of 20 here
against 16 of 40 there, and the index's `lastmod` is the day's, not eleven
days old. Twenty draws give a proportion, not a count.

## What the adapter would be

`nationalevacaturebank.py --host www.intermediair.nl` — the same routes
(index → files on the apex host → uuids; `--sample K`; `ad` from the
JobPosting), keyed `intermediair:<uuid>`, `countries: NL`. Nothing on this
host needs a different reader. **Issue: see the `adapter` label** (opened
2026-09-13 with this card).

## What is not established

- **A count the site states** — none by HTTP; a tab was not opened on
  this host.
- **How the 2 495 relate to the sister's 89 733** — different boards of
  one group; whether advertisements are shared was not read.
- **The one 404** — a uuid in a file written an hour earlier.
