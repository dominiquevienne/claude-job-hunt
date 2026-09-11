# Board measurement — jobmali.com (Mali): the name resolves, the host never answers — INDETERMINATE, and an indeterminate is not probed

<!-- verified: 2026-09-11 -->

<!-- hosts: jobmali.com, www.jobmali.com -->
<!-- script: none -->
<!-- countries: ML -->
<!-- content: indeterminate · the rules file timed out on every one of 12 attempts across 4 reads (apex and www, 14:00–14:17 UTC); no byte received, no status, no rule · 2026-09-11 -->
<!-- witness: none — no body was ever received: four reads of the rules file, twelve attempts, every one a timeout · 2026-09-11 -->

**This card is a measurement and not an adapter, and the measurement is an
absence of answer, dated.** *`jobmali.com` was named in the Atlas's «twenty
hosts named and never asked» (#147); it had no card.* **Asked, it neither
refuses nor permits: it does not reply.**

## Step 1 — the name resolves, the rules file times out: 4 reads, 12 attempts, 0 bytes

```
1.1.1.1 / 8.8.8.8    jobmali.com        54.243.117.197  13.223.25.84   NOERROR    (both resolvers, both forms)
                     www.jobmali.com    13.223.25.84    54.243.117.197  NOERROR

bin/fetch-body.py https://jobmali.com/robots.txt        #1 14:00:29Z   3 attempts, all "timed out"   state unreachable
                                                         #2 14:05:58Z   3 attempts, all "timed out"
bin/fetch-body.py https://www.jobmali.com/robots.txt    #1 14:11:26Z   3 attempts, all "timed out"
                                                         #2 14:16:56Z   3 attempts, all "timed out"
```

**Four reads, twelve attempts, zero bytes.** *The guard's verdict is
`INDETERMINATE` — «an unknown, not a permission and not a refusal» — and it is
the same on the apex and on the `www`.* The addresses are Amazon's (AWS); what
listens there, if anything, did not say.

> **A timeout is neither a refusal nor a permission, and an INDETERMINATE is
> not probed** — no root, no listing, no TCP by hand: a request past the
> rules file that could not be read is the act the rule might forbid. *This is
> not family (1) (no 403, no body), not a challenge, not a written refusal; it
> is not on #222, whose members answer a browser. It is a measurement to
> redo.*

## What would settle it, and who

**The same two requests, on another day** — the rules file answering with a
body, or a status. *If it answers 403 with the 25-byte vendor default, it joins
#222; if it answers rules, step 1 resumes from them; if it times out again, the
date on this card moves and nothing else does.* **Nothing here says the board
is closed, and nothing says it is alive.**

## What this card does not say

Nothing about the board, its size or its markup — no byte was received. **And
nothing about the operator's intention — no rule was read.** *«Mali's
`jobmali.com` did not answer on 2026-09-11» is the sentence; «Mali has one
board fewer» is not.*
