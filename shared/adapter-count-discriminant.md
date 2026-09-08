# #181 — which adapters can tell an empty board from an unread one

**Audited 2026-09-08 by `claude-job-hunt-82`. Denominator: 100 adapters —
every script a card declares in `<!-- script: -->`.**

*Six scripts on disk are declared by no card and are excluded as pipeline
tools rather than board adapters: `achievements.py`, `board_offer.py`,
`dormant.py`, `employers.py`, `ledger.py`, `tenant_offer.py`.*

## The discriminant, stated so it can be re-run

> **Does the adapter print a quantity that does NOT come from counting its
> own extracted items?**

*A partition of one's own output is not a second source — `a + b = total`
holds by arithmetic and cannot fail while the extraction fails.*

| | adapters | members |
| :-- | --: | :-- |
| **A · sibling invariant** (`count_says`) | **4** | `bnecl.py` · `bumeran.py` · `hrge.py` · `ssge.py` |
| **B · prints a total read from the response** | **16** | `adzuna.py` · `apec.py` · `arbeitsagentur.py` · `digitalrecruiters.py` · `empleate.py` · `encuentra24.py` · `hellojob.py` · `jobsireland.py` · `jobstore.py` · `kalibrr.py` · `lmisjm.py` · `mycareersfuture.py` · `oposiciones.py` · `platsbanken.py` · `stepstone.py` · `workday.py` |
| **C · neither — nude at the list level** | **80** | *the remaining 80* |

**So 20 of 100 distinguish, and 80 do not.**

## What was verified, and how much

**8 of the 100 were read by hand, four from each side**, because a detector
that is only tried on the cases it is expected to catch has not been tried:

```
positives  kalibrr        prints d.get('count') from the API
           adzuna         note(f"{kept} ads returned of {total} matching")
           mycareersfuture  note(f"filter kept {total} of {plain}")
           stepstone      note(f"{total} reported")
negatives  emploitic      note(f"{len(urls)} advertisement URL(s)...")
           jobartis       3 hits, all prose in docstrings
           ihararejobs    1 hit, a comment about a silent loss
           ofertapune     no counting word at all
```
**All eight agreed with the detector.** *That is 8 of 100 — the other 92 are
classified by a static pattern and not by reading.*

## What the instrument cannot see

**A false friend that prints two lines from one source.** *Another session
found one; my detector would call it B.* **The check is which branch each
number is computed in, and a regex cannot answer it.**

**And a count printed only on a failure path** — an adapter may distinguish
the two cases in a `die()` it never reaches in a healthy run. *`count_says`
is exactly that shape, which is why A is listed separately rather than folded
into B.*

## One correction this audit produced

**`emploitic` was credited in its own card with an external anchor it does
not have.** *Its `890 + 3 347 = 4 237` is three `len()` calls on one
extraction.* **The second source for that board exists in the card — the raw
sitemap, fetched and compared set-wise — but not in the adapter**, which is
the distinction #181 is about.

*Corrected in `emploitic.md` in the same pass as this audit.*


---

# RECOUNTED 2026-09-08 — the two columns above were the wrong shape

**The audit above answered one question and was read as answering another.**
*It asked whether an adapter prints a count not derived from its own
extraction, and 20 of 100 do. That number is unchanged.* **What was wrong is
that "the other 80" was read as "80 adapters that cannot tell an empty board
from an unread one", and the repository holds two further mechanisms the audit
never looked for.**

## Four columns, and they overlap on purpose

```
1  EXTERNAL ANCHOR — resolves the ambiguity          20 / 100
   a total read from the response, or count_says

2  FAILURE GUARD — catches a failure, not a truncation   100 / 100
   every adapter defines die() and calls it with EXIT_UNKNOWN
   on the guard/read path itself

3  DECLARED AMBIGUITY — does not resolve, but says so    22 / 100
   `_zero.zero_note()`: prints what a zero cannot distinguish

4  SILENCE — none of the three                            0 / 100
```

**`_zero.py` is the mechanism the first audit missed entirely**, and it is the
most interesting of the three: *it does not answer the question, it tells the
reader the question is open.* **Its docstring names the case it exists for —
Adzuna Switzerland returning 12 666 for `Entwickler` and 0 for `développeur`,
HTTP 200, no error.**

**Overlap, which is what makes these columns rather than a ranking:**

```
anchor AND failure guard   20        anchor AND declared ambiguity    9
failure guard AND _zero    22        all three                        9

9 adapters hold both an anchor and a declaration: `adzuna.py` · `bnecl.py` · `bumeran.py` · `encuentra24.py` · `hrge.py` · `kalibrr.py` · `lmisjm.py` · `mycareersfuture.py` · `stepstone.py`
13 declare the ambiguity WITHOUT resolving it
```

## Two things this recount contradicts, one of them mine

**The failure-guard column is universal, so it separates nothing.** *Saying
"4 adapters have `count_says`" made failure protection look rare; it is total.*
**A count that every member satisfies is not a finding about members** — it is a
property of the repository, and it belongs in one sentence rather than a column.

**And my own prediction was wrong.** *I wrote that the recount would put the
figure "nearer 16 than 20".* **It is still 20.** *I expected the trichotomy to
shrink the anchor column and it did not touch it: what the trichotomy changed is
everything AROUND that number, not the number.* **An estimate offered as a
correction is still an estimate**, and this one leaned the same way the original
error did — toward believing the published figure was too generous.

## What was read and what was matched

```
column 1   8 of 100 read by hand (4 positive, 4 negative), all agreeing
column 2   3 of 100 read — die() defined per script, called with EXIT_UNKNOWN
           on the read path in ofertapune, jobartis, mycareer
column 3   2 of 100 read — zero_note() genuinely called in adzuna and jobbkk
```

**13 of 100 read in total; 87 classified by pattern.** *The same limit as
before, and the same reason for stating it.*


---

# THE DISCRIMINANT IS NECESSARY AND NOT SUFFICIENT — 2026-09-08, from `xpressjobs`

**The test above asks whether an adapter prints a quantity that does not come
from counting its own extracted items.** *`xpressjobs` passes it: `recordCount`
is the board's own field, carried on every row, and a broken extraction would
not change it.* **And it counts the wrong thing.**

```
recordCount               4 364     row slots the pager will serve
218 x 20 + 4              4 364     the same slots, counted differently
distinct advertisements   2 761     what the question was about
duplicate rows            1 603     37 % of what was served
```

> **An anchor can be genuinely EXTERNAL and still measure a DIFFERENT
> QUANTITY.** *Column 1 assumed that "not from our extraction" implied "the same
> grandeur", and nothing implied it.*

**So `recordCount` is a real anchor against FAILURE — if the reader broke it
would still say 4 364 — and a false one against the question asked.** *The two
protections are not the same protection, and an adapter can hold one while
appearing to hold both.*

**And the agreement that looked like corroboration was guaranteed.** *`218 × 20
+ 4` and `recordCount` count the same objects; their concordance could not
fail, and it was quoted in an assignment as "two independent calculations
agree".* **Two computations of one quantity are one computation.**

### Why this one survives a sample

```
first 500 rows      15 duplicates     3 %      reads as churn
all 219 pages    1 603 duplicates    37 %      reads as a defect
```

**A head sample returns a rate indistinguishable from ordinary noise.** *Nothing
short of reading every page and keying on the identifier separates them* — which
is exactly the cost the anchor was supposed to avoid.

### What this does to the 20

**It does not reduce them, and it is not a recount.** *Each of the twenty prints
something external; whether that something counts advertisements is a separate
question, and it has been asked of ONE of them.* **The column should be read as
"has an anchor", never as "the anchor answers the question".**

*Asking it of the other nineteen is one exercise each, and it is not done here.*

---

# THE FOUR CASES — 2026-09-08, and only three of them have members

**The re-pass asked for every adapter in one of four boxes.** *Three are
measured and named; the fourth is a residue and this file does not pretend
otherwise.*

## The population, and why four counts all differ without contradicting

```
111  cards carrying `<!-- script: *.py -->`      one per card
104  DISTINCT scripts so declared                 <- the denominator used here
110  .py on disk, `_`-prefixed modules excluded
  0  declared by a card and absent from disk
```

**111 − 104 = 7, and it is two scripts declared by several cards**: `ats.py` by
seven (ashby, greenhouse, join, lever, smartrecruiters, teamtailor, workable)
and `jobup.py` by two (jobs-ch, jobup). *6 + 1 = 7.* **110 − 104 = 6**, the
pipeline tools no card declares — `achievements`, `board_offer`, `dormant`,
`employers`, `ledger`, `tenant_offer`.

## Case 3 — the anchor is PRESENT and ANNULLED on the zero path

**Six, all found and all repaired.** *This is the case the first audit could not
see at all: an anchor destroyed on its own path reads, in a scan, exactly like
an anchor.*

```
ihararejobs  ejobsfiji  myjobsfiji     ZeroDivisionError — ratio over the count
careerical-sl  emploiscongo  jobwebrwanda   ValueError — max() over the empty
                                            extraction, jobwebrwanda before any
                                            figure was printed at all
```

## Case 4 — the guard RAISES instead of guarding

**One, and it was mine.** *The first `emploitic` guard referenced `EXIT_PARTIAL`
in a module that did not define it, so it raised `NameError` on exactly the path
it was written for.* **Checked by AST across all 104: no other module references
an `EXIT_` constant it does not define.** *By AST and not by grep — a missing
name reads exactly like a name that exists.*

## Case 2 — the anchor is present

**Twenty from the first audit, plus five established since by reading**:
`cubisima` (its envelope emits the site's own `searchAnuncios` size beside the
returned count, and dies if the array is missing), and the six of case 3 once
repaired.

## Case 1 — the anchor is absent

**NOT ESTABLISHED, and this is the honest state of the re-pass.** *It is the
residue of 104 minus the cases above, and a residue is not a measurement.*

### Why no number is offered for it

**A static scan on these forms returns a LIST OF CANDIDATES, never a count.**

```
26  first scan, "operations that fail on empty"
45  after a "refinement"        <- WORSE
 3  after reading all eight surviving candidates
```

**A refinement that makes the result grow is not a refinement**: it says the
added pattern does not belong to the class. *Adding `[0]` flooded it —
`r[0]`, `parts[0]`, `kv[0]` are tuples, `split()` results and regex groups,
and the safe uses outnumber the dangerous ones by an order of magnitude.* And
four survivors were guarded by a conditional expression no AST walk of mine
recognised: `max(n) if n else None`, `min(cuts)` inside `if cuts:`.

> **Published without reading, this scan says 26 or 45. The true figure was 3.**

*The same applies to case 1: an adapter prints many numbers, and deciding
whether any of them comes from outside its own extraction is a reading, not a
match.*

---

# BATCH 1 OF THE RE-PASS — 20 adapters, read one by one

**2026-09-08. Order: `false-zero-cost.md`, sole-route adapters first. The eight
already classified are excluded.** *Evidence level is marked on every row,
because it differs: `RUN` means the adapter was executed and its own output
read; `READ` means its reporting calls were read in the source.*

| adapter | case | the anchor, or its absence | ev. |
| :-- | :-- | :-- | :-- |
| `adzuna` | **present** | `{kept} ads returned of {total} matching` — `total` is the API's `count` | READ |
| `jobrapide` | **present** | `the paginator announces {announced} pages` — *and it refuses to derive a total from it* | READ |
| `ergodotisi` | **present** | `{total} <loc>` beside the parsed counts, two granularities in one sentence | READ |
| `hellojob` | **present** | `{raw} <loc> · {len(rows)} distinct` | READ |
| `jobam` | **present** | `{raw} <loc> · {len(rows)} distinct`, and it calls the window a window | RUN |
| `jobsbotswana` | **present** | `{raw} <loc> in the sitemap, {len(rows)} advertisements` | RUN |
| `keejob` | **present** | `{raw} <url> in the sitemap, {len(rows)} distinct` | READ |
| `kalibrr` | **present** | `{len(rows)} ads returned of {reported} reported` | READ |
| `vieclam24h` | **present** | `{kept} ad(s) of {total} matching` | READ |
| `platsbanken` | **present** | `{total} match and the window is {CEILING}` | READ |
| `todasvagas` | **present** | `--limit takes the FIRST {a.limit} of {raw}` | READ |
| `mycareer` | **present** | `{raw} rows read, {len(rows)} distinct` | RUN |
| `xpressjobs` | **present** | `the board declares {record_count}` | READ |
| `jobsgovpk` | **present** | **prints the site's own header against its cards, and they disagree** | RUN |
| `computrabajo` | absent | `{kept} ads returned from {country}`; declares via `zero_note` | RUN |
| `encuentra24` | absent | `{kept} ad(s) over {read} page(s)` — every figure its own | READ |
| `glmis` | absent | `{len(rows)} advertisement(s)`; *declares the cap, resolves nothing* | RUN |
| `jobbkk` | absent | `{kept} ads returned over {page} page(s)`; declares via `zero_note` | RUN |
| `mihnati` | absent | `{kept} advertisement(s) — the home page's strip` | RUN |
| `uzjobs` | absent | `the feed's window, not the board` — declares, no second figure | READ |

**Batch 1: present 14 · absent 6 · annulled 0 · raises 0.**

## What this does to "20 of 100"

**Fourteen of these twenty have an anchor, and the first audit counted almost
none of them.** *It searched for `count_says` and for total-keys read from a
response; it could not see a raw `<loc>` count printed beside a parsed one, which
is the commonest form here.* **The original figure is not slightly low. It is the
wrong measurement**, and the re-pass exists because I said so before anyone
asked.

*No corrected total is offered until all 104 are read. 14/20 is this batch, not a
rate — the batch was ordered by cost, and sole-route adapters are not a random
sample of the rest.*

## Two limits of the method, both found by being caught out

**Static extraction of report text is unreliable, and `jobsgovpk` proves it.**
*Its anchor line — the site's header set against its own cards — is assembled
into a variable before being printed, so no scan of `note(...)` arguments finds
it.* **I only know it exists because I ran the adapter this morning.**

**And truncated evidence classifies wrongly.** *A first pass read three report
calls per adapter and would have filed `jobsgovpk` as anchorless; it has nine
count-bearing lines and the relevant one is not among the first three.*

> **Where the two disagree, the run wins.** *`RUN` and `READ` are marked per row
> so that a later reader can tell which rows rest on execution and which on
> reading.*

---

# BATCH 2 — 20 more, and the instrument had FOUR blind spots

**2026-09-08, same order, same form. All READ unless marked.**

| present (18) | the anchor |
| :-- | :-- |
| `adecco` · `crit` | *zero URLs out of `{len(blocks)}` `<url>` blocks — **that combination cannot occur in a valid sitemap*** |
| `albedis` | `{len(urls)} <loc>; {matched} matched … {unmatched} did not` |
| `angoemprego` · `angolaemprego` | `{raw} <loc>` beside the parsed count |
| `applifly` | `{kept} ad(s) of {len(ids)} linked from the listing` |
| `arbeitsagentur` | `{total} match … the API will only ever return {CEILING}` — *and names the unreachable remainder* |
| `bebee` | `{len(locs)} <loc> in the index: {len(jobs)} job file(s)` |
| `bnecl` | `{kept} match(es) after reading {read} of {len(ids)} — **say both numbers**` |
| `bumeran` | `{kept} of {total} ad URL(s)` |
| `burundijobs` | `parsed to zero entries from {len(body)} characters` |
| `empleate` | `{total} live ads match` — **written with `.format()`, not an f-string** |
| `anefa` | `{rows} of {announced}` — **printed to stderr with no `note()` helper** |
| `apec` · `digitalrecruiters` · `emploiterritorial` | a site total beside the collected count, same mechanism |
| `ats` | `{kept} of {len(jobs)} postings kept`, plus *the board is not empty — every posting …* |
| `fachkraft` | *the board is not empty — all `{len(rows)}` ads were filtered out* |

| absent (2) | |
| :-- | :-- |
| `batiactu` | `{kept} ads from {axis}/{value}` — every figure its own |
| `employtt` | declares via `zero_note`; *what the listing serves, which is not what the board serves* — an admission, not a second figure |

**Batch 2: present 18 · absent 2 · annulled 0 · raises 0.**

## The four blind spots, named so the next scan does not repeat them

```
1  count_says and response total-keys only        the original audit
2  a RAW count printed beside a PARSED one        commonest form of all
3  `.format()` instead of an f-string             empleate
4  print(..., file=sys.stderr) with no `note()`   SEVEN adapters in this batch
```

**Each was found by being caught out, never by rereading the detector.** *Seven
adapters in this batch have no `note()` at all and write to stderr directly —
a scan for `note(...)` arguments reports every one of them as silent.*

## And a fifth form that is not a number at all

**`ats` and `fachkraft` print a SENTENCE where the others print a figure:**

> *the board is not empty — all `{len(rows)}` ads were filtered out*

**That discriminates without a second count**, because it names *why* the output
is empty. *A scan looking for two interpolated values in one string does not see
it, and it is exactly what #181 asks for.*

## Running total after two batches

```
read so far   48 of 104        present 32 · absent 8 · annulled 6 · raises 1 · (already classified 1)
still to read 56
```

*No rate is offered. The batches are ordered by cost, so what has been read is
not a sample of what has not.*
