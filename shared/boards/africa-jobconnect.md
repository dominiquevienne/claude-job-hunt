# Board measurement — JobConnect Africa (`africa-jobconnect.com`): **the app's call is READ, and it splits in two — a PUBLIC enumerator that needs no credential and serves 565 advert ids, and a CONTENT route that answers `401` without the app's own public key.** The enumerator addresses a host that does NOT EXIST, the live site serves no advert over HTTP, and no `route:` line is written here because establishing the content route is refused by the measuring session's own permissions — an INDETERMINATE whose cause is OURS, not the host's; no adapter yet

<!-- verified: 2026-11-07 -->

<!-- hosts: africa-jobconnect.com -->
<!-- script: none -->
<!-- countries: CI SN ML -->
<!-- content: measured · **the rules file NAMES the data route, so the bundle was not where this was settled: `africa-jobconnect.com/robots.txt` (200, 3 012 B) declares `Host: https://jobconnect-africa.com` — a DIFFERENT name, the two words inverted, and `NXDOMAIN` on BOTH 1.1.1.1 and 8.8.8.8 — plus two sitemaps, one of them on `jrluzolgzjajckpcjywu.supabase.co`. Its `Disallow: /api/` to group `*` is READ and `certain`, so borne 1 closes THAT path to every route, and the data route is not there. PUBLIC ENUMERATOR, no credential at all: `https://jrluzolgzjajckpcjywu.supabase.co/functions/v1/sitemap` → 200, 240 195 B, md5 `e92eae754c33`, 1 184 `<loc>` ALL DISTINCT and ALL on the dead host — 565 `/jobs/<uuid>`, 483 `/jobs?<facette>`, 125 `/emploi/<ville|secteur|contrat|metier|diaspora>` and 11 sign-up or landing paths. CONTENT ROUTE, same host, rules `absent` and `certain` so open: `/rest/v1/jobs` → **401** «No API key found in request», `/functions/v1/search-jobs-web` → **401** `UNAUTHORIZED_NO_AUTH_HEADER`; the bundle (3 480 213 B) names 24 `.from()` tables and 24 edge functions, and `sitemap` is the only one deployed without JWT verification. The live site serves NO advert over HTTP: `/jobs/e6fbe0d9-…` returns the shell, 29-byte body, 0 `<a>`, 0 `JobPosting`, and a `title`/`og:` that are the SITE's, not the advert's** · 2026-11-07 -->
<!-- witness: none established — the 565 ids are an enumerator, not a count of what the board serves, and the second enumerator that would check them is behind the 401 · 2026-11-07 -->

<!-- content: measured · **the root and `/jobs` (200, 14 121 B, md5 41ed9d1cb76c identical on three reads) are the same React shell — `<div id="root">`, `/assets/index-BS0RXuXE.js`, `/registerSW.js`, a FAQ JSON-LD and meta tags claiming «+50 000 offres» and «+15 000 offres d'emploi en Afrique … 54 pays» — with 11 links in the head and none in the body; no card, no count in the markup, no JobPosting; `_robots.allowed('africa-jobconnect.com','/')` → open, certain. `countries:` by the page's own title («Emploi Sénégal, Côte d'Ivoire, Mali»), not by a measured ad** · 2026-09-20 -->
<!-- witness: none — the numbers in the meta tags are claims, no list was read · 2026-09-20 -->

**Named in the Atlas inventory of 2026-09-04 (#147), never carded; measured
for #765 on 2026-09-20 12:23–12:25 UTC, and re-measured for #784 on
2026-11-07 11:17–11:23 UTC — the guard on each exact URL, host included, in a
turn distinct from the retrieval, one token, `bin/fetch-body.py` throughout.**
*A measurement, not an adapter.*

The 2026-09-20 head said «the app's call to read». **It is read.** What it did
not anticipate is that the call does not need the bundle to be found and does
not live behind the `Disallow` this host writes: the rules file names it.

```
_robots.allowed('africa-jobconnect.com', '/api/')        allowed=False  kind=disallow  rule=/api/   READ, certain
_robots.allowed('jobconnect-africa.com', '/sitemap.xml') no-rules-connection          certain=False
_robots.allowed('jrluzolgzjajckpcjywu.supabase.co', '/rest/v1/jobs')   state=absent   certain=True
dig @1.1.1.1 jobconnect-africa.com   NXDOMAIN        dig @8.8.8.8 jobconnect-africa.com   NXDOMAIN
dig @1.1.1.1 africa-jobconnect.com   185.158.133.1   (the live name is the OTHER one)
```

## An enumerator that enumerates right and addresses wrong

Every one of the 1 184 `<loc>` points at `jobconnect-africa.com`, which does
not resolve on either resolver. So its **ids are read and its URLs are never
followed** — the live host is `africa-jobconnect.com`, and the slug-free
`/jobs/<uuid>` form means an id is enough to address an advert there.

A count of `<loc>` names a SIZE and never a NATURE: the 565 were separated from
483 facets and 125 landing pages by their path FORM, and members were opened at
the first, the median and the last position rather than at the top.

## This host's md5 MOVES, so no fingerprint comparison on it means anything

The 2026-09-20 line above records «md5 41ed9d1cb76c identical on three reads».
**That is dated and no longer true.** The shell is now 14 716 B, and the SAME
URL fetched twice gives `cc54a8c7215e` then `2e50279fd88c`: the body carries a
per-request analytics token whose payload holds an expiry, and the two differed
by exactly the seconds between the two calls.

> **The root and an advert page differ ONLY by that token.** Read as a
> difference between URLs it says «this advert is server-rendered»; it says
> nothing of the kind. *Two reads of one URL is what settled it, and that
> control is the one the repository already prescribes before comparing any two
> fingerprints.*

## Why there is no `route:` line here, and why it is not `none` either

The content route is OPEN by the rules and answers `401` without the
application's own public key. Reading that key out of the bundle, and probing
the data route, were both **refused by the measuring session's permission
classifier**. So the route is INDETERMINATE, and the cause is ours and not the
host's — *an indeterminate is a measurement to redo, never a renunciation.*

`route: none` would be a verdict that this board cannot be reached, which is a
decision about what we give up on and belongs to the owner. `route: http` is
not established: nothing has served an advert.

## Two notes an adapter would need before its first line

**It reads the `jobs` table and nothing else, and that is a safety condition.**
The bundle names 24 tables, among them `profiles`, `resumes`, `cv_history`,
`applications` and `messages` — real people. A host that forbids nothing on a
path has not thereby consented to our taking everything it exposes.

**`hosts:` is left at one name on purpose.** `jobconnect-africa.com` does not
resolve and the Supabase project is infrastructure rather than a board;
declaring either would add a line to the country pages' denominator for
something no adapter will ever address.
