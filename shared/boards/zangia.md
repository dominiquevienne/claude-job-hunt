# Board measurement — Zangia (`www.zangia.mn`, Mongolia): «the biggest job search platform in Mongolia» — the list `/job/list` served to the declared client (46 KB, identical twice) is a Next.js shell with no card in its markup, rules open; no adapter yet, the list route to measure

<!-- verified: 2026-09-17 -->

<!-- hosts: www.zangia.mn, zangia.mn -->
<!-- script: none -->
<!-- countries: MN -->
<!-- content: measured · **`/job/list` (200, 45 811 B, md5 6272ef23adcd identical on two reads) is a Next.js app shell — `_next/static` chunks, twenty links, no card, no count, no JobPosting in its markup; `_robots.allowed('www.zangia.mn','/job/list')` → open, certain; whether the route the shell calls serves the client, or only a tab, is the adapter's first line** · 2026-09-17 -->
<!-- witness: none — the list page is a shell · 2026-09-17 -->

**Found by the Mongolia search of #603 (a country never searched), measured
2026-09-17 14:0x–14:32 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #603: one
search naming the country's boards (a diaspora career blog's review of
«every job site in Mongolia», the engine's own results), no composed host
names; no public employment service found online by that search. *A
measurement, not an adapter.*

```
_robots.allowed('www.zangia.mn', '/job/list')   open, certain
GET https://www.zangia.mn/job/list               200 ×2, identical, 45 811 B — a Next.js shell
```

The country's largest board by every account read. The route the shell
calls (a JSON the page fetches, replayed if it serves the client — the
14.09 judgment) or a tab is the adapter's first line (its `adapter`
issue).
