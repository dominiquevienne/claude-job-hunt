# Board measurement — Tecnoempleo (Spain): a refusal written by hand naming six Anthropic agents, `Claude-User` under `*`, the transport OPEN, and 2 592 IT offers stated

<!-- verified: 2026-09-13 -->

<!-- hosts: www.tecnoempleo.com, tecnoempleo.com -->
<!-- script: none -->
<!-- countries: ES -->
<!-- content: measured · rules read twice and certain (953 B — a hand-written file: six Anthropic names refused including `ClaudeBot`, not `Claude-User`, which falls under `*`; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200 at the root (75 025 B) and at `/ofertas-trabajo/` (168 175 B, twice, same size): 2 592 offers stated — «2.592 Ofertas de Trabajo en Informática y Telecomunicaciones», «1-30 de 2.592», 30 a page, pager 1 2 3 4 siguiente · 2026-09-13 -->
<!-- witness: the listing's own «2.592 Ofertas», stated twice on the page (heading and pager line «1-30 de 2.592»); no adapter yet — Spain has five, this is the IT board -->

**Measured 2026-09-13 for #233, lot 8 — a measurement of the transport, not a
decision about the host.** Every fetch under the declared identity, the
guard on the exact path first, `bin/fetch-body.py`.

## The rules — reopened by the doctrine of 2026-09-07, and 2 592 offers behind them

```
robots.txt      read twice, certain: True, 953 B, md5 12f0291e9890 both times — WRITTEN BY HAND: six Anthropic agents refused (`ClaudeBot` among them), `Claude-User` not named
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07; #233: the hand-written four are measured like the others)
verdict()       sweep True, sweep_token claude-user
allowed()       True on `/`, `/ofertas-trabajo/`
crawl_delay     none
```

## The transport

```
GET https://www.tecnoempleo.com/                     200, 75 025 B    (10:22:17Z; 75 027 B at 10:22:19Z — dynamic)  «tecnoempleo - Portal de Empleo en Informática y Telecomunicaciones»
GET https://www.tecnoempleo.com/ofertas-trabajo/     200, 168 175 B   (10:23:25Z, and the same size at 10:23:27Z)  «2.592 Ofertas de Trabajo…», «1-30 de 2.592», pager to «siguiente»
```

## What the pages say

| question | answer |
| :-- | --: |
| offers stated | **2 592** — in the heading and in the pager line «1-30 de 2.592» |
| a page | 30; the pager shows 1 2 3 4 and «siguiente» — 2 592 / 30 ≈ 87 pages |
| JSON-LD | `WebSite`, `SearchAction`, `Organization` on the root; none on the listing |

**The line «refusal written by hand naming ClaudeBot» stays on this card for the owner** — #233 keeps this host under that form; the measurement is taken under the token the file does not name.

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE. **Candidate adapter** for Spain's IT board: a paged listing (30 a page), the stated 2 592 as the witness, the offer page's markup as the first question. *Not the same as the four written-by-hand hosts' listing paths: here `*` refuses nothing of the board.*
- **Not a verdict that the host is closed** — nothing in the rules refuses `Claude-User`.
- **No configuration.** A user with a URL from this host can hand it to `cover-letter`.
