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

## Before the four questions: did you read a file, and does the door open?

The four questions below assume two things — that you have read a
`robots.txt`, and that you know what the site does. **Both assumptions fail
routinely**, in ways that produce a confident wrong answer rather than an
error. That is why this section comes first: it decides whether the four
questions are being asked about anything real. Do not move it after them.

### A `robots.txt` verdict is not an access verdict

The file states the operator's wish. **It does not describe what the server
does, and it is wrong in both directions.** Two boards on one page, measured
2026-09-02:

| Site | `robots.txt` says | The pages do |
| :-- | :-- | :-- |
| **Glints** | 200, 587 bytes, permissive — nothing blocks a listing crawl | **403 to `curl` on every page**, 1.3 MB of firewall HTML — while a real Chrome loads everything |
| **Kemnaker** | 200, looks open | **825 KB of `text/html`** — an Angular skeleton. There were never any rules |

One permits and refuses; the other refuses nothing because it says nothing.
**Test two clients before concluding, and write the conclusion in the board's
own file** — "permissive file, 403 to a plain client, fine in a browser" is a
finding; "robots.txt is open" is not.

**And the two verdicts are fully independent, which one site settles on its
own.** `nea.gov.kh` **blocks access while expressing no intention at all**: its
file is the managed template, identical on three continents, so nobody there
decided anything — and the pages are shut regardless. **Access without
intention, and it is the fourth corner of the table.**

The day's count, so the asymmetry is a number and not an impression:

| | |
| :-- | --: |
| `403` to a plain client, **fine in a real browser** | **nine sites** |
| refused at *both* layers — the operator means it | **two** |
| a `200` with **no `robots.txt` at all** behind it | one, serving its home page on every path |
| a **`202` with an empty body** | one |

**Nine against two is why "curl got a 403" is never the finish.**

### Test the apex and the `www` separately — it bites in both directions

`www.findajob.dwp.gov.uk` leaves for a domain that `403`s while the apex
answers 200; and the mirror image, `jobs.co.id/robots.txt` is a clean 30-byte
rules file while `www.jobs.co.id/robots.txt` redirects and serves 171 888 bytes
of HTML. **One host is not the other host**, and `104.com.tw` serves two
different md5s across the pair.

**Three rebrands surfaced in one afternoon by reporting the answering host**,
2026-09-03: `my.indeed.com` → `secure.indeed.com`, `jobs.recruitee.com` →
**`careers.tellent.com`** (Recruitee is Tellent), and `talent-soft.com` →
**`www.cegid.com`** (Talentsoft is Cegid), whose 268 KB of HTML makes the file
`unreadable`. **A board that has been bought reaches us as a redirect long
before it reaches us as a rename**, and only the answering host shows it.

**And the host you name is not always the host that answers.** `_robots.py`
now reports both, and the first thing it corrected was one of this file's own
examples: the **126 KB of sign-in HTML** cited here as `my.indeed.com`'s reply
is served by **`secure.indeed.com`**, after a cross-host redirect. The guard
was right and the attribution was not — and nothing could show that while the
result carried only the name that had been typed. Issue #99.

**How often do the two forms really differ? Measured, because the answer
decides whether it is worth two requests a host.** Across **55 comparable
hosts** already known here, 2026-09-03:

| | |
| :-- | --: |
| raw md5 difference | **5 of 55** |
| **two real rules files that differ** | **2 of 55** |

**Three of the five were not two rules files at all** — `job-room.ch`'s apex
redirects to its home page, `job.id`'s `www` answers 59 KB of HTML, and
`digitalrecruiters.com` sends both forms to `www.cegid.com`. **Comparing bytes
without asking whether a rules file came back inflated the finding by more than
double**, which is this page's own `text/plain` guard skipped by the
measurement that was checking it.

**And the residue is not harmless.** `jobindex.dk` serves **47 bytes of
`User-agent: * / Disallow: /`** on the apex and **4 218 bytes of detailed
permissions** on the `www`. An adapter written against the `www` never sees the
refusal, and `_robots.py --siblings` says so in one line.

**So: a diagnostic run once when a board is written, not two requests on every
sweep.** Four per cent does not justify doubling every run; one blanket refusal
hidden behind a `www` justifies looking once.

**And a third host is not a variant of the first two.** `ss.ge` redirects to
`home.ss.ge`, whose jobs section redirects again to `jobs.ss.ge` — **three
hosts, three `robots.txt` files, three different sets of refusals**, measured
2026-09-03:

| Host | Size | Refuses |
| :-- | --: | :-- |
| `ss.ge` | 478 B | `/en/jobs`, `/ru/jobs`, and eight `/user/…` paths |
| `home.ss.ge` | 105 B | three `/…/user` paths — **and none of the job refusals** |
| `jobs.ss.ge` | 62 B | nothing: `Allow: /` |

**The host every request is redirected to has the more permissive file**, and
the one that governs the board says `Allow: /` while the board itself answers
`403` behind a challenge. **Which file applies depends on where the redirect
chain leaves you**, so read the file for the host you will actually fetch —
not for the name you typed. `shared/boards/ss-ge.md`.

*(Its apex file also opens with `sitemap: Disallow: /sitemap.xml` behind a BOM
— a `Sitemap:` directive whose value is a `Disallow:`. Read as either it is
nothing, which is one more reason to fetch the path rather than parse the
line.)*

**And the third mechanism in the pair is TLS, which fails before any status
code exists.** `trabajo.gob.ec` resolves and answers nothing a client will
accept — `curl: (60) SSL: no alternative certificate subject name matches
target host name` — while **`www.trabajo.gob.ec` serves the file normally**,
`200`, 176 bytes. Verified 2026-09-03.

**Which of the two names works is not predictable**, and that is the whole
point: `philjobnet.gov.ph` is this case running the other way — there the
**apex** is the service and `www` presents Azure's default certificate. Two
labour ministries, opposite answers, and a probe that tries one name and stops
writes off a live national service either way. **Try both, and record which one
you used**, because a certificate that does not cover the name is an outage of
identity, not a policy — see *A non-answer is not a refusal* below.

### A non-answer is not a refusal

**"Did not respond" and "refused" are different facts and only one of them is a
door.** Measured in one country: a board that timed out three times, one whose
TLS fails on the name, and one returning `530` from a dead origin. **None of
those is closed** — nobody refused anything; the request never arrived at
something able to answer.

A refusal is a **`403` with a body that came from the site**. A timeout, a TLS
name mismatch and an origin error are the network failing to deliver a
question, and recording them as refusals turns an outage into a policy.

**And the reverse of the same rule**: `shared/robots-policy.md` already refuses
to read an absent file as a refusal. This is that rule applied one layer down —
**absence of an answer is not an answer.**

### A `robots.txt` that is not `text/plain` is not a `robots.txt`

**And an absent header is not a declaration of HTML.** The guard was written as
*"not `text/plain`"* against a default of `""`, so a server that declares
nothing had its file rejected without being looked at: `hukoomi.gov.qa` serves
a valid **468-byte** `robots.txt` with **no `Content-Type` at all**, and the
plugin called it unreadable. **An absence of metadata is not negative
metadata** — the same asymmetry as *an absent `robots.txt` is not a refusal*,
one level further down. When the type is missing, **the first line decides and
the size corroborates**: a rules file opens on a directive and runs to a few
hundred bytes; the impostors open on `<` and run to 126 015. Issue #96.

One check, and it catches three separate traps already in this repository:

| Fetched | Status | `Content-Type` | Bytes | What it really was |
| :-- | --: | :-- | --: | :-- |
| `my.indeed.com/robots.txt` | 200 | `text/html` | **126 015** | Indeed's sign-in page — `my.` is *my profile*, not Malaysia (issue #64) |
| `kemnaker.go.id/robots.txt` | 200 | `text/html` | 825 204 | An Angular SPA skeleton |
| `mycareersfuture.gov.sg/sitemap-5.xml` | 200 | `text/html` | 7 923 | The site's own React shell, named `.xml` |

**The size is the second witness, and the gap is three orders of magnitude.**
Real files: **58 bytes** (`jobth.com`), **59** (Kalibrr), **87**
(MyCareersFuture), **275** (JOBBKK). The impostor: **126 015**. A `robots.txt`
of 126 KB does not exist.

The same test generalises: **a sitemap that is not XML is not a sitemap**, and
an index that declares six sub-files two of which are HTML shells will
overstate a corpus by a factor of three if you multiply instead of counting.

### Decide by layer: a browser can only change what happens above it

When only one client can be tested, or when a second test would tell you
nothing, **locate the failure relative to the browser**:

| A browser can change the result | A browser can change nothing |
| :-- | :-- |
| HTTP 403, client filtering, TLS fingerprinting | DNS record absent |
| A CDN interstitial | TCP silent on 443 **and** 80 |
| A stub carrying a JavaScript redirect | An honest 404 |
| A login wall on the paths you need | The host answering as a different service |

Two symmetrical mistakes follow, and both have been made here: **spending a
browser on a failure that sits below it**, and **concluding "closed" from a
single client that sits above it**.

**TLS is a third category, and it is the one that produced wrong verdicts.**
An expired or mismatched certificate stops every client that checks — a
browser included — so it looks like the right-hand column. It is not: **the
service underneath is often perfectly alive, and only its proof of identity
has lapsed.** Three boards were written off as unreachable on that basis and
all three were live: `careerbuilder.vn` answers and redirects to CareerViet,
`jobs.id` to Karir.com, `bestjobs.ph` to BestJobs Network. **A plain HTTP
request separates "expired identity" from "vanished service"** — make it
before writing the board off.

**What the rule costs when it is missing.** `doe.go.th`, Thailand's Department
of Employment, probed with `curl`: **200, 1 674 bytes, no title, no text** —
read as *"there is no service here"*, and a country's public employment service
written off. The body is a **stub carrying a JavaScript redirect**, which is
exactly what a plain client cannot follow. **Nobody caught it because the
number was small and an empty body reads like an absent service.**

And the rule pays in the other direction too: of four unreachable public
services in one survey, **three failed below the layer** — silent TCP, absent
DNS — so an instruction to *"re-test everything in a browser"* would have
wasted three probes out of four. **Exactly one failed above it, and that one
was the wrong verdict.**

### A site permission is never a manual task

**"Authorise these three domains in the browser extension" was handed to a user
as a blocking task. The permission was never missing** — the extension had been
set to all sites throughout. The cost was three entries published with no
verdict, and one blocking task that did not exist.

**If a browser probe fails, the cause is something else, and that cause is what
to name.** Never *"the user must grant access"*.

### A passive interstitial is re-read; a challenge that asks for a click is a stop

`grabjobs.co` answered `403` even on `robots.txt`, **and cleared by itself
within seconds** between two reads, with no interaction. **That is a wait, not
a wall** — re-read before concluding.

**A challenge that requires a click is the opposite**, and it is not something
to work around: it is the answer, and it is recorded as such.

> **Assuming an obstacle is a way of not looking.**

### The failure with no status code, which is on no axis at all

`HTTP/2 stream not closed cleanly: INTERNAL_ERROR` on a cold request; a read
timeout after a burst. Measured on the StepStone platform, both shapes, on
hosts that answer 200 to the very next request.

This is **not a response to interpret** — it is the absence of one, so it sits
neither above nor below the browser. What makes it worth naming is its
consequence: **it is the only category where a client that retries loops for
ever**, because there is no status to read and nothing to decide on. Its
remedy is the transport and the pace — HTTP/1.1, a warmed host, one slow retry
and then a declared truncation — not another client.

### Proving a family: the md5 answers one question, the diff answers another

Multi-country boards are usually one platform wearing national domains, and
`robots.txt` is the cheapest test of that. **But the test has two forms, and
using the wrong one gives the wrong answer.**

> **The md5 answers "is this the same file". The diff answers "is this the
> same platform". When the file contains the hostname — and every `Sitemap:`
> line does — the md5 always diverges and tells you nothing.**

Both cases, measured 2026-09-02:

- **Computrabajo declares no sitemap**, so the md5 is decisive:
  `cfcbd02061ac…`, 874 bytes, **byte-identical across eighteen Latin American
  domains with no exception**. One hash, one answer, eighteen countries.
- **The Jobint group — Bumeran, Konzerta, Laborum — gives five different
  md5s and five different sizes**, which refutes the hypothesis at first
  glance. Compare the bodies **without the `Sitemap:` lines** and four of the
  five brands are identical to the bit, with `bumeran.com.pe` diverging by
  **exactly one line**: a template, one exception, one country — the SEEK
  shape.

**And the strongest evidence there was not in any hash.** Laborum and Konzerta
declare sitemaps named **`sitemap_avisos_bum.xml`** — the `_bum` of Bumeran
surviving under the other brands' names. A filename outlived the rebrand, and
no checksum would have found it.

So: **hash when the file carries nothing host-specific, diff when it does, and
read the filenames either way.**

**And before any of that, establish that what you hashed is the file.** Re-run
on 2026-09-03, this time with a bare `curl`:

```
ec.computrabajo.com   403   118 bytes   bad2e8579dcdb79399aac2064216a37d
co.computrabajo.com   403   118 bytes   bad2e8579dcdb79399aac2064216a37d
pe.computrabajo.com   403   118 bytes   bad2e8579dcdb79399aac2064216a37d
```

**Three hosts, one hash, and the right conclusion for the wrong reason.** Those
118 bytes are a refusal page; the file is 874 bytes and appears only for a
request carrying an ordinary `User-Agent` and `Accept-Language` — at which
point all four hosts, `.com.mx` included, return `cfcbd02061ac…` as recorded
above. **A hash comparison agrees perfectly when nothing answered**, which is
`shared/plausible-and-false.md`'s *blind agreement* in its cheapest form: the
check shares its object's failure mode, because the failure is identical
everywhere. **Assert the family on responses you have confirmed are the file —
status `200`, `text/plain`, and a size that is not the size of an error
page.**

### Five words for the verdict, used identically in every board file

| Word | Means |
| :-- | :-- |
| **open** | The door answers, the file permits, the content is there |
| **refused** | The operator says no, in `robots.txt` or in the terms |
| **inaccessible** | The infrastructure stops you: DNS, TCP, a WAF, a login wall |
| **not sanctioned** | It answers and nothing forbids it, but nobody built it as an interface — `shared/boards/README.md` on Norway |
| **substituted** | **A complete HTTP 200 answering a question nobody asked** |

The last one is new and it earns its place. Kalibrr returns 818 unrelated ads
for a country it does not serve and for a nonsense keyword, flagging it in one
boolean; StepStone pads a thin result with `semantic` and `regional` ads that
are indistinguishable in the markup. Neither is *open*, neither is *refused*,
and calling either an error loses what actually happened.

## How a file splits into groups — and why `grep` gives a wrong, convincing answer

**The four questions below are answered "in the board's own file". This is how
to read that file**, because the splitting is not what it looks like.

`secretcv.com`, in full order: `User-agent: *` / `Allow: /`, then the same for
`GPTBot`, then the same for `OAI-SearchBot`, **then nineteen `Disallow:` lines
after a blank line.**

Read by eye, the site is closed to everyone. **Read by the standard, a blank
line does not end a group** — so those nineteen lines belong to the last
declared agent. Resolved with `urllib.robotparser` rather than asserted:

| agent | `/is-ilanlari/ara` |
| :-- | :-- |
| `OAI-SearchBot` | **refused** |
| `*`, `GPTBot`, `ClaudeBot` | allowed |

**The only agent that file restricts is OpenAI's**, which is almost certainly an
authoring accident.

**Here the eyeball reading errs on the cautious side.** Inverted — an `Allow: /`
written under one named agent and read as global — **it produces a false
permission**, and that is the direction that costs this project its standing.

### The three rules

1. **Group boundaries are `User-agent` lines, not blank lines.** A rule after a
   blank line still belongs to the group above it.
2. **Consecutive `User-agent` lines share one rule set.**
3. **Resolve with a parser, then quote the result.** `urllib.robotparser` is in
   the standard library and takes three lines. **`grep` on `Disallow` is wrong
   and convincing on any file with more than one group** — and multi-group
   files are the norm: 65 groups on `tr.indeed.com`, 20 on `hh.ru`, 17 on
   `youthall.com`.

### Repeated groups for the same agent are merged, not discarded

`yes123.com.tw` serves **eight consecutive `User-agent: *` groups**, one
directive each; `jobscentral.sg` served nine. **The tempting reading is that a
conforming client obeys the first and the other seven apply to nobody. That is
wrong**, and it is wrong in the permissive direction.

Measured with the standard-library parser on eight groups of one `Disallow`
each — and this is what RFC 9309 prescribes, records bearing the same product
token being combined:

```
/p1 refused   /p4 refused   /p8 refused   /elsewhere allowed
```

**All eight bind.** A reader who applied the first group only would have
concluded that seven paths were open.

### And a group with no directive forbids nothing

`cake.me` serves `User-agent: *` **with nothing under it**. Verified: every
path is allowed. **An orphan group is not a refusal** — nothing is written, so
nothing is forbidden, and *"it has a `User-agent: *`"* is not a finding.

*(All three verdicts on this page were computed with `urllib.robotparser`, not
read off the file — which is rule 3 applied to this page itself.)*

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

### The second instance, and it is much larger: Cloudflare Managed Content

Measured 2026-09-02 on two unrelated Singaporean boards, `nodeflair.com`
(tech) and `fastjobs.sg` (non-graduate). Both serve **the same preamble, word
for word**, fenced by:

```
# BEGIN Cloudflare Managed content
…
# END Cloudflare Managed Content
```

Inside: `Content-Signal: search=yes, ai-train=no, use=reference` for
`User-agent: *` followed by `Allow: /`; a citation of **Article 4 of EU
Directive 2019/790** as an express reservation of rights; and then **ten named
agents each given `Disallow: /`** — `Amazonbot`, `Applebot-Extended`,
`Bytespider`, `CCBot`, **`ClaudeBot`**, `CloudflareBrowserRenderingCrawler`,
`Google-Extended` and the rest.

**Question 3 is where this gets interesting, and the earlier phrasing of it
was not sharp enough.** This block *is* even-handed: ten AI vendors, one rule,
no favourite. What it is not is **decided**. The operator of a Singaporean job
board did not weigh Anthropic against Google; a checkbox in a CDN dashboard
did, and the same bytes appear on sites with nothing else in common.

**"Even-handed" and "decided" are two different tests, and a vendor default
passes the first without passing the second.** That distinction belongs in
question 1 as much as question 3: the refusal is aimed at a category, by
somebody who is not the operator.

**The conclusion is unchanged: obey.** No override is proposed here and none
follows from this. What changes is only what we may write down about it —
*"this operator refuses AI agents"* is not supported by the evidence, and
*"this operator has a CDN default that refuses AI agents"* is. As with the
CKAN case, the remedy that opens is **asking**, and the sentence that travels
should be the true one.

### Where it has been seen: eleven sites, eight countries

**Measured by the country surveys on 2026-09-02** (recorded here from those
surveys, not re-measured in this file):

| Country | Sites |
| :-- | :-- |
| Singapore | `nodeflair.com`, `fastjobs.sg` |
| Philippines | `jobslin` |
| Vietnam | `topdev.vn`, `mywork.com.vn` |
| Chile | `getonbrd.com` |
| Kenya | `publicservice.go.ke` — **the first public-sector site to carry it** |
| Egypt | `wuzzuf.net`, `forasna.com` |
| Ghana | `ghanajob.com` |
| Tanzania | `mabumbe.com` |

**The scope is a number, not an impression**, which is what the issue asked
for. Expect it anywhere a board sits behind Cloudflare.

### Three forms, and they do not say the same thing about intent

**1. The block alone.** Fingerprint `c6370d4bc025`, no other rule in the file:
**the operator wrote nothing.** Four sites, three continents.

**2. The block beside the operator's own rules.** Somebody wrote a file, and
the block was added to it. The operator's own lines are their decision; the
fenced ones are not, and the two must not be read as one policy.

**3. The block twice.** `wuzzuf.net` carries the **entire preamble twice** and
names `ClaudeBot` in both. The effect is nil — and it is the proof that the
block is injected without checking whether it is already there. **A rule
written twice by accident is not a rule written twice as firmly.**

### The counter-examples matter as much, and there are as many

**Publishers who do decide mostly decide on cost, not on doctrine.**
`theugandanjobline.com` leaves its engineering log in the file: *"Bingbot made
122 500 requests in three days, 24% of all traffic, four times Googlebot, for a
small fraction of the visits Google sends"* — and **`ClaudeBot` is filed beside
MJ12bot and a competing aggregator: as a cost, not as a threat.** `tazabek.kg`
names **29 agents** under *"AI robots and SEO analysers: total ban"*, with
Claude next to SemrushBot and AhrefsBot. And `bayt.com` blocks `LinkedInBot`
and `IndeedBot` while naming no AI agent at all — **that is competitor
blocking, and it has nothing to do with this argument.**

**A refusal written by hand, at scale.** The HeadHunter family — `hh.ru`,
`hh.kz`, `hh.uz`, `hh.by`, and `zarplata.ru` — names **eight AI agents each**,
barred from the advert pages only, **while `*` keeps explicit access there**,
replicated byte for byte across four countries. Nobody's CDN did that.

**And permissions, written on purpose.** JobKorea allows `ClaudeBot` on its
advert pages by an explicit path whitelist. Trade Me gives it **four groups**
and withholds only commerce. Magneto365 names `ClaudeBot` and `anthropic-ai`
and publishes an `llms.txt`. `qatarliving.com` writes **seven `Allow: /` lines
where `*` already permitted everything** — a redundant permission nobody was
obliged to write. And Tech in Asia (Singapore) and CareerViet (Vietnam) make
six.

**The honest count: eleven restrictive sites against six welcoming ones**, and
the far end of the range is `pe.jobomas.com` — **the only site in the corpus to
block `Claude-User`**, the human-driven agent.

**Both counts come from the same day's surveys and neither is a state of the
web.** Eleven is where the block was *seen*, not where it *is*; six is where a
permission was *written down*, not where we are welcome.

### `ClaudeBot` refused and `Claude-User` unnamed is not a permission

The block names `ClaudeBot` and says nothing about `Claude-User`. **The
omission is not an invitation.** Whoever wrote that list enumerated training
and crawling agents; that a person-driven fetcher was not on their list says
what was in front of them, not what they would have decided.

**And the field shows the distinction is available to publishers who want it**:
Indeed adds `Claude-User` to its widest group deliberately, and `pe.jobomas.com`
bars it outright. **A publisher who means to refuse the user-driven agent can
name it, and one of them did.**

So the rule here is the one `shared/reading-terms.md` already carries and
`softy.md` already practised: **being a user-driven tool is a reason to read an
ambiguous clause fairly, never a reason to argue past a publisher who named
us.** Where the block appears, we obey it.

### What this section settles, and what it deliberately does not

- **The block is recognised on sight** rather than read as a bespoke policy.
- **A CDN default is weaker evidence of intent than an operator's own line —
  and exactly as binding.** What changes is the sentence we may write about a
  publisher, never what we do with their file.
- **No override follows from any of it.** Nothing here is a reason to fetch
  anything, and it must not be cited as one.

**And the material does not support a conclusion in our favour.** It supports a
finer question than the one that was asked: *some* refusals are nobody's
decision, *some* are considered and about bandwidth rather than about AI, and
*some publishers say yes in writing when they did not have to.* Anyone tempted
to read this section as leverage should read the Ugandan file's traffic log
first.

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

## Being named has five values, not two

**"Named" is not "blocked", and "allowed" without saying where is as misleading
as "named" without saying which way.** Measured across the country surveys and
verified directly on 2026-09-02:

| Value | What it looks like | Example |
| :-- | :-- | :-- |
| **1. not named** | no group applies; `*` decides | the common case — **and silence settles nothing, in either direction** |
| **2. refused** | `Disallow: /` on our agents | `linkedin.com`, below |
| **3. allowed** | a bare `Allow: /` | `ethiojobs.net`, `ikman.lk` |
| **4. allowed, but restricted** | `Allow: /` for one agent, a narrow permission for another | Indeed: a bare `Allow: /` for `Claude-User` and `Claude-SearchBot`, **pagination only and 145 closed paths for `ClaudeBot`** |
| **5. refused exactly where it counts** | open everywhere except the ads | `hh.ru`: **`Disallow: /vacancy/*`**, and the rest of the site open |

**Value 5 is the one a permissive summary hides**, and value 4 is the one a
restrictive summary hides. A survey that records "named" without recording
which of the five produces a fact nobody can use.

### `linkedin.com` refuses us by hand, including the user-driven agent

**Verified directly, 2026-09-02** — 120 190 bytes, `text/plain`, hand-written
and not a managed block:

```
ClaudeBot        Disallow: /
Claude-Web       Disallow: /
Claude-User      Disallow: /
anthropic-ai     Disallow: /
Claude-SearchBot Disallow: /public-profile/ , /people/search/   ← value 4, not 2
```

**This matters more than any other entry in the file, for two reasons.**

**It settles the question the repository keeps circling.** Indeed separates the
two categories in order to *open* to the human-driven agent; **LinkedIn closes
them alike.** The distinction exists, two major operators have decided it in
**opposite directions**, and therefore **it is a choice and not an emerging
standard.** Nothing here may rest on the idea that an agent acting for a person
is generally accepted — `shared/reading-terms.md` already refuses to argue past
a publisher who named us, and this is the publisher who named us most
explicitly.

**And LinkedIn is cited as a source across nearly every country in the
survey.** A reader who finds this file after us would be right to ask why it
was not written here.

**What the adapter does is a different act, and the file must say so rather
than assume it.** `linkedin.md` drives **the user's own Chrome, in the user's
own session** — that is the person browsing their own account, not one of our
agents fetching. **LinkedIn's file is precisely the document that declines to
draw that distinction**, so this repository states it explicitly instead of
presupposing it, and states equally that **no automated fetch of LinkedIn by
our agents is permitted by that file.**

### A permission that permits nobody

`reed.co.uk` carries, commented and deliberate:

```
# Anthropic (Claude)
User-agent: AnthropicBot
Allow: /
```

**No other site in the survey uses that name.** The five that recur are
`ClaudeBot`, `Claude-User`, `Claude-SearchBot`, `Claude-Web` and
`anthropic-ai`, so a conforming client not carrying it falls back to `*`.

**It is the exact mirror of the anti-scanner file below**: one is a permission
that permits nobody, the other a refusal that refuses almost nobody. **Both
express a real intention and produce no effect, and in both cases a quick
reading gives the opposite of the effect.**

*(The reservation, kept as stated: this does not establish that `AnthropicBot`
does not exist. What is observed is that none of the other twenty-two sites in
the survey uses it — an observation about the corpus, not about our agents.)*

## Two families, and one conclusion: what counts is what you counted

Everything below this line was measured on 2026-09-02, across the country
surveys. **They divide into two families and they meet at one sentence.**

### A. What answers is not a rules file — and no status code says so

Five ways a request for `/robots.txt` returns something that is not one:

| Shape | Where | What it looks like |
| :-- | :-- | :-- |
| **A `403` the browser denies** | eight sites in one day, incl. `104.com.tw` — two md5s for apex and `www`, and its search page loads fine in Chrome | a refusal |
| **A `202` with an empty body** | `tanqeeb` | an answer |
| **An application shell** | a Jordanian LMIS (Next.js), `kemnaker.go.id` (Angular, **825 kB**) | a large permissive file |
| **The home page, on any path** | `topjobs.lk` — **1 133 363 bytes** of the site's own front page, *and an invented URL returns the same* | **a very rich rules file** |
| **A `404`** | two Georgian government portals serving 116 kB and 174 kB of plain HTML elsewhere | a block |

**A `404` on `/robots.txt` is not a refusal — it is the absence of a file**, and
reading it the other way costs a country.

**`topjobs.lk` is the sharpest of the five because it defeats both instincts at
once**: a prober that checks the status sees `200`, and a prober that checks
the *size* sees a megabyte and concludes the file is unusually thorough.

### B. What is declared is not what is there

**A `Sitemap:` that answers is not a `Sitemap:` that contains.** `jordanjobs.net`
declares **twelve**; three were pulled and each returned `200`, `text/xml`,
**413 bytes, zero `<loc>`** — a well-formed `<urlset>` with four namespaces and
an XSL stylesheet, and nothing in it. Then an invented name at the same host
returned **the same 413 bytes, same md5**. **It passes the status check, the
MIME check, the XML validation and the existence check.** Only counting the
`<loc>` elements catches it, and the site is alive — 96 kB of real pages.

**And an identical declaration can mean opposite things.** Two families
publish a sitemap URL carrying an entity id, in files of rigorously equal size
differing by one identifier:

- `hr.ge` / `cv.ge` / `career.ge` — pulled and compared: **39 287 URLs
  strictly identical**, 1 112 ads in common at 100%, files of 5 383 203 bytes.
  **Three brands, one corpus.**

  **Two brands, and a third that was reading someone else's file.** Re-measured
  2026-09-03 through the tenant numbers those sitemaps are served under:
  `hr.ge` is tenant 1 and `cv.ge` tenant 2, both **1 062 advertisements** —
  genuinely one corpus. **`career.ge` is tenant 3 and has none at all**, and it
  appeared here because **its own `robots.txt` declares `tenant/1`**, which is
  hr.ge's sitemap. The comparison was of files, and the files agreed because
  two of the three brands pointed at the same one.

  **And the file was never the ad count**: of those 39 247 `<loc>`, **36 593
  are `/customer/` employer pages** and 1 505 are search landing pages. The
  platform has six tenants, three of which publish ads —
  `shared/boards/hr-ge.md` has the table.
- `ar` / `pe` / `mx.jobomas.com` — `robots.txt` of 2 074 bytes each, one line
  of `diff`, the 172nd: their own sitemap's domain. Pulled: **2 003, 2 796 and
  5 067 `<loc>`**, 45 paths in common — the structural pages. **Three
  countries, three corpora.**

**A rule drawn from either refutes the other.** Together they permit exactly
one sentence, and it is the same one as Taleez's 296-of-14 221:

> **The declaration says nothing. Pull the files and count the URLs.**

**And the counter-example belongs here too, or the rule reads as cynicism.**
`www.trabajo.gob.ec` declares `sitemap_index.xml` from inside its Yoast block,
and it is **real**: `200`, `text/xml`, 1 585 bytes, **seven sub-sitemaps**.
Verified 2026-09-03. Against the three ghosts already catalogued — `mol.gov.om`
in `404`, `jordanjobs.net` valid and empty, `lmis.mol.gov.jo` an application
shell — that is **three ways of lying and one of telling the truth**. The rule
was never "sitemaps are worthless"; it is **"you do not know until you count"**,
and a corpus with no true case cannot say that honestly.

**Then the second half, which the count alone does not give you: real is not
relevant.** The seven files are `post`, `page`, `ads_banner`, `ps_promotion`,
`category`, `ads_banner_cat`, `author` — **a WordPress content sitemap, and not
one of them is vacancies.** Counting `<loc>` here returns a confident number
about a ministry's news articles. **A count answers "is anything there"; only
the filenames answer "is it the thing you came for"** — the same arithmetic
that would have reported Vieclam24h five times over by counting its occupation
and province families as ads.

**A fourth brand for the `_bum` filename evidence**, measured the same day:
`multitrabajos.com` (Ecuador) declares five sitemaps and **all five end in
`_bum`** — `sitemap_avisos_bum.xml`, `sitemap_core_bum.xml`,
`sitemap_empresas_bum.xml`, `sitemap_listados_ubicacion_bum.xml`,
`sitemap_tags_bum.xml`. The Bumeran marker survives under a brand whose name
shares nothing with it, exactly as it did under Laborum and Konzerta. **And the
files are real**: `avisos` is 1 158 822 bytes and carries **5 771 `<loc>`**.

**The pair on one market is the instructive part.** On Ecuador,
`multitrabajos` betrays its group in its own filenames and `computrabajo`
declares **no `Sitemap:` at all** — same country, same trade, and only one of
them can be settled this way. **A method that decided `hr.ge` and Jobomas has a
domain of validity, and this is its edge.** A non-result that bounds a method
is worth more than a third example confirming it.

### Files nobody wrote, and the asymmetry that identifies them

The managed-block section above assumes a CDN. **Four more routes produce a
rules file that no operator wrote:**

- **The CMS default.** `mlvt.gov.kh`, a labour ministry, serves the
  `robots.txt` shipped with Joomla — installation comments included, still
  explaining how to move it if the CMS sits in a subfolder, still linking
  `robotstxt.org`. **Not one line is about the site.**
- **The online generator.** `camhr.com`, 154 bytes stamped
  `# robots.txt generated at …`, carrying an empty `Disallow:` followed by two
  real ones.
- **The framework module.** `hahu.jobs` — **114 bytes** fenced by
  `# START nuxt-robots (indexable)` and `# END nuxt-robots`, an empty
  `Disallow:`, and a `Sitemap:` the module derived from the site's own base
  URL. Verified 2026-09-03 — **and only over a redirect**: the apex answers
  `301`, and a fetch without `-L` returns 178 bytes of nginx HTML, which is a
  `robots.txt` in neither content nor type.
- **The CMS plugin.** `www.trabajo.gob.ec`, the Ecuadorian labour ministry —
  **176 bytes** fenced by `# START YOAST BLOCK` and `# END YOAST BLOCK`, an
  empty `Disallow:`, one `Sitemap:` that is real (below). Verified 2026-09-03.

**The five look nothing alike, and that is the finding.** One is the same
Cloudflare block byte-for-byte across eleven sites in eight countries; another
is 176 bytes that shout their origin in comments at both ends. **The plugin
route is the most verbose of the five**, which inverts the intuition that a
default is terse: a generator that signs its work leaves *more* text than an
administrator would have written, not less. A reader looking for "short and
generic" finds three of the five and misses two.

**What they share is not infrastructure, not size and not tone — it is that a
rules file exists without anybody having wanted one.** That is visible only
with the five side by side, which is why the list is kept and not just the
rule.

**Identify them by content, never by fingerprint, and the asymmetry is the
point.** An identical md5 against a known default establishes it; **a different
md5 establishes nothing**, because one line added by an administrator changes
the hash without changing the nature of the file. **An equality concludes, an
inequality only opens a check** — the same shape as *absent is not a refusal*
in `_robots.py`.

*(Fingerprint comparison failed in both directions on one day: two identical
files that looked different because of a `Sitemap:` line, and a shared managed
block that made two unrelated governments look like one decision.)*

### Three files that mean the opposite of how they read

**A tiny `Disallow: /` is not always a content policy.**
`job.taiwanjobs.gov.tw` — the Taiwanese public employment service — is **34
bytes**:

```
User-Agent: ZoomEye
Disallow: /
```

There is **no `User-agent: *` group at all**, so nothing else has an
applicable group and everything is permitted. **The named adversary is a
network-asset scanner, not a crawler and not an AI**: this is a security
posture, not a content policy, and **it is the only file in the corpus that
misleads in the permissive→restrictive direction** while the others mislead the
other way.

**A welcoming file can close the one function that matters.**
`labourdept.gov.lk` is fully commented in English, in four numbered sections,
with a bandwidth-cost vocabulary — *"These bots drain bandwidth but don't bring
you search traffic"* — and **names no AI agent at all**. Section 3 contains
**`Disallow: /*?*`**, which forbids every URL carrying a query string. On a
WordPress site, that is the job search. **Read the patterns, never the tone.**

**And a file can say yes, on purpose, with a business reason and a date.**
`ikman.lk`:

```
#AI Assistant Crawlers - explicitly allowed for AI/GEO visibility (added per Q3 2026 GEO OKR)
```

…followed by **nine agents in `Allow: /`** — ClaudeBot, anthropic-ai, GPTBot,
ChatGPT-User, PerplexityBot, Perplexity-User, Google-Extended, OAI-SearchBot,
meta-externalfetcher — **and `meta-externalagent` in `Disallow: /` right
after**. Somebody separated two robots from the same publisher and decided
differently for each; that is not a copy-paste.

**Read it as what it is: the site describing itself in its own file.** What is
verifiable is that its structure matches what it announces.

**And it settles a question the file left open.** `akhtaboot.com` names nine
agents to close them all; `ikman.lk` names nine to open them all — **same day,
same corpus.** Two deliberate and opposite postures, **and neither is its
market's default**: three Jordanian boards out of four have no AI policy at
all. **A reference board does not represent its market on this question. Two
boards suffice to check that; none suffices to assume it.**

### An `llms.txt` says nothing about what is in it

Both bounds are in the same corpus, on the same day: one is **7 637 bytes of
real documentation** — category tree, URL template, district list, a note that
the site renders server-side — and another is **a GoDaddy sales pitch**. **The
directive is not evidence of content.** Open it or say you did not.

### And the identity check has two holes

Reading a page's `<title>` to confirm a domain is what it claims — a rule born
from mistaking a personal portfolio for a job board — **fails twice**:

- **A client-rendered application sets its title in the browser.**
  `buscojobs.com.ar` has **no `<title>` at all** for a plain fetch and is a
  perfectly real site; its identity is in `og:title`, `<html lang="es-AR">`
  and the meta description.
- **A site behind a WAF returns the challenge's title** — *"Just a moment…"*,
  *"Security Check"*.

**An absent title refutes nothing, and a WAF's title is not the site's.** Read
`og:title`, `og:site_name`, `<html lang>` and the meta description before
concluding. **An empty title is not an empty site.**

### A guessed hostname is a hypothesis, and confirming the concept does not confirm the address

**The failure of #72 has a form that survives the check meant to catch it.**
Ecuador's public employment service was looked for at **`socioempleo.gob.ec`**
— a name assembled from what the programme is called. It has **no DNS record**
(verified 2026-09-03). The obvious next step is to confirm the concept, and the
concept confirms: *Socio Empleo* is real, it is the name of the deployed
application, and it is served — at
**`encuentraempleo.trabajo.gob.ec/socioEmpleo-war/paginas/index.jsf`**, 73 761
bytes, `200`.

**So the search returns evidence that you are looking for the right thing, and
none that you are looking in the right place** — and the natural reading of the
two together is *the right service, at a domain that has died*. It has not; it
never had that name.

| Guess | What answered | Why it misleads |
| :-- | :-- | :-- |
| `hirejordan.com` | A site, and not the one claimed | A name that resolves is not a name that is right |
| `sajil` / `sajjil` | Nothing | A spelling slip — caught by re-reading |
| **`socioempleo.gob.ec`** | **Nothing, while the concept checks out** | **The concept check succeeds and is mistaken for an address check** |

**This one is not caught by re-reading, because there is nothing misspelt.** It
is caught one way only: **read the official site's outbound links**, which is
where `encuentraempleo` was found. A hostname that was never observed is a
hypothesis until a link from an authority carries it — and *"the domain is
dead"* is a claim about the world that needs the same evidence as any other.

## The same file is a source of coordinates, and reading it only for permission leaves them

Everything above is defensive: what may be fetched, what a refusal means, when
a file is not a file. **Three findings on 2026-09-02 point the other way.**
Issue #74.

**1. It names the coordinate the adapter was guessing.** Every Workday tenant's
file carries one `Allow:` line per career site it has opened. Swisscom
publishes **three**; `resolve` finds **two** through a meta-board. The employer
had been publishing the answer all along, and `workday.py sites` reads it.

**2. It names where the duplicates are.** `workventure.com` hides from
Googlebot a set of feed files **named after the boards it syndicates to** —
`indeed.xml`, `jooble.xml`, `careerjet.xml`, `incruit.xml`. Read for
permission, that is a list of paths to avoid. **Read for information, it is the
board saying where its own ads will appear again**, which is what a ledger
needs in order to deduplicate.

**3. It names a directory an adapter file said did not exist.** `solique` and
`taleez` both declared a sitemap at the standard path, under a permissive file,
and both turned out to be tenant or ad directories. **Nothing was hidden; the
file was read for whether we could fetch and not for what it said was there**
(#72).

### Accessible is not intended, and the names do not say which

Novartis's Workday tenant names **`Internal_Careers_for_Acquired_Entities`**
beside its public site. **A tenant lists what it has opened to robots, not what
a candidate should read**, and the difference is invisible from the name alone
— which is why `workday.py sites` now says so out loud when a name reads
internal, and still only enumerates.

**Enumerating is not choosing.** A name found this way is a **candidate, never
a target**.

### Three ways this goes wrong, all measured the same day

**A `Sitemap:` line is a declaration, not an inventory.** It announces URLs. It
does not say they exist, that they resolve, or that they are adverts.
**Counting sitemap entries as ads produces exactly the class of number
`shared/plausible-and-false.md` exists for** — and Taleez's own sitemap was
read at 296 of 14 221 by a regex that matched only one slug shape, while
reporting success.

**Two formats defeat a naive reader.** AllJobs writes its `Allow:` paths in
**`%uXXXX`** — a notation removed from the URL specification: it is legible and
it does **not** compare equal to a normally-encoded URL without conversion.
And `jobmaster.co.il/jobs/` sits in a **redirect loop on the trailing slash**
that `curl` abandons at the fiftieth hop. **A discovery that follows the paths
it finds needs a hop bound and a defined behaviour when it hits one** — the
answer being *stop and say which path looped*, never *treat it as absent*.

### And the case that must not be read in our favour

`jobmaster.co.il` **names `Google-Extended` and `ChatGPT-User` in order to
allow them, and does not name any Anthropic agent.** The generic `*` group is
permissive, so a mechanical reading lands on *allowed*.

**Do not let the fallback settle it.** A site that took the trouble to
enumerate agents and did not enumerate ours has expressed something the generic
group does not represent, and **the honest description of that state is "not
addressed", not "permitted"**. It is the mirror of the case in the managed-block
section above, where an omission was equally not an invitation: **an omission
is not a decision in either direction, and it is certainly not a decision in
ours.**

The question of what a user-driven agent may do where it was not named stays
open in this repository. **It is not closed by silence, and least of all by
silence read our way.**

### The rules

1. **Read the file for what it names, not only for what it forbids.**
   `Sitemap:` lines, `Allow:` paths and the names of disallowed files are
   coordinates.
2. **A name found this way is a candidate, never a target** — show it, and let
   the user choose, especially where the name suggests an internal audience.
3. **Record where a coordinate came from.** *"Published by the employer in
   their own `robots.txt`"* is stronger than *"resolved from a meta-board"*,
   and where the two disagree — Swisscom, three against two — the employer's
   own file is the one to believe.
4. **Nothing in this section is a permission.** It changes what we may *learn*
   from a file, never what we may *fetch* from a host that refused.

## Which commands ask the host, and which do not

**Every command that reads advert content asks first.** Measured coverage,
2026-09-02, across the eight families whose tenants have their own hosts:

| Family | Guarded | Not guarded |
| :-- | :-- | :-- |
| Workday | `sites`, `list`, `ad` | `facets`, `resolve` |
| Taleez | `jobs`, `ad`, `sitemap` | — |
| Personio | `jobs`, `check` | — |
| umantis | `list`, `ad`, `check` | — |
| SuccessFactors | `list`, `ad`, `check` | `locale` |
| Oracle Cloud | `search`, `read` | `sites` |
| iCIMS | `list`, `ad` | `resolve` |
| Teamtailor (`ats.py`) | the listing path, so `list` and `ad` both | `resolve` |

**The unguarded ones read no advert.** `locale`, `sites`, `facets` and
`resolve` answer *what is this host* and *what does it offer* — a question
about the service, not a use of its content. Guarding them would also make a
refusing tenant undiscoverable, which helps nobody: **better to identify a host
and then refuse it loudly than to be unable to name what was refused.**

**`sitemap` is guarded, and that is a decision rather than an oversight.**
Enumerating a closed set does what the closure exists to prevent — the same
reasoning the Belarus survey applied when it declined to count ad sitemaps
sitting outside a disallowed path.

**And `check` is guarded because it is the one `cover-letter` calls when
somebody applies.** A tenant that wrote `ai-input=no` is refusing the content,
not the pagination.

## Terms of use are a different instrument, and they are read elsewhere

This file governs **machine-readable refusals**. A board's terms of use are
prose written for many readers at once, and the question there is which reader
a clause is addressed to — a harvesting clause and an anti-automation clause
look alike and do not bind alike. **`shared/reading-terms.md` holds that rule**
(issues #48 and #81).

**It opens no door in this one.** A `robots.txt` refusal stands whatever a
board's terms say about resale, and no reading of a prose document is a reason
to revisit the four questions above.

## What this file does not license

Not credentials, not paywalls, not consent walls, not anything a login guards,
and not personal data of any kind. **The AMS override covers public job
advertisements and nothing else.** Candidate profiles, employer contact
records and anything behind the eJob-Room's authentication are out of scope
here and stay out.

And it does not license quiet reinterpretation of the four questions to reach a
convenient answer. **If the reasoning has to be strained, the answer is obey.**
