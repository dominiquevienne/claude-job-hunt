# Board measurement — Sudan Careers (`www.sudancareers.com`, Sudan): the challenge of the 11th was not met on the 13th — served to a tab, 28 of 28

<!-- verified: 2026-09-13 -->

<!-- hosts: www.sudancareers.com, sudancareers.com -->
<!-- script: none -->
<!-- countries: SD -->
<!-- content: measured · **28 distinct advertisement addresses** over `/job-vacancies-search-sudan?page=0…` (25 + 3; the next page empty), read from a connected browser tab, **against «28 Job ads found» stated by the page — equal**; the pager is zero-based, as on every AfricaWork host read since `ghanajob.md`; no challenge met by the tab on the 13th where the declared client met one on the 11th; the rules as on the 11th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: the page's own «28 Job ads found», read on every page and printed beside the distinct count («28 emitted, site states 28 — equal»); the declared client's challenge («Attention Required!», 5 515 B, md5 moving) on `/` on the 11th · 2026-09-13 -->
<!-- route: browser · 28 · 2026-09-13 -->

**Measured 2026-09-11 at 22:10:49Z UTC for #233, lot 1 — a measurement of the
transport, not a decision about the host.** Every fetch under the declared
identity, the guard on the exact path first.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True
```

*Before the decision this host was read as closed by name; the decision
reopened it on paper, and this card is the first time its transport was
asked under the permitted token.*

## The transport — a Cloudflare challenge

```
GET https://www.sudancareers.com/     403, 5515 B, md5 0130507effc9    (22:10:49Z)
GET https://www.sudancareers.com/     403, 5515 B, md5 719805e27b1a    (second fetch)
```

**Same size, different md5 on two fetches of the same URL, «Attention
Required! | Cloudflare» — a challenge**, the `revolico` / `mabumbe` family.
*The comparison across hosts is void (the `cf-ray` is in the body); the
comparison of one URL with itself is what says «challenge».* **A challenge is
where the browser branch stops** (borne 2): the plugin neither defeats one nor
asks the user to. Whether a real browser passes it without a person is not
measured, and this card claims nothing either way.

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches of the root, a challenge.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.

## 2026-09-13 16:55 UTC — the browser route, MEASURED (#222): no challenge to the tab, 28 of 28

```
tab: /                                        200 «Job Vacancies and Recruitment in Sudan | Sudancareers.com» — no interstitial; the home page links /job-vacancies-search-sudan
tab: fetch /job-vacancies-search-sudan?page=0,1,2     25 · 3 · 0  →  **28 distinct data-href addresses**, «28 Job ads found» — **equal**; every address carries its id
```

**The procedure is `ghanajob.md`'s six steps** — guard on the exact listing path first (`*` open, certain), one tab, `fetch('?page=0,1,2…')` 1.5 s apart until a page carries no card, the site's own count read on every page and printed beside the distinct count. The challenge this card recorded on the 11th was for the declared client; the tab was served on its first request. *Whether the challenge is for the client alone or intermittent is not decided by two days; both are recorded.* The smallest AfricaWork inventory read so far — a country at war, 28 advertisements.
