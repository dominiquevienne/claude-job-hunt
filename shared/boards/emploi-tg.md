# Board adapter — Emploi.tg (Togo): reopened by the 2026-09-07 doctrine, and the transport refuses the client with a static 403 — and served to a browser

<!-- verified: 2026-09-13 -->

<!-- hosts: www.emploi.tg, emploi.tg -->
<!-- script: none -->
<!-- countries: TG -->
<!-- content: measured · **130 distinct advertisement addresses** over `/recherche-jobs-togo?page=0…` (25 + 24 + 25 + 25 + 25 + 6; the next page empty), read from a connected browser tab, **against «131 Offres d'emploi trouvées» stated by the page — 1 short (a walk of a live board that posts as it is read; not a page missed: the walk started at zero)**; the pager is zero-based, as on every AfricaWork host read since `ghanajob.md`; the rules as on the 12th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: the page's own «131 Offres d'emploi trouvées», read on every page of the walk and printed beside the distinct count («130 emitted, site states 131 — 1 short») · 2026-09-13 -->
<!-- route: browser · 130 · 2026-09-13 -->

**Measured 2026-09-13 at 10:22:14Z UTC for #233, lot 8 — a measurement of the
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
GET https://www.emploi.tg/                         403, 25 B, md5 9ccabba20b9f    (10:22:14Z)
GET https://www.emploi.tg/                         403, 25 B, md5 9ccabba20b9f    (second fetch)
GET https://www.emploi.tg/recherche-jobs-togo     403, 25 B, md5 9ccabba20b9f    (10:23:22Z)
GET https://www.emploi.tg/recherche-jobs-togo     403, 25 B, md5 9ccabba20b9f    (second fetch)
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

## 2026-09-13 10:42 UTC — the browser route, MEASURED (#222): the 403 is for the declared client alone

One Claude-in-Chrome tab, the guard on `/recherche-jobs-togo` first (`*` open, certain).
**No challenge, no interstitial** — borne 0 held: the 25-byte 403 above goes
to the declared HTTP client and to nobody else.

```
navigate https://www.emploi.tg/recherche-jobs-togo      200 — «131 Offres d'emploi trouvées» · 25 cards a page · pager zero-based (the link labelled «2» is ?page=1)
fetch ?page=0, 1, 2 …  (25 + 24 + 25 + 25 + 25 + 6)        **130 distinct /offre-emploi-togo/<slug>-<id>** · the next page → 0 cards   10:42 UTC
                                       **130 emitted, site states 131 — 1 short.**
GET /offre-emploi-togo/charge-relation-client-hf-209530                  200 — a JobPosting in JSON-LD (datePosted 2026-09-11T13:55:01+00:00), the JSON rejected by a strict parser (control characters) — read tolerantly, as `ghanajob.md` says
```

**The procedure is `ghanajob.md`'s six steps with this host's two paths**
— `/recherche-jobs-togo` for the listing, `/offre-emploi-togo/<slug>-<id>` for the
advertisement (the id is the trailing number): guard → tab → `?page=0, 1,
2 …` until empty, 1.5 s apart → **«n emitted, site states N»** → the
JobPosting read tolerantly → close.

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches each of the root and a listing path, a static refusal.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.
- **AfricaWork franchise** (the same 1 836-byte managed block as `www.emploibenin.com`, `www.emploi.cm`) and the static default — **one read of this host, dated**: under this very file two lot-2 members answer a challenge instead.
