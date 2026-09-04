# Board adapter — MyCareersFuture (Singapore)

<!-- verified: 2026-09-02 -->

<!-- hosts: api.mycareersfuture.gov.sg, www.mycareersfuture.gov.sg -->
<!-- script: mycareersfuture.py -->
<!-- countries: SG -->
Singapore's national job portal, run by the **Skills and Workforce Development
Agency (SWDA)** — Workforce Singapore renamed, which is why `wsg.gov.sg` now
lands on `swda.gov.sg`. The **seventh national public employment service** here
after Switzerland, France, Spain, Germany, Ireland and Sweden, and the first
adapter outside Europe.

Its API is the most open in this repository: **no key, no cookie, no account,
no browser**, no quota, and `robots.txt` is 87 bytes with an **empty
`Disallow:`** — everything permitted, served as `text/plain`.

**And yet this is the most restrictive adapter here**, because what SWDA
publishes freely it does not license you to keep. That constraint is first,
because it decides what the code is allowed to emit.

**Everything below was verified against the live service on 2026-09-02.**

## The constraint: read everything, store almost nothing

SWDA's terms of use (read in full 2026-09-02, page footer *last updated 27 Aug
2026*) contain **no anti-automation clause, no quota, no rate limit, and no
mention of the API at all**. Reading is not the problem. Two clauses are:

> "All rights reserved. No part of any works on the Website may be reproduced,
> stored in a retrieval system, or transmitted in any form or by any means,
> whether electronic, mechanical, photocopying, recording, or otherwise,
> without written permission from SWDA." — §15, repeated verbatim at §37

> "Except as set forth below, caching and links to, and the framing of this
> website or any of the User Content and/or Website Content is strictly
> prohibited." — §11, repeated at §33

**A pipeline ledger is a retrieval system, and it is a cache.** So:

**`mycareersfuture.py` emits identifiers, URLs and the fields a match is scored
on. It never emits the text of an ad.** The `description` is read to measure
its length and then dropped; the card carries `description_chars`. To read an
ad, open its URL — that is a visit, which §7 licenses ("a personal,
non-transferable, non-exclusive, non-sublicensable right and licence to access
and use the Services, and all Website Content therein").

`ad --print-description` exists for reading one ad **now**, on screen. It
prints to stderr and the file says what the terms say: do not write it
anywhere.

**§16 is titled "Restrictions on Use", and it is a prohibition, not a
procedure.** It opens no counter and describes no process: except as otherwise
provided, Website Content may not be reproduced, republished, uploaded, posted,
transmitted, adapted, modified, displayed or distributed without SWDA's prior
written permission, and its second paragraph extends that to images, video,
audio and programs. **The written permission is the exception to a ban, not a
facility on offer** — saying it "provides for permission to go further" reads
the clause from the wrong end.

**It has a twin at §38.** The document is written twice: clauses 3–21 bind
*Visitors*, 22–42 bind Singpass/Corppass users — the same doubling this file
already notes for §15/§37 and §11/§33. The adapter operates as a Visitor, so
**§16 is the governing clause and §38 its mirror**.

**And the terms name no written channel for the request.** Clauses 20 and 42,
"For Additional Information", give a telephone number only — no address, no
form. That does not make the request impossible; SWDA has other channels
elsewhere. It does mean the document describes no route, so nothing here should
suggest a signposted one. **Making the request is the user's decision, not the
plugin's**, and nothing here should be read as having made it.

*(This is a stricter reading than the one this repository applies to, say,
France Travail, whose API terms carry no such clause. The difference is in the
documents, not in the boards.)*

## The service

```
GET  https://api.mycareersfuture.gov.sg/v2/jobs?limit=100&page=0
     → 200 {"results":[…], "total":96869, "countWithoutFilters":96869, "_links":…}
GET  https://api.mycareersfuture.gov.sg/v2/jobs/<uuid>
     → 200, the same 29-key record for one ad
     → 404 {"message":"UUID is not found in the database."}
     https://www.mycareersfuture.gov.sg/job/<uuid>
     → the ad for a human; the slug is rebuilt client-side
```

`api.mycareersfuture.gov.sg` serves **no `robots.txt` at all** — `/robots.txt`
is a 404 in `text/html`. The rules live on the website host, and they permit
everything.

**The whole corpus is reachable.** Page 967 returned 78 rows and page 968
returned 0: **96 778 ads against 96 869 reported**, with no ceiling of the kind
Indeed and JobStreet impose. `limit` caps at **100 — 101 is already a 400**,
not 200.

## Filters: silent about names, loud about values

| Call | Answer |
| :-- | :-- |
| `?categories=Not A Category` | **400** — a real rejection |
| `?employmentTypes=Full Time` | 200, **71 850 of 97 091** — the filter works |
| `?employmentType=Full Time` | 200, **97 091 of 97 091 — silently ignored** |
| `?nonsense=zzz` | 200, the whole corpus, no complaint |
| `?sortBy=relevancy` | 400 (`new_posting_date` and `min_monthly_salary` are accepted) |

**A parameter name the API does not know is accepted, ignored and answered
200.** The singular of a plural filter therefore reads as a working search over
the entire board — a full result set, correctly parsed, that answers a question
nobody asked.

The response dissents, quietly: **`total` equals `countWithoutFilters` exactly
when nothing filtered.** Every filtered call in the script compares the two and
says on stderr whether the filter kept `n of m` or changed nothing. That
comparison is the whole defence, and it is why the script never passes a filter
it has not named in `FILTERS`.

## `Re-open` is a live status, and a shallow sweep never sees it

Forty ads drawn at random from the sitemap: **31 `Open`, 9 `Re-open`, 40 of 40
answering 200**. They are not stale rows.

They are, however, deep. The search is sorted newest-first by
`newPostingDate`, and status clusters with it:

| Page | Rows | Status | Posting date |
| --: | --: | :-- | :-- |
| 0 | 100 | `Open` 100 | 2026-09-02 |
| 200 | 100 | `Open` 100 | 2026-08-28 |
| 500 | 100 | `Open` 100 | 2026-08-20 |
| **800** | 100 | **`Re-open` 100** | 2026-08-11 |
| 960 | 100 | `Open` 100 | 2026-08-03 |
| 967 | **78** | `Re-open` 78 | 2026-08-03 |
| 968 | **0** | — | — |

**Code that keeps `status == "Open"` throws away a fifth of the board**, and a
sweep of the first few pages never notices, because the first few pages are all
`Open`. The card carries `status` and the adapter filters on neither.

## What a record gives — measured, not assumed

997 unique ads over ten pages, plus 500 more spread across pages 0, 50, 300,
700 and 900:

| Field | Filled |
| :-- | --: |
| `salary.minimum` / `maximum` | **997/997**, and **997/997 monthly** |
| `postedCompany.name` | 997/997 |
| `skills` | 997/997 |
| `ssocCode` (the national occupation code) | 997/997 |
| `description` non-empty | 997/997 |
| `metadata.expiryDate` — a real closing date | 997/997 |
| `minimumYearsExperience` | 100/100 present, **90 of them above zero** |
| `address.postalCode` | 597/997 (60%) |
| `flexibleWorkArrangements` | 8/100 |
| **`hiringCompany.name`** | **59/997, and 26/500 — about 5%** |

Median minimum salary **SGD 3 400/month**. `sourceCode` was `Employer Portal`
on 500 of 500 across the spread pages; an `ATS` value exists — one turned up in
a keyword search — so do not treat it as a constant.

**The weak field is the one that matters for dedup.** On ~95% of ads the only
company named is `postedCompany`, and on this board that is frequently a
staffing agency: the second ad returned for *chef* is posted by an HR advisory
whose own description says it is a recruitment firm. **No key of any kind
crosses to the employer's own ATS** — no apply host, no external reference,
nothing. This is the `michaelpage.md` problem rather than the `sozialinfo.md`
one, and it is structural: the field exists, it is simply not filled.

`minimumYearsExperience` deserves its own warning: it is present on every ad
and **zero on 10%**. Zero means entry level. Reading a missing value into the
zero drops the junior ads.

## The website tells you nothing about an ad

`https://www.mycareersfuture.gov.sg/job/<anything>` returns **HTTP 200,
`text/html`, 7 923 bytes** — the same React skeleton, whether the id is real,
malformed or absent. There is no 404 and no content: the page is assembled in
the browser.

Two consequences:

1. **Only the API can tell you an ad still exists.** `GET /v2/jobs/<uuid>` is
   404 with `{"message":"UUID is not found in the database."}` — the same 404
   for a malformed id and for one that has been taken down.
2. **The URL is rebuildable from the uuid alone.** `/job/<uuid>` loads and the
   app rewrites itself to the canonical
   `/job/<category>/<slug>-<uuid>` — confirmed in a browser on
   `000044467a0b9375302c967f0d840312`, which resolved to the F&B chef ad. The
   card therefore builds `/job/<uuid>` and never scrapes a slug.

## The sitemap over-declares, and the MIME type is what catches it

`sitemap-index.xml` names six sub-sitemaps. **Two of them are not sitemaps:**

| File | HTTP | `Content-Type` | Bytes | Job URLs |
| :-- | --: | :-- | --: | --: |
| `sitemap-1.xml` | 200 | `application/octet-stream` | 9.6 MB | 44 998 |
| `sitemap-2.xml` | 200 | `application/octet-stream` | 9.6 MB | 45 000 |
| `sitemap-3.xml` | 200 | `application/octet-stream` | 7.1 MB | 1 802 (+43 198 company pages) |
| `sitemap-4.xml` | 200 | `application/octet-stream` | 6.9 MB | **0** (45 000 company pages) |
| `sitemap-5.xml` | 200 | **`text/html`** | **7 923** | 0 |
| `sitemap-6.xml` | 200 | **`text/html`** | **7 923** | 0 |

7 923 bytes of `text/html` is the SPA skeleton again — the same page the ad
URLs serve. Six files × 45 000 would suggest 270 000 URLs; the truth is
**91 800 job URLs, 91 795 unique uuids**, and 88 198 company pages.

**Check the `Content-Type`, not just the status.** It is one test and it
catches three known traps in this repository: these two pseudo-sitemaps, the
Angular skeleton `kemnaker.go.id` serves for `robots.txt`, and
`my.indeed.com`'s 126 KB sign-in page returned as HTTP 200 (issue #64). A
`robots.txt` that is not `text/plain` is not a `robots.txt`; a sitemap that is
not XML is not a sitemap.

## Duplicates between pages

Reading ten consecutive pages of 100 gave **997 unique of 1 000**; five pages
read six seconds apart gave **499 of 500**. So roughly **0.2–0.3%**, and it has
a visible cause: the reported total moved from 96 775 to 97 067 between two
calls in the same minute. The corpus is being written to while you page it, and
a row can shift across a page boundary.

**An independent measurement on the same API found 897 unique of 1 000 — ten
times as much — and its paging protocol was not recorded.** Two measurements
that differ by a factor of thirty are themselves the finding: **the overlap is
a property of how you page, not of the board**, and neither number should be
quoted as *the* duplicate rate. Dedup on `uuid` and both cases are covered,
which is what the script does; do not expect a stable window.

## Configuration

```yaml
boards:
  mycareersfuture:
    enabled: true
    searches:
      - keyword: "software engineer"
        salary: 6000                 # minimum monthly SGD
      - keyword: "data analyst"
        employment_types: "Full Time"
    pages: 3                         # 100 ads a page
    delay: 1.0
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `searches` | yes | Each entry is one sweep; `keyword` maps to `search=` |
| `salary` | no | Minimum **monthly** SGD. 5 000 → 50 178 of 97 087 |
| `employment_types` | no | **Plural.** `Full Time`, `Part Time`, `Contract`… the singular is silently ignored |
| `position_levels` | no | Plural. `Manager`, `Senior Executive`… |
| `categories` | no | An unknown value is a 400, not a silence |
| `pages` | no | 100 ads a page; the corpus is 968 pages |
| `delay` | no | Seconds between calls, default 1.0 |

No credentials, no login, no browser.

## Applying

**Applying requires Singpass**, Singapore's national digital identity — the ad
page says *"Log in to Apply — you'll need to log in with Singpass to verify
your identity."* The plugin does not create accounts, does not hold national
identity credentials and does not fill them. Hand the user the ad URL and their
documents; they apply themselves, in their own browser, as themselves.

## Zero-shaped answers

**1. Past the end is a 200 with an empty list.** Page 968 and page 5 000 both
answer `{"results": []}`. There is no 404 and no error, so a loop that stops on
an exception never stops.

**2. An unknown parameter name is accepted and ignored**, with a 200 and the
whole corpus. Compare `total` with `countWithoutFilters`.

**3. Every ad URL on the website is a 200**, including the ones that do not
exist. Ask the API.

**4. Two of the six sub-sitemaps are HTML pages named `.xml`.** Check the MIME
type.

**5. `Re-open` looks like a dead status and is not.** A fifth of the board.

**6. `minimumYearsExperience: 0` is a value, not a gap.**

**7. The employer is unnamed on ~95% of ads** while a company name is always
present — the field that is filled is not the field you want.

## Pace

No published limit, no `429` seen, no quota in the terms. About 1 700 calls
were made while writing this file, at 1–1.5 s apart, and nothing throttled.
The default `delay` is 1.0 s and there is no reason to go below it: a full
sweep of the corpus is 968 calls, and nobody needs the whole corpus.

SWDA does reserve, at §18 and §40, "all rights to deny or restrict access to
this Website by any particular person, or to block access from a particular IP
address … at any time, without ascribing any reasons whatsoever". Keep the pace
human.

## Verification

```bash
S=skills/job-scan/scripts/mycareersfuture.py
python3 $S count  --keyword chef                                  # 2 049
python3 $S count  --keyword chef --employment-types "Full Time"   # 1 818 of 2 049
python3 $S count  --keyword chef --categories "Not A Category"    # 400, refused
python3 $S search --keyword "software engineer" --limit 2
python3 $S ad     --id 000044467a0b9375302c967f0d840312           # the F&B chef ad
```
