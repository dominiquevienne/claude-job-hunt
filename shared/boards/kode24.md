# Board adapter — kode24 jobs / kodejobb.no (Norway): the developers' newspaper's board lives on its own host, one list page of every open ad under the menu's «Alle stillinger 16» — 16 emitted, equal

<!-- verified: 2026-09-14 -->

<!-- hosts: kodejobb.no, www.kodejobb.no, www.kode24.no -->
<!-- script: kode24.py -->
<!-- host-forms: kodejobb.no -->
<!-- host-forms-basis: read — `kode24.py:HOST`, a single literal; `www.kode24.no` is the newspaper that links here and `www.kodejobb.no` redirects to the bare host · 2026-09-14 -->
<!-- countries: NO -->
<!-- content: measured · **16 emitted over 1 page by `kode24.py list` (02:55 UTC), the menu states «Alle stillinger 16» — equal; every card carries a title, an employer, at least one place and a deadline; one ad read (JobPosting + 6 015 characters of prose)** · 2026-09-14 -->
<!-- witness: the list page's own menu badge «Alle stillinger N», read on the one page and printed beside the emitted count — «N emitted over 1 page, site states N — equal», exit 6 on a gap · 2026-09-14 -->

**The board is not on kode24.no.** The newspaper for Norwegian developers
(`www.kode24.no`, a 708 KB front page of articles) links its job menu to
`www.kodejobb.no/stillinger`, and `/jobb` on the newspaper redirects to
`https://kodejobb.no/`. **The board is `kodejobb.no`** — a Next.js site on
a Sanity back end whose `/stillinger` serves every open ad server-rendered
in `ul#job-list` (16 cards on 2026-09-14), with the menu badge **«Alle
stillinger 16»** as the count it states. No pager: the list is the
inventory. No key, no cookie, no browser. Issue #367 (Norway; #291 bloc C
had read the newspaper's rules and root, not the board's).

## The list, and the walk

```
16 emitted over 1 page, site states 16 («Alle stillinger») — equal.
```

A card: the employer's own title (`job-title-from-customer`), the
employer, a one-line subtitle, the places (each rendered twice for the
light and dark themes — emitted once: «Oslo», «Oslo, Delvis
hjemmekontor», «Remote», one ad with nine Norwegian cities), the deadline
as the site writes it («om 13 dager», emitted as `deadline_text`), a «Ny»
badge. 2026-09-14: 16 cards, 16 distinct uuids, all «Ny». A small board —
a segment (developers) that NAV Arbeidsplassen and Jobbnorge do not carry
as such, and the reason the issue was chosen.

## The ad page

`/stillinger/<employer-slug>/<uuid>`: a `JobPosting` in JSON-LD — title,
a one-line description, datePosted, validThrough, employmentType,
hiringOrganization, jobLocation — and the prose: «Firma»,
«Stillingstittel», «Arbeidssted», «Frist: 27.9.2026» (d.m.yyyy → ISO) and
the body (`description`, 2 662 and 6 015 characters on the two ads read).
The «Søk på jobben» button leads off-site; nothing behind it is read.

## The rules

`www.kode24.no/robots.txt` (24 B, 2026-09-14): `User-agent: * / Disallow:`
— nothing refused. `kodejobb.no/robots.txt`: **404** (the site's own
Next.js 404 page) — no rules, `certain: True`. The guard is taken on the
exact path before every request; 3 s own spacing.

## What is withheld

Addresses and phone numbers in the prose are replaced (`[e-mail
withheld]`, `[phone withheld]` — eight digits or more, Norwegian numbers
are eight). The board's own `kode24@hsmedia.no` sits in its footer, in no
field this file emits.

## Invocation

```
kode24.py list                                   # every open ad, one page: 16 emitted, site states 16 — equal (2026-09-14)
kode24.py ad --url https://kodejobb.no/stillinger/sikt/dce440d1-da61-4d3b-b091-1dd90b2354a2
```

Exits: 2 broken (a malformed URL) · 3 gone (404, or no JobPosting) · 6
partial (a list short of the menu's count, HTTP ≠ 200, a menu without the
count) · 7 refused by the rules · 8 rules undecidable.
