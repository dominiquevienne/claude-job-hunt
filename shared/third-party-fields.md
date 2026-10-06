# A third party's fields, and why an empty list of withholdings proves nothing

**#1007.** A board hands us a vacancy. It may also hand us a **person** — the
recruiter's name, their photograph, the hour they were last online, the exact
coordinates of a workplace. Nobody asked for those, and they travel into the
candidate's own ledger, where they persist.

## The defect this file exists for

**A redaction rule written around the FORMS of contact — an `@`, a run of
digits — finds NOTHING on a payload that carries no `phone`, `email` or `tel`
key, and writes «nothing was withheld» on a board that ships a named
individual on every advert.**

*Measured on JobToday, 2026-10-05: `company.hiringManager` present on **48 of
48** with `name`, `image` and `lastOnline`; `addressInfo` with `coordinates`
and `ghash`; and **zero e-mail addresses, zero contact-shaped keys**.*

> **This is `declarer-avoir-retenu-ce-que-personne-na-depose` taken from its
> worse end.** *There, the output ASSERTED a discretion we had not exercised — a
> lie about us, and detectable because the claim was made. Here the output is
> SILENT: there is no claim to check, and nothing in it is false.* **A board
> that hands over a person is indistinguishable, in our output, from a board
> that hands over nothing.**

**And the pattern fails in BOTH directions at once, measured on the same page:**
a plain e-mail regex returns **seven** matches of which **not one is a
contact** — a Sentry DSN, an obfuscated token, and the filename
`share-pict-1200x630@2x.jpg`. *It invents matches where there is nothing and
misses the person who is there.*

## The rule

1. **Redaction is named by FIELD, never by pattern.** *A pattern describes the
   shapes we thought of; a field list describes what the board actually sends.
   The first ages against every new board; the second is re-read on each one.*
2. **A field whose meaning you cannot state is withheld, not passed through.**
   *That default needs no decision: it is the only one whose failure is
   visible.*
3. **The declaration follows the RECORD, never the board.** A record carrying
   none of the fields declares none — *naming what was never there lies about
   our discretion instead of about the host.*
4. **A field PRESENT is not a field FILLED, and the floor is POSITIVE.** See
   below: `if x` cannot tell them apart, and a deny-list of sentinels is
   defeated by one character.
5. **What was LOOKED FOR is emitted beside what was dropped.** An empty list of
   withholdings is not a statement; an empty list beside a list of inspected
   names is.

## The mechanism — `_provenance.third_party(record, fields)`

    inspected   every field name the adapter asked about     <- the PROOF we looked
    withheld    those present and carrying a real value
    absent      those asked about and not sent by the board
    placeheld   present, but holding a placeholder

**`withheld: []` with a non-empty `inspected` means «we looked and the board
sent nothing».** *An adapter that emits no `inspected` at all is then visibly a
different thing from one that emits an empty `withheld` — which is the whole
point, and why `inspected` is not optional.*

### The floor is positive, because a deny-list is defeated by one character

**`"$undefined"` is a real stored value** (measured by `cd`). A list of
sentinels to reject that knows `undefined` does not know `$undefined`, and
counts it as a value.

So the floor judges the value's **CORE**: strip everything that is not a letter
or a digit, lower-case it, and ask whether what remains **is** a placeholder
word.

    "$undefined"               -> "undefined"               placeholder
    "N/A" / "n/a"              -> "na"                      placeholder  (the list MISSED it)
    "(null)" / "--" / ""       -> "null" / "" / ""          placeholder
    "undefined behaviour in C" -> "undefinedbehaviourinc"   A VALUE
    "0" / "false"              -> "0" / "false"             A VALUE

**`0` and `false` are deliberately NOT placeholders**: they are what a count of
zero and a boolean false look like, and a floor that ate them would drop real
data to avoid a sentinel. *The cost is that a board using the string `"0"` as
its own sentinel is not caught — written down so the next session widens this
on a MEASUREMENT and not on a hunch.*

## Worked example, and it is the Done-when of #1007

Re-reading the JobToday payload from this file alone, the fields that come out
named are:

| field | and why |
| :-- | :-- |
| `company.hiringManager.image` | a third party's photograph — rule 1 |
| `company.hiringManager.lastOnline` | **presence history**, not a way to reach anyone — the owner decided it on 2026-10-06 |
| `addressInfo.coordinates` | a point, where the town suffices — rule 2 |
| `addressInfo.ghash` | the same point, encoded |

**`company.hiringManager.name` is KEPT** — the owner's decision of 2026-10-06,
verbatim *« applique ta reco »* on *« garder le nom si une lettre doit
s'adresser à quelqu'un, écarter la photo et `lastOnline` »*. *A cover letter may
need to address someone.*

**And exercising the host added two the issue had not named** —
`addressInfo.display` (a STREET address, more precise than the coordinates it
did name) and `addressInfo.itemId` (the geohash again, equal to `ghash` on every
record measured). *An issue names the specimen; the class is measured.*

## The other direction, which this file also has to make sayable

**Ntchito exposes no contact at all** — `_application`, `_company_name` and
`_job_location` empty on 5 of 5, no address in the payload. *So its withheld
list is legitimately empty, and the tri-state is what says so: the same six
names appear under `absent` instead of under `withheld`, with `inspected`
non-empty either way.* **On JobToday the silence would have been the lie; here
it is true, and the output states it rather than leaving it to be read either
way.**

## What never appears anywhere

**No name, coordinate, geohash, photograph URL or presence timestamp appears in
this file, in any card, in any issue, or in any commit message.** *Verified
mechanically before delivery, both by `cd` on the issue and by `ab` on the
adapter: the values are read, classified by name, and dropped.*
