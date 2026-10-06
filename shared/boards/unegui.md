# Board measurement — Unegui jobs (`www.unegui.mn/ajil/`, Mongolia): the country's classifieds site's «ажил» (jobs) section — on 2026-09-17 every read answers HTTP 403 with a 5.7 KB «Just a moment...» page, the fingerprint moving: a Cloudflare challenge; consigned, not defeated (borne 2); a tab is the next reading

<!-- verified: 2026-09-29 -->

<!-- hosts: www.unegui.mn -->
<!-- script: none -->
<!-- countries: MN -->
<!-- content: indeterminate · **RE-MEASURED 2026-09-29, and the challenge HOLDS twelve days on: `/ajil/` answers HTTP 403, 5 654 B on two reads, md5 fa08ea528785 / 298b785ee232 — `<title>Just a moment...</title>`, `cf_chl` ×10, `challenge` ×8, `cdn-cgi` ×1. AND THE MOVING FINGERPRINT IS NOW EXPLAINED rather than merely observed: the two bodies differ at byte 407, in a per-request CSP nonce (`nonce-d7PNRbilvUdN6SZ6fVblzr` / `nonce-lNGmJUFoegEAhUSeRsf1Sn`) — so the classification rests on the CONTENT, not on the movement. `_robots.allowed` → open, certain, on `/ajil/` and on `/`** · 2026-09-29 -->

<!-- witness: none — nothing was served · 2026-09-17 -->
<!-- content: indeterminate · **`/ajil/` answers HTTP 403, 5 657 B, md5 c4803b639521 / 0993c3d41b29 — «Just a moment...», a Cloudflare managed challenge (the `revolico` class) — under the declared identity, twice; `_robots.allowed('www.unegui.mn','/ajil/')` → open, certain (the rules file is served, the pages are not); nothing of the section was read** · 2026-09-17 -->
## Re-measured 2026-09-29 — the challenge holds, and why that is not a fingerprint argument

**Two reads of the exact path under the declared identity, the guard taken first:**

```
HTTP 403   5 654 B   md5 fa08ea528785      <- lecture 1
HTTP 403   5 654 B   md5 298b785ee232      <- lecture 2
<title>Just a moment...</title>     cf_chl x10   challenge x8   cdn-cgi x1
```

**The fingerprint moves, and this time the reason is named: the bodies differ at byte 407, inside a
per-request CSP nonce.** *A moving `md5` alone proves only that the body carries something
per-request — it is why cross-host comparison of these bodies would be void.* **So the verdict rests
on what the body IS — a Cloudflare managed challenge — and not on the movement.**

**Borne 2 stands: a challenge is not defeated, and no one is asked to defeat it.** The HTTP route is
closed, and that is a statement about the ROUTE, not about the board: the section is not declared
closed, and §2 sexies reserves that to the owner. *What remains open is the browser reading, where
the interstitial resolves on its own — the form delivered for #658.*

**Found by the Mongolia search of #603 (a country never searched), measured
2026-09-17 14:0x–14:32 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #603: one
search naming the country's boards (a diaspora career blog's review of
«every job site in Mongolia», the engine's own results), no composed host
names; no public employment service found online by that search. *A
measurement, not an adapter.*

```
_robots.allowed('www.unegui.mn', '/ajil/')   open, certain
GET https://www.unegui.mn/ajil/               403, 5 657 B, md5 moving ×2 — «Just a moment...»
```

**A challenge in front of a classifieds site** (apartments, cars, and a
jobs section): the plugin neither defeats it nor asks the user to
(borne 2); whether a tab is served without a click is a browser-time
question (Revolico — a classifieds site too — was, 2026-09-14).
INDÉTERMINÉ; the issue says what blocks.
