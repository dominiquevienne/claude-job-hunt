# Board measurement — rabota.by (Belarus): HeadHunter's Belarusian front, open to the client, 30 406 vacancies for `area=16` — and the unfiltered page states the network's 1 025 175

<!-- verified: 2026-09-12 -->

<!-- hosts: rabota.by, www.rabota.by -->
<!-- script: none -->
<!-- countries: BY -->
<!-- content: measured · rules read twice and certain — HeadHunter's 10 379-byte file, `claudebot` refused `/vacancy/*`, `/resume$`, `/resume?*` and nothing else, `Claude-User` not named and under `*`; `identity()` answers `claude-user`, `verdict()` sweeps — and the transport answers 200 behind `ddos-guard` at the root and at `/search/vacancy`: the page states «Найдено 1 025 175 вакансий» with no area filter (the whole hh network) and **«Найдено 30 406 вакансий» for `?area=16`, Belarus**, `totalResults: 30406` in its state, 50 per page · 2026-09-12 11:22 UTC -->
<!-- witness: the `<h1>` and the embedded `totalResults` of `/search/vacancy?area=16`, two places on one page — the same number; no second document read; no adapter yet -->
<!-- route: none · non faisable — exclu par le propriétaire le 14.09.2026, qui a nommé ce board dans sa décision d'exclure le RÉSEAU hh ENTIER (#337 : `hh.ru`, `hh.kz`, `hh.uz`, **`rabota.by`**, `zarplata.ru`), « ne plus les proposer, ne plus remesurer » — validation §2 sexies ACQUISE le jour même : la décision consignée dit « Exclus, validés § 2 sexies … fiches à passer en “non faisable — validé par le propriétaire le 14.09.2026” par `cd` », et cette fiche est la SEULE des six boards exclus qui ne l'ait jamais reçu — 6 sur 7 portent la phrase, celle-ci ZERO. NON ÉTABLI, et déclaré : quel item numéroté porte ce board. Le verbatim des six est « 1, 2, 3, 4, 5 => exclue » · « 10. exclue », la liste « points en attente » à laquelle il répond n'est conservée nulle part, et le dépôt se contredit lui-même dessus — `hh.md` cite « 7. ok », les cinq autres « 1, 2, 3, 4, 5 => exclue ». AUCUNE MESURE NEUVE : ce board n'a pas été interrogé pour cette écriture, et il ne doit plus l'être · 2026-11-03 -->

**Measured 2026-09-12 at 11:19:01Z UTC for #233, lot 4 — a measurement of
the transport, not a decision about the host.** Every fetch under the
declared identity, the guard on the exact path first, `bin/fetch-body.py`.

## The rules — HeadHunter's file, `claudebot` kept off the advertisement pages

```
robots.txt      read twice, certain: True, 10 379 B, md5 a0c1c4960a51 both times
Crawl-delay     **none readable** — `rabota.by/robots.txt` answered **403** on 2026-11-02, so `state: no-rules`, and #283 makes that an ABSENCE of rules (`certain: False` today): there is no directive to record. The 10 379 B / a0c1c4960a51 above is the 2026-09 reading, which the card keeps because a correction cites what it corrects. **ONE reading, and it should have been ZERO: this host is named VERBATIM in the owner's 2026-09-14 exclusion of the whole hh network (#337, « ne plus remesurer »), and I checked that list AFTER reading instead of before** (#907)
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
- **ET LA PUCE CI-DESSUS EST CADUQUE DEPUIS LE 14.09.2026, CITÉE ET NON RÉÉCRITE (§4) : elle
  INVITE à construire ce que le propriétaire a exclu DEUX JOURS après qu'elle a été écrite.**
  *Mesurée le 12.09, exclue le 14.09 — #337, le réseau hh ENTIER, « ne plus les proposer, ne
  plus remesurer ». **Un artefact figé porte la règle qui l'a écrit**, et ce n'est pas ici une
  interdiction périmée, qui ferait se RETIRER : c'est une INVITATION périmée, qui fait AGIR —
  la plus chère des trois directions.* **Et son symptôme a été l'absence de symptôme pendant
  cinquante jours : rien ne devient faux le jour d'un renversement.** *Ce qui l'a rendue
  visible est `country-boards.py`, qui a porté la Biélorussie au rang 1 des pays à zéro
  adaptateur — son unique entrée « à construire » étant cet hôte exclu. L'outil lit `script:
  none` et il a raison ; ce qu'il ne pouvait pas lire est qu'un hôte EXCLU n'est pas une
  entrée à construire, et la prose de cette fiche ne se déclare pas : une exclusion est une
  DÉCLARATION, jamais une INTERPRÉTATION (#1136).*
- **Not a verdict on the hand-written refusal** — `/vacancy/*` is closed to
  `claudebot` by name and open to `claude-user` by silence; recorded as
  written.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
