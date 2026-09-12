# Board measurement — nea.gov.kh (Cambodia): rules open to us, the vendor default at the door, a browser served — the only host of its country

<!-- verified: 2026-09-12 -->

<!-- hosts: nea.gov.kh, www.nea.gov.kh -->
<!-- script: none -->
<!-- countries: KH -->
<!-- content: measured · **100 vacancies** on `/vacancy/popularVacancy.do` from a connected browser tab (100 distinct 32-hex `condSeq` ids, no pager — a round number, a cap as much as a count; their headcount sums to 8 053), while the site's own vacancy search answered «ទាំងអស់ : 0» and an in-page «page not found» to a blank query; the site states «90,639» as *workers to be recruited*, a headcount aggregate and not a vacancy count · 2026-09-12 -->
<!-- witness: the site's «ចំនួនកម្លាំងពលកម្មត្រូវជ្រើសរើស : 90,639» — a headcount figure on every page, not comparable to the 100 rows (which sum to 8 053 heads); the search that would state a vacancy total is broken on the day, so no page states one · 2026-09-12 -->

**This card is a measurement and not an adapter.** *No card declared `KH`
before it. The host is Cambodia's National Employment Agency — the public
employment service — and the repository knew it only as the example of «access
without intention» in `shared/robots-policy.md` (2026-09-08).* **This card
sorts the refusal, and the sort puts it on #222.**

## Step one — the rules, twice, on both hosts

*Measured 2026-09-11 13:40 UTC.*

```
https://nea.gov.kh/robots.txt        200   1 836 o   md5 c6370d4bc02563e4b1e1af4540d1e670   twice
https://www.nea.gov.kh/robots.txt    200   1 836 o   md5 c6370d4bc02563e4b1e1af4540d1e670   twice — the same file
```

**Cloudflare's managed content-signals template, identical on both forms**:
`User-agent: *` → `Content-Signal: search=yes,ai-train=no,use=reference`,
`Allow: /`; then named refusals — `Amazonbot`, `Applebot-Extended`,
`Bytespider`, `CCBot`, **`ClaudeBot`**, `CloudflareBrowserRenderingCrawler`,
`Google-Extended`, `GPTBot`, `meta-externalagent`, each `Disallow: /`.
**`Claude-User` is not named.**

**The guard's verdict, on the exact path `/`, both hosts:** `allowed: True,
rule: None, certain: True` — *«no `Disallow` matches this path in `*`»*.
**That is the 07.09 decision applied: a refusal that names `ClaudeBot` does not
bind `Claude-User`, the token this plugin declares.** *The policy's own
paragraph on this host — that the template is identical on three continents
and nobody here decided anything — still holds: the file is the vendor's, the
`ClaudeBot` line included.*

## Step two — the transport, twice per host, and the fingerprint

```
https://nea.gov.kh/         403   25 o   md5 9ccabba20b9f4ec7d18bd6644579e5bf   ×2, identical   "Your request was blocked."
https://www.nea.gov.kh/     403   25 o   md5 9ccabba20b9f4ec7d18bd6644579e5bf   ×2, identical
```

**That is the vendor default of family (1) — the twelfth host on that
fingerprint**, after `hiringcafe.com`, `www.jobstore.com`, `www.hays.fr`,
`iqjscout.com`, `eshjob.com`, `www.iraqhire.com`, `www.tala-com.com`,
`kariera.mk`, `sptojobslink.com`, `northcyprus.cv`, `jobs.af`. *Stable across
two reads on each of two hosts: not a challenge, a static refusal to a client
the infrastructure does not recognise.*

> **Rules open, transport refuses, fingerprint stable → the browser route is
> the candidate (doctrine of 07.09), and the route is an adapter in the sense
> of the 08.09 decision.** *Bound 0 is settled by the shared fingerprint:
> eleven unrelated operators do not write the same 25 bytes.*

**So this host goes to #222** — the objects waiting for the Chrome extension —
**with the priority `shared/false-zero-cost.md` gives the only host of a
country**: Cambodia has no other card, and the National Employment Agency is
the one public listing the country publishes.

## 2026-09-12 — the browser route, MEASURED (#222): the door opens, the search behind it is broken, and one list of 100 is served

**11:57–12:02 UTC, Claude in Chrome connected, one tab.** Guard first, on
both hosts and the exact paths — `/`, `/vacancy/index.do`,
`/vacancy/dtlSearch.do`, `/vacancy/popularVacancy.do`: `allowed True,
certain True` (the `*` group grants). **The 25-byte 403 goes to the declared
HTTP client and to nobody else**: the tab was served every page, with no
challenge and no interstitial — borne 0 held, borne 2 never engaged.

```
navigate https://www.nea.gov.kh/            -> /index.do, «CPES», Khmer; a Java web app (*.do)
                                              «ព័ត៌មានឱកាសការងារ 90,639 កន្លែង» — 90 639 *positions* (headcount), the only figure the site states
GET /vacancy/index.do                       the vacancy section: two forms, both POST /vacancy/dtlSearch.do (frmSearch: condDiv, condAreaCd, condCateCD, condText;
                                              frmDtlSearch: ISCO levels, area, vacancy type, salary, contract, education) — and a «new jobs» strip of 16
fnSearch() — the page's own blank search   -> POST /vacancy/dtlSearch.do:
                                              «ទាំងអស់ : 0 / ចំនួនកម្លាំងពលកម្មត្រូវជ្រើសរើស : 90,639 / ថ្មីថ្ងៃនេះ : 0»  (all: 0 · workers to recruit: 90 639 · new today: 0)
                                              and, in the results pane, the site's own «Sorry, the page you requested was not found.»
GET /vacancy/dtlSearch.do                   the same — the results pane is the not-found page either way
GET /vacancy/popularVacancy.do              «ការងារពេញនិយមថ្ងៃនេះ» (popular jobs today): **100 rows, 100 distinct condSeq (32 hex), no pager**
                                              each row: employer · title · full-time · «workers to recruit : N» · province · $min ~ $max · days left
                                              N sums to 8 053 over the 100; 9 rows carry no salary ($ ~ $ or $0 ~ $0); 25 provinces in the filter
GET /vacancy/popularVacancyView.do?condSeq=e845610fab2b11f1a66df40270d29e0d
                                              the full record: LOLC (Cambodia) Plc · Deposit and Digital Banking Management Manager · 1 head · Phnom Penh
                                              recruitment period 08/09/2026 ~ 18/09/2026 · contract indefinite, written · $230 ~ $500 / month · bachelor · 1 year
                                              English (high) · sector microfinance · company address and site · description (English) · apply by e-mail / phone
```

**The vacancy search — the route a candidate would use — is broken on the
day**: a blank query returns *all: 0* and the site's own not-found page in
the results pane, by the site's own `fnSearch()` and by a direct GET alike.
*«All: 0» is the dangerous half: a zero from a search that could not run.*
**What is served is the «popular jobs today» list**: exactly 100 rows, no
pager, so a cap as much as a count — *the floor is 100 vacancies live on
the day, the ceiling is not stated by any page.* **The 90 639 is a
headcount** («workers to be recruited»), on every page and in every state
of the search; it is not comparable to a count of vacancies, and the 100
rows account for 8 053 of it.

**The procedure a session follows — this is the adapter, at the same title
as a script (decision of 2026-09-08):**

1. guard both hosts on `/vacancy/popularVacancy.do` and
   `/vacancy/popularVacancyView.do` before anything;
2. `navigate https://www.nea.gov.kh/vacancy/popularVacancy.do` in the
   session's own tab; wait for the list;
3. read the 100 rows: the `condSeq` in each row's
   `fnPopularVacancyView('<32 hex>', …)` is the stable id; employer, title,
   headcount, province, salary range and days-left are the row's text;
   print **«n rows, 100 is the page's cap — the site states no vacancy
   total; its 90 639 is a headcount»**, never a bare 100;
4. one record: `navigate …/vacancy/popularVacancyView.do?condSeq=<id>`
   (a GET, the URL the site's own form lands on) — fields above, the
   description in the employer's language, the application e-mail and
   phone the employer published;
5. try the blank search once (`fnSearch()` on `/vacancy/index.do`) and
   record whether it still answers *all: 0 / not found* — the day it works,
   the inventory is behind it and this list is a subset;
6. close the tab.

## What this card does not say

Nothing about what the site serves — its size, its fields, whether the
listing is server-rendered — because nothing past the door was read. **The
08.09 sentence «blocks access while expressing no intention at all» is
confirmed on the transport and refined on the rules: the `*` group grants,
and the only refusal that names us names the other token.**
