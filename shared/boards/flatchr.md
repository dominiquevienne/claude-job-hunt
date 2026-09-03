# Board adapter — Flatchr

<!-- verified: 2026-09-02 -->

<!-- hosts: careers.flatchr.io -->
**No tenant directory was found. Searched 2026-09-02**, after `taleez.md` and
`solique.md` both turned out to have one at the standard path:
`careers.flatchr.io/sitemap.xml` **redirects to `www.flatchr.io/sitemap.xml`**
— 5.7 MB of `application/xml`, and **730 URLs of the vendor's own marketing
site**: blog posts, landing pages, integration pages. No tenant, no ad. The
user still supplies the careers URL.

A French ATS for **SMEs and mid-sized companies**, and the second of the French
ATS family this plugin sweeps, alongside `taleez.md`. Same shape as
`umantis.md`: one employer per careers site, **no directory**, and the user
supplies the URL.

**Everything here was verified against the live site on 2026-08-31.**

## One request returns the ads *and* their descriptions

Flatchr careers sites are Next.js, and the whole job list is server-rendered
into the page's `__NEXT_DATA__` payload — **descriptions included**. So a
tenant costs exactly one request, with no per-ad read at all.

That is the difference from Taleez, whose listing carries no description and
charges a request per ad. Here the listing is the richest payload of any
adapter in this repository: **55 fields per ad**.

```
GET https://<tenant>.flatchr.io/                     ─┐ byte-for-byte the
GET https://careers.flatchr.io/fr/company/<tenant>   ─┘ same payload

GET https://careers.flatchr.io/vacancy/<slug>/         one ad, same shape
```

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/flatchr.py" \
  jobs --tenant pokawa
```

### What robots.txt says

`flatchr.io` and `careers.flatchr.io` both serve a `robots.txt` that names
**only specific bots** — FacebookBot, bingbot, MJ12bot, UptimeRobot, WordPress,
SemrushBot — and gives them `Disallow: /`. There is **no `User-agent: *` group
at all**, so a client matching none of those groups is unrestricted. (The
marketing site `www.flatchr.io` does have a `*` group, but it only closes
HubSpot preview paths.)

## Configuration

```yaml
boards:
  flatchr:
    enabled: true
    tenants: ["pokawa"]
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `tenants` | yes | The **first label of the careers host** — `pokawa` in `pokawa.flatchr.io`. One employer each |

No login, no account, no API key, and **no `with_detail` option**, because
there is nothing left to fetch.

**There is no tenant resolver, and there cannot be one.**
`careers.flatchr.io/sitemap.xml` looks promising and is not: it is the
*marketing* site's sitemap — 728 URLs of blog posts and product pages, and
**zero vacancies**. So an employer cannot be resolved from a name. Ask the user
for the careers URL, exactly as for `umantis.md` and `taleez.md`; the script
takes `--url` and reads the tenant out of it.

## The ad id and its URL

The ledger key is the 16-character `id`. The URL is built from `slug`:

```
https://careers.flatchr.io/vacancy/<slug>/
```

In the ledger: `flatchr:<id>`.

## What one ad carries

Measured across Pokawa's 32 ads — every field on every ad except where noted:

| Field | Notes |
| :-- | :-- |
| `title`, `reference` | The reference is the employer's own (`EP - CARRE SENART`) |
| `description`, `mission`, `profile` | Three separate HTML bodies, all full text |
| `salary_min` / `salary_max` / `salary_currency` / `salary_period` | Structured, not prose |
| `city`, `location`, `lat`, `lon` | With coordinates |
| `contract`, `metier`, `activity`, `worker_status`, `remote` | Decoded to labels, not ids |
| `education_level`, `experience_years` | `"Bac"`, `2` |
| `code_rome` | `G1603` — the same vocabulary France Travail uses |
| `skills` | A real list, split from a semicolon string |
| `screening_questions` | 26/32 — the questions the employer will ask |
| `end_date` | 4/32, and it is a **contract** end date, not an ad expiry |

`code_rome` is worth noting on its own: it is the one field that lets an ad from
an employer's own ATS be compared to a France Travail search on equal terms.

## Traps

**1. The list items are wrappers, not ads.** `props.data.items` holds
*diffusion* records — `id`, `status`, `created_at` and little else. The ad is
the nested **`vacancy`** object. Read the wrapper instead and you get a board of
rows with a title of `null`, a description of `""` and a location of `None` —
**an employer who fills nothing in, rather than an error.** This cost a
detour: the first tenant sampled had exactly one item, and it was a spontaneous
application whose fields are genuinely all null, which made the wrapper look
like the ad.

**2. `/vacancy/<id>/` is a 404. Only the full `slug` opens an ad.** The slug
begins with the lowercase id (`jAONxpv2GqapPg4Q` →
`jaonxpv2gqappg4q-employe-polyvalent-...`), which makes the id look sufficient.
It is not.

**3. Repeated descriptions are not truncation.** Pokawa's 32 ads share **5
distinct descriptions**, and six in a row measured exactly 1054 characters —
which is what a fixed-length teaser looks like (`apec.md` trap 1). It is not:
lengths across the board run **724 to 1750**, and none ends in an ellipsis. A
franchise reuses one text across many towns. **Check the spread before calling
something truncated**, and check for the ellipsis.

**4. `show_salary` and `show_address` are publication choices.** The payload
carries the figures whether or not the employer chose to display them. Passing
them through regardless would put on the user's screen something the ad does
not show. The card nulls both when the flag is false, and keeps
`salary_public` so the difference between *hidden* and *absent* stays visible.

**5. A salary without its period is meaningless.** `salary: 12.31` is an hourly
rate; the period lives in `mensuality` — `h`, `m` or `y`, and Pokawa's 32 ads
used all three (14 / 10 / 8). Read one without the other and an hourly wage
reads as a monthly one.

**6. `careers.flatchr.io` is a shared host, not a tenant.** A URL like
`careers.flatchr.io/` has no tenant in it, and taking the first host label
yields `careers`, which fetches a page with no payload. The script checks the
`/company/<slug>` path first and refuses the shared hosts by name.

**7. The server compresses regardless.** As on `taleez.md`, the body arrives
gzipped; the script asks for `gzip` and decompresses rather than hoping for
plain text, because the failure mode is a silent regex miss, not an error.

**8. There is no expiry date at all** — no `validThrough`, nothing. That is the
honest option, and it puts Flatchr with Taleez rather than with `meteojob.md`
(+60 days) and `hellowork.md` (+30 days), which publish a formula that only
looks like an expiry. Freshness comes from `created_at` / `updated_at`.

## Applying

Ads carry `screening_questions` and an application form on Flatchr's own site.
**No assisted apply is implemented**, and `cover-letter` never answers a
screening question by guessing — the questions are surfaced so the user answers
them. The plugin does not create accounts and does not fill credential fields.

## Pace, and the note on access

**One request per employer, and that is the whole sweep** — no per-ad reads,
because there is nothing the ad page adds. That makes this the cheapest adapter
here alongside `taleez.md`, and a list of twenty employers is twenty requests.

These are public careers pages read as served, unauthenticated, for one
person's job search. Keep the pace human.
