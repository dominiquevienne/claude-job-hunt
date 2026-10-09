# Board measurement — Fed Group (`fedgroup.fr`): the French recruitment network — **the host form the country page names, `www.fedgroup.fr`, is NXDOMAIN on two public resolvers while the bare domain resolves**, and the bare domain's rules could not be read at all

<!-- verified: 2026-10-09 -->

<!-- hosts: fedgroup.fr -->
<!-- script: none -->
<!-- countries: FR -->
<!-- content: indeterminate · **THE FORM NAMED ON THE COUNTRY PAGE DOES NOT EXIST AND THE BARE DOMAIN RESOLVES TO 217.70.184.38** — 0 bytes of rules on the live host, so **no `Crawl-delay` could be read and the cadence is entirely ours** — checked on 2 public resolvers, never on a second host, because a DNS negative is the resolver's answer and a local cache will agree with itself: `www.fedgroup.fr` answers **NXDOMAIN on 1.1.1.1 AND on 8.8.8.8**, while `fedgroup.fr` answers **NOERROR with 217.70.184.38 on both**. `NXDOMAIN` is not `SERVFAIL`: the name is absent, not unresolved. **This is the `www.` trap taken in the opposite direction from `iefponline.iefp.pt`**, where the bare form answered and the `www.` one did not resolve — here the page carries the dead form, so an adapter built on what the page names would never connect, and the failure would read as a dead board. **THE RULES OF THE LIVE HOST COULD NOT BE READ**: `fedgroup.fr/robots.txt` yields 0 bytes, `state: no-rules`, **`certain: False`** — which the owner's decision of 13.09.2026 (#283) reads as an absence of rules and therefore an open door, **but an open door by IGNORANCE and not by knowledge.** That is a different state from Robert Half's 404 on the same pass (`state: absent`, `certain: True`), and the two print the same verdict: only `state` separates them, so `state` is what this card records. **NO CONTENT HAS BEEN RETRIEVED FROM THE LIVE HOST.** The first retrieval was attempted on the form the page names and failed at DNS (`URLError: nodename nor servname provided`), which is a fact about that NAME and not about this board — and nothing was re-attempted on the bare domain in the same turn as its guard. METHOD: two public resolvers before any conclusion; guard on the bare host in its own turn; `bin/fetch-body.py` for every retrieval** · 2026-10-09 -->

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

**Ce qui reste à établir :** ce que l'hôte vivant sert — **rien n'en a été récupéré** —, et pourquoi son fichier de règles ne se lit pas. *Et la page pays porte la forme morte : c'est elle qu'il faut corriger le jour où cette fiche devient un adaptateur, sinon le script ne se connectera jamais et l'échec ressemblera à un board mort.*
