# Board measurement — rabota.by (Belarus): HeadHunter's Belarusian front, open to the client, 30 406 vacancies for `area=16` — and the unfiltered page states the network's 1 025 175

<!-- verified: 2026-09-12 -->

<!-- hosts: rabota.by, www.rabota.by -->
<!-- script: none -->
<!-- countries: BY -->
<!-- content: measured · rules read twice and certain — HeadHunter's 10 379-byte file, `claudebot` refused `/vacancy/*`, `/resume$`, `/resume?*` and nothing else, `Claude-User` not named and under `*`; `identity()` answers `claude-user`, `verdict()` sweeps — and the transport answers 200 behind `ddos-guard` at the root and at `/search/vacancy`: the page states «Найдено 1 025 175 вакансий» with no area filter (the whole hh network) and **«Найдено 30 406 вакансий» for `?area=16`, Belarus**, `totalResults: 30406` in its state, 50 per page · 2026-09-12 11:22 UTC -->
<!-- witness: the `<h1>` and the embedded `totalResults` of `/search/vacancy?area=16`, two places on one page — the same number; no second document read; no adapter yet -->

**Measured 2026-09-12 at 11:19:01Z UTC for #233, lot 4 — a measurement of
the transport, not a decision about the host.** Every fetch under the
declared identity, the guard on the exact path first, `bin/fetch-body.py`.

## The rules — HeadHunter's file, `claudebot` kept off the advertisement pages

```
robots.txt      read twice, certain: True, 10 379 B, md5 a0c1c4960a51 both times
                groups for Yandex, YandexDirect, Googlebot … with Clean-param lines; and
                `User-agent: claudebot / Disallow: /vacancy/*, /resume$, /resume?*`   <- the advertisement pages, to that name
identity("/")   http, claude-user       <- not named; falls under `*`
verdict()       sweep True — «this host refuses 3 path(s) to claudebot and not the site as a whole»
allowed("/search/vacancy") True    allowed("/search/vacancy?area=16") True    allowed("/vacancy/123") True (under claude-user)
crawl_delay     none
```

*#233 keeps this one under «written by hand». The refusal is narrow — the
advertisement pages, to `claudebot` — and the search pages are open to every
name. Under the decision of 2026-09-07 `Claude-User` is not bound by it; the
line stays «written by hand» so the owner sees what he decides about.*

## The transport — 200 behind `ddos-guard`

```
GET https://rabota.by/                          200, 1 503 670 B, md5 802e76af0a63   (11:19:01Z)  server: ddos-guard — no <title> in the served HTML
GET https://rabota.by/                          200, 1 504 914 B, md5 23c66b5ec616   (11:19:03Z)
GET https://rabota.by/search/vacancy            200, 1 342 295 B, md5 408e49663808   (11:21:15Z)  <h1>Найдено 1 025 175 вакансий</h1>, 50 /vacancy/<id> links, pages to 100
GET https://rabota.by/search/vacancy            200, 1 328 365 B, md5 64ae6a20a8dc   (11:21:17Z)
GET https://rabota.by/search/vacancy?area=16    200, 1 210 359 B, md5 34a16df1430d   (11:22:21Z)  <h1>Найдено 30 406 вакансий</h1>, totalResults 30406
```

## Two numbers on one board, and only one is Belarus

| question | answer |
| :-- | --: |
| `/search/vacancy`, no filter | **1 025 175** — HeadHunter's whole network, Russia included: *a Belarusian front over a shared store* |
| `/search/vacancy?area=16` (Belarus) | **30 406**, in the `<h1>` and in the page state's `totalResults` — one page, two places, one number |
| per page | 50 `/vacancy/<id>`; pagination offered to page 100 — **5 000 reachable per query**, the rest behind narrower filters |
| `<title>` | none served to this client — the page is a React shell with its state inlined |

**The unfiltered number is the trap**: a card that copied «1 025 175» would
have described Russia under a Belarusian flag. *`area=16` is HeadHunter's
id for Belarus; the root's own links use `area=1002` (Minsk).*

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE.
  **Candidate — and a FAMILY candidate**: `hh.ru`, `hh.kz`, `hh.uz` and this
  host are four of the 61 on #233, one stack, one `robots.txt` shape, one
  public JSON API (`api.hh.ru`, area-filtered) that this repository has not
  measured. *One adapter would be four countries; that is the pilot's call.*
- **Not a verdict on the hand-written refusal** — `/vacancy/*` is closed to
  `claudebot` by name and open to `claude-user` by silence; recorded as
  written.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
