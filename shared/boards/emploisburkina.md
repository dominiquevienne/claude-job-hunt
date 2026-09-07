# Board adapter — Emplois Burkina (Burkina Faso)

<!-- verified: 2026-09-07 -->

<!-- hosts: emploisburkina.bf -->
<!-- hosts-source: named by the Burkina Faso country page, rank consigned, 2026-09-04; its sitemap is declared on the third-party host `afriqueemplois.com` and the guard was taken there separately · 2026-09-07 -->
<!-- script: none -->
<!-- countries: BF -->
<!-- content: indeterminate · 23 URLs listed for this host in the network sitemap; 6 probed — 5 redirect to the site root and 1 serves a real `JobPosting`. **The remaining 17 could not be read: 22 of 23 failed at the transport after ~32 requests in 90 seconds, and the rate was mine.** No count is publishable · 2026-09-07 -->
<!-- witness: none possible — no total was obtained at all, so there is nothing to witness · 2026-09-07 -->

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
