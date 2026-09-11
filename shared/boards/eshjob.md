# Board measurement — Eshjob.com (Iraq): a feed of posts, not a table of fields

<!-- verified: 2026-09-11 -->

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

## No HTTP route to the declared client — measured 2026-09-11, and it decides what may be built

**The rules permit; the transport refuses; nothing was read.** Taken in the
order the doctrine asks — the guard first, in its own turn, then the fetch
with its provenance:

```
12:32:33 UTC  _robots.allowed('eshjob.com', '/jobs')                 allowed True · rule None · certain True
              _robots.allowed('eshjob.com', '/jobs?location=erbil')  allowed True · rule None · certain True
              _robots.allowed('eshjob.com', '/')                     allowed True · rule None · certain True
12:32:46 UTC  bin/fetch-body.py https://eshjob.com/jobs              HTTP 403 · 25 bytes · not saved
12:32:57 UTC  bin/fetch-body.py https://eshjob.com/jobs  (--allow-refusal, twice)
                                                                     403 · 25 o · md5 9ccabba20b9f4ec7d18bd6644579e5bf · md5 stable ×2
12:32:58 UTC  bin/fetch-body.py https://eshjob.com/                  403 · 25 o · same md5
              body: "Your request was blocked."
```

**That md5 is the vendor default of `shared/robots-policy.md`'s family (1)** —
eleven hosts, the same 25 bytes to the byte, `eshjob.com` among them since
2026-09-08 — *and the same file records that a real browser was served 1 735
results here that day.* **So the 403 is aimed at the client, not at everyone**,
and the route this host leaves open is the browser, which is the route the
extension was not connected to provide on 2026-09-11.

**The data route the adapter would need was therefore not found — not because
it does not exist, but because the page that would name it is refused before
its script is served.** *The nine fetches of 2026-09-08 that answered 200
without the count were the last time this client was served a page at all;
today it is served the refusal.* **No adapter is delivered on this state, and
this section is the deliverable:** a dated *no HTTP route*, with the guard's
verdict, the status, the byte count, the two fingerprints and the identity.

**What would reopen it, in order of cost:** the browser route (the extension,
then a session reading the XHR the page makes for `Showing 1 to 20 of 1735`
— that call's URL is the adapter's route, if the rules permit it, and it is
guarded on its exact path before it is fetched); or the host answering a
declared client again, which nothing here can cause and which the next reader
measures rather than assumes.

## What this does not establish

**Nothing about the other 1 715.** *The census is page 1, and a later page
could be shaped differently — the count of cards without an advertisement was 2
of 20 here and is not a rate.*

**Nor that the corpus is all advertisements.** *One card seen earlier in the
feed was a message of thanks for a recovered colleague, filed under
`Education`.* **The site's 1 735 counts posts in a job feed, and a post is not
necessarily a vacancy.**
