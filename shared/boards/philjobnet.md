# Board adapter — PhilJobNet (Philippines)

<!-- verified: 2026-09-02 -->

The Philippines' public employment portal, run by the Department of Labor and
Employment. **5 145 vacancies** on the day, ten to a page, employer named on
every card. **No key, no account, no browser.**

The **eighth national public employment service** in this repository, after
Switzerland, France, Spain, Germany, Ireland, Sweden and Singapore.

**Everything below was verified against the live site on 2026-09-02.**

## `?page=2` is accepted, ignored, and answers 200 with page one

```
GET /job-vacancies/          → ten ads
GET /job-vacancies/?page=2   → 200, ten ads — the same ten, same order
POST … __EVENTARGUMENT=Page$2 → ten ads, ZERO overlap with page one
```

The query-string form is the obvious way to paginate and it is a trap: an
adapter written on it **loops for ever over the same ten ads while reporting a
complete sweep**. Nothing errors. Nothing warns. That is the purest instance
of the failure `shared/never-fail-silently.md` exists to prevent, and this
board hands it to you on the first try.

**So the check that matters is not that a page answered 200 — it is that its
ids do not intersect the previous page's.** `philjobnet.py` compares every
page against the one before it, and **stops with exit 6 and a named reason**
if they overlap, rather than trusting the mechanism it just used. It applies
that test to its own postbacks too, because a stale `__VIEWSTATE` produces the
same symptom.

## The pagination is an ASP.NET WebForms postback

```
POST /job-vacancies/
  __VIEWSTATE, __VIEWSTATEGENERATOR, __EVENTVALIDATION   (from the last response)
  __EVENTTARGET   = ctl00$BodyContentPlaceHolder$GridView1
  __EVENTARGUMENT = Page$<n>
```

**The hidden fields are per response.** They must be harvested from the page
just received, not from the first one — replaying a stale pair is the other
way to end up back on page one, with a 200 and no complaint.

The pager offers pages 2–11 plus a *Last* link, so the depth is the result set
rather than a fixed ceiling.

## The anchor sits outside the card it belongs to

Found while writing the parser, and it would have corrupted every row
silently:

```
link  stockman-1460624          at byte 18 835
first <div class="jobcard">     at byte 18 942
```

**Each card's link precedes its block.** A parser that takes the link *inside*
a block gets the **next** card's id — so every row carries the right title
against the wrong ad. The first version did exactly that: `sales-clerk-1460623`
came back titled *STOCKMAN*, and the ad page says *SALES CLERK*.

**The slug encodes the title, so the pairing checks itself.** The card carries
`slug_matches_title`, true on 10 of 10 after the fix. If it ever goes false,
the anchor and the block have drifted apart again.

## The host: a certificate that stops every client, and no robots.txt

- **`www.philjobnet.gov.ph` presents Azure's default certificate** —
  `CN=*.azurewebsites.net`, with no SAN for the site's own name — so every
  client that verifies TLS refuses it. Over plain HTTP it answers **404**.
  **The apex is the service**: `philjobnet.gov.ph` answers 200 with the
  portal.

  This is the TLS case in `shared/robots-policy.md`, and it is the first time
  it has been exercised here: a certificate that does not cover the name stops
  a browser as surely as a script, so it looks like a dead host — and a plain
  request separates *expired identity* from *vanished service*. Three boards
  were written off wrongly on that basis before the rule existed.

- **`philjobnet.gov.ph/robots.txt` is a 404.** No file is published. Absent is
  not a refusal: `_robots.py` says so and the sweep proceeds at a human pace.

## What a card yields

Ten a page: title, employer, location down to the district, salary, education
level, employment type and a posting date.

```
STOCKMAN · SURPLUS MARKETING CORPORATION · CITY OF PASIG, NCR, SECOND DISTRICT
₱695.00 · Educ level not specified · Permanent · Posted on 9/2/2026
```

**The employer is named on every card** — this is a public service publishing
employers' own vacancies, not an agency board.

**Salary is a peso figure or the words "Salary not specified".** The card
carries `salary_text` as printed: a missing figure here is the board's own
silence, not a parse failure, and the daily-rate figures (₱695.00) sit beside
monthly ones without a unit field to tell them apart. **Read the string, do
not compute on it** until somebody has measured what the units are.

## Configuration

```yaml
boards:
  philjobnet:
    enabled: true
    pages: 5          # ten ads a page
    delay: 1.5
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `pages` | no | Ten ads a page. The sweep also stops on its own if a page repeats the previous one |
| `delay` | no | Seconds between postbacks, default 1.5 |

**There is no keyword parameter here yet.** The grid has search inputs and they
are WebForms controls like the pager; driving them needs the same postback
dance and has not been measured, so this adapter reads the board in order
rather than pretending to search it.

No credentials, no login, no browser.

## Zero-shaped answers

**1. `?page=2` returning page one, with HTTP 200.** The headline trap.

**2. A postback with a stale `__VIEWSTATE`** — same symptom, same silence.

**3. A card paired with the next card's id.** Invisible unless a slug is
checked against a title; `slug_matches_title` is that check, kept in the row.

**4. `www` refusing every client on a certificate** while the apex serves the
site.

**5. "Salary not specified" as a salary.** It is text, not a number, and it is
what the employer chose to publish.

## Applying

Through the portal's own *Apply now*, which asks for a PhilJobNet account.
**The plugin does not create accounts and does not fill credential fields** —
hand the user the ad URL and their documents.

## Pace

No published limit and no `429` over about 20 requests at 1.5 s apart. Each
page is one POST carrying a large `__VIEWSTATE`, so the sweep is heavier per
request than most here; ten ads a page means a hundred ads costs ten
round-trips.

## Verification

```bash
S=skills/job-scan/scripts/philjobnet.py
python3 $S search --pages 3          # 27 unique over 3 pages, no overlap
python3 $S ad --url "https://philjobnet.gov.ph/job-vacancies/job/sales-clerk-1460623"
```
