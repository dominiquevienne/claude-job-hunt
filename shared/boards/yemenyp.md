# Board measurement — Yemen Young Platform jobs (`www.yemenyp.com/jobs`, Yemen): **every list route states «We found 0 job offers» on 2026-09-22, while the SAME page's own sector counts total 15** — the page contradicts itself, so «the board is empty» is not established; rules open, no sitemap, no adapter

<!-- verified: 2026-09-22 -->

<!-- hosts: www.yemenyp.com -->
<!-- script: none -->
<!-- countries: YE -->
<!-- content: measured · **2026-09-22, two reads of each route by the declared client, the guard on the exact path: `/jobs/all` 200 ×2, 8 784 B, md5 6f0c15633b59 identical, stating «We found 0 job offers» — and in the same markup its own sector counts, Accounting 1, Business 1, Cashier 1, Designer 1, Developer 3, IT 1, Online 1, Telecommunications 2, Web 4, total 15. `/jobs/web` 200 ×2, 9 015 B, md5 ec1994421068 identical, ALSO «0 job offers» while its own sidebar says «Web Jobs 4». `/jobs` 200 ×2, 8 027 B, md5 d9dac915c65f identical — the landing page, server-rendered, with sector and city links and no advert. `robots.txt` 200 (571 B) read: open and certain for us, its Crawl-delay of 40 s sitting in a group that names nine other bots and neither of ours. `/sitemap.xml` 404, so nothing independent names an advert page. The zero and the fifteen are both the site's own words on one page** · 2026-09-22 -->
<!-- witness: the site's own per-sector counts, printed on the very page that states zero · 2026-09-22 -->

**Found by the Yemen search of #607 (a country never searched), measured
2026-09-17 13:42–13:44 UTC and re-measured 2026-09-22 15:06–15:1x UTC by the
declared client, the guard on the exact path first, `bin/fetch-body.py`, two
reads of each route.** *A measurement, not an adapter.*

```
robots.txt                                 200, 571 B — open, certain; Crawl-delay 40 for NINE other bots, not ours
GET https://www.yemenyp.com/jobs           200 ×2, 8 027 B, md5 d9dac915c65f — sector and city links, no advert
GET https://www.yemenyp.com/jobs/all       200 ×2, 8 784 B, md5 6f0c15633b59 — «We found 0 job offers»
GET https://www.yemenyp.com/jobs/web       200 ×2, 9 015 B, md5 ec1994421068 — «We found 0 job offers», sidebar «Web Jobs 4»
GET https://www.yemenyp.com/sitemap.xml    404 — nothing independent names an advert page
```

## The zero is not established as a zero

**Two list routes state «We found 0 job offers». The same markup states, in its
sidebar, nine sector counts totalling 15** — Accounting 1, Business 1, Cashier 1,
Designer 1, Developer 3, IT 1, Online 1, Telecommunications 2, **Web 4**. The
`/jobs/web` page is the sharpest case: it says it found none, beside its own
figure of four.

> **Both numbers are the site's own, on one page, in one read. The page
> contradicts itself, and nothing outside it can settle which half is true.**

*A zero is the only result whose legitimate output and whose broken output are
identical.* Here there is, for once, a discriminant that does not come from our
extraction — and it does not confirm the zero, it **refuses** it. Two readings
remain open and this measurement cannot choose between them: the counts are
stale and the board is genuinely empty, or the listing query is broken while the
counting query still answers. **No sitemap exists to name advert pages**, so
there is no third reading available today.

## What changed since 2026-09-17, and what did not

The card then recorded an **8 KB JavaScript shell** — «no card, no count, no
JobPosting». Today's `/jobs` is **the same 8 027 bytes** and is **server-rendered
prose**: sector links, city links, the directory's own copy. *Same size,
different md5* (`d9dac915c65f` today against `c85d6036d8fc` on the 17th) — and
today's two reads are identical to each other, so the difference is a change in
the page and not a per-request element. **What was read on the 17th was read
correctly; the conclusion «a shell» no longer describes what is served.**

## What would lift it

**Any list route returning at least one advert**, or **the sector counts falling
to zero** — either resolves the contradiction, and the second would make «empty»
a finding rather than an artefact. Until then an adapter cannot be written: *a
walk built today would be written against a zero, and would carry that zero into
a statement about Yemen's market.* #647 is labelled `blocked` for that reason and
no other. **The rules are open, the host answers, nothing here is a refusal.**
