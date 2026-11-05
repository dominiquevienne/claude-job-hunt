# Board measurement — Vaga Servisu TL (`www.vagaservisu.com`, Timor-Leste): «Connecting people to opportunities» — a Blogger blog of vacancies, scholarships and tenders by NGO (CARE, Mercy Corps, Oxfam, WorldFish…), read through its Blogger feed by `vagaservisu.py` since 2026-11-05; the apex fails its TLS handshake and redirects to `www.` over http. The feed serves FEWER entries than asked without saying so, and its labels are an organisation taxonomy, so the walk steps by what it RECEIVED and the kind is ours

<!-- verified: 2026-11-05 -->

<!-- hosts: www.vagaservisu.com, vagaservisu.com -->
<!-- script: vagaservisu.py -->
<!-- route: http · 1551 · 2026-11-05 -->
<!-- countries: TL -->
<!-- content: measured · **`https://www.vagaservisu.com/` (200, 180 555 B, md5 f9fcb9b43dad / f2fc47ed2b0d — a rendered element moves) is a Blogger blog («Vaga Servisu TL») with NGO sections and its feed `/feeds/posts/default` declared; `https://vagaservisu.com/` fails the TLS handshake (`UNEXPECTED_EOF_WHILE_READING` ×2) and `http://vagaservisu.com/` answers 301 to `www.`; no count stated, no JobPosting; `_robots.allowed('www.vagaservisu.com','/')` → open, `certain: False` (the rules file did not answer as one); the feed and the posts not read** · 2026-09-18 -->
<!-- witness: the feed’s own `openSearch$totalResults` (1 551), printed by `vagaservisu.py list` beside the walk — **but it counts ALL POSTS and not vacancies**: the blog mixes vacancies with scholarships and public notices, and the per-type witness is the feed’s LABEL-SCOPED total, which Blogger states for each (`Anunsiu Vaga` 384, `Job Vacancy` 801, `Anunsiu Bolsa Estudu` 6 on 2026-11-05 — **the labels are not synonymous**, and 177 `Job Vacancy` of the 536 posts held carry no `Anunsiu Vaga`). The board’s size in VACANCIES is NOT established, and no label set is exhaustive: 126 of those 536 carry no vacancy label at all, and two opened at the median and the end are a UNICEF consultancy and a PNTL police recruitment · 2026-11-05 -->

## 2026-11-05 — #687: the adapter, and two defects that no verdict shows

**`vagaservisu.py` is shipped.** Measured 08:34–08:38 UTC by the declared
client, the guard taken on the exact path in a turn DISTINCT from the
retrieval: `_robots.allowed('www.vagaservisu.com', '/feeds/posts/default')`
→ `allowed: True`, `state: unrecognised`, `certain: False` — an absence of
rules, so open by the owner's decision of 2026-09-13 (#283) — and **no
`Crawl-delay` is written, so 3 s is ours**. The blog's `/search` and label
pages are never asked for; the feed suffices.

**THE FEED SERVES FEWER ENTRIES THAN ASKED, AND SAYS NOTHING.** It declares
`itemsPerPage: 500` and `openSearch$totalResults: 1551`, and the windows
`start-index=` 1 / 501 / 1001 / 1501 at `max-results=500` return **125, 145,
107 and 51** entries — **428 distinct against 1 551, 27.6 %**, with no error,
no non-zero code and no message. The indices are correct: `start-index=126`
after a page of 125 returns 108 with **zero overlap**, union exactly
233 = 125 + 108, and its first entry resumes on the same day the previous
page stopped. So it is the count SERVED that varies, and **the cause is not
established here and is not asserted** — what is measured is the behaviour.

> **And whether a page is short depends on the SIZE ASKED, so this is not a
> property of the host**: at `max-results=50` the same feed serves 50, 50, 50.
> The defect is therefore not «this host serves short pages» but «no page size
> is known to be honoured, and a short page is silent». A walk that steps by
> the size ASKED skips everything between what it got and what it requested —
> the form `empleosenuruguay.py` uses, correct on ITS host, where 3 750 + 27
> closed on the stated total. **The platform predicts the ROUTE, not the walk.**

Hence `start += len(entries)`, and **only an EMPTY page ends the walk**. The
live walk exercises it rather than leaving it latent: three pages asked at 500
served `[125, 108, 87]` and emitted **320 distinct, contiguous** records.

**THE LABELS ARE AN ORGANISATION TAXONOMY, SO NOTHING IS DROPPED.** A
label-only filter loses real vacancies: of the 126 held posts carrying no
vacancy label, the first is a scholarship but the **median is
«National/International Consultant … — UNICEF»** and the **last an
«Anúnsiu Públiku … Rekrutamentu Ofisiál PNTL 2025»**, both vacancies labelled
only by their organisation (`UN`, `UNICEF`, `CRS`, `CARE`) — and four carry a
title beginning «Vaga Servisu» («job vacancy» in Tetum) with no vacancy label
at all. So every post is emitted with a `kind` derived from its labels AND its
title, `kind_is_ours: true` on every record, the distribution printed beside
the count, and `--kind` left to the caller. *A board made poor by our own
filter reads exactly like a board that is poor.*

**THE CONTACTS ARE REAL AND THE WITNESS IS DERIVED.** No JobPosting JSON-LD
anywhere (0 of the 25 newest), so no structured employer; but **15 of those 25
bodies carry a recruiter's e-mail address and 4 a telephone**, and on the live
walk a contact was removed from **203 of 320**. `withheld_fields` names what
was ACTUALLY taken — `null` on a quiet post, where a card that asserted the
witness would have claimed to withhold what nobody had deposited. The phone
pattern is Timor-Leste's own (`+670`, 8-digit mobiles beginning 7, 7-digit
landlines beginning 3) and was tried in both directions against USD amounts —
`USD 1,200`, `$1,500-$2,000`, `$35000` are untouched — **because the country
pays in US dollars and a digit-count rule on a currency is how 113 of 115
salaries were once destroyed.**

```
GET /feeds/posts/default?alt=json&max-results=25            200, 519 241 B, 25 entries, 1 551 stated
GET /feeds/posts/summary?alt=json&max-results=500&start-index=1/501/1001/1501
                                                            200 x4 — 125, 145, 107, 51 entries
GET /feeds/posts/summary?alt=json&max-results=500&start-index=126
                                                            200 — 108 entries, DISJOINT from the first page
GET /feeds/posts/default/-/<label>?alt=json&max-results=1   200 x3 — 384 / 801 / 6 stated
vagaservisu.py list --pages 3                               320 emitted, served [125, 108, 87]
```

*What it will never give: the recruiters' contacts, and the employers' own
application routes are never followed.*


**Found by the Timor-Leste search of #612 (a country never searched),
measured 2026-09-18 06:33–06:36 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #612: one search naming the national portals, the Government's
recruitment page and the UN aggregators (UNjobs, UNjobnet — global, left
aside), no composed host names. *A measurement, not an adapter.*

```
GET https://www.vagaservisu.com/    200 ×2 — a Blogger blog, /feeds/posts/default declared
GET https://vagaservisu.com/        SSL: UNEXPECTED_EOF_WHILE_READING ×2 ; http:// → 301 www.
```

**A Blogger blog, the `empleosenuruguay.md` shape**: the feed on the
blog's own host states its total and pages by `start-index` — the
adapter's first line.
