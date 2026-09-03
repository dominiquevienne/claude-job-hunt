# Never fail silently

**This is the plugin's first rule, and it outranks every convenience.** It
applies to both skills, every module, every adapter, every script — and to any
contribution added later.

A job search is invisible work with delayed feedback: the user finds out weeks
later, from a silence, that something did not happen. **They cannot audit what
you did not tell them.** A scan that quietly covered half its searches, a resume
quietly missing two jobs, an application quietly never sent — each looks exactly
like success until it is far too late to fix.

So: **anything that did not happen, happened partially, or happened on a guess
must appear in the run's own output.** Not in a log file. Not on request. In
what the user reads when the run ends.

## The five failures this rule exists to prevent

| Silent failure | What it looks like to the user | What you do instead |
| :-- | :-- | :-- |
| **A skipped step** | Everything seemed fine | Name it, say why, say what it costs, give the fix |
| **A partial result presented as complete** | "8 new ads" — from 3 of 8 searches | Report *n of m*, always. `Ran 3 of 8 searches (LinkedIn throttled after the third)` |
| **A guess dressed as a fact** | A confident postcode, a score on an unread ad, a claimed skill | Mark it: `~` for a provisional score, "to be established" for a missing field, and never claim a skill the record does not carry |
| **An unconfirmed action reported as done** | "Applied" for an application nobody saw land | `applied` requires a confirmation you *saw*. Otherwise `todo` + `send not confirmed` |
| **A silent cap** | Top-10 results from 40 found | Say what was dropped and why: `read 12 of 26 descriptions — stopped to stay under the board's rate limit` |

## What every run owes the user at the end

When **anything** was skipped, degraded, guessed or capped, close with a short
block that says so. Not an apology — an inventory:

> **Not done this run**
> - jobup: skipped — `enabled: true` but no `language` set. Fix: `/job-setup boards`
> - 3 of 18 descriptions unread — the list re-ordered; their scores are marked `~`
> - No `repos.md`, so scoring saw only what your exports declare

When nothing was skipped, **say that too**, in one clause. "All 8 searches ran,
all 12 descriptions read" is information. Its absence is what makes users
wonder.

## HTTP 200 is not a yes

**The dominant way this plugin fails silently is not a crash. It is a site
answering successfully while meaning "no".** Forty-two adapters have now been
built against live sites, and **every one of them** turned up at least one case
where a request that looks like it worked carries a refusal — or, worse, where a
refusal comes back looking like data.

They were all found the same way: by deliberately asking wrongly and looking at
what came back. None was visible in the response status.

| What was asked | What came back | What it actually meant |
| :-- | :-- | :-- |
| umantis, a vacancy at the wrong `Description` segment | `200` + the tenant's chrome | wrong URL — the segment is per **vacancy** |
| umantis, an unallocated tenant number | `200` + the vendor's marketing page | wrong host, not an employer with nothing open |
| umantis, a client-rendered tenant | `200`, 64 kB, **zero** vacancy rows | the listing is not in the HTML; the board is not empty |
| SmartRecruiters, an unknown tenant | `200`, `totalFound: 0` | wrong tenant **or** nothing open — and nothing can separate them |
| SmartRecruiters, `limit=500` | `200` with **100** results | silently clamped; the rest of the board is invisible |
| SmartRecruiters, `city=boston` | `200`, zero | wrong case — `Boston` returns 17 |
| jobup / jobs.ch, `location=geneve` | `200`, zero, on **both** boards | missing accent — `Genève` returns 11 |
| HiringCafe, a city without its region | `200`, **0** ads — the same object **with** the region returns 2 162 | an incomplete location, not an empty market |
| Lever, a location string the employer does not use | zero kept | the board was not empty; the filter was |
| Lever, the wrong one of its two disjoint hosts | `404` | the employer exists, on the other host |
| Workday, a hardcoded location facet name | filters nothing at all | the facet name is per-tenant configuration |
| SuccessFactors, `/search/?q=<anything>` | `200`, byte-identical each time | client-rendered shell; it lists nothing for anyone, ever |
| SuccessFactors, `/search/rss/` | `200`, HTML | not a feed — the one shape that should have bypassed rendering |

And the same trap runs backwards, which is worse, because the failure looks
like data:

| What was asked | What came back | What it actually meant |
| :-- | :-- | :-- |
| HiringCafe, `short_name: "ZZ"` — a country that does not exist | **124 plausible ads** | not zero, not an error: ads from nowhere in particular |
| Indeed, a search with no matches | the "no results" banner **and six valid cards** | browsing-history suggestions — harvest them and six unrelated ads enter the ledger |
| Michael Page, a search with no matches | `404` | a real zero, not a broken domain |
| Michael Page, an ad page | `200` with **invalid** JSON-LD | literal newlines inside JSON strings; a strict parser sees no ad at all |
| LinkedIn, a results page | `(25)` in `<title>` | the unread-messages badge — the same `(25)` appeared on 2 259 results and on 2 |
| **LinkedIn, a search with no matches** | the *no matching jobs* banner **and seven live ads**, inside the results container | browsing-history suggestions on a query whose true answer is zero — **the second board to do this**, and the container scoping that separates them on a normal page does not separate them here |

### What follows from it

**1. Never convert an empty result into a statement about the market.** *"No ads
matched"* is a fact about a request. *"They are not hiring"* is a claim about the
world, and on the boards above the two are routinely different. Say which one
you are reporting, and if you cannot tell them apart — SmartRecruiters, by
construction — **say that too**.

**2. Every adapter must document its zero-shaped answers**, alongside its
selectors. An adapter that describes only the happy path hands the next reader a
zero with no way to interpret it. See the contract in `shared/boards/README.md`.

**3. Prefer a refusal to an empty result.** Where an adapter can tell that the
request itself was wrong — a vendor page, an unparseable block, a shell with no
rows — it should **fail loudly with its own exit code** rather than print
nothing. Printing nothing is indistinguishable from a board with nothing on it,
which is precisely the confusion this page exists to prevent.

**3b. A truncated pass is neither a success nor a breakage, and it needs its
own exit code.** HiringCafe throttles by the number of pages a run asks for —
`--pages 6` was refused eight times out of eight while one page at a time,
25 s apart, returned six of six. An adapter that dies on the first refusal
reports the same exit code as a board whose payload has changed shape, and a
sweep that got five pages of six has no way to say so.

So `hiringcafe.py` now exits **6 for throttled** and keeps **2 for broken**,
prints how many pages of how many it read, and says the rest were never
fetched. **The rule generalises**: where an adapter can obtain part of what
was asked, it must report the part, name the shortfall, and exit with
something the caller can tell apart from both success and failure. This page's
principle runs in both directions — a silent zero is one failure, and a
truncated sweep reported as a clean finish is the other.

**3c. A zero can come from the question, not from the board — and that one
is invisible from the response.** Every other entry on this page is a reply
that misleads. This one is a *request that cannot succeed against a board that
is working perfectly*: on Adzuna's Swiss index `Entwickler` returns 12 666 and
`développeur` returns **0**, with HTTP 200 and no error, and this project
builds its search terms from the user's own profile. **A French-speaking user
searching in French is handed an empty market that has twelve thousand jobs in
it.**

So an adapter that can return zero says what a zero cannot distinguish —
`skills/job-scan/scripts/_zero.py` is the shared sentence — and never lets the
run conclude the market is empty before the query has been asked in the
market's language. **Naming it does not find the ads; it stops the sweep
concluding they do not exist**, which is where the damage is.

**Where to go next on it:** `shared/search-language.md` holds the map, the
table of measured terms and — the part that matters most — **what still is not
covered**. Chiefly this: the trigger is a zero, and *a thin result misleads
just as much*. `informaticien` returns 129 of the Swiss index's 81 516 ads, 1%
of the market, and nothing fires. The same is true of a filter that quietly
drops most of an index: `category=it-jobs` on Adzuna's Swiss board returns
1 150 against 12 691 for one German keyword, because 70.7% of that index is
unclassified. **Neither is zero, so neither trips the check on this page.**

**Its corollary reaches every fill rate this repository publishes**: on 50
German Adzuna ads, a salary appeared on 0 and `contract_type` on 0. *A fill
rate measured in one language is not the board's fill rate.*

**3d. `try: … except: continue` is where boards go missing.** Every
`ld+json` reader here skips a block it cannot parse and carries on, so an
invalid block and an absent one are indistinguishable by the time the row is
written — and the row says the board publishes no structured data. Measured
2026-09-02: `json.loads` reads **0 of 3** Michael Page ads and **3 of 3** with
`strict=False`; ten of eighteen readers demanded a double-quoted `type="`
attribute that one board already writes with single quotes.

`skills/job-scan/scripts/_ldjson.py` is now the single reader, and its real
output is not the JSON — it is **`absent_reason()`, which says whose failure
this is.** "No JobPosting here" and "we could not read what is here" are
different sentences, and only one of them should make somebody go and measure
the board.

**3e. And the layer below this page: a value that parses cleanly and is
wrong.** Nothing on this page reaches it — there is no error, no empty result,
no zero to interrogate. `PHP 22962.742977478316` is an Indonesian salary
converted without its label; `amount: 2035` is 20.35; a ledger date seven weeks
out was a re-listing; `totalPages: 5637` overstates a corpus by 390 pages; and
two of the eight recorded mechanisms were produced by tooling written to hunt
this exact failure. **`shared/plausible-and-false.md` holds them, and its rule
is that plausibility cannot be the test — provenance is.**

**4. When you write an adapter, ask wrongly on purpose.** A wrong tenant, a
wrong case, a missing accent, an oversized page, an id that does not exist. That
is where every entry in the tables above came from, and none of them would have
been found by reading the site's documentation or the adapter's own code.

## Two kinds of wrong, and only one is visible in the response

*Written by two sessions working this repository in parallel — one on the
French boards, one on the country series — after a day spent finding the same
thing on boards that have nothing to do with each other.*

The section above is about a `200` that means no. This one is about the shape
underneath it, because after enough cases the failures stopped looking alike:

**A wrong body behind a right status.** The server answered something other
than what it sent — a challenge, an interstitial, a compressed stream you did
not decompress, or a payload that contradicts itself. **You can catch all of
these alone**, by looking at what came back and asking whether it is the kind
of thing you requested, and whether it agrees with itself.

**A right body behind a wrong question.** The payload is valid, internally
consistent and describes real jobs. It simply answers something you did not
ask. **You cannot catch this alone.** Nothing in the response is wrong, because
the response is not lying — the question was.

The second class has exactly one member below, and that is the point of naming
it: it is the only failure here that a response cannot betray, however
carefully you read it.

### The catalogue, as of 2026-09-01

**Wrong body, right status** — the response can betray itself, if you check:

| Signature | Where | The tell |
| :-- | :-- | :-- |
| `202 Accepted`, `Content-Length: 0`, `x-amzn-waf-action: challenge` | **tanqeeb** — 0 bytes on both observations | the header, which the WAF deliberately exposes to browser JS via `Access-Control-Expose-Headers` |
| the same, body 0 then **2 450** bytes | **welcometothejungle** — 10 of 10 challenged at one request per 6 s and again per 12 s | a 2xx whose body is too small to be an ad |
| `200` + an interstitial, 6 183 bytes, *"Pardon Our Interruption"* ×3, carrying `<meta name="robots" content="noindex, nofollow">` | **dubizzle**, on the URL its own `robots.txt` advertises as its sitemap | a page politely asking not to be indexed, where XML was promised |
| `200` + `application/x-gzip` read as text — 286 bytes, **0** `<loc>`; decompressed, 906 bytes and 5 sub-sitemaps | **jobindex.dk** `/sitemap.gz` | the magic bytes, and a length no sitemap index could have |
| `200` + a **self-closing** root: `<urlset xmlns=… xsi:schemaLocation=…/>`, 167 bytes gzipped | **jobindex.dk** `googleforjobs.gz` — the real zero, while `company.gz` holds 3 734 URLs and `content.gz` 1 507 | none, and none is needed: this one is honest. A complete, schema-referencing, valid sitemap containing nothing |
| `200` + a field contradicting its neighbours — `country: SG` on **90 ads of 90**, beside `region: United Arab Emirates` (54), Saudi Arabia (8), and `location: Dubai` (34), Abu Dhabi (11), Riyadh (8) | **michaelpage.ae** | **not in any field — between two of them.** Compare two that must agree, rather than trusting one |
| `200` + twenty plausible on-topic ads past the last page, a different twenty on each call | **jobology** — page 9999 answers like page 9 | the same URL twice does not return the same thing |

**And one that is not on either axis: a failure the client asked for.**
`www.trabajo.gob.ec` sends gzip while breaking the chunked framing around it,
so `curl --compressed` dies at exit 56 on `0x1f` — gzip's magic byte — while
the same URL without the flag returns **74 622 bytes** and `200`. The status
line still reads `200` either way. **The two rows above lie about what the
server did; this one lies about what it can do**, and the lie is undone by
changing one flag on our side. It is written up in
`shared/plausible-and-false.md`, *The flag is part of the measurement*, which
is where the rule to probe without flags first already lives.

**Right body, wrong question** — nothing in the response is wrong:

| Signature | Where | Why it cannot betray itself |
| :-- | :-- | :-- |
| An ordinal read as a code | **anefa** — department `29` returns 24 real farm jobs in the **Eure-et-Loir**, 400 km from the Finistère, because Corsica takes two slots in the list and every department past 21 is shifted by one | every field agrees with every other. The ads are genuine, the department is genuine, the postcodes match the towns. Only the question was wrong, and the response has no way to know |

| A redirect answering for the ad | **jobup / jobs.ch** — an expired ad `301`s to its trade's **category page**: 497 kB, a `<title>` reading *"102 offres…"*, **twenty valid `JobPosting` blocks**, zero mention of the job | The twenty ads exist and are genuinely open. **Nothing in the response is false** — it answers a question nobody asked, and the more carefully a check validates what it finds, the more confidently it is wrong |

That second row is the one to read before adding a third: it took a check that
**follows redirects and verifies structured data** — both good habits — and
turned them into a false *open* with twenty pieces of evidence behind it.

### Caught by the volume, not by the nature

**Three silent failures on 2026-09-02 were found because the number looked
odd — not one of them by a check.**

- **Two collectors on one `.jsonl`**, noticed because the log showed **two line
  formats** — the data itself was still clean, and would have stayed clean
  until the first loss.
- **A board serving 231 kB of HTML for 99 characters of visible text**, which
  turned a script's "no Ge'ez characters found" into a measurement of nothing.

**The lesson is not to add a check for each; it is that a plausible number
deserves a second look when it arrives in an implausible quantity.** A rate of
exactly 100%, a page whose size and content disagree by three orders of
magnitude — **neither is wrong on its face, and both were.**

### A value and its validity must travel in the same object

**A third case looked like the two above and is not.** A triage over
twenty-seven countries recorded **twelve zeros, none of them an empty market**.
But the tool had not been silent — it printed, for each one:

> `THE SWEEP IS PARTIAL: 0 of 1 page(s) read before the site refused (HTTP 403
> after 4 attempts). … **Do not report this as a complete pass.**`

…and exited non-zero. **The adapter had anticipated this exact error and named
it.** The caller redirected stderr to a log, read stdout, and wrote `0`.

**So the failure is not a missing warning — the warning was perfect. It is
that the number and its validity travelled on different channels, and only one
of them was read.**

> **Separating a value from its validity is enough to lose the validity.** A
> function that returns a figure on one channel and its caveat on another has
> already lost: the caller need only read one, which is the ordinary case.

That is a design argument, not a wording one, and it applies to everything this
repository exposes — `check`, the probes, the counters. **Here the validity
rides on the exit code**, which is why every refusal in these scripts exits 2,
6 or 7 rather than returning an empty list: a consumer that ignores the exit
code has thrown away the only part of the answer that says whether the rest
means anything.

**And the reason it was caught at all is not to be mistaken for a safeguard.**
At twelve of twenty-seven the implausibility is obvious. **At two of
twenty-seven — "these two countries have no ads in the international corpus" —
it would have passed, because it is plausible for those two.** An error gets
through when its result resembles what one already believed.

### Blind agreement

**A check and its object can share a failure mode — and then agreement proves
nothing.**

It is not a third family, and it is deliberately not one: the two families
above classify by **where the failure is**, and this classifies by **why nobody
saw it**. It applies to both of them, which is why it lives here as a note and
not as a heading.

**The name exists so it can be cited**, because it is not a curiosity — three
instances turned up in one day, on three different layers: **1. The transport layer.** A SuccessFactors control test compared an ad's page
against a deliberately invented id and concluded *does not resolve* when the
two matched. The reasoning was correct; they matched because **both** requests
had been built with a URL shape that tenant does not serve, so both landed on
the same error page **for different reasons**. The comparison meant to settle
the question confirmed instead, and a live vacancy was reported unresolvable.

**2. The measurement layer.** A concentration metric written to audit a
city-normalisation helper grouped labels by their first segment — **the same
way the helper did** — so it saw four clean cities where there was one dirty
one. It shared the blind spot of the thing it was auditing.

**3. The tooling layer.** An emit audit written to find fields that leak
counted the request bodies four adapters **send** to their APIs, then called
eighty call sites suspicious that were a card built one line above. Both
numbers were clean, well-formed, and false — **and both flattered the tool that
produced them.**

**The tell, where there is one, is that the check and the object were built by
the same hand, in the same session, on the same assumption.** A control that
agrees with what it controls has said nothing until you know it could have
disagreed.

That first row is alone, and it should stay hard to add to. Two nearby cases that
look like it are not: `batiactu`'s region filter matches the *employer's name*
rather than the job's address, and `monster` echoes *"Lyon, France"* in its own
heading while serving **Lyon, Mississippi** — both catchable by comparing the
answer to the request, without leaving the response.

### Three rules that follow

**1. The status code is not the answer. Only the payload is.** Before counting
anything, ask three things of the body: is it the *kind* of thing you asked for,
is its size plausible, and **does it agree with itself**. A `202`, a `200` and a
`429` are equally capable of carrying nothing.

**2. Wait for the second success.** On `figaro-emploi.md`, `fetch()` from an
open tab carries the page's clearance and the whole sweep runs from one tab. On
`wttj.md` the **first two** fetches return the ad and every one after that is
challenged. One success can be the wall not having noticed yet — and the
same-origin assumption turned out to be **per site, not a property of the
technique**.

**3. Some of these are ours.** Two entries here were not a site misleading us:

- A `429` from **NAV** swallowed by an `except: return None`, which became
  *"0 dated ads"* and came within one page of being published as a measurement.
- A success test written as *"body larger than 1 000 bytes"*, which counted a
  **2 450-byte challenge page** as an ad and reported *"5 of 5 served"* when
  none were.

Neither is the worse one: the first was caught before publication, the second
shipped. A catalogue of ways sites mislead you is read once. A catalogue where
two of the entries are your own error-handling is one you check your code
against. **Both were found by re-reading a result that looked fine**, which is
the only method that finds them.

### And the corollary for a guard

When a guard is added because a symptom was reported elsewhere, **check whether
the bug exists here before fixing it**. On `wttj.py` the decoding was already
correct — `Content-Encoding: gzip`, one decompress, 10 000 `<loc>`, identical
with and without `Accept-Encoding`. The guard shipped anyway, because *the
absence of a bug is not the presence of a defence*: nothing in that script would
have distinguished a healthy empty answer from an unreadable one. Zero URLs now
dies naming decompression, and says why a genuinely empty board looks different
— it is still a `<urlset>` with tags in it, unless it is `jobindex`'s, which
closes itself in fourteen characters and means it.

## Empty is a result, not a silence

**First establish that it is a zero** — see the section above; on several boards
an empty result is a refusal wearing a `200`. Then report it.

Zero new ads, zero matches above threshold, zero pending rows — **report the
zero and why it happened**: how many ads were seen, how many were already in the
ledger, how many were discarded and on what grounds. A run that ends with
nothing to show and says nothing is indistinguishable from a run that broke.

### Establishing it: look in the same document for a count that ought to match

The cheapest way to tell a zero from a misread is to find, **inside the
response you already have**, a quantity that could not be what it is if the
zero were true.

The worked case is `hays-fr.md`. Its sitemap yielded **0 `<loc>`** — and, from
the same bytes, **3 193 `<lastmod>`**. A sitemap with dates and no URLs is
impossible, so the reader was wrong rather than the file. Nothing in the HTTP
layer said so: 200, valid XML, 2.37 MB, correct content type.

**Pick the mandatory sibling, not a convenient one.** The rule as first written
keyed on `<lastmod>`, which is **optional** in the sitemaps.org schema: a valid
sitemap may carry none, and the check would then fire on a healthy file. The
container is what must be there. So, for sitemaps:

> Zero `<loc>` inside a non-zero number of `<url>` blocks cannot occur in a
> valid sitemap. Report the parse failure, never the count.

Every sitemap reader in `skills/job-scan/scripts/` makes that comparison — see
issue #55, which is also a record of how a stale count propagated through three
sessions because it was relayed instead of re-derived.

The shape generalises past sitemaps: a JSON-LD ad page that yields no
`JobPosting` but **zero `ld+json` blocks at all** is unread, not undescribed
(`infoempleo.md`); a listing whose card count is zero while its pager still
announces N pages is unread, not empty. **A correct pattern is a fact that
expires. An invariant catches the next wrapper without being told about it.**

### And the same rule applies to what we print

The paragraphs above were written as if this were only about reading a board.
It is not. **Two counters of the same object have to agree, ours included.**

`recruitee.py` shipped a run summary that said *"39 of 145 state a figure — and
the period is {month: 50}"*: **fifty units for thirty-nine salaries.** Some
offers carry a `period` with no amount, and the two counters were tallied over
different sets. Nothing was wrong with the board; the adapter's own output was
the thing that failed the arithmetic it exists to apply.

So before a run prints two numbers about the same thing, check that they can
both be true. If the counts are drawn from different subsets, say which — the
fixed line reports the orphans separately rather than folding them in. A
summary is a claim like any other, and *"it was only the log line"* is not a
defence: the log line is what the user reads.

### A field can be constant because nobody asked the question

The counterpart to a zero that is really a misread: **a value that is present
everywhere because it was never a variable.**

| Board | Field | Reads as | Actually |
| :-- | :-- | :-- | :-- |
| `empleate.md` | `modality` | remote-work status | `No informado` on 25 790 of 28 099 |
| `platsbanken.md` | `workplace_model` | on-site / remote / hybrid | `Arbete på plats` on 300 of 300 |
| `platsbanken.md` | `salary_type` | pay is documented | filled on 300/300, an amount on **0**/300 |
| `turijobs.md` | `salary` | a salary is stated | the object on 40/40, `salaryVisible` on 27, a figure on **2** |
| `recruitee.md` | `status` | the ad is live | `published` on 238 of 238 — the endpoint serves nothing else |
| `oposiciones.md` | `estadoPlazoF` | the deadline is open | `Abierto` on 76 050 of 76 050, **including 498 expired** |

**A field whose value is constant because the question was never asked looks
exactly like a field that is well filled.** A coverage check reports 100% on
every row of that table, and five of the six say nothing at all.

Two ways to tell them apart, both cheap: count the **distinct values**, not the
filled ones — one distinct value across a large sample is the signal — and
check the field against something it should correlate with, as
`oposiciones.md` does by comparing `estadoPlazoF` with the closing date it
claims to describe.

## An empty result deserves a second reading. A full one does not

**Everything above is about a board lying to you. This is about your own
scripts**, and it has a direction: a defect that breaks a request makes an
emptiness, one that breaks a count makes a zero, one that breaks a read makes
an absence. **There is almost no bug that fabricates content.**

So **a plugin whose tooling decays does not become noisy — it goes quiet, and
it looks like it did a good job.** Which is this file's own failure, arriving
through the tooling instead of through the site.

**Before writing down that something is empty, gone, or not found: re-derive it
a second way.** `shared/plausible-and-false.md`, *A tooling defect has a
direction*, holds the seven measured cases and the four habits — the strongest
being: **compare two numbers that must agree**, because a single number cannot
disagree with itself.

## Errors

- **Never swallow a tool error.** If a call fails, say which one and what it
  means for the result.
- **Never retry the same failing action in a loop.** Two attempts, then stop and
  tell the user what you tried, what happened, and what you need from them.
- **Never route around a blocker that exists for a reason** — a login wall, a
  file picker, a modal that is not in the accessibility tree. Those are dead
  ends by design. Hand them over explicitly; do not improvise a workaround and
  report success.
- **A missing prerequisite is not an error, it is a task** — see
  `shared/prerequisites.md`. Name it, offer the fix, take the fallback.

## Degrading is allowed. Degrading quietly is not

The plugin is *built* to keep working with less: no browser, no LaTeX, no
`repos.md`, no board enabled. Every one of those paths is legitimate and should
be taken rather than stopping the user's work.

**The only thing that is forbidden is taking one without saying so.**

## What you learn belongs to the next user too

Everything above is about not being silent toward **the person in front of
you**. This section points the same rule at everybody else who runs this plugin,
and it is the one that gets skipped, because **nothing in the run fails when you
skip it**.

**Anything you learn that would be true for another user of this plugin goes
upstream.** Not only *a board did not sweep*: a trap in a site's behaviour, a
response shape that lies, a defect in one of the scripts, an adapter that
returns the **wrong** data rather than none, a method that turned out to be
wrong, a capability nobody had noticed.

### The test, and it is not "is this about a board"

> **Would this still be true on another machine, for another person, tomorrow?**

| Answer | Where it goes |
| :-- | :-- |
| **Yes** — the site behaves that way for everyone, the script carries that defect, the method was wrong | **Upstream**, through `board-request` |
| **No** — this user's config, their credentials, their profile, one search that genuinely has no results, a network blip that did not reproduce | **Local.** Say it in the run's output and stop there |

**A local workaround reaches nobody and does not survive.** The plugin runs from
a version-pinned cache
(`~/.claude/plugins/cache/claude-job-hunt/claude-job-hunt/<version>/`) and the
next update overwrites it. The issue is the only route by which one user's
finding becomes every user's fix.

### The narrow trigger was not enough, and the repository's own history says so

The rule used to fire on one shape — *a board with an adapter failed to sweep*,
plus `cover-letter`'s *a URL from a board with no adapter*. Of this repository's
**46 issues that record a field finding**, that trigger names **10**. The other
**36** became issues because somebody thought to file them.

*How that was counted, so it can be disagreed with:* 54 issues on 2026-09-03,
less the eight the user asked for as capabilities rather than found in the field
(#33, #34, #40, #42, #47, #50, #52, #69), leaves 46. The ten the old trigger
names are #5, #7, #31, #32 and #35 — a URL from a board with no adapter — and
#55, #57, #59, #64 and #76, where the sweep crashed or returned nothing.
Classified by title against the trigger's own wording; **the borderline calls
were all resolved in the old rule's favour**, so 10 is its ceiling.

The five most recent are the clearest case. #85 to #89, all closed, all from
field measurement, and **not one of them is a board that failed to sweep**:

| # | What it recorded | What the sweep did |
| :-- | :-- | :-- |
| #85 | Character folding does not reconcile `Tel Aviv` and `Tel Aviv-Yafo` | Worked |
| #86 | `countries` is not a workplace — 71 Ghanaian cards labelled Gulf, two of them actually there | Worked |
| #87 | The SuccessFactors tell is the `JobPosting` block, not the `<title>` | Worked |
| #88 | An expired ad answers `200` with twenty `JobPosting` blocks, none of them the ad | Worked, and returned an ad that is gone |
| #89 | "A date in the past means the ad is closed" is false — a BCV ad open 18 days past its printed deadline | Worked, and would have closed a live vacancy |

**Every one of them is worse than a failed sweep, because a failed sweep
announces itself.** These returned a clean, plausible, wrong answer — the
failure mode the whole of *HTTP 200 is not a yes* exists to catch. It would be
a strange file that catalogues that failure for forty-two adapters and then
lets each new instance of it die in one session's memory.

### What this does not change

- **It is not a prompt on every run.** `board-request` §4 still asks once, still
  needs an explicit yes, and §3's duplicate check still runs first — including
  against **closed** issues.
- **The privacy pass is unchanged, and matters more here rather than less.**
  Findings about scripts carry paths, queries and sometimes the user's own data.
  §4's rules on search URLs, page dumps and session identifiers apply to the
  wider set exactly as written.
- **It never interrupts.** The finding is filed after the user's task finishes,
  in one clause at the end — never as a question in the middle of it.
