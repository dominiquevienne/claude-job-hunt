# Board measurement — Adecco Italy (`www.adecco.com/it-it`): the Italian sitemap EXISTS and the adapter refuses Italy, so this country is one line of a table

<!-- verified: 2026-10-06 -->

<!-- hosts: www.adecco.com -->
<!-- script: none -->
<!-- countries: IT -->
<!-- content: measured · read 2026-10-06 — `sitemap-jobs-italy-it.xml` answers 200 with 1 242 193 B and carries 6 260 `<loc>`, ALL DISTINCT and all under the single path segment `it-it`, so there is no per-language over-count; the first, median and last were opened and all three are real Italian vacancies. `adecco.py` exists and REFUSES this country before any request, so `script: none` is this country's true state and the fix is a table entry and not a rewrite · 2026-10-06 -->
<!-- witness: the board states no total of its own here; 6 260 is OUR count of distinct `<loc>` in the sitemap it publishes, and it is not a board-stated figure · 2026-10-06 -->

## Measured 2026-10-06 — 6 260 distinct adverts, and the adapter cannot address them

Opened under **#949**, tranche 3 — the Italian staffing agencies, the ATS and the
sector board. *The owner opened the campaign by tranches on 2026-10-06, verbatim
« oui, ouvre #949 par tranches, commence par l'Italie ».*

**The guard was taken on EVERY host form separately, in a turn DISTINCT from the
retrieval, because `robots.txt` binds a HOST and not a brand.** Eleven forms were
guarded across this tranche; nine answered `state: read` and two `unrecognised`,
all open, **and not one carries a `Crawl-delay`** — so the pace is ours, and an
absent delay is not an absence of rate limiting. *Retrieval through
`bin/fetch-body.py` under the declared identity, provenance written beside each
body.* No contact value is reproduced anywhere below; counts only.

**THIS CARD DECLARES `script: none` FOR A HOST THAT THREE OTHER CARDS COVER WITH A
LIVING SCRIPT, AND THAT IS NOT AN OVERSIGHT — it is measured.** `adecco.md` (FR),
`adecco-no.md` (NO) and `adecco-fi.md` (FI) all declare `www.adecco.com` and all
run `adecco.py`. **Calling `adecco.py`'s own `use_board()` refuses Italy before any
request**, in four spellings:

```
use_board('fr' | 'no' | 'fi')                 -> ACCEPTED
use_board('it') / ('IT') / ('it-it')          -> REFUSED, SystemExit 2
use_board('www.adecco.it')                    -> REFUSED, SystemExit 2
  « not a front this adapter reads — fr (France, sitemap-jobs-france-fr.xml), … »
```

*The `--host` help reads «the country's front, or its hostname», which SOUNDS like
it takes any hostname; the implementation enumerates.* **The refusal is honest and
it names what a new front needs, which is exactly what made the next measurement
cheap.**

**WHAT THE REFUSAL ASKED FOR, AND WHAT THE HOST ANSWERED.** The three known fronts
are `sitemap-jobs-<country>-<lang>.xml`. Guessed from that shape and guarded on the
exact path:

```
www.adecco.com/sitemap-jobs-italy-it.xml   200   1 242 193 B   md5 4ab9fb34611c
<loc> 6 260        distinct 6 260          no CDATA
first path segment   it-it : 6 260 of 6 260      <- one segment, so no language twin
```

**The three members opened were the FIRST, the MEDIAN and the LAST, never the first
three** — Adecco Healthcare Italia; fast-food staff at Gallarate, Varese; a waiter
at a fish restaurant in Pescara. *A count of `<loc>` names a SIZE and never a
NATURE, and the path that carries them does not say it either.*

**So Italy is a PARAMETER and not a rewrite** — one `BOARDS` entry naming the file,
the language, the ledger key and the country. *And the contrast inside this very
tranche is the point: `randstad.it` answered the same question with a **404**.
«&nbsp;It is already covered elsewhere&nbsp;» predicts nothing, and the two measured
together say opposite things.*

## What is NOT established

- **No advert page was fetched.** The guard was taken on an advert path and on its
  parents — `allowed=True`, `state: read`, no rule — but nothing was retrieved, so
  the per-advert field shape is UNREAD and so is whether a contact travels in it.
- **6 260 is our count, not a board statement.** No total was read from the site.
- **Whether the FR `JobPosting` shape holds here is unmeasured.** The sibling cards
  record «the agency as `hiringOrganization`, «null» strings, zero salaries» for
  FR/NO/FI; a shared sitemap shape predicts the ROUTE, not the extraction.
