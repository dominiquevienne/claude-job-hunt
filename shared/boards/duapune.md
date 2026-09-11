# Board adapter — Duapune (Albania): reopened by the 2026-09-07 doctrine, and the transport refuses the client with a static 403

<!-- verified: 2026-09-11 -->

<!-- hosts: duapune.com -->
<!-- script: none -->
<!-- countries: AL -->
<!-- content: indeterminate · 1 host, rules read twice and certain — `ClaudeBot` named and refused, `*` open, so `identity()` answers `claude-user` and since #230 `verdict()` sweeps under it — and the root answers HTTP 403 to that client on 2 fetches: 25 bytes, md5 `9ccabba20b9f` both times — the static provider default (`Your request was blocked.`), the same bytes as `www.jobstore.com` and `www.hays.fr`; nothing of the site was read · 2026-09-11 22:10 UTC -->
<!-- witness: none — nothing was served -->

**Measured 2026-09-11 at 22:10:56Z UTC for #233, lot 1 — a measurement of the
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

## The transport — a static 403, the provider default

```
GET https://duapune.com/     403, 25 B, md5 9ccabba20b9f    (22:10:56Z)
GET https://duapune.com/     403, 25 B, md5 9ccabba20b9f    (second fetch)
```

**Same size, same md5 on two fetches — a static body, and it is the 25-byte
default served by the same provider on unrelated hosts** (`www.jobstore.com`,
`www.hays.fr`, `kariera.mk`, `www.tala-com.com`, `sptojobslink.com`: the same
bytes, `9ccabba20b9f4ec7d18bd6644579e5bf`). *A body shared between unrelated
hosts is a provider default, not a page anyone wrote for this host.* **The
rules permit and the transport refuses the client: family (1) of #222 — the
case where a browser is legitimate** (#66: it changes the layer, not the
permission). Not measured here: this session has no browser instrument; an
OPEN under a real browser would make this host a candidate for a browser
adapter, and that is the pilot's to assign.

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches of the root, a static refusal.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.
