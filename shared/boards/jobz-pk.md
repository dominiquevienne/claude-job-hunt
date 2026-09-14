# Board measurement — Jobz.pk (`www.jobz.pk`, Pakistan): the rules file itself answers 403 — no path open, nothing read, no browser

<!-- verified: 2026-09-14 -->

<!-- hosts: www.jobz.pk, jobz.pk -->
<!-- script: none -->
<!-- countries: PK -->
<!-- witness: none the site states — a directory of employer and newspaper pages, not a counted list; from a connected tab (no challenge shown, 2026-09-14 10:39–10:42 UTC) the newspaper feed `/dawn_jobs/` carries 25 entries dated «14-Sep-2026» and no pager — the day's republished Dawn advertisements; six such feeds (Jang, Express, The News, Dawn, Nawaiwaqt, Mashriq), 655 employer / topic pages linked from `/latest-jobs-in-pakistan/`; nothing is served to the declared client (the Cloudflare challenge, never defeated) · 2026-09-14 -->
<!-- route: browser · 25 · 2026-09-14 -->
**In the #222 candidate list from the Pakistan country page as a «403
to the plain client, browser not measured».** *A measurement and not an
adapter, and a short one: the guard closed the question at the rules
file, the same shape as `kazibongo.md` and `barbadosjobregister.md`.*
Measured 2026-09-13 12:19:23 UTC with the declared client.

## The rules file is refused — twice

```
GET https://www.jobz.pk/robots.txt     403 · cloudflare · 12:19:23 UTC   (bin/fetch-body.py, body not kept by the tool)
GET https://www.jobz.pk/robots.txt     403 · the same, 2 s later
_robots.allowed('www.jobz.pk', '/')    allowed False · certain True · rule "/" · rule_kind host-closed
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
GET https://www.jobz.pk/                                 403, 5 679 B, md5 8f8e51271a7a   (15:29:32Z)
GET https://www.jobz.pk/                                 403, 5 679 B, md5 a9dcff3f1aea   (15:29:33Z)
GET https://www.jobz.pk/jobs                             403, 5 691 B, md5 e2b91c0116a5   (15:29:34Z)
GET https://www.jobz.pk/jobs                             403, 5 691 B, md5 70286d98fe94   (15:29:36Z)
```

**The transport answers a **challenge** — «Attention Required!» / «Just a moment...», the md5 moving at constant size: borne 2 of the 2026-09-07 decision, the plugin neither defeats it nor asks anyone to; a real browser is not measured here.** *A verdict of closure was never
this card's to give (§2 sexies); what it gives now is a dated transport
reading, and the class it falls in.*

## 2026-09-14 10:39–10:42 UTC — the challenge does not show to a connected tab

```
tab, /                            served — the home: 985 links, newspaper feeds (/jang_jobs/, /express_jobs/, /the_news_jobs/, /dawn_jobs/, /nawaiwaqt_jobs/, /mashriq_jobs/), employer pages (/anti-narcotics-force-anf-vacancies/ …), test results, date sheets
tab, /latest-jobs-in-pakistan/    served — a directory: 655 employer / topic pages linked, no dated list, no pager, no count
tab, /dawn_jobs/                  served — 25 entries dated «14-Sep-2026», the day's Dawn advertisements republished, no pager
```

**`route: browser · 25 · 2026-09-14`** — one newspaper feed's day; the
board is a republisher of the press's job advertisements, organised by
paper and by employer, and states no count. What a session does from a
tab: the six `/<paper>_jobs/` feeds, the dated entries of the day, the
entry's page for the scanned advertisement and its text; no JobPosting
was seen. No script: the declared client is challenged (#404).

