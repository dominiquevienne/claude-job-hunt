# Board measurement — Nationale Vacaturebank (`www.nationalevacaturebank.nl`, Netherlands): served to the declared client today, «88.909 banen» stated — an adapter to build, not a browser route

<!-- verified: 2026-09-13 -->

<!-- hosts: www.nationalevacaturebank.nl, nationalevacaturebank.nl -->
<!-- script: none -->
<!-- countries: NL -->
<!-- content: measured · **88 909 advertisements stated by the site** («88.909 banen» on `/vacature/zoeken`, read from a connected browser tab at 13:07 UTC), and the declared client is served — `GET /` 200, 183 810 B, the same md5 twice at 13:27 UTC; the Netherlands page's «WAF DPG» refusal was not met; no JSON-LD on the search page; the cards' addresses not read (masked query strings) · 2026-09-13 -->
<!-- witness: the site's own «88.909 banen» on its search page; the walk to confirm it was not made · 2026-09-13 -->
<!-- route: browser · 88909 · 2026-09-13 -->

**One of the two DPG Media boards the Netherlands page left as «browser /
to build» — and the declared client is served today.** Measured 2026-09-13
13:07 UTC (tab) and 13:27 UTC (client), the guard on the exact path first
(`*` open, certain).

```
robots.txt                          200 — `*` open on /vacature/zoeken; identity claude-user
GET / (declared client)             200, 183 810 B, server DPES — twice, identical md5
tab: /vacature/zoeken               200 «Vacatures zoeken | Nationale Vacaturebank» — **«88.909 banen»** · top functions, no JSON-LD, no challenge
```

**The route is HTTP** — the adapter reads the search page and its pager
with the declared client; the sister `intermediair.nl` (same group) was
not reached: the extension dropped before its page rendered, and the
client was not tried on it. *Not built in this pass.*
