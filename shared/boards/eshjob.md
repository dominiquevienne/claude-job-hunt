# Board measurement — Eshjob.com (Iraq): a feed of posts, not a table of fields

<!-- verified: 2026-09-08 -->

<!-- hosts: eshjob.com -->
<!-- script: none -->
<!-- countries: IQ -->
<!-- content: measured · 1 735 advertisements declared by the site's own `Showing 1 to 20 of 1735 results`, and the city filter declares a second number from the same backend — `location=erbil` returns 805 · 2026-09-08 -->
<!-- witness: a field census over the 20 cards of page 1, not an adapter — the question was which fields EXIST and which are only a sentence -->

**This card is a measurement and not an adapter**, and it says so because the
distinction decides what may be built here. *`shared/robots-policy.md` recorded
this host as a refusal fingerprint and nothing else; what it serves had never
been looked at.*

## The two numbers the site states about itself

```
Showing 1 to 20 of 1735 results          <- the corpus
/jobs?category=&location=erbil    805    <- one city, same backend
```

**Both are the site's numbers, not a reader's.** *That is the discriminant
`jobs-af.md` has and `kariera-mk.md` lacks*, and this host has it.

**But they are rendered client-side.** *Nine raw fetches of
`/jobs?location=<city>` returned HTTP 200 and **not one contained the phrase** —
the count is injected by script.* **A raw-HTML reader would see zero results on
a page that displays 1 735**, which is the `jobs.af` cold-load trap on a
different host.

## The field census — 20 cards on page 1

**18 of the 20 `div.card` elements carry an advertisement**; the other two do
not, and are not counted below.

| present on the card | 18 of 18 |
| :-- | :-- |
| category, from a fixed list of 17 | yes |
| relative time (`27 minutes ago`, `Just now`) | yes |
| free-text body, median 214 characters | yes |
| image | yes |
| two engagement counters | yes |
| a poster profile link | yes — **and it is the same account every time** |

**The poster is not the employer.** All 18 point at `/profile/29`, "Job
centre". *An adapter reading employer from that link would print one identical,
plausible, wrong company name on every advertisement in Iraq.* **That is the
value this census exists to prevent.**

**There is no per-advertisement URL.** One card of 18 carried any job link at
all. *Posts expand in place behind `... Read More`, so a ledger on this host
cannot key on an advertisement address.*

**And there is no `JobPosting` markup: `ld+json` count is 0.**

## What exists as DATA but is not on the card

**City is real and the card never shows it.** `location=erbil` returns **805 of
1 735** through a server-side query parameter, and the select offers nine
values — `Remote, Erbil, Sulaymanyah, Duhok, Karkuk, Halabja, Kalar, Ranya`.
**Category is likewise a filter, with 18 values.**

> **So city is obtainable by ITERATING THE FILTER, never by reading the body.**

## What is only a sentence

**Employer, salary, deadline, contract type and number of vacancies appear —
when they appear — inside Kurdish and Arabic free text**, mixed with emoji and
markdown emphasis. **No field carries them.**

**They were not extracted, and deliberately.** *Deriving them from prose is
exactly where a plausible-and-false value is manufactured, and the instruction
for this pass was to report presence rather than to attempt a reading.*

## What this does not establish

**Nothing about the other 1 715.** *The census is page 1, and a later page
could be shaped differently — the count of cards without an advertisement was 2
of 20 here and is not a rate.*

**Nor that the corpus is all advertisements.** *One card seen earlier in the
feed was a message of thanks for a recovered colleague, filed under
`Education`.* **The site's 1 735 counts posts in a job feed, and a post is not
necessarily a vacancy.**
