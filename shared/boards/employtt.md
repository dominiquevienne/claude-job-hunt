# Board adapter — EmployTT (Trinidad and Tobago)

<!-- verified: 2026-09-03 -->
<!-- hosts: employtt.gov.tt -->

The Ministry of Labour's national employment service. **No key, no cookie, no
browser, no endpoint** — every advertisement is in the served HTML of one page.

```
GET /jobs/list       → 21 advertisements, all of them, in the markup
GET /jobs/view/<id>  → one advertisement
```

`robots.txt` is **26 bytes** — `User-agent: *` and a bare `Disallow:` — which
closes nothing. (It also found a defect in this repository's own guard, which
counted the empty value as a refused path; fixed in v1.171.0.)

## A missing advertisement answers 200 with the listing page

Measured: `/jobs/view/2604`, `2606`, `2609`, `2617`, `2632`, `2500` and `2000`
all return **HTTP 200 with 175 396 bytes — byte for byte the listing.** No
redirect status, no 404, nothing in the body announcing a substitution.

**So the status code cannot be the check.** A real advertisement page carries
**zero** `/jobs/view/` links and its `<h1>` is the job title; the listing
carries one link per advertisement under `<h1>Jobs Listing</h1>`. `ad` tests
that and exits 3, because a card built from this body would carry **the first
advertisement's title under the id that was asked for**.

## Listing membership tracks neither expiry nor recency

| | |
|---|---|
| `/jobs/view/2603` | `Expires: 03 September 2026` — **listed** |
| `/jobs/view/2618` | `Expires: 04 September 2026` — **not listed** |

Read on 2026-09-03: the one expiring *today* is listed, the one expiring
*tomorrow* is not. And the listing carries the other half — **two of its
twenty-one expired on 02 September** (`2607`, `2615`) and were still served on
the third. Those two, and only those two, print no "expires *date*" sentence
on their card, which is the board's own mark for a deadline already past.

**Two expired advertisements in, one unexpired advertisement out.**

Scanning ids 2590-2640: **22 render an advertisement** — the listing's 21 plus
2618 — and the other 29 answer with the listing page. **There is no archive**:
ids below the live range are gone, not kept.

**Nothing visible from outside explains which of the twenty-two is listed**, so
`search` reports the listing's count and says it is the listing's. It does not
claim to be the board.

## Three things about the markup

**Read fields by their class, never by position.** The page names every one:
`title decode`, `employerfilter decode`, `locationfilter decode`,
`categoryfilter decode`, `employmentStatus`, `creationDateSort`,
`publishDateSort`, `deadlineDateSort`. The first draft of this adapter counted
text nodes and put **"Forgot your password?"** in the twenty-first
advertisement's category, because that block runs to the end of the document
and swallowed the login modal.

**Everything is escaped twice.** The stored field is HTML and the template
escapes it again, so the page literally contains `&lt;div&gt;` and `&#47;` —
a title came out `Driver&#47;Messenger`. The site's own class name for these
fields is `decode`. Unescaping runs **to a fixed point, not a fixed count**,
because a value legitimately containing `&amp;amp;` must not be over-decoded.

**The filter links are client-side.** `/jobs/list/category-cbx-1`,
`/jobs/list/city-cbx-PortofSpain` and
`/jobs/list/employmentStatus-cbx-fulltime` each returned **the same 21
advertisements**. Two readings fit that — the server sends everything and
jPList filters it, or the path segment is ignored — and **the counts alone
cannot separate them**, so this adapter neither paginates nor filters by URL.
One request is the sweep.

## Salary

**0 of 21 state a figure.** Every card carries the salary line and prints
`Concealed`, which is **the board's own word for a figure it was not given** —
not a missing field and not a parse failure. Counted on the value, never on
the key being present.
