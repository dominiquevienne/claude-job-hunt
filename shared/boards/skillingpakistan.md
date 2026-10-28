# Assessed, adapter deferred — Skilling Pakistan

<!-- verified: 2026-09-07 -->
<!-- hosts: skillingpakistan.gov.pk -->
<!-- countries: PK -->
<!-- script: none -->
<!-- content: measured · 0 advertisements — `/jobs` renders a table server-side whose only row reads "No jobs available" · 2026-09-07 -->
<!-- witness: none possible — a board that states its own emptiness leaves no count for a second source to confirm · 2026-09-07 -->

## It IS a job board, and it is empty

**`content:` was absent, which does not mean "measured at zero": it means
nobody had opened the body.** It has been opened, and the answer is a zero
that was *read* rather than inferred.

```
GET /            200 · 54 294 o · « Home - Skilling Pakistan »
GET /robots.txt  200 · 24 o · permits everyone
GET /jobs        200 · 704 683 o · « Latest Jobs - Skilling Pakistan »
                 <table> : 1
                   header  Title | Province | Country | Gender | Job Type
                   row 1   « No jobs available »
```

**This is the distinction `out-of-domain` would have destroyed.** *It is not a
site that turned out to serve something else — it is a jobs page, rendered
server-side, with a table whose columns are a vacancy's fields, and nothing in
it today.* **A board that states its own emptiness is a different fact from a
host that has no board, and the two would look identical in a column.**

**Zero is dated.** The page is server-rendered, so the emptiness is the
server's answer and not a script that failed to run — *which is what a 704 KB
page with no advertisement would otherwise suggest.* **Re-reading it costs one
request and no adapter is warranted until it is not empty.**

Pakistan's TVET portal (National Vocational and Technical Training
Commission). `robots.txt` closes nothing — `sweep: True`, no rule matched.
**`www.skillingpakistan.gov.pk` RESOLVES** — a `CNAME` to the apex, measured
2026-10-28 on two public resolvers. The sentence that stood here until then said
the opposite; it is cited and corrected below, not rewritten.

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

## The name resolves, and the clause that said otherwise is dated

**What stood in the prose above from 2026-09-03 (`81ea07f6`) until 2026-10-28:**
« `www.skillingpakistan.gov.pk` does not resolve. » — a bare sentence, with no
resolver, no status and no hour, on a card that dates everything else.
**A phrase like that cannot be reopened, because there is nothing to compare.**

**Measured 2026-10-28, the four queries and their negative control in one
command, `dig` against two public resolvers:**

```
skillingpakistan.gov.pk       @1.1.1.1   NOERROR   A 203.124.43.206
skillingpakistan.gov.pk       @8.8.8.8   NOERROR   A 203.124.43.206
www.skillingpakistan.gov.pk   @1.1.1.1   NOERROR   CNAME -> skillingpakistan.gov.pk
www.skillingpakistan.gov.pk   @8.8.8.8   NOERROR   CNAME -> skillingpakistan.gov.pk

negative control, same zone, same command, same resolvers:
zzz-ce-nom-n-existe-pas-2810-cd.gov.pk   @1.1.1.1   NXDOMAIN
zzz-ce-nom-n-existe-pas-2810-cd.gov.pk   @8.8.8.8   NXDOMAIN

the system resolver too, the one this repository's tooling INHERITS:
apex -> 203.124.43.206 · www. -> 203.124.43.206 · the control name fails
```

**The negative control is what makes four `NOERROR` readable** — a resolver that
never says no prints exactly the same thing. And no `SERVFAIL` appears, so this
is neither an ignorance nor an indeterminate.

**None of it moves this card's verdict.** `www.` is a `CNAME` to the apex, so it
serves what the apex serves and no route is discovered; `content:` stands as
measured on 2026-09-07, and no `route:` line exists here or is created by this
correction.

### Why it was wrong is NARROWED by this repository, and not closed

Two readings account for the gap — the 2026-09-03 measurement was wrong, or the
name was delegated after it — and the card cannot separate them. **The
repository can, partly, and it has carried the answer since the week it
happened:** `skills/job-scan/scripts/_robots.py` and the test class
`ADnsFailureIsTheResolversAnswerNotTheHosts` both record, from **2026-09-05 —
two days AFTER the clause** — this same zone answering

```
via 1.1.1.1   skillingpakistan.gov.pk   NOERROR   A = 203.124.43.206
via 8.8.8.8   skillingpakistan.gov.pk   SERVFAIL
              jobs.gov.pk               SERVFAIL   <- not specific to it
```

**The address is the one measured today.** So the apex was served, at this
address, two days after a sentence saying a name in this zone was not — and this
zone has a dated history of answering `SERVFAIL` on one of the two public
resolvers, which is exactly the failure that produces a false *does not
resolve*: `SERVFAIL` is not `NXDOMAIN`.

**What is still NOT established, and no instrument here reads it:** whether
`www.` carried its `CNAME` on 2026-09-03. The apex's branch is answered; the
`www.` branch is not, so « delegated since » survives for that form alone, and
it is left open rather than closed by convenience.

**And the guard came out of THIS host while the clause stood — through two
later passes over the card itself.** The 2026-09-05 report (`17db9a68`,
11:55 UTC) produced `_resolver_note()`, its two-direction test, and the sentence
« a name that does not resolve here has not been shown to be gone » — written
two days after the clause and while the clause was in the file. **The card was
then edited twice, on 2026-09-07 (`19541fa0`, +29 lines) and on 2026-09-08
(`f3239ede`), and the clause is present in the card at both.** *So it is not
that nobody came back: two passes wrote around the sentence without reading it,
and writing the guard audited neither.*

## Why no adapter yet

**No row has ever been available to parse.** A parser written against the
five column headers alone — `Title`, `Province`, `Country`, `Gender`,
`Job Type` — would be a guess at the row shape, shipped unverified, and this
repository's cards end with *"Verified against the live site"* for a reason.

**The check to re-run** is one request: fetch `/jobs` and look for
`No jobs available`. When it stops appearing, the table is the whole listing
(server-rendered, no pagination links, no AJAX route in the page) and the
adapter is half an hour's work.

*`verified:` corrected 2026-09-08 from 2026-09-03 to 2026-09-07 (#188-adjacent guard): this card's `content:` carries a measurement of 2026-09-07 and the commit that wrote it exercised the host, so the card's age was understated. **The measurement was right and the header was behind** — `adapter-age.sh` was filing it older than it is.*
