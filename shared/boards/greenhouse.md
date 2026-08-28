# Board adapter — Greenhouse

Greenhouse is an ATS, not a board. Each employer has its own job board under a
**tenant token**, and its postings are public JSON — the same feed that renders
that employer's careers page.

**Everything here was verified against the live API on 2026-08-28**, against the
`elastic` board (334 postings).

## Read this first: what this family of adapters is for

**There is no search across employers.** You ask for one tenant at a time. So
Greenhouse, Lever and Ashby answer *"is my target employer hiring?"* — they do
not answer *"who is hiring near me?"*. Discovery stays with `hiringcafe.md` and
`job-room.md`; this is the targeting half of the pair, and the two are
complementary by design.

It follows that **a user with no employer in mind gains nothing here.** Say so
rather than asking them to fill a watchlist they do not have.

## Configuration

```yaml
boards:
  greenhouse:
    enabled: true
    employers: ["elastic", "verkada"]   # tenant tokens, not display names
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `employers` | yes | Tenant tokens. Empty list → the board is skipped and says so |

**The user does not know their own employers' tenant tokens, and should not be
asked to guess.** Resolve each one at setup:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/ats.py" resolve "Elastic"
→ {"provider": "greenhouse", "tenant": "elastic", "company": "Elastic"}
```

`resolve` asks HiringCafe, which records the ATS and tenant of every ad it
indexes — the meta-board paying for itself a second time. When the employer
turns out to be on an ATS with no adapter, it says which one instead of
returning nothing, because *"they use SmartRecruiters"* is an answer and
*"not found"* is not.

## Reading a board

```bash
python3 .../ats.py list --provider greenhouse --tenant elastic \
    --location Switzerland --posted-within-days 30
```

```
GET https://boards-api.greenhouse.io/v1/boards/<tenant>/jobs?content=true
GET https://boards-api.greenhouse.io/v1/boards/<tenant>/jobs/<id>     # one posting
```

An unknown tenant is a clean **404**, which the script reports as such. No key,
no cookie, no browser.

## The ad id and its URL

The id is Greenhouse's numeric `id`. In the ledger the row is
**`greenhouse:<tenant>:<id>`** — the tenant is part of the key because the id
alone cannot rebuild a URL.

```
https://job-boards.greenhouse.io/<tenant>/jobs/<id>
```

That resolves and redirects to the employer's own careers domain. **Do not use
`absolute_url` from the feed**: it points at that custom domain directly
(`jobs.elastic.co/…`) and carries a duplicated `gh_jid` query string, so it is
neither canonical nor stable.

## Traps

**1. `content` is double-encoded HTML.** The JSON string holds
`&lt;div class=&quot;content-intro&quot;&gt;…`, so the entities must be resolved
*before* the tags are stripped. Strip first and you keep the markup as visible
text; unescape once and you feed `<div>` soup to the scorer. The script
unescapes, strips, then unescapes again.

**2. The list endpoint has no description unless you ask.** Without
`?content=true` there is no `content` key at all — not an empty one. A sweep
that forgets the flag looks like it worked and scores every ad on its title.

**3. `location.name` is one free-text string the employer chose.** Elastic
writes `Switzerland`; others write `Zurich, Switzerland`, `EMEA - Remote`, or
`Remote (Europe)`. `--location` is a substring match, and a string the employer
does not use silently keeps nothing. The script says *"the board is not empty —
every posting was filtered out"* rather than reporting zero results as an
answer.

**4. `updated_at` is not the posting date.** Elastic's whole board shares one
`updated_at` (a bulk re-index). `first_published` is the real date and is what
the adapter reads for `posted_within`.

**5. There is no server-side filter of any kind.** The entire board comes back —
334 postings for one employer — and the filtering is local. Keep the employer
list short enough that this stays honest: a watchlist is ten employers, not two
hundred.

## Applying

Greenhouse hosts the application form itself, at the ad URL plus `#app`. **The
form is not filled by this plugin.** Hand the user the URL and their documents,
as for any external ATS.

## Pace

One request per employer per sweep, one per ad read. A ten-employer watchlist
is ten requests — this is the cheapest board in the plugin.
