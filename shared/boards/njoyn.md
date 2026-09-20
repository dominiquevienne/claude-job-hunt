# Board measurement — Njoyn, by CGI (an ATS, one tenant at a time): the tenant's job list on `clients.njoyn.com/<pool>/xweb/xweb.asp?page=joblisting&CLID=<id>` is served once to the declared client, then Radware's bot manager answers a captcha page to every further request — a challenge, consigned (borne 2) — while a connected tab is served whole; a browser route, no script

<!-- verified: 2026-09-20 -->

<!-- hosts: clients.njoyn.com -->
<!-- script: none -->
<!-- countries: * -->
<!-- content: measured · **rules read (200, 369 B): ten named bots each closed with `Disallow: /` — `claudebot` among them, `claude-user` not named and no `*` group, so the guard sweeps under `claude-user` (the owner's decision of 2026-09-07: the group naming one token does not bind the other); no Crawl-delay. Transport, 2026-09-19 23:47–23:57 UTC, the declared client: the FIRST request (`/cl4/xweb/Xweb.asp?page=joblisting&CLID=71850`, CNSC) answered 200, 32 764 B — a classic ASP table (Job Number, Job Title, City, Posting Date, Closing Date; 10 rows, «Page 1 of 1», 20 `page=jobdetails` links); the second request of the same URL ten minutes later and every request after it (CIBC Mellon `cl2 … clid=51330`, York Region `cl2 … clid=60295`) answered 200 with 15 085 B of «Radware Captcha Page» («your activity and behavior on this site made us think that you are a bot») after a redirect to `validate.perfdrive.com` carrying our User-Agent — a bot-manager challenge, moving md5 (427ef0ffa8af, 32421a4b4d8d, 92cc4722acec, 9d2cf3e4747f, 479e510983d2), never defeated, nobody asked to. A connected tab, 2026-09-20 00:0x UTC: CNSC served — 10 postings, «Page 1 of 1»; CIBC Mellon served — 14 postings, «Page 1 of 1»** · 2026-09-20 -->
<!-- witness: the list's own «Page 1 of 1» and its rows — read in a tab: CNSC 10, CIBC Mellon 14 on 2026-09-20 · 2026-09-20 -->
<!-- route: browser · 24 · 2026-09-20 -->

**Issue #461 (opened under #406, the ATS families). Tenants found by the
signature `clients.njoyn.com/<pool>/xweb/xweb.asp?…CLID=<id>` on
2026-09-19 (the Canadian Nuclear Safety Commission `cl4/71850`, CIBC Mellon
`cl2/51330`, York Region `cl2/60295`, the City of St. Albert `cl4/67459`;
Queen's University and the City of Saint John on their own subdomains
`queensu.njoyn.com`, `saintjohn.njoyn.com`), measured by the declared client
and then in the user's own Chrome.** Rank: the pilot's order of 2026-09-18 —
#456 to #460, then #461; the pilot's order of 2026-09-20 puts the country
searches #764–#772 before #462.

## What Njoyn is, and where its tenants live

Njoyn is CGI's applicant-tracking system, used by Canadian public and
para-public employers. **The hosted list is
`https://clients.njoyn.com/<pool>/xweb/xweb.asp?page=joblisting&CLID=<id>`** —
the pool (`cl2`, `cl4`, `Corp`) and the client id name the tenant; some
tenants serve the same application on their own subdomain
(`<tenant>.njoyn.com/<pool>/xweb/…`). A posting is `…&page=jobdetails&jobid=…`
behind a session token (`tbtoken`) the list page issues.

## The route — served once, then challenged; a tab is served

```
GET …/cl4/xweb/Xweb.asp?page=joblisting&CLID=71850     200, 32 764 B — the CNSC table, 10 rows          (23:47:10 UTC, the first request)
GET the same URL                                        200, 15 085 B — «Radware Captcha Page»            (23:57:10 UTC, and every request after)
GET …/cl2/xweb/xweb.asp?clid=51330&page=joblisting      200, 15 085 B — the captcha                        (the client)
tab  the CNSC list                                      served — 10 postings, Page 1 of 1                  (2026-09-20)
tab  the CIBC Mellon list                               served — 14 postings, Page 1 of 1                  (2026-09-20)
```

**A captcha shown to the client is consigned, never defeated, and nobody is
asked to defeat it (borne 2)** — so no script: a script that renders a captcha
page renders nothing (#404). **The route is the user's own browser**, which
Radware serves without a challenge on both tenants tried: the list is a
table with the job number, title, city, posting and closing dates, and the
posting behind «View job details». Each page of the list ends with «Page N
of M». The rules name `claudebot` and close it; a request from here arrives
as `claude-user`, which no record names — the sweep is licit by the
owner's decision of 2026-09-07 and it is the transport, not the rules, that
closes the client after one request.

## What a browser route gives, and what it never gives

The tenant's open postings (number, title, city, posting date, closing
date) and each posting's page, in the user's Chrome; the count is the
table's own «Page N of M» and its rows. Never: the captcha (not solved, not
asked), the application (an account on the tenant's Njoyn), the
`JobMatchSubscription` alerts.
