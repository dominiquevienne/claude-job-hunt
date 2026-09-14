# Board adapter — Avature (a family of employer careers portals, one tenant at a time): the `SearchJobs` list followed «Next» after «Next», the portal's «of N» when it states one — Koch's states none, and the card says so

<!-- verified: 2026-09-14 -->

<!-- hosts: koch.avature.net, careers.ibm.com -->
<!-- script: avature.py -->
<!-- host-forms: {host} -->
<!-- host-forms-basis: read — `avature.py:271`; `--host` is REQUIRED with no default, `norm_host()` (`avature.py:137`) normalises that same argument and every route is built from it and from the locale path the portal's own redirect names, so guard and fetch agree; the tenant read on 2026-09-14 is in `hosts:`, with IBM's front door that answered nothing · 2026-09-14 -->
<!-- countries: * -->
<!-- content: measured · **`koch.avature.net/en_US/careers`: 2 002 emitted over 334 pages of 6 by `avature.py list --host koch.avature.net --all` (03:43–04:03 UTC), then **HTTP 406 at `jobOffset=2004`** — the portal's pager is capped at 2 000 and the inventory beyond is not reachable by this route (exit 6, said so); the portal states no count (`list-controls__text` empty on every page), so the walk is not compared and says so; `jobRecordsPerPage` not honoured (50 asked, 6 served); the RSS feed caps at 20; one job read (Sr Machinist, Molex, ChengDu — 4 fields and the body). `careers.ibm.com` (IBM's tenant `ibmglobal`): HTTP 202, 0 bytes to the declared client on `/en_US/careers` — a different front door, not read** · 2026-09-14 -->
<!-- witness: the portal's own «Showing A-B of N» in `list-controls__text` when it carries one, read on the first page and printed beside the emitted count — «N emitted over P page(s), portal states N — equal», exit 6 on a gap; when the portal states no count the walk says «the portal states no count; the pager's end was reached / NOT reached, not compared» and exits 0 only at the pager's end; the default walk is bounded (`--pages 10`) and says so, `--all` follows «Next» to the end · 2026-09-14 -->

**An ATS family read one employer at a time — the tenant named by the
user, never guessed** (`--host`, as for `icims.py` and `eightfold.py`).
An Avature portal lives at `https://<tenant>.avature.net/<locale>/careers`
(Koch: `/en_US/careers`, read from where `/careers` redirects when
`--path` is not given); its list is **`<path>/SearchJobs/?jobRecordsPerPage=&jobOffset=`**
— HTML, `article.article--result` cards (the title's link
`JobDetail/<slug>/<id>`, a subtitle that is the company or unit, labelled
«Location» and «Job Number») — and its only forward control is a «Next >>»
link, which the adapter follows until it is gone, deduplicating on the
id. **The page size is the portal's** (6 on Koch; 50 asked, 6 served).
Issue #450 (#406 families; #291 — bloc C had read the editor's
`www.avature.com`, which is not a board).

## The pager is capped, and the walk says so

«Next» after «Next» reached `jobOffset=2004` and the portal answered
**HTTP 406** — 2 002 distinct jobs over 334 pages (Molex 894,
Georgia-Pacific 498, Koch 102, Guardian Glass 98…), a location on 2 001.
The list stops at 2 000 by the portal's rule; the inventory beyond is not
reachable by this route; the adapter prints the bound and exits 6 — a
bound, not an end, and not a count.

## The tenant read, and the witness it does not give

Koch's portal fills `list-controls__text` with nothing on every page: **it
states no count**. Some Avature portals write «Showing 1-6 of N results»
there — then N is the witness and the walk is compared. On a portal that
states none, the honest line is the one printed: *«N emitted over P
page(s) — the portal states no count; the pager's end was reached, not
compared»* — and the exit is 0 only when «Next» ran out. The portal's RSS
(`SearchJobs/feed/`) answered 20 items — a capped feed, not a count, not
read by the adapter.

```
2 002 emitted over 334 pages of 6 by `avature.py list --host koch.avature.net --all` (03:43–04:03 UTC), then **HTTP 406 at `jobOffset=2004`** — the portal's pager is capped at 2 000 and the inventory beyond is not reachable by this route (exit 6, said so)
```

## The job page

`JobDetail/<slug>/<id>`: the banner's title (`banner__text__title` — the
page's `<h1>` is the portal's name), `article.article--details` with
labelled fields («Location(s)», «Company», «Career Field», «Job Number»)
and one unlabelled field that is the employer's own HTML («Your Job»,
«What You Will Do», «Who You Are», …) — reduced to text. The «Apply now»
route (`/careers/Login`, an account) is never followed.

## The rules, per tenant

`koch.avature.net/robots.txt` allows `/*/careers` in writing, `certain:
True`; each tenant's file is its own and is read on the exact path before
every request. 3 s own spacing per host. **`careers.ibm.com`** — IBM's
tenant `ibmglobal.avature.net` redirects there — answered **202 with 0
bytes** on `/en_US/careers` to the declared client on 2026-09-14: a front
door that serves nothing to a plain client, a browser candidate for that
tenant, not read here.

## What is withheld

Addresses and phone numbers in the prose are replaced (`[e-mail
withheld]`, `[phone withheld]` — nine digits or more). `country` is null:
a family adapter serves every country its tenants hire in, and the
location text says which.

## Invocation

```
avature.py list --host koch.avature.net                 # 10 pages of 6, bounded and said so
avature.py list --host koch.avature.net --all           # «Next» to the end; the portal states no count, said so
avature.py list --host <tenant>.avature.net --path /de_DE/careers --all
avature.py ad --url https://koch.avature.net/en_US/careers/JobDetail/Sr-Machinist/194367
```

Exits: 2 broken (no host, a malformed URL) · 3 gone (404, no details
article) · 6 partial (a walk short of a stated count, HTTP ≠ 200, a
portal path that cannot be read) · 7 refused by the rules · 8 rules
undecidable.
