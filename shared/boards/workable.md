# Board adapter — Workable

<!-- verified: 2026-09-02 -->

**Re-verified 2026-09-02.** `storyteq` still answers with live postings on the
documented route. Three other tenants — `rasa`, `contentsquare`, `sylvera` —
answered **`0 of 0 postings kept`**, which is this adapter's honest empty: the
account exists and is publishing nothing. `vercel` and `hostinger` answered a
clean 404. Both shapes are worth knowing apart, and neither is a breakage.

One employer at a time, by tenant. **No browser, no account, no cookie.** Same
family as `greenhouse.md`, `lever.md`, `ashby.md` and `smartrecruiters.md`, and
the same script: `skills/job-scan/scripts/ats.py`.

**Everything here was measured against the live API on 2026-08-30.**

## Configuration

```yaml
boards:
  workable:
    enabled: true
    employers: ["storyteq", "…"]
```

The tenant is the account slug in the employer's careers URL —
`apply.workable.com/<tenant>` — or whatever `ats.py resolve "<employer>"`
returns. **Never guess it**: an invented slug answers `404` and the adapter says
so with exit code `4`, which is the good case. Guessing a plausible one that
happens to exist gives you another company's board.

## Usage

```bash
ats.py list --provider workable --tenant storyteq
ats.py ad   --provider workable --tenant storyteq --id 6C529DB5AE
ats.py resolve "Storyteq"
```

## One request returns the whole board, descriptions included

```
GET https://apply.workable.com/api/v1/widget/accounts/<tenant>?details=true
```

HTTP 200, `application/json`, unauthenticated. **There is no paging.** With
`details=true` every ad carries its full `description`, so a complete sweep of
an employer — text and all — is a single call. Without the parameter the same
call returns the same ads with **no description field at all**, which reads as
an employer who wrote nothing rather than as a missing parameter.

`ats.py` passes `details=true` whenever descriptions are wanted, and that is
`list` by default.

## `published_on` is the posting date. `created_at` is not.

Both are present on every ad and they are **not** the same thing:

| Field | Meaning |
| :-- | :-- |
| `created_at` | when the ad was drafted |
| `published_on` | when it went live |

On a live posting measured that day they were **six weeks apart** — created
`2026-07-13`, published `2026-08-24`. HiringCafe was serving the earlier one,
which made a six-day-old vacancy look like a month-and-a-half-old one and put it
in the at-risk band of `cover-letter` step 1b for nothing.

The card exposes **`published` = `published_on`** and keeps `created` beside it.
Age is judged on `published`. Never on `created`.

## `remote` alone is a trap — read `remote_countries`

Workable ads set `telecommuting: true` freely, and on this board a remote role is
very often remote **within one country only**. The countries sit in
`locations[]`:

```json
"locations": [{"country": "South Africa", "countryCode": "ZA", "city": ""}]
```

That is the ad's real eligibility rule — schema.org calls it
`applicantLocationRequirements`, and `jobs.workable.com` publishes it under that
name. The card carries it as **`remote_countries`** (codes) and
**`remote_country_names`**.

**Score it as a hard blocker when the candidate cannot live there.** This is not
a hypothetical: an ad matching a candidate's stack at 86 %, the best fit in their
pipeline, was remote-but-South-Africa-only while the aggregator that surfaced it
recorded the country as the Netherlands. Reading `remote: true` and stopping
there produces a perfect-looking match nobody is allowed to take.

## The id, and the two URL shapes

The identifier is **`shortcode`** — 10 uppercase hex characters, e.g.
`6C529DB5AE`. The ledger row is `workable:<tenant>:<shortcode>`.

| Shape | Use |
| :-- | :-- |
| `apply.workable.com/j/<shortcode>` | the ad — redirects to `/<tenant>/j/<shortcode>/`, so the shortcode alone resolves the tenant |
| `apply.workable.com/j/<shortcode>/apply` | the application form (`apply_url`) |
| `jobs.workable.com/view/<22-char id>/<slug>` | Workable's own cross-employer board — **a different id**, and how the ad appears when an aggregator links to it |

**The two ids are not derivable from one another.** If a row arrives carrying a
`jobs.workable.com` id, it will not match a `shortcode`; dedupe on `apply_url`
instead, as `hiringcafe.md` already recommends.

## What this adapter does NOT do

**It does not search across employers.** Like the rest of this family it answers
"is X hiring?", never "who is hiring near me?".

Workable does run a cross-employer board at `jobs.workable.com/search`, but its
results are fetched client-side, the page sets a Turnstile feature flag, and one
attempt at the obvious query parameters returned an empty embedded result set.
**Not implemented, and not to be assumed working** — see the *possible future*
note in the board request.

## Fields on the card

`title`, `company` (the account's real name, not the slug), `location`
(assembled from `city` / `state` / `country`, falling back to `locations[0]`),
`published`, `created`, `department` (or `function`), `employment_type`,
`remote`, `remote_countries`, `remote_country_names`, `description`.

`updated` is `null`: Workable's widget API publishes no modification date.

## Exit codes

| Code | Meaning |
| :-- | :-- |
| `4` | no such tenant (HTTP 404) — check the slug with `resolve` |
| `3` | `ad` was asked for a shortcode no longer on the board — filled or pulled, record it `discarded` |

**A `403` has never been observed here**, unlike umantis. Absence from the
listing is the only closure signal this board gives, and it is a reliable one:
the endpoint returns the employer's whole live board every time.

## `resolve` can hand you a tenant `list` refuses

Re-verified 2026-09-02. `ats.py resolve "Storyteq"` returns two rows, and the
second one works. The first does not:

```
{"provider": "workable", "tenant": "inspired_thinking_group_(itg)", …}
→ ats.py list --provider workable --tenant "inspired_thinking_group_(itg)"
→ HTTP 404, raw and percent-encoded alike
```

`resolve` reads HiringCafe's `ats_tenant` field, and HiringCafe sometimes
records **a label rather than the slug Workable answers to**. The old error
message told the reader to run `resolve` — which is what produced the bad
value — so the advice looped. It now says where the real slug is: **in the
employer's own `apply.workable.com/<tenant>` URL**.

**A tenant that 404s is not proof the employer has no Workable board.**

