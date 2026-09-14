# Board adapter — Eightfold (a family of employer careers sites, one tenant at a time): the JSON route the tenant's own page calls, `count` as the count it states — 602 emitted, 602 stated on `bayer.eightfold.ai`; a second shape (PCSX) named, not read

<!-- verified: 2026-09-14 -->

<!-- hosts: bayer.eightfold.ai, talent.bayer.com, micron.eightfold.ai -->
<!-- script: eightfold.py -->
<!-- host-forms: {host} -->
<!-- host-forms-basis: read — `eightfold.py:262`; `--host` is REQUIRED with no default, `norm_host()` (`eightfold.py:123`) normalises that same argument and every route is built from it, so guard and fetch agree; the two tenants read on 2026-09-14 are in `hosts:` with Bayer's vanity name · 2026-09-14 -->
<!-- countries: * -->
<!-- content: measured · **`bayer.eightfold.ai`: 602 emitted over 61 pages of 10 by `eightfold.py list --host bayer.eightfold.ai --all` (03:25–03:28 UTC), the tenant states `count` 602 — equal; every position with a location and a date; one position read through the vanity host `talent.bayer.com` (3 764 characters of description). `micron.eightfold.ai`: the careers page served, the v2 route answers 403 «Not authorized for PCSX» — a second variant, named and not read** · 2026-09-14 -->
<!-- witness: the tenant's own `count` in the first JSON answer, printed beside the emitted count — «N emitted over P page(s), tenant states N (<host>, domain <employer>) — equal», exit 6 on a gap; the default walk is bounded (`--pages 10` of 10) and says so, `--all` walks to the count · 2026-09-14 -->

**An ATS family, read one employer at a time — the employer named by the
user, never guessed.** An employer on Eightfold serves
`https://<tenant>.eightfold.ai/careers`, often under a vanity name too
(`talent.bayer.com` is `bayer.eightfold.ai`); the page fills its list from
**`GET /api/apply/v2/jobs?domain=<employer domain>&start=<n>&num=10`** —
JSON with **`count`** and `positions[]` — and reads one position from
**`GET /api/apply/v2/jobs/<id>?domain=…`** (the same record plus the
employer's `job_description` and its apply redirect). The `domain` the
routes need is the employer's own (`bayer.com`), read from the careers
page's config when `--domain` is not given. `num` is capped at 10 by the
server (100 asked, 10 answered). No key, no cookie, no browser. Issue #451
(#406 families; #291).

## The two tenants read

| tenant | `/careers` | the v2 route | on 2026-09-14 |
| :-- | :-- | :-- | :-- |
| `bayer.eightfold.ai` (= `talent.bayer.com`) | 200, 194 KB | `count` 602 | **602 emitted over 61 pages — equal**; onsite 583, hybrid 17, remote 2; a location and a creation date on every row; one position read through the vanity host |
| `micron.eightfold.ai` | 200, 254 KB, «Careers at Micron Technology» | **403 `{"message": "Not authorized for PCSX"}`** | the PCSX variant: its list is drawn by the bundle and its data route is not named in clear on the page — a second shape to measure, not a closed employer; the adapter says so and exits 7 |

The employer's own domain is the key the routes want, not the tenant's
name: `domain=bayer.com` on `bayer.eightfold.ai`, and the same on
`talent.bayer.com`.

## The record

`id` (the position's, 15 digits — the ledger key is `eightfold:<host>:<id>`),
`ats_job_id` (the employer's own reference), the URL the tenant declares
canonical (`canonicalPositionUrl`, on the vanity host when there is one),
title, `locations` (as the employer writes them — «Muttenz,Basel-Country,
Switzerland»), department, business unit, `work_location` (onsite / hybrid
/ remote_local), locale, `posted` and `updated` from the epoch stamps. `ad`
adds `description` (the employer's HTML, reduced to text) and
`apply_is_external`. **`country` is null**: a family adapter serves every
country its tenants hire in, and the location text says which.

## The rules, per tenant

Each tenant's `robots.txt` is its own and is read on the exact path
before every request — `bayer.eightfold.ai` refuses nothing under
`/careers` or `/api/apply` (`certain: True`); the editor's `eightfold.ai`
refuses `/wp-admin/` and is not a board. 3 s own spacing per host.

## What is withheld

Addresses and phone numbers in the description are replaced (`[e-mail
withheld]`, `[phone withheld]` — nine digits or more). The apply route
(`apply_redirect_url`, the tenant's own form) is never followed.

## Invocation

```
eightfold.py list --host bayer.eightfold.ai --all             # 602 over 61 pages, tenant states 602 — equal (2026-09-14, 3 min)
eightfold.py list --host talent.bayer.com --pages 2           # the vanity name, the same tenant
eightfold.py list --host <tenant>.eightfold.ai --q python     # the route's own `query`
eightfold.py ad --url https://talent.bayer.com/careers/job/562949978473187
```

Exits: 2 broken (no host, a malformed URL) · 3 gone (404, no position in
the answer) · 6 partial (a walk short of `count`, HTTP ≠ 200, a page that
names no `domain=`) · 7 refused by the rules, or a PCSX tenant · 8 rules
undecidable.
