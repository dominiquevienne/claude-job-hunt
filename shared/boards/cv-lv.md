# Board adapter — CV.lv (Latvia): reopened by the 2026-09-07 doctrine, and the transport refuses the client with a static 403 — and served to a browser

<!-- verified: 2026-09-13 -->

<!-- hosts: www.cv.lv, cv.lv -->
<!-- script: none -->
<!-- countries: LV -->
<!-- content: measured · **2 286 advertisements stated by the site** — «Rādīt 2286 rezultātus» on `/lv/search`, and the same stack's API from the tab: `/api/v1/vacancy-search-service/search?limit=1&offset=0` → `total 2276`, `…&showHidden=true` → `total 2286` — the UI's figure is the `showHidden` one, exactly as on `cv.ee`; read from a connected browser tab; the rules as on the 12th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: the site's own `total` in its search API, read twice with and without `showHidden` from the tab, and the UI's «Rādīt 2286 rezultātus» matching the second — three figures, two questions, all stated · 2026-09-13 -->
<!-- route: browser · 2286 · 2026-09-13 -->

**Measured 2026-09-12 at 12:06:59Z UTC for #233, lot 6 — a measurement of the
transport, not a decision about the host.** Every fetch under the declared
identity, the guard on the exact path first, by `bin/fetch-body.py
--allow-refusal` — the four records carry the status, the bytes, the md5 and
the `cf-ray` that answered.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 1875 B, md5 223cfe58b143 both times — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True
```

*The file is Cloudflare's managed content block — the `Content-Signal` preamble and nine named crawlers refused, `ClaudeBot` among them — followed by the operator's own lines (1 875 B in all) — the same file shape as `www.cv.ee`.* Before the decision this host was read as closed by name; the decision reopened it on paper, and this card is the first time its transport was asked under the permitted token.

## The transport — a static 403, the provider default

```
GET https://www.cv.lv/                                                           403, 25 B, md5 9ccabba20b9f    (12:06:59Z)
GET https://www.cv.lv/                                                           403, 25 B, md5 9ccabba20b9f    (second fetch)
GET https://www.cv.lv/api/v1/vacancy-search-service/search?limit=1&offset=0     403, 25 B, md5 9ccabba20b9f    (12:07:02Z)
GET https://www.cv.lv/api/v1/vacancy-search-service/search?limit=1&offset=0&showHidden=true     403, 25 B, md5 9ccabba20b9f    (second fetch, the flag added)
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

## 2026-09-13 10:48 UTC — the browser route, MEASURED (#222): the CV-Online stack, and `showHidden` again

One Claude-in-Chrome tab, the guard on `/lv/search` and the API path first
(`*` open, certain). **No challenge** — the 25-byte 403 goes to the
declared client alone.

```
navigate /lv/search                                          200 «Vakanču meklēšana | CV-Online» — **«Rādīt 2286 rezultātus»**
fetch /api/v1/vacancy-search-service/search?limit=1&offset=0                  200 — total **2 276**; vacancies[0]: id, positionTitle, positionContent, employerId, employerName, publishDate, renewedDate, expirationDate, workTimes, …
fetch …&showHidden=true                                                        200 — total **2 286** = the UI's figure
```

**The same API as `cv.ee`, with the same `showHidden` behaviour** — the
UI counts with hidden ones, the default API call without; the difference
is ten here. `cvonline.py --host www.cv.lv` is the adapter the day the
declared client is served (it was refused on the 12th); from a tab the
procedure is the same calls the page makes: guard → tab → the two totals →
`limit=…&offset=…` pages → **«n emitted, site states 2 286 (2 276 without
hidden)»** → close.

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches each of the root and a listing path, a static refusal.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.
- **CV-Online's stack** (`www.cv.ee`, shipped as `cvonline.py`; `www.cvonline.lt`): the same rules shape and the same Next.js search service — **and this host refuses the client where `cv.ee` serves it, in the same minute.** The adapter accepts `--host www.cv.lv` and names this refusal; the country is declared nowhere until a transport answers.
