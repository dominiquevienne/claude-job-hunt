# Board measurement — Kariyer.net (`www.kariyer.net`, Turkey — the white-collar board of record): a moving Cloudflare challenge to the declared client, and a browser served the whole board — «30719» advertisements stated by the list's own counter, 50 a page, a pager capped at 100, no JobPosting on the ad; `route: browser`, no script

<!-- verified: 2026-09-14 -->

<!-- hosts: www.kariyer.net -->
<!-- script: none -->
<!-- countries: TR -->
<!-- content: measured · **the declared client gets a 403 of 4 913 B on the root (2026-09-13 17:01 UTC — the Cloudflare challenge family, borne 2: never defeated, nobody asked to defeat it); a connected tab is served without any challenge or interaction: `/is-ilanlari` lists 50 advertisements a page (`/is-ilani/<employer-slug>-<title-slug>-<id>`, ids ~4 555 688), a pager `?cp=2 … 100` («100 sayfa») whose page 100 is the last — the plain walk reaches 5 000, the city / district / category facets partition the rest; the list's own counter is client-rendered («0» on first paint, «30719» once hydrated — read on page 100 at 10:12 UTC); the ad page carries a BreadcrumbList JSON-LD and no JobPosting — the fields are the page's own (title, employer, the date in the `<title>` «… İş İlanı - 14.09.2026»); the rules (1 297 B, read 2026-09-01) refuse the signed-in spaces and the filter parameters, never the ads; the sitemap of 2026-09-01 named 96 786 URL of which 65 294 result pages to set aside by their shape** · 2026-09-14 -->
<!-- witness: the list's own hydrated counter «30719», read once on `?cp=100` from a connected tab (10:12 UTC; «0» before hydration on page 1); the pager caps at 100 × 50 = 5 000, so a walk prints its own figure against the counter and says what the cap leaves to the facets; nothing was served to the declared client, so no script prints anything · 2026-09-14 -->
<!-- route: browser · 30719 · 2026-09-14 -->

**Kariyer.net is Turkey's white-collar board of record — 30 719
advertisements by its own counter on the day.** Issue #383. Measured
2026-09-14 10:10–10:14 UTC from a connected tab, in decreasing order after
the pilot's risk list of 09:4x UTC.

## What the client gets, and what a tab gets

```
client, GET /                          403, 4 913 B (2026-09-13) — the Cloudflare challenge family, never defeated
tab, /is-ilanlari                      served — 50 cards, pager ?cp=2 … 100, the counter «0» on first paint (client-rendered)
tab, /is-ilanlari?cp=100               served — the last page («Go to next page» disabled), the counter hydrated: «30719»
tab, /is-ilani/<employer>-<title>-<id> served — a BreadcrumbList JSON-LD, no JobPosting; the page's own fields, the date in the <title>
```

**`route: browser · 30719 · 2026-09-14`.** What a session does from a
tab: `/is-ilanlari?cp=N` to 100, then the city facets for what the cap
leaves, the id from the address tail, the hydrated counter beside the
walk, the ad page's own fields (no JobPosting to read). No script: nothing
is served to a client (#404). Turkey's other fronts: `yenibiris.md` (the
same challenge family, served to a tab the same morning), `secretcv.md`,
`eleman.md`, `iskur.md`.
