# Board adapter — Kariera.mk (North Macedonia): refused to our client, open to a browser

<!-- verified: 2026-09-12 -->

<!-- hosts: kariera.mk -->
<!-- script: none -->
<!-- countries: MK -->
<!-- content: measured · **291 cards** in the exhausted front-page feed from a connected browser tab (268 «активен до» + 23 «плата од», a clean partition, 197 with an employer grouping) — 282 on 2026-09-08 by the same instrument; the site states no total, and the 391 floor (53 employer pages) is the 8th's · 2026-09-12 -->
<!-- witness: at least 391 live advertisements, counted through the company pages rather than the feed; the archive is a different question — `sitemap.xml` holds 17 604 `/job/` URLs -->
<!-- route: browser · 291 · 2026-09-12 -->

**The apex is the only form measured.** `www.kariera.mk` serves the apex's
rules and the guard reports it as such; this card claims nothing about that
form, and declares no `host-forms:` because it declares no script to reach
them. *The 2026-09-08 browser reading below also used the apex throughout.*

**North Macedonia's named board, and the first card for it.** It has been
mentioned in this repository since 2026-09-05 with no status established;
this card establishes one and it is not coverage.

## The rules are silent about us — which is not the same as open

```
User-agent: Googlebot-Image
Disallow: /uploads/articles
Disallow: /uploads/files

Sitemap: https://kariera.mk/sitemap.xml
```

**One group, and it names a crawler that is not us.** No `*` group, no record
for either of this project's tokens. So nothing here binds us, and nothing
here was written for us: *silence towards us, not a permission.*

**This is the second shape of the groupless file found on 2026-09-07**, and it
is not the shape that opened #180. `ihararejobs.com` carries seven `Disallow:`
lines **above any `User-agent:`**; this one carries a group addressed to
somebody else. They reach the same place — `group_for()` returns `None`,
`_star_group()` returns `[]` — and they are different facts, which the guard
said in one identical and partly false sentence until it was corrected the
same day.

*The file also declares its sitemap, which is a coordinate, and the coordinate
is refused at the transport.*

## The transport refuses, at the root and not only at a path

```
GET /               403   25 bytes   md5 9ccabba20b9f4ec7d18bd6644579e5bf
GET /sitemap.xml    403   25 bytes   md5 9ccabba20b9f4ec7d18bd6644579e5bf   (twice)
body                "Your request was blocked."
```

**Taken at the root, because a 403 on a sitemap is not a closed board** — a
site can shut its sitemap to robots and serve its pages. Here the root is shut
too, so the scope of the refusal is the host.

**And the body is a vendor default, not this operator's words.** It is
identical, byte for byte, to `jobstore` and `hays` — two other countries, two
other operators. *`shared/robots-policy.md` now lists three.* The sitemap was
fetched twice first: the body does not change between reads, so the
fingerprint is comparable across hosts rather than carrying a per-request
element.

## What follows — the browser opens it, and that is measured

**2026-09-08. The refusal above is aimed at the client, not at everyone.**
Same host, same day: our declared HTTP client is refused twice at 04:45 UTC,
and a real browser is served the board between 04:48 and 04:54 UTC. **No
captcha, no challenge, no interstitial** — nothing to defeat, so the owner's
second bound is not engaged. *This is the measurement the previous version of
this card said it was not making.*

### The feed, and where its number comes from

The front page carries the whole live inventory behind one control.

```
GET /                          27 distinct /job/ URLs
click "Вчитај уште огласи…"   -> POST /APICalls.aspx/JobsLazy
                              282 distinct /job/ URLs, control gone
advertisement URL             /job/<22-char id>/<slug>
```

**One click exhausts it.** *The control does not reappear, so 282 is the end
of the feed and not a page of it.*

**282 is a count of advertisements and not of links, and the difference is
load-bearing.** Every one of the 282 carries a card marker — **260 `активен
до` (active until) + 22 `плата од` (salary from) = 282**, a clean partition.
*A `/job/` link on its own is not an advertisement:* the Bitola page below
holds 106 such links of which **96 carry no marker at all.**

### The second anchor confirms on the small city and cannot speak on the large

| | feed attributes | the city's own page says |
| :-- | --: | :-- |
| Битола / Bitola | 9 | **10 marked** (of 106 `/job/` links) |
| Скопје / Skopje | 228 | **exactly 200**, all marked, no load-more |

**Bitola agrees within one**, and the one is unexplained — most likely a card
my city pattern missed, not a missing advertisement.

**Skopje neither confirms nor contradicts: 200 is a round number and the feed
claims 228, which is more.** *A city page that stops at exactly 200 is a
rendering cap, and a cap cannot be read as a count* — the same shape as the
1 000-at-the-first-file trap this repository has already paid for.

### 282 IS NOT THE INVENTORY — the site declares ads the feed does not show

**Cards carry an employer grouping**, `+21 огласи` or `+ еден оглас`, so one
card can stand for several advertisements. *That makes 282 a count of cards
and a lower bound on advertisements, not the inventory.*

```
282 cards, of which 182 carry a grouping
 54 distinct employers carry one
968 = naive sum of the 138 digit groupings   <- WRONG, employers repeat
 44 groupings spelled "+ еден оглас"          <- a number written in WORDS
226 = the same, deduplicated by employer
```

**The naive sum is wrong in the way that looks right.** `+21 огласи` appears on
three separate cards because one employer holds three of the feed's slots;
adding them counts that employer three times. **And 44 of the groupings write
their number as a word**, so a digit pattern never sees them at all — *this
repository has paid for that one before, on six dead counters written
`cent quatre-vingt-quatre`.*

**The semantics ARE settled, and the earlier reading on this card was wrong.**
`+N огласи` means **N *other* advertisements**, so the employer's total is
**N+1**. *Measured across the 53 employers the feed names, each counted on its
own company page:* **40 of 53 satisfy `total = N+1` exactly**, one is equal to
`N`, and twelve differ — ten of them by two or three ads **above** `N+1`, which
is what a live board does between two reads, and two by falling to zero.

### CORRECTION — "41 live advertisements" was my own over-count

**The previous version of this card said one employer held 41. It holds 25.**

```
same bytes, 368 624 of them, one company page
   25   literal occurrences of `активен до`   <- correct
   41   my DOM walk over the same document    <- wrong
```

**The DOM walk took `closest('div,li,article')` as the card**, and that
ancestor can hold several cards, so a card with no status line inherited a
sibling's. *Two instruments on one document, and the disagreement was mine, not
the site's.* **The literal count is the one that survives**, and `25` against a
declared `+24` is what settled the semantics above.

**The conclusion the wrong number was used for still stands.** *That employer
shows **5** cards in the exhausted feed and holds **25**;* **the feed is a
selection either way**, and 25 versus 5 says it as well as 41 did.

### The floor, measured through a different door

**53 of the 54 employers named by the feed were counted on their own company
pages** — the 54th carries a Latin `È` that the transliteration did not match,
and it contributes nothing. **All 53 answered HTTP 200, and each page was
verified to name the employer it was fetched for.**

```
291   live advertisements across those 53 employers
100   feed cards carrying NO grouping — employers with a single advertisement
---
391   a floor that does not come from counting the feed's cards
```

**Distribution across the 53: median 3, minimum 0, maximum 25, three zeros.**
*Two employers declare a grouping and show none today, which a board that
expires advertisements will do.*

**This replaces `≥ 282` with `≥ 391`, and it is still a floor** — *the feed
names only employers it chose to show, so every employer it never showed
contributes zero to this sum and an unknown number to the board.*

### The archive is 17 604, and it answers a different question

`sitemap.xml` — **refused to our HTTP client, HTTP 200 and 8 447 801 bytes to
a browser** — holds 41 654 `<loc>`:

```
/job/     17 604      /article/  16 147      /company/  6 229
/tag/      1 116      /oglas/       300      /state-job/   37
```

**17 604 is the stock; the flux is at least 391, and neither is an estimate
of the other.** *Nothing on the page distinguishes them, and the larger number is the
one that gets quoted.*

### Two counts that were nearly published and are not

**`2026 JOBS` and `2026 Offres`** — the copyright year adjacent to the right
noun, produced twice in one morning by a `(\d[\d,]*)\s*(jobs|offres)`
pattern, on this board's neighbour and on `hays.fr`. *An integer, on the right
page, beside the right word.* **A number adjacent to the right noun is the
count of nothing.**

## 2026-09-12 — the browser route, re-measured from a connected tab (#222)

**11:54–11:56 UTC, Claude in Chrome connected, one tab.** The guard first,
on the exact paths — `/`, `/job/<id>/<slug>`, `/sitemap.xml`: all `allowed
True, certain True` (the groupless file above binds nobody). No challenge,
no interstitial: the page renders to the declared session as it did to a
real browser on the 8th.

```
navigate https://kariera.mk/                 27 distinct /job/ links · 20 «активен до» + 7 «плата од» = 27
click «Вчитај уште огласи...» (a.btn-primary, href="#", from the page's own script)
                                             -> POST /APICalls.aspx/JobsLazy, control gone
                                             **291 distinct /job/ ids** · cards: 268 «активен до» + 23 «плата од» + 0 both + 0 neither = 291   11:55:27 UTC
                                             (272 «активен до» on the whole page: 4 sit outside the cards, in the page's chrome)
                                             197 employer groupings «+N огласи / + еден оглас» on the cards
GET /job/IyWjJgaCAkqH0Ewhnz25SA/b2b-sales-representative   200, 74 121 B, title «ЕНЕРМАК ДООЕЛ Тетово: B2B Sales Representative»
                                             **no JSON-LD, no JobPosting** — the advertisement is markup only
```

**291 cards on the 12th against 282 on the 8th, by the same instrument
(distinct `/job/` ids after one exhausting click), and the partition by card
marker is clean on both days.** *The site still states no total: the feed's
end is the only anchor, and the 391 floor of the 8th (53 employer pages) was
not re-walked today.* The procedure a session follows — this is the adapter,
at the same title as a script (decision of 2026-09-08):

1. guard `kariera.mk` on `/` and on `/job/…` before anything;
2. `navigate https://kariera.mk/` in the session's own tab; wait for the
   feed (27 cards);
3. find the anchor whose text is «Вчитај уште огласи…» and call its
   `click()` from the page (a coordinate click on this page landed on the
   `/edu` link beside it — the button moves as the feed grows); wait ~5 s;
   the control disappears when the feed is exhausted;
4. collect the distinct `/job/<22-char id>/<slug>` addresses; on each card,
   read employer, city, and exactly one of «активен до <date>» / «плата од
   <amount>»; print **«n cards, k with a grouping — the site states no
   total»**, never a bare count;
5. an advertisement page is markup only: read it from the tab if the body is
   wanted; the ad URL is the card's own address, rebuilt from id and slug;
6. close the tab.

**Borne 0 held again**: the 25-byte 403 goes to the declared HTTP client and
to nobody else — the page, its lazy feed and its advertisement pages all
answered 200 to the session's tab, with nothing to defeat.

## What this card still does not claim

**No script ships, and `script: none` says so.** The route here is the
browser, which is what `job-scan` already drives; this card records the recipe
and the numbers, not a Python adapter.

**North Macedonia is no longer at zero *reachable* inventory** — at least
391 advertisements are readable today by the route this repository already
owns.

**And this card is nude at the list level, by its own admission.** *Every
number above comes from a reader of mine — the 391 as much as the 282, since
counting status markers on 53 company pages is still my counting: if my
extraction stopped working, the figure and 0 would be two outputs of one
instrument and nothing here would tell them apart.* **The site states no total
of its own that I could find** — no result counter, no declared pagination —
*and the employer groupings, which are the one figure the site does state, do
not have settled semantics.* **That is a named gap, not an oversight**, and it
is what #181 asks a card to say out loud.

*The ad pages carry no `JobPosting` markup at all — `ld+json` count 0 — so
there is no structured second reading available on this host either.*
*A second Macedonian board is named in the coverage queue and is still not
measured here.*
