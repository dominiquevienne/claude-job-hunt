# Board adapter — Burundi Jobs (Burundi)

<!-- verified: 2026-09-07 -->

<!-- hosts: www.burundijobs.bi -->
<!-- script: burundijobs.py -->
<!-- countries: BI -->
<!-- content: measured · 52 live advertisements of 160 sitemap entries, every one of the 160 fetched once; 52/52 carry a JobPosting; 24 of the 52 titles read as procurement · 2026-09-07 -->
<!-- witness: none found — the site serves no counter, and the 52 is our own reading of all 160 entries rather than a figure the board states. **A total this adapter computed is not a total anybody confirmed**; the only second source that would settle it is a site-served count, and there is none · 2026-09-07 -->

**Burundi had no adapter at all until today**, and this host was not
undiscovered — it was **reported closed by our own guard**.

```
burundijobs.py list                                # the sitemap alone, one request
burundijobs.py list --limit 20 --fetch             # newest first, dead entries dropped
burundijobs.py list --limit 40 --fetch --jobs-only # and procurement notices dropped
burundijobs.py ad --slug ingenieur-des-travaux
```

## It was classed "refuses at transport" for two days, and it never refused

*Recorded by the pilot session on 2026-09-07, and kept here because it is the
part of this board's story that our own files caused.*

This host sat in a population of nineteen filed as *the rules open and the
transport refuses*. **That measurement was taken by a tool that sent a Chrome
`User-Agent` and returned success on any HTTP code**, and it left no provenance
record. Re-measured on 2026-09-07 with the declared identity and a record,
**four of the nineteen answered 200. This is one of them.**

**The lesson is not "re-verify": it is that both faults of that tool pushed
toward the same conclusion.** A browser identity passes where ours would be
refused, and a success on any code turns a refusal into a body.

```
GET /            200, 237 083 o, « offres d'emplois - burundijobs »   (pilot, 2026-09-07)
GET /robots.txt  200, 2 012 o, md5 ce7b5a2e05dc — the managed block
                 `claudebot` named once · `claude-user` named zero times
```

## And then our own guard kept it shut for two more days

**Two decisions, and only the second one reaches an adapter.**

The owner's decision of **2026-09-05** — *one permitted token is enough* — is
implemented in `identity()`, which has answered `claude-user · http` for this
host since. **But every `gate()` in this repository calls `allowed()`**, whose
default still unioned six names we might be *called*, four of which we never
send. So the module knew the host was open and refused it anyway, in the
function adapters actually ask.

The decision of **2026-09-07** — *a named refusal binds the token it names and
no other* — aligned `allowed()` on `identity()`. **This adapter is the first
written because of that**, and the gap between the two dates is the whole
reason there was nothing here yesterday.

## The candidate sitemap is not read, and that is a decision

`sitemap_index.xml` declares eight children. One of them is
`iwj_candidate-sitemap.xml`: **people looking for work.** Nothing here needs
it, the rules do not distinguish it from any other path, and *the rules permit
it* is not a reason to read something. The adapter names one child file and
never composes another.

*This is also the wildcard trap in its other form.* Aggregating
`iwj_*-sitemap.xml` would have swept candidates into a job ledger — the same
shape as `merojob`, where a sibling file held 15 940 tenders.

## The sitemap is an archive index, not a list of live pages

Every one of the 160 entries was fetched once, paced at one request a second,
on 2026-09-07:

```
160 <loc>, 160 distinct, all /job/<slug>/
     52  HTTP 200   -- and 52 of 52 carry a JobPosting
    108  HTTP 404   -- listed in the sitemap, gone from the site
```

**And `lastmod` does not predict which is which.** August 2026 holds 25 live
entries and 33 dead ones; one September entry is already gone. *So `--since`
narrows the list and cannot replace fetching* — a freshness filter here tells
you when the file was touched, not whether the page exists.

```
live  by lastmod   2025-10 ×1   2026-08 ×25   2026-09 ×26
dead  by lastmod   2024-01 ×1   2026-05 ×9    2026-06 ×43
                   2026-07 ×21  2026-08 ×33   2026-09 ×1
```

**So the file's length is not the board's size**, and the gap is not the
off-by-one this repository has seen three times — it is most of the file.

**Order matters more here than anywhere else.** The file is oldest-first and
the old end is dead, so `--limit 20` on the served order would return twenty
404s and read like a broken board. The adapter sorts newest-first before it
limits.

## Two fields are present and wrong, and neither is emitted

The InWave Jobs theme fills a `JobPosting`, and two of its fields carry the
template's defaults rather than the advertisement's facts:

```
baseSalary.currency   XPF  — the CFP franc, of French Polynesia and New
                             Caledonia. Burundi uses BIF.
baseSalary.value      the string "négociable" — not a number
addressCountry        a province: "Muramvya", "Plusieurs provinces"
```

**A field present and wrong is worse than one absent**: *négociable XPF* on a
Burundian advertisement would enter the ledger looking like data, and nothing
downstream would question a currency code. Neither is emitted.

What the page wrote about place is kept verbatim as `place_as_written`, so
nothing is discarded — it is simply not called a country. `countries` is
`["BI"]`, which is the fact we actually have.

`employmentType` and `industry` are absent from every sampled posting, so there
is nothing to decide about them. **What a field is worth is a property of the
board**, not of the vocabulary.

## Procurement notices sit among the advertisements

`avis d'appel d'offres`, `demande d'offre de service`, `fourniture des kits
scolaires` — this board carries tenders in the same sitemap as its vacancies,
the way `jobsnepal` does at 31 %.

**They are counted and reported; they are not silently filtered.** The share
travels in the output as `tender_like`, and `--jobs-only` drops them.

**The test is lexical and French, and it is declared as such in the flag's own
help.** Its limits are demonstrable rather than hypothetical: *"Appel à projets
pour soutenir les initiatives entrepreneuriales"* — measured on this board,
2026-09-07 — is **not** a vacancy and the pattern does **not** catch it. A
semantic defect does not yield to a predicate; that is why the count is
published beside the filter and the filter is never the default.

## The `[d]` fallback, and why it is written down

The theme emits its `JobPosting` as a **bare top-level object with no
`@graph`**. A reader that only walks `@graph` reports *no structured data here*
on every single advertisement — which is exactly what happened during this
adapter's own measurement, and it looked like a board that publishes none.

**A parser missing one shape does not return less; it returns a confident
zero.**

## Shape, and the family it belongs to

**WP Job Manager**, the same family as `jobsearchzm.md` and `jobzambia.md` — which is why `/job/<slug>/` and a `job_listing`-style sitemap were the right things to look for. *The family suggested where to look; every figure above comes from reading, not from the family.*

## Pace

One request per second, ours — the host declares no `Crawl-delay`, and the
floor is declared as ours rather than presented as the host's.
