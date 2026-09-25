# Board measurement — MyanmarJobLink (`www.myanmarjoblink.com`, Myanmar): a generalist whose **list carries every field**, so the whole board is 27 requests and not 405. The pager is a sliding window that also names its last page. Adapter `myanmarjoblink.py` (#639)

<!-- verified: 2026-09-25 -->

<!-- hosts: www.myanmarjoblink.com -->
<!-- script: myanmarjoblink.py -->
<!-- countries: MM -->
<!-- route: http -->
<!-- content: measured · **the rules file is served (`state: read`, `certain: True`) and writes NO Crawl-delay (2 s are ours); it declares no sitemap and `/sitemap.xml` answers 404, so there is no published enumerator and the list is walked; `/find-jobs` 200, 159 415 B, **15 distinct adverts**, the pager naming 2 3 4 5 6 and **27**; server-rendered throughout — no `__NEXT_DATA__`, no `JobPosting`; the list carries title, reference, employer, salary, place, date and an excerpt, so no advert page need be fetched** · 2026-09-25 -->
<!-- witness: 15 adverts on page 1 against a bound of 27 named by the pager — the board sits in [391, 405] if every page holds 15, and the last page's count pins it · 2026-09-25 -->

**Measured 2026-09-25 18:3x UTC by the declared client, the guard on the exact
path; the adapter exercised against the host with `--max-pages 1` (15 emitted)
and `--max-pages 2`.** *The full 27-page walk was not run — the figure that
matters is the bound the site names, and the run prints it beside what it
emitted.*

## Two figures that predict one another, and a window that must not be re-read

The pager on page 1 names `2 3 4 5 6` **and 27**. It is a sliding window that
also carries its last page: **read on every page it would follow the walk
instead of bounding it.** Page 1 holds 15 adverts, so the board sits between
26 × 15 + 1 = **391** and 27 × 15 = **405**, and the last page's count pins it
exactly. *Same shape as `myjobs.com.mm`, and the same rule: the bound is read
from page 1 and only from page 1.*

## The same field is carried by two different tags

```
<span class="fprize"><b>Salary</b>: 500,000 - 700,000 </span>     ordinary advert
<p    class="fprize"><b>Salary</b>: Negotiable</p>                another
```

**Anchoring on the tag returned `salary` and `place` null on EVERY row** — and
the output stayed a complete, well-formed JSON whose two empty fields read as
«&nbsp;this board publishes no salary&nbsp;». *It is the `job_position_featured`
variance one layer down.*

> **Read by the CLASS the site sets, never by the tag that carries it.**

**And a featured advert is an advert**: items are `job_listing clearfix` and
`job_listing clearfix job_position_featured`. The exact class drops every
featured one, and what remains still looks like a board — the defect that cost
33 adverts of 3 232 on Wazifaha.

## The salary really does collide here

«&nbsp;500,000 - 700,000&nbsp;» is a long run of digits and separators: **the exact shape
of the rule that destroyed 113 salaries on `myjobs.com.mm`.** The mutation that
puts the salary back under the telephone rule returns
`'500,[telephone withheld],000'`. *Unlike BestJobMyanmar — where no measured
value collided and the exemption was merely defensive — `money()` is
load-bearing on this board.*

**The title carries the reference** («&nbsp;Junior Accountant&nbsp;&nbsp;&nbsp;JO-59112&nbsp;»), and
they are separated by the reference's own shape. *Splitting on whitespace would
cut a two-word title in half.*

**WITHHELD:** e-mail addresses and telephone numbers in free text. Many
employers here are recruitment agencies and the board names them openly —
nothing is anonymised, unlike MyWorld.
