# Board adapter — Vieclam24h (Vietnam)

<!-- verified: 2026-09-02 -->

<!-- hosts: vieclam24h.vn -->
One of Vietnam's largest boards, and **the richest per-ad record measured in
this repository**: 110 fields on the ad page, 69 on a search card. **No key,
no cookie, no browser** — every search page carries its own results in
`__NEXT_DATA__`.

`robots.txt` is **356 bytes of `text/plain`**, identical on the apex and on
`www`. It closes `/admin/`, `/taikhoan/` (accounts), `/asset/`, `/*?q` and two
jobseeker pages, gives `SemrushBot` and `AhrefsBot` a crawl delay, **names no
AI agent**, and **declares a sitemap index**.

**Everything below was verified against the live site on 2026-09-02.**

## The record carries other people's contact details, on every ad

Measured on 90 ads:

| Field | Filled |
| :-- | --: |
| `employer_info` (43 keys, including the board's own named account manager) | **90/90** |
| `contact_name` | **90/90** |
| `contact_email` | filled |
| `contact_phone` | filled |
| `contact_address` | filled |

**The five fields are not the same problem, and the reason differs by
field:**

- **`employer_info` is a leak.** It carries the board's own account manager —
  an intermediary's internal staff data, **not in the advert, not addressed to
  the candidate**. It has no business anywhere near a ledger.
- **`contact_name`, `contact_email`, `contact_phone` and `contact_address` are
  the contact the employer published so that candidates would use it.**
  Applying through them is the intended use. They are excluded here for a
  different reason: **proportion, not leakage** — a mass sweep records
  hundreds of ads the person will never apply to, and a named recruiter's
  direct line does not need to sit in a local file for each of them. The
  person gets them at the ad, at the moment they apply.

A rule written from the leak alone would strip exactly what the employer put
there for the reader; a rule written from proportion alone would miss that one
of the five was never addressed to anyone outside the board. **Both reasons
land on the same card here, and they will not always.**

*(Whether a pipeline ledger should hold a named recruiter's details at all,
for ads nobody applies to, is a question for `shared/pipeline-format.md` and
is not settled by this file.)*

**And the card is an allow-list, not a deny-list — for a reason about failure
modes rather than about these fields.** An allow-list that is too narrow
produces a **missing field**: visible, and fixed in one line. A deny-list that
is too narrow produces a **leak**: invisible, and found by somebody else. When
two errors are possible, prefer the one that announces itself — the same
asymmetry as `_robots.py` passing on an unreadable file rather than inventing
a refusal.

**So:** `KEEP` in
`skills/job-scan/scripts/vieclam24h.py` names the sixteen fields the card may
carry, and nothing else is copied out of the payload — **a field added
tomorrow cannot leak through it**.

That distinction was earned rather than assumed: the obvious design is to drop
`employer_info` by name, and it would have **left `contact_email`,
`contact_phone`, `contact_name` and `contact_address` behind** — four of five.

**Nothing is lost by it.** Applying goes through the ad URL, where the
employer publishes what it chose to publish, to a person who is applying.

## Count the salary on values, not on keys

| | |
| :-- | --: |
| `salary_min` / `salary_max` **present as keys** | **90/90 — 100%** |
| carrying a **real figure** | **89/90 — 98.9%** |

The gap is one ad. The habit is the point: the same slip has been worth 80
points elsewhere in this repository — `baseSalary` on jobs.ch is a shell on
three quarters of ads, and `salary_shown` on Kalibrr is true on 88% of ads of
which four fifths carry nothing.

`salary_unit` was **0 on 90 of 90**, and what the code means is **not
established**; the amounts — 8 to 15 million against Vietnamese salaries — are
consistent with VND per month, which is an inference and is written here as
one. The card carries the raw pair and `salary_stated`.

## A bare request is refused and an ordinary browser is not

```
curl -A '<browser UA>' …/…id3054296.html                → 403
the same URL with Accept and Accept-Language            → 200
```

**This is header sniffing, not a bot wall.** Nothing in `robots.txt` refuses
the path, and the 403 disappears when the request looks like what a person's
browser sends. The script sends those two headers and nothing more.

Worth separating from the other 403s in this repository: `cadremploi` and
`figaro-emploi` refuse **every** scripted request including `robots.txt`
itself, which is a client filter above the browser layer. This one answers a
normal request normally.

## Reading

```
GET /tim-kiem-viec-lam-nhanh?q=<terms>&page=<n>
    → props.initialState.api.getJobList.data
      30 items a page, with `total_items` and `last`
GET /<slug>id<id>.html
    → props.initialState.api.jobDetailHiddenContact.data — 110 keys
```

*ke toan* (accounting) returned **973 matches across 33 pages** of 30.

**The ad URL's category segment is optional.** The sitemap writes
`/<category>/<slug>id<id>.html` and the search card carries no category —
but `/ke-toan-ban-hangid200897251.html` answers **200 without redirecting**,
so the card builds the short form rather than spending a request to learn the
category.

## The sitemap, and what to count in it

`robots.txt` declares `/file/sitemap/sitemap-index.xml`, which names **12
families** on a CDN host: `job`, `employer`, `blog`, and nine of search
landing pages — `nganhnghe` (occupations), `tinhthanh` (provinces),
`quanhuyen` (districts), `sub-occupation` ×6, `level-occupation`.

**Only the job family is ads.** `job-0.xml` points at four files:

```
tintuyendung-0..3.xml → 4 180 + 4 282 + 4 373 + 4 254 = 17 089 ad URLs
```

Counting every family would report a much larger board made mostly of search
pages — the same arithmetic that would have inflated Jobstore fivefold.

## Configuration

```yaml
boards:
  vieclam24h:
    enabled: true
    searches:
      - keyword: "kế toán"
    pages: 2
    delay: 1.5
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `searches` | no | `keyword` → `q=`. Without one the sweep is the unfiltered board |
| `pages` | no | 30 ads a page; the payload states `last` |
| `delay` | no | Seconds between pages, default 1.5 |

No credentials, no login, no browser.

## Zero-shaped answers

**1. A 403 that is not a refusal** — send `Accept` and `Accept-Language`.

**2. A salary pair present on every ad and empty on one in ninety.** Read the
value.

**3. A sitemap index whose families are mostly search pages**, not ads.

**4. `salary_unit: 0` on every ad**, meaning unestablished.

**5. And the one that is not an error at all: 110 fields, of which sixteen
belong in a ledger.** The richest record here is also the one that most needs
an allow-list.

## Applying

Through the ad URL, in the user's own browser. **The plugin does not create
accounts and does not fill credential fields** — and it does not carry the
recruiter's phone number into a local file on the way.

## Pace

No published limit and no `429` seen over about 30 requests at 1.5 s apart.
The search page is ~113 KB and carries 30 ads, so a sweep is cheap in requests
and moderate in bytes.

## Verification

```bash
S=skills/job-scan/scripts/vieclam24h.py
python3 $S search --keyword "ke toan" --limit 2     # 973 matching, 33 pages
python3 $S ad --url "https://vieclam24h.vn/ke-toan/ke-toan-tong-hop-c17p73id3054296.html"
python3 $S sitemap --limit 3
```
