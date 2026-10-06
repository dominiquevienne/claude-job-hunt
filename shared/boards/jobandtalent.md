# Board measurement — Jobandtalent (`jobs.jobandtalent.com`, five country fronts): temporary and shift work — **the offers live on a THIRD host that neither corporate `robots.txt` mentions, and the two obvious hosts are both wrong**: `www.jobandtalent.es` refuses every query string while its declared sitemap holds 120 URLs and not one advert; the offers host states **117 adverts** which are **149 posts** on the 25 read, and ships the complete workplace address — street, number, postcode and coordinates — on 25 of 25

<!-- verified: 2026-10-05 -->

<!-- hosts: jobs.jobandtalent.com, www.jobandtalent.es, www.jobandtalent.com -->
<!-- script: none -->
<!-- countries: CO ES GB SE US -->
<!-- host-forms-basis: read and unrecognised — THREE hosts, and they do not answer alike: `www.jobandtalent.es` serves 232 B (md5 29939a67918a, `state: read`, `certain: True`) and `www.jobandtalent.com` serves 233 B (md5 77b931b81147), the two files IDENTICAL except for the sitemap they declare (ES against US); `jobs.jobandtalent.com`, where the offers actually are, serves 99 B that are a SINGLE COMMENT LINE with no `User-agent` and no directive, so `state: unrecognised`, `certain: False` — an absence of rules under #283, and nothing refused · 2026-10-05 -->
<!-- content: measured · **117 adverts are stated by the board and they are 149 POSTS on the 25 read, which are two counts answering two questions: `jobs.jobandtalent.com/es/` (261 349 B) carries an HTML-ESCAPED JSON hydration payload of 97 181 escaped characters holding `csrfToken` and `defaultState`, whose `totalNumber` is 117 and `perPage` is 25 — five pages — while the 25 `jobOpportunities` records sum `vacancies_total` to 149 with one advert carrying 50. So an advert is not a post here, and neither figure may be published as the other. THE OFFERS ARE ON A THIRD HOST AND THE TWO OBVIOUS ONES ARE BOTH WRONG: `www.jobandtalent.es` and `www.jobandtalent.com` serve rules files identical except for the sitemap each declares (ES against US), and the ES one holds 120 `<loc>` of which NOT ONE is an advert or a listing — `/empresas` 65, `/noticias` 38, `/legal` 9 and `/candidatos` only 2, the second being `descarga-app`; `/empleo` and `/trabajo` both answer 404 at 19 684 B. The candidate page names «Ofertas de trabajo» and points it at `https://jobs.jobandtalent.com/es/`, a host neither rules file mentions and whose rules bind separately. AND THE QUERY-STRING RULE I MEASURED BELONGS TO THE WRONG HOST: the corporate hosts write `Disallow: /*?*` with five `Allow` exceptions in `?page=*` form, and the guard refuses `/empleo?page=2` and `/trabajo?page=2` while permitting `/emprego?page=2` — a Portuguese word in a list shipped unchanged to every country front. On the offers host none of that applies, and the advert links carry `?locale=es`, which `/*?*` would have refused. THE FIELDS, on 25 records: `salary` is non-empty on 25 and names its currency AND its period on 25 (`13.17 EUR hourly`; hourly 24, monthly 1), and `pay_rate` adds `base_salary`, `base_salary_period` and `currency_code` filled on 25 while `variable_pay` and `expenses` are empty on 25, so `if x` on `pay_rate` counts twenty-five and only the subfields decide. FOUR DATE FIELDS THAT ARE NOT THE SAME QUANTITY: `created_at` 9 distinct over 2026-09-04 to 2026-10-05; `start_date` 5 distinct; `end_date` 15 distinct reaching 2027-01-31; `valid_through` 5 distinct and STRICTLY BELOW `end_date` on 24 of 25 — so `valid_through` is a deadline to apply and `end_date` the contract's end, and treating either as the other would be wrong on nearly every advert. THE ADDRESS IS COMPLETE AND MUST NOT BE EMITTED: `geodatum` carries `street`, `street_number`, `postal_code` and `coordinates` on 25 of 25 plus `formatted_hidden_location` on 25, and `formatted_location` holds a five-digit postcode on 25 of 25 and a street number on 19. `company_name` is filled on 25 and `hide_company_info` is FALSE on 25 — the board owns a flag to conceal the employer and never sets it on this page. Zero e-mail addresses and no key matching phone, email or tel. METHOD: guard on each of the three host forms and each exact path in turns distinct from the retrievals, `bin/fetch-body.py` throughout, the 404s kept only under `--allow-refusal`, no `Crawl-delay` written anywhere so 2 s are ours** · 2026-10-05 -->

<!-- witness: the offers host states its own total twice — `totalNumber: 117` with `perPage: 25` inside the hydration payload, and `117` in the visible header — read 2026-10-05, and it counts ADVERTS; the 25 records read sum `vacancies_total` to 149, which counts POSTS, so the two are different grandeurs and neither is offered as the other. The declared corporate sitemap's 120 `<loc>` are not adverts and are no witness of anything about the board · 2026-10-05 -->

## Measured 2026-10-05 — 117 adverts that are 149 posts, on a third host neither rules file names

```
TROIS hotes, et les deux evidents sont les mauvais
  www.jobandtalent.es        232 o  md5 29939a67918a  read, certain
  www.jobandtalent.com       233 o  md5 77b931b81147  read, certain
    les deux fichiers IDENTIQUES sauf le sitemap declare (ES contre US)
    groupe *                 Disallow: /*?*   + 5 Allow en ?page=*
      /emprego?page=*  /emprego/*?page=*  /empresas/blog?page=*
      /foretag/blogg?page=*  /companies/blog?page=*     <- emprego = portugais
                                                           foretag = suedois
    la garde, eprouvee dans les DEUX sens :
      /empleo?page=2         False  rule /*?*       <- l'espagnol est REFUSE
      /trabajo?page=2        False  rule /*?*
      /emprego?page=2        True   rule /emprego?page=*
  jobs.jobandtalent.com       99 o  UNE LIGNE DE COMMENTAIRE, zero directive
                                    state unrecognised, certain False -> rien refuse
le sitemap ES DECLARE       23 441 o  120 loc / 120 distincts
  /empresas 65 · /noticias 38 · /legal 9 · /candidatos 2 · divers 6
  annonces ou listes                AUCUNE sur les 120
  120 lastmod                       UNE valeur : 2026-10-05 (date de BUILD)
/empleo · /trabajo                  404, 19 684 o chacun (la MEME page)
/candidatos                70 316 o  « Ofertas de trabajo » -> jobs.jobandtalent.com/es/
                                    seul lien d'app : l'App Store
jobs…/es/                 261 349 o  charge JSON ECHAPPEE en HTML, 97 181 car.
  defaultState.totalNumber          117        <- le board l'enonce, DEUX fois
  defaultState.perPage              25         -> 5 pages
  jobOpportunities                  25 enregistrements
  somme de vacancies_total          149        <- des POSTES, pas des annonces
  forme d'annonce                   /es/<fonction>/<province>/<slug>?locale=es
  salary                            25/25, monnaie ET periode 25/25
                                    hourly 24 · monthly 1
  pay_rate                          25/25 ; base_salary, period, currency 25/25
                                    variable_pay 0/25 · expenses 0/25
  company_name                      25/25   ·  hide_company_info FALSE 25/25
  geodatum.street / number / postal_code / coordinates      25/25 chacun
  formatted_location  code postal   25/25    numero de rue  19/25
  courriels · cles de contact       0 · AUCUNE
```

**Found by the Spain pass of #949.** *The offers host carries five country fronts — `/co`, `/es`,
`/gb`, `/se`, `/us` — so this card declares `CO ES GB SE US`.*

### `robots.txt` binds a host, and here it took three hosts to find the one that matters

**The two obvious hosts both answer, both serve rules, and neither serves the offers.** *Their
files are identical to the byte except for the sitemap each declares — ES on one, US on the other —
which is exactly the kind of difference that reads as "the same site, localised".*

**The offers are at `https://jobs.jobandtalent.com/es/`, and the only thing that says so is the
candidate page's own menu.** *Neither rules file mentions that host; its rules bind separately, and
they are 99 bytes containing a single comment line.*

> **And the consequence runs the other way from Bast.af.** *There the corporate host refused our
> path in writing while the data sat on a sibling with no rules, so reading the refusal would have
> declared a board closed.* **Here the corporate host's refusal is real, specific, and simply
> about something else** — and my own guard, taken carefully and exercised in both directions, was
> answering a question about a host that serves no advert.

**What that guard established, correctly and irrelevantly:** `Disallow: /*?*` closes every query
string to `*`, with five `Allow` exceptions all in `?page=*` form. **`/empleo?page=2` and
`/trabajo?page=2` are refused; `/emprego?page=2` is permitted** — *and `emprego` is Portuguese or
Galician, `foretag/blogg` Swedish: one list shipped unchanged to every country front, so the
pagination it opens is not the pagination a Spanish listing would use.*

**On the offers host none of it applies**, and the advert links carry `?locale=es` — *a query
string, which `/*?*` would have refused had the offers lived where the sitemap does.*

### The declared sitemap is a corporate site, and 120 is small enough to read

**120 `<loc>`, and not one is an advert or a listing.** *`/empresas` 65 (platform marketing, case
studies, a demo request), `/noticias` 38, `/legal` 9, and `/candidatos` **two** — the second being
`descarga-app`.*

*The seven paths that match an offer keyword are blog and news slugs where the word appears in
passing* — «&nbsp;el impacto de la IA en los trabajos esenciales&nbsp;». **Reading all 120 rather than
sampling six is what settled it**, and 120 is small enough that sampling would have been a choice
rather than a necessity.

**And `/empleo` and `/trabajo` both answer 404 at 19 684 bytes — the same page twice**, so the
absence of a Spanish listing on that host is measured and not inferred from the sitemap.

*Its 120 `lastmod` carry a single value, the day of the reading: a build stamp, the third board in
this pass to do that.*

### 117 was invisible to two instruments, for two opposite reasons

| how I looked | what I saw | why |
| :-- | :-- | :-- |
| in the TAG-STRIPPED text | «&nbsp;117 jobs&nbsp;», looking fabricated | adjacency manufactured by stripping; the same pass produced «05 4 jobs» |
| in the MARKUP, as `>117 jobs<` | **nothing** | a `</span>` sits between the number and the word |
| in the raw markup WITH CONTEXT | **real, stated twice** | `"totalNumber":117` in the payload, and `<span …>117</span>jobs` in the header |

> **The same figure read as an artefact and then as an absence, and only looking at the raw bytes
> around it settled which.** *«&nbsp;A string has several forms at the point of call&nbsp;» is a line
> here already; this is that line applied to a NUMBER, where the two failures point in opposite
> directions and each looks like diligence.*

### An advert is not a post, and both counts are real

**`totalNumber` is 117 and counts ADVERTS. The 25 records read sum `vacancies_total` to 149, and
one advert alone carries 50.**

> **So «&nbsp;how many jobs&nbsp;» has two true answers here, and they answer different questions.**
> *Publishing 117 as posts understates; publishing a vacancy sum as adverts overstates. Each
> number carries its own denominator or it is not published.*

### The address is complete, and that is what must not be emitted

**`geodatum` gives `street`, `street_number`, `postal_code` and `coordinates` on 25 of 25**, plus
`formatted_hidden_location` on 25. **`formatted_location` carries a five-digit postcode on 25 of 25
and a street number on 19.** *So the board ships the precise workplace, down to the door.*

*This is well-precedented rather than novel — `beesite`, `softgarden`, `prospective` and
`talentlyft` all withhold street and postcode, and Batiactu is the coordinates case* — **but it is
measured here rather than assumed, and it is every record and not a fraction.**

**And the employer is named honestly on this page**: `company_name` filled on 25 of 25 with
`hide_company_info` **false on 25 of 25**. *The board owns a flag to conceal the employer and does
not use it here* — **which is the opposite of Portalento, where the placer occupied the employer
field on every advert.** *That the flag EXISTS is the thing to carry forward: a later reading may
find it set, and an adapter that ignores it would publish a name the board chose to hide.*

### Four date fields, and they are not the same quantity

| field | non-empty | distinct | range |
| :-- | :-- | :-- | :-- |
| `created_at` | 25/25 | 9 | 2026-09-04 → 2026-10-05 |
| `start_date` | 25/25 | 5 | 2026-10-05 → 2026-10-09 |
| `end_date` | 25/25 | 15 | 2026-10-08 → **2027-01-31** |
| `valid_through` | 25/25 | 5 | 2026-10-05 → 2026-10-09 |

**`valid_through` is strictly below `end_date` on 24 of 25**, and its range is five days against
`end_date`'s four months. *So `valid_through` is the deadline to apply and `end_date` the contract's
end* — **and taking either for the other would be wrong on nearly every advert.**

*A note on method, because it nearly cost something:* **a script of mine printed «&nbsp;25/25 expire
today&nbsp;» as a conclusion, while the measurement immediately above it said 1 of 25.** *I had written
the conclusion into the output instead of deriving it from the numbers beside it — a bench that
asserts rather than measures, and the fix is that a bench prints only what it computed.*

### What an adapter would do

```
route   : http on jobs.jobandtalent.com — NOT on www.jobandtalent.es, whose
          `Disallow: /*?*` is real and governs a host with no adverts. 2 s pace
          (no Crawl-delay anywhere). Advert links carry ?locale=es.
witness : defaultState.totalNumber (117 on 2026-10-05), perPage 25 -> 5 pages.
          Print «N emitted, the board states 117» so a shortfall shows.
counts  : report adverts and posts SEPARATELY. 117 adverts; the 25 read sum 149
          vacancies_total, one of them 50. Never one figure for both questions.
parse   : the payload is HTML-ESCAPED JSON in an attribute — unescape, then
          json. Address `jobOpportunities` BY NAME, not as "the longest list":
          `jobFunctions` has 62 entries and is not adverts.
carries : title, company_name (while hide_company_info is false — HONOUR the
          flag, it exists), description, responsibilities, timetable,
          job_function_slug, locality, created_at, start_date, and the salary
          with its currency AND period (hourly on 24 of 25, monthly on 1)
dates   : valid_through = deadline to apply ; end_date = contract end. They
          differ on 24 of 25 and are not interchangeable.
NEVER   : geodatum.street, street_number, postal_code, coordinates,
          formatted_hidden_location, and the street number inside
          formatted_location — the complete workplace address, on every record.
          Trim to locality. No contact field exists to withhold.
```

### What this card does NOT say

**It does not say 117 is the board's size, nor that the field rates hold beyond 25 records.** *117
is what one country front states on one date; the five fronts were not summed and their overlap is
unknown.* **And every rate above — salary on 25 of 25, the address on 25 of 25, `hide_company_info`
false on 25 of 25 — comes from the FIRST page of the Spanish front.** *A second page and a second
front are the first things to measure.*

**Measured 2026-10-05 by the declared client, the guard taken on each of the three host forms and
each exact path in a turn distinct from the retrieval, `bin/fetch-body.py` throughout, the 404s kept
only under `--allow-refusal` so their status travels in their records, DNS on two public resolvers.**
*No value of any address or coordinate field was printed at any point — only counts.* *A measurement,
not an adapter.*

```
_robots.verdict('www.jobandtalent.es')      state: read,          certain: True,  232 B
_robots.verdict('www.jobandtalent.com')     state: read,          certain: True,  233 B
_robots.verdict('jobs.jobandtalent.com')    state: unrecognised,  certain: False,  99 B
allowed('www.jobandtalent.es', '/empleo?page=2')    False  (rule '/*?*')
allowed('www.jobandtalent.es', '/emprego?page=2')   True   (rule '/emprego?page=*')
allowed('jobs.jobandtalent.com', '/es/?page=2')     True   (no rules at all)
GET www.jobandtalent.es/assets/sitemaps/ES/sitemap.xml   200, 120 <loc>, 0 advert
GET www.jobandtalent.es/empleo · /trabajo                404 x2, 19 684 B each
GET www.jobandtalent.es/candidatos                       200, 70 316 B
GET jobs.jobandtalent.com/es/                            200, 261 349 B, totalNumber 117
```
