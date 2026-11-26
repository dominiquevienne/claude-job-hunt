# Board measurement — Careers.gy (`careers.gy`, Guyana): «Vacancies in Guyana» — an Angular shell whose list lives on ANOTHER host, the public Laravel collection `api.careers.gy/public/api/jobs` (748 records, of which 96 within their own `expires_at` on 2026-11-26); no rules written on either host; adapter `careersgy.py`

<!-- verified: 2026-11-26 -->

<!-- hosts: careers.gy, api.careers.gy -->
<!-- script: careersgy.py -->
<!-- countries: GY -->
<!-- content: measured · **ADAPTER DELIVERED 2026-11-26 (#706): every path of `careers.gy` returns the same 79 442-byte shell; the environment object names `apiUrl: https://api.careers.gy/public/`, an interceptor prefixes it, and the jobs service composes `api/jobs` — so the list is `api.careers.gy/public/api/jobs?page=N`, 25 a page, Laravel `total`. Both `robots.txt` are not rules files (the shell, and Laravel's welcome page): an absence of rules, open, `certain: False`, guarded on the API host. No credential is sent: the same object carries a client secret for a password grant, never used. 748 records, all `status_id` 2, and 652 past their own `expires_at`: 96 emitted by default, the rest counted and emitted flagged only with `--include-expired`.** · 2026-11-26 -->
<!-- content: measured · **the root (200, 99 244 B, md5 c62ea5f8784b identical on two reads) is an Angular application shell — `<app-root>`, hashed bundles, `accounts.google.com/gsi/client` — with no job card, no count, no link and no JobPosting in its markup; the list is fetched by the app; `_robots.allowed('careers.gy','/')` → open, `certain: False` (the rules file did not answer as one)** · 2026-09-18 -->
<!-- witness: 748 · **the Laravel paginator's own `total` on `api.careers.gy/public/api/jobs`, read by `careersgy.py`; 748 read against 748 stated on 2026-11-26, of which 96 within their `expires_at`** · 2026-11-26 -->
<!-- witness: none — the shell states nothing · 2026-09-18 -->
**Found by the Guyana search of #621 (a country never searched), measured
2026-09-18 06:54–06:56 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #621:
three searches naming the public sources and the private boards, no
composed host names. *A measurement, not an adapter.*

```
_robots.allowed('careers.gy', '/')   open
GET https://careers.gy/   200 ×2 — see the content line
```

The adapter's first line: the API the app calls (read in a browser's network panel — replayed with the page's own parameters, as SparkHire's is), or a browser route if the API is not served to the client.
