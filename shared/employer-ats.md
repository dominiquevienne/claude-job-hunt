# Employer ↔ ATS registry — the FORMAT, proposed and not decided (#1094 point 1)

**This file is a PROPOSAL.** It carries the format, the three decisions that had
to be taken before the first entry, and **three entries verified by exercising**.
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

## The entries — two, verified by EXERCISING, 2026-10-07

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

## What this file does NOT contain, and why

- **The owner's employers.** #1094 point 2 reads his `config.yml`; *he lifted the
  pilot's reserve, and that does not make the gesture automatic.*
- **Pointers from `config.yml`** (#1094 point 3) and **the migration of his file**
  (#1094 point 4). *They depend on this format, and migrating to a format that
  will still move is migrating twice.*
