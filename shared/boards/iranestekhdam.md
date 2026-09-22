# Board measurement — Iran Estekhdam (`iranestekhdam.ir`, «ایران استخدام», Iran): its search list (`/search?page=N`) — **4 352 adverts emitted over 121 pages on 2026-09-22, and the list states NO count**, which is the finding and not a gap; `iranestekhdam.py` — the pager's arithmetic is printed as a BOUND, the key is the site's `data-id` and never the Persian slug, and a missing span in the MIDDLE is not a missing span at the end

<!-- verified: 2026-09-22 -->

<!-- hosts: iranestekhdam.ir -->
<!-- script: iranestekhdam.py -->
<!-- countries: IR -->
<!-- content: measured · **4 352 emitted over 121 pages, and THE LIST STATES NO COUNT** — no total anywhere in 341 719 B; the figures it does print in Persian digits are per-EMPLOYER and one is CAPPED («۱۰۰+»), so reading one as the total would give a witness specific, plausible and false; the pager ends at page 121 → at most 4 356 (121 × 36), printed as a BOUND. Read by the declared client, 2026-09-22 13:06–13:21 UTC, the guard on each exact path: the rules are `User-agent: *` then `Disallow:` — an EMPTY directive that refuses nothing — plus ten `Sitemap:` lines; the root answers 200 at **139 786 B on both reads while its md5 moves** (`3cec496b3b40`, `949505638644`), and it measured 135 868 B on 2026-09-17 — the size grew, the fingerprint never repeats. The key is the card's `data-id` (`3118112`), never the Persian slug at the root path: an ASCII fold of it is empty and collides, and each card carries the SAME link twice (mobile and desktop), so a walk keyed on the address counts 28 where there are 36. **The three `span.detail` are NOT padded at the end**: the site omits the city rather than emitting it empty, so padding slid the contract into the city on 87 of 4 352 rows and left 107 without a contract — the employer is first, the contract-and-salary span is LAST, the city exists only when there are three. The advert page carries **no `JobPosting`** — its only ld+json is a `BreadcrumbList` — and the record says so rather than leaving the field blank. Exercised: `jobs --country-code IR` → **4 352 emitted, «the site states no count» said**, 4 352 distinct ids, 0 e-mail and 0 telephone pattern, 0 city carrying a contract · 2026-09-22 -->
<!-- witness: none — the list states no count; the pager's bound (121 × 36) is printed as a bound, never as a total · 2026-09-22 -->
<!-- route: http · 4352 · 2026-09-22 -->

**Found by the Iran search of #600 (a country never searched), issue #630;
measured 2026-09-22 13:06–13:21 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py` for the survey and `iranestekhdam.py`
for the walk.** Two reads of every page that carries a number.

## What the host says

```
GET /robots.txt                200 — `User-agent: *` then `Disallow:` (EMPTY) + ten Sitemap: lines
GET /                          200 ×2 — 139 786 B both, md5 3cec496b3b40 then 949505638644
GET /search                    200 — 341 719 B, 36 cards, pager to 121, NO total anywhere
GET /search?page=2             200 — 343 985 B, 36 cards
GET /search?page=121           200 — 310 325 B, 32 cards
GET /<persian-slug>            200 — 67 008 B, ld+json = BreadcrumbList only
```

`_robots.allowed('iranestekhdam.ir', '/search')` → **open, `certain: True`**,
group `*`, no directive matching, no `Crawl-delay`. **An empty `Disallow:`
refuses nothing** — it is the standard's way of saying «everything is allowed»,
and it is not the same object as an absent file.

## The finding: a list that states no count

Every other Iranian board measured this week prints its own total — Jobinja
«۱۶,۲۰۱ فرصت شغلی», IranTalent «۱۷۴۴ نتیجه», Karboom «۳۹۳ آگهی استخدام».
**Here there is none.** No `#search-result-count`, no `"total"`, no «N نتیجه»
in 341 719 bytes.

What the page DOES print in Persian digits are **per-employer** figures on its
company carousel — «۲ آگهی فعال», «۶ آگهی فعال» — and **one of them is capped:
«۱۰۰+ آگهی فعال»**. Reading any of them as the list's total would produce a
witness that is specific, plausible and false; `fa_int()` therefore refuses a
number carrying a `+` rather than reading it as 100.

> **So the adapter says «the site states no count», and prints the pager's
> arithmetic beside what it emitted, calling it a bound.**

| | |
| :-- | --: |
| pages read (`?page=1` … `?page=121`) | 121 |
| cards on page 1, page 2, page 121 | 36, 36, **32** |
| the pager's bound (121 × 36) | 4 356 |
| **adverts emitted** | **4 352** |
| distinct ids among them | 4 352 |
| e-mail addresses in the output | 0 |
| telephone patterns in the output | 0 |

**4 356 − 4 352 = 4**, which is exactly the last page's shortfall (32 instead
of 36). The bound and the walk agree, and they agree for a reason that can be
stated — which is not the same thing as the site having told us a total.

## Three things the markup does that cost a rewrite

**1. The key is the `data-id`, never the slug.** Each card is a
`li.search-post-item` carrying `data-id="3118112"` — the site's own advert
number. The address is a Persian title at the ROOT path, and an ASCII fold of
it is empty (50 097 of 56 095 folded to nothing on Jobvision the same week).
**And each card holds the same link twice**, once for the mobile layout and
once for the desktop: a walk keyed on the address counts 28 where there are 36.

**2. A missing span in the MIDDLE is not a missing span at the end.** The card
carries `<strong class="detail title">` then `span.detail` for the employer,
the city, and the contract-with-salary — but **the site omits the city rather
than emitting it empty**. Padding the list at the end, which is what the
neighbouring adapter does correctly for a site that emits empty spans, slid
the contract into the city: **87 of 4 352 rows carried «تمام وقت (حقوق
توافقی)» as their CITY and 107 carried no contract at all**, on the first full
walk. Found by the walk's own control, not by reading. The employer is first,
the pay span is LAST, and the city exists only when there are three.

**3. The contract and the salary share one span.** «تمام وقت (حقوق توافقی)» is
two fields: the contract, then the salary in parentheses, taken exactly as the
site writes it and never converted — «از ۳۰ میلیون به بالا», «حقوق توافقی».
A span without parentheses is a contract and **no** salary, not a salary of
nothing. On the full walk: 4 245 rows of 4 352 carry a written salary.

## The advert page carries no JobPosting

Its only `application/ld+json` is a `BreadcrumbList`. The title, the employer,
the city and the age are in the page's own markup, and the record carries
`structured_data: "none — the page's only ld+json is a BreadcrumbList"`:
**an absent JobPosting is not an absent advert**, and a field left blank would
have said the opposite.

## The criterion is a fact of the BOARD, not of the row

**The gender is printed in the NOTICE, and is not carried.** ZERO of thirty-six cards carried «جنسیت» on 2026-09-22 while 4 352 of 4 352 rows declared one — the worst instance of the defect #885 names. **No list row declares a withheld criterion**; the advert's own record declares it, and only when the page carries it.

## What is emitted, and what is withheld

Emitted: the site's `data-id`, the address, the title, the employer, the city
when the card has one, the contract and the salary as written, the age as the
site writes it («۲۲ دقیقه پیش», «۱ ساعت پیش») and the badge when there is one
(«فوری» — urgent; 289 of 4 352).

Withheld: **e-mail addresses and telephone numbers in every text, Persian
digits included**; the employer's logo; the application route; **the gender
criterion** the notices print (#183 — the advert is served, the criterion is
not). Every record carries `contacts_withheld: true`.

## What the survey of 2026-09-17 said

The card this one replaces read the root twice at **135 868 B, `md5
d06fb1d98b65` / `7965075252c8`**, found the rules open and «no count stated»,
and read nothing past the root — saying so. Both statements hold: the ROOT
still states no count, and now neither does the list. **And the root has
answered four times over five days at two different sizes and four different
fingerprints** — the size grew by 3 918 bytes between the 17th and the 22nd,
which is a fact about the page and not yet one about the market.

## Invocation

```
iranestekhdam.py jobs --all        # the whole list; «N emitted — the site states no count»
iranestekhdam.py jobs --pages 3    # a BOUNDED read, and the output says which bound
iranestekhdam.py ad --url https://iranestekhdam.ir/<persian-slug>
```
