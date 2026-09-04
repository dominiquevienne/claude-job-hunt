# Board adapter — LMIS Jamaica (Ministry of Labour and Social Security)

<!-- verified: 2026-09-03 -->
<!-- hosts: lmis.gov.jm -->
<!-- script: lmisjm.py -->

Jamaica's Labour Market Information System. **No key, no cookie, no browser** —
the page renders client-side and the endpoint behind it answers a plain POST.

**Sixteen live vacancies on the day**, and that is the whole board: one request.

## The permission is accidental, and that does not make it less real

`robots.txt` is **Drupal's shipped default** — 22 `Disallow` lines, every one
administrative (`/node/add/`, `/user/`, `/search/`). **Nothing in it concerns
the vacancies**, and the paths this adapter reads come back `allowed=True`.

**The symmetry with `empleate.gob.hn` is the point.** There, a file copied
verbatim from Google's documentation **forbids** the vacancies. Here, a file
shipped with a CMS **allows** them. **Neither operator wrote the rule that
decides**, and the position does not change with the direction: an accidental
permission is still a permission.

**But it is not a welcome.** It is an absence of objection — so this adapter
fetches **once**, takes everything, and does not come back. And it asks the
module every run rather than recording the verdict: **the day an operator
writes their own file is the day a transcription would be wrong.**

## The endpoint accepts every parameter and filters on none

```
POST /api/job/listing   {"offset": 0, "limit": n}
    → 200 application/json   {"count": "16", "data": [...]}
```

Measured 2026-09-03:

| Sent | Returned |
| :-- | :-- |
| `{"job_title": "counsellor"}` | count 16, **all 16 rows** |
| `{"skills": "Communication"}` | count 16, **all 16 rows** |
| `{"job_title": "zzzznothing"}` | count 16, **all 16 rows** |

**`job_title` and `skills` are the site's own parameter names**, read out of
`job-search.js`. They are accepted and ignored.

> **A search that cannot fail is not a search.**

This is `job-room.md`'s `communalCodes` trap in its strongest form — there a
real commune code was silently ignored; here **every** filter is. So
`lmisjm.py` **offers no filter to the endpoint** and narrows after the fetch,
which costs nothing on a board of sixteen.

## What sixteen ads let you say, and what they do not

| | |
| :-- | --: |
| Ads | **16**, and `count` agrees with the rows |
| Distinct employers | 6 |
| Expired but still listed | **0 of 16** |
| `location`, `skills` filled | 16 of 16 |
| `job_status` | `"1"` on **16 of 16** — constant, and a string |
| `author` | empty on 16 of 16 |
| Ads outside Jamaica | **1** — a US Navy posting at Guantánamo, `CU` |

**`count` is a string, not a number** (`"16"`). **And `date` is relative
prose** — *"2 days 16 hours ago"*, *"3 weeks 2 days ago"* — not a date. The
card carries it as `posted_relative` and never parses it: turning it into a
timestamp would invent a precision the board does not publish.
**`expiration_date` is ISO and is the only storable date here.**

**Zero expired of sixteen is measured and is not a property.** Sixteen is a
small sample, and a board that serves stale ads looks identical until it does.

**`job_status` is `"1"` on every ad**, so it distinguishes nothing — the
`estadoPlazoF` shape, at a smaller scale. Not emitted.

## The skills list carries HTML entities

*"Career Guidance &amp;amp; Counselling"* — the field is authored in a
rich-text widget, so `&amp;` reaches a ledger as `&amp;` unless somebody
unescapes it. Same shape as job-room's markdown escaping: **it looks like data
and it is markup that survived.** The card unescapes.

## There is no per-ad endpoint

`/jobs/detail/<id>` is client-rendered too — **30 999 bytes for 1 763 visible
characters, no `JobPosting`** — so `ad` finds its record in the listing, which
is one request for a board this size. **An id that is not in the listing is
gone, not hidden**: the listing is the whole board and there is nothing else
to ask.

## Configuration

```yaml
boards:
  lmisjm:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no login, no browser. **No search parameters, on purpose** —
see above.

## Zero-shaped answers

**1. Every filter accepted and ignored.** The headline: a keyword that matches
nothing returns the whole board.

**2. `count` as a string**, so a numeric comparison against it needs a cast.

**3. A relative date** that looks like a field and cannot be stored.

**4. `job_status` constant on every ad.**

**5. `&amp;` in a skills list.**

**6. And a `--limit` run compared against `count`.** The first version reported
*"the endpoint states 16 and returned 3"* as a discrepancy when the 3 was the
limit — a false number that reads like a check, and **the third produced that
way in one session.** It now says it stopped and compares nothing.

## Applying

Through the ad URL, in the user's own browser. **The plugin does not create
accounts and does not fill credential fields.**

## Pace

**One request for the board.** Nothing here justifies a second.

## Verification

```bash
S=skills/job-scan/scripts/lmisjm.py
python3 $S search                      # 16, the whole board
python3 $S search --keyword counsellor # narrowed here, not by the endpoint
python3 $S ad --id 15276 --with-text
```
