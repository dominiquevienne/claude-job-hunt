# Board adapter — Taleez

<!-- verified: 2026-09-02 -->

<!-- hosts: taleez.com -->
<!-- script: taleez.py -->
<!-- countries: * -->
## The directory this file said did not exist

**Corrected 2026-09-02.** This file said there was no tenant directory and
that the user must supply a careers URL. **The platform publishes the whole
board**:

```
https://taleez.com/sitemap.xml       → an index, 2 entries
https://taleez.com/sitemap-job.xml   → 1.8 MB, application/xml
                                       **14 221 /apply/<slug> URLs**
taleez.py sitemap                    → those slugs
taleez.py ad <slug>                  → the ad, **with no tenant**
```

That last line is what makes it a directory rather than a list: an ad reads
without knowing which employer it belongs to, so enumerate-then-read works
across the whole platform.

**One shape to get right.** The slug is not always the short opaque id: **296
of the 14 221 look like `fmudc`, and the other 13 925 are long descriptive
ones** ending in the contract type. Matching only the short form finds **2% of
the board** — measured here while writing the command, which is how it is
known.

**It is the board, not a search.** No keyword, no location, no filter: the
sitemap enumerates and nothing narrows. Per-tenant reading through
`taleez.py jobs` stays the targeted route, and this is the one for coverage.



A French ATS, built in Toulouse, used by **SMEs and mid-sized companies**. Its
careers sites are the French counterpart of `umantis.md`: employers that no
meta-board indexes, reachable one tenant at a time — **and also, since
2026-09-02, through the platform's own sitemap of 14 221 ads.**

**Everything here was verified against the live API on 2026-08-31.**

## Why it earns a place

`shared/boards/README.md` calls the French ATS family the biggest remaining
blind spot, for the reason `umantis.md` documents on the Swiss side: an ATS
serves one employer, so a meta-board built on job-board feeds never sees it.
Taleez says it carries **19 000 HR users**; the six tenants sampled here held
**22, 74, 412, 3, 1 and 5** open ads.

Unlike an agency board, the employer is not merely named — **the site *is* the
employer**, so `company` is the workplace, never an intermediary.

## Two endpoints, no browser, no key

```
GET https://<tenant>.taleez.com/api/careez
→ the whole careers site as JSON — every job, plus the tenant's property
  referential and its units — in ONE request

GET https://taleez.com/apply/<job slug>
→ the ad, server-rendered, with a full JobPosting block
```

Both unauthenticated. `ufcv-emploi` returned **412 ads in a single call**.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/taleez.py" \
  jobs --tenant bertintechnologies --with-detail
```

**`api.taleez.com` is a different thing** — the recruiter API, which answers
`403 Authentication required` without a key. Do not confuse the two: the one
this adapter uses is on the *tenant* host and needs nothing.

### What robots.txt says, on which host

Worth reading carefully, because the two hosts differ and the difference is
what this adapter rests on.

- **Tenant hosts** — `bertintechnologies.taleez.com`, `animalis.taleez.com`,
  `ufcv-emploi.taleez.com`, all three checked: `User-agent: *` and a `Sitemap:`
  line, **and no `Disallow` at all**. Nothing on a tenant host is closed,
  including `/api/careez`, which is the endpoint that host's own public careers
  page calls to render itself for candidates.
- **`taleez.com`** — the marketing and apply domain — disallows `/api/`,
  `/widgets/`, `/ssr/`, `/u/`, `/files/`, `/feeds/` and `/exports/`. It does
  **not** disallow `/apply/`, which is where the ads live. It also explicitly
  `Allow`s GPTBot and ClaudeBot.

So: the listing comes from a host that forbids nothing, and the ad comes from a
path that is not forbidden on a host that forbids several others. **Do not read
`taleez.com`'s `Disallow: /api/` as covering the tenant endpoint** — different
host, different file — but do note the tension rather than pretending it is not
there, and never fetch `taleez.com/api/…` or `/widgets/`.

## Configuration

```yaml
boards:
  taleez:
    enabled: true
    tenants: ["bertintechnologies", "ufcv-emploi"]
    with_detail: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `tenants` | yes | The **first label of the careers host** — `bertintechnologies` in `bertintechnologies.taleez.com`. One employer each |
| `with_detail` | no | Reads each ad page for the description. **One request per ad**, and the listing has no description at all |

No login, no account, no API key.

**There is no tenant resolver, and there cannot be one.** `app.taleez.com/jobs`
is an empty SPA shell with no cross-tenant ads; every tenant sitemap lists only
its static pages and **no job URLs**. So a tenant cannot be looked up from an
employer's name — **ask the user for the careers URL**, exactly as
`umantis.md` requires. The script accepts `--url` and reads the tenant out of
the host.

## The ad id and its URL

The ledger key is the numeric `id`. The **URL is built from the `slug`, not the
id**:

```
https://taleez.com/apply/<slug>
```

In the ledger: `taleez:<id>`.

## Traps

**1. The server compresses whatever you ask for.** Sending
`Accept-Encoding: identity` is **ignored** — the body still arrives compressed,
`200 OK`, right length. Nothing errors; every regex simply finds nothing, so an
ad page reads as "no JobPosting" and a whole tenant looks like it changed its
markup. The script asks for `gzip` — the one encoding the standard library can
undo — and undoes it. **This cost a debugging cycle; do not remove it.**

**2. A property's label is in `value`, not in any `*Name` field.** The
definition uses `internalName` / `publicName`, so reading a *choice* the same
way returns `None` for every ad — which looks like a tenant that fills nothing
in, not like a bug. The choices carry `value`.

**3. Tenants rename their own fields, so key on `lockedType`.** Bertin calls a
property *"Domaine métier"*, UFCV calls its *"Profil"*. The definition's
`lockedType` — `DEPARTMENT`, `XP`, `REMOTE`, `APPRENTICESHIP` — is the stable
meaning underneath, and the card uses it where present, falling back to the
tenant's own label otherwise. Never build a rule on the French label.

**4. Only the slug opens an ad, and only on `taleez.com`.**
`taleez.com/apply/<numeric id>` is a 404, and so is
`<tenant>.taleez.com/apply/<slug>`. Both are plausible enough to try; neither
works.

**5. There is no `validThrough` and no `baseSalary`.** Unlike `meteojob.md`
(+60 days) and `hellowork.md` (+30 days), Taleez publishes no expiry at all —
which is **better**, because those two publish a formula that only looks like
one. Nothing here needs to go into `shared/ats-open-check.md` as an oracle;
freshness comes from `publishDate`, which every ad carries.

**6. The listing has no description whatsoever.** Not a teaser, not a snippet —
the field does not exist. Scoring on the listing alone means scoring a title, a
contract and a town, so `--with-detail` is not optional here the way it is on
boards that ship an excerpt.

**7. An empty tenant is not a wrong tenant.** A tenant with nothing open
returns `200` and `jobs: []`; a wrong slug is a `404`. The script says which it
saw. One tenant returned zero ads once and three ads immediately afterwards
with no change in the request — **unexplained, observed once** — so treat a
lone zero as worth one re-check before recording dormancy.

## Applying

Ads link to Taleez's own apply flow at `taleez.com/apply/<slug>`, and there is
also a spontaneous-application URL per tenant. **No assisted apply is
implemented**, and the plugin does not create accounts and does not fill
credential fields. Hand the user the ad URL with their documents.

## Pace, and the note on access

**One request per tenant** for the whole board — the cheapest listing of any
adapter here — plus one per ad with `--with-detail`, spaced by `--delay`
(default 1s). A tenant with 412 ads is 413 requests with details on, so put
large tenants behind a decision rather than sweeping them nightly.

These are public careers pages read through the endpoint the pages themselves
use, unauthenticated, for one person's job search. Keep the pace human.
