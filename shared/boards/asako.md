# Board measurement — Asako.mg (Madagascar): reopened by the 2026-09-07 doctrine, the transport is OPEN, and `/emploi` states 251 offers rendered by script

<!-- verified: 2026-09-12 -->

<!-- hosts: www.asako.mg, asako.mg -->
<!-- script: none -->
<!-- countries: MG -->
<!-- content: measured · rules read twice and certain (1 877 B, Cloudflare's managed block naming `ClaudeBot`, `*` open — `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200 on Vercel at the root (330 453 B, byte-identical twice) and at `/emploi` (136 440 B, byte-identical twice): the listing states «251 offres disponibles» and «Vous voyez 20 offres sur 251 — Charger plus», a Next.js app-router page whose 20 cards are in the RSC payload and whose «load more» is a script; 0 `/emploi/<id>` links in the HTML · 2026-09-12 15:28 UTC -->
<!-- witness: the page's own «251 offres disponibles» and «20 offres sur 251» — two places, one number; the enumeration is behind the app router's «Charger plus», not measured here; no adapter yet -->

**Measured 2026-09-12 at 15:27:50Z UTC for #233, lot 7 — a measurement of
the transport, not a decision about the host.** Every fetch under the
declared identity, the guard on the exact path first, `bin/fetch-body.py`.

## The rules — reopened by the doctrine of 2026-09-07, and 251 offers behind them

```
robots.txt      read twice, certain: True, 1877 B, md5 ba46383a2cc3 both times — Cloudflare's managed block (`ClaudeBot` named and refused, `*` open) plus the operator's lines
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed()       True on `/`, `/emploi`
crawl_delay     none
```

*#233's consolidated list put this host under the fifth form — «Claude-User
permitted by name» — on a 2026-09-11 read; the file read on 2026-09-12 is
the managed block naming `ClaudeBot`, and `Claude-User` falls under `*`.
Both are readings, each dated; the route is the same.*

## The transport — 200, on Vercel

```
GET https://www.asako.mg/          200, 330 453 B, md5 574e7cbe280b   (15:27:50Z, and identical at 15:27:51Z)  «Asako.mg — Offres d'emploi à Madagascar», server: Vercel
GET https://www.asako.mg/emploi    200, 136 440 B, md5 5d3a334cf46c   (15:28:48Z, and identical at 15:28:49Z)  «Toutes les offres d'emploi à Madagascar»
```

## What the listing says

| question | answer |
| :-- | --: |
| offers stated | **251** — «251 offres disponibles», and «Vous voyez 20 offres sur 251» beside the «Charger plus d'offres» button |
| cards in the served HTML | 20 (title · employer · city · sector · contract; «Sponsorisé» on the first) — in the RSC payload (`self.__next_f`), not as `<a href>`: **0 links to an offer page in the HTML** |
| the enumeration | behind «Charger plus», a script; the app router's data route is the adapter's first question |
| JSON-LD | `Organization`, `WebSite`, six `Question`/`Answer` on the root; `BreadcrumbList` on `/emploi`; no `JobPosting` seen |

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE:
  the site serves, states 251, and hides the list behind a script. **Candidate
  adapter** — the Next.js data route (`?_rsc=` or a `/api/`) is what an
  adapter reads; not asked here. *Madagascar's other host of #233,
  `portaljob-madagascar.com`, is an Inertia shell that serves no
  advertisement to a plain client (its own card).*
- **Not a verdict that the host is closed** — nothing refuses us.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
