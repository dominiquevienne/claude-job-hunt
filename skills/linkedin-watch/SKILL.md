---
name: linkedin-watch
description: Read the user's LinkedIn feed in their own Chrome and pull out the job leads nobody posts on a board — "my team is hiring", "we're looking for a…", a connection sharing an opening. Produces a separate report and never touches the ledger. Use when the user says "regarde mon fil LinkedIn", "check my LinkedIn feed", "des offres dans mon réseau ?", "any leads on LinkedIn", "veille LinkedIn", or asks what their network has been hiring for. Reads only; it applies to nothing and writes nowhere.
user-invocable: true
allowed-tools: Read, Bash(*), AskUserQuestion, ToolSearch, mcp__claude-in-chrome__*
---

# LinkedIn feed — leads, and what they are not

**A post is not an advertisement.** *No structured employer, no location, no
contract type, usually no URL.* **So this skill writes a report of its own and
never the ledger** — mixing an inferred inventory into a measured one would make
the board-coverage counters include unverified leads, and no figure would become
visibly wrong.

## The feed has no denominator, and the report has to say so

**The feed is algorithmic. Two passes do not return the same posts, and there is
no «&nbsp;total posts in my network&nbsp;» to consult.**

> **Never write «&nbsp;N leads out of M posts&nbsp;».** *There is no M.*
> **Write «&nbsp;N leads in the P posts I saw, between HH:MM and HH:MM, scrolling
> until &lt;stop rule&gt;&nbsp;».**

**Two things follow, and they are not stylistic:**

1. **The stop rule is chosen before scrolling and printed in the report** —
   a scroll depth, a post count, or the date of the oldest post reached.
   *A run whose stopping point is decided afterwards has no denominator AND no
   boundary.*
2. **No claim of completeness, in any wording.** *Not «&nbsp;the feed holds
   nothing else&nbsp;», not «&nbsp;no openings this week&nbsp;».* **On a feed
   that is not exhaustive, zero means «&nbsp;none in what I was shown&nbsp;» and
   nothing more** — and a reader takes «&nbsp;no openings this week&nbsp;» as a
   fact about the market.

## Scope is an option, asked at run time

```
posts only            the default — high precision, little to sift
posts + comments      real openings often live there («DM me»)
                      -> every post becomes several reads
```

**Ask which, with `AskUserQuestion`, before the first scroll.** *The second mode
multiplies fetches: it takes its own pace and its own stop rule, and the report
says which mode produced it.* **A report that does not name its mode cannot be
compared with the next one.**

## The author of a post is not the employer

**Sometimes they are — and that is exactly what makes the inference tempting and
wrong the rest of the time.**

> **Carry what the source IS, not what you deduce from it.** *Record «&nbsp;posted
> by X&nbsp;», never «&nbsp;employer: X&nbsp;», unless the post itself names the
> employer.*

*A recruiter posting for a client, an employee relaying a colleague's opening, a
connection resharing a stranger's post: three shapes, one field, and only the
post's own words separate them.*

**Same for everything else the post does not state.** *If it says «&nbsp;Product
Owner in Lausanne&nbsp;» and names no company, no contract and no rate, the
report says a Product Owner in Lausanne and leaves the rest empty.* **An empty
field is a measurement; a filled one that nobody stated is a fabrication.**

## Three verdicts, and the third one is not an absence

| | |
| :-- | :-- |
| **lead** | the post states an opening, in its own words |
| **uncertain** | it may be one and the post does not settle it |
| **not a lead** | it is something else |

**«&nbsp;Uncertain&nbsp;» is reported as uncertain and counted separately.**
*A lead one cannot classify is not an absence of an opening — and folding it
into either of the other two turns a limit of the reading into a property of the
network.*

*«&nbsp;We're growing!&nbsp;» with no role named is the ordinary case, and it
belongs in that column rather than being resolved by guessing.*

## Deduplicate against the ledger — read it, never write it

**A post pointing at an advertisement already in the ledger is flagged as
already known rather than proposed a second time.**

*The prefix defect that made this unreliable — two spellings for one board that
never met — was fixed on 2026-09-08 (#188), and a closure guard now asserts that
every prefix an adapter can emit names a card this repository knows.* **Five
ledger lines written under the old spelling remain orphaned**, so a match
against them can still fail; that is a data question the repository owner holds,
not a defect of this skill.

## What never leaves the browser

**This repository is public, and this corpus is more sensitive than a job
board's**: *the posts are written by real people the user knows, under their own
names.*

**No post text, no author name, no company name from the feed is ever written
into the repository** — not into a card, not into a test, not into an example.
**Tests for this skill use invented posts.** *The report belongs in the
conversation, and in a file under the user's own workspace if they ask for one.*

## What this skill does not do

**It applies to nothing, contacts nobody, and writes nowhere.** *It does not
message the poster, does not react, does not follow, and does not open a
conversation — every one of those is an action on the user's account, under
their name, visible to people they know.* **The report ends with the leads; what
to do about them is the user's next move, taken by them.**
