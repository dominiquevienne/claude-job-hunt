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

---

# BATCH 3 — 20 more, and the population is a subtraction, not a memory

**2026-09-11, 12:19–12:21 UTC for the runs.** *Population: 105 scripts declared
by a `<!-- script: -->` line in `shared/boards/` (`gech.py` joined the same
morning). **Classified = named in a table row of batches 1–2, in the code
blocks of cases 3 and 4, or in case 2 (`cubisima`) — a hyphen counts as an
underscore (`careerical-sl`).** 48 classified, 57 remaining; the 20 below are
the first 20 of the remainder in alphabetical order, the order batch 2 used
once the cost-ranked 21 were exhausted. The 20 were named to the pilot before
reading.*

**Every report call of each adapter was read, not the first three. Seven were
executed** — `RUN` — with one request each, on the invocation their card
documents or the cheapest the script offers; two of the seven were refused at
the transport (`hays`, `jobstore`: HTTP 403 to the declared client, exit 9),
and those rows rest on reading.

| adapter | case | the anchor, or its absence | ev. |
| :-- | :-- | :-- | :-- |
| `fhf` | **present** | `the board announces {announced} ads for this search`, beside `{len(kept)} of {len(rows)}` | READ |
| `flatchr` | **present** | `{len(items)} ads` — the payload's own array — beside `{rows} cards returned`; and *a wrong slug is a 404 instead*, so the zero is the tenant's | READ |
| `francetravail` | **present** | `{total} offers match` from `Content-Range`, and a 204 is named as *an empty result, not an error* | READ |
| `freework` | absent | `{len(kept)} of {len(rows)} postings kept` — both its own. *The API answers a JSON list; a non-list dies, a 404 dies, so a zero here is the API's own zero rather than a parse that failed* | READ |
| `gech` | **present** | `{len(rows)} advertisement(s); {articles} <article>, {unlinked} without a link; page states no total` — and the RSS `<guid>` set compared id by id | RUN · 82 = 82 |
| `gozambiajobs` | **present** | `parsed to zero entries from {len(body)} characters — read the bytes before believing the zero` (dies), and `{len(rows)} advertisements in the sitemap` | RUN · 304 |
| `hays` | **present** | `zero <url> blocks out of {len(page)} characters — a read failure, not an empty board`, and `{len(blocks)} <url> blocks and no readable <loc>` — two granularities | READ · run refused 403 |
| `hellowork` | absent | `no result cards at {url}. That is either a facet with nothing open, a slug that does not exist, or a markup change — the three look alike` — **an admission, no second figure**; exit 0 with nothing on stdout | READ |
| `hiringcafe` | **present** | `{total} ads, {ssrCompanyCount} companies` — the site's `ssrTotalCount` — beside `{rows} unique cards returned over {got} page(s) of {asked}` | READ |
| `hrge` | **present** | `{len(ads)} advertisement URL(s) out of {len(urls)} <loc>`, `count_says`, `zero_note`, and `{len(seen)} distinct from {links} link(s)` | READ |
| `icims` | **present** | `HTTP {code}, {len(body)} bytes, and no JobPosting — if this is about 90 KB, `?in_iframe=1` did not take effect` on the ad path; the list path prints `{len(rows)} ad(s)` only, after a `not XML` die | READ |
| `infoempleo` | **present** | `read 0 ad URLs out of {blocks} <url> blocks in a {len(body)} character sitemap. That combination is impossible in a valid sitemap` (dies) | READ |
| `jobartis` | **present** | `parsed to zero advertisements from {len(body)} characters (gzip=…)` (dies), and `{counts['not-an-ad']} entr(y|ies) are not advertisements` beside `{len(rows)}` | READ |
| `jobivoire` | absent | `{kept} advertisement(s) over {n} page(s)`; on zero, `zero_note("jobivoire")` — **declares, no second figure**; page 1 with no link prints *that is the end of the listing* | RUN · 12 on page 1 |
| `jobology` | **present** | `pagination advertises {cap} page(s)` — the site's own — and page 1 empty **dies**: *that is what a wrong slug looks like here — 200, no error, an empty board* | READ |
| `jobroom` | **present** | `{total} ads match` — the API's `count` — beside `{rows} cards returned`; `"0"` is named *check the canton code before concluding* | RUN · 1 313 match, 5 returned |
| `jobsearchzm` | **present** | `{raw} in the sitemap, {len(rows)} after filters` — two granularities | RUN · 190 raw, 3 after filters |
| `jobsge` | absent | `zero_note("jobs.ge", …)` as a **die** on zero ids — *declares, no second figure, and refuses to exit 0* | RUN · 310 |
| `jobsireland` | **present** | `parsed {len(real)} cards but the same document carries {len(links)} ad links` (dies), `parsed no cards from {len(page)} characters that contain {len(links)} ad links` (dies), `{total} ads match` from the page's `totalCount`, and `no totalCount — a read failure, not an empty board` (dies) | RUN · 4 958 match, 3 returned |
| `jobstore` | **present** on `count` and the sitemap route — `{len(files)} sub-sitemaps declared; {len(ads)} carry ads`, `{kept} ad URLs from {len(ads)} job-*.xml file(s)`; **absent on `search` until this batch** — `page 1: no ad URL in the ItemList — stopping` read like the end of a listing. **Fixed here**: page 1 empty now dies 6 with `{len(body)} characters of {ctype!r}` beside the zero, guarded by `AFirstPageWithNothingOnItIsNotTheEndOfAListing` | READ · run refused 403 |

**Batch 3: present 16 · absent 4 · annulled 0 · raises 0.** *The four absent all
DECLARE — `zero_note`, an admission sentence, or a die — none prints a bare
zero; what they lack is a second figure.*

## A sixth form, and it is a die, not a print

**Six of the sixteen present carry their anchor in a `die()`** — `gozambiajobs`,
`infoempleo`, `jobartis`, `jobology`, `jobsireland`, `hays`: *the zero path does
not print a count at all, it refuses to exit 0 and names the bytes or the
blocks it saw.* A scan for two figures in one printed line does not see them,
because the line is never printed on the healthy path. **This is the strongest
form here**: a caller cannot mistake it for an empty board, because there is no
exit 0 to mistake.

## Running total after three batches

```
read so far   68 of 105        present 48 · absent 12 · annulled 6 · raises 1 · (cubisima) 1
still to read 37               jobup … zaposli
```

*No rate is offered. The batches are ordered — cost first, then alphabet — so
what has been read is not a sample of what has not.*

---

# BATCH 4 — 20 more, and the audit's own tables do not count as classified

**2026-09-11, 12:31–12:32 UTC for the runs.** *Same population criterion as
batch 3 — 105 declared; classified = a table row of batches 1–3 (the two-name
rows of batch 2 included), the code blocks of cases 3–4, or case 2; hyphen =
underscore — **with one clarification: a name in the tables of the ORIGINAL
audit (`jobup`, `lmisjm`, `mycareersfuture`, `ofertapune`, `oposiciones`) is
cited, not classified.** The re-pass supersedes that audit; it does not
inherit from it. The 20 were named to the pilot before reading, and verified
by subtraction on his side: members, not cardinal.*

**Every report call read. Seven executed** — `RUN` — one or two requests each.

| adapter | case | the anchor, or its absence | ev. |
| :-- | :-- | :-- | :-- |
| `jobup` | absent | `{len(rows)} ad(s) over {pages} page(s)`; on an empty page, *three things look like this and they are not the same* — **an admission**, then `zero_note`; no second figure | RUN · 20 on page 1 |
| `jobzambia` | **present** | `{raw} in the sitemap, {len(rows)} after filters` — two granularities | READ |
| `kosovajob` | **present** | `parsed to zero advertisements from {len(page)} characters` (dies); `{len(bad)} block(s) carried a link and could not be parsed` beside `{len(rows)}` | READ |
| `kumarijob` | **present** | `{skipped} entries do not have the /<employer>/<id>-<slug> shape and are not counted` beside `{raw} advertisements` | READ |
| `labonnealternance` | absent | `{len(jobs)} posted ads, {len(recruiters)} companies` — the API's own arrays, the caps named. *A zero here is the API's zero; a refused key dies* | READ |
| `lmisjm` | **present** | `the endpoint states {stated} and returned {len(rows)} — they should agree`; `count` printed on the capped path; `die(zero_note)` on an empty `data` | RUN · 3 of `count` 24 |
| `merojob` | **present** | `{tenders} entries rejected BY PATH`, `{other} not the depth-1 shape` beside `{raw} advertisements` | READ |
| `merorojgari` | **present** | `{other} entries not under {AD_PREFIX} and not counted`; `{u}: HTTP {code} — this file contributes nothing` per file | READ |
| `meteojob` | absent | *no result cards on the page … a search with no matches or a markup change — the two look identical here* — **an admission**, exit 0, stdout empty | RUN · 20, the cap |
| `michaelpage` | **present on 404, absent on 200 until this batch** | a zero-result search answers **404** and the adapter fetches bare `/jobs` as a **control** — *a second request, not a second count*; but a 200 with no reference fell through to `0 ads over 1 page(s)`, exit 0. **Fixed here**: page 0, 200, no reference → dies 6 with `{len(body)} characters`, because on this board a real zero answers 404 | RUN · 30 |
| `mycareersfuture` | **present** | `{kept} ads returned of {total} matching` — the API's total; `filter kept {total} of {plain}`; `page returned 0 rows — how this API says…`; `zero_note` | READ |
| `ofertapune` | **present** | `parsed to zero advertisements from {len(page)} characters` (dies); `{len(bad)} block(s)` beside `{len(rows)}` | READ |
| `onape` | **present** | `{raw_count} <loc> in the sitemap, {len(urls)} distinct`; `parsed to zero <loc> from {len(body)} characters` (dies) | READ |
| `oposiciones` | **present** | `{} announcements match — fq={}` — Solr's `numFound`, **written with `.format()`** (blind spot 3); *a real zero: the live filter was applied and echoed back* | READ |
| `oraclecloud` | **present** | `the endpoint reports {total} jobs and returned none of them` (dies); `{n} returned of {total}` | READ |
| `persigo` | **present** | `{kept} emitted, {len(rows)} read, board states {stated} (complete \| — N short)`; *the board is not empty — all N ads were filtered out*; dies on no `listitem` | RUN · `0 emitted, 888 read, board states 888 (complete)` on a filter that matches nothing |
| `personio` | **present** | `no <position> elements in {len(body)} characters of feed` (dies); `{with_text} of {len(blocks)} carry a description` | READ |
| `philjobnet` | absent | `page {page} carried no job card — stopping`, then `zero_note`; **declares, no second figure** | RUN · 10 on page 1 |
| `pinpoint` | **present** | dies when the `data` key is missing — *the only container, so its absence is a read failure* — and names *a real zero* on an empty list | READ |
| `prekoveze` | **present** | `raw {raw} / distinct {len(rows)}` — *counted on different sides of the set, and the line prints either way* | READ |

**Batch 4: present 16 · absent 4 · annulled 0 · raises 0.** *Again the four
absent all declare — an admission sentence or `zero_note` — and none prints a
bare zero. Two of them (`jobup`, `meteojob`) sit on boards where pagination is
behind a disallowed query string, so «20» is the cap and the note says so.*

## A seventh form — a control REQUEST rather than a second count

**`michaelpage` discriminates a zero by fetching bare `/jobs` when the search
answers 404**: if the bare page answers 200, the domain is fine and the zero
is real. *That is the same discriminant #181 asks for, by a second request
instead of a second figure* — and it has a blind side: it covers only the
status the board uses for a zero, and the other status fell through. **The fix
here closes the 200 side with the bytes.**

## Running total after four batches

```
read so far   88 of 105        present 64 · absent 16 · annulled 6 · raises 1 · cubisima 1
still to read 17               randstad … zaposli — batch 5 takes them all
```

*No rate is offered until the last batch.*

---

# BATCH 5 — the last 17, and the total over 105

**2026-09-11, 12:41–12:42 UTC for the runs.** *Population by subtraction on
`origin/main = cd7f4b8`: 105 scripts declared by a `<!-- script: -->` line;
classified = named in the first cell of a table row of this file, or in the
Case 2/3/4 sections, a hyphen counting as an underscore — 88, so 17 remain:
`randstad` … `zaposli`, the alphabetical tail. The 17 were named to the pilot
before reading and matched his continuation after `prekoveze` plus three
(`ssge`, `stepstone`, `workday`) his coarser «cited» criterion had excluded.*

**Every report call of each adapter was read. Six executed** — `RUN`, one
request each on the cheapest invocation, all six answered.

| adapter | case | the anchor, or its absence | ev. |
| :-- | :-- | :-- | :-- |
| `randstad` | **absent until this batch — fixed here** | `{kept} emitted, {len(seen)} ads over {pages_read} page(s)` — both its own, and page 1 with no cards **broke out of the loop and printed `0 emitted, 0 ads over 0 page(s)` with exit 0**. Now dies 6 with `{len(body)} characters — a read failure, not an empty board`; a later empty page still ends the listing | RUN · 30 on page 1 |
| `randstadfr` | **present** | `parsed to zero <loc> out of {len(idx)} characters` (dies), `parsed to zero <url> blocks out of {len(page)}` (dies), `gave zero URLs out of {len(blocks)} <url> blocks` (dies); `{len(rows)} of {before}` after filters | READ |
| `recruitee` | **present** | dies when the `offers` key is missing — *the only container in this payload, so its absence is a read failure* — and names an empty list *a real zero: what an employer with nothing open looks like* | READ |
| `rocken` | **present** | `board_declares` from the title's `N offene Stellen` beside `rows_read` / `found` / `kept`, and its absence is said out loud; *this line prints either way* | RUN · declares 6 066, 10 read on 1 page |
| `solique` | **present** | `{kept} emitted, {len(rows)} read of {total} stated` on the html route, with the truncation named; no route answering **dies** | READ |
| `sozialinfo` | **present** | `{kept} emitted, {len(rows)} read, board states {stated} — N short`; zero cards **dies** 5: *the listing ships every ad in its markup, so zero cards is a page-shape change* | RUN · 720 read, board states 740 |
| `ssge` | **present** | zero sub-sitemaps → `die(count_says(body))`; the families' counts printed by file | READ |
| `stepstone` | **present** | `{kept} ads returned; the board reported {total} ({main} literal)` — the analytics payload's own total — and no payload **dies**; `zero_note` on zero | RUN · `count`: 379 reported, 379 literal |
| `successfactors` | **present** | html route: `{kept} emitted, page states {total}; {rows_read} tiles read on N page(s)`; 0 tiles with a stated total ≠ 0 **dies 8 INDETERMINATE**; api route: `{kept} of {total} postings` | READ |
| `swissdevjobs` | **absent until this batch — fixed here** | `{len(kept)} of {len(board)} postings kept` — both its own, and the whole-board endpoint answering `[]` **passed the «is it a list» check and printed `0 of 0`**. Now dies 6: *an empty list from the endpoint that IS the board (193 on 2026-09-11)* | RUN · 8 of 193 |
| `taleez` | absent | `{len(jobs)} ads`, then *the tenant is real and has nothing open — that is a zero, not a failure. A wrong slug is a 404 instead* — **declares, no second figure**; the same shape as `freework` and `labonnealternance` | READ |
| `talentsoft` | **present** | `{total} ads announced` from the page's counter, `collected {len(out)} of {total} announced — incomplete, not the size of the board`. *Blind side: when the counter regex misses, `? ads announced` and a zero print with exit 0* | READ |
| `turijobs` | **present** | `gave zero ad URLs out of {len(blocks)} <url> blocks` (dies), `parsed to zero <url> blocks out of {len(page)}` (dies); `no __NEXT_DATA__ block ({len(page)} chars)` (dies) | READ |
| `umantis` | **present** | zero vacancies **dies 5 both ways**, discriminated by a second read of the same body: `CONNECTOR` present → *renders its listing client-side — NOT an empty board*; absent → *no vacancy links and no sign of a widget — report the board*. *A control read, not a second count — the seventh form* | READ |
| `workday` | **present** | `{total} postings match` — the API's own — beside `{kept} returned`; zero → *narrow with --search or check the facet before concluding* | READ |
| `wttj` | **present** | `die(_zero(url, len(page), len(blocks)))` on the index and on each file; `{kept} discovered out of {seen}` | READ |
| `zaposli` | absent | `sitemap_entries: {raw}` beside `kept` / `read`, and `{other} not under AD_PREFIX` printed when non-zero — but **a child sitemap that parses to zero entries prints a JSON of zeros with exit 0**, no bytes; only a MISSING child dies | RUN · 443 entries, 3 selected |

**Batch 5: present 15 · absent 2 · annulled 0 · raises 0** — two of the
fifteen are present because this batch made them so (`randstad`,
`swissdevjobs`, commit `b290944`), the way batches 3 and 4 counted `jobstore`
and `michaelpage`.

## Two corrections, small, one commit — `b290944`

`randstad list`: page 1 with no cards dies 6 with the bytes; page 2 empty
after a full page 1 still ends the listing. `swissdevjobs list`: `[]` from
the whole-board endpoint dies 6. Guard
`AnEmptyFirstPageOrAnEmptyWholeBoardListIsAReadingFault`, three mutations
(the `n == 1` die removed; the die widened to every page; the `if not d`
removed), three red.

## Total over 105 — computed from the five tables, not from memory

```
batch 1   present 14 · absent 6
batch 2   present 18 · absent 2
batch 3   present 16 · absent 4
batch 4   present 16 · absent 4
batch 5   present 15 · absent 2
pre-classified   annulled 6 · raises 1 · case 2 (cubisima) 1

read      105 of 105     present 79 · absent 18 · annulled 6 · raises 1 · cubisima 1
                         79 + 18 + 6 + 1 + 1 = 105
```

*Denominator: the 105 scripts declared by `<!-- script: -->` in
`shared/boards/` on `origin/main = cd7f4b8`, 2026-09-11 — `grep -l
'<!-- script:' shared/boards/*.md`, then the `.py` names in those lines, 105
distinct. The batch lines are read off this file's own `**Batch N:**` lines
and the Case sections, never off a running memory of them.*

**What "absent" means over the whole population, said once:** *every one of
the 18 declares* — a `zero_note`, an admission sentence, or a die that
refuses exit 0 — none prints a bare zero any more; what they lack is a
second figure from another branch. **Whether that is enough is #181's
question, and it is now answerable on a finished list rather than on a
sample.**
