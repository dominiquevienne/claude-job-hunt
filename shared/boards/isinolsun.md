# Board adapter — İşin Olsun (`isinolsun.com`, Türkiye): the enumeration ships, no advertisement page answers — NON FAISABLE at 13.09.2026 by the owner's decision (#404)

<!-- verified: 2026-09-13 -->

<!-- hosts: isinolsun.com, www.isinolsun.com -->
<!-- script: isinolsun.py -->
<!-- countries: TR -->
<!-- content: measured · **NON FAISABLE au 13.09.2026 — l'énumération sort (87 504 clés), aucune page d'annonce ne répond, sur deux clients** (décision du propriétaire, #404 : «un script qui ne rend rien ne compte pas et est classé comme infaisable» — la ligne `route: none` prime sur `script:`; elle se rouvre le jour où une page répond) — rules read twice and certain (66 B, `Allow: /`, one Sitemap line, no agent named; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200 on the root and the sitemaps: `/sitemap.xml` names 30 files, `jobdetailsitemap1.xml` (9 790 616 B, 50 000 `<loc>`) and `jobdetailsitemap2.xml` (7 432 763 B, 37 504) hold **87 504** distinct keys `/is-ilani/<slug>-0ioj<32 hex>`, a `lastmod` each, eight slugs with a literal tab; the root states «87.394 İş İlanı» — 110 more emitted than stated, two witnesses never merged; **every request under `/is-ilani/` and `/is-ilanlari` stalled without a byte** (25 s, 120 s, HEAD or GET, declared identity or curl's own name, 17:41–17:47 UTC) while the root answered in 0.4 s — the page is a browser question, `ad --url` reports and never pretends to read · 2026-09-13 17:49 UTC -->
<!-- witness: the root page's own «87.394 İş İlanı» (2026-09-13 17:47 UTC), beside the 87 504 keys of the two job-detail sitemaps — «87 504 emitted, site states 87 394 — 110 more emitted than the site states», printed by `isinolsun.py list` and never merged; the advertisement page has never been served to this client, so no reader is written -->
<!-- route: none · for the advertisement PAGE only: every request under /is-ilani/ stalls without a byte — for the declared client (2026-09-13 17:41–17:47 UTC, 25 s then 120 s) AND for a real browser (a tab on the root, then same-origin `fetch()` of two advertisement addresses, one of them a link the root itself offers: no byte in 25 s and in 40 s, 18:05–18:06 UTC); nothing refused in writing, no challenge — the enumeration by sitemap is shipped, the page is a dated fact on two clients, not a verdict · 2026-09-13 -->

**Shipped 2026-09-13 under #382 — Turkey's first national adapter, half of
one by construction: the enumeration is served, the page is not.** Every
fetch under the declared identity, the guard on the exact path first.
*Page Turquie of 2026-09-01 counted 82 407 in the same two files; twelve
days later 87 504.*

```
isinolsun.py list                  # the index and two job-detail files (4 KB, 10 MB, 7 MB) at 2 s, then the root for its count — ~15 s
isinolsun.py ad --url https://isinolsun.com/is-ilani/<slug>-0ioj<hex>     # attempts once (30 s) and REPORTS — see below
```

## The rules — sixty-six bytes

```
robots.txt      66 B, md5 6df34341f3fd, read twice, certain: True — `User-agent: *` / `Allow: /` / `Sitemap: https://isinolsun.com/sitemap.xml`
identity("/")   http, claude-user — no agent named; `www.` answers the same file
verdict()       sweep True, certain True, crawl_delay none  -> Pace(HOST, own=2.0), two seconds, ours (files of 7 and 10 MB)
allowed()       True on `/`, `/sitemap.xml`, `/sitemaps/jobdetailsitemap1.xml`, `/is-ilani/…`, `/is-ilanlari`
```

## The sitemaps — two files, one hex key, and the root's own count

| question | answer (2026-09-13, 17:38–17:49 UTC) |
| :-- | --: |
| `/sitemap.xml` | 4 227 B, 30 files: **`jobdetailsitemap1`, `jobdetailsitemap2`**, then positions, cities, towns, companies (14 files), part-time, disabled, custom URLs, the blog — the other 28 never read |
| the two job-detail files | 50 000 + 37 504 = **87 504** `<loc>`, a `lastmod` each (`2026-09-13T02:10:10+03:00`, one nightly generation), all of the shape `/is-ilani/<slug>-0ioj<32 hex>` — **87 504 distinct keys**, none repeated across the two files |
| the slug | the title and the employer run together, in Turkish without diacritics («tatli-ustasi-carmen-tatlicilik», «magaza-satis-danismani-…» 1 664 times): emitted as `slug`, never split — no mechanical boundary between the two |
| eight slugs | carry a **literal tab** («…-bandido-cosmetics-\t bandido-cosmetics-ic-ve-dis-ticaret-…», one employer): the adapter's slug pattern is `[^/]+?` so that the sound key behind them is kept |
| the root's own count | **«87.394 İş İlanı»** beside «16.155.987 İndirme» (a download counter, never read) → «87 504 emitted, site states 87 394 — 110 more emitted than the site states» |

**The two witnesses are printed apart and never merged.** *110 more keys
in a file generated at 02:10 than in a counter read at 17:47 is two clocks;
the adapter says both and stops there.*

## The advertisement page — stalled for every plain client, and said so

| request (2026-09-13) | under the declared identity | under curl's own name |
| :-- | --: | --: |
| `GET /is-ilani/tatli-ustasi-…-0ioj898A…` | **no byte in 25 s, then in 120 s** (17:41–17:44) | no byte in 25 s (17:46) |
| `HEAD` on the same | no byte in 25 s | — |
| `GET /is-ilani/guvenlik-gorevlisi-…-0iojD487…` | no byte in 25 s | no byte in 25 s |
| `GET /is-ilanlari`, `/is-ilanlari/istanbul` | no byte in 25 s | — |
| `GET /`, `/robots.txt`, `/sitemaps/mainpagesitemap.xml` (17:47, control) | **200 in 0.36 s, 0.20 s, 0.22 s** | — |

**Nothing refused us in writing, and no status was ever returned: the
page's backend does not answer a plain client, whatever its name.** *So
`ad --url` does not carry a reader that no page was ever served to write
against: it attempts the page once and REPORTS — stalled → the dated fact,
exit 6; served → the status, the size and the `JobPosting` count, exit 6,
because the reader is then the next commit, written from the page.* **A
browser route is the next measurement (a tab and its `fetch()`, as #222
measures); it belongs to a session with a tab, and the card says so.** This
is not a verdict that the board is closed — the board serves its whole
inventory by sitemap.

## What the adapter does, and refuses to do

- **Three sitemap requests and one root request, at 2 s** — no page walk;
  a file that disagrees with itself prints no count (exit 6).
- **Never splits the slug into a title and an employer** it cannot separate.
- **Never pretends to read the page**; never emits a contact (nothing of the
  page is emitted at all).
- **Not a verdict that anything is closed.**

## Tests

`TwoJobDetailSitemapsAgainstTheRootsOwnCountAndAPageThatIsReportedNotRead`
in `tests/test_core.py` — two cases (the keys deduped across the two files,
the tab slug kept, a URL of another shape set aside, the root's count
printed apart and the download counter never read; the page reported
stalled with the dated fact, reported served with its `JobPosting` count
and nothing emitted, a non-advertisement URL refused). Six mutations under
`python3 -B` on a detached copy, six reds: the dedup removed, the thousands
dot kept, the key taken from the slug, the slug narrowed so the tab is
lost, the stall branch dropped, the served report's count zeroed.

## 2026-09-13 18:05 UTC — the advertisement page from a browser tab: the same stall (#382)

```
tab: https://isinolsun.com/is-ilani/tatli-ustasi-…-0ioj898A…     navigate — the tab never left chrome://newtab (no document arrived)
tab: https://isinolsun.com/                                      200 «Evinin Yakınındaki O İşi Hızlıca Bul | İşin Olsun», 202 380 characters — served, no challenge; 9 /is-ilani/ links on the page
tab: fetch('/is-ilani/tatli-ustasi-…-0ioj898A…')                 AbortError at 25 s — no byte
tab: fetch('/is-ilani/site-yoneticisi-…-0iojB641…')  (the root's own first link)   AbortError at 40 s — no byte
```

**The stall is not a client filter**: a real browser, on the site's own
link, with the site's own cookies, gets no byte either. Not a challenge
(borne 2 does not enter), not a refusal in writing, not a verdict — a
dated fact on two clients, one hour apart, from one network. The
`ad` reader stays as it is (one attempt, a report); what would change it
is a byte, from anywhere, on any day.

## Provenance

- `io/robots.txt`, `io/sitemap.xml`, `io/jobdetailsitemap{1,2}.xml`,
  `io/root.html` — 2026-09-13 17:38–17:40 UTC, `bin/fetch-body.py`,
  provenance beside each; the stalled requests left no body (a refusal has
  no trace; the lines above are the trace); scratchpad of
  `claude-job-hunt-ab`.
- `isinolsun.py list --limit 1` at 17:49:02–17:49:13 UTC: the two
  `[isinolsun]` lines quoted above verbatim (87 496 + 8 tab slugs on that
  run, before the slug pattern was widened; 87 504 after).
