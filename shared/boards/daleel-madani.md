# Board measurement — Daleel Madani jobs (`daleel-madani.org/jobs`, Lebanon): the civil-society network's job board (NGO vacancies) — on 2026-09-17 every read answers HTTP 403 with a 5.5 KB «Just a moment...» page, the fingerprint moving: a Cloudflare challenge; consigned, not defeated (borne 2); a tab is the next reading

<!-- verified: 2026-09-28 -->

<!-- hosts: daleel-madani.org -->
<!-- script: none -->
<!-- countries: LB -->
<!-- content: measured · **188 adverts stated by the site and the list SERVED in a tab on 2026-09-28 — «Displaying 1 - 20 of 188», 20 per page over a sliding pager, so ten pages.** *The interstitial resolves BY ITSELF after ~12 s: no click, no captcha, no puzzle, and the site writes what is happening («Cette page s'affiche pendant que le site verifie que vous n'etes pas un bot»). Borne 2 is respected and the distinction is the one that matters — nothing was defeated, a real browser was served after ITS OWN verification.* **Per advert the list carries: title, organisation, country, region and city, contract type, and the application DEADLINE.** *The declared HTTP client stays refused — 403 «Just a moment...», both size and fingerprint moving on the 2026-09-27 re-measurement — and the two facts coexist without contradicting: the challenge closes the HTTP route and opens to a browser.* **THIS LINE EXISTS BECAUSE THE MEASUREMENT WAS ALREADY IN THIS CARD AND NOTHING READ IT: the 2026-09-17 `content: indeterminate` line below says «nothing of the board was read», and being FIRST it was the one the tooling parsed** — `read_cards()` does a `setdefault`, so the first occurrence wins. *A new measurement that nothing reads has exactly the shape of a measurement made: it is in the file, it is dated, it is right, and no artefact carries it.* · 2026-09-28 -->
<!-- content: indeterminate · **`/jobs` answers HTTP 403, 5 551 then 5 572 B, md5 c37422907d09 / c120d88602b2 — «Just a moment...», a Cloudflare managed challenge (the `revolico` class: same title, moving fingerprint) — under the declared identity, twice; the rules file could not be read (absence of rules, `certain: False`); nothing of the board was read** · 2026-09-17 -->
<!-- witness: partial — **188 stated by the site in its own «Displaying 1 - 20 of 188» string, and 20 adverts served per page over a pager of ten pages**; the count is the HOST's and not our extraction, and no page beyond the first was walked, so the walk is PARTIAL. *The pager's last page was never requested, so the board's size rests on the site's own statement alone* · 2026-09-28 -->
<!-- witness: none — nothing was served · 2026-09-17 -->
<!-- route: browser · 188 · 2026-09-28 -->
<!-- route-http: none · le defi Cloudflare tient — REMESURE le 2026-09-27 16:1x UTC, deux lectures : 403, 5 569 puis 5 548 o, md5 2eb0dac98bd9 / 09bd6890f9ba, titre «Just a moment...» ; **la TAILLE et l'empreinte bougent toutes deux**, donc c'est un defi et non un refus statique. Borne 2 : on ne le dejoue pas et on ne demande a personne de le dejouer. La lecture suivante est un onglet, pour voir si la page est servie SANS CLIC. Consigne, pas un verdict (§2 sexies) · 2026-09-27 -->


## La route navigateur est MESUREE, et le defi n'a pas ete dejoue

**2026-09-28 : l'onglet a ete pris, et l'interstitiel se resout de lui-meme.**

```
au chargement   « Un instant… »  ·  « Verification de securite en cours »
12 s plus tard  « Jobs | Daleel Madani »  ·  Displaying 1 - 20 of 188
```

**Aucun clic, aucun captcha, aucune enigme.** *Le site ecrit lui-meme ce qui se
passe : « Cette page s'affiche pendant que le site verifie que vous n'etes pas un
bot ».* **Borne 2 est respectee et c'est la distinction qui compte : nous n'avons
rien dejoue — un vrai navigateur a ete servi apres SA propre verification.** *Un
defi qui exigerait un clic ou une resolution nous arreterait, et nous ne pouvions
pas le savoir avant de regarder.*

**Ce que la liste porte, par annonce** : intitule, organisation, pays, region et
ville, type de contrat, **date limite de candidature**. Le compte est enonce par
le site — **188** — et la pagination est de 20, avec un pager glissant
(`1 2 3 4 … next › last »`), donc dix pages.

**Le client declare reste refuse** : 403 « Just a moment... », empreinte ET taille
mouvantes (remesure du 2026-09-27). *Les deux faits coexistent et ne se
contredisent pas : le defi ferme la voie HTTP et s'ouvre a un navigateur.*

## Ce qui manque est de NOTRE cote, et ce n'est pas une propriete de l'hote

**2026-09-27 16:1x UTC : la route navigateur attend un Chrome ouvert.** L'extension
n'etait pas connectee — elle l'etait le matin meme, sur d'autres hotes — donc
l'onglet n'a pas pu etre pris. *Deux tentatives, puis arret : on n'insiste pas sur
un outil absent.*

> **Cette ligne decrit notre outillage, pas le board.** *Le defi Cloudflare est une
> propriete de l'hote&nbsp;: elle se mesure et elle dure. «&nbsp;Chrome est ferme&nbsp;» est
> la meteo de notre cote, et la confondre avec la premiere ferait classer `blocked`
> ce qui est faisable dans l'heure — or ce compte decide des assignations.*

**Donc cette fiche ne conclut RIEN sur l'accessibilite par navigateur** : la
question reste ouverte et se reprend des qu'un Chrome est disponible.

**Found by the Lebanon search of #609 (a country never searched), measured
2026-09-17 13:53–13:55 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads, two public resolvers on a DNS
negative.** The method is written on #609: one search naming the boards,
the National Employment Office (ILO and UNESCWA name its e-labour
exchange at `neo.gov.lb`) and the regional aggregators (Bayt — already
`bayt.md`; Naukrigulf, Tanqeeb — regional, left aside), no composed host
names. *A measurement, not an adapter.*

```
GET https://daleel-madani.org/jobs   403, 5 551 B, md5 c37422907d09 ; 403, 5 572 B, md5 c120d88602b2 — «Just a moment...»
```

**A challenge**: the plugin neither defeats it nor asks the user to
(borne 2); whether a tab is served without a click is a browser-time
question (Revolico and Mabumbe were, 2026-09-14). INDÉTERMINÉ; the issue
says what blocks.
