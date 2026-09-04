# Board adapter — jobs.ch

<!-- script: jobup.py -->
<!-- verified: 2026-09-02 -->
<!-- countries: CH -->

Swiss board, German-speaking Switzerland. **Same platform as jobup.ch
(JobCloud)**, and this file exists because "same platform" turned out to mean
*the same DOM and the same ad ids* — which is a much stronger statement than it
sounds, and it changes how the ledger has to treat both boards.

**Everything below was verified against the live site on 2026-08-28.** Selectors
rot; re-check before trusting an old note.

## The finding that governs everything else: the id is shared with jobup

**An ad published on both boards carries the same UUID on both.** Verified on two
unrelated Romandie ads:

| UUID | jobs.ch | jobup.ch |
| :-- | :-- | :-- |
| `a9ed2520-…` | `200` — *Développeur C# / Vue.js Full Stack Senior (H/F)* | `200` — same title |
| `80dba334-…` | `200` — *Senior Cloud Platform Engineer*, SICPA SA | `200` — *Ingénieur principal plateforme cloud*, SICPA SA |

Read the second row twice. **The same posting, the same id, two different
titles** — jobup serves a machine translation. So the fuzzy employer-name check
in `skills/job-scan/SKILL.md` would not catch this duplicate, and a title
comparison would actively disagree. **The UUID is the only thing that matches.**

**One precision, added 2026-09-02: that is true when the source language
differs, not systematically.** UUID `203ad37f-744b-4828-8b0d-a89f583b320b`
surfaced in both listings and was pulled from both sides: **identical title, a
description identical to the character (2 572), the same employer and the same
timestamp to the second** — only the contract-type label was localised
(`Festanstellung` / `Durée indéterminée`). A French-origin ad is served
unchanged on both boards; jobup translates when the source is German. **The
rule does not change — deduplicate on the UUID — but the reason is "titles are
unreliable", not "titles are actively in disagreement".** The strong claim held
for SICPA and would have been wrong here.

Not every ad is on both: German-region ads (Bern, Pratteln, Zürich) answered
`404` on jobup, and one Lausanne ad answered `404` too. So the two boards
overlap, neither contains the other.

**Ledger rule.** Record ads from here as `jobs.ch:<uuid>` — the prefix
`job-room.md` already emits in its `duplicate_of` field, so it is settled, not
invented. **Before writing a `jobs.ch:<uuid>` row, look for `jobup:<uuid>` in the
ledger, and vice versa.** Same UUID means the same posting, with the certainty
`shared/pipeline-format.md` reserves for exact keys: discard the new row naming
the one it duplicates, and do not fall back to the fuzzy check.

## It does not replace jobup, and it is not a superset

Nationally it is roughly three times the board. In Romandie it is the thinner
one. Same query, same day:

| Query | jobs.ch | jobup.ch |
| :-- | --: | --: |
| `term=laravel` | **186** | 61 |
| `term=php` | **96** | 32 |
| `term=laravel&location=lausanne` | 6 | **18** |
| `term=php&location=lausanne` | 6 | **11** |
| `term=php&location=Genève` | 3 | **11** |

**A Romandie user who switches from jobup to jobs.ch loses ads.** Enable both,
or keep jobup if only one. The dedup above is what makes running both safe.

## Configuration

```yaml
boards:
  jobs-ch:
    enabled: true
    language: "de"   # optional, "de" (default) or "en" — affects URL paths only
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → this board is not scanned at all |
| `language` | no | `de` → `/de/stellenangebote/`. Defaults to `de` |

**There is no French on jobs.ch.** `/fr/emplois/` and `/fr/offres-emploi/` both
answer `404` — French-language JobCloud is jobup, a different host. Only
`/de/stellenangebote/` and `/en/vacancies/` exist. Selectors below were verified
on `de`; `en` answers `200` and was not otherwise checked.

No profile URL and no account setting: **searching jobs.ch does not require a
login.** An account is only needed to apply — and to see the salary estimate,
see trap 3.

## Prerequisites

1. **The sweep does not need the browser**, and this file said it did. Same
   correction as `jobup.md`, same date, same method: measured 2026-09-02 with
   plain `curl`, no cookie and no session, the listing
   `https://www.jobs.ch/de/stellenangebote/?term=entwickler` answered **200,
   `text/html`, 552 KB**, and **5 of 5 ads drawn from it answered 200** at
   279–306 KB, each carrying an `application/ld+json` `JobPosting` with a
   `description` of **2 601 to 5 004 characters** and the employer named.
   Drive the browser when it is there; do not require it.
2. **The two traps are the same as jobup's, because it is the same platform.**
   `baseSalary` is a `MonetaryAmount` shell with no amount on **5 of 5**, and
   `jobLocation.address.addressLocality` is empty on **5 of 5** — the city
   lives in the listing's per-card JSON (`locations[]`, with canton, postcode
   and coordinates), not on the ad page. Read
   `jobup.md` § *The plain-HTTP route* for the full measurement and for what
   was deliberately **not** measured; none of it is repeated here, because one
   platform should not be documented twice.
3. **Applying was not instructed.** If it needs the browser this adapter
   splits like `wttj.md` rather than going back to a browser prerequisite for
   reading.
4. **No login is required to scan.** Say so, as for jobup.

Never fill a credential field, here or anywhere.

## Building a search URL

```
https://www.jobs.ch/de/stellenangebote/?term=<keywords>
   &location=<town>              # SEE TRAP 1 — the accent is load-bearing
   &publication-date=30          # 1 | 3 | 7 | 30 (days)
   &benefit=working-from-home    # home-office ads only; set when remote_only
   &page=2                       # 1-indexed (omit for page 1)
```

Verified on `term=laravel`: bare → 185; `&location=lausanne` → 6;
`&publication-date=7` → 57; `&publication-date=30` → 173;
`&benefit=working-from-home` → 10; both filters together → *Keine Laravel Jobs*,
i.e. a real zero. `&page=2` returns a different first card and appends `- 2` to
the page title.

`search.posted_within` maps as on jobup: `week` → `7`, `month` → `30`,
`quarter` → omit the parameter and **say so** rather than silently narrowing the
user's window to 30 days.

## The ad id and its URL

The id is a UUID on the card's link element, exactly as on jobup:

```
<a data-cy="job-link" id="vacancy-link-4270df19-41e9-441f-a1f0-24c465782211" …>
```

Strip the `vacancy-link-` prefix. The card also carries
`data-cy="serp-item-<uuid>"`, which is a second route to the same id. Rebuild the
canonical URL from the bare id:

```
https://www.jobs.ch/de/stellenangebote/detail/<ID>/
```

**Never return a URL from page JS** — the tool blocks any result carrying a
query string. Read the `id` attribute and rebuild.

## Extracting search results

The jobup snippet works here, but **its label filter is French and lets German
labels through**. Use this one, whose filter covers both:

```js
JSON.stringify([...document.querySelectorAll('[data-cy="serp-item"]')].map(c=>{
  const a=c.querySelector('[data-cy="job-link"]');
  const id=a?(a.id||'').replace(/^vacancy-link-/,''):null;
  const drop=/^(Arbeitsort:|Pensum:|Vertragsart:|Ist der Job relevant für dich\?|Promoted|Einfach bewerben|Lieu de travail:|Taux d'activité:|Type de contrat:|Offre pertinente \?)$/;
  const p=c.innerText.split('\n').map(s=>s.trim()).filter(Boolean).filter(s=>!drop.test(s));
  return {i:id, q:!!c.querySelector('[data-cy="quick-apply"]'),
          promo:!!c.querySelector('[data-cy="recommended"]'), s:p.join(' · ')};
}))
```

Yields, per card: posting age, title, town, workload, contract type, company,
`q` = in-site apply available, `promo` = paid placement (trap 2).

**The plain-HTTP sweep works here too, through the same adapter**:
`jobup.py search --site jobs-ch`. Verified 2026-09-02 — 21 ads from one
listing page, no browser, no cookie. The measurement and the traps live in
`shared/boards/jobup.md`; only the host and the path differ.

**A closed ad answers in four different ways, and this board shares the
mechanism with jobup** — same operator, measured on both: a `410` that still
serves the ad's own `JobPosting` block, an expired ad that **redirects to its
category page** (22 blocks here, 20 on jobup, and no mention of the job), a
`404` for an id that never existed, and a plain `200` for the ad itself.
**The table and the reading order live in `shared/boards/jobup.md`** — one
place, so a corrected figure cannot survive in a second copy. Issue #88.

**The posting age is the age of this listing, not of the ad.** *"Vor 3 Wochen"*
on a re-listed ad is three weeks since the re-listing, and the card does not
distinguish the two — jobup, the same operator, put a date seven weeks wrong
into a ledger that way and changed which ad topped a ranking. Read the ad
page's own date, and where it was not opened leave the ledger's `Posted` empty
rather than deriving it. Issue #84.

Sample output, verbatim from a real run:

```
{"i":"f465da67-…","q":true,"promo":false,"s":"Vor 3 Wochen · Full-Stack Entwickler/in PHP / Symfony / React · Pratteln · 80 – 100% · Festanstellung · IWF AG"}
```

## Reading one ad

**The standalone ad page renders fully**, as on jobup, and **every `data-cy`
selector is identical** — verified field by field. The jobup snippet works
unchanged:

```js
(()=>{const q=s=>(document.querySelector(s)?.innerText||'').replace(/\s+/g,' ').trim();
 const vd=document.querySelector('[data-cy="vacancy-description"]');
 let d='';
 if(vd){const c=vd.cloneNode(true);
   c.querySelectorAll('[data-cy="jobfit-teaser-cta"],[data-cy="vacancy-mood"]').forEach(e=>e.remove());
   d=c.innerText.replace(/\s+/g,' ').trim();}
 return JSON.stringify({
   t:q('[data-cy="vacancy-title"]'),
   pub:q('[data-cy="info-publication"]'),      // "04 August 2026" — GERMAN month, trap 4
   wl:q('[data-cy="info-workload"]'),          // "100%"
   ct:q('[data-cy="info-contract"]'),          // "Festanstellung"
   ho:q('[data-cy="info-homeoffice"]'),        // absent on many ads
   loc:q('[data-cy="info-location-link"]'),    // "Chemin d'Entre-Bois 25, 1018 Lausanne"
   sal:q('[data-cy="info-salary_estimate"]'),  // a LOGIN PROMPT, not a number — trap 3
   d:d});})()
```

## Traps

**1. The accent in a place name is load-bearing, and getting it wrong returns
zero silently.** This is the worst failure this adapter can produce: HTTP `200`,
a normal page, no error, no ads. Measured on `term=php`:

| `location=` | jobs.ch | jobup.ch |
| :-- | --: | --: |
| `Genève` / `genève` | 3 | 11 |
| `Genf` / `geneva` | 3 | 11 |
| **`geneve`** | **0** | **0** |
| `Neuchâtel` | 0 | 1 |
| **`neuchatel`** | **0** | **0** |
| `Zürich` | 30 | 0 |
| `zurich` | 22 | 0 |

Case is irrelevant; **the diacritic is not**. Exonyms are fine — `Genf` and
`geneva` both work on the French board — so this is not a language mapping, it
is accent-sensitive place resolution. `zurich` vs `Zürich` returns 22 vs 30:
not zero, but **not the same result set either**, so an unaccented spelling is
never merely "a few less".

**Pass the town exactly as the user wrote it, accents included, and never
lowercase-and-strip it.** If a location returns zero, retry once with the
accented form before reporting an empty board — and report which spelling you
used, per `shared/never-fail-silently.md`.

**This trap applies to jobup too**, and its adapter did not document it: a jobup
search for `geneve` has always returned zero.

**2. The page holds more cards than results, and paid ones repeat across pages.**
Page 1 of `term=laravel` returned **21** `serp-item` cards, one carrying
`data-cy="recommended"`; page 2 returned **22**, two of them recommended. The
card promoted on page 1 reappeared on page 2 as an ordinary organic result.

So: the page size is **20 organic plus a variable number of promoted**, not 20;
a promoted card is **not** evidence the ad matches the search; and the same id
will legitimately arrive twice in one sweep. The ledger's dedup absorbs the
repeat — but do not compute "how many results did I read" from card counts.
**jobup does the same thing** (21 cards, 1 promoted, on the same query).

**3. `info-salary_estimate` is not a salary, and logged out it is not even an
estimate.** It reads *"Melde dich an, um die Gehaltsschätzung von jobs.ch zu
sehen"* — a prompt to log in. Read naively it lands a German sentence in the
salary field of `job-ad.md`. **Never put this field in front of the user as a
salary.** On jobup the same field holds jobup's own estimate, which is a
different wrong thing; neither is the employer's range.

**4. `info-publication` is exact, and it is in German.** `04 August 2026`, where
the card says `Vor 3 Wochen`. Prefer the ad page's date, and parse German month
names — a French-only parser drops it. Ages on cards are German too: `Letzte
Woche`, `Vorgestern`, `Vor 3 Tagen`, `Vor 4 Quartalen`.

**5. The page language is not the ad language.** A `/de/` page served a Lausanne
ad whose body is entirely French, under a German `Über den Job` heading. Do not
infer the ad's language, or the employer's, from the path — read the text.

**6. The description container carries JobCloud's AI matching widget**, exactly
as on jobup: `jobfit-teaser-cta` inside `[data-cy="vacancy-description"]`. That
is the platform's opinion of the fit, not the employer's text, and left in it
contaminates the scoring. The snippet above removes it; do not simplify it back
to a plain `innerText`.

## The employer's own posting URL

Same gift as jobup, same shape, and it is present here too:

```
"applicationOptions":{…,"method":"APPLICATION_METHOD.EXTERNAL","externalUrl":"…"}
```

Harvest it into `Note` on the ledger row — it is the key that survives the
crossing to another board, and what step 1b needs to ask whether the ad is still
open (`shared/ats-open-check.md`). Observed pointing at easyapply.jobs,
onlyfy.jobs, abaservices.ch and contactrh.com.

**Some of those are redirectors, and reading the host as published is wrong.**
`sicpa.contactrh.com` answers **302 with a zero-byte body**, to
`career012.successfactors.eu` and then to `jobs.sicpa.com` — a SuccessFactors
tenant this repository has an adapter for. An implementation that reads the
provider off the published host concludes *"contactrh, unknown provider"* and
misses it.

**And following to the very end is wrong in the other direction**: measured on
2026-09-02, `boards.greenhouse.io/elastic` ends at `jobs.elastic.co/`, the
employer's own vanity domain, which names no provider either — the provider was
visible at the hop in between. **Identify at every hop and take the first that
names one**; `skills/job-scan/scripts/tenant_offer.py` does exactly that
(issue #83).

**Anchor the match on `applicationOptions`.** A detail page contains **four or
five** `"externalUrl"` keys, most of them empty strings belonging to other
blocks, so an unanchored match is a match on whichever one happens to be
non-empty first:

```js
(()=>{const m=document.documentElement.innerHTML
        .match(/"applicationOptions":\{[^{}]*?"externalUrl":"([^"]*)"/);
 return m&&m[1]?m[1].replace(/\\u002F/g,'/'):'';})()
```

**An empty string is the normal case**, meaning the ad applies in-site — treat it
as absent, not as a failure. Verified 2026-08-28 on seven ads across both hosts:
the anchored and unanchored forms agreed on all seven, and the anchored one is
the one that stays right when a neighbouring block is populated.

## Applying

Cards can carry *Einfach bewerben* (`quick-apply`), JobCloud's in-site apply
flow. **That flow has not been verified**, so this adapter documents scanning
only. Report the ad as a jobs.ch quick-apply, hand the user the URL, and say the
assisted flow is not supported yet. An application sent wrong is not
recoverable.

Where `externalUrl` is set, treat it like any external ATS: give the user the URL
and the files, do not attempt the form.

## Pace

Pace it like a person reading ads — a few dozen page views per run. Pagination
makes it tempting to pull ten pages at once; do not.
