# When this plugin overrides a robots.txt

**The default is to obey, and it is not close.** This file exists because
"obey" and "refuse" were being decided board by board, and one board — the
Austrian AMS — is now decided the other way. A rule applied once is a
preference. A rule written down is a policy, and it has to explain the cases it
already decided as well as the new one.

`robots.txt` is not law. It is the operator's stated wish, published in the one
place a machine will look. This plugin's users are individuals asking for a
fetch on their own behalf — the `Claude-User` class, not a training crawl — so
the wish is usually aimed at somebody else. **That is a reason to read the file
carefully, not a reason to skip it.**

Obeying costs coverage. Overriding costs the user's own access when an IP is
blocked, and costs the project its standing the first time someone reads the
code. **Default: obey.** What follows is the only route out.

## The four questions

Answer all four **in the board's own file**, in writing, before any code. One
"no" and the answer is: do not build it.

**1. Is the refusal aimed at us?** Read which class the file is talking about —
the answer stopped being binary a long time ago. `leboncoin` allows
`Claude-User` and closes `/recherche`: it permits the fetch and refuses the
sweep, which is precisely us. `softy` bans every AI agent outright.
`tecnoempleo` names six Anthropic agents. **AMS names nobody** — it names
`LinkedInBot` to *allow* it, and closes the rest by omission.

**2. Is there a sanctioned door?** An API, a feed, a sitemap, an open-data set.
If one exists the debate is moot, and this has happened more often than not:
France Travail, ITJobs, Reed and Adzuna all publish one. **Establish its
absence, and record how you established it** — a 404 on a guessed API path is
not evidence.

**3. Is the refusal even-handed?** A site that closes the door to everyone has
made a policy, and it is entitled to it. **A public body that opens the door to
one commercial party and closes it to all others has not made a policy — it has
picked a winner.** Those are different acts, and only the second is a reason to
weigh an override at all. Note what this excludes: being big, being useful, or
being inconvenient to us are not reasons.

**4. Would the override be visible?** `shared/never-fail-silently.md` outranks
this file. An override the user cannot see in the run's own output is not
allowed, however good the argument for it.

## The five cases, decided by the same rule

| Board | Aimed at us? | Sanctioned door? | Even-handed? | Verdict |
| :-- | :-- | :-- | :-- | :-- |
| **Softy** | Yes — every AI agent, Anthropic twice | No | Yes — same rule for all | **Obey.** Browser adapter, by choice not constraint |
| **Tecnoempleo** | Yes — six Anthropic agents named | No | Yes | **Obey.** No adapter, and there will not be one. Its ads still reach us through Empléate — see *When a refused board's ads reach us through an open one* |
| **InfoJobs (ES)** | Yes — `ClaudeBot`, `Claude-SearchBot` **and `Claude-User`** | Yes — `developer.infojobs.net`, key required | Yes — every AI vendor, same treatment | **Obey.** The API is the only route |
| **Leboncoin** | Yes — the sweep, not the fetch | No | Yes | **Obey.** Ad-by-ad via `cover-letter <URL>` already works |
| **AMS (AT)** | By omission | **None found** — see below | **No** — `LinkedInBot` allowed, all others refused | **Override, opt-in only** |

## AMS — the reasoning, in full

`jobs.ams.at/robots.txt`, read 2026-08-31, is four rules:

```
user-agent: LinkedInBot
Allow: /public/emps/
Disallow:

user-agent: *
Allow: /public/emps/$
Disallow: /public/emps/
```

`LinkedInBot` gets the employer pages entire. Everyone else gets the index page
at that exact path — the `$` anchor — and nothing beneath it.

**Question 3 is why this one is decided differently.** The AMS is Austria's
federal public employment service, funded publicly and charged with placing
people in work. It has granted machine access to one privately held American
platform and refused it to every other actor — free, paid, closed or
open-source alike. That is not an operator protecting its infrastructure; it is
a public body allocating access to a public register.

**Question 2 was checked and came back empty**, and the check is the weak part
of this file: the `data.gv.at` CKAN endpoints tried returned `404` and `301`,
and the eJob-Room is an Angular application whose backend is inside a bundled
`main.js`. **No open-data route was found; none was proven absent.** If someone
finds one, it supersedes this section and the override goes away.

**What the argument does not extend to.** It is about *this* asymmetry, at a
*public* body. It says nothing about StepStone, willhaben or Monster, which
refuse everyone evenly and are entitled to. It does not travel by analogy to a
private board that happens to be large.

## If the answer is override: how

**Never a default.** The board's config takes an explicit key, absent means
off, and no setup flow turns it on for the user:

```yaml
boards:
  ams:
    enabled: true
    override_robots: true   # required; absent or false → the board is skipped
```

**Skipped, not silently obeyed.** `enabled: true` without `override_robots`
must report the skip and say why, per `never-fail-silently.md`.

**The user is told before they are asked.** `shared/setup.md` **section 5d**
raises AMS during onboarding whenever the user's geography reaches Austria: it
quotes the four rules, states the ground the decision rests on, says that the
address that gets blocked is *theirs*, and says that this is the only override
in the plugin. It offers three answers — enable, leave off, decide later — with
**no default and nothing pre-ticked**, and a refusal is a hard off that is never
raised again. Until an adapter exists the step configures nothing and says so:
the stance is recorded under `pending_decisions.ams`, outside `boards:`, because
a board switched on with no adapter behind it reads as a bug.

**The run says it out loud**, every time, in the output the user reads:

> `ams: robots.txt override ACTIVE — jobs.ams.at disallows /public/emps/ to all
> agents but LinkedInBot. You enabled this. See shared/robots-policy.md`

**Pace as if you were welcome.** One request at a time, a real delay between
them, no parallelism. An override is not a licence to be expensive.

**Stop on the first block.** A `403`, a captcha or a rate limit is the operator
answering the question directly. Report it and stop — do not rotate, do not
retry with another agent string, do not go to the browser to get around it.
`shared/boards/cadremploi.md` uses a browser because a script is *blocked*;
nothing of the kind applies to a site that has told you no.

## A refusal nobody wrote — the vendor default

Question 1 asks whether the refusal is aimed at us. There is an answer none of
the earlier cases produced: **it is aimed at nobody, because nobody wrote it.**

`datos.gob.mx/robots.txt` and `datos.gob.ar/robots.txt`, fetched 2026-09-02:

```
User-agent: *
Disallow: /dataset/rate/
Disallow: /revision/
Disallow: /dataset/*/history
Disallow: /api/
Crawl-Delay: 10
```

**123 bytes, and byte-identical** — same MD5, `924dd2f6cedd956be8d4888a634876ca`
— on two unrelated national open-data portals. Every path it names is a
**CKAN** route. It is the file the software ships with, and neither
administration has touched it.

**What follows, and what does not.**

- **Obey it anyway.** A rule nobody revisited is still the rule the server
  publishes, and this file's default does not bend for a weak reason. Nothing
  here licenses ignoring it.
- **But do not describe it as a decision.** Writing *"the portal has
  explicitly closed its API"* attributes an intent that the evidence
  contradicts, and that sentence then travels. Say what is true: *the default
  file has not been changed.*
- **It changes the remedy.** A declared refusal is answered by respecting it.
  A default nobody edited is answered by **asking the operator** — an
  open-data portal that has never considered the question may simply say yes.
  That is a route the other cases in this file do not have.

**The tell is provenance, not text.** Finland's `tyomarkkinatori.fi` also
carries `Disallow: /api/`, written by hand into a file with its own structure
and its own other rules. **The same directive, one deliberate and one shipped
in a box.** Nothing in the line distinguishes them; only where the file came
from does. Check whether the whole file is a stock artefact — a known default,
byte-identical elsewhere — before calling any single rule a policy.

*(Measured and reported by claude-job-hunt-8e on the Mexico page, which had
first described it as an explicit closure; re-verified here before being
written down. The correction is the useful half.)*

## When a refused board's ads reach us through an open one

Decided 2026-09-01, on Empléate. It will recur, so it is written down.

`empleate.gob.es` is Spain's public employment service. Its `robots.txt` names
nobody and its search API is open. It is also an **aggregator**: 2 436 of its
28 099 live ads come from **Tecnoempleo**, which the table above rules out
entirely, and the full text of each one is in the record.

**Reading them there is not reading tecnoempleo.com.** `robots.txt` is an
instruction to crawlers about access to *that server*. It is not a licence
term on the content, and it does not follow the content to a third party the
operator chose to supply. Tecnoempleo feeds this register; the register serves
it openly; we read the register. Nothing is circumvented, and the alternative —
treating a syndicated copy as untouchable — would mean discarding ads from a
public body because of a private site's crawler policy.

**The part that does need care is the link.** Those records carry the
partner's own URL, so an adapter that emits it as *the* ad URL sends
`cover-letter <URL>` to fetch a refused host, from the user's own address,
later, with nobody watching. That is the actual violation, and it is one
field away from happening by accident.

**The rule.** When an open board republishes a refused board's ads:

1. **Read them.** The open board is the source of record.
2. **Emit the open board's URL as the ad URL**, always. Never the partner's.
3. **Carry the partner link separately and mark it** — `empleate.md` uses
   `source_url` plus `source_url_do_not_fetch: true` — so nothing downstream
   follows it and the reason is visible in the row.
4. **Make the list of refused hosts inspectable per run.** `empleate.py
   fuentes` prints the flag per feed, so the next partner to appear is seen
   rather than assumed.

**What this does not extend to.** It is about content an operator *published to*
an open third party. It says nothing about a mirror, a scraper's copy, or a
cache — those are not the operator's act. And it never reaches a login, a
paywall, or anything the refused site keeps behind one.

## What this file does not license

Not credentials, not paywalls, not consent walls, not anything a login guards,
and not personal data of any kind. **The AMS override covers public job
advertisements and nothing else.** Candidate profiles, employer contact
records and anything behind the eJob-Room's authentication are out of scope
here and stay out.

And it does not license quiet reinterpretation of the four questions to reach a
convenient answer. **If the reasoning has to be strained, the answer is obey.**
