# Board measurement — Jobs in Seychelles (`jobsseychelles.sc`, Seychelles): «discover real job opportunities in Seychelles» by its search snippet — Cloudflare answers 522 (origin unreachable) to the declared client twice and to curl on 2026-09-18, ~80 s each; nothing of the site was read; indeterminate, a measure to redo; no adapter yet

<!-- verified: 2026-09-21 -->

<!-- hosts: jobsseychelles.sc -->
<!-- script: none -->
<!-- countries: SC -->
<!-- content: indeterminate · **the root answers 522 on two reads by the declared client (07:12:28→07:13:51 and →07:15:14 UTC; 16 B `error code: 522`, md5 2c2dae9e9cdd), the same 522 to curl — Cloudflare could not reach the origin; nothing read, rules not read (`_robots.allowed` → open, `certain: False`); the search engine's snippet is the only text known — reported, not measured** — **second control 2026-09-21, 06:19:15 and 06:20:38 UTC: the same 522 twice — 16 B `error code: 522`, md5 2c2dae9e9cdd, the bytes of 2026-09-18; the origin is still unreachable behind Cloudflare, nothing read** · 2026-09-21 -->
<!-- witness: partial — CONTROL OF 2026-10-27 17:39–17:47 UTC on `jobsseychelles.sc`, and the « un hôte muet » half of the `route:` line below is PÉRIMÉE on the object: the root now SERVES. Two reads by the declared client (`Claude-User`, claude-job-hunt/1.256.0), the guard taken on the exact URL in a turn of its own: **200 — 111648 B at 17:44:12Z** and **200 — 111648 B at 17:46:55Z** — against **16 B of Cloudflare `error code: 522`, nothing read, on 2026-09-18 AND again on 2026-09-21**. The rules file is now READ with a 200 (`state: read`, `certain: True`) where a 522 is served on every path, `robots.txt` included. **RATE, because an absent `Crawl-delay` is NOT an absence of a rate limit — only a threshold nobody stated, and ~9 requests in 2 min 30 once raised an antirobot interstitial on a host that writes no delay:** this host writes NO `Crawl-delay` (`crawl_delay_s: null` in the provenance of both reads, and none rendered by the guard), so the cadence is OURS and it is recorded here — **3 requests in this control, one for `robots.txt` in the guard turn at 17:39–17:41 UTC then the root at 17:44:12Z and at 17:46:55Z, 2 min 43 s apart** — and nothing beyond the root was walked. **The `md5` MOVES between the two reads (71dc89b230ee → 5c319760e47e), so the body carries a per-request element and the SIZE is the stable witness here, never the fingerprint** — and no cross-host md5 comparison is valid for this family. NATURE, because a byte count names a SIZE and never a nature: WordPress 7.1.3 on the `superio` theme with `wp-job-board-pro`, i.e. a job board BY CONSTRUCTION (« Login as Candidate/Employer », « Post Jobs », « Find Jobs »), and the five hosts of this family carry the IDENTICAL set of eight plugins; but the ROOT serves an editorial guide with **0 `JobPosting` and 0 `ld+json` block**, so this verdict describes the ROOT and NOT the ad pages — the listing route is still TO BE ESTABLISHED and was deliberately not swept. **THE CLASSIFICATION DOES NOT MOVE, AND THAT IS BY DESIGN:** `classify()` reads `route_none_of()` FIRST and returns `infaisable` at once, and its own source says of `witness:` « which this function never reads » — so this line is a DETECTOR, not a reclassification, and nothing downstream (the page counter, `data-nonfaisable`, the ratio, the Atlas aggregate) can show it. **Do not « fix » `classify()` on the strength of this contradiction: it is sound.** Lifting a closure is the OWNER's decision (§2 sexies); measured under #1142 point 4 and carried there · 2026-10-27 -->
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

## The control three days on — the same 522 twice

```
GET https://jobsseychelles.sc/   522 ×2 by the declared client (06:19:15 and 06:20:38 UTC) — 16 B «error code: 522», md5 2c2dae9e9cdd, identical to 2026-09-18
```

**Three days later the origin is still unreachable, and the six island hosts
on these 16 bytes answer the same today** (jobsstlucia.lc, jobsseychelles.sc,
jobsantigua.ag, jobsstvincent.com, jobsindominica.com; jobsnassaubahamas.com
was not in this control). Nothing read, still not «closed»: #748 stays
`blocked` with this date; next control 2026-09-28.
