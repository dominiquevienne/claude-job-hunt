# Board measurement — Feina Activa (`feinaactiva.gencat.cat`, Spain/Catalonia): the SOC's candidate portal — **138 API endpoints read across the bundle and 21 of 22 lazy chunks, and NOT ONE lists offers publicly**: every offers endpoint is `admin/`, `private/` (the employer's own) or `candidate/applications/` (the candidate's own); the declared sitemap answers 404; the root is an Angular shell with 2 377 characters of visible text and no offer in it. **No HTTP route to the offers is established. Nothing is declared closed.**

<!-- verified: 2026-10-05 -->

<!-- hosts: feinaactiva.gencat.cat -->
<!-- script: none -->
<!-- countries: ES -->
<!-- host-forms-basis: read — the APEX serves rules (`state: read`, `certain: True`); `www.feinaactiva.gencat.cat` serves NONE (`state: no-rules`, `certain: False`), so the two forms do not carry the same verdict and the apex is the one to address · 2026-10-05 -->
<!-- content: measured · **the offers are NOT reachable by the HTTP route, and the absence is established rather than assumed: 138 distinct `/api/` paths were read across `main.1fee695726017481.js` (1 595 713 B) and 21 of the 22 lazy chunks named by `runtime.3126fb1ac6f751c4.js`, and EVERY offers endpoint is administrative or account-bound — `offers/admin/list`, `offers/private`, `offers/private/${n}/applications`, `offers/candidate/applications`, `offers/block/`, `offers/claims`, `offers/questionnaire`; `candidates/searches` is the candidate's SAVED searches and `cvs/search` searches CVs on the employer side. NO public offers list or search exists among the 138. WHAT ELSE THE ROUTE DOES NOT GIVE: the sitemap the `robots.txt` DECLARES — `https://feinaactiva.gencat.cat/sitemap.xml` — answers HTTP 404; and the root (1 458 071 B) is an Angular shell with NO server-rendered content: 773 052 B of inline script for **2 377 characters** of visible text, all of it form-validation strings, with `oferta` 0, `ofertes` 0, `Barcelona` 0, `jornada` 0, `contracte` 0. THE GAP IS NAMED: chunk `592.2f970611b9da29d6.js`, listed in the chunk map, answers HTTP 404 with a 168 344 B body (the shell under a 404 code — a readable body is not an answer), so the reading covers 21 of 22. METHOD: apex `robots.txt` 84 B, `state: read`, `certain: True`, group `*`, **`Disallow` EMPTY**, no AI agent named, no `Crawl-delay` — so 2 s are ours — and it declares the sitemap that 404s; guard open and certain on `/`, `/ca/home`, `/sitemap.xml`, `/ofertes`** · 2026-10-05 -->

<!-- witness: none — no page or endpoint states a count, and no public listing was found to count from · 2026-10-05 -->

## Measured 2026-10-05 — 138 endpoints read, and the public search is in none of them

```
robots.txt (APEX)        84 o   groupe *, Disallow VIDE, aucun agent d'IA nomme
                                declare sitemap.xml  ->  qui repond 404
robots.txt (www.)         —     AUCUNE regle : state no-rules, certain FALSE
racine            1 458 071 o   Angular, 773 052 o de script inline
                                2 377 caracteres visibles, 0 « oferta », 0 « ofertes »
main.js           1 595 713 o   37 chemins /api
+ 21 chunks sur 22              138 chemins /api au total
offers endpoints                admin/ · private/ · candidate/applications/ · block/
                                claims/ · questionnaire · experience/period
PUBLIC offers list/search       AUCUN sur les 138
```

**Found by the Spain pass of #949.** The country page carried this host as «&nbsp;à construire&nbsp;»
with «&nbsp;Service public de l'emploi de Catalogne (SOC)… le deuxième bassin d'emploi du pays —
Site public, joignable. **Structure non examinée.**&nbsp;» *Joignable is confirmed. The structure is
now examined, and it does not give what the line assumed.*

### The absence is ESTABLISHED, and here is how — because that is what makes it usable

*`shared/robots-policy.md` asks that an absence be established and that the manner be recorded.*
**Read: the main bundle and 21 of the 22 chunks the runtime names, 138 distinct `/api/` paths.**
Every path mentioning an offer is one of:

| family | what it serves |
| :-- | :-- |
| `offers/admin/list`, `offers/admin/${o}` | administration |
| `offers/private`, `offers/private/${n}/applications` | **the employer's own** offers |
| `offers/candidate/applications`, `…/accept`, `…/reject` | **the candidate's own** applications |
| `offers/block/`, `offers/claims`, `offers/questionnaire` | moderation, disputes, forms |

*And the two that read like a search are not one:* **`candidates/searches` is the candidate's SAVED
searches**, and **`cvs/search` searches CVs** on the employer side. **There is no anonymous way in,
in the API the site's own client uses.**

> **A door not found is not a door closed** — so this was pushed as far as it goes: the declared
> sitemap (404), the root for server-rendered content (none), the main bundle, and every lazy chunk
> the runtime names. **The one chunk not read is named below, and it answers 404 too.**

### Two defects of the host itself, worth recording

**The DECLARED sitemap does not exist.** `robots.txt` names
`https://feinaactiva.gencat.cat/sitemap.xml`; the host answers **404**. *A declared door that is not
served — the mirror of «&nbsp;a door not found is not a door closed&nbsp;».*

**And a chunk the runtime names is not served either**: `592.2f970611b9da29d6.js` answers **404 with
a 168 344 B body** — the shell under a 404 code. *`bin/fetch-body.py` refused to save it, which is
the right refusal: a readable body is not an answer, the code decides.* **So the reading is 21 of
22, stated as such and not rounded to «all».**

### Two host forms, two verdicts

**The apex serves rules (`state: read`, `certain: True`); `www.` serves none (`state: no-rules`,
`certain: False`).** *The two forms do not carry the same verdict, so the host to address is the
apex* — and a guard taken on `www.` would be `certain: False` where the apex is certain.

### What remains possible, and it is not for this card to decide

**The offers are visible to a human on this site; they are simply not in the API without an
account.** *So the remaining route is a browser one driven from the candidate's OWN session —
exactly the LinkedIn pattern already delivered here, which the France and Spain pages both note as
«&nbsp;le seul board du lot qui exige d'être connecté&nbsp;».*

**Nothing is declared closed, and that is deliberate:** §2 sexies reserves writing a host off to the
owner, and this is not even a refusal — *it is an account wall on a public employment service, which
is a different thing from a `Disallow` and from a 403.* **We never create an account; a candidate's
own session is the owner's and the candidate's call, not ours.**

**Measured 2026-10-05 by the declared client, the guard on the exact path AND the exact host form
first, `bin/fetch-body.py`, provenance beside every body.** *The content-hashed bundles were fetched
in the same pass as the root and the runtime that name them.* *A measurement, not an adapter.*

```
_robots.verdict('feinaactiva.gencat.cat')      state: read,     certain: True,  delay: None
_robots.verdict('www.feinaactiva.gencat.cat')  state: no-rules, certain: False
GET /                                  200, 1 458 071 B, 2 377 chars visible
GET /sitemap.xml                       404   (declared by robots.txt)
GET /main.*.js · /runtime.*.js         200
GET 22 lazy chunks                     21 x 200, 1 x 404 (592.2f970611b9da29d6.js)
```
