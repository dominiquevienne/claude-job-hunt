# Board measurement — Melli Kar (`mellikar.com`, «ملی کار», Iran): an ASP.NET WebForms board walked by POSTBACK — **270 adverts emitted from one category on 2026-09-23 against the 592 it states**, eighteen a round; `mellikar.py` — **the list resets itself to its first slice**, so a round with nothing new is not the end, and the rule that separates the three cases is the page's own row count

<!-- verified: 2026-09-23 -->

<!-- hosts: mellikar.com -->
<!-- script: mellikar.py -->
<!-- countries: IR -->
<!-- content: measured · **the list RESETS itself to its first slice — twice in eight rounds measured — so «a round with nothing new» is NOT the end**; a stop on that rule emits 18 of the 5 365 the category states, with exit 0 and no error; the discriminator is the PAGE'S OWN ROW COUNT, which grows each round, falls back to 18 on a reset and stops growing only at the end. Read by the declared client, 2026-09-23 15:3x–15:5x UTC, the guard on each exact path: the rules refuse nothing matching (open, `certain: True`, no `Crawl-delay`); `/jobs` answers **404** — there is no unfiltered list — and the routes are `/jobs/category/<slug>` and `/jobs/city/<slug>`. A category page carries **18 adverts rendered SERVER-side** in a `Repeater` (`HideAgahiID`, `lblName2`), addressed by `__doPostBack` and **not by `<a href>`** — a probe that counts links reads six facets and concludes «no list», which is what mine did on 2026-09-22. The postback carries `__VIEWSTATE`, `__VIEWSTATEGENERATOR`, `__EVENTVALIDATION` **and nothing else: echoing the whole form answers 500**. The page ACCUMULATES (111 KB → 424 KB in four rounds, `__VIEWSTATE` 9 → 38 KB), so a full category walk is **quadratic in bytes** — ~298 rounds, a 21 MB last response, over a gigabyte for one category of eight — and `--rounds` is the default. The witness is the HOME page: eight per-category counts («۵۳۶۵ موقعیت باز») that MOVED between 09-17, 09-22 and 09-23 (5316→5358→5365), so they are computed; the front's «بیش از 70000 شغل» is «MORE THAN 70 000», a claim. `lblEnteshar` means «publication» and holds the CONTRACT. The salary is behind a login and is DECLARED. Exercised: `jobs --category sewing --rounds 14` → **270 emitted, the site states 592** · 2026-09-23 -->
<!-- witness: the home page's per-category counts, printed beside the emitted count; they move between reads, so they are computed and not written in · 2026-09-23 -->
<!-- route: http · 270 · 2026-09-23 -->

**Found by the Iran search of #600, issue #631; measured 2026-09-22 and
2026-09-23 by the declared client, the guard on the exact path first.**

## The reset, and why it has no symptom

```
GET     18 cumul
POST1 page=  18 nouv=  0 cumul=  18 vs=9368o   <-- nothing new
POST2 page=  36 nouv= 18 cumul=  36 vs=14080o
POST3..7  +18 each round                cumul= 126 vs=37996o
POST8 page=  18 nouv=  0 cumul= 126 vs=9368o   <-- nothing new
```

A barren round returns **the first eighteen again with a `__VIEWSTATE` back at
its starting size**: the server has dropped the accumulation. **Every other
adapter in this repository stops when a round brings nothing new** — here that
rule emits **18 of 5 365**, with exit 0, no error and nothing to re-read.

## «Nothing new» is ambiguous in THREE ways, and only one is the end

Measured on «sewing» the same day: the list reset at round 7, **and rounds 8
and 9 also brought nothing new** — not because it was over, but because the
server was **climbing back** through rows already seen (18, then 36, then 54…).
A first version of this adapter treated three barren rounds as the end and
stopped at 126; it was wrong for the same reason, one level down.

| what a barren round can mean | what the page's row count does |
| :-- | :-- |
| the list RESET | falls back to 18 |
| the server is CLIMBING BACK after a reset | grows, 36 → 54 → 72 |
| the list is over | stops growing |

> **So the walk is driven by the page's OWN row count, not by novelty.** It
> continues while the page grows, names a reset when the count falls back, and
> stops after two rounds without growth. With the rule fixed the same category
> yielded **270 over 14 rounds** instead of 126.

## What the walk costs, and why it is bounded by default

The page returns everything read so far. 111 KB at the GET, 424 KB at the
fourth round; the `__VIEWSTATE` grows from 9 to 38 KB. One category of 5 365
would need ~298 rounds whose last response is ~21 MB — **over a gigabyte for
one category of eight**. `--rounds 3` is the default and the output says it is
a bounded read.

## The counts: one is a claim, eight are measurements

The front says «امروز **بیش از** 70000 شغل» — **«MORE THAN 70 000»**, and the
site says so in its own word: an advertising claim. The eight per-category
figures are counts, and they **moved on every reading**:

| | 2026-09-17 | 2026-09-22 | 2026-09-23 |
| :-- | --: | --: | --: |
| کارگر (manual-worker) | 5 316 | 5 358 | **5 365** |
| فروش و بازاریابی | 3 822 | 3 858 | **3 872** |
| کارمند اداری | 1 875 | 1 881 | **1 882** |

*A claim and a count look alike in a page; what separates them is that a count
moves.*

## Two smaller traps

**A field name that lies.** `lblEnteshar` means «publication» and carries the
CONTRACT («تمام وقت» — full time). It is read for what it holds.

**The salary is behind a login** — «برای مشاهده حقوق وارد شوید» («log in to see
the salary»). It is DECLARED (`salary_behind_login: true`) rather than left
absent: *a field a site hides is not a field the site does not have.* No
account is created.

## What is emitted, and what is withheld

Emitted: the site's advert id, the category walked, the title (the tile
appends the job family, which is removed and emitted separately), the city,
the contract as written, and whether the salary is behind a login.

Withheld: e-mail addresses and telephone numbers in every text — **the home
page carries the operator's own street address and two telephone numbers**,
never emitted; the employer's logo; the application route. An advert has **no
address of its own** on this board: the rows open by `__doPostBack`, so
`mellikar.py ad` refuses with that reason rather than inventing a URL.

## What the survey of 2026-09-17 said, and the correction of 2026-09-22

The first card read the root twice (55 721 B, `md5 a9a0dadc07f2` /
`0730a6f22c46`) and said «no count stated, the list and the ad not read» —
true of the root, which still states none.

**On 2026-09-22 I then wrote, here, that a category page is «a search form,
not a list» with «zero advert links».** The second half is true; the first is
false, and it is corrected on #631: the eighteen adverts were there, addressed
by postback. *«Zero links» is not «zero content»* — the repository already had
that lesson from an Inertia.js page carrying its rows in `data-page`, and the
faulty control is the same: counting links in markup that does not use them.

## Invocation

```
mellikar.py categories                                   # the eight, with their counts
mellikar.py jobs --category sewing --rounds 14           # a BOUNDED read, and it says so
mellikar.py jobs --category sewing --all                 # expensive: see the cost above
```
