# Board measurement — Motravay (`motravay.mu`, Mauritius): «Find Jobs in Mauritius — Motravay» — the root is an app front, and `/jobs` is rendered by the SERVER with its cards and its count («8 results» on 2026-11-26); rules open except `/candidate`, `/employer` and the account pages; adapter `motravay.py`

<!-- verified: 2026-11-26 -->

<!-- hosts: motravay.mu -->
<!-- script: motravay.py -->
<!-- countries: MU -->
<!-- content: measured · **ADAPTER DELIVERED 2026-11-26 (#700): the premise was the ROOT, and `/jobs` is served — 62 427 B, 8 cards `data-testid=job-card-<uuid>`, and the page states «8 results»; no API to replay, no browser. The sitemap the rules declare (`/api/sitemap.xml`) names 115 `/jobs/<uuid>` pages with `lastmod` 2026-05-24 to 2026-11-25, and the 8 live cards are a strict subset of them by uuid, so it is an ARCHIVE and is not walked. Each card field is read by its icon (`lucide-map-pin`, `lucide-briefcase`, `lucide-banknote`), never by position; 1 card of 8 states a salary. The employer is only in the ad's JobPosting `hiringOrganization`: 7 ads of code `MOT` name the board itself, 1 of code `MAD` names a third party; emitted as stated.** · 2026-11-26 -->
<!-- content: measured · **the root (200, 54 590 B, md5 5085c84afa02 identical on two reads) is a front with `/jobs` and no card, count or JobPosting in its markup — client-rendered; `_robots.allowed('motravay.mu','/')` → open, certain; whether `/jobs` serves the client is the adapter's first line** · 2026-09-18 -->
<!-- witness: 8 · **the list page's own line «8 results», read by `motravay.py` on the page it extracts from; 8 against 8 emitted on 2026-11-26** · 2026-11-26 -->
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
