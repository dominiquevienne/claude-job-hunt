# Board measurement — Eshjob.com (Iraq): a feed of posts, not a table of fields

<!-- verified: 2026-09-12 -->

<!-- hosts: eshjob.com -->
<!-- script: none -->
<!-- countries: IQ -->
<!-- content: measured · **1 677 posts** declared by the site's own «Showing 1 to 20 of 1677 results», read from a connected browser tab, and the pager closes on it exactly — 83 pages of 20 plus a last page of 17 = 1 677 (pages 1, 2 and 84 read, 20 + 20 + 17 cards, 0 overlap between 1 and 2); 1 735 on 2026-09-08 by the same sentence · 2026-09-12 -->
<!-- witness: a field census over the 20 cards of page 1, not an adapter — the question was which fields EXIST and which are only a sentence -->
<!-- route: browser · 1677 · 2026-09-12 -->

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

## 2026-09-12 — the browser route, MEASURED (#222): there is no XHR, the data route is the page

**12:05–12:06 UTC, Claude in Chrome connected, one tab.** Guard first, on
the exact paths — `/`, `/jobs`, `/jobs?location=erbil`: `allowed True,
certain True`. The tab is served: no challenge, no interstitial — **borne 0
held**, the 25-byte 403 goes to the declared HTTP client and to nobody else.

```
navigate https://eshjob.com/jobs            200 — «Showing 1 to 20 of 1677 results», pager 1 2 3 … 83 84
the page's own network calls                only /check-cache, twice — **no XHR carries the feed: the listing is server-rendered HTML**
20 <div class="card"> per page              each with a numeric post id in its element ids — description-28556, short-desc-28556, read-more-28556, like-btn-28556
                                            poster (a /profile/<n> link — the card of 2026-09-08 says it is NOT the employer), «43 seconds ago», a category, the text in #description-<id>
fetch /jobs?page=2                          200 — 20 cards, 0 shared with page 1
fetch /jobs?page=84                         200 — 17 cards
                                            **83 × 20 + 17 = 1 677 — the pager closes on the site's number exactly.**  12:05:47 UTC
```

**The route the 11th could not find exists and is the plainest one: the
paginated HTML itself.** *The 8th's sentence «Showing 1 to 20 of 1735» is
printed by the server, not fetched by a script — so there is no call to
guard beyond `/jobs?page=N`, which the rules open.* The stable id is the
number in the card's element ids (`28556`); **there is still no URL per
post** — the site addresses a post nowhere but in the feed — so an
advertisement URL cannot be rebuilt and the row carries the page it was
read on. 1 677 on the 12th against 1 735 on the 8th: the feed shrinks as
posts age out.

**The procedure a session follows — this is the adapter, at the same title
as a script (decision of 2026-09-08):**

1. guard `eshjob.com` on `/jobs` and `/jobs?page=N` before anything;
2. `navigate https://eshjob.com/jobs` in the session's own tab; read the
   «Showing 1 to 20 of N results» sentence — **N is the site's count**;
3. for each page — from the tab, `fetch('/jobs?page=N')` and parse the
   `.card` blocks (or navigate) — collect the id from `#description-<id>`,
   the poster, the age label, the category, the text; 2 s apart, 84 pages
   on the day;
4. print **«n cards over p pages, site states N»** — equal, or k short;
   and say that a card is a *post*, not necessarily a vacancy (the census
   of the 8th: 2 of 20 were not);
5. no per-post URL exists: the ledger id is `eshjob:<post id>` and the
   URL is `/jobs?page=<p>`;
6. close the tab.

## What this does not establish

**Nothing about the other 1 657 (1 715 on the 8th).** *The census is page 1, and a later page
could be shaped differently — the count of cards without an advertisement was 2
of 20 here and is not a rate.*

**Nor that the corpus is all advertisements.** *One card seen earlier in the
feed was a message of thanks for a recovered colleague, filed under
`Education`.* **The site's 1 735 counts posts in a job feed, and a post is not
necessarily a vacancy.**
