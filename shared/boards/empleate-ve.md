# Board measurement — Empléate (`www.empleate.com`, Venezuela): served on 13.09, refused on 16.09 to the declared client AND to a connected tab by an AWS WAF, the sitemap served — 1 632 dated advertisement URLs; no script yet, the day decides

<!-- verified: 2026-09-16 -->

<!-- hosts: www.empleate.com -->
<!-- script: none -->
<!-- countries: VE -->
<!-- content: indeterminate · **the rules open (`User-agent: *` … `Allow: /`, four paths refused — `/cgi-bin/`, `/tmp/`, `/ofertas/compartir_email/*`, `/denunciar/*` — and `Sitemap: https://www.empleate.com/sitemap.xml`); the root was SERVED to the declared client on 2026-09-13 19:50 UTC (200, 108 309 then 108 167 B, «2429 vacantes de empleo», 17 distinct ad links `/venezuela/ofertas/empleo/<id>/<title>/<place>/`, the area lists `/venezuela/ofertas/empleos_encontrados/1/trabajos-en-venezuela-en-el-area-de-<area>`) and REFUSED on 2026-09-16 05:54 UTC — `server: awselb/2.0`, 403, 118 B, md5 `bad2e8579dcd` stable on two reads, on `/`, `/venezuela/`, the list and an ad; a connected tab got «403 Forbidden» too, two readings 30 s apart; `curl/8.7.1` on the same URL got 200 and a bare `Mozilla/5.0` got 405 «Human Verification» (an AWS WAF challenge) — the WAF sorts by client shape, and neither the plugin's identity nor a real browser passes today; the sitemap IS served to the declared client: 1 679 `<loc>` with `<lastmod>` (2026-08-17 … 2026-09-15), 1 632 of them `/venezuela/ofertas/empleo/<id>/…` — the inventory, short of the «2429» the root stated three days earlier** · 2026-09-16 -->
<!-- witness: the sitemap · 1 632 advertisement URLs with lastmod, `Claude-User` served, 409 939 B, md5 `d12d3a0b3359` · 2026-09-16 -->

**Issue #426 (opened under #418, Venezuela never searched). Measured
2026-09-16 05:54–05:58 UTC, after the 13.09 reading that opened the
issue.** The script's name is settled by the issue — `empleate_ve.py`, since
`empleate.py` is the Spanish SEPE — and it is not written: **the day the
list and the ad are served to the declared client, the adapter is a
sitemap walk plus an ad read; the day they are not, it emits the sitemap
alone.** Today is the second kind of day, and a first-of-kind adapter is
not written against a body nobody has.

## What the client gets, dated — and the 2×2 that says it is the WAF's sort, not a burst

```
2026-09-13 19:50Z  GET /  → /venezuela/          200, 108 309 B   «2429 vacantes de empleo», ad cards (title | employer | place), area lists   fetch-body, Claude-User
2026-09-16 05:54Z  GET /venezuela/                403, 118 B, md5 bad2e8579dcd ×2, server awselb/2.0                                    fetch-body, Claude-User
2026-09-16 05:54Z  GET /                          403, same body
2026-09-16 05:54Z  GET /venezuela/ofertas/empleos_encontrados/     403, same body
2026-09-16 05:55Z  GET /venezuela/ofertas/empleo/1995679/…/        403, same body — the ad
2026-09-16 05:54Z  GET /sitemap.xml               200, 409 939 B — 1 679 <loc>, 1 632 ads, lastmod 2026-08-17 … 2026-09-15
2026-09-16 05:56Z  tab, /venezuela/                                «403 Forbidden», two readings 30 s apart
2026-09-16 05:57Z  tab, /venezuela/ofertas/empleos_encontrados/    «403 Forbidden»
```

**One URL, one client (`curl`), six identities, one second apart — only
the identity varies (2026-09-16 05:55:46Z):**

```
200  110 774 B   curl/8.7.1
403      118 B   Mozilla/5.0 (compatible; Claude-User; claude-job-hunt/1.233.0; +https://github.com/…)   ← the plugin's identity
403      118 B   Mozilla/5.0 (compatible; test; +https://example.org)                                       ← any «(compatible; …; +url)» shape
405    2 523 B   Mozilla/5.0                                    «Human Verification», window.awsWafCookieDomainList — the AWS WAF challenge
405    2 523 B   claude-job-hunt/1.233.0
405    2 523 B   Mozilla/5.0 (Macintosh) Chrome/128.0
```

*The 403 is not the burst effect of `ve.buscojobs.com` (five 405 in a
rafale, seven of seven served at 30 s): the FIRST request of the day, alone,
got it, and the tab got it thirty seconds apart.* **It is a WAF rule on the
client's shape: bot-shaped identities 403, browser-shaped ones a challenge,
`curl/…` through.** The plugin presents itself under its own name and no
other (§2 quater: a third name to undo a refusal is not a route), and a
challenge is not defeated (borne 2). **So today: no page route, by any
client the plugin may be.**

## What stays true of the board, and what a session does

The board is real and sized: «2429 vacantes» stated on 13.09, 1 632 ad URLs
in the sitemap on 16.09 (the sitemap is a window — id 1 993 259 … 1 995 679
on its edges, lastmod from 2026-08-17 — and 1 632 < 2 429: the gap is not
explained here). The URL carries the title and the place as slugs
(`supervisor_de_recursos_humanos_falcon` / `edo_falcon`), the employer does
not travel in it.

**Next reading (a control, not a re-sonde):** one `fetch-body.py` of
`/venezuela/` under the declared identity, dated; served → `empleate_ve.py`
is written as the issue describes (root count · sitemap inventory · ad
read, the count printed beside the emitted); refused again → the sitemap
alone is what the plugin can honestly emit, and that is a decision for the
owner (a script that renders the inventory without the ad is not «a script
that renders nothing», #404 — but it renders less than the issue promises).

## What is withheld

Nothing was read that could carry a recruiter; the ad page is 403 today. The
13.09 root cards show title, employer name and place — the employer is
public, no person's name was on a card.
