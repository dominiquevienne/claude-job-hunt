# Present, plausible, and false

<!-- verified: 2026-09-02 -->

`shared/never-fail-silently.md` governs the transport layer: a response that
misleads, a zero that cannot be told from an absence, a 200 that is not a yes.
**This page is the layer below it** — the value that arrives, parses cleanly,
looks entirely ordinary, and is wrong.

**Nothing errors. Nothing is empty. A human reading the row would accept it.**
That is the whole difficulty, and it is why the test cannot be the value.

> **Plausibility is not a check. Provenance is.**
>
> You cannot look at `2035` and see that it means 20.35, or at `2026-09-01` and
> see that it is a re-listing, or at `80 of 100` and see that the tool counted
> the wrong thing. **The only question that separates them is: where did this
> number come from, and what did the thing that produced it actually measure?**

## The mechanisms, each found separately

**1. A unit or a currency that travels separately from the number.** Kalibrr
returns Indonesian salaries as `PHP 22962.742977478316 – 32803.91853925474`
while Philippine ones come back `PHP 17000 – 18000`. The round numbers were
typed by an employer; **the twelve-decimal floats are a conversion**, and the
label says PHP either way — wrong by a factor of ~250. `join.com` writes
`amount: 2035` for **20.35**: wrong by 100, and 2 035 reads like a salary.

**Two more instances of mechanism 1, both found 2026-09-03, and neither is
the board lying.** `mihnati.com` publishes `baseSalary.currency: "PKR"` on ten
Saudi advertisements of ten — Pakistani rupees on Jeddah and Riyadh salaries,
from the Pakistani platform underneath. **That one is the board's.** The other
two are ours:

- **`currency` is a sibling of `value`, not a child.** The shape eight
  adapters use to reach `minValue` — `one(jp["baseSalary"])["value"]` —
  **walks straight past it**. `batiactu.py` did, and a ledger carried
  `42000.00` with no unit while the page published `{"currency": "EUR",
  "value": {"minValue": "42000.00", …}}`.
- **Knowing the currency too well to write it down.** `adzuna.py` serves
  **nineteen country indexes through one code path**, and the API publishes
  **no currency field anywhere in its response** — so `salary_min: 90000` was
  CHF, GBP, BRL or ZAR depending on a flag. Three single-country boards
  omitted it for the opposite reason: obvious to whoever wrote the adapter,
  absent from the row a ledger keeps.

**The harm is the same in all three, and it is not that the number is wrong.**
`identifier` holding an employer name — mihnati's other defect — collides
*visibly*: two jobs at one company conflict and somebody notices. **A salary in
the wrong unit produces nothing visible at all.** It enters a ranking and comes
out as an exceptional offer, arriving filed under a field with the right name.

A repository-wide check now fails if any adapter emits a salary figure with no
field naming its unit.

**2. A machine field contradicted by the human field beside it.**
`michaelpage.ie` publishes `addressCountry: "GB"` on **21 Irish ads of 21**, in
the same block that says `addressRegion: "Republic of Ireland"`. Three of ten
national sites are wrong this way. **No line of adapter code differs between
the ten measurements** — the platform varies, not the reader.

**3. An estimate wearing a measurement's name.** Adzuna's `salary_is_predicted`
means the min and max came from its own estimator. The number is real; it is
not the employer's.

**4. A string that means "empty".** `€ Not Disclosed` on 73 cards of 100;
`Undisclosed` 11 times in 60; Kalibrr's `salary_shown` **true on 88%** where
about 20% carry an amount. A parser testing "non-empty string" reports 88%
coverage on a board that publishes 20%.

**5. A declared total larger than the data.** Colombia's public API answers
`totalPages: 5637` while `total_registros` says 262 275 — which is 5 245 pages.
Page 5 245 returns 50 rows; **pages 5 300 and beyond return zero, with HTTP 200
and no error.** A sweep that trusts the declared total reads ~390 empty pages
and reports a complete corpus.

**6. A date that measures a different event.** A jobup card's *"Il y a 3
semaines"* is the age of **this listing**; on a re-listed ad that is the age of
the re-listing. A ledger carried `2026-09-01` for an ad published `2026-07-14`
— **seven weeks out, and it decided which of two ads tied at 62% was ranked
first**, which decides what gets drafted.

**7. A parse that shifts columns.** Ten ledger rows of 474 contain `\|`, an
escaped pipe inside a cell. Splitting on `|` moved every column after it and
produced a row whose **status read `42`**. A wrong status means an ad silently
re-proposed, or silently buried.

**8. And the one that is not the board's fault at all: a measuring tool whose
method is wrong.** In one hour, two numbers from an audit written *for this
very issue*: it counted the request bodies four adapters **send** to their APIs
as potential leaks, and then reported **80 suspicious sites** that were almost
all a card built one line above. Both were clean, well-formed and false.

**Mechanism 8 has a name, and it is in `never-fail-silently.md`: blind
agreement** — a check and its object sharing a failure mode, so that agreement
proves nothing. Both of the false numbers above were produced by tooling
written to hunt this exact class, by somebody looking for it.

**Mechanism 8 is why this page is not called "boards lie".** A value's
provenance is the question whoever reads it must ask — and *your own script* is
a provenance like any other.

## A share is a share *of the thing you grouped by*

**A concentration measured over labels is a label concentration, not a city
concentration** — and the two differ by half. Measured on 239 Israeli cards,
2026-09-02: Tel Aviv appears **78 times under eight labels and three names**
(the usual one, the municipality's official one, an anglicised one), so
grouping by label reads **45%** where the city's share is **90%**.

**Character folding cannot close that gap**, because it is not a variation on a
name — `Tel Aviv-Yafo` *is* a different name. The knowledge that two names
denote one place is declared, never computed.

So the fix is the one this page always reaches for: **put it in the name** —
and name the **denominator** with it, because the two naive divisions do not
fail in the same direction:

| Divide the dominant label by | Error |
| :-- | :-- |
| **every card of the market** | **always low — an honest lower bound** (Taipei: 24% read, 58% real) |
| the cards *sharing its first segment* | **no bound at all** (Tel Aviv: 90% read, 45% real — 35 of 39, the city's other cards dropped from the denominator too) |

**Only the first may be called a lower bound.** Publish it as a *label*
concentration, over the whole market, and say so. Writing a
translation table instead would be the failure this page catalogues — **an
incomplete table looks exactly like a complete one**, corrected where somebody
thought of it and silently not elsewhere. And the cheap version of that table
is worse than incomplete: `X City → X` would fold **Quebec City into a
province** and **Mexico City, Panama City, Guatemala City and Kuwait City into
countries.**

**And the metric had missed it for weeks, for the reason that matters most
here: it grouped labels by first segment — the same way the helper it was
meant to audit compares them.** It saw four clean cities where there was one
dirty one. That is *blind agreement* (`never-fail-silently.md`), and it is why
a measurement built alongside the thing it measures proves less than it looks.

## One level up: a count is a claim about *something*, and rarely about matches

The user's question is **how many ads match me**. A board answers a different
question, and there are at least five different "different questions" —
measured 2026-09-02:

| What the board shows | What it counts |
| :-- | :-- |
| StepStone NL, *software developer*: **26** | 1 literal match and 25 related ads, by the platform's **own** decomposition |
| LinkedIn, a zero-result search | 7–8 suggestion cards, unmarked (#46) |
| `greatugandajobs.com`: **102 924 Jobs Posted** | a historical cumulative total |
| `enbek.kz`: **44 521 ads for 78 421 posts** | two correct counters measuring different objects |
| `mabumbe.com`: **44 156** | a WordPress archive counter inflated with expired ads |
| Colombia's public API: **262 275 offers** | true — but the corpus is grouped by operator, so a share read off consecutive pages measures the start of the index |

**`stepstone.nl` holds one Dutch "software developer" ad and serves a full page
of 25 cards.** Nothing in the markup distinguishes the other 24 — and **the
padding is heaviest exactly where the board is thinnest**, which is the worst
possible place for it.

**So: a reported total is not a match count, and it is not always a count of
open adverts either.** Where a board publishes its own decomposition, record
it. Where it does not, do not treat the total as matches.

**And mark the rows rather than dropping them.** `_match.py` marks each card
`literal`, `semantic?` or `regional?` from the card's own title and town — and
only `literal` is asserted, because the test is wrong on another language, on a
keyword that lives in the description, and on a location field naming a region.
**A test wrong in three known directions must not silently remove rows**; it
gives the reader a lead and says so on stderr while the run is happening.

## The flag is part of the measurement, and it destroys evidence

**Every convenience flag is a transformation.** `--compressed` replaces the
file with its transfer encoding; `-L` replaces the response with the last
response in a chain. **Both are the right default for fetching and the wrong
default for measuring**, and neither raises anything.

| Flag | What it hid | Where |
| :-- | :-- | :-- |
| `--compressed` | **sizes 2 to 7 times too small** — `%{size_download}` reports bytes *transferred* | four files measured at 373, 964, 133 035 and 219 309 against real sizes of 1 335, 2 190, 912 986 and 1 511 079 |
| `--compressed`, again | **3 255 reported against 5 582 counted** — on a WAF page whose *size was the signature* | a second occurrence, on a measurement that used size as its tell |
| `-L` | **a `302` reported as "never returns an error status"** | Jobvite: both a real and an invented token `302` to `?invalid=1`, and the operator names the reason in the query. The file had built an oracle on two title strings that no longer exist |
| `-L` | **a redirect loop read as a dead site** — `curl` gives up at the fiftieth hop | two hosts, where the truth is a trailing-slash loop and not a failure |
| `--compressed`, a third time | **it did not distort a measurement — it manufactured a failure** | `www.trabajo.gob.ec`: `curl: (56) chunk hex-length char not a hex digit: 0x1f`. Without the flag, `200` and **74 622 bytes** |

### The third one is a different kind, and it deserves its own name

The first four entries **distort a measurement of something that worked**. The
last one is not that. Verified 2026-09-03:

```
curl --compressed  https://www.trabajo.gob.ec/   → exit 56, http=200, bytes=0
curl               https://www.trabajo.gob.ec/   → exit  0, http=200, bytes=74622
```

**`0x1f` is gzip's first magic byte.** The server sends gzip while breaking the
chunked framing around it, so the transfer dies mid-body — **and only if the
client asked for compression.** The site is not blocking, not challenging, not
absent and not refusing. **It works.**

**A prober that always sends `--compressed` records this host as a network
error**, and every conclusion drawn from that — the country page, the "no
adapter possible" note, the absence in a survey — is downstream of a flag.

**And note what the transport failure did not do**: `%{http_code}` still says
**200**. A probe that records the status and not the byte count reads it as a
success with an empty body — the application shell of `lmis.mol.gov.jo` by
another road. **Which of the two wrong answers you get depends on what your
probe writes down**, and neither of them is the site.

**Where it sits against the responses that lie:**

| Shape | What it lies about |
| :-- | :-- |
| `202` with an empty body (tanqeeb) | what the server **did** |
| A `200` shell with no content (topjobs, LMIS) | what the server **did** |
| **Broken chunking under gzip** | what the server **can do** |

**It is the first case that belongs to both this file and the taxonomy of
misleading responses**, and the only one of the three where the client is a
participant: change one flag and the lie disappears. `shared/robots-policy.md`,
*A non-answer is not a refusal*, is the neighbouring rule — a transport that
fails to deliver a question is not a policy — with the addition that here **you
chose the transport.**

**The rules:**

1. **Probe without the flag first.** Add it once you know what it hides.
2. **Report the status of the first response, not the last** — and where a
   chain exists, record the chain.
3. **A size is a property of the decompressed body.** A tool reporting
   *"downloaded"* is not reporting a size.
4. **Say which flags a measurement used.** A figure without its probe is not
   reproducible — and *both* errors above were caught only by a second
   measurement disagreeing with a first, which requires the method to be
   written down.
5. **A transport error is a claim about your request, not about the site.**
   Before recording a host as unreachable, retry it with the flags removed.
   Exit 56 under `--compressed` and exit 0 without it is the same server,
   answering.

**And the same trap is the default in `urllib`, not only in `curl`.** It
follows redirects silently: of 63 fetch sites in this repository, **four record
where they landed** — and each of the four does so because the landing URL
turned out to *be* the answer. An id that does not resolve redirects to an
error page; an expired ad redirects to a category page carrying twenty valid
postings. **Where a redirect changes what the response means, the landing URL
is not diagnostics — it is half the result**, and `successfactors.py`,
`jobup.py` and `tenant_offer.py` are the worked examples.

*(That is a property of the default rather than a list of defects: most fetches
legitimately want to follow. The rule is to notice when yours is not one of
them.)*

## A tooling defect has a direction, and the direction is set by the layer that broke

**This is a claim about our own scripts, not about boards, and it changes what
deserves a second look.**

> **A tool that breaks *retrieval* impoverishes the world. A tool that breaks
> *reading* can enrich it with things that are not there.**

| The broken layer | Which way it errs |
| :-- | :-- |
| **Retrieval** — the request, a stale file, a compression nobody asked for, a redirect lost, `stderr` discarded | **emptiness, always.** There is nothing else it can produce |
| **Interpretation** — a grammar, a pattern, a way of splitting | **usually emptiness too — but it is the only layer that can invent** |

**So an empty result still deserves a second reading that a full one does not**,
because both layers can produce it. What changed is the other half: **a full
result is no longer safe by construction**, only rarer.

### How this file got the rule too wide, and it is the same fault it warns about

The first version read *"a tooling error almost always errs towards there is
nothing"*, full stop. **It was written from eighteen measurements that were
almost all retrieval defects** — a sample of one half of the phenomenon,
presented as the whole.

**That is this file's own rule on independence, broken on this file's own
doctrine.** Eighteen agreeing cases felt like strong evidence; they were
eighteen instances of one mechanism.

**The counter-example arrived the same day.** A counter of malformed
`User-agent` groups reported **41 files of 143**; the true figure is **6 of 76
— 8%**. A factor of seven, **in the direction of invention**, because it
treated consecutive `User-agent:` lines as separate groups when they form one.
`indeed.com`, `totaljobs.com`, `hays.fr`, `hellowork.com`, `infoempleo.com` and
`vieclam24h.vn` were all false positives.

**And an invented pathology looks like a discovery.** The false 41 presented
itself as a publishable result: a frequent pattern, a percentage, a list of
large boards. **An emptiness invites doubt; a fullness invites writing it up.**

**It was not caught by a number.** Every earlier defect announced itself with
an absurd figure — twelve zeros, 0 `<loc>` beside 3 193 `<lastmod>`. This one
was caught by **the names**: `indeed.com` and `hays.fr` do not belong in a list
of badly written files.

> **For a retrieval defect, the tell is a number that cannot be true. For an
> interpretation defect, it is a name that does not belong.**

*(Six of 76, incidentally, is not a curiosity to collect: `mtss.go.cr`'s `www`,
`ikman.lk`, `jobsireland.ie`, `mtps.gob.sv` and `apec.fr`'s `www` — **an
ordinary way to write a malformed file**, and reason enough for a parser to
handle it rather than to note it.)*

### The eighteen, which are all still true — and all of one half

**Measured on this repository's own scripts, 2026-09-03**, each verified rather
than recalled. **Read them now as what they are: retrieval and pattern defects
that impoverished**, not as evidence about the other direction:

| The defect | What it produced |
| :-- | :-- |
| Five adapters read `<loc>` with a pattern blind to CDATA | **0 URLs** from a valid 2.37 MB sitemap |
| `taleez.py sitemap` read an argument its parser never defined | the command **crashed before the network** — it had never worked |
| A slug pattern of `[a-z0-9-]+` on Bumeran | **1 160 of 5 771 ads dropped, 20% of a board**, in silence |
| A facet pattern demanding a city segment | **1 260 of 3 953 read — 32%** — while reporting the rest as "forms not measured" |
| `_robots.py` treating an absent `Content-Type` as a wrong one | a valid `robots.txt` classed **unreadable without being looked at** |
| `employers.py` reading the file's own preamble as employers | would report a company's **absence of decisions as fact** |
| `--compressed` on a host with broken chunked framing | `200`, **0 bytes**, or a network error depending on what you recorded |

**And one of them already pointed the other way, which should have been the
warning.** The undated-fact check in `employers.py` reported four undated facts
in a file where two carried their date on a wrapped line — **an interpretation
defect, inventing a fault that was not there.** It was filed as an exception
that "ends in the same place as the rule" because it gets switched off. **That
was true and it was not the point**: it was the second half of the phenomenon,
already measured, and read as a footnote to the first.

### The false full, which is rare and therefore worse

**Everything above says a defect errs towards emptiness. The exception is not
symmetrical, and knowing why is what makes it findable.**

A page past the end of a listing that answers `200` **with page one's contents**
does not make a sweep loop. **It makes volume.** A sweep that never terminates
gets noticed; a sweep that returns the same twenty advertisements for ever
under rising page numbers **looks like it is working**, and its output is
plausible at every row.

**And it is almost never a bug of ours.** That is the whole force of the rule
above: a broken request yields an emptiness, a broken count a zero. **Nothing
in our own code fabricates content** — so a full result that is false came from
the outside, from a server answering badly on purpose or out of indifference.

| Measured 2026-09-03 | What it did |
| :-- | :-- |
| `encuentra24`, page 31 of 30 | `200`, and **page one's twenty ads**. Pages 50 and 500 too |
| `hr.ge`, `/jobs/today` | 8 pages × **100 links = 800**, for **281 distinct ads** — and **page 4 returned a full hundred and zero new ones** |
| `jobology`, page 9999 | twenty plausible on-topic ads, a different twenty on each call |

**The same gesture on two boards on the same day, and only one of them is
honest**: hr.ge's page 50 returns nothing; encuentra24's returns page one.

### A refusal read as a fault, because the fault was the plausible reading

**The false full is a server returning content that is wrong. This is a server
returning a *refusal* that gets translated into a breakdown** — the same
family, *what qualifies itself by resemblance*, and a different mechanism.

**Measured, 2026-09-03.** One board answered **`403` to 226 of 524 requests —
43%**. The rate was read as throttling, and two days went into adjusting the
delay between requests. **The site's `robots.txt` refused the URL shape being
built**, to `User-agent: *`, and the file had been on disk for forty minutes.

**A repeated `403` genuinely is a rate limit sometimes**, which is why this is
not a rule about `403`s. The reading was not absurd; **it was untested.** What
was missing is not the right interpretation — it is any confrontation of the
one already held with the source that could refute it.

> **A plausible technical reading gets adopted without being put to the source
> that would refute it.**

**And the actionable form, which is worth more than the maxim:**

> **A refusal rate that is high and stable triggers reading the `robots.txt`,
> not tuning the delay.** 43% over 524 requests is not a badly set pace — a
> badly set pace yields to slowing down, and this one did not.

**That is the sign that was there and unread: the remedy did not cure, and a
remedy that does not cure refutes the diagnosis.** It refuted it for two days.

**And the two expressions of the refusal failed in different ways, which is
worse than the same failure twice.** The file was never read; the `403`s were
read and translated. **An absence of reading, then a misreading — and the
second held because the first was missing.**

### And the same family without the volume: what qualifies itself by looking right

A false full persuades by quantity. **Two things measured the same day persuade
by resemblance alone**, and they belong beside it because the reader accepts
them for the same reason — they look like what was being searched for.

| What was found | Why it passed | What it was |
| :-- | :-- | :-- |
| `…/jobs-job-offers` on Encuentra24 | a **guessed URL that answers** — an existence check succeeds | a redirect to the site root |
| *"All Job Ads on a Single Page"* on jobs.ge | a **string that names the feature** being looked for | the caption of a banner advertisement |
| `rd.computrabajo.com` | a **guessed host that answers `200` with 33 730 bytes of the right operator's site** | the **global** portal — the Dominican one is `do.` |

**A guessed name that does not resolve disqualifies itself**; one that answers
does not. **A string that describes a capability is not the capability.**

**And the third is the hardest, because even a brand check passes it.**
`rd` is what a Spanish speaker abbreviates *República Dominicana* to, and
`rd.computrabajo.com` answers `200` with a real Computrabajo page. *Is it
reachable?* yes. *Is it the right operator?* yes. **Only the `<title>`
separates the global portal from the Dominican site**, which is `do.` — so the
check that works is the one for the thing you actually wanted, not for the
thing you would have accepted. Both
were accepted by plausibility and refuted only by looking at what came back —
which is the same discipline as counting distinct ids instead of links.

**It is caught by a pair, like everything else here** — *links fetched* against
*distinct ids kept*. 800 against 281 is the finding; 800 alone is a good day's
work. So a sweep reports **what it counted, never what it fetched**, and the
two numbers travel together:

> `281 distinct advertisement(s) from 800 link(s) over 8 pages — a factor of
> 2.85.`

**A single number cannot disagree with itself.**

### And a third case, which is neither layer: a number nobody recomputed

**A hand that copies is not a tool that runs.**

Retrieval is *mechanically* constrained: a broken request can only yield an
emptiness. **A person transcribing a figure has no such constraint** — and what
gets transcribed wrongly tends to be the flattering version. This is not the
interpretation layer either: nothing was misread, a correct figure simply
stopped being true.

Measured the same day, on this repository's own Atlas: **36 counters could be
checked against their pages and 16 were wrong.** The nine untouched by that
day's work **overstated coverage, all nine** — one country by nineteen points.
**The opposite direction from the seven above**, and the difference is not the
subject, it is the carrier: those seven went through a script, these nine were
copied by hand.

**And the mechanism was not a typing slip, which is what makes it worth
writing.** The pages had *improved* afterwards — rows describing the same
refusal were merged, the denominator fell — and the summary kept the figure
from before the merge.

> **A number goes stale because the work behind it got better**, and nothing in
> it looks abnormal. There is no run of twelve zeros to raise an eyebrow.

**Two rules, then, and they do not simplify into one:**

| The carrier | Which way it errs | What catches it |
| :-- | :-- | :-- |
| **Broken retrieval** | towards *"there is nothing"* | a value that cannot be true — twelve zeros, 0 `<loc>` beside 3 193 `<lastmod>` |
| **Broken interpretation** | usually the same, **but it can invent** | **a name that does not belong** — `indeed.com` in a list of malformed files |
| **A hand transcribing** | towards *the flattering reading* | **nothing looks wrong** — only re-deriving it does |

**The second is the more dangerous, because a dashboard makes it credible**,
and the first is the one that gets noticed. So a figure that was copied rather
than computed needs re-deriving **on a schedule**, not on suspicion — there
will be no suspicion.

**And the parade that worked was the same one as below**: two numbers that must
agree, counted separately — the rows in each page, and then the visible
markers. They agreed on the 36, and that agreement is what authorised the
correction.

### What follows, and it is a habit rather than a check

**Nine of eleven tooling defects found in three days were caught because a
number looked odd — not one by a control.** Twelve zeros in a row. Two byte
counts identical to the byte. One `<loc>` in 7 864 bytes. 231 KB of HTML with
99 characters of text. **Every control was working. They were correctly
validating the wrong thing.**

So:

1. **A zero is a claim about your tooling before it is a claim about the
   world.** Re-derive it a second way before writing it down.
2. **Report the remainder.** *n of m*, always — a pattern that reads 32% while
   saying *"forms not measured"* is a true sentence doing the work of a false
   one.
3. **Compare two numbers that must agree.** `<loc>` against `<url>`; bytes
   against visible characters; ads found against the count the board states.
   **A single number cannot disagree with itself**, which is why every one of
   these was caught by a pair.
4. **A full result needs none of this.** The asymmetry is the point: the effort
   goes where the errors are.

## Repetition corroborates only if the measurements are independent

**A pattern published on five country pages and in a consolidated table was
believed because it kept recurring.** Kenya, Egypt, Ghana, Uganda, Tanzania:
five times the same two destinations at the top.

**It was 65 identical cards counted five times.** The samples overlapped by
92–96%, because a board with little local data answers with the same non-local
ads everywhere.

**Nothing in the procedure checked that the five measurements were
independent** — and five agreeing samples feel like far more evidence than one,
which is exactly the trap. It is *blind agreement* seen from the other side:
there the check shared the object's blind spot, here five checks shared each
other's input.

**So before treating repetition as corroboration, ask what the samples have in
common.** Two tenants of one vendor measured on different dates corroborate;
five country queries served from one pool do not.

## The rules

**1. Make the confusion impossible in the name, not in the documentation.** A
field whose meaning depends on a caveat gets a name that carries the caveat.
`kalibrr.md` is the model: it never emits `salary_min`. It emits
`salary_php_min`, `salary_php_max`, `salary_converted` — and the useless flag
as `salary_shown_flag`. **Prose is skipped; a field name is not.**

**2. Count values, never keys.** A fill rate is the share of rows carrying
usable information, not the share carrying the key. Every fill table says which
it measured.

**3. A converted or estimated figure is not the same field as a quoted one**,
and must never share its name.

**4. Where a second endpoint or a sibling field contradicts the machine field,
record the contradiction** rather than picking a winner. Michael Page's
`addressRegion` was right while `addressCountry` was wrong, and it is the
*pair* that is the evidence.

**5. Cross-check a suspicious value against a second source before trusting
it.** Kalibrr's original currency was discoverable only on the legacy endpoint;
that a second endpoint existed at all is what made the trap visible.

**6. Believe a declared total only where the data agrees with it**, and say
which one you used. A count the service publishes about itself is a claim, not
a measurement.

**7. Say what a value measures, not only where it came from.** *"Prefer the ad
page's date"* did not prevent the seven-week error; *"the card's date is the
age of the listing"* would have. Rule 1 applied to semantics rather than to
names.

**8. When a number surprises you, suspect the instrument before the world.**
Two of the eight mechanisms above were produced by tooling written the same
day, by someone who knew the failure mode and was looking for it. **A number
that arrives clean from your own script has a provenance too, and it is the one
nobody audits.**

## How to tell you are in this class

None of these announce themselves, so the tells are indirect:

- **A number that is round where its neighbours are not**, or twelve decimals
  where a human typed the value.
- **A rate near 100%** on something people usually omit — salaries, contact
  details, dates.
- **A field and its human-readable sibling disagreeing**, which is the only
  case here that is visible by looking.
- **A total that no page of data ever reaches.**
- **A result that flatters the thing you just built.** Mechanism 8 twice, and
  both times the number said the work was going well.
