# Board adapter — JOBBKK (Thailand)

Thailand's largest board by volume, and **the first Thai adapter here**. Plain
HTML, **no key, no cookie, no account, no browser**.

`robots.txt` is **275 bytes of `text/plain`** — checked as a MIME type, and
byte-identical on the apex and on `www`. It closes résumés, uploads, mail,
captchas, a demo tree and **`/jobs/apply/`**; it says nothing about the
listings and **names no AI agent**, for or against.

**Everything below was verified against the live site on 2026-09-02.**

## The listing is the payload

The site is a Next.js application, and its flight data carries **the complete
record for each of the 25 cards on a result page** — not a title and a link:

```
jobpost_id, company_id, company_name, position, detail (the duties text),
province_name, district_name, location, gmap_la, gmap_lo,
salary_start, salary_end, salary_not_show, job_format_type, employment_type,
occupation_sub_name, business_name, created_at, updated_at, date_up,
is_new_graduated, is_disability, is_online
```

So **one request buys 25 ads**, and a sweep costs one request per 25 rather
than one per ad. The ad page is worth reading only for a fuller address; the
duties text is already on the card.

```
GET /jobs/lists/<page>/หางาน,<keyword>,<province>,<category>.html
    → 200 text/html, ~1.2 MB, 25 cards
GET /jobs/detail/<company_id>/<jobpost_id>
    → 200 text/html, with an application/ld+json JobPosting
```

The path is Thai and positional: `หางาน` ("find work"), then the keyword, the
province — `ทุกจังหวัด` for all — and the category, `ทั้งหมด` for all.

## Past the end, the board serves the last page for ever

Measured on *โปรแกรมเมอร์* (programmer):

| Page | Result |
| --: | :-- |
| 4 | 25 cards, distinct |
| **5** | 25 cards, distinct — **the last real page** |
| 200 | **the same 25 cards as page 5** |
| 500 | the same 25 |
| 5 000 | the same 25 |

**No 404, no empty list, no error, no change of status.** A sweep that pages
until it gets nothing back never stops, and every page past the wall adds 25
duplicates it has already recorded. Verified by comparing id lists: pages 200,
500 and 5 000 overlap each other 25 of 25.

**The wall is per search, not global.** *บัญชี* (accounting) and the
unfiltered listing were still returning distinct pages at page 20. So the
depth is the size of that result set — 5 pages and 133 ads for *programmer* on
the day — and the adapter cannot hard-code it.

`jobbkk.py` therefore **stops when a page repeats the previous page exactly**.
That is the only end-of-results signal this board gives.

## And the page says "no results" while showing results

The Thai string *ขออภัยไม่พบตำแหน่งงานที่คุณค้นหา* — "sorry, we did not find
the position you searched for" — is in the served HTML of a page carrying 25
ads, inside a hidden template. **Never decide emptiness by searching for it.**
Count the cards.

## The date that is not the posting date

`created_at` and `updated_at` are both on every card, and they are years
apart. Over 133 ads from one search:

| | Years seen |
| :-- | :-- |
| `created_at` | **2010, 2012, 2013, 2016, 2018–2026** — only 42 of 133 in 2026 |
| `updated_at` | **2026 on 133 of 133** |

An ad created in 2010 was refreshed the day before it was read. The board
displays the refresh — `date_up`, and a label like *1 วันที่แล้ว* ("1 day
ago") — and a scorer that reads `created_at` as the posting date **ages a live
ad by up to sixteen years** and drops it as stale.

The card carries both, named for what they are: **`created`** and
**`refreshed`**. Read `refreshed`.

**The ad page agrees with `refreshed`, not with `created`.** On
`40904/844353` the JSON-LD `datePosted` is `2026-09-01` while the card's
`created` is `2022-11-17` — so the two surfaces are consistent once you know
which date each is showing, and `datePosted` on the ad page is the refresh.

## Salary — well filled, and one figure that must not be republished

**79 of 133 ads (59%) carried a stated range**, which is high for this
repository: Kalibrr manages 20%, IrishJobs 27%, the four StepStone sites zero.
`salary_start`/`salary_end` are `0` when nothing was stated — a zero, not a
null.

**But `salary_not_show` is the employer asking for the figure to be hidden,
and the payload sends it anyway.** Of 133 ads, 18 carried `"1"` — and **17 of
those 18 also carried an amount**. The site does not display them.

**This adapter does not emit them either.** When the flag is set the card
carries `salary_withheld: true` and no figure. Reading a field the operator
serves is fair; passing on one the operator was asked to hide is not, and the
difference costs nothing here — 17 rows out of 133.

*(The remaining values are `"0"` on 88 and empty on 27. The flag is not a
disclosure indicator and must not be read as one; it is only a suppression
request.)*

## The ad page

Twelve ads read, twelve `application/ld+json` `JobPosting` blocks:

| Field | Filled |
| :-- | --: |
| `title`, `hiringOrganization.name` | 12/12 |
| `jobLocation.address` — street, district, province, postcode | **12/12** |
| `datePosted` | 12/12 |
| `validThrough` | 12/12 |
| `employmentType` | 12/12, **`FULL_TIME` on all twelve** |
| `identifier` | 10/12 |
| `baseSalary` | **0/12** — absent, not empty |

Two cautions. **`validThrough` is a listing expiry, not an application
deadline**: the dates ran from 2026-12 to **2027-09**, up to a year out. And **the `description` is the duties block only** — 24 to 942 characters,
median 325 — while the rendered page for the same ad ran about 5 600
characters and also carried working hours, level, qualifications and benefits.
The structured description is a section, not the ad.

`employmentType: FULL_TIME` on 12 of 12 is a uniform value and should be
treated as a default until it is seen to vary; the card's own
`job_format_type` (*งานประจำ*, permanent) carries the board's own wording.

## The ad id and its URL

The id is the pair the URL is built from:

```
https://www.jobbkk.com/jobs/detail/<company_id>/<jobpost_id>
```

In the ledger: `jobbkk:<company_id>/<jobpost_id>`. Both halves are needed —
the job id alone does not resolve.

## Configuration

```yaml
boards:
  jobbkk:
    enabled: true
    searches:
      - keyword: "โปรแกรมเมอร์"      # Thai or English, as typed on the site
        province: "กรุงเทพมหานคร"    # optional; default ทุกจังหวัด (all)
    pages: 5
    delay: 1.5
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `searches` | yes | `keyword` is required per entry; it goes in the path, not a query string |
| `province` | no | Thai province name. Default `ทุกจังหวัด` — every province |
| `category` | no | Thai category name. Default `ทั้งหมด` — every category |
| `pages` | no | 25 ads a page; the sweep stops itself when a page repeats |
| `delay` | no | Seconds between pages, default 1.5. The pages are 1.2 MB each |

No credentials, no login, no browser.

## Zero-shaped answers

**1. The last page, repeated for ever.** Page 5 000 answers 200 with page 5's
ads. The only end signal is repetition.

**2. A "no position found" message inside a page of results.** A hidden
template, present in every page's HTML.

**3. `created_at` from 2010 on a live ad.** The board refreshes; the creation
date is not the age.

**4. `salary_start: 0` is "not stated", not "free".**

**5. A salary present under a suppression flag.** Withheld here by choice.

**6. `baseSalary` absent from the JSON-LD on 12 of 12** while 59% of cards
carry a range — the structured block is the poorer source, which is the
opposite of the usual arrangement and worth remembering.

## Applying

**`robots.txt` closes `/jobs/apply/`.** The plugin does not drive an
application on this board and does not fill any field there. Hand the user the
ad URL and their documents; applying is theirs, in their own browser.

## Pace

No published limit and no `429` seen over roughly 60 requests at 1.2–1.5 s
apart. The pages are 1.2 MB, so a sweep is heavy in bytes rather than in
requests — one page per 25 ads is already frugal. Keep `delay` at 1.5 s and
prefer a narrower search over a deeper one; the wall arrives on its own.

## Verification

```bash
S=skills/job-scan/scripts/jobbkk.py
python3 $S search --keyword "โปรแกรมเมอร์" --limit 3
python3 $S search --keyword "โปรแกรมเมอร์" --pages 8   # stops itself at the repeat
python3 $S ad --id 40904/844353
```
