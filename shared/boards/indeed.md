# Board adapter — Indeed

<!-- verified: 2026-09-02 -->

<!-- hosts: my.indeed.com -->
<!-- countries: * -->
**Re-tested 2026-09-02: the browser requirement holds.** `ch.indeed.com/robots.txt` answers 200 in `text/plain` (13 097 bytes), so the rules are readable — but `ch.indeed.com/jobs?q=…` answers **HTTP 403** to a plain client. The listing needs the user's own browser, exactly as this file says.

Country-scoped: `ch.indeed.com`, `fr.indeed.com`, `www.indeed.com`… The search
domain is configured; ad URLs work from the generic `www.indeed.com` whatever
the country (verified: a Swiss ad opens identically from both).

**Verified against `ch.indeed.com` on 2026-08-26, re-verified 2026-08-28.**
Every selector below still holds. Selectors rot; re-check before trusting an old
note.

## Configuration

```yaml
boards:
  indeed:
    enabled: true
    domain: "ch.indeed.com"   # required — your country's Indeed
    language: "fr"            # optional, becomes hl=<language>
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `domain` | yes | The country site the user actually browses. **No default**: guessing the country silently searches the wrong market. Read the host table above before writing this: `my.indeed.com` is not Malaysia, `us.indeed.com` does not exist |
| `language` | no | `hl=` parameter. Defaults to the site's own |

### The host is `<iso2>.indeed.com` — except where it is not

**`my.indeed.com` is not Malaysia.** At Indeed the `my.` prefix is *my
profile*: it answered `403` on 2026-09-02 and, when issue #64 measured it, a
`200` carrying **126 kB of login page** at `/robots.txt`. **Malaysia is
`malaysia.indeed.com`** — 13 097 bytes, `text/plain`, the same file as every
other country.

**Swept 2026-09-02, 55 ISO-2 codes plus three named hosts**, reading only
`/robots.txt`:

| | |
| :-- | :-- |
| Country sites on **one identical file** — md5 `674618fb2278`, 13 097 B | 49 codes, plus `malaysia.` and `www.` |
| **`th.indeed.com` diverges** — 13 164 B, four lines | one exception, and only just |
| **`ru.indeed.com` is `User-agent: * / Disallow: /`** — 25 bytes | **a total refusal**, on a host whose siblings are wide open |
| `gb` **redirects** to `uk.indeed.com` | both work; `uk` is the canonical |
| **`my`** | the profile login, not Malaysia |
| **`us`, `ke`** | **no such host** — the United States is `www.indeed.com` |

**So the pattern holds for 49 of 55 and the exceptions are not guessable.**
Check the host before configuring it, and check it by reading `/robots.txt`:
a country site answers `text/plain`, and anything else is a different product.
`shared/robots-policy.md` makes that a precondition (#60, #64) and
`skills/job-scan/scripts/_robots.py` enforces it at run time.

**And `ru.indeed.com` refuses every crawler.** The guard already stops there
— `User-agent: *` with `Disallow: /` is one of the two states `_robots.py`
refuses on — but the reason is worth knowing before somebody reads it as a
broken adapter.

## Prerequisites — read the bot-detection section first

1. **The Claude extension for Chrome**, installed and connected.
2. **Indeed challenges automated-looking traffic.** See below. This is the
   defining constraint of this adapter, not a footnote.
3. Whether browsing requires a login was **not verified** — the session used
   for verification was logged in throughout. Assume it may be needed.

## ⚠ Bot detection — the rule that overrides the rest

**Indeed serves anti-bot challenges, and this was observed in real use**: during
the very session that produced this adapter, the user hit a challenge and
solved it themselves.

**Never solve, click through, or work around a challenge.** Not a checkbox, not
an image grid, not a slider. When one appears:

1. Stop scanning. Do not retry, do not navigate elsewhere hoping to slip past.
2. Tell the user plainly: *"Indeed is showing me a human-verification
   challenge. It is yours to solve — open the tab, complete it, and tell me
   when it's done."*
3. Resume only when they confirm.
4. If it recurs in the same run, **stop for good** and say so. Repeated
   challenges mean the pace was wrong; hand the user the search URLs to browse
   themselves, and fall back to `cover-letter <ad URL>` for anything they find.

**The challenge markup has now been observed** — 2026-08-28, on the first
request of a re-verification run, before any pace could be at fault:

| Signal | Value |
| :-- | :-- |
| `document.title` | `Security Check - Indeed.com` |
| Body text | *"Vérification supplémentaire requise"*, followed by *"Voici votre Ray ID pour cette requête"* |
| `Ray ID` | a Cloudflare request id — the challenge is served by Cloudflare, not by Indeed itself |
| `.job_seen_beacon` | **0** |

**The detection rule below fired correctly on it**: zero cards, and `v[ée]rifi`
matched *Vérification*. That is the first time it has been checked against a
real challenge rather than reasoned about.

**It did not clear on its own.** The user solved it in the running session, and
the run resumed on the real results page. Do not wait one out.

Detect it by what is *missing* as much as by the wording, since the body is
localised:

```js
// Run this before trusting any extraction.
(()=>{const t=document.body.innerText.slice(0,1500);
 return JSON.stringify({
   cards: document.querySelectorAll('.job_seen_beacon').length,
   suspicious: /v[ée]rifi|captcha|robot|human|unusual traffic|Cloudflare/i.test(t)
 });})()
```

Zero cards, or `suspicious` true, means **hand over to the user** — never
improvise around it.

**Pace accordingly.** Indeed is the least tolerant board that ships here: a few
searches per run, several seconds between page views, and no batch-opening of
results. The throttle lands on the user's own account and IP.

## Building a search URL

```
https://<domain>/jobs?q=<terms>&l=<place>&hl=<language>
   &fromage=7      # posted within N days — verified with 7
   &radius=25      # around the location. Accepted; the UNIT (km or miles) was
                   # not verified, so treat it as approximate, never as the
                   # commute rule
   &start=10       # pagination, 0-indexed by result count (10 per step)
```

Verified: `?q=développeur PHP&l=Suisse` returns results; `&start=10` returns a
different first ad, so paging works; `&fromage=7` and `&radius=25` are accepted.

Roughly **10 to 16 cards** hydrate per page — enough that a broad search plus
paging beats many narrow ones.

**The remote filter is an opaque `sc=0kf:attr(...)` token that was NOT
verified.** Do not guess it. Filter remote work from the card text instead —
but **not on the exact string `Travail à domicile`**, which is only one of three
forms. Observed on a single page of ten cards, 2026-08-28:

| Card text | Reading |
| :-- | :-- |
| `Travail à domicile` | home office, standing alone |
| `Télétravail à Lausanne, VD` | remote — **and the town is fused into the marker** |
| `Travail hybride à Le Vaud, VD` | hybrid, town fused the same way |

Matching `Travail à domicile` exactly therefore **misses the most remote ads of
the three**, silently. Match on the stem instead —
`/t[ée]l[ée]travail|à domicile|hybride/i` — and read the work mode from the ad
text, never from the marker alone. The fused town is not a location field: the
card's own location line is.

## The ad id and its URL

The id is `data-jk` on the card's title link — 16 hex characters:

```
<a id="job_c8a3978553801746" data-jk="c8a3978553801746" class="jcs-JobTitle …">
```

In the ledger it is recorded **prefixed**, as `indeed:<jk>`. Rebuild the URL:

```
https://www.indeed.com/viewjob?jk=<jk>
```

The generic domain resolves a country ad correctly — verified on a Swiss job
from `www.indeed.com`. **Never return a URL from page JS**; read `data-jk` and
rebuild.

## Extracting search results

**Check the no-results banner first — see trap 1. Then filter before you
extract — see trap 5: every page carries a decoy card, and this snippet used
to harvest it.**

```js
(()=>{
  const all=[...document.querySelectorAll('.job_seen_beacon')];
  // trap 5 — the decoy: 0×0 on screen (the discriminant), and, as checks,
  // a single-line innerText and a hand-made data-jk
  const real=all.filter(c=>{const r=c.getBoundingClientRect();
                            return r.width>0 && r.height>0;});
  const nl=c=>(c.innerText.match(/\n/g)||[]).length;
  const rows=real.map(c=>{
    const a=c.querySelector('[data-jk]');
    const p=c.innerText.split('\n').map(s=>s.trim()).filter(Boolean)
            .filter(s=>!/^(Candidature simplifiée|nouveau|Publiée|Employeur actif|PostulerEnregistrer|Enregistrer)/i.test(s));
    return {i:a?a.getAttribute('data-jk'):null, s:p.join(' · ').slice(0,180), nl:nl(c)};
  });
  return JSON.stringify({
    emitted: rows.length,
    dropped_by_geometry: all.length-real.length,
    // the two secondary signatures, counted on what was DROPPED — a check
    // that the geometry dropped the decoy and not a real card
    dropped_single_line: all.filter(c=>!real.includes(c) && nl(c)<=1).length,
    kept_single_line: rows.filter(r=>r.nl<=1).length,   // must be 0
    rows
  });
})()
```

**Read the two counts before the rows.** `dropped_by_geometry: 0` on a page
that carries a decoy is a filter that has stopped working, and nothing else
would say so — every measured page since 2026-08-27 carried at least one
(five over eight searches, one per page over four pages, one apiece over
two). `kept_single_line > 0` is a real card the line-break check would have
questioned: look at it before trusting it. **Both counts are printed so that
a filter that silently passes everything cannot look like a clean page.**

**What this filter rests on, with its denominator.** The geometry signal —
`getBoundingClientRect()` returning **0 × 0** — was measured on 2026-09-09
by session `18`: **4 pages of `ch.indeed.com`, 4 decoys, one per page, all
four at 0 × 0**, all four passing every visibility test (`display: block`,
`visibility: visible`, `opacity: 1`, no `aria-hidden`), all four with a
rotated-alphabet `data-jk` and a single-line `innerText` cloning the card
above. One domain, four pages, one day. *Issue #199.*

**Written on that measurement, and NOT exercised on a live page since:**
on 2026-09-11 the snippet above was assembled from the 09.09 measurement and
the 08.27/09.05 line-break filter, and could not be run — the Chrome
extension was not connected. So this file does not claim to have SEEN the
geometry filter separate; it claims the 09.09 measurement, which it quotes.
**The first operator to run it records `emitted` and `dropped_by_geometry`
here, with the URL and the hour, and #199 closes on that line — not on this
paragraph.** What WAS exercised on 2026-09-11, in `node` on three stub
cards (a real 4-line card at 600 × 120, a decoy clone at 0 × 0, a real
one-line card): `emitted: 2, dropped_by_geometry: 1, kept_single_line: 1`,
the decoy's id absent from the rows — and with the geometry test mutated
to `true`, `emitted: 3, dropped: 0`. *That tests the snippet's logic, not
Indeed's page.*

Sample output of the pre-filter version, verbatim from a real run (the
rows' shape is unchanged; the counts are new):

```
{"i":"c8a3978553801746","s":"Développeur Informatique · QUARIQ · Travail hybride à 1228 Plan-les-Ouates, GE · 100% +1"}
{"i":"9ebfecb5d0e02ee4","s":"Mission Plugin Developper - 2 mois prolongeable - 40% · Academic Work · Lausanne, VD · 100% · Travail à domicile"}
```

## Reading one ad

**The standalone ad page renders fully** — `navigate` and read, no click-through.

```js
(()=>{const q=s=>{const e=document.querySelector(s);return e?e.innerText.replace(/\s+/g,' ').trim():null;};
 return JSON.stringify({
   t:   q('[data-testid="jobsearch-JobInfoHeader-title"]') || q('h1'),
   co:  q('[data-testid="inlineHeader-companyName"]'),
   loc: q('[data-testid="inlineHeader-companyLocation"]'),
   meta:q('#salaryInfoAndJobType'),        // salary and/or workload, when present
   d:   q('#jobDescriptionText')
 });})()
```

## Traps

**1. A zero-result search still renders cards.** This is the dangerous one.
`?q=laravel&l=Lausanne` returns the banner *"ne donne aucun résultat"* **and
six `.job_seen_beacon` cards with valid `data-jk`** — "Emplois similaires à ceux
consultés", suggestions based on browsing history, not results. Harvest them and
you inject six unrelated ads into the ledger, attributed to a search they never
matched, with nothing to show anything went wrong.

**Always check the banner before extracting:**

```js
/ne donne aucun résultat|aucun résultat|did not match any jobs/i.test(document.body.innerText)
```

If it is true, the search returned **nothing** — record zero and move on,
whatever the cards say.

**2. `#salaryInfoAndJobType` mixes salary and workload.** It returned `100%` on
one ad (a workload) and a salary range on another. Parse it, do not assume which
one you got, and never report a workload as a salary.

**3. The location carries a postcode** — `1228 Plan-les-Ouates, GE`,
`1003 Lausanne, VD`. Like jobup, that is exactly what an unemployment-office
declaration needs and what most boards omit. **Capture it while the ad is open**
(see `shared/modules/job-room-ch.md`).

**4. Opening a search auto-selects the first ad**, appending `&vjk=<jk>` to the
URL and opening a side panel. Harmless, but do not mistake that id for a
selection you made.

**5. Some result cards are fabricated duplicates.** Observed live on
`ch.indeed.com` on 2026-08-27: **five cards across eight searches** carried
hand-made `data-jk` values — `a1b2c3d4e5f67890`, `abcdef0123456789`,
`0f1e2d3c4b5a6978`, `789abcdef0123456`, `cdef0123456789ab` — each **cloning the
real ad immediately above it**. Ingest them and the ledger gains phantom rows
pointing at ad URLs that do not exist.

They were inspected: no hidden instructions, no URLs, no injected markup beyond
the duplication. Treat them as bad data, not as an attack — but **never harvest
them**.

Two signals, in order of reliability:

- **The card's text has no line breaks.** A real card's `innerText` splits into
  title / company / location / workload; these come back as one concatenated
  string. This is the robust test, because it does not depend on the id's shape.
- The `data-jk` is a hand-made pattern rather than random hex — sequential
  (`abcdef0123456789`), rotated (`cdef0123456789ab`) or interleaved
  (`a1b2c3d4e5f67890`). Useful for recognising one by eye, too brittle to filter
  on.

Filter on the line-break count — verified over eight searches on 2026-08-27:
it removed all five fabricated cards and kept every genuine one:

```js
[...document.querySelectorAll('.job_seen_beacon')]
  .filter(c => (c.innerText.match(/\n/g) || []).length > 1)
```

**And since 2026-09-09 the discriminant is the GEOMETRY, with the line
breaks and the id shape demoted to checks** (#199). Measured by session
`18` on four pages of `ch.indeed.com`, one decoy per page: the decoy
**carries the same class as the real cards and passes every visibility
test** — `display: block`, `visibility: visible`, `opacity: 1`, no
`aria-hidden` — and the one thing that separates it is
`getBoundingClientRect()` at **0 × 0**. Its `data-jk` was, all four times, a
rotation of the hexadecimal alphabet (`456789abcdef0123`,
`abcdef0123456789`, `cdef0123456789ab`) or the interleaved form
(`0f1e2d3c4b5a6978`), and its `innerText` cloned the card above without a
line break — the two signatures of 08.27 and 09.05, again. **A signature of
the id is a property of the day; the geometry is what makes the card
invisible to a person and visible to a script, which is what a decoy is
for.** So the extraction snippet under *Extracting search results* now
filters on `width > 0 && height > 0` first, and prints the line-break count
of what it kept and what it dropped as the check that the two signals still
agree. **It has not been exercised on a live page since it was written** —
see that section for what is measured and what is not.

> **A decoy is not noise: it is a test, and harvesting it is the failing
> answer.** Emitting its id into the ledger is what marks the client as an
> automaton — that is, most likely, what the card exists for.

**Re-measured 2026-09-05, and the ranking of the two signals is now load-bearing
rather than a preference.** Two searches on `ch.indeed.com`, sixteen cards each:
one fabricated card apiece — `789abcdef0123456` (Geneva, index 13) and
`123456789abcdef0` (Lausanne, index 2). Both cloned the card immediately above,
**text identical after whitespace is stripped**, and both signals coincided on
every card: *rotation id ⇔ single-line `innerText`*. Genuine cards ran 3 to 7
lines, so the `> 1` line-break filter separated them with margin.

**And the repair that suggests itself does not work.** The fabricated card's own
links sometimes carry the cloned ad's real `jk` — Geneva's index 13 held
`fb99e059bea7e87e`, which is index 12's id — so "take the second `jk` from the
card's `href`s" looks like a fix. **On the Lausanne page the same card's links
held the placeholder and nothing else.** The fallback finds nothing there, and
where it does find something it assigns an id that already belongs to another
row.

**These cards are not ads with a broken id. They are a second rendering of the
ad above.** The action is to drop them, never to repair the identifier — which
is why the line-break test, and not the id's shape, is the one to filter on.

**A note on reading these cards.** Dumping a list of raw `data-jk` values or a
card's `innerHTML` can trip the extension's own content filter, which returns
`[BLOCKED: Cookie/query string data]` — sixteen-character hex strings look like
session tokens to it. That is the filter doing its job, not evidence about the
card. Extract the fields you need rather than raw markup.

## Applying

Cards can carry *Candidature simplifiée* (Indeed's in-site apply). **That flow
was not verified**, so this adapter documents scanning only. Hand the user the
ad URL and the files; do not improvise a submission — an application sent wrong
is not recoverable.
