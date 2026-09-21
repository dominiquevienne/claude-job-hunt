# Board measurement — PEPE — IEFP Cabo Verde (`pepe.iefp.cv`, with the institute's site `iefp.cv`, Cabo Verde): the public employment institute's platform where employers file internships and vacancies, served to the declared client — **its two lists are public and rendered server-side**, `oferta-emprego` and `oferta-estagio`, **4 entries on 2026-09-21** (1 job, 3 internships), no pager and no stated count; `pepeiefp.py` — the account is needed to APPLY, not to read

<!-- verified: 2026-09-21 -->

<!-- hosts: pepe.iefp.cv, iefp.cv -->
<!-- script: pepeiefp.py -->
<!-- countries: CV -->
<!-- content: measured · **the two lists read by the declared client, 2026-09-21 13:51–14:05 UTC, the guard on the exact path, two reads each: `/frontend/web/pt/site/oferta-emprego` 200 ×2 (9 444 B, md5 3cb132bfe3e5 / d0ada41efc4a — **only the CSRF meta moves**, identical to the byte once that one tag is removed) carries **1 row**; `/frontend/web/pt/site/oferta-estagio` 200 ×2 (10 131 B, fa8fdc74a617 / 481d8ad6f624, same identity once the tag is removed) **3 rows**. **4 entries, and nothing states a count** — no pager either. Each list is one `<table>` whose `<thead>` names five cells — Designação, Validade, Vagas, Entidade, Referência (Designation, Validity, Vacancies, Entity, Reference in `en`) — and the adapter reads the cells by position and refuses a header that does not name exactly five. The row's own link, `/frontend/web/<lang>/oportunidades/oferta-<kind>?value=<designação>`, answered **404** in both shapes (with and without `index.php`), and so did `backend/web/index.php?r=api/empregos`, the JSON call the home page's own cards make — the two HTML lists are the route. The 2026-09-18 reading asked `/site/ofertas` (404) and concluded no public list; the platform's Angular bundle names these two. Exercised: `jobs --country-code CV` → **4 entries, «no pager and no stated count» said** · 2026-09-21 -->
<!-- witness: none — neither list states a count and neither pages; `pepeiefp.py jobs` prints what each table listed · 2026-09-21 -->
<!-- route: http · 4 · 2026-09-21 -->

**Found by the Cabo Verde search of #614 (a country never searched),
measured 2026-09-18 06:42–06:45 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #614: one Portuguese search naming the public employment institute
(IEFP and its PEPE platform) and the private aggregator, no composed host
names. *A measurement, not an adapter.*

```
GET https://pepe.iefp.cv/                                 200 — «PEPE-IEFP», account creation and login
GET https://pepe.iefp.cv/frontend/web/pt/site/mobilidade  200 ×2 — the mobility service, «Crie Sua Conta»
GET https://pepe.iefp.cv/frontend/web/pt/site/ofertas     404
GET https://iefp.cv/empregos/                             200 ×2, identical — the institute's WordPress site, no list
```

**What that reading concluded, and what 2026-09-21 corrected:** «the public
employment service exists online and keeps its vacancies behind a candidate
account, no public route found by this reading» — *true of the pages it
asked, and false of the platform.* The two lists below were found three days
later in the platform's own Angular bundle. **What holds from it**: the
plugin creates no account and never logs in — applying still requires one.

## The adapter — `pepeiefp.py` (#693, 2026-09-21)

```
GET /frontend/web/pt/site/oferta-emprego   200 ×2 — 1 row  (khym Negoce Lda, ref 176/2024, valid to 02-06-2027)
GET /frontend/web/pt/site/oferta-estagio   200 ×2 — 3 rows (CONTACOF ×2, VZP Importações)
GET /frontend/web/pt/oportunidades/oferta-emprego?value=khym+negoce+lda   404 — the row's OWN link
GET /backend/web/index.php?r=api/empregos                                 404 — the home cards' JSON call
```

**The issue's premise was stale, and this is the reading that reopened it.**
#693 recorded, on 2026-09-18, «aucune route publique trouvée par cette
lecture ; ce qui rouvrirait l'issue : une page de liste publique de la
plateforme que la recherche n'a pas fait remonter» — the search had asked
`/frontend/web/pt/site/ofertas`, which answers 404. The platform's Angular
bundle (`main.4fea70c6e545a598091f.js`) names the two pages its home cards
link to, and **both answer 200 with no account and no login**. *The account
is needed to APPLY, not to read — two different statements about one
platform, and only the first was measured in September.*

**The header is the lock.** Each list is one table; the adapter reads the
five cells **by position** and refuses any header that does not name exactly
five, because a column added or dropped would shift every field in silence —
and a shifted field is a plausible wrong answer, not a crash. A row whose
cell count disagrees with the header dies too, and each says which of the two
it was.

**The row's own link is published, dated, and never followed.** The list
writes its hrefs unquoted (`<a href=/frontend/web/...>`); the address it
publishes answered 404 on the day in both path shapes, so the record carries
it with `url_answered_404: "2026-09-21"` rather than dropping it or
pretending it resolves. A detail page that comes back is a change on their
side.

**A reference has the shape of a telephone number.** «176/2024» matches the
adapter's phone pattern to the character; the platform's filing numbers are
spared by name, and an e-mail or a real number in any cell is still withheld
(«(+238) 261 64 46» → «[telephone withheld]»). `contacts_withheld` on every
record.

`--kind` picks a list (`emprego`, `estagio`, `both` — default both), `--lang`
the interface language (`pt`, `en`, `fr`; the entries are Portuguese whatever
it says, and the run does not translate), `--country-code` STAMPS and says so.

**Tests and mutations.**
`APublicPlatformWhoseTableHeaderNamesItsCellsAndWhoseOwnRowLinkIsGone`, both
ways on fixtures (five cells read by position, the quoted and the unquoted
href, the reference spared and the number withheld, a six-cell header, a row
that disagrees with its header, a 200 without a table, a 404 on a list, an
empty tbody as 0 entries and not an error, a bad `--lang`, the `www.` host
refused). Mutation bench on a detached copy, `python3 -B`, **9 / 9 red**: the
header check loosened · the row cell count dropped · the reference exception
dropped · the scrub dropped · the unquoted-href branch dropped · the «no
stated count» note dropped · the 404-on-the-row-link note dropped · the host
check dropped · the day and month swapped in the deadline.
