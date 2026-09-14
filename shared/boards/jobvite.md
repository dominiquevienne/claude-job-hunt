# Board adapter — Jobvite (a family of employer career sites on one host, one tenant at a time): the search page paged «Next» after «Next», its «1-50 of N» as the witness — and the «View All» page, which is not the inventory

<!-- verified: 2026-09-14 -->

<!-- hosts: jobs.jobvite.com -->
<!-- script: jobvite.py -->
<!-- host-forms: jobs.jobvite.com -->
<!-- host-forms-basis: read — `jobvite.py:58` (`HOST = "jobs.jobvite.com"`, the only host the script builds a URL on); the tenant is `--tenant` (`jobvite.py:245`, REQUIRED, no default), normalised by `norm_tenant()` (`jobvite.py:129`) to the path segment of the employer's careers URL; every route is `https://jobs.jobvite.com/<tenant>/…`, so guard and fetch agree · 2026-09-14 -->
<!-- countries: * -->
<!-- content: measured · **`jobs.jobvite.com/nutanix`: 224 emitted over 5 pages of 50 by `jobvite.py list --tenant nutanix --all` (04:31–04:32 UTC), the site states «1-50 of 224» — equal; a location on 224 of 224, 51 of them «N Locations», California 36, India 28, Singapore 11; `/nutanix/jobs` («View All») shows 97 rows and states no count; one job read (Systems Sales Engineer, Req.Num. 32278, Sales, two locations, the description without its leading comment). `pragmaticplay` (ARRISE): 78 rows on `/jobs`. `zscaler`, recorded in this repository's notes, is no longer a tenant: HTTP 200 on `www.jobvite.com/support/job-seeker-support/?invalid=1`, exit 3** · 2026-09-14 -->
<!-- witness: the site's own «A-B of N» in `jv-pagination-text` on the search page, read on the first page and printed beside the emitted count («N emitted over P page(s), site states N — equal», exit 6 on a gap); a tenant whose search page states no count is said so, not compared; the default walk is bounded (`--pages 10`) and says so, `--all` follows «Next» to the end · 2026-09-14 -->

**An ATS family read one employer at a time — the tenant named by the
user, never guessed** (`--tenant`, the path segment of the employer's own
careers URL, as `icims.py`, `eightfold.py`, `avature.py` and `taleo.py`
take `--host`). Every Jobvite board lives on **one host,
`jobs.jobvite.com`**, at `/<tenant>`; the guard is taken on that host and
the exact path. Issue #454 (#406 families; #291).

## Two lists, and only one is complete

`/<tenant>/jobs` is the «View All» page: jobs grouped under department
headings, no pager, no count — **and on the tenant read it carried 97
rows where the search page states 224.** A walk of that page would have
emitted 97 with nothing to compare against, and 97 looks like an
inventory. The route is **`/<tenant>/search?q=&l=`**: `table.jv-job-list`
rows (`td.jv-job-list-name a[href=/<tenant>/job/<id>]`,
`td.jv-job-list-location` — a city, or `div.jv-meta` «N Locations», kept
as text with the number beside it), a footer `jv-pagination-text`
«1-50 of 224» — the count the site states — and a `jv-pagination-next`
link (`/<tenant>/search/?p=1`, zero-based) followed until it is gone,
deduplicating on the id.

```
224 emitted over 5 page(s), site states 224 (jobs.jobvite.com/nutanix) — equal    (04:31–04:32 UTC)
```

## A tenant the host does not know is not a 404

The host answers **HTTP 200** and lands on the editor's support page
(`www.jobvite.com/support/job-seeker-support/?invalid=1`). `zscaler`,
found in this repository's own notes, lands there on 2026-09-14 — the
employer has moved on. The adapter reads the final URL and exits 3, so a
tenant that has left never reads as an empty board.

## The job page

`/<tenant>/job/<id>`: `h2.jv-header` the title, `p.jv-job-detail-meta` the
department, the locations and «Req.Num.: N» separated by
`jv-inline-separator`, `div.jv-job-detail-description` the employer's own
HTML — which may open with an **HTML comment holding an older text**
(`<!-- removed ===== … removed=====--->`, 1 711 characters on the job
read): comments are dropped before the text is read, so the withdrawn
text is never emitted as the current one. `/apply` is never followed.

## The rules

`jobs.jobvite.com/robots.txt` answers 404 — no rules, certain; read on
the exact path before every request. 3 s own spacing.

## What is withheld

Addresses and phone numbers in the prose are replaced (`[e-mail
withheld]`, `[phone withheld]` — nine digits or more). `country` is null:
a family adapter serves every country its tenants hire in, and the
location text says which.

## Invocation

```
jobvite.py list --tenant nutanix              # 10 pages of 50, bounded and said so
jobvite.py list --tenant nutanix --all        # «Next» to the end, compared with «A-B of N»
jobvite.py ad --url https://jobs.jobvite.com/nutanix/job/oxVCAfwo
```

Exits: 2 broken (no tenant, a malformed URL) · 3 gone (404, a tenant the
host does not know, a job page without its header) · 6 partial (a walk
short of the stated count, HTTP ≠ 200) · 7 refused by the rules · 8
rules undecidable.
