# Board measurement — Lambda (`lambda.global`, Mongolia): «Ажлын байр | Ламбда». The adverts live in the streamed React payload, and reading them needs a decode that, done wrong, **returns text instead of raising**. Three figures said «the sitemap is the enumerator»; membership says the two sets intersect in TWO. Adapter `lambdaglobal.py` (#661)

<!-- verified: 2026-09-29 -->

<!-- hosts: lambda.global, www.lambda.global -->
<!-- script: lambdaglobal.py -->
<!-- countries: MN -->
<!-- route: http -->
<!-- content: measured · **the rules file is served (`state: read`, `certain: True`), writes NO Crawl-delay (2 s are ours) and declares its sitemap on `lambda.global` — WITHOUT `www`, a host the guard had not seen; `/sitemap.xml` is an INDEX pointing at `/sitemap-0.xml` (200, 245 876 B — 1 412 `<loc>`, 1 403 with a `lastmod`, of which 50 under `/jobs`, 1 152 `/salary`, 77 `/ai`, 51 `/companies`); `/jobs` answers 200, 849 452 B, links 30 adverts, has no pager and states no count; the advert page (362 485 B) renders navigation only and its single `ld+json` is an `Organization` — the advert itself is a `JobPosting` inside the `self.__next_f` RSC payload, readable only after a `unicode_escape` AND a `latin-1` to `utf-8` round trip** · 2026-09-29 -->
<!-- witness: none established — the two enumerators (sitemap 50, listing 30) intersect in 2 and neither states a count, so the board's size is NOT established by this route; what the walk asserts instead is `emitted + unreachable + withdrawn + unread == named` over their union (78 distinct on 2026-09-29: 47 emitted, 31 withdrawn) · 2026-09-29 -->

**Measured 2026-09-29 by the declared client, the guard on the exact path and on
the DECLARED host; the adapter exercised against the host (a full walk of both
enumerators).** *Supersedes the 2026-09-17 measurement of #603, which read the
root only and recorded «no adapter yet».*

## A broken decode does not raise — it returns TEXT

The advert is not in the HTML. It is in the RSC payload, and getting it out needs
two steps:

```python
brut = "".join(re.findall(r'self\.__next_f\.push\(\[\d+,"(.*?)"\]\)', page, re.S))
dec  = brut.encode().decode("unicode_escape")     # suffit pour du latin
dec  = dec.encode("latin-1").decode("utf-8")      # INDISPENSABLE ici
```

**Without the second line the whole payload comes back as mojibake.** Every
search for an advert then fails, and the honest-looking conclusion is *«the HTTP
route does not carry the adverts»* — a board declared empty that is not. Nothing
contradicts it: **no exception, no error code, a payload read end to end.** This
adapter was one line away from filing that verdict.

**So the run checks LEGIBILITY before concluding any absence** — and by the
SIGNATURE OF THE FAILURE (a `[\u00c0-\u00df][\u0080-\u00bf]` pair, which is what
UTF-8 read as latin-1 leaves behind), never by looking for a known word.
*Requiring a word of the site's language assumes one reads that language, which
on Cyrillic is exactly what is not true.* On a non-Latin site, **a wrong decode
and absent content are indistinguishable without that check.**

And for the same reason the advert is found by STRUCTURE and never by a keyword:
the payload carries `salary`, `location`, `company` and `title` **as form labels
and placeholders**. *A fully localised interface dictionary contains every word of
the domain, so counting one measures the translation, not the content.*

## Three figures read as one enumerator; membership refuted it

```
sitemap /jobs        50     listing /jobs (linked)   30     stated count   none
intersection          2     linked & not in sitemap  28     sitemap & not linked   48
```

**50, 30, and no count stated anywhere reads as «the sitemap is the enumerator
and the listing is its first page».** It is not. The two sets intersect in **two**.

```
walking the sitemap alone    19 emitted   — and 28 live adverts lost
walking the union            47 emitted   (17 sitemap · 2 both · 28 listing)
```

Four of the 28 listing-only adverts were sampled and **all four carry a complete
`JobPosting`** (9 `@type` kinds each). *No total, no cardinal and no re-reading
distinguishes «same order of magnitude» from «same members».* **So the run walks
both enumerators, emits their union, names each record's enumerator in
`enumerated_by`, and states that the board's size is not established.**

## A withdrawn advert is a 200 with a legible payload and no structure at all

31 of the sitemap's 50 answer **200**, decode cleanly, and declare **no structured
object whatsoever** — where a live advert declares nine kinds (`JobPosting`,
`Organization`, `Place`, `MonetaryAmount`, `PostalAddress`, …). The listing
corroborates: **none of those 31 is linked from `/jobs`.**

**The run counts them apart from «the payload HAS structure but no JobPosting».**
The first is a fact about the board; the second would be a fact about our reading.
*Collapsing them would let a reader defect hide inside a board's staleness* — and
the second case says so in as many words when it fires.

## Fields, and the two rules this board re-exercised

- **`baseSalary.currency` is never carried** and the salary travels as the string
  the site prints — the rule measured on one vendor's two fronts (#638/#655);
- **the LABELLED salary escapes the telephone rule.** A Mongolian month runs to
  seven digits (`3000000 - 3500000`), so it has the *form* of a phone number —
  the defect that destroyed 113 Burmese salaries out of 115. Free text is still
  scrubbed;
- **`text()` removes the `<i>` ELEMENT, not only its tag** — an icon font puts its
  glyph *inside* the element (136 adapters of 138 still carry that defect);
- e-mail addresses and telephone numbers in free text are withheld;
  `contacts_withheld` on every record.

```
lambdaglobal.py jobs --country-code MN
  → 47 emitted, 31 withdrawn — every advert the enumerators name
  → sitemap names 50, the /jobs listing links 30, 2 in common, 78 distinct
```

`--enumerator {both,sitemap,listing}` walks one side alone; `--max N` caps the
walk. `--country-code` STAMPS — the board states no country.
