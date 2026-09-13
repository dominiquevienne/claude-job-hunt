# Board measurement — Pracuj.pl (`www.pracuj.pl`, Poland): a challenge to the declared client, a served tab, three counts on one page — and the pager closes on the one the listing is paged by

<!-- verified: 2026-09-13 -->

<!-- hosts: www.pracuj.pl, pracuj.pl -->
<!-- script: none -->
<!-- countries: PL -->
<!-- content: measured · **46 267 grouped postings — the pager closes at page 926 (925 × 50 + 17 on the last page, re-read), equal to the page's own `groupedOffersTotalCount: 46267`**; the same page states `offersTotalCount: 59534` (a grouped posting counted once per location) and, in its heading, «78 403 oferty pracy» = 59 534 + `jobCenterOffersCount: 18869` — three figures, three questions, none corrected into another; read from a connected browser tab (`fetch('/praca?pn=N')`, 16:21–16:22 UTC), the declared client answering 403 with a 5 696-byte «Just a moment...» whose md5 moves · 2026-09-13 -->
<!-- witness: the pager closing under the reader — page 925 carries 50 group ids, 926 carries 17, 927 and 928 carry 0 — and the arithmetic lands on the page's `groupedOffersTotalCount` to the unit; the heading's «78 403» is the sum of two other keys on the same page, checked by addition · 2026-09-13 -->
<!-- route: browser · 46267 · 2026-09-13 -->

**Poland's largest general board, the last #222 object without a
measurement.** Measured 2026-09-13 16:20 UTC (the declared client, twice)
and 16:21–16:22 UTC (a Claude-in-Chrome tab), the guard on the exact path
first (`*` open on `/praca`, `/praca?pn=2` and the advertisement shape,
`certain: True`).

## Rules, and a transport that challenges the client and serves the tab

```
robots.txt                 200, `User-agent: *` — 21 Disallow, all assets/account/files (`/_styles/`, `/konto/`, `/L/` …); no line touches /praca; 8 Sitemap: lines (SearchedOffers by city/title/region, CurrentOffers/SiteMapIndexJobOffers.xml); no Crawl-delay; no named AI crawler
identity("/praca")         http, claude-user — certain: True
GET /praca (declared)      403, 5 696 B, «Just a moment...» — twice at 16:20 UTC, md5 74b87540… then d8af227b…: same size, moving fingerprint, a Cloudflare challenge (the revolico/3amal family)
tab: /praca                200 «Oferty pracy – Pracuj.pl» — no challenge; 47 advertisement links in the DOM; __NEXT_DATA__ 174 105 characters
tab: fetch /praca?pn=1..3  200, ~680 kB each — 50 `groupedOffers` a page (groupId, jobTitle, companyName, lastPublicated, initialPublicated, expirationDate, salaryDisplayText, jobDescription …)
tab: fetch /praca?pn=925   200 — 50 group ids  ·  pn=926  200 — 17  ·  pn=927, 928  200 — 0 (142 694 B, the empty shell)
tab: fetch an advertisement   200, 321 531 B — one JSON-LD JobPosting (`<script id="job-schema-org" type="application/ld+json">`)
```

**The challenge is for the declared client alone**: the tab was served
without a challenge, borne 0 held, and nothing was asked of anyone. *The
challenge itself is where a script stops (borne 2); this card claims
nothing about what a browser passes without a person, because the tab did
not meet one.*

## Three figures on one page, and which one the pager counts

```
heading            «Praca - 78 403 oferty pracy»
__NEXT_DATA__      offersTotalCount 59534 · groupedOffersTotalCount 46267 · jobCenterOffersCount 18869
                   59 534 + 18 869 = 78 403   <- the heading, by addition
pager              925 pages × 50 + 17 = 46 267 = groupedOffersTotalCount   <- the walk, by the last page re-read
```

**The listing is paged by grouped postings** — one employer's posting
with several locations is one group (`groupId`, a uuid) and several
offers (`,oferta,<id>` per location: 62, 134 and 118 distinct offer ids on
pages 1–3 for 50 groups each, one promoted id `1004855013` on every
page). So the pager's arithmetic lands on 46 267 to the unit; 59 534
counts the same groups once per location; and the heading adds a
second inventory, the site's «JobCenter» offers (18 869), that the
listing under `/praca` does not page. **Three numbers, three questions**;
the route's figure is the one the pager closed on.

## The advertisement

A JobPosting in `<script id="job-schema-org" type="application/ld+json">`
— with **`@content` where `@context` is meant** (the site's own typo,
harmless to a reader that keys on `@type`) — title, description,
datePosted (`2026-08-24T16:19:06.547Z`), validThrough (`2026-09-23`),
employmentType as a Polish phrase («umowa o pracę, umowa zlecenie»),
hiringOrganization, industry, jobBenefits, responsibilities, jobLocation
{name, locality, region «śląskie», country «Polska», postalCode,
streetAddress}; `baseSalary` **null** on the one read (the listing's
`salaryDisplayText` was empty too). `__NEXT_DATA__` carries `offerId`,
`jobTitle`, `workModes[{code: full-office …}]`. Read on one.

## What the adapter would be — and why it is a browser route today

The rules are open and name no one; the transport challenges the
declared client. Under the 2026-09-07 doctrine that is the browser
branch: a session drives a tab, `fetch('/praca?pn=N')` 1.5 s apart until
a page carries no group, reads `groupedOffers` from each page's
`__NEXT_DATA__` (title, employer, both dates, expiry, salary text, a
description excerpt) and the JobPosting per advertisement. **Delivered
here as a measured route** (the owner's rule of 2026-09-13: browser
routes need no issue). A script would need the challenge to lift; the
8 sitemaps were not read (`CurrentOffers/SiteMapIndexJobOffers.xml` is the
one to try by HTTP first, since the challenge may not sit on it).

## What is not established

- **Whether the sitemaps are served to the declared client** — not
  fetched; if they are, an HTTP route exists and gets its `adapter` issue.
- **The full walk** — 926 pages read as four; the count is the pager's
  arithmetic on the last page, not a sum of every page's ids.
- **What «JobCenter» is** — 18 869 offers the heading includes and the
  listing does not page; a second product of the group, not read.
- **How often `baseSalary` is published** — null on one; the listing has
  `salaryDisplayText` per group, empty on the one read.
