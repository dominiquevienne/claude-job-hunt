# Board measurement — Emploi Bénin (`www.emploibenin.com`, Benin): 403 to the declared client, served to a tab — 177 of 177

<!-- verified: 2026-09-13 -->

<!-- hosts: www.emploibenin.com, emploibenin.com -->
<!-- script: none -->
<!-- countries: BJ -->
<!-- content: measured · **177 distinct advertisement addresses** over `/recherche-jobs-benin?page=0…` (7 × 25 + 2; the next page empty), read from a connected browser tab, **against «177 Offres d'emploi trouvées» stated by the page — equal**; the pager is zero-based, as on every AfricaWork host read since `ghanajob.md`; the rules as on the 11th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: the page's own «177 Offres d'emploi trouvées», read on every page and printed beside the distinct count («177 emitted, site states 177 — equal»); the declared client's 25-byte 403 on the same path, the family's vendor default · 2026-09-13 -->
<!-- route: browser · 177 · 2026-09-13 -->

**Measured 2026-09-11 at 22:10:39Z UTC for #233, lot 1 — a measurement of the
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
GET https://www.emploibenin.com/     403, 25 B, md5 9ccabba20b9f    (22:10:39Z)
GET https://www.emploibenin.com/     403, 25 B, md5 9ccabba20b9f    (second fetch)
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

## 2026-09-13 16:36 UTC — the browser route, MEASURED (#222): 177 of 177

```
tab: /                                   200 «Offres d´Emploi et Recrutement au Bénin» — no challenge; the home page links /recherche-jobs-benin
tab: fetch /recherche-jobs-benin?page=0…8     25 × 7 · 2 · 0  →  **177 distinct data-href addresses**, «177 Offres d'emploi trouvées» — **equal**; every address carries its id
```

**The procedure is `ghanajob.md`'s six steps** — guard on the exact listing path (`*` open, certain), one tab, `fetch('?page=0,1,2…')` 1.5 s apart until a page carries no card, the site's own «N Offres d'emploi trouvées» read on every page and printed beside the distinct count. The declared client gets the family's 25-byte 403 (md5 `9ccabba20b9f…`) on the same path — the vendor's default, for the client alone. **The cards are keyed by their `data-href` address, not by a trailing number**: on `emploi.cd` six of seventy addresses carry no id at all (`…/retail-operations-specialist-local-congolese`), and a reader keyed on the number printed «64 emitted, site states 70 — 6 short» with nothing else wrong — the same shape as `gulftalent.md`'s two address shapes, found the same day.
