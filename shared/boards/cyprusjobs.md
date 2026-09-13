# Board adapter — CyprusJobs (Cyprus): reopened by the 2026-09-07 doctrine, and the transport refuses the client with a static 403 — and served to a browser

<!-- verified: 2026-09-13 -->

<!-- hosts: www.cyprusjobs.com, cyprusjobs.com -->
<!-- script: none -->
<!-- countries: CY -->
<!-- content: measured · **208 advertisements stated by the site** — «Found 208 Jobs» on `/en/listing` (the `/jobs` path redirects there), 20 advertisement links a page under `/en/listing/…`, a pager on the query string; page 1 read from a connected browser tab; the rules as on the 12th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: the site's own «Found 208 Jobs» on its listing; the walk to confirm it was not made · 2026-09-13 -->
<!-- route: browser · 208 · 2026-09-13 -->

**Measured 2026-09-12 at 11:00:33Z UTC for #233, lot 3 — a measurement of the
transport, not a decision about the host.** Every fetch under the declared
identity, the guard on the exact path first, by `bin/fetch-body.py
--allow-refusal` — the four records carry the status, the bytes, the md5 and
the `cf-ray` that answered.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 1860 B, md5 2a0812ac5756 both times — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True
```

*The file is Cloudflare's managed content block — the `Content-Signal` preamble and nine named crawlers refused, `ClaudeBot` among them — followed by one operator group, `User-agent: * / Disallow:` — empty, everything open (1 860 B in all).* Before the decision this host was read as closed by name; the decision reopened it on paper, and this card is the first time its transport was asked under the permitted token.

## The transport — a static 403, the provider default

```
GET https://www.cyprusjobs.com/          403, 25 B, md5 9ccabba20b9f    (11:00:33Z)
GET https://www.cyprusjobs.com/          403, 25 B, md5 9ccabba20b9f    (second fetch)
GET https://www.cyprusjobs.com/jobs     403, 25 B, md5 9ccabba20b9f    (11:02:04Z)
GET https://www.cyprusjobs.com/jobs     403, 25 B, md5 9ccabba20b9f    (second fetch)
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

## 2026-09-13 10:56 UTC — the browser route, MEASURED (#222): the count on the listing

```
navigate /jobs            -> /en/listing, 200 «Jobs in Cyprus - Cyprus Jobs» — **«Found 208 Jobs»** · 20 advertisement links · /el/listing the Greek edition
```

No challenge; the 25-byte 403 is for the declared client alone. **208 is
the site's count**; the procedure: guard → tab → read «Found N Jobs» →
walk the pager (query-string pages) 1.5 s apart → «n emitted, site
states N» → close. *One page of 20 read; the advertisement page not
opened.*

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches each of the root and a listing path, a static refusal.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.
- **Not an AfricaWork host** (#233: «another managed block naming ClaudeBot»); the sibling `www.cypruswork.com`, measured in the same minute of this lot, **answers 200 under the same managed block** — the rules file predicts nothing about the transport, which is why each host got its own dated read.
