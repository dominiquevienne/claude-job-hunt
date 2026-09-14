# Board measurement — CareerLink (Vietnam): the root is served, and the listing answers 200 with a Cloudflare Turnstile — a challenge served as a page, borne 2 on the one path that matters

<!-- verified: 2026-09-14 -->

<!-- hosts: www.careerlink.vn, careerlink.vn -->
<!-- script: none -->
<!-- countries: VN -->
<!-- content: measured · rules read twice and certain (1 148 B, `ClaudeBot` named and refused, `*` open — the written refusal #233 recorded on 2026-09-11 is this file, and it does not name `Claude-User`; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200 at the root (126 549 B, nginx, twice, same size) but at `/vieclam/tim-kiem-viec-lam` a **200 of 26 218 then 25 522 B carrying a Cloudflare Turnstile** (`challenges.cloudflare.com/turnstile/v0/api.js`, `cf-turnstile`, a «recaptcha-loading» spinner, «Phiên làm việc của bạn đã hết hạn») and 0 advertisement links: the listing is behind a challenge that the status code does not show · 2026-09-13 -->
<!-- witness: the site's own «32300 việc làm» on `/vieclam/list`, read from a connected tab (no challenge shown, 2026-09-14 10:36–10:38 UTC) — 50 cards a page, `?page=2 … 646`: 646 × 50 = 32 300, equal to the statement; nothing is served to the declared client (the Cloudflare challenge, never defeated) · 2026-09-14 -->
<!-- route: browser · 32300 · 2026-09-14 -->

**Measured 2026-09-13 for #233, lot 8 — a measurement of the transport, not a
decision about the host.** Every fetch under the declared identity, the
guard on the exact path first, `bin/fetch-body.py`.

## The rules — reopened by the doctrine of 2026-09-07, and 0 advertisements behind them

```
robots.txt      read twice, certain: True, 1148 B, md5 cecf63e6f27a both times — `ClaudeBot` named and refused, `*` open (the file #233 called «written by hand»; it names ClaudeBot, not Claude-User)
identity("/")   http, claude-user
verdict()       sweep True, sweep_token claude-user
allowed()       True on `/`, `/vieclam/tim-kiem-viec-lam`
crawl_delay     none
```

## The transport

```
GET https://www.careerlink.vn/                             200, 126 549 B   (10:22:40Z, 10:22:43Z — same size)  «Kiếm việc làm trên Mạng tuyển dụng trực tuyến | CareerLink.vn», server: nginx — 76 links, navigation
GET https://www.careerlink.vn/vieclam/tim-kiem-viec-lam    200, 26 218 B    (10:24:01Z)  a Turnstile page: `cf-turnstile` widget, «recaptcha-loading», 0 advertisement links
GET https://www.careerlink.vn/vieclam/tim-kiem-viec-lam    200, 25 522 B    (10:24:14Z)  the same, a different size — the widget's token
```

## What the pages say

| question | answer |
| :-- | --: |
| the root | served — a navigation page (city links `/tim-viec-lam-tai/ho-chi-minh/HCM` ×16, `/vieclam/tim-kiem-viec-lam` ×14) |
| the listing | **a Cloudflare Turnstile served with HTTP 200** — the challenge is in the body, not in the status |
| advertisements read | **0** |
| a stated count | none reachable |

**A challenge with a 200 is still a challenge** (borne 2: the plugin neither defeats one nor asks the user to) — and it is the case `un-refus-servi-en-200-echappe-au-controle-de-code` described and then retracted for another host; here it is measured: the code says 200, the body says Turnstile. *The root is not the board; the listing is, and it is closed to a script.*

## What this card is, and is not

- **A measurement, not an adapter** — and no script can ship: the listing path serves a Turnstile. **Not a candidate by HTTP**; whether a real browser passes it without a person is not measured, and this card claims nothing either way.
- **Not a verdict that the host is closed** — nothing in the rules refuses `Claude-User`.
- **No configuration.** A user with a URL from this host can hand it to `cover-letter`.

## 2026-09-14 10:36–10:38 UTC — the challenge does not show to a connected tab

```
tab, /vieclam/list        served — «32300 việc làm», 50 cards a page (title, employer, city, «Cập nhật: 8 phút trước»), sort by update, pager ?page=2 … 646
cards                     /tim-viec-lam/<slug>/<id>?source=site — the id the 7-digit tail; the ad page not read this session
```

**`route: browser · 32300 · 2026-09-14`** — 646 pages of 50 equal the
statement. What a session does from a tab: `/vieclam/list?page=N`, the id
from the `/tim-viec-lam/<slug>/<id>` tail, the card's employer, city and
update age, the ad page for the rest. No script: the declared client is
challenged (#404).

