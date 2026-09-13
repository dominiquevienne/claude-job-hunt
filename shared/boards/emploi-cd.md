# Board measurement — Emploi.cd (`www.emploi.cd`, DR Congo): the challenge of the 12th was not met on the 13th — served to a tab, 70 of 70, six addresses without a number

<!-- verified: 2026-09-13 -->

<!-- hosts: www.emploi.cd, emploi.cd -->
<!-- script: none -->
<!-- countries: CD -->
<!-- content: measured · **70 distinct advertisement addresses** over `/recherche-jobs-congo-rdc?page=0…` (25 + 25 + 20; the next page empty), read from a connected browser tab, **against «70 Offres d'emploi trouvées» stated by the page — equal**; six of the seventy addresses carry no trailing id and are keyed by path; the pager is zero-based; `/recherche-jobs-rdc` (the path this card named on the 12th) answers 404 — the site's own link is `/recherche-jobs-congo-rdc`; the rules as on the 12th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: the page's own «70 Offres d'emploi trouvées», read on every page and printed beside the distinct count («70 emitted, site states 70 — equal»); the declared client's 25-byte 403 (md5 9ccabba20b9f) on the same path, the family's vendor default · 2026-09-13 -->
<!-- route: browser · 70 · 2026-09-13 -->

**Measured 2026-09-12 at 10:54:54Z UTC for #233, lot 2 — a measurement of the
transport, not a decision about the host.** Every fetch under the declared
identity, the guard on the exact path first, by `bin/fetch-body.py
--allow-refusal` — the four records carry the status, the bytes, the md5 and
the `cf-ray` that answered.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 1836 B, md5 c6370d4bc025 both times — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True
```

*The file is Cloudflare's managed content block, byte for byte — the
`Content-Signal` preamble and nine named crawlers refused, `ClaudeBot` among
them — with not one line of the operator's own.* Before the decision this
host was read as closed by name; the decision reopened it on paper, and this
card is the first time its transport was asked under the permitted token.

## The transport — a Cloudflare challenge

```
GET https://www.emploi.cd/                        403, 5508 B, md5 7b749ec356bd    (10:54:54Z)
GET https://www.emploi.cd/                        403, 5508 B, md5 e8f3834e6d7c    (second fetch)
GET https://www.emploi.cd/recherche-jobs-rdc     403, 5508 B, md5 520b7564f04c    (10:55:53Z)
GET https://www.emploi.cd/recherche-jobs-rdc     403, 5508 B, md5 2e601304478a    (second fetch)
```

**Same size, different md5 on two fetches of the same URL, «Attention
Required! | Cloudflare» — a challenge**, the `revolico` / `mabumbe` /
`sudancareers` family. *Masking the 16-hex `cf-ray` in the two bodies leaves
one difference, a base64 timestamp in `__CF$cv$params` — the whole of the
movement is the edge's own stamp.* *The comparison across hosts is void (the
`cf-ray` is in the body); the comparison of one URL with itself is what says
«challenge».* **A challenge is where the browser branch stops** (borne 2): the
plugin neither defeats one nor asks the user to. Whether a real browser passes
it without a person is not measured, and this card claims nothing either way.

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches each of the root and a listing path, a challenge.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.
- **AfricaWork franchise**: the same rules file (1836 B, md5 `c6370d4bc025`) as
  `www.emploibenin.com`, `www.emploi.cm`, `www.emploisenegal.com` and the
  other members of lot 1 — **this is one read of this host, dated, not a
  verdict copied from a sibling**: two members of this very lot answer a
  challenge where the other five answer the static default, under one and the
  same rules file.

## 2026-09-13 16:34–16:35 UTC — the browser route, MEASURED (#222): no challenge today, 70 of 70

```
tab: /recherche-jobs-rdc                200 «Page non trouvée» — the path this card named on the 12th is a 404 page; the home page links /recherche-jobs-congo-rdc
tab: fetch /recherche-jobs-congo-rdc?page=0,1,2,3     25 · 25 · 20 · 0  →  **70 distinct data-href addresses**, «70 Offres d'emploi trouvées» on every page — **equal**
                                        6 of the 70 addresses end in a slug with no number (…/retail-operations-specialist-local-congolese); keyed by path
```

**The procedure is `ghanajob.md`'s six steps** — guard on the exact listing path (`*` open, certain), one tab, `fetch('?page=0,1,2…')` 1.5 s apart until a page carries no card, the site's own «N Offres d'emploi trouvées» read on every page and printed beside the distinct count. The declared client gets the family's 25-byte 403 (md5 `9ccabba20b9f…`) on the same path — the vendor's default, for the client alone. **The cards are keyed by their `data-href` address, not by a trailing number**: on `emploi.cd` six of seventy addresses carry no id at all (`…/retail-operations-specialist-local-congolese`), and a reader keyed on the number printed «64 emitted, site states 70 — 6 short» with nothing else wrong — the same shape as `gulftalent.md`'s two address shapes, found the same day.

**The challenge this card recorded on the 12th («Attention Required!», md5 moving) was not met by the tab on the 13th** — the page was served on the first request, no interstitial. Whether the challenge is for the client alone or intermittent is not decided by two days; both are recorded.
