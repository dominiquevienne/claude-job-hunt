# Board adapter — Skywalker (Greece): reopened by the 2026-09-07 doctrine, and the transport answers a challenge

<!-- verified: 2026-09-12 -->

<!-- hosts: www.skywalker.gr, skywalker.gr -->
<!-- script: none -->
<!-- countries: GR -->
<!-- content: indeterminate · 1 host, rules read twice and certain — `ClaudeBot` named and refused, `*` open, so `identity()` answers `claude-user` and since #230 `verdict()` sweeps under it — and the root and a listing path answer HTTP 403 to that client on 2 fetches each: 5642 bytes titled «Just a moment...», md5 `dd28c2fd29b0` then `91686e7b0ac0` at constant size — a challenge, nothing of the site was read · 2026-09-12 11:56 UTC -->
<!-- witness: none — nothing was served -->

**Measured 2026-09-12 at 11:56:45Z UTC for #233, lot 5 — a measurement of the
transport, not a decision about the host.** Every fetch under the declared
identity, the guard on the exact path first, by `bin/fetch-body.py
--allow-refusal` — the four records carry the status, the bytes, the md5 and
the `cf-ray` that answered.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 2945 B, md5 e31260c3dad9 both times — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True
```

*The file is Cloudflare's managed content block — the `Content-Signal` preamble and nine named crawlers refused, `ClaudeBot` among them — followed by the operator's own lines, among them `Crawl-delay: 10` — honoured on every request here (2 945 B in all).* Before the decision this host was read as closed by name; the decision reopened it on paper, and this card is the first time its transport was asked under the permitted token.

## The transport — a Cloudflare challenge

```
GET https://www.skywalker.gr/                       403, 5642 B, md5 dd28c2fd29b0    (11:56:45Z)
GET https://www.skywalker.gr/                       403, 5642 B, md5 91686e7b0ac0    (second fetch)
GET https://www.skywalker.gr/aggelies-ergasias     403, 5714 B, md5 bc691d04b9d8    (11:57:59Z)
GET https://www.skywalker.gr/aggelies-ergasias     403, 5714 B, md5 703f4b5f4ce1    (second fetch)
```

**Same size, different md5 on two fetches of the same URL, «Just a moment...» — a challenge**, the `revolico` / `mabumbe` /
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
- **Not an AfricaWork host**; the «Just a moment...» page is the `revolico` form of the challenge (5 642 B, a `cf-ray` and a timestamp in the body), where the `sudancareers` form says «Attention Required!». **Borne 2 stops here either way.**
