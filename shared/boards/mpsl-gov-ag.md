# Board measurement — Ministry of Public Safety and Labour (`mpsl.gov.ag`, Antigua and Barbuda): a WordPress 7.1.1 ministry site with a «JOB OPPORTUNITIES — Browse Vacancies Today» banner and no vacancy link in its served markup; served to curl (200, 89 KB) while the declared client's TLS verification fails — the server sends its leaf certificate only, no intermediate (`unable to get local issuer certificate`); rules unreadable to the client (`certain: False`); no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: mpsl.gov.ag -->
<!-- script: none -->
<!-- countries: AG -->
<!-- content: measured · **`https://mpsl.gov.ag/` — the declared client fails TLS verification on two reads (07:29:48–07:29:55 UTC, `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`); `openssl s_client` shows one certificate in the chain (the leaf only, `verify error:num=21`), so a client that does not fetch the issuer by AIA cannot verify it; curl (with the platform trust store) reads 200, 88 838 B, md5 5d259fac00df, WordPress 7.1.1 — a ministry site (departments: police, fire, labour) whose front carries the banner «JOB OPPORTUNITIES Browse Vacancies Today Read More» and no `vacanc|job|labour|osec` link among its 30+ internal links; `http://` redirects 301 to https; `_robots.allowed('mpsl.gov.ag','/')` → open, `certain: False` (`no-rules-tls`)** · 2026-09-18 -->
<!-- witness: none — no list read · 2026-09-18 -->

**Found by the Antigua and Barbuda search of #620 (a country never
searched), measured 2026-09-18 07:29–07:34 UTC by the declared client, the guard
on the exact path first, `bin/fetch-body.py`, two reads.** The method is
written on #620: four searches naming the Government, the Labour
Department's One Stop Employment Centre and the private boards, no composed
host names. *A measurement, not an adapter.*

```
_robots.allowed('mpsl.gov.ag', '/')   open, certain False (no-rules-tls)
GET https://mpsl.gov.ag/   client: CERTIFICATE_VERIFY_FAILED ×2 (leaf only in the chain) · curl: 200, 88 838 B · http → 301 https
```

**The failure is the server's chain, not a refusal:** a browser completes the chain by itself and is served. Whether the ministry lists vacancies somewhere behind its banner is unknown — the served front does not link one. The adapter's first line: the banner's target (in a browser), then the list if there is one — over a route that verifies the chain the way a browser does, never by disabling verification.
