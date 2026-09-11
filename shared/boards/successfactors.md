# Board adapter — SAP SuccessFactors

<!-- hosts: per-tenant -->
<!-- script: successfactors.py -->
<!-- verified: 2026-09-11 -->
<!-- countries: * -->

An ATS, not a board: one employer per host, no search across employers.
Employers front it with a vanity domain of their own (`jobs.<employer>.ch`,
`www.carrieres-<employer>.com`), so **the host tells you nothing and the path
tells you everything.**

Read by `skills/job-scan/scripts/successfactors.py`.

**Verified 2026-08-28** against `jobs.bcv.ch` (36 postings, read in full), with
the refusal paths cross-checked on `www.carrieres-rolex.com`.

## Two routes, and the rules file chooses — #202, 2026-09-11

**`/services/`, the JSON service and until today this adapter's only route, is
refused by 3 tenants of 3** — `Disallow: /services/` to `User-agent: *` on
`jobs.fr.ch`, `jobs.bcv.ch` and `jobs.sicpa.com`, measured with
`_robots.allowed()` path by path on 2026-09-11 11:35 UTC:

| host | `/services/recruiting/v1/jobs` | `/search/` | `/job/…` |
| :-- | :-- | :-- | :-- |
| `jobs.fr.ch` | **False** (`/services/`) | True | True |
| `jobs.bcv.ch` | **False** (`/services/`) | True | True |
| `jobs.sicpa.com` | **False** (`/services/`) | True | True |

*Three tenants of the three configured in one workspace — not a property of
the platform proved, and not an isolated case either.* Every one of them
answered `list` with exit 7 and zero rows, **a zero indistinguishable from an
employer with nothing open**, and the État de Fribourg publishes 133 vacancies.

**So the adapter now has a second route, and the rules file picks between
them, path by path** — `route_for()`, and the chosen route is printed on every
run:

```
api    /services/ permitted                 → POST the JSON service, as before
html   /services/ refused, /search/ + /job/ permitted
                                            → GET /search/?q=&startrow=N   the job tiles
                                              GET /job/<slug>/<id>/        one JobPosting (microdata)
none   every route refused                  → exit 7 · rules unreadable → exit 8
```

**And the HTML route returns THREE states, not two** — this is the point that
decides the value of the fix:

| what `/search/` served | what `list` says | exit |
| :-- | :-- | :-- |
| `n` tiles | `n` cards, and «`n` emitted, page states `N`» | 0 |
| **no tile, no stated total** | **INDETERMINATE — this tenant does not serve its list to a plain client, and `/services/` is refused to it: a browser route to document** | **8** |
| no tile, the page states «0 offres» | a real zero | 0 |

**Measured 2026-09-11 11:39–11:40 UTC, the same invocation on the three:**

```
list --host jobs.fr.ch    --pages 6   exit 0   133 emitted, page states 133; 133 tiles on 6 pages (25+25+25+25+25+8), 0 repeated
list --host jobs.bcv.ch   --pages 3   exit 8   /search/ returned no job tile — INDETERMINATE
list --host jobs.sicpa.com --pages 3  exit 8   /search/ returned no job tile — INDETERMINATE
```

*Before, at 11:35 UTC on `main` 5ffd40b: all three exit 7, zero rows.*
`--with-description` on `jobs.fr.ch` reads each vacancy's `JobPosting`
**microdata** (no JSON-LD on this platform): 25 of 25 with a description and
a `datePosted`, one request per vacancy.

**Two traps the first run fell into, both now in the pattern's comment:** a
tenant's brand sub-site prefixes the vacancy path — `/Police_Cantonale/job/…`,
2 tiles of 25 on page 3, so a pattern anchored on `/job/` read 23 of the 25
the page itself declared (`data-record-returned="25"`); and the label span
beside each field carries `aria-describedby="…-section-city-value"`, so a
pattern without the `id="` anchor read «Ville» as the city.

### «Rendered entirely client-side» was measured on one tenant and written as the platform

v1.9.0 recorded, and this card repeated, that `/search/` *is rendered entirely
client-side and lists nothing to a plain fetch*. **That is a property of the
TENANT, dated** — `jobs.bcv.ch` serves a 66 kB shell with 0 `/job/` links
(2026-09-09, and again 2026-09-11); `jobs.sicpa.com` the same (2026-09-11);
`jobs.fr.ch` serves 25 tiles a page and states «133 offres» (378 kB,
2026-09-11). *The sentence was true where it was measured and served as the
reason for having only the route that is refused.* `shared/ats-open-check.md`
carried the same sentence and is corrected with this card.

The JSON service, where its path is permitted, remains the better route: it
answers unauthenticated, with no key, no cookie and **no browser**.

```
POST https://<host>/services/recruiting/v1/jobs
{"locale": "fr_FR", "pageNumber": 0, "keywords": "analyste"}
```

It was found by watching what the page actually requests, after five guessed
endpoint shapes had all returned 404 or 302. The field names came from the
widget's own bundle: `locale`, `pageNumber`, `keywords`, `location`, `sortBy`,
`facetFilters`, `brand`, `categoryId`. **`keyword` singular is silently
ignored** — it returns the unfiltered board, which is how the first attempt
concluded the parameters did nothing.

- `pageNumber` is **0-indexed**, **10 postings per page**, fixed. `limit` and
  `offset` are ignored. Past the last page the service returns zero rows and no
  error.
- `totalJobs` is reliable and is what the script reports against.


## The open/closed check reads a `JobPosting` block, not a title

**The tell, the two URL shapes and the numbers live in
`shared/ats-open-check.md`** — one place, so a corrected figure cannot survive
in a second copy. In short: a served vacancy carries exactly one
`itemtype="…JobPosting"`, an id that does not resolve carries none and lands on
the portal's `/errorpage/`, **and the vacancy URL has two shapes that differ by
tenant** — reading only the first reported a live SICPA advert as unresolvable.

`successfactors.py check --host … --id …` implements it, and **the slug is
decorative**: the id alone rebuilds the URL. Issue #87.

## The locale is the trap, and it fails silently

**A locale the tenant does not publish returns an EMPTY board with
`error: null`.** On `jobs.bcv.ch`: `fr_FR` → 36 postings, `en_US` → **0**, no
error, no warning. That is indistinguishable from an employer with nothing open.

**Re-tested 2026-09-02, still silent, and now with the byte counts:** `fr_FR`
answered 200 with 4 079 bytes and `totalJobs: 32`; `en_US` and `de_DE` both
answered **200 with 15 bytes — `{"totalJobs":0}` — and `error: null`**. A
fifteen-byte success is the whole warning this service gives, and it is not
one.

**Never guess it.** The tenant declares it in its own `/search/` page, and the
script reads it from there:

```
$ successfactors.py locale --host jobs.bcv.ch
{"host": "jobs.bcv.ch", "locale": "fr_FR"}
```

`list` does this on its own when `--locale` is omitted, and when a run comes
back empty it re-reads the locale and says *"zero jobs for locale 'en_US', and
this tenant publishes 'fr_FR'"* rather than reporting an empty board.

Each posting also carries `supportedLocales`, which confirms it — but only once
you already have a posting.

## A tenant that refuses says so, and that is not an empty board

`www.carrieres-rolex.com` answers the same endpoint with an explicit refusal —
`{"error": {"code": "Error", "message": "Error retrieving jobs"}}`, and on a
later run **HTTP 401**. The endpoint exists on every SuccessFactors host; **it
is not enabled for every tenant.** The script refuses with its own exit code and
says to read that tenant in a browser instead — never *"they are not hiring"*.

## Traps

**1. `location` takes a facet value, not a town.** `location: "Lausanne"`
returns **0** on a Lausanne bank whose postings all say `Lausanne`. It is not
free text. Filter locally on `location_raw` instead, and never pass a town here.

**2. `filter1`…`filter5` are per-tenant configuration**, exactly as on Workday.
On BCV, `filter1` is a region (*Lausanne*, *Broye*, *Chablais*, and *Non-défini*
on two postings) and `filter5` a business area. Another tenant may map them to
anything. They are recorded raw — `location_raw`, `category_raw` — and never
renamed into a location the commute rule would trust.

**3. The slug is decorative, and the API returns it HTML-escaped.**
`Responsable-d&apos;applications-...` comes straight out of `unifiedUrlTitle`.
`/job/x/<id>-<locale>` answers `200` just as well, so the slug is unescaped for
readability rather than relied on — confirmed on a second host, where
`/job/Zzz-Not-A-Job/<real id>/` serves the whole vacancy.

**But the rest of that URL is not decorative, and it differs by tenant.** BCV
serves `/job/<slug>/<id>-<locale>`; SICPA serves `/job/<slug>/<id>/` and sends
the locale form to `/errorpage/`. **Try both** — reading only the first
reported a live SICPA vacancy as unresolvable. `shared/ats-open-check.md`
carries the measurement (issue #87).

**4. Reading the description needs the vacancy page, not the API.** The search
payload carries no description at all. The vacancy page **is** server-rendered —
unlike `/search/` — and its text sits in `.joblayouttoken` (4 216 characters on
the ad measured). `--with-description` therefore costs one request per posting.

## Is it still open? Use a control, not a rule

`ats-open-check.md` says the job title is present in `<title>` if and only if
the requisition resolves. True, and **a first implementation still gets it
wrong**: the empty slot is not empty text. A live requisition reads

```
IT Business Analyst - domaine Opérations de Marché Détails du poste | BCV
```

and an invented id reads `  Détails du poste | BCV` — the chrome is still there.
Testing that "something precedes the separator" passes an invented id, which is
exactly what this adapter did on its first run. The chrome phrase is per-tenant
**and** per-locale, so it cannot be matched either.

**One control request settles it without knowing any of that:** fetch an id that
cannot exist on the same tenant, and compare. Identical page → the requisition
does not resolve.

```
$ successfactors.py check --host jobs.bcv.ch --id 31130   # exit 0, open
$ successfactors.py check --host jobs.bcv.ch --id 99999   # exit 1, unverified
```

> **A genuinely *closed* requisition has still never been observed.** Only the
> invented-id state was tested, here and in v1.9.0. So *"does not resolve"* is
> reported as **unverified**, never as *closed* — the affirmative direction is
> the only sound one on this ATS.

## The ledger

```
successfactors:<host>:<id>        e.g. successfactors:jobs.bcv.ch:31130
```

The host is part of the key: one board per employer, and the id alone cannot
rebuild a URL.

## Applying

The employer's own SuccessFactors flow, behind account creation. **The plugin
does not create accounts and does not fill credential fields.** One tenant was
also recorded (2026-08-20) as opening its portal *only* in the tab where the
session was authenticated — hand the user the URL and their documents.

## Pace

One `list` per employer is a handful of POSTs. `--with-description` multiplies
it by the number of postings kept; filter first, read second.

**Re-exercised 2026-09-08**: `list --host jobs.bcv.ch` **exits 7** —
`jobs.bcv.ch` refuses `/services/recruiting/v1/jobs` to our token. *A refusal on
one tenant is a refusal on that tenant*, and this card's other hosts were not
asked.
