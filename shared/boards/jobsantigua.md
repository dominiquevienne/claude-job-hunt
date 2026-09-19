# Board measurement — Jobs Antigua and Barbuda (`jobsantigua.ag`, Antigua and Barbuda): «current government vacancies refreshed regularly» by its search snippet — Cloudflare answers 522 (origin unreachable) to the declared client twice and to curl on 2026-09-18, ~80 s each; nothing of the site was read; indeterminate, a measure to redo; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: jobsantigua.ag -->
<!-- script: none -->
<!-- countries: AG -->
<!-- content: indeterminate · **the root answers 522 on two reads by the declared client (07:31:20→07:32:42 and →07:34:05 UTC; 16 B `error code: 522`, md5 2c2dae9e9cdd), the same 522 to curl — Cloudflare could not reach the origin; nothing read, rules not read (`_robots.allowed` → open, `certain: False`); the search engine's snippet is the only text known — reported, not measured** · 2026-09-18 -->
<!-- witness: none — nothing was read · 2026-09-18 -->
<!-- route: none · non faisable — décision du propriétaire du 18.09.2026 (un hôte muet reçoit un ticket adapter+blocked qui dit pourquoi et ce qui lèverait), #749 · 2026-09-19 -->

**Found by the Antigua and Barbuda search of #620 (a country never
searched), measured 2026-09-18 07:29–07:34 UTC by the declared client, the guard
on the exact path first, `bin/fetch-body.py`, two reads.** The method is
written on #620: four searches naming the Government, the Labour
Department's One Stop Employment Centre and the private boards, no composed
host names. *A measurement, not an adapter.*

```
_robots.allowed('jobsantigua.ag', '/')   open, certain False (the rules file did not answer)
GET https://jobsantigua.ag/   522 ×2 (client, ~80 s each), 522 (curl) — «error code: 522», Cloudflare's origin timeout
```

**An origin down is neither a refusal nor a permission** — the fourth «Jobs <country>» island host with the same 16 bytes today (`jobsstlucia.lc`, `jobsseychelles.sc`, and `jobsnassaubahamas.com` on 2026-09-16): one operator's family, one origin down, by the shape of it — observed, not concluded. Not «closed»: the next control is 2026-09-21 (a deferred task of the session that measured).
