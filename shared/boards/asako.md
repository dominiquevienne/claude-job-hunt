# Board adapter — Asako.mg (`www.asako.mg`, Madagascar): the listing states its count on the server (478 of the 479 it states, read 2026-11-02 from the `totalCount` of its RSC flight), the ads are named by the sitemap the HOST DECLARES — `/sitemap-jobs.xml`, not `/sitemap.xml`, which carried them until 2026-09-14 and carries none now — each ad carries a JobPosting — `asako.py`, the count printed beside every walk with the witness it came from

<!-- verified: 2026-11-02 -->

<!-- hosts: www.asako.mg, asako.mg -->
<!-- script: asako.py -->
<!-- host-forms: www.asako.mg -->
<!-- host-forms-basis: read — every sitemap row and every card link is on `www.asako.mg`; `asako.py` names the host as a literal and refuses an ad address on any other · 2026-09-14 -->
<!-- countries: MG -->
<!-- content: measured · rules read and certain (1 877 B, md5 ba46383a2cc3 — the SAME md5 as 2026-09-14: `Claude-User` keeps its own group, `Allow: /`, no Crawl-delay) — and the transport answers 200 on Vercel at `/emploi` (353 739 B, byte-identical twice, REDESIGNED: no «offres disponibles» anywhere, the count three times otherwise and `totalCount: 479` in its RSC flight, and its 20 cards are now real `<a href="/annonces/...">` links where 2026-09-12 recorded ZERO), at `/emploi/page/2` (204 801 B, the OLD template with «479 offres disponibles» intact and `/page/3` behind a server link), at `/sitemap.xml` (31 202 B, 361 rows and NOT ONE advertisement) and at `/sitemap-jobs.xml` (72 329 B, 479 rows of which 478 ads, lastmod 2026-09-18 … 2026-11-01) · 2026-11-02 03:17 UTC -->
<!-- witness: `totalCount: 479` in the RSC flight of `/emploi` AND of `/emploi/page/2`, the structural witness the redesign did not move, beside «479 offres disponibles» still served on page 2 — and the two enumerators AGREE, which was checked and not assumed: the 40 ad links of pages 1–2 are ALL in `/sitemap-jobs.xml` (0 outside) and its 479 rows match the 479 the page states, so the sitemap is a witness and not a second population; `/emploi/page/N` is a measured fallback route; a page with no witness at all still exits 6 · 2026-11-02 -->
<!-- route: http · 478 · 2026-11-02 -->

## 2026-11-04 18:03:59Z — the refused row is GONE, which is not «repaired» (#1245)

**Zero rows of `/sitemap-jobs.xml` are set aside today, so the premise of #1245 is
WITHOUT OBJECT rather than fixed.** Read 2026-11-04 18:03:59Z under the declared
`Claude-User`: 200 on Vercel, 81 541 B, `md5 e9d3320036a4630d12893f2483681435`,
`Age: 2846` so the body was up to 48 min old at the edge — **541 `<loc>` rows, 541
distinct, 541 accepted by the address pattern, 0 set aside**. The row this card names,
`/annonces/sdr-b2b-freelance7d468b86`, is NO LONGER IN THE SITEMAP. The pattern was not
touched and nothing was emitted: this pass held the sitemap and read it.

**The discriminant between «repaired» and «expired», because the two call for opposite
conduct.** The ad is gone AND the address form is unchanged: 541 of 541 rows are
`<slug>-<hex>`, and **ZERO** carry a hex run glued to the slug with no separating
hyphen. So nothing on the site stops the next ad from being named the same way, and the
decision this card declines — guessing where a slug ends — remains the only way such a
row could be emitted. «Repaired» would assert a property of the SITE where there is
only a dated behaviour, and it would close an issue that can reopen by itself.

**Two numbers, two grandeurs: the 541 above does NOT correct the 478 of `route:`.**
`478` is what the adapter EMITS of the `479` the LISTING states, read from the
`totalCount` of its RSC flight on 2026-11-02; `541` is the ROW COUNT OF THE SITEMAP,
read today. The sitemap has grown, 479 → 541 rows. **NOT established, and declared:**
the listing's `totalCount` was NOT read on 2026-11-04, so the `witness:` line above —
the two enumerators agree — is neither confirmed nor refuted for today, and the
sitemap's 541 is not a second population until it is checked against the listing again.
`route:`, `content:`, `witness:` and `verified:` are therefore LEFT AS THEY STAND:
re-verifying means RUNNING the adapter, which this pass did not do.

## 2026-11-02 03:14–03:17Z — two things moved, the adapter's guard caught both, and #1239 is the remeasurement

**The adapter exited `rc=6` on «200 and no «N offres disponibles»» and that verdict was
RIGHT — the phrase has gone from `/emploi`.** It had not gone from the board, and nothing
here is a defect of the adapter: the `die` that refused to report zero is untouched, and it
is the reason this board never silently reported an empty market.

**What the four header fields above corrected.** `verified` was `2026-09-14`; `route` was
`http · 253 · 2026-09-14`; `content` described `/emploi` at 136 440 B with «251 offres
disponibles» and **«0 `/emploi/<id>` links in the HTML»**; `witness` was the page's own
«<strong>253</strong> offres disponibles». All four were true on their day.

| what was read | then | now |
| :-- | :-- | :-- |
| the count's wording on `/emploi` | «<strong>253</strong> offres disponibles» | **gone** — «479 offres d'emploi» twice, «Vous voyez <strong>20</strong> offres sur <strong>479</strong>», and `totalCount: 479` in the flight |
| the count on `/emploi/page/2` | not read | **«<strong>479</strong> offres disponibles», the OLD template intact** |
| the 20 cards in the served HTML | **0 links to an offer page** | **20 real `<a href="/annonces/…">`** |
| «Charger plus d'offres» | a client action | **a server link, `/emploi/page/2` → `/page/3` → …** |
| the ads' sitemap | `/sitemap.xml`, 582 rows / 253 ads | **`/sitemap-jobs.xml`, 479 rows / 478 ads** — and `/sitemap.xml` now has 361 rows and **not one ad** |
| the ad page | a JobPosting | **unchanged** — 153 074 B, `record()` reads it with nothing altered |
| `robots.txt` | 1 877 B, md5 ba46383a2cc3 | **the same md5**, `Claude-User` with its own group, no Crawl-delay |

**So the template changed on PAGE 1 ONLY, and the reader was pointed at the one page that
stopped carrying its phrase.** That is the whole of the `rc=6`.

**And the host had been publishing the new address the whole time.** `robots.txt` declares
four sitemaps — `/sitemap.xml`, `/sitemap-jobs.xml`, `/sitemap-blog.xml`,
`/sitemap-guides.xml` — and until today not one of those declarations was read: the adapter
held `/sitemap.xml` as a constant. It now DERIVES its candidates from the declarations
(`_robots.sitemaps_for`, whose own docstring documents this trap), tries the ones whose
address hints at jobs first, and names the one that answered on the line that always prints.
Only `www.asako.mg` and `asako.mg`: a row from a third host would ride into every record's
`url`.

**One row of the 479 is not emitted, and it says so rather than vanishing.**
`/annonces/sdr-b2b-freelance7d468b86` has its hex glued to the slug with no hyphen, so the
address pattern refuses it and no identifier can be read from it. It is counted and NAMED,
never filed under «other rows set aside» — an ad dropped in silence is the one thing a row
count cannot show — and `478 of the 479 the site states` already reports the gap
arithmetically. Emitting it would need a guess at where the slug ends, which is a decision
and not a fix.

**Not a verdict that the host is closed, and no antirobot control appeared.** Nothing refused
us; every fetch under the declared identity through `bin/fetch-body.py`, the guard taken on
each exact path in a turn distinct from the retrieval, 2 s of our own between requests.

**Measured 2026-09-12 at 15:27:50Z UTC for #233, lot 7 — a measurement of
the transport, not a decision about the host.** Every fetch under the
declared identity, the guard on the exact path first, `bin/fetch-body.py`.

## The rules — reopened by the doctrine of 2026-09-07, and 251 offers behind them

```
robots.txt      read twice, certain: True, 1877 B, md5 ba46383a2cc3 both times — Cloudflare's managed block (`ClaudeBot` named and refused, `*` open) plus the operator's lines
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed()       True on `/`, `/emploi`
crawl_delay     none
```

*#233's consolidated list put this host under the fifth form — «Claude-User
permitted by name» — on a 2026-09-11 read; the file read on 2026-09-12 is
the managed block naming `ClaudeBot`, and `Claude-User` falls under `*`.
Both are readings, each dated; the route is the same.*

## The transport — 200, on Vercel

```
GET https://www.asako.mg/          200, 330 453 B, md5 574e7cbe280b   (15:27:50Z, and identical at 15:27:51Z)  «Asako.mg — Offres d'emploi à Madagascar», server: Vercel
GET https://www.asako.mg/emploi    200, 136 440 B, md5 5d3a334cf46c   (15:28:48Z, and identical at 15:28:49Z)  «Toutes les offres d'emploi à Madagascar»
```

## What the listing says

| question | answer |
| :-- | --: |
| offers stated | **251** — «251 offres disponibles», and «Vous voyez 20 offres sur 251» beside the «Charger plus d'offres» button |
| cards in the served HTML | 20 (title · employer · city · sector · contract; «Sponsorisé» on the first) — in the RSC payload (`self.__next_f`), not as `<a href>`: **0 links to an offer page in the HTML** |
| the enumeration | behind «Charger plus», a script; the app router's data route is the adapter's first question |
| JSON-LD | `Organization`, `WebSite`, six `Question`/`Answer` on the root; `BreadcrumbList` on `/emploi`; no `JobPosting` seen |

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE:
  the site serves, states 251, and hides the list behind a script. **Candidate
  adapter** — the Next.js data route (`?_rsc=` or a `/api/`) is what an
  adapter reads; not asked here. *Madagascar's other host of #233,
  `portaljob-madagascar.com`, is an Inertia shell that serves no
  advertisement to a plain client (its own card).*
- **Not a verdict that the host is closed** — nothing refuses us.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.

## 2026-09-14 09:48–09:58 UTC — the name is back, and the adapter is written (#338)

`dig @1.1.1.1` and `@8.8.8.8` answer NOERROR (76.76.21.21, Vercel): the
NXDOMAIN of 2026-09-13 is over. The declared client is served; the rules
name `Claude-User` with its own group (`Allow: /`; `/api/`, `/admin/`,
`/recruteur/`, `/candidat/`, `/dashboard/`, `/go/` refused — never sent).

```
GET /emploi                 200, 132 972 B — «<strong>253</strong> offres disponibles», «Vous voyez 20 offres sur 253», 20 cards in the RSC flight, «Charger plus d'offres» a client action
GET /sitemap.xml            200, 582 rows — 253 /annonces/<slug>-<hex> with lastmod (2026-09-01 … 2026-09-14), 229 /emploi/… facets, 87 employer profiles, pages
GET /annonces/<slug>-<hex>  200, ~160 KB — a JobPosting JSON-LD (title, description, identifier UUID, dates, employmentType, hiringOrganization with url and sameAs, jobLocation or TELECOMMUTE + applicantLocationRequirements, responsibilities, qualifications, skills, industry, occupationalCategory)
GET /annonces/<slug>-10053  200, 145 KB — an older ad: a BreadcrumbList and no JobPosting; read from its own markup (<h1>, «chez MADIXY» in the title, «Publiée le 25 avril 2026», «Lieu de travail», «Missions principales», «Profil recherché»), `no_jobposting: true`
tab, /emploi                «Charger plus» ×12 → «Vous voyez 253 offres sur 253»; 253 distinct /annonces/
```

**`asako.py`**: `sitemap` (the 253 rows, one request), `list` (the stated
count, then the sitemap's ads read from their pages — 20 unless `--limit`,
2 s apart — «N emitted of the 253 the site states … not a shortfall»),
`ad`. Descriptions, responsibilities and qualifications scrubbed of
e-mail addresses and Malagasy telephone numbers; the application never
touched. Tests, six mutations red. `route: http · 253`.

