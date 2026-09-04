# Board adapter — Oracle Recruiting Cloud

<!-- hosts: per-tenant -->
<!-- script: oraclecloud.py -->
<!-- countries: * -->
One employer at a time, by host. **The biggest ATS family this repository did
not cover.**

Measured across twelve countries by a sibling session: `oraclecloud` is the
largest provider with no adapter — **164 cards of 2 838** — and one of only
four families (with `icims2`, `eightfold` and `taleo_careersection`) present in
**all twelve markets sampled**. That is precisely what the *reach* criterion in
this file's *Choosing which board to build next* section is for: it was picked
on a measurement across twelve markets rather than one.

**Verified against two live tenants on 2026-09-02.**

## Access

```
GET /hcmRestApi/resources/latest/recruitingCESites                  → career sites
GET /hcmRestApi/resources/latest/recruitingCEJobRequisitions        → the board
GET /hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails  → the text
https://<host>/hcmUI/CandidateExperience/en/sites/<segment>/requisitions/job/<id>
```

**No browser, no account, no key.** `robots.txt` on a tenant host is a **404** —
none published, nothing disallowed.

**The host is the tenant**: `ecwl.fa.us2.oraclecloud.com`,
`fa-etjg-saasfaprod1.fa.ocs.oraclecloud.com`. There is no directory; take the
host from a careers URL. A host that is not an Oracle Recruiting tenant answers
the Fusion **login page**, not an error, and the adapter says so.

**The whole board is reachable.** `limit=200` is served in full, and offset
1 425 of 1 428 returned the last three while 1 430 returned none. No window —
unlike `arbeitsagentur.md` (10 000 of 994 348) or `platsbanken.md` (2 100 of
39 865).

## Traps

**1. Without `expand=requisitionList`, the endpoint reports 1 428 jobs and
returns none of them.**

```
…&finder=findReqs;siteNumber=CX_1,limit=5
    → 200, TotalJobsCount 1428, requisitionList: []

…&expand=requisitionList&finder=findReqs;siteNumber=CX_1,limit=5
    → 200, TotalJobsCount 1428, requisitionList: 5 items
```

Valid JSON, HTTP 200, and **a large confident count attached to an empty
list**. A caller who trusts `TotalJobsCount` reports a board of 1 428; one who
trusts the list reports zero; **neither is told which they got**.

This is the pair that `never-fail-silently.md` now warns about in our own
output, met in a board: two counters of the same object that do not agree. The
adapter always sends the expand and treats *a non-zero count with an empty
list* as a hard error naming the parameter.

**2. `siteNumber` does nothing, and never says so.**

| Query | Jobs | First id |
| :-- | --: | :-- |
| `siteNumber=CX` | 1428 | 238677 |
| `siteNumber=CX_1` | 1428 | 238677 |
| `siteNumber=CX_2001` | 1428 | 238677 |
| `siteNumber=TOTALLY_BOGUS` | 1428 | 238677 |
| `siteNumber=` *(empty)* | 1428 | 238677 |

It looks like the parameter that picks which career site to read. **A value
that does not exist returns the same board as the right one**, so nothing
distinguishes a correct call from a typo.

So this adapter **does not claim site scoping**. It reports the tenant's
requisitions and says so on every run. `recruitingCESites` is a real directory
— `ecwl` declares *ClubCorp* and a copy of its old site — but the number is not
a filter.

**3. `Distance` is the posting date.**

On 100 of 100 requisitions the field named `Distance` held
`1788220800000.0` — `PostedDate` as a millisecond epoch, **the same value on
every row**, with no location search anywhere in the query.

It is not a distance. A reader who takes it for one gets a number that grows by
86 400 000 a day and sorts every ad by publication date while believing it is
sorting by proximity. It is emitted only as
`distance_field_is_the_posted_date`.

**4. The ad URL is not built from `siteNumber`.**

```
SiteNumber   SiteURLName        SiteName                        Status
CX           (null)             ClubCorp                        ACTIVE
CX_2001      (null)             FMOLHS Career Portal            INACTIVE
CX_3001      fmolhs-careers     FMOL Health Career Portal       ACTIVE
```

The public path is `SiteURLName` when the tenant has set one and `SiteNumber`
otherwise: ClubCorp publishes at `/sites/CX/`, FMOLHS at
`/sites/fmolhs-careers/` — **from a site whose number is `CX_3001`**. Building
the URL from the number alone produces a link that does not resolve.

And **the first site in the list is not necessarily the live one**: `eqtm`
lists its INACTIVE portal first. The adapter ranks by `StatusCode` then by the
presence of a URL name, and says when it did not take the first.

*(The first version of this adapter took `got[0]` and built URLs from
`SiteNumber`. Both were wrong on the second tenant tested, which is the
argument for testing two.)*

## What the record carries

Measured on 100 requisitions from one tenant.

| Field | Coverage | Note |
| :-- | --: | :-- |
| `Id`, `Title`, `PostedDate` | 100/100 | |
| `PrimaryLocation`, `PrimaryLocationCountry` | 100/100 | `"Irving, TX, United States"` |
| `secondaryLocations` | varies | Present on the second tenant; a multi-site ad |
| `ShortDescriptionStr` | 91/100 | **Equals the title on 88** — not a description |
| `JobFamily`, `JobFunction`, `JobType`, `JobSchedule` | **0/100** | Null on every row of this tenant |
| `LegalEmployer`, `Department`, `Organization` | **0/100** | Same |
| `PostingEndDate` | 0/100 | |

**The listing is an id, a title, a date and a place.** Everything that sounds
descriptive is null on the tenant measured — carried anyway, because another
tenant may fill them, and reported as absent rather than dropped.

**The description is in the details resource**, `ExternalDescriptionStr` —
5 823 and 5 896 characters on the first two ads — at **one request per job**.
`search` does not fetch it and says so; `read` does.
`ExternalQualificationsStr` and `ExternalResponsibilitiesStr` exist and were
empty on both.

## Verification

```bash
S=skills/job-scan/scripts/oraclecloud.py
python3 $S sites  --host eqtm.fa.us2.oraclecloud.com   # shows the INACTIVE first
python3 $S search --host ecwl.fa.us2.oraclecloud.com --limit 3
python3 $S read   --host ecwl.fa.us2.oraclecloud.com --limit 2
```

The URL is the thing to re-check on a new tenant, because a wrong one is a link
that 404s for the user rather than an error in the run:

```bash
python3 $S search --host eqtm.fa.us2.oraclecloud.com --limit 1
# → .../sites/fmolhs-careers/requisitions/job/…, not .../sites/CX_3001/…
```
