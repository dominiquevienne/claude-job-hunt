# Board measurement — Air Côte d'Ivoire — careers (`jobs.aircotedivoire.com`, Côte d'Ivoire): one employer's own careers site on Teamtailor — three postings (two training «concours», one «nous recrutons»), `/jobs` and `/jobs.rss`; an employer, not a board of the country, and a family the plugin already reads (`teamtailor.md`)

<!-- verified: 2026-09-20 -->

<!-- hosts: jobs.aircotedivoire.com -->
<!-- script: none -->
<!-- countries: CI -->
<!-- content: out-of-domain · **the root (200, 84 772 B, md5 817c0f59dbeb identical on two reads) is «Bienvenue sur notre site carrières - Air Côte d'Ivoire», built on Teamtailor (48 mentions, `teamtailor-cdn.com/assets/careersite-…`): `/jobs`, `/jobs.rss`, three `/jobs/<id>-<slug>` postings; no count, no JobPosting on the front; `_robots.allowed('jobs.aircotedivoire.com','/')` → open, certain** · 2026-09-20 -->
<!-- witness: none — an employer's site, three postings · 2026-09-20 -->

**Named in the Atlas inventory of 2026-09-04 (#147), never carded; measured
for #765 on 2026-09-20 12:23–12:25 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** *A measurement, not an
adapter.*

**Not a board of the country: the national airline's own careers page**, hosted by Teamtailor on a custom domain. The family is carded (`teamtailor.md`, `teamtailor.py`, host form `{tenant}.teamtailor.com`); whether the adapter accepts a tenant on its own domain is that card's question, not this one's. Out of Côte d'Ivoire's denominators — the 2026-09-04 inventory listed it beside the country's boards, and it is an employer.

```
_robots.allowed('jobs.aircotedivoire.com', '/')   open
GET https://jobs.aircotedivoire.com/   200 ×2 — a Teamtailor careers site, 3 postings, /jobs.rss
```
