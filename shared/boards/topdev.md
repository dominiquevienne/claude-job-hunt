# Board measurement — TopDev (Vietnam): reopened by the 2026-09-07 doctrine, the transport is OPEN, and the search states 4 942 IT jobs

<!-- verified: 2026-09-13 -->

<!-- hosts: topdev.vn, www.topdev.vn -->
<!-- script: none -->
<!-- countries: VN -->
<!-- content: measured · rules read twice and certain (2 190 B, the managed block naming `ClaudeBot`, `*` open bar the operator's paths; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200 at the root (1 873 351 B, twice, same size) and at `/viec-lam/tim-kiem` (1 449 130 B, twice, same size): «Tuyển dụng 4942 việc làm lương cao [Update 13/9/2026]», 29 `/viec-lam/<slug>-<id>` links on the page; no JSON-LD · 2026-09-13 -->
<!-- witness: the search page's own «4942 việc làm», dated by the site itself «[Update 13/9/2026]» — the day of the read; no adapter yet -->

**Measured 2026-09-13 for #233, lot 8 — a measurement of the transport, not a
decision about the host.** Every fetch under the declared identity, the
guard on the exact path first, `bin/fetch-body.py`.

## The rules — reopened by the doctrine of 2026-09-07, and 4 942 IT jobs behind them

```
robots.txt      read twice, certain: True, 2190 B, md5 3bf3b2ef1857 both times — the managed block (`ClaudeBot` named and refused, `*` open) plus the operator's lines
identity("/")   http, claude-user
verdict()       sweep True, sweep_token claude-user
allowed()       True on `/`, `/viec-lam/tim-kiem`
crawl_delay     none
```

## The transport

```
GET https://topdev.vn/                     200, 1 873 351 B   (10:22:34Z, 10:22:36Z — same size, a per-response token)  «TopDev - Việc Làm Lương Cao Hàng Đầu»
GET https://topdev.vn/viec-lam/tim-kiem    200, 1 449 130 B   (10:23:45Z, 10:23:48Z — same size)  «Tuyển dụng 4942 việc làm lương cao [Update 13/9/2026]», 29 advertisement links
```

## What the pages say

| question | answer |
| :-- | --: |
| jobs stated | **4 942** — «Tuyển dụng 4942 việc làm lương cao», with the site's own «[Update 13/9/2026]» |
| on the page | 29 `/viec-lam/<slug>-<id>` links — the trailing number is the key |
| pages | a 1.4 MB page with no `?page=` link found in the HTML — the pager is a script or a query the adapter will find |
| by city, on the root | Hà Nội «Hơn 1000», Hồ Chí Minh … — «more than» figures, not counts |

*A 1.4-megabyte listing served to a plain client: the enumeration is on the page, and its pagination is the adapter's first question.*

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE. **Candidate adapter** for Vietnam's IT board: the stated 4 942 as the witness, ids in the URL, the pager to find. *Vietnam has one adapter; the two other hosts of #233 — `mywork.com.vn` (static 403) and `careerlink.vn` (a Turnstile on the listing) — are on their own cards.*
- **Not a verdict that the host is closed** — nothing in the rules refuses `Claude-User`.
- **No configuration.** A user with a URL from this host can hand it to `cover-letter`.
