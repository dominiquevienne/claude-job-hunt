# Board measurement — Spring Professional España: **the host the country page names has NO DNS DELEGATION AT ALL** — NXDOMAIN on six record types from both resolvers — and the class that would validate it was explicitly NOT granted on 2026-10-26

<!-- verified: 2026-10-05 -->

<!-- hosts: springprofessional.es, www.springprofessional.es, springprofessional.com -->
<!-- script: none -->
<!-- countries: ES -->
<!-- host-forms-basis: `springprofessional.es` and `www.springprofessional.es` answer **NXDOMAIN on all six record types (A, AAAA, NS, SOA, MX, CNAME) from BOTH public resolvers** — no delegation at all, so there is no rules file to have a state; `springprofessional.com` resolves (NOERROR, 149.232.252.3) and its rules file is `no-rules-connection` after 3 attempts (`Errno 61 Connection refused`), `certain: False` · 2026-10-05 -->
<!-- content: measured · **NXDOMAIN on 6 record types, from 2 public resolvers, on BOTH host forms this country page names — and the 3rd form resolves only to refuse the connection.** The host this country page names does not exist: `springprofessional.es` answers **NXDOMAIN** — not `SERVFAIL`, not `NOERROR` with no `A` — **on A, AAAA, NS, SOA, MX and CNAME, from both 1.1.1.1 and 8.8.8.8**, and so does its `www`. *There is no delegation, so there is no rules file and no state to record: the page's list has aged.* `springprofessional.com` does resolve and then **refuses the connection** (`Errno 61`, 3 attempts, `no-rules-connection`, `certain: False`). **AND IT IS NOT DECLARED A SUCCESSOR: a guess that resolves is not a discovery, and nothing read says this `.com` serves Spain** — the `.es` host told us nothing because it answered nothing. **NOR DOES THIS CARD DECLARE THE BOARD CLOSED, AND THAT IS A MEASURED POINT AND NOT A PRUDENCE: the class «a name without delegation, measured on two resolvers» was RECOMMENDED to the owner and he did NOT grant it on 2026-10-26** — he answered on the OBJECTS he was asked about (`goafricaonline.com`, then `bestjobs-mg` and `emploimali`, each «sort du faisable») and never on the class, and §2 sexies records his validations as classes only when he states the class himself, as he did on 2026-10-06 for «un exploitant qui déclare lui-même sa plateforme fermée». *So the next dead commercial name is re-asked rather than inferred, and this host IS that next name.* **Nor does it get a `blocked` ticket**: the owner's decision of 2026-09-18, as he extended it on 2026-10-06 (#1021, verbatim «oui, c'est la même règle»), covers a public employment service **national or regional**, and this is a PRIVATE firm — extending it a third time would be exactly the over-generalisation that was flagged rather than assumed on LABORA. WHAT IS NOT ESTABLISHED: **nothing of any board was read on any of these three forms**, so no count, no enumerator and no field shape is known; and whether a Spanish host exists under another name is **not** established, because a resolving guess is not a reading. METHOD: DNS resolved through two public resolvers for every host form before any conclusion, and the negative QUALIFIED by record type and rcode rather than read off an empty answer; the guard taken on the one form that resolves, in a turn distinct from the retrieval · 2026-10-05 -->

<!-- witness: none — nothing was read. Two of the three host forms have no DNS delegation at all, so there is nothing to enumerate and no count to witness; the third resolves and refuses the connection · 2026-10-05 -->

## Split out of a grouped card on 2026-10-27 — #1205

This card and its two siblings — `hays-es.md` and `robertwalters-es.md` — were **one** card declaring **seven** host forms on a single `hosts:` line. **This is the firm the split exists for:** a dead name could not be expressed at the scale of a card that also carried a live board — acting on the card would have closed Hays, and not acting left the dead name with no expression at all. **Nothing measured here changed in the split**; the dates, the figures and the method are those of 2026-10-05.

## Measured 2026-10-05

```
SPRING PROFESSIONAL — l'hote que la page pays NOMME n'existe pas

springprofessional.es        A AAAA NS SOA MX CNAME  ->  NXDOMAIN
www.springprofessional.es    les six aussi           ->  NXDOMAIN
  sur 1.1.1.1 ET 8.8.8.8     ni SERVFAIL, ni NOERROR-sans-A : AUCUNE delegation
  -> pas de fichier de regles, donc aucun etat a consigner. La liste a vieilli.

springprofessional.com       NOERROR, 149.232.252.3
  robots.txt                 no-rules-connection, 3 tentatives
                             Errno 61 — Connection refused, certain FALSE

  ET IL N'EST PAS DECLARE SUCCESSEUR : une devinette qui resout n'est pas une
  decouverte, et rien de ce qui a ete lu ne dit que ce `.com` sert l'Espagne.
```

## Why no closure is written here, and it is a measurement rather than a caution

```
la CLASSE « nom sans delegation, mesuree sur deux resolveurs »
  recommandee au proprietaire                 26.10.2026
  sa reponse                                  il a repondu sur les OBJETS
                                              (goafricaonline, bestjobs-mg,
                                               emploimali : « sort du faisable »)
  la classe                                   N'EST PAS ACCORDEE
  -> §2 sexies n'enregistre une validation comme une CLASSE que lorsqu'il
     ENONCE la classe (06.10 : « un exploitant qui declare lui-meme sa
     plateforme fermee »). Donc le prochain nom mort commercial SE REDEMANDE,
     et cet hote EST ce prochain nom.

ni ticket `blocked` : la decision du 18.09, telle que le proprietaire l'a
etendue le 06.10 (#1021, « oui, c'est la meme regle »), couvre un service
public de l'emploi NATIONAL OU REGIONAL. Ce sont des cabinets PRIVES.
```

## What this card does not say

**Nothing of any board was read on any of the three host forms**, so no count, no enumerator and no field shape is known.

**Whether a Spanish host exists under another name is not established.** `springprofessional.com` resolves, and that is all it does: a guess that resolves is not a discovery, and nothing read says it serves Spain.
