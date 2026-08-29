# Board adapter — Solique

An ATS, not a board: one employer per tenant, no search across employers. Public
HTML and JSON, unauthenticated, **no key, no cookie, no browser**.

Read by `skills/job-scan/scripts/solique.py`.

**Verified 2026-08-29** against six live tenants — `iss`, `ktzh`, `manor`,
`ottosag`, `vebegoag`, `united-machining`.

## It does not have one architecture. It has three.

And which one a tenant uses is invisible until you ask. The script tries them in
order and always reports which answered.

| Route | Shape | Tenants seen | Completeness |
| :-- | :-- | :-- | :-- |
| `<tenant>/<lang>/ajax/` | JSON | `iss` (105 ads) | **complete** |
| `<tenant>/<lang>/api/v1/data/` | JSON | `ktzh` (177 ads) | **complete** |
| `<tenant>/` | HTML | `manor`, `vebegoag`, `united-machining`, `ottosag` | **sometimes truncated — see trap 2** |

**All six tenants are reachable**, which is the finding that made this adapter
worth building: the first look suggested only the server-rendered ones worked,
because `/iss/` and `/ktzh/` answer `200` with **zero ad links** and look like
empty boards. They are AngularJS shells, and their data is one request away.

**The language segment is required on the JSON routes.** `/iss/ajax/` is a 404;
`/iss/de/ajax/` is the board. Getting that wrong reads as "this tenant has no
JSON route" and silently falls through to the truncated HTML one.

## Traps

**1. The two JSON routes share no field names.** They are not one contract with
two paths:

| | `ajax/` (iss) | `api/v1/data/` (ktzh) |
| :-- | :-- | :-- |
| title | `jobTitle` (string) | `title` (**object** `{value, id}`) |
| date | `publicDate` | `dateModified` |
| place | `locationFreeText`, `zip`, `region` | `location` (**object**) |
| text | `fullTextSearch` | `htmlContent` |

**ktzh wraps most fields as `{"value": …, "id": …}` and iss does not.** Emitting
them raw puts `{'value': 'Aufseher/in', 'id': …}` in the title column, which is
what a first implementation here did. Only `link` is common to both, which is
why the id comes from it.

`startDate` on the `ajax/` route is a **unix timestamp**, not a date string —
read as one it lands in 1970.

**2. The JSON is served with a UTF-8 BOM.** `json.loads` rejects it outright —
*"Unexpected UTF-8 BOM"*. Decode with `utf-8-sig`; this is required, not
defensive.

**3. The HTML route can be truncated, and nothing pages it.** `ottosag` states
**157 Stellen** on its own page and serves **25 ad links**. Every offset and
page parameter tried — `?page=2`, `?p=2`, `?start=25`, `?offset=25`,
`?limit=200`, `?seite=2`, `/page/2`, `?showall=1` — either repeats the same rows
or returns an error page. The shortfall is real and permanent.

The other three HTML tenants state 10 and serve 10, so the route is **not**
always partial. The script compares what it read against the stated total and
says *"25 read of 157 stated — this board is TRUNCATED and cannot be paged"*
only when the two disagree. Never report the count as the size of the board when
it does.

**4. An unknown ad id does not always answer 404.** `iss`, `manor` and `ottosag`
return `404`; **`ktzh` returns `200` with its own landing page** — 1 112 bytes
against 23 196 for a real ad. A status-only check therefore reports a
non-existent ad as **open**, which is what this adapter did on its first run.

**The control is the tenant's landing page.** Fetch `<tenant>/` once and compare
its `<title>` to the ad page's. Equal means the id does not resolve, whatever
the status code was. `ad` and `check` both do this.

**5. A `JobPosting` block is not a test.** It is present on `iss`, `ktzh`,
`manor` and `vebegoag`, absent on `ottosag` and `united-machining`, and never on
`Microsites/showPublication/` pages. Its presence describes the employer's
configuration, not the ad — the card reports it as `has_jobposting` and never
decides on it. See `shared/ats-open-check.md`, where Solique is also an
open/closed oracle.

## The ledger

```
solique:<tenant>:<id>            e.g. solique:iss:4061853
```

The tenant is lowercased in the key, and the ad URL rebuilds from the pair:
`https://live.solique.ch/<tenant>/job/details/<id>/`.

## Where tenants come from

There is no directory. HiringCafe indexes no Solique ad; **job-room does** —
24 ads across these six tenants in a 2 800-ad sweep (`job-room.md`). A tenant
name is the path segment of any of its ad URLs, and it is case-insensitive
(`ktzh` and `KTZH` both answer).

## Applying

The employer's own flow, behind account creation. **The plugin does not create
accounts and does not fill credential fields** — hand the user the ad URL and
their documents.

## Pace

One `list` per tenant is one to three requests. The JSON routes return the whole
board in a single call, descriptions included, so there is nothing to page.
