# Board measurement — Careers Malawi (`careersmw.com`, Malawi): «No One Knows Better» — a WordPress job board whose WHOLE list is one server-rendered page, `/?job_all=1` (101 cards on 2026-11-26), whose REST collection `job_listing` states the same count in `X-WP-Total`, rules open; adapter `careersmw.py`

<!-- verified: 2026-11-26 -->

<!-- hosts: careersmw.com -->
<!-- script: careersmw.py -->
<!-- countries: MW -->
<!-- content: measured · **ADAPTER DELIVERED 2026-11-26 (#677): `careersmw.py jobs` reads ONE page, `/?job_all=1` — the no-JavaScript fallback of the home page's «Load more jobs» button — which renders every card; 101 cards, 101 distinct `/job/<id>/` ads. Three enumerators were compared MEMBER BY MEMBER the same hour — that page, the REST collection `/wp-json/wp/v2/job_listing` (100 + 1) and `wp-sitemap-posts-job_listing-1.xml` (101 `<loc>`) — and the intersection is 101 on every side. The employer and the place live ONLY on the card (`cmw-cjm-meta`: the employer, a middle dot, then «City, Malawi»): the ad page's `job-single-meta` is empty, it carries no JSON-LD, and the REST `meta` is `[]`. Two of the 101 are typed by the host «Other» (a supplier prequalification) and «Training»; they are emitted with `not_a_job_by_type: true`, never dropped. `ad <id>` reads the REST `content`: four e-mail addresses on the first record measured, taken out and named.** · 2026-11-26 -->
<!-- content: measured · **the root (200, 78 095 B, md5 7d48132b905b identical on two reads) links ads as `/job/<slug>/` («project-manager-debottlenecking», «project-engineer-N») and `/post-a-job/`; no count stated, no JobPosting on the root; `_robots.allowed('careersmw.com','/')` → open, certain; the list and the ad not read** · 2026-09-17 -->
<!-- witness: 101 · **`X-WP-Total` of `/wp-json/wp/v2/job_listing`, read on its own request by `careersmw.py`, a count our card extraction did not make; 101 against 101 emitted on 2026-11-26** · 2026-11-26 -->
<!-- witness: none — the root states no count · 2026-09-17 -->

**Found by the Malawi search of #622 (a country never searched), measured
2026-09-17 16:49–16:52 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #622: one
search naming the national boards and aggregators, no composed host
names; no public employment service found online by that search. *A
measurement, not an adapter.*

```
_robots.allowed('careersmw.com', '/')   open, certain
GET https://careersmw.com/   200 ×2 — see the content line
```

The list, its pager and the ad are the adapter's first line (its `adapter` issue).
