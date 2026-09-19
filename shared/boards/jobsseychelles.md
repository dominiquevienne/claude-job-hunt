# Board measurement — Jobs in Seychelles (`jobsseychelles.sc`, Seychelles): «discover real job opportunities in Seychelles» by its search snippet — Cloudflare answers 522 (origin unreachable) to the declared client twice and to curl on 2026-09-18, ~80 s each; nothing of the site was read; indeterminate, a measure to redo; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: jobsseychelles.sc -->
<!-- script: none -->
<!-- countries: SC -->
<!-- content: indeterminate · **the root answers 522 on two reads by the declared client (07:12:28→07:13:51 and →07:15:14 UTC; 16 B `error code: 522`, md5 2c2dae9e9cdd), the same 522 to curl — Cloudflare could not reach the origin; nothing read, rules not read (`_robots.allowed` → open, `certain: False`); the search engine's snippet is the only text known — reported, not measured** · 2026-09-18 -->
<!-- witness: none — nothing was read · 2026-09-18 -->
<!-- route: none · non faisable — décision du propriétaire du 18.09.2026 (un hôte muet reçoit un ticket adapter+blocked qui dit pourquoi et ce qui lèverait), #748 · 2026-09-19 -->

**Found by the Seychelles search of #617 (a country never searched),
measured 2026-09-18 07:10–07:17 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #617: one search naming the Ministry and the private boards, no
composed host names. *A measurement, not an adapter.*

```
_robots.allowed('jobsseychelles.sc', '/')   open, certain False (the rules file did not answer)
GET https://jobsseychelles.sc/   522 ×2 (client, ~80 s each), 522 (curl) — «error code: 522», Cloudflare's origin timeout
```

**An origin down is neither a refusal nor a permission** — the same bytes as `jobsstlucia.lc` an hour earlier and `jobsnassaubahamas.com` on 2026-09-16 (three Cloudflare-fronted island boards with the same 16-byte body: a provider's page, not the sites'). Not «closed»: the next control is 2026-09-21 (a deferred task of the session that measured).
