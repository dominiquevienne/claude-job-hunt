# Board measurement — Shaqo.com (Somaliland / Somalia): refused to our client, served to a browser, and a GraphQL count that names the archive unless the page's own date filter is added

<!-- verified: 2026-09-12 -->

<!-- hosts: shaqo.com, www.shaqo.com -->
<!-- script: none -->
<!-- countries: SO -->
<!-- content: measured · **23 live advertisements** — `job_aggregate` with the page's own filter (`status = APPROVED`, `closing_date > now`) states 23, and the `job` query with the same filter returns 23 distinct ids (12 full-time, 5 tenders, 4 consultancies, 1 internship, 1 training; Hargeisa 3, «Somalia» 10, Mogadishu, Galkayo, Dhusamareeb, Djibouti 1); the same aggregate WITHOUT the date filter states 4 574 — the archive; from a connected browser tab at 12:11 UTC · 2026-09-12 -->
<!-- witness: the site's own `job_aggregate` — the count its explore page asks Hasura for — read twice with two filters and printed beside the walk: «23 emitted, site states 23 (live) — equal; 4 574 approved ever»; the explore page itself shows 10 and a one-page pager, and neither of those is the count · 2026-09-12 -->
<!-- route: browser · 23 · 2026-09-12 -->

**The only commercial board based in Somaliland — HarHub Building, Hargeisa
— and it serves Somalia and Djibouti as much as Somaliland: 3 of its 23 live
posts are in Hargeisa.** *Named in the Somaliland page and in
`somaliland-le-lisible-est-le-fabrique` since 2026-09-04 as «rules open to
`claude-user`, transport refused, 05.09 11:33 UTC» — 25-byte 403 on `/` and
`/sitemap.xml`, the managed Cloudflare template on `/robots.txt`.* This card
is what a browser sees past that door. Measured 2026-09-12 12:08–12:11 UTC,
Claude in Chrome connected, one tab, the guard on the exact path first.

## Rules, transport, and the door

```
robots.txt        200, 1 836 B, the managed template — `*` → Allow: / ; `ClaudeBot` refused, `Claude-User` not named → guard allowed True, certain True (decision of 2026-09-07)
identity("/")     http, claude-user — «claude-user may fetch this path (claudebot may not)»
declared client   / and /sitemap.xml → 403, 25 B (2026-09-05, 11:33 UTC) — the vendor default of `robots-policy.md`'s family (1)
browser tab       / → 200 «HOME - SHAQO.COM» · /explore → 200 «EXPLORE - SHAQO.COM» · no challenge, no interstitial
```

**Borne 0 held**: the 403 goes to the declared HTTP client and to nobody
else. A Nuxt 2 app (`window.__NUXT__`, Apollo cache, reCAPTCHA v2 configured
for forms — never met on a read). `/sitemap.xml` is a 404 rendered as the
app's HTML shell (972 518 B).

## What the pages show, and why none of it is the count

```
/                  «View the latest 30 jobs posted by the hiring companies» — 18 distinct /job/<uuid> links
/explore           10 cards, a pager reading «1», /explore?page=2 → the same 10 (SSR ignores the parameter)
                   card: employer · city · title · type (Full-time / Consultancy / Tender / Internship / Training) · «Posted N days ago» · «Deadline in N days»
/job/<uuid>        the advertisement address (id = the job's uuid)
footer             «+252-63-3331134» — a phone number, which a (\d+)\s*jobs pattern reads as «3331134 jobs» three lines above the word
```

**The explore page asks Hasura for two things, and they disagree with
each other by design** — read from the Apollo cache the page ships
(`__NUXT__.apollo.defaultClient.ROOT_QUERY`):

```
job(limit: 10, offset: 0, order_by: {created_at: desc},
    where: {status: {_eq: "APPROVED"}, closing_date: {_gt: "<now>"}, title/company/category/location/type: {_ilike: "%%"}})   -> 10 rows
job_aggregate(where: {status: {_eq: "APPROVED"}, category/location/type: {_ilike: "%%"}})                                    -> count 4 574
```

*The list is filtered on `closing_date > now`; the count is not.* **So 4 574
is every approved post ever, and the page's own pager — one page — is
computed from something else again.** The endpoint is
`https://www.shaqo.com/graphql/v1/graphql` (read in `/_nuxt/fb6246f.js`),
on the host the rules open; the guard on that exact path is `allowed True,
certain True`.

## The count — the page's filter, applied to the page's counter

One POST from the tab, both aggregates and the live list in a single query:

```
live  job_aggregate(status = APPROVED, closing_date > 2026-09-12T12:11:01Z)   count **23**
all   job_aggregate(status = APPROVED)                                         count 4 574
jobs  job(same live filter, order_by created_at desc, limit 100)               **23 rows, 23 distinct uuids** — 23 emitted, site states 23 — equal
      types   Full-time 12 · Tender 5 · Consultancy 4 · Internship 1 · Training 1
      places  Somalia 10 · Hargeisa 3 · Dollo Ado 2 · Mogadishu · Galkayo · Dhusamareeb · Guricel · Marka · Djibouti · Multiple · «Somaliland/ Somalia»
      fields  id · title · type · location · category · created_at · closing_date · company{name} (+ qualification, experience, status, description on the object)
```

**Five of the 23 are tenders and four are consultancies** — a `type` filter
is the line between a vacancy and a procurement notice here, and the
adapter must apply it. *23 is a flux: the youngest post was created
2026-09-10 and closes 2026-09-16.*

**The procedure a session follows — this is the adapter, at the same title
as a script (decision of 2026-09-08):**

1. guard `shaqo.com` on `/explore` and `www.shaqo.com` on
   `/graphql/v1/graphql` before anything;
2. `navigate https://shaqo.com/explore` in the session's own tab (the 403
   is for the declared HTTP client; the tab is served);
3. from the tab, POST the query above to `/graphql/v1/graphql` **with the
   page's own live filter** — `status = APPROVED`, `closing_date > now` —
   asking `job_aggregate.count` and `job(limit 100)` in one request; print
   **«n emitted, site states count(live) — equal / k short; count(all) is
   the archive»**, never the 4 574 alone;
4. emit one row per uuid with `type` kept, and let the caller drop
   `Tender`; the advertisement URL is `/job/<uuid>`;
5. close the tab.

## What this card does not establish

- **The advertisement page** — `/job/<uuid>` was not opened; `description`
  on the cached object was `null` on the one read, and the page may carry
  it elsewhere.
- **Whether `status = APPROVED` is the only visible state** — the page
  asks for it; nothing else was queried.
- **The home's 18 against explore's 10** — 9 of the 10 are among the 18;
  the home's «latest 30» includes posts past their closing date or the
  explore's list is capped at 10 by its `limit`, and both readings fit.
- **No script ships.** The route is a browser tab and one GraphQL POST
  from it; whether the declared HTTP client is ever served again is
  measured, not assumed.
