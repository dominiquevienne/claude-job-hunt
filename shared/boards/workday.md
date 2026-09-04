# Board adapter — Workday

<!-- script: workday.py -->
<!-- verified: 2026-09-02 -->
<!-- countries: * -->

**The tenant's own `robots.txt` lists its career sites — `workday.py sites`
reads them.** Measured on four tenants 2026-09-02: swisscom, novartis, roche
and adobe all publish one `Allow:` line and one `Sitemap:` line per career
site they have opened, plus `Disallow: /refreshFacet/`. The files differ only
in the site names, which is what a per-tenant file should differ in — **no
divergence of policy, so nothing in this file needed correcting**, and the
robots guard from issue #73 is wired anyway because nothing guarantees that
stays true.

```
workday.py sites --host swisscom.wd103.myworkdayjobs.com
→ SwisscomExternalCareers, cablexExternalCareers, FWVFJOBExternal
```

So the `site` coordinate does not have to be guessed: **the tenant names it**.
`resolve` found two of Swisscom's three through HiringCafe.

**Read the list before sweeping it.** Novartis names
`Internal_Careers_for_Acquired_Entities` alongside its public site — a tenant
lists the sites it has opened to crawlers, not the sites a jobseeker should be
reading. Choose, rather than sweeping everything named.

**Re-verified 2026-09-02 on `swisscom.wd103.myworkdayjobs.com`**, and it found
a defect in the ledger key rather than in the fetch.

**The `site` coordinate is case-insensitive at the API and case-preserving in
the URL**, so the same vacancy could arrive under two ledger keys depending on
where the caller got the spelling: `workday.py resolve "Swisscom"` returns
`swisscomexternalcareers`, while the configuration example below and the
employer's own careers URL say `SwisscomExternalCareers`. **Both list the same
ads.** `R-0005958` was recorded twice, once per spelling.

The key now folds the site name; the URL keeps the caller's spelling, because
that is what the employer publishes. This is the Workable shape from the same
day — `resolve` and `list` disagreeing about an identifier — in its quieter
form: nothing errored, the rows simply duplicated.

Workday is an ATS, not a board. Each employer runs its own career site at
`<tenant>.wdN.myworkdayjobs.com/<site>`, backed by a public JSON endpoint that
needs no key, no cookie and no browser.

**Everything here was verified against live boards on 2026-08-28** — Swisscom
(60 postings), Hitachi (2 000), Roche (1 216), Lindt & Sprüngli (293).

## Read this first: what this family of adapters is for

**There is no search across employers.** Like `greenhouse.md`, `lever.md` and
`ashby.md`, this answers *"is my target employer hiring?"*, never *"who is
hiring near me?"* — discovery stays with `hiringcafe.md` and `job-room.md`.

Workday is where the large Swiss employers are, which is why it matters here:
Swisscom, Swiss Life, Roche, Lindt & Sprüngli, Hitachi, most banks and pharma.

## Three coordinates, not one

A Workday board is identified by **host, tenant and site** — and all three must
match or the endpoint answers 404.

```
https://swisscom.wd103.myworkdayjobs.com/SwisscomExternalCareers
        └── host ────────────────────────┘ └── site ───────────┘
        └tenant┘
```

Find them from the employer's name:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/workday.py" resolve "Swisscom"
→ {"host": "swisscom.wd103.myworkdayjobs.com", "tenant": "swisscom", "site": "swisscomexternalcareers", …}
→ {"host": "swisscom.wd103.myworkdayjobs.com", "tenant": "swisscom", "site": "cablexexternalcareers", "company": "cablex"}
```

Two results there, and both are real: **one tenant can run several career
sites**, one per subsidiary. Ask the user which they meant rather than taking
the first.

## Configuration

```yaml
boards:
  workday:
    enabled: true
    employers:
      - host: "swisscom.wd103.myworkdayjobs.com"
        tenant: "swisscom"
        site: "SwisscomExternalCareers"
        location: "Lausanne"     # optional, a facet value THIS employer defines
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `employers` | yes | Each entry needs all three coordinates. Empty list → skipped, and said so |
| `location` | no | Must be one of that board's own facet values — see trap 5 |

## Reading a board

```bash
python3 .../workday.py facets --host … --tenant … --site … --like Lausanne
python3 .../workday.py list   --host … --tenant … --site … --location Switzerland --pages 3
python3 .../workday.py ad     --host … --tenant … --site … --req-id R-0006153
```

```
POST https://<host>/wday/cxs/<tenant>/<site>/jobs
     {"appliedFacets":{},"limit":20,"offset":0,"searchText":""}
GET  https://<host>/wday/cxs/<tenant>/<site><externalPath>      # one posting
```

## The ad id and its URL

The id is the **requisition id** (`R-0006153`, `R0110830`), from
`bulletFields[0]` on a card or `jobReqId` on a posting. In the ledger:
**`workday:<tenant>:<site>:<reqId>`**.

The public URL is `https://<host>/<site><externalPath>`. The site segment is
case-insensitive; the path is not, and it encodes the location and the title, so
**never build it by hand** — take `externalPath` from the payload.

That leaves the usual question: can the URL be rebuilt from the id alone?
**Yes, at the cost of one request.** `searchText: "<reqId>"` returns exactly
that posting — verified on Swisscom (`R-0006153` → total 1) and Hitachi
(`R0110830` → total 1) — and `workday.py ad --req-id` does precisely that.

## Traps

**1. HiringCafe's `board_token` is unusable for Workday.** It looks like
`<tenant>-<wdN>-<site>`, which is tempting, but it is **lowercased and truncated
at 43 characters**: Lindt's real site is `lindtspruengligroupcareers` and the
token holds `lindtspruengligroupcare`. Parsing it yields a 404 on a board that
exists. **`apply_url` is authoritative** and `resolve` reads that instead.

**2. The page size is capped at 20.** `limit: 21` and above are answered with
HTTP 400 — not truncated, refused. Pagination is by `offset`.

**3. `postedOn` is a relative string**, not a date: *"Posted Today"*, *"Posted
30+ Days Ago"*. The absolute `startDate` exists **only on the detail endpoint**.
So a sweep that needs real dates costs one request per posting; a sweep that
only needs an ordering can use the relative text and say so.

**And it measures this listing, not the role.** A re-posted requisition shows
its re-posting age, and nothing in the string says so — which is why
`startDate` is worth the request when the date will be written anywhere. Never
derive a ledger date from `postedOn`: an empty date is a question, a wrong one
is an answer (issue #84).

**4. `remoteType` does not mean what it says.** Swisscom fills it with
`80-100%` and `100%` — a *workload*, not a work mode. It is a free-text field
each employer configures. The adapter records it as `remote_type_raw` and never
derives remote/hybrid from it; judge the work mode from the ad text, per the
commute rule in `shared/scoring-rubric.md`.

**5. The location facet parameter name is per-tenant configuration.** Swisscom
exposes `locations`, holding cities (Basel, Bern, Lausanne, Zurich). Hitachi
exposes `locationCountry`, holding countries (Switzerland, Austria, Belgium).
Hardcoding either one filters nothing on the other board — silently. The
adapter reads the facets first and resolves the user's word against whatever
that employer actually offers; when it matches nothing it prints the available
values rather than sweeping into a void.

**6. `locationsText` is often not a place.** A posting open in several offices
reads `9 Locations` or `3 Locations`. The real location is on the detail
endpoint (`Remote - Zurich, Switzerland`). Never write `9 Locations` into the
ledger as a town, and never apply the commute rule to it.

**7. These boards are large and the pages are small.** Hitachi returns 2 000
postings, Roche 1 216 — at 20 per page that is a hundred requests for one
employer. **Always narrow first**, with a location facet or `searchText`, and
let `--pages` stay small. The script reports `20 returned of 90; raise --pages
to go further` rather than pretending it read everything.

## Applying

Workday hosts the application form, and **it requires the candidate to create an
account** on that employer's site. The plugin never creates accounts and never
fills credential fields. Hand the user the ad URL with their documents and let
them do it — as for any external ATS.

## Pace

One request per page of results, one per posting read in full. A narrowed sweep
of a watchlist is a few dozen. An unnarrowed sweep of Hitachi is a hundred —
which is the reason trap 7 exists.
