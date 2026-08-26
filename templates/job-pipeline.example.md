# Job pipeline — <Full name>

Shared file: `job-scan` fills it and uses it to skip ads already seen;
`cover-letter` reads it and writes the outcome of each application back.

Statuses: `todo` · `applied YYYY-MM-DD` · `rejected YYYY-MM-DD` ·
`no-go YYYY-MM-DD` · `discarded`

- `applied` — sent, no answer yet.
- `rejected` — sent, and the employer said no.
- `no-go` — decided not to apply after reviewing the ad.
- `discarded` — noise or out of scope, never proposed again.

Applications that actually went out = `applied` + `rejected`. Keep them
distinct: a count based on `applied` alone silently drops every application an
employer turned down.

A `~` in front of a match score means it is provisional — read from the search
card only, description not opened.

Pay: gross range, full-time equivalent. `(A)` stated in the ad · `(B)` board
estimate · `(C)` derived · `—` not established.

Last scan: —

## Ads

| ID | Role | Company | Location / mode | Posted | Match | Pay | Status | Note |
| :-- | :-- | :-- | :-- | :-- | --: | :-- | :-- | :-- |

## Log

- <!-- one line per run: date, what was searched, what came back -->
