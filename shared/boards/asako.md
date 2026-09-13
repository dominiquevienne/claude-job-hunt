# Board measurement — Asako.mg (Madagascar): 251 offers behind a script on 2026-09-12, and on 2026-09-13 a name the .mg registry no longer delegates — NXDOMAIN at `ns.nic.mg`, three public resolvers agree

<!-- verified: 2026-09-13 -->

<!-- hosts: www.asako.mg, asako.mg -->
<!-- script: none -->
<!-- countries: MG -->
<!-- content: measured · rules read twice and certain (1 877 B, Cloudflare's managed block naming `ClaudeBot`, `*` open — `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200 on Vercel at the root (330 453 B, byte-identical twice) and at `/emploi` (136 440 B, byte-identical twice): the listing states «251 offres disponibles» and «Vous voyez 20 offres sur 251 — Charger plus», a Next.js app-router page whose 20 cards are in the RSC payload and whose «load more» is a script; 0 `/emploi/<id>` links in the HTML (2026-09-12 15:28 UTC) — and on 2026-09-13 `www.asako.mg` and `asako.mg` are NXDOMAIN at the registry's own server `ns.nic.mg` (SOA serial 2026091316) and on 1.1.1.1, 8.8.8.8, 9.9.9.9: no delegation today, nothing to read, an adapter cannot be built against a name that does not resolve — a measurement to repeat, not a verdict · 2026-09-13 16:13 UTC -->
<!-- witness: the page's own «251 offres disponibles» and «20 offres sur 251» on 2026-09-12 — two places, one number; on 2026-09-13 the name does not resolve, so there is no witness to read; no adapter yet -->
<!-- route: none · the name has no delegation on 2026-09-13 — NXDOMAIN at the .mg registry's own `ns.nic.mg` (SOA serial 2026091316) and on three public resolvers, where it answered 200 on Vercel on 2026-09-12; a route to nothing declares no browser, and this is a reading to repeat, not a verdict -->

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

## 2026-09-13 — the name no longer resolves, at the registry itself

Asked for the adapter (#233 lot 7), the first fetch of `/emploi` at 16:12 UTC
failed before any request: `URLError: nodename nor servname provided, or
not known`. **A DNS negative is checked by a second resolver, never by a
second host, and at the zone's own authority when it can be** — and
`SERVFAIL` is not `NXDOMAIN`:

```
1.1.1.1   www.asako.mg   NXDOMAIN     asako.mg   NXDOMAIN
8.8.8.8   www.asako.mg   NXDOMAIN     asako.mg   NXDOMAIN
9.9.9.9   www.asako.mg   NXDOMAIN     asako.mg   NXDOMAIN
ns.nic.mg (the .mg registry, +norecurse)   asako.mg NS   NXDOMAIN   — SOA of mg. serial 2026091316, i.e. a zone edited on 2026-09-13
```

**Three public resolvers and the registry's authoritative server: the name
has no delegation on 2026-09-13 at 16:13 UTC**, twenty-five hours after it
answered 200 on Vercel (2026-09-12 15:28 UTC, above). *That is not a
refusal and not a verdict on the board — a delegation can lapse and come
back (a registrar hold, an unpaid renewal), and `bestjobs.mg` on this same
registry went NXDOMAIN on 2026-09-11.* **What it is: no adapter can be
written today, by script or by browser, against a name that does not
resolve** — the script route needs the app router's data route and the
browser route needs a page, and neither exists without the name. *The
251 of 2026-09-12 stands as that day's reading.* **To repeat: `dig
@ns.nic.mg asako.mg NS +norecurse` — a delegation that returns reopens the
candidate adapter exactly where the section below left it.**

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE:
  the site serves, states 251, and hides the list behind a script. **Candidate
  adapter** — the Next.js data route (`?_rsc=` or a `/api/`) is what an
  adapter reads; not asked here. *Madagascar's other host of #233,
  `portaljob-madagascar.com`, is an Inertia shell that serves no
  advertisement to a plain client (its own card).*
- **Not a verdict that the host is closed** — nothing refuses us; on
  2026-09-13 nothing answers, which is a different fact, dated above.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
