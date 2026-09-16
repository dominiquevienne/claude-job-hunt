# Board adapter — EmpleosEnUruguay (`www.empleosenuruguay.com`, Uruguay): a Blogger blog whose every post is a rewritten job offer — the feed states «3 777» on 2026-09-16, pages by `start-index` fifty at a time, and is an archive back to 2023; `empleosenuruguay.py`, the stated total printed beside a bounded walk, the bodies scrubbed

<!-- verified: 2026-09-16 -->

<!-- hosts: www.empleosenuruguay.com -->
<!-- script: empleosenuruguay.py -->
<!-- host-forms: www.empleosenuruguay.com -->
<!-- host-forms-basis: read — the feed and every post's `alternate` link are on `www.`; the feed's own `next` link points at `www.blogger.com`, which the adapter does not follow (it asks the blog's host by `start-index`); `empleosenuruguay.py` names `www.` as a literal and accepts the apex on an ad address · 2026-09-16 -->
<!-- countries: UY -->
<!-- content: measured · **rules read (86 B): `User-agent: *` — `Disallow: /search`, a Sitemap line; the feed `/feeds/posts/default?alt=json&max-results=50` (200, 617 056 B) is Blogger's JSON — `openSearch$totalResults` 3 777, fifty entries, each with `id` (`…post-<n>`), `published`, `updated`, `category` (labels: a city, an area, a schedule, a level, and on some posts «7 Vacantes» and «$60.610»), `title`, `content` (HTML with AdSense stubs; 39 of the 50 newest embed a JobPosting JSON-LD naming «Empresa empleadora» with validThrough, employmentType, locality, region, industry), an `alternate` link `/<yyyy>/<mm>/<slug>.html`; `start-index=3751` 27 entries — 3 750 + 27 = 3 777, equal, the oldest 2023-01-01: an archive, the live set is not distinguishable from here; `path=/2026/09/<slug>.html` returns the one entry (43 030 B); no e-mail and no phone in the fifty bodies read; `empleosenuruguay.py list --pages 1` on the day: «50 emitted from 1 page(s) of 50, the feed states 3 777 — walked by request»** · 2026-09-16 -->
<!-- witness: the feed's own `openSearch$totalResults` (3 777), read by `empleosenuruguay.py list` beside the walk; the last page's 27 entries close the count on the day — but the total counts the archive, not the live offers · 2026-09-16 -->
<!-- route: http · 3777 · 2026-09-16 -->

**Issue #437 (opened under #417, Uruguay searched on 2026-09-13). Measured
2026-09-16 12:05 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`; the script exercised on the same minute.**
Rank: the pilot's risk order of 2026-09-14 10:4x, after Empleos.hn (#439).

## What this board is — a blog that rewrites offers, not a board that hosts them

Every post is an offer rewritten for search («Buscan Operario de Limpieza
para Trabajar en Montevideo …», «Migración Abre Llamado para 56
Administrativos Zafrales – Sueldo $41.969»); the employer is named in the
prose when it is a public body (Aduanas, ASSE, Migración) and «Empresa
empleadora» otherwise; «Postularse» links to the employer's own form or
portal, never followed. **What the adapter gives is what the blog wrote:
title, date, labels, openings and salary when the title or a label says
them, the embedded JobPosting's fields when there is one, the prose
scrubbed.** *A user who wants the employer's own posting takes the URL to
the employer.*

## The rules, the feed, the transport

```
robots.txt                                           200, 86 B — `*`: Disallow: /search ; Sitemap: /sitemap.xml
allowed('/feeds/posts/default')                      open, certain — the feed is not /search; /search is refused before the gate (exit 7)
GET /feeds/posts/default?alt=json&max-results=50     200, 617 056 B   totalResults 3 777, 50 entries, next → www.blogger.com (not followed)
GET …?alt=json&start-index=3751&max-results=50       200, 252 246 B   27 entries, the oldest published 2023-01-01 — 3 750 + 27 = 3 777
GET …?alt=json&path=/2026/09/operario-limpieza-montevideo-oferta-empleo.html   200, 43 030 B   the one entry
```

**The total is the archive's.** 3 777 posts since 2023 stay in the feed;
nothing marks an offer as closed. So `list` walks two pages (100 posts,
newest first) unless `--pages` says more, and prints «walked by request
(N page(s); the feed is an archive back to 2023), not a shortfall» beside
the stated total — the count is honest about the feed, not about the
market's live offers, and the card says so.

## What the adapter emits, and withholds

`list [--pages N]`: id (the post number), url, title, labels, openings
(«N Vacantes» in the title or a label), salary_uyu («$60.610» in the title
or a label), published, updated, and from the embedded JobPosting when
present — valid_through, employment_type, place, region, industry,
`jobposting: true` — then the prose flattened (AdSense stubs and the
JSON-LD script dropped) and scrubbed. `ad --url`: the same record from
the feed's `path=` lookup, one request, no page markup.

**Withheld:** e-mail addresses and Uruguayan telephone numbers (`+598`,
mobiles `09x xxx xxx`, landlines `2xxx xxxx` / `4xxx xxxx`) in the prose —
none in the fifty read on the day, the scrub is prospective;
`contacts_withheld` on every record; the «Postularse» destination never
followed; the embedded JobPosting's «Empresa empleadora» placeholder not
emitted as a company.

## Tests and mutations

`AUruguayanBloggerBlogWhoseFeedStatesItsTotalAndPagesByStartIndexAndWhosePostsSometimesEmbedAJobPosting`,
both ways on fixtures (the walk by `start-index` with a repeated post read
once, openings from a label and from a title, the embedded JobPosting read
apart and kept out of the prose, the scrub, `--pages`, the equal case, the
two exit-6 cases, `/search` refused, the `path=` lookup). Mutation bench on
a detached copy, `python3 -B`, 6 / 6 red: the total not read · the labels
not searched · the JSON-LD kept in the prose · the body not scrubbed · the
`path=` lookup replaced · the dedup dropped.
