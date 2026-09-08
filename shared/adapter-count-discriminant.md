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
