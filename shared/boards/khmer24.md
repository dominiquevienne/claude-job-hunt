# Board adapter — Khmer24 (Cambodia): reopened by the 2026-09-07 doctrine, and the transport refuses the client with a static 403 — and served to a browser

<!-- verified: 2026-09-13 -->

<!-- hosts: www.khmer24.com, khmer24.com -->
<!-- script: none -->
<!-- countries: KH -->
<!-- content: measured · **52 advertisement links on the first page of `/en/c-jobs`** (`/en/<slug>-adid-<n>`), read from a connected browser tab; the site states no count for the section — a classifieds site (Sell, Jobs) whose `/en/jobs` landing carries the category list and whose ads live under `/en/c-jobs`; no JobPosting on the listing; the rules as on the 12th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: none the site states — no total on the section or its landing; 52 is one page's links, not a count · 2026-09-13 -->
<!-- route: browser · 52 · 2026-09-13 -->

**Measured 2026-09-12 at 12:22:46Z UTC for #233, lot 6 — a measurement of the
transport, not a decision about the host.** Every fetch under the declared
identity, the guard on the exact path first, by `bin/fetch-body.py
--allow-refusal` — the four records carry the status, the bytes, the md5 and
the `cf-ray` that answered.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 2380 B, md5 34e7e26aeb9f both times — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True
```

*The file is Cloudflare's managed content block — the `Content-Signal` preamble and nine named crawlers refused, `ClaudeBot` among them — followed by the operator's own lines (2 380 B in all).* Before the decision this host was read as closed by name; the decision reopened it on paper, and this card is the first time its transport was asked under the permitted token.

## The transport — a static 403, the provider default

```
GET https://www.khmer24.com/             403, 25 B, md5 9ccabba20b9f    (12:22:46Z)
GET https://www.khmer24.com/             403, 25 B, md5 9ccabba20b9f    (second fetch)
GET https://www.khmer24.com/en/jobs     403, 25 B, md5 9ccabba20b9f    (12:24:54Z)
GET https://www.khmer24.com/en/jobs     403, 25 B, md5 9ccabba20b9f    (second fetch)
```

**Same size, same md5 on four fetches, root and listing alike — a static
body, and it is the 25-byte default served by the same provider on unrelated
hosts** (`www.jobstore.com`, `www.hays.fr`, `kariera.mk`, `www.tala-com.com`,
`sptojobslink.com`, and the five of lot 1: the same bytes,
`9ccabba20b9f4ec7d18bd6644579e5bf`). *A body shared between unrelated
hosts is a provider default, not a page anyone wrote for this host.* **The
rules permit and the transport refuses the client: family (1) of #222 — the
case where a browser is legitimate** (#66: it changes the layer, not the
permission). Not measured here: this session has no browser instrument; an
OPEN under a real browser would make this host a candidate for a browser
adapter, and that is the pilot's to assign.

## 2026-09-13 11:00 UTC — the browser route, MEASURED (#222): a classifieds section with no stated total

```
navigate /en/jobs          200 «in cambodia - www.khmer24.com» — 859 characters: the category list (/en/c-jobs-accounting, …), login, post
fetch /en/c-jobs           200 «Jobs in cambodia», 425 711 B — **52 distinct /en/<slug>-adid-<n>** links; filters (location, sort, salary); no count anywhere on the page
```

No challenge. **The section states no total**; the ad id is the `adid`
number. The procedure: guard → tab → `/en/c-jobs` and its pager (not
exercised) 1.5 s apart, collecting `-adid-<n>` → «n links, the site
states no total» → close. *One page read; the advertisement page not
opened.*

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches each of the root and a listing path, a static refusal.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.
- **Not an AfricaWork host**; the 25-byte refusal is the provider default shared with every static host of #233 — **the body says who fronts the site, not who runs it.** A classifieds site with a jobs section; the third Cambodian host of the lot, and the third static refusal.
