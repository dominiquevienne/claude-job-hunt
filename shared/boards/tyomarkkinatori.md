# Board measurement — Työmarkkinatori (Finland): the public employment service's every data route lives under `/api/`, refused in writing to `*` — the search widget posts to `/api/jobpostingfulltext/search/v2/search`, the posting comes from `/api/jobposting-new/v1/public/jobpostings/<id>`, and no page carries either

<!-- verified: 2026-09-13 -->

<!-- hosts: tyomarkkinatori.fi, www.tyomarkkinatori.fi -->
<!-- script: none -->
<!-- countries: FI -->
<!-- content: measured · rules read twice and certain (639 B, `*` refused 15 paths — **`/api/` and `/*/api/`**, `/.rest/errorlog`, the signed-in areas in three languages —, no agent named, no Sitemap line; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200 on the pages: `/henkiloasiakkaat/avoimet-tyopaikat` (163 056 B) is a shell that loads the widget `TmtTyopaikkaHakuV2` (1 500 919 B of JavaScript, served), whose axios client has `baseURL: "/api"` and POSTs the search to `/api/jobpostingfulltext/search/v2/search` and GETs a posting from `/api/jobposting-new/v1/public/jobpostings/<id>` — every advertisement, listed or read, passes through the prefix the rules refuse; `/sitemap.xml` is the site's own 404; 0 advertisement links in the HTML; the open-data portal `avoindata.fi` answers a static 403 to this client · 2026-09-13 17:58 UTC -->
<!-- witness: none reachable by a permitted path — the count lives in the search response (`totalElements`) under `/api/`; nothing was requested there -->
<!-- route: none · every data route of the board — the search and the posting — is under `/api/`, refused in writing to `*` (`Disallow: /api/`, `/*/api/`, 2026-09-13); a refusal read in the rules is honoured by every route, browser included (borne 1); the one exit is the USER's own key `boards.tyomarkkinatori.override_robots: true`, set in their own name and conscience — the owner's decision of 2026-09-13 (#403) generalised the key to every board refused in writing; the adapter is #371's, and without the key it is skipped and says so · 2026-09-13 -->

**Measured 2026-09-13 17:56–17:58 UTC for #371 — a measurement of the
rules and of where the data lives, not a decision about the host.** Every
fetch under the declared identity, the guard on the exact path first. *The
page Finlande of 2026-08-31 read the same `Disallow: /api/` and left «is
there a sanctioned door?» open; this card answers where the data is and
that no door was found today.*

## The rules — fifteen refusals, two of them the whole API

```
robots.txt      639 B, md5 befc2a9ded19, read twice, certain: True
User-agent: *
Disallow: /api/            <- the search and the posting live here
Disallow: /*/api/
Disallow: /.rest/errorlog
# new site: /henkiloasiakkaat/oma-tyopolku/, /henkiloasiakkaat/asiointi, /tyonantajat-ja-yrittajat/yrityksen-asiointi/ — and their sv/en twins
# old site (before 3.0): /omat-sivut/ and twins
identity("/")   http, claude-user — no agent named
verdict()       sweep True, certain True, crawl_delay none — 15 paths refused, "not the site as a whole"
allowed()       True on `/`, `/henkiloasiakkaat/avoimet-tyopaikat`, `/widgets/TmtTyopaikkaHakuV2/index.js` — **False on `/api/jobpostingfulltext/search/v2/search` and `/api/jobposting-new/v1/public/jobpostings/<id>`**
Sitemap:        none declared; `/sitemap.xml` answers the site's own 404 («Sivua ei löydy», 157 793 B)
```

## Where the advertisements are — read from the widget's own code, never requested

| question | answer (2026-09-13, 17:56–17:58 UTC) |
| :-- | --: |
| `/henkiloasiakkaat/avoimet-tyopaikat` (and `/haku`) | 200, 163 056 B — a shell: a header, the cookie banner, and a loader that injects `/widgets/TmtTyopaikkaHakuV2/index.js`; **0 links to an advertisement in the HTML**, no JSON-LD |
| the widget | `/widgets/TmtTyopaikkaHakuV2/index.js`, 200, 1 500 919 B — permitted, read once |
| its search | `qU = axios.create({baseURL: "/api"})`, then `qU.post("/jobpostingfulltext/search/v2/search", {query, filters, paging: {pageNumber, pageSize}, sorting})` → a response with `totalElements`, `totalPages` — **`/api/jobpostingfulltext/search/v2/search`, refused** |
| its posting | `/jobposting-new/v1/public/jobpostings/<id>` on the same base — **`/api/jobposting-new/v1/public/jobpostings/<id>`, refused**; the service map names `/api/jobposting/v1`, `/api/jobposting-new/v1`, `/api/jobpostingfulltext/search/v1`, `/api/aggregation/v1` … all under the prefix |
| a sanctioned door elsewhere | `www.avoindata.fi/data/fi/dataset?q=työpaikat` → **403, 118 B, static** to this client (its rules file 403 too — an absence since #283); the EURES aggregation (`eures.europa.eu`, linked from the page) is another board, not this one, and was not measured here |
| what was requested under `/api/` | **nothing** |

**A refusal read in the rules is honoured by every route.** *`Disallow:
/api/` is not a firewall's answer — it is the operator's line, written to
everyone, and both the list and the posting sit behind it. A browser tab
renders the same widget calling the same `/api/`; borne 1 of §2 quater
says a written refusal is not walked around by a browser either.* **What
would open this board is the user's own override key — the form of
`boards.smartrecruiters.override_robots` and `boards.hiringcafe.override_robots`,
set by the user and costing the user's own address.** *Until 2026-09-13 that
key was the owner's to grant, board by board; on that day the owner decided
the mechanism once and for all — «&nbsp;oui, l'utilisateur doit pouvoir
émettre une dérogation en son âme et conscience&nbsp;» (#403) — and the
guard reads `boards.<board>.override_robots` for every adapter.* The
adapter is #371's: `POST /api/jobpostingfulltext/search/v2/search` for the
list, `GET /api/jobposting-new/v1/public/jobpostings/<id>` for a posting,
`totalElements` as the witness, no contact — skipped without the key, and
saying so; with it, the banner on every run. The card does not say the
board is closed: it says where the door is and that the user holds the key.

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, and no adapter is
  buildable by a permitted path today: no sitemap, no server-rendered
  listing, no posting page outside `/api/`.
- **Not a verdict that the host is closed** — the pages are served, the
  widget is served; the data is refused in writing.
- **The next step is the owner's**: an override (#371 stays open and
  `blocked`), or a sanctioned door found later (`avoindata.fi` from a
  client it serves, or a published API of the KEHA-keskus).
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.

## Provenance

- `tmt/robots.txt` (639 B, 17:56:2xZ), `tmt/henkiloasiakkaat_avoimet-tyopaikat.html`,
  `…_haku.html`, `tmt/sitemap.xml.html` (the 404 body), `tmt/widget.js`
  (1 500 919 B), `tmt/avoindata.html` (the 403 body, 118 B) — 2026-09-13
  17:56–17:58 UTC, `bin/fetch-body.py`, provenance beside each; scratchpad
  of `claude-job-hunt-ab`.
- The endpoints are quoted from `widget.js` verbatim (`baseURL:"/api"`,
  `qU.post("/jobpostingfulltext/search/v2/search"`, `.get(\`/jobposting-new/v1/public/jobpostings/\``).
