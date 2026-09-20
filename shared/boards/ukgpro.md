# Board adapter — UKG Pro, ex-UltiPro (an ATS, one tenant at a time): the tenant's job board on `recruiting.ultipro.com/<code>/JobBoard/<guid>` is permitted in writing and read; the list it loads lives under `JobBoardView/LoadSearchResults` — refused in writing to `*` (`Disallow: */JobBoardView`) — and `ukgpro.py` requests it only under the user's own `boards.ukgpro.override_robots: true` (#792, on #403); the opportunity page needs no key

<!-- verified: 2026-09-20 -->

<!-- hosts: recruiting.ultipro.com, recruiting2.ultipro.com -->
<!-- host-forms: recruiting.ultipro.com, recruiting2.ultipro.com -->
<!-- host-forms-basis: read — `ukgpro.py:HOSTS` names both literals and refuses any other host before the gate; the tenant is a path (`/<code>/JobBoard/<guid>`), never a subdomain, so the host forms are closed · 2026-09-20 -->
<!-- script: ukgpro.py -->
<!-- override: boards.ukgpro.override_robots — the user's own key, the general mechanism of #403 applied on #792 (2026-09-20); lifts the written `Disallow: */JobBoardView` on the list route only; the board and opportunity pages are permitted and read without it; cost: the user's own address · 2026-09-20 -->
<!-- countries: * -->
<!-- content: measured · **rules read (200): `User-agent: *` / `Disallow: /` / `Allow: */JobBoard/` / `Disallow: */JobBoardView` / `Disallow: */JobBoard/*/Styles` / `Disallow: */JobBoard/*/AnonymousSessionCheck` — the tenant's board page is permitted by the Allow, the list route it calls is refused; the board page `/HOL1002HPHM/JobBoard/be27b89b-…` (Macmillan; 200, 741 036 B, one read — the second read broke off at 523 351 B, an IncompleteRead) and `/UNI1076UNFI/JobBoard/86df2700-…` (UNFI; 200, 403 954 B ×2, md5 5bd3a01eacea / 6c0ae8917e89 — a token moves) are a Knockout application with no list in the markup, a `__RequestVerificationToken`, its settings in an inline script (`pageSize: 50`, `loadUrl: "/<code>/JobBoard/<guid>/JobBoardView/LoadSearchResults"`, `opportunityLinkUrl: "…/OpportunityDetail"`) and `initialFeaturedOpportunities` (a subset, one on Macmillan); the opportunity page `…/OpportunityDetail?opportunityId=ea9c0150-…` (permitted; 200, 94 017 B) carries the opportunity as JSON in `new US.Opportunity.CandidateOpportunityDetail({…})` — Id, Title, RequisitionNumber, FullTime, HoursPerWeek, JobCategoryName, Locations (Address with Line1, City, PostalCode, State, Country as alpha-3 «USA», Coordinates), PostedDate, UpdatedDate, Description (HTML), PayRange, criteria, `SupervisorName`; the bundle `site.min.js` (rec-cdn-prod.cdn.ultipro.com, no rules file, 3 115 955 B) builds the list request — `POST loadUrl` with `X-RequestVerificationToken`, body `{opportunitySearch: {Top, Skip, QueryString, OrderBy: [{Value: postedDateDesc, PropertyName: PostedDate, Ascending: false}], Filters: []}, matchCriteria: {PreferredJobs: [], Educations: [], LicenseAndCertifications: [], Skills: [], hasNoLicenses: false, SkippedSkills: []}}` — and reads `opportunities`, `locations`, `totalCount`, `initialTotalOpportunitiesCount`; no JobPosting; `_robots.allowed('recruiting.ultipro.com', '/HOL1002HPHM/JobBoard/<guid>')` → allowed, certain, rule `*/JobBoard/`; the list route falls under `Disallow: */JobBoardView` — a written refusal, honoured by every route (borne 1) and crossed only by the user's own key; no request was made under `JobBoardView/` by this repository** · 2026-09-20 -->
<!-- witness: none reachable by a permitted path — the count lives in the list's answer (`totalCount`), under the refused route; `ukgpro.py jobs` prints it beside the emitted count on a keyed run · 2026-09-20 -->
<!-- route: http · under the user's own `boards.ukgpro.override_robots: true` ONLY — the list route is refused in writing to `*` (2026-09-20); without the key `ukgpro.py jobs` requests nothing and exits 7 naming the rule and the key; with it the guard crosses and says so on every run (#403, applied on #792); `ukgpro.py ad` reads the permitted opportunity page with no key; no request was made under `JobBoardView/` by this repository — the key is the user's · 2026-09-20 -->

**Issue #463 (opened under #406, the ATS families). Tenants found by the
signature `recruiting.ultipro.com/<code>/JobBoard/<guid>` on 2026-09-20 (UNFI,
BMD, Macmillan, ARUP on `recruiting2`, Helix Electric, TridentCare),
measured by the declared client, the guard on the exact path first, two
reads of the board page; the decision on #792 (2026-09-20 12:5x UTC): the
adapter is built under the user's key, the general mechanism of #403.**
*The pilot's order of 2026-09-20 12:5x, after #793 and before #464.*

## What UKG Pro is, and where its tenants live

UKG Pro (Ultimate Software's UltiPro, merged into UKG) is a US HR suite
whose recruiting module hosts the employer's job board at
**`https://recruiting.ultipro.com/<code>/JobBoard/<guid>`** (or
`recruiting2.ultipro.com` for other tenants); an opportunity at
`…/JobBoard/<guid>/OpportunityDetail?opportunityId=<guid>`. The user names
the tenant as the board's address spells it — `UNI1076UNFI/86df2700-…` — or
gives the address itself; a tenant on `recruiting2` passes `--host`.

## The route — permitted page, refused list, the user's key

The rules file, verbatim (200, 2026-09-20):

```
User-agent: *
Disallow: /
Allow: */JobBoard/
Disallow: */JobBoardView
Disallow: */JobBoard/*/Styles
Disallow: */JobBoard/*/AnonymousSessionCheck
```

```
GET  https://recruiting.ultipro.com/HOL1002HPHM/JobBoard/be27b89b-…                          200 — the board's application: token, pageSize 50, loadUrl, one featured opportunity
GET  …/JobBoard/be27b89b-…/OpportunityDetail?opportunityId=ea9c0150-…                          200 — the opportunity as JSON (permitted, `ad`, no key)
POST …/JobBoard/be27b89b-…/JobBoardView/LoadSearchResults                                      NOT SENT — refused in writing; `jobs` without the key: exit 7, nothing requested
```

**Without the key `jobs` requests nothing — not even the permitted page**:
the gate is taken on the list route first, and the refusal quotes the rule,
the key to write and the file consulted. **With the key** — the user's own
line, in the user's own workspace, never set by `job-setup` — the guard
crosses (`kind: override`), prints the banner once per host and run (what is
crossed before what it costs), and the adapter reads the board page (its
token and cookies are the anti-forgery pair), then POSTs the page's own
request 50 a page, 2 s apart, `Skip` advancing to the `totalCount` the
answer states — bounded by that count's last page, a page that repeats
dies with 6. `ad` needs no key.

**Not exercised on the live list:** the key was absent on this machine, by
design, and it is not the developer's to set. The request body and the
answer's shape are the bundle's (`site.min.js`, read from the CDN, which
publishes no rules file); the first keyed run is the first measurement of
the list, and `totalCount` is its witness.

## What the adapter emits, and withholds

`jobs --tenant <code>/<guid> [--host] [--q] [--country-code ISO2]
[--max-pages N]`: id, url (the opportunity page), title, requisition,
category, full_time, featured, place · region · country (alpha-3 converted
by `_iso3`), locations (name, city, region, country), posted, summary
(scrubbed). `ad --url`: the same plus description (scrubbed, 20 000 chars),
updated, hours_per_week, salaried, closed, travel, pay_range (when the
tenant shows it), education, skills, experience, equal_opportunity.

**Withheld:** `SupervisorName` — the hiring manager, a person — never
emitted, not even as a key; the premises' street (`Line1`/`Line2`), postal
code and coordinates; descriptions scrubbed of e-mail addresses and
telephone numbers; `contacts_withheld` on every record; the application
(`QuickApply`, an account) never touched.

## Tests and mutations

`AnATSWhoseBoardPageIsPermittedButWhoseListRouteIsRefusedInWritingAndTakenOnlyUnderTheUsersOwnKey`,
both ways on fixtures (no key: nothing requested, exit 7 naming the key;
with the key: the page's own request, the token header, Skip 0 then 2 to the
stated 3, alpha-3 to alpha-2, street/postal/coordinates absent, the country
filter, the bounded walk, the empty board, a repeating pager, a page whose
`loadUrl` is another tenant's, a 404 tenant, the ad with the supervisor
withheld and the description scrubbed, other hosts refused). Mutation bench
on a detached copy, `python3 -B`, 8 / 8 red: the gate taken after the page ·
the token header dropped · alpha-3 kept · the country filter dropped · the
repeating pager tolerated · the supervisor emitted · the description not
scrubbed · the `loadUrl` check dropped.
