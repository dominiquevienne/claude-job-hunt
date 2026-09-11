# Board adapter — Sudan Careers (Sudan): reopened by the 2026-09-07 doctrine, and the transport answers a challenge

<!-- verified: 2026-09-11 -->

<!-- hosts: www.sudancareers.com, sudancareers.com -->
<!-- script: none -->
<!-- countries: SD -->
<!-- content: indeterminate · 1 host, rules read twice and certain — `ClaudeBot` named and refused, `*` open, so `identity()` answers `claude-user` and since #230 `verdict()` sweeps under it — and the root answers HTTP 403 to that client on 2 fetches: 5515 bytes titled «Attention Required! | Cloudflare», md5 `0130507effc9` then `719805e27b1a` at constant size — a challenge, nothing of the site was read · 2026-09-11 22:10 UTC -->
<!-- witness: none — nothing was served -->

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
