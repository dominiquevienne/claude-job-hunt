# Board adapter — eJobsFiji (Fiji)

<!-- verified: 2026-09-07 -->

<!-- hosts: ejobsfiji.com -->
<!-- host-forms: ejobsfiji.com -->
<!-- host-forms-basis: read — `ejobsfiji.py:BASE`, a single literal; no second form is fetched · 2026-09-07 -->
<!-- script: ejobsfiji.py -->
<!-- countries: FJ -->
<!-- content: measured · 9 advertisements in a sitemap of 397 URLs, the other 388 being 377 company pages, 6 blog posts and the site's static pages; nothing published since 2026-08-03 · 2026-09-07 -->
<!-- witness: none published by the site; 9 is the count of `/jobs/view?id=<n>` entries in its own sitemap, and Fiji's country page recorded 14 on 2026-09-04 · 2026-09-07 -->
<!-- overlap: myjobsfiji.md · 6 shared advertisements, title match confirmed on the employer 6 of 6; 9 read on ejobsfiji and 190 on myjobsfiji, both from their own sitemaps · 2026-09-07 -->

**Fiji's second board, and a small one.** Open, readable, and quiet —
**nothing has been published here since 2026-08-03**, thirty-five days. *Those
are three different facts from «broken», and a card that wrote «broken» would
have been wrong in a way nobody would reopen.*

## Nine advertisements in 397 URLs

```
/companies/…  377      /blogs/…   6      /jobs/…   10      static  4
/jobs/view?id=<n>   9      <- the advertisements
```

Fiji's country page recorded fourteen on 2026-09-04. **Both are counts of the
same thing three days apart, and neither corrects the other.**

## The identifier is in the query string

`/jobs/view?id=1120`. **Every advertisement shares the path `/jobs/view`**,
so the query is not part of the identity — it *is* the identity.

The guard is taken on path **and** query through `full_path()`, which exists
because 54 of this repository's 55 call sites once took `parts.path` alone.
*On most boards that defect would have asked about a refused path; here it
would have asked about a path the board never serves on its own.*

The schema states the same number in `identifier.value`, and the module
prefers it. **They agreed on all nine**, and `id_source` records which was
used so a future disagreement is visible rather than silent.

## Dates are real here, and worthless on the board next door

```
9 advertisements · 9 with lastmod · 6 distinct dates · 2026-05-29 → 2026-08-03
```

**So `--since` works on the sitemap alone**, one request. *`myjobsfiji`
stamps all 3 152 of its entries with a single rebuild date and cannot.*

> **Two boards in one country, and the same field is load-bearing on one and
> worthless on the other.**

*The busiest day carries four of nine. That is not reported as 44 %: at n = 9
it is four advertisements, and a percentage would dress a count as a rate.*

## Six of its nine are also on `myjobsfiji`

**Confirmed on the employer, 6 of 6** — not inferred from the titles that
found them:

```
ej 1120 / mj 50965   Ram Sami & Sons (Fiji) Pte Limited   ==
ej 1027 / mj 50866   Ram Sami & Sons (Fiji) Pte Limited   ==
ej 1049 / mj 50889   Fiji Govt                            ==
ej 1036 / mj 50882   Fiji Govt                            ==
ej  827 / mj 49080   Fiji Airports                        ==
ej  811 / mj 50561   PKF ALIZ PACIFIC                     ==
```

**The relation is asymmetric and the single number hides that**: six is two
thirds of this board and three per cent of the other. *Neither figure is
wrong; a reader who takes «6» for a measure of `myjobsfiji` has taken the
wrong one.*

*Two of the six are confirmed against `Fiji Govt`, a name several ministries
share, so the employer adds less there than it does on `Ram Sami & Sons`.*
**The titles carrying them are specific** — *«Junior Physiotherapist
(Open)(Ministry of Health and Medical Services)»* — and the two together are
what this card rests on.

**And the slug is not an identifier on either side**: `myjobsfiji` renders 190
advertisements under 184 distinct slugs. *That is the same caveat the Kosovo
pair required, measured again rather than carried over.*

## The schema carries HTML entities inside its JSON

`hiringOrganization.name` arrives as `Ram Sami &amp;amp; Sons (Fiji) Pte
Limited`. **The entity survives JSON decoding because it was never JSON
escaping** — it is HTML escaping applied before the block was serialised.
Emitting it raw would put `&amp;amp;` into every employer name containing an
ampersand, and the first run of this adapter did exactly that.

Every string taken from the schema now passes `html.unescape`.

## What was exercised, 2026-09-07

```
list                      9 ads · 388 other · newest lastmod 2026-08-03
list --fetch              9 read · 9 kept · 0 unreadable · 0 lax
list --since 2026-08-01   1 of 9   (only 1120, dated 2026-08-03)
list --live without --fetch   exit 2
```
