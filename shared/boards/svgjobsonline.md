# Board measurement — SVG Jobs Online (`www.svgjobsonline.com`, Saint Vincent and the Grenadines): «Introducing SVG Job Board» — answers 503 with its own holding page («Thank you for your interest in SVG Job Board. Our website will be live again soon.», 4 278 B, identical to the client twice and to curl) on 2026-09-18; nothing of the board was read; indeterminate, a measure to redo; no adapter yet

<!-- verified: 2026-09-21 -->

<!-- hosts: www.svgjobsonline.com -->
<!-- script: none -->
<!-- countries: VC -->
<!-- content: indeterminate · **the root answers 503 on two reads by the declared client (07:56:00–07:56:22 UTC; 4 278 B, md5 29f18927cac9 identical) and to curl — the site's own holding page, «Our website will be live again soon», not a provider's error; nothing read, rules not read (`_robots.allowed` → open, `certain: False`)** — **second control 2026-09-21, 06:23:34 and 06:23:46 UTC: the same 503 twice — 4 278 B, md5 29f18927cac9, the holding page of 2026-09-18 byte for byte; nothing read** · 2026-09-21 -->
<!-- witness: none — nothing was read · 2026-09-18 -->
<!-- route: none · non faisable — décision du propriétaire du 18.09.2026 (un hôte muet reçoit un ticket adapter+blocked qui dit pourquoi et ce qui lèverait), #751 · 2026-09-19 -->

**Found by the Saint Vincent and the Grenadines search of #616 (a country
never searched), measured 2026-09-18 07:55–08:01 UTC by the declared client, the
guard on the exact path first, `bin/fetch-body.py`, two reads.** The method
is written on #616: two searches naming the Government, the Service
Commissions Department and the private boards, no composed host names. *A
measurement, not an adapter.*

```
_robots.allowed('www.svgjobsonline.com', '/')   open, certain False (the rules file did not answer)
GET https://www.svgjobsonline.com/   503 ×2 (client), 503 (curl) — the board's own «live again soon» page
```

**A holding page is neither a refusal nor a permission**: the operator says the board is down and coming back. Not «closed»: the next control is 2026-09-21 (a deferred task of the session that measured).

## The control three days on — the same holding page

```
GET https://www.svgjobsonline.com/   503 ×2 by the declared client (06:23:34, 06:23:46 UTC) — 4 278 B, md5 29f18927cac9, identical to 2026-09-18
```

**«Live again soon» has lasted three days.** Nothing read, not «closed»:
#751 stays `blocked` with this date; next control 2026-09-28.
