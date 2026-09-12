# Board adapter — リクナビNEXT / Rikunabi NEXT (Japan): rules open, and a session-less client is sent to `/session/destroy`

<!-- verified: 2026-09-11 -->

<!-- hosts: next.rikunabi.com -->
<!-- script: none -->
<!-- countries: JP -->
<!-- content: indeterminate · 1 host, rules read twice and certain — 64 `Disallow` to `*`, every one a query-string pattern (`/*?jobKey=` …), no path and no Sitemap line; the root answers 200 and REDIRECTS a session-less client to `/session/destroy/?type=webSso` (15 144 B, a Next.js shell with no visible text); `/sitemap.xml` 404; the two listing paths this card knew (`/rnc/docs/cp_s00700.jsp`, `/job/`) 404 — no listing route found by a permitted path, 5 paths tried · 2026-09-11 18:40 UTC -->
<!-- witness: none — nothing of the board was served -->

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
