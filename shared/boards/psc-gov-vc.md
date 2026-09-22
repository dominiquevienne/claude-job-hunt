# Board measurement — Service Commissions Department (`psc.gov.vc`, Saint Vincent and the Grenadines): the public service's own recruiter — **2 open posts under 2 ministries on 2026-09-22** (Procurement Officer I, deadline 2026-09-28; Information Officer API, deadline 2026-10-05), each a PDF advertisement; `pscgovvc.py` — the ministry is read as the HEADING it is, the advertisement is named and never downloaded, and the page's footer is not read at all

<!-- verified: 2026-09-22 -->

<!-- hosts: psc.gov.vc -->
<!-- script: pscgovvc.py -->
<!-- countries: VC -->
<!-- content: measured · **2 open posts under 2 ministries**; this is the country's ONLY open door — both private boards answer 522 (#751, #752), so two adverts here are the whole coverage. **the page read by the declared client, 2026-09-22 08:4x UTC, the guard on the exact path, two reads: `/psc/index.php/vacancies` 200 ×2, 21 397 B both, md5 b9fda0a5f3f9 both — everything is inside `div[itemprop=articleBody]`, where a `&lt;p&gt;&lt;strong&gt;` names a MINISTRY and the `&lt;li&gt;` that follow are its posts, each an `&lt;a&gt;` to a PDF under `/psc/images/PDF/Vacancies/` and a «(Deadline: September 28, 2026)». **2 posts, 2 ministries, both open**, and nothing states a count. `psc.gov.vc` answers **404 to `/robots.txt`** — a knowledge, not an ignorance: there is no file, so no rule (open, certain). The footer carries the Department's street address and hours and is NOT parsed. Exercised: `jobs --country-code VC` → **2 emitted under 2 ministries, «the page states no count» said** · 2026-09-22 -->
<!-- witness: none — the page states no count; `pscgovvc.py jobs` prints the posts read, the ministries, the undated and the already-closed · 2026-09-22 -->
<!-- route: http · 2 · 2026-09-22 -->

**Found by the Saint Vincent and the Grenadines search of #616 (a country
never searched), measured 2026-09-18 07:55–08:01 UTC by the declared client, the
guard on the exact path first, `bin/fetch-body.py`, two reads.** The method
is written on #616: two searches naming the Government, the Service
Commissions Department and the private boards, no composed host names. *A
measurement, not an adapter.*

The public-service recruiter of the State (the Personnel Department, Halifax Street, Kingstown); the Government portal's own vacancies page (`gov-vc.md`) links this department's PDFs too.

```
_robots.allowed('psc.gov.vc', '/psc/index.php/vacancies')   open
GET https://psc.gov.vc/psc/index.php/vacancies   200 ×2 — two posts with deadlines, a PDF each
```

The adapter's first line: the page's list (ministry, post, deadline, PDF link) as the list and the PDF's text as the ad; a thin, dated flow.

## The adapter — `pscgovvc.py` (#732, 2026-09-22)

```
GET /psc/index.php/vacancies   200 ×2, 21 397 B — 2 posts, 2 ministries, 2 PDFs, no count stated

<p><strong>Ministry of Higher Education, Grenadines Affairs, Airports and Seaports</strong></p>
<ul><li><a href="…/423_-_Procurement_Officer_I_-_Urban.pdf">Post of Procurement Officer I</a>
        <strong><em>(Deadline: September 28, 2026)</em></strong></li></ul>
```

**The ministry is a HEADING, not a field of the post.** It is carried forward
to every post that follows until the next heading — and **a post that appears
before any heading carries `None`**, never the ministry of the block above it.
*That is the failure a carried-forward value produces when nothing resets it,
and it produces a plausible wrong employer rather than a missing one.* A
paragraph that is itself a link («Application forms») is not a heading.

**This page is the country's live public route.** Its two private boards
answer a Cloudflare 522 (#751 and #752, both `blocked`), and the national
portal `www.gov.vc` mirrors this page with a post that expired in 2025 — so a
thin flow here is not a thin market, it is the only door open.

**The advertisement is a PDF the Department publishes: it is NAMED, never
downloaded.** The post gives the title and the deadline beside it, and the
key is the document's own file name.

**The footer is not read at all.** It carries the Department's street address
and its office hours; the parse stops at the article body, so no street is
emitted **by construction, not by scrubbing** — a scrub can be dropped, a
boundary cannot be dropped without the guard seeing it.

`--open-on` keeps the posts whose stated deadline is on or after a day and
**says how many it dropped**; by default nothing is filtered, a post without
a deadline is emitted with `null` and counted, and a deadline already past is
emitted and counted — *the Department's own filing, never dropped in
silence.* `--country-code` stamps and says so.

**Tests and mutations.**
`APublicServiceRecruiterWhoseMinistryIsAHeadingAndNotAField`, both ways on
fixtures (two ministries and their posts, a post before any heading, a
paragraph-link placed exactly where it would be taken for a heading, a post
without a deadline, a deadline long past, `--open-on` and its drop count, a
footer whose street and telephone must not appear, a 200 without the article
body, a 404, a bad `--open-on`, the `www.` host refused). Mutation bench on a
detached copy, `python3 -B`, **10 / 10 red**: the ministry not carried
forward · paragraph-links taken as headings · the «no count» note dropped ·
the undated count silenced · the `--open-on` drop count silenced · the closed
count silenced · the document marked downloaded · the body not scoped to the
article · the scrub dropped · the host check dropped.
