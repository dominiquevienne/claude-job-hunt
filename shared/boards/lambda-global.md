# Board measurement — Lambda (`www.lambda.global`, Mongolia): «Ажлын байр | Ламбда» — a Mongolian recruiting platform whose jobs page is served to the declared client (848 KB, identical twice) with thirty `/jobs/<slug>-<id>` links and per-role salary pages, rules open, no count stated; no adapter yet

<!-- verified: 2026-09-17 -->

<!-- hosts: www.lambda.global -->
<!-- script: none -->
<!-- countries: MN -->
<!-- content: measured · **the root (200, 847 839 B, md5 a281e2c06877 identical on two reads) is a Material-UI page titled «Ажлын байр | Ламбда» with 30 distinct `/jobs/<slug>-<id>` links and 42 `/salary/job/<role>` pages; no count stated, no JobPosting; `_robots.allowed('www.lambda.global','/')` → open, certain; the pager and the ad not read** · 2026-09-17 -->
<!-- witness: none — the page states no count · 2026-09-17 -->

**Found by the Mongolia search of #603 (a country never searched), measured
2026-09-17 14:0x–14:32 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #603: one
search naming the country's boards (a diaspora career blog's review of
«every job site in Mongolia», the engine's own results), no composed host
names; no public employment service found online by that search. *A
measurement, not an adapter.*

```
_robots.allowed('www.lambda.global', '/')   open, certain
GET https://www.lambda.global/               200 ×2, identical — thirty /jobs/<slug>-<id> links, salary pages
```

The pager, the ad and what it carries are the adapter's first line.
