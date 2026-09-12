# Board measurement — SPTOJobsLink (`sptojobslink.com`, Pacific): refused to our client, served to a browser, a hundred-card page with no pager, and a sitemap whose second file answers 404 with the newest 548 posts in its body

<!-- verified: 2026-09-12 -->

<!-- hosts: sptojobslink.com -->
<!-- script: none -->
<!-- countries: FJ -->
<!-- content: measured · **2 548 job posts in the sitemap its rules declare** (`wp-sitemap-posts-jobs-vacancies-1.xml` 2 000 + `-2.xml` 548, `<lastmod>` on all, 2025-08-01 → 2026-09-11; 116 in September 2026, 207 in August), read from a connected browser tab; the `/jobs/` page shows exactly 100 cards (31-08 → 10-09-2026), no pager — a cap, not a count; the site states no total · 2026-09-12 -->
<!-- witness: none the site states — the `/jobs/` page carries no figure and no pager; the only external anchor is the sitemap's own `<lastmod>` distribution (116 posts dated September against the page's 100 cards from 31 August on), which bounds the live window without stating it · 2026-09-12 -->

**The South Pacific Tourism Organisation's job board — «jobs from around the
Pacific»: Fiji first (Nadi, Sigatoka, Suva), Cook Islands, and the rest of
the region by category.** Named in `myjobsfiji.md` since 2026-09-07 as the
fourth host of the 25-byte vendor refusal, sitemap included. *This card is
what a browser sees past that door.* Measured 2026-09-12 12:13–12:15 UTC,
Claude in Chrome connected, one tab, the guard on the exact path first.

## Rules, transport, the door

```
robots.txt        200, 117 B — `*` open; Sitemap: https://sptojobslink.com/wp-sitemap.xml; no Crawl-delay; certain: True
declared client   / · /wp-sitemap.xml · /sitemap.xml → 403, 25 B, md5 9ccabba… (2026-09-07/08, myjobsfiji.md) — family (1) of robots-policy.md
browser tab       / → 200 «SPTOJobsLink – Connecting people with jobs in the Pacific» · WordPress 7.1 · no challenge, no interstitial
```

**Borne 0 held**: the refusal goes to the declared HTTP client and to
nobody else.

## The sitemap — the inventory, and a 404 that carries the newest file

```
GET /wp-sitemap.xml                          200, 1 185 B — 11 children: posts-post, posts-page, posts-jobs-vacancies-1, -2, taxonomies (category, post_tag, location, no-form, contract-type, industry), users
GET /wp-sitemap-posts-jobs-vacancies-1.xml   200 — 2 000 <loc> /jobs-vacancies/<slug>/, <lastmod> 2025-08-01 → 2026-07-03
GET /wp-sitemap-posts-jobs-vacancies-2.xml   **404 — and the body is the file: 548 <loc>, <lastmod> 2026-07-03 → 2026-09-11**
                                             by month: 2026-07 249 · 2026-08 207 · 2026-09 116 (across both files)
```

**The second file answers HTTP 404 with a complete sitemap in its body —
read twice from the tab, the same both times.** *A client that trusts the
code drops the 548 newest posts and keeps the 2 000 oldest; a client that
trusts the body reads the inventory.* This is the reverse of the rule this
repository wrote against `403` pages entering fingerprint tables («a
readable body is not an answer — the code decides») — **here the code is
wrong and the body is right, and only reading both says which.** The
adapter reads the index, then every child it declares, and records the
status beside each; a 404 whose body parses as a `urlset` is emitted **with
the 404 named**, never silently promoted and never silently dropped.

**2 548 is the archive of posts since August 2025, not the live count.**
The `lastmod` is the post's date (the page's «POSTED: 10-09-2026» matched
its sitemap entry on the one checked); what closes a post is not in the
sitemap — the page carries no closing date either.

## The `/jobs/` page — one hundred cards and nothing after

```
GET /jobs/    200 — 100 distinct /jobs-vacancies/<slug>/ cards, POSTED 31-08-2026 → 10-09-2026, category, city + country
              no pager, no load-more, no admin-ajax call on scroll (two scrolls to the bottom, still 100)
```

**A hundred is a cap.** The sitemap dates 116 posts to September alone;
the page stops at 31 August after exactly 100 cards. *The site states no
count anywhere read.* The stable id is the slug (the WordPress post name;
numbered suffixes — `sous-chef-9`, `head-chef-2` — are the site's own
disambiguation, so the slug is unique by construction).

## The advertisement

```
GET /jobs-vacancies/housekeeping-supervisor-spa-therapist/   200, 87 752 B
title · city + country («Sigatoka Fiji») · category («Tourism & Hospitality») · «Posted: 10-09-2026» · body · an application form (JetFormBuilder)
no JSON-LD, no JobPosting
```

## The procedure a session follows — this is the adapter (decision of 2026-09-08)

1. guard `sptojobslink.com` on `/wp-sitemap.xml` and on each child it
   declares before anything;
2. `navigate https://sptojobslink.com/` in the session's own tab;
3. from the tab, `fetch` the index, then `wp-sitemap-posts-jobs-vacancies-N.xml`
   for every N it declares; **record the HTTP status of each and parse
   the body regardless**; a non-200 whose body is a `urlset` is counted
   and reported as such («file 2: 404, 548 entries read from the body»);
4. emit one row per `<loc>` with its `<lastmod>` as `posted`; print
   **«n posts in the sitemap, m dated the last 30 days — the site states no
   total; /jobs/ shows 100 and stops»**, never a bare 2 548;
5. `--since` on `<lastmod>` is the live window here (the page's POSTED date
   is the same field); one advertisement page for the body when wanted;
6. close the tab.

## What this card does not establish

- **The live count** — no page states one; the September posts (116) and
  the 100-card page bound it from two sides without meeting.
- **Why file 2 is a 404** — a WordPress sitemap provider answering 404 on
  its second page while rendering it is not explained here; only measured,
  twice.
- **The other Pacific countries' share** — `countries: FJ` is the market
  the cards name most; Cook Islands and others appear, and the
  `taxonomies-location-1.xml` child (not read) would give the list.
- **No script ships.** The route is a browser tab and fetches from it.
