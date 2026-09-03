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

## A tooling defect has a direction, and it points at "there is nothing"

**This is a claim about our own scripts, not about boards, and it changes what
deserves a second look.**

**A defect that breaks a request produces an emptiness. A defect that breaks a
count produces a zero. A defect that breaks a read produces an absence. There
is almost no bug that fabricates content.** So when the tooling is wrong, it is
wrong in one direction — and that direction is *giving up*.

**A plugin whose tooling decays does not get noisy. It goes quiet, and it looks
like it did a good job.**

> **A tooling error almost always errs towards "there is nothing", so an empty
> result deserves a second reading that a full result does not.**

**Measured on this repository's own scripts, 2026-09-03**, each verified rather
than recalled:

| The defect | What it produced |
| :-- | :-- |
| Five adapters read `<loc>` with a pattern blind to CDATA | **0 URLs** from a valid 2.37 MB sitemap |
| `taleez.py sitemap` read an argument its parser never defined | the command **crashed before the network** — it had never worked |
| A slug pattern of `[a-z0-9-]+` on Bumeran | **1 160 of 5 771 ads dropped, 20% of a board**, in silence |
| A facet pattern demanding a city segment | **1 260 of 3 953 read — 32%** — while reporting the rest as "forms not measured" |
| `_robots.py` treating an absent `Content-Type` as a wrong one | a valid `robots.txt` classed **unreadable without being looked at** |
| `employers.py` reading the file's own preamble as employers | would report a company's **absence of decisions as fact** |
| `--compressed` on a host with broken chunked framing | `200`, **0 bytes**, or a network error depending on what you recorded |

**And the counter-example, because "almost always" is the honest form.** The
undated-fact check in `employers.py` erred the *other* way: it reported four
undated facts in a file where two carried their date on a wrapped line. **That
one cries wolf, and its failure mode is being switched off** — after which the
real ones go unseen. So the exception ends in the same place as the rule.

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

**It is caught by a pair, like everything else here** — *links fetched* against
*distinct ids kept*. 800 against 281 is the finding; 800 alone is a good day's
work. So a sweep reports **what it counted, never what it fetched**, and the
two numbers travel together:

> `281 distinct advertisement(s) from 800 link(s) over 8 pages — a factor of
> 2.85.`

**A single number cannot disagree with itself.**

### The direction depends on what carries the number, not on what it is about

**A hand that copies is not a tool that runs, and they lean opposite ways.**

The rule above holds because a tool is *mechanically* constrained: a broken
request yields an emptiness, a broken count a zero, a broken read an absence.
**A person transcribing a figure has no such constraint** — and what gets
transcribed wrongly tends to be the flattering version.

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
| **A script** | towards *"there is nothing"* | a value that looks impossible — twelve zeros, 0 `<loc>` beside 3 193 `<lastmod>` |
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
