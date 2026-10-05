# Board measurement — Portalento (`www.portalento.es`, Spain): Inserta Empleo / Fundación ONCE, the disability-employment board — **582 adverts are enumerable through a DECLARED `sitemap_ofertas.xml` and every one carries a real `JobPosting`, but `hiringOrganization` names the INTERMEDIARY on 8 of 8 and never the end employer**; the listing itself is WebForms and shows zero advert links, which is a signature and not a content; rules open with no AI agent named

<!-- verified: 2026-10-05 -->

<!-- hosts: www.portalento.es -->
<!-- script: none -->
<!-- countries: ES -->
<!-- content: measured · **582 adverts are enumerable in ONE request and each carries a real `JobPosting`: `sitemap_ofertas.xml` (200, 97 702 B, md5 4d2930eb4c17) declares 582 `<loc>`, all `/Candidatos/Ofertas/Detalle/<slug>/<guid>`, and 8 adverts fetched (1 first + 7 sampled with a fixed seed) carried a `JobPosting` block 8 times out of 8, with `title`, `datePosted`, `employmentType`, `hiringOrganization` and `jobLocation`. WHAT THE FIELDS DO NOT GIVE: `hiringOrganization` is the bare string «Inserta Empleo» on 8 of 8 — Fundación ONCE's own placement arm, the INTERMEDIARY and never the end employer; `baseSalary` is null on 7 of 7 sampled; `validThrough` is null on 7 of 7; and `jobLocation.address` is a STRING, not a `PostalAddress`, so a reader expecting `address.addressLocality` gets nothing. THE SITEMAP CANNOT DATE ANYTHING — it carries ZERO `lastmod` — but every advert states its own `datePosted`, and the eight span 2026-03-30 to 2026-10-02, so freshness is establishable PER ADVERT and not from the enumerator. The listing `/Candidatos/Ofertas` («Búsqueda de ofertas», 40 287 B) carries ZERO advert link, ZERO `<article>` and `__VIEWSTATE` ×4: ASP.NET WebForms, whose results arrive by `__doPostBack` — the sitemap bypasses it entirely. METHOD: `robots.txt` 4 597 B (`state: read`, `certain: True`, group `*`, no AI agent named, no `Crawl-delay` — so 2 s are ours), declaring five sitemaps of which `sitemap_ofertas.xml`; guard open and certain on `/`, `/Candidatos/Ofertas`, an advert path and `/sitemap.xml`** · 2026-10-05 -->

<!-- witness: none — the board states no count anywhere, and the listing that would state one is a WebForms search page that returns no result without a postback; 582 is the sitemap's extent · 2026-10-05 -->

## Measured 2026-10-05 — the enumerator is declared, and the employer field is filled by the intermediary

```
robots.txt            4 597 o   groupe *, aucun agent d'IA nomme, aucun Crawl-delay
                                declare 5 sitemaps, dont sitemap_ofertas.xml
sitemap_ofertas.xml  97 702 o   582 <loc>, /Candidatos/Ofertas/Detalle/<slug>/<guid>
                                AUCUN lastmod — l'enumerateur ne date rien
/Candidatos/Ofertas  40 287 o   0 lien d'annonce, 0 <article>, __VIEWSTATE x4
8 annonces lues                 8/8 portent un JobPosting
  hiringOrganization            « Inserta Empleo »  8/8
  datePosted                    2026-03-30 … 2026-10-02, present partout
  baseSalary / validThrough     null 7/7
  jobLocation.address           une CHAINE, pas un PostalAddress
```

**Found by the Spain pass of #949.** The country page carried this host as «&nbsp;à construire&nbsp;» and
named its value precisely: *«&nbsp;les employeurs soumis à l'obligation d'emploi y publient ce qu'ils
ne publient nulle part ailleurs&nbsp;»*. **That is why it was taken before bigger boards — the
ordering is additivity, not volume** (`shared/false-zero-cost.md`): its absence is a hole, not a
duplicate.

### The employer field is filled, and filled by the intermediary

**«&nbsp;Inserta Empleo&nbsp;» on 8 of 8** — Fundación ONCE's placement arm, which is who *places* the
worker, not who *employs* them.

> **The empty field is honest; the field filled by the intermediary is not, and it is the second
> that never gets a warning** — because no automatic check fires on a non-empty string.

*This is the defect the Spain page already documented for InfoEmpleo («&nbsp;ANANDA GESTION ETT&nbsp;»):
a real, verifiable name, and the company where the candidate will actually work is still not
named.* **Here it is not one advert in three, it is all of them, and it is structural rather than
accidental: the board belongs to the placement body.** *So an adapter must carry the name as what
it is — the placer — and must not let it occupy a field a reader will take for the employer.*

### The sitemap cannot date anything, and the advert can

**Zero `lastmod` in 582 rows.** *So the Manfred question (#949, `getmanfred.md`) — «&nbsp;is this
index an archive?&nbsp;» — cannot be answered from the enumerator here at all.* **But every advert
states `datePosted`, and the eight read span 2026-03-30 to 2026-10-02.** *Six months, so the 582
are plainly not all fresh; the difference from Manfred is that the discriminant EXISTS and sits one
request away, on the advert itself.*

| board | enumerator dates? | advert dates? | so freshness is |
| :-- | :-- | :-- | :-- |
| Manfred (#949) | `lastmod` over SIX years | not yet read | measurable on the index, coarsely |
| **Portalento** | **none at all** | **`datePosted` on 8/8** | **measurable per advert, exactly** |

### Zero advert links on the listing is a SIGNATURE, not a content

`/Candidatos/Ofertas` is titled «&nbsp;Búsqueda de ofertas&nbsp;» and carries **no** advert link, **no**
`<article>`, and **`__VIEWSTATE` four times**. *ASP.NET WebForms: the results arrive through
`__doPostBack`, and the advert identity lives in hidden fields.* **Counting links on markup that
does not use them returns a perfect false negative — 200, clean parse, no exception, and a quiet
wrong conclusion.** *The repository has paid for this twice (Inertia.js, then WebForms).*

**It costs nothing here, because the declared sitemap bypasses the listing entirely** — but it is
written down so that nobody re-measures the listing and concludes the board is empty.

### What an adapter would do

```
route   : http — sitemap_ofertas.xml is DECLARED: 582 adverts for one request,
          then one request per advert for its JobPosting. 2 s pace (none written).
carries : title, datePosted, employmentType, and the location as the STRING the board
          writes (no PostalAddress to unpack — a reader expecting one gets nothing)
NEVER   : no salary (null 8/8) and no deadline (null) are to be invented
          and `hiringOrganization` is NOT emitted as the employer: it is «Inserta Empleo»
          on every advert, so it is carried as the PLACER or not at all
no count: the board states none, and the only page that could is a postback search
```

**Measured 2026-10-05 by the declared client, the guard on each exact path first,
`bin/fetch-body.py`, provenance beside every body.** *Eight adverts read: the first row of the
sitemap plus seven drawn with a fixed seed — a sample, named as one, not the 582.* *A measurement,
not an adapter.*

```
_robots.verdict('www.portalento.es')   state: read, certain: True, group '*', delay: None
GET /sitemap_ofertas.xml               200, 582 <loc>, 0 lastmod
GET /Candidatos/Ofertas                200, 0 advert link, __VIEWSTATE x4
GET /Candidatos/Ofertas/Detalle/…      200 x8, JobPosting 8/8
```
