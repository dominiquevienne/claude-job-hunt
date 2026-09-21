# Board measurement — Endalia (a Spanish HCM/ATS, one tenant at a time): the tenants' portals are ASP.NET «selection portals» on `<tenant>.endalia.com` or the employer's own host (`/selectionportal/web/offersjob/…`, `/web/offersjob/offers.aspx`) — on 2026-09-21 the three a search engine names answer a 502 gateway, an Azure placeholder with a 404 on the list, and a written `Disallow: /`; nothing of a list was read; indeterminate, a measure to redo (#488)

<!-- verified: 2026-09-21 -->

<!-- hosts: portalempleonavantia.endalia.com, trabajaconnosotros.endalia.com, empleados-endalia.grupo5.net, career.endalia.com -->
<!-- script: none -->
<!-- countries: * -->
<!-- content: indeterminate · **2026-09-21 09:07–09:09 UTC, the declared client, the guard on the exact path, two reads each. `portalempleonavantia.endalia.com` (rules absent — open): `/` 200 ×2 (636 B, md5 9c4e9f75482f — «Azure Application Server 01 - ENDAZASP01 — Esta web no está disponible», a placeholder), `/web/offersjob/offers.aspx?y=CL` 404 ×2 (1 936 B, ASP.NET «The resource cannot be found»), the ad `/web/offersjob/offerdetails.aspx?offerID=…` 404; `trabajaconnosotros.endalia.com` (rules file not readable — open, certain False): `/`, `/selectionportal/homepage.aspx`, `/selectionportal/web/offersjob/homepage.aspx` 502 ×2 each, 183 B, md5 c3da608da097 (Microsoft-Azure-Application-Gateway/v2), 7 s apart; `empleados-endalia.grupo5.net` (Grupo 5's own host for the Endalia portal): `robots.txt` 200, 25 B, `User-agent: * / Disallow: /` — a written refusal, nothing under it read. `career.endalia.com` (rules read, open) is Endalia's own recruiting page — `/jobs`, `/jobs.rss`, `/jobs/<id>-<slug>`: the Teamtailor shape, not Endalia's product, and not a tenant of this family** · 2026-09-21 -->
<!-- witness: none — no list was read · 2026-09-21 -->
<!-- route: none · nothing served today on the two tenant hosts that do not refuse (a 502 gateway, an Azure placeholder with a 404 on the list), a written refusal on the third; a measure to redo — next control 2026-09-28 · 2026-09-21 -->

**Issue #488 (opened under #406, the ATS families). The premise of 13.09
(`www.endalia.com` open, «rien de connu ne bloque») concerns the vendor's
site; measured 2026-09-21 on the family's tenant hosts, named by the
signature `endalia.com/selectionportal` / `/web/offersjob` in a search
engine.** Rank: the pilot's order of 2026-09-21 06:13 UTC — #479 → #488
after the dated controls; GO of 09:04 UTC.

## What the family's hosts answer today

```
GET https://portalempleonavantia.endalia.com/                                   200 ×2 — 636 B «Esta web no está disponible» (an Azure app server's placeholder)
GET https://portalempleonavantia.endalia.com/web/offersjob/offers.aspx?y=CL     404 ×2 — ASP.NET «The resource cannot be found»
GET https://portalempleonavantia.endalia.com/web/offersjob/offerdetails.aspx?offerID=53CC…   404
GET https://trabajaconnosotros.endalia.com/  …/selectionportal/homepage.aspx  …/web/offersjob/homepage.aspx   502 ×2 each — 183 B, Azure Application Gateway
GET https://empleados-endalia.grupo5.net/robots.txt                             200 — User-agent: * / Disallow: /   (nothing under it read)
GET https://career.endalia.com/jobs                                             200 ×2 — Endalia's OWN careers, the Teamtailor shape (/jobs.rss, /jobs/<id>-<slug>); not this family
```

**A 502 and a placeholder are neither a refusal nor a permission** — the
portals behind them may list offers when their servers answer; the URL
shape a search engine still indexes (`offers.aspx?y=CL`, `offerdetails.aspx?
offerID=<64 hex>`) is what an adapter would read. Grupo 5's host refuses
in writing, and that host stays refused whatever the others do. Not
«closed»: **the next control is 2026-09-28** (deposited in the deferred
tasks); if a tenant host serves its list, the adapter follows — ASP.NET
WebForms, the list page and the `offerdetails.aspx` ad, two tenants.

Endalia's own recruiting on `career.endalia.com` is a Teamtailor site —
covered by `teamtailor.py`, not a measurement of this family.
