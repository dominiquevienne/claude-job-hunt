# Board measurement — PaperPk (`www.paperpk.com`, Pakistan): the rules file itself answers 403 — no path open, nothing read, no browser

<!-- verified: 2026-09-14 -->

<!-- hosts: www.paperpk.com, paperpk.com -->
<!-- script: none -->
<!-- countries: PK -->
<!-- witness: none — nothing past the rules file was requested; the guard's verdict (`allowed False, certain True, rule_kind host-closed`) is the only body this card holds, taken twice two seconds apart · 2026-09-13 -->
<!-- route: none · non faisable — validé par le propriétaire le 14.09.2026 (verbatim : « 1, 2, 3, 4, 5 => exclue ») — measured: Cloudflare's «Sorry, you have been blocked» to a real browser on 2026-09-14 — a block page, not a challenge; the declared client challenged · 2026-09-14 -->
**In the #222 candidate list from the Pakistan country page as a «403
to the plain client, browser not measured».** *A measurement and not an
adapter, and a short one: the guard closed the question at the rules
file, the same shape as `kazibongo.md` and `barbadosjobregister.md`.*
Measured 2026-09-13 12:19:27 UTC with the declared client.

## The rules file is refused — twice

```
GET https://www.paperpk.com/robots.txt     403 · cloudflare · 12:19:27 UTC   (bin/fetch-body.py, body not kept by the tool)
GET https://www.paperpk.com/robots.txt     403 · the same, 2 s later
_robots.allowed('www.paperpk.com', '/')    allowed False · certain True · rule "/" · rule_kind host-closed
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
«route: none — Cloudflare (13.09)» — a verdict taken on the rules file alone. Since #283 the 403 on
`/robots.txt` is `no-rules-403`, `allowed: True, certain: False`: nothing
was read, nothing forbids, and **the transport decides**. Measured with
`bin/fetch-body.py --allow-refusal` under the new guard, the root (and a
listing path where one was known) twice:

```
GET https://www.paperpk.com/                             403, 6 163 B, md5 9fdf12bfb889   (15:29:37Z)
GET https://www.paperpk.com/                             403, 6 163 B, md5 c1f294f71515   (15:29:38Z)
```

**The transport answers a **challenge** — «Attention Required!» / «Just a moment...», the md5 moving at constant size: borne 2 of the 2026-09-07 decision, the plugin neither defeats it nor asks anyone to; a real browser is not measured here.** *A verdict of closure was never
this card's to give (§2 sexies); what it gives now is a dated transport
reading, and the class it falls in.*

## 2026-09-14 10:42 UTC — «Sorry, you have been blocked» to a connected tab

`https://www.paperpk.com/` in a real browser: Cloudflare's «Attention
Required! — Sorry, you have been blocked — You are unable to access
paperpk.com», a block page and not a challenge (nothing to solve; the
operator's firewall rule refuses the visitor). Borne 0 of the 2026-09-07
doctrine: a refusal rendered to a real browser is the operator's. `route:
none` stands; the word «closed» is the owner's (§2 sexies). The same
publisher's `paperpk.jobz.pk` is linked from Jobz.pk (`jobz-pk.md`), which
a tab reads.

## 2026-09-14 11:0x UTC — non faisable, validé par le propriétaire

**non faisable — validé par le propriétaire le 14.09.2026 (verbatim : « 1, 2, 3, 4, 5 => exclue »)** — relayed verbatim by the pilot (#323). What was measured above is the measurement; the word «closed» is the owner's, and he has given it: Cloudflare's «Sorry, you have been blocked» to a real browser on 2026-09-14 — a block page, not a challenge; the declared client challenged. The card stays as the record of the measurements; `route: none` is dated and motivated by this line, and the Atlas excludes the entry from the feasible denominator (#404). What would reopen it is written in the sections above; nothing is scheduled.

