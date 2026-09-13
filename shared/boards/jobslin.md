# Board measurement — Jobslin (Philippines and 20 other countries): the host of #233 is a country chooser — the Philippine board lives on `ph.jobslin.com`, served, 10 posts on its front page

<!-- verified: 2026-09-13 -->

<!-- hosts: www.jobslin.com, jobslin.com -->
<!-- script: none -->
<!-- countries: PH -->
<!-- content: measured · rules read twice and certain (1 836 B, the bare managed block naming `ClaudeBot`, `*` open; `identity()` answers `claude-user`, `verdict()` sweeps) — and `www.jobslin.com` answers 200 → `https://jobslin.com/` (13 468 B, byte-identical twice): «Choose Your Country» — Asia (Philippines, Malaysia, Singapore), Africa, Oceania, Ibero-America — a hub with **0 advertisements**; `/jobs` on it is the site's own 404; `ph.jobslin.com` answers 200 (179 496 B, `Crawl-delay: 2` honoured) with 10 `/job/` links on its front page and no stated total · 2026-09-13 -->
<!-- witness: the hub's own «Choose Your Country» page — 21 country sub-hosts, the Philippine one read once; no count stated anywhere read; no adapter yet -->

**Measured 2026-09-13 for #233, lot 8 — a measurement of the transport, not a
decision about the host.** Every fetch under the declared identity, the
guard on the exact path first, `bin/fetch-body.py`.

## The rules — reopened by the doctrine of 2026-09-07, and 10 posts behind them

```
robots.txt      read twice, certain: True, 1836 B, md5 c6370d4bc025 both times — Cloudflare's managed block, `ClaudeBot` named and refused, `*` open
identity("/")   http, claude-user
verdict()       sweep True, sweep_token claude-user
allowed()       True on `/`, `/jobs`; on `ph.jobslin.com`: True on `/`, with `Crawl-delay: 2`
crawl_delay     none on the hub; 2 s on `ph.jobslin.com` (honoured)
```

## The transport

```
GET https://www.jobslin.com/       200 → https://jobslin.com/, 13 468 B   (10:22:23Z, byte-identical at 10:22:25Z)  «New Opportunities, Every Day | Jobslin» — the country chooser
GET https://www.jobslin.com/jobs   404, 6 615 B                       (10:23:32Z, twice)  the site's own 404 — a guessed path
GET https://ph.jobslin.com/        200, 179 496 B                     (10:25:02Z; 179 502 B at 10:25:05Z)  «Jobslin: Job Opportunities in Philippines» — 10 `/job/` links, no stated total
```

## What the pages say

| question | answer |
| :-- | --: |
| what `jobslin.com` is | **a hub** — «Choose Your Country»: `ph.`, `my.`, `sg.` and 18 more sub-hosts; 0 advertisements on it |
| the Philippine board | `ph.jobslin.com` — served, 10 posts on the front page («Full Time · Cavite · 05/08/2026»), no count stated, not paged on the front page |
| the object of #233 | the hub host, which is not a board — the board is a sub-host, one per country |

*The class `labour-gov-bb` opened: a served host whose object is elsewhere. Here the elsewhere is 21 sub-hosts of the same operator.*

## What this card is, and is not

- **A measurement, not an adapter** — and the hub is **not a board**: 0 advertisements by object. **Candidate: `ph.jobslin.com`** (and its siblings `my.`, `sg.` …), a served front page with `/job/` links; its listing and count are the adapter's first question. *Only `ph.` was read, once.*
- **Not a verdict that the host is closed** — nothing in the rules refuses `Claude-User`.
- **No configuration.** A user with a URL from this host can hand it to `cover-letter`.
