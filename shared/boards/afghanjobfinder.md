# Board measurement — Afghan Job Finder (`afghanjobfinder.com`): «Launching Soon — Premier Job Portal in Afghanistan» — on 2026-09-17 the TLS certificate does not verify for the declared client and the page behind it is a 6 KB launch notice; not a board yet

<!-- verified: 2026-09-17 -->

<!-- hosts: afghanjobfinder.com -->
<!-- script: none -->
<!-- countries: AF -->
<!-- content: indeterminate · **the declared client's TLS handshake fails (`CERTIFICATE_VERIFY_FAILED`, twice); with verification disabled — a control only, never a route — the root is a 6 149 B «Launching Soon» page; the search engine's title says the same; no rules file could be read (absence of rules, `certain: False`); nothing to list** · 2026-09-17 -->
<!-- witness: none — CONTROL OF 2026-10-24 18:16–18:22 UTC (both clock readings taken in the same turn), and it CORRECTS the cause this card lets a reader infer: the handshake does NOT fail because the client cannot complete a chain. `openssl s_client -connect afghanjobfinder.com:443 -servername afghanjobfinder.com -showcerts` serves FOUR certificates and ends on `Verify return code: 0 (ok)`, so the chain is valid and complete; `curl` with its own store fails at `no alternative certificate subject name matches target host name 'afghanjobfinder.com'` (exit 60, `http_code` 000, `ssl_verify_result` 1). The certificate is valid for ANOTHER name, so every verifying client fails identically and no CA store, no pinned intermediate and no AIA fetch repairs it: on this host the TLS failure IS a fact about the host, and not a verdict of the client. Not «closed» and not a verdict at all: the verification-disabled control of 2026-09-17 read a 6 149 B «Launching Soon» page, so the host serves, and `content: indeterminate` with `certain: False` stands unchanged. Tool: curl 2>&1 and openssl s_client, never the declared client. -->
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
