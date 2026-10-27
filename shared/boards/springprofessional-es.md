# Board measurement — Spring Professional España: **the host the country page names has NO DNS DELEGATION AT ALL** — NXDOMAIN on six record types from both resolvers — and the owner's class of 2026-10-26 covers its two dead forms while that class's own second borne excludes its third

<!-- verified: 2026-10-05 -->

<!-- hosts: springprofessional.es, www.springprofessional.es, springprofessional.com -->
<!-- script: none -->
<!-- countries: ES -->
<!-- host-forms-basis: `springprofessional.es` and `www.springprofessional.es` answer **NXDOMAIN on all six record types (A, AAAA, NS, SOA, MX, CNAME) from BOTH public resolvers** — no delegation at all, so there is no rules file to have a state; `springprofessional.com` resolves (NOERROR, 149.232.252.3) and its rules file is `no-rules-connection` after 3 attempts (`Errno 61 Connection refused`), `certain: False` · 2026-10-05 -->
<!-- content: measured · **NXDOMAIN on 6 record types, from 2 public resolvers, on BOTH host forms this country page names — and the 3rd form resolves only to refuse the connection.** The host this country page names does not exist: `springprofessional.es` answers **NXDOMAIN** — not `SERVFAIL`, not `NOERROR` with no `A` — **on A, AAAA, NS, SOA, MX and CNAME, from both 1.1.1.1 and 8.8.8.8**, and so does its `www`. *There is no delegation, so there is no rules file and no state to record: the page's list has aged.* `springprofessional.com` does resolve and then **refuses the connection** (`Errno 61`, 3 attempts, `no-rules-connection`, `certain: False`). **AND IT IS NOT DECLARED A SUCCESSOR: a guess that resolves is not a discovery, and nothing read says this `.com` serves Spain** — the `.es` host told us nothing because it answered nothing. **NOR DOES THIS CARD DECLARE THE BOARD CLOSED — AND THE REASON FIRST PUBLISHED HERE ON 2026-10-27 WAS FALSE, CORRECTED THE SAME DAY.** *It read, verbatim: «the class «a name without delegation, measured on two resolvers» was RECOMMENDED to the owner and he did NOT grant it on 2026-10-26».* **The owner GRANTED that class on 2026-10-26, verbatim «fais en une classe», and §2 sexies gained a FOURTH validated class**, which reads «un board, commercial compris, dont le nom n'a AUCUNE DÉLÉGATION — `NXDOMAIN` mesuré sur DEUX résolveurs publics, apex compris». *The refusal and the grant were recorded SIXTEEN MINUTES apart, the later entry citing the earlier one by name and describing itself as its reversal, and the shared journal arbitrates by APPEND ORDER — **the LAST match wins**, which is the exact opposite of the `read_cards()` rule that gives a card its FIRST occurrence. A motif that stopped at the first match read the refusal as the state: the defect is by MEMBERS, and it was visible only because two entries of opposite value exist with a rule that arbitrates between them.* **AND THE CLASS’S OWN SECOND BORNE EXCLUDES THE THIRD HOST FORM OF THIS CARD: «un nom qui RÉSOUT dont le transport échoue reste un INDÉTERMINÉ et pas un membre».** `springprofessional.es` and its `www` ARE members — NXDOMAIN on six record types, two public resolvers, apex measured — while `springprofessional.com` resolves and then refuses the connection, so that borne makes it an INDÉTERMINÉ. *A `route:` written here would assert closure over a form the class itself excludes: three host forms, two states — the very defect this card was split out of, one level down.* **So no `route:` is written, and the exact text of the class is OPEN with the owner**: it rests on a four-word verbatim recorded without its protasis, and §2 requires the entire text before a derogatory permission is relied on. **Nor does it get a `blocked` ticket**: the owner's decision of 2026-09-18, as he extended it on 2026-10-06 (#1021, verbatim «oui, c'est la même règle»), covers a public employment service **national or regional**, and this is a PRIVATE firm — extending it a third time would be exactly the over-generalisation that was flagged rather than assumed on LABORA. WHAT IS NOT ESTABLISHED: **nothing of any board was read on any of these three forms**, so no count, no enumerator and no field shape is known; and whether a Spanish host exists under another name is **not** established, because a resolving guess is not a reading. METHOD: DNS resolved through two public resolvers for every host form before any conclusion, and the negative QUALIFIED by record type and rcode rather than read off an empty answer; the guard taken on the one form that resolves, in a turn distinct from the retrieval · 2026-10-05 -->

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

## Why no closure is written here — and the first reason published was FALSE

**Corrected on 2026-10-27, the same day it was published.** *The block that stood here said the
class had NOT been granted. It had. A correction cites what it corrects rather than rewriting it
in silence (§4).*

```
la CLASSE « nom sans delegation, mesuree sur deux resolveurs »
  journal partage, 26.10 22:00   « la quatrieme CLASSE ... N'EST PAS accordee »
  journal partage, 26.10 22:16   « fais en une classe » — IL ACCORDE, et la puce
                                 CITE la precedente et se dit son renversement
  -> SEIZE MINUTES d'ecart, et le journal arbitre par l'ORDRE D'APPEND :
     la DERNIERE correspondance fait foi. C'est l'INVERSE de la regle des
     fiches, ou `read_cards()` donne la PREMIERE occurrence — et c'est le seul
     endroit ou un lecteur se trompe, parce que les deux conventions coexistent.

ce que la classe dit, formulation du journal :
  « un board, commercial compris, dont le nom n'a AUCUNE DELEGATION —
    NXDOMAIN mesure sur DEUX resolveurs publics, apex compris »

ses TROIS bornes, et la deuxieme decide ici :
  1  SERVFAIL n'est PAS NXDOMAIN
  2  un nom qui RESOUT dont le transport echoue reste un INDETERMINE
     et PAS un membre            (forme labora.gva.es / #1021)
  3  l'apex se mesure : un sous-domaine mort sous un apex vivant ne dit rien

application aux TROIS formes de cette fiche :
  springprofessional.es        NXDOMAIN, 6 types, 2 resolveurs, APEX   MEMBRE
  www.springprofessional.es    idem                                    MEMBRE
  springprofessional.com       NOERROR puis Errno 61                   NON MEMBRE
                                                                       (borne 2)

  -> une ligne `route:` posee ici porterait sur les TROIS, donc elle declarerait
     ferme une forme que la classe EXCLUT elle-meme. C'est le defaut dont cette
     fiche a ete scindee, un etage plus bas : trois formes, deux etats.
```

**Et le texte exact de la classe est OUVERT chez le propriétaire** : elle tient sur un verbatim de
QUATRE MOTS consigné sans sa protase, et §2 exige le texte entier avant qu'une permission
dérogatoire soit utilisée. *Le pilote la lui repose ; ce n'est pas à cette fiche de trancher.*

Ni ticket `blocked` : la décision du 18.09, telle que le propriétaire l'a étendue le 06.10 (#1021,
« oui, c'est la même règle »), couvre un service public de l'emploi NATIONAL OU RÉGIONAL. Ce sont
des cabinets PRIVÉS.

## What this card does not say

**Nothing of any board was read on any of the three host forms**, so no count, no enumerator and no field shape is known.

**Whether a Spanish host exists under another name is not established.** `springprofessional.com` resolves, and that is all it does: a guess that resolves is not a discovery, and nothing read says it serves Spain.
