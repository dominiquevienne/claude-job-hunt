# Board adapter — Ashby

<!-- verified: 2026-09-11 -->

<!-- hosts: jobs.ashbyhq.com -->
<!-- host-forms: api.ashbyhq.com -->
<!-- host-forms-basis: read — `ats.py:268` builds it as a literal. The `hosts:` line above names `jobs.ashbyhq.com`, which no code path fetches · 2026-09-07 -->
<!-- script: ats.py -->
<!-- countries: * -->
<!-- content: measured · per-tenant feed, not a board: `list --provider ashby --tenant docker` returns 65 postings, 65 of 65 kept, one request; the host still answers HTTP 401 to /robots.txt, which since #201 is an absence of rules (`allowed: True`, `certain: False`) · 2026-09-11 11:28 UTC -->
<!-- witness: none found — the posting-api feed states no total; «65 of 65 kept» compares the feed with itself, and one tenant is not the host · 2026-09-11 -->

## REOPENED 2026-09-11 — a 401 on the rules file is an absence of rules (#201)

**Owner's decision of 2026-09-09, verbatim:** *«&nbsp;quand le robots.txt nous
renvoie une 401, il faut considérer qu'il s'agit d'une absence de règles et
donc, une porte ouverte au scan&nbsp;».* **`api.ashbyhq.com` is the case that
produced it**: an API gateway that demands a token on every path and makes no
exception for `/robots.txt`. *There is no rules file behind that 401 — there is
an authentication in front of everything.* The verdict below was **correct on
the rule of its day and is reopened by a change of rule, not of host** — the
host answers exactly as it did on 2026-09-07.

```
# 2026-09-11 11:28 UTC — the same call, before and after #201
main 2ce1048   ats.py list --provider ashby --tenant docker   exit 7, « Not swept »
after          ats.py list --provider ashby --tenant docker   exit 0, 65 postings, 65 of 65 kept

allowed("api.ashbyhq.com", "/posting-api/job-board/docker")
    allowed True · kind None · certain False
    no rules were read — the host answered HTTP 401 and the state is `unauthenticated`.
```

**`certain` is False and stays so**: nothing was read. A 404 is knowledge; a
401 is ignorance, and ignorance does not forbid. **The scope is 401 and only
401** — 403, 429 and 451 still refuse, and `WhichStatusMeansWhat` pins each
code to its state by name.

## STOPPED 2026-09-07 — the host this adapter reads refused us *(superseded above)*

**Measured 2026-09-07, under the rule of that day — 401 was `refused`:**

```
allowed("api.ashbyhq.com", "/posting-api/job-board/<tenant>")
    allowed False · kind host-closed · certain True
    HTTP 401 — the host replied, and the reply was no.
```

**`ats.py --provider ashby` exits 7 and sends nothing.** The other four
providers are unaffected: `boards-api.greenhouse.io`, `api.lever.co`,
`apply.workable.com` and `<tenant>.teamtailor.com` are all permitted, measured
the same minute.

**This adapter read that host on every run since the provider was added**, and
no exemption covered it — checked both ways. `shared/robots-policy.md` names
the four keyed-API adapters that skip the guard and `ats` is not among them;
the owner's #100 decision needs a door explicitly closed **and** a keyed API,
and this endpoint asks for no key.

### The `hosts:` line pointed at the wrong host, and that is why nobody saw it

**This card declared `jobs.ashbyhq.com`. The script fetches
`api.ashbyhq.com`.** One permits and the other refuses:

```
jobs.ashbyhq.com   allowed True    <- what the card named
api.ashbyhq.com    allowed False   <- what the script asks for
```

**So an audit that reads `hosts:` and consults the guard comes back green**,
and its green says nothing about what the adapter does. *That is #173 in its
sharpest form: not a card that is out of date, but a card that is accurate
about a host nobody fetches.* Both hosts are declared now, with which is which.

**And what let the code itself hide it was a true, incomplete enumeration.**
`smartrecruiters_gate`'s docstring lists four verified hosts and every word of
it is still correct; Ashby is the one of the seven it does not mention, and it
is the one that refuses. *Nothing distinguishes a true partial list from an
exhaustive one* — which that same docstring says four lines earlier, about
SmartRecruiters.

**The guard now sits at `fetch()`**, the choke point every provider passes
through, rather than beside two of them. A provider added tomorrow is covered
by having been written.

**Re-verified 2026-09-02**: an unknown job board still answers a clean **404**.

Ashby is an ATS, not a board. Each employer publishes its job board as public
JSON under a **tenant token**.

**Everything here was verified against the live API on 2026-08-28**, against
the `cohere` board (146 listed postings).

## Read this first: what this family of adapters is for

**There is no search across employers.** You ask for one tenant at a time.
Ashby, Greenhouse and Lever answer *"is my target employer hiring?"*; discovery
stays with `hiringcafe.md` and `job-room.md`. A user with no employer in mind
gains nothing here — say so rather than asking them to fill an empty watchlist.

## Configuration

```yaml
boards:
  ashby:
    enabled: true
    employers: ["cohere", "ontic"]   # tenant tokens, not display names
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `employers` | yes | Tenant tokens. Empty list → the board is skipped and says so |

Resolve each token at setup rather than guessing it:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/ats.py" resolve "Cohere"
→ {"provider": "ashby", "tenant": "cohere", "company": "Cohere"}
```

## Reading a board

```bash
python3 .../ats.py list --provider ashby --tenant cohere --location London
```

```
GET https://api.ashbyhq.com/posting-api/job-board/<tenant>?includeCompensation=true
```

An unknown tenant is a clean **404**. No key, no cookie, no browser. There is no
per-posting endpoint: reading one ad means fetching the board and selecting the
id, which the script does — so a posting that has been filled is reported as
gone rather than returning stale text.

## The ad id and its URL

The id is Ashby's UUID. In the ledger: **`ashby:<tenant>:<uuid>`**, the full
UUID.

Take `jobUrl` and `applyUrl` from the feed. They follow
`https://jobs.ashbyhq.com/<tenant>/<uuid>` and `…/application`, but the feed's
own values are what the adapter records.

## Traps

**1. `isListed: false` means the employer pulled it from the public board.**
Those entries are still in the feed. Publishing one to the user sends them to a
posting the employer deliberately unlisted; the adapter drops them.

**2. `location` is one city, `secondaryLocations` holds the rest.** Cohere's
"Senior HR Business Partner" reads `New York` in `location` and carries London,
the United States and Toronto in `secondaryLocations`. Filtering on `location`
alone would have hidden it from a London search. The adapter matches against
the union.

**3. `isRemote` is often `true` on multi-city roles**, which is a statement
about the role, not a promise that any country works. Combined with trap 2, a
posting can be `isRemote: true`, listed in six cities, and still expect
attendance in one of them. Read the ad text before treating it as remote — the
commute rule in `shared/scoring-rubric.md` applies to what the ad actually says.

**4. `publishedAt` can be very old on a live posting.** Cohere's "Member of
Technical Staff, Modeling" was published in November 2024 and is still listed.
Do not discard on age, and do not present `posted_within` as freshness here.

**5. `compensation` is usually an empty shell.** Every Cohere posting returned
`compensationTierSummary: null`, `compensationTiers: []`. The
`includeCompensation=true` flag is worth passing because it costs nothing, but
**an empty compensation object is not evidence the role pays nothing** and must
never reach `shared/salary-estimate.md` as a figure.

**6. `descriptionPlain` is present without the compensation flag** — verified.
Use it rather than stripping `descriptionHtml`.

**7. There is no server-side filter.** The whole board comes back and the
filtering is local, so `--location` matches the employer's own free text. A
string they do not use keeps nothing, and the script says the board was not
empty rather than reporting zero as an answer.

## Applying

Ashby hosts the form at `applyUrl`. **The plugin does not fill it.** Hand the
user that URL with their documents.

## Pace

One request per employer per sweep, and one per ad read (there being no
per-posting endpoint). A ten-employer watchlist is ten requests.

## The `resolve` example above is refused, and correctly — 2026-09-08

**`ats.py resolve` searches through HiringCafe, and
`hiringcafe.com/robots.txt` refuses that URL shape to `User-agent: *`** —
`Disallow: /*?searchState=*`, measured 2026-09-03, issue #123. **The adapter
exits 7 and makes no request.**

*So the invocation printed above no longer runs, and the reason is doctrinal
rather than a defect.* **`list` and `ad` are unaffected** — re-exercised
2026-09-08, figures below. To resolve an employer by hand meanwhile, open its
careers page and read the host, tenant and site out of the URL; the adapter
prints that advice itself.

**`list --provider ashby --tenant cohere` exited 7 on 2026-09-08**: `api.ashbyhq.com`
answers **HTTP 401 on its rules file**, which was `host-closed` that day.
**Since #201 (2026-09-11) that 401 is an absence of rules and `list` runs** —
see the REOPENED section at the top; `docker` returned 65 postings.
