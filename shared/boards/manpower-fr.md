# Board measurement — Manpower France (`www.manpower.fr`): the staffing network's French board — **the rules are read, open, and set `Crawl-delay: 10`; the transport then serves a Cloudflare challenge titled «Just a moment...»** — so this is INDETERMINATE and borne 2 forbids defeating it, by script or by browser

<!-- verified: 2026-10-09 -->

<!-- hosts: www.manpower.fr, manpower.fr -->
<!-- script: none -->
<!-- countries: FR -->
<!-- content: indeterminate · **THE RULES OPEN AND THE HOST SETS ITS OWN RATE — `Crawl-delay: 10`**, read on 1 661 B (`state: read`, `certain: True`, group `*`, in a turn distinct from every retrieval): the 32 refusals are the Drupal default on assets (`/misc/*.css$`, `/modules/*.js?`, …) and **not one of them names a path a board would serve**, so nothing written refuses the adverts. **AND THE TRANSPORT ANSWERS 403 WITH AN ANTIROBOT CHALLENGE**: `GET /` returned **HTTP 403, 5 641 B**, and the identity of the body is what decided — `<title>Just a moment...</title>`, the words `Cloudflare` and `challenge` present. **THE FINGERPRINT MOVES BETWEEN TWO FETCHES OF THE SAME URL AND I CHECKED THAT BEFORE COMPARING ANYTHING**: md5 50b0cac02753 then 356d96172b9c at the same 5 641 B, and the diff is **two lines, both a CSP nonce** (`nonce-oeCNP123oUXT1ozwA94J0m` against `nonce-GoRHY1CkDMMeDH1aMOvZnc`) — so any comparison of this body's md5 against another host's is void, which is exactly why the two fetches came before the comparison and not after. **WHY THE BROWSER ROUTE DOES NOT OPEN HERE**: the decision of 07.09.2026 drives the browser when the rules open and the infrastructure refuses — but borne 2 comes first, and a control titled «Just a moment...» with a moving fingerprint is an antirobot challenge, which is never defeated and is never handed to the plugin's user to defeat. **TWO REQUESTS, TEN SECONDS APART BECAUSE THE HOST ASKED FOR TEN, AND NOTHING RETRIED.** This is a measurement to redo the day something changes on the host's side — never a renunciation, and never a verdict on the board. METHOD: guard on the exact URL in a turn distinct from the retrievals; `bin/fetch-body.py`, both refusals kept under `--allow-refusal` so their status travels in their record** · 2026-10-09 -->

## Measured 2026-10-09 — open rules, a ten-second rate, and a challenge

```
robots.txt        1 661 o   state read, certain True · groupe *
  Crawl-delay          10   <- l'allure de L'HOTE, pas la notre
  32 refus                  le defaut Drupal sur les ASSETS : /misc/*.css$ /modules/*.js? ...
                            aucun ne nomme un chemin qu'un board servirait
  sitemaps                  aucun declare
/ (racine)                  **HTTP 403**, 5 641 o
  title                     « Just a moment... »        <- le discriminant
  marqueurs                 Cloudflare · challenge
  empreinte MOUVANTE        md5 50b0cac02753 puis 356d96172b9c, meme taille
  la cause                  2 lignes : un nonce CSP (nonce-oeCNP... / nonce-GoRHY...)
```

**Pourquoi ce n'est pas la route navigateur.** La décision du 07.09 ouvre le navigateur quand les règles ouvrent et que l'infrastructure refuse — **mais la borne 2 passe devant** : un contrôle antirobot ne se déjoue pas, et il n'est jamais demandé à l'utilisateur du plugin de le déjouer. *Donc INDÉTERMINÉ, deux requêtes, aucun réessai.*

**Ce qui reste à établir :** tout, et la mesure se refait le jour où l'hôte a changé — pas en réessayant celle-ci.
