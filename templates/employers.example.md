# Employers

**One section per employer. What is true of the *employer*, not of an ad.**

The ledger is indexed by advertisement and cannot hold this: a decision about a
company, written on one ad's row, is found only by luck. That is not
hypothetical — a freeze declared on 19.08 and lifted on 27.08 lived on two
rows eighteen lines apart, and on 02.09 a scan discarded two live ads citing
the freeze. Issue #94.

## The two rules, and they are not optional

**1. Never copy the ledger.** This file holds what the ledger does not, and
**references** rows instead of duplicating them. No scores, no application
statuses, no ad titles. *Two places that say the same thing eventually
disagree* — a wrong percentage here once survived two clean-ups because it was
written in three places.

**2. Date and source every fact.** *"Read on evooq.com, 02.09"* is not
*"confirmed against the commercial register"*. **A fact about an employer goes
stale, and without its date nobody can tell when.**

## Authority

**The ledger is authoritative about advertisements. This file is authoritative
about the employer. They never speak about the same thing** — and where one of
them strays into the other's subject, the other wins.

---

## Acme SA

- **Legal name** — `Acme SA` · *confirmed against the commercial register,
  2026-09-01*
- **Also trades as** — `Acme Labs` on its careers site · *read on acme.com,
  2026-09-01*
- **Address** — Rue de l'Exemple 1, 1000 Lausanne · *as an official
  declaration expects it*
- **ATS** — SmartRecruiters, tenant `Acme` · *the platform's own behaviour
  lives in `shared/ats-open-check.md`, not here*

### Standing decisions

| From | Decision | Lifted | Why |
| :-- | :-- | :-- | :-- |
| 2026-08-19 | **Freeze** — no new application while the kDrive one is pending | **2026-08-27** | 8 days of silence against a 5-day known cadence |

**A lifted decision stays in the table with its lifting date.** Deleting the
row leaves the freeze looking current in anyone's memory, and leaves nothing to
contradict it.

### Behaviour observed

- **Requisitions run past the published deadline** — 18 days on one, 2026-09-02.
  *A property of this employer, which is why it is here and not on an ad's row.*

### Applications

Rows in the ledger: `jobup:4302da20`, `jobup:e1ab58f6`. **References only** —
their status, score and dates live there and are not repeated.
