# Board measurement — Bast.af (`www.bast.af`, Afghanistan): «Find Jobs, Careers & Employment Opportunities in Kabul» — the root served to the declared client is a 4.9 KB shell (client-rendered), rules open; no adapter yet, the list route to measure

<!-- verified: 2026-09-24 -->

<!-- hosts: www.bast.af -->
<!-- script: none -->
<!-- countries: AF -->
<!-- content: measured · **the root (200, 4 871 B, md5 cc04db6aba3e identical on two reads) is a JavaScript shell titled «Jobs in Afghanistan | Bast.af …» with no card, no count and no JobPosting in its markup; `_robots.allowed('www.bast.af','/')` → open, certain; whether the route the shell calls serves the client, or only a tab, is the adapter's first line** · 2026-09-17 -->
<!-- witness: none — the root is a shell · 2026-09-17 -->

**Found by the Afghanistan search of #613 (the private boards beside
`jobs.af`, which the country page already carries), measured 2026-09-17
13:38–13:39 UTC by the declared client, the guard on the exact path first,
`bin/fetch-body.py`, two reads.** The method is written on #613: two
searches (the NGO coordination body's portal, which the first Afghan
portal grew from; and the portals the engine returns by name), no composed
host names. *A measurement, not an adapter.*

```
_robots.allowed('www.bast.af', '/')   open, certain
GET https://www.bast.af/               200 ×2, 4 871 B — a shell, the content client-rendered
```

## The control — the shell is unchanged, and the list route is NOT established

*Control of 2026-09-24, issue #643.* **A heading here carries no figure on purpose**: the repository's guard compares any number in a card's first `##` against its `content:` line, and a date in a title would be compared as though it were a count.

**2026-09-24, declared client, the guard on the exact path, two reads of the
root.** The root answers **200, 4 871 B, md5 `cc04db6aba3e`** — *byte for byte
what it answered on 2026-09-17*, and still a JavaScript shell with no card, no
count and no `JobPosting`.

```
robots.txt                          open, certain — and Crawl-delay: 1
GET https://www.bast.af/            200 ×2, 4 871 B, md5 cc04db6aba3e (identical to 17.09)
GET https://www.bast.af/sitemap.xml 200, 2 949 B — 14 URLs, ALL static pages
GET .../assets/index-7d427d26.js    200, 2 843 014 B — the application bundle
```

**`Crawl-delay: 1` is recovered here**: the 2026-09-17 reading did not record it.
*An instruction of the host missing from a card is a breach waiting to happen* —
the third time this week a re-measurement has picked one up.

**The sitemap is not an inventory.** Its fourteen URLs are the site's static
pages — `/`, `/jobs`, `/company`, `/cv-bank` — and **not one advert**. So the
route that would have been cheapest does not exist here.

### What the bundle says, and what it does not

The application is Vue with axios, and its instance is created with
`baseURL: "https://db.bast.af/api"` — **the board's data lives on a host the
root never mentions**. But only two endpoints appear as literals, and both are
about applying and storage (`/api/jobseeker/apply_jobs`, `/api/storage/…`).
**The list endpoint is assembled from variables and is not recoverable
statically**: every `.get("search")`, `.get("category")`, `.get("page")` in the
bundle is a `URLSearchParams` getter, not an HTTP call.

> **So the HTTP route is not established, and it will not be established by
> reading the bundle harder.** *Naming a plausible endpoint on `db.bast.af` and
> trying it would be composing a path the site has not shown us* — the thing
> this repository refuses to do with host names, for the same reason.

**What would establish it: a browser on `bast.af/jobs` watching its own network
requests.** That is a different kind of reading and a different kind of route,
and it is the next step — not a failure of this one. **#643 stays open as work**:
the rules are open, the host answers, nothing here is a refusal.
