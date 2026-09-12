# Board adapter — CV.lv (Latvia): reopened by the 2026-09-07 doctrine, and the transport refuses the client with a static 403

<!-- verified: 2026-09-12 -->

<!-- hosts: www.cv.lv, cv.lv -->
<!-- script: none -->
<!-- countries: LV -->
<!-- content: indeterminate · 1 host, rules read twice and certain — `ClaudeBot` named and refused, `*` open, so `identity()` answers `claude-user` and since #230 `verdict()` sweeps under it — and the root and a listing path answer HTTP 403 to that client on 2 fetches each: 25 bytes, md5 `9ccabba20b9f` all four times — the static provider default (`Your request was blocked.`), the same bytes as `www.jobstore.com` and `www.hays.fr`; nothing of the site was read · 2026-09-12 12:06 UTC -->
<!-- witness: none — nothing was served -->

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

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches each of the root and a listing path, a static refusal.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.
- **CV-Online's stack** (`www.cv.ee`, shipped as `cvonline.py`; `www.cvonline.lt`): the same rules shape and the same Next.js search service — **and this host refuses the client where `cv.ee` serves it, in the same minute.** The adapter accepts `--host www.cv.lv` and names this refusal; the country is declared nowhere until a transport answers.
