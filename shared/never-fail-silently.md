# Never fail silently

**This is the plugin's first rule, and it outranks every convenience.** It
applies to both skills, every module, every adapter, every script — and to any
contribution added later.

A job search is invisible work with delayed feedback: the user finds out weeks
later, from a silence, that something did not happen. **They cannot audit what
you did not tell them.** A scan that quietly covered half its searches, a resume
quietly missing two jobs, an application quietly never sent — each looks exactly
like success until it is far too late to fix.

So: **anything that did not happen, happened partially, or happened on a guess
must appear in the run's own output.** Not in a log file. Not on request. In
what the user reads when the run ends.

## The five failures this rule exists to prevent

| Silent failure | What it looks like to the user | What you do instead |
| :-- | :-- | :-- |
| **A skipped step** | Everything seemed fine | Name it, say why, say what it costs, give the fix |
| **A partial result presented as complete** | "8 new ads" — from 3 of 8 searches | Report *n of m*, always. `Ran 3 of 8 searches (LinkedIn throttled after the third)` |
| **A guess dressed as a fact** | A confident postcode, a score on an unread ad, a claimed skill | Mark it: `~` for a provisional score, "to be established" for a missing field, and never claim a skill the record does not carry |
| **An unconfirmed action reported as done** | "Applied" for an application nobody saw land | `applied` requires a confirmation you *saw*. Otherwise `todo` + `send not confirmed` |
| **A silent cap** | Top-10 results from 40 found | Say what was dropped and why: `read 12 of 26 descriptions — stopped to stay under the board's rate limit` |

## What every run owes the user at the end

When **anything** was skipped, degraded, guessed or capped, close with a short
block that says so. Not an apology — an inventory:

> **Not done this run**
> - jobup: skipped — `enabled: true` but no `language` set. Fix: `/job-setup boards`
> - 3 of 18 descriptions unread — the list re-ordered; their scores are marked `~`
> - No `repos.md`, so scoring saw only what your exports declare

When nothing was skipped, **say that too**, in one clause. "All 8 searches ran,
all 12 descriptions read" is information. Its absence is what makes users
wonder.

## HTTP 200 is not a yes

**The dominant way this plugin fails silently is not a crash. It is a site
answering successfully while meaning "no".** Thirteen adapters have now been
built against live sites, and **every one of them** turned up at least one case
where a request that looks like it worked carries a refusal — or, worse, where a
refusal comes back looking like data.

They were all found the same way: by deliberately asking wrongly and looking at
what came back. None was visible in the response status.

| What was asked | What came back | What it actually meant |
| :-- | :-- | :-- |
| umantis, a vacancy at the wrong `Description` segment | `200` + the tenant's chrome | wrong URL — the segment is per **vacancy** |
| umantis, an unallocated tenant number | `200` + the vendor's marketing page | wrong host, not an employer with nothing open |
| umantis, a client-rendered tenant | `200`, 64 kB, **zero** vacancy rows | the listing is not in the HTML; the board is not empty |
| SmartRecruiters, an unknown tenant | `200`, `totalFound: 0` | wrong tenant **or** nothing open — and nothing can separate them |
| SmartRecruiters, `limit=500` | `200` with **100** results | silently clamped; the rest of the board is invisible |
| SmartRecruiters, `city=boston` | `200`, zero | wrong case — `Boston` returns 17 |
| jobup / jobs.ch, `location=geneve` | `200`, zero, on **both** boards | missing accent — `Genève` returns 11 |
| HiringCafe, a city without its region | `200`, **0** ads — the same object **with** the region returns 2 162 | an incomplete location, not an empty market |
| Lever, a location string the employer does not use | zero kept | the board was not empty; the filter was |
| Lever, the wrong one of its two disjoint hosts | `404` | the employer exists, on the other host |
| Workday, a hardcoded location facet name | filters nothing at all | the facet name is per-tenant configuration |
| SuccessFactors, `/search/?q=<anything>` | `200`, byte-identical each time | client-rendered shell; it lists nothing for anyone, ever |
| SuccessFactors, `/search/rss/` | `200`, HTML | not a feed — the one shape that should have bypassed rendering |

And the same trap runs backwards, which is worse, because the failure looks
like data:

| What was asked | What came back | What it actually meant |
| :-- | :-- | :-- |
| HiringCafe, `short_name: "ZZ"` — a country that does not exist | **124 plausible ads** | not zero, not an error: ads from nowhere in particular |
| Indeed, a search with no matches | the "no results" banner **and six valid cards** | browsing-history suggestions — harvest them and six unrelated ads enter the ledger |
| Michael Page, a search with no matches | `404` | a real zero, not a broken domain |
| Michael Page, an ad page | `200` with **invalid** JSON-LD | literal newlines inside JSON strings; a strict parser sees no ad at all |
| LinkedIn, a results page | `(25)` in `<title>` | the unread-messages badge — the same `(25)` appeared on 2 259 results and on 2 |

### What follows from it

**1. Never convert an empty result into a statement about the market.** *"No ads
matched"* is a fact about a request. *"They are not hiring"* is a claim about the
world, and on the boards above the two are routinely different. Say which one
you are reporting, and if you cannot tell them apart — SmartRecruiters, by
construction — **say that too**.

**2. Every adapter must document its zero-shaped answers**, alongside its
selectors. An adapter that describes only the happy path hands the next reader a
zero with no way to interpret it. See the contract in `shared/boards/README.md`.

**3. Prefer a refusal to an empty result.** Where an adapter can tell that the
request itself was wrong — a vendor page, an unparseable block, a shell with no
rows — it should **fail loudly with its own exit code** rather than print
nothing. Printing nothing is indistinguishable from a board with nothing on it,
which is precisely the confusion this page exists to prevent.

**4. When you write an adapter, ask wrongly on purpose.** A wrong tenant, a
wrong case, a missing accent, an oversized page, an id that does not exist. That
is where every entry in the tables above came from, and none of them would have
been found by reading the site's documentation or the adapter's own code.

## Empty is a result, not a silence

**First establish that it is a zero** — see the section above; on several boards
an empty result is a refusal wearing a `200`. Then report it.

Zero new ads, zero matches above threshold, zero pending rows — **report the
zero and why it happened**: how many ads were seen, how many were already in the
ledger, how many were discarded and on what grounds. A run that ends with
nothing to show and says nothing is indistinguishable from a run that broke.

## Errors

- **Never swallow a tool error.** If a call fails, say which one and what it
  means for the result.
- **Never retry the same failing action in a loop.** Two attempts, then stop and
  tell the user what you tried, what happened, and what you need from them.
- **Never route around a blocker that exists for a reason** — a login wall, a
  file picker, a modal that is not in the accessibility tree. Those are dead
  ends by design. Hand them over explicitly; do not improvise a workaround and
  report success.
- **A missing prerequisite is not an error, it is a task** — see
  `shared/prerequisites.md`. Name it, offer the fix, take the fallback.

## Degrading is allowed. Degrading quietly is not

The plugin is *built* to keep working with less: no browser, no LaTeX, no
`repos.md`, no board enabled. Every one of those paths is legitimate and should
be taken rather than stopping the user's work.

**The only thing that is forbidden is taking one without saying so.**
