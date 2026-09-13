# Board measurement — Job Cameroun (`www.job-cameroun.com`, Cameroon): not an AfricaWork host at all — a classifieds-style board served to a tab, 3 982 of 3 982 over 200 pages

<!-- verified: 2026-09-13 -->

<!-- hosts: www.job-cameroun.com, job-cameroun.com -->
<!-- script: none -->
<!-- countries: CM -->
<!-- content: measured · **3 982 distinct advertisement ids** over `/offres?page=1…200` (199 × 20 + 2; page 201 empty), read from a connected browser tab 16:38–16:48 UTC, **against «3,982 offres trouvées» stated on every page — equal**; a one-based pager of 20, `/offre/<id>-<slug>` addresses, a JobPosting per advertisement (validThrough = datePosted + 30 days on the one read, employer «Recruteur privé — <town>», salary null, applications by WhatsApp in the body); **this is not AfricaWork** — the 25-byte 403 the declared client gets on `/` is the same vendor default, but the site behind it is a classifieds-style board of its own; the rules as on the 11th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: the page's own «3,982 offres trouvées», read on every one of the 200 pages and printed beside the distinct count («3 982 emitted, site states 3 982 — equal»); the declared client's 25-byte 403 on `/`, the vendor default · 2026-09-13 -->
<!-- route: browser · 3982 · 2026-09-13 -->

**Measured 2026-09-11 at 22:10:43Z UTC for #233, lot 1 — a measurement of the
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
GET https://www.job-cameroun.com/     403, 25 B, md5 9ccabba20b9f    (22:10:43Z)
GET https://www.job-cameroun.com/     403, 25 B, md5 9ccabba20b9f    (second fetch)
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

## 2026-09-13 16:38–16:48 UTC — the browser route, MEASURED (#222): served, one-based, 3 982 of 3 982

```
tab: /                          200 «Offres d'emploi au Cameroun 2026 — Trouvez un poste sur Job Cameroun» — no challenge; «3,982 postes disponibles»; JSON-LD WebSite; links /offres, /offres?categorie=<btp|sante|education|…>, /offres-douala/
tab: fetch /offres              200, 45 721 B — «3,982 offres trouvées», 20 /offre/<id>-<slug> links, pager ?page=2, ?page=3 (ONE-based, unlike the AfricaWork hosts)
tab: fetch /offres?page=1…201   20 × 199 · 2 · 0  →  **3 982 distinct ids** (ids 4 379 → …), «3,982 offres trouvées» on every page — **equal**; 201 requests 1.5 s apart, 10 min 40 s
tab: fetch /offre/4379-…        200, 30 421 B — JobPosting: title · datePosted 2026-09-13 · validThrough 2026-10-13 · employmentType FULL_TIME · hiringOrganization «Recruteur privé — Dschang» · jobLocation {Dschang, CM, postalCode 00000} · baseSalary null; the body carries a phone number and «Contact : +237 …» — a classifieds board, applications by WhatsApp
```

**This card called the host AfricaWork on the 11th, from the 25-byte 403 the declared client gets — the family's vendor default.** The body behind that default is not the family's template: no `/recherche-jobs-<country>`, a one-based `?page=N` of 20, `/offre/<id>-<slug>`, categories by query string, a «Publier une offre» button and a phone number in every advertisement. **A refusal body identifies the vendor, never the site** — `bestzambiajobs.md` said it first, and this is the second host where it mattered. The procedure that fits is the plain pager walk, not `ghanajob.md`'s six steps (zero-based); the witness is the same — the page's own count beside the distinct count, equal on the day.
