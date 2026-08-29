# Board adapter — SAP SuccessFactors

An ATS, not a board: one employer per host, no search across employers.
Employers front it with a vanity domain of their own (`jobs.<employer>.ch`,
`www.carrieres-<employer>.com`), so **the host tells you nothing and the path
tells you everything.**

Read by `skills/job-scan/scripts/successfactors.py`.

**Verified 2026-08-28** against `jobs.bcv.ch` (36 postings, read in full), with
the refusal paths cross-checked on `www.carrieres-rolex.com`.

## v1.9.0 said this host needed a browser. It does not.

`shared/ats-open-check.md` recorded that `/search/` is rendered entirely
client-side and lists nothing to a plain fetch. **That is still true, and it is
beside the point:** the widget is backed by a public JSON endpoint that answers
unauthenticated, with no key, no cookie and **no browser**.

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

## The locale is the trap, and it fails silently

**A locale the tenant does not publish returns an EMPTY board with
`error: null`.** On `jobs.bcv.ch`: `fr_FR` → 36 postings, `en_US` → **0**, no
error, no warning. That is indistinguishable from an employer with nothing open.

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
readability rather than relied on.

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
