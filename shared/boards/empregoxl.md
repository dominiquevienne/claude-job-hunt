# Board adapter — Emprego XL (`www.empregoxl.com`, Portugal): a sitemap and a footer that agree because both count the archive, and a dated listing that holds the live

<!-- verified: 2026-09-12 -->

<!-- hosts: www.empregoxl.com, empregoxl.com -->
<!-- script: empregoxl.py -->
<!-- host-forms: www.empregoxl.com -->
<!-- host-forms-basis: read — `empregoxl.py:HOST`, a single literal; the apex serves the same rules and every address the site writes carries `www.` (guard taken on both, 2026-09-12) · 2026-09-12 -->
<!-- countries: PT -->
<!-- content: measured · 84 876 distinct advertisement ids in `sitemap.xml` (ids 486 946 → 580 784, no `<lastmod>`), **and the footer states «84876 Ofertas de Emprego» — equal, and both count the archive**: id 520 128 (10-11-2022) is still served, labelled «mais de 90 dias»; the live window is read from the dated listing — 53 cards on the three newest pages, all 10–12 Sep; `empregoxl.py sitemap` at 11:41 UTC · 2026-09-12 -->
<!-- witness: the footer's own count, read in the same run and printed beside the sitemap's («84 876 emitted, site states 84 876 — equal; both count the archive») — and its drift: 84 875 / 84 875 at 11:35 UTC, 84 876 / 84 876 at 11:41, one advertisement posted between the two reads and both figures moved with it · 2026-09-12 -->

**A Portuguese board that never deletes — 84 876 advertisements in its
sitemap and in its footer on the day, from 2022 to the minute, and a
listing that posts tens a day, most of them from a handful of real-estate
recruiters. Portugal's fourth adapter.** Measured 2026-09-12 11:34–11:42
UTC, every fetch under the declared identity, the guard on the exact path
first.

## Rules, transport, and one route that is dead

```
robots.txt      200, 390 B — `User-agent: *` Disallow /_includes · /_includes/smarty · /_templates/default · /_tools · /_config · /uploads · /admin (two more commented out); seven SEO crawlers named and refused everything; no Sitemap line; no Crawl-delay; certain: True
identity("/")   http, claude-user
GET /                200, 42 349 B — home; footer `<div id="stats"><strong>84875 Ofertas de Emprego</strong>`
GET /sitemap.xml     200 — 92 756 <loc>: 84 875 /emprego/<id>/<slug> · 7 821 /emprego-de/<term>/ · 28 /empregos/… · 20 /emprego-em/<district>/ · chrome; no <lastmod>
GET /empregos        200 — 20 cards, newest first, `<div id="paginacao">` with a 7-page window and « » » to the next; /empregos?p=7 and ?p=8 still on 09 Sep
GET /emprego/<id>/<slug>   200, ~32 kB — JobPosting MICRODATA (itemscope), not JSON-LD
GET /rss/all/        500, 0 B, `server: cloudflare` — the feed the home page links to, dead on the day
```

Behind Cloudflare, 200 to the declared identity on every page read; the
feed alone answers 500 with an empty body. Nothing this adapter reads is
refused.

## The two figures agree — and that is the finding, not the count

```
92 757 <loc> in sitemap.xml: **84 876 distinct advertisement id(s)** (486 946 → 580 784), 7 881 other addresses. No <lastmod>. **This is the archive, not the live inventory** — advertisements from 2022 are still listed and served; use `recent` for what is current.
84 876 emitted, site states 84 876 «Ofertas de Emprego» in its footer — equal; both count the archive.
```

**The sitemap and the footer count the same store, and the store is
everything ever published.** The oldest id in the file, 520 128, opens to a
page published 10-11-2022 with the site's own banner «Este anúncio de
emprego tem mais de 90 dias …» — served, indexed, counted. *Two figures that
agree to the unit are a strong witness for what they measure; here they
measure the archive, and the adapter says so on both lines rather than
letting «equal» read as «live».*

The pair moved together between two reads six minutes apart — 84 875 /
84 875 at 11:35 UTC, 84 876 / 84 876 at 11:41 — one advertisement posted in
between, both counters up by one.

## The live inventory — the dated listing

```
53 card(s) emitted from 3 page(s) of 20 (newest first, oldest kept 2026-09-10); stopped because --max-pages 3 reached — the window may hold more. **The board states no count for this window** — its only figure counts the archive.
```

`/empregos?p=N` serves 20 cards a page, newest first, each with a date
label «12 Sep» — day and month, **no year**. `recent --days N` walks the
pages and stops at the first card older than the window. **The year is
inferred for the stop rule only** (the current year, or the previous one
when the label's month is ahead of today's) **and is never emitted**: the
row carries `posted_label` as printed and `posted: null`; the advertisement
page carries the full `datePosted`. On 2026-09-12, pages 7 and 8 were still
on 09 Sep — ids 580 618 → 580 784 between the 9th and the 12th, so tens
of postings a day, and the 90-day window the site itself labels by would be
thousands of cards; `--max-pages` bounds the walk.

**The board states no live count anywhere read**: the category list in the
listing's sidebar renders `()` empty beside every category, and the only
figure on the site is the archive's.

## The advertisement — microdata, a decoded e-mail, and the site's own age label

```
<div id="job-details" itemscope itemtype="http://schema.org/JobPosting">
  <div id="old-ad"><p>Este anúncio de emprego tem mais de 90 dias ...</p></div>        <- only on old ones
  <div id="applied-to-job"> 0 <p>candidaturas</p></div>
  <h2 itemprop="title">… <img alt="Full-time" /></h2>
  <a itemprop="hiringOrganization" href="http://www.melhoremprego.pt"><span itemprop="name">IOR - Parque das Nações</span></a>   <- linked employer
  <strong itemprop="hiringOrganization">Yupi!</strong>                                                                          <- unlinked employer, the other shape
  <span itemprop="jobLocation"><strong itemprop="addressLocality">Lisboa</strong></span>
  (Publicado em <strong itemprop='datePosted'>12-09-2026</strong>)
  <div id="description" itemprop="description"> … Candidaturas:<br /><a class="__cf_email__" data-cfemail="1765…">[email protected]</a> …</div>
```

**Two employer shapes on the two pages read**, linked and bare — the adapter
reads both. **The description spans an `<a>`** — the employer's application
e-mail, obfuscated by Cloudflare — so a capture that stops at the first
closing tag returns the 1 154-character body cut at the e-mail; the adapter
captures to the element's own closing tag, and decodes the address
(`recrutamento@ior.pt`), because the employer published it for candidates
to write to. `over_90_days: true` when the site's own banner is on the page;
`applications` is the site's counter. Read in full on two: `580783`
(12-09-2026, linked employer, e-mail in the body) and `520128` (10-11-2022,
bare employer, over 90 days).

## Configuration

```yaml
boards:
  empregoxl:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no browser. `recent` is one request per 20 cards;
`sitemap` is two (file, home) and pulls ~10 MB of XML; `ad` is one.

## What is not established

- **The live count** — the site states none; the 90-day window it labels
  by would be thousands of cards, not walked.
- **Whether the listing ever ends** — pages 7 and 8 were read, the window
  keeps advancing; 84 876 / 20 ≈ 4 244 pages if it runs the archive.
- **`/rss/all/`** — 500 on the day; other feeds (`/rss/<category>/`) not
  tried.
- **The `/emprego-de/<term>/` pages** (7 821) — facets, not read.
- **How many of a day's postings are distinct offers** — the newest three
  were the same recruiter's three titles, posted on the 11th and again on
  the 12th under new ids.

## 2026-09-12 — shipped

`empregoxl.py sitemap`: 84 876 distinct, footer states 84 876 — equal, both
the archive. `recent --days 2 --max-pages 3`: 53 cards. `ad` on two. Four
tests; eight mutations on a detached worktree (`python3 -B`), eight red,
each on the test written for it.
