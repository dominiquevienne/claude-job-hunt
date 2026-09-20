# Board adapter — HR-Manager / Talentech Talent Recruiter (a Nordic ATS, one tenant at a time): the employer's positions by the JobPortal API its own career site calls on `api.hr-manager.net` — `take`/`skip`, `PositionCountCustomer` stated in every answer — and the advert by its permitted page on `candidate.hr-manager.net`; `hrmanager.py`, the hiring manager and the recruiters never emitted

<!-- verified: 2026-09-20 -->

<!-- hosts: api.hr-manager.net, candidate.hr-manager.net -->
<!-- host-forms: api.hr-manager.net, candidate.hr-manager.net -->
<!-- host-forms-basis: read — `hrmanager.py:HOSTS` names both literals and refuses any other host before the gate; the tenant is a path segment of the API (`/jobportal.svc/<alias>/`) and a `cid=` on the page host, never a subdomain, so the host forms are closed · 2026-09-20 -->
<!-- script: hrmanager.py -->
<!-- countries: * -->
<!-- content: measured · **three tenants with positions, 2026-09-20 13:3x–13:5x UTC, the declared client, the guard on the exact path first, each answer read twice. Rules: `api.hr-manager.net/robots.txt` 404 (no file, no rules — knowledge); `candidate.hr-manager.net/robots.txt` (200, 118 B, a BOM before the first line — read since #738): `User-agent: *` / `Allow: /ApplicationInit.aspx?` / `Disallow: /ApplicationInit.aspx?*SkipAdvertisement=True*` / `Disallow: /` — the advert page is permitted, the hosted list `/vacancies/list.aspx` and the application form are refused and never requested. The API `GET /jobportal.svc/<alias>/positionlist/json/?incads=0&take=50&skip=N` (200, JSON): Region Syddanmark `regionsyddanmark` 511 127 B ×2 same md5 with `incads=1` (the default 25 with the advert bodies), `PositionCountCustomer` 256, walked 6 calls of 50 → 256 emitted; Region Hovedstaden `regionh` 367 779 B ×2 same md5, 366 stated; KL `kl` 15 089 B ×2 same md5, 2 = 2; `take=` sets the page (50 honoured), `skip=` the offset (`PositionCountSkipped` echoes it); `top`, `pagesize`, `size`, `max`, `limit`, `page`, `pageindex` are ignored (measured on KL and Region Syddanmark); no single-position call found (`projectid=`, `id=`, `search=` do not select); an unknown alias answers 400 with `TransactionStatus.StatusCode 1` («Value cannot be null … connectionString»). The item: Id, Name, AdvertisementUrlSecure (`candidate.hr-manager.net/ApplicationInit.aspx?cid=&ProjectId=&DepartmentId=&MediaId=`), ApplicationFormUrl (`SkipAdvertisement=True`), dates as `/Date(ms+0200)/` (Published, LastUpdated, ApplicationDue, StartDate), WorkHours, PositionType, Department and DepartmentTree (Name, City, County, Country «Danmark», Address «Damhaven 12», Zip, POBox), PositionLocation, PositionCategory, Languages, fifteen CustomList/CustomText slots, and **ProjectLeader / ProjectParticipants / Users — the hiring manager with e-mail, telephone, title and a portrait URL (Region Hovedstaden fills them)**; the advert page `ApplicationInit.aspx?cid=198&ProjectId=237101&DepartmentId=6704&MediaId=5` (200, 70 724 B) is server-rendered: `h1.ProjectName`, `#AdvertisementInnerContent` (HTML, nested divs, the contact's name and e-mail in the prose), a `contact` block in a side column (name, title, telephone, portrait), the apply button to the refused form; no JobPosting** · 2026-09-20 -->
<!-- witness: the API's own `PositionCountCustomer` — `hrmanager.py jobs` prints it beside the emitted count on every walk · 2026-09-20 -->
<!-- route: http · 624 · 2026-09-20 -->

**Issue #467 (opened under #406, the ATS families). The premise of 13.09
(«directives hors de tout groupe» on `candidate.hr-manager.net`) was the
BOM before the first `User-agent:` — read since #738; verified 2026-09-20:
one group, `*`, the advert page permitted and the rest refused. Tenants
named by the signature `candidate.hr-manager.net/vacancies/list.aspx?customer=<alias>`
in a search engine (`regionsyddanmark`, `regionh`, `kl`, `eniro`,
`statensrekrutteringsloesning_tr`) — the same alias the API takes; three
measured, as the README's two-tenant rule asks.** Rank: the pilot's order
of 2026-09-20 12:5x, after #466.

## What HR-Manager is, and where its tenants live

HR-Manager (Talentech Talent Recruiter, Oslo/Copenhagen) is a Nordic ATS
— Danish regions, municipalities and the State's recruitment solution,
Norwegian and Swedish employers. The employer's own career site lists its
positions through the **JobPortal API**, `api.hr-manager.net/jobportal.svc/
<alias>/positionlist/json/` (also `/xml/`), a public feed keyed by the
customer alias and nothing else; the hosted list and the advert pages live
on `candidate.hr-manager.net`. **The user names the tenant by its alias**,
or by a list/API address that carries it.

## The route — the API for the list, the permitted page for the advert

```
GET https://api.hr-manager.net/jobportal.svc/regionsyddanmark/positionlist/json/?incads=0&take=50&skip=0     200 — 50 of 256 (PositionCountCustomer)
GET …?incads=0&take=50&skip=250                                                                           200 — the last 6
GET https://candidate.hr-manager.net/ApplicationInit.aspx?cid=198&ProjectId=237101&DepartmentId=6704&MediaId=5  200 — the advert (the `ad` command; permitted)
GET https://api.hr-manager.net/jobportal.svc/zzznosuchalias/positionlist/json/?…                           400 — StatusCode 1: no such tenant, exit 3
    https://candidate.hr-manager.net/vacancies/list.aspx?customer=…                                         NOT SENT — refused in writing (Disallow: /)
    …ApplicationInit.aspx?…&SkipAdvertisement=True                                                         NOT SENT — the form, refused in writing; the flag is dropped from any address given
```

`take=50&skip=N` walks to the stated count, bounded by that count's last
call; a call that repeats dies with 6. `incads=0` keeps the advert bodies
out of the list (511 KB for 25 with them); the advert is read from its
page, balanced across its nested divs. The page's `contact` block is
dropped whole when a template nests it in the content, and the text is
scrubbed. Two seconds between requests are ours; neither host writes a
Crawl-delay.

## What the adapter emits, and withholds

`jobs --tenant <alias> [--country-code ISO2] [--max-pages N]`: id, url
(the advert page), title, company, department, organisation, place
(PositionLocation or the department's city), region (county), country
(the department tree's country name mapped — «Danmark» → DK; a tree
without a country is stamped with `--country-code`, and the note says so),
category, position_type, work_hours, workplace, published, updated, closes,
starts (or «ASAP»), summary, languages. `ad --url`: id, customer_id, title,
description (scrubbed, 20 000 chars).

**Withheld:** `ProjectLeader*`, `ProjectParticipants`, `Users`,
`ProjectAdministratorId` — the hiring manager and the recruiters (names,
e-mails, telephones, portraits) — never emitted, not even as keys; the
department's street, postal code and PO box; the advert's contact block;
e-mail addresses and telephone numbers in the prose; the application form
never touched; `contacts_withheld` on every record.

## Tests and mutations

`AnATSWhoseJobPortalAPIPagesByTakeAndSkipStatesTheCustomersTotalAndNamesTheHiringManagerInEveryItem`,
both ways on fixtures (take/skip to the stated 56 over two calls, the
dates, the country from the tree and the stamp, the filter, the bounded
walk, a repeating call, the empty tenant, the unknown alias (400 / 1), the
advert page with a nested div and a nested contact block, the form flag
dropped from the address, a gone advert, a non-advert page, bad addresses,
other hosts refused, bad tenants). Mutation bench on a detached copy,
`python3 -B`, 10 / 10 red: the hiring manager emitted · the street emitted
· `skip` not advancing · a repeating call tolerated · the unknown alias
read as empty · dates left raw · the country filter dropped · the form flag
sent · the contact block kept · a nested div ending the advert. *The first
bench was green on the contact block: the guard's dump escaped «Cheflæge»
to `æ` — the withheld-strings check now dumps without ASCII escaping.*
