# Reading a board's terms of use

<!-- verified: 2026-09-02 -->

`shared/robots-policy.md` governs machine-readable refusals. **Terms of use are
prose, and a different object**: they are written for many readers at once, and
the question is which of those readers a clause is addressed to.

This file is the one place that answers it. **An adapter file applies the rule
and records its working; it does not re-derive the rule**, because when each
file decided from scratch the answer depended on who read it that day —
Singapore was read too strictly and needed a correction. Issues #48 and #81.

## The position

**An agent of this kind is a tool the user starts, not a harvester.** In the
user's own words:

> *Toujours considérer le sweep comme un utilisateur standard du point de vue
> des conditions générales. Il ne s'agit jamais de moissonner des offres pour
> en revendre l'accès. Il s'agit de trouver les bonnes offres pour un candidat
> et les lui soumettre rapidement en fonction de critères qu'il a défini.*

Four things are true of every sweep this project performs, and they are what a
clause is read against:

- **One person, their own search**, at their request, on their machine, in
  their own session where a board requires one. Nothing runs on a schedule
  nobody asked for.
- **Their criteria, not a corpus.** The work is reducing thousands of ads to
  the handful matching one profile — the opposite of accumulating.
- **Nothing is republished, resold or served onward.** The ledger keeps
  identifiers, URLs and the fields a match is scored on.
  `mycareersfuture.py` is the shape: the description is read to measure its
  length and dropped, and the row carries `description_chars`.
- **The output is a shortlist a person reads**, not a database.

**A clause written against commercial harvesting does not describe that**, and
reading it as though it did makes the plugin refuse work its own user is
entitled to do.

## What this does not license — read this before applying anything above

**The position changes how an ambiguous clause is read. It never creates
permission where a board withheld it.** Concretely, and none of these bend:

- **A clause that forbids automated access *as such* still binds.** Leboncoin's
  *"It's forbidden to use search robots or other automatic methods to access
  Leboncoin.fr"* is not about harvesting or resale; it is about the means. It
  binds, and that board has no adapter and will not get one.
- **A rate limit still binds**, and so does a pace a board asks for in prose.
  Being one candidate is a reason to be slow, not a reason to be exempt.
- **A login wall is not worked around.** Not credentials, not paywalls, not
  consent walls, not anything an authentication guards.
- **Nothing here overrides `robots.txt`.** That is a separate instrument with
  its own policy and its own four questions, and this file does not open a
  door in it. A board that refuses in `robots.txt` is refused whatever its
  terms say about harvesting.
- **Personal data is out of scope entirely** — a candidate profile, an
  employer's named contact, a recruiter's direct line. `vieclam24h.md` is the
  worked example, and it excludes those fields for reasons that have nothing
  to do with this page.
- **The user signs.** This file is about how a document is read. It is never
  about acting against a board that has said no, and it never moves
  responsibility for what somebody submits or where they apply.

**And the repository has already gone further than this rule requires, on
purpose.** `softy.md` describes a site whose `robots.txt` blocks no script at
all but enumerates AI agents by name and refuses Anthropic's twice. The letter
left the door open; the sweep was routed through the user's own browser anyway,
because *"a plugin whose whole function is OpenWork reading job ads for you sits
inside the spirit of that refusal even when it is outside its letter"*. **That
decision stands, and it is the shape of this whole page**: being a user-driven
tool is a reason to read an ambiguous clause fairly, never a reason to argue
past a publisher who named us.

**If the reasoning has to be strained, the answer is the restrictive one** —
the same closing rule as `shared/robots-policy.md`, and for the same reason.

## Two clauses that look alike and do not bind alike

| | A **harvesting** clause | An **anti-automation** clause |
| :-- | :-- | :-- |
| What it names | resale, redistribution, republication, building a competing service, aggregation | robots, crawlers, scripts, *automatic means*, non-human access |
| Who it is addressed to | somebody making a product out of the board | anybody not using a browser |
| What it does to a sweep | **nothing** — the sweep does none of those things | **it binds** — the sweep is exactly what it names |
| What it may still restrict | what is *kept* and what is *published* | the access itself |

**The distinction is the whole of this file.** A clause about resale usually
restricts **storage and publication** rather than reading, and the honest
response is to narrow what the adapter keeps — not to refuse to look.

Three decided cases, each keyed to its own document:

- **Adzuna** — the terms exclude *aggregation* by name ("vacancy counts,
  average salaries … in aggregation"). So **no Adzuna figure enters anything
  this project publishes**, and searching under a registered key is untouched.
- **Kalibrr** — the clause forbids reproducing and disseminating *content*. A
  number this project measured is neither, so volumes and fill rates **are**
  published, with the reasoning on the page carrying them. *The documents
  differ; the practice does not.*
- **MyCareersFuture** — a retrieval-system and caching clause. The adapter
  therefore **never writes the text of an ad**, reads the description only to
  count its characters, and sends the reader to the URL. §16 is a prohibition
  with an exception, **not a permission counter**: saying it "provides for
  permission to go further" reads the clause from the wrong end, and that is
  the correction this rule exists to prevent repeating.

## What an adapter file must record

**Quote before concluding.** Three things, so a later reader can disagree with
the reading without having to find the clause again:

1. **The clause, quoted**, with its section number and any twin. Documents are
   often written twice — MyCareersFuture binds *Visitors* at §3–21 and
   authenticated users at §22–42, and the adapter operates as a Visitor.
2. **The reading applied**, in one or two sentences: which of the two kinds of
   clause it is, and what it restricts — access, storage, or publication.
3. **The date it was read**, because terms change and a quotation without one
   ages into a claim.

`shared/boards/mycareersfuture.md` and `shared/boards/kalibrr.md` are the
worked examples. A file that concludes without quoting is not applying this
rule; it is repeating somebody's impression of a document.

## The pass over what already shipped

**Done 2026-09-02.** The search, so it can be repeated or faulted: all 67
adapter files plus `shared/boards/README.md`, matched on *prohibit*, *forbid*,
*not permitted*, *interdit*, *licence*, *restriction*, then each hit read to
see whether it reasoned from prose terms or from `robots.txt`.

**Four reason from prose terms**: `adzuna.md`, `kalibrr.md`,
`mycareersfuture.md`, `turijobs.md`. The rest turned out to be about
`robots.txt` paths (`hellowork`, `meteojob`, `stepstone`, `taleez`,
`softy`, and Leboncoin in the README) or about an unrelated word — `softy.md`'s
*driving licence* in a list of ad fields.

**That search found no shipped adapter refusing a sweep on the strength of a
harvesting clause.** Every restrictive conclusion in the four is about **what
is kept or published** — aggregate figures, ad text, a recruiter's name —
which is what those clauses actually govern. The one file that had read a
clause the wrong way round, MyCareersFuture's §16, was corrected before this
rule was written.

So the inconsistency this rule fixes was **in the reasoning, not yet in the
outcomes**: each file re-derived the question, and one of them got it wrong.
Recording that the pass found no second error is part of the finding — a rule
justified by a fault it cannot point at would be a rule justified by fear.
