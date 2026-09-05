#!/usr/bin/env python3
"""Are these `<loc>` records, or are they lists? — #154

    from _records import audit
    verdict = audit(urls, fetch)      # fetch(url) -> page text, or None

**A count of `<loc>` is not a count of advertisements**, and the difference is
not visible in the file. `irantalent.com` publishes a 1.7 MB sitemap of 6 932
URLs under `/en/jobs/…` of which **none is an advertisement** — they are
category landing pages. The number is the right order of magnitude for a
country that size, it is stable, it is reproducible, and it measures nothing.

WHY THIS CANNOT BE A PREDICATE ON THE URL

    /en/jobs/banking-investment-jobs        a category page
    /en/jobs/<slug>-<id>                    an advertisement

**Same host, same directory, same shape.** A pattern that separates those two
condemns legitimate records elsewhere — `ergodotisi.com` serves
`/en-CY/jobs/vacancy-4312e752-36722372` and `/en-CY/jobs/senior-ai-engineer-91183625`
side by side, and both are advertisements. **A semantic defect does not yield to
a predicate**, which this repository has already established twice.

And the file name settles nothing either, in **both** directions: `job-filter`
promised lists and held lists (#154), `jobs-sitemap.xml` promised advertisements
and was 31 % tenders (#151). **Two symmetric errors, both attested.**

THE SIGNAL IS PAGINATION, AND IT IS SEMANTIC RATHER THAN LEXICAL

**A page that offers pagination is offering a list.** A single advertisement
does not paginate — there is no second page of one job. So the question asked
of each sampled page is not *what is your URL* but *do you present yourself as
one of many*.

Measured 2026-09-05 across six boards on three continents:

    LIST    irantalent /en/jobs/data-scientist-jobs-in-outside-of-iran     30
            irantalent /en/jobs/banking-investment-jobs                    30
    RECORD  ergodotisi · keejob · job.am · hellojob · jobsbotswana          0
            onape.td                                                        1

**Thirty against nought or one**, and the six records come from six different
sites with six different generators. The threshold is not tuned to a specimen.

WHAT IT DOES WHEN IT CANNOT TELL

**It refuses the count rather than reducing it.** A sample that could not be
fetched, or that splits, returns `state: "unknown"` and no figure — because a
count quietly reduced is the defect this module exists to prevent, wearing a
different number. *`plausible-and-false.md`: a rate near the truth is more
dangerous than an absent one.*
"""

import random
import re

# Pagination as it is expressed in markup: a numbered page in a link, a named
# container, or the standards-track rel attributes. Deliberately not a list of
# site-specific class names — those would be a lexical predicate wearing a
# semantic hat.
_PAGINATION = re.compile(
    r"""(?ix)
    \bpage[=/]\d            # ?page=2, /page/2
    | \bpagination\b        # the usual container
    | rel=["'](?:next|prev)["']
    """)

# Above this many markers a page is presenting itself as one of many. One
# stray `page=` in an unrelated link does not make a list — `onape.td`
# advertisements carry exactly one.
LIST_THRESHOLD = 3

# Below this share of a sample being clearly records, the count is refused.
RECORD_SHARE = 0.8


def markers(page):
    """How many ways this page says *there is more of this*."""
    return len(_PAGINATION.findall(page or ""))


def looks_like_list(page):
    return markers(page) >= LIST_THRESHOLD


def audit(urls, fetch, sample_size=8, seed=None):
    """Sample the URLs, fetch them, and say whether they are records.

    `fetch(url)` returns the page text, or `None` when it could not be read.
    **Sampling is random, never the head or the tail**: on
    `jobsbotswana.info` the last eight entries of a sitemap were one
    advertiser's batch and gave a rate two and a half times the truth.

    Returns a dict carrying **the counts, not only the verdict** — a guard
    green on a denominator it shrank itself proves nothing, so the caller is
    given `records`, `lists`, `unreadable` and `of` to check.
    """
    rng = random.Random(seed)
    pool = list(urls)
    out = {"of": len(pool), "sampled": 0, "records": 0, "lists": 0,
           "unreadable": 0, "state": "unknown", "share": None, "reason": ""}
    if not pool:
        out["reason"] = "no URLs given"
        return out
    picks = pool if len(pool) <= sample_size else rng.sample(pool, sample_size)
    for u in picks:
        page = fetch(u)
        out["sampled"] += 1
        if page is None:
            out["unreadable"] += 1
        elif looks_like_list(page):
            out["lists"] += 1
        else:
            out["records"] += 1
    readable = out["records"] + out["lists"]
    if not readable:
        out["reason"] = (f"none of the {out['sampled']} sampled pages could be "
                         f"read. **No count is returned**: a figure from an "
                         f"unread sample is the defect this checks for.")
        return out
    out["share"] = round(out["records"] / readable, 3)
    if out["share"] >= RECORD_SHARE:
        out["state"] = "records"
        out["reason"] = (f"{out['records']} of {readable} sampled pages carry "
                         f"no pagination, so the {len(pool)} entries may be "
                         f"counted as advertisements.")
    elif out["records"] == 0:
        out["state"] = "lists"
        out["reason"] = (f"all {readable} sampled pages present themselves as "
                         f"one of many. **The {len(pool)} entries are not "
                         f"advertisements and the count is refused**, not "
                         f"reduced — there is no correct fraction to keep.")
    else:
        out["state"] = "mixed"
        out["reason"] = (f"{out['records']} of {readable} sampled pages look "
                         f"like records. **The count is refused rather than "
                         f"scaled**: a rate near the truth is more dangerous "
                         f"than an absent one, and this sample cannot say "
                         f"which entries are which.")
    return out
