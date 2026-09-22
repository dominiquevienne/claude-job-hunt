# Board measurement — Karboom (`karboom.io`, «کاربوم», Iran): its own list (`/jobs?page=N`) — **393 adverts emitted against the 393 the page states on 2026-09-22**, twenty a page over twenty pages; `karboom.py` — the bare `/jobs` is the CATEGORY HUB and not page one, `employmentType` is the site's own row rather than a word, and the gender the board prints beside an advert is never carried (#183)

<!-- verified: 2026-09-22 -->

<!-- hosts: karboom.io -->
<!-- script: karboom.py -->
<!-- countries: IR -->
<!-- content: measured · **393 emitted, the page states 393: equal**; `/jobs` bare is the CATEGORY HUB (nine featured adverts, no count) and NOT page one — the walk asks `?page=` for every page, page one included; the site's `employmentType` is a row, not a word, and its `created_at` is stamped at request time. Read by the declared client, 2026-09-22 09:14–09:22 UTC, the guard on each exact path: the rules (`User-agent: *`, fourteen `Disallow`) refuse `/*?q=` and `/jobs/sokan_academy` by name and nothing else this walk asks; the root answers 200 at **103 597 B on both reads while its md5 moves** (`c58ffb47f9ae`, `467583f03e1c`) — the SIZE is the witness here, not the md5. The list states its own total in `span#search-result-count` («۳۹۳», Persian digits) and names what it counts in the `<h1>` beside it («آگهی استخدام»); its pager ends at page 20, and 20 × 20 = 400 ≥ 393. The key is the site's **hashid** (`wmjevl`), never the Persian slug — an ASCII fold of it is empty and an empty key collides. Exercised: `jobs --country-code IR` → **393 emitted over 20 pages — the site states 393: equal**, 393 distinct ids, zero e-mail and zero telephone pattern in the output; `ad --url …` → JobPosting read, «withheld: contacts, gender» · 2026-09-22 -->
<!-- witness: the page's own `span#search-result-count`, printed beside the emitted count on every run · 2026-09-22 -->
<!-- route: http · 393 · 2026-09-22 -->

**Found by the Iran search of #600 (a country never searched), issue #629;
measured 2026-09-22 09:14–09:22 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py` for the survey and `karboom.py` for the
walk.** Two reads of every page that carries a number.

## What the host says, and what it refuses

```
GET https://karboom.io/robots.txt    200 — User-agent: *, fourteen Disallow lines
GET https://karboom.io/             200 ×2 — 103 597 B both times, md5 c58ffb47f9ae then 467583f03e1c
GET https://karboom.io/jobs         200 — 137 062 B, the CATEGORY HUB: 72 tiles, 9 featured adverts, NO count
GET https://karboom.io/jobs?page=1  200 — 275 462 B, the LIST: 20 adverts and «۳۹۳ آگهی استخدام»
GET https://karboom.io/jobs/<hashid>/<slug>   200 — 63 518 B, a JobPosting
```

`_robots.allowed('karboom.io', '/jobs')` → **open, `certain: True`**, group
`*`, no directive matching. The two refusals that bear on a job walk are
`Disallow: /*?q=` — a query string carrying `q=`, which the pager's `?page=N`
is not — and **`Disallow: /jobs/sokan_academy`, one facet refused by name**.
Neither is ever asked. The back office, the candidate's own area and the
assessments are refused too and are none of our business.

## The three things this board does that the neighbouring one does not

**1. `/jobs` is not page one.** The bare path is a hub — seventy-two category
tiles, the city tiles, nine featured adverts, and no `#search-result-count`
anywhere on it. The list is `?page=N`. *`jobinja.ir` (#627), measured the same
week, has the opposite convention: there the bare `/jobs` IS page one.* A walk
that carries the habit over reads the hub, emits **nine**, and says nothing is
wrong — so the adapter asks `?page=` for every page and **refuses a list page
that states no count**, in the walk and in `--from` alike.

**2. `employmentType` is the site's own row, HTML-escaped.** The JobPosting
carries `{"id":118711,"job_id":48484,"cooperation_type":"FULL_TIME",
"created_at":…}` in that field. Emitted whole it publishes the board's
internal identifiers; and **its `created_at` is stamped at the moment of the
request** — it read `2026-09-22T09:15:10` on a fetch made at 09:15:10, for an
advert posted the day before. The field is parsed, `cooperation_type` is kept,
the ids and that stamp are dropped. *A value that changes between two reads is
not a measurement* — and it is the same class of moving element that makes the
root's md5 useless while its size holds.

**3. The gender is printed, and is not carried.** The advert shows
«جنسیت / زن» (gender: woman) among its labelled fields. The repository serves
the advert and does **not** propagate the criterion (#183, as `jobinja.py`
does with the same field and `jobcentrebrunei.py` with an age range): it is
never emitted, and every row SAYS what was left behind —
`criteria_withheld: ["gender"]` — so that a silence is not read as an absence.

## What the walk emitted

| | |
| :-- | --: |
| pages read (`?page=1` … `?page=20`) | 20 |
| adverts emitted | **393** |
| the page's own stated count | **393** |
| distinct ids among the emitted | 393 |
| e-mail addresses in the output | 0 |
| telephone patterns in the output | 0 |

**393 emitted — the site states 393: equal.** The count printed beside our own
does not come from our extraction: it is the page's `span#search-result-count`,
which is what makes a zero from a broken read distinguishable from a zero from
an empty board.

**One difference measured and left unexplained**, because two numbers with two
provenances are not one grandeur: the Tehran facet (`/jobs/tehran`, read
09:16:22 UTC) states **۲۴۵** in the same element, while the unfiltered walk
(09:21–09:22 UTC) emitted **244** rows whose city reads «تهران». The facet
count and the city label are two questions, and five minutes separate the two
reads. Nothing here says which — it is recorded, not resolved.

## The criterion is a fact of the BOARD, not of the row

**The gender is printed on the ADVERT page, and is not carried.** One card of twenty carried «جنسیت» on the list of 2026-09-22 — so **no list row declares a withheld criterion** (#885): a claim about the board does not belong in a field that reads as a claim about the advert. The advert's own record declares it, and only when the page carries it.

## What is emitted, and what is withheld

Emitted per advert, from the list: the site's hashid, the canonical address,
the title, the employer, the city, and the age as the board writes it
(«امروز», «دیروز», «۳ هفته قبل», «بیش از ۱ ماه قبل»). From the advert page:
the JobPosting's title, employer, locality, the contract read out of the row
above, the education and occupational category, `datePosted`, `validThrough`,
and the description.

Withheld: **e-mail addresses and telephone numbers in every text, Persian
digits included**; the employer's logo and every `/storage/` path; the
application route; the board's internal identifiers; **the gender criterion**.
Every record carries `contacts_withheld: true`.

## What the survey of 2026-09-17 said, and what this measurement adds

The card this one replaces was a survey: the root read twice at **103 597 B,
`md5 9d17eecb15b5` / `71d761af3419`**, rules open, «no count stated», nothing
past the root read. The host had been named by two independent lists — a
technology magazine's ranking and a training centre's list, both found by the
search written on #600 — and by a search engine's own answer for «سایت
کاریابی استخدام ایران».

Two of its statements are now more precise, and neither was wrong:

- **«no count stated»** was true of the ROOT, and the root still states none.
  The count lives on `/jobs?page=N`, which the survey did not read and said it
  did not read.
- **the md5 pair.** Five days and four reads apart — `9d17eecb15b5`,
  `71d761af3419` (2026-09-17), `c58ffb47f9ae`, `467583f03e1c` (2026-09-22) —
  the root has answered **103 597 bytes every single time and never the same
  fingerprint twice**. The element rendered at request time is not a passing
  accident, and on this host an md5 comparison would find a change every time
  it looked.

## Invocation

```
karboom.py jobs --all        # the whole list against its own stated count
karboom.py jobs --pages 3    # a BOUNDED read, and the output says so
karboom.py ad --url https://karboom.io/jobs/<hashid>/<slug>
```
