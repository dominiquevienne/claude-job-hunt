# Local repository evidence

Lives at `$JOB_HUNT_HOME/repos.md`. Optional, and worth the twenty minutes it
takes.

Technologies **verified by reading the candidate's own repositories**. This file
exists because profile exports systematically *understate* the stack: whole
technologies backed by real, authored, dated code are missing from a LinkedIn
skills page — usually the ones the candidate never got round to adding.

Treat it as a first-class part of the factual record, alongside `profile/`.
It is used for **both** the fit scoring and the drafting.

**How to build it:** inspect manifests, file counts and commit authorship —
never infer from a folder name. Record the verification date; repos evolve, so
re-check with `git -C <repo> log` before leaning on an old entry.

*The entries below are illustrative. Replace them.*

---

## <repo-name> — what it establishes

`~/path/to/repo` · **N commits, authored by <email>** · <period> · <context: a
job, a client, personal>

What it is, in two or three sentences: the language and version, the framework,
the platform, the scale (file counts, modules, users).

- **<Feature>**: what was built and the technique behind it — enough for a
  reader to judge the depth, not a feature list.
- **<Feature>**: same.
- Supporting stack: libraries, persistence, CI, tests, tooling.

**Why it matters:** what this repository proves that the exports do not, and
which kinds of ads should score against it.

**Depth:** production / prototype / learning exercise. Be exact — the scoring
reads this word literally.

**Confidentiality:** if the work belongs to an employer or client, say so here
and state the limit — e.g. *"describe at architecture level only: no endpoints,
no internal class names, no ticket references."* A cover letter goes to a third
party; an NDA does not pause for a job search.

---

## Never claim these

The other half of the file's value, and the half people skip. List the
technologies that look adjacent to the above but are **not** supported by any
code here — the ones a generous reading would happily assert.

- **<Technology>** — not present. <One line: what was mistaken for it.>
- **<Technology>** — read about, never written. Stays at `0`.

Being explicit here is what lets the scoring trust everything above it.

---

## Depth vocabulary

Use these words, consistently, so the scoring can act on them:

| Word | Means | Scores |
| :-- | :-- | :-- |
| **production** | Shipped, maintained, used by real users | `1` |
| **substantial** | Real, complete work, not shipped to end users | `1` or `0.5` by context |
| **prototype** | A working proof, small, unmaintained | `0.5` |
| **learning exercise** | A tutorial followed, a toy | `0` |
| **absent** | Not present | `0` |
