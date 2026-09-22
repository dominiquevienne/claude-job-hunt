# Board measurement — Wazefni Syria (`www.wazefnisy.com/jobs/`, Syria): «وظفني سوريا — منصة الوظائف وفرص العمل في سوريا» — **888 adverts emitted against the 888 its own API sent, in one request**, 23 categories, 14 governorates, filed between 2025-07-15 and 2026-09-22; `wazefnisy.py` — Syria's first adapter, and the contacts (622 numbers, 476 inboxes) are dropped and named

<!-- verified: 2026-09-22 -->

<!-- hosts: www.wazefnisy.com -->
<!-- script: wazefnisy.py -->
<!-- countries: SY -->
<!-- content: measured · **888 emitted against the 888 the API sent**, in ONE request. The page `/jobs/` (200, 95 446 B, md5 76df6e248848 twice) carries no advert at all — its `script.js` asks `/jobs/api.php?action=get_jobs`, which returns the whole board as JSON (200 ×2, **1 671 442 B, md5 717704ff3382 both**, `success: true`, 888 adverts, **888 distinct ids**), filtering and paging being done in the browser. The Arabic labels of the 23 categories, 15 cities and 5 types are read from the site's own script, and **every token the adverts use is named by it**. Contacts never emitted and named advert by advert: 622 phone numbers (the field carries something on 734, but on 112 it is a stub — «0» on 92, «963» on 14), 476 application e-mails, 9 links that open a conversation or are not addresses; 106 of the 115 filed links emitted as `apply_url`. Free text scrubbed at a threshold of 9 digits: of 180 digit runs **158 withheld, 22 left**, every one of the 22 read. `is_premium` and `is_urgent` false on 888 of 888 — counted, carried only when set. Exercised 2026-09-22: `jobs --country-code SY` → **888 emitted, the API sent 888** · 2026-09-22 -->
<!-- witness: the length of the array the API itself returns, printed beside the emitted count on every run · 2026-09-22 -->
<!-- route: http · 888 · 2026-09-22 -->

**Found by the Syria search of #608 (a country never searched), measured
2026-09-17 13:46–13:47 UTC, adapter written and the board read
2026-09-22 13:09–13:11 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads of each path.** *Syria had no route at
all before this one: #649 (Syria Jobs Network) is `blocked` — its own API
answers HTTP 500 — and `tanqeeb.md` records HTTP 202 with an empty body since
2026-09-05.*

```
robots.txt                                          HTTP 404 → no file, so no rules: open, certain
_robots.allowed('www.wazefnisy.com', '/jobs/')      open, certain, no Crawl-delay
GET https://www.wazefnisy.com/jobs/                 200 ×2, 95 446 B, md5 76df6e248848 — no advert, filters and a «load more» button
GET https://www.wazefnisy.com/jobs/script.js        200, 104 669 chars — API_URL, and the three label lists
GET https://www.wazefnisy.com/jobs/api.php?action=get_jobs
                                                    200 ×2, 1 671 442 B, md5 717704ff3382 — success: true, 888 adverts
GET https://www.wazefnisy.com/jobs/job_details.php?id=1047
                                                    200, 38 229 B — og:url is the id form; the adapter emits it and never reads it
```

## The adapter

```
wazefnisy.py jobs [--city ID] [--category ID] [--type ID] [--since YYYY-MM-DD] [--country-code SY]
wazefnisy.py labels
```

**Two requests for the whole board**, and no pager: the site fetches every
advert at once and filters in the browser. *So the array's own length is the
witness* — the run prints it beside what it emitted, and says `N short` if a
record went missing for a reason it cannot name.

**What is read, and from where.** The API speaks in tokens
(`sales_marketing`, `rif_dimashq`, `remote`); the Arabic names live in the
site's own `script.js`. The run reads them **there** rather than copying them
here: a token the site does not name is emitted raw and counted, and a list
that cannot be parsed says `labels_read: false` instead of dying. *A label is a
decoration; the token is the datum.*

**What never reaches a record.** Phone, application e-mail, and any link that
opens a conversation with a person (`wa.me`, `t.me`). A form does not —
`forms.gle` 76, `tally.so` 9, `docs.google.com` 4 — so those are emitted as
`apply_url`; and an address that is not an address (`http://www. homs`,
`hodnk:iskr/isvwk/fe.com`, both typed by employers) is dropped too, because a
link nobody can follow is worse than saying there was one.

**And `withheld_fields` names what was THERE, not what the field was called.**
`phone` carries something on 734 adverts and a number on **622**: on 112 it
holds «0» (92) or the country code «963» (14). Claiming to have withheld a
number nobody filed is a false statement about our own discretion — quieter
than a leak, and just as wrong. *Six digits is the floor; Syrian numbers are
ten.*

**And the floor is a property of THIS field on THIS board, stated so that it
does not travel.** It was chosen against what was measured here — 92 «0» and
14 «963» against 622 numbers of nine or ten digits — and it is read only on
`wazefnisy`'s own `phone`. *What it would cost elsewhere is not known and is
not guessed*: a jurisdiction whose subscriber numbers are five digits would
need a lower one, and a board that files short codes would need the question
asked again. Seven- and eight-digit numbers pass it; **nothing below six was
seen on this board, and that is a reading of 888 adverts on one day, not a rule
about telephones.**

**The scrub's threshold is nine digits, and it is declared.** Of 180 digit runs
in the free text, 158 are withheld and 22 left as the employer wrote them —
five of those carry seven or eight digits (`1.725.000` twice, `300 - 1000`,
`1.800.000`, `1.925.000`), and **the run prints that five** rather than hiding
what the threshold costs. Arabic-Indic digits are covered by the same rule:
`٢٠ - ٥٠` is among the 22 read, and a ten-digit Arabic-Indic number is
withheld like any other.

**Two fields the board sells and nobody bought.** `is_premium` and `is_urgent`
were false on **888 of 888**. A value true of nothing separates no more than a
value true of everything: the record carries the flag only when it is set, and
the run prints the count. *The badges are priced on the page, so the day one is
sold the record will say so.*

`--city`, `--category` and `--type` filter on the site's own ids after the one
request; **an id the site does not know is refused with the list of the ones it
does** — a filter that fails toward everything is indistinguishable from a
successful one. `--country-code` STAMPS: the board names Syria in its title and
its cities are the fourteen governorates, but the API carries no country field
and the record does not invent one.

**The advert page is never fetched.** `job_details.php?id=N` is the site's own
address — its `og:url` is exactly that form, without the title its script
appends — and the API already carries the description. `detail_read: false`.

## What the board holds, 2026-09-22

888 adverts, 888 distinct ids, filed 2025-07-15 → 2026-09-22. Damascus 449,
Aleppo 76, Rif Dimashq 57, Homs 55, Lattakia 51, Deir ez-Zor 50; remote 424,
full-time 338, part-time 82, shifts 44; sales and marketing 266, other 108,
translation 103, tech 96, engineering 70. Salary stated on 605 (SYP 487,
USD 399 across the corpus), monthly 488, weekly 206, daily 112, hourly 82.
