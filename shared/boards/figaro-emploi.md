# Board adapter — Figaro Emploi (ex-Keljob)

A large French generalist board — **244 815 ads in its own sitemap** — run by
Figaro Classifieds, the group that also owns `cadremploi.md`.

**This is a browser adapter.** It runs in the user's own Chrome, in their own
session, like `linkedin.md`, `jobup.md`, `jobs-ch.md`, `indeed.md`,
`cadremploi.md` and `softy.md`. There is no script in
`skills/job-scan/scripts/` for it, and there cannot be one.

**Everything here was verified by driving the live site on 2026-08-31.**

## Ask for Keljob, get this

`keljob.com` is gone, and it shut down honestly — worth saying, having just
written the opposite case up under *Investigated and closed — Monster*:

| Asked | Answer |
| :-- | :-- |
| `keljob.com/` | `301` → `emploi.lefigaro.fr/#home` |
| `keljob.com/recherche` | `301` → `emploi.lefigaro.fr/recherche/offres-emploi#offers` |
| `keljob.com/emploi/recherche` | **`410 Gone`** |
| anything else | `404`, on a page titled *"Keljob c'est fini !"* |

Live paths redirect to their successor, retired ones return `410` rather than a
soft 404, and the page says so in words. **If a user asks for Keljob, this is
the adapter to offer them** — and an old `keljob.com` ad link is genuinely dead,
not silently repointed at a home page.

## Why there is no no-browser adapter

Cloudflare answers **HTTP 403 to every scripted request** on
`emploi.lefigaro.fr`, with its *"Sorry, you have been blocked"* page — the
listing pages, the ad pages, `/sitemap/fem/*`, and **`robots.txt` itself**.

Only `https://emploi.lefigaro.fr/sitemap/` (the editorial index) answers `200`
to a script, and it contains no ads.

Same edge, same group, same conclusion as `cadremploi.md`: a refusal at the
edge, not a rule to interpret. **Do not add a `figaroemploi.py`.** The same
pages load normally in the user's Chrome, which is the only route this adapter
takes.

**One consequence that makes this adapter cheap:** once *any* page of the origin
is open in the tab, `fetch()` from that page carries the browser's Cloudflare
clearance and returns fully server-rendered HTML (`data-n-head-ssr`,
`window.__NUXT__`). So the whole sweep — every listing page and every ad page —
runs as `fetch()` calls from one open tab. **Do not navigate once per ad.**

## Prerequisites

The Claude extension connected to the user's Chrome. **No login is needed** —
every measurement below was taken from a logged-out session. If a challenge
ever appears, **the user solves it, never the plugin**, exactly as on
`indeed.md`.

## What robots.txt disallows, and why the sweep never touches it

Read in the browser on 2026-08-31, because a script cannot read it. The
`User-Agent: *` group closes, among others:

```
Disallow: /recherche/offres-emploi          ← the search results page
Disallow: /recherche/offres-emploi?q=*      ← and again, with its query
Disallow: /services/search/jobs             ← the JSON search endpoint
Disallow: /services/*                       ← the whole API surface
Disallow: /entreprises/*                    ← company pages
Disallow: /ai-agent
Disallow: /_nuxt/*
```

**The search is disallowed twice over — the page and the API behind it.** This
adapter never requests either. What it uses instead is the browse hierarchy
under `/offres-emploi/`, which is **not** disallowed for `*` (only for
`Applebot`), and which the site advertises in its own sitemaps. Discovery by
the paths built for readers, not by the endpoint built for the search box.

## Building a search

Five allowed entry points, all counted from the site's own sitemaps:

| Path | How many exist | Example |
| :-- | :-- | :-- |
| `/offres-emploi/r/<region>` | 18 | `/r/fr-ara` — Auvergne-Rhône-Alpes |
| `/offres-emploi/d/fr-<dd>` | 96 | `/d/fr-69` — Rhône |
| `/offres-emploi/v/<ville>-<cp>` | 2 883 | `/v/lyon-69000` |
| **`/offres-emploi/d/fr-<dd>/m/<metier>`** | **28 855** | `/d/fr-69/m/aide-comptable` |
| `/offres-emploi/v/<ville>-<cp>/m/<metier>` | 9 623 | `/v/agen-47000/m/aide-comptable` |

**Department × métier is the one to reach for** — it is the finest allowed
narrowing and the largest set. Pagination is `?page=<n>`, 30 ads a page, on
every one of them:

```
https://emploi.lefigaro.fr/offres-emploi/d/fr-69/m/aide-comptable?page=2
```

The métier segment is URL-encoded and may contain spaces and accents
(`/d/fr-69/m/%C3%A9lectricien%20automobile`). **Take it from the sitemap rather
than inventing it** — see trap 2.

### `/offres-emploi/m/<metier>` is a trap, not a sixth entry point

The 3 356 bare-métier pages look like the others and are listed in the same
sitemap family. They are **client-side redirects into the disallowed search**:

```
/offres-emploi/m/developpeur
  → /recherche/offres-emploi?q=cT1kZXZlbG9wcGV1cg%3D%3D     ← Disallow'd
                               └ base64 of "q=developpeur"
```

The redirect happens after hydration, so a fetch of the path looks innocent
while a real page load lands on the closed door. **Never request
`/offres-emploi/m/…` without a `/d/` or `/v/` prefix.**

## Configuration

```yaml
boards:
  figaro-emploi:
    enabled: true
    searches:
      - { departement: "69", metier: "aide-comptable" }
      - { ville: "lyon-69000" }
      - { departement: "01" }
    pages: 4
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `searches` | yes | Each entry needs `departement`, `ville` **or** `region` |
| `departement` | one of three | Two characters, written `69` — the URL is `/d/fr-69` |
| `ville` | one of three | **`<slug>-<postcode>`**, e.g. `lyon-69000` |
| `region` | one of three | `fr-ara`, `fr-bre`… 18 of them |
| `metier` | no | Only with `departement` or `ville`. Never alone |
| `pages` | no | 30 ads a page |

## What a card yields

Cards are `a.search-result-job-card` on any listing page. Measured across 150
ads in Lyon and the Rhône, and **every field below was present on every card**:

| Field | Where | Example |
| :-- | :-- | :-- |
| `id` | `href` — `/offres-emploi/<id>` | `156545550585986984` |
| `title` | `.search-result-job-card__title` | Technicien d'installation audiovisuel |
| `company` | `.legal-container` | LIDL, EOSIUM, Aquila Rh |
| `location` | 1st `span.tag` | Lyon, *Lyon - 3Ème Arrondissement* |
| `contract` | 2nd `span.tag` | **CDI, CDD, Intérim, Apprentissage / Alternance, Indépendant / Freelance / Auto entrepreneur, Franchisé** |
| `salary` | 3rd `span.tag`, **when there is one** | `28K € à 35K € annuels`, `1932 € mensuels` |
| `teaser` | `.search-result-job-card__description` | first ~200 characters |
| `published` | `time[datetime]` | `2026-08-24T00:00:00Z` |

**The employer is always named.** Contract vocabulary over those 150 ads: CDI
109, Indépendant 20, Intérim 10, CDD 5, Apprentissage 5, Franchisé 1.

**A salary is on roughly a third of ads** — 11 of 30 on one page, 7 of 16 on
another. That is far more than most boards here, and it comes from the card,
never from the ad's structured data (trap 4).

The real total is in the `<h1>`: *"314 offres d'emploi Aide-comptable Rhône
(69), Rhône"*. Read it there and compare it with what you collected.

## The ad id and its URL

The id is an 18-digit number with **no slug attached**:

```
https://emploi.lefigaro.fr/offres-emploi/156545550585986984
```

In the ledger: `figaro-emploi:<id>`.

The ad page carries a full JSON-LD `JobPosting` — `title`, `description`
(4 365 characters on the ad measured), `datePosted`, `employmentType`,
`jobLocation` with `addressLocality` / `addressRegion` / `postalCode`,
`hiringOrganization.name`, `qualifications`, `salaryCurrency`. Read the
description from there. Read the contract and the salary from the card.

## Traps

**1. A one-page result never empties — it repeats forever.** A search with 30
ads or fewer serves the *same* page for every `?page=` value. Measured on
`/d/fr-69/m/échafaudeur`, a single ad: pages 1, 2, 3, 5 and **50** all returned
that one ad. A sweep that stops "when a page comes back empty" **never
terminates** here.

Larger results do stop cleanly, and stop *exactly*: Lyon announces 7 619, pages
1–253 gave 30 each, page 254 gave 29 — 7 619 — and page 255 gave zero. Rhône
aide-comptable announces 314, page 11 gave 14, page 12 gave zero. **No cap, no
ceiling, no silent truncation** — which is rare enough in this repository to be
worth saying plainly.

**So the rule is: stop when a page yields no id you have not already seen** —
never "stop when the page is empty".

**2. The sitemap's `lastmod` is the build time, not the ad's date.** All 30 000
entries in `online-job-postings-1.xml` carry the **same** timestamp
(`2026-08-31T06:01:27Z`), and it changes wholesale when the file is rebuilt.
It says nothing about any ad. The real date is the card's `time[datetime]`, or
the ad's `datePosted`.

*(And the sitemap is only useful for the métier and place vocabularies. It
holds 244 815 ad URLs and nothing else — no title, no company, no location —
so there is nothing to filter on before fetching. Discovery is allowed; useful
discovery goes through the browse paths above.)*

**3. `validThrough` is `datePosted + 30 days`, on every ad.** Measured on 14 of
14. It is a formula, exactly like `hellowork.md` (+30) and `meteojob.md` (+60),
and it is not an expiry. Do not put it in the ledger as one. `emploi-territorial.md`
remains the board here that publishes a real deadline.

**4. The structured data is emptier than the page it sits on.** This inverts
the rule every other adapter here follows.

- **`baseSalary` is a hollow shell.** On all 14 ads measured it is a
  well-formed `MonetaryAmount` whose `value` is a `QuantitativeValue` carrying
  **no `value`, `minValue` or `maxValue`**. Meanwhile the listing card for the
  same ad reads *"50K € à 200K € annuels"*. A reader that trusts JSON-LD gets a
  salary object, parses it successfully, and records nothing.
- **`employmentType` flattens the distinction that matters most in France.**
  Measured, card label → JSON-LD value:

  | Card | JSON-LD |
  | :-- | :-- |
  | **CDI** | `FULL_TIME` |
  | **CDD** | `FULL_TIME` |
  | Intérim | `TEMPORARY` |
  | Apprentissage / Alternance | `INTERN` |
  | Indépendant / Freelance | `CONTRACTOR` |
  | Franchisé | `CONTRACTOR` |

  CDI and CDD arrive as the same value; so do freelance and franchise. And an
  apprenticeship is not an internship in French law. **Take the contract from
  the card's second `span.tag`.**

**5. The Vue build hashes look like selectors and are not.** Every element
carries `data-v-96e3c8ea` / `data-v-bb2e0b7c` — Vue scoped-style attributes
that change with each deploy. The `search-result-job-card__*` class names are
the stable handles. Same lesson as the Tailwind utility classes elsewhere:
**a name the framework generated is not a name.**

Related, and measured the hard way: the anchor carries a `total="30"`
attribute. That is the page size. The total is in the `<h1>`.

**6. Two date formats in one field, and the `ld+json` tag has attributes before
`type`.** `time[datetime]` came back both as `2026-08-24T00:00:00Z` and as
`2026-08-31T01:29:56.50915+02:00` — different precision, different zone, same
field. And the ad page's script tag is
`<script data-n-head="ssr" type="application/ld+json">`, so a regex anchored on
`<script type=` matches nothing and reports *"this ad has no structured data"*
on every ad. Both were found by writing the naive version first.

## Applying

The apply flow is the employer's or the board's, behind
`/offres-emploi/redirect/*` — which robots.txt disallows, and which this plugin
does not follow. Many cards carry a *"Candidature rapide"* badge, which needs an
account. **The plugin does not create accounts and does not fill credential
fields.** Hand the user the ad URL with their documents.

## Pace, and the note on access

One request per page of 30, plus one per ad whose description is read. A
department × métier search is a handful of pages; a whole department is
hundreds, and a whole region is thousands — narrow with `metier` rather than
sweeping `region`, and the run should say how much of the `<h1>` total it
actually collected.

Everything is fetched from the browse paths the site publishes in its own
sitemaps, in the user's own browser, at the volume one person's job search
needs. The search page and the search API stay untouched, because the site
asked.
