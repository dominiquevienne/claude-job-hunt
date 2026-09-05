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
