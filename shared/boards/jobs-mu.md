# Board adapter — Jobs.mu (`www.jobs.mu`, Mauritius): `jobsmu.py` since 2026-11-07 (#698) — a board that states **no total of its own**, whose size is established by **three independent enumerators agreeing on the same members**, and whose **own RSS feed publishes links that return 404**; the witness #698 proposed — the sum of the category counters — is measured FALSE and over-counts by multi-membership

<!-- verified: 2026-11-07 -->

<!-- route: http · 8 · 2026-11-07 -->
<!-- hosts: www.jobs.mu -->
<!-- script: jobsmu.py -->
<!-- countries: MU -->
<!-- content: measured · **`jobsmu.py` shipped. The board STATES NO TOTAL: `/jobs/` (200, 86 405 B, md5 7201332b2d52, 03:22 UTC) is rendered server-side, its pager carries exactly `data-num="1"`, and its `ItemList` states `numberOfItems: 8` which is the PAGE's count and not the board's. THREE INDEPENDENT ENUMERATORS AGREE ON THE SAME 8 MEMBERS: that `ItemList` (8 elements, 8 distinct hrefs for 16 links, each advert linked twice in its card), the `/rss/` feed (200, 11 393 B, md5 3d7f4a8f8385, 8 items), and the UNION of the 7 category pages. THE WITNESS #698 PROPOSED IS FALSE and over-counts: the category counters sum to 9 for 8 adverts, advert 139890 being filed under both 707 accounting-finance and 703 customer-service-bpo, and the union is 8 distinct so no ninth advert is withheld. THE FEED'S OWN LINKS ARE DEAD: its `<link>` and `<guid>` are CDATA addressing `/display-job/<id>/<Title>.html` and `/display-job/139963/Driver.html` returns 404, so its IDS are read and its URLS never followed. THE SLUG IS OPTIONAL — `/job/139963/` returns 200 with 71 529 B and md5 09ed83f51bea, identical to the byte to `/job/139963/driver/`, which is what lets `ad --code` resolve the feed's ids. Every advert is a complete `JobPosting` with ISO `datePosted` and `validThrough`, `PostalAddress`, `identifier`, `directApply` and `baseSalary` in MUR with a min, a max and `unitText: MONTH`. Rules: `/robots.txt` 200, 274 B, three lines, ZERO `Disallow` and ZERO `Allow`, `state: read`, `certain: True`, group `*`, and no `Crawl-delay` written so 4 s is ours. PAGINATION IS NOT ESTABLISHED: `?page=2` returns the same 8 ids, which on a one-page list cannot distinguish a pager that clamps from a parameter that is ignored** · 2026-11-07 -->
<!-- witness: the `/rss/` feed, a SECOND ENUMERATOR and not a second reading of the list — 8 items naming the same 8 ids, corroborated by the UNION of the 7 category pages (8 distinct). **This REPLACES the «none» of 2026-09-18 and REFUTES the witness #698 proposed**: the sum of the category counters is 9 for 8 adverts, over-counting by multi-membership, and the member is named (139890). The board states no total of its own, so the `ItemList`'s `numberOfItems` is the PAGE's count · 2026-11-07 -->

## 2026-11-07 — #698: the adapter ships, the proposed witness is refuted, and the feed addresses a form the site no longer serves

The head this card carried until today read «**no adapter yet**» and «the list, its pager and the ad are the adapter's first line»; both are history. #698's «rien de mesuré ; la liste n'est pas encore lue» is answered, and its premise of 2026-09-18 was **fifty days old** when it was refreshed.

**What the measurement established, and what it refuted:**

- **The board states no total.** The list is rendered server-side, the pager carries exactly `data-num="1"`, and nothing on the page says how big the board is. The site's «2,700+ employers» and «Hundreds of new jobs added daily» are its own marketing copy in a `<meta>` description: not a total, not dated, and no denominator.
- **The witness #698 proposed OVER-COUNTS, and the member is named.** The issue wrote «la somme des compteurs de catégorie comme témoin». The seven non-empty categories summed to **9** while the list served **8**, and that DISAGREEMENT is what tested it — an agreement on the small case proves nothing, being the regime where a page count and a board count coincide. The seven category pages were walked and their UNION is **8 distinct ids, exactly the list's members**, so no ninth advert is withheld. The cause is MULTI-MEMBERSHIP: advert **139890** is filed under both `707 accounting-finance` and `703 customer-service-bpo`. *A sum over categories is not a count of adverts, and it is wrong by exactly the number filed twice.*
- **What stands in is the RSS feed, because it is a SECOND ENUMERATOR and not a second reading of the first.** `/rss/` carries 8 `<item>`s naming the same 8 ids. Three instruments then agree on the same MEMBERS, not merely on a count: the page's own `ItemList` (`numberOfItems: 8`, 8 elements, 8 distinct hrefs for 16 links, each advert being linked twice in its card), the feed, and the union of the categories. *Weaker than a board stating its own total, and declared weaker.*
- **The feed's own links are DEAD, and that decides the shape of `ad`.** Its `<link>` and `<guid>` are **CDATA** addressing `/display-job/<id>/<Title-cased-and-accented>.html`, and `/display-job/139963/Driver.html` returns **HTTP 404** while the list's `/job/139963/driver/` returns 200. The adapter reads the feed's IDS and never follows its URLS, and it refuses that form BY NAME rather than by a request whose answer is already known.
- **The slug is OPTIONAL, which is what makes those ids usable at all.** `/job/139963/` returns 200 with **71 529 B and md5 `09ed83f51bea` — identical to the byte** to the slugged form, and declares `rel="canonical"` on the slugged one. Hence `ad --code`: a slug is not reconstructible from a title, `Receptionist - Réceptionniste` becoming `receptionist-receptionniste`.
- **Every advert is a complete `JobPosting`**: ISO `datePosted` and `validThrough`, `employmentType`, `hiringOrganization` with the employer's own site in `sameAs`, `jobLocation` as a `PostalAddress` (locality, region, `addressCountry: MU`), `identifier`, `directApply`, and **`baseSalary` in MUR with a min, a max and `unitText: MONTH`**. Reading the posting BOUNDS the redaction structurally: this site's own telephone lives in the page footer, outside every posting.
- **The list itself carries six fields per advert, classified by their ICON and never by their position** — `icon-feather-briefcase` is the employer, `location-on` the place, `awesome-money` the salary, `access-time` the posting date, `access-alarm` the closing date. An icon class is a DECLARATION; the order of the `<li>`s would be a motif to prove in both directions. An unknown icon goes to `unclassified` and the run says so.

**Two defects found by RUNNING it, and the second is the first one moved one consumer further:** a hand-rolled table of six named entities put `Vos responsabilit&eacute;s` into an `excerpt`, and fixing it for the LIST did not audit the ADVERT, which reads its text from the posting and never passes through that function — a live `ad` emitted `client&rsquo;s representative`. *A hand-rolled decode does not raise; it returns TEXT.* And the first path filter was a REFUSAL list that was **INERT**: the advert motif refused anything outside `/job/<id>/` before the chokepoint was reached, so `ad --url .../registration/` was refused by the WRONG guard with the wrong reason. It is now a POSITIVE allowlist whose default fails visibly, and it is measured reachable.

**PAGINATION IS NOT ESTABLISHED, and it is declared rather than concluded.** The pager renders one page and `?page=2` returns the SAME 8 ids; **on a one-page list that cannot distinguish a pager that clamps from a parameter that is ignored**, and CareerHub's conclusion does NOT transpose, its pager having offered further pages. The adapter follows the pager's own `data-num` and claims nothing. *Consequence: its multi-page branch is green on a fixture and never taken on the live board, and a run reports which happened instead of leaving a green that reads «covered».*

**NOT ESTABLISHED, and declared:** that `sitemap-main.xml` — named by `/sitemap.xml`, a 283 B sitemapindex pointing at it and at the blog's `advice/sitemap_index.xml` — holds nothing the list omits. It is not walked, three enumerators already agreeing on the same members, and «we did not look» is not «there is nothing there».

**And the phone anchor's reason is MEASURED, not transported.** Unanchored, the motif takes **the sixteen ISO dates** the adapter emits and, over the whole advert page, the `rgba()` numbers of the site's stylesheet. Anchored on the Mauritian dialling code or a written label it takes none of them, and nothing at all on this board, whose adverts deposit no telephone — so an empty `withheld_fields` here is honest. *The rupee range is NOT the candidate: `Rs 12,501 - Rs 25,000` is not taken even unanchored, the `Rs` between the two numbers interrupting the motif. That claim was written first and measured false, and its test was DISARMED until it was.* And `salary_text` never reaches the scrubber at all, coming through a positive floor instead — structural rather than careful, which is the kyat's lesson.

```
jobsmu.py jobs --country-code MU            the list, with the RSS feed as its witness
jobsmu.py jobs --no-witness                 one request fewer, and the run says it has NO witness
jobsmu.py ad --code 139963                  one advert, by its identifier; the slug is optional
jobsmu.py ad --url https://www.jobs.mu/job/139963/driver/
```

Measured 2026-11-07 03:22–03:27 UTC by the declared client, the guard on each exact path in a turn distinct from retrieval and with one token (`claude-user`): `/robots.txt` 200 (274 B, md5 `fdf4c951f001`, three lines, **zero `Disallow` and zero `Allow`**, no `Crawl-delay` so 4 s is ours), `/jobs/` 200 (86 405 B, md5 `7201332b2d52`), `/jobs/?page=2` 200 (86 405 B, md5 `6b2a575e2c65` — the same size and a different digest, so the page carries a rendered element), `/rss/` 200 (11 393 B, md5 `3d7f4a8f8385`, 8 items), `/job/139963/driver/` 200 (71 529 B, md5 `09ed83f51bea`), `/job/139963/` 200 (identical, same md5), `/display-job/139963/Driver.html` **404** (61 187 B of readable body, not kept), `/sitemap.xml` 200 (283 B), and the seven category pages.

<!-- content: measured · **the root (200, 82 882 B, md5 3c59c90be4b6 identical on two reads) is the board's front — `/jobs/`, category blocks with small counters («2 Jobs»); no total, no JobPosting; `_robots.allowed('www.jobs.mu','/')` → open, certain; the list and the ad not read** · 2026-09-18 -->
<!-- witness: none — the root states category counters, no total · 2026-09-18 -->

**Found by the Mauritius search of #618 (a country never searched),
measured 2026-09-18 06:45–06:47 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #618: one search naming the National Employment Department's portal
and the private boards, no composed host names. *A measurement, not an
adapter.*

```
_robots.allowed('www.jobs.mu', '/')   open
GET https://www.jobs.mu/   200 ×2 — see the content line
```

The list, its pager and the ad are the adapter's first line (its `adapter` issue).
