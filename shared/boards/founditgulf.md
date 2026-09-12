# Board adapter — foundit Gulf (Gulf + Egypt, formerly Monster Gulf): 58 930 advertisements through three active-jobs sitemaps, `/jobs/` and `/search/` never read, and a refusal written by hand that names `ClaudeBot`

<!-- verified: 2026-09-12 -->

<!-- hosts: www.founditgulf.com, founditgulf.com -->
<!-- script: founditgulf.py -->
<!-- countries: AE SA QA KW BH OM EG -->
<!-- content: measured · rules read twice and certain — a hand-written group naming `GPTBot`, `ClaudeBot`, `CCBot`, `Bytespider`, `Meta-ExternalAgent`, `Google-Extended` with `Allow: /` and `Disallow: /jobs/`, `/search/`; `Claude-User` is not named and falls under `*`; `identity()` answers `claude-user`, `verdict()` sweeps — and the transport answers 200: the sitemap index names 49 children, the 3 `active-jobs-sitemap<n>.xml.gz` hold 58 930 `<loc>`, 58 930 distinct ids, and `todays-jobs-sitemap.xml` 1 041, all among them; a `JobPosting` JSON-LD on 10 of 10 sampled, the country in each · 2026-09-12 11:42 UTC -->
<!-- witness: today's sitemap against the active ones — «today's sitemap lists 1 041, 1 041 of them among the 58 930 active — consistent» on 2026-09-12 11:42 UTC, and the count of those NOT among them when they part; the root's «Over 800,000+ jobs» is printed as a slogan, never compared -->

**Shipped 2026-09-12 — under a condition set by the pilot and recorded
here: the adapter reads neither `/jobs/` nor `/search/`, the two paths the
operator closed by hand to six AI crawlers, `ClaudeBot` among them.** The
decision of 2026-09-07 (owner, against the pilot's advice, «not replayed»)
makes the host lawful under `claude-user`, which that group does not name;
#233's body says the hand-written four are measured like the others; and
`gate()` still exits 7 on those two paths before the rules are asked. *The
owner is told in the pilot's report; this card keeps the line.*

```
python3 skills/job-scan/scripts/founditgulf.py sitemap [--limit N] [--no-site-total]   # index + 3 active files (+ today's + the root): 4 to 6 requests, ~15 s
python3 skills/job-scan/scripts/founditgulf.py ad --url https://www.founditgulf.com/job/<slug>-<id>
```

## The rules — a refusal written by hand, and it names `ClaudeBot`

```
robots.txt      read twice, certain: True, 706 B, md5 572ee93fb164 both times
                `User-agent: *`            Disallow: /seeker/dashboard, /seeker/profile, /*radialhr, /pwa/, /trex/*/, */middleware/…, /mthinking/, *track_aor.html, /penguin/…, /middleware/, /xmlsitemap/expired-jobs-sitemap*.xml
                `User-Agent: GPTBot / ClaudeBot / CCBot / Bytespider / Meta-ExternalAgent / Google-Extended`
                                           Allow: /, /career-advice/, /career-services   Disallow: /jobs/, /search/     <- WRITTEN BY HAND
                Sitemap: /xmlsitemap/sitemap-index.xml, /xmlsitemap/todays-jobs-sitemap.xml
identity("/")   http, claude-user       <- not named; the group that names ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True
allowed()       True on `/`, `/xmlsitemap/sitemap-index.xml`, `/xmlsitemap/active-jobs-sitemap0.xml.gz`, `/job/<slug>-<id>`; False on `/xmlsitemap/expired-jobs-sitemap0.xml.gz`
adapter         refuses `/jobs/` and `/search/` itself (exit 7) — a promise, not a rules verdict
crawl_delay     none — the adapter paces itself at 2 s
```

*The pilot's view, recorded (2026-09-12): lawful under the doctrine, and the
adapter stays off the two paths so the refusal is honoured in substance
while the owner decides. The line «refusal written by hand naming
ClaudeBot, `/jobs/` `/search/`» stays on this card.*

## The transport — 200 everywhere asked

```
GET https://www.founditgulf.com/                                            200, 226 430 B   (11:18:56Z)  «Latest Jobs in Gulf (2026)…» — «Over 800,000+ jobs to explore», a network slogan
GET https://www.founditgulf.com/xmlsitemap/sitemap-index.xml                200, 7 459 B     (11:22:22Z)  49 children
GET https://www.founditgulf.com/xmlsitemap/active-jobs-sitemap{0,1,2}.xml.gz   200, 521 657 / 508 845 / 195 516 B   (11:22:59–11:23:00Z)   24 975 + 24 954 + 9 001 <loc>
GET https://www.founditgulf.com/xmlsitemap/todays-jobs-sitemap.xml          200, 191 894 B   (11:22:22Z)  1 041 <loc>
GET https://www.founditgulf.com/job/technical-sales-engineer-atec-egypt-66495664   200, 677 351 B   (11:40:49Z)  JobPosting JSON-LD
```

*`/search/it-jobs` was fetched twice at 11:21 UTC during the lot-4
measurement (200, 1 794 514 B, 82 `/job/` links, no stated count) — before
the condition was set; the adapter does not read it.*

## What the sitemaps say — 58 930 advertisements, seven countries

| question | answer |
| :-- | --: |
| `<loc>` across `active-jobs-sitemap0..2` | **58 930** — `/job/<slug>-<id>`, **58 930 distinct ids**, 0 of another shape |
| `todays-jobs-sitemap.xml` | 1 041, **1 041 of them among the 58 930** — the adapter prints this each run, and the count of those NOT among when they part |
| distinct `<lastmod>` | 36 — **all between 2026-09-11 13:06:53 and 13:07:xx +02:00**: a rebuild stamped by the second, not a posting date; no `--since` |
| by the slug's tail (lot 4) | AE 29 360 · SA 13 600 · **EG 12 080** · QA 2 215 · KW 777 · BH 263 · OM 32 · two names 392 · none 211 |
| the root's figure | «Over 800,000+ jobs to explore» — the foundit network's slogan, printed and named, never compared |
| a stated count of this board | **none found** — the listing pages are not read; the second document is today's file against the active ones |

**Egypt is a fifth of the board** — `countries:` says so, and `ad` reads the
country from each advertisement. *The other 45 index children are facets
(by location, function, skill, designation); `expired-jobs-sitemap*` is
refused to `*` and never matched by `ACTIVE_RE`.*

## What an advertisement carries — 10 of 10 sampled, 11:42 UTC

Ten drawn at random (seed 20260912) from the 58 930, plus the one read at 11:40:

| field | 10 of 10 | what it says |
| :-- | --: | :-- |
| `title`, `description` (HTML), `identifier.value` (the id, an integer) | 10 | present |
| `datePosted`, `validThrough` | 10 | **`DD-MM-YYYY`** — emitted as published in `*_as_published` and as ISO beside |
| `employmentType` | 10 | «Full time» on all ten |
| `hiringOrganization.name` | 10 | «Confidential» on 2; `sameAs` is the name again, not a URL |
| `jobLocation.address.addressCountry` | 10 | **an ISO-2 code** — AE 7, EG 2, QA 1 in the sample |
| `addressLocality` | 10 | «Dubai, United Arab Emirates», «Doha, Qatar», or the country alone («Egypt») |
| `experienceRequirements.monthsOfExperience` | 10 | 1 on four of them (a placeholder), 12–192 on the rest |
| `skills` | 10 | a list of 4–23 |
| `baseSalary` | **0** | **no salary field at all in the JSON-LD** |

## What this card is, and is not

- **An adapter, shipped under a recorded condition** — `sitemap` for the
  enumeration and the two checks, `ad` for one advertisement from its
  JSON-LD with the country it carries. No key, no browser; four to six
  requests for the enumeration.
- **Not a verdict on the hand-written refusal** — recorded as written, for
  the owner; the adapter honours it in substance and the doctrine in law.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
