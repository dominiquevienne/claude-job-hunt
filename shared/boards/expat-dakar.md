# Board measurement — Expat-Dakar (`www.expat-dakar.com`, Senegal): the rules file itself answers 403 — no path open, nothing read, no browser

<!-- verified: 2026-09-14 -->

<!-- hosts: www.expat-dakar.com, expat-dakar.com -->
<!-- script: none -->
<!-- countries: SN -->
<!-- witness: the site's own «327 résultats trouvés» on `/emploi`, read from a connected tab on page 1 and page 32 (no challenge shown, 2026-09-14 10:31–10:33 UTC) — ten cards a page, `?page=2 … 32` and a «Suivant »» to 33: 327 in 33 pages; the «14 Offres d'emploi» beside it is the category's sub-filter; nothing is served to the declared client (the Cloudflare challenge, never defeated) · 2026-09-14 -->
<!-- route: browser · 327 · 2026-09-14 -->
**In the #222 candidate list from the Senegal country page as a «403
to the plain client, browser not measured».** *A measurement and not an
adapter, and a short one: the guard closed the question at the rules
file, the same shape as `kazibongo.md` and `barbadosjobregister.md`.*
Measured 2026-09-13 12:19:31 UTC with the declared client.

## The rules file is refused — twice

```
GET https://www.expat-dakar.com/robots.txt     403 · cloudflare · 12:19:31 UTC   (bin/fetch-body.py, body not kept by the tool)
GET https://www.expat-dakar.com/robots.txt     403 · the same, 2 s later
_robots.allowed('www.expat-dakar.com', '/')    allowed False · certain True · rule "/" · rule_kind host-closed
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
GET https://www.expat-dakar.com/                         403, 5 674 B, md5 f90470bc02c5   (15:29:39Z)
GET https://www.expat-dakar.com/                         403, 5 674 B, md5 c93ec172d9cd   (15:29:40Z)
GET https://www.expat-dakar.com/emploi                   403, 5 692 B, md5 289f381546d3   (15:29:42Z)
GET https://www.expat-dakar.com/emploi                   403, 5 692 B, md5 aee748063bc2   (15:29:43Z)
```

**The transport answers a **challenge** — «Attention Required!» / «Just a moment...», the md5 moving at constant size: borne 2 of the 2026-09-07 decision, the plugin neither defeats it nor asks anyone to; a real browser is not measured here.** *A verdict of closure was never
this card's to give (§2 sexies); what it gives now is a dated transport
reading, and the class it falls in.*

## 2026-09-14 10:31–10:33 UTC — the challenge does not show to a connected tab

```
tab, /emploi                 served — «327 résultats trouvés», ten cards a page (/annonce/<slug>), the city facets (/emploi/dakar …), pager ?page=2 … 32 «Suivant »»
tab, /emploi?page=32         served — «327 résultats trouvés», «Suivant »» to page 33: 33 pages of ten
cards                        /annonce/<slug>; the ad page not read; the page's JSON-LD is the site's graph (Organization, WebSite, WebPage, BreadcrumbList), no JobPosting on the list
```

**`route: browser · 327 · 2026-09-14`** — the site's own count for the
«Emploi» section of the classifieds site. What a session does from a tab:
`/emploi?page=N` to the last, the slug of `/annonce/<slug>` as the key, the
card, the ad page for the text — telephone numbers (the way to apply on a
classifieds site) withheld. No script: the declared client is challenged
(#404).
