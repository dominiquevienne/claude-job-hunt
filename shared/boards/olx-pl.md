# Board measurement — OLX Poland (`www.olx.pl`, Poland): the rules file itself answers 403 — no path open, nothing read, no browser

<!-- verified: 2026-09-13 -->

<!-- hosts: www.olx.pl, olx.pl -->
<!-- script: none -->
<!-- countries: PL -->
<!-- witness: none — nothing past the rules file was requested; the guard's verdict (`allowed False, certain True, rule_kind host-closed`) is the only body this card holds, taken twice two seconds apart · 2026-09-13 -->
<!-- route: none · the rules file answers 403 — an absence of rules since #283 (2026-09-13) — and the transport answers a static 403 to this client, twice (family (1) of #222): a browser route is legitimate and not yet measured · 2026-09-13 -->
**In the #222 candidate list from the Poland country page as a «403
to the plain client, browser not measured».** *A measurement and not an
adapter, and a short one: the guard closed the question at the rules
file, the same shape as `kazibongo.md` and `barbadosjobregister.md`.*
Measured 2026-09-13 12:19:44 UTC with the declared client.

## The rules file is refused — twice

```
GET https://www.olx.pl/robots.txt     403 · CloudFront («Error from cloudfront») · 12:19:44 UTC   (bin/fetch-body.py, body not kept by the tool)
GET https://www.olx.pl/robots.txt     403 · the same, 2 s later
_robots.allowed('www.olx.pl', '/')    allowed False · certain True · rule "/" · rule_kind host-closed
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
«route: none — CloudFront (13.09)» — a verdict taken on the rules file alone. Since #283 the 403 on
`/robots.txt` is `no-rules-403`, `allowed: True, certain: False`: nothing
was read, nothing forbids, and **the transport decides**. Measured with
`bin/fetch-body.py --allow-refusal` under the new guard, the root (and a
listing path where one was known) twice:

```
GET https://www.olx.pl/                                  403, 919 B, md5 28e3167e761b   (15:29:54Z)
GET https://www.olx.pl/                                  403, 919 B, md5 19b58ef54879   (15:29:55Z)
GET https://www.olx.pl/praca/                            403, 919 B, md5 398f926a069c   (15:29:56Z)
GET https://www.olx.pl/praca/                            403, 919 B, md5 083dadd614fd   (15:29:57Z)
```

**The transport answers a **static 403** — the same bytes on every fetch: a refusal at the transport aimed at the client, family (1) of #222, where a browser is legitimate and is not measured here.** *A verdict of closure was never
this card's to give (§2 sexies); what it gives now is a dated transport
reading, and the class it falls in.*
