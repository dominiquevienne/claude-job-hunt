# Board measurement — Spain's health-service `bolsas` (SAS · SERMAS · Osakidetza): **33 professional categories and one single pool, and NOT ONE ADVERT** — the country page said «&nbsp;ce n'est pas un board mais un calendrier&nbsp;» and that is now measured: zero tables, zero rows, zero per-post detail pages, because the object a candidate needs here is a REGISTRATION in a permanent pool and not a vacancy

<!-- verified: 2026-10-05 -->

<!-- hosts: www.sspa.juntadeandalucia.es, ws027.sspa.juntadeandalucia.es, www.comunidad.madrid, sede.comunidad.madrid, www.euskadi.eus, www.osakidetza.euskadi.eus -->
<!-- script: none -->
<!-- countries: ES -->
<!-- host-forms-basis: six host forms read, and the Andalusian health host is the first in this repository to REFUSE its rules file while SERVING its pages — `www.sspa.juntadeandalucia.es` answers **403 on `/robots.txt`** (`state: no-rules`, kind `no-rules-403`, `certain: False`, an absence of rules and an open door under #283) and then answers **200 with 643 459 B** on its own pages, which is the usual asymmetry taken the other way round; `www.comunidad.madrid` is read, 95 `Disallow`, `Crawl-delay: 10`, `certain: True`; `sede.comunidad.madrid` carries the 67 bolsa pages; `www.euskadi.eus` is read and `certain: True` with **958 `Disallow`** and 21 `Allow`, and `www.osakidetza.euskadi.eus` — the SAME IP via the SAME CNAME target `nombres.euskadi.eus` — serves a DIFFERENT file: **930 `Disallow`**, 0 `Allow`, 31 905 B against 33 250 B, md5 d01a09755bb1 against e03ff54341c1, sharing 924 rules with 30 proper to euskadi and 2 proper to osakidetza; `ws027.sspa.juntadeandalucia.es` carries the VEC registration application and was reached only as a declared link, not fetched · 2026-10-05 -->
<!-- content: measured · **33 professional categories, 67 registry pages, 958 and 930 refusals on two Basque hosts, and NOT ONE ADVERT on any of the three services — the country page's «&nbsp;ce n'est pas un board mais un calendrier&nbsp;» is now a measurement rather than a remark.** ANDALUCÍA (SAS): the entry point was found by LINK TEXT from the regional portal — «&nbsp;Tu salud&nbsp;» and «&nbsp;Salud Responde&nbsp;» lead to `www.sspa.juntadeandalucia.es`, a host the country page never names — and `/servicioandaluzdesalud/profesionales/ofertas-de-empleo` plus `…/bolsa-de-empleo` were read at 709 664 B and 763 026 B. **Both carry ZERO `<table>`, ZERO `<tr>` and ZERO `.pdf` links, and their `<main>` holds 589 and 8 245 characters of text against 707 873 and 761 040 characters of markup** — so 99.92 % of the hub's payload is chrome. What the text says is a PROCEDURE: «&nbsp;Bolsa única de empleo… se constituye sobre un modelo de baremo homogéneo y de procedimiento único para toda Andalucía… La inscripción de las solicitudes… se gestionan desde la aplicación Ventanilla Electrónica del Candidato (VEC)&nbsp;», with a «&nbsp;Fecha de actualización 02/10/2026&nbsp;». **There is no advert object at all: one registers once, is ranked by a scoring scale, and the events are `convocatorias`, `listados` and `cuadros de evolución` — so `job-scan` has nothing to enumerate here, and that is a finding about the OBJECT and not a failure of the route** (§2 sexies: nothing is declared closed, and the route answers 200 to the declared client). The bolsa page names three further hosts: `ws027.sspa.juntadeandalucia.es/profesionales/seleccion/seleccion.asp?idap=2`, the VEC registration front and a classic **ASP** application; **`resuelve.ayesa.link` — a PRIVATE VENDOR's domain on a `.link` TLD, carrying 11 links of the bolsa's own official FAQ documentation**; and raw Drupal `/node/20791` and `/media/14508` paths beside the friendly URLs, so the same content is reachable under two URL shapes and an extractor that does not normalise would count it twice. MADRID (SERMAS): the entry was again found by LINK TEXT — «&nbsp;Bolsas de contratación temporal en el Servicio Madrileño de Salud&nbsp;» — and it is **on the PORTAL host, not on a separate one**, which BREAKS the pattern the previous card measured for the three employment services (portal refuses, offers live on an unruled sibling). Its `<main>` holds 14 124 characters, again **zero `<table>`, zero `<tr>` and only 2 PDFs**, and the structure is **33 professional categories** (5 + 16 + 7 + 4 + 1 across five accordions, separated from the **13** FAQ items by MEASURING which accordion items carry a bolsa link rather than by assuming) **each with its own registry pages on a fourth host, `sede.comunidad.madrid` — 67 distinct `/oferta-empleo/` links, two per category («&nbsp;Inscripción en bolsa o actualización de méritos&nbsp;» and «&nbsp;Listados provisionales y definitivos&nbsp;»)**. Still not one vacancy: 33 pools, 67 doors into them, zero adverts. BASQUE COUNTRY (Osakidetza) — AND THE SHARPEST LANGUAGE FINDING OF THE PASS: `www.euskadi.eus` serves `<html lang="eu">` BY DEFAULT, and over its **139 anchors a Spanish employment-word matcher (`empleo|oferta|trabajo|bolsa|vacante|oposici`) finds ZERO while a Basque one (`enplegu|lana|lan|lanpostu|hautaketa|deialdi`) finds FIVE** — `Enplegu publikoa`, `Lana eta enplegua`, `Lanbide-Euskal Enplegu Zerbitzua`, `Osakidetza-Euskal Osasun Zerbitzua`. **A Spain pass that matched Spanish words would have concluded that the Basque portal links no employment section at all: 0 of 139, under 200, with a clean parse and no error** — the previous card said sefcarm's discriminant was «&nbsp;language-dependent&nbsp;»; here the language is a DIFFERENT one and it is the default. **AND `grep` WENT BLIND ON THAT SAME PAGE, WHICH IS A DEFECT OF THE TOOL AND NOT OF THE PATTERN: the 34 791-byte body contains exactly FOUR bytes ≥ 0x80, the first being `0xf3` at offset 238 inside a leftover developer HTML comment** (`previsualizacización`, `páginas`, written in latin-1 while the rest of the document is clean ASCII) — **so under `LC_CTYPE=UTF-8` BSD `grep` classifies the whole file as BINARY and reports no match with `exit 1`, indistinguishable from the string being absent: `grep -c osanet` prints nothing and exits 1, `grep -ac osanet` prints 1.** Python decoding with `errors='replace'` found the string throughout. *That is «&nbsp;a string has several forms at the point of call&nbsp;» one storey lower — the pattern is right, the file is right, and the TOOL declines to look — and four bytes in a forgotten comment are enough to blind a measurement over an entire file.* The href it was hiding is `https://www.osanet.euskadi.net/o22War/…?servicio=16&amp;idioma=eus`: **`euskadi.NET`, not `.eus`** — which CONFIRMS and generalises `lanbide.md`'s `apps.lanbide.euskadi.net`, two unrelated Basque services splitting content from application across two registrable domains — **and it carries `&amp;` inside the attribute, the third occurrence of that trap in two days after inaem's sitemap `<loc>`.** THE ARCHITECTURE THAT EXPLAINS WHY «ROBOTS BINDS A HOST, NOT A BRAND» KEEPS RECURRING IN THIS PASS — three administrations, three sibling registrable domains, and in all three the APPLICATION lives on the sibling: `juntadeandalucia.es` ↔ `junta-andalucia.es` (hyphenated, from the SAE bundle), `euskadi.eus` ↔ `euskadi.net`, `comunidad.madrid` ↔ `madrid.org` (`gestiona.madrid.org`, `gestiona7.madrid.org`). **The Madrid page alone names three registrable domains of its own administration (`comunidad.madrid`, `madrid.org`, `playmad.madrid`) over nine distinct hosts.** THREE RULE STATES INSIDE ONE ADMINISTRATION, measured on the same day: `www.juntadeandalucia.es` read with 272 refusals (`certain: True`), `saempleo.es` 404 (`absent`, `certain: True`), `www.sspa.juntadeandalucia.es` **403** (`no-rules`, `certain: False`). AND THE TWO BASQUE FILES ARE THE LARGEST THIS REPOSITORY HAS MET: 958 and 930 `Disallow`, of which **337 each end in `.pdf`** (35–36 %), 951 and 926 carry a wildcard, the longest rule is 232 characters, 4 are exact duplicates and 2 contain an unescaped space. *Same pathology as Andalucía's 219 dated gazette articles — a rules file used as a document-withdrawal register — in a different shape: there a gazette, here attachments.* **AN md5 THAT MOVES AT IDENTICAL LENGTH, which is a fourth distinct reason and the only one where the size does not betray it:** the SAS page fetched twice gave 643 459 B both times with different md5s (296ae3fce078 / d3ba590ed7b5), and locating the differing offsets showed **576 single-byte differences spread over 288 asset URLs** — Drupal's cache-busting query token (`?tmgax1` against `?tmga81`), regenerated per request. *A comparison that checks length first and hash second reads «&nbsp;same size, different hash&nbsp;» and may call it tampering or per-user variation; only the offsets say stylesheet.* EXPURGATION, AND HERE IT IS THE POSITIVE CASE: Madrid's bolsa page carries **2 distinct institutional mail boxes** and **5 distinct anchored nine-digit runs, all five beginning with Madrid's area code**, which its own text labels «&nbsp;Teléfonos de consulta&nbsp;». *These are PUBLIC INSTITUTIONAL contacts — a service mailbox and a switchboard — exactly the `012` helpline case of empregoxunta.md, and a nine-digit rule attaches to all five CORRECTLY here.* **So the question on this board is not whether the pattern fires but whether withholding a public helpline from a candidate serves them, and that is a decision about the FIELD's meaning rather than its shape.** *No contact value is reproduced in this card.* WHAT IS NOT ESTABLISHED: **Osakidetza's own bolsa was not read** — only the rule state of its host and the Basque-language entry point; no advert was counted on any of the three because none was found to count; `resuelve.ayesa.link` was named and not fetched; the VEC application on `ws027` was named and not fetched; and whether the `convocatorias` published in each gazette (`bocm.es` for Madrid, the BOJA for Andalucía) constitute an enumerable stream is a SEPARATE question this card does not open. METHOD: the guard was taken on every one of the six host forms and on each exact path in turns distinct from the retrievals; DNS resolved through two public resolvers for every host; the SAS page fetched TWICE before any fingerprint was compared, which is what made the moving md5 visible; readability checked before every conclusion of absence (0.000 on all five bodies, over 1 440, 1 075, 493 and 300 possible latin leads, so the negative is exercised); `www.comunidad.madrid`'s written 10 s applied to every request to it and our own 2 s on the hosts that write none · 2026-10-05 -->

<!-- witness: none — and that IS the finding: no listing was enumerated and no advert was found on any of the three services, so there is nothing to count and no count is claimed. The figures here are categories (33), registry pages (67), refusal counts (958 / 930 / 272 / 95), byte sizes and rule-state verdicts. A `bolsa` is a permanent pool one registers in, not a stream of vacancies · 2026-10-05 -->

## Measured 2026-10-05 — three services, 33 categories, 67 doors, and zero adverts

```
CE QU'UNE `BOLSA` EST, ET POURQUOI job-scan N'A RIEN A ENUMERER

SAS (Andalousie)        « Bolsa UNICA de empleo »
  le texte de l'hote    baremo homogeneo + procedimiento unico pour toute l'Andalousie
  l'inscription         application VEC (Ventanilla Electronica del Candidato)
  la page /ofertas-de-empleo    709 664 o ·  <table> 0 ·  <tr> 0 ·  .pdf 0
                                <main> = 589 caracteres de texte
  la page /bolsa-de-empleo      763 026 o ·  <table> 0 ·  <tr> 0 ·  .pdf 0
                                <main> = 8 245 caracteres
  -> 99,92 % de la charge du hub est du gabarit, et il n'y a AUCUN objet annonce

SERMAS (Madrid)         33 CATEGORIES professionnelles, une bolsa chacune
  separees de la FAQ    en MESURANT quel item d'accordeon porte un lien de bolsa
                        33 categories (5+16+7+4+1) contre 13 items de FAQ
  les portes            67 liens DISTINCTS sur sede.comunidad.madrid/oferta-empleo/
                        deux par categorie : « Inscripcion » et « Listados »
  <table> 0 · <tr> 0 · .pdf 2
  -> 33 viviers, 67 portes, ZERO annonce

Osakidetza (Euskadi)    l'etat des regles et le point d'entree seulement
                        la bolsa elle-meme N'A PAS ete lue
```

```
LE BASQUE EST LA LANGUE PAR DEFAUT, ET UN MATCHEUR ESPAGNOL REND ZERO

www.euskadi.eus     <html lang="eu">         139 ancres avec href
  motif ESPAGNOL  empleo|oferta|trabajo|bolsa|vacante|oposici   ->  0 ancres
  motif BASQUE    enplegu|lana|lan|lanpostu|hautaketa|deialdi   ->  5 ancres
    Enplegu publikoa · Lana eta enplegua
    Lanbide-Euskal Enplegu Zerbitzua · Osakidetza-Euskal Osasun Zerbitzua

  Une passe Espagne qui aurait cherche des mots ESPAGNOLS aurait conclu que
  le portail basque ne lie aucune section emploi : 0 sur 139, sous 200,
  analyse propre, aucune erreur.
```

```
ET `grep` A REFUSE DE LIRE CETTE PAGE — defaut de l'OUTIL, pas du motif

le corps                34 791 octets, dont QUATRE >= 0x80
le premier fautif       0xf3 a l'offset 238
ou il vit               dans un COMMENTAIRE HTML laisse par un developpeur
                        (« previsualizacización », « páginas » en latin-1)
                        tout le reste du document est de l'ASCII propre
sous LC_CTYPE=UTF-8     grep -c  osanet  ->  RIEN, exit 1
                        grep -ac osanet  ->  1,    exit 0
Python errors=replace   trouve la chaine partout

  Le motif est juste, le fichier est juste, et c'est l'OUTIL qui ne regarde pas.
  Son refus a la forme exacte d'un fait : pas de message, zero correspondance.
  QUATRE octets dans un commentaire oublie aveuglent une mesure sur tout un fichier.

et ce que grep cachait :
  https://www.osanet.euskadi.NET/o22War/...?servicio=16&amp;idioma=eus
    euskadi.NET et non .eus  -> confirme et generalise apps.lanbide.euskadi.net
    &amp; DANS l'attribut    -> 3e occurrence du piege en deux jours
```

```
L'ARCHITECTURE QUI EXPLIQUE TOUTE LA PASSE : trois administrations, trois
domaines ENREGISTRABLES freres, et dans les trois l'APPLICATION est sur le frere

  Andalousie   juntadeandalucia.es   <->  junta-andalucia.es   (trait d'union)
  Euskadi      euskadi.eus           <->  euskadi.net
  Madrid       comunidad.madrid      <->  madrid.org           (gestiona, gestiona7)

  et la seule page des bolsas madrilenes nomme NEUF hotes et TROIS domaines
  enregistrables de sa propre administration :
    sede.comunidad.madrid 84 · www.comunidad.madrid 45 · digital. 4 · 012. 4
    stats. 2 · gestiona. 2 · participa. 2 · gestiona.madrid.org 3 · playmad.madrid 2
```

```
TROIS ETATS DE REGLES DANS UNE SEULE ADMINISTRATION, le meme jour

www.juntadeandalucia.es        200, 8 794 o   read    certain TRUE   272 Disallow
saempleo.es                    404            absent  certain TRUE     0
www.sspa.juntadeandalucia.es   403            no-rules certain FALSE    -
  et il SERT ses pages : 643 459 o sous 200
  -> l'asymetrie habituelle prise a l'envers : les regles refusent, les pages servent
     (#283 : un 403 sur le fichier de regles est une ABSENCE de regles, donc ouvert)

ET LES DEUX FICHIERS BASQUES SONT LES PLUS GROS RENCONTRES ICI

www.euskadi.eus                33 250 o  md5 e03ff54341c1   958 Disallow · 21 Allow
www.osakidetza.euskadi.eus     31 905 o  md5 d01a09755bb1   930 Disallow ·  0 Allow
  MEME adresse IP, MEME cible de CNAME (nombres.euskadi.eus), DEUX fichiers
    communes 924 · euskadi seul 30 · osakidetza seul 2
  composition identique dans les deux : 337 se terminent par .pdf (35-36 %),
    951/926 portent un joker, la plus longue fait 232 caracteres,
    4 doublons exacts, 2 avec un espace non echappe
  -> meme pathologie que les 219 articles dates du BOJA andalou : un fichier de
     regles tenu comme un REGISTRE DE RETRAIT de documents, sous une autre forme
```

```
UN md5 QUI BOUGE A LONGUEUR IDENTIQUE — 4e raison, et la seule indetectable
a la taille

la page du SAS, recuperee DEUX fois avant toute comparaison
  643 459 o   md5 296ae3fce078
  643 459 o   md5 d3ba590ed7b5
localiser les offsets : 576 octets differents, repartis sur 288 URL d'assets
  ?tmgax1   contre   ?tmga81      le jeton anti-cache de Drupal, par requete

  une comparaison qui lit la taille d'abord et l'empreinte ensuite conclut
  « meme taille, empreinte differente » et peut y voir une alteration ou une
  variation par utilisateur. Seuls les OFFSETS disent « feuille de style ».
```

```
EXPURGATION — ici c'est le cas POSITIF, et la question n'est pas le motif

la page des bolsas madrilenes porte
  2 boites de courriel INSTITUTIONNELLES distinctes
  5 suites de neuf chiffres ancrees, distinctes
    les CINQ commencent par l'indicatif de Madrid
    et le texte de la page les nomme lui-meme « Telefonos de consulta »

  Ce sont des contacts PUBLICS de service — exactement le 012 d'Emprego Xunta —
  et une regle « neuf chiffres = un telephone » les attrape CORRECTEMENT ici.
  Donc la question n'est pas si le motif tire, mais si retenir un standard
  public SERT le candidat : c'est une decision sur le SENS du champ et non
  sur sa forme. Aucune valeur n'est reproduite ici.
```

## What this card does not say

**No advert was found on any of the three services, so none is claimed** — and the
absence is a property of the OBJECT, not of the route: all three answer 200 to the
declared client, nothing is refused in writing on their employment paths, and
nothing here is declared closed (§2 sexies). Osakidetza's own bolsa was not read;
only its host's rule state and the Basque-language entry point are measured.
`resuelve.ayesa.link` and the VEC application on `ws027.sspa.juntadeandalucia.es`
were named by the pages and not fetched.

**And the separate question this card deliberately does not open:** whether the
`convocatorias` each service publishes in its official gazette — `bocm.es` for
Madrid, the BOJA for Andalucía — form an enumerable stream. That is a different
object again, with a different cadence, and the Andalusian portal already refuses
219 individual BOJA articles in writing.
