# Board measurement — Jobs in Dominica (`jobsindominica.com`, Dominica): Cloudflare answers 522 (origin unreachable) to the declared client twice and to curl on 2026-09-18, ~80 s each; nothing of the site was read — the sixth «Jobs <country>» island host on the same 16 bytes in two days; indeterminate, a measure to redo; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: jobsindominica.com -->
<!-- script: none -->
<!-- countries: DM -->
<!-- content: indeterminate · **the root answers 522 on two reads by the declared client (08:07:26→08:08:49 and →08:10:12 UTC; 16 B `error code: 522`, md5 2c2dae9e9cdd), the same 522 to curl — Cloudflare could not reach the origin; nothing read, rules not read (`_robots.allowed` → open, `certain: False`)** · 2026-09-18 -->
<!-- witness: none — nothing was read · 2026-09-18 -->
<!-- route: none · non faisable — décision du propriétaire du 18.09.2026 (un hôte muet reçoit un ticket adapter+blocked qui dit pourquoi et ce qui lèverait), #754 · 2026-09-19 -->

**Found by the Dominica search of #615 (a country never searched),
measured 2026-09-18 08:06–08:11 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #615: one search naming the Government portal and the private boards, no
composed host names. *A measurement, not an adapter.*

```
_robots.allowed('jobsindominica.com', '/')   open, certain False (the rules file did not answer)
GET https://jobsindominica.com/   522 ×2 (client, ~80 s each), 522 (curl) — «error code: 522», Cloudflare's origin timeout
```

**An origin down is neither a refusal nor a permission** — with `jobsnassaubahamas.com` (2026-09-16), `jobsstlucia.lc`, `jobsseychelles.sc`, `jobsantigua.ag` and `jobsstvincent.com` (2026-09-18) that is six hosts of one naming family on one 16-byte body: one operator, one origin down, by the shape of it — observed, not concluded. Not «closed»: the next control is 2026-09-21 (a deferred task of the session that measured).
