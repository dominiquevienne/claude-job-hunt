# Board adapter — マイナビ転職 / Mynavi Tenshoku (Japan): seven job sitemaps, a site total that refutes them, a full JobPosting on every advertisement

<!-- verified: 2026-09-11 -->

<!-- hosts: tenshoku.mynavi.jp -->
<!-- script: mynavi.py -->
<!-- host-forms: tenshoku.mynavi.jp -->
<!-- host-forms-basis: read — `mynavi.py:BASE`, a single literal; every address comes from the sitemap as served · 2026-09-11 -->
<!-- countries: JP -->
<!-- content: measured · 77 504 distinct advertisement ids across the 7 `sitemap_jobs_NN.xml.gz` files (346 385 `<loc>`, up to six facet variants of one id), `<lastmod>` per entry from 2024-02-27 to 2026-09-08 — **against 掲載求人数 61 989 件 stated on the home page the same day: the sitemap is a superset of the board, closed advertisements still declared**; `mynavi.py sitemap` at 18:44 UTC · 2026-09-11 -->
<!-- witness: second source on a different question — the home page's 掲載求人数 61 989 件 (advertisements listed) against the sitemap's 77 504 distinct ids; it REFUTES «sitemap = board» rather than confirming a figure, and the adapter prints both side by side on every full run · 2026-09-11 -->

**Japan's first adapter — one of the country's two or three largest boards,
Japanese interface, UTF-8, and nothing translated: the adapter emits what the
site publishes.** Measured 2026-09-11, 18:37–18:46 UTC, every fetch through
`bin/fetch-body.py` or the adapter under the declared identity, the guard on
the exact path first.

## Rules and transport — open, and the parser keeps every rule

```
GET /robots.txt        200, twice, same body — 47 Disallow to `*` (/a/, /b/, /c/, /entry/ …), none on the
                       sitemap or /jobinfo-…/; no Crawl-delay; three Sitemap: lines
GET /                  200, 214 256 B, <title>転職はマイナビ転職…</title>, md5 moving (session tokens, not a challenge)
```

`identity()` → `http`, `claude-user`. *The country page of 2026-09-01 warned
that `urllib.robotparser` before 3.14 loses wildcard rules after a blank line;
`_robots` is not that parser — checked on `next.rikunabi.com`'s 64-rule file,
64 kept, the 37 wildcards after the blank line included.*

## The sitemap — seven job files, 346 385 URLs, 77 504 advertisements

```
sitemap/sitemap_index.xml            345 children; sitemap_jobs_01…07.xml.gz are the advertisements
sitemap_jobs_NN.xml.gz               50 000 <loc> each (07: 46 385), served Content-Encoding: x-gzip, ~10 MB decoded
<loc>  https://tenshoku.mynavi.jp/jobinfo-<id>-<a>-<b>-<c>/      <lastmod>2026-09-08T00:00:00+09:00</lastmod>
```

**The id is the advertisement; the three numbers are a facet** (occupation,
area, order): 50 000 URLs of file 01 are 23 227 ids, and one id appears up to
53 times across the seven files. `<lastmod>` is real and per entry — 100
distinct values in one file — so `--since` narrows on it. **The adapter keys
on the id, keeps the newest `<lastmod>` and the first URL, and prints raw
`<loc>`, matched, unmatched and distinct.**

**A gzip stream decoded as text is 118 502 replacement characters and zero
`<loc>`** — `empty_first_page` caught it on the first run (exit 6, «from
270 766 characters»), and `get()` now undoes the encoding by the header or the
magic bytes, as `bin/fetch-body.py` does.

## The count, and the site's own total that refutes it

```
7 of 7 job files: 346 385 <loc>, 346 385 matched, 77 504 distinct advertisement id(s)
site states 掲載求人数 61 989 件 on its home page — the sitemap's 77 504 distinct ids are MORE than that by 15 515:
  the sitemap keeps ids whose <lastmod> goes back years — closed advertisements still declared — so it is a
  SUPERSET of the board, and this count is not the board's size.
```

*The home page also states 新着求人 13 086 件, 9月11日更新 — new advertisements,
updated that day.* **Neither figure is the adapter's count and neither is
compared as if it were: 77 504 answers «how many ids has the sitemap ever
kept», 61 989 answers «how many does the site list now».** The
advertisement's own `validThrough` is on its page, and `--since` on the
sitemap's `<lastmod>` is the cheap approximation — `--since 2026-09-01` keeps
4 532 of file 01's 23 227.

## The advertisement — a JobPosting in JSON-LD, in Japanese

```
GET /jobinfo-407994-1-46-1/     200, 241 740 B, exactly one JobPosting
title 貿易事務／一般事務・庶務 · hiringOrganization ランスタッド株式会社 · employmentType FULL_TIME
industry · occupationalCategory · datePosted 2026-09-08 · validThrough 2026-10-05
jobLocation[] with addressRegion (埼玉県, 千葉県, 東京都 … — one Place per office, deduplicated)
baseSalary JPY 3 120 000 – 4 000 000 / YEAR · workHours · jobBenefits · experienceRequirements · description (HTML inside the JSON)
```

`ad` emits these as published, tags stripped from the prose fields, `<br>` to
newlines, `language: ja`. **Read in full on one advertisement**; the fields
are asserted on one page, not a sample.

## Configuration

```yaml
boards:
  mynavi:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no browser. A full `sitemap` run is 9 requests (index, seven
10 MB files, the home page for the total) — `--files 1` is the cheap probe.

## What is not established

- **Which of the 77 504 are open** — the sitemap does not say; `validThrough`
  on each page does, one request each.
- **The facet numbers' meaning** (`-1-46-1`): inferred as occupation / area /
  order from their distributions, not read from documentation.
- **Search and filters**: `/list/` and keyword paths exist in the index's other
  338 children; none exercised.

## 2026-09-11 — shipped

Rules twice, root twice, index once, seven job files once each, one
advertisement. `sitemap --files 1 --since 2026-09-01`: 4 532 of 23 227;
full seven files: 77 504 distinct against 61 989 stated.
