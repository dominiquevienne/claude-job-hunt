# Employer ↔ ATS registry — the FORMAT, proposed and not decided (#1094 point 1)

**This file is a PROPOSAL.** It carries the format, the three decisions that had
to be taken before the first entry, and **twenty-one entries verified by EXERCISING** — the two of point 1,
plus the nineteen of point 2.
*It carries none of the owner's employers: #1094 point 2 reads his `config.yml`,
and that is his list, not ours.*

## Why a registry at all, measured

```
familles d'ATS dont `shared/setup.md` dit « The employers they would work for »   13
adaptateurs expedies par le depot                                               313
registre partage                                                                  0
```

**Thirteen shipped families are INERT until somebody supplies an identifier**, and
the failure is silent: *a wrong tenant answers 200 with zero advertisements* — the
false zero of `false-zero-cost.md`, placed where the user cannot see it.
`bin/host-drift.py` already says it in its own docstring: *«inventing a tenant
would be asking about a site that may not exist»*.

## Decision 1 — the key is `(family, identifier)`, NEVER the employer name

**An employer name is a LABEL. It is not a key, and the first entry below proves
it rather than arguing it:** `gmk` is *Groep Maatschappelijke Kinderopvang*, which
**is itself a merger of Akros, Impuls, Combiwel voor Kinderen and Elan** — four
names for one tenant, and the merger is in the advertisement text. *Fusions,
languages, accents, «&» against «and»: a name-keyed registry makes duplicates that
NO COUNT shows, because two spellings of one employer are two valid-looking rows.*

**`gmk` is stable. «Groep Maatschappelijke Kinderopvang» was not stable last year
and will not be next year.**

## Decision 2 — several ATS for one employer need no schema at all

It falls out of decision 1: **`employer_label` is explicitly NOT UNIQUE.** Three
ATS for one employer are three entries sharing a label, by country, by subsidiary
or by trade. *Written down because the alternative is that somebody adds a
uniqueness guard on the label later and it reddens on a correct registry — the
«mal décrite» species, which accuses sound data.*

## Decision 3 — a dead entry is MARKED, never removed

**Removal guarantees rediscovery**, and not inventing a tenant is the whole point
of the file. So a dead pair keeps its row with `state: dead`, the date, and what
was observed.

**AND THERE IS A THIRD STATE, FOUND BY EXERCISING AND NOT BY DESIGN: `indeterminate`.**
*Point 1 offered `live` or `dead`, and that vocabulary cannot hold what the
exercise actually returned.* `successfactors / jobs.bcv.ch` answers **exit 8** and
says so itself: *«This is NOT an empty board and NOT a zero, and it does not say
what this host serves — only what we failed to recognise in it.»* **Writing that row
`dead` would put at the centre of the registry the exact false zero the registry
exists to prevent.** So `state: indeterminate` carries `recheck_after` like a dead
row, and means *we could not tell*, never *there is nothing*.

**BUT A MARKED-DEAD ROW NEEDS AN HOUR, or it becomes a stale interdiction whose
symptom is the absence of symptom** — a session that skips it looks exactly like a
session behaving well. So `state: dead` carries `recheck_after`, and a row past
that date is a row to re-exercise rather than a verdict.

## The field that makes an entry USABLE rather than merely true

**The identifier's KIND differs by family, and so does the parameter the adapter
takes — measured, not assumed:**

```
ce que `setup.md` qualifie      URL carrieres 5 · nom de tenant 3 · nom d'hote 2
                                domaine carrieres 1 · etiquette d'hote 1 · non qualifie 1
ce que l'argparse PREND         --tenant : recruitee taleez personio flatchr
                                --host   : umantis oraclecloud
```

**So a registry with one `tenant` column is wrong by the tenth entry.** Every row
carries `adapter_param` — *the flag name READ FROM THE ADAPTER'S `argparse`, never
guessed.* I guessed twice while writing this file (`--company`, `--tenant` for
umantis) and both guesses failed loudly; the field exists so the next reader does
not have to guess at all.

## The row format

```
| family | identifier | adapter_param | employer_label | state | checked | verified_by |
```

| field | rule |
| :-- | :-- |
| `family` | the adapter's filename without `.py` |
| `identifier` | the value the adapter's own parameter takes — **the key, with `family`** |
| `adapter_param` | the flag, read from that adapter's `argparse` |
| `employer_label` | a human label, **NOT unique and never a key** |
| `state` | `live` or `dead` + `recheck_after` |
| `checked` | the date the row was last EXERCISED |
| `verified_by` | **the command that proved it, and by which tool** — *a refusal to the HTTP client is not a refusal to a browser* |

**`verified_by` is a COMMAND and never a reasoning.** *«Re-verifying means RUNNING
the adapter, not re-reading it» — `shared/boards/README.md`.*

## The entries — two from point 1, verified by EXERCISING, 2026-10-07

| family | identifier | adapter_param | employer_label | state | checked | verified_by |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| recruitee | `gmk` | `--tenant` | Groep Maatschappelijke Kinderopvang (NL) | live | 2026-10-07 | `recruitee.py jobs --tenant gmk` → 3 advertisements in Amsterdam, `ledger_id` `recruitee:gmk:1803558` and two more, by the declared HTTP client |
| oraclecloud | `ecwl.fa.us2.oraclecloud.com` | `--host` | ClubCorp (US) | live | 2026-10-07 | `oraclecloud.py sites --host ecwl.fa.us2.oraclecloud.com` → 2 sites, `CX` ORA_ACTIVE and `CX_2001` ORA_INACTIVE, by the declared HTTP client |

**Two entries and not three: a third family would have needed a third exercise and
the margin did not carry it — stated rather than padded.** *And the first draft of
this section carried a second `recruitee`/`gmk` line dressed as a «note», which
would have been a DUPLICATE KEY in a file whose first decision is that
`(family, identifier)` is the key. It was removed rather than explained: a row
that a guard must be taught to ignore is a row in the wrong file.*

### Two things the entries taught the format, which an agreed schema would not have

**`gmk` IS ITSELF A MERGER** — *Groep Maatschappelijke Kinderopvang* was formed
from Akros, Impuls, Combiwel voor Kinderen and Elan, and the advertisement text
says so. **So decision 1 is demonstrated by entry one rather than argued**: four
names, one tenant, and a name-keyed registry would have had up to five rows for it.

**AND `oraclecloud` EXPOSES A SITE NUMBER THAT IS NOT A KEY.** The adapter's own
output says it: *«The number does not filter the board — a value that does not
exist returns the same jobs. It is only used to build the ad URL.»* One of the two
sites is `ORA_INACTIVE`. *So the identifier is the HOST and the site number stays
out of the registry — recording it would invite the next reader to treat it as a
key, and it would answer like one while filtering nothing.*

**One family can be enumerated and the others cannot.** `recruitee.py tenants
--country ISO2` asks the host for its tenants, so for that family the registry can
be DERIVED; `umantis`, `oraclecloud`, `taleez`, `personio` and `flatchr` take an
identifier and offer no enumeration. *A format that assumed either one would be
wrong for the other, which is why `identifier` is a value and never a query.*

## The entries of point 2 — nineteen, read from the owner's `config.yml`, exercised 2026-10-08

**Only the triple *(family, identifier, employer_label)* left that file.** Not his
address, not his thresholds, not his document paths — the repository is public and
indexed. **And his configuration was not modified in passing:** the one pair that did
not answer is recorded *here*, not corrected *there*.

**Every row below was EXERCISED**, and the guard was taken on each exact host and path
in a turn distinct from the retrieval, interrogated with the single token a request
carries (`claude-user`) and never with the set.

| family | identifier | adapter_param | employer_label | state | checked | verified_by |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| ats | `scandit` | `--tenant` | Scandit (CH) | live | 2026-10-08 | `ats.py list --provider greenhouse --tenant scandit` → **13** advertisements, first *Accounts Payable (A/P) Specialist* |
| ats | `canonical` | `--tenant` | Canonical (UK) | live | 2026-10-08 | `ats.py list --provider greenhouse --tenant canonical` → **311** advertisements, first *Accountant* |
| ats | `proton` | `--tenant` | Proton (CH) | live | 2026-10-08 | `ats.py list --provider greenhouse --tenant proton` → **57**, first *Backend Engineer (VPN)*. *The config's own comment says 68 on 2026-09-17: a live board moves, and that is what `checked` is for.* |
| ats | `frontify` | `--tenant` | Frontify (CH) | live | 2026-10-08 | `ats.py list --provider lever --tenant frontify` → exit 0, **0 postings**. **Established by a counter-test, not by the zero:** a bogus tenant (`zzz-aucun-board-ici`) dies **exit 4, «both 404»**, so Lever distinguishes an unknown tenant from an empty board. The board EXISTS and is currently empty. |
| ats | `docker` | `--tenant` | Docker (US) | live | 2026-10-08 | `ats.py list --provider ashby --tenant docker` → **61**, first *Account Executive, Mid-Enterprise (West)* |
| ats | `kraken.com` | `--tenant` | Kraken (US) | live | 2026-10-08 | `ats.py list --provider ashby --tenant kraken.com` → **80**, first *Staff Security Architect* |
| ats | `nexthink` | `--tenant` | Nexthink (CH) | live | 2026-10-08 | `ats.py list --provider smartrecruiters --tenant nexthink` → **70**, first *Field Marketing Intern*. **Reached only under the owner's own `override_robots: true`** — see the note below. |
| ats | `swissquote` | `--tenant` | Swissquote (CH) | live | 2026-10-08 | `ats.py list --provider smartrecruiters --tenant swissquote` → **47**, first *Financial Controller* |
| ats | `sportradar` | `--tenant` | Sportradar (CH) | live | 2026-10-08 | `ats.py list --provider smartrecruiters --tenant sportradar` → **98**, first *Lead DevSecOps Security Engineer* |
| ats | `Evooq` | `--tenant` | Evooq (CH) | live | 2026-10-08 | `ats.py list --provider smartrecruiters --tenant Evooq` → **9**, first *Application & Integration Manager*. *Case matters: the identifier is the path segment as served.* |
| ats | `AudemarsPiguet` | `--tenant` | Audemars Piguet (CH) | live | 2026-10-08 | `ats.py list --provider smartrecruiters --tenant AudemarsPiguet` → **84**, first *Stagiaire Simulation des chocs* |
| workday | `swisscom.wd103.myworkdayjobs.com` | `--host` | Swisscom (CH) | live | 2026-10-08 | `workday.py list --host … --tenant swisscom --site SwisscomExternalCareers` → **20 on the first page**, first *Sales Manager Digital Media & LMS* |
| workday | `logitech.wd5.myworkdayjobs.com` | `--host` | Logitech (CH) | live | 2026-10-08 | `workday.py list --host logitech.wd5.myworkdayjobs.com --tenant logitech --site logitech` → **20 on the first page**, first *E-Commerce Developer* |
| workday | `richemont.wd3.myworkdayjobs.com` | `--host` | Richemont (CH) | live | 2026-10-08 | `workday.py list --host richemont.wd3.myworkdayjobs.com --tenant richemont --site richemont` → **20 on the first page**, first *Sales Associate Temporal Montblanc* |
| workday | `lombardodier.wd3.myworkdayjobs.com` | `--host` | Lombard Odier (CH) | live | 2026-10-08 | `workday.py list --host lombardodier.wd3.myworkdayjobs.com --tenant lombardodier --site lombard_odier_careers` → **20 on the first page**, first *Collaborateur/-trice Trésor, Caisse* |
| workday | `sunrise.wd3.myworkdayjobs.com` | `--host` | Sunrise (CH) | live | 2026-10-08 | `workday.py list --host sunrise.wd3.myworkdayjobs.com --tenant sunrise --site sunrise` → **20 on the first page**, first *Sales Agent Spreitenbach 20-40%* |
| workday | `weforum.wd3.myworkdayjobs.com` | `--host` | World Economic Forum (CH) | live | 2026-10-08 | `workday.py list --host weforum.wd3.myworkdayjobs.com --tenant weforum --site Forum_Careers` → **14**, first *Senior Manager, Grant Governance* |
| successfactors | `jobs.bcv.ch` | `--host` | Banque Cantonale Vaudoise (CH) | indeterminate + `recheck_after: 2026-11-08` | 2026-10-08 | `successfactors.py list --host jobs.bcv.ch` → **exit 8**. Its rules refuse `/services/` in writing, so the adapter took the permitted HTML route (`/search/`, `/job/`) and recognised **no tile in either markup**. Its own words: *«This is NOT an empty board and NOT a zero… only what we failed to recognise in it.»* **Not `dead`.** |
| umantis | `jobs.bobst.com` | `--host` | Bobst (CH) | live | 2026-10-08 | `umantis.py list --host jobs.bobst.com` → **10**, first *Dessinateur bâtiment et technique* |

### Three things the EXERCISE taught the format, which point 1 could not have guessed

**MARKDOWN EMPHASIS BREAKS A MACHINE-READ FIELD.** *I first wrote the state as
`**indeterminate**` and the guard refused it: `'**indeterminate**'` does not start
with `indeterminate`.* **The red was correct — it is the same property that keeps
`state` from drifting into prose, and bold is prose.** *So `state`, `checked` and
`adapter_param` carry no emphasis; `employer_label` and `verified_by` may.*

**0. «FAMILY» IS THE ADAPTER FILE, NOT THE ATS BRAND — and my first eleven rows got it
wrong before the guard caught them.** *I wrote `greenhouse`, `lever`, `ashby` and
`smartrecruiters` in the `family` column. There is no `greenhouse.py`: those four
providers all live in **`ats.py`**, one adapter for four brands, and the format's own
rule says `family` is «the adapter's filename without `.py`».* **So the eleven rows now
say `ats`, and the brand rides in `verified_by` as `--provider <brand>`, which is where
the command lives.**

> **The format assumed one family = one file = one parameter = one identifier, and BOTH
> kinds of adapter break that assumption** — `ats.py` is one file for four brands
> (`--provider` + `--tenant`), `workday.py` needs three coordinates. *The key
> `(family, identifier)` still holds; what does not hold is that the identifier alone
> reconstructs the invocation.* **Naming the limit beats hiding it: a reader of this
> table cannot rebuild the command without `verified_by`, and that is now true by
> design rather than by accident.**

**1. One `identifier` is not always enough — Workday needs THREE coordinates.** `--host`,
`--tenant` and `--site`, and the site spelling is *case-preserving in the URL* while
case-insensitive at the API. The key stays `(family, identifier)` with the **host** as
identifier, because the host is what is unique; the other two ride in `verified_by` as
part of the command that proved the row. *A format that had fixed one parameter per
family would have had to be reopened here.*

**2. A round number is a PAGE, not a board.** Five of the six Workday tenants returned
**exactly 20**. That is a page size, and `verified_by` therefore says *«20 on the first
page»* and never *«this board has 20 advertisements»*. **For the registry's purpose a
non-zero count is enough — it proves the pair answers with real advertisements — and
claiming it as a total would be a false witness produced by our own paging.**

**3. THE FALSE ZERO IS PROVIDER-SPECIFIC, AND IT IS TESTABLE.** `false-zero-cost.md`
and `shared/boards/smartrecruiters.md` warn that *a wrong tenant answers 200 with zero
advertisements* — true of SmartRecruiters, and there a zero is indeed undecidable. **It
is NOT true of Lever**, which 404s on both of its disjoint hosts and dies exit 4. *So
`frontify`'s zero is not an indeterminate: the board exists and is empty.*

> **The discriminator is not the zero, it is whether the provider distinguishes «unknown
> tenant» from «empty board» — and that is settled with one bogus tenant per family,
> once.** *Which turns an unfalsifiable zero into a decidable one, for the cost of a
> single request.*

**And `api.smartrecruiters.com` refuses us in writing** — `verdict()` returns
`sweep: False`, `allowed: False`, rule `/`, kind `host-closed`. Those five rows exist
**only because the owner posed `override_robots: true` on `smartrecruiters` in his own
configuration**, which is his derogation to make (#403, 13.09.2026) and never ours. *A
session that finds this file without that key must not reach those five.*

## What this file does NOT contain, and why

- **The owner's employers.** #1094 point 2 reads his `config.yml`; *he lifted the
  pilot's reserve, and that does not make the gesture automatic.*
- **Pointers from `config.yml`** (#1094 point 3) and **the migration of his file**
  (#1094 point 4). *They depend on this format, and migrating to a format that
  will still move is migrating twice.*
