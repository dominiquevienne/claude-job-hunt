# Board adapter — Emplois Burkina (Burkina Faso)

<!-- verified: 2026-09-08 -->

<!-- hosts: emploisburkina.bf -->
<!-- hosts-source: named by the Burkina Faso country page, rank consigned, 2026-09-04; its sitemap is declared on the third-party host `afriqueemplois.com` and the guard was taken there separately · 2026-09-07 -->
<!-- script: none -->
<!-- countries: BF -->
<!-- content: indeterminate · remeasured 2026-09-08 09:01-09:07 UTC at 10 s spacing: of the 24 URLs the network attributes to this host, **4 serve a real `JobPosting`**, **7 redirect to the site root** (271 550 bytes each, identical), and **13 could not be read at all** — the host stopped accepting connections after the 11th request and never resumed. So the live count is **between 4 and 17**, and no single number describes it · 2026-09-08 -->
<!-- witness: 4 advertisements confirmed live, which is a floor and not a total — 13 of the 24 are unknown, not absent · 2026-09-08 -->

**Burkina Faso had no card in this repository.** This one records a
measurement that **stopped**, and why.

## The network, re-verified today

`emploisburkina.bf` declares its sitemap on **another host** —
`https://afriqueemplois.com/sitemap.xml` — and the guard was taken there in
its own turn.

```
2026-09-04 (country page)   149 advertisements · 25 for Burkina
2026-09-07 (this reading)   141 advertisements · 23 for Burkina

partition        141 ids, 141 distinct, ZERO present on two domains
                 afriqueemplois.com 75 · emploiivoire.ci 37
                 emploisburkina.bf  23 · emploisenegal.sn  6
lastmod          141 of 141, 2026-01-12 … 2026-09-07
```

**The third archetype holds three days later**, on a smaller inventory.
*And the dates are on the sitemap, which the country page does not record:
freshness is measurable here without opening an advertisement.*

**`sitemap-jobs-BF.xml` still answers with 6 615 bytes that are not a
sitemap** — the country page called it a Laravel error page and the byte count
is identical. **The general file is what carries the Burkinabè URLs.**

## What six probes showed, and why they are not twenty-three

```
5 of 6   redirect to https://emploisburkina.bf/ — the HOMEPAGE title
1 of 6   serves a real advertisement, `JobPosting` present
         « World Vision recrute un Directeur en Recherche stratégique »
```

**Without `final_url` the five would have been counted as advertisements**, at
272 KB of homepage each. *That field is why this card does not open with a
count of 23.*

**And the behaviour belongs to the domain, not to the network**:
`afriqueemplois.com` served both its probes, `emploiivoire.ci` one of two,
`emploisenegal.sn` redirected both to `/sn`.

## The measurement stopped, and the cause is mine

**Reading all 23 was the right instinct — 23 is small, and a rate on six is
worse than a count on twenty-three.** It failed:

```
23 attempted · 1 answered · 22 failed at the transport
~32 requests to this host in about 90 seconds
     9 through bin/fetch-body.py, 16:29:54Z … 16:31:06Z
    23 in a sweep that paced itself at 1 s and knew nothing of the 9
```

**The host answered every probe minutes earlier and then stopped.** *The most
likely reading is that the rate was mine.* **No count is published, and
`content:` says `indeterminate` rather than a zero** — *a zero manufactured by
one's own request rate is the defect this repository has already paid for.*

### Two faults in my own instrument, and the second is worse

**`Pace` is per-process.** The sweep started fresh and had no knowledge of the
nine requests already made from another script. **Two tools pacing correctly
can still hammer a host together**, and nothing in either one can see it.

**And the sweep recorded `code: null` with no reason.** The exception text was
discarded, so the record cannot distinguish a refusal from a timeout from a
reset — *the failure is attested and its nature is not.* **A record that
cannot say why is why this card cannot say what.**

## What remains to be done, and it is not more requests today

**Re-read the 23 after a pause, from one process, at a slower rate.** The
sitemap is on a third host and costs one request; the 23 are the whole
Burkinabè inventory of this network.

*And the question that decides whether an adapter is worth writing is already
sharp: if five in six of the listed URLs redirect to the root, this facade
lists far more than it serves, and the board carrying the matter is
`afriqueemplois.com`.*


## 2026-09-08 — remeasured, and the pacing theory does not survive it

**The 2026-09-07 card blamed our own rate:** *~32 requests in 90 s, 22 of 23
failing.* **Today's run used 10 s spacing — 6 requests a minute, roughly a
third of that — and the host still cut us off.**

```
ordre des 24, 09:01 -> 09:07:16 UTC
.....A..AAAxxxxxxxxxxxxx
. redirect to root (271 550 bytes, identical)   A real JobPosting   x unreadable

11 requests answered, then 13 consecutive failures and no recovery
```

**What the 13 are, exactly — and they are not refusals.**

```
INDETERMINATE: robots.txt could not be read after 3 attempt(s):
               <urlopen error [Errno 61] Connection refused>
```

**The guard could not be taken, so nothing was fetched.** *`fetch-body.py`
declined rather than reaching for the page without a verdict, which is the
behaviour it was written for.* **13 unknown is not 13 closed**, and this card
does not count them either way.

### What this measures, and what it retracts

| of the 24 URLs the network attributes to this host | |
| :-- | --: |
| serve a real `JobPosting`, no redirect | **4** |
| redirect to the site root — 271 550 bytes, identical to the byte | **7** |
| unreadable, connection refused at the guard | **13** |

**So the live inventory is between 4 and 17.** *Four is measured; seventeen is
four plus the thirteen unknowns; and no figure of 23, 24 or 25 was ever a count
of live advertisements — those are counts of URLs in a third party's sitemap.*

**And the redirects are why `final_url` was in the protocol.** *All seven answer
HTTP 200 with a 271 550-byte body.* **Without recording where they landed, all
seven would have been counted as advertisements** — a plausible 11 instead of a
measured 4.

### The pacing theory is now doubtful, and that changes the prescription

**Yesterday's reading was "a rate that was ours". At a third of that rate the
host still stopped, after 11 requests rather than after 90 seconds.** *That
points at a cumulative count rather than a rate* — **and if it is cumulative,
waiting longer between runs does not help, which is exactly what yesterday's
prescription assumed.**

**This is a hypothesis and not a measurement.** *One request 35 seconds after
the run was also refused, and 35 seconds is not a test of recovery.* **What
would test it: a single request after a long idle period.** *Two observations
now share a shape; neither isolates the variable, and the honest reading is that
we do not know what trips it.*
