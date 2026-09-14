# Board adapter — Skywalker (Greece): reopened by the 2026-09-07 doctrine, and the transport answers a challenge

<!-- verified: 2026-09-14 -->

<!-- hosts: www.skywalker.gr, skywalker.gr -->
<!-- script: none -->
<!-- countries: GR -->
<!-- content: indeterminate · 1 host, rules read twice and certain — `ClaudeBot` named and refused, `*` open, so `identity()` answers `claude-user` and since #230 `verdict()` sweeps under it — and the root and a listing path answer HTTP 403 to that client on 2 fetches each: 5642 bytes titled «Just a moment...», md5 `dd28c2fd29b0` then `91686e7b0ac0` at constant size — a challenge, nothing of the site was read · 2026-09-12 11:56 UTC -->
<!-- witness: the site's own «Βρέθηκαν 1375 Αποτελέσματα» on `/el/aggelies-ergasias`, read from a connected tab on page 1 and page 55 (10:28–10:31 UTC; no challenge shown) — 25 a page, `?page=2 … 55`, page 55 carrying 25: 55 × 25 = 1 375, equal; the footer's «561.617 Συνολικές αναρτημένες θέσεις εργασίας» is a lifetime total, not this count; nothing is served to the declared client (the moving «Just a moment…», never defeated) · 2026-09-14 -->
<!-- route: browser · 1375 · 2026-09-14 -->

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

## 2026-09-14 10:28–10:31 UTC — the challenge does not show to a connected tab

```
tab, /el                                   served — the home, the search form, popular searches
tab, /el/aggelies-ergasias                 served — «Βρέθηκαν 1375 Αποτελέσματα», 25 cards a page (title, municipality, contract, presence, a salary when stated — «από 1,100 εώς 1,400 € /μήνας μεικτά» —, the date), «Αποτελέσματα ανά σελίδα 10 / 25 / 50 / 100», pager ?page=2 … 55
tab, /el/aggelies-ergasias?page=55         served — «1375» again, 25 cards, the last page: 55 × 25 = 1 375, equal
cards                                      /el/aggelia-ergasias/<slug>; the ad page not read this session
```

**`route: browser · 1375 · 2026-09-14`.** What a session does from a tab:
`/el/aggelies-ergasias?page=N` (or the 100-a-page setting) to the last
page, the slug of `/el/aggelia-ergasias/<slug>` as the key, the card's own
date, place, contract and salary, the ad page for the rest. The footer's
«561.617» is the site's lifetime total, not the list's. No script: the
declared client is challenged (#404).

