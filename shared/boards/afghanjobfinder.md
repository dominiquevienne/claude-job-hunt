# Board measurement — Afghan Job Finder (`afghanjobfinder.com`): «Launching Soon — Premier Job Portal in Afghanistan» — on 2026-09-17 the TLS certificate does not verify for the declared client and the page behind it is a 6 KB launch notice; not a board yet

<!-- verified: 2026-09-17 -->

<!-- hosts: afghanjobfinder.com -->
<!-- script: none -->
<!-- countries: AF -->
<!-- content: indeterminate · **the declared client's TLS handshake fails (`CERTIFICATE_VERIFY_FAILED`, twice); with verification disabled — a control only, never a route — the root is a 6 149 B «Launching Soon» page; the search engine's title says the same; no rules file could be read (absence of rules, `certain: False`); nothing to list** · 2026-09-17 -->
<!-- witness: none — a launch page · 2026-09-17 -->

**Found by the Afghanistan search of #613 (the private boards beside
`jobs.af`, which the country page already carries), measured 2026-09-17
13:38–13:39 UTC by the declared client, the guard on the exact path first,
`bin/fetch-body.py`, two reads.** The method is written on #613: two
searches (the NGO coordination body's portal, which the first Afghan
portal grew from; and the portals the engine returns by name), no composed
host names. *A measurement, not an adapter.*

```
GET https://afghanjobfinder.com/   SSL: CERTIFICATE_VERIFY_FAILED ×2 (the declared client verifies certificates)
curl -k                             200, 6 149 B — «Launching Soon» (a control reading, not a route)
```

**Not a board today**: a portal announced, not published. No issue; a later
reading decides whether it launched and whether its certificate is fixed.
