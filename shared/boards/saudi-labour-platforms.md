# Assessed, no adapter — Musaned and Ajeer (Saudi Arabia)

<!-- verified: 2026-09-03 -->
<!-- hosts: musaned.com.sa, ajeer.qiwa.sa -->
<!-- countries: SA -->

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
asset links. **What that landing page does *not* establish is the absence of
content routes** — a Remix application splits them and loads them client-side,
so they are invisible from the landing page by construction. That is the trap
`umantis.md` documents two files away, and the earlier wording here — *"with no
content routes … no vacancy listing exists to read, public or otherwise"* —
inferred it from a page. **Corrected 2026-09-03.**

**The verdict stands on a different argument, and it never needed the page:**
Ajeer exists so establishments can **lend or transfer** workers to one another;
**the party who signs in is an employer, not a candidate.** That is what it is
for, not what a page happened to show — and it is why there is no adapter.

## The rule this stops on

Neither is refused, and neither is closed. **They are simply not boards**, and
the assessment stops there rather than at an authentication wall — which
matters, because "it needs a login" invites someone to make one. **This
repository does not create accounts**, and here it does not need to: there is
nothing behind the login that is a job advertisement.
