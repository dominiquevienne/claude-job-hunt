# Board adapter — jobup.ch

Swiss board, French-speaking Switzerland. Same platform as jobs.ch (JobCloud);
the German-language sibling very likely behaves identically but **has not been
verified** — do not assume it.

**Everything below was verified against the live site on 2026-08-26.** Selectors
rot; re-check before trusting an old note.

**It is markedly easier to scan than LinkedIn.** Every result card hydrates, the
standalone ad page renders, and the address carries a postcode. Where LinkedIn
needs coordinate clicks and narrow searches, here plain navigation works.

## Configuration

```yaml
boards:
  jobup:
    enabled: true
    language: "fr"   # optional, "fr" (default) or "de" — affects URL paths only
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → this board is not scanned at all |
| `language` | no | `fr` → `/fr/emplois/…`. Defaults to `fr` |

No profile URL and no account setting: **searching jobup.ch does not require a
login.** An account is only needed to apply.

## Prerequisites

1. **The Claude extension for Chrome** must be installed and connected — this
   drives the user's own browser. Without it, say so and fall back to
   `cover-letter <ad URL>`, which needs no browser.
2. **No login is required to scan.** Say so — it is a genuine difference from
   LinkedIn, and users expect to be asked. A logged-in session simply adds the
   user's saved jobs and application history to the page; it changes nothing
   this adapter reads.

Never fill a credential field, here or anywhere.

## Building a search URL

```
https://www.jobup.ch/fr/emplois/?term=<keywords>
   &location=<town>              # lowercased town or region, e.g. "lausanne"
   &publication-date=30          # 1 | 3 | 7 | 30 (days) — map from search.posted_within
   &benefit=working-from-home    # home-office ads only; set when remote_only
   &page=2                       # 20 results per page, 1-indexed (omit for page 1)
```

Verified: `?term=laravel` → 63 ads; adding `&location=lausanne` → 18;
adding `&benefit=working-from-home` → 4; `&page=2` returns a different first ad.

`search.posted_within` maps as: `week` → `7`, `month` → `30`,
`quarter` → omit the parameter (30 days is jobup's longest option; say so rather
than silently narrowing the user's window).

**Unlike LinkedIn, all 20 cards on a page hydrate**, and pagination works. So a
broad search is fine here: prefer fewer, wider searches plus paging over many
narrow ones.

## The ad id and its URL

The id is a UUID on the card's link element:

```
<a data-cy="job-link" id="vacancy-link-4302da20-da24-449c-af7b-2e7577ce45a8" …>
```

Strip the `vacancy-link-` prefix. Rebuild the canonical URL from the id:

```
https://www.jobup.ch/fr/emplois/detail/<ID>/
```

**Never return a URL from page JS** — the tool blocks any result carrying a
query string. Read the `id` attribute and rebuild.

## Extracting search results

```js
JSON.stringify([...document.querySelectorAll('[data-cy="serp-item"]')].map(c=>{
  const a=c.querySelector('[data-cy="job-link"]');
  const id=a?(a.id||'').replace(/^vacancy-link-/,''):null;
  const p=c.innerText.split('\n').map(s=>s.trim()).filter(Boolean)
          .filter(s=>!/^(Lieu de travail:|Taux d'activité:|Type de contrat:|Offre pertinente \?)$/.test(s));
  return {i:id, q:!!c.querySelector('[data-cy="quick-apply"]'), s:p.join(' · ')};
}))
```

Yields, per card: posting age, title, town, workload, contract type, company,
and `q` = whether it offers *Candidature simplifiée* (in-site apply).

Sample output, verbatim from a real run:

```
{"i":"78a17d04-…","q":false,"s":"Il y a 3 semaines · Développeur·euse full stack senior · Lausanne · 100% · Durée indéterminée · Université de Lausanne - Centre informatique"}
```

## Reading one ad

**The standalone ad page renders fully** — `navigate` to it and read. No
coordinate clicking, no click-through from the results list. This is the single
biggest difference from LinkedIn.

```js
(()=>{const q=s=>(document.querySelector(s)?.innerText||'').replace(/\s+/g,' ').trim();
 const vd=document.querySelector('[data-cy="vacancy-description"]');
 let d='';
 if(vd){const c=vd.cloneNode(true);
   c.querySelectorAll('[data-cy="jobfit-teaser-cta"],[data-cy="vacancy-mood"]').forEach(e=>e.remove());
   d=c.innerText.replace(/\s+/g,' ').trim();}
 return JSON.stringify({
   t:q('[data-cy="vacancy-title"]'),
   pub:q('[data-cy="info-publication"]'),      // exact date, e.g. "18 août 2026"
   wl:q('[data-cy="info-workload"]'),          // "100%"
   ct:q('[data-cy="info-contract"]'),          // "Durée indéterminée"
   ho:q('[data-cy="info-homeoffice"]'),        // "Possible" / absent
   loc:q('[data-cy="info-location-link"]'),    // "Chemin des Plaines 4, 1007 Lausanne"
   sal:q('[data-cy="info-salary_estimate"]'),  // jobup's ESTIMATE — not the employer's
   d:d});})()
```

## Traps

**1. The description container contains jobup's own AI matching widget.**
`[data-cy="vacancy-description"]` opens with a `jobfit-teaser-cta` section —
*"Vous correspondez très bien à ce poste… Voir mon match"*. That is **jobup's
opinion of the fit, not the employer's text.** Left in, it contaminates the ad
text and the scoring reads a third party's guess as a requirement. The snippet
above removes it; do not simplify the snippet back to a plain `innerText`.

**2. `info-salary_estimate` is jobup's estimate, not the ad's salary.** It is
labelled *"Estimation salariale de jobup.ch"* on the page. Never report it to
the user as the advertised range — say it is jobup's estimate, or leave it out.

**3. The posting date is exact, so use it.** `info-publication` gives a real
date where the card gives "Il y a 3 semaines". Prefer the ad page's date in the
ledger.

**4. `info-homeoffice` reads "Possible", not a work mode.** It means home office
is allowed, not that the role is remote. Judge the work mode from the ad text
and the location, per the commute rule in `shared/scoring-rubric.md` — "home
office possible" is a hybrid signal, not a remote one.

## A gift for the Swiss module

`info-location-link` carries the **street, postcode and town**
(`Chemin des Plaines 4, 1007 Lausanne`). That is exactly the field the ORP's
job-room.ch PRE form demands and that LinkedIn ads almost never provide (see
`shared/modules/job-room-ch.md`). **Capture it into `job-ad.md` while the ad is
open** — on this board it is free, and it is the field users most often have to
hunt down weeks later.

## Applying

`apply-button-external` was observed on an ad that hands off to the employer's
own site: treat it like any external ATS — give the user the URL and the files,
do not attempt the form.

Cards can carry a *Candidature simplifiée* badge (`quick-apply`), meaning jobup
has an in-site apply flow. **That flow has not been verified**, so this adapter
documents scanning only. Do not improvise it: an application sent wrong is not
recoverable. Report the ad as a jobup quick-apply, hand the user the URL, and
say the assisted flow is not supported yet.

## Pace

Pace it like a person reading ads. Pagination makes it tempting to pull ten
pages at once; do not. A few dozen page views per run is the shape of a scan
that does not get throttled.
