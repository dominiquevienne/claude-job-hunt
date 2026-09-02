# Board adapter — jobup.ch

Swiss board, French-speaking Switzerland. Same platform as jobs.ch (JobCloud).
**The sibling has now been verified** (`jobs-ch.md`, 2026-08-28): same DOM, same
selectors, and — the part that matters — **the same ad ids**. An ad on both
boards carries one UUID, so `jobup:<uuid>` and `jobs.ch:<uuid>` are the same
posting. Check the ledger for the other prefix before writing a row.

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

1. **The sweep does not need the browser.** This file said the Chrome
   extension was a prerequisite and that a user without it had no jobup sweep
   at all. **That was wrong**, and it cost the two largest Swiss boards to
   every user without the extension. Measured 2026-09-02, plain `curl`, no
   cookie and no session: **the listing and 5 of 5 ads answered 200 in
   `text/html`**, and every ad carried a full `JobPosting` — see *The
   plain-HTTP route* below. Drive the browser if it is there; do not require
   it.
2. **The application flow is a separate question and it has not been
   instructed.** What was measured is reading. If applying needs the browser,
   this adapter splits like `wttj.md` — an HTTP discovery half and a browser
   apply half — rather than reverting to a browser prerequisite for
   everything.
3. **No login is required to scan.** Say so — it is a genuine difference from
   LinkedIn, and users expect to be asked. A logged-in session simply adds the
   user's saved jobs and application history to the page; it changes nothing
   this adapter reads.

Never fill a credential field, here or anywhere.

## The plain-HTTP route

**Measured 2026-09-02** on `https://www.jobup.ch/fr/emplois/?term=developpeur`
and five ads drawn from it, with `curl`, `Accept-Encoding: identity`, no
cookie:

| What | Result |
| :-- | :-- |
| Listing page | **200**, `text/html`, 510 KB |
| Ads | **5 of 5 → 200**, 297–353 KB each |
| `application/ld+json` `JobPosting` | **5 of 5** |
| `description` inside it | **2 547 – 4 389 characters**, the ad's own text |
| `hiringOrganization.name` | 5 of 5 |

**And the listing carries a complete JSON record per card**, not merely a
title: `id` (the UUID this board deduplicates on), `title`, `place`, and a
`locations[]` array with `city`, `cantonCode`, `postalCode`, `street`,
`latitude`/`longitude`, plus `publicationDate`, `employmentGrades` (the 80–100%
band), `isActive` and `listingTags` (`quickApply`, `easyApply`). Twenty cards a
page.

**Two traps, both measured, both of the `#67` family — a field that is present
and false:**

1. **`baseSalary` is a shell.** Served as
   `{"@type":"MonetaryAmount","currency":"CHF","value":{"@type":"QuantitativeValue"}}`
   — the block on **5 of 5** ads, an amount on **0 of them** in this sample
   (an independent run found 3 of 12 across both boards). **Counting the key
   gives 100%; counting the value gives a quarter or less.** Read the amount,
   never the presence.
2. **The ad page has no usable location.** `jobLocation.address.addressLocality`
   was empty on **5 of 5**. The geography is on the listing, in `locations[]`.
   An adapter that reads only ad pages loses the city — so the sweep goes
   through the listing, which is open anyway.

**Prefer `ld+json` to the DOM selectors below.** Both work; the structured
block does not move when the site is redesigned, and `[data-cy="…"]` does. The
selectors stay documented because the browser path still uses them and because
they are what a human debugging a page will see.

**What was not measured — do not extrapolate.** Rate limiting under a real
sweep (this was ~12 requests at one per second), the behaviour of an expired
ad, whether the `ld+json` `description` is character-for-character what the
page shows, and whether other parasitic content rides in the payload — the AI
matching widget documented in *Traps* below does not appear in it, which is
one absence rather than a clean bill.

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

**The accent in `location` is load-bearing, and dropping it returns zero
silently** — HTTP `200`, a normal page, no error, no ads. On `term=php`:
`Genève` and `Genf` both return 11, **`geneve` returns 0**; `Neuchâtel` returns
1, **`neuchatel` returns 0**. Case is irrelevant, the diacritic is not, and
exonyms are fine. **Pass the town exactly as the user wrote it** — never
lowercase-and-strip it — and if a location returns zero, retry once with the
accented form before reporting an empty board. Measured 2026-08-28; the same
trap applies to jobs.ch.

**Unlike LinkedIn, every card on a page hydrates**, and pagination works. So a
broad search is fine here: prefer fewer, wider searches plus paging over many
narrow ones.

**A page holds more cards than results.** `term=laravel` returned **21**
`serp-item` cards, one of them carrying `data-cy="recommended"` — a paid
placement sitting on top of the 20 organic results. It is **not** evidence the
ad matches the search, and on jobs.ch such cards were observed repeating across
pages. Capture the flag rather than the count: add
`promo:!!c.querySelector('[data-cy="recommended"]')` to the card map, and never
compute "how many results did I read" from the number of cards. Measured
2026-08-28.

## The ad id and its URL

The id is a UUID on the card's link element:

```
<a data-cy="job-link" id="vacancy-link-4302da20-da24-449c-af7b-2e7577ce45a8" …>
```

Strip the `vacancy-link-` prefix. In the ledger it is recorded **prefixed**, as
`jobup:<ID>`. Rebuild the canonical URL from the bare id:

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

## A second gift: the employer's own posting URL

The ad's detail page carries the vacancy JSON, and that JSON names the
employer's own ATS posting:

```
"externalUrl":"https://jobs.<employer>.ch/job/<slug>/<id>-fr_FR"
"isActive":true
```

**Harvest it while the ad is open**, into `Note` on the ledger row. It plays the
same role as HiringCafe's `apply_url` (`shared/pipeline-format.md`): the jobup id
identifies the ad *on jobup*, the `externalUrl` identifies the same posting on
the employer's ATS — the only key that survives the crossing to another board,
and the one step 1b needs to ask whether the ad is still open.

It matters most where the requisition id is otherwise unguessable. On SAP
SuccessFactors it is the *only* route to a checkable URL, because that host's
own search page renders nothing — see `shared/ats-open-check.md`.

Read it out of the page source rather than the DOM, and **anchor the match on
`applicationOptions`**:

```js
(()=>{const m=document.documentElement.innerHTML
        .match(/"applicationOptions":\{[^{}]*?"externalUrl":"([^"]*)"/);
 return m&&m[1]?m[1].replace(/\\u002F/g,'/'):'';})()
```

**The anchor is not decoration.** A detail page contains **four or five**
`"externalUrl"` keys, most of them empty strings belonging to other blocks, so an
unanchored `/"externalUrl":"([^"]+)"/` matches whichever one is non-empty first
— which is the ad's own only by luck. Corrected 2026-08-28, after counting the
occurrences; on the seven ads measured across both hosts the two forms agreed,
and the anchored one is the one that stays right.

**An empty string is the normal case**, meaning the ad applies in-site — treat it
as absent, not as a failure.

**Observed 2026-08-27** on a BCV ad, alongside `"isActive":true` and a rendered
*Postuler* button — two independent corroborations of the same fact. A
`data-cy` selector for this field was **not** established; the source match is
what was run.

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
