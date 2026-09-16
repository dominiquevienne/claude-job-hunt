# Board adapter — Forasna (Egypt): a challenge to the declared client on every path, and a connected tab served the whole board — «2,974 وظائف خالية», `?start=N` by 20; `route: browser`, no script

<!-- verified: 2026-09-16 -->

<!-- hosts: forasna.com -->
<!-- script: none -->
<!-- countries: EG -->
<!-- content: measured · **the declared client gets a 403 challenge on the root and the two guessed sitemap paths (5 645–5 717-byte «Just a moment...», md5 moving at constant size, 2026-09-11); a connected tab was served everything without any click on 2026-09-16 05:3x UTC: the root («2833 وظائف خالية» in its header block), the list `/وظائف-خالية` stating «2,974 وظائف خالية» — 30 cards on page 1, then `?&start=N` in steps of 20 (`start=20` opens on the 21st card of page 1; `start=2960` lists 14 = 2 974 − 2 960, the last), each card the title, employer, governorate/district, experience, openings, gender, hours, area / speciality, base salary in EGP or «غير معلن», benefits; the ad `/job/p/<slug>-<id>` prints employer, workplace, posting age, headcount, requirements (experience, licence, gender, English, age, degree), salary, hours, area, speciality, the description — and the employer's applicant counters; no JobPosting JSON-LD looked for from the tab** · 2026-09-16 -->
<!-- witness: none — the list's own «2,974» is the count beside the walk; the rules declare no Sitemap line -->
<!-- route: browser · 2974 · 2026-09-16 -->

**Egypt's second board on a card with `wuzzuf.net`, and the same family of
«no» — with one difference that decides the route.** Measured 2026-09-11,
13:54 UTC, every fetch through `bin/fetch-body.py` under the declared
identity, the guard on the exact path first.

## The rules — the Cloudflare managed file, `ClaudeBot` refused, `*` open

```
GET /robots.txt        200, fetched twice, same body
User-agent: *          Content-Signal: search=yes,ai-train=no,use=reference   Allow: /
User-agent: Amazonbot · Applebot-Extended · Bytespider · CCBot · ClaudeBot ·
            CloudflareBrowserRenderingCrawler · Google-Extended · GPTBot · meta-externalagent   Disallow: /
```

No `Crawl-delay`, **no `Sitemap:` line** — `shared/robots-policy.md` already
lists this host with `wuzzuf.net` among the Egyptian carriers of the managed
file. `identity("forasna.com", "/")` → `http`, `claude-user`; `allowed()`
`True`, `certain: True` on `/`, `/jobs`, `/jobs/egypt`, `/sitemap.xml`.
**The permitted token exists on paper and is the one that was tried.**

## The transport — a challenge on every path, the XML included

```
GET /                     403, 5 645 B, «Just a moment...», md5 a2d8d492…  then 43fcbfed…   ← same URL twice
GET /sitemap.xml          403, 5 678 B, «Just a moment...»
GET /sitemap_index.xml    403, 5 717 B, «Just a moment...»
```

**Same size, different md5 on two fetches of the same URL — a challenge, the
`revolico` / `mabumbe` / `wuzzuf` family.** *The comparison across hosts is
void by the rule of 2026-09-07 (the `cf-ray` is inside the body), and the
comparison of one URL with itself is what says «challenge».* **Where
`wuzzuf.net` serves its sitemap XML from behind the same interstitial, this
host does not** — the two guessed sitemap paths answer the challenge like the
root, and the rules declare none. *So there is no address inventory here, and
no script.*

**A challenge is where the browser branch stops** (borne 2): the plugin
neither defeats one nor asks the user to. Whether a real browser passes this
managed challenge without a person is not measured, and this card claims
nothing either way.

## What this card is, and is not

- **Not a verdict that the board is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: three content paths, one
  day, one client, a challenge each time.
- **Not the #222 case as measured here**: a challenge, not a static 403.
- **No script, no configuration.** A user with a forasna.com URL can hand it
  to `cover-letter`; whether that page is served to a browser is not
  established here.
- **What would change it:** a `Sitemap:` line, or XML served from behind the
  interstitial as `wuzzuf.net` does — one request to check, dated.

## 2026-09-16 — the tab is served, without a click: `route: browser · 2974`

**Point 2 of the pilot's assignment of 2026-09-15 — the owner had said of the
«domain permission» refusals of 2026-09-14 that «le plugin brave valide
l'ensemble des sites. ce doit être autre chose».** Two readings from a
connected tab, 05:3x UTC, no click anywhere, no challenge shown:

```
tab, https://forasna.com/                                    served — the front page, «2833 وظائف خالية» in the header block, today's ads
tab, /وظائف-خالية                                            served — «2,974 وظائف خالية», 30 cards, pager 1 … 6 التالى
tab, /وظائف-خالية?&start=20                                  served — opens on the 21st card of page 1 (the step is 20)
tab, /وظائف-خالية?&start=2960                                served — 14 cards, 2 974 − 2 960 = 14: the last page
tab, /job/p/…-440483                                          served — the ad: employer, workplace, age, headcount, requirements, salary, description
```

**Two counts on the same site, two questions:** the header block says
«2833», the list says «2,974» — the list's figure is the one beside the walk,
the header's is not explained by this card (a cached badge, a different
filter: not established). **What a session does from a tab:**
`/وظائف-خالية?&start=N` for N = 0, 20, 40 … until a page lists fewer than
20, the id from the tail of `/job/p/<slug>-<id>`, «2,974» read from the
list beside the emitted count. No script: the declared client is still
answered by the challenge (#404), and the challenge is not defeated — the
tab was simply served.

**The refusal of 2026-09-14 was named, wrongly, «the extension's domain
permission».** Measured today on the same tool: the text «Navigation to this
domain is not allowed» is rendered by the `navigate` tool when it runs as a
NON-FIRST item of a `browser_batch` toward a domain the session has not yet
visited — the same URL as the first item of a batch, or standalone, is
navigated (4 refusals / 4 passes on `tecoloco.md`, this host served at the
first try today). It is not the site, not the browser, not an allowlist.

**What is withheld:** the ad prints the employer's applicant counters and
nothing of a recruiter; the application is a login (`/login`,
`/jobseeker/register`), never touched.
