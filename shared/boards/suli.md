# Board adapter — Suli (`suli.gl`, Greenland): the government's job portal, three culture sitemaps with a key in the slug, and a body behind a path the rules refuse

<!-- verified: 2026-09-12 -->

<!-- hosts: suli.gl, sulisussat.gl -->
<!-- script: suli.py -->
<!-- host-forms: suli.gl -->
<!-- host-forms-basis: read — `suli.py:BASE`, a single literal; `sulisussat.gl` redirects to it (robots.txt and /da/jobs/ both land on suli.gl, canonical https://suli.gl/da/jobs/) · 2026-09-12 -->
<!-- countries: GL -->
<!-- content: measured · 392 distinct advertisement ids in `sitemap.xml?culture=en` (392 job `<loc>` of 528, `<lastmod>` on all 392; 353 slugs carry the first 8 hex of the job GUID, 39 do not — all 39 last modified 2026-07-08), and the `da` and `kl` files hold 392 each with the same 353 keys; `suli.py sitemap` at 11:00 UTC · 2026-09-12 -->
<!-- witness: the other two culture files, read in the same run and printed beside the count — «en 392 · da 392 · kl 392 — equal; 353 keys shared by all three cultures»; the site's own listing count is behind `/api/`, which its rules refuse, so no page states a number this adapter may read · 2026-09-12 -->

**Greenland's public job portal — Naalakkersuisut's, «Namminersorlutik
Oqartussat, Imaneq 4, 3900 Nuuk» in every footer — 392 advertisements in its
sitemap on the day, in Danish, Greenlandic and English as each employer
filled them, and the country's first adapter.** Measured 2026-09-12
10:55–11:01 UTC, every fetch under the declared identity, the guard on the
exact path first. *The Greenland country page named this host and no other, as read by the
pilot on 2026-09-12 when queuing it.*

## Rules, transport, and the one thing they refuse

```
robots.txt        200, 101 B, md5 a66cced60084 — `User-agent: *` · `Allow: /` · `Disallow: /umbraco/` · `Disallow: /api/` · `Sitemap: https://suli.gl/sitemap.xml`; certain: True; no Crawl-delay
identity("/")     http, claude-user (both tokens fall in `*`, both allowed)
GET /             200, 75 078 B, Greenlandic home page (kl is the default culture)
GET /sitemap.xml  200, 512 B — an index of three children, ?culture=en|da|kl, each with a <lastmod> of 10:00 UTC the same day
GET /sitemap.xml?culture=en   200, 528 <loc> — 392 /en/jobs/<slug>/, 86 /en/companies/, 25 /en/apprenticeships/, chrome
GET /en/jobs/     200, 40 820 B — <title>Find job</title>, 0 advertisement links, 0 JobPosting: a React shell
GET /en/jobs/<slug>/          200, ~41 kB — <head> with title, description, og:description; body = <div data-id="react-job-page" data-guid="…">
```

**`/api/` is refused to everyone, and every listing and every advertisement
body is drawn from it.** Read in the site's own bundles (`assets/index-*.js`
→ `job-page-*.js` → `jobHandler-*.js`, all on open paths): the job page's
data call is `/api/job-editor/job/<guid>`; the listing's is under `/api/`
too. **Nothing in this repository calls those paths — not the adapter, not a
browser route.** A refusal written in the rules is an intention, and it is
honoured by every route, browser included (`shared/robots-policy.md`). *This is not a
transport refusal with open rules — the transport answers 200 everywhere —
so it is not a #222 candidate either: the rules themselves draw the line.*

What the rules leave open is what the adapter reads: the sitemap, and the
`<head>` of a page.

## The id — in the slug for 353, in the page for all

```
/en/jobs/regnskabschef-90b35708/     <div data-id="react-job-page" data-guid="90b35708-9d35-424c-bfae-2f502b42d5b5">
/da/jobs/regnskabschef-90b35708/     same key, Danish slug
/kl/suliffissat-jobs/regnskabschef-90b35708/   same key, Greenlandic section name
```

**353 of the 392 slugs end in eight hex digits, and those digits are the
first block of the job's GUID** — verified on the four keyed pages read
(`b498d8fc`, `c664f3d5`, `90b35708`, `4501e40f`), slug key = GUID prefix on
all four; the three unkeyed pages read carry GUIDs (`5534cb82` twice — the
same job under its English and Danish slugs — and `d603af17`) that appear
nowhere in their slugs. So the id is read from the sitemap without opening the page, and
it is the same across the three cultures: the adapter emits `id: 90b35708`,
`key: guid8`, and the `ad` command emits the full GUID beside it.

**The other 39 carry no key — `administrative-assistant`, `nurse`,
`helena-testjob`, `softwareudvikler-web-test`, `pilote` — and all 39 have
`<lastmod>` 2026-07-08, the oldest date in the file.** Their heads read like
placeholders (`Support the office team` / `Handle documents, schedules and
citizen requests.`; «Arctictech», a SaaS shop in Nuuk, on the one whose
Danish slug ends in `-test`). *That is a reading, not a measurement: nothing
on an open path says which of the 39 are live.* They are emitted with the
slug as id, `key: slug`, and counted apart on stderr — never dropped, and the
ledger id for one of them is culture-specific (its slug is), which the
adapter's row says with `culture`.

**Every page also carries a second GUID, `e468b033-…`, before the island —
the page node's, once on each of the seven pages read.** The adapter anchors on
`data-id="react-job-page"`; a pattern on `data-guid` alone would emit the
node's GUID as every advertisement's id, and the mutation bench holds that
case red.

## The count, and its second view

```
528 <loc> in https://suli.gl/sitemap.xml?culture=en, 392 in the job section, **392 distinct id(s)**: 353 carry the site's key in the slug (8 hex, the first block of the job GUID) and 39 do not — those 39 are last modified on 2026-07-08. <lastmod> present on 392 of 392.
The site states no count on any path these rules open — the listing is drawn from /api/, which robots.txt refuses; the second view is the other culture files.
en 392 · da 392 · kl 392 — equal; 353 keys shared by all three cultures, one store under three sets of slugs.
```

*Three files, one store: the same 353 keys appear in all three, and the
39 unkeyed slugs are translated per culture (201 slugs shared en/da, 365
en/kl — the Greenlandic file reuses the English slug where no Greenlandic
one was written).* When the files part, the adapter says so and names the
keys shared by the files it read. `--no-cross-cultures` makes it two
requests instead of four.

`<lastmod>` on every job URL — 2026-07-08 to 2026-09-12, 109 in September,
64 in August, 180 in July (the 39 unkeyed among them). **The day's youngest
is `regnskabschef-90b35708`, 2026-09-12; the file moves daily** (the index's
own `<lastmod>` was 10:00 UTC that morning).

## The advertisement — a head, and a body not read

```
GET /en/jobs/regnskabschef-90b35708/    200
<title>Regnskabschef</title>
<meta name="description" content="fagligt stærk Regnskabschef" />           <- the employer's headline
<meta property="og:description" content="Vil du være med til at udvikle økonomifunktionen i en af Grønlands førende installationsvirksomheder? VVS & EL Firmaet A/S søger en erfaren og fagligt stærk…">
<meta name="culture" content="en" />  <meta name="pageType" content="jobPage" />
```

What `ad` emits: `id`, `key`, `guid`, `slug`, `url`, `culture`, `title`,
`headline`, `description_snippet` (og:description, ~150 characters, cut by
the site — `description_truncated: true` when it ends in «…»),
`page_culture`. **Employer and location are not in the head**: the employer
appears in the snippet's prose when it does (`VVS & EL Firmaet A/S`,
`Permagreen`, `Kommuneqarfik Sermersooq`) and is not extracted — a name
pulled from a sentence is a guess. **The `/en/` page serves whichever
language the employer filled** — `siunnersorti-b498d8fc` on `/en/` is
Greenlandic throughout — so `language` is `null`, not detected.

*The body — description, deadline, hours, contact, `reservedForGreenlandic-
Applicants`, the fields `jobHandler-*.js` names — is one `GET
/api/job-editor/job/<guid>` away, and that path is refused. The adapter
prints the route it did not take on every `ad` run.*

## Configuration

```yaml
boards:
  suli:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no browser. `sitemap` is four requests (index, one culture
file, the other two); `--no-cross-cultures` makes it two. `ad` is one.

## What is not established

- **Which of the 39 unkeyed advertisements are live** — their slugs and
  heads read as a launch-day population, and no open path says more.
- **What `/en/companies/` (86) and `/en/apprenticeships/` (25) hold** — not
  read; the apprenticeship section has its own React island
  (`react-apprenticeship-page`) and may be a second inventory.
- **The site's own count** — behind `/api/`; not readable by these rules.
- **Whether the sitemap lists closed advertisements** — `<lastmod>` is a
  modification date, and a page that has gone returns 404 → exit 3.

## 2026-09-12 — shipped

`suli.py sitemap`: 392 distinct (353 keyed, 39 unkeyed), en · da · kl equal
at 392, 353 keys shared. `ad` on `regnskabschef-90b35708` and
`administrative-assistant`: head fields above, GUID prefix = slug key on the
first, slug as id on the second. Seven mutations on a detached worktree
(`python3 -B`), seven red, each on the test written for it.
