# Board adapter — JobWeb Rwanda (Rwanda): open, readable, and stopped

<!-- verified: 2026-09-08 -->

<!-- hosts: jobwebrwanda.com -->
<!-- host-forms: jobwebrwanda.com -->
<!-- host-forms-basis: read — `jobwebrwanda.py:BASE`, a single literal. `www.jobwebrwanda.com` answers 302 into the same login loop as the apex and is never fetched · 2026-09-08 -->
<!-- script: jobwebrwanda.py -->
<!-- countries: RW -->
<!-- content: measured · 558 advertisements in `job_listing-sitemap.xml` out of 559 `<loc>`, the extra being `/jobs/` itself; 167 distinct dates 2019-05-08 → 2026-06-24, busiest day 8 (1.4 %), and **0 dated on or after 2026-08-01** · 2026-09-08 -->
<!-- witness: none published by the site; 558 is the count of `/jobs/<slug>/` entries in its own sitemap. Rwanda's country page recorded «201 offres vivantes» on 2026-09-04 — a different question, and see below · 2026-09-08 -->

**Rwanda's first adapter**, and the board that served as the *control* when
the fabricated network was screened: its 1 % title overlap with the Rwandan
node is what made the network's 19–40 % mean something.

## The most evenly spread board measured here, and it has stopped

```
558 advertisements   167 distinct dates   2019-05-08 → 2026-06-24
busiest day            8, which is 1.4 %
since 2026-06-01      65
since 2026-08-01       0
```

**1.4 % on the busiest day**, against 18.5 % for `jobartis` and 60.5 % for
`ihararejobs`. *A clean distribution and a dead board are not contradictory*:
this site published steadily for seven years and then stopped in June.

## The host asks for thirty seconds, and it gets them

`robots.txt` is two lines — `User-agent: *` and **`Crawl-delay: 30`**. *A
directive, not a remark*, which is the lesson `ejob.az` taught this repository
at a delay of 5.

**`list` costs one request; `--fetch` costs half a minute per
advertisement** — four and a half hours for the board. The flag prints the
arithmetic before it starts, and `Pace` is constructed **without an `own`
spacing**: passing one could only make us faster, which is the single
direction that is not ours to choose.

## The root demands a login and the advertisements do not

```
GET /                        302 → /login/?redirect_to=…/login/?redirect_to=…
GET /sitemap.xml             200 → /sitemap_index.xml
GET /job_listing-sitemap.xml 200
GET /jobs/<slug>/            200, a complete JobPosting, 100 kB
```

**A redirect loop into a login page, and the inventory behind it is public
anyway.** *A reader that took the root for the board's answer would have filed
Rwanda as closed* — the verdict is taken where the advertisements are, and
this module never requests `/`.

**No account is created and none is needed.** If the advertisements ever move
behind that login, the adapter stops on the redirect and says so rather than
authenticating.

## The sitemap's date is the posting date here — checked

`lastmod` equals `datePosted` on **3 of 3** sampled, the most recent included.
**So `--since` works on one request.** That is worth stating because the two
boards measured just before it could not:

```
ihararejobs    the date MOVES when the page is read      our own crawl
myjobsfiji     ONE value across 3 152 entries            a rebuild stamp
jobwebrwanda   lastmod == datePosted, 3 of 3             the posting date
```

**A `lastmod` is worth nothing until it has been looked at, and there are at
least three ways for it to be worthless.** The adapter emits `date_conflict`
when a fetched page disagrees, and counts them: *a rise there retires
`--since` on one request, and would otherwise be silent.*

## Nothing is likely to be live, and this card does not claim a census

The newest advertisement is dated 2026-06-24 and its own `validThrough` is
**2026-07-04**, already past. On the three sampled, `validThrough` falls ten to
eleven days after `datePosted`.

*If that interval holds, nothing on this board is live.* **That is an
inference from three, not a count** — liveness is per advertisement at thirty
seconds each.

**Rwanda's country page recorded «201 offres vivantes» on 2026-09-04.** This
module cannot reproduce that at reasonable cost and **does not contradict
it**: it reports what the sitemap says and what three advertisements said.

## One sitemap by name, never a wildcard

`/job_listing-sitemap.xml`. The index also offers `job_loc-`, `job_cat-` and
`job_type-`, **which a `job_listing*` glob would sweep in** — taxonomies, not
advertisements, and this repository has paid for that before. `/jobs/` itself
sits among the entries: 559 `<loc>`, 558 advertisements.

## What was exercised, 2026-09-08

```
list                             558 ads · 1 other · newest 2026-06-24
list --since 2026-06-01          65
list --since 2026-08-01          0
list --live without --fetch      exit 2, and it prices the flag: "5 × 30 s"
list --fetch --limit 2           2 read · 2 kept · 0 unreadable · 0 lax
                                 0 date conflicts · salary in RWF on both
ad  a slug that does not exist   exit 3
```

**And a lesson that cost three runs.** An exercise loop suppressed `stderr`;
three consecutive invocations returned nothing and the reason went with it.
*The module was doing its job — `die()` with a message — and the message was
being discarded by the harness around it.* **A run that produces no output has
already told you why, unless you threw it away.**
