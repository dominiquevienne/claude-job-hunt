# Board adapter — Personio (DACH ATS)

Personio is the applicant-tracking system most German, Austrian and **Swiss**
SMEs run their careers page on. Each tenant publishes a **documented XML feed**
of its open positions, with the full description, and it needs nothing.

It sits alongside `umantis.md`, `join.md` and `solique.md` as an **employer's
own careers page** rather than a national board — the kind of source that
answers *"is this employer hiring?"* instead of *"who is hiring near me?"*.

**Everything here was verified against a live tenant on 2026-09-01.**

## Access

```
GET https://<tenant>.jobs.personio.de/xml     → every open position
GET https://<tenant>.jobs.personio.com/xml    → the same bytes
https://<tenant>.jobs.personio.de/job/<id>    → the ad, for a human
```

**No browser, no account, no key.** Not even a published key as on
`arbeitsagentur.md`, and no window as on the country boards: **one request
returns the employer's whole board, descriptions included** — the same shape as
`workable.md` and `flatchr.md`.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/personio.py" \
  jobs --tenant ottonova
```

### What could and could not be established about `robots.txt`

`robots.txt` on a **tenant** host is a `404` — none is published, so nothing is
disallowed, and the tenant host is all this adapter reads.

`www.personio.de/robots.txt` and `www.personio.com/robots.txt` answered **HTTP
429 on every attempt**. **The marketing host's robots.txt could not be read**,
and that is recorded as not established rather than assumed in either
direction. If someone reads it, it supersedes this paragraph.

*(The 429 is worth knowing for its own sake: Personio throttles per host. A
sweep across many tenants should be paced, and the adapter waits five seconds
and retries rather than hammering.)*

## Configuration

```yaml
boards:
  personio:
    enabled: true
    tenants:
      - "ottonova"
      - "someemployer.jobs.personio.de"
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `tenants` | yes | Tenant name or careers hostname. **Ask the user for the URL** |
| `office` | no | Keep positions in one office |
| `language` | **no — read trap 1** | |

**There is no tenant directory.** Like `umantis.md`, `taleez.md` and
`flatchr.md`, Personio publishes no cross-tenant search, and a tenant that does
not exist answers the careers app's own **Next.js 404 page**, not an error. Ask
for the careers URL and never guess.

## Traps

**1. `?language=` empties the ads without emptying the board.**

| Feed | Positions | With a description | Median chars |
| :-- | --: | --: | --: |
| `/xml` | 7 | **7** | 4 556 |
| `/xml?language=de` | 7 | **7** | 4 556 |
| `/xml?language=en` | 7 | **1** | 0 |
| `/xml?language=fr` | 7 | **0** | 0 |

Same count, same ids, HTTP 200, valid XML — and on `fr` **not one of the seven
ads carries a word of its own description**.

The parameter does not filter the board and does not translate it. It serves
whatever translation the employer happened to enter, and returns the position
with an empty body when there is none. Nothing in the response says so.

**It is the worst shape this failure takes**, because the request that
triggers it is a reasonable one: anybody who asks for the language they read
receives a full-looking board of empty ads — right count, right titles, right
employer, no text — and `cover-letter` is then asked to write from nothing.

So the adapter reads the **default** feed, and when a language is requested it
fetches both and **refuses** to report one whose text has gone:

```
$ personio.py jobs --tenant ottonova --language fr
ERROR: --language fr returned 7 positions and only 0 of them carry any
description (median 0 characters). The default feed returns 7 positions with
7 described (median 4544).
```

*(My first reading of this was wrong and is worth recording: the `fr` feed is
4.9 KB against 89 KB, so it looks like **fewer ads**. It is not — it is the
same seven ads with the text removed. Counting the positions rather than the
bytes is what separated the two.)*

**2. Issue #55's CDATA, in a new element.**

```xml
<value><![CDATA[<span style="…">ottonova - wir sind eine digitale …</span>]]></value>
```

Every `<value>` in `<jobDescriptions>` is CDATA-wrapped, so a
`<value>([^<]*)</value>` extractor returns **nothing at all** from a perfectly
valid feed.

It is the same wrapper `hays-fr.md` found in `<loc>` — different element,
different vendor, different country. Two independent sightings is the argument
for the tolerant pattern being the house default rather than a per-board fix,
which is what v1.56.2 made it.

**3. A position can be posted in more than one office, in a sibling element.**

```xml
<office>München</office>
<additionalOffices>
    <office>Köln</office>
</additionalOffices>
```

Two of seven measured. Reading `<office>` alone puts the candidate in the wrong
city on an ad that also runs where they live — the same shape as `ashby.md`'s
`secondaryLocations` and `softy.md`'s multi-town ads. `locations_count` and
`additional_offices` carry it, and the run reports how many were multi-site.

## What the record carries

Measured on one tenant's seven positions.

| Field | Coverage | Note |
| :-- | --: | :-- |
| `id`, `name` | 7/7 | |
| `jobDescriptions` | **7/7** | Median **4 556 characters**, and **already split into the employer's own named sections** |
| `subcompany` | 7/7 | The legal entity — on a group tenant this is not the tenant name |
| `office` | 7/7 | Plus `additionalOffices` on 2 |
| `department`, `recruitingCategory` | 7/7 | |
| `employmentType`, `seniority`, `schedule` | 7/7 | `permanent` / `entry-level` / `full-time` |
| `occupation`, `occupationCategory` | 7/7 | |
| `createdAt` | 7/7 | A real per-ad timestamp |
| `keywords` | 1/7 | |

**The description arrives pre-split** — `DEIN TEAM`, `DEIN WIRKUNGSBEREICH`,
`DEIN PROFIL`, `WORAUF DU DICH FREUEN DARFST` — with the employer's own
headings. Only `join.md` does the same, and there the section names are fixed;
here they are whatever the employer typed, so they are carried as data rather
than mapped to a schema. The joined text is emitted as well, because a cover
letter wants the whole thing and a scorer wants the requirements.

**There is no salary and no closing date** anywhere in the feed.

## Verification

```bash
S=skills/job-scan/scripts/personio.py
python3 $S check --tenant ottonova      # positions, description coverage, languages
python3 $S jobs  --tenant ottonova
python3 $S jobs  --tenant ottonova --language fr   # → must ERROR, not return 7 empty ads
```

The language guard is the one to re-check after any change: its failure mode is
seven correct-looking ads with nothing in them.
