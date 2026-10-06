# Board measurement — Bast.af (`www.bast.af`, Afghanistan): «Find Jobs, Careers & Employment Opportunities in Kabul» — **the route is `db.bast.af/api/get_post_jobs`, a DIFFERENT HOST that publishes no `robots.txt`, and it states 11 adverts and KEEPS it**; `www.bast.af` refuses `/api/` in writing and that refusal does NOT govern the data host, which is the whole finding; nothing is signed and nothing had to be defeated; **`bastaf.py` reads it, asserts the stated total, and talks to `db.bast.af` ALONE**

<!-- verified: 2026-10-02 -->

<!-- hosts: www.bast.af, db.bast.af -->
<!-- script: bastaf.py -->
<!-- countries: AF -->
<!-- content: measured · **11 adverts, and the board's own stated total HOLDS: `GET https://db.bast.af/api/get_post_jobs` answers 200 with `total_jobs: 11`, and the walk reads 11 distinct ids across two pages (10 then 1), `?page=99` returning an empty `data` with `has_more_pages: false`. WHAT THE ROUTE DOES NOT RETURN: nothing server-side — `/`, `/jobs` AND `/job-list` all serve one identical 4 871 B SPA shell with no advert and no count, and the declared sitemap carries 14 hand-written section URLs and ZERO advert, so neither is an enumerator. AND THE ROUTE LIVES ON A HOST THE RULES OF `www` DO NOT GOVERN: `www.bast.af` refuses `/api/` IN WRITING, but the data host `db.bast.af` publishes no rules at all, so reading `www`'s refusal as the verdict would have declared an open board closed. 34 fields per advert, `job_status: active` on 11/11, `countries: AF` on 11/11, `post_date` 2025-10-12 → 2026-09-08, zero past deadlines; the literal string `"undefined"` is stored as a VALUE on six fields (`number_Of_vacancy` truthy on 11 and real on 2, `email` truthy on 10 and real on 4); `gender` is posed on 3 of 11 and is not propagated (#183); nothing is signed — `Bearer` only when a user is logged in. METHOD: `www.bast.af/robots.txt` 485 B (`state: read`, `certain: True`, group `*`, `Crawl-delay: 1`, `Disallow: /candidates-dashboard/ /employers-dashboard/ /admin/ /api/ /private/`); the shell md5 `cc04db6aba3e` is IDENTICAL to the 2026-09-17 reading, so unchanged in two weeks; it carries two `ld+json` (a `WebSite` and an invented `@type: JobBoard`, not a schema.org type) and one bundle `/assets/index-7d427d26.js` (2 843 014 B) naming `baseURL: "https://db.bast.af/api"`; `bast.af/sitemap.xml` 2 949 B, every `lastmod` 2024-01-15; `db.bast.af/robots.txt` HTTP 404 → `state: absent`, `certain: True`, no `Crawl-delay`, so 2 s are ours; 27 resources requested through one wrapper, the public pair being `get_post_jobs` and `post_jobs/<id>`; list body 169 690 B** · 2026-10-02 -->
<!-- content: measured · **the root (200, 4 871 B, md5 cc04db6aba3e identical on two reads) is a JavaScript shell titled «Jobs in Afghanistan | Bast.af …» with no card, no count and no JobPosting in its markup; `_robots.allowed('www.bast.af','/')` → open, certain; whether the route the shell calls serves the client, or only a tab, is the adapter's first line** · 2026-09-17 -->
<!-- witness: `total_jobs` = 11 stated by the API, and the walk reads 11 distinct ids across two pages — the total HOLDS, verified in the same read · 2026-10-02 -->

<!-- witness: none — the root is a shell · 2026-09-17 -->

## Re-measured 2026-10-02 — the route exists, and it lives on a host the rules of `www` do not govern

```
www.bast.af/robots.txt   485 o   read, certain, groupe *, Crawl-delay 1
                                 Disallow: /candidates-dashboard/ /employers-dashboard/ /admin/ /api/ /private/
/  ·  /jobs  ·  /job-list        LA MEME coquille, 4 871 o, md5 cc04db6aba3e  (= celle du 17.09)
bast.af/sitemap.xml    2 949 o   14 URL de sections, lastmod 2024-01-15 partout, ZERO annonce
/assets/index-*.js 2 843 014 o   baseURL: "https://db.bast.af/api"
db.bast.af/robots.txt    ABSENT  HTTP 404 -> state: absent, certain: True, aucun delai ecrit
GET db.bast.af/api/get_post_jobs   200   total_jobs 11   page 1 -> 10   page 2 -> 1   page 99 -> 0
UNION 11  =  TOTAL ANNONCE 11      le temoin TIENT
```

**The blocker this issue carried — «&nbsp;Route&nbsp;: à mesurer en première ligne&nbsp;» — is cleared, and the
answer turned on a host name.**

### `robots.txt` is per-HOST, and reading `www`'s rules as the verdict would have closed an open board

`www.bast.af` refuses `/api/` **in writing**, to the `*` group that applies to us. *Read as the
verdict on the data route, that is a `Disallow` on our path — borne 1 — which blocks every route,
browser included, and would have sent «&nbsp;this board refuses us in writing&nbsp;» to the owner under
§2 sexies.*

> **But the data route is `db.bast.af/api/…`, and `robots.txt` binds a HOST, not a brand.** *`www`'s
> `Disallow: /api/` governs a path on `www` that may not even exist.* **The host that actually
> serves the adverts publishes no rules at all**, so it is open and `certain` — by the 404 branch,
> which is KNOWLEDGE.

**This is exactly what §3 bis exists for&nbsp;: «&nbsp;garder l'URL exacte qu'on s'apprête à récupérer,
HÔTE COMPRIS&nbsp;».** *The trap is sharper here than for a sitemap on a sibling host, because the
sibling's rules are not merely ABSENT — they are PRESENT and they say no.* **A refusal read on the
wrong host is a false closure that nothing downstream would contradict.**

*And the `certain: True` here is the `absent` branch, not the `read` branch (§2 quater)&nbsp;: the host
looked and there is no file. **Not** «&nbsp;the rules file is served&nbsp;» — the two print the same word
and a glose that confuses them conflicts with nothing.*

### The witness holds, and the pager is honest

`pagination` declares `{current_page, last_page, per_page 10, total 11, has_more_pages}` and tells
the truth at every step: 10 then 1, and `page=99` returns an empty `data` with
`has_more_pages: false` rather than looping or clamping. **`promoted` is an empty list** — it is not
a second inventory, and it is named here so that a future reading does not take it for one.

*The first page alone reads 10 against a stated 11, which is a **one-short that must not be papered
over**&nbsp;: the eleventh is on page 2, and it took the walk to establish that rather than the
cardinals.*

### The string `"undefined"` is stored in the database as a VALUE

**A JavaScript artefact, persisted.** *Measured across the 11 adverts&nbsp;:*

| field | `if x` says filled | REALLY filled | the gap |
| :-- | :-- | :-- | :-- |
| `number_Of_vacancy` | 11 | **2** | 9 |
| `contract_duration` | 11 | **3** | 8 |
| `email` | 10 | **4** | **6** |
| `probation_period` | 11 | 8 | 3 |
| `reference` | 11 | 9 | 2 |
| `experiance` | 11 | 10 | 1 |

> **A field that is PRESENT is not a field that is FILLED, and `if x` cannot tell the
> difference** — `"undefined"` is a non-empty string, so it is truthy.

**And the `email` line is the one that matters, because it is a CONTACT field.** *A
`withheld_fields: ["email"]` written on `if r["email"]` would declare that we withheld a recruiter's
address on **6 adverts where the employer deposited the word «&nbsp;undefined&nbsp;»**.* **That lies about
OUR discretion, not about the board** — and it is undetectable by re-reading, because the output is
identical either way. *This is `declarer-avoir-retenu-ce-que-personne-na-depose`, met in the wild
rather than in a fixture.* **The floor that says what a value IS must exclude the literal
`"undefined"`, and the mutation that removes it must redden.**

*Caught in this very measurement&nbsp;: a first pass reported «&nbsp;`email` filled on 10/11&nbsp;» on exactly
that `if x`, and the figure was wrong by six.*

### A systematic SENTINEL and an isolated ABERRANT value are not the same thing

`closing_date` carries **`2040-07-01` on 1 advert of 11**, among dates that otherwise run 2026-10-18
to 2027-06-02. **One in eleven is an implausible data entry, not a template default** — *contrast
`iscikler` (#720), whose `2099-12-31` sat on **9 of 28**, which is systematic and therefore a
sentinel meaning «&nbsp;none&nbsp;».*

> **The discriminant is the SHARE, not the shape.** *A sentinel is dropped because the board never
> meant it as a date&nbsp;; an outlier is CARRIED, because the board did mean it and one employer typed
> something odd.* **Dropping an outlier would be substituting our judgement for the board's filing.**

*And zero of the 11 are past their deadline, with `job_status: active` on all 11 — so this board, unlike
the four Northern Cyprus ones, neither expires nor accumulates stale adverts.*

### And the telephone rule was DECORATIVE until a guard reached for it

**Afghan mobiles group 4-3-3** — `0700 123 456`, `+93 7xx xxx xxx`. *A first draft of the
adapter's rule counted `7\d` then three then three, so it could not match a real number at
all.* **It was not too wide, it was UNREACHABLE: an expurgation rule that cannot fire, whose
comment nonetheless claimed the discipline.** *Found by the guard, not by re-reading — and on
the REAL corpus the corrected rule finds `+93775934920` twice in advert 755's
`job_requirement`, which the decorative version would have emitted.*

*Both directions measured: the five real Afghan forms are caught, and `TKR/09/26/46`,
`2026-09-08`, `ISO 9001`, `Grade C, Step 4 - 6` and `2040-07-01` are untouched — none of the
9 real advert references is destroyed.*

### What the adapter does

```
route   : http — GET https://db.bast.af/api/get_post_jobs?page=N until has_more_pages is false
          the total is STATED and it HOLDS, so the run asserts union == total_jobs
          2 s pace (db.bast.af writes no Crawl-delay) ; www writes 1 s but is not the data host
fields  : 34 ; `provinces` is JSON INSIDE a string ('["Kabul"]') and needs a second decode
          `salary_range` is FREE TEXT («As per Salary Scale») — no figure, so no unit to name
          the literal "undefined" is excluded by a floor, never emitted, and never counted as filled
withheld: 4 real e-mails in `email`, 4 `apply_online_link`, and a mail inside `submission_guideline`
          on 5 of 11 and `job_requirement` on 1 — the HTML bodies must be scrubbed too, not only
          the structured fields
#183    : `gender` is posed on 3 of 11 (male 1, female 2) — the criterion is NOT propagated.
          The law of Afghanistan is NOT asserted here; the field treatment is carried over
NEVER   : no signature is computed and no token is forged. The site sends `Bearer` only when a
          user is logged in; we are not a user.
```

**Re-measured 2026-10-02 by the declared client, the guard on each exact path AND EACH HOST first,
`bin/fetch-body.py`, provenance beside every body.** *The content-hashed bundle was fetched in the
same pass as the shell that names it.* *A measurement, not an adapter.*

```
_robots.verdict('www.bast.af')  state: read,   certain: True, group '*', delay: 1.0
_robots.verdict('db.bast.af')   state: absent, certain: True, no rules published
GET / · /jobs · /job-list · /assets/index-7d427d26.js · bast.af/sitemap.xml
GET db.bast.af/api/get_post_jobs (page 1, 2, 99)                           — all 200
```
