# Board adapter — Duapune (Albania): reopened by the 2026-09-07 doctrine, and the transport refuses the client with a static 403

<!-- verified: 2026-09-14 -->

<!-- hosts: duapune.com -->
<!-- script: none -->
<!-- countries: AL -->
<!-- content: indeterminate · 1 host, rules read twice and certain — `ClaudeBot` named and refused, `*` open, so `identity()` answers `claude-user` and since #230 `verdict()` sweeps under it — and the root answers HTTP 403 to that client on 2 fetches: 25 bytes, md5 `9ccabba20b9f` both times — the static provider default (`Your request was blocked.`), the same bytes as `www.jobstore.com` and `www.hays.fr`; nothing of the site was read · 2026-09-11 22:10 UTC -->
<!-- witness: the search page's own «892 postime aktive» on `/search/advanced/filter`, read from a connected tab on page 1 and page 18 (10:54–10:58 UTC) — 50 cards a page, `?page=2 … 18`, page 18 carrying 42: 17 × 50 + 42 = 892, equal; the header's «907 Punë aktive» is another counter of the same site (the search's figure is the list's); the city facet Tiranë 711; nothing is served to the declared client (403, 25 B, the provider default) · 2026-09-14 -->
<!-- route: browser · 892 · 2026-09-14 -->

**Measured 2026-09-11 at 22:10:56Z UTC for #233, lot 1 — a measurement of the
transport, not a decision about the host.** Every fetch under the declared
identity, the guard on the exact path first.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True
```

*Before the decision this host was read as closed by name; the decision
reopened it on paper, and this card is the first time its transport was
asked under the permitted token.*

## The transport — a static 403, the provider default

```
GET https://duapune.com/     403, 25 B, md5 9ccabba20b9f    (22:10:56Z)
GET https://duapune.com/     403, 25 B, md5 9ccabba20b9f    (second fetch)
```

**Same size, same md5 on two fetches — a static body, and it is the 25-byte
default served by the same provider on unrelated hosts** (`www.jobstore.com`,
`www.hays.fr`, `kariera.mk`, `www.tala-com.com`, `sptojobslink.com`: the same
bytes, `9ccabba20b9f4ec7d18bd6644579e5bf`). *A body shared between unrelated
hosts is a provider default, not a page anyone wrote for this host.* **The
rules permit and the transport refuses the client: family (1) of #222 — the
case where a browser is legitimate** (#66: it changes the layer, not the
permission). Not measured here: this session has no browser instrument; an
OPEN under a real browser would make this host a candidate for a browser
adapter, and that is the pilot's to assign.

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches of the root, a static refusal.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.

## 2026-09-14 10:54–10:58 UTC — served to a connected tab

```
tab, /                               served — «907 Punë aktive», «191525 Punëkërkues», «14253 Punëdhënës»; links to /jobs/<id>-<slug>, /employers/<slug>, /search/…
tab, /search/advanced/filter         served — «892 postime aktive», 50 cards a page (title, employer, category, city, the closing date and «mbaron sot / edhe N ditë»), the category counts («Kamarier (40 postime)» …), the city counts (Tiranë 711, Durrës 79 …), pager ?page=2 … 18
tab, /search/advanced/filter?page=18 served — 42 cards, the last: 17 × 50 + 42 = 892, equal to the search's statement
cards                                /jobs/<6-digit id>-<slug>; the ad page not read this session
```

**`route: browser · 892 · 2026-09-14`** — the search's own count; the
header's «907» is the site's other counter. What a session does from a
tab: `/search/advanced/filter?page=N` to the last, the id from
`/jobs/<id>-<slug>`, the card's employer, category, city and closing date,
the ad page for the text. No script: the declared client gets the
provider's 25-byte 403 (#404). GjejPunë24, the other Albanian board, is
`route: none`; Duapune is the country's board from a tab.

