# Board adapter — Tecnoempleo (Spain): six Anthropic agents refused by hand and not this one, 2 145 offers in the sitemap against a stated 2 592, and an identifier that names the employer

<!-- verified: 2026-09-13 -->

<!-- hosts: www.tecnoempleo.com, tecnoempleo.com -->
<!-- script: tecnoempleo.py -->
<!-- countries: ES -->
<!-- content: measured · rules read twice and certain (953 B, written by hand: `AnthropicBot`, `Claude`, `ClaudeBot`, `anthropic-ai`, `Claude-Web`, `Claude-SearchBot` refused everything, `Claude-User` not named and under `*`, which refuses 17 paths of its own and none of the offers; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200: `/sitemap.xml` (2 931 262 B) holds 30 891 `<loc>` of which 2 145 are offers (`/<slug>/<skills>/rf-<hash>`, 2 145 distinct, 234 distinct real `<lastmod>`), `/ofertas-trabajo/` states «2.592 Ofertas» — «2 145 emitted, site states 2 592 — 447 short» on 2026-09-13 10:55 UTC; a `JobPosting` JSON-LD on the offer page, `addressCountry: ES` · 2026-09-13 -->
<!-- witness: the listing's own «2.592 Ofertas de Trabajo…» and «1-30 de 2.592», parsed past the Spanish thousands dot and printed beside the sitemap's distinct count — «447 short» on the day: two views of one store, neither copied as the size -->

**Shipped 2026-09-13 — under the doctrine of 2026-09-07 and with a
reservation recorded for the owner.** The rules file names six Anthropic
agents and closes the whole site to them; `Claude-User` is not among them,
and the owner's decision (against the pilot's advice, «not replayed») says a
group that names one token does not bind the other — #233's body: the
hand-written files are measured like the others; the pilot told the owner
on 2026-09-12 and again on 2026-09-13, with no refusal. **The reservation,
once: a file that lists six Anthropic names reads as an intention toward
Anthropic, and the seventh name's absence may be an omission rather than a
permission. It is the owner's to weigh; this card keeps the six names.**
The `*` refusals — statistics, images, policies, the candidate area, ajax,
matomo, the RSS alert, `/accesoempresa.php` — are honoured by the guard on
every URL, and the adapter asks for nothing under them.

```
python3 skills/job-scan/scripts/tecnoempleo.py sitemap [--limit N] [--no-site-total]   # 1 request (2.9 MB), 2 with the listing's count
python3 skills/job-scan/scripts/tecnoempleo.py ad --url https://www.tecnoempleo.com/<slug>/<skills>/rf-<hash>
```

## The rules — written by hand, and 2 592 offers behind them

```
robots.txt      read twice, certain: True, 953 B, md5 12f0291e9890 both times — WRITTEN BY HAND:
                `User-agent: * / Disallow: /graficos_estadisticas/, /imagenes/, /politicas/, /profesionales/, /marco*.php, /politica*.php, /validacion_enviar.php, /amp/*.mpt, /graficos/amp/, /_ajax/select_ajax.php, /assets5/fonts/flaticon/, /matomo/, /alertas-empleo-rss.php, /demanda-trabajo-informatica.php?, /accesoempresa.php`
                `User-agent: AnthropicBot / Claude / ClaudeBot / anthropic-ai / Claude-Web / Claude-SearchBot — Disallow: /`   <- six Anthropic names, the whole site; also yacybot, emsi_bot, GPTBot
                `User-agent: Bingbot / Crawl-delay: 5`      `Sitemap: https://www.tecnoempleo.com/sitemap.xml`
identity("/")   http, claude-user      <- not named; the group that names ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user
allowed()       True on `/`, `/ofertas-trabajo/`, `/sitemap.xml`, `/<slug>/<skills>/rf-<hash>`; False on `/profesionales/x`, `/matomo/x`
crawl_delay     none for us (Bingbot gets 5) — 2 s is ours
```

## The transport — 200, and the site is served

```
GET https://www.tecnoempleo.com/                     200, 75 025 B     (10:22:17Z; 75 027 B at 10:22:19Z)  «tecnoempleo - Portal de Empleo en Informática y Telecomunicaciones»
GET https://www.tecnoempleo.com/ofertas-trabajo/     200, 168 175 B    (10:23:25Z, and the same size at 10:23:27Z)  «2.592 Ofertas de Trabajo…», «1-30 de 2.592», 30 a page, pager to «siguiente»
GET https://www.tecnoempleo.com/sitemap.xml          200, 2 931 262 B  (10:52:48Z)  one urlset, 30 891 <loc>
GET https://www.tecnoempleo.com/…/rf-ffe41cf10288133e9f4d   200, 74 500 B   (10:52:49Z)  JobPosting JSON-LD — Michael Page, Madrid
```

## The sitemap and the listing — two views of one store

| question | answer |
| :-- | --: |
| `<loc>` in `/sitemap.xml` | **30 891** — one `urlset`, no index |
| of the offer shape `/<slug>/<skills>/rf-<hash>` | **2 145** (2 146 at 10:52, 2 145 at 10:55 — a live board), 2 145 distinct hashes |
| the rest | company pages (`/<company>-trabajo`), site pages |
| `<lastmod>` on the offers | **234 distinct dates** (1 066 of 2 146 on the day of the read at 10:52) — real dates, and the adapter says so each run |
| offers stated | **2 592** — «2.592 Ofertas de Trabajo en Informática y Telecomunicaciones», «1-30 de 2.592», a Spanish thousands dot parsed |
| the gap | **447** — «2 145 emitted, site states 2 592 — 447 short» on 2026-09-13 10:55 UTC: the listing counts more than the sitemap lists; which offers the sitemap omits (the oldest? the unpaid?) is the next question, not this card's |

## What an offer carries — and whose id the `identifier` is

`JobPosting` JSON-LD with `title`, `description`, `datePosted`,
`employmentType` (`FULL_TIME`), `directApply`, `hiringOrganization.name`,
`jobLocation.address` (`addressLocality`, `addressRegion`,
`addressCountry: ES`); **no `baseSalary`, no `validThrough`** on the pages
read. **`identifier.value` is the EMPLOYER's id — `206974` for Atos,
`160827` for Michael Page, the number of the logo file** — not the offer's,
whose key is the `rf-` hash in the URL; the adapter keeps them apart
(`employer_id`, `id`), the test asserts it. The only `tel:` on the page is
the board's own; nothing of a recruiter's contacts is read.

## What this card is, and is not

- **An adapter, shipped** — `sitemap` for the enumeration with the stated
  count as the check, `ad` for one offer from its JSON-LD. No key, no
  browser; two requests for the enumeration.
- **The six names are recorded as written, and the reservation once** —
  the owner decides; nothing here is a verdict on the file.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
