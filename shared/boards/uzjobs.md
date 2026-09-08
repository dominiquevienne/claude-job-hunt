# Board adapter — UzJobs (Uzbekistan): the «gibberish» decodes

<!-- verified: 2026-09-08 -->

<!-- hosts: uzjobs.uz -->
<!-- host-forms: uzjobs.uz -->
<!-- host-forms-basis: read — `uzjobs.py:BASE`, a single literal; `www.uzjobs.uz` serves the same rules and is never fetched · 2026-09-08 -->
<!-- script: uzjobs.py -->
<!-- countries: UZ -->
<!-- content: measured · 21 advertisements from one request to `/rss_vak.cgi`, each carrying employer, region, salary and both ends of its posting period; **this is the feed's window and not the board**, whose vacancy list paginates through an unexercised form and whose identifiers run to 33951 · 2026-09-08 -->
<!-- witness: none — the site publishes no total, and 21 is the length of a feed rather than a count of anything · 2026-09-08 -->

**Uzbekistan's first adapter, and Central Asia's.** The country page recorded
six of its eight hosts as dead, silent or unreadable; this was the one that
answered, and it was recorded as answering *«200 et du charabia»*.

## The gibberish decodes, and the reason matters

Recorded 2026-09-04: a redirect chain declaring `iso-8859-1`, then nothing,
then `windows-1251`, **and no charset in the HTML**.

Measured 2026-09-08:

```
GET /          200 · no redirect · Content-Type: text/html; charset=windows-1251
charset_of()   'windows-1251', from the header
decode_body()  windows-1251  ->  clean XHTML, <title>UzJobs …</title>
```

**There is no chain today: the requested URL is the final URL, and the single
declaration is right.** *Whether the site changed or the earlier reading
followed a hop that no longer happens, this card cannot say* — it reports what
one request returns now, and retires the earlier verdict rather than
contradicting it.

**Everything here is `windows-1251`** — the HTML and the feed, which declares
it in its XML prologue. *Nothing is decoded by hand;* `_decode.decode_body`
receives the headers and picks it up.

## One request returns the advertisements complete

`/rss_vak.cgi` is linked from the home page and the vacancy list, and its
`description` is a structured block rather than prose:

```
Компания: Index Consulting Company
Период размещения: 07.09.2026 - 06.10.2026
Регион: Ташкент
Предлагаемая зарплата: По результатам собеседования
```

**So employer, region, salary and both ends of the posting period come from
the feed — no advertisement page is opened by `list` at all.**

### 21 is the feed's window, not the board

The vacancy list shows ten per page with identifiers running to **33951**, and
its pagination goes through a form `POST`ing to `/vakansy.cgi` with `raz`,
`lan`, `search`, `keyword`, `go` and the selects `sfera1`, `sfera2`, `pol`,
`obraz`, `zanyat`, `region`.

**That form was not exercised.** *Those names are recorded so the next session
does not rediscover them, and so nobody reads 21 as a count of the board.*

## Two dates, both the site's own

`Период размещения` carries **both ends**, so `posted` and `expires` come from
the advertisement rather than from a file's timestamp. `pubDate` agrees with
the first on **21 of 21**, and disagreements are counted on every run.

**`pubDate` is parsed with `email.utils`, never sliced.** *An RFC-822 date
compared as a string sorts «Fri, 04 Sep» after «Wed, 02 Sep» — which is how a
first probe of this feed reported its range backwards.*

## This board publishes age and gender requirements, and this adapter does not

An advertisement carries `Возраст: 30-45 лет`, and the site's own search form
offers `pol` — gender — beside education and employment type.

**Neither is emitted, and no filter is offered on either** — #183, decided
2026-09-08. *Uzbekistan's Labour Code, new edition, law No. ZRU-798 of
2022-10-28 and in force since 2023-04-01, admits no employment restriction
founded on age or sex.*

> **The advertisement is still served.** *Dropping the ones that carry such a
> requirement would deny a candidate a real opening — the opposite of the
> point.* **It is the criterion that does not propagate, not the vacancy.**

**Measured before and after, same six identifiers**: `age_requirement` was
present on 3 of the 4 advertisements that answered (`30-45 лет`, `30-40 лет.`
twice); afterwards no emitted field matches `Возраст`, `Пол:`, `лет`, `мужчин`
or `женщин`, and **the same 4 advertisements are still emitted**. *The `list`
command never carried either field: 22 of 22 feed items clean, before and
after.*

**The Code reserves factors related to the exercise of the occupation**, so a
requirement *can* be lawful in narrow cases — and this adapter cannot decide,
advertisement by advertisement, whether a given one falls inside that reserve.
*Not propagating is the safe conduct under that uncertainty, and it is what the
repository's owner asked for.*

**This is per jurisdiction.** *The Uzbek Code says nothing about anywhere else;
this is not a template for other adapters.*

### A claim this card first made and could not support

**The first version said `Возраст` had to stay in the label set or the age
would be appended to `category`.** *Removing it from every label set and
re-reading four advertisements changed **zero fields**.* **The label is kept as
a precaution against a page order we have not seen — which is a weaker reason
than the one first given**, and it is written down because a card that
overstates its own mechanism is how the next reader is misled.

`tests/test_core.py::TheUzbekAdapterDoesNotCarryAgeOrSex` holds five
assertions, and each reddens under its own mutation: re-adding the emitted
field, re-adding the `PAGE_LABELS` key, dropping the label from the parser,
adding a `--age` option, and inserting a line that would skip such
advertisements.

## Three parsing defects, each found by exercising

**1. A value that swallowed every field after it.** The feed separates fields
with `<br><br>`; stripping tags removes exactly that boundary, so `employer`
came back as the company *plus* the period, the region and the salary — **a
value that is wrong and looks full rather than empty.** Fields are now cut at
the next known label, and the feed is read before its tags are stripped.

**2. A label with no colon.** `Информация о вакансии` is printed as a heading,
and a cut that required `:` left it glued to the employer's name. The cut now
tries both forms.

**3. The `<h1>` is `Вакансии (8)` on every page** — neither the job title nor
evidence the advertisement exists. *The title is the last non-empty line
before `Работодатель:`, taken from the page split into lines, because
collapsing the document to one string returns the navigation bar.*

**And the third defect hid a fourth**: `ad` tested the `<h1>` for emptiness to
detect a missing advertisement, so **an invented id returned exit 0**. This
host answers an unknown id with **HTTP 200** and a page carrying no
`Работодатель:` — that label is the discriminator, and `ad` now exits 3.

## What was exercised, 2026-09-08

```
list                        21 items · 0 date disagreements
list --since 2026-09-07     4 of 21
list --since 2027-01-01     0
ad --id 33951               title, employer, category, both dates, age
ad --id 99999999            exit 3, soft 404 detected
```

**Uzbekistan's other hosts, from the country page and not re-measured here:**
`mehnat.uz` moved into `gov.uz`; `ish.mehnat.uz` times out; `ishga.uz` has an
off-topic certificate and redirects to a *Coming Soon* template; `bandlik.uz`
has been reassigned to an application called *FITCITY*.
