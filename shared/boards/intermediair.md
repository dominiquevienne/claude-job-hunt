# Board adapter — Intermediair (`www.intermediair.nl`, Netherlands): DPG Media's second board on the same template as Nationale Vacaturebank — `nationalevacaturebank.py --host intermediair`, 2 160 in the sitemap on the 14th, 10 of 10 sampled served, the recruiter's address no longer a field

<!-- verified: 2026-09-14 -->

<!-- hosts: www.intermediair.nl, intermediair.nl -->
<!-- script: nationalevacaturebank.py -->
<!-- host-forms: www.intermediair.nl, intermediair.nl -->
<!-- host-forms-basis: read — `nationalevacaturebank.py:BOARDS["intermediair"]` is `www.intermediair.nl`; the sitemap index sends its one file to the apex `intermediair.nl` and the guard is taken there on the exact path; every `<loc>` and every page carries `www.` · 2026-09-14 -->
<!-- countries: NL -->
<!-- content: measured · **2 160 distinct advertisement uuids in the declared sitemap (`/cdn/sitemaps/vacature.xml` → one file on the apex host, index lastmod 2026-09-14T00:21:16Z) — and of 10 drawn spread over the file, 10 served with a JobPosting whose validThrough is on or after the day**; `nationalevacaturebank.py sitemap --host intermediair --sample 10` by the declared client, 00:36–00:37 UTC (2 495 and 19 of 20 on the 13th at 16:16 UTC); **the site states no figure by HTTP** — its «2.361 banen» (a tab, 16:19 UTC on the 13th) is rendered from the API behind the search the rules refuse, never copied into the adapter; the same DPG template as `nationalevacaturebank.md`, the same rules to the line · 2026-09-14 -->
<!-- witness: the sample — 19 of 20 served open (a proportion that predicts ≈ 2 370 live of 2 495, and the tab's «2.361» sits inside it), the index's lastmod an hour before the read; the tab's figure is read once, never copied into an adapter · 2026-09-13 -->

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
days old. Twenty draws give a proportion, not a count — 19 / 20 of 2 495
is ≈ 2 370, and the search page's «2.361 banen» (tab, 16:19 UTC) sits
inside that: the file and the site agree once the gone are taken out.

## What the adapter would be

`nationalevacaturebank.py --host www.intermediair.nl` — the same routes
(index → files on the apex host → uuids; `--sample K`; `ad` from the
JobPosting), keyed `intermediair:<uuid>`, `countries: NL`. Nothing on this
host needs a different reader. **Issue: see the `adapter` label** (opened
2026-09-13 with this card).

## What is not established

- **A count the site states by HTTP** — none; «2.361 banen» is the tab's
  reading at 16:19 UTC, from the API behind the refused search.
- **How the 2 495 relate to the sister's 89 733** — different boards of
  one group; whether advertisements are shared was not read.
- **The one 404** — a uuid in a file written an hour earlier.

## 2026-09-14 — shipped (#295): `--host intermediair`

`nationalevacaturebank.py sitemap --host intermediair [--limit N]
[--sample K]` and `ad --url <www.intermediair.nl/vacature/<uuid>/<slug>>`
— the board's key is read off the address. **The same script**: the
index is asked on the named host, the file on the apex host is guarded on
its exact path, `source` and `ledger_id` carry `intermediair`, and a
file that named the sister's host would yield no row (a fault, not a
row). Measured 2026-09-14 00:36–00:37 UTC: **2 160 distinct uuids** (335
fewer than the 13th — the file is fresh, its lastmod fifteen minutes
before the read), **10 of 10 sampled served open**; `ad` on one.

**A correction to the sister's adapter, shipped in the same PR**:
`hiringOrganization.email` on this template is a recruiter's own address
(a first name at the employer's domain on the ad read) — #287 emitted it
as `employer_email`; it is no longer a field on either board,
`contacts_withheld` says so, and the description is scrubbed of e-mail
addresses.

```
nationalevacaturebank.py sitemap --host intermediair --sample 10 --limit 3
[nationalevacaturebank] **2 160 distinct advertisement uuid(s)** on www.intermediair.nl in 1 file(s) (vacature-1.xml 2 160); 3 emitted (--limit 3); the index's own lastmod 2026-09-14T00:21:16Z.
[nationalevacaturebank] The site states no figure by HTTP — its «N banen» is rendered in a browser from the API behind the search the rules refuse; no second figure is compared here.
[nationalevacaturebank] Sample of 10 spread over the file(s): 10 served with a JobPosting whose validThrough is on or after 2026-09-14, 0 gone (410), 0 gone (404), 0 other — **the sitemap lists what has left the board**; its count is not the live inventory.
```

### Configuration

```yaml
boards:
  intermediair:
    enabled: true
    host: intermediair      # the board key `nationalevacaturebank.py` takes; the sister is the default
```

Three tests; six mutations on a detached worktree (`python3 -B`), six
red — the host not put on the index, the key not on the record, the
other board's rows accepted, the e-mail field restored, the description
not scrubbed, the unknown host accepted.

