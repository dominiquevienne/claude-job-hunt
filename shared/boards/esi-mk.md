# Board measurement — ESI Employment Services International (`www.esi.mk`, North Macedonia): open, server-rendered, and its OWN counter says zero active advertisements — and it is Trenkwalder's Macedonian instance, not the public employment service

<!-- verified: 2026-10-21 -->

<!-- hosts: www.esi.mk -->
<!-- script: none -->
<!-- countries: MK -->
<!-- content: measured · **ZERO active advertisements, and the figure is the BOARD's own** — the listing `/mk/Ads` is server-rendered (200, 31 504 B, `h1` «Огласи за работа») and prints «0 активни огласи за работа пронајдени» in its served text. `bin/fetch-body.py https://www.esi.mk/` recorded `final_url: null`, so this host serves directly and no redirect is involved (`server: Microsoft-IIS/10.0`). The absence is a property of the OBJECT and not of the route: both `/` (200, 46 246 B) and `/mk/Ads` answer the declared client, the rules file is read and refuses nothing. 36 city facets — 35 municipalities plus «Странство», abroad — behind a `SearchAdvertisments()` search; advertisements are addressed by an `AdvertismentId` hidden field and applied to through `/Account/EasyApply`. No sitemap declared, and no `JobPosting`, no JSON-LD, no `__NEXT_DATA__`, no `data-page` and no `__doPostBack` on either page · 2026-10-21 -->
<!-- witness: the board's own «0 активни огласи за работа пронајдени», printed on `/mk/Ads` — a count that is NOT our extraction, which is the discriminant this repository requires of a zero. There is no second enumerator to cross it against: no sitemap is declared · 2026-10-21 -->

**Two requests, `bin/fetch-body.py` with the declared identity, 2026-10-21
18:25:16Z and 18:27:15Z.** Guard taken on the exact host in a turn distinct
from the retrieval: `allowed: True`, `state: read`, **`rule: None`**, and **no
`Crawl-delay`** — so the cadence is ours and a silent file does not say there is
no limit.

## It is a private staffing agency, and the page says so itself

**`www.esi.mk` is Trenkwalder Macedonia.** *Its own markup carries
`linkedin.com/company/trenkwalder-macedonia/`, and its prose dates the company
to May 2007 with its head office in Skopje, offering «посредување при
вработување и времени вработувања» — placement and temporary employment.*

> **CORRECTION OF CLASS, and it is the reason this sentence is in the card: a
> working note had this host down as the Macedonian *public employment
> service*. It is not.** *That service is the Agencija za vrabotuvanje. The
> distinction is not cosmetic — the owner's decision of 18.09.2026, extended to
> regional services on 06.10, grants an ACQUIRED validation for a **public
> employment service** whose host does not answer: it becomes a dated
> non-feasible plus a motivated `blocked` ticket, with nothing to validate host
> by host. **A private agency is outside that class**, so the same silence here
> would need §2 sexies the ordinary way — the owner seeing and validating it.*

*The host answers 200 today, so nothing turns on it this time. It would the day
it stops.*

## Zero is the finding, and the board is what says it

```
/           200   46 246 B   root, Cyrillic, readable (0 mojibake pairs)
/mk/Ads     200   31 504 B   h1 «Огласи за работа», 2 181 characters of visible text
                             «0 активни огласи за работа пронајдени»  <- the board's count
```

**An extraction finding zero and a market holding nothing look identical from
here, and the thing that separates them is a count the tool did not compute** —
here the page prints its own. *So this is the `bolsas-sanitarias-es` shape:
there is nothing to enumerate, every path answers, and nothing is refused in
writing.* **Nothing is declared closed** (§2 sexies): the city facets and the
search form are intact, and a board that holds no advertisement in October may
hold some in November.

**This card declares NO `route:` line, and that is the finding rather than an omission.**
*`bolsas-sanitarias-es.md` is the one other card of this species — every path answers,
nothing is refused, and there is nothing to enumerate — and it carries no `route:`
either. A `route: http · 0` would assert a route that carries something, and a route to
nothing is not a covered board; what is measured lives in `content:` and `witness:`,
the zero included.*

## Two things deliberately not carried

**The page publishes a contact block — two mailboxes, a telephone, a fax and a
street address.** *None is reproduced here and none went into any output: the
figures that matter to this card are the count and the facets.*

**`#349 Adaptateur : Trenkwalder Slovaquie` is CLOSED as COMPLETED — the
sibling adapter WAS DELIVERED, and `trenkwalder.py` ships beside
`shared/boards/trenkwalder-sk.md`.** *Read, because a closed match excuses
nothing on its own: the reason decides, delivered or set aside.*

**And the «does the sibling-country adapter transpose?» question answers NO
here, measured — the OPPOSITE of the answer `jobartis-ga.md` got in the same
turn.**

| | stack | enumerator | listing |
| :-- | :-- | :-- | :-- |
| `.sk` (#349) | Next.js | `/sitemap-jobs`, 32 rows | `__NEXT_DATA__` carrying an Algolia state, `nbHits` 32 |
| `.mk` (here) | ASP.NET MVC, `Microsoft-IIS/10.0` | **none declared** | server-rendered, no JSON of any kind |

**So the shape is NOT shared: this is the `randstad` case, a rewrite — while
Jobartis Gabon, measured the same evening, is the `hays-fr` case, a
parameter.** *Two instances of one question, opposite answers, one day — which
is the denominator that makes the discriminant a rule and not an anecdote, and
the discriminant is again whether the URL SHAPE is shared and never whether the
BRAND is. Both brands are shared.*

**One finding travels from the sibling anyway, and it is a safety one: `.sk`
publishes `recruiter {name, e-mail, telephone}` on EVERY record, and its
adapter never emits them.** *Different editor and a different stack here, so
this is a reason to LOOK before emitting and not a fact about this host — but
it is the first thing to look at the day this board carries advertisements
again.*

*No `adapter` issue is opened for this host today: there is nothing to extract
from zero, and a rewrite priced against an empty board prices nothing. A search
of all 634 issues returns zero for `esi.mk` and zero for `Macedonia`.*
