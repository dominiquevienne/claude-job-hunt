# Board adapter — Revolico (Cuba): rules open, and an anti-robot challenge

<!-- verified: 2026-09-07 -->

<!-- hosts: www.revolico.com -->
<!-- script: none -->
<!-- countries: CU -->
<!-- content: indeterminate · the root answers HTTP 403 with a 5 642-byte Cloudflare interstitial titled `Just a moment...`; nothing of the site was read · 2026-09-07 -->
<!-- witness: none — nothing was served -->

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
