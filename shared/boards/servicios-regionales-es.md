# Board measurement — ECyL · INAEM · SEF (`empleo.jcyl.es`, `inaem.aragon.es`, `sefcarm.es`): three of Spain's seventeen regional employment services — **three different rule states, three different URL philosophies, and three different entry points, measured rather than asserted**: rules read with 39 refusals / read with an EMPTY `Disallow` / absent entirely; semantic paths / Liferay slugs / opaque numeric ids; and on one of the three the search-results endpoint is refused in writing

<!-- verified: 2026-10-05 -->

<!-- hosts: empleo.jcyl.es, inaem.aragon.es, www.sefcarm.es, sefcarm.es -->
<!-- script: none -->
<!-- countries: ES -->
<!-- host-forms-basis: read, read and absent — the three answer differently and that IS the finding: `empleo.jcyl.es` serves 1 899 B (md5 cba755041536, `state: read`, `certain: True`) with 39 `Disallow` and a second group for its own `YIPPY_JCYL` bot; `inaem.aragon.es` serves 70 B (md5 cc737d130db5, `state: read`, `certain: True`) whose `Disallow:` is EMPTY — nothing closed — and which declares a sitemap as `http://inaem.aragon.es:80/sitemap.xml`; `sefcarm.es` and `www.sefcarm.es` answer 404 on the rules file, so `state: absent`, `certain: True` — a knowledge and an open door under #283, not an ignorance · 2026-10-05 -->
<!-- content: measured · **the country page's claim that these services share no common base is now measured on three layers, and they differ on every one: 39 refusals against an empty `Disallow` against no rules file at all; `empleo.jcyl.es` writes 1 899 B of hand-maintained CMS exclusions (templates, contact forms, PDF generators, base64-looking `cid=` and `param1=` patterns, one malformed `remotousuarios*` with no leading slash) plus a separate group for its own `YIPPY_JCYL` search bot, and NOT ONE of the 39 names an offer — but `*/SEResultadosBuscador17` IS refused, and that is its search-RESULTS endpoint, so if its offers are served through that searcher the route is closed in writing to every route (borne 1); `inaem.aragon.es` closes nothing at all in 70 bytes; `sefcarm.es` publishes no rules file. THREE URL PHILOSOPHIES, WHICH IS A SHARPER STATEMENT THAN «THREE DIFFERENT SITES»: jcyl uses semantic paths (`/web/es/busco-empleo/buscador-ofertas-empleo.html`), inaem uses Liferay friendly slugs (`/ofertas-de-empleo`), and sefcarm uses OPAQUE NUMERIC IDS on a single path (`/web/pagina?IDCONTENIDO=70767&IDTIPO=100&RASTRO=…`) where nothing in the URL says what it holds — so on sefcarm a path-based discriminant cannot exist and the entry point is findable only by the Spanish LINK TEXT, which makes the discriminant language-dependent. WHAT WAS READ: the three roots answer 200 and are readable (153 598 B / 38 146 B / 35 493 B; 7 615 / 2 155 / 5 010 characters of visible text), inaem is Liferay (97 occurrences) and serves `/ofertas-de-empleo` at 133 723 B with «oferta» 43 times and no JSON-LD, no `__NEXT_DATA__` and no Angular marker; jcyl's root carries one JSON-LD block and 51 of its 108 links name an offer, including a second HOST over http (`empleocastillayleon.jcyl.es/oficinavirtual`); sefcarm's root links no offer at all — its only offer-word href is its own LinkedIn page — and the section is reached only through the text «Ofertas de empleo». AND INAEM'S DECLARED SITEMAP IS A SIXTH SHAPE: 20 233 B, a Liferay `sitemapindex` of 118 children each keyed by CMS layout (`/sitemap.xml?p_l_id=…&layoutUuid=…&groupId=51284`), ZERO `lastmod`, and not one path naming an offer — plus the `<loc>` values carry `&amp;` inside the XML, so a consumer that does not unescape requests the wrong layout. WHAT IS NOT ESTABLISHED: no advert was read on any of the three, no count is claimed, and no per-advert shape is known — the entry point of each is identified and the enumeration behind it is not. METHOD: guard taken on all four host forms and on each exact path in turns distinct from the retrievals and exercised in BOTH directions (jcyl's `*/SEResultadosBuscador17` refused, its searcher page and the other paths permitted); none of the three writes a `Crawl-delay`, so the 2 s of our own pace apply to all three** · 2026-10-05 -->

<!-- witness: none — no advert was read and no listing was enumerated on any of the three, so there is nothing to count and no count is claimed; the only figures here are byte sizes, rule counts and link counts · 2026-10-05 -->

## Measured 2026-10-05 — three services, three rule states, and 39 refusals of which none names an offer

```
empleo.jcyl.es     robots.txt  1 899 o  md5 cba755041536, read, certain
  groupe *                              39 Disallow, 0 Allow, aucun sitemap declare
    ce qu'ils visent                    gabarits CMS, formulaires de contact,
                                        generateurs de PDF, motifs cid=/param1=
    aucun des 39 ne nomme une offre
    MAIS  */SEResultadosBuscador17      REFUSE  <- son moteur de RESULTATS
    et    remotousuarios*               malforme : pas de / initial
  groupe YIPPY_JCYL                     son propre robot de recherche, liste voisine
inaem.aragon.es    robots.txt     70 o  md5 cc737d130db5, read, certain
  User-Agent: * / Disallow:             VIDE -> rien n'est ferme
  Sitemap:                              http://inaem.aragon.es:80/sitemap.xml
sefcarm.es · www.  robots.txt       —   404 -> state absent, certain TRUE
                                        une CONNAISSANCE, pas une ignorance (#283)
aucun des trois n'ecrit de Crawl-delay  -> les 2 s sont les notres
les trois racines                       200 · 200 · 200, toutes LISIBLES
  inaem        153 598 o   7 615 car.   Liferay (97) · lie /ofertas-de-empleo
  sefcarm       38 146 o   2 155 car.   AUCUN lien d'offre ; seul mot d'offre = LinkedIn
  jcyl          35 493 o   5 010 car.   1 bloc JSON-LD · 51 liens sur 108 nomment une offre
                                        dont un AUTRE hote, en http :
                                        empleocastillayleon.jcyl.es/oficinavirtual
trois philosophies d'URL
  jcyl       /web/es/busco-empleo/buscador-ofertas-empleo.html      semantique
  inaem      /ofertas-de-empleo                                      slug Liferay
  sefcarm    /web/pagina?IDCONTENIDO=70767&IDTIPO=100&RASTRO=…       ID OPAQUE
             -> sur sefcarm, le chemin ne dit RIEN : l'entree se trouve
                uniquement par le TEXTE du lien « Ofertas de empleo »
inaem /ofertas-de-empleo      200, 133 723 o, 10 134 car., « oferta » x43
                              aucun JSON-LD, aucun __NEXT_DATA__, aucun Angular
le sitemap DECLARE d'inaem     20 233 o, sitemapindex de 118 enfants
                              chacun /sitemap.xml?p_l_id=…&layoutUuid=…&groupId=51284
                              ZERO lastmod · aucun chemin ne nomme une offre
                              et les <loc> portent « &amp; » DANS le XML
```

**Found by the Spain pass of #949**, where the country page carries these three on a single line
*«&nbsp;cités ici pour ce qu'ils illustrent : chaque communauté a son domaine, son moteur et son
format… **Aucun socle commun observé** — c'est le contraire du réseau français des centres de
gestion, où un seul adaptateur couvre tout le monde&nbsp;»*.

> **That claim is now measured rather than asserted, and it holds on three separate layers.**
> *Three rule states, three URL philosophies, three entry points — and no two of the three agree on
> any of them.* **A single adapter for Spain's regional services is not a thing that could be
> written from these three.**

### Layer one: the rules, and they could not differ more

| service | rules | what it closes |
| :-- | :-- | :-- |
| `empleo.jcyl.es` | **read**, 1 899 B | **39 `Disallow`**, plus a group for its own bot |
| `inaem.aragon.es` | **read**, 70 B | **nothing** — `Disallow:` is EMPTY |
| `sefcarm.es` | **absent** (404) | nothing — there is no file |

**`inaem`'s empty `Disallow:` is how a file says *nothing is closed*** — the form this repository
already knows from `employtt.gov.tt`'s 26 bytes — *and the guard reads it correctly as zero rules
rather than as one rule matching everything.*

**And `sefcarm`'s 404 is a KNOWLEDGE, not an ignorance**: under the owner's #283 decision a 404 is
`certain: True` — *the host looked and there is nothing* — where a timeout or a 403 would have been
`certain: False`.

### And one of the 39 refusals bites, which is why they were read rather than counted

**Not one of jcyl's 39 names an offer** — they are CMS templates, contact forms, PDF generators,
base64-looking `cid=` and `param1=` patterns, and one malformed `remotousuarios*` with no leading
slash. **But `*/SEResultadosBuscador17` is refused, and that is its search-RESULTS endpoint.**

> *So if ECyL serves its offers through that searcher, the route is closed in writing — borne 1,
> which blocks every route including a driven one.* **The guard was exercised in both directions:
> `/SEResultadosBuscador17` returns `False` with that exact rule, while the searcher PAGE
> (`/web/es/busco-empleo/buscador-ofertas-empleo.html`) returns `True`.**

*Which of the two actually carries the results is the first thing to establish on jcyl, and it is
not established here.*

### Layer two: three URL philosophies, and one of them forbids a path-based discriminant

```
jcyl      /web/es/busco-empleo/buscador-ofertas-empleo.html     SEMANTIQUE
inaem     /ofertas-de-empleo                                     SLUG Liferay
sefcarm   /web/pagina?IDCONTENIDO=70767&IDTIPO=100&RASTRO=…      ID OPAQUE
```

**On sefcarm every content link is the same path with a different number.** *Nothing in the URL
says what it holds, so no path-based discriminant can exist* — **the offers section is findable
only through the Spanish link text «&nbsp;Ofertas de empleo&nbsp;», which makes the discriminant
language-dependent in a way the other two are not.**

*This repository has written «&nbsp;only the PATH sorts facets from natures&nbsp;» before. Here the
path sorts nothing, and that is a property of the CMS rather than of the board.*

### Layer three: what each root actually serves

**All three answer 200 and all three are readable** (the mojibake check was taken before any
conclusion of absence). *But they do not serve the same kind of page:*

- **`inaem`** is Liferay and links its offers directly; `/ofertas-de-empleo` serves 133 723 B with
  «&nbsp;oferta&nbsp;» 43 times, **no JSON-LD, no `__NEXT_DATA__`, no Angular marker** — a
  server-rendered page.
- **`jcyl`** carries one JSON-LD block and 51 of its 108 links name an offer — **including a second
  HOST, over http: `empleocastillayleon.jcyl.es/oficinavirtual`.** *Whose rules bind separately and
  were not read.*
- **`sefcarm`** links **no** offer at all. *Its only offer-word href is its own LinkedIn company
  page* — a reminder that a keyword count on links can find a social profile and call it a board.

### A sixth sitemap shape, and an escaping trap inside it

**`inaem`'s declared sitemap is a Liferay `sitemapindex` of 118 children**, each keyed by CMS
layout — `/sitemap.xml?p_l_id=…&layoutUuid=…&groupId=51284` — with **zero `lastmod`** and not one
path naming an offer.

> *Sixth distinct way a declared sitemap has failed to be a witness in this pass:* **Manfred spans
> six years; Portalento carries no `lastmod`; Feina Activa declares one that 404s; Emprego Xunta
> serves an undeclared one naming an unresolvable host; Hosco and JobToday stamp every row with
> their build date; and this one enumerates CMS LAYOUTS.**

**And its `<loc>` values carry `&amp;` inside the XML**, so a consumer that does not unescape
requests a literally different layout. *The same «a string has several forms at the point of call»
trap, this time one layer down, in XML rather than in HTML.*

*The declaration itself is also odd and is recorded as read:* `http://inaem.aragon.es:80/sitemap.xml`
— **http, with the default port written explicitly.** *The resource was fetched over https on the
same host; the mismatch is the host's, and nothing here depends on it.*

### What this card does NOT say

**No advert was read on any of the three, no count is claimed, and no per-advert shape is known.**
*The ENTRY POINT of each service is identified and the ENUMERATION behind it is not* — which is
three separate pieces of work, because the three share nothing that would let one serve for
another.

**And this is three of seventeen.** *The page names the other large ones separately — LABORA, SAE,
Comunidad de Madrid — and the health-service `bolsas` on a different axis again.* **Nothing measured
here predicts any of them**, which is the same reserve that held for Feina Activa, Lanbide and
Emprego Xunta: *three regional services measured earlier in this pass produced three unrelated
obstacles, and these three produce three more.*

**Measured 2026-10-05 by the declared client, the guard taken on all four host forms and each exact
path in a turn distinct from the retrieval and exercised in both directions, `bin/fetch-body.py`
throughout at our own 2 s since none of the three writes a `Crawl-delay`, DNS on two public
resolvers.** *A measurement, not an adapter.*

```
_robots.verdict('empleo.jcyl.es')    state: read,   certain: True,  1 899 B, 39 Disallow
_robots.verdict('inaem.aragon.es')   state: read,   certain: True,     70 B,  0 Disallow
_robots.verdict('www.sefcarm.es')    state: absent, certain: True   (404 on the rules file)
allowed('empleo.jcyl.es', '/SEResultadosBuscador17')   False  (rule '*/SEResultadosBuscador17')
allowed('empleo.jcyl.es', '/web/es/busco-empleo/buscador-ofertas-empleo.html')   True
GET empleo.jcyl.es/        · inaem.aragon.es/        · www.sefcarm.es/     200 x3
GET inaem.aragon.es/sitemap.xml      200, 20 233 B, 118 layout children, 0 lastmod
GET inaem.aragon.es/ofertas-de-empleo  200, 133 723 B, «oferta» x43, no structured data
```
