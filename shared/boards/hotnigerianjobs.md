# Board adapter — HotNigerianJobs (Nigeria): 4 190 posts in the newest weekly sitemap, the post as the unit, and a digest's «N positions» a field that is never a multiplier — its positions are posts of their own in the same file

<!-- verified: 2026-09-13 -->

<!-- hosts: www.hotnigerianjobs.com, hotnigerianjobs.com -->
<!-- script: hotnigerianjobs.py -->
<!-- countries: NG -->
<!-- content: measured · rules read twice and certain (2 302 B, Cloudflare's managed block naming `ClaudeBot`, `*` open bar `/kgb/` and `/images/`; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200: `/sitemap.xml` indexes 21 weekly files, the newest `sitemap-37-2026.xml` holds 4 190 posts `/hotjobs/<id>/<slug>.html` over 5 days (2026-09-07 … 09-11, ids 953270 … 957460 contiguous), 228 of them digests declaring 1 208 positions in their slugs and 1 weekly bag — a digest's positions are single posts in the same file (BIC's four are 956940 … 956946), so 4 190 double-counts and the adapter prints posts and positions apart, never summed; a single carries a `JobPosting` with `totalJobOpenings`, a digest a numbered list read as ONE row; no total stated anywhere on the site · 2026-09-13 16:05 UTC -->
<!-- witness: none the site states — the weekly sitemap is the only enumeration, checked against itself (`<loc>` = `<url>`, 4 190 = 4 190) and never against a figure the site does not give; a digest's title «(N Positions)» is compared to the N read from its list, one row either way -->

**Shipped 2026-09-13 — the card of 2026-09-12 (a transport measurement for
#233, lot 7, «measured, no adapter yet») is replaced by this one.** Every
fetch under the declared identity, the guard on the exact path first.

```
hotnigerianjobs.py list                              # every post of the newest weekly file — 4 190 on 2026-09-13, one sitemap read, ~1 s
hotnigerianjobs.py list --file sitemap-12-2026.xml   # an older week, by name
hotnigerianjobs.py post --url https://www.hotnigerianjobs.com/hotjobs/<id>/<slug>.html
```

## The rules — 4 190 posts behind a managed block that names ClaudeBot and opens to Claude-User

```
robots.txt      read twice, certain: True, 2302 B, md5 f98a071dcf74 both times — the managed block (`ClaudeBot` named and refused, `*` open) plus `Disallow: /kgb/`, `/images/`; `Sitemap: http://www.hotnigerianjobs.com/sitemap.xml`
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed()       True on `/`, `/sitemap.xml`, `/sitemap-37-2026.xml`, `/hotjobs/957082/…`
crawl_delay     none  -> Pace(HOST, own=2.0), two seconds between requests, ours — a post page is 180–195 kB
```

## The sitemap — posts, and what a post is

| question | answer (2026-09-13, 16:05 UTC) |
| :-- | --: |
| the index | 21 weekly files `sitemap-<week>-<year>.xml`; **37-2026 first** (lastmod 2026-09-11), then 12-2026 back to 45-2025 — weeks 13–36 of 2026 absent; the adapter picks the newest by (year, week), not by the index's order |
| `sitemap-37-2026.xml` | **4 190** `<loc>`, 4 190 `<url>`, 4 190 distinct ids, 953270 … 957460 (a contiguous range of exactly 4 190), 5 `lastmod` days: 07 → 819, 08 → 969, 09 → 965, 10 → 709, 11 → 728 |
| a SINGLE | «Mobile Developer at Ardova Plc» (953280, 194 813 B): one JSON-LD `JobPosting` — `title`, `hiringOrganization.name`, `datePosted`, `validThrough` (2026-09-09, two days after posting), `employmentType`, `addressRegion` «Lagos», `addressCountry` NG, **`totalJobOpenings` «1»**, `occupationalCategory`, `industry`, a `description` entity-encoded a second time inside the JSON |
| a DIGEST | «BIC Nigeria Job Recruitment (4 Positions)» (957082, 180 948 B): no JSON-LD; «Posted on Fri 11th Sep, 2026»; a numbered list «1.) Title / Location: Lagos / Click Here To View Details» — **and each link is a single post of its own, in the same weekly file** (956940, 956941, 956943, 956946) |
| a BAG | «HNJ Exclusive Job Goody Bag — September Week Two» (957293): a weekly digest of digests, one per file |
| digests by slug | **228** posts whose slug ends «-N-positions», declaring **1 208** positions; the slug is cut at ~50 characters («…-job-recruitment» 274 times), so a digest whose number fell off reads as a single until its page is opened |
| a stated total | **none** — no page read states one; the sitemap is checked against itself |

**The post is the unit, and the positions are a field.** *4 190 posts is
not 4 190 advertisements — a digest of 124 positions is one `<loc>` — and
it is not 4 190 − 228 either, because a digest's positions are posts too:
the two numbers describe two different objects and the adapter prints them
apart: «4 190 distinct post(s)» and «228 digest(s) declare 1 208 position(s)
in their slugs … printed apart and never summed».* `post --url` on a digest
emits **one row** whose `positions` is the list `{n, title, location, url}`
and whose `positions_stated` is the title's number, «4 read, the title
states 4 — equal; one row» on BIC; it never walks the list's links and never
turns one post into N rows.

## What the adapter does, and refuses to do

- **Reads the index, then ONE weekly file** — 4 190 rows from one 730 kB
  request; `--file` names another week. `_sitemap.count` checks `<loc>`
  against `<url>` and a file that disagrees with itself prints no count
  (exit 6).
- **`post --url`**: a single → its `JobPosting`, `totalJobOpenings` →
  `positions`, the description unescaped once before the tags are stripped;
  a digest → one row, the list read by its «`<strong>N.)`» markers.
- **Never emits a contact.** No recruiter address, no phone.
- **Not a verdict that anything is closed** — nothing refuses us.

## Tests

`ThePostIsTheUnitAndItsPositionsAreAFieldNeverAMultiplier` in
`tests/test_core.py` — four cases (the newest file by name, the dedup, the
two numbers apart; a digest as one row with 3 read against 4 stated; a
single with its description unescaped once and a non-post URL refused; a
file that disagrees with itself). Six mutations under `python3 -B` on a
detached copy, six reds, each on the case that names it: the newest file
by the index's order, the dedup removed, the positions summed into the post
count, the digest emitted as N rows, the slug's number ignored, the second
unescape dropped.

## Provenance

- `hnj/index.xml` (3 005 B, 16:05:11Z), `hnj/s37.xml` (730 202 B),
  `hnj/digest.html` (180 948 B), `hnj/single.html` (194 813 B) —
  2026-09-13, `bin/fetch-body.py`, provenance beside each, scratchpad of
  `claude-job-hunt-ab`.
- `hotnigerianjobs.py list --limit 2` at 16:1x UTC: the three
  `[hotnigerianjobs]` lines quoted above verbatim.
