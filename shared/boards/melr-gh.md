# Assessed, no adapter — MELR (Ghana, Ministry of Labour, Jobs and Employment)

<!-- verified: 2026-09-03 -->
<!-- hosts: melr.gov.gh -->
<!-- countries: GH -->
<!-- script: none -->
<!-- content: out-of-domain · a ministry site, not a board: 71 941 o of server-rendered HTML, zero `JobPosting`, and its single employment route `/6/7/job-seekers` answers HTTP 404 · 2026-09-07 -->
<!-- witness: none possible — there is no count to witness; the page names GLMIS as holding the vacancies and gives no address for it · 2026-09-07 -->

## Measured 2026-09-07 — it is not a board, and the board it points at has no address here

**`content:` was absent, which does not mean "measured at zero": it means
nobody had opened the body.** It has been opened.

```
GET /                        200 · 71 941 o · no redirect
                             « Ministry of Labour, Jobs & Employment »
                             121 <a href> · 2 <form> · 18 <script>
                             JobPosting 0 · ld+json 0
GET /robots.txt              404 — an ABSENCE, which is knowledge
GET /6/7/job-seekers         404 · 355 o        <- the one employment route
```

**The verdict was taken at the root and by fetching, not by guarding.** *A
`robots.txt` survives a domain's change of use and says nothing about what is
served today; here there is no rules file at all, and a 404 there is an
absence rather than a refusal.*

### The site names its own job board and never addresses it

Its visible text reads *"GLMIS offers a variety of jobs vacancies for people
seeking employment. Hundreds of jobs…"*, and the navigation entry **Job
Seekers** points at the path that answers 404.

```
mentions of `glmis` anywhere in the body : 1, and it is the bare word
external hosts linked from the homepage  : moys.gov.gh, presidency.gov.gh,
                                           nlcghana.com, yea.gov.gh, ndpc.gov.gh
                                           — no GLMIS among them
```

**So GLMIS is a lead and not a host.** *Composing `glmis.gov.gh` from the
acronym is exactly what this repository forbids: a hostname is read, never
built.* **Whoever follows this must find the address declared somewhere, not
derive it.** *Done on 2026-09-07: the host was obtained from a search
index carrying the pages' own titles, confirmed by fetching it, and it
is a board — `glmis.md`. **The provenance is written there because it is
weaker than usual**, and because `glmis.gov.gh` is exactly what the
acronym would have produced.*

**Three of the four job-shaped paths on this site are news articles and a PDF
about a national green-jobs strategy.** A path that contains the word *job* is
not a vacancy route.

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
