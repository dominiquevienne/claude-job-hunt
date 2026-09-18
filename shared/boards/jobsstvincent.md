# Board measurement — Jobs St Vincent and the Grenadines (`jobsstvincent.com`, Saint Vincent and the Grenadines): Cloudflare answers 522 (origin unreachable) to the declared client twice and to curl on 2026-09-18, ~80 s each; nothing of the site was read — the fifth «Jobs <country>» island host on the same 16 bytes in two days; indeterminate, a measure to redo; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: jobsstvincent.com -->
<!-- script: none -->
<!-- countries: VC -->
<!-- content: indeterminate · **the root answers 522 on two reads by the declared client (07:57:46→07:59:08 and →08:00:31 UTC; 16 B `error code: 522`, md5 2c2dae9e9cdd), the same 522 to curl — Cloudflare could not reach the origin; nothing read, rules not read (`_robots.allowed` → open, `certain: False`)** · 2026-09-18 -->
<!-- witness: none — nothing was read · 2026-09-18 -->

**Found by the Saint Vincent and the Grenadines search of #616 (a country
never searched), measured 2026-09-18 07:55–08:01 UTC by the declared client, the
guard on the exact path first, `bin/fetch-body.py`, two reads.** The method
is written on #616: two searches naming the Government, the Service
Commissions Department and the private boards, no composed host names. *A
measurement, not an adapter.*

```
_robots.allowed('jobsstvincent.com', '/')   open, certain False (the rules file did not answer)
GET https://jobsstvincent.com/   522 ×2 (client, ~80 s each), 522 (curl) — «error code: 522», Cloudflare's origin timeout
```

**An origin down is neither a refusal nor a permission** — with `jobsnassaubahamas.com` (2026-09-16), `jobsstlucia.lc`, `jobsseychelles.sc` and `jobsantigua.ag` (2026-09-18) that is five hosts of one naming family on one 16-byte body: one operator, one origin down, by the shape of it — observed, not concluded. Not «closed»: the next control is 2026-09-21 (a deferred task of the session that measured).
