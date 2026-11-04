# Board measurement — St Lucia Business Online — Job Vacancies (`www.stluciabusinessonline.com`, Saint Lucia): the vacancies section of a business directory (WordPress 6.9.8 with WooCommerce) — `/job-vacancies/` links 61 distinct vacancy posts (`/vacancy-for-<role>-at-<employer>/`, `/multiple-vacancies-at-<employer>/`), the newest dated 2026-09-16, served to the declared client (185–188 KB), rules open; no count stated THEN — **SHIPPED 2026-11-04 as `stluciabusinessonline.py` (#712) on the WordPress REST route, whose `X-WP-Total` of 3 594 is an ARCHIVE over 36 pages and NOT an inventory: 52 posts emitted inside a 120-day window, and the two date fields differ by a DAY on half of them**

<!-- verified: 2026-11-04 -->

<!-- hosts: www.stluciabusinessonline.com -->
<!-- script: stluciabusinessonline.py -->
<!-- countries: LC -->
<!-- content: measured · **the list is the WordPress REST route `wp/v2/posts?categories=132` (the id EXTRACTED from `/wp-json/wp/v2/categories`, never composed), whose `X-WP-Total` and the category's own `count` BOTH state 3594 over 36 pages — an ARCHIVE and not an inventory, page one alone spanning 2026-03-03 to 2026-11-03, so it is reported and never used as a completeness gate. `robots.txt` 200/289 B, `state: read`, `certain: True`, group `*` refusing only /xmlrpc.php and /wp-admin/, and NO `Crawl-delay` written so the rate is ours. The site also hosts `trinidad-job-vacancies` (229) and `barbados-vacancy` (230): 0 of the 100 most recent carries one, and such a post is skipped and named. `date` (local) and `date_gmt` (UTC) differ by a DAY on 25 of the 52 emitted. Exercised: 52 posts, exit 0, 120-day boundary reached, 2026-07-14 to 2026-11-03** · 2026-11-04 -->
<!-- witness: `X-WP-Total` AND the category's own `count`, cross-checked and both 3594 — two numbers from the host, neither our extraction. **They answer «is this route still the whole category», NEVER «did we read everything»**: it is an archive, so completeness is measured against the `--since-days` boundary instead · 2026-11-04 -->
<!-- content: measured · **`/job-vacancies/` (200, 184 658 / 187 866 B, md5 aafed3038150 / f8d9697dbc53 — the body moves between two reads 4 s apart) is a WordPress 6.9.8 page listing 61 distinct vacancy posts as `/vacancy-for-<role>-at-<employer>/` and `/multiple-vacancies-at-<employer>/` (Anse Chastanet, Bay Gardens Resorts, Sunswept Resorts, Secrets St Lucia, M&C Drugstore, Sixt…), dates 2026-09-16 on the newest, a «Next» control and no `/page/N/` link; no count stated, no JobPosting; `_robots.allowed('www.stluciabusinessonline.com', '/job-vacancies/')` → open, certain** · 2026-09-18 -->
<!-- witness: none — the page states no count; 61 posts linked from it is a count of links, not the site's · 2026-09-18 -->

**Found by the Saint Lucia search of #619 (a country never searched),
measured 2026-09-18 07:01–07:06 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #619: two searches naming the Government's portal and the private boards,
no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('www.stluciabusinessonline.com', '/job-vacancies/')   open
GET https://www.stluciabusinessonline.com/job-vacancies/   200 ×2 — see the content line
```

The adapter's first line: the WordPress REST `wp/v2/posts` (a category or tag for vacancies, `X-WP-Total`) as the list with its count, the post as the ad; what «Next» loads (a second page or an AJAX call) is to be measured.

## 2026-11-04 — #712 SHIPPED as `stluciabusinessonline.py`: 52 posts, and the stated total of 3 594 is an ARCHIVE

**THE PREMISE WAS REMEASURED BEFORE BEING USED, and unlike #733 it HELD** — the
contrast is what makes that check worth its cost rather than ritual. Measured
2026-11-04 12:30 UTC: `/job-vacancies/` answers **200, 176 642 B** (against
184 658 / 187 866 on 18.09), **75 858 characters of visible text** so no shell,
**32** `/vacancy-for-` links and **10** `/multiple-vacancies-at-` — *both* forms
the card names — `wp-json` still exposed, newest post **2026-11-03**. The size
drop is the ordinary attrition of old posts, not a rebuild. *(Remeasurement
REPORTED by a peer; everything below is measured here.)*

### The route, and the witness that comes with it

```
robots.txt 200, 289 B, state: read, certain: True — group `*` refuses TWO paths
  and neither is ours: /xmlrpc.php, /wp-admin/.  NO `Crawl-delay` is written,
  so the rate is OURS — `Pace(host, own=1.0)`, consulted on every request.
GET /wp-json/wp/v2/posts?categories=132&per_page=100&page=N&orderby=date&order=desc
    -> X-WP-Total: 3594 · X-WP-TotalPages: 36
```

The category id **132** (`job-vacancies`) is EXTRACTED from
`/wp-json/wp/v2/categories`, never composed.

**AND `X-WP-Total` IS AN ARCHIVE, NOT AN INVENTORY — this is the finding that
shapes the adapter.** 3 594 posts over 36 pages, and **page one alone spans
2026-03-03 to 2026-11-03**, eight months. A vacancy has a deadline; three and a
half thousand of them do not describe what is open. **Wiring that as the
completeness gate would make every run partial for ever** — the warning §4
spends its length on, *a warning that always fires is no better than one that
never fires, and it is harder to remove because it looks prudent*. So the total
is REPORTED as the archive, and what the tool calls complete is **reaching the
`--since-days` boundary**, which a run can establish.

*The witness still earns its place, and it is cross-checked: the category's own
`count` and the header `X-WP-Total` both say **3 594** — two numbers from the
host, neither of them our extraction. They answer «is this route still the whole
category», never «did we read everything».*

### Two dates, and they differ by a day on HALF the corpus

`date` is the site's local time, `date_gmt` is UTC: the newest post reads
`2026-11-02T20:14:36` local and `2026-11-03T00:14:36` UTC. **25 of the 52
emitted records carry a different calendar day in the two fields.** Two hands
measured this board within the hour and reported 02.11 and 03.11 — **both right,
on different fields, and nothing in their form says which**. The adapter emits
`date_gmt` with its `Z`, and keeps the local one beside it as
`posted_local_stated`: a ledger that mixes zones cannot be compared with itself.

### The site hosts other territories' vacancies

`trinidad-job-vacancies` (id 229, 11 posts) and `barbados-vacancy` (id 230, 8) —
so a post in one of those is NOT Saint Lucia, and emitting it as `LC` would be
another country's advertisement in this ledger. **Measured: 0 of the 100 most
recent carries one**, and the guard exists anyway, because a window that is
clean today is not a property of the board. When one appears it is skipped and
NAMED on stderr.

### Exercised

`stluciabusinessonline.py jobs` → **52 vacancy posts over 1 page, exit 0**,
boundary of 120 days reached, spanning **2026-07-14 to 2026-11-03**.

```
title 52/52 · url 52/52 (given by the host in `link`, never composed)
posted 52/52, all UTC with `Z` · description 44/52 · status `publish` 52/52
26 of 100 titles arrive HTML-escaped (`&#038;`) -> 0 entity survives the output
contacts: 65/100 carry an e-mail and 6/100 a `+1 758`; over the run they left
  31 of 52 descriptions, and 0 e-mail and 0 `+1 758` survive ANYWHERE in it
`contacts_withheld` is ABSENT when nothing was taken (21 of 52), never `False`
```

**AND A BRANCH THAT IS INERT ON THIS CORPUS IS DECLARED RATHER THAN DISCOVERED
LATER: the telephone redaction fired 0 times on the 52-post run**, while the
wider measurement saw `+1 758` in 6 of 100. Its coverage therefore rests on the
named test case and on that measurement — **not on the run, whose green says
nothing about it.** That is the fifth species of defective guard: green on the
fixtures, never travelled by the corpus.

**The order of operations in the text extractor is itself a guard**: tags are
stripped BEFORE entities are undone, because a `&lt;b&gt;` unescaped first would
become a tag that the strip then eats with its content.
