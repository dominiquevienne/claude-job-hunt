# Board measurement — Jobs St Lucia (`jobsstlucia.lc`, Saint Lucia): «new job openings added every morning» by its search snippet — Cloudflare answers 522 (origin unreachable) to the declared client twice and to curl on 2026-09-18, after 80 s each; nothing of the site was read; indeterminate, a measure to redo; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: jobsstlucia.lc -->
<!-- script: none -->
<!-- countries: LC -->
<!-- content: indeterminate · **the root answers 522 on two reads by the declared client (07:02:54→07:04:16 and →07:05:38 UTC, ~80 s each; 16 B `error code: 522`, md5 2c2dae9e9cdd), the same 522 to curl — Cloudflare could not reach the origin; nothing read, rules not read (`_robots.allowed` → open, `certain: False`); the search engine's snippet (entry-level to senior roles, Castries and Vieux Fort, alerts) is the only text known — reported, not measured** · 2026-09-18 -->
<!-- witness: none — nothing was read · 2026-09-18 -->
<!-- route: none · non faisable — décision du propriétaire du 18.09.2026 (un hôte muet reçoit un ticket adapter+blocked qui dit pourquoi et ce qui lèverait), #747 · 2026-09-19 -->

**Found by the Saint Lucia search of #619 (a country never searched),
measured 2026-09-18 07:01–07:06 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #619: two searches naming the Government's portal and the private boards,
no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('jobsstlucia.lc', '/')   open, certain False (the rules file did not answer)
GET https://jobsstlucia.lc/   522 ×2 (client, ~80 s each), 522 (curl) — «error code: 522», Cloudflare's origin timeout
```

**An origin down is neither a refusal nor a permission** — the same shape as `jobsnassaubahamas.com` on 2026-09-16. Whether a board answers when the origin is back is unknown today. Not «closed»: the next control is 2026-09-21 (a deferred task of the session that measured).
