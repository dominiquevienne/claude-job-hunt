# Board measurement — Portal Pune (`portalpune.com`, Kosovo): the rules file itself answers 403 — no path open, nothing read, no browser

<!-- verified: 2026-09-14 -->

<!-- hosts: portalpune.com -->
<!-- script: none -->
<!-- countries: XK -->
<!-- witness: the site's own «192 konkurse aktive» on `/jobs`, read from a connected tab (no challenge shown, 2026-09-14 10:37 UTC) — 192 distinct `/jobs/<id>-<slug>` on the one page, equal; the home's «408 Vende të lira pune» is positions and «36.361 Konkurse të publikuara» lifetime, neither this count; nothing is served to the declared client (the Cloudflare challenge, never defeated) · 2026-09-14 -->
<!-- route: browser · 192 · 2026-09-14 -->
**In the #222 candidate list from the Kosovo country page as a «403
to the plain client, browser not measured».** *A measurement and not an
adapter, and a short one: the guard closed the question at the rules
file, the same shape as `kazibongo.md` and `barbadosjobregister.md`.*
Measured 2026-09-13 12:19:18 UTC with the declared client.

## The rules file is refused — twice

```
GET https://portalpune.com/robots.txt     403 · cloudflare · 12:19:18 UTC   (bin/fetch-body.py, body not kept by the tool)
GET https://portalpune.com/robots.txt     403 · the same, 2 s later
_robots.allowed('portalpune.com', '/')    allowed False · certain True · rule "/" · rule_kind host-closed
```

**A `403` on the rules file is a refusal, and the doctrine keeps it one**
(the 2026-09-09 decision reopened `401` alone). No path is open, so the
browser branch — «the rules open, the transport refuses» — has nothing to
start from: **nothing beyond the rules file was requested, no tab was
opened.** *A refusal at the rules does not say what it refuses — a front
rule on `/robots.txt`, a firewall keyed on our identity, or a host that
serves no rules to anyone look the same from here.*

## What reopens it

- `robots.txt` answering anything but 403 to the declared client;
- a later pair of reads minutes apart (`grabjobs.co` once cleared within
  seconds — `robots-policy.md`);
- a doctrine decision on a 403 *at the rules file* — posed by
  `kazibongo.md`, `barbadosjobregister.md` and this card, not decided by
  them. **Eleven hosts now sit on that question.**

## What this card does not say

Nothing about what the site serves, its size, or whether a browser is
served — a browser was not opened.

## 2026-09-13 — #283: an unread rules file is an absence of rules, and the transport measured

**Owner's decision of 2026-09-13, verbatim: «toutes incapacité d'ouvrir robots.txt
doit aboutir à l'absence de règles et donc à l'ouverture».** This card read
«route: none — Cloudflare 403 on the rules file (13.09)» — a verdict taken on the rules file alone. Since #283 the 403 on
`/robots.txt` is `no-rules-403`, `allowed: True, certain: False`: nothing
was read, nothing forbids, and **the transport decides**. Measured with
`bin/fetch-body.py --allow-refusal` under the new guard, the root (and a
listing path where one was known) twice:

```
GET https://portalpune.com/                              403, 4 575 B, md5 4e7c037b1d9a   (15:29:29Z)
GET https://portalpune.com/                              403, 4 575 B, md5 49831b149b72   (15:29:31Z)
```

**The transport answers a **challenge** — «Attention Required!» / «Just a moment...», the md5 moving at constant size: borne 2 of the 2026-09-07 decision, the plugin neither defeats it nor asks anyone to; a real browser is not measured here.** *A verdict of closure was never
this card's to give (§2 sexies); what it gives now is a dated transport
reading, and the class it falls in.*

## 2026-09-14 10:36–10:38 UTC — the challenge does not show to a connected tab

```
tab, /                       served — the home: «408 Vende të lira pune» (positions), «36.361 Konkurse të publikuara» (lifetime), «+7 konkurse sot», employers (/businesses/<slug>)
tab, /jobs                   served — «192 konkurse aktive», every card on the one page: 192 distinct /jobs/<10-digit id>-<slug>, no pager, no load-more
```

**`route: browser · 192 · 2026-09-14`** — equal to the statement. The
same postings as Shpallje Pune's (the KEC tender, the «Shofer (kategoria
C)» ad) appear on both — two boards on one Kosovar market, the id
different on each. What a session does from a tab: `/jobs`, the id from
`/jobs/<id>-<slug>`, the card, the ad page for the text. No script: the
declared client is challenged (#404).

