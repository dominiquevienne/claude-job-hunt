# Board adapter — Jobinja (`jobinja.ir`, «جابینجا», Iran): la liste du site contre le compte que le site énonce lui-même — «۱۶,۲۰۱ فرصت ‌شغلی» **فعال** en chiffres persans, vingt cartes par page, pager à 811 pages le 2026-09-22 — et le JobPosting de l'annonce ; `jobinja.py`, **le sexe que le board imprime à côté de chaque annonce n'est pas propagé** (#183)

<!-- verified: 2026-09-22 -->

<!-- hosts: jobinja.ir -->
<!-- script: jobinja.py -->
<!-- countries: IR -->
<!-- content: measured · **2026-09-22 07:49–07:55 UTC, le client déclaré, la garde sur le chemin exact. Règles (relues ce jour) : `User-agent: *` — `Disallow:` (directive vide : rien n'est refusé) puis `Disallow: /style_guide/` ; **une chaîne de requête est donc permise ici**, contrairement à `jobvision.ir` dont les règles refusent `*?*`, et le `?page=N` de la liste EST la route. `/jobs` 200 (250 680 B) énonce **«۱۶,۲۰۱ فرصت ‌شغلی» + «فعال»** — 16 201 opportunités ACTIVES, en chiffres persans — et vingt cartes `li.o-listView__item` : titre et adresse `/companies/<employeur>/jobs/<id>/<slug persan>` (paramètres de suivi `_ref`/`_t` **retirés de ce qui est émis**), employeur, ville, âge relatif («امروز»). Le pager nomme sa dernière page : **811** (811 × 20 = 16 220, soit les 16 201 énoncés plus une page partielle). `jobinja.py jobs --pages 3` en direct : **60 émis**, le compte énoncé ayant bougé à 16 203 entre deux lectures — une liste vivante. L'annonce (101 193 B) : un `JobPosting` — `title`, `hiringOrganization.name`, `datePosted`, `baseSalary` (devise IRT, valeur, unité), `employmentType`, `jobLocation`, `jobLocationType` — à côté des champs libellés de la page (موقعیت مکانی, نوع همکاری, حداقل سابقه کار, حقوق, حداقل مدرک تحصیلی) ; un id absent → 404 (exit 3)** · 2026-09-22 -->
<!-- witness: le compte que la page énonce elle-même, «۱۶,۲۰۱ فرصت ‌شغلی» marqué «فعال» (actives), lu en chiffres persans et imprimé à côté du compte émis ; une lecture bornée par `--pages` le DIT et n'est pas comparée au total · 2026-09-22 -->
<!-- route: http · 16201 · 2026-09-22 -->

```
jobinja.py jobs [--pages N | --all]      # vingt par page ; «N émis … le site énonce M «فعال»»
jobinja.py ad --url https://jobinja.ir/companies/<employeur>/jobs/<id>/<slug>
```

**LE SEXE N'EST PAS PORTÉ.** Chaque annonce imprime «جنسیت : زن» (sexe :
femme) comme critère de recrutement. Le dépôt sert l'annonce et **ne propage
pas le critère** (#183 — et `jobcentrebrunei.py` fait de même avec une
tranche d'âge) : le champ n'est jamais émis, et chaque ligne **dit ce qui a
été laissé** — `criteria_withheld: ["gender"]` — pour qu'un silence ne se
lise pas comme une absence.

**La clé est l'id court du site, jamais le slug.** Le slug est le titre
persan ; son repli ASCII est vide, et une clé vide collisionne — mesuré la
même semaine sur Jobvision : 50 097 slugs sur 56 095 se replient sur rien. La
garde l'asserte (39 lignes, 39 clés distinctes, titres persans compris).

**Deux détails de forme qui ont chacun coûté une lecture :** la carte du
board contient des `<li>` imbriqués, donc une coupe `<li …>(.*?)</li>` perd la
ville et le contrat (la garde rougit si on la restaure) ; et l'adresse des
cartes porte les paramètres de suivi du board (`_ref`, `_t`) — **ce qui est
émis est un lien, pas une trace**, et ils ne sont pas non plus envoyés sur
`ad`.

**Retenu :** adresses e-mail et téléphones de tous les textes (chiffres
persans compris), le logo de l'employeur, la route de candidature, le critère
de sexe ci-dessus ; `contacts_withheld` sur chaque ligne.

**Garde** `AListThatStatesItsOwnCountInPersianDigitsAndPrintsACriterionWeDoNotCarry`
dans `tests/test_core.py` — dans les deux sens (chiffres persans lus comme un
nombre, lecture bornée dite bornée, marche complète comparée au compte
énoncé et `short` → 6, `<li>` imbriqués, paramètres de suivi retirés, id
répété une fois, clé jamais repliée depuis le slug, sexe jamais émis et
toujours nommé comme retenu, contacts épurés, 404 → 3, autre hôte refusé
avant la garde). Banc de mutations 2026-09-22 : **10 mutations, 10 rouges**.

**Found by the Iran search of #600 (a country never searched), measured
2026-09-17 09:25–09:26 UTC by the declared client, the guard on the exact
path first, `bin/fetch-body.py`, two reads of the root.** The host was named
by two independent lists (a technology magazine's ranking and a training
centre's list, both found by the search written on #600) and by the search
engine's own result for «سایت کاریابی استخدام ایران». *A measurement, not
an adapter: the adapter is its own `adapter` issue, opened with this card.*

## What was read

```
_robots.allowed('jobinja.ir', '/')     open, certain
GET https://jobinja.ir/                 200 twice — see the content line for sizes and fingerprints
```

«۱۶,۰۷۹ آگهی» on the root, 16 079 in Persian digits. Nothing past the root was read: the list route, the pager,
the ad page and what it carries (a JobPosting or the site's own markup) are
the first line of the adapter, as every `adapter` issue of #291 says.

## What this card does not say

Nothing about the board's markup, its ids or its contacts — not read.
Nothing about the operator's intention beyond the rules file, which refuses
nothing on `/`. *A host served today is a host served today.*
