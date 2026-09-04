# Board adapter — Applifly (Swiss ATS, one employer per host)

<!-- hosts: per-tenant -->
<!-- script: applifly.py -->
<!-- verified: 2026-09-03 -->
<!-- countries: CH -->

A Swiss applicant-tracking system. **Employers front it with their own vanity
domain** — `jobs.<employer>.ch` — so **the host never says Applifly and the
path does**: `/job/view-job.php` and `/jobs.php`, with `source=` in the query.
Same topology as SuccessFactors, which `shared/modules/ats-open-check.md`
already records as recognised by path rather than by host.

**No key, no cookie, no browser.** The ad carries a complete `JobPosting` —
**in microdata, not JSON-LD** — with coordinates on 8 of 8.

**Everything below was verified against `jobs.meanquest.ch` on 2026-09-03.
That is one tenant.** A web search for the template on other hosts returned
nothing, which establishes **nothing** about how many exist (#72): this is one
deployment, written as one deployment, and every line that could be
tenant-local says so.

## The parameter you would strip as tracking is the one that renders the page

Measured on one ad id:

| Query | Status | Bytes | The ad? |
| :-- | :-- | --: | :-- |
| `?id=1453` | `200` | 718 | no |
| `?id=1453&language=fr` | `200` | 718 | no |
| `?id=1453&source=applifly` | `200` | 99 | no |
| `?id=1453&language=fr&source=applifly` | `200` | **204 739** | **yes** |
| `?id=1453&language=fr&source=zzz` | `200` | 204 486 | **yes** |
| `?id=9999999&language=fr&source=applifly` | `302` | 0 | gone |

**Both parameters are required, and `source`'s value is irrelevant** — `zzz`
works. `language` must be a code the tenant knows: `language=xx` returns the
99-byte body.

**And the 718 bytes are not an error page.** They are a script that reads
`document.referrer` and reloads the same URL with `?source=<referrer>`
appended:

```html
var url = document.referrer.length > 0 ? encodeURIComponent(document.referrer) : 'direct';
window.location.href = urlToUse + "&source=" + encodeURIComponent(url);
```

**So a browser always sees the ad and a script never does, while the status
line says `200` every time.** This is referrer capture implemented as a
client-side self-redirect — **not client-side rendering, and it does not need
a browser.** That distinction is the expensive one: the first reading of this
host concluded *"a shell, probably client-rendered"* and wrote the ad off as
unverifiable. `shared/robots-policy.md`'s **decide by layer** is the rule — a
browser would fix it, which is exactly what makes it look like a browser-layer
problem, and the cause is one layer above at the cost of one query parameter.

**The site itself publishes the URL that does not work.** Its own
`og:url` and `<link rel="canonical">` carry `?id=…&language=fr` **without
`source`** — the form that answers `200` with the shell.

## And the advice that breaks it is already in this repository

`shared/boards/job-room.md` says of an `externalUrl`: *"Strip the query string
before storing or comparing."*

**Right for a dedup key, fatal for a fetch.** Here the id lives in the query,
so a stripped URL is not a shorter URL — it is a different page, and it
answers `200`. **Normalise for comparison, never for retrieval**, and keep the
two forms apart in whatever you store.

## The `JobPosting` is microdata, and two reasonable checks disagree

```
grep -c JobPosting page.html      → 1     "the ad is there"
parse every ld+json block         → none  "no structured data"
```

Both are looking at the same complete posting:
`itemscope itemtype="http://schema.org/JobPosting"`, twenty `itemprop`s.
`successfactors.md` established that **the tell is the block, not the
string**; this is the other half — **the block is not always JSON.**
`skills/job-scan/scripts/_microdata.py` reads it, with a real tag stack
because microdata nests.

**Three things the markup does that a spec-pure reader gets wrong:**

- **Coordinates live in `<input type="hidden" itemprop="latitude">`.**
  `input` is not one of schema.org's value elements, so a correct reader
  returns a `GeoCoordinates` block **with no properties** — present and empty,
  the shape this repository keeps finding in payloads. Reading the attribute
  turns **0 of 8 into 8 of 8.**
- **The `<h1 itemprop="title">` wraps a hidden `Organization` and a submit
  button**, so the spec-correct title reads *"Meanquest SA Cheffe / Chef de
  projet IT Envoyer"*. **The adapter takes the title from `<title>`**, and
  `_microdata.py` exposes `props_direct` (text excluding nested items) beside
  `props` for callers who need the other answer.
- **The address is on `PostalAddress`, not on `Place`** — `Place` carries only
  `address` pointing at it.

## What a card yields

Eight ads on the day, each fetched individually — the listing carries links
and little else.

| Field | Filled |
| :-- | --: |
| `title`, `company`, `location_text`, `posted_text`, `valid_through`, `employment_type`, `industry` | **8/8** |
| `latitude` / `longitude` | **8/8** |
| `street_address` | **4/8** — and **two of the four are a bare postcode** (`1820`, `1400`), two a street plus postcode |
| `description` | 8/8, 260 to 4 558 characters |

**`employmentType` mixes two things.** `CDI` on one ad, `Temps plein = 100%`
on the next — a contract type and a workload in one field. Emitted as printed:
one tenant is not a platform, and splitting it here would be a guess.

**`datePosted` is `dd/mm/yyyy` while `validThrough` is ISO**, in the same
block. Not normalised, for the same reason.

## An unknown id answers `302`, and the redirect is the answer

**Do not follow it.** `urllib` follows redirects by default and lands on a page
that serves the referrer shell — so a dead ad comes back looking like a
parameter mistake. Found while writing this: exit 2 where exit 3 was true.
That is the `-L` trap of `shared/plausible-and-false.md` in its silent,
no-flag form.

`applifly.py` builds an opener that returns the redirect, and exits **3** on
any `3xx` for an ad. **This host confirms both ways** — `200` with a
`JobPosting` for a live id, `3xx` for an unknown one — so it is a real second
witness for `cover-letter`'s step 1b, not a silent one.

## `robots.txt`

**3 196 bytes of `text/plain`**, and it is a discovery document as much as a
permission one (#74). It closes `/admin/`, `/candidate/`, `/employer/`,
`/company_area/`, `/ws/` and the worker back-offices; it **allows**
`/sitemap.xml` and the public assets; **it names no AI agent**; and neither
`/jobs.php` nor `/job/view-job.php` is refused.

**It also names the boards this ATS syndicates to**, one `Disallow` per
apply-bridge: `adzunaApply.php`, `broadbeanApply.php`, `careerjetApply.php`,
`indeedApply.php`, `jobrapidoApply.php`, `monsterApply.php`, `neuvooApply.php`,
`talentApply.php`, `whatsappApply.php`, `facebookApply.php`, `bakecaApply.php`.
**Read for permission that is a list of paths to avoid; read for information it
is the platform saying where its ads appear again** — which is what a ledger
needs in order to deduplicate.

`/sitemap.xml` is **real and carries no ads**: 1 099 bytes, four `<loc>`, all
of them landing pages (`jobs.php`, `jobs-by-region.php`, `jobs-by-role.php`,
`jobs-by-sector.php`). Counting `<loc>` here answers *is anything there* and
not *is it the thing you came for*.

## Configuration

```yaml
boards:
  applifly:
    enabled: true
    hosts:
      - jobs.meanquest.ch
    language: fr
    delay: 1.0
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `hosts` | yes | One employer per host. **There is no platform-wide index**: an Applifly host is found from an ad URL, not by enumeration |
| `language` | no | Default `fr`. A code the tenant does not know returns the 99-byte body |
| `delay` | no | Seconds between ad fetches, default 1.0 |

No credentials, no login, no browser.

## Zero-shaped answers

**1. The referrer shell, `200`, 718 bytes.** The headline. `applifly.py`
refuses to read it as an empty board and says which parameter is missing.

**2. The 99-byte body** for a `language` the tenant does not know.

**3. A `302` followed silently**, turning a dead ad into a parameter error.

**4. `GeoCoordinates` present and empty** to a spec-pure microdata reader.

**5. A `JobPosting` that no JSON-LD parser will find**, on a page where
`grep JobPosting` succeeds.

## Applying

Through the ad URL — **with its parameters** — in the user's own browser. The
apply flow asks for an account on the tenant's portal; **the plugin does not
create accounts and does not fill credential fields.**

## Pace

No published limit and no `429` over about 30 requests at 1 s apart. The
listing is 77 kB and an ad is ~205 kB, so the sweep is heavy per ad and cheap
in requests: eight ads cost nine round trips.

## Verification

```bash
S=skills/job-scan/scripts/applifly.py
python3 $S search --host jobs.meanquest.ch --limit 3
python3 $S ad --url "https://jobs.meanquest.ch/job/view-job.php?id=1453&language=fr&source=applifly"
python3 $S ad --url "https://jobs.meanquest.ch/job/view-job.php"   # refuses: no id
```
