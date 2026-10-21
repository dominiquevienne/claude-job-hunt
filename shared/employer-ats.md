# Employer ↔ ATS registry — the FORMAT, DECIDED and implemented (#1094 points 1–3)

**CORRECTION, 2026-10-21.** *This file said* **«This file is a PROPOSAL»** *and its
title said* **«proposed and not decided»** *— and both had been false for nine days.*
The owner decided the format on **2026-10-11**, verbatim: « je valide ta proposition
avec le fichier contentant les arguments en un bloc », and `083d745f` implemented it
on **2026-10-12** — the single `args` column that replaced `adapter_param`, which
named ONE flag where seventeen of twenty-one rows need more.

> **The reserve outlived the decision because the pass that implemented it edited the
> TABLE and left the paragraph above it standing.** `git log -S'This file is a
> PROPOSAL' -- shared/employer-ats.md` returns **one** commit — `31ee7982`, 2026-10-07
> — and this file has been edited three times since. *A stale permission makes you act
> wrongly and that shows; a stale interdiction makes you OBEY wrongly, and a session
> that declines to write here looks exactly like a session being careful.* The decision
> of 11.10 had already nearly been asked for a second time on this ground.

**What the file carries:** the format, the three decisions that had to be taken
before the first entry, and **twenty-one entries verified by EXERCISING** — the two of point 1,
plus the nineteen of point 2.
*It carries the nineteen employers of point 2, read from the owner's `config.yml`
under the reserve he lifted himself — and NOT his address, his thresholds or his
document paths: the repository is public and indexed.*

**What is still open is point 4, and it is the OWNER'S**: pointing his own
`config.yml` at this registry. *Nothing here waits on a decision about the format
any more, and that is the whole of this correction.*

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

**So a registry with one `tenant` column is wrong by the tenth entry — and a
registry with one FLAG column is wrong by the eleventh.** *`adapter_param` named ONE
flag. Measured on the twenty-one rows by interrogating the interface each adapter
DECLARES: **seventeen** need something beyond the key — eleven `ats` rows require
`--provider` as well, six `workday` rows require `--tenant` and `--site`, and only
four (`recruitee`, `oraclecloud`, `successfactors`, `umantis`) are invoked by the key
alone.* I guessed twice while writing this file (`--company`, `--tenant` for umantis)
and both guesses failed loudly; the column exists so the next reader does not have to
guess at all.

**SO THE ROW CARRIES `args`: the ENTIRE argument string that follows the
sub-command.** *Decision of the owner, 2026-10-11, verbatim: «je valide ta
proposition avec le fichier contentant les arguments en un bloc» (#1094 point 3).*

```
relancer une ligne  =  <family>.py <sous-commande> <args>
```

**`args` is DERIVED from `verified_by` and NEVER retyped**, and the guard gives it to
that adapter's own `argparse`: a row whose arguments do not parse is a row nobody can
re-run. *Why one free column rather than `provider`/`tenant`/`site` columns: there is
NO schema to agree on, so a new ATS family with an unknown flag forces no change of
format. That was the objection to answer — «migrating to a format that will still
move is migrating twice», this file calling itself a proposal — and it falls because
there is no longer a format to move.*

**And it exposes nothing new, which is what decided it against the alternative:**
every token `args` structures was ALREADY on the same row, in the prose of
`verified_by`, because a witness must be a RUNNABLE command. *The alternative — zero
parameters in the repository — cost the runnable witness, hence twenty-one claims
nobody could test again.* **The sub-command stays in the witness, because it is NOT
uniform** — `recruitee.py jobs`, `oraclecloud.py sites`, `list` for the other
nineteen — *so `args` alone does not rebuild the invocation, and saying so beats
implying otherwise.*

## The row format

```
| family | identifier | args | employer_label | state | checked | verified_by |
```

| field | rule |
| :-- | :-- |
| `family` | the adapter's filename without `.py` |
| `identifier` | the value the adapter's own parameter takes — **the key, with `family`** |
| `args` | the ENTIRE argument string following the sub-command — **DERIVED from `verified_by`**, never retyped, and it must PARSE in that adapter's own `argparse` |
| `employer_label` | a human label, **NOT unique and never a key** |
| `state` | `live` or `dead` + `recheck_after` |
| `checked` | the date the row was last EXERCISED |
| `verified_by` | **the command that proved it, and by which tool** — *a refusal to the HTTP client is not a refusal to a browser* |

**`verified_by` is a COMMAND and never a reasoning.** *«Re-verifying means RUNNING
the adapter, not re-reading it» — `shared/boards/README.md`.*

## The entries — two from point 1, verified by EXERCISING, 2026-10-07

| family | identifier | args | employer_label | state | checked | verified_by |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| recruitee | `gmk` | `--tenant gmk` | Groep Maatschappelijke Kinderopvang (NL) | live | 2026-10-07 | `recruitee.py jobs --tenant gmk` → 3 advertisements in Amsterdam, `ledger_id` `recruitee:gmk:1803558` and two more, by the declared HTTP client |
| oraclecloud | `ecwl.fa.us2.oraclecloud.com` | `--host ecwl.fa.us2.oraclecloud.com` | ClubCorp (US) | live | 2026-10-07 | `oraclecloud.py sites --host ecwl.fa.us2.oraclecloud.com` → 2 sites, `CX` ORA_ACTIVE and `CX_2001` ORA_INACTIVE, by the declared HTTP client |

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

**What left that file is the key triple *(family, identifier, employer_label)* AND,
inside `verified_by`, the parameters the invocation needs** — for `workday` the
`--tenant` and the `--site`, and at least one `--site` is NOT derivable from the
identifier. *An earlier version of this line claimed the triple ALONE, which the six
`workday` witnesses exceed. The witness column exists so that re-verifying means
RUNNING, so those parameters belong in it: the CLAIM was wrong, not the rows.* Not his
address, not his thresholds, not his document paths — the repository is public and
indexed. **And his configuration was not modified in passing:** the one pair that did
not answer is recorded *here*, not corrected *there*.

**Every row below was EXERCISED**, and the guard was taken on each exact host and path
in a turn distinct from the retrieval, interrogated with the single token a request
carries (`claude-user`) and never with the set.

| family | identifier | args | employer_label | state | checked | verified_by |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| ats | `scandit` | `--provider greenhouse --tenant scandit` | Scandit (CH) | live | 2026-10-08 | `ats.py list --provider greenhouse --tenant scandit` → **13** advertisements, first *Accounts Payable (A/P) Specialist* |
| ats | `canonical` | `--provider greenhouse --tenant canonical` | Canonical (UK) | live | 2026-10-08 | `ats.py list --provider greenhouse --tenant canonical` → **311** advertisements, first *Accountant* |
| ats | `proton` | `--provider greenhouse --tenant proton` | Proton (CH) | live | 2026-10-08 | `ats.py list --provider greenhouse --tenant proton` → **57**, first *Backend Engineer (VPN)*. *The config's own comment says 68 on 2026-09-17: a live board moves, and that is what `checked` is for.* |
| ats | `frontify` | `--provider lever --tenant frontify` | Frontify (CH) | live | 2026-10-08 | `ats.py list --provider lever --tenant frontify` → exit 0, **0 postings**. **Established by a counter-test, not by the zero:** a bogus tenant (`zzz-aucun-board-ici`) dies **exit 4, «both 404»**, so Lever distinguishes an unknown tenant from an empty board. The board EXISTS and is currently empty. |
| ats | `docker` | `--provider ashby --tenant docker` | Docker (US) | live | 2026-10-08 | `ats.py list --provider ashby --tenant docker` → **61**, first *Account Executive, Mid-Enterprise (West)* |
| ats | `kraken.com` | `--provider ashby --tenant kraken.com` | Kraken (US) | live | 2026-10-08 | `ats.py list --provider ashby --tenant kraken.com` → **80**, first *Staff Security Architect* |
| ats | `nexthink` | `--provider smartrecruiters --tenant nexthink` | Nexthink (CH) | live | 2026-10-08 | `ats.py list --provider smartrecruiters --tenant nexthink` → **70**, first *Field Marketing Intern*. **Reached only under the owner's own `override_robots: true`** — see the note below. |
| ats | `swissquote` | `--provider smartrecruiters --tenant swissquote` | Swissquote (CH) | live | 2026-10-08 | `ats.py list --provider smartrecruiters --tenant swissquote` → **47**, first *Financial Controller* |
| ats | `sportradar` | `--provider smartrecruiters --tenant sportradar` | Sportradar (CH) | live | 2026-10-08 | `ats.py list --provider smartrecruiters --tenant sportradar` → **98**, first *Lead DevSecOps Security Engineer* |
| ats | `Evooq` | `--provider smartrecruiters --tenant Evooq` | Evooq (CH) | live | 2026-10-08 | `ats.py list --provider smartrecruiters --tenant Evooq` → **9**, first *Application & Integration Manager*. *Case matters: the identifier is the path segment as served.* |
| ats | `AudemarsPiguet` | `--provider smartrecruiters --tenant AudemarsPiguet` | Audemars Piguet (CH) | live | 2026-10-08 | `ats.py list --provider smartrecruiters --tenant AudemarsPiguet` → **84**, first *Stagiaire Simulation des chocs* |
| workday | `swisscom.wd103.myworkdayjobs.com` | `--host swisscom.wd103.myworkdayjobs.com --tenant swisscom --site SwisscomExternalCareers` | Swisscom (CH) | live | 2026-10-08 | `workday.py list --host … --tenant swisscom --site SwisscomExternalCareers` → **20 on the first page**, first *Sales Manager Digital Media & LMS* |
| workday | `logitech.wd5.myworkdayjobs.com` | `--host logitech.wd5.myworkdayjobs.com --tenant logitech --site logitech` | Logitech (CH) | live | 2026-10-08 | `workday.py list --host logitech.wd5.myworkdayjobs.com --tenant logitech --site logitech` → **20 on the first page**, first *E-Commerce Developer* |
| workday | `richemont.wd3.myworkdayjobs.com` | `--host richemont.wd3.myworkdayjobs.com --tenant richemont --site richemont` | Richemont (CH) | live | 2026-10-08 | `workday.py list --host richemont.wd3.myworkdayjobs.com --tenant richemont --site richemont` → **20 on the first page**, first *Sales Associate Temporal Montblanc* |
| workday | `lombardodier.wd3.myworkdayjobs.com` | `--host lombardodier.wd3.myworkdayjobs.com --tenant lombardodier --site lombard_odier_careers` | Lombard Odier (CH) | live | 2026-10-08 | `workday.py list --host lombardodier.wd3.myworkdayjobs.com --tenant lombardodier --site lombard_odier_careers` → **20 on the first page**, first *Collaborateur/-trice Trésor, Caisse* |
| workday | `sunrise.wd3.myworkdayjobs.com` | `--host sunrise.wd3.myworkdayjobs.com --tenant sunrise --site sunrise` | Sunrise (CH) | live | 2026-10-08 | `workday.py list --host sunrise.wd3.myworkdayjobs.com --tenant sunrise --site sunrise` → **20 on the first page**, first *Sales Agent Spreitenbach 20-40%* |
| workday | `weforum.wd3.myworkdayjobs.com` | `--host weforum.wd3.myworkdayjobs.com --tenant weforum --site Forum_Careers` | World Economic Forum (CH) | live | 2026-10-08 | `workday.py list --host weforum.wd3.myworkdayjobs.com --tenant weforum --site Forum_Careers` → **14**, first *Senior Manager, Grant Governance* |
| successfactors | `jobs.bcv.ch` | `--host jobs.bcv.ch` | Banque Cantonale Vaudoise (CH) | indeterminate + `recheck_after: 2026-11-08` | 2026-10-08 | `successfactors.py list --host jobs.bcv.ch` → **exit 8**. Its rules refuse `/services/` in writing, so the adapter took the permitted HTML route (`/search/`, `/job/`) and recognised **no tile in either markup**. Its own words: *«This is NOT an empty board and NOT a zero… only what we failed to recognise in it.»* **Not `dead`.** |
| umantis | `jobs.bobst.com` | `--host jobs.bobst.com` | Bobst (CH) | live | 2026-10-08 | `umantis.py list --host jobs.bobst.com` → **10**, first *Dessinateur bâtiment et technique* |

### Three things the EXERCISE taught the format, which point 1 could not have guessed

**MARKDOWN EMPHASIS BREAKS A MACHINE-READ FIELD.** *I first wrote the state as
`**indeterminate**` and the guard refused it: `'**indeterminate**'` does not start
with `indeterminate`.* **The red was correct — it is the same property that keeps
`state` from drifting into prose, and bold is prose.** *So `state`, `checked` and
`args` carry no emphasis; `employer_label` and `verified_by` may.* **Backticks are not
emphasis**: `args` and `identifier` carry theirs, and the guard strips them, which is
the step a control of mine omitted on 2026-10-12 — it rendered `0 on 21` on
twenty-one sound rows because the stored cell carries its backticks and the prose
citing it does not.

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
> reconstructs the invocation.* **Naming the limit beats hiding it.**
>
> **CORRECTION, 2026-10-12 (#1094 point 3):** *this quote ended «a reader of this table
> cannot rebuild the command without `verified_by`, and that is now true by design
> rather than by accident». Half of it is now false and the half that remains is the
> sub-command: the ARGUMENTS live in `args`, in a column, so the coordinates no longer
> live only in prose — but `args` still does not carry the sub-command, which is not
> uniform. A reader rebuilds `<family>.py` + the sub-command from `verified_by` and the
> arguments from `args`.*

**1. One `identifier` is not always enough — Workday needs THREE coordinates.** `--host`,
`--tenant` and `--site`, and the site spelling is *case-preserving in the URL* while
case-insensitive at the API. The key stays `(family, identifier)` with the **host** as
identifier, because the host is what is unique; the other two ride in `args` — and
still in `verified_by`, which is the command that proved the row and the source `args`
is derived from. *A format that had fixed one parameter per
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

## The two rows OWED — found by point 4b's resolver, exercised 2026-10-21

**They are point 2 work and not a regression of 4b**, and the way they surfaced is
constraint 1 of point 3 in operation: *«a pointer that does not resolve renders UNKNOWN
and SAYS SO, never zero»*. `employer_pointers.py plan` named them, by board and by
identifier, instead of rendering an absence it had not measured — two of the owner's
configured employers that the nineteen of 2026-10-08 never carried.

**Both were EXERCISED**, guard taken on each exact host and path in a turn distinct from
the retrieval, with the single token a request carries (`claude-user`) and never the set:
`boards-api.greenhouse.io` refuses `/embed/` to `*` and nothing else, `apply.workable.com`
writes no `Disallow` at all, and neither names a `Crawl-delay` — so the cadence is ours.

| family | identifier | args | employer_label | state | checked | verified_by |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| ats | `workwize` | `--provider greenhouse --tenant workwize` | Workwize (NL/US) | live | 2026-10-21 | `ats.py list --provider greenhouse --tenant workwize` → **17** advertisements, first *Business Development Representative, New York*, `ledger_id` `greenhouse:workwize:4570507101`, by the declared HTTP client |
| ats | `itecor` | `--provider workable --tenant itecor` | Itecor (CH) | live | 2026-10-21 | `ats.py list --provider workable --tenant itecor` → **17** advertisements, first *Business Analyst IT* in Lausanne, `ledger_id` `workable:itecor:1867F69E1B`, by the declared HTTP client |

**The two counts are both 17 and that is a COINCIDENCE, not a confirmation** — two
boards, two providers, one number. *Nothing is inferred from the equality; this file has
already taken an accidental equality for a measurement twice (#1094's two 19s).*

**And 17 is a TOTAL here, where the `workday` rows above say «20 on the first page».**
*Neither of these two endpoints pages: `greenhouse_list` and `workable_list` each make
ONE request and the whole board comes back. The count is still our own extraction of
that response and not a board-declared total, so it is written as advertisements SERVED,
which is what a non-zero witness needs to be.*

### What the exercise added to note 3 above: the false zero is testable, and it was tested

Note 3 settles that *«the discriminator is not the zero, it is whether the provider
distinguishes unknown tenant from empty board — and that is settled with one bogus tenant
per family, once»*. **It had been measured for Lever and for SmartRecruiters only.**
`workable` is a provider this registry had never carried, and `greenhouse` had carried
three rows without it ever being taken. Both now are:

```
ats.py list --provider greenhouse --tenant zzz-aucun-board-ici  ->  exit 4, "HTTP 404"
ats.py list --provider workable   --tenant zzz-aucun-board-ici  ->  exit 4, "HTTP 404"
```

**So both providers DISTINGUISH, and a zero from either is a MEASUREMENT and not an
indeterminate** — the same standing as Lever's, and the opposite of SmartRecruiters'.
*Neither of the two rows above needed it, both answering non-zero: it was taken because
the rule says it is taken BEFORE a family's first insertion and holds for every later
one, so the cheap moment is now and not the day a zero arrives.*

## What this file does NOT contain, and why

- **Anything of the owner's beyond the nineteen pairs and the invocations that
  re-run them** — his address, his thresholds, his document paths. *The nineteen
  themselves ARE here, since 2026-10-08. This list claimed the opposite until
  2026-10-11, and a file that says it does not carry what it carries cannot be
  contradicted by any count.*
- **The migration of his file** (#1094 point 4), *which does not assign itself.*
- **Point 3 is no longer in this list**, settled by the owner on 2026-10-11 and
  delivered above as the `args` column. *And what it delivered is NOT the «partial
  pointer» it was first written as: that set is EMPTY, not small. The four rows where a
  pointer would RESOLVE from the structured columns have nothing to remove — the key IS
  the whole invocation — and the seventeen that have something to remove do not resolve,
  the coordinate living only in the PROSE of a witness field.*
