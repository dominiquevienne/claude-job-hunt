# Board adapter — HR.ge (six Georgian brands, one API)

<!-- verified: 2026-09-03 -->

<!-- hosts: api.p.hr.ge -->
<!-- script: hrge.py -->
**No key, no cookie, no browser.** Every brand's `robots.txt` is **109 bytes**,
`Allow: /`, names no AI agent, and declares a sitemap **on the platform's API
host**:

```
Sitemap: https://api.p.hr.ge/public-portal/tenant/<n>/api/v3/seo/sitemap
```

**The tenant number in that one line is the whole discovery.** And the ad page
completes it: `tenant/1`, `/2`, `/4` and `/5` all appear in a single ad's own
markup.

## Six tenants, and only four have ads

| Tenant | Host | `<loc>` | Advertisements |
| --: | :-- | --: | --: |
| 1 | `www.hr.ge` | 39 247 | **1 062** |
| 2 | `www.cv.ge` | 39 247 | **1 062** |
| 3 | `www.career.ge` | 38 185 | **0** |
| 4 | `www.doctor.ge` | 38 249 | 64 |
| 5 | `www.chefs.ge` | 38 345 | 160 |
| 6 | `www.bankers.ge` | 38 185 | **0** |

Tenants **7 upward answer `500`**, which is where the enumeration stops.

`hr.ge` and `cv.ge` are genuinely one corpus: identical `<loc>` counts and
**identical byte counts, 5 377 511**, differing only in the host they name.

## Three corrections to what this repository recorded, all the same shape

**1. 1 062 ads, not 39 247.** Of tenant 1's `<loc>` elements, **36 593 are
`/customer/` employer pages** and 1 505 are search landing pages. Counting the
file reports a board **thirty-seven times its size** — the arithmetic that
would have inflated Jobstore and Vieclam24h, and the reason
`shared/robots-policy.md` says *pull the files and count the URLs* rather than
*count the file*.

**2. `career.ge` has no ads at all.** It was recorded here as sharing hr.ge's
corpus, and it does — **because its own `robots.txt` declares `tenant/1`,
which is hr.ge's sitemap, while career.ge is tenant 3.** A brand pointing at
another brand's file, and a conclusion drawn from the file rather than from the
brand. Its own tenant publishes employer pages and **zero** advertisements, as
does `bankers.ge`.

**3. `doctor.ge` and `chefs.ge` were not known here** — vertical boards,
medical and culinary.

## The listing counts links, not ads

```
/jobs/today?p=<n>     8 pages × 100 links = 800
                      281 distinct advertisements
                      page 4 added ZERO new ones
```

**A factor of 2.85, and nothing on the page says so.** A sweep that reports
what it fetched claims three times the board. `hrge.py search` deduplicates and
**prints both numbers**, because only their difference exposes the padding.

**And the end of the listing is honest**, which is worth saying beside
`encuentra24.md`: page 50 returns **0 ads**, not page one again.

## The payload carries contacts the ad itself asks to hide

On the measured advertisement:

```
hideContactPerson: true
contactName / contactEmail / contactMobilePhoneNumber   all populated
```

**So the allow-list here is not tidiness — it is the publisher's own
instruction.** The record has **150 keys**, about forty of them Google Ads slot
configuration, and `KEEP` in `hrge.py` names the twenty a ledger has any use
for. Nothing outside it is copied, so a field added tomorrow cannot leak
through.

**And `similarAnnouncements` embeds other ads inside an ad.** A reader that
harvests every `announcementId` in the payload collects the neighbours — the
LinkedIn suggestion-block trap, in JSON. It is not read.

## Count the salary on values

`showSalary` is **false** and both bounds are `null` on the measured ad, while
`hideSalary` is a third field saying nothing. A "salary field present" count
would report 100%. The card carries `salary_stated`, computed from the values.

**The board also carries `drivingLicenses`** — the field
`shared/scoring-rubric.md` asks for and most boards do not have.

## The search endpoint exists, and its request shape does not

`POST …/api/v3/announcement-search` answers **`500` — *"Attempted to divide by
zero"*** to `{"page","pageSize"}`, `{"pageNumber","pageSize"}`,
`{"page","size"}` and `{"paging":{…}}` alike — **all four with an identical
279-byte body**, which is agreement produced by nothing having parsed. Guessing
further would be #72's fault. The listing works and is used instead; **this is
recorded so the next reader starts from the four that failed, not from
scratch.**

## Configuration

```yaml
boards:
  hrge:
    enabled: true
    tenants: [1]        # 2 is the same corpus under another brand
    delay: 0.8
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `tenants` | yes | 1 or 2 for the general board — **not both**, they are one corpus. 4 medical, 5 culinary. 3 and 6 have no ads |
| `pages` | no | The listing ends by returning nothing, and the sweep stops there |
| `delay` | no | Seconds between listing pages, default 0.8 |

No credentials, no login, no browser.

## Zero-shaped answers

**1. 39 247 `<loc>` read as 39 247 ads.** Thirty-seven times the truth.

**2. 800 links read as 800 ads.** Nearly three times.

**3. `career.ge` and `bankers.ge` answering with a full sitemap and no
advertisement.** A real state, not a parse failure — the adapter says which.

**4. A brand's `robots.txt` naming another brand's tenant.**

**5. `showSalary`, `salaryFrom`, `salaryTo`, `hideSalary` — four fields, and
the ad states no figure.**

## Applying

Through the ad URL, in the user's own browser. **The plugin does not create
accounts and does not fill credential fields** — and it does not carry the
recruiter's phone number into a local file on the way, least of all when the
advertisement asked for it to be hidden.

## Pace

No published limit and no `429` over about 40 requests. The API answers in
tens of kilobytes; a **listing page is 1.5 MB** and the sitemap **5.4 MB**, so
prefer the sitemap for enumeration and the API for reading.

## Verification

```bash
S=skills/job-scan/scripts/hrge.py
python3 $S tenants --check
python3 $S sitemap --tenant 5 --limit 3
python3 $S search --tenant 1 --pages 4     # 259 distinct from 400 links
python3 $S ad --url "https://www.hr.ge/announcement/491744/x"
```
