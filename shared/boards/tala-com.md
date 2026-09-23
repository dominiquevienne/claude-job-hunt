# Board adapter — Tala-Com (DR Congo): the national directory's job section `/offres-demploi/`, fifteen a page to the pager's last page, the site stating no total and the pager the only bound (29 on 2026-09-21, 16–30); the advert's labelled block and dates; `talacom.py`, the applicant's e-mail and the application link withheld

<!-- verified: 2026-09-21 -->

<!-- hosts: www.tala-com.com -->
<!-- script: talacom.py -->
<!-- countries: CD -->
<!-- content: measured · **2026-09-21 07:33–07:38 UTC, the declared client, the guard on the exact path. Rules (1 583 B, md5 a6ff584c1562): `*` refuses the WordPress internals and `/*?*` (no query string is ever sent); a group naming sixteen AI agents — `ClaudeBot`, `Claude-Web`, `anthropic-ai` — carries no directive: nothing refused; no Crawl-delay. `/offres-demploi/` 200 (250 086 B) — fifteen `article.emploi-item` cards (employer, region, post, contract, `/offres-emploi/<slug>/`), pager `.talacom-pagination` naming page 2; `/page/2/` 200 fourteen; `/page/3/` **200 with no card** (224 631 B of shell — the walk ends on the pager, not on a 404). `talacom.py list` live 07:38 UTC: **«29 emitted — the site states no total; the pager bounds 16–30; 29 of 29 in the job sitemap (60 addresses, the archive with its expired adverts)»** — all 29 with employer, region, contract; Kinshasa 16, Nord-Kivu 6; CDD 23, CDI 4, autres 2. The Yoast `offre_emploi-sitemap.xml` (60 `<loc>`, lastmod 2025-10-22 → 2026-09-18) holds the 29 and 31 more — expired adverts the listing no longer shows. `/wp-json/wp/v2/offre_emploi` answers 200 (ten an answer, `content`, `date`, `city` id, `acf: []` — no expiry): the archive, not the route. The advert (`/offres-emploi/superviseur-nutrition-sante/`, 200, ~237 KB of Divi): title, `.acf-offre-infos` (Type de contrat, Nombre de postes, Référence, a «Document offre» PDF under `/wp-content/uploads/`), `.offre-ville`, a Cloudflare-protected e-mail, «Date d'expiration : 24/09/2026», a «Postuler» link, the description; JSON-LD WebPage `datePublished` 2026-09-18T20:31:18, no JobPosting; **the employer is not on the advert page** (the listing card carries it); an unknown slug 404 (exit 3)** · 2026-09-21 -->
<!-- witness: none stated — the site publishes no total; `talacom.py list` prints the pager's bound beside the count («the pager bounds 16–30», exit 6 when the count falls outside it) and checks every emitted address against the job sitemap (an absent one named) · 2026-09-21 -->
<!-- route: http · 29 · 2026-09-21 -->

## 2026-09-21 — `talacom.py` (#339)

```
talacom.py list [--no-sitemap]      # /offres-demploi/, /page/N/ to the pager's last page; «29 emitted — the site states no total; the pager bounds 16–30; 29 of 29 in the job sitemap (60 …)»
talacom.py ad --url https://www.tala-com.com/offres-emploi/<slug>/
```

**Only `/offres-demploi/` is read — the host is a hub (directory, tenders,
classifieds with scam listings, section below), and the adapter targets the
employment section and nothing else.** The walk stops at the pager's last
page (a page beyond it answers 200 with no card, so a 404 would never end
it); a promised page that shows nothing is said and the walk stopped; the
count is compared to the pager's bound and the job sitemap is read once so
an emitted address the sitemap does not carry is named. `ad` gives what the
listing does not — contract, number of posts, reference, the offer's PDF,
region, expiry (`dd/mm/yyyy` → ISO), the WebPage `datePublished`, the
description scrubbed — and the listing gives what the advert does not: the
employer.

**Withheld:** the applicant's e-mail (Cloudflare-protected on the page,
never decoded; scrubbed wherever it appears in text), telephones, the
«Postuler» link and the Google-Forms application link in the text, the
employer's logo. `contacts_withheld` on every record.

**Guard** `ACongoleseDirectoryWhoseJobSectionStatesNoTotalAndWhosePagerIsTheOnlyBound`
in `tests/test_core.py` — both ways (the walk to the pager and no further, a
repeated slug once, the promised empty page, the bound, the sitemap check,
`--no-sitemap`, no pager, not the listing, the advert's block and dates, the
scrub, the 404 slug, bad addresses and query strings refused before a
request, another host refused before the gate). Mutation bench 2026-09-21:
10 mutations, 10 red.

**A national board in a country of a hundred million people, and it refused our
client at the transport for three days.**

## The refusal targets our client, not every visitor

*This is the question the 2026-09-07 decision calls borne zero, and a browser
answers it in one request.*

```
python3 bin/fetch-body.py https://www.tala-com.com/...
   -> HTTP 403, 25 bytes, md5 9ccabba20b9f4ec7d18bd6644579e5bf
      body: b'Your request was blocked.'   (a shared provider default —
      www.hays.fr and three others serve the same 25 bytes)

a real browser, same path, 2026-09-08
   -> the page renders, 15 advertisements, no challenge of any kind
```

**The rules permit and the firewall refuses**, so under the 2026-09-07 decision
this was a browser candidate. **The browser answers the question the fingerprint
could not: the refusal is aimed at the simple client, not at every visitor.**

*Borne 2 is not strained here — **no antirobot control was presented and none
was defeated.** The page simply loaded.*

**And access is per session.** *One session was refused navigation to this
domain outright; two others reached it.* **A refusal in one session is not a
property of the host**, and it is not borrowed from another session either.

## This host is NOT a job board, and that is the first thing to know

`www.tala-com.com` is a **hub**: a company directory, brand promotions, public
**tenders**, events, and classified ads — *and its classifieds carry outright
scam listings.* **An adapter that swept this host would emit those as
vacancies.**

> **Only `/offres-demploi/` is the employment section.** *Anything built here
> targets that path and nothing else* — this is `appels-doffres-melanges-aux-annonces`
> on a host where nobody had looked for it.

## What the employment section holds

```
page 1   15 advertisements
page 2   15
page 3    1
         --
         31   no address repeated between pages
```

**Each card carries employer, city and contract type** — `CDD`, `CDI`, or
`autres`, in the board's own doubled form `CDD|CONTRAT A DUREE DETERMINEE (CDD)`.

**The employers are real and mostly humanitarian**: ACTED, Action contre la
Faim, Mercy Corps, INTERSOS, Handicap International, Médecins du Monde, COOPI,
ADRA, Fondation Mérieux — beside commercial ones (HSD Solutions, D-Pro
Services, Multi Task Company, Prodimpex, Pullman Kinshasa).

## The site declares no total, and that is a gap worth naming

**Nothing on the listing states how many advertisements exist.** The pagination
`1 2 3` bounds the count without stating it, and 31 is *our* count of *our*
extraction.

> **So an adapter here would have no anchor outside its own reader** — issue
> #181's exact shape. *A broken extractor would report zero, and the only thing
> contradicting it would be the pagination still showing three pages.*

**That is a weaker anchor than a declared total, and it is the one available.**
*Naming the gap is what this card can do; inventing a total is not.*

## 2026-09-12 — the name is out of the zone: NXDOMAIN everywhere, `clientHold` at the registrar

**Measured 2026-09-12 11:48 UTC, before any browser was opened for #222.**
The guard on `/offres-demploi/` returned INDETERMINATE — *«nodename nor
servname provided»* — and the second-resolver rule says a DNS negative is a
resolver's answer until two public resolvers agree:

```
dig @1.1.1.1  www.tala-com.com A   -> NXDOMAIN      tala-com.com A -> NXDOMAIN   NS -> (none)
dig @8.8.8.8  www.tala-com.com A   -> NXDOMAIN      tala-com.com A -> NXDOMAIN   NS -> (none)
dig @9.9.9.9  www.tala-com.com A   -> NXDOMAIN
whois tala-com.com   Registrar OVH sas · created 2023-09-20 · **expiry 2026-09-20** · Updated 2026-09-11T22:38:40Z
                     Domain Status: **clientHold** · clientDeleteProhibited · clientTransferProhibited · NS diva/grant.ns.cloudflare.com
```

**`clientHold` is the registrar withholding the delegation — the name servers
are still recorded, and the name is not published.** Three resolvers, two
names, one answer. *Updated at the registry the evening before, nine days
before the domain's expiry date.* **This is neither the 403 of the days
before nor a verdict on the board: it is a name that does not resolve today,
for a reason the registry states.**

So the browser route — first in the #222 order because this is the only
board of its country — **cannot be measured today by any client**, and
nothing was requested. *An INDETERMINATE is not probed.* What reopens it:
the name resolving again (`dig @1.1.1.1 www.tala-com.com A` returning an
address), which is the first line to run on any later pass — the expiry date
of 2026-09-20 is when the answer is most likely to change either way.

## What this card does not establish

- **no advertisement page was opened** — the fields above are the listing's;
- **no dates**: neither posting nor deadline appears on the listing, and
  whether the advertisement pages carry them was not checked;
- **nothing about the rest of the host**, beyond that it exists and must not be
  swept;
- **no adapter is built.** *Reading this board needs the browser, and whether
  that is a shape this repository wants is a decision, not a measurement.*

## No `route:` line — #264, 2026-09-12 (history: the line is back at the top since 2026-09-21)

**This card declared `route: none`, not `route: browser`, and that was the finding then.** The 31
advertisements above were read in a browser on 2026-09-08; since 2026-09-11
the name is `clientHold` at the registrar and NXDOMAIN on every resolver
(section above). *A route to a host that does not resolve is a route to
nothing, and a route to nothing is not a coverage.* The line returns the
day the name comes back and a count is read again.

## 2026-09-14 09:43–09:47 UTC — the name is back, and a tab reads the board

`dig @1.1.1.1` and `@8.8.8.8` both answer NOERROR with two Cloudflare
addresses (172.67.163.152, 104.21.10.145): the `clientHold` of 2026-09-11
is lifted. The declared client still gets the provider's 25-byte 403
(`9ccabba20b9f`, 2026-09-13); a connected tab is served:

```
tab, /offres-demploi/            served, no challenge — 16 <article> (15 ads + 1 company block), pager /offres-demploi/page/2/
tab, /offres-demploi/page/2/     served — 12 ads, no page 3: 27 distinct /offres-emploi/<slug>/ (31 on 2026-09-08)
tab, /offres-emploi/chef-dequipe-psycho-social/   served, 240 KB — WebPage / BreadcrumbList / WebSite / Organization JSON-LD, datePublished 2026-09-11; no JobPosting; four e-mail addresses in the text
```

**`route: browser · 27 · 2026-09-14`** (superseded by the HTTP route above) — the walk's own figure, the site
states none. What a session does from a tab: `/offres-demploi/page/N/`
until the pager ends, the slug of `/offres-emploi/<slug>/` as the key, the
ad's `datePublished` from its WebPage node, the body with every e-mail
address and telephone withheld. No script: the client is refused (#404).
The control of 2026-09-21 in the pilot's deferred tasks can be closed as
done here.

## The control three days on — the declared client is served: the HTTP route is open

```
dig @1.1.1.1 / @8.8.8.8 www.tala-com.com      NOERROR — 104.21.10.145, 172.67.163.152; whois ACTIVE, expiry 2028-09-20
GET https://www.tala-com.com/                        200 ×2 (06:27:04, 06:27:07 UTC) — 349 529 B, the hub's home
GET https://www.tala-com.com/offres-demploi/         200 ×2 (06:30:02, 06:30:04 UTC) — 15 ads, pager → page 2
GET https://www.tala-com.com/offres-demploi/page/2/  200 ×2 (06:32:12, 06:32:14 UTC) — 14 ads, no page 3
```

**Twenty-nine distinct `/offres-emploi/<slug>/` over two pages, to the plain
client, no challenge, no 403** — the reason this card gave for «no script»
(the client is refused, #404) has fallen. The route became `http · 29 · 2026-09-21` with `talacom.py` (section at the top); **#339 was reopened on this reading** — the
script walks `/offres-demploi/page/N/` until the pager ends, keys on the
slug, reads the ad's `datePublished` from its WebPage node, scrubs every
e-mail address and telephone, and prints «N emitted, the site states no
total». The 2026-09-21 control of the deferred tasks is done here.

## 2026-09-23 (#894) — this one compares, and it tells the truth about what it did

**Checked against the defect of #894 and found sound.** The walk ends on a page
that only repeats, *and it says so against the site's own bound*:

```
if page <= last:  note(f"page {page} of {last}: only repeats — the pager promised more; stopped.")
```

**The pager's last page is the site's own figure, and it is compared, not
printed.** A walk that stops early therefore announces itself as a walk that
stopped early — which is the whole of what #894 asks for.

*What it does not do is exit `6` on that shortfall: the run says it, the exit
code does not.* **That is a candidate, not a defect** — the difference from
`empleos_hn.py` is that nothing here asserts a completeness it does not have.
