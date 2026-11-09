# Board measurement — GuyanaJobs.net (`guyanajobs.net`, Guyana): TWO populations that are not the same kind of object — **3 plugin entries carrying a full `JobPosting`** and **18 flyer posts whose vacancy text is inside the image**. The kind comes from the sitemap MEMBER and never from the flat slug, which a page shares

<!-- verified: 2026-11-09 -->

<!-- hosts: guyanajobs.net -->
<!-- script: guyanajobs.py -->
<!-- countries: GY -->
<!-- route: http · 21 · 2026-11-09 -->
<!-- content: measured · read 2026-11-09: **this board publishes TWO populations and they are not the same kind of object.** The 118-byte rules file refuses only `/wp-admin/`, declares no `Crawl-delay` (`delay_for()` → `None`, so the 2 s pace is ours) and DECLARES its enumerator — `Sitemap: https://guyanajobs.net/sitemap_index.xml`, **which is not `/sitemap.xml`**, so it was guarded on its own exact path (§3 bis). Its index has five members. **`job_listing-sitemap.xml` holds 3 `/job/<slug>/` entries, each with a FULL `JobPosting`** — `hiringOrganization`, `jobLocation` (`Region 4 Demerara-Mahaica`), `datePosted`, `validThrough`, `employmentType`, `directApply` and a description measured at **4 035 characters**. **`post-sitemap.xml` holds 18 flyers at a flat `/<slug>/`, and `_ldjson.postings()` returns 0 on them** with `absent_reason()` saying `no-jobposting, our_fault=False`: **the vacancy text is inside the IMAGE**, and this adapter does not read images, so a flyer yields its title and says so in the record. *That answers the blocker the issue carried, and it answers it DIFFERENTLY for the two.* **THE KIND COMES FROM THE MEMBER AND NEVER FROM THE SHAPE**: a flyer and an ordinary page are the SAME flat slug, so a shape test counted `page-sitemap.xml` as twelve flyers — `/about-us/`, `/contact-us/`, `/privacy-policy/`, `/cv-template/`, `/terms-and-conditions/`, `/blog/`, `/employer-submit-job/` and five more — and reported 30 where there are 18. **And counting `<loc>` would report the board two and a half times too large**: `count_says()` gave 46 `<loc>` against 19 `<url>` on the posts and 5 against 3 on the plugin's, the excess being `<image:loc>`; the count is therefore taken on `<url>` blocks with the address on the FIRST `<loc>` inside each, which makes an image structurally uncountable. *`_sitemap.locs()` is SOUND — its namespace tolerance is what makes it work elsewhere — and is not to be repaired.* · 2026-11-09 -->
<!-- content: measured · **the root (200, 350 027 B, md5 2508bfc96069 identical on two reads) is WordPress 7.1.1: the front is a feed of vacancy flyers (one `<article>` block on the front, `/page/N/` up to 8), a job-listing plugin's pages `/job-listing/`, `/employer-submit-job/`, `/employer-job-dashboard/`; the JobPosting on the root carries the site's own title («Find your Next Job in Guyana - guyanajobs.net»), not an ad; no count stated; `_robots.allowed('guyanajobs.net','/')` → open, certain** · 2026-09-18 -->
<!-- witness: none, and the one the issue proposed is UNREACHABLE BY OUR ROUTE — `X-WP-Total` is a response HEADER, and `bin/fetch-body.py` records `status`, `bytes`, `md5`, `agent`, `cache.headers` (`vary` only), `content_encoding`, `final_url` and `vendor`, and no arbitrary response header. The site states no count anywhere either, which the 2026-09-18 line already said. So 3 and 18 are this adapter's own extraction with nothing corroborating them, and the `<url>`/`<loc>` discipline is the only thing standing between 21 and 51 · 2026-11-09 -->
<!-- witness: none — the root states no count · 2026-09-18 -->
**Found by the Guyana search of #621 (a country never searched), measured
2026-09-18 06:54–06:56 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #621:
three searches naming the public sources and the private boards, no
composed host names. *A measurement, not an adapter.*

```
_robots.allowed('guyanajobs.net', '/')   open
GET https://guyanajobs.net/   200 ×2 — see the content line
```

The adapter's first line: `/job-listing/` (the plugin's list) and the WordPress REST `wp/v2/posts` with `X-WP-Total`; the flyers are images — what an ad carries as text is to be measured.
