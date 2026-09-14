# Board adapter — Práca SME (`praca.sme.sk`, Slovakia — the daily SME's board): the rules path answers a moving «Security Verification» challenge, every page a static 402 «Please contact the site owner for access» — measured twice on 2026-09-14, no adapter, a browser candidate not yet measured (#346)

<!-- verified: 2026-09-14 -->

<!-- hosts: praca.sme.sk, www.praca.sk -->
<!-- script: none -->
<!-- countries: SK -->
<!-- content: measured · **`/robots.txt` answers HTTP 403 with 22 955 B titled «Security Verification | SME» (captcha/challenge words in the body, md5 moving between two reads: 1e18b5674616 / 4b15655603a4) — no rules readable, an absence of rules under #283; `/` and `/ponuky` answer HTTP 402, 55 B, `{"message":"Please contact the site owner for access."}`, md5 48817d6864f7 identical on three reads (02:41–02:42 UTC), the same body the country search read on 2026-09-13 16:59; `www.praca.sk` redirects here and meets the same 402** · 2026-09-14 -->
<!-- witness: none — no page was served to the declared client, so no count of the site's own was read · 2026-09-14 -->

**Two refusals of two kinds, and the one that matters for the browser
branch is the static one.** Issue #346 (Slovakia; #291 bloc C) named a
402 on the root on 2026-09-13; on 2026-09-14 the declared client, guard
on the exact path, read:

| address | answer | reads |
| :-- | :-- | :-- |
| `/robots.txt` | **403**, 22 955 B, «Security Verification \| SME», captcha/challenge in the body, **md5 moving** | 2 |
| `/` | **402**, 55 B, `{"message":"Please contact the site owner for access."}`, **md5 identical** (`48817d6864f7`) | 3 (and the country search's read of 2026-09-13: the same md5) |
| `/ponuky` | 402, the same 55 B | 1 |
| `https://www.praca.sk/` | redirects to `praca.sme.sk/`, the same 402 | 1 |

## What this is, under the doctrine

- **The rules path is behind a challenge** — a page whose purpose is to tell
  a robot from a person. Under #283 an unreadable `robots.txt` is an absence
  of rules (`certain: False`); the challenge on that path is not defeated
  and is not the site's answer about its pages.
- **The pages answer a static 402** — 55 bytes, the same md5 on four reads
  over two days, a JSON message, not a challenge: the `jobstore` family,
  not the `revolico` family. Under the 2026-09-07 doctrine a static refusal
  served to the declared client is a **browser candidate**: borne 0 asks
  whether a real browser is served the same 402 (the editor's refusal to
  everyone) or the board (an infrastructure that does not know who we are).
- **That measurement is not made here**: the session that wrote this card
  has no browser attached (the Chrome extension was not connected on
  2026-09-14 02:4x UTC). So this card carries no `route:` line — neither
  `browser · N` nor `none` — and the issue stays open for a session with a
  tab: one visit to `https://praca.sme.sk/`, the count the list states,
  the walk to it; or the same 402 in the tab, and then `route: none · the
  402 is served to a browser too · <date>`, which the owner validates
  (§2 sexies).

## What the board is, from outside

`praca.sk` — the historic Slovak board — redirects to `praca.sme.sk`, the
daily SME's job section. Nothing of its inventory was read: no count, no
card, no ad page. Slovakia's read boards on this day: Profesia
(`profesia.md`), the public employment service (`sluzbyzamestnanosti.md`,
which republishes Profesia, Kariéra and four others, not this one) and
Kariéra (`kariera.md`).
