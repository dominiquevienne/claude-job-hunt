# Board measurement — Randstad Germany (`www.randstad.de`): the index the delivered adapter reads EXISTS here, and the first of its three advert files carries 5 000 vacancies

<!-- verified: 2026-10-07 -->

<!-- hosts: www.randstad.de, randstad.de -->
<!-- script: none -->
<!-- countries: DE -->
<!-- content: measured · read 2026-10-06 — `/sitemaps/sitemap.xml` answers 200 with 2 513 B and names 15 files of which THREE match `sitemap-jobdetails*`, the exact predicate `randstadfr.py` applies to an index; no language twin is present, so the FRENCH predicate is the right one and not the Czech or Hungarian variant. The first advert file answers 200 with 768 297 B and 5 000 `<loc>` ALL DISTINCT, all under `/jobs`, and the first, median and last opened are real German vacancies. `randstadfr.py` REFUSES this country before any request, so `script: none` is this country's true state and the fix is one table entry · 2026-10-07 -->
<!-- witness: the board states no total of its own here; 5 000 is OUR count in ONE of its three advert files, and the other two are UNREAD, so no board size is claimed · 2026-10-07 -->

## Measured 2026-10-06 — 5 000 distinct adverts in the first of three files

Opened under **#949**, first German tranche. *The campaign runs by tranches on the
owner's word of 2026-10-06, verbatim « oui, ouvre #949 par tranches, commence par
l'Italie » — Italy is finished and the country was chosen by MEASURING the gap
«hosts named on the page minus hosts carded», not by judgement.*

**Every host form was guarded SEPARATELY in a turn distinct from the retrieval,
because `robots.txt` binds a HOST and not a brand** — 28 forms across this tranche,
**26 open and 2 refused in writing**. *Retrieval through `bin/fetch-body.py` under
the declared identity, provenance written beside each body.* No contact value is
reproduced below; counts only.

**AND THIS CARD EXISTS BECAUSE THE SAME QUESTION ANSWERED THE OPPOSITE WAY IN
ITALY — the two measured together is what makes either sentence safe.**

```
                          ITALIE (2026-10-06)        ALLEMAGNE (2026-10-06)
Adecco, sitemap pays      200, 6 260 annonces        404
Randstad /sitemaps/…      404                        200, 15 fichiers
```

*Same two brands, same two questions, opposite answers in two countries.* **So
neither brand's «it transposes» generalises, and measuring ONE country would have
produced a confident false rule in EITHER direction.** *It is the Hays FR→ES
against Randstad CH→ES finding, met again on a different pair.*

**WHAT THE ADAPTER REFUSES, CALLED AND NOT READ:**

```
use_board('fr') -> ACCEPTED   country=FR  host=www.randstad.fr
use_board('de') / ('DE') / ('www.randstad.de')  -> REFUSED, SystemExit 2
  « not a front of this platform — fr (www.randstad.fr), cz, hu »
```

**AND ONE STEP OF THIS MEASUREMENT WAS A FALSE REFUTATION OF ITSELF, WHICH IS WHY
THE LEVEL IS NAMED.** *The advert URLs are `/jobs/<slug>_<city>_c<id>/` and contain
**no** «jobdetails» string. Read against the predicate `own: lambda u: "jobdetails"
in u`, that looks like the French predicate matching ZERO here.* **It does not:
line 204 applies `own` to `all_maps`, the SITEMAP FILE urls of the index — never to
advert urls.** *So the predicate matches the three files, as intended.* **What
settled it was asking where `u` COMES FROM, not re-reading the lambda** — a real
measurement confronted with the wrong model of the code reads exactly like a
refutation.

## What is NOT established

- **No advert page was fetched**, so the per-advert field shape is UNREAD — and
  with it whether the FR `JobPosting` shape (`identifier.value` the reference,
  `baseSalary` written `0` when unset) holds here. *A shared index shape predicts
  the ROUTE, never the extraction.*
- **The board's size.** 5 000 is one file of three; the other two are unread, and
  no total was read from the site. *A `<loc>` count names a SIZE, never a NATURE —
  which is why first, median and last were opened rather than the first three.*
- **Whether a `-internal` file exists** (the sibling cards flag Randstad's own
  vacancies) — not looked for.
