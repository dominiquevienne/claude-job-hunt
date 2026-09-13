# Board adapter — Virtuális Munkaerőpiac (`vmp.munka.hu`, Hungary): the public employment service states its count when it refuses to list — 1 806 — and answers 404 to everything after fourteen requests

<!-- verified: 2026-09-13 -->

<!-- hosts: vmp.munka.hu -->
<!-- script: vmp.py -->
<!-- host-forms: vmp.munka.hu -->
<!-- host-forms-basis: read — `vmp.py:HOST`, a single literal; every link the site writes is relative to it · 2026-09-13 -->
<!-- countries: HU -->
<!-- content: measured · **«A lista túl sok elemet tartalmaz (1806)» — the site's own count, stated on the unfiltered search it refuses to list** (18:19 UTC; 1 799 for the letter «a»); a filtered search is listed with «(N találat)» — Budapest 141 over 3 pages of 50, category 14 «Jog» 4, category 3 «Asszisztencia» refused at 203, category 7 refused at 435 — so the site's own threshold sits between 141 and 203; `vmp.py search --helyseg Budapest --pages 1` emitted 50 of 141 (18:22 UTC, bounded); **at 18:23 UTC, after 14 requests in four minutes at 2 s, the host answered 404 with a 546-byte «A megadott cím nem található» page on every path, the root included, still at 18:25** — a rate limit rendered as not-found is the likeliest reading, not a verdict; no rules file (404, an absence); the employer's name «Bejelentkezés után látható» on every row · 2026-09-13 -->
<!-- witness: the site's own figures, of two kinds — «(N találat)» when it lists, read on every page and printed beside the emitted count; «túl sok elemet tartalmaz (N)» when it refuses, printed as the site's count and exited on; `categories` sums the 25 and calls the sum a bound · 2026-09-13 -->

**Hungary's public employment service, in a market served by one
private board (Profession.hu) — 1 806 open postings by the site's own
sentence on the day, an employer's name behind a login on every one of
them, and a host that stopped answering after fourteen polite
requests.** Issue #358. Measured 2026-09-13 18:19–18:25 UTC by the
declared client, the guard on the exact path first (no rules file →
`allowed()` True, `certain: True`, an absence).

## The form, and what the site does with a search

```
robots.txt                                   404 — an absence of rules (a knowledge: nothing refused, nothing asked); no Sitemap, no Crawl-delay
GET /                                        200, 53 827 B — «Virtuális Munkaerőpiac Portál»; form GET /allas/talalatok (kulcsszo, helyseg, kategoria [25], tipus=allas); /allas/reszletes_kereses adds isk, feor, nyelv[], jogsi[] …
GET /allas/talalatok                         200, 48 436 B — «A lista túl sok elemet tartalmaz (1806), kérjük, szűkítse az eredményt»: NO list, the count stated
GET /allas/talalatok?helyseg=Budapest        200, 75 216 B — «Találatok listája (141 találat)», 50 rows, pager ?helyseg=Budapest&oldal=2&sorrend=2&irany=ASC (to 3)
GET /allas/talalatok?kategoria=14            200 — «(4 találat)», 4 rows          ·  ?kategoria=3   «túl sok … (203)»   ·  ?kategoria=7   «túl sok … (435)»   ·  ?kulcsszo=a   «túl sok … (1799)»
GET /allas/talalatok?helyseg=Pest            200 — «(0 találat)» — a county's bare name matches nothing; the city does
GET /allas/reszletek/590506                  200, 65 440 B — the detail
18:23 UTC and after: GET / and every path      404, 531–546 B — «A megadott cím nem található. The specified URL cannot be found.»
```

**The site states its count in both of its answers.** When the set is
small enough it lists it under «Találatok listája (N találat)», 50 a
page; when it is not, it prints «A lista túl sok elemet tartalmaz (N)»
and no list — **and that N is the board's figure**: 1 806 unfiltered.
The threshold is the site's, between 141 (listed) and 203 (refused), and
the adapter never guesses it: a listed search is walked and compared, a
refused one prints the site's N and exits 6 with the word «narrow».
`categories` asks the 25 categories once each and prints every count
with its state, listed or refused, and the sum beside the unfiltered
count — **a sum of categories, an upper bound** (an advertisement may sit
in two).

```
vmp.py search --helyseg Budapest --pages 1
[vmp] 50 emitted of the 141 the site states (helyseg=Budapest) — 1 page(s) of 50 walked by request (--pages/--limit), not a shortfall.
[vmp] the employer's name is behind a login on every row — never read; `employer` is null on 50 of 50.
vmp.py search
[vmp] the site states 1 806 for this search and refuses to list it («A lista túl sok elemet tartalmaz») — narrow with --kategoria/--helyseg/--kulcsszo/--isk; 1 806 is the site's own count, not the adapter's.
```

## Fourteen requests, then 404 on everything

Between 18:19 and 18:23 UTC the declared client made fourteen requests
at 2 s or more apart — the root, two forms, ten searches, one detail —
and every one was answered 200. **The fifteenth, and every one after it
for the minutes that followed, was a 404**: the root, the search, the
detail, all with the same 531–546-byte «A megadott cím nem található»
page. *A rate limit rendered as not-found is the likeliest reading; an
outage is not excluded; a verdict is not taken.* The adapter's spacing
is 5 s since, its 404 on the search page says «the host answered 404 to
the root as well after a burst — wait, and try the root first», and
**the full walk of `categories` (26 requests) was not run** for that
reason: what it prints is exercised on stubs and its sum on the live
site is not established.

## The row and the detail — and the login in the middle

```
row      <td><a href="/allas/reszletek/600230">1332 - Vendéglátó tevékenységet folytató egység vezetője</a></td> <td>…egyetem, főiskola…</td> <td>Budapest 21. ker.</td> <td><i>Bejelentkezés után látható</i></td>
detail   «Általános irodai adminisztrátor - ügyintéző (8015711)» · Munkakör (FEOR) · Munkakör kiegészítése · Felajánlott havi bruttó kereset (Ft) «373 200 - 0» · Munkavégzés helye «1139 Budapest 13. ker. Teve út 4-6»
         Elvárt iskolai végzettség · Megjegyzés (the description) · Érvényesség időtartama «2026.01.20 - 2026.09.25» · Alkalmazni kívánt létszám «40 fő» · Teljes/rész munkaidő «8 / 0» · Munkarend
         «A foglalkoztató részletes adatainak megjelenítéséhez kérjük jelentkezzen be!»
```

The row gives the FEOR code and occupation (the site's title), the
education required, the workplace to the district, and — where the
employer's name would be — «Bejelentkezés után látható», visible after
login: **`employer` is null on every row and `employer_hidden` says
why; the plugin never logs in.** The detail adds what the site does
state: **the salary as «havi bruttó kereset (Ft)» — monthly, gross, HUF,
the unit stated on the page** (`salary_unit_stated: true`; the upper
bound «0» is emitted as null), the headcount, the validity dates, hours,
schedule, education, the description under «Megjegyzés». The workplace
there is a street address; it is cut to the city and district, the
row's own granularity. No contact is on either page. Read in full on
one (`590506`).

## Configuration

```yaml
boards:
  vmp:
    enabled: true
    helyseg: "Budapest"     # a city as the site spells it; a bare county name matched nothing
    kategoria: ""           # 1–25; see `categories`
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `helyseg`, `kategoria`, `kulcsszo`, `isk` | no | the search must be narrow enough for the site to list it; unfiltered it states 1 806 and lists nothing |

No credentials, no browser, no login. `search` is one request per 50 at
5 s; `categories` is 26; `ad` is one.

## What is not established

- **The threshold** — between 141 and 203 on the day; the site's.
- **The sum of the 25 categories** — the walk was not run after the
  404s; the command is exercised on stubs.
- **What the 404 is** — a rate limit, an outage, or a block; it began
  after the fourteenth request and was still on two minutes later.
- **How to name a county** — `helyseg=Pest` and `Borsod-Abaúj-Zemplén`
  matched nothing; `Budapest` did.
- **Whether a login shows more than the employer** — not the plugin's
  view.

## 2026-09-13 — shipped

`search --helyseg Budapest --pages 1`: 50 of 141. `search` unfiltered:
the site's 1 806, refused. `ad` on one. Four tests; six mutations on a
detached worktree (`python3 -B`), six red — the refusal regex broken,
the employer taken from the cell, the «találat» regex broken, the dedup
dropped, the category sum ignoring refused counts, the salary unit set
to null.
