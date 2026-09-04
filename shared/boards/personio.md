# Board adapter — Personio (DACH ATS)

<!-- hosts: jobs.personio.de -->
<!-- script: personio.py -->
<!-- countries: DE AT CH -->

Personio is the applicant-tracking system most German, Austrian and **Swiss**
SMEs run their careers page on. Each tenant publishes a **documented XML feed**
of its open positions, with the full description, and it needs nothing.

It sits alongside `umantis.md`, `join.md` and `solique.md` as an **employer's
own careers page** rather than a national board — the kind of source that
answers *"is this employer hiring?"* instead of *"who is hiring near me?"*.

**Measured on four tenants — 2026-09-01, extended 2026-09-02.**

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

| Tenant | default | `?language=de` | `?language=en` | `?language=fr` |
| :-- | --: | --: | --: | --: |
| ottonova | **7/7** | 7/7 | 1/7 | **0/7** |
| autarcenergy | **11/12** | — | 3/12 | **0/12** |
| dieseo-gmbh | **64/69** | — | 12/69 | **0/69** |
| **merantix** | **1/16** | 1/16 | **15/16** | 0/16 |

*(positions carrying any description, out of positions returned — the counts
are identical in every column)*

Same count, same ids, HTTP 200, valid XML — and on `fr` **not one ad on any of
the four tenants carries a word of its own description**.

The parameter does not filter the board and does not translate it. It serves
whatever translation the employer happened to enter, and returns the position
with an empty body when there is none. Nothing in the response says so.

**And the default feed is not reliably the full one.** On `merantix` the
default carries text on **1 of 16** and English on **15** — the reverse of the
other three. An adapter that trusts the default and refuses every language
would hand that tenant's user fifteen empty ads *and* reject the feed that
works.

**This was found by testing a second tenant**, and it is the case in
`shared/boards/README.md` § *An ATS-family adapter is verified against two
tenants*: the first version of this adapter treated the default as
authoritative, which is correct on ottonova and wrong on merantix.

**It is the worst shape this failure takes**, because the request that
triggers it is a reasonable one: anybody who asks for the language they read
receives a full-looking board of empty ads — right count, right titles, right
employer, no text — and `cover-letter` is then asked to write from nothing.

So the check is **symmetric**: whichever feed was asked for, if it is mostly
empty the alternatives are measured and the caller is told which one carries
the ads — never handed the empty one.

```
$ personio.py jobs --tenant merantix.jobs.personio.com
ERROR: (default) returned 16 positions and only 1 carry any description:
    (default)         16 positions,   1 with text, median 0
    --language de     16 positions,   1 with text, median 0
    --language en     16 positions,  15 with text, median 3361
**--language en carries the text on this tenant** — 15 of 16.
```

When no feed carries text, it says that instead, rather than naming a winner
that is only marginally less empty.

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
