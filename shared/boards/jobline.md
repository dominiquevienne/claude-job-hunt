# Board adapter — Jobline (`www.jobline.hu`, Hungary): the root is the operator's own notice — «the operation of the Jobline.hu job portal is suspended from 31 January 2026, the site is no longer available» — every other path 404; measured 2026-09-14, no adapter, `route: none` (#361)

<!-- verified: 2026-09-14 -->

<!-- hosts: www.jobline.hu -->
<!-- script: none -->
<!-- countries: HU -->
<!-- content: measured · **the root answers 200 with 11 623 B (md5 692f6b493000, the same the country search read on 2026-09-13 17:00) whose whole text is a notice in Hungarian: «Tájékoztatunk, hogy a Jobline.hu álláskereső portál üzemeltetését 2026. január 31-től szüneteltetjük, az oldal a továbbiakban nem érhető el» — the operator (HVG) suspended the portal from 2026-01-31 and points readers to hvg.hu; the page is a saved-page artifact (`./Jobline.hu_files/…`, a maintenance favicon on cdn.hvg.hu) with no data route; `/allasok`, `/allas`, `/kereses` answer 404 with 0 bytes (02:47 UTC)** · 2026-09-14 -->
<!-- witness: none — there is no list, no count and no ad page: the site states, in its own words, that it is suspended · 2026-09-14 -->
<!-- route: none · non faisable — validé par le propriétaire le 14.09.2026 (verbatim : « 1, 2, 3 => exclure. Plus disponible ») — measured: the operator's own notice: «Jobline.hu … üzemeltetését 2026. január 31-től szüneteltetjük, az oldal a továbbiakban nem érhető el» on the root, 404 on every other path — a route to nothing, by the site's own statement; the verdict of closure is the owner's (§2 sexies) · 2026-09-14 -->

**What #291 bloc C read as «a shell rendered client-side» is the
operator's farewell.** The root's 11 623 bytes are thirteen tracking
scripts saved with the page (`cmp2.js`, `fbevents.js`, `hotjar-284291.js`,
`analytics.js`… under `./Jobline.hu_files/`) and 389 characters of text:

> *Tájékoztatunk, hogy a Jobline.hu álláskereső portál üzemeltetését 2026.
> január 31-től szüneteltetjük, az oldal a továbbiakban nem érhető el.
> Köszönjük, hogy az évek során használtad a Jobline.hu szolgáltatásait.*

— «we inform you that the operation of the Jobline.hu job-search portal
is suspended from 31 January 2026; the site is no longer available. Thank
you for using Jobline.hu over the years» — followed by links to `hvg.hu`,
HVG Rendezvények and HVG Könyvek. Measured 2026-09-14 02:46–02:47 UTC by
the declared client, guard on the exact path:

| address | answer |
| :-- | :-- |
| `/robots.txt` | 200, 1 248 B — the Cloudflare content-signals preamble and not one directive; open, `certain: True` |
| `/` | 200, 11 623 B, md5 `692f6b493000` — the notice; the same md5 the country search read on 2026-09-13 |
| `/allasok`, `/allas`, `/kereses` | 404, 0 B |

There is no data route behind a notice: no list, no search, no ad page, no
sitemap named. **`route: none`, by the site's own statement** — a route to
nothing, dated. Whether Jobline is *closed* to this project is the owner's
word (§2 sexies); what this card records is that the operator says the
portal is suspended, and since when. Hungary's read boards on this day:
Profession.hu (`profession.md`) and the public Virtuális Munkaerőpiac
(`vmp.md`).

## If the portal comes back

The day `/` serves something other than the notice — a list, a search
form, a count — the measurement starts again from the rules and the root;
nothing here presumes what the board's routes were.

## 2026-09-14 04:4x UTC — the owner's decision, and this card's verdict is his

**non faisable — validé par le propriétaire le 14.09.2026 (verbatim : « 1, 2, 3 => exclure. Plus disponible »)** — relayed verbatim by the pilot (#361). What was measured above is
unchanged; what changes is who says «closed»: until this line the card
could only say what it had read and that the verdict was the owner's to
give (CLAUDE.md §2 sexies) — he has given it. The `route: none` line
leads with it, dated, so the Atlas and the country page (#404: a card
declaring `route: none` is «non faisable», excluded from the feasible
denominator) read a decision and not a measurement. A re-measure stays possible — the operator's notice is dated and quoted above — but it is not owed: the owner has excluded the board.
