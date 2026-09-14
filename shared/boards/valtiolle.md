# Board adapter — Valtiolle (`valtiolle.fi`, Finland): the State's own board on the municipalities' template — `kuntarekry.py --host valtiolle`, 212 counted by the site and 212 emitted, the contact person on every ad withheld

<!-- verified: 2026-09-14 -->

<!-- hosts: valtiolle.fi, www.valtiolle.fi -->
<!-- script: kuntarekry.py -->
<!-- host-forms: valtiolle.fi -->
<!-- host-forms-basis: read — `kuntarekry.py:BOARDS["valtiolle"]` is `valtiolle.fi`; the `www.` host redirects to the apex (the root read went `www.` → apex) and answers its home page to a rules request, an absence; every card link is root-relative on the apex · 2026-09-14 -->
<!-- countries: FI -->
<!-- content: measured · **«count: 212» stated by the site's own counter (`/fi/tyopaikat/?view=count&format=json`), 212 emitted over 9 pages of 24 — equal** — read by the declared client through `kuntarekry.py search --host valtiolle`, 00:59 UTC; Puolustusvoimat 16, Ulosottolaitos 14, Helsingin poliisilaitos 10, Rikosseuraamuslaitos 7 among the employers; no promoted card; the rules on the apex `*` Allow: / with two sitemaps that are HTML pages; **the same template as `kuntarekry.md` — `<job-card>`, `<ip-pagination>`, the counter, the JobPosting on the ad — and the same contact block on every ad, withheld** · 2026-09-14 -->
<!-- witness: the site's own counter, asked once per walk on the same path as the walk and printed beside the emitted count; the pager's `current`/`total` checked after every turn · 2026-09-14 -->

**Finland's State — ministries, agencies, the defence forces, the
police, the courts, the universities — recruits on Valtiolle, which
KL-Kuntarekry runs on the municipalities' template (its assets are the
same, `kuntarekry-white-1.svg` in its `<meta image>`); 212 open postings
on the day, beside the municipalities' 1 356.** Issue #372. Measured
2026-09-14 00:57–01:00 UTC by the declared client, the guard on the exact
path first (`*` Allow: / on the apex, certain).

## Rules and the pages — the municipalities' to the line

```
valtiolle.fi/robots.txt                              200 — User-agent: * / Allow: / ; Sitemap: tuotanto.valtiolle.fi/fi/sivukartta/ and /se/sitemap/ (HTML pages)
www.valtiolle.fi/robots.txt                          200 — the site's own HOME PAGE (229 KB) answered to the rules request: no rule read, an absence
GET https://www.valtiolle.fi/                        200 → https://valtiolle.fi/, 229 464 B — «Avoimet työpaikat valtiolla»
GET /fi/tyopaikat/?view=count&format=json            200 — {"count":212}
GET /fi/tyopaikat/                                   200, 244 145 B — 24 <job-card …>, 0 promoted; <ip-pagination current="1" total="9" next="/fi/tyopaikat/sivu2/">
GET /fi/tyopaikat/opetusaliupseeri-joukkueen-varajohtaja-24521/   200 — a JobPosting (Puolustusvoimat, Kirkkonummi, EUR «2 699,38 €/kk»), the text, and three telephone numbers on the page
```

**The same script reads both boards**: `--host valtiolle` puts the host
on the counter and the list, `source` and `ledger_id` carry `valtiolle`,
the card's addresses are built on `valtiolle.fi`, and `ad --url` reads
the board off the address; an unknown `--host` is refused before any
request, naming the two the script knows. `--filter` is a path the site
serves, as on the sister. No Crawl-delay; 2 s is the adapter's own; 9
pages is the whole board and `--pages` (10 by default) covers it.

```
kuntarekry.py search --host valtiolle
[kuntarekry] 212 emitted over 9 page(s), site counts 212 (valtiolle.fi) — equal.
```

The record and the ad are the sister's (`kuntarekry.md`): title, hiring
unit, publication, deadline with its time, key, id; the JobPosting with
the salary as free text in EUR (`salary_text`, never a number), the
sections; **the contact person's block not read, the description and
the salary line scrubbed of e-mail addresses and Finnish telephone
numbers** — «Tiedustelut 0299 326200» leaves as «[telephone withheld]».

## Configuration

```yaml
boards:
  valtiolle:
    enabled: true
    host: valtiolle        # the board key `kuntarekry.py` takes; the municipalities are the default
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `host` | yes | `valtiolle` |
| `filter` | no | a path the site serves |

No credentials, no browser, no login. `search` is 1 + pages requests at
2 s (10 on the day); `ad` is one.

## What is not established

- **Whether Työmarkkinatori re-lists the State's postings** — the
  national service (#371) is under the user's own key; overlap not
  measured.
- **`tuotanto.valtiolle.fi`** — the sitemaps' host, an HTML page map;
  not a job sitemap and not read by the adapter.
- **The Swedish route** (`/se/`) — the same site; the adapter reads
  Finnish.

## 2026-09-14 — shipped

`search --host valtiolle`: 212 of 212, equal; `ad` on one, no number in
the output; `--host kela` refused. Two tests for the host, the sister's
four still green (their notes name the host now); six mutations on a
detached worktree (`python3 -B`), six red — the host not on the counter,
the host not on the list, the key not on the record, the card's address
on the default host, the board not read off the ad's address, the
unknown host accepted.
