# Board adapter — Oracle Taleo Enterprise (a family of employer career sections, one tenant at a time): the list read by the page's own ajax pager and keyed by the slot names the page declares, `nbElements` as the witness

<!-- verified: 2026-09-14 -->

<!-- hosts: dubaiholding.taleo.net -->
<!-- script: taleo.py -->
<!-- host-forms: {host} -->
<!-- host-forms-basis: read — `taleo.py:332`; `--host` is REQUIRED with no default, `norm_host()` (`taleo.py:161`) normalises that same argument, `--section` (`taleo.py:333`, `norm_section()` at `taleo.py:168`) is required too, and every route is `https://{host}/careersection/{section}/…`, so guard and fetch agree; the tenant read on 2026-09-14 is in `hosts:` · 2026-09-14 -->
<!-- countries: * -->
<!-- content: measured · **`dubaiholding.taleo.net/careersection/jum_ext_quickapply` (Jumeirah): 32 emitted over 2 pages by `taleo.py list --host dubaiholding.taleo.net --section jum_ext_quickapply --all` (04:21 UTC), `listRequisition.nbElements` 32, the page prints «(32 jobs found)» — equal; a location on 32 of 32, a posting date on 32, Bahrain 20 and Oman 12; one job read (Sales Manager, 2600001H — title, location, job field, organisation, the description as text). Six guessed tenant hosts (emerson, tetrapak, mattel, cn, bbraun, tdbank) do not resolve on 2026-09-14** · 2026-09-14 -->
<!-- witness: `listRequisition.nbElements` in the field section of every `joblist.ajax` answer — the count the portal itself states, printed beside the emitted count («N emitted over P page(s), portal states N — equal», exit 6 on a gap), and the page's «(N jobs found)» printed beside it when the two differ; a portal whose answer carries no `nbElements` is said to «state no count», not compared; the default walk is bounded (`--pages 10`) and says so, `--all` reads to the end · 2026-09-14 -->

**An ATS family read one employer at a time — the tenant AND its career
section named by the user, never guessed** (`--host --section`, as
`icims.py`, `eightfold.py` and `avature.py` take `--host`). A Taleo
Enterprise section lives at
`https://<tenant>.taleo.net/careersection/<section>/joblist.ftl`; the
section is in the employer's own careers URL, and `/careersection/` alone
lands on an administrative table of contents (`smartorg/…/toc.jsf`), not
on a list. Issue #453 (#406 families; #291). **Not Oracle Recruiting
Cloud** (`oraclecloud.md`, `<pod>.oraclecloud.com`, a JSON API) and **not
Taleo Business Edition** (`tbe.taleo.net/tbe/…`, another product, another
URL shape — no tenant named, not read).

## The page is a data island, and it declares its own slot names

The list page ships no table of jobs: its rows are one `!|!`-separated
string in a hidden field (`initialHistory`), and the page's JavaScript
fills a template row by POSITION. The meaning of each position is
declared beside it — the inline script's `listRequisition._hlid` names
the k-th slot of every row (`reqlistitem.title`,
`reqlistitem.contestnumber`, `reqlistitem.basiclocations`,
`reqlistitem.postingdate`, `reqlistitem.organization`,
`reqlistitem.jobschedule`, `reqlistitem.no` for the plumbing). The
adapter reads that array and zips it with the values, exactly as the page
does: **a tenant that shows other columns changes nothing** — the row
length and the names move together. Values are `escape()`-encoded (`%26`
an ampersand, `%u2019` a curly quote), a colon is written `\:`, an HTML
value starts with `!*!`.

## The pager is an ajax POST, and the first page is read by it too

Pages come from `POST joblist.ajax` with the pager component's
parameters (`ftlinterfaceid=requisitionListInterface`,
`ftlcompid=rlPager`, `ftlcompclass=PagerComponent`,
`rlPager.currentPage=N`) plus the page's `ftlpageid` and `ftlhistory` —
no session, no cookie beyond `locale`. The answer has four `!$!`
sections; the fourth carries **`listRequisition.nbElements` — the count
the portal states**, and `listRequisition.size`, the page size (25 on the
tenant read). **The island of the HTML page and the ajax pages sort
differently**: on the tenant read, 5 of the 25 ids on the page's island
came back on ajax page 2, so a walk that mixed the two counted 27 of 32.
The adapter reads every page, the first included, by the POST — 25 + 7,
union 32. A POST whose body encodes a space as `+` is answered **HTTP
500 «A system error has occurred»**; `%20` is served (`quote_via=quote`,
and the test asserts the byte string).

```
32 emitted over 2 page(s), portal states 32 (dubaiholding.taleo.net/careersection/jum_ext_quickapply) — equal    (04:21 UTC)
```

## The job page

`jobdetail.ftl?job=<contest>&lang=en` is the same island under
`descRequisition`, keyed the same way: `reqlistitem.title`,
`.contestnumber`, `.description`, `.qualification`, `.primarylocation`,
`.jobfield`, `.organization`, `.joblevel`, `.postingdate` — the tenant's
configuration decides which are filled. The description is the
employer's own HTML, reduced to text. «Apply», «Apply by Email» and the
job cart are never followed.

## The rules, per tenant

`dubaiholding.taleo.net/robots.txt` answers 404 — no rules, certain; each
tenant's file is its own and is read on the exact path before every
request. 3 s own spacing per host.

## The family has shrunk, and a tenant is named

Six hosts guessed from memory of long-standing Taleo customers —
`emerson`, `tetrapak`, `mattel`, `cn`, `bbraun`, `tdbank` `.taleo.net` —
do not resolve on 2026-09-14: the employers have moved on. The tenant
comes from the user's own careers URL; the one read here was found in a
job-board redirect (`founditgulf.com` → Jumeirah's section).

## What is withheld

Addresses and phone numbers in the prose are replaced (`[e-mail
withheld]`, `[phone withheld]` — nine digits or more). `country` is null:
a family adapter serves every country its tenants hire in, and the
location text says which.

## Invocation

```
taleo.py list --host dubaiholding.taleo.net --section jum_ext_quickapply          # 10 pages, bounded and said so
taleo.py list --host dubaiholding.taleo.net --section jum_ext_quickapply --all    # to the end, compared with nbElements
taleo.py ad --url 'https://dubaiholding.taleo.net/careersection/jum_ext_quickapply/jobdetail.ftl?job=2600001H&lang=en'
```

Exits: 2 broken (no host or section, a malformed URL) · 3 gone (404, no
such section, an island without a job) · 6 partial (a walk short of the
stated count, HTTP ≠ 200, a page that is not a Taleo careersection) · 7
refused by the rules · 8 rules undecidable.
