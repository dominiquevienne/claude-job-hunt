# Board adapter — ss.ge (Georgia, classifieds)

<!-- verified: 2026-09-03 -->

Georgia's largest classifieds site. Its jobs section holds **1 705 live
advertisements**, and this adapter finds every one of them **without fetching a
single advertisement page.**

**That is not a limitation worked around. It is the shape of the site**, and
the two reasons are the operator's, not ours.

## Three hosts, three different `robots.txt` files

| Host | Size | What it says |
| :-- | --: | :-- |
| `ss.ge` | 478 B | a **BOM**, a **malformed first line**, and it **disallows `/en/jobs` and `/ru/jobs`** |
| `home.ss.ge` | 105 B | **a different file — the job refusals are not in it**; declares `ss.ge/sitemap.xml` |
| `jobs.ss.ge` | 62 B | **`Allow: /`**; declares `ss.ge/sitemap-jobs.xml` |

**The host every request is redirected to has the more permissive file.**
`shared/robots-policy.md`'s *test the apex and the `www` separately* has never
bitten this hard: these are not two files differing by a `Sitemap:` line, they
are **three files with different refusals**, and which one governs depends on
which host the redirect chain leaves you on.

**The apex's first line is not a directive at all:**

```
﻿sitemap: Disallow: /sitemap.xml
```

A `Sitemap:` whose value is a `Disallow:`. Read as either, it is nothing — and
the real sitemap index is at the path that line mentions, found by asking for
it rather than by parsing that.

## The jobs board is a subdomain, and the file is what said so

```
ss.ge/jobs  →  ss.ge/ka/jobs  →  jobs.ss.ge/ka/
```

Neither a path prefix nor a query parameter. **So the apex's refusal of
`/en/jobs` is a refusal of a redirect stub**, and the file that governs the
board itself says `Allow: /`.

## And the board is behind a Cloudflare challenge

`jobs.ss.ge/ka/` answers **`403` with *"Just a moment…"***, as does
`home.ss.ge`. **Permission is open and the door is shut** — *a `robots.txt`
verdict is not an access verdict*, in the direction that costs.

**A challenge that asks for a click is a stop.** `ssge.py ad` therefore **does
not fetch**: it returns the id and the slug, says why there is nothing else,
exits `6`, and hands the URL to the person, who has a browser and a click.

## What is readable, and it is most of what matters

`jobs.ss.ge/robots.txt` declares **`https://ss.ge/sitemap-jobs.xml`** — on the
apex, which is **not** challenged, and **absent from the apex's own sitemap
index**, whose 21 files are all real estate. **Reading the file for discovery
found what the index omitted** (#74).

| Family | Count | What it is |
| :-- | --: | :-- |
| `/ka/ads/<n>` | 20 | the advertisements — **1 705 distinct from 1 740 `<loc>`** |
| `/en/ads/<n>` | 20 | the same ads, same ids, in English |
| `/{ka,en}/jobs/sitemap-listing-<n>.xml` | 16 | **search-filter URLs, not advertisements** |

Counting all 56 would report a board several times its size — the arithmetic
that inflated Jobstore and hr.ge.

**The two languages carry the same ids**, so the ledger key is
`ss.ge:<id>` with no language in it.

## Which paths are refused, exactly

**8 of the 56 sub-sitemaps are under a path the apex refuses by name** — the
**English *listing*** families at `/en/jobs/sitemap-listing-N.xml`. The English
***advertisement*** families are `/en/ads/<n>` and are **not** refused.

**That distinction was wrong in the first draft of this adapter**, which said
"the English families are refused" — true of eight files, false of twenty, and
it read exactly like diligence. **Both the refusal and the permission are read
off the file; neither is inferred from a language.**

**And the jobs sitemap advertises files under the refused prefix.** That is a
conflict between two of the operator's own files, and **a `Sitemap:` line is
not a permission**: the refusal governs, and `get()` refuses those URLs before
any request.

## Zero-shaped answers

**1. Three `robots.txt` files with different refusals**, the permissive one on
the host you are redirected to.

**2. A first line that is two directives glued together**, behind a BOM.

**3. `Allow: /` on a host that answers `403`.**

**4. 56 sub-sitemaps of which 16 are search pages.**

**5. A `--limit` run reporting the limit as duplicates.** The first version
compared a file's `<loc>` against the ids it emitted **after the limit had cut
it short**, and printed the difference as *"299 URLs were duplicates"*. A false
number that reads like care. It now says it stopped, and counts nothing.

## Configuration

```yaml
boards:
  ssge:
    enabled: true
    lang: ka
    delay: 0.4
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `lang` | no | `ka` by default; `en` is the same ads under the same ids |
| `delay` | no | Between sitemap files, default 0.4 s |

No credentials, no login. **A browser is needed to read an advertisement and
never to find one** — and the browser is the user's, because what stands in the
way is a challenge addressed to a person.

## Applying

Through the ad URL, in the user's own browser — which is also where the
description is read.

## Pace

21 requests for the whole board: one sitemap index and twenty family files,
3.4 kB and ~40 kB each. **No advertisement page is ever requested by this
adapter.**

## Verification

```bash
S=skills/job-scan/scripts/ssge.py
python3 $S families                 # 56 sub-sitemaps, 20/20/16
python3 $S sitemap --limit 5
python3 $S sitemap                  # 1 705 from 1 740 <loc>
python3 $S ad --url "https://jobs.ss.ge/ka/details/molare-88215005"   # exits 6
```
