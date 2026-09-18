# Board measurement — Motravay (`motravay.mu`, Mauritius): «Find Jobs in Mauritius — Motravay», «the number 1 job board of Mauritius» by its description — the root served to the declared client (55 KB, identical twice) is an app front with a `/jobs` link and no card in its markup, rules open; the list route to measure; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: motravay.mu -->
<!-- script: none -->
<!-- countries: MU -->
<!-- content: measured · **the root (200, 54 590 B, md5 5085c84afa02 identical on two reads) is a front with `/jobs` and no card, count or JobPosting in its markup — client-rendered; `_robots.allowed('motravay.mu','/')` → open, certain; whether `/jobs` serves the client is the adapter's first line** · 2026-09-18 -->
<!-- witness: none — the root is a front · 2026-09-18 -->

**Found by the Mauritius search of #618 (a country never searched),
measured 2026-09-18 06:45–06:47 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #618: one search naming the National Employment Department's portal
and the private boards, no composed host names. *A measurement, not an
adapter.*

```
_robots.allowed('motravay.mu', '/')   open
GET https://motravay.mu/   200 ×2 — see the content line
```

The list, its pager and the ad are the adapter's first line (its `adapter` issue).
