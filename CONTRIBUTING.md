# Contributing

Four rules that govern this repository. They were given aloud and applied for a
whole day before anyone noticed they were written nowhere — **so they survived
on one session's memory, which is to say on nothing.** Issue #105.

**Each is written with its reason.** A rule without its reason gets worked
around the first time it costs something, and every one of these costs
something.

---

## 1. Every board identified deserves an adapter, even one already covered

The question *"is it worth it, since another adapter already serves those
ads?"* **does not arise.** A board reached indirectly — through an ATS family,
through an aggregator — is still to be written for itself.

**Why.** A direct adapter does not render the same service as indirect
coverage. **It sees what the aggregator filters, it gives the ad at its
source, and it survives the day the aggregator changes.** Redundancy is the
point, not the cost.

**And the measurement never gates the decision.** Counting how many employers
run a platform tells you *how to build* the adapter, never *whether to*.
Deciding not to build because only one ad has been met is concluding from what
was seen to what exists — the fault `shared/plausible-and-false.md` names, put
to a platform instead of a domain.

---

## 2. The plugin is an open tool, not one person's

**The user's location, their market and their results must steer neither the
choice of adapters nor the writing.** A Swiss board is not a priority because
the user is Swiss; a country is not skipped because it does not concern them.

**Why.** This is the easiest rule to break without noticing, **because the
reference user is also the only tester.** Everything that works is verified
against one market, so the pull towards that market is constant and never
announces itself.

**In practice:** a board card describes the board, not what it returned for one
search. A country is worked because it is unworked, not because someone might
apply there.

---

## 3. Anything that affects every user becomes an issue, not a local workaround

A broken adapter, a board's trap, an access policy misread: **the issue, not
the patch in the workspace of whoever met it.**

**Why.** The plugin runs from a version-pinned cache. **A local fix reaches
nobody and does not survive the next update** — the issue is the only route by
which one user's finding becomes every user's.

`shared/never-fail-silently.md`, *What you learn belongs to the next user too*,
holds the standing form and the one test: **would this still be true on another
machine, for another person, tomorrow?** Yes → upstream. No → the run's own
output, and it stops there.

*Of this repository's issues, that rule accounts for #96 and #98 to #104.*

---

## 4. Branch, then rebase. Never commit on `main`

**Why it needs saying at all:** the linear history and the absence of branches
are **the result of rebasing and deleting the branch**, not evidence that
people commit directly.

**It is the only one of the four whose history actively gives the wrong
impression.** A reader of `git log` would conclude the opposite and follow what
they saw.

```bash
git checkout -b <short-name>
# work, commit
git fetch origin && git rebase origin/main
git checkout main && git merge --ff-only <short-name>
git push origin main && git branch -d <short-name>
```

---

## Two habits that belong here as much as in a docstring

Both were learned on this repository's own tooling and are currently recorded
in `bin/host-drift.py`, which is not where doctrine is read.

**A clean run is not a clean state.** A check that finds nothing has found
nothing *this time*. `my.indeed.com` redirected across hosts one afternoon and
answered under its own name an hour later — **one observation of drift is a
finding; one observation of no drift is not a clearance.**

**One path is not a host.** A tool that reads `/robots.txt` reports on
`/robots.txt`. `entreprise.francetravail.fr` moved its site root and left its
partner API where it was, and the report was generalised from the one to the
other before it was caught. **Generalising from one path to a host is the same
step as generalising from one ad to a board.**

---

## Where the rest is written

This file holds what governs the repository. **What governs the work is in
`shared/`**, and it is not optional reading:

| | |
| :-- | :-- |
| `shared/never-fail-silently.md` | The first rule: nothing skipped, partial or guessed goes unreported — and nothing learned that would be true for another user stays local |
| `shared/plausible-and-false.md` | Fields that are present, plausible and false; which way a defect errs, and what catches it |
| `shared/robots-policy.md` | What may be fetched, what a refusal means, and when a file is not a file |
| `shared/boards/README.md` | Writing an adapter: the helpers to use rather than a pattern of your own |
