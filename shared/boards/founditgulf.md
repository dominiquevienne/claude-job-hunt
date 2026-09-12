# Board measurement — foundit Gulf (Gulf, formerly Monster Gulf): the operator wrote `ClaudeBot: Disallow /jobs/ /search/` by hand, `Claude-User` falls under `*`, and the active-jobs sitemaps hold 58 930 advertisements

<!-- verified: 2026-09-12 -->

<!-- hosts: www.founditgulf.com, founditgulf.com -->
<!-- script: none -->
<!-- countries: AE SA QA KW BH OM EG -->
<!-- content: measured · rules read twice and certain — a hand-written group naming `GPTBot`, `ClaudeBot`, `CCBot`, `Bytespider`, `Meta-ExternalAgent`, `Google-Extended` with `Allow: /` and `Disallow: /jobs/`, `/search/`; `Claude-User` is not named and falls under `*`, which refuses only dashboards, middleware and the expired-jobs sitemap; `identity()` answers `claude-user`, `verdict()` sweeps — and the transport answers 200 at the root, at `/search/it-jobs` (82 `/job/` links, an `ItemList`) and on the sitemaps: 3 active-jobs files, 58 930 `<loc>`, 58 930 distinct ids; `todays-jobs-sitemap.xml` 1 041, all among them · 2026-09-12 11:23 UTC -->
<!-- witness: the todays-jobs sitemap against the active-jobs sitemaps — 1 041 of 1 041 present in the 58 930; the listing states no count to a plain client; no adapter yet -->

**Measured 2026-09-12 at 11:18:56Z UTC for #233, lot 4 — a measurement of
the transport, not a decision about the host.** Every fetch under the
declared identity, the guard on the exact path first, `bin/fetch-body.py`.

## The rules — a refusal written by hand, and it names `ClaudeBot`

```
robots.txt      read twice, certain: True, 706 B, md5 572ee93fb164 both times
                `User-agent: *`            Disallow: /seeker/dashboard, /seeker/profile, /*radialhr, /pwa/, /trex/*/, */middleware/…, /mthinking/, *track_aor.html, /penguin/…, /middleware/, /xmlsitemap/expired-jobs-sitemap*.xml
                `User-Agent: GPTBot / ClaudeBot / CCBot / Bytespider / Meta-ExternalAgent / Google-Extended`
                                           Allow: /, /career-advice/, /career-services   Disallow: /jobs/, /search/
                Sitemap: /xmlsitemap/sitemap-index.xml, /xmlsitemap/todays-jobs-sitemap.xml
identity("/")   http, claude-user       <- not named; the group that names ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True
allowed("/search/it-jobs") True    allowed("/jobs/") True    allowed("/xmlsitemap/sitemap-index.xml") True
crawl_delay     none
```

*#233 keeps this one under «written by hand»: the operator chose six AI
crawlers and closed the two paths that ARE the board to them. The decision
of 2026-09-07 is about tokens, not authors — `Claude-User` is not in that
group — and the measurement is taken like the others.* **The line stays
«written by hand» on the card so that the owner sees what he is deciding
about.**

## The transport — 200 everywhere asked

```
GET https://www.founditgulf.com/                                       200, 226 430 B,  md5 34118fac87ee   (11:18:56Z)  «Latest Jobs in Gulf (2026), Job Vacancies, Recruitment - foundit Gulf»
GET https://www.founditgulf.com/                                       200, 226 430 B,  md5 5f30a3a49066   (second fetch)
GET https://www.founditgulf.com/search/it-jobs                         200, 1 794 514 B, md5 5c038ac0371e  (11:21:09Z)  82 `/job/` links, JSON-LD `ItemList` + `FAQPage`
GET https://www.founditgulf.com/search/it-jobs                         200, 1 794 514 B, md5 f971c463e74c  (second fetch)
GET https://www.founditgulf.com/xmlsitemap/sitemap-index.xml           200, 7 459 B,    md5 0d5f8d0348ee   (11:22:22Z)  49 children
GET https://www.founditgulf.com/xmlsitemap/todays-jobs-sitemap.xml     200, 191 894 B,  md5 e061236b7ee7   (11:22:22Z)  1 041 <loc>
GET https://www.founditgulf.com/xmlsitemap/active-jobs-sitemap{0,1,2}.xml.gz   200, 521 657 / 508 845 / 195 516 B   (11:22:59–11:23:00Z)   24 975 + 24 954 + 9 001 <loc>
```

## What the sitemaps say — 58 930 advertisements, seven countries by the slug

| question | answer |
| :-- | --: |
| `<loc>` across `active-jobs-sitemap0..2` | **58 930** — `/job/<slug>-<id>`, **58 930 distinct ids** |
| `todays-jobs-sitemap.xml` | 1 041, **1 041 of them among the 58 930** |
| distinct `<lastmod>` | 36 — **all between 2026-09-11 13:06:53 and 13:07:xx +02:00**: a rebuild, stamped second by second, not a posting date |
| by the slug's tail | AE 29 360 · SA 13 600 · **EG 12 080** · QA 2 215 · KW 777 · BH 263 · OM 32 · two names 392 · none 211 |
| the listing's own count | none found on `/search/it-jobs` — no «N jobs found» in the HTML served to a plain client |

**Egypt is a fifth of the board** — `countries:` says so; a Gulf label would
have hidden 12 080 advertisements. *The other 45 index children are
facets — by location, function, skill, designation — and the `expired-jobs`
sitemaps are refused to `*`: they are not the enumeration and are not read.*

## What this card is, and is not

- **A measurement, not an adapter** — `script: none`, a measurement DUE.
  **Candidate adapter**: three sitemap files enumerate, the id is the slug's
  tail, and a `/job/` page's JSON-LD is the adapter's first question, not
  asked here. *`monster.py` in this repository reads Monster's US API; this
  host is the Gulf franchise on a different stack (`/xmlsitemap/`), and
  nothing transposes.*
- **Not a verdict on the hand-written refusal** — recorded as written, for
  the owner; the transport was measured under the token that is not named.
- **No configuration.** A user with a URL from this host can hand it to
  `cover-letter`.
