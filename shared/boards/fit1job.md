# Board assessment — Fit1Job (Switzerland, Romandie): 5 advertisements, and a retired one that is served in full and carries no structured block

<!-- verified: 2026-10-05 -->

<!-- hosts: fit1job.ch, www.fit1job.ch -->
<!-- script: fit1job.py -->
<!-- countries: CH -->
<!-- content: measured · 5 advertisements emitted against 5 declared by the board's own Yoast job sitemap, identical by MEMBERSHIP and not only by count, and against a cap of 10 that the listing container declares on itself (`data-per_page`) — so the page is not full and the five are the whole board; the route returns no employer (the field is present and empty on all five), no `jobLocation` at all, no salary and no `employmentType`, and the town, canton and contract type exist on the listing card only; a RETIRED advertisement is returned by neither enumerator and still answers HTTP 200, read by `fit1job.py list --fetch` · 2026-10-05 -->
<!-- witness: the Yoast job sitemap `/job_listing-sitemap.xml`, written by a different plugin from the one that renders the listing, so it is not our own extraction under another name — **and it has never been read on a case where the two should differ**, which needs the listing capped at ten and this board has five -->
<!-- closure: detail · the ad page LOSES its `JobPosting` block and still answers 200 with a full 85 kB and no visible notice; the listing and the Yoast job sitemap simply omit it, so neither enumerator can distinguish a retired ad from one that never existed · 2026-10-05 -->

**Requested in #868, and the request's premises were re-measured rather than
repeated.** *Two of them did not hold, and one of the two is the reason this
card is worth more than the board is.*

## The finding: a retired advertisement answers 200 and loses its `JobPosting`

```
GET /poste/program-manager-fr-en-h-f/              200   96 407 B   JobPosting present
GET /poste/chef-fe-de-projet-informatique-fr-en/   200   84 836 B   NONE
```

The second is **the example advertisement of #868 itself**. On 2026-10-05 it
still answers `200` with a complete, ad-shaped page — masthead, menu, footer,
85 KB — and the `JobPosting` block is gone. **There is no visible notice
anywhere in the body**: no «pourvu», no «expiré», nothing a reader could see.
It appears in neither enumerator: not in `/les-postes/`, not in the job
sitemap.

> **So on this board «the ad page is still up» carries no information at all,
> and the discriminant is the presence of the structured block.** *That is
> `shared/ats-open-check.md` step 1b, in one measured case, on a host whose
> markup makes the signal mechanical.*

*WP Job Manager emits the structured block for a published listing and drops it
when the listing is unpublished; nothing else on the page changes. The
`<title>`, the breadcrumb and Yoast's own `WebPage` block are all still there
and still parse — which is why `_ldjson.absent_reason()` returns
`no-jobposting` with `our_fault=False` rather than a reading failure.* **The
adapter reports `retired` only on that value**: a page we failed to read can
never be reported as a position that closed.

### And `validThrough` is not what retires an advertisement here

The board does publish and maintain `validThrough` — measured on all five live
advertisements, 42 to 61 days after `datePosted`, and the oldest of the five
expires **tonight**:

| id | `datePosted` | `validThrough` | status 2026-10-05 |
| :-- | :-- | :-- | :-- |
| 6328 | 2026-09-29 | 2026-11-29 | listed |
| 6302 | 2026-09-10 | 2026-11-01 | listed |
| 6299 | 2026-09-04 | 2026-10-27 | listed |
| 6295 | 2026-08-31 | 2026-10-20 | listed |
| 6290 | 2026-08-24 | **2026-10-05** | listed |

**The retired one was retired with weeks of its horizon left.** *#868 reports
reading `validThrough 2026-11-17` on it on 2026-09-22 — **reported by the
issue, not re-measurable now**, because the block that carried it is exactly
what disappeared; it is consistent with the 42-to-61-day spread above and it is
still a figure this card did not take.* What **is** measured today is that it
is retired while an advertisement posted five weeks earlier is still listed.

> **Retirement is the agency unpublishing a filled position, not an expiry date
> arriving.** *A consumer that trusted `validThrough` would have held this
> advertisement open for another six weeks; a consumer that trusted the HTTP
> code would hold it open forever.*

## Open by plain HTTP — no browser, no key, no cookie

```
GET /les-postes/                  200    87 626 B
GET /categorie-poste/it/          200    84 709 B
GET /job_listing-sitemap.xml      200     2 141 B
GET <advertisement>               200    ~96 000 B
```

`robots.txt` read 2026-10-05 (`state: read`, `certain: True`): a WPForms block
disallowing `/wp-content/uploads/wpforms/`, and a Yoast block whose `Disallow:`
is **empty** — which permits. **No `Crawl-delay` anywhere in the file, for `*` or for
any named agent**, so this host asks for no rate: the adapter paces itself at **1 s**
between requests and prints that provenance on its first line — *«1s, this adapter's own
spacing — www.fit1job.ch asks for nothing»*. **A host that sets no rate is not a host
that wants none asked of it.** *Guard taken on `/`, `/robots.txt`,
`/les-postes/`, `/categorie-poste/it/`, `/job_listing-sitemap.xml`,
`/les-postes/page/2/` and four advertisement paths, on both host forms, in a
turn of its own before anything was fetched.* **The apex redirects to `www.`:
the host that answered is `www.fit1job.ch` on every form.**

## The two premises of #868 that did not hold

- *«Each ad page carries a `JobPosting` JSON-LD block»* — **every LISTED one
  does, and the retired one carries none.** The sentence is true of the board's
  live set and false of its URL space, and that difference is the finding
  above. *It is not an error in the report: it was true of every page the
  reporter looked at.*
- *«Stable per-ad id? the URL slug»* — **there is a numeric id**, published
  twice per card: `data-job_id="6328"` on the `<li>` and `post-6328` in the
  anchor's class list. It is the WordPress post id. The adapter keys on it and
  carries the slug beside it, because the canonical URL is rebuilt from the
  slug.

## Two traps in the markup, both of which produce a plausible wrong answer

**The cards nest a `<ul>` of `<li>`s inside each card.** A non-greedy
`<li\s+data-longitude=.*?</li>` therefore ends at the card's own *location*
item: it finds the right number of cards and truncates each one before its
date. *Measured while writing this: five cards, five correct titles, five
correct towns, and `None` for the date on all five* — **which reads exactly
like a board that publishes no dates.** The bound that works is the anchor's
close, `</a></li>`, and each card holds exactly one `</a>`, one
`<time datetime=` and one `location-on`.

**The job sitemap contains the archive page.** `/les-postes/` is one of its six
`<loc>` entries, so counting `<loc>` declares one advertisement more than
exists. Anything that is not `/poste/<slug>/` is dropped before counting.

## What the route does not return

- **The employer, ever.** `hiringOrganization.name` is `""` and the card's
  `data-company` is `""` on all five — *a field that is present and empty,
  which `if x` cannot distinguish from a field that is absent.* The texts
  describe the client (*«notre client, situé dans la banlieue de Fribourg»*)
  and never name it. **So the ledger's employer dedup does not work on these
  rows**, and the adapter invents nothing from the host name.
- **No `jobLocation` in the structured data at all** — the town and canton are
  on the listing card only. *Checked for the Batiactu trap, where a region came
  from the employer's head office and a third of a page was 300 km away: the
  five towns are five different ones across three cantons (Fribourg, Genève ×2,
  Valais, Vaud) and only one is the agency's own, so the place is the job's.*
- **No salary and no `employmentType`.** The contract type is a card class,
  `data-job_type_class="fixe"` on all five.

## What it adds, given that jobup already carries these advertisements

**Coverage is not the answer**: #868 says the ads are mirrored on jobup and
syndicated to job-room through it, so a user sweeping jobup already sees them.
What this adapter adds is the retirement signal above, the maintained
`validThrough`, and the dossier rule for an agency that never names its client.

*And the board is small by nature rather than by accident — a Romandie IT
recruitment agency, five simultaneous mandates. «Small» is not a reason to
decline a board* (`2 sexies`: the default is that we use it).

## What is not established, and is not assumed here

- **The `load_more_jobs` route on `admin-ajax.php` has never been called.** The
  listing has never been full, so the capped branch has never fired against the
  live host; the suite exercises it on a fixture and the adapter says `capped`
  rather than pretending completeness.
- **The witness has never been read on a divergence.** Both sides say five
  today. The case where they should differ needs ten advertisements.
- **`lastmod` in the sitemap equalled `datePosted` to the second on one
  advertisement** (6328, `2026-09-29T17:27:24`). *One match is not a rule*, so
  the date is read from the card and from the advertisement, never from
  `lastmod`.
- **The keyword / place / category search form was not exercised.** The
  category pages list everything without a query, so nothing needed it.
