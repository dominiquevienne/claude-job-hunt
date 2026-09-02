# Board adapter — DigitalRecruiters

<!-- verified: 2026-09-02 -->

**Re-verified 2026-09-02** on the question that decides how this adapter is
used: whether a tenant directory exists. The search is recorded below rather
than its conclusion — a negative claim cannot be checked by reading it.

A French ATS, part of **Cegid** since 2022, built for **multisite, multibrand**
employers: retail, franchise networks, large service groups. Renault, Decathlon,
Monoprix, O2 are named clients.

It is the fourth French ATS here, after `taleez.md`, `flatchr.md` and
`softy.md`, and the one with the most ads per employer — the tenant sampled had
**948**.

**Everything here was verified against the live API on 2026-08-31.**

## Why it is hard to find, and why that matters

DigitalRecruiters careers sites are **white-labelled on the employer's own
domain** — `recrutement.monoprix.fr`, not `monoprix.digitalrecruiters.com`.
Nothing about the URL says DigitalRecruiters, which is why these employers are
invisible to a meta-board *and* why no directory of them exists.

So the tenant key is **the careers hostname itself**, and it comes from the
user. To confirm a domain is a DR site before configuring it:

```
GET https://api.digitalrecruiters.com/careers/v1/careers-sites/<host>
→ 200 with the site's uuid, name and is_multibrand flag
```

## Two endpoints, no browser, no key

```
POST https://api.digitalrecruiters.com/public/v1/careers-site/job-ads
     ?domainName=<host>&locale=fr_FR&limit=200&page=1
→ {"count": 948, "items": [...], "filters": {...}}

GET  https://<host>/fr/annonce/<url>        one ad, with a JobPosting block
```

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/digitalrecruiters.py" \
  jobs --domain recrutement.monoprix.fr
```

948 ads came back in **3.7 seconds** across five pages.

### robots.txt, per host

- **The careers host** publishes `User-agent: *` / `Allow: /` /
  **`Crawl-delay: 10`**. Nothing is closed, and the pace is stated.
- **The API host** publishes no robots.txt at all — the path returns *"No
  context-path matches the request URI."*

The listing is a handful of requests on the API host; **every ad read hits the
careers host**, so ad reads are spaced at the published 10 seconds. That is
what makes `--with-detail` expensive here, and the script caps it (trap 5).

## Configuration

```yaml
boards:
  digitalrecruiters:
    enabled: true
    domains: ["recrutement.monoprix.fr"]
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `domains` | yes | The **careers hostname**, no scheme, no path. One employer each |
| `locale` | no | `fr_FR` by default |

No login, no account, no API key.

**No tenant directory was found. Searched 2026-09-02:**

| Looked at | Answer |
| :-- | :-- |
| `digitalrecruiters.com/robots.txt` | **301 → `www.cegid.com/fr/produits/cegid-hr/talent-acquisition/`**, 200 `text/html`, 384 KB — a product page, not a rules file |
| `digitalrecruiters.com/sitemap.xml` | the same redirect, the same page |
| `api.digitalrecruiters.com/robots.txt` | **404** `text/plain` — *"No context-path matches the request URI."* |
| `api.digitalrecruiters.com/careers/v1/careers-sites` and `…/` | **404** |
| `api.digitalrecruiters.com/public/v1/careers-sites` | **403** JSON — `{"message":"You're not allowed to access this resource"}` |

**That last row is the interesting one, and it is why this says *not found*
rather than *does not exist*.** A `403` on a path whose siblings `404` is an
endpoint that **is there and is closed**, not one that is absent. A tenant
listing may well exist behind it; it is simply not public, and nothing here
would reveal it.

So: ask the user for the careers URL, exactly as for `umantis.md`,
`taleez.md` and `flatchr.md` — and if that 403 ever becomes a 200, this
paragraph is the thing to re-read.

*(The vendor is now Cegid: the whole `digitalrecruiters.com` domain redirects
into Cegid's product pages, and `talentsoft.md` documents the other half of
the same acquisition. If a directory ever appears it will probably be a Cegid
one, covering both.)*

## The ad id and its URL

**The ledger key is the composite `id`, not `job_ad_id`** — see trap 1. The URL
comes from the item's own `url` field:

```
https://<host>/fr/annonce/<url>
```

In the ledger: `digitalrecruiters:<composite id>`.

## What the listing gives, and what it does not

Per ad: `title`, `contract`, `location`, `job_family`, `brand`, and the flags
below. **No description, no publication date and no salary** — those are on the
ad page.

The ad page adds, from its `JobPosting`: the description, `datePosted`,
`employmentType`, and a **full street address** (`1 Pl. Garibaldi`, `06300`,
`Nice`). That last one is rare — it is the field the ORP's PRE form wants and
that most boards omit entirely (see `shared/modules/job-room-ch.md`).

`baseSalary` exists but its `minValue`/`maxValue` were null on the ads sampled.

## Traps

**1. `job_ad_id` is not unique, and using it loses ads silently.** One posting
opened in several towns shares a single `job_ad_id`: on the tenant sampled,
948 ads carried only **940 distinct `job_ad_id`s** — two ads were each open in
five towns. The composite `id` (`<job_ad_id>-<location_id>`) is unique on all
948, and so is the `url`. Key the ledger on the composite: keying on
`job_ad_id` collapses five real postings into one and drops four with no error.

**2. The ad page names the group; only the listing names the brand.** The
tenant sampled carries four brands — Monoprix 884, Naturalia 36, monop' 21,
monop'beauty 7 — and every ad page says `hiringOrganization: Groupe MONOPRIX`.
The brand lives in the listing's `brand_id`, decoded through
`filters.brands`. Drop it and a Naturalia job reads as a Monoprix one.

**3. `is_aggregated` means the ad came from another careers site.** All 36
aggregated ads on the tenant sampled were Naturalia's — pulled in from
Naturalia's own site. So **the same posting may also be reachable under that
other domain**, and configuring both employers can double a row. The card
carries `aggregated` so the ledger can see it coming.

**4. A `GET` to the job-ads route answers `403`.** Not 404, not 405 — a
permissions-shaped error for what is only a wrong verb. It cost a detour here:
`/public/v1/...` looked like a closed partner API until the browser showed the
site itself calling the same path with `POST`. **Check the method before
concluding anything about access.**

**5. `--with-detail` on a whole tenant is not a thing you want.** 948 ads at the
published 10-second crawl-delay is **over two and a half hours**. The script
caps detail reads at `--max-detail` (default 50) and marks the rest
`detail_skipped: true` rather than letting the option quietly become an
afternoon. Screen on title, contract, brand and town first; read what passes.

**6. `limit=1000` works and then does not.** A single request for all 948 ads
succeeded once and **timed out at 60 seconds** on a later run. The sweep pages
at 200 instead — same total, no request big enough to hang. Do not "optimise"
it back into one call.

**7. There is no expiry date.** Like the other three French ATS, and unlike
`meteojob.md` (+60 days) and `hellowork.md` (+30), `validThrough` is absent
entirely. Freshness comes from the ad page's `datePosted` — which means it
costs a request, and the listing alone cannot tell you how old an ad is.

## The facet catalogue

```bash
python3 .../digitalrecruiters.py filters --domain recrutement.monoprix.fr
```

Returns every filter the site offers with names and counts — jobs (47 on the
tenant sampled), contract types, working times, brands, remote-work types and
the employer's own custom fields (19 choices). Unlike `apec.md`, the ids come
**with their labels**, so nothing has to be guessed.

## Applying

The apply flow is on the employer's own careers site. **No assisted apply is
implemented**, and the plugin does not create accounts and does not fill
credential fields. Hand the user the ad URL with their documents.

## Pace, and the note on access

The listing is five requests for a 948-ad employer, on a host that publishes no
robots.txt. Ad reads go to the careers host and are spaced at its published
**10-second** crawl-delay, capped by `--max-detail`.

These are public careers pages, read through the endpoint the pages themselves
call, unauthenticated, for one person's job search — at the pace the site asked
for.
