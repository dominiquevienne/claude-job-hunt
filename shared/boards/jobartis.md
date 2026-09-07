# Board adapter — Jobartis (Angola)

<!-- verified: 2026-09-07 -->

<!-- hosts: www.jobartis.com -->
<!-- host-forms: www.jobartis.com -->
<!-- host-forms-basis: read — `jobartis.py:BASE`, a single literal. `info.jobartis.com` is declared as a second sitemap in `/robots.txt` and is never fetched; `m.jobartis.com` is offered to phones and is not used · 2026-09-07 -->
<!-- script: jobartis.py -->
<!-- countries: AO -->
<!-- content: measured · 40 882 advertisements in one gzipped sitemap — 38 588 under `/emprego-<slug>` and 2 294 under a bare `/<slug>`, plus 212 entries that are not advertisements, summing to the file's 41 094 `<loc>`; 216 dated on or after 2026-08-01 · 2026-09-07 -->
<!-- witness: none found — the site publishes no total; 41 094 is the file's own length and 40 882 is what remains after the 212 non-advertisements are named · 2026-09-07 -->

**The largest archive in Angola and the smallest flow.** `angoemprego` holds
1 434 and published 924 since 1 August; this board holds 40 882 and published
**216**. The two other Angolan cards already said the first half of that. What
this adapter adds is that the archive is **bigger than this repository
recorded**, and why nobody noticed.

## Two URL forms, and only one of them had ever been counted

```
/emprego-<slug>    38 588    2 528 distinct dates    2018-01-15 .. 2026-09-06
/<slug>             2 294       60 distinct dates    2018-01-17 .. 2026-07-30
neither               212    home, sign-up, help, search, employer pages
                   ------
                   41 094    = every <loc> in sitemap.xml.gz
```

**`angoemprego.md` and `angolaemprego.md` both record 38 547 for this board.**
That is the `/emprego-` form alone; the same form counts 38 588 today, forty-one
more after two days. **The 2 294 bare-slug advertisements are in neither
figure.**

And they are advertisements — checked by fetching two, not inferred from the
shape. `/anonimo-caixeiro-de-pecas` serves a vacancy with a role, an industry,
a required education and *«&nbsp;Oferta aberta até 30/09/2014&nbsp;»*.

### They are not the same advertisements wearing a second URL

113 slugs appear under both forms, which is the reading that would make the
counts overlap instead of add. **It is wrong.** The pair that was fetched —
`adding-talent-contabilista` under each — is **two different vacancies from
the same employer**: one closing 04/09/2014, the other referenced `Con_2015`
and closing 22/01/2015. *Same employer, same job title, different years.*

*A pattern matching one form returned 94 % of the board and looked complete.*
**A narrow extractor does not return less, it returns false** — and its
silence has the shape of an absence.

## The archive is one import and a trickle

```
/emprego-   busiest day  2018-01-26   7 138   18.5 %
/<slug>     busiest day  2018-01-24     956   41.7 %
```

**2 528 distinct dates, and one January day carries a fifth of the file.** A
high count of distinct dates does not protect against a single import — the
check `angolaemprego.md` passes at 2.8 % is the one this board fails.

The bare-slug corpus is worse and also **frozen**: its most recent entry is
2026-07-30, so it takes nothing new at all.

`lastmod` is present on **40 882 of 40 882**, so `--since` costs one request
and is the flag that makes this board usable.

## One second between requests is too fast for this host

Seven requests about a second apart drew **alternating 503s** — the URL that
failed succeeded twenty seconds later, and a different URL failed in its
place. *That is a rate, not a property of any URL.*

**The adapter paces at five seconds**, and `list` needs exactly one request.
This matters beyond politeness: **a zero, or a refusal, produced by our own
request rate is ours and not the site's**, and it reads identically to the
site's.

*One of those 503s nearly produced a false finding.* A comparison of the two
URL forms reported *«&nbsp;text identical: False&nbsp;»* — but the refused half
had not been written, so a fresh file was being compared against **the
previous slug's page**. The conclusion happened to be right and its evidence
was not.

## The fields, and a state read from two markers

`data-job-id="59272"` is the board's own identifier and the ledger key. There
is **no `ld+json` and no `JobPosting`**: the fields are `data-label` pairs in
Portuguese — contract type, closing date, role, industry, number of posts,
minimum education, years of experience, nationality, languages, functional
area.

**The state is read from two markers and never inferred from one absence.** An
open advertisement carries *«&nbsp;Enviar candidatura&nbsp;»*; a closed one
carries *«&nbsp;Vaga fechada&nbsp;»*. A page with neither reports `null` and
says so in `state_basis`, rather than being called open by default.

## What was exercised, 2026-09-07

```
list                    40 882 advertisements, one request, gzip=True
--form emprego --since 2026-08-01    216
--form bare    --since 2026-08-01      0   (that corpus ends 2026-07-30)
--since 2027-01-01                     0
--search zzzznotaslug                  0
ad  emprego-abreu-...-agricultura   id 59272 · open   · until 2026-10-08
ad  anonimo-caixeiro-de-pecas       id  2707 · closed · until 2014-09-30
ad  a slug that does not exist      exit 3
```

**`.gz` is a name, not a promise.** The adapter decompresses on the magic bytes
and reports which it saw, because a host that stops compressing keeps the file
name.
