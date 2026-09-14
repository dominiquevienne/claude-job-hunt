# Board measurement — Emploi.cm (`www.emploi.cm`, Cameroon): 403 to the declared client; a challenge to the tab on 2026-09-13, the whole board to the tab on 2026-09-14 — «405 Offres d'emploi trouvées», `route: browser`

<!-- verified: 2026-09-14 -->

<!-- hosts: www.emploi.cm, emploi.cm -->
<!-- script: none -->
<!-- countries: CM -->
<!-- content: measured · **a Cloudflare challenge to a real browser** — the tab on `/` renders «Un instant…» (28 580 characters of interstitial) and is still on it 10 s later, 16:35 UTC; nothing of the board was read by any client; the declared client's 25-byte 403 on the same path as on the 11th; the rules as on the 11th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230; the fifth of the five AfricaWork hosts read that day, the only one to challenge a browser — the tab was not asked to wait past ten seconds · 2026-09-13 -->
<!-- witness: the site's own «405 Offres d'emploi trouvées» on `/recherche-jobs-cameroun`, read from a connected tab (no interstitial today, 2026-09-14 09:58 UTC) — 25 a page, a zero-based pager to `?page=16` carrying 5: 16 × 25 + 5 = 405, equal; the front page's «3637 postes ouverts» is another figure (positions), not this count; nothing is served to the declared client (403, 25 B) · 2026-09-14 -->
<!-- route: browser · 405 · 2026-09-14 -->

**Measured 2026-09-11 at 22:10:46Z UTC for #233, lot 1 — a measurement of the
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
GET https://www.emploi.cm/     403, 25 B, md5 9ccabba20b9f    (22:10:46Z)
GET https://www.emploi.cm/     403, 25 B, md5 9ccabba20b9f    (second fetch)
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
- **AfricaWork family**: the same rules file (1 836 B) and the same refusal
  to the byte as `www.emploibenin.com`, `www.job-cameroun.com`, `www.emploi.cm`
  and `www.emploisenegal.com` — one fingerprint dates the family; the other
  members need one read each to be dated, not to be classified.

## 2026-09-13 16:35 UTC — the browser route, MEASURED (#222): a challenge to the tab, and it stays

```
tab: /            «Un instant…» — a Cloudflare interstitial, 28 580 characters; re-read 8 s later: the same title, the same page, no listing link in it
```

**Borne 2 of the 2026-09-07 doctrine**: a challenge is where the browser branch stops; the plugin neither defeats one nor asks the user to. The four sister hosts read in the same ten minutes (`emploi.cd`, `emploibenin`, `emploisenegal`, and `job-cameroun`, which is not AfricaWork) were served without one — so the challenge is this host's setting, not the family's. **Not a verdict that the host is closed** — the owner's, on his express validation; recorded: one tab, ten seconds, one day.

## 2026-09-14 09:58–10:02 UTC — no interstitial today; the board from a tab

The tab that got «Un instant…» on 2026-09-13 is served at once today:

```
tab, /                                       served — «Trouvez votre futur job parmi 3637 postes ouverts» (positions, not the list's count), 10 regions, 17 trades, the latest ads
tab, /recherche-jobs-cameroun                served — «405 Offres d'emploi trouvées», 25 cards /offre-emploi-cameroun/<slug>-<id>, pager ?page=1 … 16 (zero-based)
tab, /recherche-jobs-cameroun?page=16        served — 5 cards, the last: 16 × 25 + 5 = 405, equal to the statement
tab, /offre-emploi-cameroun/<slug>-1226742   served — two JSON-LD blocks the browser's JSON.parse rejects (the AfricaWork form; `_ldjson`'s repair reads them on the sister hosts)
```

**`route: browser · 405 · 2026-09-14`** — the AfricaWork procedure from a
tab (`africawork.py`'s walk driven from the tab: the zero-based pager, the
id from the address tail, the count the page prints beside the walk, the
repaired JobPosting). The declared client still gets the provider's
25-byte 403. The interstitial of 2026-09-13 was a reading of that day, not
a property of the host.

