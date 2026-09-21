# Board adapter — Eritrea Job Search (`eritreajobsearch.com`, Eritrea — a node of the `*jobsearch.com` network operated from India): the only host naming Eritrea that publishes a list, «468 Jobs Available» in its own counter, read by the site's own per-page form and pager; `eritreajobsearch.py`, and a fabrication-suspected flag on EVERY row — the adverts bear the marks and nobody has established it (#549, the owner: «pourquoi les écarter ?»)

<!-- verified: 2026-09-21 -->

<!-- hosts: eritreajobsearch.com -->
<!-- script: eritreajobsearch.py -->
<!-- countries: ER -->
<!-- content: measured · **2026-09-21 09:16–09:19 UTC, the declared client, the guard on the exact path (13.09: «456 Jobs Available», cd, #420). Rules: `*` refuses the WooCommerce internals and `add-to-cart` queries, nothing else; no Crawl-delay. `/job-vacancy-eritrea/` 200 (230 722 B): ten `article.job-grid.post-<id>` cards — title, `/job/<slug>/`, `.job-location`, `.type-job`, «N views» — a pager to `/page/47/`, the site's counter `.job-count-number` **468** («Total Active Jobs in Eritrea … Jobs Available»), a per-page form `GET ?jobs_ppp=12|24|48|96|192|384|-1`; `?jobs_ppp=384` 200 (875 033 B) 384 cards, pager to `/page/2/?jobs_ppp=384`. `eritreajobsearch.py jobs` live 09:18 UTC: **468 emitted over 2 pages of 384 — the site states 468: equal** (468 distinct ids; Barentu 79, Badi 42, Asmara 35, Keren 25, Assab 23; all «Full Time»; views 0–212). The advert (`/job/<slug>/`, 148 KB): a JobPosting — `title`, `datePosted`, `validThrough` (six months on), `hiringOrganization.name`, `jobLocation.address` (a town), `baseSalary` currency **Nfk** with min/max, `description` — and the page's «Job Description» paragraphs (Position, Company, Location, Experience, Education, Employment Type, Industry, Department, **Salary: SSP 1,500,000 – SSP 2,500,000 per annum**, Vacancies, a «Company Overview»); «Apply Now» → «Please Register here as Candidate to apply» (a login, a «Pricing» page); the network's own +91 telephone and `@africajobsearch.com` addresses in every header. **An unknown slug answers 200 with the LISTING page** (no JobPosting, the counter present) — exit 3. THE MARKS, consigned without verdict: titles at one template «<role> Job Vacancy in <town>, Eritrea – <sector>»; «Deloitte Eritrea» in Zalambessa and «Huawei Technologies» in Dekemhare (border towns); the SAME salary line «SSP 1,500,000 – SSP 2,500,000 per annum» in the attorney's and the network engineer's adverts, in South Sudanese pounds while the JobPosting says Nfk; a generated «Company Overview» in each; one to six views on fresh adverts; no application route** · 2026-09-21 -->
<!-- witness: the site's own counter «468 Jobs Available» — `eritreajobsearch.py jobs` walks the form's largest option (384) by the pager and prints the counter beside the emitted count («468 emitted over 2 page(s) of 384 — the site states 468: equal»; «short» is exit 6, a counter not read is exit 6) · 2026-09-21 -->
<!-- route: http · 468 · 2026-09-21 -->

```
eritreajobsearch.py jobs [--per-page 384]          # one of the form's own options; «468 emitted … the site states 468: equal»
eritreajobsearch.py ad --url https://eritreajobsearch.com/job/<slug>/
```

**What this board is, said before it is used.** A WordPress + WP Job
Manager site (Superio theme) in a network of one-per-country clones
(`africajobsearch.com`, the same +91 telephone), with 468 adverts for a
country whose public employment service has no DNS delegation and whose UN
aggregators show two posts. The adverts read as generated: one title
template, international employers placed in border towns, a salary in the
wrong currency repeated verbatim across unrelated adverts, a marketing
«Company Overview» each, and no way to apply except registering on the
network. **None of this is established** — the measurement that would settle
it (one employer confirming or denying one advert) has not been made — and
the owner decided on 2026-09-14 to build rather than discard. So the
adapter emits what the site publishes and says on every row what is
suspected: `source_signals: ["fabrication-suspected (2026-09-21): …"]`, and
the run prints it once more. The advert record keeps the salary **as
written** (`salary_as_written`, SSP) beside the JSON-LD's currency
(`salary_currency_ldjson`, Nfk) rather than choosing between them.

**Withheld:** the network's e-mail addresses and telephones (scrubbed
wherever they appear in text), the registration link; `contacts_withheld`
on every record. Country ER on every row.

**Guard** `ANetworkNodeWhoseAdvertsBearTheMarksOfFabricationAndSayItOnEveryRow`
in `tests/test_core.py` — both ways (the form's own options only, the walk
by the pager and no further, a repeated id once, the count against the
counter, short → 6, no counter → 6, the flag on every row, the advert's
JobPosting and description with the salary as written beside the JSON-LD
currency, the network scrubbed, the listing page for an unknown slug → 3,
bad addresses and query strings refused, another host refused before the
gate). Mutation bench 2026-09-21: 10 mutations, 10 red.
