# Board measurement — Emprego Xunta (`emprego.xunta.gal`, Spain/Galicia): the Galician public employment service — **297 live offers arrive in ONE request through the page's own AJAX route, and all 297 carry the employer's contact, so the withholding rule is the first line of any adapter**; the board's own redirect DOWNGRADES HTTPS to HTTP and its application then refuses its own hostname, so a client that follows redirects faithfully gets a 400 on the root; the declared-nothing sitemap exists anyway and names 286 URLs on a host that does not resolve

<!-- verified: 2026-10-05 -->

<!-- hosts: emprego.xunta.gal -->
<!-- script: none -->
<!-- countries: ES -->
<!-- host-forms-basis: read — `emprego.xunta.gal` serves rules (`state: read`, `certain: True`, 2 027 B, md5 96ef753f2731) and they are DRUPAL'S STOCK FILE unmodified; `emprego.xunta.es` is a DIFFERENT address (85.91.64.81 against 85.91.64.105) and serves NONE (`state: no-rules`, `certain: False`); `www.emprego.xunta.gal` does not resolve on either 1.1.1.1 or 8.8.8.8; `xunta.gal` serves its own 433 B of rules with 16 `Disallow` — four forms, four different answers, and the one that matters is the first · 2026-10-05 -->
<!-- content: measured · **297 offers are reachable in ONE request and the count was taken by IDENTIFIER: the page's own AJAX route — `POST /gl/demandantes/busca-emprego/busca-emprego-en-galicia?ajax_form=1`, declared in the page's `drupalSettings` — returns 777 851 B of Drupal commands whose `insert` carries 478 961 B of table (233 314 characters of text, 597 `<tr>`), and `selector_provincia=1` («Ver todas») covers all four Galician provinces at once, so nothing is iterated and nothing is circumvented. TWO ENUMERATORS ON ONE PAGE, AND THEY ARE EQUAL BY MEMBERSHIP: the column identifier gives 297 distinct and the detail's «Identificador da Oferta» gives 297 distinct, intersection 297, zero on either side — compared member by member and never by cardinal. Columns: Oferta; Emprego; Localidade; Data, the newest dated 05/10/2026 which is the day of this reading, every identifier of the year 2026, and no sentinel date. WHAT THE ROUTE RETURNS THAT WE MUST NOT EMIT: 297 of 297 offers carry «Medio de Contacto» and 206 of 297 carry a LABELLED «Teléfono», with 63 e-mail occurrences and 17 distinct — so contact withholding is not an edge case here, it is every record. AND THE WITHHOLDING RULE MUST BE ANCHORED ON THE BOARD'S OWN LABEL, NEVER ON DIGIT SHAPE: a nine-digit Spanish-mobile pattern matches 547 times, of which EXACTLY 297 are the board's own public 012 helpline repeated once per offer in boilerplate, a number published in order to be called. THE ROOT IS A FALSE NEGATIVE: `https://…/` answers 301 to `http://…/gl` — the site downgrades its own scheme — then 301 to `http://…/gl/`, which answers HTTP 400 «The provided host name is not valid for this server», while `https://…/gl` fetched directly answers 200. METHOD: guard taken on each host form and on each exact path separately, in turns distinct from the retrievals; `bin/fetch-body.py` for every GET; the single POST by a scratchpad client reproducing its four disciplines, because our fetcher is GET-only; no `Crawl-delay` is written in the 2 027 B, so the 2 s of our own pace are the ones that apply** · 2026-10-05 -->

<!-- witness: none — the board states no total anywhere, and the result table paginates client-side rather than announcing a count; 297 is OUR count of distinct identifiers, agreed by two enumerators on the same page · 2026-10-05 -->

## Measured 2026-10-05 — 297 offers in one request, and every one of them carries a contact

```
robots.txt            2 027 o   groupe *, 34 Disallow / 18 Allow
                                = LE FICHIER PAR DEFAUT DE DRUPAL, non modifie
                                aucun agent d'IA nomme, aucun Crawl-delay -> 2 s a nous
                                DECLARE AUCUN SITEMAP
/sitemap.xml        124 029 o   286 <loc>, 286 lastmod (2024: 3 · 2025: 170 · 2026: 113)
                                les 286 sur speg15.xunta.gal, QUI NE RESOUT PAS
                                aucune des 286 n'est une annonce
https://.../          301   ->  http://.../gl        <- le site DEGRADE son schema
http://.../gl         301   ->  http://.../gl/
http://.../gl/        400       « The provided host name is not valid for this server. »
https://.../gl        200       (en direct, sans suivre : sain)
POST .../?ajax_form=1 200       777 851 o de commandes Drupal
  commande insert           478 961 o de table, 597 <tr>, 233 314 car. de texte
  offres par IDENTIFIANT    297 distincts (colonne) ∩ 297 (detail) = 297, 0 de chaque cote
  « Medio de Contacto »     297 / 297
  « Teléfono » etiquete     206 / 297
  regle a 9 chiffres        547 appariements, DONT 297 = la helpline 012 du board
```

**Found by the Spain pass of #949.** The country page carried this host as «&nbsp;à construire&nbsp;»
with «&nbsp;Service public de l'emploi de Galice… Site public, joignable.&nbsp;» *Joignable is true,
and it is true in a way the root cannot show.*

### The root answers 400 while the site is healthy — and the cause is the site's own redirect

**`https://emprego.xunta.gal/` redirects to `http://emprego.xunta.gal/gl`** — the scheme is
*downgraded by the site itself* — **and over plain HTTP the application refuses its own hostname**
with Drupal's trusted-host message. *Fetched directly, `https://…/gl` answers 200.*

> **A client that follows redirects faithfully — which is the correct behaviour — ends on a 400,
> and a 400 on the root reads exactly like «&nbsp;the board is down&nbsp;».** *Nothing in the response
> says a redirect was involved: the status is real, the body is real, and the diagnosis is wrong.*

*This cost two false diagnoses before the chain was read.* **First I read the 400 as the
application refusing the hostname outright; `/gl` and `/es` answering 200 refuted that. Then I read
a 200-on-invalid against 400-on-valid as a mystery; it was the 303 of a successful submission being
followed into `http://`.** **Neither was found by re-reading — only by refusing to follow
redirects and printing every hop with its host.**

**The conduct this requires is narrow and it is not a bypass:** *read the `Location`, raise
`http://` back to `https://`, and re-request.* **No control of the site is disabled; we decline only
to be downgraded.**

### `robots.txt` is Drupal's stock file, which is a fact about the CMS and not about the board

**34 `Disallow` and 18 `Allow`, byte for byte the file Drupal core ships.** *My first reading of the
counts was that someone had carved paths out deliberately — a non-empty `Allow` set is unusual in
this campaign. That reading is wrong:* **nobody carved anything, and the file therefore expresses no
editorial intention about offers at all.**

*One line still had to be checked rather than assumed:* **`Disallow: /search/` is Drupal's own
search path, and had the offers search lived under it the route would have been refused in
writing** — borne 1, which blocks every route. **It does not: the search is at
`/gl/demandantes/busca-emprego/…`, and the guard returns `allowed=True` on the exact path while
correctly returning `allowed=False` on `/search/node`.** *The rule was exercised in both
directions, which is the only way a guard says anything.*

### A sitemap that nobody declared, pointing at a host that does not exist

| what | what it says |
| :-- | :-- |
| `robots.txt` | declares **no** sitemap |
| `/sitemap.xml` | answers **200**, 124 029 B, 286 `<loc>`, **286 `lastmod`** |
| the 286 `<loc>` | all on **`speg15.xunta.gal`** — **no DNS on 1.1.1.1 or 8.8.8.8** |
| the 286 paths | institutional pages; **not one is an advert** |

**So the enumerator is present, undeclared, well-formed and complete — and every row names a host
that cannot be resolved.** *The paths are right; the host is wrong, baked in from the site's own
base-URL configuration.* **A walker that follows `<loc>` verbatim gets 286 DNS failures and
concludes the board is dead.**

> *This is the fourth distinct way an offers sitemap has failed to be a witness in this campaign,
> and the four do not overlap:* **Manfred's `lastmod` spans six years; Portalento carries no
> `lastmod` at all; Feina Activa's sitemap is DECLARED and answers 404; this one is UNDECLARED,
> answers 200, and names an unresolvable host.** *A sitemap enumerates. It never attests.*

### The contact exposure is total, and the obvious rule would make us lie 297 times

**297 of 297 offers carry `Medio de Contacto`.** *The board announces this itself on the search
page: «&nbsp;No detalle da oferta aparecerán, ademais, os datos de contacto&nbsp;».* **206 of the 297
carry a labelled `Teléfono`, and there are 17 distinct e-mail addresses.** *So withholding is not an
edge case on this board; it is the shape of every record.*

**And the rule must be anchored on the board's own label.** *A nine-digit Spanish-mobile pattern
matches 547 times — and 297 of those 547 are a single value: the Xunta's public **012** helpline,
repeated once per offer in the boilerplate that tells the candidate how to apply.*

> **Withholding a number that is published in order to be called does not protect anyone, and it
> makes `withheld_fields` claim 297 withholdings that nobody ever posted** — *the exact defect of
> «&nbsp;declaring we withheld what nobody deposited&nbsp;», at a scale larger than the real contacts it
> would be hiding.*

*And the shape rule's surplus is not all helpline:* **547 − 297 = 250 remain against 206
label-anchored, and those 250 are NOT established to be phone numbers.** *That gap is named here
rather than resolved, because resolving it needs the per-offer detail pages and this is a
measurement.*

### What an adapter would do

```
route   : http — ONE POST to …/busca-emprego-en-galicia?ajax_form=1 with
          selector_provincia=1 («Ver todas»), selector_orden=4 («Data»),
          form_build_id + form_id harvested from the page in the same pass.
          2 s pace (no Crawl-delay written). 297 offers for one request.
FIRST   : do NOT follow the site's redirects into `http://` — raise them back to
          `https://`, or the walk ends on a 400 that looks like an outage.
carries : the identifier (NN/YYYY/NNNN), the occupation, the locality, the date,
          and the free-text «Detalles» with its stated requirements
NEVER   : the contacts. 297/297 carry one, so the withholding rule runs BEFORE
          any extraction — and it is anchored on «Medio de Contacto: Teléfono»,
          never on nine digits, or it withholds the public 012 line 297 times
          and declares a discretion it never exercised
no count: the board states no total; 297 is ours, agreed by two enumerators
```

### A tooling gap this board is the first to hit

**`bin/fetch-body.py` can only GET** — no `--data`, no `--method`. *This is the first board of the
campaign whose search is a POST, so the repository's own disciplined fetcher cannot measure it.*
**The single POST was therefore made by a scratchpad client that reproduces its four disciplines
explicitly** — guard on the exact URL, declared identity from `_ua.UA`, the HTTP code tested, and
provenance written beside the body — *rather than quietly dropping them, which is what an ad-hoc
script does by default.* **Reported rather than patched: `fetch-body.py` is shared tooling.**

### What this card does NOT say

**It does not say 297 is the size of the Galician market, nor that the 297 are all open.** *The
column `Data` is a date the board prints, not a status, and no offer states that it is open.*
**What is established is narrow and dated: on 2026-10-05, one POST returned 297 distinct offer
identifiers, agreed by two enumerators on the same page.**

**Measured 2026-10-05 by the declared client, the guard taken on EACH host form and EACH exact path
in a turn distinct from the retrieval, `bin/fetch-body.py` for the GETs, DNS on two public
resolvers, redirect chain read hop by hop without following.** *A measurement, not an adapter.*

```
_robots.verdict('emprego.xunta.gal')   state: read,     certain: True,  2 027 B, 34 Disallow / 18 Allow
_robots.verdict('emprego.xunta.es')    state: no-rules, certain: False
allowed('emprego.xunta.gal', '/gl/demandantes/busca-emprego/busca-emprego-en-galicia')  True
allowed('emprego.xunta.gal', '/search/node')                            False  (rule '/search/')
dig @1.1.1.1 / @8.8.8.8  emprego.xunta.gal  ->  85.91.64.105  (identique)
dig @1.1.1.1 / @8.8.8.8  speg15.xunta.gal   ->  AUCUNE REPONSE des deux cotes
GET  /robots.txt · /sitemap.xml · /gl/buscar-emprego-en-galicia          200
GET  /  ->  301 http://…/gl  ->  301 http://…/gl/  ->  400
POST /gl/demandantes/busca-emprego/busca-emprego-en-galicia?ajax_form=1  200, 777 851 B
```
