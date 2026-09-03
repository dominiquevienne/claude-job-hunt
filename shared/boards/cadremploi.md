# Board adapter — cadremploi.fr

<!-- verified: 2026-09-02 -->

<!-- hosts: www.cadremploi.fr -->
**Re-tested 2026-09-02: the constraint holds.** `cadremploi.fr/robots.txt` still answers **HTTP 403** with 4 574 bytes of `text/html` to a scripted request — the rules themselves are unreadable to anything but a browser.

The reference board for French **cadres** alongside the APEC — one of the oldest,
now part of the HelloWork group.

**This is a browser adapter.** It runs in the user's own Chrome, in their own
session, like `linkedin.md`, `jobup.md`, `jobs-ch.md` and `indeed.md`. There is
no script in `skills/job-scan/scripts/` for it, and there cannot be one.

**Everything here was verified by driving the live site on 2026-08-30.**

## Why there is no no-browser adapter

Cadremploi is behind Cloudflare bot protection that answers **HTTP 403 to every
scripted request** — `/`, `/sitemap.xml`, and `robots.txt` itself, with
Cloudflare's *"Sorry, you have been blocked"* page rather than the site's.

That is a refusal at the edge, not a rule to interpret, and getting past it
would mean defeating bot detection — which this plugin does not do. **Do not
add a `cadremploi.py`.** The same pages load normally in the user's Chrome,
which is the only route this adapter takes.

## Prerequisites

The Claude extension connected to the user's Chrome. **No login is needed to
scan** — every measurement below was taken from a logged-out session. If a
challenge ever appears, **the user solves it, never the plugin**, exactly as on
`indeed.md`.

## Configuration

```yaml
boards:
  cadremploi:
    enabled: true
    searches:
      - { motscles: "data engineer", ville: "paris-75" }
      - { motscles: "ingénieur",     ville: "lyon-69" }
    pages: 3
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `searches` | yes | `motscles` free text, `ville` as **`<slug>-<postcode>`** |
| `pages` | no | 30 ads per page |

`ville` is not optional in practice — see trap 1.

## Building a search

```
https://www.cadremploi.fr/emploi/liste_offres?motscles=<mots>&ville=<slug>-<cp>&page=<n>
```

| `search.*` config | Parameter | Verified |
| :-- | :-- | :-- |
| `keywords` | `motscles` | `data engineer` → 19 nationally, 8 around Paris |
| `location` | `ville` — `paris-75`, `lyon-69` | Applies a **+20 km radius**, stated in the page heading |
| pagination | `page` | Page 2 served 30 ads with **zero overlap** with page 1 |
| `posted_within` | — | Not supported; the card states an age in words |

**Get `ville` from the site's own field, not from a guess.** Type the town into
the location box and read the slug back out of the URL — that is how
`paris-75` was established, and how trap 1 was found.

## What a card yields

Measured across one full 30-card page:

| Field | Selector | Filled |
| :-- | :-- | :-- |
| `id` | `a[href*="offreId"]` → the `offreId` value | 30/30 |
| `title` | `.job-title` | 30/30 |
| `company` | `.company-name` | 30/30 |
| `location` · `contract` · `salary` | three `p.text-grey-800` | 30/30 · 30/30 · **20/30** |
| `teaser` | `.job-posting-snippet` | 30/30 |
| `posted_age` | `.text-pale-grey-40` | 30/30 |

The three `p.text-grey-800` are **not reliably ordered** — a card with no salary
has two. Identify them by content: the one carrying `€` is the pay, the one
matching `CDI|CDD|Intérim|Stage|Alternance|Freelance` is the contract, what
remains is the location. This extractor was run against the live page:

```js
const txt = e => e ? e.textContent.replace(/\s+/g,' ').trim() : null;
[...document.querySelectorAll('.job-posting-card')].map(c => {
  const a  = c.querySelector('a[href*="offreId"]');
  const id = a ? (a.getAttribute('href').split('offreId=')[1]||'').split('&')[0] : null;
  const t  = [...c.querySelectorAll('p.text-grey-800')].map(txt);
  const salary   = t.find(x => /[€kK]/.test(x) && /\d/.test(x)) || null;
  const contract = t.find(x => /^(CDI|CDD|Int[ée]rim|Stage|Alternance|Freelance|Ind[ée]pendant)/i.test(x)) || null;
  return { id,
    url: 'https://www.cadremploi.fr/emploi/detail_offre?offreId=' + id,
    title: txt(c.querySelector('.job-title')),
    company: txt(c.querySelector('.company-name')),
    location: t.find(x => x !== salary && x !== contract) || null,
    contract, salary,
    teaser: txt(c.querySelector('.job-posting-snippet')),
    posted_age: txt(c.querySelector('.text-pale-grey-40')) };
});
```

## The ad id and its URL

The id is an 18-digit `offreId`:

```
https://www.cadremploi.fr/emploi/detail_offre?offreId=<id>
```

In the ledger: `cadremploi:<id>`.

The listing's `ld+json` carries a `BreadcrumbList` and an `ItemList` of 30 ad
URLs — useful as a cross-check on the ids, but it holds **no `JobPosting`**, so
it adds no fields.

## Traps

**1. `localites=75` is accepted and does nothing.** It survives in the URL, the
location box stays **empty**, and the results are unfiltered — a Paris search
returned ads in Lille and Darmstadt. The working parameter is `ville=paris-75`.
This is the trap that cost the most to find, because the URL looks filtered.

**2. The card list drifts out of the search area, with nothing marking where.**
On `data engineer` + `paris-75`, the page heading said **8 offres … Paris (75)
+20km** and the DOM held **30 cards**: the first 8 were Paris and Massy, and the
rest ran out through Bezons, Rungis, Meaux and on to **Lille**, 200 km away. No
separator, no heading, no different class — all 30 sit in the same
`.list-container`.

**So filter the cards by the location the user asked for**, and do not trust
position. Trimming to the stated count happens to work here, but see trap 3.

**3. The stated count is not the size of the result set, and it is only on page
1.** `ingénieur` + `paris-75` announced **248 offres** — and page 9 still served
30 ads, all in Paris, with the pagination offering a page **65**. So 248 does
not bound anything. On page 2 and beyond there is **no `h1` at all**, so the
count is not even available to check against.

What the count is exactly was not established. Treat it as a label, never as an
arithmetic input: **do not compute a page budget from it**, and stop on a page
that returns nothing new instead.

**4. Pagination buttons carry no `href`** — they are Vue handlers. But clicking
one writes `page=N` into the URL, so once that is known **pages are navigable
directly** and no clicking is needed. Verified: page 2 shared **zero** ids with
page 1.

**5. Every element carries a Vue build hash** — `data-v-6a325289` — which
changes on each front-end deploy. **Never anchor a selector on it.** The classes
used above (`job-posting-card`, `company-name`, `job-title`,
`job-posting-snippet`) are semantic and were stable across the session.

**6. Salary is absent on a third of ads** — 20 of 30. That is normal, not a
parse failure; the card simply has two tags instead of three, which is why the
extractor identifies tags by content.

**7. Much of this board is recruitment agencies and job-board resellers.**
One 30-card page named FREE-WORK repeatedly, alongside LHH, MERCATO DE L'EMPLOI
and FIGARO CLASSIFIEDS. The employer field is filled, but what it names is often
the intermediary, not the workplace — read it as on `randstad.md` and
`michaelpage.md`.

## Applying

There is an in-site *"Candidature rapide"* on many cards. **It is not driven**:
no assisted apply is implemented here, and the plugin does not create accounts
and does not fill credential fields. Hand the user the ad URL with their
documents.

## Pace, and the note on access

One page load per page of results, in the user's own browser, at reading speed.
This adapter opens pages a person could open, in their own session, for their
own job search — and it does not touch the paths Cloudflare closes to scripts.

A `403` or a challenge in the browser is a **stop**: report it and hand it to
the user. Never retry it in a loop, and never move this board to a script to get
around it.
