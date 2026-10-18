---
name: linkedin-profile-write
description: Fill the user's own LinkedIn profile in their own Chrome, field by field, after they have validated each text in the conversation — and never save for them. Use when the user says "remplis mon profil LinkedIn", "écris mon profil LinkedIn", "complète mon LinkedIn", "fill in my LinkedIn", "rewrite my LinkedIn experience", or asks for the headline or the About section to be written. Milestones 2 to 11 of issue #184: the writing loop, under the owner's decisions of 08.09.2026 and 16.10.2026. Run `linkedin-profile` first — this skill works from a difference, not from a blank page.
user-invocable: true
allowed-tools: Read, Bash(*), ToolSearch, mcp__claude-in-chrome__*
---

# LinkedIn profile — the writing loop

**This milestone writes into the form. It never saves.** *The user validates
every text in the conversation before it enters a field, and the user is the one
who clicks Save — two gestures by them, not one: the first is on the content,
the second on the act.*

## Before anything

**The account is the user's own, in the user's own logged-in Chrome.** *If the
browser is not logged in, stop and say so — do not offer to log in, and never
ask for a password.*

**LinkedIn's user agreement restricts automated access to the service, and the
repository owner settled it on 16.10.2026: we build the function, and we tell
the user.** His decision, verbatim, because a permission that derogates from a
written rule travels whole or not at all: «&nbsp;Oui, nous développons l'outil. Lors de son utilisation par un utilisateur, nous le prévenons que cette fonction est en marge des conditions d'utilisation de la plateforme.&nbsp;»

> **SAY IT, in the first message of the run, before reading or writing
> anything:** this feature operates at the margin of LinkedIn's terms of use;
> the account is the user's own, the browser is their own, and they are the one
> who saves.

**The warning is part of the decision and not an improvement on it.** *Shipping
the function without it would be citing an authorisation without its condition —
and a condition dropped in transit reads exactly like a permission.* **And this
milestone owes it more than the survey did**, *because this one puts text into a
form: the mildest member of the family already owed the warning, so the one that
writes cannot be the one that drops it.*

**The design is settled — the agent fills, THE USER SAVES.** *Design A, the
agent submitting the form, is closed independently of LinkedIn by a constraint
of our own: modifying public content takes an explicit permission action by
action, so no session submits the form for the account holder.*

```
1. the agent PROPOSES the text   in the conversation, not in the form
2. the user VALIDATES it          in the conversation
3. the agent FILLS the field      with the text exactly as validated
4. the user SAVES                 themselves, in LinkedIn
```

**Step 3 writes the text EXACTLY as validated.** *No retouching between the
validation and the keystroke — not a word, not a comma: if the text has to
change, it goes back through the conversation.* **A text the user approved and a
text the agent improved afterwards are indistinguishable in the field**, and
only one of them was approved.

**Never click Save, Submit, Post, Publish, Add or Done on the user's behalf**,
and never press Enter in a form that submits on Enter. *Say which button they
have to click and where it is.*

## The entry condition, and why it is not a formality

**Run `linkedin-profile` first and work from its difference.** *This skill fills
gaps; a skill that starts from a blank page asks the user everything they have
already written down, and proposes entries that already exist under another
wording.*

**And the reading is not done once.** The owner's decision of 08.09.2026 is
«&nbsp;lire avant toute action&nbsp;» — before EVERY action, not only at the start.

> **So before each write: re-read the section you are about to touch, in the
> page, and compare it to what the survey said.** *The page can have changed
> between the survey and the keystroke — the user may have edited in another
> tab, LinkedIn may have restored a draft, an earlier write of this run may have
> reordered the section.*

**This is the repository's own rule about a shared tree, on someone's profile:
the verification goes in the same action as the act, never in the turn
before.** *A state read ten minutes ago is a reading, not a state.*

**If the re-reading disagrees with the survey, stop on that entry and say so.**
*Re-surveying one entry is cheap; writing over an edit the user made themselves
is not recoverable by us — only by them.*

## The order of the session, and why the last two are last

**The scope is the PROFILE and not the flow**, by the owner's decision of
08.09.2026: «&nbsp;les champs manquants devront aussi être remplis&nbsp;»

```
 0. the difference, from `linkedin-profile`      <- the entry condition
 1. identity and contact details                 what is missing ONLY
 2. education      institution · degree · field of study · dates
 3. certifications name · issuer · dates · credential id · URL
 4-8. THE LOOP, one post at a time
 9. skills         the list AND their attachment to the posts
10. languages      language + level, for each
11. headline and About — written LAST, from everything above
```

**The headline and the About close the session, they do not open it.** *They
summarise what the loop collected; written first they would have to be rewritten
at the end, and nobody would.* **They obey the same non-invention rule as the
rest** — *they are the two most-read fields after the name, which makes them the
ones where an invented scope travels furthest.*

> **And this list is not the authority: the form is.** *Enumerate the fields the
> page actually shows and treat them all. A field present in the form and absent
> from this list is to be filled too; a field in this list that LinkedIn has
> removed is not a failure.*

**Character limits are read from the form, never from a list kept here.** *If the
form states a limit, obey it — and if a validated text does not fit, it goes
back to the conversation to be shortened there.* **Never truncate a validated
text to make it fit:** *the user approved a sentence, and half a sentence is not
a shorter version of it.*

## The loop, one post at a time

**One post is one pass, and the pass ends before the next one starts.** *A loop
that gathers five posts and then writes five times has put four of them out of
the user's sight.*

For each post, in this order:

1. **the employer entity** — see below, it is the one choice with a silent
   failure;
2. **title · employment type · location and mode** — on site, hybrid, remote;
3. **the dates**, as the user states them;
4. **the description**, sharpened and validated in the conversation;
5. **the skills attached to this post**;
6. **the projects attached to this post** — name, description, dates, the
   experience it is «&nbsp;associated with&nbsp;», and the project URL.

## The constraint that this issue exists for — «&nbsp;affûter&nbsp;», not «&nbsp;valoriser&nbsp;»

**The owner replaced «&nbsp;valoriser au maximum&nbsp;» with
«&nbsp;affûter&nbsp;», and the word IS the rule.** *«&nbsp;Valoriser&nbsp;»
invites you to ADD — a figure that impresses, a wider scope, a higher title.
«&nbsp;Affûter&nbsp;» only lets you remove the vagueness, tighten, and name things
precisely.* **A sharpened text says the SAME thing, better.**

```
ALLOWED     restructure · condense · cut the filler
            name in the trade's vocabulary what the user described
            put forward what they said and what counts

FORBIDDEN   adding a fact, a figure, a scope, a team size,
            a budget, a technology, a seniority
            — that the user has not stated
```

**The word «&nbsp;affûter&nbsp;» goes to the agent literally.** *An agent told to
valorise will produce facts; an agent told to sharpen will not.*

### The control is POSITIVE, and that is the whole of it

**Before proposing any text, every verifiable claim in it must point at a
sentence of the user's own — or at a line of `profile/`.** What cannot point
anywhere is **removed**, or asked as a **question** — *«&nbsp;you say you led the
team: how many people?&nbsp;»* — **never filled in.**

> **The list of forbidden additions above is a list of EXAMPLES, not the test.**
> *A list of refusals bets that we enumerated the problem, and the next invented
> field will be one nobody wrote down — a certification body, a client name, a
> language level, a date made precise to the month.* **So the floor is positive:
> a clause ships only if it can name its source.** *This repository has the
> defect in its own history under another name — a plausible value where a blank
> belonged — and the only control that held was the one that asked what a value
> was derived FROM.*

**Name the source in the proposal itself.** *Quote the user's sentence next to
the clause it justifies, so the validation is on a mapping and not on a
paragraph.* **A proposal the user cannot audit is a proposal they will approve.**

**Where a document is vague, say so and stop.** *«&nbsp;Led a team&nbsp;» is not
«&nbsp;led a team of eight&nbsp;»: report the sentence as it stands, and let the
user supply the number if they have one.*

*A number nobody said is on a real person's CV, in front of recruiters, and they
are the one who has to defend it in the interview.*

## What the user validates, and what may be batched

The owner's decision of 08.09.2026 is «&nbsp;il est indispensable de faire valider à l'utilisateur&nbsp;» — mandatory, not
optional — and it bears on the four places where the agent chooses in the user's
stead:

| | |
| :-- | :-- |
| **the employer entity** | several candidates with what tells them apart |
| **each sharpened text** | post description, project, headline, About |
| **each skill** | added or attached |
| **each write into the form** | before they save |

**A batch validation is acceptable for SKILLS. It is not acceptable for a
TEXT.** *A user who validates ten descriptions at once has read none of them.*

## The employer entity — the choice with a silent failure

- **Offer SEVERAL candidates with what distinguishes them** — domain, sector,
  size, head office — *never one result presented as the answer.*
- **Say whether what you are about to put in the field is a LinkedIn ENTITY or
  free TEXT.** *A web search that finds the company does not supply a LinkedIn
  page: the field will then accept free text, the post will not be attached to
  the company page, and that difference is visible on the profile.*
- **If nothing is found, the user supplies it and it goes in as free text,
  assumed as such** — not as an attachment.

## Contact fields are ASKED, and that is the owner's own reserve

**The owner's own reserve, verbatim: « Remplir les champs manquants » ne doit pas devenir « publier des coordonnées personnelles »**

**The profile carries contact fields — telephone, address, date of birth, email
— whose visibility is configured separately.** *The rest of the profile is
professional by nature; these are not, and a user may want them empty without it
being an oversight.*

> **So for every contact field: ask explicitly whether it is to be filled, and
> say who will see it.** **This is the only exception to «&nbsp;fill what is
> missing&nbsp;», it is asked, and it is never decided for them.**

**And it is never pre-filled from `profile/`.** *A document in the repository
holding a telephone number is not a permission to publish it.*

## When to stop

**Stop, and say why, on any of these:**

- the browser is not logged in, or the account shown is not the user's;
- the form does not contain the field the difference named — *report it, do not
  hunt for a substitute elsewhere in the page*;
- a validated text does not fit a stated limit;
- the re-reading before a write disagrees with the survey;
- **the page asks a human verification** — *a captcha, a challenge, an identity
  check.* **Never attempt it and never ask the user to defeat one**; say what
  appeared and hand the session back.

**And never trigger a dialog** — a confirm, an alert, a «&nbsp;discard changes?&nbsp;»
modal: a blocked dialog freezes everything that follows, and the run cannot
report what it did.

## What never leaves the browser

**This repository is public.** *No profile content — name, employers, dates,
descriptions, contact details — is ever written into the repository: not into a
card, not into a test, not into an example.* **Tests for this skill use invented
data.** *The user's own documents live in `profile/`, which is not part of the
public tree, and everything this skill produces belongs in the conversation and
in the user's own profile.*
