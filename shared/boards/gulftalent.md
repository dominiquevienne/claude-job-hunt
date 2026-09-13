# Board measurement — GulfTalent (`www.gulftalent.com`, UAE and the Gulf): served to the declared client today, an ItemList of 25 a page and a pager to 627 — an adapter to build, not a browser route

<!-- verified: 2026-09-13 -->

<!-- hosts: www.gulftalent.com, gulftalent.com -->
<!-- script: none -->
<!-- countries: AE SA QA KW BH OM -->
<!-- content: measured · **the pager closes at 15 675 for the UAE listing** — `/uae/jobs` serves a JSON-LD `ItemList` of 25 a page, its pager reaches page 627 and page 627 carries 25 (627 × 25 = 15 675), read from a connected browser tab; and the declared client is served too — `GET /` 200, 144 682 B, twice (md5 moving: a rendered element in the body); the site states no figure on the listing · 2026-09-13 -->
<!-- witness: none the site states — the ItemList and the pager's last page close the arithmetic; the UAE country page's «403 to the plain client» was not met today (2 × 200 at 13:27 UTC) · 2026-09-13 -->
<!-- route: browser · 15675 · 2026-09-13 -->

**In the #222 list from the UAE page as a 403 candidate — and today it is
not one: the declared client is served.** Measured 2026-09-13 12:35 UTC
(tab) and 13:27 UTC (client), the guard on the exact path first (`*`
open, certain).

```
robots.txt                 200 — `*` open on /uae/jobs and /uae/jobs/<slug>-<id>; identity claude-user
GET / (declared client)    200, 144 682 B, nginx/1.25.5 — twice, 3 s apart; md5 differs (a per-request element in the page), status and size identical
tab: /uae/jobs             200 «Jobs in UAE | GulfTalent» — JSON-LD BreadcrumbList + **ItemList (25)** · 21 /uae/jobs/<slug>-<id> links in the DOM · pager /uae/jobs/2 … /uae/jobs/627
tab: /uae/jobs/627         25 advertisements on the last page → 627 × 25 = **15 675**
```

**The route is HTTP, not the browser** — a script reading `/uae/jobs/N`
and its ItemList is the adapter, one per country edition (`/saudi-arabia/jobs`,
`/qatar/jobs` … not measured here). *Not built in this pass: the
measurement is what #222 asked for.* The advertisement page was not
opened.
