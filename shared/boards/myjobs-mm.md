# Board measurement — MyJobs (`myjobs.com.mm`, Myanmar): «Myanmar's Pioneer Job Portal» — **177 adverts emitted, against the 177 its thirty category counts sum to, over the 15 pages its own pager bounds, the last carrying exactly the 9 that arithmetic predicted**; `myjobsmm.py` — Myanmar's second living board

<!-- verified: 2026-09-23 -->

<!-- hosts: myjobs.com.mm -->
<!-- script: myjobsmm.py -->
<!-- countries: MM -->
<!-- route: http · 177 · 2026-09-23 -->
<!-- content: measured · **177 emitted over 15 pages of 12, and THREE figures agree that were checked before a line was written: the home page names 30 categories summing to 177; `/jobs` pages twelve and its pager names 15 on page 1, so 15 × 12 = 180 bounds the walk; and 177 implies the last page carries 177 − 14 × 12 = 9 — it carried 9, and page 16 carried none. 30 of 30 per-category counts are the counts the cards give. Root 200 ×2 (812 162 B), `/jobs` 200 ×2 (523 096 B, 12 adverts), `/jobs?page=15` 200 (9 adverts), `/jobs?page=16` 200 (none), `/jobs/category/sales-business-development` 200 (12, pager on `?functionalAreaId=`). Salary «Hidden» on 30, «Negotiable» on 32, a figure written on 115; 2 cards carry no employer and 1 no employment type, counted. Exercised 2026-09-23: `jobs --country-code MM` → **177 emitted, they agree, 30 of 30 categories agree** · 2026-09-23 -->
<!-- witness: the home page's own thirty category counts (177 together) AND the pager's largest page read on page 1, three figures that predict one another and are checked on every unfiltered run · 2026-09-23 -->

**Found by the Myanmar search of #601 (a country never searched), measured
2026-09-17 09:35–09:39 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads of the root, two public resolvers on
a DNS negative.** The method is written on #601: one search for the
country's boards (a recruiting vendor's ranking of ten, cross-read with
the engine's own results) and one for the public employment service (the
Ministry of Labour's Labour Exchange Office system, named by the national
portal). *A measurement, not an adapter.*

```
_robots.allowed('myjobs.com.mm', '/')     open, certain
GET https://myjobs.com.mm/                 200 twice — see the content line
```

Nothing past the root was read: the list route, the pager, the ad page
and what it carries are the first line of the adapter, as its `adapter`
issue says.

## The adapter, 2026-09-23

```
myjobsmm.py jobs [--category SLUG] [--since-days N] [--country-code MM] [--max-pages N]
myjobsmm.py categories
```

**Three figures that predict one another — and the prediction was tested before
a line was written.** The home page names **30 categories summing to 177**;
`/jobs` pages twelve and its pager names **15** on page 1, so 15 × 12 = 180
bounds the walk; and if the board holds 177, the last page must carry exactly
**177 − 14 × 12 = 9**. *It carried 9, and page 16 carried none.*

> **This is what separates it from Yemen HR and HireLebanese.** There the total
> and the per-category counts came off the **same page**, so they could agree by
> construction. Here the categories, the pager and the last page's fill are
> **three separate statements**, and a walk that disagrees with them disagrees
> with something.

**The pager is a sliding window, so the bound is read from page 1 only.** Page
15 itself offers a link to 16, which is empty. A bound re-read on every page
would follow the window instead of bounding the walk.

**The fields are read by what they ARE, never by position.** Some cards open
with a badge («Latest»), others with the employer's name — so the third string
is a title on one card and a location on the next. The title is the advert
link's `aria-label`, the employer the `/companies/…` link's text, and of what
remains the **category is the one the site names**, matched against its own
thirty labels.

**A salary the board hides is declared, not dropped**: «Hidden» (30) and
«Negotiable» (32) are two different statements, and neither is «no salary
field»; a figure is carried as written (115).

### The scrub had to be taken off one field, and the guard is why

**`350000 - 450000 MMK` came out as `[telephone withheld] MMK`, and 113 of the
115 written salaries were destroyed the same way on the first full run.** A
Myanmar salary range is twelve digits with a separator — *exactly* the shape the
nine-digit rule exists to catch.

> **The rule was right about the shape and wrong about the field.** On the Syrian
> board the same threshold separated seven-digit salaries from ten-digit numbers
> cleanly; here it cannot, and the difference is **the currency, not the rule**.

So the telephone rule no longer touches a field whose meaning is known — a
salary the board prints under its own label. The e-mail scrub stays there,
costing nothing; free text keeps both. *It surfaced only because the guard's
fixture used a real Myanmar figure: `1000 USD` would have passed and shipped the
corruption.*

**Two categories named almost alike are carried as two.**
`sales-business-development` (32) and `sales-and-business-development` (1) are
distinct slugs with distinct counts, and merging them would invent a decision
the site has not made. *It is the mirror of HireLebanese, where three ids lived
under one truncated label and telling them apart would have invented the
distinction.* **Both times the rule is the same: carry what the site exposes,
never what we infer from it.**

**The fingerprint is mute by a NAMED cause.** Two reads of the root give
different md5 at identical length: **1 342 positions differ, every one inside a
`/cdn-cgi/l/email-protection#<hex>`**, which Cloudflare re-keys per request.
*Mute by a named cause is not mute* — what held twice (the twelve adverts, the
thirty counts, the pager) is what may be carried. **The corollary is a rule:
the page carries addresses, so `/cdn-cgi/` is never requested and the hex is
never decoded.**

**WITHHELD:** e-mail addresses everywhere, telephone numbers in free text at
nine digits, `contacts_withheld` on every record; **0 leaks measured on the
177**. The advert pages are not fetched (`detail_read: false`) and no account is
ever created.
