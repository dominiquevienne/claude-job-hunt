# Board measurement — Jobfluent (`jobfluent.com`, Spain): startup and tech jobs in Barcelona, Madrid, Valencia and remote — **the application itself answers 403 to our declared client on every path, and a tab is served the whole site**, so this is the 2026-09-07 case measured rather than inferred; four hub listings each STATE their own count (356, 215, 23, 155) and page by `?page=N` at 25 adverts a page; no contact appears on the advert read, and no `JobPosting` anywhere

<!-- verified: 2026-10-05 -->

<!-- hosts: jobfluent.com -->
<!-- script: none -->
<!-- countries: ES -->
<!-- route: browser · 749 · 2026-10-05 -->
<!-- host-forms-basis: no-rules — `/robots.txt` answers **403** to the declared client, which under the owner's #283 decision is an ABSENCE of rules and therefore an open door with `certain: False`; `jobfluent.com` and `www.jobfluent.com` behave identically, and `www` resolves to a different edge address on each of the two public resolvers (99.83.185.157 against 3.33.249.164), which is a CDN with several edges and not a disagreement · 2026-10-05 -->
<!-- content: measured · **four hub listings state 356, 215, 23 and 155 adverts of their own accord — 749 in sum — and a tab reads every one of them while the declared client is refused on EVERY path, so the browser route is measured and not inferred: `/robots.txt`, `/`, `www./` and `/en/jobs` all answer HTTP 403 with the same 10-byte `text/plain` body «Forbidden» (md5 086d9069069e, identical across two readings of the same URL taken before any comparison), and the response carries `server: Heroku`, `via: 1.1 heroku-router` and — the header that decides the reading — `X-Runtime: 0.002337`, which Rack emits from the APPLICATION; so the request reached the application and the application refused it in 2,3 ms, which is a middleware rejection and not a rendered page. BORNE 0 IS SETTLED BY MEASUREMENT: the 403 is NOT served to everyone, because a connected tab was served the full site («All Startup Jobs in tech hubs in Europe»); nothing was forged to establish this, and `Vary` names only `Accept-Encoding`, so no response claims to vary by agent. WHAT THE TAB READS: four hub listings — `/jobs-barcelona`, `/jobs-madrid`, `/jobs-valencia`, `/jobs-remote` — each STATING its own count and company count («356 jobs from 115 companies»; Madrid 215 of 86; Valencia 23 of 9; Remote 155 of 61), paging by `?page=N` at 25 adverts a page, verified by a different first advert on page 2 under an unchanged stated total, and Valencia agreeing exactly at 23 on a single page because it is smaller than one. The adverts are `/jobs/<slug>-<city>-<hash6>`, indexed `?result=0` upward. 749 IS A SUM AND A BOUND, NEVER A BOARD TOTAL: Remote may overlap the three cities, so the union is at most 749 and at least 356, and a union is taken over IDENTIFIERS. ONE ADVERT READ (`/jobs/data-engineer-barcelona-307395`, 73 246 B, 12 618 characters of text): no `JobPosting` and no JSON-LD block at all; ZERO e-mail and ZERO telephone, which is the opposite of `empregoxunta.md`; and NO salary figure on it, while the listing offers a «Sort by Salary» control — so the field exists somewhere and this advert has none, both stated and neither extrapolated from one. METHOD: guard taken on each host form and each exact path in turns distinct from the retrievals; `bin/fetch-body.py --allow-refusal` for the refusals so their status travels in the record; the tab used for reading, 2 s between its requests, no `Crawl-delay` being written anywhere** · 2026-10-05 -->

<!-- witness: the board states its own counts per hub and they are the witness — «356 jobs from 115 companies» (Barcelona), 215 of 86 (Madrid), 23 of 9 (Valencia), 155 of 61 (Remote), read 2026-10-05; there is NO global total anywhere, and 749 is their arithmetic sum, an upper bound on a union that was not measured · 2026-10-05 -->

## Measured 2026-10-05 — 403 from the application, 749 stated across four hubs, and a tab served every one

```
robots.txt                403   10 o  « Forbidden »  md5 086d9069069e
/ · www./ · /en/jobs      403   10 o  LE MEME md5 — tous les chemins
  server                        Heroku      ·  via  1.1 heroku-router
  X-Runtime                     0.002337    <- Rack : l'APPLICATION a repondu
  Vary                          Accept-Encoding   (PAS User-Agent)
  defi / captcha                AUCUN — borne 2 non engagee
onglet connecte           200   « All Startup Jobs in tech hubs in Europe »
  /jobs-barcelona               « 356 jobs from 115 companies »   25/page
  /jobs-madrid                  « 215 jobs from  86 companies »   25/page
  /jobs-valencia                «  23 jobs from   9 companies »   23 sur UNE page
  /jobs-remote                  « 155 jobs from  61 companies »   25/page
  ?page=2                       200, 25 annonces, PREMIERE differente, total inchange
  forme d'annonce               /jobs/<slug>-<ville>-<hash6>?result=<N>
une annonce lue           200  73 246 o, 12 618 car. de texte
  JobPosting / JSON-LD          AUCUN (0 bloc)
  courriels · telephones        0 · 0
  salaire                       aucun sur CELLE-LA (la liste offre « Sort by Salary »)
```

**Found by the Spain pass of #949.** *The country page carried this host as «&nbsp;à construire&nbsp;».*

### The refusal comes from the application, and that is a different fact from a WAF

**Every path answers the same 10-byte `Forbidden`** — `/robots.txt`, the root, the `www.` form and a listing path, md5 identical, and the body fetched **twice before any comparison** as §2 quater requires.

*The headers decide the reading, and they are not a CDN's:* **no `cf-ray`, no CloudFront, no `awselb` — but `X-Runtime: 0.002337`, which Rack emits from the application itself.** **So the request reached the application, and the application refused it in 2,3 ms** — the shape of a middleware rejection, not of a page anyone wrote.

> *This is where the empleate-ve precedent differs and the difference is worth keeping:* **there the 403 came from `awselb/2.0`, a load balancer; here it comes from the app.** *Same status, same generic body, different layer — and only the headers separate them.*

### Borne 0 is settled by MEASUREMENT, and nothing was forged to settle it

**Borne 0 asks whether the 403 targets the client or everyone.** *A 10-byte `text/plain` body is the most generic refusal there is, so by borne 0's own fingerprint test it is a middleware default rather than an editorial page* — **but that is an inference, and the measurement was available.**

**A connected tab was served the whole site.** *So the 403 is not rendered to all, and the 2026-09-07 decision applies: the rules open the path (a 403 on `robots.txt` is an absence of rules under #283) and the infrastructure refuses that same path, so we drive the browser.*

**What was NOT done, deliberately: no browser User-Agent was ever sent by our HTTP client.** *Forging an identity to test whether the refusal is identity-based is the documented `fetch.sh` defect, and the memory records eleven hours spent measuring our own configuration.* **`Vary` names only `Accept-Encoding`, so no response claims to vary by agent — and that is the end of what the host tells us.** *The cause of the refusal is not published here: a correlation visible from the network is not a cause, and only whoever reads their code can say.*

**And borne 2 is not engaged:** *no challenge, no captcha, no interstitial, no moving fingerprint — the md5 is stable across readings.* **Unlike Ko-fi (#936) and the `revolico` family, there is nothing here to defeat and nothing to ask a candidate to defeat.**

### The hubs state their own counts, which is the witness

| hub | the board's own words | adverts a page |
| :-- | :-- | :-- |
| Barcelona | «&nbsp;356 jobs from 115 companies&nbsp;» | 25 |
| Madrid | «&nbsp;215 jobs from 86 companies&nbsp;» | 25 |
| Valencia | «&nbsp;23 jobs from 9 companies&nbsp;» | **23 on one page** |
| Remote | «&nbsp;155 jobs from 61 companies&nbsp;» | 25 |

**Valencia is the useful check:** *it is the only hub smaller than a page, and its page yields exactly the 23 it states* — **so the page size is not truncating a count, which is the thing a per-page walk gets wrong silently.**

**Pagination is `?page=N`, verified by variation and not by hope:** *page 2 returns 25 adverts with a **different first advert** under an **unchanged** stated total.* **So Barcelona is fifteen pages, and a walker that read one page would emit 25 against a stated 356 — 331 short, and the board's own figure is exactly what makes that detectable.**

> **749 is an arithmetic SUM and an UPPER BOUND, never a board total.** *Remote plainly may overlap the three cities, and deducing a union from cardinals is the mistake this campaign has already paid for* (`meme-cardinal-membres-differents`). **The union lies between 356 and 749, and establishing it means intersecting IDENTIFIERS across the four hubs** — one walk, named here as the adapter's first measurement.

### What one advert gives, and what one advert cannot establish

**No `JobPosting`, and no JSON-LD block at all** — *so every field has to come from the markup.* **Zero e-mail and zero telephone on it**, which is worth recording beside `empregoxunta.md`, where 297 of 297 carried a contact: *two Spanish boards measured the same day, opposite exposure.*

**And no salary figure on the advert read, while the listing offers a «&nbsp;Sort by Salary&nbsp;» control.** *Both are facts. Neither is stretched:* **a sort control is evidence the field exists for some adverts; one advert without one is a denominator of 1, and a single observation is dated, never a property of the board.** *Establishing the salary rate needs a sample, and that is the adapter's work.*

*A small reminder landed here too:* **a bare-number rule matched the advert's own hash `307395` and the years `2024` and `2026`** — the same shape that, on `empregoxunta.md`, would have withheld a public helpline 297 times.

### What an adapter would do

```
route   : BROWSER — the declared client gets 403 from the application on every
          path, and a tab is served. 2 s between requests (no Crawl-delay
          anywhere, the rules file itself being refused).
walk    : four hubs /jobs-{barcelona,madrid,valencia,remote}, ?page=N, 25 a page,
          each hub's own stated count as the bound AND as the shortfall witness
          — «N emitted, the hub states M» printed per hub, never one global sum
FIRST   : intersect the four hubs' advert IDENTIFIERS. Remote may overlap the
          cities; until that is measured the board's size is NOT established and
          749 is an upper bound to be published as such
carries : title, employer, city, the relative age the card shows, the skill tags
          the listing already categorises (the board's own stated value)
unknown : the salary rate. One advert read had none; the listing sorts by salary.
          To be measured on a sample, not assumed from the sort control
NEVER   : no JobPosting exists, so nothing is to be taken on trust from one; and
          a bare-number rule must not run — it matched the advert's own hash here
```

### What this card does NOT say

**It does not say the board is closed, nor that 749 adverts exist.** *The host refuses our HTTP client and serves a browser; that is a route, not a verdict* — **and the 08.09 decision counts a browser route equally with a script, because the candidate gets the same data either way.**

**Measured 2026-10-05 by the declared client for the refusals and by a connected tab for the reading, the guard taken on each host form and each exact path in a turn distinct from the retrieval, `bin/fetch-body.py --allow-refusal` so each refusal's status travels in its record, bodies fetched twice before any fingerprint comparison, DNS on two public resolvers.** *A measurement, not an adapter.*

```
_robots.verdict('jobfluent.com')       state: no-rules, certain: False  (robots.txt -> 403, #283)
GET /robots.txt · / · www./ · /en/jobs  403 x4, 10 B each, md5 086d9069069e identical
  server Heroku · via heroku-router · X-Runtime 0.002337 · Vary Accept-Encoding
onglet  https://jobfluent.com/          200, « All Startup Jobs in tech hubs in Europe »
onglet  /jobs-barcelona                 200, « 356 jobs from 115 companies », 25 adverts
onglet  /jobs-barcelona?page=2          200, 25 adverts, first advert DIFFERENT, total unchanged
onglet  /jobs-{madrid,valencia,remote}  200, 215 / 23 / 155 stated
onglet  /jobs/data-engineer-barcelona-307395   200, 0 JSON-LD, 0 contact, no salary
```
