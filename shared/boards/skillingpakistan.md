# Assessed, adapter deferred — Skilling Pakistan

<!-- verified: 2026-09-03 -->
<!-- hosts: skillingpakistan.gov.pk -->

Pakistan's TVET portal (National Vocational and Technical Training
Commission). `robots.txt` closes nothing — `sweep: True`, no rule matched.
`www.skillingpakistan.gov.pk` does not resolve.

**`/jobs` exists, is 704 kB, and its table says `No jobs available`.**

## The board is empty, and it says so in its own words

That distinction matters. This is **not** a zero inferred from a parse that
found nothing — the server-rendered table contains the sentence. `_zero.py`
exists because *a search that matches nothing and a market that has nothing
look identical*; here the board removes the ambiguity itself.

Checked against every filter the form offers, including values drawn from the
site's **own** occupation vocabulary:

```
/jobs                              No jobs available
/jobs?jobType=1        (Govt)      No jobs available
/jobs?jobType=4        (Private)   No jobs available
/jobs?jobType=2        (Overseas)  No jobs available
/jobs?occupation=Security+Guard    No jobs available
/jobs?gender=Male                  No jobs available
```

The occupation dropdown is populated from real data — *Security Guard*, *AUTO
DENTER*, *Senior Civil Engineer* — so the database is not empty. **The
listing is.**

## The number on that page is not an advertisement count

The same `/jobs` page prints, above the empty table:

```
Total Male Jobs    299,334
Total Female Jobs    3,279
Total Jobs         302,613
```

**Those are labour-market statistics under an "Employment Trends" heading, and
they sit directly above a table with nothing in it.** Anyone quoting 302 613
as this board's advertisement count would be out by 302 613. It is the exact
shape `atlas`-facing work has been wrong on before: *a headline number that
reads as a total.*

## Why no adapter yet

**No row has ever been available to parse.** A parser written against the
five column headers alone — `Title`, `Province`, `Country`, `Gender`,
`Job Type` — would be a guess at the row shape, shipped unverified, and this
repository's cards end with *"Verified against the live site"* for a reason.

**The check to re-run** is one request: fetch `/jobs` and look for
`No jobs available`. When it stops appearing, the table is the whole listing
(server-rendered, no pagination links, no AJAX route in the page) and the
adapter is half an hour's work.
