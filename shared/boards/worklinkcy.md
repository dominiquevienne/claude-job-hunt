# Board measurement — Work Link (`www.worklinkcy.com`, Northern Cyprus): **a CLAMPED pager of 12 and a FEED of 20 overlapping in four — and their union is exactly the 28 the board states.** A currency on an amount that does not exist, and two sources whose dates disagree by five months. Adapter `worklinkcy.py` (#722)

<!-- verified: 2026-10-01 -->

<!-- hosts: www.worklinkcy.com -->
<!-- script: worklinkcy.py -->
<!-- countries: CYN -->
<!-- route: http -->
<!-- content: measured · **`/tr/jobs` (200, 357 323 B, md5 bd546ef2f6ab / 1faa6d672fd0 — a rendered element moves) lists ads as `/tr/jobs/<slug>` (10 distinct on the first page), a pager `?page=2`, `?page=3`, and a feed `/tr/feed/jobs`; no count stated, no JobPosting; `_robots.allowed('www.worklinkcy.com','/tr/jobs')` → open, certain** · 2026-09-18 -->
<!-- witness: none — the list states no count · 2026-09-18 -->

<!-- content: measured · **the rules file is served (`state: read`, `certain: True`) on `/`, `/tr/jobs` and `/tr/feed/jobs` and writes no Crawl-delay — 2 s are ours. THE PAGER IS CLAMPED: `?page=2`, `?page=3`, `?page=4` each return the SAME 12 slugs and the same «Showing 1 – 12 of 28 results», though the page renders pager links — a pager one can SEE is not a pager that advances. AND THE FEED IS NOT THE INVENTORY: `/tr/feed/jobs` is RSS 2.0 with 20 `<item>`, holding 20 of 28 and missing 8 that page 1 carries. pager 12 · feed 20 · intersection 4 · union 28. The advert (86 376 B) carries THREE `ld+json` blocks — `BreadcrumbList`, `WebSite`, `JobPosting` — so the block is chosen by `@type`; its `baseSalary` reads `{currency: EUR, minValue: null, maxValue: null}` and the rendered page prints NO salary** · 2026-10-01 -->
<!-- witness: the board's own «of 28», and the union of the two enumerators is exactly 28 — so completeness is VERIFIED here, where Lambda (#661) and İş Kıbrıs (#719) stated no total and could only report that their size was not established. Neither enumerator alone reaches it · 2026-10-01 -->

## Adapter delivered 2026-10-01 — and this closes a form met three times in three days

```
worklinkcy.py jobs --country-code CY
  pager 12 · feed 20 · intersection 4 · UNION 28 == «Showing 1 – 12 of 28 results»
```

| | Lambda #661 | İş Kıbrıs #719 | **Work Link #722** |
| :-- | --: | --: | --: |
| enumerator A | sitemap 50 | sitemap 12 | **pager 12** |
| enumerator B | listing 30 | home page 12 | **feed 20** |
| intersection | 2 | 6 | **4** |
| total stated? | no | no | **yes, 28** |
| union verified? | — | — | **yes, exactly** |

**Three boards, three days, and in none of them did either enumerator contain the other.** *It is a
form, not three accidents.* **And this is the sharpest case, because a FEED is the artefact most
likely to be taken for the inventory** — this one misses nearly a third of the board while the
clamped page 1 holds those eight.

**What is new is that the union is VERIFIABLE.** The first two boards stated no total, so the honest
report was «&nbsp;the size is not established&nbsp;». This one states 28 and the union is 28, so the run
ASSERTS it — and says plainly when the two disagree, because then something enumerates adverts that
neither the pager nor the feed carries.

### The pager advertises pages it will not serve

`?page=2`, `?page=3` and `?page=4` each return the same slugs and the same «&nbsp;of 28&nbsp;». The
2026-09-18 reading recorded «&nbsp;pager `?page=2`, `?page=3`&nbsp;» because the links are there.
**A pager one can see is not a pager that advances**, and only asking for page 2 and comparing the
IDENTIFIERS separates them — which is one extra request, and the adapter spends it.

### A currency on an amount that does not exist

`baseSalary` reads `{"currency": "EUR", "minValue": null, "maxValue": null, "unitText": "MONTHLY"}`,
and the rendered page prints no salary at all. **A currency without a value is not a salary but a
template default**, so nothing is carried: emitting `EUR` would declare a figure the board never
published, on every one of its adverts. *Third variant of the `baseSalary.currency` rule
(#638/#655) — there the currency was WRONG; here there is nothing for it to be wrong about* — and
`salary_currency_without_amount` records that one was declared, so a board that one day fills the
amount appears as a change rather than as a bug.

### Two sources, two dates, five months apart

For `/tr/jobs/barber`: the advert's `datePosted` reads **2025-10-03** (`validThrough` 2025-11-17),
the feed's `pubDate` reads **2026-03-10**. **Neither is adjudicated here.** Both travel, each named
by its source — `posted` and `feed_published` — and the run counts the disagreements. *Choosing one
silently would publish a date whose provenance nobody could recover, and the disagreement is itself
the finding.*


**Found by the Northern Cyprus search of #606 (a country never searched),
measured 2026-09-18 07:20–07:22 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #606: two searches in Turkish naming the Labour Department and the
private boards, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('www.worklinkcy.com', '/tr/jobs')   open
GET https://www.worklinkcy.com/tr/jobs   200 ×2 — see the content line
```

The adapter's first line: `/tr/feed/jobs` (a feed is the inventory if it is whole) against the paged list, the ad's fields.
