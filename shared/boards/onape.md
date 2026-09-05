# Board adapter — ONAPE (Chad)

<!-- verified: 2026-09-04 -->

<!-- hosts: onape.td -->
<!-- script: onape.py -->
<!-- countries: TD -->
<!-- content: measured · every advertisement read, 30 of 30 yielded a JobPosting · 2026-09-04 -->
<!-- witness: none found — /offres-demploi/ answers 404 and no counter was located -->
<!-- hosts-source: named by the search result for Chad's public employment service · 2026-09-04 -->

**Chad's Office National pour la Promotion de l'Emploi.** A public employment
service on WordPress, and it names its own files: `/wp-sitemap.xml` separates
`job_listing` from `company`, `testimonial`, `tribe_venue` and the taxonomies.
**The advertisements are reachable without guessing a URL and without counting
anything that is not one** — which is not the ordinary case. Of nineteen Asian
and nine African boards measured on 2026-09-04, this is one of two whose index
does that.

```
onape.py list [--search mécanicien] [--limit 5] [--text]
onape.py ad   --slug chef-de-base-5 [--text]
```

## Thirty, and the file says thirty-two

```
wp-sitemap-posts-job_listing-1.xml    32 <loc>   30 distinct
                                      one advertisement listed three times
```

**A count taken off the file length is wrong by two, and wrong in the direction
that flatters.** `list` deduplicates and reports both numbers, because the gap
is a property of the site: hiding it makes the next reader recompute it, and
publishing 32 would make Chad look larger than it is by seven per cent.

*The first figure this repository published for Chad was 32, on 2026-09-04,
before the duplicates were counted. It was corrected the same evening.*

**Measured 2026-09-04**: 30 advertisements, posted `2026-07-18` → `2026-09-04`,
**30 of 30 read**, zero unreadable. Regions: N'Djamena 12, Lac Tchad 8, Ouaddaï
7, then Ouadi Fira, Ennedi Est and Sila with one each.

## What an advertisement carries, and the field it never carries

Each page holds exactly one well-formed `ld+json` `JobPosting`.

**`hiringOrganization.name` is empty on 30 of 30.** Not missing — present, as a
key, with an empty string, every time. **So the adapter emits `employer: null`
and `employer_absent: true`, and never fills it with "ONAPE"**: the office
publishes these advertisements, it does not employ for them. A placeholder here
would put an employer name into a ledger row that no employer ever wrote.

**`jobLocation.address` is a plain string, not a `PostalAddress`** — `"Ouaddai,
Abéché"`, sometimes `"Ouaddai, Abéché, Farch"`. Region first, then city, then
occasionally a village. `addressLocality` does not exist here.

**`validThrough` is usually real and sometimes not.** Most fall a few days after
`datePosted`; one reads `2032-11-23`, six years out. It is reported as it stands
and **never used to decide whether an advertisement is live** — a six-year
expiry is a default somebody left in a form, not a fact about the job.

**`description` is HTML-escaped twice.** One `unescape` yields markup, the
second yields text.

## Access

`robots.txt` reads, the host sweeps, and the paths this adapter uses are
permitted — asked per path, not per host. **That distinction is not a
formality**: `vieclam24h.py` shipped for weeks fetching the one path its own
host refused, because a host-level verdict answered *sweep* and nothing ever
asked about the path (#156).

## What this adapter does not do

No search endpoint is used: `--search` filters titles locally, on what the
sitemap already gave. **There is no query-string route here and none is
guessed** — the whole board is thirty advertisements, and reading all of them
costs thirty requests.
