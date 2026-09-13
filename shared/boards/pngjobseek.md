# Board adapter — PNG JobSeek (Papua New Guinea): 31 advertisements on a server-rendered listing, read from the card's cells — and a card lost to a 200-byte window before the tag was tested

<!-- verified: 2026-09-13 -->

<!-- hosts: www.pngjobseek.com, pngjobseek.com -->
<!-- script: pngjobseek.py -->
<!-- countries: PG -->
<!-- content: measured · rules read twice and certain (3 695 B, Cloudflare's managed block naming `ClaudeBot`, `*` open bar the operator's paths; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200: `/jobs` states «31 jobs found — Showing 1 – 25 of 31», `?page=2` carries the last 6; no JSON-LD on any page; the adapter reads the card's rendered cells and printed «31 emitted, site states 31 — equal» on 2026-09-13 14:54 UTC; 31 of 31 with a place, a date and an employer · 2026-09-13 -->
<!-- witness: the page's own «N jobs found», read on page 1 and printed beside the distinct count after the walk — «31 emitted, site states 31 — equal» on 2026-09-13 14:54 UTC; «6 short» eleven minutes earlier, when the card's tag was tested on a byte window -->

**Shipped 2026-09-13 — measured in lot 7 of #233 and shipped with its own
defect on record.** Every fetch under the declared identity, the guard on
the exact path first, 2 s between requests (no `Crawl-delay`).

```
python3 skills/job-scan/scripts/pngjobseek.py list [--limit N] [--no-site-total]   # 25 a page, walked until a page adds nothing — 3 requests on 2026-09-13
python3 skills/job-scan/scripts/pngjobseek.py ad --url https://www.pngjobseek.com/jobs/<id>
```

## The rules — reopened by the doctrine of 2026-09-07, and 31 jobs behind them

```
robots.txt      read twice, certain: True, 3695 B, md5 a8efc8bf9a7a both times — the managed block (`ClaudeBot` named and refused, `*` open) plus the operator's lines
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user
allowed()       True on `/`, `/jobs`, `/jobs?page=2`, `/jobs/<id>`
crawl_delay     none — 2 s is ours
```

## The transport — 200

```
GET https://www.pngjobseek.com/                200, 263 145 B   (2026-09-12 15:28:03Z)  «31 Jobs are waiting for you»
GET https://www.pngjobseek.com/jobs            200, 415 307 B   (15:29:01Z, and the same size at 15:29:04Z)  «31 jobs found», «Showing 1 – 25 of 31», 25 cards
GET https://www.pngjobseek.com/jobs?page=2     200, 211 937 B   (2026-09-13 11:35:24Z)  6 cards — the last page
GET https://www.pngjobseek.com/jobs/18254      200, 149 633 B   (11:35:25Z)  the head cells and «Job Description» / «Requirements», no JSON-LD
```

## The listing — cells, not fields

A React Router app rendered on the server (Mantine): **no JSON-LD anywhere,
no data island read**. The card is `<div style="…" class="_card_…">` and its
rendered text is read as cells — title (the `<h4>` of the `/jobs/<id>`
link), employer (the logo's `alt`), «City, Province», the work type, a date
recognised by its shape («11 September 2026» → ISO), a snippet, a category.
The pages are walked until one adds no new id; the page's «N jobs found» is
printed beside the distinct count.

| question | answer |
| :-- | --: |
| jobs stated | **31** — «31 jobs found», «Showing 1 – 25 of 31»; «31 Jobs are waiting for you» on the root |
| pages | 2 (25 + 6); the adapter reads a third, empty, and stops |
| the walk of 2026-09-13 14:54 UTC | **«31 emitted, site states 31 — equal»**; 31 of 31 with a place, a date and an employer; «Full Time» on all 31; categories «Others» 4, «Manufacturing/ Transport / Logistics» 3, «Mining / Engineering» 2 … |

**The defect, on record.** The first walk (14:53 UTC) printed «25 emitted,
site states 31 — 6 short»: the card's opening tag carries a long `style`
attribute before its `class`, and the adapter tested for the class in the
fragment's first 200 bytes — six cards had longer styles and were lost, with
no error. *The count against the stated figure is what caught it — the
walk «succeeded» otherwise.* The tag is tested now (`CARD_TAG` on the
fragment's opening `<div>`), the fixture carries a 400-byte style, and the
mutation back to the window reddens.

## What an advertisement page carries

The head cells after «Back to Jobs» — title, employer, city (Kokopo),
category, **salary as published («Not Disclosed» on the page read; a figure
when the employer gives one)**, date — then «Job Description» and
«Requirements» blocks read as text up to «Apply Now». No JSON-LD; no
contacts of a recruiter are read.

## What this card is, and is not

- **An adapter, shipped** — `list` for the paged enumeration with the
  stated count as the check, `ad` for one advertisement from its rendered
  head. No key, no browser; three requests for the whole board.
- **Small and served**: thirty-one is the whole of Papua New Guinea's board
  on 2026-09-13, and the country's first adapter.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
