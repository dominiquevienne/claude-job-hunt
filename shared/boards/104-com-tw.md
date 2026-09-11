# Board measurement — 104.com.tw (Taiwan): a challenge page to our client, and a challenge is not crossed

<!-- verified: 2026-09-11 -->

<!-- hosts: 104.com.tw, www.104.com.tw -->
<!-- script: none -->
<!-- countries: TW -->
<!-- witness: none — nothing was read past the refusal; the only figure this card holds is the refusal's own size, 5 648 bytes, and its fingerprint moves on every request · 2026-09-11 -->

**This card is a measurement and not an adapter.** *No card declared `TW`
before it; the host was known to the repository as a line in
`shared/robots-policy.md` — «a 403 the browser denies … two md5s for apex and
www, and its search page loads fine in Chrome» (2026-09-08) — and nothing
had measured which KIND of refusal it is.* **That is the question this card
answers, and the answer closes the browser route for now.**

## Step 1 — the rules, twice, on both hosts (2026-09-11 13:39–13:41 UTC)

```
https://104.com.tw/robots.txt        403   twice   Cloudflare (server, cf-ray)   guard: host-closed, rule "/", certain True
https://www.104.com.tw/robots.txt    403   twice   Cloudflare                    guard: host-closed, rule "/", certain True
```

**The host refuses its own rules file** — on the apex and on the `www`, four
reads, four 403s. *`_robots.allowed()` calls this `host-closed`: not an absent
file, not an unreadable one — the host replied, and the reply was no.* No
`Disallow` was ever read, so nothing here is a rule written by the operator.

## The question that sorts — STABLE or MOVING fingerprint — and the answer

**The refusal body, read four times, is the SAME request the guard sends
(`/robots.txt`, our declared identity), repeated to read what it carries:**

```
104.com.tw      #1  403   5 648 o   md5 e62ed710fce62e82b751b7696a677a6e   <title>Just a moment...</title>
104.com.tw      #2  403   5 648 o   md5 9862ba5ee99133871e29321dd4aa8dc3   bodies differ at byte 408
www.104.com.tw  #1  403   5 648 o   md5 678323f188f937df0d22ddcb76eae616
www.104.com.tw  #2  403   5 648 o   md5 93c637511161a16a6911d9bac4490f09
                                     `challenge` ×8 in the body
```

**Same size every time, a different fingerprint every time, titled «Just a
moment…»** — *this is family (3) of `shared/robots-policy.md`, the challenge
page whose md5 moves per request, the `revolico.com` class — and not
family (1), the 25-byte vendor default of `eshjob`, `kariera.mk`, `jobs.af`.*

> **A challenge is bound 2 of the 07.09 doctrine: we do not defeat it, and we
> do not ask the user of the plugin to defeat it.** *So this host does NOT go
> to #222 — that list is the eleven whose refusal is a static 403 to a client
> that a browser is served past without a challenge.*

**What stays open, and cannot be sorted from here.** The policy's own
distinction — *a passive interstitial is re-read; a challenge that asks for a
click is a stop* — decides whether a browser route exists, and **it is a
browser-time question**: from a scripted client both shapes are the same
5 648 bytes. The 08.09 note that «its search page loads fine in Chrome» is
consistent with a passive interstitial and with a human having clicked; it does
not say which. **If a session with the extension connected loads a search page
here without any click, that observation reopens this card as a browser
candidate; until then it is closed by a challenge, dated.**

## What this card does not say

Nothing about the board's size, its markup, its ids or its language — nothing
was read. Nothing about the operator's intention — no rule was read either.
**«Taiwan has no board» is not a sentence this repository can write from this
card; «Taiwan's largest board serves our client a challenge page» is.**
