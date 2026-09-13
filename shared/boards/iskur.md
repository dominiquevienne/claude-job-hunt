# Board adapter — İŞKUR (`esube.iskur.gov.tr`, Türkiye): the public employment agency's WebForms search, turned page by page by postback — 34 049 stated, the employer's name behind a login and left there

<!-- verified: 2026-09-13 -->

<!-- hosts: esube.iskur.gov.tr -->
<!-- script: iskur.py -->
<!-- host-forms: esube.iskur.gov.tr -->
<!-- host-forms-basis: read — `iskur.py:HOST`, a single literal; the site's own share buttons write `http://esube.iskur.gov.tr/…` and nothing else · 2026-09-13 -->
<!-- countries: TR -->
<!-- content: measured · **«Toplam Kayıt: 34049» stated by the search for all provinces, 2 270 pages of 15** — read by the declared client through the page's own WebForms POST, 18:08 UTC; İstanbul (`--il 34`) states 3 847 over 257 pages and `iskur.py search --il 34 --pages 2` emitted 30 of them (18:11 UTC, bounded by request); page 2 by `btnNext` and page 5 by a page jump both answered the page asked; the rules (70 B) `*` Allow: / with one Disallow on a popup path; **the employer's name is behind a login on every row** («İşyeri adını görmek için Sisteme Üye Girişi yapmanız gerekmektedir») and the adapter never logs in · 2026-09-13 -->
<!-- witness: the page's own «Toplam Kayıt: N» and «/ M Sayfaya Git», read on every page of every walk and printed beside the emitted count; a bounded walk says so and is never «short»; the pager's `txtCurrentPage` is checked after every turn and a page that did not turn is a fault, not a page · 2026-09-13 -->

**Türkiye's public employment agency — the country's largest open
inventory, 34 049 postings on the day, on a market of 85 million where
the only other script enumerates half of a private board's sitemap
(`isinolsun.md`).** Issue #381. Measured 2026-09-13 18:07–18:11 UTC by
the declared client, the guard on the exact path first (`*` Allow: /,
`certain: True`; the 01.09 «Request Rejected» on the rules file was not
met).

## Rules and the form

```
robots.txt                              200, 70 B — `User-agent: *` / `Allow: /` / `Disallow: /Meslek/ViewMeslekDetayPopUp.aspx/`; no Sitemap, no Crawl-delay
GET /                                   200, 71 575 B — ASP.NET WebForms («Türkiye İş Kurumu - Ana Sayfa»); links Istihdam/AcikIsIlanAra.aspx
GET /Istihdam/AcikIsIlanAra.aspx        200, 82 090 B — the form: __VIEWSTATE, __EVENTVALIDATION, ctl04$ctlIl (81 provinces + «Tüm İller»), ctl04$ctlIlce, ctl04$ctlMeslek…, ctl04$ctlCalismaYeri (Yurtiçi selected) …
POST every field + __EVENTTARGET=ctl04$ctlAcikIsPageCommand$CommandItem_Search      200, 290 220 B — «Toplam Kayıt: 34049», «/ 2270 Sayfaya Git», 15 rows
POST every field of the results + __EVENTTARGET=ctl04$ctlDataPagerDetay$btnNext     200 — page 2, txtCurrentPage=2
POST … btnChangeCurrentPage with txtCurrentPage=5                                    200 — page 5, txtCurrentPage=5
GET /Istihdam/AcikIsIlanDetay.aspx?uiID=00009806651                                   200, 33 411 B — the public detail: occupation, education bounds, «sisteme giriş yapınız» for the rest
```

**A WebForms page turns by re-posting itself**: every field a browser
would send (hidden, text, checked, each select's chosen option), the
`__EVENTTARGET`/`__EVENTARGUMENT` pair stripped from what the page
carried and set once to the button pressed. `--il` overrides the
province select before the search. No Crawl-delay; 3 s is the adapter's
own. **`--pages` defaults to 10** (150 rows) and the note says the walk
was bounded by request — 2 270 pages is not a run.

## The row — what the share button knows

```
<a class="dropdown-toggle share-toggle" data-url='http://esube.iskur.gov.tr/Istihdam/AcikIsIlanDetay.aspx?uiID=00009806651' data-ilanno='00009806651' data-sontarih='15.09.2026'
   data-il='İl Geneli Başvuru (ÇANKIRI / ŞABANÖZÜ) ' data-acikissayi='1' data-isverentur='Özel' data-calismasekli='Tam Zamanlı' data-meslekler='Beden İşçisi (Genel)'>
<span>İşyeri adını görmek için Sisteme Üye Girişi yapmanız gerekmektedir.</span>   <- where the employer's name would be
```

The adapter reads the share button's data attributes — the row's own
fields in the site's own names: id (11 digits), occupation (`title`),
employer TYPE (Özel / Kamu), work type, workplace, open positions,
application deadline (`DD.MM.YYYY`, as published). **`employer` is null
on every row and `employer_hidden` says why**: the name is shown to
members only, and the plugin never logs in. The public detail page adds
the education bounds and nothing else — the description, the employer
and the application are behind the same login (`login_required_for`).
No contact is on either page.

```
iskur.py search --il 34 --pages 2
[iskur] 30 emitted of the 3 847 the site states (il 34), 257 page(s) of 15 — 2 walked by request (--pages/--limit), not a shortfall.
[iskur] the employer's name is behind a login on every row — never read; `employer` is null on all 30.
```

## Configuration

```yaml
boards:
  iskur:
    enabled: true
    il: "34"            # a province code as the site numbers them; none = all provinces, 10 pages
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `il` | no | 1 Adana … 34 İstanbul … 81 Düzce, the site's own numbering |

No credentials, no browser, no login. `search` is 2 + pages requests at
3 s; `ad` is one.

## What is not established

- **What the login shows** — the employer's name and the description;
  a member's view is not the plugin's.
- **Whether the firewall of 01.09 («Request Rejected») returns** — not
  met on the 13th on any of nine requests; the adapter names it when a
  page comes back without a `__VIEWSTATE`.
- **The province codes beyond the four read** (1, 2, 3, 34) — the select
  carries 81; the adapter passes what it is given.
- **Whether `Yurtdışı` (abroad) postings are in the 34 049** — the form's
  default is Yurtiçi (domestic) and the adapter keeps it.

## 2026-09-13 — shipped

`search --il 34 --pages 2`: 30 of 3 847; `search --pages 1 --limit 3`:
3 of 34 049. `ad` on one. Four tests; six mutations on a detached
worktree (`python3 -B`), six red — the event pair not stripped, `btnNext`
swapped for `btnLast`, the total regex broken, the employer filled from
its type, `--il` not overriding, the `__VIEWSTATE` check dropped (inert
on the first draft of the firewall case, which failed the GET check
before the postback's; red once the form was served and the search
answered by the firewall).
