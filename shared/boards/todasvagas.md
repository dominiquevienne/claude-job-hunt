# Board adapter — Todas Vagas (Mozambique)

<!-- verified: 2026-09-08 -->

<!-- hosts: todasvagas.com -->
<!-- host-forms: todasvagas.com -->
<!-- host-forms-basis: read — `todasvagas.py:BASE` is a literal; `www.todasvagas.com` answers under the bare name, so one host is declared · 2026-09-08 -->
<!-- script: todasvagas.py -->
<!-- countries: MZ -->
<!-- content: measured · 855 advertisements under `/vaga/` in a flat `sitemap.xml` of 914 `<loc>`, raw 855 / distinct 855, 0 duplicates; the other 59 are 52 `/dicas/` articles and 7 site pages; `JobPosting` on 4 of 4 read · 2026-09-08 -->
<!-- witness: none found — the site serves no total, and the sitemap's 914 is a count of pages rather than of advertisements · 2026-09-08 -->
<!-- hosts-source: named as Mozambique's rank-1 board by the nine-country page of 2026-09-04, which recorded that it names this project's token and permits it · 2026-09-08 -->

**Mozambique's first adapter, and the country's only measured board that is not
a node of the fabricated network.**

*`mozambiquejobsearch.com` is one of the thirty-one nodes `shared/fabricated-network.md`
lists — name verified, content never measured. This host is a different object.*

## One flat sitemap, two kinds of thing, and the path sorts them

```
/vaga/<slug>       855   advertisements
/dicas/<slug>       52   articles — tips, not jobs
seven site pages     7   /, /vagas, /empresas, /sobre, /contacto, …
                   ---
                   914   <loc> in ONE file — this is not an index
```

**Neither a filename nor a `lastmod` could sort this**: there is one file, and
its dates are almost all the same day. **The path could, and the rejection is
reported with a count** — `59 not under /vaga/` — *so the check says whether the
predicate still holds instead of assuming it did.*

*Fourth board on which the path decided, after Nepal's three
(`shared/robots-policy.md` §7). The denominator is now four boards in two
countries, and it is still not a law.*

## The sitemap stamps one date on almost every row

```
900 of 914 entries carry 2026-09-08     the day of the reading
the advertisements themselves span      2026-01-19 -> 2026-09-08
```

**`--since` is refused without `--fetch`, in code, exit 8.**

*Sixth board where a sitemap date is not the advertisement's, and the third
distinct way of failing: `kumarijob` dates the file, `merojob` carries an inert
middle layer, `merorojgari` lists an entry earlier than the ad — and here one
stamp is applied to almost every row at once.* **Four failures, four shapes.**

## `--limit` reads the NEWEST here, and that is the opposite of the neighbour

```
entry 0     posted 2026-09-08   validThrough 2026-10-23   LIVE
entry 300   posted 2026-06-20   validThrough 2026-08-04   expired
entry 600   posted 2026-03-18   validThrough 2026-05-02   expired
entry 854   posted 2026-01-19   validThrough 2026-03-05   expired
```

**The file is ordered newest first**, measured on four spread points. *`merojob.md`
records a file ordered the other way, where `--limit 5` returned five expired
advertisements and made a live board look dead.* **The order is a property of
one publisher, not of sitemaps, and each adapter says which way its own runs.**

**Three of four are expired, so `--live` is the flag that matters on this
board.** *`--fetch --live --limit 5` keeps 5 of 5 at the fresh end, all posted
2026-09-08 and valid to 2026-10-23.*

## Shapes read before the adapter was written

| field | shape here |
| :-- | :-- |
| `validThrough` | ISO **with an offset** — `2026-10-23T04:17:13+02:00` |
| `datePosted` | a bare date |
| `employmentType` | a string, `FULL_TIME`, 4 of 4 |
| `jobLocation` | a `Place` with a `PostalAddress` carrying `addressLocality` |
| `JobPosting` | present 4 of 4 |

*The offset is dropped when the field is compared: this filters on dates, not on
instants, and a board two hours from UTC would otherwise expire an hour early.*

## Access

`todasvagas.com` answers `read` and permits `/`, `/sitemap.xml`, `/vaga/…` and
`/dicas/` — `allowed=True`, `certain=True`, group `*`, measured 2026-09-08.
**`www.todasvagas.com` answers under the bare name**, so one host is declared.

## What this card does not establish

- **no rate.** *855 is a stock read once, and the ordering means the head is its
  best case by construction.*
- **nothing about the other Mozambican hosts.** *The Atlas counts six for this
  country; `mozambiquejobsearch.com` is a fabricated-network node whose content
  has never been measured, and the remaining four were not touched here.*
- **nothing about the 52 `/dicas/` articles** beyond their count and their path.
