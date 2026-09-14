# Board adapter — タウンワーク / Townwork (Japan): rules open, the SSO's exit, and an AWS WAF challenge on top

<!-- verified: 2026-09-14 -->

<!-- hosts: townwork.net -->
<!-- script: none -->
<!-- countries: JP -->
<!-- content: indeterminate · 1 host, rules read twice and certain — 85 `Disallow` to `*`, query-string patterns like its Recruit sibling, no Sitemap line; the root answers 200 and REDIRECTS a session-less client to `/session/destroy/?type=webSSO` (5 460 B, a Next.js shell with no visible text) **that loads `edge.sdk.awswaf.com/…/challenge.js`** — an AWS WAF challenge, passive; `/sitemap.xml` 404; nothing of the board was served, 3 paths tried · 2026-09-11 18:40 UTC -->
<!-- witness: the site's own per-prefecture count — «1,080件» on `/prefectures/tokyo/job_search/`, read from a connected tab at 10:19 UTC; the national figure is the sum of the 47 prefectures' counts, not summed here; nothing is served to the declared client (the AWS WAF challenge), so no script prints anything · 2026-09-14 -->
<!-- route: browser · 1080 · 2026-09-14 -->

**Recruit's part-time and hourly-work board.** Measured 2026-09-11, 18:37–18:41
and 23:47 UTC, every fetch under the declared identity, the guard on the exact
path first.

## The rules, and the transport

```
robots.txt        read twice, certain: True — 85 Disallow to `*` (/*?betk=, /*?referrerId= …), no Crawl-delay, no Sitemap
identity("/")     http, claude-user · allowed("/") True

GET /             200 → https://townwork.net/session/destroy/?type=webSSO   5 460 B, twice (md5 moving)
                  <script src="https://e900f1d4dcad.edge.sdk.awswaf.com/e900f1d4dcad/c8a8b1cd90d8/challenge.js">
                  no <title>, no visible text, no link
GET /sitemap.xml  404, 0 B
```

**Two things at once, and they are read separately.** *The redirect is the
same as `next.rikunabi.com`'s: a client without a Recruit session is sent to
the session's exit, which links nothing.* **And the shell loads an AWS WAF
`challenge.js`** — the word «challenge» found in the body on the first read
was this script, not an interstitial: the status is 200, not 403, and the
page is a shell either way. *A passive challenge is still a challenge*: what
the WAF gates is the content a session would see, and the plugin neither
executes a challenge script to obtain its token nor asks the user to. **Whether
a real browser passes it without a person is not measured, and this card
claims nothing either way.**

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision. Recorded:
  the rules open, a 200 shell behind an SSO redirect, a WAF challenge script
  in it, no sitemap.
- **No script.** What would change it: a listing path reachable without a
  session and without the WAF token, or a browser measurement — the pilot's
  to assign.

## 2026-09-14 10:17–10:21 UTC — the AWS WAF challenge does not show to a connected tab

```
tab, /                                     served — the home (areas, popular wards); the WAF script is in the page, no challenge shown
tab, /prefectures/tokyo/                   served — the prefecture's hub: 194 links to /prefectures/tokyo/job_search/prf-<code>/ (wards, trades, features)
tab, /prefectures/tokyo/job_search/        served — «1,080件», cards /viewjob/jobid_<16 hex>/ (title, employer, access, hourly wage), sort by relevance / newest; no pager link in the markup (loaded on scroll)
tab, /viewjob/jobid_6802a5f8d07e42ed/      served — a JobPosting JSON-LD (hiringOrganization 株式会社イエロージャム, datePosted 2026-09-10) beside a BreadcrumbList; one telephone number in the page text — never to be emitted
```

**`route: browser · 1080 · 2026-09-14`** — Tokyo's own count, one
prefecture of 47; the national figure is their sum, not taken. What a
session does from a tab: `/prefectures/<pref>/job_search/`, the count the
page prints, the list scrolled to its end (no pager link), the id from
`/viewjob/jobid_<hex>/`, the ad's JobPosting, the telephone withheld. No
script: the declared client gets the challenge (#404).

