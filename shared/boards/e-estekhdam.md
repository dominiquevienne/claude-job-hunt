# Board measurement — E-Estekhdam (`www.e-estekhdam.com`, «ای استخدام», Iran): the aggregator's list behind a Nuxt shell; `eestekhdam.py` — **the delivered route is a walk PER PROVINCE** (127 adverts in 47 seconds, ended on its own), because **the pager CLAMPS instead of ending** at page 100 and because **the host cut the unfiltered walk on both attempts**; every count here is a LOWER BOUND, the board states no total anywhere

<!-- verified: 2026-09-24 -->

<!-- hosts: www.e-estekhdam.com, e-estekhdam.com, cdn.e-estekhdam.com -->
<!-- script: eestekhdam.py -->
<!-- countries: IR -->
<!-- content: measured · **`jobs --all` emitted 780 adverts over 40 pages of 20 before the transport cut it, and a second attempt reached 160 over 8** — the host does not sustain a hundred-request walk; the root is a Nuxt shell of 8 383 B titled «بارگذاری» and the list is `POST /search-api/search?page=N` (JSON filter body, `{}` = everything), the axios `baseURL` carried in `cdn.e-estekhdam.com/_nuxt/assets/index.V1k0iVya.js` — **and it answers 201, not 200**, so a status check written for `== 200` refuses every page. **THE PAGER CLAMPS INSTEAD OF ENDING**: pages 100, 500 and 5000 of the unfiltered query are identical TO THE BYTE (md5 973706fe9df1), twenty items, `ok: true`, no error — found by bisection between 50 and 500 (page 99 distinct, page 100 clamped) — while a narrow query ends properly with `data: {}`. **So both usual stop rules fail in silence**: «stop on an empty page» never stops on a broad query, «stop when nothing is new» stops at 2 000 and calls the cap the board. The walk stops on a page that REPEATS the previous one and says the query hit the cap. **`data` is a LIST when full and a DICT when empty**, so anything that indexes before checking dies on the page that means «done». **NO STATED COUNT EXISTS**: `meta` carries a URL and a title, `filter-options` returns 253 professions / 50 provinces / 29 sectors / 133 technologies without one count, `/sitemap.xml` is 404 — every count here is a lower bound and says so. Coverage past the cap goes through `--where`, which does NOT partition: a nationwide advert carries 31 provinces, so the dedup by `id` is mandatory. Rules read 2026-09-23: open, `certain: True`; the file names `ClaudeBot` with `Crawl-delay: 5` while `Claude-User` falls into `*` which imposes none — **the adapter paces at 5 s anyway** ; `*` refuses `sort=`/`posted=` and the facets `/jobs/*حقوق-از` and `/jobs/*-برای-`, which this route escapes by its path — **refused BY NAME in `--filter` all the same**. Exercised 2026-09-24: `jobs --where ایلام --all` → **127 over 7 pages, ended on its own** ; `jobs --all` → **780 over 40 pages, CUT by the transport** (SSL EOF), and again **160 over 8**, cut by two timeouts on page 9 · 2026-09-24 -->
<!-- witness: none — the board states no total anywhere (meta, filter-options and sitemap all carry none), so every count is declared a LOWER BOUND ; the only bound that exists is the page cap · 2026-09-24 -->
<!-- route: http · 780 · 2026-09-24 -->

**Found by the Iran search of #600 (a country never searched), issue #632;
measured 2026-09-17, 2026-09-23 and 2026-09-24 by the declared client, the
guard on each exact path first.**

## The shell says «loading» and the bundle says everything

```
GET  /                       200, 8 383 B — «بارگذاری - ای استخدام», no card, no count
     cdn…/_nuxt/assets/index.V1k0iVya.js   3,3 MB
       axios.create({ baseURL: "/search-api", headers: { "x-lang": "fa" } })
       search = (e, B) => client.post("/search", e, { params: B })
POST /search-api/search?page=N            201, twenty adverts, {ok, status, data, meta}
```

## The pager clamps instead of ending

```
no filter               page 100 == page 500 == page 5000, IDENTICAL TO THE BYTE
{"where":["ایلام"]}     page 50 answers `data: {}` — empty: the real end
```

The server caps the page index at **100** and re-serves the hundredth for
ever, with no error and no mark of any kind. **Both stop rules every other
adapter here uses therefore fail, and both in silence:**

| rule | what it does on this board |
| :-- | :-- |
| stop on an empty page | **never stops at all** on a broad query |
| stop when nothing is new | stops at 2 000 and **calls the cap the board** |

The walk stops on a page that **repeats the previous one**, names it, and
declares the count a lower bound for that query. *This is #894's family in its
sharpest form: `new == 0` does not return zero here — it returns a round
number that is wrong.*

## Three shapes that kill a careless reader

- **`data` is a LIST when full and a DICT (`{}`) when empty.** `data[0]` raises
  `KeyError` on exactly the page that means «done».
- **The list answers `201`**, not 200, to a POST that creates nothing. A check
  written for `== 200` refuses every page and reads like a host that closed.
- **A chunk address is a content hash.** The bundle is re-read in the same
  session as the shell; yesterday's copy points at addresses that no longer
  exist, and the 404 they earn looks exactly like a refusal.

## There is no witness, and the card says so

`meta` carries a URL and a title. `POST /search-api/search/filter-options`
returns 253 professions, 50 provinces, 29 sectors, 133 technologies, 20
benefits — **and not one count**. `/sitemap.xml` answers 404.

> **Nothing on this board can be held against what the tool emits.** So every
> count it prints carries «a LOWER BOUND» in the same sentence, and the only
> bound that exists is the page cap.

And the province facet, which is how a query stays under that cap, **does not
partition**: of the hundred adverts held, ninety-nine carry one province and
one carries **thirty-one**. The dedup by `id` is mandatory, and a sum over
provinces is worth nothing as a witness.

## Two things honoured beyond the letter

1. The rules name **`ClaudeBot` with `Crawl-delay: 5`**; `Claude-User` is not
   named and falls into `*`, which imposes none. **The adapter paces at 5 s
   anyway** — the host set five seconds for every robot it names, and our token
   escapes it only through a gap in its file.
2. `*` refuses **`sort=` and `posted=`** on `/jobs` and `/search`, and the
   facets `/jobs/*حقوق-از` (salary-from) and `/jobs/*-برای-` («for …»). This
   route is covered by none of those lines — and the four are **refused by
   name** in `--filter` all the same. *A written `Disallow` is an intention; a
   route that dodges it by the path betrays it just as well.*

   **And the refusal had to be made reachable to be a refusal.** A first
   version built the query body from `--where`/`--query` only and then checked
   it for `sort`/`posted`: the keys could never be there, so the check could
   never fire while its comment claimed a discipline the code did not have.

## What is never emitted

The **`gender`** the board prints beside every advert — present on every row of the 780 — is never carried (#183), and every row says `criteria_withheld:
["gender"]` because the field really is on every row. Recruiter contacts and
internal identifiers are never read.

## The host does not sustain a hundred-request walk, and that points the same way as the cap

Two full attempts on 2026-09-24, both cut:

```
attempt 1   780 emitted over 40 pages   SSL: UNEXPECTED_EOF_WHILE_READING
attempt 2   160 emitted over  8 pages   Operation timed out, twice on page 9
```

A hundred requests five seconds apart is **eight minutes of exposure**, and the
rows are written as they are read precisely because of it — both attempts kept
everything they had read, and each ended with a line saying it had been cut
rather than leaving a pile of rows with nothing under them. *A truncated walk
that says nothing reads as a smaller board.*

> **The cap and the fragility point at the same conduct: walk BY PROVINCE.**

`jobs --where ایلام --all` emitted **127 over 7 pages in 47 seconds and ended
on its own**, exit 0. A province walk is short, finishes, and stays under the
cap; the unfiltered walk is the one that exposes longest for the most bounded
result — it stops at 2 000 whatever happens.

**And the route invites its own trap, so the warning belongs here and not only
further down: DO NOT ADD THE PROVINCES UP.** Of the hundred adverts held, one
carries **thirty-one** provinces — a nationwide posting appears in thirty-one
province walks. The facet does not partition, so a sum over provinces is not a
count of the board and not a witness; **only the union, deduplicated by `id`,
is a number**. The adapter dedups within a run; across runs it is the caller's
to do.

## No `ad` command, and that is a measurement

The advert's own address is the same Nuxt shell, and the bundle exposes **no
per-advert endpoint** — only `/related-jobs/…`. What the list row carries is
what this board gives.

## Invocation

```
eestekhdam.py jobs [--pages N | --all] [--where KEY] [--query Q] [--filter KEY=VALUE]
eestekhdam.py filters
```
