# Board adapter — CV-Online.lt (Lithuania): reopened by the 2026-09-07 doctrine, and the transport refuses the client with a static 403 — and served to a browser

<!-- verified: 2026-09-13 -->

<!-- hosts: www.cvonline.lt, cvonline.lt -->
<!-- script: none -->
<!-- countries: LT -->
<!-- content: measured · **3 590 advertisements stated by the site** — «Rodyti 3590 rezultatus» on `/lt/search`, and the same stack's API from the tab: `/api/v1/vacancy-search-service/search?limit=1&offset=0` → `total 1650`, `…&showHidden=true` → `total 3590` — the UI's figure is the `showHidden` one, as on `cv.ee` and `cv.lv`, and here the two differ by 1 940; the rules as on the 12th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: the site's own `total` in its search API, read with and without `showHidden` from the tab, the UI's «Rodyti 3590 rezultatus» matching the second · 2026-09-13 -->
<!-- route: browser · 3590 · 2026-09-13 -->

**Measured 2026-09-12 at 12:07:02Z UTC for #233, lot 6 — a measurement of the
transport, not a decision about the host.** Every fetch under the declared
identity, the guard on the exact path first, by `bin/fetch-body.py
--allow-refusal` — the four records carry the status, the bytes, the md5 and
the `cf-ray` that answered.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 1881 B, md5 77c75bedd305 both times — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True
```

*The file is Cloudflare's managed content block — the `Content-Signal` preamble and nine named crawlers refused, `ClaudeBot` among them — followed by the operator's own lines (1 881 B in all) — the same file shape as `www.cv.ee`, and `Content-Signal: search=yes, ai-train=no, use=reference`: the use here is reference, and nothing here trains.* Before the decision this host was read as closed by name; the decision reopened it on paper, and this card is the first time its transport was asked under the permitted token.

## The transport — a static 403, the provider default

```
GET https://www.cvonline.lt/                                                           403, 25 B, md5 9ccabba20b9f    (12:07:02Z)
GET https://www.cvonline.lt/                                                           403, 25 B, md5 9ccabba20b9f    (second fetch)
GET https://www.cvonline.lt/api/v1/vacancy-search-service/search?limit=1&offset=0     403, 25 B, md5 9ccabba20b9f    (12:07:05Z)
GET https://www.cvonline.lt/api/v1/vacancy-search-service/search?limit=1&offset=0&showHidden=true     403, 25 B, md5 9ccabba20b9f    (second fetch, the flag added)
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

## 2026-09-13 10:59 UTC — the browser route, MEASURED (#222): the CV-Online stack, and the largest `showHidden` gap of the three

```
navigate /lt/search                                              200 «Darbo paieška | CV-Online» — **«Rodyti 3590 rezultatus»**
fetch /api/v1/vacancy-search-service/search?limit=1&offset=0     200 — total **1 650**
fetch …&showHidden=true                                          200 — total **3 590** = the UI's figure
```

No challenge. **The same API and the same `showHidden` behaviour as
`cv.ee` and `cv.lv`** — and here the hidden ones are more than half:
1 650 shown by default, 3 590 with them. Which of the two a scan should
count is the `cv.ee` card's question, answered there; the adapter is
`cvonline.py --host www.cvonline.lt` the day the declared client is
served, and from a tab the same calls the page makes.

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches each of the root and a listing path, a static refusal.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.
- **CV-Online's stack** (`www.cv.ee`, shipped as `cvonline.py`; `www.cv.lv`): the same rules shape and the same Next.js search service — **and this host refuses the client where `cv.ee` serves it, in the same minute.** The adapter accepts `--host www.cvonline.lt` and names this refusal; the country is declared nowhere until a transport answers.
