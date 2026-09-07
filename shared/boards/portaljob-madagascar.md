# Board adapter — PortalJob Madagascar (open, and unreadable)

<!-- verified: 2026-09-07 -->

<!-- hosts: www.portaljob-madagascar.com -->
<!-- script: none -->
<!-- countries: MG -->
<!-- content: indeterminate · HTTP 200 on the root and no content served — 8 598 o carrying 5 links, all to `/build/` assets and icons, zero `<a>` to a page, zero `<form>`, no `<title>`, no `ld+json` · 2026-09-07 -->
<!-- witness: none — nothing could be read, and the reason is the page, not the host -->

**This host answers `200` and serves nothing. Madagascar stays at zero
coverage, and the reason is neither a refusal nor an absent board.**

## `200` is not `readable`, and that is the whole card

**Do not read the status code as access.**

```
GET /   → 200, 8 598 o
          <div>      1
          <script>   6
          <a>        0        <- the discriminator
          <form>     0
          <title>    absent
          ld+json    absent
          the 5 hrefs point at /build/… assets and two icons
```

**It is an application shell.** The page is a mount point; a browser runs the
scripts and the content appears. **A plain HTTP client — ours, or any
enumerator — receives the shell and nothing else.**

## The control that distinguishes it, so the next reader does not rediscover it

> **The signature is zero content links on a body of several kilobytes — not
> the size.**

*A small body can be a real page. A large body can be a shell. **What separates
them is that a shell links only to its own assets.*** `rozeegpt.ai` and
`recruit-ai.co` gave the same reading — `<div id="root">`, a bundle, no
content — and so did two advertisement URLs on `rozee.pk` that were answered by
someone else's shell.

**A card that wrote "open" on this host would manufacture coverage that does
not exist**, and every aggregate counting open hosts would carry Madagascar.
*That is `bestzambiajobs.com` on a different object: there the rules were
impeccable and the domain had changed hands; here the object is genuinely a
board and its content is not served.*

## What would change this

**Nothing that this repository does today.** *Reading it needs a browser to run
its scripts — the branch the owner opened on 2026-09-07 for hosts whose rules
open and whose transport refuses.* **This host's transport does not refuse: it
answers `200`.** So it is not that branch either, and it belongs to no route we
have.

**It is not disqualified. It is not qualifiable.** *The distinction matters:
`jobstore.md` is refused, `tanqeeb.md` is unreadable at the rules layer, and
this one serves a page that contains nothing — three different facts that a
single "no" would flatten.*
