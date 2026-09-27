# Board measurement — MyWorld Careers Laos (`laos.myworld-careers.com`): the agency's Vientiane front, and **NOT the same build as its Myanmar one**. The issue proposed one script per `--host`; measurement refuses it. Adapter `myworldla.py` (#655)

<!-- verified: 2026-09-27 -->

<!-- hosts: laos.myworld-careers.com -->
<!-- script: myworldla.py -->
<!-- countries: LA -->
<!-- route: http -->
<!-- content: measured · **the rules file is served (`state: read`, `certain: True`), writes NO Crawl-delay (2 s are ours) and NAMES `https://laos.myworld-careers.com/sitemap.xml`, which answers 200, 37 086 B — 179 `<loc>`, every one with a `lastmod`, of which 44 adverts under `/jobs/`; `/jobs` answers 200, 25 137 B and carries NO advert link, which is why the sitemap is the route; each advert carries a `JobPosting` JSON-LD beside a second `WebSite` block, and its `baseSalary.currency` reads GBP on a salary the same object prints in LAK** · 2026-09-27 -->
<!-- witness: 44 adverts named by the site's own sitemap against the emitted count; the walk's invariant is emitted + unreachable == named · 2026-09-27 -->

**Measured 2026-09-26 19:2x UTC – 2026-09-27 03:4x UTC by the declared client, the
guard on the exact path; the adapter exercised against the host.**

## Why this is a second script and not a `--host` flag

#655 proposed «&nbsp;un même script par `--host` pour les fronts de l'agence&nbsp;».
Measured on both fronts:

```
styles_metaLabel__ / styles_metaValue__   Myanmar: every field   Laos: 0
the page's labelled field pairs           Myanmar: 5 per advert  Laos: absent
/jobs listing                             Myanmar: 56 887 B      Laos: 25 137 B, no advert link
```

**A `--host` flag over `myworldmm.py` would have produced a reader returning
`None` on every field** — «a reader inherited from the neighbour returns `None`,
not an error». *What the fronts DO share is the approach — a sitemap named in the
rules file — and the agency's `TMY…`/`ASI…`/`EPHYO…` consultant codes.* **Sharing
a markup is not sharing a meaning, and here they do not even share the markup.**

## The structured salary is wrong on both fronts, in two different ways

```
Myanmar   baseSalary  {"currency": "£",   "value": {"minValue": 4}}      <- the number truncated
Laos      baseSalary  {"currency": "GBP", "value": {"value": "Up to 45,000,000 LAK + Allowances"}}
Laos page Salary      Up to 45,000,000 LAK + Allowances                 <- the string agrees
```

Here the *string* is right and the **currency field is wrong**. There the number
itself was corrupt. **The rule covering both: carry the salary as the site prints
it, and never carry `baseSalary.currency`** — one vendor writing a British
currency on South-East Asian salaries, twice. *And «45,000,000» is eight digits,
so the salary is a labelled field the telephone rule must not touch.*

## Three fields that parse cleanly and mean nothing

**`employmentType` is the literal string «undefined»** on every advert read — a
JavaScript artefact. *Worse than absent: `if x` keeps it.* Dropped, and the run
says how many carried it.

**`jobLocation` smears one string across every address field**: `streetAddress`,
`addressLocality`, `addressRegion` **and** `addressCountry` all read «Pakxe,
Laos», `postalCode` «-». Carrying `addressCountry` would publish a town as a
country. One field is carried and `location_fields_identical` records that they
agreed, **so a front that one day fills them properly appears as a disagreement
rather than passing unnoticed.**

**And the page carries TWO `ld+json` blocks**, the non-JobPosting one first. The
choice is explicit on `@type`; the string filter beside it is an optimisation,
not the protection — *the mutation that removes only the filter leaves the guard
green.*

## A filter tested in one direction cost two adverts of forty-four

The reference code was read as `[A-Z]{2,4}` because every sample seen was three
letters (`TMY`, `ASI`, `EMI`). **`EPHYO` is five**, so two adverts were dropped in
silence: the walk stayed coherent, the sitemap's own count fell with it, and the
emitted-equals-named invariant held **because both sides shrank together**. *The
tell was a number written down earlier (44) disagreeing with a number the run
printed (42).*

**WITHHELD:** e-mail addresses and telephone numbers in free text; the agency's
consultants are never contacted. The employer is anonymised by the agency —
`employer` is null **by measurement**, `employer_anonymised` says so, and the
agency travels under its own name.
