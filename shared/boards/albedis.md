# Board measurement — Albedis (Switzerland): the JSON-LD is there, and it does not parse

<!-- verified: 2026-09-08 -->

<!-- hosts: www.albedis.com, albedis.com -->
<!-- script: none -->
<!-- countries: CH -->
<!-- content: measured · 95 advertisements, each published in four languages — 380 `<loc>` in `sitemap_jobs0.xml` of which 95 are `/emploi/` and 95 × 4 = 380 exactly; every advertisement carries a `JobPosting` that a plain `json.loads` cannot read · 2026-09-08 -->
<!-- witness: 95 × 4 = 380, the site's own sitemap partitioned by language; the site declares no running total anywhere this measurement found -->

**#189 asked for a measurement and named two traps. Both are answered here, and
the request's central premise is corrected.**

## The premise that was wrong — and it was wrong in the useful direction

**#189 records `AUCUN bloc JSON-LD JobPosting — l'extraction passe par le
HTML`.** *There is one on every advertisement.* **It simply does not parse**,
and a reader that concludes absence from a parse failure reports the site as
unstructured when it is fully structured.

**Two distinct malformations, and both are the site's:**

```
1  an array wrapped in quotes
   "employmentType" : "["FULL_TIME", "INTERN"]"     -> breaks the string

2  a raw control character inside a string
   "description" : "...\n..."                        -> strict JSON refuses
```

**Measured on four advertisements: all four need repair 1, one of the four also
needs lax parsing.** *A plain `json.loads` reads **0 of 4**.* **That is exactly
the observation that produced the false premise**, and it is why this card
records the repair rather than the conclusion.

*The same three-path reader that `careerical-sl.md` documents applies here —
try strict, then lax, each with and without the repair — and the order of
attempts is itself the finding.*

## Trap 1 — the neighbouring advertisements, and the bound is VERIFIED

**#189 is right that the page carries other advertisements' fields.** *Measured
across four pages:*

```
page                      ad ids in the HTML     JobPosting blocks
IT Solutions Specialist            5                     1
Verkaufsexperte                    6                     1
Supply Chain Coordinator           7                     1
Sales expert                       9                     1
```

**The HTML always names several advertisements; the `JobPosting` is always
exactly one.** *So the JSON-LD block IS the container — it is bounded to the
advertisement by construction, where any HTML selector sees between five and
nine.*

**This was checked on four pages rather than one**, which is what #189 asked
for: *a selector that works on a page with one advertisement can take the
neighbour on the next.* **Here the bound held on every page, including the one
carrying nine.**

## Trap 2 — the two identifiers, and which is the key

```
identifier.value   INT-121357            declared by the site in its JobPosting
URL id             3028979735            addresses the page
```

**Both are stable across the four language forms of the same advertisement** —
`/emploi/…-fr/`, `/stellenangebot/…-de/`, `/jobs/…-en/`,
`/annuncio-di-lavoro/…-it/` all carry id `3028979735` and identifier
`INT-121357`. *Verified by fetching the French and German forms and comparing.*

**The `INT-` prefix survived the merger — it is on all four sampled
advertisements — but its numeric part has TWO shapes:**

```
INT-120553          INT-121498          INT-121357        six digits
INT-4163915104116                                      thirteen digits
```

> **Recommended ledger key: the numeric URL id.** *It is uniform in shape, it is
> what `sitemap_jobs0.xml` enumerates, and it addresses the resource in all four
> languages.* **`INT-…` is the site's own declared identifier and should be
> carried alongside**, because it is the reference a recruiter would quote — but
> a parser that assumes six digits after `INT-` breaks on the sample above.

## The count, and the anchor that does not exist

```
sitemap_jobs0.xml   380 <loc>   95 under /emploi/   95 × 4 = 380
lastmod             2026-06-18 → 2026-09-08T06:23
```

**95 advertisements, and the four-language partition closes the arithmetic
exactly** — *which is what makes 95 a count of advertisements rather than of
URLs.*

**NAMED GAP: this site states no running total that this measurement found.**
*Unlike `rocken.jobs`, which puts `6104 offene Stellen` in its `<title>`, and
`jobs.af` and `kalibrr`, whose APIs return their own `count`.* **So 95 is our
enumeration of the site's sitemap, not the site's own figure**, and if the
reader broke, 95 and 0 would be two outputs of one instrument.

*Two listing paths were guessed and both answered 404 — `/emplois/` and
`/jobs/`. `/jobs/` is a language prefix for English advertisements, not a
listing. The sitemap was read instead of a third guess.*

## The employer is the agency, on every advertisement

**`hiringOrganization.name` is `albedis` on all four sampled advertisements**,
and the description says *"Notre client, acteur majeur du secteur de la
construction"* — the end employer is deliberately unnamed.

**This is the fourth host in one day with that shape**, after `rocken.jobs`
(`ROCKEN` on 6 105), `eshjob.com` (18 cards, one poster account) and one other.
**An adapter must leave the employer empty and say why.**

## What is not established

**No script ships**, and under the owner's decision of 2026-09-08 that is a
measurement owed rather than a renunciation.

**Four advertisements of 95 were parsed.** *The container bound, the repair
requirement and the agency-as-employer are observed on four, not demonstrated on
95.*

**The `DDMMYY`-style suffix seen on other Swiss hosts does not appear here**;
the slug ends in a language tag instead.
