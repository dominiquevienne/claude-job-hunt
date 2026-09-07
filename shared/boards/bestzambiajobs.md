# Assessed, not a board — `bestzambiajobs.com` (a repurposed domain that kept its rules)

<!-- verified: 2026-09-07 -->

<!-- hosts: www.bestzambiajobs.com -->
<!-- script: none -->
<!-- countries: ZM -->
<!-- content: out-of-domain · HTTP 200 serving a Turkish sports-streaming page, its sitemap index pointing entirely at a 3rd domain, and 0 occurrences of `zambia`, `job` or `vacancy` — this host publishes no advertisements at all · 2026-09-05 -->
<!-- witness: none possible — the question is what the host SERVES, and no second source states that; the rules file states the opposite of the truth -->
<!-- hosts-source: named by a "best job sites in Zambia" listing — the same listing that named `gozambiajobs`, `jobsearchzm` and `jobzambia`; no hostname composed · 2026-09-05 -->

**This card exists because its absence was the argument of #162.** *The host was
published as an open Zambian board on 2026-09-05 and retracted fifteen minutes
later. **The retraction worked, and that is exactly why its provenance was
nowhere** — a discarded host left no trace, so the error rate of the listing
that named it could not be computed.*

**Nothing here is a new measurement.** Every figure below was taken on
2026-09-05 by another session and is quoted with its date;
`gozambiajobs.md` and `jobsearchzm.md` hold it.

## What it is

```
GET /            2026-09-05   HTTP 200
                 a Turkish sports-streaming page
                 sitemap index -> entirely a THIRD domain
                 0 occurrences of `zambia`, `job`, `vacancy`
GET /robots.txt  2026-09-05   the Cloudflare managed default, byte-identical
                 to the one `gozambiajobs.com` and `jobsearchzm.com` carry
```

**A Zambian-sounding name does not make a Zambian board**, and that was
established rather than assumed.

## It was classified three times in one day, and the first two were right

```
« refus gere »            <- a correct reading of its robots.txt
« ouvre au transport »    <- a correct reading of its HTTP code
« n'est pas un board »    <- the only one that asked what it SERVES
```

> **The first two came from correct measurements on the wrong object.**

**A `robots.txt` survives a domain's change of use, and nothing in the file
signals it.** *So a guard verdict says nothing about what the host serves today:
the board verdict is taken by fetching, never by guarding.*

## Two sub-species, and this card exists to keep them apart

**On 2026-09-07 a second host of this family turned up** —
`www.rwangaforas.com`, listed as a job portal by an Iraqi directory
(`iraq-hosts.md`). **It is NOT the same shape, and the earlier wording that
called it *"`bestzambiajobs.com`'s exact shape"* was too strong.**

| | `bestzambiajobs.com` | `www.rwangaforas.com` |
| :-- | :-- | :-- |
| body | **content** — a working streaming site | **709 bytes**, no content |
| marker | none held; identified by what it serves | `window._trfd.push({ap:"parking"})`, `LANDER_SYSTEM="PW"` |
| species | **repurposed** — someone runs a different business here | **parked** — nobody runs anything |

**The parked one announces itself in one grep. The repurposed one does not** —
it has a title, a sitemap and a business, and only reading the body in a
language you may not speak tells you it is not a job board.

> **The cheap marker exists for one sub-species and not the other, so a check
> built on `ap:"parking"` would pass `bestzambiajobs.com` cleanly.**

## What this card does not establish

- **nothing about the host today** — the measurement is 2026-09-05, and it was
  deliberately not re-taken: re-measuring would be a new enquiry, and the
  question this card answers is what was already known;
- **nothing about the listing's error rate in Zambia** — three of its Zambian
  hosts have cards and this is the fourth, but the listing's full membership
  was never enumerated, so there is no denominator. *`iraq-hosts.md` shows what
  it takes to get one: a population the source defines mechanically, censused
  whole.*
