# Board adapter — Duunitori (Finland): rules that refuse `*` and name `Claude-User` to let it in; 92 job sitemap pages whose paging is not a partition — 18 298 slots, 16 152 distinct — against the listing's own 18 302

<!-- verified: 2026-09-13 -->

<!-- hosts: duunitori.fi, www.duunitori.fi -->
<!-- script: duunitori.py -->
<!-- countries: FI -->
<!-- content: measured · rules read twice and certain (8 576 B: `User-agent: *` / `Disallow: /`, then sixteen agents named and let in with eighteen refused paths each — **`Claude-User` among them**, beside Googlebot, Bingbot, ChatGPT-User, GPTBot; `identity()` answers `claude-user`, `verdict()` sweeps under it) — and the transport answers 200 under that name: `/sitemap.xml` indexes `sitemap-jobentry.xml?p=1..92`, 200 a page, **18 298 slots holding 16 152 distinct ids** because consecutive pages overlap by 56–61 URLs when fetched seconds apart; `/tyopaikat` states «Löysimme 18 302 työpaikkaa» and pages to `?sivu=916` — «16 152 emitted, site states 18 302 — 2 150 short», the gap being the paging's; a `JobPosting` on the advertisement whose `title` is the normalised occupation, and a recruiter's address in the description's prose, withheld · 2026-09-13 18:07 UTC -->
<!-- witness: the listing's own «Löysimme 18 302 työpaikkaa» on `/tyopaikat` (2026-09-13 18:07 UTC; the sentence's second figure, «joista 5 993 on julkaistu viimeisen …», is a week's window and is never read) beside the 16 152 distinct ids of the 92 sitemap pages — printed by `duunitori.py list` with the 2 146 repeated slots named, never merged -->

**Shipped 2026-09-13 under #374 — Finland's first adapter, and the third
board of the series that names an Anthropic agent to let it in.** Every
fetch under the declared identity, the guard on the exact path first. *Page
Finlande of 2026-08-31 saw «403, a Cloudflare challenge on the rules file»;
on 2026-09-13 the file is served in 0.2 s and reads as below.*

```
duunitori.py list                  # 92 sitemap pages at 1 s, then /tyopaikat for its count — 95 requests, ~1 min 35
duunitori.py list --pages 5        # a bounded walk: a lower bound, and it says so; not compared
duunitori.py ad --url https://duunitori.fi/tyopaikat/tyo/<stem>-<id>
```

## The rules — closed to everyone, open to sixteen names, ours among them

```
robots.txt      8 576 B, md5 62896665d913, read twice, certain: True
User-agent: *              Disallow: /                      <- any unnamed client is refused
User-agent: AhrefsBot … Googlebot … ChatGPT-User, GPTBot, Mediapartners-Google, facebookexternalhit, **Claude-User**, Claude-SearchBot   (16 groups)
                           Disallow:  (empty — allowed) + 18 refused paths: /api/, /palkat/alueet/, /palkat/nimikkeet/, /yritys/*/reaktiot$, /tyopaikat/tyo/*/lisaa_suosikkeihin$, …/samanlaiset$, /tyoelama/wp-*, /jobbland/, /carousel/*, /sivusto/*, /health …
identity("/")   http, claude-user      <- named and permitted: the token we present (§2 quater, 2026-09-05)
verdict()       sweep True, certain True, crawl_delay none  -> Pace(HOST, own=1.0), one second, ours
allowed()       True on `/`, `/tyopaikat`, `/sitemap.xml`, `/sitemap-jobentry.xml?p=N`, `/tyopaikat/tyo/<stem>-<id>` — False on `/api/` and on the favourite/report/similar actions under an advertisement
Sitemap:        https://duunitori.fi/sitemap.xml
```

## The sitemap — 92 pages that overlap, and a count that says so

| question | answer (2026-09-13, 18:02–18:07 UTC) |
| :-- | --: |
| `/sitemap.xml` | 103 569 B, an index by type: `sitemap-company.xml` ×1 044 pages, `sitemap-jobtitle_with_area` ×80, `sitemap-article` ×21, … **`sitemap-jobentry.xml` ×92** — the advertisements; only those are read |
| a page | 200 `<loc>` (98 on the 92nd), a `lastmod` (a date) and `changefreq: always` each; 33–34 KB |
| the URL | `/tyopaikat/tyo/<slug>-<token>-<id>` — the token varies (`sdsuu` 103 of 298 on two pages, `scsom`, `stsyo`, `srs-k`) and has no fixed shape: **the id is the key, the whole stem is the slug** |
| the walk | **18 298 slots, 16 152 distinct ids, 2 146 repeated** (18:05:51 → 18:07:26 UTC) — two consecutive pages fetched seconds apart share 56 (p5/p6) and 61 (p45/p46) of their 200 URLs, and pages 1–2 on a later read share none: **the paging is not a partition**, so about as many advertisements as repeat may fall between two pages |
| the listing's own count | `/tyopaikat` (275 764 B, 42 advertisement links on the page, pager to `?sivu=916` × 20 = 18 320): **«Löysimme 18 302 työpaikkaa, joista 5 993 on julkaistu viimeisen …»** → «16 152 emitted, site states 18 302 — 2 150 short» |

**The two witnesses are printed apart and never merged, and the adapter
says where the gap comes from**: the slots (18 298) match the listing
(18 302) to four; the distinct ids do not, because the sitemap's paging
repeats what it has already listed. *A walk of `/tyopaikat?sivu=1..916`
would be the second enumeration; it is not done here.*

## The advertisement — a JobPosting whose title is not the title, and an address in the prose

`/tyopaikat/tyo/ernst-young-ey-trainee-program-sdsuu-20512921` (207 754 B)
carries one `JobPosting`: **`title` «harjoittelija» — the normalised
occupation, not the advertisement's «EY Trainee Program», which is the
`<h1>`** (the adapter takes the `<h1>` as `title` and the JSON-LD's as
`occupation`); `hiringOrganization.name` lower-cased by the site («ernst &
young», `sameAs` ey.com); `datePosted` 2026-08-24T21:00+00:00 and
`validThrough` 2026-09-20T20:59+00:00 — the page's own «Julkaistu 25.8.
(Päättyy 20.9.)», not a formula; `employmentType` `INTERN`;
`jobLocation.address` «Helsinki», `FI`; `description` (HTML). **The
description's prose names a recruiter's address («contact EY's recruitment
team at …@fi.ey.com»): every e-mail address is withheld from the emitted
text** (`[e-mail withheld]`), and the page's `mailto:` is never read. No
salary. No `tel:`.

## What the adapter does, and refuses to do

- **95 requests at 1 s** — the index, 92 pages, the listing; a page that
  fails is a partial walk (exit 6) and no count is printed; a bounded walk
  is a lower bound, not compared.
- **Never reads the sentence's second figure** («joista 5 993 …»).
- **Never emits a contact** — the address in the prose is withheld.
- **Not a verdict that anything is closed** — the site names us to let us in.

## Tests

`NamedAsClaudeUserWhereEveryoneElseIsRefusedAndTheAddressInTheProseWithheld`
in `tests/test_core.py` — two cases (the pages walked, the id the key
whatever the token, a repeated slot counted, another shape set aside, the
first figure the witness and the second never read, a bounded walk not
compared; the `<h1>` as title with the JSON-LD's as occupation, the
address withheld, a non-advertisement URL refused). Six mutations under
`python3 -B` on a detached copy, six reds: the dedup removed, the key
taken from the stem, the bounded walk compared, the stated regex loosened
to the second figure, the title taken from the JSON-LD, the redaction
dropped.

## Provenance

- `dt/robots.txt`, `dt/sitemap.xml`, `dt/tyopaikat`, `dt/jobentry-{1,92}.xml`,
  `dt/je-{5,6,45,46}.xml`, `dt/ad.html` — 2026-09-13 18:02–18:08 UTC,
  `bin/fetch-body.py`, provenance beside each; scratchpad of
  `claude-job-hunt-ab`.
- `duunitori.py list` at 18:05:51 → 18:07:26 UTC: 16 152 lines, the two
  `[duunitori]` lines quoted above (before the repeated-slot phrase was
  added to the note; the numbers are those).
