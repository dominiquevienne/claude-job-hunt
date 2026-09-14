# Board adapter — Jobsgarden (`www.jobsgarden.hu`, Hungary — a recruitment agency's own board): the «jobs-hu» posts through the WordPress REST API the site publishes, `X-WP-Total` as the count it states — 77 emitted, 77 stated, equal

<!-- verified: 2026-09-14 -->

<!-- hosts: www.jobsgarden.hu, jobsgarden.hu -->
<!-- script: jobsgarden.py -->
<!-- host-forms: www.jobsgarden.hu -->
<!-- host-forms-basis: read — `jobsgarden.py:HOST`, a single literal; `jobsgarden.hu` redirects to it · 2026-09-14 -->
<!-- countries: HU -->
<!-- content: measured · **77 emitted over 1 page by `jobsgarden.py list --all` (03:1x UTC), the API states `X-WP-Total` 77 — equal, and the category's own `count` is 77; a reference on 63, a summary on 77 (SSC 33, industry 24, IT 18, corporate 2); one ad read with its page's header line «2026-08-25 • Budapest • IT»** · 2026-09-14 -->
<!-- witness: the REST API's own `X-WP-Total` (and `X-WP-TotalPages`) on the first page of every walk, printed beside the emitted count — «N emitted over P page(s), site states N (X-WP-Total) — equal», exit 6 on a gap; the default walk is bounded (`--pages 10` of 100) and says so, `--all` walks to the count · 2026-09-14 -->

**A recruitment agency whose board is a WordPress category, and the API
that WordPress publishes is the route.** Every ad on `jobsgarden.hu` is a
post in «jobs-hu» (category 8), with a sub-category per practice
(industry 4, IT 5, SSC 6, corporate 7); `GET
/wp-json/wp/v2/posts?categories=8&per_page=100&page=<p>&_fields=…` answers
the posts as JSON and **`X-WP-Total` in the headers** — the count the
site states. The theme's grid at `/allasajanlatok/` (7 pages) is the same
inventory and is not walked. No key, no cookie, no browser. Issue #364
(Hungary; #291 bloc C had read an empty `*` group and an undecounted
sitemap).

## The walk

```
77 emitted over 1 page(s), site states 77 (X-WP-Total) — equal.
```

2026-09-14 03:1x UTC. Two figures of the site agree: the API's
`X-WP-Total` (77) and the category's own `count` in `/wp-json/wp/v2/categories`
(77). 77 distinct ids; the reference in the title's brackets («(VB-12683)»,
«(PE-10961)») emitted as `reference` on 63 of 77 and stripped from
`title`; a one-sentence `summary` (the excerpt) on all — it names the
client's sector, never the client («partnerünk», the agency's choice);
`posted` and `modified` from the post.

## The ad page

`/<slug>/` (an opaque slug, `a0fp900000iudxdmar`). `ad` reads the post
through the API (`slug=`, with `content`) — the body — and the page
itself for what the API does not carry: the header line
`div.jg-job-attributes` **«2026-08-25 • Budapest • IT»**, emitted as
`header_line`, `location`, `sector`. The application form on the page is
never submitted.

## The rules

`/robots.txt` (66 B, 2026-09-14): `User-agent: *` with no directive and a
`Sitemap:` line (a Yoast index: posts, pages, attachments, portfolio,
categories, tags — the posts sitemap is the same inventory, not walked).
Open, `certain: True`; the guard is taken on the exact path before every
request; 3 s own spacing.

## What is withheld

The agency's own office («1134 Budapest, Dévai utca 19.»), phones and
e-mail (`office[kukac]jobsgarden.hu`) sit in the page footer — in no field
this file emits; addresses and phone numbers in the prose are replaced
(`[e-mail withheld]`, `[phone withheld]` — nine digits or more, the
«[kukac]» spelling of «@» included).

## Invocation

```
jobsgarden.py list --all      # 77 emitted over 1 page, site states 77 — equal (2026-09-14)
jobsgarden.py ad --url https://www.jobsgarden.hu/a0fp900000iudxdmar/
```

Exits: 2 broken (a malformed URL) · 3 gone (no post with the slug, or a
post that is not an ad) · 6 partial (a walk short of `X-WP-Total`, HTTP ≠
200, an answer that is not JSON) · 7 refused by the rules · 8 rules
undecidable.
