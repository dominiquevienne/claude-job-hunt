---
name: linkedin-profile
description: Survey the user's own LinkedIn profile in their own Chrome and report what is missing or out of date against the documents in `profile/`. Reads only — it fills nothing in and saves nothing. Use when the user says "améliore mon profil LinkedIn", "improve my LinkedIn", "mon profil LinkedIn est incomplet", "what's missing from my LinkedIn", "compare mon LinkedIn à mon CV", or asks what a recruiter would see on their profile. Milestone 1 of issue #184: the survey and the difference, so a person can see the gap before anything is written.
user-invocable: true
allowed-tools: Read, Bash(*), ToolSearch, mcp__claude-in-chrome__*
---

# LinkedIn profile — survey and difference

**This milestone reads. It does not write, it does not submit, and it asks the
user nothing.** *It produces one thing: the difference between what the profile
says and what the user's own documents say.*

**Why the reading comes first, and comes first every time.** The flow this skill
serves says «&nbsp;edit the existing entry, otherwise create it&nbsp;» — and a
post already present under a slightly different title will be created twice,
because LinkedIn does not prevent it. *A survey taken once at the start is not
the same as a survey taken before each action: the page can change between the
reading and the writing, and the later milestones write.*

## Before anything

**The account is the user's own, in the user's own logged-in Chrome.** *If the
browser is not logged in, stop and say so — do not offer to log in, and never
ask for a password.*

**LinkedIn's user agreement restricts automated access to the service, and the
repository owner settled it on 16.10.2026: we build the function, and we tell
the user.** His decision, verbatim, because a permission that derogates from a
written rule travels whole or not at all: «&nbsp;Oui, nous développons l'outil.
Lors de son utilisation par un utilisateur, nous le prévenons que cette fonction
est en marge des conditions d'utilisation de la plateforme.&nbsp;»

> **SAY IT, in the first message of the run, before reading anything:** this
> feature operates at the margin of LinkedIn's terms of use; the account is the
> user's own, the browser is their own, and they are the one who saves.

**The warning is part of the decision and not an improvement on it.** *Shipping
the function without it would be citing an authorisation without its condition —
and a condition dropped in transit reads exactly like a permission.* **This
milestone only reads pages the user is already looking at, which is the mildest
form, and it owes the warning all the same:** *reading a logged-in account with
a browser tool is already an automated interaction with the service, so «&nbsp;we
only read&nbsp;» is a reason to keep the warning short, never to skip it.*

**And the design is settled too — the agent fills, THE USER SAVES.** *Design A,
the agent submitting the form, is closed independently of LinkedIn by a
constraint of our own: modifying public content takes an explicit permission
action by action, so no session submits the form for the account holder.* The
sequence every later milestone obeys:

```
1. the agent PROPOSES the text   in the conversation, not in the form
2. the user VALIDATES it          in the conversation
3. the agent FILLS the field      with the text exactly as validated
4. the user SAVES                 themselves, in LinkedIn
```

*Two gestures by the user, not one: the first is on the content, the second on
the act.* **The bound is written in the milestone that READS rather than in the
one that writes, on purpose** — *a milestone that opens by choosing its own
design has already chosen A, and the paragraph this one replaces said the owner
had yet to decide, which was true when it was written and stopped being true on
16.10.*

## Step 1 — enumerate the fields, do not recall them

**Open the section's own edit form and list the inputs it actually shows.**

> **The form is the authority. A list written in this file is a snapshot of a
> product that changes.** *Any inventory kept here would be true on the day it
> was written and quietly incomplete afterwards — and an incomplete inventory
> reports a field as absent from the profile when it is absent from our list.*

For each section, record: the field's label, whether it is filled, and its
character limit if the form states one.

**Sections to visit** — *this list is where to LOOK, not what to expect:*

```
Identity     first name · last name · headline · location · industry
About        the summary
Experience   one entry per post
Education    one entry per course
Certifications · Projects · Skills · Languages
```

*Two of these are the most-read fields after the name — the headline and the
About — and the flow this skill serves did not produce them at all.*

## Step 2 — read the profile as it is

**Section by section, entry by entry, with dates.** Record what is there
verbatim; do not summarise, do not judge yet.

**An entry that exists under a different wording is still that entry.** *Match
on employer and date range before matching on title: a post held from 2020 to
2023 at one employer is one post however each source names it.*

## Step 3 — read `profile/`

`profile/` holds the user's own documents — CV, certificates, portfolio pieces.
**Read them to fill in what the profile lacks, rather than asking the user
things they have already written down.**

*If `profile/` is absent or empty, say so and continue: the survey of the live
profile is still worth having, and «&nbsp;nothing to compare against&nbsp;» is a
result.*

## Step 4 — produce the difference, and nothing else

**Three columns and no fourth:**

| | |
| :-- | :-- |
| **absent** | the profile has no such entry or the field is empty |
| **divergent** | both have it and they do not agree — quote both, verbatim |
| **unverifiable** | `profile/` says nothing either way |

**«&nbsp;Unverifiable&nbsp;» is a result and it is the one that gets dropped.**
*A field neither source covers is not a gap in the profile; reporting it as one
sends the user to invent something.*

### What the difference must never do

**Never propose a fact the user has not stated.** *This skill's later milestones
rewrite text, and the word for what they do is «&nbsp;affûter&nbsp;» —
sharpen — never «&nbsp;valoriser&nbsp;».* **Restructure, condense, name the
trade's vocabulary precisely, put forward what the person said. Never add a
figure, a scope, a team size, a budget, a technology or a seniority the user has
not stated.**

> *A number nobody said is the same defect as a city taken from the publisher's
> address — a plausible value where a blank belonged. The difference is that
> this one is on a real person's CV, in front of recruiters, and they have to
> defend it in the interview.*

**Where a document is vague, the difference says so and stops.** *«&nbsp;led a
team&nbsp;» is not «&nbsp;led a team of eight&nbsp;»: report the sentence as it
stands and let the user supply the number, in a later milestone, if they have
one.*

## Step 5 — hand it over and stop

**Print the difference. Do not offer to fix it in the same breath.** *This
milestone exists so that a person can see the gap before anything is written
into their profile, and an assistant that surveys and immediately proposes
edits has removed the pause the milestone is for.*

## What never leaves the browser

**This repository is public.** *No profile content — name, employers, dates,
descriptions, contact details — is ever written into the repository: not into a
card, not into a test, not into an example.* **Tests for this skill use invented
data.** *The user's own documents live in `profile/`, which is not part of the
public tree, and the difference this skill produces belongs in the conversation.*
