# Board adapter — SmartRecruiters

<!-- verified: 2026-09-11 -->

<!-- hosts: api.smartrecruiters.com -->
<!-- script: ats.py -->
<!-- countries: * -->
SmartRecruiters is an ATS, not a board. Each employer has its own board under a
**tenant token**, and its postings are public JSON — the same feed that renders
that employer's careers page. No key, no cookie, no browser.

**Everything here was verified against the live API on 2026-08-28**, against two
unrelated tenants: `nexthink` (103 postings, headquarters in Lausanne) and `sgs`
(4 387 postings, headquarters in Geneva).

Read by `skills/job-scan/scripts/ats.py`, the fourth provider alongside
Greenhouse, Lever and Ashby. It answers *"is my target employer hiring?"*, never
*"who is hiring near me?"* — see `greenhouse.md` for what this family is for.

## Why it was worth adding

`ats.py resolve` has been naming this ATS and then stopping since v1.7.0:

```
$ ats.py resolve "Nexthink"
'Nexthink' was found, but on an ATS this script does not cover:
  Nexthink -> smartrecruiters / nexthink
```

The resolver already knew the tenant. Only the reader was missing, so this is
the cheapest adapter in the repository — and it closes the most common dead end
the resolver produced. It now answers:

```
$ ats.py resolve "Nexthink"
{"provider": "smartrecruiters", "tenant": "nexthink", "company": "Nexthink"}
```

## Reading a board

```
https://api.smartrecruiters.com/v1/companies/<tenant>/postings   # the list
https://api.smartrecruiters.com/v1/companies/<tenant>/postings/<id>   # one ad
```

```
ats.py list --provider smartrecruiters --tenant nexthink --country ch
ats.py ad   --provider smartrecruiters --tenant nexthink --id 744000145952849
```

**The tenant is case-insensitive in the API path** — `nexthink`, `Nexthink` and
`NEXTHINK` all return the same 103 postings. The **public URL is not**: it uses
the employer's canonical capitalisation (`Nexthink`, `SGS`), which the payload
carries as `company.identifier`. Build URLs from that field, never from what the
user typed.

## The trap that has no answer

**A wrong tenant and an employer with nothing open are the same response.**

```
GET /v1/companies/nosuchtenantxyz/postings   ->  HTTP 200, {"totalFound": 0}
```

Not a 404. Greenhouse, Lever and Ashby all answer 404 on an unknown tenant; this
one does not, and **there is no second request that separates the two cases**:

- `/v1/companies/<tenant>` answers **404 for valid tenants too** — it is not a
  public endpoint, so it proves nothing.
- `careers.smartrecruiters.com/<tenant>` answers **200 for anything**, including
  `NOSUCHTENANTXYZ`.

**Re-tested 2026-09-02, and it is now byte-proven rather than asserted.** An
invented tenant and an employer that is not on this ATS return **the same 52
bytes, same md5 `9cfa41d4…`**:

```
nosuchtenantxyz → 200, {"offset":0,"limit":100,"totalFound":0,"content":[]}
bosch           → 200, byte-identical
visa            → 200, byte-identical
```

And the endpoint that could have separated them still refuses everyone:
`/v1/companies/<tenant>` answered **404 for `Nexthink` too** — a tenant whose
`/postings` returns 172 KB of live vacancies the same minute. **The response
headers carry nothing either**: no company or tenant field, and the only
differences between a real and a fake tenant are `content-length` and `vary`,
both artefacts of body size.

*What was not tested: a genuine SmartRecruiters tenant with zero open
postings. None was found to try. By construction it would return the same
paged empty list, but that is reasoning, not a measurement — so the claim
here is that **nothing distinguishes an unknown tenant from a non-tenant**,
which is measured, and that no second request is known to separate either from
a genuinely empty one.*

So the script refuses on zero rather than reporting an empty board, and says
both possibilities out loud. **Never report "they are not hiring" from this
board without confirming the token**, with `ats.py resolve` or the employer's
own careers URL. `bosch`, `visa`, `ubisoft` and `logitech` all return zero here
— none of them is out of vacancies; none of them is a SmartRecruiters tenant.

## Traps

**1. `limit` is silently clamped at 100.** Asking for 500 returns 100 with HTTP
200 — no error, no warning. Workday refuses an oversized page with HTTP 400,
which is the honest behaviour; this one does not, so a reader that trusts its
own `limit` silently sees a fraction of the board. Pagination via `offset` is
mandatory, and it works at depth (verified at `offset=4000` on SGS).

**2. The list feed carries no description at all.** Unlike Greenhouse's
`?content=true`, there is no flag: the description lives only on the per-ad
endpoint. `--with-description` therefore costs **one extra request per ad**, and
the script says so in its own `--help`.

**3. The ad is split across sections, and the one that matters most is not
`jobDescription`.** A posting's `jobAd.sections` holds `companyDescription`,
`jobDescription`, `qualifications` and `additionalInformation` — and
`qualifications`, which carries the must-haves the scoring reads, ran 1 627 to
2 256 characters on the ads sampled, entirely outside `jobDescription`. Taking
`jobDescription` alone loses the requirements while looking like a complete
read. Some boards add further sections (`videos` was observed), so the script
concatenates the four known ones **and then anything else it finds**.

**4. `country` and `city` want opposite capitalisation, and both fail
silently.** These are the only server-side filters in this adapter family:

| Filter | Form | Wrong form |
| :-- | :-- | :-- |
| `country` | lowercase ISO-2 — `ch` | `zz` returns **0**, HTTP 200 |
| `city` | **capitalised** — `Boston` → 17, `Callao` → 217 | `boston`, `callao` return **0**, HTTP 200 |

Verified on both tenants. A reader that normalises user input to lowercase — the
obvious thing to do — empties the board on `city` and works on `country`. The
script exposes `--country` only, because it is the one whose convention is
stable; filter towns locally with `--location`, which is accent-insensitive.

**5. Boards can be very large.** SGS carries 4 387 postings at 100 per page. The
script stops at 30 pages and says *"read 3 000 of 4 387 — narrow it with
--country"* rather than implying it read the board.

## What the feed gives that the siblings do not

`location` carries **separate `remote` and `hybrid` booleans**, plus
`fullLocation` (`Lausanne, VD, Switzerland`) and coordinates. That is a real
work-mode signal, unlike Workday's `remoteType`, which employers fill with a
workload. Both are recorded on the card. The per-ad payload also carries
`active`, a direct answer for `cover-letter` step 1b.

Everything on the list feed came back `visibility: PUBLIC` on both tenants;
whether a non-public posting can appear here was **not** established, so nothing
is filtered on that field.

## The ledger

```
smartrecruiters:<tenant>:<id>     e.g. smartrecruiters:nexthink:744000145952849
```

The tenant is lowercased in the key so that one board yields one row whatever
capitalisation the user typed, and the id alone cannot rebuild a URL without it.

## Applying

The employer's own SmartRecruiters flow, behind account creation. **The plugin
does not create accounts and does not fill credential fields** — hand the user
`apply_url` and their documents, as for any external ATS.

## Pace

One `list` per employer per run is a handful of requests. `--with-description`
multiplies it by the number of ads kept, so filter first and read descriptions
second.

## `robots.txt` — measured, and the earlier justification retracted

**Decided 2026-09-03 by the user: read this host. The reasoning below is the
second one written that day; the first was wrong on its decisive fact.**

`api.smartrecruiters.com/robots.txt` — **the host `ats.py` actually reads**
(`SR_API = "https://api.smartrecruiters.com/v1/companies"`) — is 72 bytes, four
lines, verbatim:

```
User-agent: LinkedInBot
Allow: /v1/companies/
User-agent: *
Disallow: /
```

**It names one commercial crawler, allows it exactly the path we read, and
closes everyone else.** No Anthropic token appears.

> **Retracted 2026-09-03, same day.** This section first argued that the
> operator *"publishes an `llms.txt` index addressed to AI agents"*, and that
> between two statements the more specifically addressed one governs.
> **The fact is wrong: `api.smartrecruiters.com/llms.txt` returns 404.** The
> `llms.txt` files live on `developers.` (documentation index) and `www.`
> (generated by an SEO plugin for the marketing site) — **other hosts, other
> content.** And the argument then inverts: **the most specific declaration for
> this host is this host's own `robots.txt`, and it refuses.** That is the rule
> this repository applies in the mirror case — a permissive statement on one
> host does not open a neighbouring host that refuses.

**What the file actually is: the AMS shape.** `shared/robots-policy.md` already
describes it — *"jobs.ams.at disallows /public/emps/ to all agents but
LinkedInBot"* — and answers it under question 3: **a site that closes the door
to everyone has made a policy and is entitled to it; one that opens it to a
single commercial party and closes it to all others has not made a policy, it
has picked a winner.** That, and only that, is what makes an override weighable
here.

**So this is not an exception to the doctrine — it is the case the doctrine
already provides for**, and it must go through the same route as AMS: the
`override_robots` configuration key, absent by default, the onboarding step that
warns before asking with no pre-ticked box, and the sentence printed on every
run. **Not a condition hardcoded in `ats.py`**, which would remove the one thing
that procedure exists to guarantee — that the user is told and decides, each
time.

**Until that route is wired, the honest state is the one to record: `ats.py`
reads this host without consulting the guard at all** (it calls it only for
teamtailor, line 418). **That is the state to end, whichever way the override
goes.**

### The open alternative, not taken

The operator supports a key without requiring it on this path. Taking one would
make the read attributable, at the cost of a credential to obtain and store.
**Not taken, for simplicity** — recorded so the choice stays visible.

**Re-exercised 2026-09-08**: without the override, `list --provider
smartrecruiters` **exits 7**. `api.smartrecruiters.com` publishes
`User-agent: * / Disallow: /` — everything closed, evenly — so the board is
skipped rather than silently obeyed. **It does not generalise**: Greenhouse,
Workable and Lever publish files of the same kind that permit.

### The override was a dead switch until 2026-09-08, and now it is not — #185

**It printed «&nbsp;override ACTIVE&nbsp;» and the guard on the next line killed
the request.** *Same zero, same exit 7, with the flag and without.* **#121 put
the override at `fetch()`'s choke point and #175 put the generic guard at the
same one**; each did what its issue asked, and their composition was false.

**Decision A of the repository's owner: honour the override.** Measured after:

```
list --provider smartrecruiters --tenant Evooq                     exit 7,  0 postings
list --provider smartrecruiters --tenant Evooq --override-robots   exit 0,  8 postings
```

> **The waiver is bounded by construction, not by care**: it can only be set
> inside `url.startswith(SR_API)`, so no other host reaches it however
> `fetch()` is later edited. **The #175 guard is untouched everywhere else**,
> and a test asserts that for Ashby, Greenhouse and Lever by name.

### What the announcement says first — #192, 2026-09-08

**`api.smartrecruiters.com` publishes `User-agent: * / Disallow: /`.** *That
group is not an anti-crawler clause: it is the one addressed to everybody, and
it is the least ambiguous refusal a site can write.*

**The banner names that refusal before it names the cost.** *The earlier wording
opened on «&nbsp;the address that gets blocked is yours&nbsp;» — a consequence —
and never said what the host had actually written.*

> **Consenting to a risk is not consenting to an act.** *A reader told
> «&nbsp;you might get blocked&nbsp;» agrees to a risk they run. A reader told
> «&nbsp;this site refused everybody and you are going in anyway&nbsp;» agrees
> to what they are doing.*

**Four places say the same thing** — the banner, the message printed when the
key is absent, `shared/setup.md`, and this card — *and the test asserts the
NATURE of the refusal is in the banner, not only its cost: a guard that checks
a `[bypass]` line was printed stays green on a banner that lies by omission,
which is what had happened.*

*This repository is public: the switch ships to whoever installs the plugin,
and the owner's consent covers the owner.*

*A test that checks `smartrecruiters_gate()` is called stays green on the old
defect — it was called. What was missing is a test of the composition, and the
general form is: **wherever a choke point carries more than one guard, exercise
their composition rather than each in isolation.***

### The key was set and nothing read it — #206, 2026-09-11

**`override_robots: true` had been in the user's `config.yml` since 2026-09-08,
and the four tenants they had configured returned `0` each.** *The flag worked
(`--override-robots`, #185); it was documented as «&nbsp;carrying&nbsp;» the
key from the config; and no step of `job-scan` passed it.* Measured 2026-09-11
11:08 UTC, the invocation this card documents, without the flag: `0 0 0 0`,
exit 7 each. With the flag by hand: `12 30 1 7` — **50 postings from employers
the user had chosen, lost to a zero that this card itself names as the trap of
this host.**

> **A consent that has to be re-transmitted by prose is a consent that gets
> lost.** *And its loss reads as «&nbsp;this employer is not hiring&nbsp;».*

**Now `ats.py` reads the key itself** — `override_enabled()`, the workspace
resolved by `bin/workspace-path.py` as `_secrets.py` resolves it, the block
parsed by `dormant.read_boards`, **one key, this host only**. Same invocation,
no flag, 11:10 UTC: `12 30 1 7`, one `[bypass]` banner each. With no config
found, exit 7 and the message says which file it looked for — *an absent key and
an unfound config are two different things to fix.* The flag stays for a run
whose config is elsewhere. `skills/job-scan/SKILL.md`'s «&nbsp;no adapter reads
the config&nbsp;» now says *for the profile*, and a test keeps the exception at one
adapter.
