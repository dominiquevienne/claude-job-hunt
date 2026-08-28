# Board adapter — Lever

Lever is an ATS, not a board. Each employer has its own postings feed under a
**tenant token**, public as JSON.

**Everything here was verified against the live API on 2026-08-28**, against
`caseware` (56 postings, US host) and `coinspaid` (33, EU host).

## Read this first: what this family of adapters is for

**There is no search across employers.** You ask for one tenant at a time. Lever,
Greenhouse and Ashby answer *"is my target employer hiring?"*; discovery stays
with `hiringcafe.md` and `job-room.md`. A user with no employer in mind gains
nothing here — say so rather than asking them to fill an empty watchlist.

## Configuration

```yaml
boards:
  lever:
    enabled: true
    employers: ["caseware", "coinspaid"]   # tenant tokens, not display names
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `employers` | yes | Tenant tokens. Empty list → the board is skipped and says so |

Resolve each token at setup rather than guessing it:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/ats.py" resolve "Caseware"
→ {"provider": "lever", "tenant": "caseware", "company": "Caseware"}
```

## Reading a board

```bash
python3 .../ats.py list --provider lever --tenant caseware --location Netherlands
```

```
GET https://api.lever.co/v0/postings/<tenant>?mode=json        # US
GET https://api.eu.lever.co/v0/postings/<tenant>?mode=json     # EU
```

`?limit=N` is honoured. No key, no cookie, no browser.

## The two hosts are disjoint, and this is the trap that matters

**A tenant lives on exactly one host, and the other returns 404.** Verified both
ways: `caseware` is 200 on `api.lever.co` and **404** on `api.eu.lever.co`;
`coinspaid` is the reverse. There is no redirect and no hint — the wrong host
looks exactly like an employer who does not exist.

So the adapter tries `api.lever.co` first, then `api.eu.lever.co`, and only
reports "no such board" when **both** answer 404. Never conclude an employer is
absent from one host alone.

## The ad id and its URL

The id is Lever's UUID. In the ledger: **`lever:<tenant>:<uuid>`**, the full
UUID, never shortened.

**Take the URL from the feed, do not build it.** `hostedUrl` and `applyUrl` are
provided per posting and already carry the right host — `jobs.lever.co/…` or
`jobs.eu.lever.co/…`. Building `jobs.lever.co/<tenant>/<id>` by hand produces a
dead link for every EU tenant.

## Traps

**1. `createdAt` is epoch milliseconds**, not a date string. Read as seconds it
lands in 1970 and every ad looks ancient; the adapter converts it.

**2. `createdAt` is the creation date, and it can be old.** One live Caseware
posting was created in February 2024 and is still open. That is not stale data,
it is a long-running vacancy — do not discard on age alone, and do not report
`posted_within` as a freshness guarantee on this board.

**3. `categories.location` is one string, `allLocations` is the full list.** A
posting reachable in three cities carries only the first in `location`. The
adapter matches against both, joined.

**4. There is no server-side filter.** The whole board comes back and the
filtering is local, so `--location` matches whatever free text the employer
typed — `Apeldoorn, Netherlands`, `Remote - European Region`. A string the
employer does not use keeps nothing, and the script says the board was not
empty rather than reporting zero as an answer.

**5. `descriptionPlain` exists — use it.** Lever ships a plain-text description
alongside the HTML one. There is no reason to strip tags on this board, and
doing so loses the paragraph breaks the plain version keeps.

**6. `commitment` carries contract detail worth reading.** Values seen:
`Full-time`, `Full Time - 12 Month Contract (NL)`. That parenthesis is the
difference between a permanent role and a one-year contract, and it is not
repeated anywhere else in the payload.

## Applying

Lever hosts the form at `applyUrl`. **The plugin does not fill it.** Hand the
user that URL with their documents.

## Pace

One request per employer per sweep. A watchlist of ten employers is ten
requests, or twenty if half of them turn out to be on the EU host.
