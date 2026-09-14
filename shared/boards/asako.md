# Board adapter — Asako.mg (`www.asako.mg`, Madagascar): the listing states its count on the server («253 offres disponibles» on 2026-09-14), the sitemap names every advertisement, each ad carries a JobPosting — `asako.py`, the count printed beside every walk; the name back after two days of NXDOMAIN

<!-- verified: 2026-09-14 -->

<!-- hosts: www.asako.mg, asako.mg -->
<!-- script: asako.py -->
<!-- host-forms: www.asako.mg -->
<!-- host-forms-basis: read — every sitemap row and every card link is on `www.asako.mg`; `asako.py` names the host as a literal and refuses an ad address on any other · 2026-09-14 -->
<!-- countries: MG -->
<!-- content: measured · rules read twice and certain (1 877 B, Cloudflare's managed block naming `ClaudeBot`, `*` open — `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200 on Vercel at the root (330 453 B, byte-identical twice) and at `/emploi` (136 440 B, byte-identical twice): the listing states «251 offres disponibles» and «Vous voyez 20 offres sur 251 — Charger plus», a Next.js app-router page whose 20 cards are in the RSC payload and whose «load more» is a script; 0 `/emploi/<id>` links in the HTML · 2026-09-12 15:28 UTC -->
<!-- witness: the page's own «<strong>253</strong> offres disponibles» on `/emploi`, printed on the server and read by `asako.py list` beside the sitemap's rows («6 emitted of the 253 the site states … 253 in the sitemap»); a tab pressed «Charger plus d'offres» twelve times and reached «Vous voyez 253 offres sur 253»; a page without the count exits 6 · 2026-09-14 -->
<!-- route: http · 253 · 2026-09-14 -->

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

