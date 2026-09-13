# Board measurement — Bikroy (`bikroy.com`, Bangladesh): the rules file itself answers 403 — no path open, nothing read, no browser

<!-- verified: 2026-09-13 -->

<!-- hosts: bikroy.com -->
<!-- script: none -->
<!-- countries: BD -->
<!-- witness: none — nothing past the rules file was requested; the guard's verdict (`allowed False, certain True, rule_kind host-closed`) is the only body this card holds, taken twice two seconds apart · 2026-09-13 -->
<!-- route: none · the rules file answers 403 — an absence of rules since #283 (2026-09-13) — and the transport answers a Cloudflare challenge, twice (borne 2): no route by script, a browser not measured · 2026-09-13 -->
**In the #222 candidate list from the Bangladesh country page as a «403
to the plain client, browser not measured».** *A measurement and not an
adapter, and a short one: the guard closed the question at the rules
file, the same shape as `kazibongo.md` and `barbadosjobregister.md`.*
Measured 2026-09-13 12:19:36 UTC with the declared client.

## The rules file is refused — twice

```
GET https://bikroy.com/robots.txt     403 · cloudflare · 12:19:36 UTC   (bin/fetch-body.py, body not kept by the tool)
GET https://bikroy.com/robots.txt     403 · the same, 2 s later
_robots.allowed('bikroy.com', '/')    allowed False · certain True · rule "/" · rule_kind host-closed
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
«route: none (13.09)» — a verdict taken on the rules file alone. Since #283 the 403 on
`/robots.txt` is `no-rules-403`, `allowed: True, certain: False`: nothing
was read, nothing forbids, and **the transport decides**. Measured with
`bin/fetch-body.py --allow-refusal` under the new guard, the root (and a
listing path where one was known) twice:

```
GET https://bikroy.com/                                  403, 5 636 B, md5 d4a490503140   (15:29:44Z)
GET https://bikroy.com/                                  403, 5 636 B, md5 a82174c5ad77   (15:29:45Z)
GET https://bikroy.com/jobs                              403, 5 648 B, md5 3935e8866c5a   (15:29:46Z)
GET https://bikroy.com/jobs                              403, 5 648 B, md5 d58145a45cc6   (15:29:48Z)
```

**The transport answers a **challenge** — «Attention Required!» / «Just a moment...», the md5 moving at constant size: borne 2 of the 2026-09-07 decision, the plugin neither defeats it nor asks anyone to; a real browser is not measured here.** *A verdict of closure was never
this card's to give (§2 sexies); what it gives now is a dated transport
reading, and the class it falls in.*
