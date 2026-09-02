# Board adapter — SmartRecruiters

<!-- verified: 2026-09-02 -->

SmartRecruiters is an ATS, not a board. Each employer has its own board under a
**tenant token**, and its postings are public JSON — the same feed that renders
that employer's careers page. No key, no cookie, no browser.

**Everything here was verified against the live API on 2026-08-28**, against two
unrelated tenants: `nexthink` (103 postings, headquarters in Lausanne) and `sgs`
(4 387 postings, headquarters in Geneva).

Read by `skills/job-scan/scripts/ats.py`, the fourth provider alongside
Greenhouse, Lever and Ashby. It answers *"is my target employer hiring?"*, never
*"who is hiring near me?"* — see `greenhouse.md` for what this family is for.

## Why it was worth adding

`ats.py resolve` has been naming this ATS and then stopping since v1.7.0:

```
$ ats.py resolve "Nexthink"
'Nexthink' was found, but on an ATS this script does not cover:
  Nexthink -> smartrecruiters / nexthink
```

The resolver already knew the tenant. Only the reader was missing, so this is
the cheapest adapter in the repository — and it closes the most common dead end
the resolver produced. It now answers:

```
$ ats.py resolve "Nexthink"
{"provider": "smartrecruiters", "tenant": "nexthink", "company": "Nexthink"}
```

## Reading a board

```
https://api.smartrecruiters.com/v1/companies/<tenant>/postings   # the list
https://api.smartrecruiters.com/v1/companies/<tenant>/postings/<id>   # one ad
```

```
ats.py list --provider smartrecruiters --tenant nexthink --country ch
ats.py ad   --provider smartrecruiters --tenant nexthink --id 744000145952849
```

**The tenant is case-insensitive in the API path** — `nexthink`, `Nexthink` and
`NEXTHINK` all return the same 103 postings. The **public URL is not**: it uses
the employer's canonical capitalisation (`Nexthink`, `SGS`), which the payload
carries as `company.identifier`. Build URLs from that field, never from what the
user typed.

## The trap that has no answer

**A wrong tenant and an employer with nothing open are the same response.**

```
GET /v1/companies/nosuchtenantxyz/postings   ->  HTTP 200, {"totalFound": 0}
```

Not a 404. Greenhouse, Lever and Ashby all answer 404 on an unknown tenant; this
one does not, and **there is no second request that separates the two cases**:

- `/v1/companies/<tenant>` answers **404 for valid tenants too** — it is not a
  public endpoint, so it proves nothing.
- `careers.smartrecruiters.com/<tenant>` answers **200 for anything**, including
  `NOSUCHTENANTXYZ`.

**Re-tested 2026-09-02, and it is now byte-proven rather than asserted.** An
invented tenant and an employer that is not on this ATS return **the same 52
bytes, same md5 `9cfa41d4…`**:

```
nosuchtenantxyz → 200, {"offset":0,"limit":100,"totalFound":0,"content":[]}
bosch           → 200, byte-identical
visa            → 200, byte-identical
```

And the endpoint that could have separated them still refuses everyone:
`/v1/companies/<tenant>` answered **404 for `Nexthink` too** — a tenant whose
`/postings` returns 172 KB of live vacancies the same minute. **The response
headers carry nothing either**: no company or tenant field, and the only
differences between a real and a fake tenant are `content-length` and `vary`,
both artefacts of body size.

*What was not tested: a genuine SmartRecruiters tenant with zero open
postings. None was found to try. By construction it would return the same
paged empty list, but that is reasoning, not a measurement — so the claim
here is that **nothing distinguishes an unknown tenant from a non-tenant**,
which is measured, and that no second request is known to separate either from
a genuinely empty one.*

So the script refuses on zero rather than reporting an empty board, and says
both possibilities out loud. **Never report "they are not hiring" from this
board without confirming the token**, with `ats.py resolve` or the employer's
own careers URL. `bosch`, `visa`, `ubisoft` and `logitech` all return zero here
— none of them is out of vacancies; none of them is a SmartRecruiters tenant.

## Traps

**1. `limit` is silently clamped at 100.** Asking for 500 returns 100 with HTTP
200 — no error, no warning. Workday refuses an oversized page with HTTP 400,
which is the honest behaviour; this one does not, so a reader that trusts its
own `limit` silently sees a fraction of the board. Pagination via `offset` is
mandatory, and it works at depth (verified at `offset=4000` on SGS).

**2. The list feed carries no description at all.** Unlike Greenhouse's
`?content=true`, there is no flag: the description lives only on the per-ad
endpoint. `--with-description` therefore costs **one extra request per ad**, and
the script says so in its own `--help`.

**3. The ad is split across sections, and the one that matters most is not
`jobDescription`.** A posting's `jobAd.sections` holds `companyDescription`,
`jobDescription`, `qualifications` and `additionalInformation` — and
`qualifications`, which carries the must-haves the scoring reads, ran 1 627 to
2 256 characters on the ads sampled, entirely outside `jobDescription`. Taking
`jobDescription` alone loses the requirements while looking like a complete
read. Some boards add further sections (`videos` was observed), so the script
concatenates the four known ones **and then anything else it finds**.

**4. `country` and `city` want opposite capitalisation, and both fail
silently.** These are the only server-side filters in this adapter family:

| Filter | Form | Wrong form |
| :-- | :-- | :-- |
| `country` | lowercase ISO-2 — `ch` | `zz` returns **0**, HTTP 200 |
| `city` | **capitalised** — `Boston` → 17, `Callao` → 217 | `boston`, `callao` return **0**, HTTP 200 |

Verified on both tenants. A reader that normalises user input to lowercase — the
obvious thing to do — empties the board on `city` and works on `country`. The
script exposes `--country` only, because it is the one whose convention is
stable; filter towns locally with `--location`, which is accent-insensitive.

**5. Boards can be very large.** SGS carries 4 387 postings at 100 per page. The
script stops at 30 pages and says *"read 3 000 of 4 387 — narrow it with
--country"* rather than implying it read the board.

## What the feed gives that the siblings do not

`location` carries **separate `remote` and `hybrid` booleans**, plus
`fullLocation` (`Lausanne, VD, Switzerland`) and coordinates. That is a real
work-mode signal, unlike Workday's `remoteType`, which employers fill with a
workload. Both are recorded on the card. The per-ad payload also carries
`active`, a direct answer for `cover-letter` step 1b.

Everything on the list feed came back `visibility: PUBLIC` on both tenants;
whether a non-public posting can appear here was **not** established, so nothing
is filtered on that field.

## The ledger

```
smartrecruiters:<tenant>:<id>     e.g. smartrecruiters:nexthink:744000145952849
```

The tenant is lowercased in the key so that one board yields one row whatever
capitalisation the user typed, and the id alone cannot rebuild a URL without it.

## Applying

The employer's own SmartRecruiters flow, behind account creation. **The plugin
does not create accounts and does not fill credential fields** — hand the user
`apply_url` and their documents, as for any external ATS.

## Pace

One `list` per employer per run is a handful of requests. `--with-description`
multiplies it by the number of ads kept, so filter first and read descriptions
second.
