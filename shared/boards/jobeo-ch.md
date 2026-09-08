# Assessed, adapter not built — Jobeo.ch (Switzerland)

<!-- verified: 2026-09-08 -->

<!-- hosts: www.jobeo.ch -->
<!-- script: none -->
<!-- countries: CH -->
<!-- content: measured · the board declares 1 130 advertisements and exactly 20 are reachable by any route its `robots.txt` permits — every query parameter tried returns the identical first twenty, and pagination lives behind `/jobsearch/api/`, which is disallowed · 2026-09-08 -->
<!-- witness: served by the site — `"total":1130` in the listing's own payload, present and identical on `/jobs` and on `/jobs?page=2` · 2026-09-08 -->

**The Swiss staffing-agency board, and it reaches us today only by ricochet:**
an LHH advertisement matching the candidate's profile arrived because
`job-room` syndicates it. *The day the ricochet stops, the advertisements
simply stop appearing — no error, no zero, no symptom.*

## The reachable surface is 20 of 1 130, and that is the finding

```
"total":1130            the board's own figure, in the listing payload
/jobs                   20 advertisements
/jobs?page=2            20 — THE SAME 20, all twenty shared
/jobs?p=2               idem      /jobs?offset=20   idem
/jobs?pageSize=150      idem      (150 is offered in the page's own pageSizeList)
```

> **No query parameter moves the window.** *Pagination is an API call, and
> `robots.txt` disallows `/api/` and `/jobsearch/api/`.*

**And the rules are precise about it:**

```
Disallow: *?*           every query string, everywhere
Allow:    /jobs?*       except on this path
Disallow: /api/  ·  Disallow: /jobsearch/api/
```

*So `/jobsearch/offers?page=2` is refused outright while `/jobs?page=2` is
permitted — and permitted or not, both return the same twenty.*

**This is the same shape as `meteojob.md`**, whose card records one search page
and no licit pagination. *The listing payload names `app.meteojob.title`: the
two boards run the same engine, and the constraint is the engine's.*

> **An adapter here would emit 20 and the board would hold 1 130.** *That is
> issue #181 in its worst form — not a zero, a plausible number — and the site
> hands us the figure that contradicts it. **Naming the ratio is worth more
> than shipping the 1.8 %.***

## Two facts the prior investigation had wrong

**`identifier` is not a GUID.** It is a `PropertyValue`, and its `value`
changes in KIND between advertisements:

```
REF6151Y   the employer's own reference   (HUG)
711290     jobeo's own numeric id          (Cie Chemin de Fer et d'Autobus SMC SA)
711376     jobeo's own numeric id          (m b d sa architectes sia)
```

*So `identifier.value` is whatever the source supplied and cannot be the ledger
key.* **The trailing number of the advertisement slug is jobeo's own and is
consistent across the three read** — that is the candidate key, and it has been
checked on three advertisements, not on the board.

**`hiringOrganization` is not always the agency.** *On these three it is the
real employer — HUG is Geneva's university hospitals.* **The agency case is
real and is not universal**, so an adapter must not blank the field by rule; it
must carry the field and say it is the poster, which on this board is sometimes
the employer and sometimes the intermediary.

## `datePosted` is a re-stamp, and the ledger must not read it as a publication date

```
2026-09-08T01:07:04.408Z
2026-09-08T05:50:40.649Z
2026-09-08T05:52:02.657Z     <- 82 seconds after the previous one
```

**Three advertisements, three timestamps, all today, milliseconds included.**
*Two of them 82 seconds apart is an ingest cadence, not three employers
publishing at dawn.*

**And it explains the divergence the issue flagged**: `job-room` dates the same
LHH advertisement 2026-08-10 and jobeo dates it 2026-09-07. *Four weeks apart,
and now we know which one moves.*

> **Record it as «&nbsp;the date jobeo declares&nbsp;», never as the posting
> date.** *A date wrong in the «&nbsp;more recent&nbsp;» direction floats the
> advertisement to the top of every freshness sort — the family of #84.*

**`validThrough` is absent**, reconfirmed on all three.

## What is established about access

Guard taken 2026-09-08 on each path: `/`, `/jobs`, `/jobsearch/offers`, the
advertisement paths and the sitemaps all answer `read`, `allowed=True`,
`certain=True`. **The listing is server-rendered** — its data sits in an
HTML-encoded JSON blob where `&q;` stands for `"` — so no browser is needed.

**The sitemap is four children.** `/sitemap-jobs-portals.xml` holds **477
employer portal pages** (`/Emploi-<Employer>`) and **no advertisement**;
`/sitemap/sitemap-1.xml` answers 404. *An employer portal was opened and
carries no advertisement in the listing's format* — so the `kariera` route,
reaching ads through employer pages, does not transpose here on the one page
read.

## What is not established

- **whether any licit route reaches beyond the twenty** — the sitemap, the
  employer portals and every query parameter tried have been ruled out, and
  that is not the same as proving none exists;
- **the slug id as a stable key**: three advertisements, not a board;
- **nothing about the 477 employer portals** beyond the one opened.
