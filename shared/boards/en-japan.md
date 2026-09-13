# Board adapter — エン転職 (`employment.en-japan.com`, Japan): a dated job sitemap of 10 811, a front page that states 125 248, and a JobPosting per advertisement

<!-- verified: 2026-09-12 -->

<!-- hosts: employment.en-japan.com -->
<!-- script: enjapan.py -->
<!-- host-forms: employment.en-japan.com -->
<!-- host-forms-basis: read — `enjapan.py:BASE`, a single literal; the sitemap index and its job file address the same host · 2026-09-12 -->
<!-- countries: JP -->
<!-- content: measured · 10 811 distinct advertisement ids in `sitemap_work_0001.xml.gz` (10 811 `/desc_<id>/`, `<lastmod>` on all, 2025-12-22 → 2026-09-11), **against «求人数 125248 件！ 2026年9月10日 更新» on the front page — 114 437 short, and both are printed: the file is the subset the site publishes to crawlers, the front page counts its whole store**; `enjapan.py sitemap` at 15:29 UTC · 2026-09-12 -->
<!-- witness: the site's own «求人数 N 件» on the front page, read in the same run and printed beside the file's count — not as an equality to reach but as the other question; the file's `<lastmod>` are real dates (1 331 in September, 3 479 in August) · 2026-09-12 -->

**One of Japan's largest boards — «日本最大級の転職サイト» in its own title —
and the fourth Japanese host with a script here** (after Mynavi, type,
Green). Measured 2026-09-12 15:26–15:30 UTC, every fetch under the declared
identity, the guard on the exact path first. *Everything is Japanese and
nothing is translated.*

## Rules — `ClaudeBot` refused everything, `Claude-User` under the common regime

```
robots.txt                      200, 2 869 B, 74 Disallow lines in five groups
  User-agent: ClaudeBot         Disallow: /                      <- the other token, refused entirely
  User-agent: GPTBot            Crawl-delay: 30 · the faceted listings refused
  User-agent: *                 /k_*/*_*/*_*/ · /s_*/*_*/*_*/ · *sort* · *refine* · ~50 /api/… · **/desc_eng*** · /apply_eng*
                                nothing on /desc_<id>/, the sitemap or /
identity("/")                   http, claude-user — «claude-user may fetch this path (claudebot may not)» (decision of 2026-09-07)
```

**Two consequences the adapter carries.** `/desc_eng*` — the English
rendering of an advertisement — is a written refusal and is never
fetched; `ad` rejects the address before any request. And `Crawl-delay:
30` binds `GPTBot` alone; the `*` group sets none, and the adapter spaces
2 s.

## The count — a subset and a whole, printed side by side

```
GET /sitemap_index.xml                  200 — sitemap_static, **sitemap_work_0001.xml.gz** (lastmod 2026-09-11), sitemap_company_0001/0002
GET /sitemap_work_0001.xml.gz           200, 42 646 B gzip → 1 059 587 chars — 10 811 <loc>, all /desc_<id>/, all with <lastmod>
GET /                                   200 — «求人数 125248 件！ 2026年9月10日 更新！» (and «1万5000件の非公開求人», the non-public ones, apart)

10 811 <loc> across 1 job file(s); **10 811 distinct advertisement id(s)**, 0 without <lastmod>; 10 811 emitted.
10 811 in the sitemap, site states 125 248 (updated 2026-09-10) — 114 437 short; the sitemap is the subset the site publishes to crawlers, the front page counts its whole store — two questions, both printed.
```

**The file is one twelfth of what the front page states, and neither
number is wrong**: the site chooses what it puts in a crawler's file, and
it counts everything it holds on its front page. *The adapter never lets
«short» read as a defect here — the sentence names the two questions —
and never lets 125 248 stand alone as an inventory it can reach.* What the
plugin can read is the file; `--since` filters on its `<lastmod>`, which
is the advertisement's own date (the newest, `desc_1442658`, is dated
2026-09-11 in the file and «掲載期間 26/09/11 ～ 26/12/10» on its page).
By month: 2026-09 1 331 · 2026-08 3 479 · 2026-07 2 249 · 2026-06 1 773 ·
2026-05 674 · 2025-12 700.

## The advertisement — a JobPosting, twice-escaped, with a whole prefecture in its places

```
GET /desc_1442658/    200, 231 682 B — one JobPosting in JSON-LD (the reserve note of 2026-09-11 said none; one is there on the page read)
title · description (HTML escaped TWICE: &amp;lt;p&amp;gt; — unescaped until stable) · datePosted 2026-09-11 · validThrough 2026-12-10
hiringOrganization 株式会社クロス・マーケティング · employmentType ["FULL_TIME"] · baseSalary JPY 4 000 000 – 5 500 000 YEAR
jobLocation: a LIST of 51 places — every ward and city of 東京都, when the page's own text names the prefecture
educationRequirements 大学 以上 · experienceRequirements · industry ["専門コンサルタント"] · jobBenefits · workHours
identifier.value "140476" — the site's EMPLOYER-side number, not the URL's desc_1442658
```

**Two values kept as published and named for what they are**: `places` is
the list the site gives (51 entries for one Tokyo posting — the prefecture
enumerated, not fifty-one offices), and `identifier_value` is the
employer-side number, not the advertisement id — the id is the URL's.
Read in full on one advertisement.

## Configuration

```yaml
boards:
  en-japan:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no browser. `sitemap` is three requests (index, job file,
front page); `--no-site-total` makes it two; the job file is 1 MB
uncompressed.

## What is not established

- **Which of the 125 248 are the 10 811** — the file's selection rule is
  the site's; nothing on an open path says it.
- **The faceted listings** (`/k_*/`, `/s_*/`) — refused to `*`; the count a
  facet would state is behind them.
- **Whether every page carries a JobPosting** — one read; the reserve note
  of the day before said none on the page it read.
- **`sitemap_company_*`** — not read.

## 2026-09-12 — shipped

`enjapan.py sitemap`: 10 811 distinct, site states 125 248 — both printed.
`ad` on 1442658. Three tests; six mutations on a detached worktree
(`python3 -B`), six red, each on the test written for it.
