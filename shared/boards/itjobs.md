# Board adapter — ITJobs (`itjobs.pt`, Portugal): a keyed read-only API, an adapter exercised on a stub of the documented envelope, and no live call until the user holds a key

<!-- verified: 2026-09-13 -->

<!-- hosts: api.itjobs.pt, www.itjobs.pt -->
<!-- script: itjobs.py -->
<!-- host-forms: api.itjobs.pt, www.itjobs.pt -->
<!-- host-forms-basis: read — `itjobs.py:API` and `:SITE`, two literals: the API host for every call, the site host for the advertisement address · 2026-09-13 -->
<!-- countries: PT -->
<!-- content: indeterminate · no live call was made — `ITJOBS_API_KEY` is absent on this machine by design and the adapter exits 7 saying so; the documentation's own example envelope states `total: 2449` (a 2015 example, not a count of today) and the adapter prints «n emitted, site states total» on the first keyed run · 2026-09-13 -->
<!-- witness: the API's own `total` in every list/search envelope, printed beside the distinct count on the first keyed run; until then, none — a stub is not a witness and this line says so · 2026-09-13 -->

**Portugal's IT board, with a public read-only API that issues a key
against an e-mail address — the fourth Portuguese host with a script here,
and the first whose count is not measured, because measuring it needs a
key the plugin does not obtain.** Written 2026-09-13 10:18–10:4x UTC from
the site's own API documentation, exercised against a stub of the envelope
it documents; the only live requests were the rules and the documentation
pages, under the declared identity.

## Rules, and why they are not the gate here

```
api.itjobs.pt/robots.txt    200, 2 227 B — `*` open on /job/… (guard allowed True, certain True)
www.itjobs.pt/robots.txt    200 — `*` open on / and /api/…
identity                    claude-user, http
```

*On an API host the access control is the key, not the rules — decision
of 2026-09-04 (#100).* The identity is still sent on every call.

## The API, as the site documents it

```
https://api.itjobs.pt/job/list.json      api_key · limit · page · company · type · contract   -> {total, page, limit, results[]}
https://api.itjobs.pt/job/search.json    api_key · q (comma-separated) · limit · page · …     -> {total, page, limit, query, results[]}
https://api.itjobs.pt/job/get.json       api_key · id                                          -> the job · or {error: {message: "Job not found."}} in a 200 body
record   id · title · body (HTML) · ref · company{id, name, url, slug, address, phone, email} · companyId · salaryMin · salaryMax
         workModel · types[{id, name}] · contracts[] · locations[{id, name}] · country · publishedAt · updatedAt · slug
sandbox  api.sandbox.itjobs.pt — a daily replica, HTTP only, «no limits on job slots» (not used: it needs the same key)
```

**Two traps are handled before the first run.** «Job not found.» comes
back as a 200 body with an `error` object — the adapter reads
`error.message` before anything else and exits 3 on it, never a success
on a readable body. And the key is a credential: read from the
environment first, then from the workspace `credentials.env` or
`~/.itjobs.env` (`_secrets.get`), **never printed, never asked for by the
plugin** — without it the adapter exits 7 with the where-to-put-it note,
and the mutation bench holds «the key appears in no output» red (a
`note()` echoing it inside the request path reddens the test, once the
test stubs `urlopen` and not the caller).

## What the adapter prints on the first keyed run, and what it says now

```
itjobs.py list            n emitted, site states <total> over p page(s) — equal / k short   (50 a page)
itjobs.py search --query  the same, on the site's search
itjobs.py ad --id         the record in full, body as text
without the key           ERROR: `ITJOBS_API_KEY` not found — … exit 7, no request made
```

**The advertisement address is rebuilt from the id and slug as
`www.itjobs.pt/oferta/<id>/<slug>` and the row carries
`url_shape_confirmed: false`** — the site's listing page renders its
links client-side (69 691 B of `/empresa/<slug>` and chrome, no
advertisement link in the HTML), so the shape was not read anywhere; the
first keyed run opens one `url` and corrects `ad_url()` if it is wrong.

## Configuration

```yaml
boards:
  itjobs:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `ITJOBS_API_KEY` | yes — **a credential, not a config key** | environment, or `credentials.env` in the workspace, or `~/.itjobs.env`; obtained by the user at www.itjobs.pt/api |

## What is not established

- **The count** — no live call; the documentation's `total: 2449` is a
  2015 example and is not cited as a figure.
- **The URL shape** — see above.
- **The salary's unit** — the API states neither a currency nor a period
  for `salaryMin`/`salaryMax` (the documentation's 11 000–17 000 on a Lisbon
  job reads as EUR a year, and «reads as» is not «stated»); the row carries
  `salary_currency: null, salary_unit_stated: false`.
- **The page size the API accepts** — 50 requested; the documentation
  gives no maximum.
- **Whether `contracts[]` is on list rows** — the documentation shows it
  on search rows and not on list rows; the adapter reads it when present.

## 2026-09-13 — shipped on a stub

Three tests on the documented envelope; five mutations on a detached
worktree (`python3 -B`), five red — the fifth only after the test was
moved from stubbing `call()` to stubbing `urlopen`, because an echo
inside `call()` was invisible to a test that never ran `call()`.
