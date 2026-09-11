# Board measurement — bestjobs.mg (Madagascar): the name has no delegation, on two public resolvers

<!-- verified: 2026-09-11 -->

<!-- hosts: bestjobs.mg, www.bestjobs.mg -->
<!-- script: none -->
<!-- countries: MG -->
<!-- witness: none — no HTTP request reached a host: the name does not resolve; the only measurement is DNS, on two public resolvers and the zone's own SOA · 2026-09-11 -->

**This card is a measurement and not an adapter, and the measurement never
reached HTTP.** *`bestjobs.mg` was named in a survey's prose on 2026-09-04 as
a Madagascar board and never asked.* **Asked, there is nobody to ask.**

## Step 1 — the rules could not be requested: the name does not resolve (2026-09-11 13:48–13:49 UTC)

```
local resolver     bestjobs.mg / www.bestjobs.mg    "nodename nor servname provided, or not known"   ×4
                   (bin/fetch-body.py → INDETERMINATE: robots.txt could not be read after 3 attempts)
```

**A DNS negative is checked by a SECOND RESOLVER, never by a second host**
(memory of 2026-09-05: two hosts on one cached resolver «confirmed» each other
and were both a cache artefact), and `SERVFAIL` is not `NXDOMAIN`:

```
1.1.1.1   bestjobs.mg        NXDOMAIN        www.bestjobs.mg   NXDOMAIN
8.8.8.8   bestjobs.mg        NXDOMAIN        www.bestjobs.mg   NXDOMAIN
1.1.1.1   bestjobs.mg SOA    NXDOMAIN        bestjobs.mg NS    NXDOMAIN
```

**Two independent public resolvers, both forms, the zone's own records: the
name has no delegation on 2026-09-11.** *That is not a refusal, not an
indeterminate transport, not a challenge — it is an absence, and an absence is
dated: a name can be registered tomorrow.*

## The network question, asked as the assignment required — and left as a guess

`bestjobs.ph` is cited in `shared/robots-policy.md` as belonging to the
«BestJobs Network» (`bestjobs.eu`). **One DNS query was made on
`mg.bestjobs.eu` — a GUESS at how that network might name Madagascar — and it
resolves, as a CNAME to `www.bestjobs.eu`.** *A guess that resolves is not a
discovery* (memory: `devinette-qui-resout-nest-pas-une-decouverte`): nothing in
the repository and nothing served by a site names that host as Madagascar's
board, so **it was not requested and this card measures nothing on it.**
*If a session finds that host named — on the network's own pages, in a
sitemap, in an artefact — the network's card is the place to measure it, and
`countries:` there carries only what is measured.*

## What this card does not say

Nothing about a board: there is no host to describe. **«Madagascar's
`bestjobs.mg` is dead» is what this card can write, with its date and its two
resolvers; «Madagascar has no BestJobs board» it cannot — the network may serve
the country under a name this repository has not seen declared.**
