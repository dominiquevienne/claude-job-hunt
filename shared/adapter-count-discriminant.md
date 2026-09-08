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
