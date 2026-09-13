# Board measurement — OLX Poland (`www.olx.pl`, Poland): 403 to the declared client, served to a browser — «ponad 1000 ogłoszeń» on a listing capped at 25 pages, 83 725 across 40 categories

<!-- verified: 2026-09-13 -->

<!-- hosts: www.olx.pl, olx.pl -->
<!-- script: none -->
<!-- countries: PL -->
<!-- content: measured · **a browser tab is served — `/praca/` 200, 52 advertisement links a page, the page states «Znaleźliśmy ponad 1000 ogłoszeń» (a floor, not a count) and its pager stops at 25 (page 26 redirects to page 1); the 40 top-level category links on the same page carry counts summing to 83 725 — a sum of categories, an upper bound, not the board's size**; the declared client gets a 403 (919 B, md5 moving) on the same path; tab 16:27 UTC · 2026-09-13 -->
<!-- witness: the page's own «ponad 1000» and pager (25 × 52), read on the page and on page 25 and 26 by `fetch()`; the category counts are the site's own per-category figures, summed here — a bound · 2026-09-13 -->
<!-- route: browser · 1000 · 2026-09-13 -->
**In the #222 candidate list from the Poland country page as a «403
to the plain client, browser not measured».** *A measurement and not an
adapter, and a short one: the guard closed the question at the rules
file, the same shape as `kazibongo.md` and `barbadosjobregister.md`.*
Measured 2026-09-13 12:19:44 UTC with the declared client.

## The rules file is refused — twice

```
GET https://www.olx.pl/robots.txt     403 · CloudFront («Error from cloudfront») · 12:19:44 UTC   (bin/fetch-body.py, body not kept by the tool)
GET https://www.olx.pl/robots.txt     403 · the same, 2 s later
_robots.allowed('www.olx.pl', '/')    allowed False · certain True · rule "/" · rule_kind host-closed
```

**A `403` on the rules file is a refusal, and the doctrine keeps it one**
(the 2026-09-09 decision reopened `401` alone). No path is open, so the
browser branch — «the rules open, the transport refuses» — has nothing to
start from: **nothing beyond the rules file was requested, no tab was
opened.** *A refusal at the rules does not say what it refuses — a front
rule on `/robots.txt`, a firewall keyed on our identity, or a host that
serves no rules to anyone look the same from here.*

## What reopens it

- `robots.txt` answering anything but 403 to the declared client;
- a later pair of reads minutes apart (`grabjobs.co` once cleared within
  seconds — `robots-policy.md`);
- a doctrine decision on a 403 *at the rules file* — posed by
  `kazibongo.md`, `barbadosjobregister.md` and this card, not decided by
  them. **Eleven hosts now sit on that question.**

## What this card does not say

Nothing about what the site serves, its size, or whether a browser is
served — a browser was not opened.

## 2026-09-13 — #283: an unread rules file is an absence of rules, and the transport measured

**Owner's decision of 2026-09-13, verbatim: «toutes incapacité d'ouvrir robots.txt
doit aboutir à l'absence de règles et donc à l'ouverture».** This card read
«route: none — CloudFront (13.09)» — a verdict taken on the rules file alone. Since #283 the 403 on
`/robots.txt` is `no-rules-403`, `allowed: True, certain: False`: nothing
was read, nothing forbids, and **the transport decides**. Measured with
`bin/fetch-body.py --allow-refusal` under the new guard, the root (and a
listing path where one was known) twice:

```
GET https://www.olx.pl/                                  403, 919 B, md5 28e3167e761b   (15:29:54Z)
GET https://www.olx.pl/                                  403, 919 B, md5 19b58ef54879   (15:29:55Z)
GET https://www.olx.pl/praca/                            403, 919 B, md5 398f926a069c   (15:29:56Z)
GET https://www.olx.pl/praca/                            403, 919 B, md5 083dadd614fd   (15:29:57Z)
```

**The transport answers a **static 403** — the same bytes on every fetch: a refusal at the transport aimed at the client, family (1) of #222, where a browser is legitimate and is not measured here.** *A verdict of closure was never
this card's to give (§2 sexies); what it gives now is a dated transport
reading, and the class it falls in.*

## 2026-09-13 16:27 UTC — the browser route, MEASURED (#222): served, capped, counted by category

```
tab: /praca/                       200 «Oferty pracy … | OLX Praca» — no challenge; 52 /oferta/ links; JSON-LD WebPage + BreadcrumbList (no ItemList, no JobPosting on the listing)
                                   «Znaleźliśmy ponad 1000 ogłoszeń» — MORE THAN 1 000: a floor the site prints on every capped listing
                                   pager … ?page=25 (last link)
tab: fetch /praca/?page=25         200, 52 links      ·  ?page=26  → redirected to /praca/ (the cap, not an end)
tab: 40 top-level categories with a count each — Kierowca 10 621 · Produkcja 10 628 · Budowa / remonty 8 198 · Gastronomia 7 509 · Sprzedaż 5 862 · Pracownik sklepu 5 216 · Prace magazynowe 4 640 … Badania i rozwój 42 · Prawo 48   → **83 725 summed**
                                   (five further links — Praktyki / staże, Kadra kierownicza, Praca sezonowa, Zapraszamy seniorów, Praca dodatkowa — are cross-cutting tags, not categories; not summed)
```

**The 403 is for the declared client alone**: the tab is served, no
challenge, nothing asked of anyone. **What the site states is a floor
(«ponad 1000») and forty per-category figures**; the listing itself shows
25 pages of ~52 and loops — so a full enumeration by browser goes category
by category, each capped at 1 000 visible, and **ten categories are above
1 000** (Kierowca, Produkcja, Budowa, Gastronomia, Sprzedaż, Pracownik
sklepu, Prace magazynowe, Montaż i serwis, Sprzątanie, Praca za granicą,
Administracja biurowa, Edukacja …) — the route reaches at most 1 000 of
each. The route figure is the listing's own 1 000; **83 725 is the sum of
what the site says per category — a bound on the board, not a count of
what the route can read.** *`ASumOfCategoriesIsAnUpperBoundNotTheBoardsSize`
is the guard this sentence exists for.*

**The JSON API the page itself calls (`/api/v1/offers/`) was not tried**
— it is the same search under another path, and the rules file could not
be read to say whether it is refused; a reader who establishes that the
API answers the declared client has an HTTP route and opens its `adapter`
issue (#291).
