# Board adapter — Kariera.mk (North Macedonia): refused to our client, open to a browser

<!-- verified: 2026-09-08 -->

<!-- hosts: kariera.mk -->
<!-- script: none -->
<!-- countries: MK -->
<!-- content: measured · 282 live advertisements on the front-page feed once exhausted (one click of `Вчитај уште огласи…`, 27 → 282 distinct `/job/` URLs, the control then disappears); every one of the 282 carries a card marker, 260 `активен до` + 22 `плата од` = 282; read in a browser because the HTTP route answers 403 · 2026-09-08 -->
<!-- witness: 282 live advertisements, and the archive is a different question — `sitemap.xml` holds 17 604 `/job/` URLs -->

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

### The archive is 17 604, and it answers a different question

`sitemap.xml` — **refused to our HTTP client, HTTP 200 and 8 447 801 bytes to
a browser** — holds 41 654 `<loc>`:

```
/job/     17 604      /article/  16 147      /company/  6 229
/tag/      1 116      /oglas/       300      /state-job/   37
```

**17 604 is the stock; 282 is the flux, and neither is an estimate of the
other.** *Nothing on the page distinguishes them, and the larger number is the
one that gets quoted.*

### Two counts that were nearly published and are not

**`2026 JOBS` and `2026 Offres`** — the copyright year adjacent to the right
noun, produced twice in one morning by a `(\d[\d,]*)\s*(jobs|offres)`
pattern, on this board's neighbour and on `hays.fr`. *An integer, on the right
page, beside the right word.* **A number adjacent to the right noun is the
count of nothing.**

## What this card still does not claim

**No script ships, and `script: none` says so.** The route here is the
browser, which is what `job-scan` already drives; this card records the recipe
and the numbers, not a Python adapter.

**North Macedonia is no longer at zero *reachable* inventory** — 282
advertisements are readable today by the route this repository already owns.
*A second Macedonian board is named in the coverage queue and is still not
measured here.*
