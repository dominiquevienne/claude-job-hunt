# Board adapter — Seychelles YP jobs (`www.seychellesyp.com/jobs`, Seychelles): «Jobs in Seychelles», the jobs section of a Seychellois business directory served whole on the server — `/jobs/all` pages twenty cards, PRINTS ITS OWN TOTAL (33 on 2026-11-11) and ends of itself, each ad a labelled block with its employer, its dates and its presentation; `seychellesyp.py`

<!-- verified: 2026-11-11 -->

<!-- hosts: www.seychellesyp.com -->
<!-- script: seychellesyp.py -->
<!-- countries: SC -->
<!-- route: http · 33 · 2026-11-11 -->
<!-- content: measured · **rules read ENTIRE before any bundle (200, 575 B): `User-agent: *` with FOURTEEN `Disallow` and NO `Allow` — `/admin/`, `/autocomplete`, `/edit/*`, `/sign-in/*`, `/user/*`, `/userszone`, `/getnavprofile`, `/getlogin`, `/getnav`, `/getsearch`, `/redir/*`, `/gadgets/*`, `/comments/reply/*`, `*/get_table_results` — none of them matching `/jobs`, `/jobs/all`, its pager or `/job/<id>/<slug>`; NO `Host:` line and NO `Sitemap:` line, so no other canonical name and no enumerator on a third host; a SECOND group names Yandex, Baiduspider ×3, AhrefsBot, DuckDuckBot, aspiegelbot, sogouspider and GPTBot and gives it `Crawl-delay: 10`, which does not bind us. `allowed()` exercised BOTH ways in a turn distinct from the retrieval: `/jobs`, `/jobs/`, `/jobs/all`, `/jobs/all/2`, `/jobs/all/3`, `/jobs/all?page=2`, `/job/8124/Human_Resources_Officer`, `/job/8125/Driver`, `/sitemap.xml` open with no rule in the way — and `/admin/x`, `/user/42`, `/jobs/get_table_results` REFUSED, each naming its rule. `/jobs/all` (200, 24 777 B) 20 `<div class="company">` cards and `<div class="total"><strong>33</strong> results`, pager `/jobs/all/2` `rel="next"`; `/jobs/all/2` (200, 20 512 B) 13 cards and NO `rel="next"`: 20 + 13 = 33 = the printed total, the walk ends of itself. The ad `/job/<id>/<slug>` (200, 17 549–24 094 B) is a block of `<div class="label">` headings, measured on SEVEN ads spread over the thirty-three: `Announced`, `Job Status`, `Job Type`, `Expiration Date`, `Job Title`, `Work At`, `Job Presentation` on 7/7 and `Job Category` on 6/7 — dates `dd/mm/yyyy` with the site's own relative arithmetic in a `<small>`, no JSON-LD and no `JobPosting` anywhere, and `How to Apply` an outward link to the feeder's page (`https://jobo.sc/jobs/<slug>/`). `seychellesyp.py list` on the day: «33 emitted over 2 page(s) — board states 33, and the walk ended of itself: the two agree»** · 2026-11-11 -->
<!-- content: measured · **`/jobs` (200, 11 942 B, md5 33d2ab47736c identical on two reads) lists 8 «Latest Job Vacancies» as `/job/<id>/<slug>` with `/jobs/all` and `/jobs/all/city:Mahe`; here the cards are in the served markup (on `www.yemenyp.com` the same template served an empty shell); no count stated, no JobPosting; `_robots.allowed('www.seychellesyp.com', '/jobs')` → open, certain** · 2026-09-18 -->
<!-- witness: the board PRINTS its own total — `<div class="total"><strong>33</strong> results` on both list pages, a count this project did not produce, and the walk agreed with it exactly (33 emitted, 33 stated); the 2026-09-18 «no count stated» was measured on `/jobs`, which prints none, and is not a property of `/jobs/all` · 2026-11-11 -->
<!-- witness: none — no count stated; `/jobs/all` and its pager bound the list · 2026-09-18 -->

**Issue #716. Measured 2026-11-11 16:29–16:35 UTC by the declared client, the
guard on the exact path FIRST and in a turn distinct from the retrieval,
`bin/fetch-body.py`; the script exercised on the saved bodies and on the host.**
Assigned by the pilot; the premise was read on the object before the guard, and
the exclusion crossing taken on the `hosts:` line on both sides.

## What the board is

The jobs section of a Seychellois business directory — the same template as
`guyanaindex.md` and `yemenyp.md`, and **the template shipped no reader: there
was no `guyanaindex.py` and no `yemenyp.py`, so «one reader for three hosts» was
a possible gain and never a premise.** Thirty-three live vacancies on the day,
all of them posted by one feeder (`JOBO.sc`), the whole inventory on two pages.
Small, and exactly the kind of board the 08.09 rule says is used anyway.

## The rules, the transport

```
robots.txt                 200, 575 B — `*`: 14 Disallow, NO Allow, no Host:, no Sitemap:
                                        a second group: 9 named crawlers + Crawl-delay: 10
GET /jobs/all              200, 24 777 B, md5 e4f46ac61244   (16:29:35Z)   20 cards, total 33
GET /jobs                  200, 13 755 B, md5 e853cb127546   (16:29:36Z)   the landing list
GET /jobs/all/2            200, 20 512 B, md5 f3bfece1dc05   (16:30:44Z)   13 cards, no rel=next
GET /job/8124/Human_…      200, 17 549 B, md5 fd06ac3d91cc   (16:30:45Z)   the labelled block
```

`/admin/`, `/user/`, `/edit/`, `/sign-in/`, `/redir/`, `/gadgets/`,
`/comments/reply/`, `/getnav*`, `/getlogin`, `/getsearch`, `/autocomplete`,
`/userszone` and `*/get_table_results` are never sent (exit 7 before the gate):
the host's INTENTION is honoured and not its prefix match. **No `Crawl-delay`
binds us and that is not an absence of a rate limit: 3 s is OURS, above this
repository's usual 2 s because the operator writes 10 for every crawler he
names.**

## What the adapter emits, and withholds

`list [--max N]` (one request a page): id, url, title, `posted_by` (the feeder
named «JOB BY» on the card — **not the employer**), `posted_relative` as
written. **No description from the list: the card's own is TRUNCATED**, which is
why the ad page exists. The note prints the emitted against the total the board
states, and says which of the three cases it is — they agree, they differ by N,
or the route printed no total and the size is NOT ESTABLISHED.

`ad --url`: title, employer, `posted` and `expires` in ISO, `schedule`,
`engagement`, `category`, the presentation, `apply_url`. **The two labels are
placed by what they CARRY and never by what they say — this host's `Job Status`
holds «Full Time» and its `Job Type` holds «Employee» — and both were CONSTANT
on the seven ads measured, so neither discriminates anything on that sample.**

**Withheld, and the witness is DERIVED from what the redaction took.** `Work At`
holds the employer's name and, inside a `<small>`, its TELEPHONE on 7/7: the
name is emitted and the number leaves the record as `employer_phone`, so
`contacts_withheld` is true because something was actually taken. The
presentation is scrubbed of e-mail addresses and Seychellois numbers; **on the
seven measured it carried NEITHER, so `description_contacts_withheld` is False
there and the record claims no redaction nobody filed** (#1007). The feeder's
own address block — its logo, its street, its number — is never emitted, and
`How to Apply` is a page a candidate can open, not a way to reach a person, so
nothing is withheld for it.

Guards: a first list page of 200 without a card exits 6 (`_zero`, never read as
an empty board); an ad without its `Job Title` and `Work At` labels exits 6; a
path refused in writing exits 7; an address that is not an ad exits 2.

## Tests and mutations

Mutation bench on a DETACHED copy, `python3 -B`, each mutation asserted
different from the source, compiled, and asserted to CHANGE the judge's answer
on its own named field — **8 / 8 red**: the dedup across pages removed · the
`rel="next"` pager not followed · the `<small>` not stripped from the dates ·
the `<small>` not stripped from `Work At` (the telephone staying inside the
employer's name) · the presentation not scrubbed · the printed total not read ·
the witness ASSERTED instead of DERIVED (the #1007 lie) · the paths refused in
writing no longer refused.

**A ninth mutation came back GREEN and the bench's own control named it: a dedup
INSIDE `cards()` cannot fire.** The chunking gives one card per
`<div class="company">` and only the heading's link is read, so the forty raw
hrefs for twenty ads are settled there — the first draft's docstring claimed
that dedup was a condition of the count being right, and that was false for this
reader. **The dedup that CAN fire is across PAGES, in `merge`**: an ad posted
between the two requests shifts the window and pushes page 1's twentieth onto
page 2, which would file one vacancy twice and exceed the stated total with
nothing wrong at the board. Judged on the only input where it can fire — the
same page handed to `merge` twice — 20 against 40.

**Two defects were found by RUNNING the adapter and not by rereading it:** the
dates were ISO on one ad and `dd/mm/yyyy 8 days ago` on six, because the
`<small>` entered the cell's text and `DMY_RE` then matched nothing — *a date
field right on one record and wrong on six reads exactly like a date* — and the
refusal branch was unreachable from the command line, `/admin/x` being rejected
one line higher as «not a job address», so it was moved to one point of
application called before the shape test.
