# Writing a guard

Three rules, each paid for. They are not style: every one of them is the
shortest statement of a defect this repository shipped, and in each case the
guard that should have caught it was already written.

## A branch that looks right and is never taken reads exactly like one that is

**Assert the behaviour, never the position of the call.**

`ats.py` carried `smartrecruiters_gate()` in the right place and a check that
found it there. `None and smartrecruiters_gate()` leaves the text exactly where
that check looks, never runs, and the suite stays green — while `fetch` reaches
a host publishing `User-agent: * / Disallow: /`.

The same shape three more times in one day: a pacing guard that searched the
source for the string `_pace`, so removing the call left the import behind and
nothing failed; a test that asserted a TLS context appears in the source rather
than that `urlopen` receives one; a test that read `smartrecruiters_gate()`
within 500 characters of `def fetch`, which a correct insertion broke.

**So: spy on the thing that acts.** Count the requests. Read the header the
`Request` object carries. Capture the argument `urlopen` was given. *A guard
that reads a name reads the name.*

## A predicate that never fires cannot be told from one that finds nothing

**Count what the walk examined, and exercise the predicate on cases the
repository does not contain.**

These are two different failures and a single assertion catches neither
reliably. A walk that stopped is caught by a denominator: *"the guard compared
three cards"* fails when it compares none. **A predicate neutered to `if False`
is not** — with nothing wrong in the tree, finding nothing is the correct
answer, so the guard passes for the wrong reason.

Measured: on a repository with no market disagreement between overlapping
cards, `if False:` in the comparison left the guard green. The predicate was
extracted and exercised on ten pairs the repository does not hold — five that
must answer yes, five no — and only then did a mutation that ignored the
wildcard turn red.

**Both, always.** A scope counter and a predicate exercise. Writing one while
believing it covers the other happened four times in a day.

## A `.get()` on a key never carried is indiscernible from a key carried whose value is legitimately `None`

**This one is not about guards — it is a trap in API design, and it survives
every fix applied to its instances.**

`_robots.allowed()` returned a subset of what `verdict()` builds. Reading a
dropped field gave `None`, so the gate reported *this host asked for nothing*
about a host asking for ten seconds. The field was added to the carried list.
**One key further along, `group_conflict` failed identically** — and that one
says whether the verdict is reliable at all, so a caller saw a clean boolean
and never learned two records contradict each other about us.

Filling the list repairs instances and leaves the form: the next field added
upstream and forgotten fails the same way, in silence, in the direction that
costs.

**So make the absence loud**, not the list longer. A key the mapping knows
exists upstream and does not carry must raise; a key nobody builds stays an
ordinary miss.

**And keep silence sayable.** A carried field whose value is genuinely `None`
must still answer `None` — otherwise *the host set no rate* becomes
unrepresentable, and that is the very fact the fix exists to distinguish. **A
correction that tightens a screw can remove the only way to say the empty
case**, and that is not recoverable afterwards.

## Three ways a guard fails, and a report has two colours for them

They are disjoint, they are repaired differently, and **the repair everyone
reaches for first is wrong two times out of three.**

| species | what is wrong | reads as | repair |
| :-- | :-- | :-- | :-- |
| **inert** | it *cannot* fail | **green** | rewrite the guard |
| **unexercised** | no test reaches the branch | **green** | add the case |
| **misdescribed** | it fails on **correct** code | **red** | fix what it looks for |

**A green can mean three things** — *there is nothing to find*, *I cannot
find it*, or *I did not look there* — and nothing in the output separates them.
Writing the guard more strongly does not cover a branch no test reaches, and
that is the reflex.

All three were produced in one day, by the same hand, hours apart.

**Inert:** a pacing guard searched the source for the string `_pace`, so
deleting the call left the import behind and nothing failed.

**Unexercised:** two mutations of `_pace` stayed green because the test stubbed
the rules lookup and never reached the fallback branch — the guard was sound
and its case was missing. *Rewriting it would have changed nothing.*

**Misdescribed:** a guard asserted that a source contains `git clean`. It
contains `["git", "clean", "-fdq"]`. **The guard was right about the behaviour,
wrong about the spelling, and it failed on correct code** — the most expensive
kind, because a red is trusted.

**Telling them apart takes a mutation, not a reading.** Break the thing the
guard is for: still green means inert or unexercised, and which of the two is
answered by asking whether any test reaches that line at all. A red on
unmutated code is the third.

## And a bench's runs must be independent

A mutation that removed a *where do I write this* check made the tool save a
body to a file named `None`. Restoring the source left it there, so **the next
mutation ran against a tree the previous one had changed** — and nothing in
either result said so.

*Restoring the source is not restoring the tree.* Clean between runs, not only
at the end, and record what each run left behind. **A bench whose trials are
not independent does not measure what it believes**, and none of its rows will
say otherwise.

**The same applies to reading its output.** A count taken while the file was
being written gave 23 rows for 24 mutations: not wrong, one second stale, with
nothing in the file saying so — and the next step was publishing *23 of 24*
with one unexplained. Write a last line carrying the expected total, and refuse
any file that lacks it. **The flag alone would certify a truncated run; it is
the count beside it that makes the file checkable.**
