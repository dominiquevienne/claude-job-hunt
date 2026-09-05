# Board adapter — Jobs Botswana (Botswana)

<!-- verified: 2026-09-05 -->

<!-- hosts: jobsbotswana.info -->
<!-- script: jobsbotswana.py -->
<!-- countries: BW -->
<!-- content: measured · 367 sitemap entries read, 20 of 20 sampled pages parsed; the site lists ~5 123 · 2026-09-05 -->
<!-- witness: the site's own listing, 5 123 — it disagrees by 14x and the reason is measured -->

**Rank 4 in Botswana, and what rank 1 does is refuse us** — the managed
Content-Signals default, the same 1 834-byte file that closes Niger, Mauritania,
Libya and Albania. So this is not a fourth board in a covered country; **it is
the country's readable market.**

```
jobsbotswana.py list                              # the sitemap alone, one request
jobsbotswana.py list --limit 20 --live --fetch    # newest first, expired dropped
jobsbotswana.py ad --slug workshop-manager-bango-trading
```

## 367 in the sitemap — and the site lists about 5 123

**The sitemap is a recent slice, not the board.** Measured 2026-09-05: the
site's own listing reports **`Showing 1–15 of 5123 jobs`**, and its pagination
runs to **page 342** — 342 × 15 ≈ 5 130, two signals from the site agreeing
with each other and disagreeing with the sitemap by a factor of fourteen.

**Page 342 carries advertisements dated `8 years ago` and `9 years ago`**, and
one of its eleven links is in the sitemap. **So the 5 123 is a nine-year
archive and the 367 is what the sitemap declares** — roughly the last nine
months, `2025-12-10 → 2026-09-04`.

*This card first published `367 advertisements` as though it were the size of
the board. It is not, and the same lesson had been written six hours earlier on
`job.am`: a window is not a size. **A single-file sitemap with no duplicates and
no gaps looks complete, and completeness is not what it demonstrates.***

## 367, and the sitemap holds 368

The extra entry is **`/jobs/` — the listing page itself**, sitting among the
advertisements. Small here, and the same shape as `caglobalint.com` (183 for
180) and `onape.td` (32 for 30) the same night. **Three boards, three different
ways of not being their own file length**, and none of the three announces it.

`/sitemap_index.xml` declares **sixteen** children; `noo_job-sitemap.xml` is the
only one of advertisements. The other fifteen are two of companies, one of
products, four of taxonomies, and pages and posts.

## The dates are the posting dates, and that was checked

```
31 distinct dates, 2025-12-10 → 2026-09-04
357 of 367 within thirty days
lastmod == datePosted on 10 of 10 checked
```

**The last line is the one that matters.** `myjobsfiji.com` gave all 3 187 of
its entries the same `lastmod`, so a freshness count taken from it would have
counted one afternoon's rebuild. Here the two agree, so the sitemap's date is
usable — but it is usable *because it was compared*, not because it is a date.

**Expired advertisements stay in the file.** Of the ten oldest, five have a
`validThrough` in the past. `--live` drops them; without it everything is
returned and `valid_through` travels with each row.

**The file is served oldest-first, and the adapter sorts newest-first.** Left as
served, `--limit 4` returned the four oldest — all expired — so
`--limit 4 --live` returned nothing and read like a broken board. **A default
that makes the ordinary request return the wrong end is a defect even when every
row is correct.**

## The employer is usually real, sometimes the site — and the rate depended on how I sampled

`hiringOrganization.name` reads **`Jobs Botswana`** — the site itself — on **2
of a random 20**. The other eighteen name a genuine employer.

**The first sample said 5 of 8.** It was the last eight entries of the file, and
they are one poster's batch of trade vacancies. **A contiguous slice from one
end of a sorted file is not a sample**, and the figure on this card comes from
`random.sample`.

The site's name is emitted as written with `employer_is_site: true`, never as
`None` — *"the board named no employer"* and *"we could not find one"* are
different facts.

## Fields, on twenty advertisements

| field | rate | note |
| :-- | :-- | :-- |
| title · employer · posted · valid_through | 20/20 | |
| city | 18/20 | `addressLocality`, real Botswana towns |
| `employment_type` | 20/20 | `FULL_TIME` 16, `CONTRACTOR` 4 — **real** |
| `baseSalary` | 0/12 | never present |
| `industry` | 10/12 | **not emitted** |

**`employment_type` is emitted here and is not on `keejob.py`**, where it reads
`OTHER` on every advertisement. Same field, same vocabulary, opposite worth:
**what a field is worth is a property of the board, not of the schema** — and
the only way to know is to look at the values.

**`industry` is not emitted.** It holds `Construction` on one row and `Driver`
or `Sales Manager` on the next — a sector and a job title in one field. A caller
filtering on it would be filtering on nothing consistent.

## Access and cost

`robots.txt` reads, the host sweeps, and its six rules cover WooCommerce upload
paths and `/wp-admin/` — none of them a path used here, asked **per path**.

`list` without `--fetch` costs one request. With it, one per advertisement:
`--since` and `--limit` bound it, and the board is 367 pages.
