# Board adapter — SecretCV (`www.secretcv.com`, Türkiye): the generalist whose every parameterised address answers 410 to this client — its list read one first page at a time (the country's, and the 33 city and sector lists it links), never paged; «20.409 İş İlanı Listelendi» stated on 2026-09-14; the ad open to anyone, its text scrubbed, the application a login never touched

<!-- verified: 2026-09-14 -->

<!-- hosts: www.secretcv.com, secretcv.com -->
<!-- script: secretcv.py -->
<!-- host-forms: www.secretcv.com -->
<!-- host-forms-basis: read — every card link, section link and pager link is absolute on `www.secretcv.com`; `secretcv.py` names that host as a literal and refuses an ad address on any other · 2026-09-14 -->
<!-- countries: TR -->
<!-- content: measured · **`/is-ilanlari` states «20.409 İş İlanı Listelendi» (200, 341 093 B, 02:36 UTC), 20 cards, a pager whose «Son Sayfa» names `?sf=342` — and `?sf=2` answers HTTP 410 to this client (314 650 B, with page 2's 17 cards in the body), as does every parameterised address tried: `?sf=342`, `?l=50` (50 cards in a 410 body), `?sr=4`, with a Referer, without the slash (02:39–02:41 UTC); the first page of a city or sector list (`/is-ilanlari/istanbul-is-ilanlari`, 341 292 B) answers 200 — 33 such lists are linked from the listing; 48 distinct cards read from three first pages** — read by the declared client, the guard on the exact path (the rules, 550 B: `*` → `Allow: /`; nineteen `Disallow` lines — `*/?sf=*`, `*/?ilanId=*`, `*/?redirect=*`, `*hesabim*`, `/is-ilanlari/ara` … — under the `OAI-SearchBot` group by the parser, `certain: True`); the ad (200, 155 557 B) carries a JSON-LD JobPosting with its full description, a labelled table («İlan Tarihi», «İstihdam Türü», «Sektör», «Eğitim Seviyesi», «Şehirler», «Yabancı Uyruklu Çalışabilir») and an «İşe Başvur» button that is `/giris-yap?redirect=1&ilanId=<id>` — the login, never touched; **the description and the qualifications scrubbed of Turkish telephone numbers and e-mail addresses** · 2026-09-14 -->
<!-- witness: the list's own «N İş İlanı Listelendi» and its pager's «Son Sayfa» — printed beside what is read on every run («… the list states 20 409 over 342 pages — the pager answers 410 to this client: first pages only, never a shortfall claimed»); a 200 page without one card exits 6 · 2026-09-14 -->

**SecretCV is a Turkish generalist with 20 409 advertisements stated on
the day — beside İŞKUR (`iskur.md`), Eleman.net (`eleman.md`) and İşin
Olsun (`isinolsun.md`, not feasible) — whose list can be read one first
page at a time and whose advertisements are open to anyone.** Issue #385.
Measured 2026-09-14 02:36–02:41 UTC by the declared client, the guard on
the exact path before each request.

## The rules, the 410, and what is read

```
www.secretcv.com/robots.txt               200, 550 B — User-agent: * → Allow: /; GPTBot → Allow: /; OAI-SearchBot → Allow: / + Disallow /banner/redirect/*, /ilan-begen-iptal/*, *hesabim*, /is-ilanlari/ara, /cikis-yap, *kvkk-modal?ilanId=*, *ara?k=*, */?ilanId=*, */?sf=*, */?redirect=*, */?k=*, */?s=*, */?b=*, */?p=*, */?o=*, */?wtime=*, */?parameters=*, /qr-basvuru, /yeniden-biz; Sitemap: /sitemap
GET https://www.secretcv.com/is-ilanlari                 200, 341 093 B — «20.409 İş İlanı Listelendi», 20 cards, «Sonraki» → /is-ilanlari/?sf=2, «Son Sayfa» → ?sf=342
GET https://www.secretcv.com/is-ilanlari/?sf=2           410, 314 650 B — 17 cards of page 2 in the body
GET https://www.secretcv.com/is-ilanlari?sf=2            410 · ?sf=342 410 · ?l=50 410 (50 cards) · ?sr=4 410 · with Referer 410
GET https://www.secretcv.com/is-ilanlari/istanbul-is-ilanlari   200, 341 292 B — the city list's first page, 20 cards, its own ?sf= pager
GET https://www.secretcv.com/amasya-et-urunleri-10868/magaza-mudur-yardimcisi-city-center-outlet-avm-is-ilanlari-1877236   200, 155 557 B — JSON-LD JobPosting + BreadcrumbList; the table; «İş Açıklaması»; İşe Başvur → /giris-yap?redirect=1&ilanId=1877236
```

**The nineteen `Disallow` lines sit under the `OAI-SearchBot` group by
the file's layout, so the `*` group this client falls in reads
`Allow: /` — and the transport says what the layout does not: every
parameterised address answers 410, with the page's content in the body.
A readable body is not an answer; the code decides.** The adapter never
sends a parameter (one in an address is refused before the gate, exit
7), reads first pages only, and says so on every run. The pages beyond
the first are a browser candidate — a refusal by code on a path the
rules open — and the issue's «les fiches exigent une connexion» was the
application, not the advertisement: the ad page answers 200 to anyone.

## The list — first pages, and the lists the site links

```
secretcv.py list --sections istanbul,cagri-merkezi
[secretcv] 48 emitted from 3 first page(s) (60 cards, 48 distinct), the list states 20 409 over 342 pages — the pager answers 410 to this client: first pages only, never a shortfall claimed; --sections all reads the 33 lists the site links.
[secretcv] no parameter is ever sent (the pager included); the application («İşe Başvur») is a login and is never touched; the ad's text is scrubbed.
```

`list` reads `/is-ilanlari` (20 cards); `--sections all` adds the first
page of each of the 33 city and sector lists the listing links
(`part-time`, `yeni-mezun`, `istanbul`, `ankara`, `izmir`, `istanbul-avrupa`,
`istanbul-anadolu`, `bursa`, `cagri-merkezi`, `bilgisayar-bt-internet` …),
deduplicated by id; a slug the site does not link is an error. A card:
the ad's address (`/<firm>-<firmId>/<slug>-is-ilanlari-<id>`, the id at
the tail), title, employer and its `/firma/` slug, city («İstanbul
Avrupa», «Tüm Türkiye»), the age the site prints («Bugün», «1 gün önce»,
«4 yıl 2 ay 20 gün önce» on one). A 200 page without one card exits 6.

## The ad

```
secretcv.py ad --url https://www.secretcv.com/amasya-et-urunleri-10868/magaza-mudur-yardimcisi-city-center-outlet-avm-is-ilanlari-1877236
{"id": "1877236", "title": "Mağaza Müdür Yardımcısı (City Center Outlet AVM)", "employer": "Amasya Et Ürünleri", "city": "İstanbul Avrupa", "employment_type": "Tam Zamanlı", "sector": "Mağazacılık / Perakendecilik", "education": "Lise (Mezun), Yüksek Okul (Mezun), …", "foreigners": "Farketmez",
 "salary_min": null, "salary_unit_stated": false, "posted": "2026-09-13", "posted_on_page": "2026-09-10", "valid_through": "2027-01-08", "qualifications": "…", "description": "…", "contacts_withheld": true}
```

The JSON-LD JobPosting: title, `datePosted` (13 September, where the
page's table says «İlan Tarihi 10-09-2026» — both emitted, `posted` and
`posted_on_page`), `validThrough`, `employmentType`, the employer and
its page, the city, `qualifications`, `baseSalary` — **«-» with
`unitText: MONTH` on the day: a value is a number, and a period without
a number is not a stated salary**. The table adds the sector, the
education levels, the cities, «Yabancı Uyruklu Çalışabilir». The
description is the «İş Açıklaması» block, ended at the «İşe Başvur»
button (the site's «İlana başvuru yapabilmeniz için…» boilerplate is not
the ad); **description and qualifications are scrubbed of Turkish
telephone numbers (`0216 572 25 25`, `+90 …`, `05…`) and e-mail
addresses; `contacts_withheld` on every record; the application is a
login (`/giris-yap?redirect=1&ilanId=`) and is never touched.**

## Configuration

```yaml
boards:
  secretcv:
    enabled: true
    sections: all         # or a few slugs: istanbul,ankara,cagri-merkezi
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `sections` | no | `all` = 34 requests, 2 s apart; none = the country's first page only |

No credentials, no browser, no login. `ad` is one request.

## What is not established

- **Why the pager answers 410** — a refusal aimed at clients without a
  browser session, or a bot rule keyed on any query string; the body
  carries the page either way. Not probed further; a browser would tell.
- **The 342 pages** — the list beyond the 20 × 34 first pages is not
  read; the count is the site's, the coverage is the first pages'.
- **`/sitemap`** — the country page of 2026-09-01 read 14 sitemaps
  without advertisements; not re-read.
- **The company lists** (`/firma/<slug>-is-ilanlari`) — another first
  page each; not walked.

## 2026-09-14 — shipped

`list`: 48 distinct from three first pages against 20 409 stated,
every card with an employer, a city and an age; `ad`: one, the table
and the posting read, the description ended at the login button, no
number or address in the output. Two tests; six mutations on a detached
worktree (`python3 -B`), six red — the parameter guard dropped, a
repeated id counted twice across lists, an unlinked section accepted,
the description not ended at the login button, a salary «-» read as a
figure, the telephone not scrubbed.
