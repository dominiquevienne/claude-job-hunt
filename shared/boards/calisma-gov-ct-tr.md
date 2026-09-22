# Board measurement — KKTC Çalışma Dairesi (`calisma.gov.ct.tr`, Northern Cyprus): the Labour Department — a DotNetNuke site served over plain HTTP only (https closes the TLS handshake to the client and to curl), **and its five top-level menu entries carry no vacancy list**: work-permit forms, statistics, legislation and press releases. **Controlled again on 2026-09-22 — unchanged.** No adapter, and the reason is the site, not the route

<!-- verified: 2026-09-22 -->

<!-- hosts: calisma.gov.ct.tr -->
<!-- script: none -->
<!-- countries: CYN -->
<!-- content: measured · **the site answers in the clear and publishes NO list**; what would reopen it is a page of vacancies; it does NOT say the Department has no employment service, nor the country no public route. What the five menu entries carry instead: work permits, statistics, legislation, press releases. **`https://` fails the TLS handshake on two reads (`SSL: UNEXPECTED_EOF_WHILE_READING`, 07:20:45–07:20:52 UTC) and to curl (exit 35); `http://calisma.gov.ct.tr/` answers 200 ×2 (89 639 B, md5 dcc118a0a4ba / 8705b2e55cde — a rendered element moves), a DotNetNuke portal («KKTC Çalışma Dairesi») whose front links its pages as `/ANASAYFA/PgrID/N/PageID/N` and carries the foreign-worker employment request forms (İSTİHDAM TALEP FORMU), no vacancy list, no count, no JobPosting; `_robots.allowed('calisma.gov.ct.tr','/')` → open, `certain: False` (`no-rules-tls`)** — measured 2026-09-18; **CONTROL OF 2026-09-22 09:1x UTC, two reads: nothing has moved.** `https://` still fails the handshake (`SSL: UNEXPECTED_EOF_WHILE_READING`); `http://` answers 200 ×2, **89 639 B both**, md5 3c7ae412b06e / eae02e85422b (a DotNetNuke antiforgery token moves). The site's own menu has **five top-level entries** — ÇALIŞMA DAİRESİ MÜDÜRLÜĞÜ, BASIN VE HALKLA İLİŞKİLER, ÇALIŞMA DAİRESİ İSTATİSTİKLERİ, e-MEVZUAT, and the news pager `/ANASAYFA/PgrID/13073/PageID/1..10` — and **not one job-ad word appears anywhere in the page's text** (`iş ilan`, `ilan pano`, `açık iş`, `kadro`, `münhal`: zero). **Plain HTTP is a ROUTE, not a verdict** — the site is reachable and readable; what it does not carry is a list of posts. · 2026-09-22 -->
<!-- witness: none — the department publishes no vacancy list on this site; the control of 2026-09-22 read its whole menu · 2026-09-22 -->

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

## The control of 2026-09-22 (#718) — no adapter, and why

```
GET https://calisma.gov.ct.tr/   TLS handshake closed (UNEXPECTED_EOF), as on 2026-09-18
GET http://calisma.gov.ct.tr/    200 ×2, 89 639 B both — the department's site, read whole
    menu: ÇALIŞMA DAİRESİ MÜDÜRLÜĞÜ · BASIN VE HALKLA İLİŞKİLER · İSTATİSTİKLER · e-MEVZUAT
    job-ad words in the page text (iş ilan | ilan pano | açık iş | kadro | münhal): 0
```

**The route is fine and the content is not there.** *Plain HTTP is a route, not
a verdict*: the site answers, it is complete, it is readable — and what it
publishes is the Department's administration (employment-permit forms for
foreign workers, labour statistics, legislation, press releases), not posts to
apply for. **An adapter here would have nothing to emit**, and a script that
returns nothing does not count (#404).

**What would open it**, and it is a measurement rather than a hope: a page of
the Department's own carrying posts — the site's menu would name it, as it names
the four sections it has — or a separate host of the employment service that a
search surfaces. *Neither exists in this reading; the issue says so with its
date, and the control is the way it will be reopened.*

**What is NOT claimed:** that the Department has no employment service, or that
Northern Cyprus has no public route. This card measures one site on two days.
