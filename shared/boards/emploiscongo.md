# Board adapter — Emplois Congo (RD Congo): a Jobartis site, and a closed archive

<!-- verified: 2026-09-08 -->

<!-- hosts: www.emploiscongo.com -->
<!-- host-forms: www.emploiscongo.com -->
<!-- host-forms-basis: read — `emploiscongo.py:BASE`, a single literal. `info.jobartis.com` is named in this host's own rules file as its second sitemap and is never fetched · 2026-09-08 -->
<!-- script: emploiscongo.py -->
<!-- countries: CD -->
<!-- content: measured · 446 advertisements under `/emploi-<slug>` and **0 under a bare slug**, out of 723 `<loc>`; 92 distinct dates 2019-02-20 → 2026-08-19, of which 23 in 2026 and 1 since 1 August · 2026-09-08 -->
<!-- witness: none published by the site; 446 is the count of single-segment `/emploi-` entries in its own gzipped sitemap, and RD Congo's country page recorded 446 on 2026-09-04 · 2026-09-08 -->

**RD Congo's first adapter.** Its country page recorded seven hosts on
2026-09-04: rank 1 refuses, two are not enumerable, one is a news site, one
holds 18 advertisements all dated the same day. **This is the largest thing
that opens.**

## It is a closed archive, not a dormant board

```
446 advertisements   92 distinct dates   2019-02-20 → 2026-08-19
since 2026-01-01      23
since 2026-07-01       2
since 2026-08-01       1        <- and it is closed
sampled states         7 of 7 closed, the three most recent included
```

**The newest posting already carries *«&nbsp;Offre d'emploi fermée&nbsp;»*.**
*Useful for what an employer has recruited for and when; not useful for
applying* — and the adapter says so on every run rather than returning 446
rows that look live.

*Seven is a sample and not a census.* **What makes it load-bearing is which
seven**: the three most recent are in it, and if anything here were open it
would be the newest.

## The same operator as `jobartis`, and the rules file proves it

`www.emploiscongo.com/robots.txt` and `www.jobartis.com/robots.txt` are
**byte-identical once the first-party host is normalised** — the same eleven
`Disallow`, the same `Allow: //info.jobartis.com`, and the Congolese file
declares `https://info.jobartis.com/…` as its second sitemap **by name**. The
advertisement page carries an `m.jobartis.com` button.

### And `shares-platform:` does NOT apply here — it was written and withdrawn

*In this repository that key asserts **the same postings on both brands**, and
a guard checks it against the two cards' own `countries:`.* **Angola and RD
Congo share no market, so they cannot share advertisements** — the guard said
so, and it was right.

**This is the second time in two days the key has been filled with something
it does not mean.** *The Kosovo pair got it for «same template, different id
spaces»; this got it for «same operator, different countries».* **Both times
the name read as «same platform software» and the key means «same postings».**

The operator relation is real and belongs in prose, which is where it now is.

## What transposed, and the one thing that did not

```
same   /sitemap.xml.gz, gzipped, flat urlset
same   /<prefix>-<slug> advertisements, one segment
same   data-job-id on the advertisement page
same   data-label pairs for the fields
NOT    the second, bare-slug URL form
```

**`jobartis` serves 2 294 advertisements under a bare `/<slug>` beside its
38 588 prefixed ones** — the discovery that corrected two cards on 2026-09-07.
**Here there are zero.** *Checked across the whole file, not assumed from the
shared template.*

> **The template is shared; the defect is not.**

*This is why the deferred entry said «probably, to be verified».* A finding
carried across on the strength of a common operator would have had this
module hunting a form that does not exist — and reporting its absence as a
change in the board.

## The slug is not canonical, and the id is

`emploi-unops-engineer-intern` and
`emploi-unops-engineer-intern-121ff0dd-…-7e24d3e245c1` both return **id
58850**. A genuinely absent slug returns a real 404 and exits 3.

**A ledger keyed on the URL would file one vacancy under as many identities as
there are ways to spell it.** `data-job-id` is the key.

*Found by expecting a truncated slug to be gone and being wrong: the code was
right and the expectation was not.*

## French labels, and entities inside them

`Secteur d&#39;activité` — and **the closed marker itself is
`Offre d&#39;emploi fermée`**. Both key and value pass through
`html.unescape`; matching the raw form would miss every label with an
apostrophe, which in French is most of the interesting ones.

## No state is ever reported as «open»

The closed marker is measured. **An open marker has never been observed on
this host**, because no sampled advertisement was open. `jobartis` uses
*«&nbsp;Enviar candidatura&nbsp;»* and the French template would plausibly say
*«&nbsp;Envoyer candidature&nbsp;»* — **plausibly is not measured, and this
module does not match a string it has never seen.**

So `state` is `"closed"` or `null`, with `state_basis` saying which. The
deadline travels separately, unparsed into a state: *inferring «open» from a
future date would manufacture exactly the claim this refuses.*

**If an open advertisement ever appears here, the marker must be measured
before it is matched.**

## Pacing is inherited, and that is an assumption

Five seconds, carried from `jobartis.py` where one second drew alternating
503s. **Same operator, so the limit is assumed shared** — *assumed, not
measured on this host.* The assumption errs towards slower, which is the safe
direction, and it is written here so a future reader knows it was never
tested.

## What was exercised, 2026-09-08

```
list                        446 ads · 0 bare · 277 non-advertisements · gzip=True
list --fetch --limit 3      3 read · 3 kept · 0 unreadable · 3 closed
list --since 2026-08-01     1
list --since 2027-01-01     0
ad  a truncated slug        exit 0 — it resolves, id 58850
ad  emploi-zzz-…            exit 3, real HTTP 404
ad  zzz-sans-prefixe        exit 3
```

**RD Congo's six other hosts are untouched here**, and the country page's
reserve stands: a country of a hundred million people whose rank-1 board
refuses, measured at a few hundred advertisements. *`www.tala-com.com` is a
browser candidate — 403, 25 bytes, md5 `9ccabba2…` read twice, the fifth
member of the vendor default — and not an HTTP target.*
