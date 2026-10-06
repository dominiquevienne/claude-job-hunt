# Board measurement — iş-cikler (`iscikler.com`, Northern Cyprus): a Vite/React shell whose **API is now READ — `GET /api/jobs` answers 200 to the declared client with NO forged header**, states a total of 28 and KEEPS it, and whose pager advances honestly; the signature and fingerprint headers its own client sends are NOT enforced, so nothing was defeated; **`iscikler.py` reads it, asserts the stated total, and signs nothing**

<!-- verified: 2026-10-02 -->

<!-- hosts: iscikler.com -->
<!-- script: iscikler.py -->
<!-- countries: CYN -->
<!-- content: measured · **THE API IS READ, and it is the route: the shell (200, 8 557 B) names three content-hashed bundles; `/assets/index-Ci11pkKW.js` (1 088 752 B) names the base `https://iscikler.com/api` and 88 endpoints. `GET /api/jobs?per_page=3&page=1` answers **200 to `Claude-User` with no forged header** (3 510 B, md5 50b042e18a68) and returns `{success, data, meta}`. **THE BOARD STATES A TOTAL AND KEEPS IT: `meta.total` = 28, and one page returns 28 DISTINCT ids** — the first of these Northern Cyprus boards with a witness that holds. The pager ADVANCES: `per_page=20&page=2` returns 8 (20+8=28, `last_page` 2) and `page=99` returns 0 honestly; **`per_page=100` is CLAMPED to 50 by the server, which says so in its own `meta.per_page`**. 24 fields per advert, no contact field in the listing. `salary_min`: a real TL amount on 11 (20 000-120 000), the string `"0.00"` on 10, `null` on 7. `expires_at`: the sentinel `2099-12-31 23:59:59` on 9, and **19 of the 28 carry a deadline already PAST while all 28 are `status: approved`**. `created_at` 2026-01-15 to 2026-08-18; 4 cities, 4 employment types; 6 descriptions carry an e-mail and 3 a telephone The rules file is served (`state: read`, `certain: True`, group `*`, NO Crawl-delay — 2 s are ours).** · 2026-10-02 -->
<!-- content: measured · **`iscikler.com` (200 ×2, 8 557 B, md5 a7b861f7f9a0 identical) is a Vite/React shell (`<div id="root">`, one bundle) with no card, count or link; `_robots.allowed('iscikler.com','/')` → open, certain** · 2026-09-18 -->
<!-- witness: `meta.total` = 28 stated by the API, and 28 distinct ids returned — the total HOLDS, verified in the same read · 2026-10-02 -->

<!-- witness: none — the shell carries nothing · 2026-09-18 -->

## Re-measured 2026-10-02 — the API is read, and nothing had to be defeated to read it

```
/                         8 557 o   coquille Vite/React, 3 bundles a empreinte de contenu
/assets/index-*.js    1 088 752 o   base « https://iscikler.com/api », 88 points d'entree
GET /api/jobs?per_page=3&page=1     200 a Claude-User, SANS aucun en-tete forge
  meta  {current_page 1, per_page 3, total 28, last_page 10}
  per_page=100  ->  CLAMPE a 50 par le serveur, qui l'ANNONCE dans son propre meta
  per_page=20&page=2  ->  8 annonces (20+8 = 28)      page=99  ->  0, honnetement
TOTAL ENONCE 28   =   28 IDENTIFIANTS DISTINCTS       le temoin TIENT
```

**The blocker this card carried — «l'API n'est pas encore lue (panneau réseau d'un navigateur)» — is
cleared without a browser**: the bundle names its own base and endpoints, and the endpoint answers
the declared client.

### The control exists in the client and is NOT enforced by the server — and that is the whole question

The bundle's axios interceptor signs **every** request:

```js
headers["X-Request-Timestamp"] = s          // l'horloge
headers["X-Request-Nonce"]     = Xj()       // un nonce
headers["X-Request-Signature"] = qj(A,s,a)  // un hachage du corps
headers["X-Client-Fingerprint"] = btoa(navigator.userAgent + navigator.language)
```

**A per-request signature plus a browser fingerprint is a mechanism to ensure requests come from the
official client — so reproducing `qj()` or forging a fingerprint would be DEFEATING an anti-automation
control, which borne 2 forbids.** *The candidate is not a means, and that holds for our HTTP client
exactly as for the browser route.*

> **So the question was never «can we compute the signature» — it was «is the control ENFORCED».**
> *One honest request answers it: asked as ourselves, unforged, the endpoint returns **200** with the
> adverts.* **The headers are client-side decoration on this endpoint. Nothing was defeated, because
> nothing had to be.**

**And the discriminant is cheap and repeatable**: one request as the declared client. *If it had
returned 401 or 403, the measurement would have stopped there and said so* — **a control that is
enforced is a wall, not a puzzle to solve.**

### Three sentinels, and each would publish something the board never said

| the field | what it holds | why it cannot be carried as-is |
| :-- | :-- | :-- |
| `salary_min` / `salary_max` | **`"0.00"` on 10 of 28** | *a wage of zero is not a wage*: carrying it publishes «this job pays 0 TL» |
| `salary_min` | `null` on 7 | honest absence — nothing to carry, and nothing to flag |
| `expires_at` | **`2099-12-31 23:59:59` on 9 of 28** | a far-future sentinel meaning «no deadline»; carried as a date it is false precision |

**And the fourth variant of the salary family is here: a ZERO where absence is meant.** *#638/#655 had
a currency that was WRONG, #722 a currency on NULL values, #721 a row COMMENTED OUT — and this board
writes `"0.00"`.* **Four hosts, four mechanisms, one rule: a salary is carried only when the board
states an amount, and `0.00` is not an amount.**

**The 11 real salaries are 5- and 6-figure TL (20 000 - 120 000), which is exactly the digit range
where the Myanmar rule destroyed 113 of 115 salaries** (`shared/boards/` 23.09). *Measured here, not
assumed: the anchored telephone rule — `+90`/`0` then `5xx` or `392` — matches **none** of the 11.*
**The anchor is what saves them; a loose nine-digit rule would not.**

### The board does not expire its adverts

**19 of the 28 carry an `expires_at` already past (2026-02-15 to 2026-02-19) and ALL 28 are
`status: approved`.** *So `expires_at` is not a filter the board applies — an adapter that dropped
past adverts would substitute its own judgement for the board's filing, which this repository has
already settled (#724): the board lists it, so we emit it and we say the deadline has passed.*

`created_at` runs 2026-01-15 to 2026-08-18 — **the newest advert is six weeks old, so this board is
live, not dormant** (unlike `ekonomikibris`, 21 months, and `kktcportal`, 12 weeks).

### What the adapter does

```
route   : http — `GET /api/jobs?per_page=50&page=N` until the stated total is reached
          the total is STATED and it HOLDS, so the run can assert union == meta.total
          per_page is clamped to 50 BY THE SERVER, which declares the clamp itself
fields  : 24 per advert; no salary from "0.00", no deadline from the 2099 sentinel
          the past deadlines are carried and NAMED, never dropped
withheld: 6 descriptions carry an e-mail and 3 a telephone — anchored rule, +90/0 then 5xx/392
NEVER   : no signature is computed and no fingerprint is forged. If the server ever begins to
          enforce them, the route STOPS and is recorded — it is not solved.
```

**Re-measured 2026-10-02 by the declared client, the guard on each exact path first,
`bin/fetch-body.py`, provenance beside every body.** *The content-hashed bundle was fetched in the
same pass as the shell that names it — such a chunk 404s once the site redeploys.* *The measurement; the adapter is `skills/job-scan/scripts/iscikler.py`.*

```
_robots.verdict('iscikler.com')   state: read, certain: True, group '*', delay: None
GET / · /assets/index-Ci11pkKW.js · /api/jobs (×3 paginations)   — all 200
```
