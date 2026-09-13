# Board adapter — foundit Philippines (formerly Monster): the second host of `founditgulf.py` — 42 504 advertisements in two active-jobs sitemaps, the same hand-written `ClaudeBot: Disallow /jobs/ /search/`, never read here either

<!-- verified: 2026-09-13 -->

<!-- hosts: www.foundit.com.ph, foundit.com.ph -->
<!-- script: founditgulf.py -->
<!-- countries: PH SG MY -->
<!-- content: measured · rules read twice and certain (703 B — a hand-written group naming `GPTBot`, `ClaudeBot`, `CCBot`, `Bytespider`, `Meta-ExternalAgent`, `Google-Extended` with `Allow: /` and `Disallow: /jobs/`, `/search/`; `Claude-User` under `*`; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200: the sitemap index (37 children) and its 2 active-jobs files hold 42 504 `<loc>`, 42 504 distinct ids — PH 40 491, SG 78, MY 57 by the slug, 1 552 without a place in it; today's file lists 1 031 and 23 of them are NOT among the active — the adapter says so; a `JobPosting` JSON-LD on 10 of 10 sampled, `addressCountry: PH` on all ten · 2026-09-13 10:52 UTC -->
<!-- witness: today's sitemap against the active ones — «today's sitemap lists 1 031 and 23 of them are NOT among the 42 504 active — the two files disagree; the active count may be short» on 2026-09-13 10:52 UTC; the root's «100,000+ Jobs in Philippines» printed as a slogan, never compared -->

**Shipped 2026-09-13 as a second host of `founditgulf.py` — measured in lot
8 of #233 and shipped the same hour, under the condition recorded on
`founditgulf.md`: the adapter reads neither `/jobs/` nor `/search/`, the two
paths the operator closed by hand to six AI crawlers, on this host either
(`gate()` exits 7 on them for both hosts; mutated, red).** The line
«refusal written by hand naming ClaudeBot, `/jobs/` `/search/`» stays here
for the owner, as on the Gulf card.

```
python3 skills/job-scan/scripts/founditgulf.py sitemap --host www.foundit.com.ph [--limit N] [--no-site-total]   # index + 2 active files (+ today's + the root): 3 to 5 requests
python3 skills/job-scan/scripts/founditgulf.py ad --url https://www.foundit.com.ph/job/<slug>-<id>              # the host is read from the URL; rows keyed foundit-ph:
```

## The rules — a refusal written by hand, and it names `ClaudeBot`

```
robots.txt      read twice, certain: True, 703 B, md5 365ec2d7dab4 both times — WRITTEN BY HAND:
                `User-Agent: GPTBot / ClaudeBot / CCBot / Bytespider / Meta-ExternalAgent / Google-Extended`: Allow: /, Disallow: /jobs/, /search/
identity("/")   http, claude-user       <- not named; the group that names ClaudeBot does not bind Claude-User (owner, 2026-09-07; #233: the hand-written four are measured like the others)
verdict()       sweep True — «refuses 2 path(s) to claudebot and not the site as a whole»
allowed()       True on `/`, `/xmlsitemap/sitemap-index.xml`, `/xmlsitemap/active-jobs-sitemap0.xml.gz`, `/job/<slug>-<id>`
adapter         refuses `/jobs/` and `/search/` itself on this host too (exit 7) — a promise, not a rules verdict
crawl_delay     none — 2 s is ours
```

## The transport — 200 everywhere asked

```
GET https://www.foundit.com.ph/                                        200, 194 625 B   (10:22:20Z, 10:22:21Z — same size)  «100,000+ Jobs in Philippines: Apply for September 2026 Hiring» — a slogan
GET https://www.foundit.com.ph/xmlsitemap/sitemap-index.xml            200, 5 601 B     (10:23:28Z, byte-identical at 10:23:30Z)  37 children
GET https://www.foundit.com.ph/xmlsitemap/active-jobs-sitemap{0,1}.xml.gz   200          (10:52Z, by the adapter)   42 504 <loc> in all
GET https://www.foundit.com.ph/xmlsitemap/todays-jobs-sitemap.xml      200              (10:52Z)  1 031 <loc>
GET https://www.foundit.com.ph/job/<slug>-<id>  ×10                    200              (10:53–10:54Z)  JobPosting JSON-LD on all ten
```

## What the sitemaps say — 42 504 advertisements, and a disagreement the adapter names

| question | answer |
| :-- | --: |
| `<loc>` across `active-jobs-sitemap0..1` | **42 504** — `/job/<slug>-<id>`, **42 504 distinct ids**, 0 of another shape |
| `todays-jobs-sitemap.xml` | 1 031 — **23 of them NOT among the 42 504 active**: «the two files disagree; the active count may be short» (printed each run; «consistent» on the Gulf host the day before) |
| by the slug's tail | **PH 40 491** · SG 78 · MY 57 · SA 1 · two places 325 · none 1 552 — `countries: PH SG MY`, the country read per advertisement by `ad` |
| the root's figure | «100,000+ Jobs in Philippines» — a slogan, printed and named, never compared |
| a stated count of this board | none found — the listing pages are not read; the second document is today's file against the active ones |

## What an advertisement carries — 10 of 10 sampled, 10:53 UTC

Ten drawn at random (seed 20260913) from the 42 504: `JobPosting` on all
ten, `addressCountry: PH` on all ten, `addressLocality` «Philippines» (no
city) on all ten, `employmentType` «Full time» on all ten, `datePosted`
2026-07-07 → 2026-09-10 (`DD-MM-YYYY` on the site, ISO beside),
`monthsOfExperience` 1 on three (a placeholder), 12–84 on the rest, `skills`
0–10; no `baseSalary` field, as on the Gulf host.

## What this card is, and is not

- **An adapter's second host, shipped under the same recorded condition** —
  `sitemap --host www.foundit.com.ph`, `ad` on a PH URL; rows keyed
  `foundit-ph:`. No key, no browser; three to five requests for the
  enumeration.
- **Not a verdict on the hand-written refusal** — recorded as written, for
  the owner; the adapter honours it in substance and the doctrine in law.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
