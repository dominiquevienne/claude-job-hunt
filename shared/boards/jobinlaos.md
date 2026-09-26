# Board measurement — Jobinlaos (`jobinlaos.com`, Laos): «Find Your Dream Job in Laos» — a **white label of `jobsmerch.com`** whose front answers 200 while the platform's API behind it is **dead (522)**; no adapter is possible until that origin answers, so NOT FEASIBLE dated, `blocked` on #653

<!-- verified: 2026-09-25 -->

<!-- hosts: jobinlaos.com, api.jobsmerch.com -->
<!-- script: none -->
<!-- countries: LA -->
<!-- route: none · non faisable — l'API de la plateforme dont ce front dépend (`api.jobsmerch.com`) rend 522 sur TOUS ses chemins et le front ne la proxifie pas (404 sous son propre hôte, et le bundle appelle l'apiBase complet du tiers) ; le front répond 200 mais ne porte aucune annonce ; lèverait le blocage en une requête : `api.jobsmerch.com/api/v1/jobs` rendant autre chose qu'un 522, ticket #653 `blocked` · 2026-09-25 -->
<!-- content: measured · **the front answers (200, 47 897 B) but carries no advertisement: `__NUXT_DATA__` is 384 B / 19 elements with none. The root declares `apiBase: "https://api.jobsmerch.com/api/v1"` — a third party — and `api.jobsmerch.com` answers **522, 16 B** on `/`, `/robots.txt` AND `/api/v1/jobs`. The board is NOT closed: its front serves, and the PLATFORM's origin is off.** · 2026-09-25 -->
<!-- witness: none — the front serves no advertisement and the API serves nothing · 2026-09-25 -->

**Measured 2026-09-25 19:2x–19:4x UTC by the declared client, the guard taken
on each exact path, `bin/fetch-body.py`.** The front and the API are measured in
the **same pass**, so both halves of the finding carry the same hour. *A
measurement, not an adapter.*

```
jobinlaos.com/                       200, 47 897 B   Nuxt shell, <title> still «jobsmerch.com»
  __NUXT_DATA__                      384 B, 19 elements — NO advertisement
  the root declares                  apiBase: "https://api.jobsmerch.com/api/v1"
jobinlaos.com/api/v1/jobs            404, 226 B      the front does NOT relay
api.jobsmerch.com/api/v1/jobs        522, 16 B ×2    «error code: 522»
api.jobsmerch.com/                   522, 16 B
api.jobsmerch.com/robots.txt         522, 16 B
```

## What is broken is the platform, not the board

`jobinlaos.com` is a **white label of `jobsmerch.com`** — eight references in
its own root, and its `<title>` still carries the template's name. **This
explains the anomaly recorded here on 2026-09-17** and left open then: the title
was not a mistake, it is the platform's name showing through the label.

**The 522 is Cloudflare saying the origin behind `api.jobsmerch.com` is off.**
So the scope must be stated exactly: *the third party's API is down*, **not**
*this board refuses us* — its front answers 200 to the declared client.

### The front does not proxy, and that rests on two independent witnesses

1. **`jobinlaos.com/api/v1/jobs` answers 404** under its own host — there is no
   relay at the obvious path;
2. **the bundle calls the third party's FULL `apiBase`** — `$fetch(${o}/auth/refresh)`,
   `${o}/users/profile` — so the site's own configuration points at
   `api.jobsmerch.com` by construction.

**The second witness holds even if the host comes back.** *A proxy could be
added tomorrow; the configuration saying there is none today is a property of
the shipped bundle, not of the host's mood.*

### The refusal is STABLE — and the fingerprint is not what proves it

Two reads, **2026-09-25T19:29:42Z and 19:31:08Z**: 16 bytes, `error code: 522`,
`md5 2c2dae9e9cdd73404ecdd9db22102374` both times.

> **On a 16-byte body an identical fingerprint demonstrates nothing about a
> provider.** *`2c2dae9e9cdd…` is Cloudflare's factory string; finding it on
> another host links no two operators.* **The verdict is carried by the 522 and
> by the host that serves it**; the two reads establish that the refusal is
> **stable**, not where it comes from.

## The rules file reads perfectly — and it is not a rules file

`allowed('jobinlaos.com', '/')` → **open, `certain: False`, `state: unrecognised`**,
and that is the correct verdict.

**CORRECTION of this card's own gloss of 2026-09-17**, which read *«rules
unreadable … the rules file could not be read»*: **the file answers 200 on
1 248 bytes.** It is Cloudflare's **content-signals preamble**, every byte a
comment, setting **no signal** and declaring **no `User-agent` group** — so
nothing could be read *as a rule*, which is a different fact from a file that
did not answer.

> **`certain: False` has more than one branch and they print the same word.**
> *«Not read» and «read, and not rules» reach the identical verdict, so no
> comparison separates them and a gloss of one for the other contradicts
> nothing.* **The field that says what happened is `state`.**

*The doctrine drawn from this file — clause (c) settling its own case, and the
Article 4 sentence being present and inert where no signal is expressed — is in
`shared/robots-policy.md`, because Cloudflare serves this preamble by default
and it is therefore not a note about this board.*

## Consequence: NOT FEASIBLE, dated, and what would lift it

**No adapter is possible while the origin behind `api.jobsmerch.com` does not
answer.** What would lift it is named and costs one request:
**`api.jobsmerch.com/api/v1/jobs` returning anything other than 522.** Ticket
**#653**, labelled `blocked`, carries the dated measurement.

**And Laos stays at ZERO adapters — which is a fact about Laos, not about us.**
Five cards, all `script: none`: `108-jobs`, `cvconnect-la`, `jobinlaos`,
`jobweb-la`, `myworld-la`. #652 is `blocked` (an antirobot control — we do not
defeat it and we ask nobody to defeat it) and #742 as well (a silent host).
**#654 CVConnect and #655 MyWorld Laos are not measured: the country is not
exhausted.**
