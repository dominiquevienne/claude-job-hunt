# Board measurement — foundit Philippines (formerly Monster): the same stack and the same hand-written `ClaudeBot: Disallow /jobs/ /search/` as foundit Gulf, the transport OPEN, the sitemap index served

<!-- verified: 2026-09-13 -->

<!-- hosts: www.foundit.com.ph, foundit.com.ph -->
<!-- script: none -->
<!-- countries: PH -->
<!-- content: measured · rules read twice and certain (703 B — a hand-written group naming `GPTBot`, `ClaudeBot`, `CCBot`, `Bytespider`, `Meta-ExternalAgent`, `Google-Extended` with `Allow: /` and `Disallow: /jobs/`, `/search/`; `Claude-User` under `*`; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200 at the root (194 625 B, «100,000+ Jobs in Philippines») and at `/xmlsitemap/sitemap-index.xml` (5 601 B, byte-identical twice): 37 children, `active-jobs-sitemap0.xml.gz`, `active-jobs-sitemap1.xml.gz`, `todays-jobs-sitemap.xml.gz` among them — the enumeration `founditgulf.py` reads on the Gulf host; the active files were not counted here · 2026-09-13 -->
<!-- witness: the sitemap index — 37 children of the same names as `www.founditgulf.com`'s; the count of the active files is the adapter's first run, not this card's; no adapter yet -->

**Measured 2026-09-13 for #233, lot 8 — a measurement of the transport, not a
decision about the host.** Every fetch under the declared identity, the
guard on the exact path first, `bin/fetch-body.py`.

## The rules — reopened by the doctrine of 2026-09-07, and 37 sitemap children behind them

```
robots.txt      read twice, certain: True, 703 B, md5 365ec2d7dab4 both times — WRITTEN BY HAND: `User-Agent: GPTBot / ClaudeBot / CCBot / Bytespider / Meta-ExternalAgent / Google-Extended`: Allow /, Disallow /jobs/, /search/
identity("/")   http, claude-user      <- not named; the group that names ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True — «refuses 2 path(s) to claudebot and not the site as a whole»
allowed()       True on `/`, `/xmlsitemap/sitemap-index.xml`; `/jobs/` and `/search/` are not read by the family adapter under any token (a promise, see founditgulf.md)
crawl_delay     none
```

## The transport

```
GET https://www.foundit.com.ph/                              200, 194 625 B   (10:22:20Z, 10:22:21Z — same size, a per-response token)  «100,000+ Jobs in Philippines: Apply for September 2026 Hiring» — a slogan
GET https://www.foundit.com.ph/xmlsitemap/sitemap-index.xml  200, 5 601 B     (10:23:28Z, byte-identical at 10:23:30Z)  37 children
```

## What the pages say

| question | answer |
| :-- | --: |
| index children | **37** — `active-jobs-sitemap0`, `active-jobs-sitemap1`, `todays-jobs-sitemap`, and facets by location, function, skill, designation, as on the Gulf host |
| the root's figure | «100,000+ Jobs in Philippines» — a slogan, not a count (the Gulf host says «Over 800,000+»); never compared |
| the active count | **not read here** — two gzip files; `founditgulf.py`'s `sitemap` command generalised to this host would print it beside today's file |

**Same stack, same refusal, same condition**: `/jobs/` and `/search/` are the paths the operator closed by hand to six AI crawlers; the family adapter never reads them (`founditgulf.md`). The line stays on this card for the owner.

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE. **Candidate: the `founditgulf.py` stack with `www.foundit.com.ph` as a second host** (`countries:` read per advertisement, as there — a PH board lists abroad too); the active files' count is its first run.
- **Not a verdict that the host is closed** — nothing in the rules refuses `Claude-User`.
- **No configuration.** A user with a URL from this host can hand it to `cover-letter`.
