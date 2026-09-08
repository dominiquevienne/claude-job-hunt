# Board assessment — Rocken (Switzerland): open by plain HTTP, and it never names the employer

<!-- verified: 2026-09-08 -->

<!-- hosts: rocken.jobs, www.rocken.jobs, de.rocken.jobs -->
<!-- script: none -->
<!-- countries: CH -->
<!-- content: measured · 6 105 advertisements, the number the site states in its own `<title>` (`Stellensuche Schweiz - 6104 offene Stellen auf Rocken.jobs`), and the pager closes on it exactly — 610 full pages of 10 plus a last page of 5 · 2026-09-08 -->
<!-- witness: 6 105, and it is the site's figure rather than a reader's; the count moved from 6 104 to 6 105 during the measurement itself -->

**Requested in #191, and the request's premises hold.** *Listing at `/jobs/`,
pagination `/jobs/page/<N>/`, no authentication, German first — each checked
rather than repeated.*

## Open by plain HTTP — no browser, no key, no cookie

```
GET /jobs/            200   700 807 bytes, as Claude-User
GET /jobs/page/2/     200
GET <ad url>          200   one JobPosting
```

**The rules permit and the transport agrees**, which is the case this repository
has seen least often today. *Guard taken on `/`, `/jobs/`, `/jobs/page/2/` and a
real advertisement path, on both `rocken.jobs` and `www.rocken.jobs`, in a turn
of its own before anything was fetched — `*` group present, no rule matching.*

**A third host form exists and is declared above:** *`de.rocken.jobs` appears in
the listing's own links.* **It was not fetched**, so nothing here describes it.

## The site states its own total, and the pager closes on it

```
<title>Stellensuche Schweiz - 6104 offene Stellen auf Rocken.jobs</title>

page   1  ->  10 advertisements        page 611  ->   5
page   2  ->  10, zero overlap         page 612  ->   0
                       610 x 10 + 5  =  6 105
```

**That total is the site's own field, not a count of what we parsed** — *the
figure #181 asks for.* **If the extraction broke, the `<title>` would still say
six thousand and "empty board" could not be confused with "I read nothing".**

**And the total moved while it was being measured: 6 104 at 09:24:41 UTC, 6 105
about three minutes later.** *The arithmetic closes on the later figure, which
is why it is quoted.* **A one-off against the earlier one is the board being
alive, not an error** — *and had the check been run once, the mismatch would
have looked like a defect in the pager.*

## Every advertisement carries a `JobPosting`

`title` · `hiringOrganization` · `jobLocation` · `datePosted` · `validThrough`
· `employmentType` · `occupationalCategory` · `description`

## The trap, and it is the reason this card ships before an adapter does

**`hiringOrganization.name` is `ROCKEN` on every advertisement.**

*The intermediary names itself where the employer belongs; the ads say
`unser Rocken Partner`, and #191 says so too.* **An adapter reading that field
would print one identical, plausible, wrong company on all 6 105 rows** —
Switzerland's entire inventory on this host, under a name that is not the
workplace.

> **This is the second host today with that exact shape.** *On `eshjob.com` all
> eighteen advertisement cards carry a poster link and all eighteen point at one
> account.* **Both would fail silently: the field is present, populated, and
> wrong.**

**So an adapter here must leave the employer EMPTY rather than fill it**, and
say why — *an absent employer is a measurement; `ROCKEN` on six thousand rows is
a fabrication.*

*The consequence for a candidate is in #191 and is not ours to solve: the
workplace cannot be researched before applying, and no deduplication against the
end employer's own ATS is possible.*

## What is not established

**No script ships.** *Under the owner's decision of 2026-09-08 — there is never
a reason not to use a board — that is a measurement owed and not a renunciation:
this host is open, structured and large, and what stands between it and an
adapter is work, not a refusal.*

**The `DDMMYY` in the slug was checked once, not verified.** *`-080926` against
`datePosted: 2026-09-08` on one advertisement — they agree.* **One case is not a
rule**, and #191 was right to flag that the slug date may be the date the slug
was minted.

**Nothing beyond page 1, page 2, page 611 and page 612 was read**, so the 10
per page is observed on four pages of 611.
