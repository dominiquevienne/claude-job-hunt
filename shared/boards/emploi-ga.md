# Board measurement — Emploi.ga (`www.emploi.ga`, Gabon, AfricaWork): refused to our client, served to a browser, 67 stated and 67 walked from page zero

<!-- verified: 2026-09-12 -->

<!-- hosts: www.emploi.ga, emploi.ga -->
<!-- script: none -->
<!-- countries: GA -->
<!-- content: measured · **67 distinct advertisement addresses** over `/recherche-jobs-gabon?page=0…` (25 + 25 + 17; the next page empty), read from a connected browser tab, **and the page states «67 Offres d'emploi trouvées» — equal**; the pager is zero-based, as on `ghanajob.md` and `namijob.md` · 2026-09-12 -->
<!-- witness: the page's own «67 Offres d'emploi trouvées», read on every page of the walk and printed beside the distinct count («67 emitted, site states 67 — equal») · 2026-09-12 -->
<!-- route: browser · 67 · 2026-09-12 -->

**Gabon's AfricaWork board — the family's managed template, the family's
25-byte refusal to the declared client, and its own dated reading.**
Measured 2026-09-12 12:35–12:40 UTC: two reads with the declared client,
then one Claude-in-Chrome tab, the guard on the exact path first. *One of
four hosts read in the same six minutes — Sierra Leone, Rwanda, Gabon,
Côte d'Ivoire — each walked and counted on its own; the template is
shared, the numbers are not.*

## Rules, transport, the door

```
robots.txt        200, 1 836 B — the managed template: `*` open, `ClaudeBot` refused, `Claude-User` not named → allowed True, certain True; identity claude-user
declared client   GET https://www.emploi.ga/   403, 25 B, md5 9ccabba20b9f4ec7d18bd6644579e5bf, server cloudflare — twice, 2 s apart, identical
browser tab       / → 200 «Offres d´Emploi et Recrutement au Gabon | Emploi.ga» · no challenge, no interstitial
```

## The listing — the site's count met exactly, from page zero

```
/recherche-jobs-gabon              «67 Offres d'emploi trouvées» · 25 cards a page · pager zero-based (the link labelled «2» is ?page=1)
fetch ?page=0 …  25 + 25 + 17 → **67 distinct /offre-emploi-gabon/<slug>-<id>** · the next page → 0 cards
                 **67 emitted, site states 67 — equal.**
advertisement id the trailing number of the address (…-libreville-438467)
```

## The advertisement

```
GET /offre-emploi-gabon/expert-cyber-securite-libreville-438467    200 — two ld+json blocks; the first a JobPosting (datePosted 2026-09-11T15:45:13+01:00)
JSON.parse rejects both blocks («Bad control character in string literal») — read tolerantly, as `ghanajob.md` says; never «no JobPosting»
```

## The procedure a session follows — this is the adapter (decision of 2026-09-08)

The six steps of `ghanajob.md` with this host's two paths — `/recherche-jobs-gabon` for
the listing, `/offre-emploi-gabon/<slug>-<id>` for the advertisement: guard → tab →
`?page=0, 1, 2 …` until empty, 1.5 s apart → **«n emitted, site states
N»** → the JobPosting read tolerantly → close.

## What this card does not establish

- **The JobPosting's full field set** — head fields only.
- **Whether the count moves within the day** — one read.
- **No script ships.** The route is a browser tab and fetches from it.
