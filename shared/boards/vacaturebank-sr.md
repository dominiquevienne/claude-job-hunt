# Board measurement — Vacaturebank.sr (`vacaturebank.sr`, Suriname — «Suriname's grootste vacatureplatform sinds 2011»): the provider's static 403 to the declared client, and a browser served the whole board — 30 advertisements behind two «Laad meer vacatures» loads on 2026-09-14, a JobPosting per ad; `route: browser`, no script

<!-- verified: 2026-09-14 -->

<!-- hosts: vacaturebank.sr -->
<!-- script: none -->
<!-- countries: SR -->
<!-- content: measured · **the declared client gets the provider's static 403 (25 B, `9ccabba20b9f`, the `jobstore`/`hays` bytes) on the root — the rules open (`_robots.allowed('vacaturebank.sr','/')` → open, certain); a connected tab is served everything: the front page (WordPress; a WebPage / WebSite / Organization JSON-LD graph, «240+ bedrijven», «6000+ volgers» of the WhatsApp alerts, no count of advertisements) lists 8 advertisements and a «Laad meer vacatures» button — two loads bring 23 then 30 and the button disappears: 30 advertisements `/vacature/<slug>/` dated 11 September back to 28 July 2026 (employer, address, Fulltime/Parttime on the card); each ad carries a JobPosting JSON-LD — datePosted, validThrough (30 days), title, description, hiringOrganization (the employer — «HCC Accountants NV»), identifier, jobLocation, directApply — beside the site's graph; no recruiter line seen on the ad read; the application is the candidate account (`/aanmelden`, `/kandidaat-registratie`), never touched** · 2026-09-14 -->
<!-- witness: none the site states — the load-more's end is the count (8 → 23 → 30, the button gone), read once; nothing was served to the declared client, so no script prints anything · 2026-09-14 -->
<!-- route: browser · 30 · 2026-09-14 -->

**Suriname's board of record states no count; thirty advertisements is
what its list yields when «Laad meer» is pressed to the end.** Issue
#444. Measured 2026-09-14 09:37–09:40 UTC from a connected tab, after the
declared client's static 403 of 2026-09-13.

## What the client gets, and what a tab gets

```
_robots.allowed('vacaturebank.sr','/')     open, certain
client, GET /                               403, 25 B, md5 9ccabba20b9f ×2 (2026-09-13) — the provider default seen on eleven hosts
tab, /                                      served — 8 cards, «Laad meer vacatures»; click → 23; click → 30; the button is gone
tab, /vacature/assistant-financial-controller-3/   served — a JobPosting: HCC Accountants NV, 2026-09-11 → 2026-10-11
```

**`route: browser · 30 · 2026-09-14`.** What a session does from a tab:
the front page, «Laad meer vacatures» until it disappears, the slug of
`/vacature/<slug>/` as the key, the ad's JobPosting; the site states no
count, so the load-more's end is printed as the walk's own figure. No
script: nothing is served to a client (#404). Suriname's other board is
Werkstraat (#445), not measured here.
