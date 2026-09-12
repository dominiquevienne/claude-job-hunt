# Board measurement — Emploi.ci (`www.emploi.ci`, Côte d'Ivoire, AfricaWork): refused to our client, served to a browser, 392 stated and 392 walked from page zero

<!-- verified: 2026-09-12 -->

<!-- hosts: www.emploi.ci, emploi.ci -->
<!-- script: none -->
<!-- countries: CI -->
<!-- content: measured · **392 distinct advertisement addresses** over `/recherche-jobs-cote-ivoire?page=0…` (15 × 25 + 17; the next page empty), read from a connected browser tab, **and the page states «392 Offres d'emploi trouvées» — equal**; the pager is zero-based, as on `ghanajob.md` and `namijob.md` · 2026-09-12 -->
<!-- witness: the page's own «392 Offres d'emploi trouvées», read on every page of the walk and printed beside the distinct count («392 emitted, site states 392 — equal») · 2026-09-12 -->

**Côte d'Ivoire's AfricaWork board — the family's managed template, the family's
25-byte refusal to the declared client, and its own dated reading.**
Measured 2026-09-12 12:35–12:40 UTC: two reads with the declared client,
then one Claude-in-Chrome tab, the guard on the exact path first. *One of
four hosts read in the same six minutes — Sierra Leone, Rwanda, Gabon,
Côte d'Ivoire — each walked and counted on its own; the template is
shared, the numbers are not.*

## Rules, transport, the door

```
robots.txt        200, 1 836 B — the managed template: `*` open, `ClaudeBot` refused, `Claude-User` not named → allowed True, certain True; identity claude-user
declared client   GET https://www.emploi.ci/   403, 25 B, md5 9ccabba20b9f4ec7d18bd6644579e5bf, server cloudflare — twice, 2 s apart, identical
browser tab       / → 200 «Offres d´Emploi et Recrutement en Côte d´Ivoire | Emploi.ci» · no challenge, no interstitial
```

## The listing — the site's count met exactly, from page zero

```
/recherche-jobs-cote-ivoire              «392 Offres d'emploi trouvées» · 25 cards a page · pager zero-based (the link labelled «2» is ?page=1)
fetch ?page=0 …  15 × 25 + 17 → **392 distinct /offre-emploi-cote-ivoire/<slug>-<id>** · the next page → 0 cards
                 **392 emitted, site states 392 — equal.**
advertisement id the trailing number of the address (…-abidjan-2055761)
```

## The advertisement

```
GET /offre-emploi-cote-ivoire/local-agent-office-manager-abidjan-2055761    200 — two ld+json blocks; the first a JobPosting (datePosted 2026-09-12T01:00:01+00:00, validThrough 2026-10-22)
JSON.parse rejects both blocks («Bad control character in string literal») — read tolerantly, as `ghanajob.md` says; never «no JobPosting»
```

## The procedure a session follows — this is the adapter (decision of 2026-09-08)

The six steps of `ghanajob.md` with this host's two paths — `/recherche-jobs-cote-ivoire` for
the listing, `/offre-emploi-cote-ivoire/<slug>-<id>` for the advertisement: guard → tab →
`?page=0, 1, 2 …` until empty, 1.5 s apart → **«n emitted, site states
N»** → the JobPosting read tolerantly → close.

## What this card does not establish

- **The JobPosting's full field set** — head fields only.
- **Whether the count moves within the day** — one read.
- **No script ships.** The route is a browser tab and fetches from it.
