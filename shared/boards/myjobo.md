# Board measurement — MyJobo (`www.myjobo.com`, Malawi): **the domain is PARKED and the board measured on 2026-09-17 is GONE** — re-measured 2026-10-30, when the root, `/search-jobs` and the apex all answer the same 709 B of registrar parking lander; `content: out-of-domain` is PROPOSED and deliberately not written, because it would take this card out of both denominators and that verdict is the owner's (see `shared/boards/afgjobs.md`, a hosting parking page he validated himself in #644) — **and what follows is what it WAS on 2026-09-17, not what it is**: a board and talent platform covering the 28 districts, its front served to the declared client (105 KB) with `/search-jobs?state_id=N` per district and «0 jobs» counters on the front, rules open, no adapter written

<!-- verified: 2026-10-30 -->

<!-- hosts: www.myjobo.com -->
<!-- script: none -->
<!-- countries: MW -->
<!-- content: measured · **THE DOMAIN IS PARKED AND THE BOARD IS GONE.** The root, `/search-jobs` and the apex `myjobo.com` all answer HTTP 200 with the SAME 709 B, `md5 7429192af95d` — a registrar parking lander (`window.LANDER_SYSTEM="PW"`, `ap:"parking"`, assets on `img1.wsimg.com/parking-lander/`, server `openresty`) — against 105 173 B and two moving md5 on this same root on 2026-09-17. Both public resolvers agree on the addresses, so this is not a resolver artefact. Read with `bin/fetch-body.py` as the declared client, the guard taken on each exact path in a turn of its own. **The state stays `measured` and NOT `out-of-domain`: that one leaves the table and both denominators, and for a parking page the precedent is that the owner validated it himself — a host WE judge dead without it saying so is his call, not ours.** · 2026-10-30 -->
<!-- witness: the host's OWN `/sitemap.xml`, 158 B, declares exactly ONE url, `/lander` — a count that does not come from our extraction, and it names the parking page · 2026-10-30 -->
<!-- content: measured · **the root (200, 105 173 B, md5 b089b655f423 / d3827d740239 — a rendered element moves) links `/search-jobs` and 29 `/search-jobs?state_id=N` district filters and prints «0 jobs» counters on its front blocks; no JobPosting; `_robots.allowed('www.myjobo.com','/')` → open, certain; the search page and the ad not read — whether the district counters are live is the adapter's first line** · 2026-09-17 -->
<!-- witness: the front's «0 jobs» counters — read on the search page before trusting them · 2026-09-17 -->

**RE-MEASURED 2026-10-30 16:29–16:32 UTC, and there is nothing left to adapt.**
Four paths and two hosts, each guarded on its exact URL in a turn distinct from the
retrieval, interrogated with the single token a request would carry:

```
_robots.allowed('www.myjobo.com', '/')                      open, certain, group *, no Crawl-delay
_robots.allowed('www.myjobo.com', '/search-jobs')           open, certain  <- never guarded before
_robots.allowed('www.myjobo.com', '/search-jobs?state_id=1')  open, certain
GET https://www.myjobo.com/            200,   709 B, md5 7429192af95d   parking lander
GET https://www.myjobo.com/search-jobs 200,   709 B, md5 7429192af95d   the SAME bytes
GET https://myjobo.com/                200,   709 B, md5 7429192af95d   the apex too
GET https://www.myjobo.com/sitemap.xml 200,   158 B, ONE url: /lander
```

**And a reading of mine is RETRACTED here, because it was published before the board
verdict was taken at the root.** This host's `robots.txt` points at an LLM policy
(`LLM-Policy: /llms.txt`), and that file carries `Allow: /` with `Disallow-Training: /`.
I read that as the operator opening reading and closing training — *a statement about
MyJobo's intention.* It is nothing of the kind: both files are 65–66 B of the parking
provider's boilerplate, and the operator they speak for is not MyJobo. A domain that
changes hands keeps serving a rules file, and nothing in the file says so; a guard
verdict says nothing about what the host serves today, which is why the verdict is taken
by retrieving. *The rule was known and applied one step late.*

**What can no longer be settled, and it is declared rather than dropped:** this card said
29 `/search-jobs?state_id=N` district filters where #675 said 28, and that contradiction
was to be cut on the object. **The object is gone, so the question is now unanswerable
from here** — neither number can be confirmed and neither should be reused.

*What stays open for the owner: whether this card becomes `out-of-domain` and #675 is
written off. The measurement is ours; the renouncement is his.*

**Found by the Malawi search of #622 (a country never searched), measured
2026-09-17 16:49–16:52 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #622: one
search naming the national boards and aggregators, no composed host
names; no public employment service found online by that search. *A
measurement, not an adapter.*

```
_robots.allowed('www.myjobo.com', '/')   open, certain
GET https://www.myjobo.com/   200 ×2 — see the content line
```

The list, its pager and the ad are the adapter's first line (its `adapter` issue).
