# Board measurement — KKTC Çalışma Dairesi (`calisma.gov.ct.tr`, Northern Cyprus): the Labour Department — a DotNetNuke site served over plain HTTP only (https closes the TLS handshake to the client and to curl), forms for foreign-worker employment permits and no vacancy list on its front (90 KB); rules unreadable (TLS, `certain: False`); no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: calisma.gov.ct.tr -->
<!-- script: none -->
<!-- countries: CYN -->
<!-- content: measured · **`https://` fails the TLS handshake on two reads (`SSL: UNEXPECTED_EOF_WHILE_READING`, 07:20:45–07:20:52 UTC) and to curl (exit 35); `http://calisma.gov.ct.tr/` answers 200 ×2 (89 639 B, md5 dcc118a0a4ba / 8705b2e55cde — a rendered element moves), a DotNetNuke portal («KKTC Çalışma Dairesi») whose front links its pages as `/ANASAYFA/PgrID/N/PageID/N` and carries the foreign-worker employment request forms (İSTİHDAM TALEP FORMU), no vacancy list, no count, no JobPosting; `_robots.allowed('calisma.gov.ct.tr','/')` → open, `certain: False` (`no-rules-tls`)** · 2026-09-18 -->
<!-- witness: none — the front lists no vacancy · 2026-09-18 -->

**Found by the Northern Cyprus search of #606 (a country never searched),
measured 2026-09-18 07:20–07:22 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #606: two searches in Turkish naming the Labour Department and the
private boards, no composed host names. *A measurement, not an adapter.*

The public labour administration of Northern Cyprus; its front is an administrative portal (work permits, forms), and whether it publishes vacancies on an inner page is unknown — the front does not link one by name.

```
_robots.allowed('calisma.gov.ct.tr', '/')   open, certain False (no-rules-tls)
GET https://calisma.gov.ct.tr/   TLS: UNEXPECTED_EOF_WHILE_READING ×2 (client), exit 35 (curl)
GET http://calisma.gov.ct.tr/    200 ×2 — a DotNetNuke portal, forms, no list
```

The adapter's first line: the portal's page tree (`PageID`) for a vacancy page, if any — over plain HTTP, which the plugin only does where the site offers nothing else.
