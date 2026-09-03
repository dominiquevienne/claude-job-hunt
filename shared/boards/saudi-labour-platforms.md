# Assessed, no adapter — Musaned and Ajeer (Saudi Arabia)

<!-- verified: 2026-09-03 -->
<!-- hosts: musaned.com.sa, ajeer.qiwa.sa -->

Both permit reading — `ajeer.qiwa.sa` publishes `User-agent: *` with a bare
`Disallow:`, and `musaned.com.sa` serves markup for its `robots.txt`, so no
rules were read and none were invented.

**Neither is a job board, and neither has a public listing of vacancies.**

## Musaned (مساند) — a directory of agencies, not of jobs

The platform through which **households** contract domestic workers via
licensed offices. Its `/marketplace` route is titled *"Recruitment Companies &
Offices — List of licensed recruitment offices and companies"*: it lists
**agencies**, not vacancies. Everything transactional is behind `Sign In`.

**And this is one to leave alone rather than dig at.** The records this
platform exists to move are about **individual migrant domestic workers**, not
job advertisements. Even if a data route were found, it would not be job data,
and it is the kind of data an adapter has no business collecting.

## Ajeer (أجير) — labour transfer between establishments

A Remix single-page application whose landing page is 86 lines of text and 45
asset links, with no content routes. Ajeer exists so establishments can **lend
or transfer** workers to one another; the party who signs in is an employer,
not a candidate. **No vacancy listing exists to read**, public or otherwise.

## The rule this stops on

Neither is refused, and neither is closed. **They are simply not boards**, and
the assessment stops there rather than at an authentication wall — which
matters, because "it needs a login" invites someone to make one. **This
repository does not create accounts**, and here it does not need to: there is
nothing behind the login that is a job advertisement.
