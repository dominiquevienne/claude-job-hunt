# Board adapter — Pinpoint (ATS)

One employer at a time, by tenant. Pinpoint is a UK-origin ATS, and **the fifth
most common provider in a 360-card HiringCafe sample** — 24 ads, ahead of ADP,
Taleo, UltiPro and Avature. Each tenant publishes its board as public JSON.

**Measured on 684 postings across five tenants on 2026-09-01.**

## Access

```
GET https://<tenant>.pinpointhq.com/postings.json   → the publications
GET https://<tenant>.pinpointhq.com/jobs.json       → the requisitions
https://<tenant>.pinpointhq.com/en/postings/<uuid>  → the ad, for a human
```

**No browser, no account, no key**, and one request returns the whole board
with descriptions.

`robots.txt` closes `/mydata`, `/admin` and `/companies`. Neither JSON path is
disallowed, and no crawler or AI agent is named.

*(`/api/v1/jobs` also exists and answers **401 — `X-API-KEY header not
provided`**. That is the tenant's own admin API, not a door for this adapter,
and the 403/401 handler says so rather than letting it read as a broken key.)*

## The two endpoints are two entities, and their ids never overlap

| Tenant | `postings.json` | `jobs.json` | Ids in common |
| :-- | --: | --: | --: |
| menzies | 52 | 43 | **0** |
| davies | 276 | 251 | **0** |
| nfamilyclub | 281 | 281 | **1** |

A **posting** is a publication; a **job** is the requisition behind it. Each
posting carries `job.id`, and all 52 of menzies' resolve into `jobs.json`.
**Fifteen jobs across the five tenants are published more than once, one of
them seven times.**

The `nfamilyclub` row is the dangerous one: **281 against 281, and still
disjoint**. Equal counts are exactly what would convince someone the two
endpoints are two views of one list. They are not, and nothing in either
response says so — a ledger keyed on `jobs.json` ids with an ad URL built from
`postings.json` would describe different objects.

**This adapter reads `postings.json`**, because that is what a candidate
applies to: the URL, the location and the compensation all hang off the
posting.

### Three identifiers per ad, which is one more than it looks

```
id            389422                                  ← numeric, the ledger key
url  /en/postings/68f11550-4d80-4a08-a057-c8f6f804761f ← a UUID
job.id        401509                                  ← the requisition
```

All three are emitted. `job_id` is **not** a unique key for an ad, for the
reason above.

## `province` is not a province

Across 684 postings the field holds, verbatim:

```
London 149 · United Kingdom 96 · Maharashtra 68 · Bolton 44 ·
England 38 · Surrey 32 · uk
```

A city, a country, an Indian state, a town, a nation, a county, and a lowercase
country code — **in one field, across five tenants**. It is `hays-fr.md`'s
`addressLocality == addressRegion` problem with the *levels* mixed as well as
the granularity: there the field held a town or a department or a region, all
of them places; here it also holds countries.

It is emitted as `province_freetext` and is never a key. `city` (680 of 684)
and `postal_code` (548) mean what they say.

## Where this board gets it right

Worth recording, because after six adapters in a row that got it wrong the
contrast is the useful part.

**`compensation_visible` actually tracks the figure.** True on 337 of 684, a
figure on 333, and only **4** visible-with-no-amount.

| Board | Flag says yes | Figure present |
| :-- | --: | --: |
| **Pinpoint** | **337** | **333** |
| `turijobs.md` | 27 | 2 |
| `platsbanken.md` | 300 *(pay type)* | 0 |

**`workplace_type` is a real three-value enum** — `onsite` 366, `hybrid` 259,
`remote` 59 — where `recruitee.md` has three overlapping booleans that
misclassify 51 of 238 if read as exclusive, and `empleate.md`'s equivalent is
one constant on 92% of the board.

## What the record carries

| Field | Coverage | Note |
| :-- | --: | :-- |
| `title`, `description` | 684/684 | Description median **1 649 characters** |
| `key_responsibilities` | **684/684** | Median 656 — a separate, always-present field |
| `skills_knowledge_expertise` | 365/684 | |
| `benefits` | 248/684 | |
| `location.city` | 680/684 | |
| `location.postal_code` | **548/684** | |
| `location.street_address` | 400/684 | |
| `employment_type` | 684/684 | `permanent_full_time` 472, `flexible` 94, … |
| `compensation_*` | 333/684 | **299 real ranges, 34 a single point** written into a range's shape |
| `deadline_at` | 83/684 | Real when present |

**The description arrives in four named parts** and `key_responsibilities` is
on **every** posting — which is what `shared/scoring-rubric.md` actually reads.
Only `join.md`, `personio.md` and `recruitee.md` also pre-separate it, and none
of them fills the requirements part on 100% of ads.

`compensation` also exists as free text and is formatted inconsistently —
`32,000`, `£26,230 / year` — so the structured fields are the ones used.

## Finding tenants, and a lesson about doing it by URL

There is no directory. `pinpoint.py tenants --country GB` reads HiringCafe's
cards through the **`ats` / `ats_tenant` fields the HiringCafe adapter already
extracts** — not by matching `pinpointhq.com` in the apply URL.

The difference is not cosmetic. On one draw of 120 cards:

| Method | Tenants found |
| :-- | --: |
| Matching the apply URL | **5** |
| Reading `ats_tenant` | **23** |

Some Pinpoint tenants serve their board on their own domain, so the apply URL
never says `pinpointhq`. `mountainwarehouse` (187 postings), `breedongroup`
(97) and `blackpooltransport` (3) are all real boards a URL matcher misses.

**Re-deriving what an upstream adapter already labelled is how you under-count
a family by four fifths.** The first version of this adapter did exactly that.

It remains a hint rather than a directory: HiringCafe indexes a fraction of
Pinpoint. And the command distinguishes *"no Pinpoint ads in this draw"* from
*"the sweep failed"* — it checks HiringCafe's exit code and says which it got,
because an empty tenant list from a failed sweep reads exactly like a provider
nobody uses.

## Verification

```bash
S=skills/job-scan/scripts/pinpoint.py
python3 $S tenants --country GB --pages 3 --plugin-root .
python3 $S jobs --tenant menzies         # 52 postings, 43 requisitions
python3 $S jobs --tenant nfamilyclub     # 281 of 281 state a salary
python3 $S jobs --tenant notarealtenantzzz   # → must name the tenant, not report zero
```
