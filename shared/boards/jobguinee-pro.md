# Board adapter — JobGuinée Pro (Guinea): reopened by the 2026-09-07 doctrine, and the transport refuses the client with a static 403

<!-- verified: 2026-09-14 -->

<!-- hosts: www.jobguinee-pro.com, jobguinee-pro.com -->
<!-- script: none -->
<!-- countries: GN -->
<!-- content: indeterminate · 1 host, rules read twice and certain — `ClaudeBot` named and refused, `*` open, so `identity()` answers `claude-user` and since #230 `verdict()` sweeps under it — and the root and a listing path answer HTTP 403 to that client on 2 fetches each: 25 bytes, md5 `9ccabba20b9f` all four times — the static provider default (`Your request was blocked.`), the same bytes as `www.jobstore.com` and `www.hays.fr`; nothing of the site was read · 2026-09-12 10:55 UTC -->
<!-- witness: the site's own «493 offres d'emploi disponibles en Guinée» and «Affichage de 1–20 sur 493 offres» on `/jobs`, read from a connected tab (no challenge, 2026-09-14 10:59–11:02 UTC); the home's category counts («42 offres», «15 offres» …); 20 cards a page, the pager a client control (no `?page=` address); nothing is served to the declared client (403, 25 B, the provider default) · 2026-09-14 -->
<!-- route: browser · 493 · 2026-09-14 -->

**Measured 2026-09-12 at 10:55:06Z UTC for #233, lot 2 — a measurement of the
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
GET https://www.jobguinee-pro.com/                           403, 25 B, md5 9ccabba20b9f    (10:55:06Z)
GET https://www.jobguinee-pro.com/                           403, 25 B, md5 9ccabba20b9f    (second fetch)
GET https://www.jobguinee-pro.com/recherche-jobs-guinee     403, 25 B, md5 9ccabba20b9f    (10:56:05Z)
GET https://www.jobguinee-pro.com/recherche-jobs-guinee     403, 25 B, md5 9ccabba20b9f    (second fetch)
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
- **AfricaWork franchise**: the same rules file (1836 B, md5 `c6370d4bc025`) as
  `www.emploibenin.com`, `www.emploi.cm`, `www.emploisenegal.com` and the
  other members of lot 1 — **this is one read of this host, dated, not a
  verdict copied from a sibling**: two members of this very lot answer a
  challenge where the other five answer the static default, under one and the
  same rules file.

## 2026-09-14 10:59–11:02 UTC — served to a connected tab

```
tab, /                      served — the home (jobguinee-pro.com without www), category counts («42 offres», «15 offres» …), /offres, /jobs
tab, /offres                served — a hub page (no cards)
tab, /jobs                  served — «493 offres d'emploi disponibles en Guinée», «Affichage de 1–20 sur 493 offres», the town facets (Conakry's communes among them), sort by relevance / newest / most viewed / salary; 20 cards a page, the pager a client control
```

**`route: browser · 493 · 2026-09-14`** — the list's own count. What a
session does from a tab: `/jobs`, the pager clicked to the end (no
address per page), the card's link as the key, the ad page for the text.
No script: the declared client gets the provider's 25-byte 403 (#404).
Guinea's other board, EmploiGuinée, is `route: browser · 57` the same
day.

