# Board adapter — INFOTEP (Dominican Republic): reopened by the 2026-09-07 doctrine, and the transport answers a challenge

<!-- verified: 2026-09-12 -->

<!-- hosts: www.infotep.gob.do, infotep.gob.do -->
<!-- script: none -->
<!-- countries: DO -->
<!-- content: indeterminate · 1 host, rules read twice and certain — `ClaudeBot` named and refused, `*` open, so `identity()` answers `claude-user` and since #230 `verdict()` sweeps under it — and the root and a listing path answer HTTP 403 to that client on 2 fetches each: 6160 bytes titled «Attention Required! | Cloudflare», md5 `6a38c5509346` then `e24276e5e6c2` at constant size — a challenge, nothing of the site was read · 2026-09-12 11:00 UTC -->
<!-- witness: none — nothing was served -->

**Measured 2026-09-12 at 11:00:36Z UTC for #233, lot 3 — a measurement of the
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
GET https://www.infotep.gob.do/            403, 6160 B, md5 6a38c5509346    (11:00:36Z)
GET https://www.infotep.gob.do/            403, 6160 B, md5 e24276e5e6c2    (second fetch)
GET https://www.infotep.gob.do/empleo     403, 6160 B, md5 784f808d7ead    (11:02:06Z)
GET https://www.infotep.gob.do/empleo     403, 6160 B, md5 823d4681ec85    (second fetch)
```

**Same size, different md5 on two fetches of the same URL, «Attention
Required! | Cloudflare» — a challenge**, the `revolico` / `mabumbe` /
`sudancareers` family. *Masking the 16-hex `cf-ray` in the two bodies leaves
ten differing lines, and every one is an edge stamp: the Rocket Loader nonce
on four `<script type>` attributes, a beacon `<script>` present in one body
only, and the base64 timestamp in `__CF$cv$params` — nothing of the site.* *The comparison across hosts is void (the
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
- **Not an AfricaWork host** — the state's technical-training institute, under the same 1 836-byte managed block as the franchise; its challenge page is 6 160 B where the franchise ones are 5 508–5 515 B (Rocket Loader nonces in this one), and the `revolico` reading holds: a challenge is a challenge whatever the operator.
