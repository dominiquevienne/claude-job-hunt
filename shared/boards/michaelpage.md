# Board adapter — Michael Page

<!-- hosts: per-country -->
<!-- script: michaelpage.py -->
<!-- countries: * -->
**A board, not an ATS**: one search across many employers. It is the first
recruitment *agency* here, and that changes what comes back more than the
technology does — see the trap below, which is the reason to read this file.

Server-rendered HTML, and every ad carries a **schema.org `JobPosting`**, so the
extraction does not hang on CSS selectors. **No key, no cookie, no browser.**

Read by `skills/job-scan/scripts/michaelpage.py`.

**Everything here was verified against the live site on 2026-08-28**, on
`www.michaelpage.ch` (39 ads around Lausanne, read in full) with the URL shapes
cross-checked on `.fr`, `.de` and `.co.uk`.

## Country-scoped, and references do not cross the border

```
https://<domain>/jobs?search=<terms>&location=<place>&page=<n>
https://<domain>/job-detail/ref/<reference>
```

`<domain>` is `www.michaelpage.ch`, `.fr`, `.de`, `.co.uk` … **with no default**,
for the same reason as Indeed: guessing the country silently searches the wrong
market.

The id is the agency's own reference, `jn-<MMYYYY>-<digits>`, and
**`/job-detail/ref/<reference>` rebuilds the URL on its own** — no slug, no
language prefix. That matters because the slug form carries a per-ad language
segment (`/de/job-detail/…`, `/fr/job-detail/…`) which is the *ad's* language,
not the site's, and the slug without it 404s.

**A reference is served only by the domain that published it.** Verified both
ways: a Swiss reference answers 404 on `.fr`, and a French one answers 404 on
`.ch`. So the domain is part of the ledger key, and **a 404 is not proof an ad
died** — it may be alive on another country's site.

```
michaelpage:<domain>:<reference>
        e.g. michaelpage:www.michaelpage.ch:jn-072026-7075230
```

## The trap: the employer is described and never named

**0 of 39 ads named the hiring employer.** `hiringOrganization` is *Michael
Page* on every one — the agency, not the client. The employer appears only as
prose in the body, under *About Our Client* / *Unser Kunde* / *À propos de notre
client*: "an established company in the consumer-goods sector…".

Three consequences, none of them cosmetic:

- **The card carries `company: null` and `employer_named: false`**, deliberately.
  Writing "Michael Page" into the employer column would be false, and would put
  the agency's name where the ledger expects the company the user would work for.
- **The fuzzy employer-name dedup in `skills/job-scan/SKILL.md` cannot work
  here.** The same role, posted by the agency and by the employer's own ATS, has
  no shared key and no shared name. Expect that duplicate to survive; say so
  rather than pretending the ledger caught it.
- **The user cannot research the employer before applying.** That is a real
  property of agency ads, not a defect to hide — surface it at the gate.

## Traps

**1. The JSON-LD is invalid JSON, and a strict parser sees no ad at all.**
Every ad embeds **literal newlines inside JSON strings**. `json.loads` fails
with *"Invalid control character"* on **6 of 6** ads sampled; Python needs
`strict=False`, and most languages' default parser will reject the block
outright. A reader that trusts its parser concludes the page has no structured
data and falls back to selectors it did not need.

**2. A zero-result search answers HTTP 404, not an empty page.**
`?search=zzzqqqxyz`, `?search=quantum+cryptographer` and `?location=Zzzqqq` all
return 404. So a 404 on the first page is **ambiguous**: no match, or a wrong
domain. The script settles it in one extra request — the unfiltered `/jobs`. If
that answers 200, the domain is fine and the zero is real.

Paging past the last page is also a 404, which is the end-of-results signal.

**3. Pages overlap.** A `location=Lausanne` run returned 30 references on page 0
and **12 on page 1 of which only 9 were new**. Dedupe on the reference, never on
position or count. There is **no result total anywhere on the page**, so the
number of ads read is never the size of the board — the script says so on
stderr rather than implying coverage.

Page size is ~30 on `.ch` and `.de`, but **20 on `.fr` and 17 on `.co.uk`** —
do not hardcode it.

**4. `location` is often a region, not a place.** *Lausanne Region* on **25 of
39** ads, against *Lausanne* on 10 — plus one ad with no locality at all, and
*International* seen elsewhere. **A region cannot be geocoded to a commute
time**, so it does not satisfy the commute rule in `shared/scoring-rubric.md`.
Treat it as a coarse filter and read the body for the actual place.

**5. `baseSalary` is present on every ad and populated on almost none** — **3 of
39** carried a real range. The rest are hollow objects: `currency: ""`,
`minValue: ""`, `maxValue: ""`. Emit a figure only when one is genuinely there;
a hollow object read naively becomes an empty salary rather than no salary.

**6. `jobLocationType: TELECOMMUTE` appears on 10 of 39 ads** and is the only
work-mode signal in the markup. It was **not** corroborated against the ad text,
so treat it as a hint, not as the work mode — judge that from the body and the
location, per the commute rule.

## Applying

Applications go through Michael Page's own flow, and through a consultant. The
plugin does not create accounts and does not fill credential fields — hand the
user the ad URL and their documents.

Worth telling them: an agency ad means a human intermediary, and the employer's
identity usually arrives only after contact.

## Pace

One `list` per search is one request per page, plus one per ad read.
`--with-description` is where the cost is; filter first, read second.
