# Board measurement — Biznetwork (`www.biznetwork.mn`, Mongolia): named by an expatriates' forum as «a good internet resource for finding jobs in Mongolia» — on 2026-09-17 the root answers HTTP 404 (196 B) on `www.` and on the apex, twice each: no page at the root, no list found

<!-- verified: 2026-09-24 -->

<!-- hosts: www.biznetwork.mn, biznetwork.mn -->
<!-- script: none -->
<!-- countries: MN -->
<!-- content: indeterminate · **`https://www.biznetwork.mn/` and `https://biznetwork.mn/` answer HTTP 404, 196 B, md5 62962daa1b19 identical — a bare «404 Not Found» from the server, no redirect, no page (re-measured 2026-09-24 19:42 UTC, unchanged to the byte); **`/robots.txt` answers the SAME 404 and the SAME 196 B, md5 62962daa1b19** — so `_robots.allowed('www.biznetwork.mn','/')` → open, `certain: True`, `state: absent`, and the 2026-09-17 gloss «the rules file is served» was FALSE; nothing on this host has been shown to be served** · 2026-09-24 -->
<!-- witness: none — nothing was served · 2026-09-24 -->

**Found by the Mongolia search of #603 (a country never searched), measured
2026-09-17 14:0x–14:32 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #603: one
search naming the country's boards (a diaspora career blog's review of
«every job site in Mongolia», the engine's own results), no composed host
names; no public employment service found online by that search. *A
measurement, not an adapter.*

```
_robots.allowed('www.biznetwork.mn', '/')   open, certain — state: absent (the rules PATH is one of the 404s)
GET https://www.biznetwork.mn/            404, 196 B, md5 62962daa1b19  ×2   (2026-09-17)
GET https://biznetwork.mn/                404, 196 B                         (2026-09-17)
GET https://www.biznetwork.mn/            404, 196 B, md5 62962daa1b19       (2026-09-24 19:42 UTC)
GET https://www.biznetwork.mn/robots.txt  404, 196 B, md5 62962daa1b19       (2026-09-24 — byte-identical to the root)
```

**A CORRECTION OF 2026-09-24, and it removes this card's only sign of life.**
The card wrote «open, certain (**the rules file is served**)». It is not: the
rules path answers the same bare 404 as everything else, byte for byte. The
tool's `reason` says so in words — «no rules were read — the host answered HTTP
404 … **A 404 is knowledge**» — and sets `state: absent`.

> **`certain: True` means «no rules apply», not «we read the file».** *Both
> readings give the same verdict — open — so nothing ever contradicted the
> gloss.*

**Why it mattered here more than as a wording slip**: every other line of this
card says nothing was served, and «the rules file is served» was the single
sentence implying a live server behind the name. Removing it, **what remains is
a host that answers one 196-byte 404 to every path tried.**

**Still INDÉTERMINÉ, and deliberately so (§2 sexies)**: the site may live under
a path neither search gave. What is measured is that on two dates, one week
apart, three paths returned the same bare 404. No issue until a list is found.
*Found by the same gloss-hunt as `afgjobs` (#644); `unegui.md` carries the same
sentence and there it is TRUE — its file is read (`state: read`), so it stands.*
