# Board measurement — KKTC Portal — iş ilanları (`kktcportal.net`, Northern Cyprus): **a pager that actually ADVANCES** — 390 adverts over 17 pages, the walk ending on an empty page with no count stated anywhere — and **a board that has stopped publishing**: every advert past its `validThrough`, newest `datePosted` 2026-07-09. Adapter `kktcportal.py` (#724)

<!-- verified: 2026-10-01 -->

<!-- hosts: kktcportal.net -->
<!-- script: kktcportal.py -->
<!-- countries: CYN -->
<!-- route: http -->
<!-- content: measured · **the rules file is served (`state: read`, `certain: True`) and writes no Crawl-delay — 2 s are ours. THE PAGER ADVANCES: `/is-ilanlari` 200 (374 788 B) 24 adverts, `?sayfa=2` 200 (386 467 B) 24 sharing NONE with page 1, `?sayfa=17` 200 (271 426 B) 6, `?sayfa=18` 200 (232 719 B) **0 — the walk's end**: 390 adverts read, where 17 × 24 bounded it at 408. Of the clamp/crush/reset/announce family this board exhibits NONE. The advert (256 092 B) carries TWO `ld+json` blocks — an Organization/WebSite pair and the `JobPosting` — so the block is chosen by `@type`, never by position; it gives title, hiringOrganization, jobLocation, employmentType, datePosted, validThrough, description. The LIST carries a title and a link, no employer and NO date** · 2026-10-01 -->
<!-- witness: none stated — 390 is what the pager SERVED, bounded by 17 pages and ended by an empty one; the run says which. And `emitted + unreachable + unread == enumerated` holds · 2026-10-01 -->

<!-- content: measured · **`/is-ilanlari` (200, 375 033 B, md5 d0f24e297e25 / 1cdab24cea82 — a rendered element moves) lists 24 distinct ads as `/is-ilanlari/<slug>-<district>-<id>` with a pager `?sayfa=2`, `?sayfa=3` … `?sayfa=17` (at most 17 × 24 = 408, not stated); no JobPosting; `_robots.allowed('kktcportal.net','/is-ilanlari')` → open, certain** · 2026-09-18 -->
<!-- witness: none — no count stated; the pager bounds the list (17 pages) · 2026-09-18 -->
## Adapter delivered 2026-10-01 — and two findings that are about the board, not the route

```
kktcportal.py jobs --country-code CY
  -> 390 advert(s) enumerated over 17 pages; the walk ended on an empty page
  -> no count stated anywhere: this is what the pager SERVED
  full run: 17 list pages + 1 request an advert = 407 requests at 2 s, about 14 minutes
```

### The pager advances, which is worth marking as the exception

Of the stop-rule family this repository has collected — **clamp** (re-serves the last page), **crush**
(identical bytes), **reset** (falls back to the first slice), **announce** (states a total it does not
carry) — *this board exhibits none*. Page 1 and page 2 share no advert, page 17 is partial at 6, page
18 is empty. **The repetition check is kept anyway**: it costs one comparison, and its absence is what
the family is made of.

### The board is DORMANT, which is not BROKEN

**Every advert emitted is past its `validThrough`, and the newest `datePosted` read is 2026-07-09** —
twelve weeks old, six weeks expired. Ids descend, so the first page carries the newest. *The route
works; the site has stopped publishing.* **The run states that with the board's own date as the
bound**, because reporting a dormant board as empty or broken would be a claim about our tooling
dressed as a claim about the market. Expired adverts are **emitted and counted, never dropped**: the
board lists them, and discarding them would replace its statement with ours.

### A premise of the 2026-09-18 reading no longer holds

That reading reported *«&nbsp;the list's markup dates are aberrant, 26/05/1779&nbsp;»*. **Measured
2026-10-01, the list markup carries no `jj/mm/aaaa` date at all** — zero, not an aberrant one. Either
the site changed or the figure described something else; **recorded rather than quietly dropped**, and
the date now comes from the advert's `datePosted`.

*No salary field exists anywhere in this payload, so neither the `baseSalary.currency` rule nor the
telephone-digits rule has anything to act on — said so that their absence reads as measured rather
than forgotten. A telephone number in a description IS withheld; one was met on the first page.*


**Found by the Northern Cyprus search of #606 (a country never searched),
measured 2026-09-18 07:20–07:22 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #606: two searches in Turkish naming the Labour Department and the
private boards, no composed host names. *A measurement, not an adapter.*

```
_robots.allowed('kktcportal.net', '/is-ilanlari')   open
GET https://kktcportal.net/is-ilanlari   200 ×2 — see the content line
```

The adapter's first line: the 17 pages, the ad's fields (the dates in the markup are odd — «26/05/1779» — and to be read on the ad).
