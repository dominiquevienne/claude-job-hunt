# Board adapter — Hello Work (`www.hellowork.mhlw.go.jp`, Japan): the public employment service's own search form, walked by its fields — 1 082 197 stated, a filter at a time, no contact ever emitted

<!-- verified: 2026-09-13 -->

<!-- hosts: www.hellowork.mhlw.go.jp, hellowork.mhlw.go.jp -->
<!-- script: hellowork_jp.py -->
<!-- host-forms: www.hellowork.mhlw.go.jp -->
<!-- host-forms-basis: read — `hellowork_jp.py:HOST`, a single literal; every address the site writes carries `www.` (the root's links, the detail addresses) · 2026-09-13 -->
<!-- countries: JP -->
<!-- content: measured · **«検索結果 1082197件» stated by the site for 一般 (general) with no filter, 30 cards a page** — read by the declared client through the form's own POST, 17:04 UTC; a Tokyo filter (`todohukenHidden=13`) states 102 981; Tokyo + «ｐｙｔｈｏｎ» states 33 and **`hellowork_jp.py search --pref 13 --word python` emitted 33 over 2 pages — equal** (17:14 UTC); no rules file (404 — an absence, a knowledge), no Crawl-delay, 3 s is the adapter's own; not `hellowork.com`, the French board of `hellowork.py` · 2026-09-13 -->
<!-- witness: the page's own «検索結果 N件 中 a～b件», read on every page of every walk and printed beside the emitted count («33 emitted over 2 page(s), site states 33 — equal»); a bounded walk says so and is never «short»; the whole inventory is never walked (36 000 pages of 30) · 2026-09-13 -->

**Japan's public employment service — the largest inventory of the
country, 1 082 197 general postings on the day, and the first public
board of the four Japanese adapters (the others are private: Mynavi,
type, Green, en-japan).** Issue #304. Measured 2026-09-13 17:03–17:15 UTC,
every request by the declared client, the guard on the exact URL first
(no rules file: `allowed()` → True, `certain: True`, kind absence).

## Rules — none, and a form that refuses a doubled field

```
robots.txt                                   404 — an absence of rules: nothing is refused, nothing is asked (Crawl-delay none)
GET /                                        200, 28 523 B — links /kensaku/GECA110010.do?action=initDisp&screenId=GECA110010 (求人検索), GECA150010 (新卒), GECA160010
GET /kensaku/GECA110010.do                   200, 5 037 B — «システムエラー»: the bare address without the query is the site's system-error page
GET …?action=initDisp&screenId=GECA110010    200, 112 891 B — the form (370 inputs), a JSESSIONID
POST hidden fields + kjKbnRadioBtn=1 + searchBtn + action=searchBtn + screenId    200, 278 361 B — «検索結果 1082197件 中 1～30件», 30 cards, pager fwListNaviBtn1…7
POST the whole results form + fwListNaviBtn2 + action=fwListNaviBtn2               200 — «31～60», fwListNowPage=2
```

**Three ways to get the error page, each found by getting it**: the
bare `.do` without its query; a first search that carries the form's
own hidden `action`/`screenId` AND the appended ones (a doubled field —
17:09 UTC); a page request with `screenId` appended to a form that
already carries one (17:11 UTC). The first search **replaces** the two,
the page request **appends only the button and its action**. And the
free word must be full-width («全角50文字以内»): `--word python` is sent
as «ｐｙｔｈｏｎ» and the note says so; ASCII answers «入力エラーがあります».

## The walk — filters, pages, and what the count is

```
hellowork_jp.py search --pref 13 --word python --pages 3
[hellowork-jp] free word sent full-width, as the form requires: «ｐｙｔｈｏｎ»
[hellowork-jp] 33 emitted over 2 page(s), site states 33 (一般, pref 13, «ｐｙｔｈｏｎ») — equal.
```

`--pref` takes JIS prefecture codes (13 Tokyo, 27 Osaka; up to three,
comma-separated — the form's own limit); `--word` the free word; `--kind`
the 求人区分 (1 一般, the default). **`--pages` defaults to 10** (300
cards) and the note says «walked by request, not a shortfall»; the
1 082 197 are never walked — 36 000 pages is not a run. The stated count
is the site's for that filter, read on every page.

**The 求人番号 is the id** (`NNNNN-NNNNNNNN`), and **its first five digits
are the registering office, not the workplace**: a Tokyo search returns
ids from the 04 (Miyagi), 09, 11 offices whose 就業場所 is Tokyo — the
adapter emits `registering_office` beside `workplace` so the two are never
read as one.

## The card and the detail — and what never leaves

The card: 受付年月日, 紹介期限日, the employment labels (正社員 / 有期雇用 /
フル / パート …), 職種 (title), 仕事の内容 (an excerpt), 事業所名, 就業場所,
賃金 (a yen range; **no period on the card** — 月額 is the site's
convention, and «read as» is not «stated»: `salary_unit: null,
salary_unit_stated: false`), 就業時間, 休日, 求人数.

The detail (`ad --url <詳細を表示 address> --pref … --word …`): 82 rows
under `<th scope="row">` — session-bound, so the search that listed it is
re-issued first. **Contact rows are dropped before anything is printed
and their labels listed** (`contact_dropped`): 所在地, 電話, ＦＡＸ, メール,
担当者, 郵便番号, 法人番号, 役職／代表者名, 事業所番号. The detail's 就業場所
is a street address with a postal code; it is cut to prefecture + city,
the listing's own granularity. Read in full on one (`13040-28009562`, 73
rows kept, 5 dropped).

## Configuration

```yaml
boards:
  hellowork_jp:
    enabled: true
    pref: "13"          # JIS code(s); the walk is a filter, never the whole
    word: ""            # optional
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `pref` | no | one to three JIS codes; none = the whole country, 10 pages |
| `word` | no | sent full-width |

No credentials, no browser. `search` is 2 + pages requests at 3 s; `ad`
is 3 (session, search, detail).

## What is not established

- **The 表示件数 50** — the form offers 50 a page; 30 is the default the
  adapter keeps.
- **The other 求人区分** (新卒・既卒 lives on `GECA150010`, a second form)
  — not read.
- **How long a session lives**, and whether the site paces — 14 requests
  in eight minutes were answered; the error page carries the word
  «混雑» (congestion) and was seen only on malformed requests.
- **Whether the detail can be opened without its search** — not tried;
  the adapter re-issues the search.

## 2026-09-13 — shipped

`hellowork_jp.py search --pref 13 --word python --pages 3`: 33 over 2
pages, site states 33 — equal. `ad` on one. Three tests; six mutations
on a detached worktree (`python3 -B`), six red — `screenId` appended on
the page request, the free word sent as typed, the count regex broken,
the contact drop list emptied, the system-error test dropped, the form's
own `action` kept on the first search.
