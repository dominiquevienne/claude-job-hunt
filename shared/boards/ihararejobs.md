# Board adapter — iHarare Jobs (Zimbabwe)

<!-- verified: 2026-09-07 -->

<!-- hosts: ihararejobs.com -->
<!-- host-forms: ihararejobs.com -->
<!-- host-forms-basis: read — `ihararejobs.py:BASE`, a single literal; `ihararejobs.co.zw` appears as `sameAs` in the schema and is never fetched · 2026-09-07 -->
<!-- script: ihararejobs.py -->
<!-- countries: ZW -->
<!-- content: measured · 6 295 advertisements in one sitemap of 6 503 `<loc>`, all distinct, all carrying the board's id; the other 208 are category pages · 2026-09-07 -->
<!-- witness: none found — the site states no total; 6 503 is the file's own length and 6 295 is what remains once the category pages are named · 2026-09-07 -->

**Zimbabwe's only reachable board.** The country's rank-1 answers HTTP 500, so
without this there is nothing.

## Reading this board changes it — measured, not suspected

**`lastmod` is not a publication date. It moves when the page is fetched, and
our own requests moved it.**

```
read 1   18:08:41Z   6 295 advertisements
read 2   18:16:22Z   6 295 advertisements, 0 gained, 0 lost
              7 min 41 s apart, from the provenance records
lastmod changed          6
   of those, fetched by us      6
   of those, NOT fetched by us  0    out of 6 286 untouched
```

Nine pages were fetched between the two reads. **Six moved; the other three
were already stamped with the current date** and could not move within a field
of day granularity. **Nothing we did not touch moved at all.**

*The mechanism is an inference — a view counter writing a timestamp would do
this — but the observation needs none:* **a sweep of this board dates
everything it reads to the day of the sweep.**

That is why the file looked the way it did at read 1:

```
28 distinct dates, 2024-01-30 .. 2026-09-07
2026-09-07   3 811   60.5 %
2026-09-06   1 404   22.3 %
2026-09-05     652   10.4 %
```

**This repository already held «3 417 dates moving under identical URLs» for
this host and had not found the cause.** It is us, and whoever else reads it.

**So `--since` is refused on the sitemap** and offered only with `--fetch`,
where it filters the advertisement's own `datePosted`. A `--since` on
`lastmod` would return almost the whole board and call it this week's — *and
it would be our own crawl that made it look that way.* **An instrument that
alters what it measures does not become reliable by being run more often.**

## The rules file has no `User-agent:` line at all

Seven `Disallow:` directives and no group, so they bind no agent and the guard
answers `allowed: True` for every one of them — **issue #180**.

```
/login/  /static/  /register/  /candidate/  /employer_admin/  /admin/  /vacancy/apply/
```

**This adapter refuses all seven itself**, in `gate()`, before the guard is
consulted, and says why in the message. *The behaviour of `allowed()` is
defensible under RFC 9309; its stated reason — «no `Disallow` matches this
path in `*`» — is not, because there are seven and there is no `*`.*

The inventory is under `/job/` and `/sitemap.xml`, neither of which the file
names.

## The real dates are in the schema, in Django's format

```
"Sept. 7, 2026, 12:44 p.m."     "Oct. 9, 2024"       "April 29, 2024"
"June 5, 2024, 1:36 p.m."       "May 3, 2024"        "Aug. 14, 2024"
```

**Django's `N j, Y` — AP style.** Four months abbreviate to three letters and
a dot, five are spelled out in full, and **September is `Sept.`, which is
four.** `%b` parses none of the last six, and `value[:10]` yields `Sept. 7, 2`
— not a date, and not shaped like an error either.

The month table is explicit and **all twelve are exercised**, along with five
inputs that must return `None`. An ISO date is accepted as well: if this host
ever switches format, a parser that knows only the AP form returns `None` on
every advertisement — *a total, silent loss that looks exactly like a board
with no dates.*

## `strict=False` is load-bearing here, more than next door

**Six of eight sampled advertisements need the lax JSON pass** — the
descriptions carry raw control characters. A parser that tries once reads
three quarters of this board as having no structured data at all.
`angolaemprego.md` records the same trap at a far lower rate; the count is
reported in `lax_json` on every `--fetch` rather than being assumed stable.

## An unknown advertisement answers 200 with the listing page

Not 404, not 410: **50 kB, `<h1>Browse Jobs</h1>`, no `ld+json`.** A soft 404
is worse than a hard one in both directions — a sweep banks it as a live page
that merely lacks structured data, and a check asking *«did it 404?»* reports
the advertisement as still there.

`ad` exits 3 on it; `list --fetch` names it `gone` rather than `unreadable`.
**Mutated both ways**: the marker fires on an invented slug and does not fire
on a real advertisement.

## The employer is usually real and sometimes the site

`hiringOrganization.name` reads `iHarare Jobs`, with the board's own street
address, on **1 of 8 sampled**. The other seven name Old Mutual, the World
Food Programme, two universities and an embassy. The site's own name is
emitted as written with `employer_is_site: true`, never as `None`: *«the board
did not name an employer»* and *«we could not find one»* are different facts.

`addressLocality` is genuine — Harare, Bindura, Gweru — even where the street
address is the board's. **It is not always a city**: one advertisement carries
`Zimbabwe` there, so a count of cities taken from this field would be short by
whatever share does that. Not measured beyond the eight sampled.

## The file holds 208 category pages, and they carry every anomaly

```
6 503 <loc>  =  6 295 advertisements  +  208 /categories/ pages
```

**Counting the file would report the board 3.3 % larger.** And the 105
duplicated `<loc>` and the 104 entries without `lastmod` are **all**
categories: the advertisements have neither a duplicate nor a missing date.
*Blaming those anomalies on the advertisements is the reading that a whole-file
count invites.*

## What was exercised, 2026-09-07

```
list                              6 295 held, one request
list --limit 2                    advertisements 6 295 · returned 2
list --since … without --fetch    exit 2, and it says why
list --live  … without --fetch    exit 2
list --fetch --limit 3            3 read · 3 kept · 0 unreadable · 2 lax
list --fetch --limit 3 --since 2026-09-05   3 read · 2 kept · 1 dropped
ad  general-hand-x-2-posts-1498   1498 · 2024-04-29 -> 2024-05-03 · Gweru
ad  an invented slug              exit 3, soft 404 detected
gate /candidate/ · /vacancy/apply/          exit 7
gate /job/…                                 allowed
iso() on all twelve months        12/12; five malformed inputs -> None
```
