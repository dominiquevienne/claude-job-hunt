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
