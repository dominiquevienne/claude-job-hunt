# Assessed, no adapter — MELR (Ghana, Ministry of Labour, Jobs and Employment)

<!-- verified: 2026-09-03 -->
<!-- hosts: melr.gov.gh -->

**There is nothing to read here, and the reason is stronger than "not a job
board": the site serves one page under every URL.**

`robots.txt` is a 404 on both `melr.gov.gh` and `www.melr.gov.gh` — **absent,
which is not a refusal**, so nothing stopped the assessment.

## Every path answers 200 with the home page

The site's own menu links are relative — `6/7/job-seekers`, `2/1/brief-history`
— and resolve to 404 as written. Prefixing `index.php` makes them answer:

```
/index.php/6/7/job-seekers                200   71 966 bytes
/index.php/2/1/brief-history              200   71 968 bytes
/index.php/99/99/complete-nonsense-xyzzy  200   71 980 bytes
/index.php                                200   71 950 bytes
```

**Compared line by line against the home page, `/index.php/6/7/job-seekers`
has zero unique lines.** 184 lines, all identical. The few bytes of difference
are a token, not content. **A path that does not exist answers exactly like one
that does**, so the router is not reading the path at all.

## Why this is worth a card rather than a shrug

**An adapter written here would have looked like it worked.** HTTP 200, a
72 kB page, hundreds of links, no error anywhere. It would have parsed the
home page's navigation as job data on every run, for every query, and reported
a steady count — the shape `shared/never-fail-silently.md` exists for, and the
same one `employtt.md` records in a different form: *a status code that
describes the server's routing rather than the answer to the question asked.*

The check that settles it is not the status and not the size. **It is whether
two different requests produce two different bodies** — and here they do not.

## What was actually found

A ministry information site: news, publications, a "Job Seekers" menu entry
that is a content page rather than a listing, and no vacancy index of any
kind. **No advertisements were located**, so there is no fill rate, no total,
and nothing counted.

The page also carries mojibake in its own stored content — `GHANAâ€™S` for
*GHANA'S* — while correctly declaring `charset=UTF-8`. **That is
double-encoded at the source, not a decoding fault**: `_decode.py` reads the
declaration and gets it right. Recorded so nobody re-opens it as an encoding
bug.
