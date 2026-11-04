# Board adapter — jobup.ch

<!-- hosts: www.jobup.ch -->
<!-- script: jobup.py -->
<!-- verified: 2026-09-08 -->
<!-- countries: CH -->
<!-- overlap: jobstore.md · 15.5 % measured from JOBSTORE's side; the source states no unit for this ratio and no raw count, and is refused to this project's HTTP client while a browser is served (2026-09-08), so it is not re-readable by script · 2026-09-03 -->
<!-- same-postings: jobs-ch.md · the same posting UUID appears on both — one platform, two brands -->
<!-- (anciennement `shares-platform:`, renommé le 08.09.2026 — le nom affirmait une parenté de plateforme là où la clé affirme des annonces identiques) -->

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

### The adapter that does it: `jobup.py`

```bash
python3 "$S/jobup.py" search --site jobup --term developpeur --pages 2
python3 "$S/jobup.py" search --site jobs-ch --term entwickler --location Bern
python3 "$S/jobup.py" ad --url "https://www.jobup.ch/fr/emplois/detail/<uuid>/"
```

**One request per page of twenty**, both boards, no browser. Verified
2026-09-02: 40 unique ads over two jobup pages, 21 over one jobs.ch page.

**The listing's `JobPosting` blocks are wrapped in an `ItemList`**, and
`_ldjson.py` had to learn to unwrap `itemListElement` — before that it saw
**zero postings on a page carrying twenty.** That unwrapping is in the shared
reader rather than here, because `ItemList` is a schema.org container and the
next board to use it should not have to rediscover it.

**A promoted card is repeated across pages.** One ad sat at **position 13 of
page 1 and position 1 of page 2**. `search` deduplicates on the UUID and says
how many repeated — **and it distinguishes that from a pagination failure**: a
page whose ids are *entirely* contained in what came before has not advanced
and exits 6, while a handful of repeats is paid placement.

**`ad` reads the state before the body**, per the four-state table above:
`410` and `404` exit 3 with which of the two it is, **a redirect exits 3
refusing to conclude anything**, and only a plain `200` is parsed. Verified on
all four.

## 2026-11-04 — #1260: the list was a cached body 51.6 h old, and the encoding variant is why

`search` returned a **frozen list** on the 02, 03 and 04.11 sweeps: status 200,
`exit 0`, *"ended by itself — the board's total was reached"*, well-formed
advertisements, and **not one new ad in three days**. The only symptom was an
absence.

**The host names the cause itself: `Vary: Accept-Encoding`.** This adapter asked
for `Accept-Encoding: identity` (#71, so one body would have one size rather than
two), so the CDN kept a separate cache entry for a variant **no other client on
earth requests** — and nothing refreshed it. Measured at one edge POP
(`ZRH52-P1`), the same `Cache-Control: no-cache="Set-Cookie"` on every response
and no `max-age` at all, so the lifetime is the distribution's own:

| `Accept-Encoding` | X-Cache | `Age` | newest `datePosted` | stated total |
| :-- | :-- | --: | :-- | --: |
| `identity` — what this adapter sent | **Hit** | **185 671 s = 51.6 h** | 2026-11-02 00:48 | 1360 |
| `gzip` — what every browser sends | Hit | **69 s** | 2026-11-04 08:44 | 1322 |

Across ten listing keys the eight served from cache **all carried `Age` 51.6 h,
each to a tenth of an hour** — one snapshot written at one instant, and its
`Date` header (`Mon, 02 Nov 2026 06:42:46 GMT`) is our own sweep of the 02.11 at
07:41 +01:00. **We populated that cache ourselves and have been re-reading it
since.**

**AND THE FAILURE MODE IS NOT «&nbsp;identity VERSUS gzip&nbsp;» — the four cells were
measured and they disagree.** This renaming is the part that outlives the
specimen, and a peer established the two jobs.ch rows and the stale gzip hit:

| host | encoding | what was served |
| :-- | :-- | :-- |
| jobup | `identity` | **Hit, 51.6 h stale** — the reported symptom (measured here) |
| jobup | `gzip` | 5 Hit / 5 Miss, and one HIT serving **11 ads where the origin served 12** (reported) |
| jobs.ch | `identity` | **Hit, fresh to the second** — three keys agreeing to the unit (reported) |
| jobs.ch | `gzip` | Miss, so fresh by construction (reported) |

So `identity` is not inherently a cold variant: on the sibling host it is warm
AND current. **The defect is a HIT ON A LONG-LIVED ENTRY**, and whether a request
lands on one depends on the keyspace we inhabit and on each key's own traffic —
two things we neither control nor can predict, since the four cells behave
differently under the same declared configuration. **Switching the encoding is
therefore not a fix to the mechanism: it is a move to a keyspace that is better
today**, which is the right thing to do and closes nothing. Measured for the
sibling before switching it: jobs.ch `identity`, `gzip` and a fresh key all
returned 23 ads and the same newest `datePosted` to the second, so the shared
`get()` costs it nothing.

**WHICH IS WHY THE GUARD IS NOT THE REMEDY'S BELT — IT IS THE REMEDY.** A gzip
HIT was measured serving 11 advertisements where a fresh key served 12, and the
twelfth had been published before both reads: **an advertisement really missed,
on the variant we are moving to**. The count is what establishes it — 11 against
12 is not a sorting artefact, where a newest-date gap would be.

**AND THE GZIP SIDE IS PARTLY OUR OWN WRITING, WHICH IS DECLARED BECAUSE IT
CHANGES WHAT THE REMEDY IS WORTH** (the question was put by the pilot, and the
answer is in this session's own record). Of the ten gzip reads, **eight were
MISSES** — the origin's own answer, hence today's data, and silent on whether
anything keeps that variant warm. Of the two HITS, `Chef de projet` at `Age`
0.1 h was **our own request fifteen minutes earlier** and establishes nothing.
**The only uncontaminated witness is `Scrum Master`: a HIT at `Age` 11.5 h on a
key we had never requested in gzip**, so real traffic does reach that variant —
one specimen, declared as one.

**SO THIS IS NOT ESTABLISHED, and it is the open question:** whether real
traffic keeps the gzip variant warm for our RARE terms, or whether we end up
alone on it one notch further along. If the second, gzip buys days and **the
guard below is the only real protection** — which is why it is not a
belt-and-braces.

**And it does not affect this board's own users:** the gzip variant is 69 s old,
so there is nothing to report upstream about a page broken for them. What is
theirs is a long lifetime on a search-results page; what was ours is having sat
alone on a variant their traffic never touches.

**THE REPORTED CAUSE WAS WRONG, AND THE SUGGESTED FIX WOULD HAVE BOUGHT ONE
DAY.** The issue measured `Chef de projet` frozen where `chef de projet` was
fresh, and proposed lowercasing the term. The case is a red herring: `Chef de
Projet` and `CHEF DE PROJET`, **both capitalised**, measured fresh in the same
minute, and the lowercase form was fresh only because the measurement had just
populated it (`Age` 454 s). A fixed key freezes as soon as our own sweep
populates it, whatever its case.

**Viewer revalidation is not available either:** `Cache-Control: no-cache` and
`Pragma: no-cache` as request headers are both ignored — three shots, three
Hits, `Age` climbing by 6 s each time, with a bare control that did return a Hit
so the bench was armed.

**What the adapter does now.** It asks for `gzip, deflate` and `decompress_body`
(in `_decode.py`) undoes it, so the size reserve of #71 is honoured **on the
decompressed body** rather than by staying on a cold variant. The two variants
carry the same content, measured: on the two keys our sweeps had not populated,
`identity` and gzip returned stated totals equal to the unit (160/160 and
132/132) and the same newest date. **No `br`** — the standard library cannot
decode it, and `decompress_body` raises rather than hand back bytes that would
be read one layer down as a charset fault.

**And because that remedy can go stale in its turn, the symptom has its own
guard.** A page served from the edge's cache with `Age` above `MAX_BODY_AGE`
(24 h) makes the run **exit 5 after its rows are on stdout**, naming the page
and the age, and saying that every sentence above it describes that body and not
this hour. `5` is declared here because a code outside the contract reads as its
nearest neighbour: across the 238 adapters of this repository the contract is
**2 broken · 3 gone · 6 partial · 7 refused · 8 unknown**, and `9` already
carries two different meanings elsewhere. A cached page whose `Age` cannot be
read is **declared on stderr and changes no code** — the ignorance neither frees
nor accuses.

**The witness is the `Age` the host declares, never a publication date.** Page 1
is sorted by RELEVANCE, and `Laravel` and `Symfony` carried a newest ad of 30.10
and 19.10 **on both variants** — legitimately thin listings. A guard reading
that date would have reddened on correct data, and it would have looked prudent.
**The 24 h threshold rests on the USE and not on a gap**: a daily sweep cannot
learn anything from a body older than its own interval. Nothing was observed
between 11.5 h and 51.6 h, but that gap has **one** uncontaminated gzip
specimen under it, so it is a remark and never the justification.

**Prefer `ld+json` to the DOM selectors below.** Both work; the structured
block does not move when the site is redesigned, and `[data-cy="…"]` does. The
selectors stay documented because the browser path still uses them and because
they are what a human debugging a page will see.

**What was not measured — do not extrapolate.** Rate limiting under a real
sweep (this was ~12 requests at one per second), whether the `ld+json`
`description` is character-for-character what the page shows, and whether other parasitic content rides in the payload — the AI
matching widget documented in *Traps* below does not appear in it, which is
one absence rather than a clean bill.

## A closed ad: four states, and the block count decides none of them

**Measured 2026-09-02, on four real ad URLs.** This is the whole of what an ad
URL can answer, and no single signal separates them:

| State | HTTP | redirect | `JobPosting` blocks | `isActive` |
| :-- | --: | :-- | --: | :-- |
| **live** | 200 | none | **1** | `true` |
| **gone** | **410** | none | **1** | **`false`** |
| **expired** | 200 | **301 → the category page** | **20** | `true` — of the *other* ads |
| **never existed** | **404** | none | 0 | — |

**The `410` is the one that breaks a naive check.** It returns **460 kB, its own
JobPosting block, and the ad's own text** — with `isActive: false` and the page
saying *"n'est plus… expirée… plus disponible"*. **A test that reads "one
JobPosting block, therefore open" calls it open.**

**And the `301` is the one that breaks a careful check.** An expired ad
redirects to the category page of its own trade: 497 kB, a `<title>` reading
*"102 offres d'emploi dans la catégorie…"*, **twenty JobPosting blocks**, and
**zero occurrences of the job's own title**. Nothing on that page is false —
the twenty ads exist and are genuinely open. **The more carefully a check
follows the redirect and validates what it finds, the more confidently it is
wrong.** Reproduced on `jobs.ch`, 22 blocks, same mechanism, same operator.

**So the reading order is: status, then landing URL, then the ad's own
`isActive` — and the block count last, if at all.**

1. **`410`** → the board says gone. Believe it.
2. **`404`** → this id never existed. Different fact, different action.
3. **Any redirect** → **it is forbidden to conclude "open"**, whatever the
   landing page contains. A `<title>` that starts with a count, more than one
   `JobPosting`, or the job's own title absent all confirm a category page.
4. **`200`, no redirect, `isActive: true`** → served.

*(A third, independent corroboration for the expired case: an employer search on
jobup showed that employer publishing seven other roles that day and not this
one.)*

**What is still not measured here**: whether a `410` can ever be served for an
ad that is in fact open — no reason to think so, and it has not been tested.

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

**This block returns `d` with no bound, and `javascript_tool` stops at 1 000
characters** — whole result, framing included, then a literal `[TRUNCATED]`,
measured 2026-11-01 (`shared/page-js-output-ceiling.md`). So a description
longer than that comes back as a prefix inside unterminated JSON, with nothing
in the output saying so. **Read the description with `get_page_text`** and keep
page JS for the short structural fields. *The snippet is left as it stands: it
was measured for this board on its own day, and changing it belongs to the run
that re-measures it.*

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

**3. The card's date is not the posting date, and on a re-listed ad it is
wrong by weeks.** `info-publication` gives a real date — *"18 août 2026"* —
where the card gives *"Il y a 3 semaines"*.

**Say what each one measures, because that is what the preference rests on:**

| | What it is |
| :-- | :-- |
| `info-publication`, on the ad page | **when the ad was published.** The only date that means that |
| *"Il y a 3 semaines"*, on the card | **how long ago this listing last appeared** — which on a re-listed ad is the age of the re-listing, not of the ad |

**Nothing on the card distinguishes the two**, and a relative label reads as an
age. Measured 2026-09-02: a ledger row carried `2026-09-01` for an ad whose
real `datePosted` is **`2026-07-14`** — seven weeks out, because the card was
showing a re-listing.

**And it was not a cosmetic field.** Two ads were tied at 62% in the `todo`
pool and the tie was broken by the most recent date, so **the older ad came
out on top of a ranking that decides what gets drafted**. The cost of this one
is a dossier written for the wrong ad. Issue #84.

**So: never write the card's date to the ledger.** Read `info-publication` from
the ad page, and if the ad page was not opened, leave the date empty rather
than filling it from the card — an empty field is a question, a wrong date is
an answer.

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

## The bare listing carries no structured data; a filtered search does

Measured 2026-09-03, and stated narrowly because a wider reading of the same
numbers was published and had to be retracted:

```
/fr/emplois/                          275 kB    0 JobPosting
/fr/emplois/?page=1                   275 kB    0
/fr/emplois/?term=developpeur         534 kB   22
/fr/emplois/?location=Lausanne        517 kB   22

/de/stellenangebote/                  288 kB    0
/de/stellenangebote/?term=entwickler  546 kB   21
/de/stellenangebote/?location=Bern    288 kB    0
```

**Re-measured 2026-09-04, and the first line of that table is no longer
true.** The same unfiltered URLs now carry **20 `JobPosting` each**, on both
boards:

```
/fr/emplois/            was 0   now 20
/fr/emplois/?page=1     was 0   now 20
/de/stellenangebote/    was 0   now 20
```

**Two observations a day apart, opposite, and nothing here can tell a
deployment from an intermittency.** That is the same shape as
`maliemploi.org`, whose Apache error page had gone back to a real 115-byte
file by the time it was investigated — **a behaviour measured once is dated,
and this one dated in under twenty-four hours.**

**What still holds:** `location` alone is honoured by jobup and **not** by
jobs.ch — `?location=Bern` and the bare URL return byte-identical pages there.
One platform, two behaviours.

**And what the refusal now stands on.** `search` still requires a filter, but
not because the listing is always empty — **because a zero taken from that URL
means one thing today and another yesterday**, and a zero from it was already
read once as a dead board, on this board, in this repository (#122). A filter
makes the answer interpretable.

**So `search` refuses a call with no filter** (#126). Without one it fetched
the bare listing and returned zero every time, and a zero from a board reads
as a board with no jobs — it was reported as one, and an Atlas page was
published saying these boards had broken. **A tool that accepts an invocation
which cannot succeed manufactures false results.**

Two faults in the same command made that worse and are fixed: `--location`
never entered the query string — it was applied afterwards, to rows fetched
from the *unfiltered* listing — and `drop_report` returns `(kept, dropped,
labels)` where the call site unpacked two, so `--location` alone raised
`ValueError` after the sweep had been paid for.

**And the empty-result message named two causes of three.** It offered *a
reading failure or the end of the results* and omitted the one that was
happening: **a query this site does not answer with structured data.** Naming
two of three is not a false statement and it had the same effect as one — it
pointed at *the board is broken*.

**Re-exercised 2026-09-08**: `search --site jobup --term informatique` returns
**20 advertisements over 1 page**, and `--site jobs-ch` the same. *Salary: 0 of
20 carry a figure on either site — the block is present and empty (#67).*
