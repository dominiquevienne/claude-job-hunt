# Board adapter — Oferta Pune (Kosovo)

<!-- verified: 2026-09-07 -->

<!-- hosts: ofertapune.net -->
<!-- host-forms: ofertapune.net -->
<!-- host-forms-basis: read — `ofertapune.py:BASE`, a single literal; no tenant and no second host · 2026-09-07 -->
<!-- script: ofertapune.py -->
<!-- countries: XK -->
<!-- content: measured · 481 advertisements from one request to the homepage, 481 distinct slugs, 0 unreadable blocks; no sitemap is declared and none was composed · 2026-09-07 -->
<!-- witness: none found — the site states no total, and 481 is the count of rows it rendered rather than a figure it publishes · 2026-09-07 -->

**Kosovo's first adapter.** Its country page named six hosts on 2026-09-04 and
built none: two answer 403 on `/robots.txt` itself, one is a client-rendered
application, one is general classifieds, and two were open and unmeasured.
**This is one of the two, and it serves its whole inventory in one request.**

## What the other Kosovar hosts do, re-measured

```
shpalljepune.com · portalpune.com   403 on /robots.txt — unchanged since 04.09
kastori.net                         open, and see below
kosovajob.com                       open, server-rendered, 617 links — unbuilt
merrjep.com                         general classifieds, not a job board
```

### `kastori.net` — the country page called its sitemap frozen, and it is worse

The page recorded *«&nbsp;le seul sitemap d'annonces du pays porte vingt-quatre
adresses&nbsp;»*, all dated 2025-05-15. **Sixteen months on it is unchanged —
and not one of the twenty-four is an advertisement.**

```
/  /about-us  /blog  /check-email  /companies  /companies/registry
/contact  /faqs  /forgot-password  /login  /me/branches  /me/dashboard
/me/invoices  /me/invoices/status  /me/jobs  /me/jobs/Applications
/me/jobs/create  /me/profile  /me/settings  /offers  /privacy-policy
/register  /terms-and-conditions  /unsubscribed
```

**It is the sitemap of an application's static routes.** *The page's caution —
«&nbsp;ce n'est pas un board à vingt-quatre offres&nbsp;» — was right for the
wrong reason: it is not twenty-four stale advertisements, it is none.*

**And the site is a client-rendered Next.js export**: its root returns
`pageProps` of twenty characters, the navigation labels are drawn by script,
and no job route appears in any HTML served. **`content: indeterminate` for
that host, and no adapter is warranted.**

## One request gives 481 advertisements, complete

**No sitemap is declared and none was composed.** The homepage carries every
row, server-rendered:

```html
<a href="/jobs/<slug>">
  <div class="jobListTitle" date="21.09.2026">Call Agent (Deutsch)</div>
  <div class="saveToFavBtn" ids="109849"></div>
  <div class="jobListTitleComp">Sonnecto</div>
  <div class="jobListExpires">21.09.2026</div>
  <div class="jobListCity">Prishtinë</div>
```

```
481 blocks · 481 distinct slugs · 0 unreadable
ids 481/481 · employer 481/481 · expires 481/481 · city 480/481
```

## The date is an expiry, and there is no posting date at all

`jobListExpires` and the `date=` attribute carry the same value, and the page
offers *«&nbsp;Më njofto para se të skadojë konkursi&nbsp;»* — *notify me
before the competition expires*.

**A reader that took it for `datePosted` would date every advertisement in the
future.** *This board publishes no posting date*, so **`--since` is not
offered**: a filter on a field the source does not carry would silently return
everything, which reads exactly like a board on which nothing is old.
`--expiring-before` filters on what is there.

## The identifier is the board's own, and it was checked

`saveToFavBtn ids="109479"` on the listing, and `/jobs/accounts-receivable-clerk`
**redirects to `/jobs?id=109479`**. *The markup id and the canonical id are the
same number* — verified on one advertisement rather than assumed.

## A pattern that matched a longer word, for the third time today

**`jobListCntsInner` begins with `jobListCnts`.** Splitting the page on the
bare prefix cut every block in two, before its title, and the parser reported
**481 unreadable of 481** — a number its own guard printed rather than
swallowing.

*`<th` counted `<thead` on 2026-09-04; `faqe` — Albanian for «page» — matched
`perfaqesues`, «representative», an hour before this; and this.* **A delimiter
has to say what follows it.**

## No structured data anywhere

`ld+json` is absent from the homepage and from the advertisement, and
`JobPosting` appears zero times. **The parsing is HTML, in Albanian**, and
every field is read from a class name rather than a schema. *This is the first
board in this repository measured on a Balkan host and the first with no
schema at all.*
