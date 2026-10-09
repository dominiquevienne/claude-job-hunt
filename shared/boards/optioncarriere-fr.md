# Board measurement — Option Carrière France (`www.optioncarriere.com`): the aggregator's French instance — **`/emploi` answers HTTP 200 with an antirobot verification page**, 11 984 bytes whose `<h1>` reads «Vérification requise», so the status says success and the body says challenge

<!-- verified: 2026-10-09 -->

<!-- hosts: www.optioncarriere.com, optioncarriere.com -->
<!-- script: none -->
<!-- countries: FR -->
<!-- content: indeterminate · **THE CODE SAYS 200 AND THE BODY IS A CHALLENGE — and only an identity marker caught it**: `GET /emploi` returned 200 with 11 984 B (md5 0a65a54ccf59, 2026-10-09T07:08:31Z, as Claude-User) whose `<title>` is «Optioncarriere» and whose **`<h1>` is «Vérification requise»** — 2 368 characters of visible text that are a spinner's keyframes, ONE `<a>` tag, no form, no refresh meta, **zero JSON-LD and zero link at any advert pattern**. A counter run over this page would have returned 0 and that 0 would have entered a sum as the tail of an enumeration; what distinguished «this page has none» from «this is not that page» was reading the `h1`, not the count. **BORNE 2 APPLIES AND NOTHING WAS RETRIED**: an antirobot control is never defeated, and the plugin's user is never asked to defeat one — so this is recorded as INDETERMINATE, which is a measurement to redo and never a renunciation. **AND A CHALLENGE SAYS NOTHING ABOUT WHAT SITS BEHIND IT**: this verdict is about THE PATH INTERROGATED on this date, not about the host, and the real listing path remains to be established. THE RULES, read in a turn distinct from the retrieval: the group that applies to `claude-user` is `*`, with **no `Disallow`** and **no `Crawl-delay`** (1 386 B, `state: read`, `certain: True`) — the file permits what the infrastructure then interrupts, which is the ordinary shape of a firewall that does not know who we are, and **NO sitemap is declared**, so there is no index to follow instead. One request, one challenge, nothing repeated. METHOD: guard on the exact URL in a separate turn; `bin/fetch-body.py`, provenance beside the body** · 2026-10-09 -->

## Measured 2026-10-09 — a 200 that is not an answer

```
robots.txt        1 386 o   state read, certain True
  groupe *                  AUCUN Disallow · aucun Crawl-delay · aucun sitemap
/emploi          11 984 o   **HTTP 200**
  title                     « Optioncarriere »
  h1                        « Verification requise »    <- le SEUL discriminant
  contenu                   2 368 car. de texte : les keyframes d'un spinner
                            1 balise <a> · 0 JSON-LD · 0 lien d'annonce
```

**Pourquoi ce n'est pas écrit comme un refus de l'éditeur :** son fichier de règles n'interdit rien et ne nous nomme pas. Un contrôle antirobot servi en 200 est une infrastructure qui ne sait pas qui nous sommes — et la borne 2 interdit de le déjouer, par le navigateur comme par un script. **Donc : INDÉTERMINÉ, une seule requête, aucun réessai**, et la mesure se refait le jour où quelque chose a changé du côté de l'hôte.

**Ce qui reste à établir :** tout — le chemin de liste, ce qu'une annonce sert, et s'il existe une route que le défi ne garde pas.
