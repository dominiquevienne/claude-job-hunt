# Board adapter — Revolico (Cuba): rules open, and an anti-robot challenge

<!-- verified: 2026-09-14 -->

<!-- hosts: www.revolico.com -->
<!-- script: none -->
<!-- countries: CU -->
<!-- content: indeterminate · the root answers HTTP 403 with a 5 642-byte Cloudflare interstitial titled `Just a moment...`; nothing of the site was read · 2026-09-07 -->
<!-- witness: none the site states — «Empleos» is a classifieds section without a count; from a connected tab (no challenge shown, 2026-09-14 10:22–10:27 UTC) the search `?category=empleos_` pages to `page=23` (page 30 empty), about a hundred items a page and some forty on the last — about 2 200, the walk's own rough figure, mixing job offers, job seekers («Busco empleo») and goods; nothing is served to the declared client (the moving «Just a moment…», never defeated) · 2026-09-14 -->
<!-- route: browser · 2200 · 2026-09-14 -->

**Cuba's third named host. Its rules open and its transport serves a
challenge, and those are two different kinds of «no».**

## The rules open

```
User-agent: *
Allow: /
Disallow: /checkout/   /cdn-cgi/   /account   /auth   /favorites/
```

**A plain `Allow: /` with five account paths refused**, none of which is a
listing.

## The transport serves an interstitial, not a refusal page

```
GET /   403   5 642 bytes   <title>Just a moment...</title>   cf-ray present
read 1  md5 c516d9a232d3a73f
read 2  md5 ed3be9d53f8a42e1      same size, DIFFERENT fingerprint
```

**The two reads were taken before any comparison**, and that control is what
makes this card correct rather than plausible: *the body carries a
per-request element, so its md5 cannot be compared against any other host's.*
Had it been compared once, this would have been filed as a distinct refusal
page written by this operator — the opposite of what it is.

*`kariera.mk`, measured an hour earlier, is the contrasting case: 25 bytes,
stable across two reads, identical to two other hosts. That one is a vendor
default and the fingerprint says so.*

## And this is where the browser branch stops

The reversal of 2026-09-07 opens the browser to a host whose rules permit and
whose infrastructure refuses. **It keeps four bounds, and the second one
lands here:**

> **We never ask the plugin's user to defeat an anti-robot control** — a
> captcha, a puzzle, a verification. *If the page poses one, we stop and
> record it.*

**`Just a moment...` is that control.** So this host is **not** a browser
candidate, and the distinction from `kariera-mk.md` is not a matter of degree:
that one serves a static refusal, this one serves a challenge meant to be
solved. *A card that filed both as «rules open, transport closed, try the
browser» would have been right about the first and would have walked the
second into exactly the thing the bound forbids.*

## What Cuba is left with

`cubisima.md` is the country's coverage. `yellocu.md` was never a job board.
This host is reachable only through a control we do not defeat.

**Nothing here is a permanent verdict about Revolico** — an interstitial is a
configuration, and it is dated 2026-09-07 like every other observation on a
third-party site in this repository.

## 2026-09-14 10:22–10:27 UTC — the challenge does not show to a connected tab

The 5 642-byte «Just a moment…» with a moving fingerprint is what the
declared client gets (2026-09-07; borne 2, never defeated). A connected
tab was not challenged:

```
tab, /empleos                                    served — redirects to /search?cu=0&category=empleos_ («Empleos Cuba - Revolico»)
tab, /search?cu=0&category=empleos_              served — «Destacados» then the list: about a hundred classifieds, /item/<slug>-<id>, a price on many, pager 1 … 6 «Siguiente >»
tab, …&page=23                                   served — «Página 23», some forty items, «< Anterior 1 … 20 21 22 23», no «Siguiente»: the last page
tab, …&page=30                                   served — «Página 30», an empty list
```

**`route: browser · 2200 · 2026-09-14`** — about 2 200 classifieds by
the pager (22 pages of about a hundred and a last of about forty), the
site's own count nowhere; the section mixes offers («Se busca dependiente»,
«Gestores de venta»), seekers («Busco empleo») and goods, so a reader
sorts them by the title. What a session does from a tab: the search
`?category=empleos_&page=N` to the last page, the id from the `/item/…-<id>`
tail, the price and the title from the card, the ad page for the text —
telephone numbers in the text (they are the way to apply here) withheld.
No script: the declared client is challenged (#404).

