# Board measurement — PEPE — IEFP Cabo Verde (`pepe.iefp.cv`, with the institute's site `iefp.cv`, Cabo Verde): the public employment institute's platform where employers post internships and vacancies and candidates apply — served to the declared client, but its vacancies are behind a candidate account («Crie a sua conta e concorra a vagas»); no public list found; the institute's `/empregos/` page is institutional

<!-- verified: 2026-09-18 -->

<!-- hosts: pepe.iefp.cv, iefp.cv -->
<!-- script: none -->
<!-- countries: CV -->
<!-- content: measured · **`pepe.iefp.cv/` (200, 9 298 B) and `/frontend/web/pt/site/mobilidade` (200, 15 442 B, md5 c1710b461ce1 / c2b81369b0b8) present the platform — «Crie a sua conta e concorra a vagas de estágio profissional/emprego», «Criar conta como Candidato / Entidade», «Faça Login» — with no vacancy list on any page read; `/frontend/web/pt/site/ofertas` answers 404; `iefp.cv/empregos/` (200, 247 077 B, md5 e69b7e830ed4 identical on two reads) is the institute's WordPress site (mission, organisation, registration forms), not a list; rules: `iefp.cv` open, certain; `pepe.iefp.cv` open, `certain: False`; no JobPosting anywhere** · 2026-09-18 -->
<!-- witness: none — no public list · 2026-09-18 -->

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

**The public employment service exists online and keeps its vacancies
behind a candidate account** — the plugin never creates one and never
logs in. No public route found by this reading; the issue says so and
what would reopen it (a public listing page, if the platform has one
the search did not surface).
