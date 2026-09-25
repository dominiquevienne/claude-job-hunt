# Board measurement — MyWorld Careers (`www.myworld.com.mm`, Myanmar): a Yangon agency whose **rules file declares its sitemap**, so the enumeration is published rather than guessed — 219 adverts on 2026-09-25. **And its `JobPosting` JSON-LD is wrong on the two fields a machine would trust most.** Adapter `myworldmm.py` (#638)

<!-- verified: 2026-09-25 -->

<!-- hosts: www.myworld.com.mm -->
<!-- script: myworldmm.py -->
<!-- countries: MM -->
<!-- route: http -->
<!-- content: measured · **the rules file is served (`state: read`, `certain: True`), writes NO Crawl-delay (2 s are ours) and NAMES `https://www.myworld.com.mm/sitemap.xml`, which answers 200, 166 099 B — 836 `<loc>`, every one carrying a `lastmod`, of which 219 under `/jobs/`; `/jobs` answers 200, 56 887 B and states no count and no pager, which is why the sitemap is the route; each advert carries a `JobPosting` JSON-LD whose `baseSalary` and `hiringOrganization` contradict the rendered page** · 2026-09-25 -->
<!-- witness: 219 advert URLs named by the site's own sitemap, against the emitted count; the walk's invariant is emitted + unreachable == named · 2026-09-25 -->

**Measured 2026-09-25 18:1x UTC by the declared client, the guard on the exact
path, `bin/fetch-body.py`; the adapter then exercised against the host with
`--max 3`: 3 emitted, 219 named.** *The full walk is 219 requests at 2 s and was
not run — the count that matters is the site's own, and it is printed beside
whatever the run emits.*

## The structured field is the wrong half of its own page

Every advert carries a `JobPosting` JSON-LD. It parses, it is the site's own
declaration, and on two fields it says something the page contradicts.

```
JSON-LD   baseSalary  {"currency": "£", "value": {"unitText": "YEAR", "minValue": 4}}
the page  Salary      Up to 4,000,000 MMK + Other Allowances
```

**«&nbsp;£4 per year&nbsp;» for a job paying four million kyats.** The structured field has
kept the leading digit of «&nbsp;4,000,000&nbsp;» and a pound sign from a template.

> **A structured field is not the truer one because it is structured.** *An
> adapter that prefers JSON-LD on principle would publish £4/YEAR, and nothing
> would contradict it: it is well-formed, parseable, and plausible to anything
> that does not also read the page.*

**The salary is therefore read from the labelled field the page prints, and the
JSON-LD's `baseSalary` is not carried at all.** *And it is a labelled field, so
the telephone rule does not touch it — «&nbsp;4,000,000&nbsp;» is seven digits, the shape
that destroyed 113 salaries on `myjobs.com.mm`.*

```
JSON-LD   hiringOrganization  {"name": "MyWorld Myanmar", "sameAs": "https://www.myworld.com.mm"}
```

**That is the AGENCY, not the employer.** Taking it would attribute all 219
adverts to one company. The employer is anonymised on purpose — «&nbsp;at a Leading
International Chemicals Factory&nbsp;» — so `employer` is **null by measurement**,
`employer_anonymised` says why, and the agency travels under its own name. *A
null that does not declare its reason reads like a parse failure.*

## The class names are build artefacts

The page's fields are `styles_metaLabel__qSmzr` / `styles_metaValue__8o2_t`
pairs — **CSS-module hashes, which change on any rebuild.** The patterns match
the stable prefix and ignore the hash. *Anchoring on `__qSmzr` would break
silently at the next deploy, and a board that suddenly yields no field reads
exactly like a board that stopped publishing.*

## A dead check is worse than an inert one

The walk first compared emitted against named under `not manques` — **and that
branch could never fire**, since a row is appended for every 200, so a shortfall
implies `manques > 0`, which the same condition excluded. *An inert guard can at
least redden one day; that one was empty.* It is replaced by an invariant —
**emitted + unreachable == named** — which a silently dropped row breaks, and a
mutation adding a mute `continue` reddens on it.
