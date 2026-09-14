# Board adapter — リクナビNEXT / Rikunabi NEXT (Japan): rules open, and a session-less client is sent to `/session/destroy`

<!-- verified: 2026-09-14 -->

<!-- hosts: next.rikunabi.com -->
<!-- script: none -->
<!-- countries: JP -->
<!-- content: indeterminate · 1 host, rules read twice and certain — 64 `Disallow` to `*`, every one a query-string pattern (`/*?jobKey=` …), no path and no Sitemap line; the root answers 200 and REDIRECTS a session-less client to `/session/destroy/?type=webSso` (15 144 B, a Next.js shell with no visible text); `/sitemap.xml` 404; the two listing paths this card knew (`/rnc/docs/cp_s00700.jsp`, `/job/`) 404 — no listing route found by a permitted path, 5 paths tried · 2026-09-11 18:40 UTC -->
<!-- witness: the site's own per-area count — «1392件» with «1〜100件目を表示中» on `/job_search/area-tokyo/`, read from a connected tab at 10:46 UTC; the home's «掲載求人数 1,816,000件以上» is the site's marketing total (partner listings included), not this list's; nothing of the board is served to the declared client — every page, the area lists included, answers 200 with the `/session/destroy` shell (re-read 10:42 UTC) · 2026-09-14 -->
<!-- route: browser · 1392 · 2026-09-14 -->

**Recruit's flagship job-change site — one of Japan's largest boards — and
the first of the Japanese hosts this repository measured.** Measured
2026-09-11, 18:37–18:42 UTC, every fetch under the declared identity, the
guard on the exact path first.

## The rules — sixty-four query patterns, no path, and the parser keeps them all

```
User-agent: *
                                   <- a blank line, then the rules
Disallow: /*?jobKey=   Disallow: /*&jobKey=   Disallow: /*?jrtk=   … 64 lines, 37 with a wildcard
```

*The country page of 2026-09-01 warned that `urllib.robotparser` before 3.14
loses wildcard rules after a blank line. `_robots` is not that parser: checked
against the raw file, 64 rules parsed for `claude-user`, the 37 wildcards after
the blank line included.* No `Crawl-delay`, no `Sitemap:`, no group naming
this project. `identity()` → `http`, `claude-user`; `allowed()` `True` on `/`,
`/job/`, `/rnc/docs/…`, `/sitemap.xml`.

## The transport — 200, and a redirect to the SSO's exit

```
GET /                          200 → https://next.rikunabi.com/session/destroy/?type=webSso   15 144 B, twice (md5 moving — a csrfToken in the head)
                               a Next.js shell: <title> empty, no visible text, no link to any listing
GET /sitemap.xml               404, 0 B
GET /rnc/docs/cp_s00700.jsp    404, 20 220 B «ページが見つかりません»   <- the listing path of the old site
GET /job/                      404, 20 220 B
```

**A client without a Recruit session is sent to the session's destruction
page, and that page links nothing.** *This is not a refusal and not a
challenge: a 200 with a shell, and no route from it.* The listing lives
somewhere the site only reveals to a session, and composing paths to find it
would be guessing — five paths were tried, none invented beyond the two the
old site used. **No listing route found; the size of the board is not
measurable from here.** `townwork.net`, the other Recruit host, answers the
same redirect — with an AWS WAF challenge on top (its own card).

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision. Recorded:
  the rules open, the transport serves a shell to a session-less client.
- **No script.** What would change it: a `Sitemap:` line, a listing path
  reachable without a session, or a browser measurement of what the shell
  renders — the pilot's to assign.

## 2026-09-14 10:40–10:48 UTC — the shell is the client's; a connected tab gets the board

The declared client still gets, on every path — the root, a keyword list,
the area lists — a 200 whose `__NEXT_DATA__` is the `/session/destroy`
page (`type: webSso`, `shouldClearCache: true`): the app sends a
session-less client to its SSO exit and renders nothing. A connected tab,
whose first load establishes the session, is served the board:

```
tab, /                                  served — «掲載求人数 1,816,000件以上» (a marketing total), keyword and area entries
tab, /job_search/kw/英語/                served — «1562件以上», «1〜100件目を表示中», 100 cards /viewjob/jk<16 hex>/, employer links /company/…
tab, /sitemap/                          served — 167 /job_search/area-<pref>/ and /city-<name>/ lists
tab, /job_search/area-tokyo/            served — «1392件», 100 a page, pager 1 … (?sc=N)
tab, /viewjob/jk686ec6c4df03f234/       served — a JobPosting JSON-LD (株式会社ＲＵＳＨ, datePosted 2026-07-30) beside a BreadcrumbList; __NEXT_DATA__ 28 KB
client, the same addresses            200, 15 KB — the /session/destroy shell, no card, no count (10:42 UTC)
```

**`route: browser · 1392 · 2026-09-14`** — Tokyo's own count, one area
of 47 listed on `/sitemap/`; the national figure is their sum, not taken.
What a session does from a tab: the 47 `/job_search/area-<pref>/` lists
and their pagers, 100 a page, the count each prints beside the walk, the
id from `/viewjob/jk<hex>/`, the ad's JobPosting. No script: the
declared client gets the shell (#404). The `Crawl-delay` lines are
Applebot's (30) and bingbot's (5); none binds `*`.

