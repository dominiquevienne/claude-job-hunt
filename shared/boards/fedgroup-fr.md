# Board measurement — Fed Group (`fedgroup.fr`): the French recruitment network — **the host form the country page names, `www.fedgroup.fr`, is NXDOMAIN on two public resolvers, and the bare domain that resolves serves a REGISTRAR PARKING PAGE over port 80 while refusing the connection on 443** — so this name serves no board, and the `no-rules` recorded here on 2026-10-09 was the verdict of the SCHEME and not of the host: the rules file answers 200 with one byte over the port that answers

<!-- verified: 2026-10-17 -->

<!-- hosts: fedgroup.fr -->
<!-- script: none -->
<!-- countries: FR -->
<!-- content: out-of-domain · **THE LIVE HOST SERVES A REGISTRAR PARKING PAGE, AND THE `no-rules / certain: False` OF 2026-10-09 WAS THE VERDICT OF THE SCHEME AND NOT OF THE HOST** — measured 2026-10-17 by RETRIEVING the host and never by re-reading this card. `https://fedgroup.fr/` is **Connection refused** (no TLS listener; `kind: transport-failure`, and the refusal is RECORDED by the tool with `body_kept: false` since its repair of 11.10), while `http://fedgroup.fr/` answers **HTTP 200, 2326 bytes, md5 eb1335a03f0e624572576e90cfb7b57b, server nginx** and the body is Gandi's own parking page: «This domain name has been registered with Gandi.net. It is currently parked by the owner» and «fedgroup.fr is unavailable». **THAT IS A STATEMENT ABOUT THE NAME AND NOT ABOUT FED GROUP, AND A REGISTRAR IS NOT AN OPERATOR**: the class the owner validated on 2026-10-06 — «un exploitant qui déclare lui-même sa plateforme fermée ou indisponible» — DOES NOT APPLY here, nothing in this card is `route: none`, and where the company's board lives is UNMEASURED and not inferred. **AND THE RULES ARE READ, NOT UNREADABLE**: `http://fedgroup.fr/robots.txt` answers **HTTP 200 with 1 byte** (md5 68b329da9893e34099c7d8ad5cb9c940, a single newline), so `state: read` and `certain: TRUE` — an open door by KNOWLEDGE where this card recorded one by IGNORANCE, which is the pair where only `state` separates two identical verdicts. The cause is in OUR instrument and it is measured by reading the line that builds the URL: `_robots.py:329` hard-codes `https://{host}/robots.txt` with no fallback and `allowed(host, path, agents, board)` takes no scheme, so on a host that refuses 443 and serves 80 it can only ever render `no-rules`. **INERT HERE — the rules are empty either way — and PERMISSIVE in general**: the same shape on a host serving `Disallow: /` over port 80 would be read as an absence of rules under #283 and would silently bypass borne 1 · 2026-10-17 -->
<!-- content: indeterminate · **THE FORM NAMED ON THE COUNTRY PAGE DOES NOT EXIST AND THE BARE DOMAIN RESOLVES TO 217.70.184.38** — 0 bytes of rules on the live host, so **no `Crawl-delay` could be read and the cadence is entirely ours** — checked on 2 public resolvers, never on a second host, because a DNS negative is the resolver's answer and a local cache will agree with itself: `www.fedgroup.fr` answers **NXDOMAIN on 1.1.1.1 AND on 8.8.8.8**, while `fedgroup.fr` answers **NOERROR with 217.70.184.38 on both**. `NXDOMAIN` is not `SERVFAIL`: the name is absent, not unresolved. **This is the `www.` trap taken in the opposite direction from `iefponline.iefp.pt`**, where the bare form answered and the `www.` one did not resolve — here the page carries the dead form, so an adapter built on what the page names would never connect, and the failure would read as a dead board. **THE RULES OF THE LIVE HOST COULD NOT BE READ**: `fedgroup.fr/robots.txt` yields 0 bytes, `state: no-rules`, **`certain: False`** — which the owner's decision of 13.09.2026 (#283) reads as an absence of rules and therefore an open door, **but an open door by IGNORANCE and not by knowledge.** That is a different state from Robert Half's 404 on the same pass (`state: absent`, `certain: True`), and the two print the same verdict: only `state` separates them, so `state` is what this card records. **NO CONTENT HAS BEEN RETRIEVED FROM THE LIVE HOST.** The first retrieval was attempted on the form the page names and failed at DNS (`URLError: nodename nor servname provided`), which is a fact about that NAME and not about this board — and nothing was re-attempted on the bare domain in the same turn as its guard. METHOD: two public resolvers before any conclusion; guard on the bare host in its own turn; `bin/fetch-body.py` for every retrieval** · 2026-10-09 -->

## Measured 2026-10-17 — the live host was retrieved: a parked name, and a `state` that was the scheme's

```
https://fedgroup.fr/          Connection refused (errno 61)   pas d'ecouteur TLS
http://fedgroup.fr/           HTTP 200 · 2326 o · nginx        page de PARKING Gandi
                              md5 eb1335a03f0e624572576e90cfb7b57b
http://fedgroup.fr/robots.txt HTTP 200 · 1 o (un saut de ligne) state read · certain TRUE
                              md5 68b329da9893e34099c7d8ad5cb9c940
garde sur l'hote EXACT, jeton `claude-user` seul, dans un tour DISTINCT :
  allowed true · kind no-rules-connection · state no-rules · certain false
  -- et ce verdict est celui du SCHEMA : `_robots.py:329` ne construit que https
```

**CORRECTION DATÉE.** This card recorded, on 2026-10-09: «0 bytes of rules on the live host, `state: no-rules`, `certain: False` ... an open door by IGNORANCE and not by knowledge», and «**NO CONTENT HAS BEEN RETRIEVED FROM THE LIVE HOST**». Both are now measured, and both move: the live host **does** serve content, and its rules **are** read. The old reading was true of **HTTPS** and was written as a fact about the **HOST** — the same family as a verdict taken on `/` that is read as a verdict on the ad pages, and as a refusal read on the wrong host, with the varying thing being the **SCHEME** this time.

**WHAT VARYING ONE THING BOUGHT.** The first retrieval of this turn refused at the transport, and stopping there would have published «the live host serves nothing» — which is exactly the failure this card had warned about, a page that would read as a dead board. Only the port changed between the two requests.

**WHAT THE PARKING PAGE DOES AND DOES NOT SETTLE.** It settles that `fedgroup.fr` serves no board: the registrar says the name is parked, in its own words. It settles nothing about Fed Group as a company, and **no candidate host is proposed here, because none was measured** — guessing a sibling domain is the devinette that cannot be verified by the thing it invents.

**WHAT REMAINS, AND WHO HOLDS IT.** (a) The FRA country page still names the dead form `www.fedgroup.fr`; the published pages are the artefact session's by the ceiling of §2 bis's third source, so this card names the fact and does not touch the page. (b) The instrument defect above is this repository's code, not a host's behaviour, and it is reported as MEASURED — the URL-building line was read and the two ports were retrieved.

## Measured 2026-10-09 — the page names a host that does not exist

```
www.fedgroup.fr   @1.1.1.1   NXDOMAIN        <- la forme que la page FRA nomme
www.fedgroup.fr   @8.8.8.8   NXDOMAIN           deux resolveurs, jamais deux hotes
fedgroup.fr       @1.1.1.1   NOERROR  217.70.184.38
fedgroup.fr       @8.8.8.8   NOERROR  217.70.184.38
fedgroup.fr/robots.txt       0 o · state no-rules · certain FALSE
                             -> porte ouverte par IGNORANCE, pas par connaissance
                             (contre roberthalf.fr : 404, state absent, certain TRUE)
```

**Ce qui restait à établir est ÉTABLI le 17.10.2026 — voir la section de ce jour :** l'hôte vivant sert une page de PARKING de registrar sur le port 80 et refuse la connexion sur 443, et son fichier de règles se LIT (200, un octet) sur le port qui répond — donc le `no-rules` du 09.10 était le verdict du SCHÉMA. *Et la page pays porte toujours la forme morte : c'est elle qu'il faut corriger le jour où cette fiche devient un adaptateur, sinon le script ne se connectera jamais et l'échec ressemblera à un board mort — elle est à la session des artefacts.*
