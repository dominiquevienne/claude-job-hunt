# Board adapter — Youthall (`www.youthall.com`, Türkiye — internships, young-graduate programmes and entry jobs): the listing walked page after page to its empty page, the job sitemap as the second enumeration — 28 emitted, 28 listed, equal on 2026-09-20; the advert's own JobPosting

<!-- verified: 2026-09-20 -->

<!-- hosts: www.youthall.com, youthall.com -->
<!-- script: youthall.py -->
<!-- host-forms: www.youthall.com -->
<!-- host-forms-basis: read — `youthall.py:HOST`, a single literal; every request checked against it before it leaves · 2026-09-20 -->
<!-- countries: TR -->
<!-- content: measured · **28 emitted over 2 pages by `youthall.py jobs` (14:44 UTC), `sitemap.tr-jobs.xml` lists 28 — equal; 27 on 2026-09-13 (the issue's count). Rules (`/robots.txt`, 3 626 B, 17 groups): `Claude-User` and `Claude-SearchBot` Allow: / by name, `ClaudeBot` and `anthropic-ai` Disallow: / by name, `*` Allow: / with `?v331`, `?trk`, `?hl`, `/youth/login/`, `/crm-sales` closed, no Crawl-delay — the plugin's own distinction written by the site. Listing `/tr/is-ilanlari/` 200 ×2 (286 751 B, md5 moving — a rendered element), `?page=2` 200 (13 cards), `?page=3` 200 (0 cards); every card carries an employer, a title, a type, a closing date and a city (28 of 28 filled); one advert read twice (4 260 859 B, two base64 images), its JobPosting complete** · 2026-09-20 -->
<!-- witness: the page states no count — the job sitemap is the second enumeration, read after the walk and compared address by address: «N emitted, the sitemap lists M — equal», or the two differences named (in the sitemap not on the pages, on the pages not in the sitemap); `--no-sitemap` says the sitemap was not read; the walk ends on the first page without a card (page 3 on 2026-09-20) or a page of repeats only, and says so when `--max-pages` cut it · 2026-09-20 -->
<!-- route: http · 28 · 2026-09-20 -->

**Issue #387 (bloc C of #291 — the country pages' boards without a card:
this one is born with the adapter).** The Turkey page (01.09) named the
host for its rules — 17 groups that allow `Claude-User` by name and refuse
`ClaudeBot` by name — and counted 27 on 2026-09-13; measured again on
2026-09-20 the day the adapter was written: 28.

## What Youthall is

The board of internships, long-term internship programmes, management-
trainee and young-graduate programmes of the large Turkish employers
(Toyota Türkiye, Şişecam, BİM, Akçansa, Doğuş Otomotiv, Norm Holding …),
with a smaller share of entry-level jobs (`Tam Zamanlı`, `Yarı Zamanlı`,
`Proje Bazlı`, `Sözleşmeli`, `Gönüllü`, `Dönemsel`, `Serbest Zamanlı`,
`Management Trainee` — the nine types seen on the 28 of 2026-09-20). Small
by count, and the only board here that carries this segment for Türkiye;
the generalists (`isinolsun`, `eleman`, `secretcv`, `iskur`) carry the
volume, not the programmes. A second object lives beside the adverts:
**«Yetenek Programları»**, a catalogue of employers' talent programmes with
their reviews (`sitemap.tr-talent_programs.xml`, 328 programme pages and
260 review pages on 2026-09-20) — named here, not advertisements, not
counted.

## The route — the listing to its empty page, the sitemap beside it

```
GET https://www.youthall.com/tr/is-ilanlari/            200   «Öne Çıkan İlanlar» (featured, 5) · «Tüm İlanlar» (15) · «Yetenek Programları» (6, no job link)
GET https://www.youthall.com/tr/is-ilanlari/?page=2     200   «Tüm İlanlar» 13
GET https://www.youthall.com/tr/is-ilanlari/?page=3     200   «Tüm İlanlar» 0 — the walk ends
GET https://www.youthall.com/sitemap.tr-jobs.xml        200   28 <loc>, one <lastmod> each (10.08 → 11.09.2026)
```

Only the «Tüm İlanlar» block is read: the featured block repeats cards of
the list and the programmes block has no advert. A card is `div.jobs > a`
to `/tr/<company>/<slug>_<n>/`, the employer's logo `alt="<Employer>
logo"`, an `<h5>` title and three `jobs-tag`s — the type (briefcase), the
closing date (clock; the ad's `<title>` calls it «Son Başvuru») and the
city (map marker). **The key is the address**: `_<n>` is the employer's own
sequence (`toyotaturkiye/…_4` is the site's advert 8262), so the ledger
key is `youthall:<company>:<n>` and `ad` adds the site's `identifier` as
`site_id`. `?page=` is not among the three query strings the rules close.

## The advert — a complete JobPosting

`/tr/toyotaturkiye/gelecek-toyotada-uzun-donem-staj-programi_4/` (200 ×2,
4 260 859 B — two images inlined in base64): `JobPosting` with `title`,
`description` (HTML), `datePosted` 2026-09-04, `validThrough`
2026-09-27T23:59:59+03:00, `employmentType` INTERN, `hiringOrganization`
(name, `sameAs` the employer's Youthall page, logo), `identifier`
(«Youthall», 8262), `jobLocation[]` (İstanbul, İstanbul, TR),
`directApply: true`. `youthall.py ad --url` reads it through
`_ldjson.postings` and dies with 6 on a page without one (a company page,
a programme page).

## What the adapter emits, and what it withholds

`jobs`: `ledger_id`, `id`, `url`, `title`, `company`, `kind`, `closes`
(as written, `27.09.2026`), `place`, `country: TR`, `contacts_withheld`;
`ad`: the JobPosting's fields, `posted` and `closes` as the site writes
them (ISO), `employment_type`, `place` and `region`, `site_id`, the
description as text. **Withheld**: e-mail addresses and telephone numbers
scrubbed from the description; the logo and cover images; the application
(`directApply`, an account) never touched. 2 s between requests; a full
`jobs` is four requests.

Guard in `tests/`: the list block alone read, the walk ending on the empty
page and on a page of repeats, the key from the address, the sitemap
compared and its differences named, `--no-sitemap`, a page without the
block (6), the ad's fields and the scrubbed description, a page without
JobPosting (6), a bad address refused before any request, another host
never sent (7) — 6 mutations on the committed file, 6 red (2026-09-20).
