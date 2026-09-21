# Board measurement — Ministry of Labour (Guyana): open on 2026-09-21, served to the declared client, and NOT a board — its «Jobs Bank» page is one link to the National Job Bank on `jobs.gov.gy` (card `jobs-gov-gy.md`); refused at the transport on 2026-09-12, a broken WordPress to a browser on 2026-09-14

<!-- verified: 2026-09-21 -->

<!-- hosts: labour.gov.gy, www.labour.gov.gy -->
<!-- script: none -->
<!-- countries: GY -->
<!-- content: out-of-domain · **the ministry's WordPress is served to the declared client on 2026-09-21 — `/` 200 ×2 (06:32:49 UTC, 208–211 KB; the provider refusal of 2026-09-12 gone), `/jobs-bank/` 200 ×2 (06:33:09, 06:33:10 UTC; 128 760 B) — and lists nothing itself: the «Jobs Bank» page is a text about the National Job Bank whose one outbound link is `https://jobs.gov.gy/`, the board (measured the same minute, card `jobs-gov-gy.md`); rules read, `*` open, `ClaudeBot` still named and refused, no Crawl-delay; nothing to enumerate on this host** · 2026-09-21 -->
<!-- content-2026-09-12: indeterminate · 1 host, rules read twice and certain — `ClaudeBot` named and refused, `*` open, so `identity()` answers `claude-user` and since #230 `verdict()` sweeps under it — and the root and a listing path answer HTTP 403 to that client on 2 fetches each: 25 bytes, md5 `9ccabba20b9f` all four times — the static provider default (`Your request was blocked.`), the same bytes as `www.jobstore.com` and `www.hays.fr`; nothing of the site was read · 2026-09-12 11:56 UTC -->
<!-- witness: the page text and its one outbound link — the board is another host, `jobs.gov.gy`, measured on its own card; nothing to enumerate here · 2026-09-21 -->
<!-- route-2026-09-14: none · WordPress «critical error» on every path in a browser, the provider 403 to the client · superseded 2026-09-21 -->

**Measured 2026-09-12 at 11:56:58Z UTC for #233, lot 5 — a measurement of the
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

## The transport — a static 403, the provider default

```
GET https://labour.gov.gy/               403, 25 B, md5 9ccabba20b9f    (11:56:58Z)
GET https://labour.gov.gy/               403, 25 B, md5 9ccabba20b9f    (second fetch)
GET https://labour.gov.gy/vacancies     403, 25 B, md5 9ccabba20b9f    (11:58:12Z)
GET https://labour.gov.gy/vacancies     403, 25 B, md5 9ccabba20b9f    (second fetch)
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
- **A ministry, under the bare 1 836-byte managed block, refusing with the provider default** — whether a job bank lives on this host or on another (as Barbados' does, `labour-gov-bb`) is not established: nothing was served. *Not a verdict; a 403 to the plain client, browser not measured.*

## Browser reading, 2026-09-14 09:09–09:11 UTC (#314)

The extension answered this session, so the browser route named above was
measured: a tab on `https://labour.gov.gy/`, then `www.labour.gov.gy/`,
`/vacancies`, `/wp-json/wp/v2/pages`, and the root again five minutes later.
**Every one of them was served — no provider 403 to a browser — and every
one of them is the same page: «WordPress › Error — There has been a critical
error on this website. Learn more about troubleshooting WordPress.»** The
managed 403 is for the client only; behind it the site is down today.

So: the browser route is confirmed legitimate and open, and it leads to
nothing — `route: none` with this reason, dated, not a verdict on the
host (§2 sexies). Whether the ministry publishes vacancies here is still
unknown; the Barbadian counterpart (`labour-gov-bb`) points elsewhere.
**Next control 2026-09-21**: the same tab on the root; if WordPress answers,
the measurement is the usual one (the list, its count, a stable key, a
JobPosting or not) and `route: browser · N · date` replaces the line.

## The control three days on — the site answers, and the job bank lives on `jobs.gov.gy`

```
GET https://labour.gov.gy/             200 ×2 (06:32:49 UTC) — «Ministry of Labour and Manpower Planning», WordPress up; the 25-byte refusal of 2026-09-12 is gone
GET https://labour.gov.gy/jobs-bank/   200 ×2 (06:33:09, 06:33:10 UTC) — «What is the National Job Bank?» … «View National Job Bank Portal» → https://jobs.gov.gy/
```

**The ministry's site is up and served to the plain client, and it is not
the board: it describes the National Job Bank and links to it.** The same
shape as Barbados (`labour-gov-bb.md` → `barbadosjobregister.gov.bb`):
`content: out-of-domain`, nothing to enumerate here. The board itself —
`jobs.gov.gy`, served, «187 Jobs Found» — is measured on `jobs-gov-gy.md`,
and #314 (the ministry's offers, if it publishes any) is lifted from
`blocked` on that reading: it does, on that host.
