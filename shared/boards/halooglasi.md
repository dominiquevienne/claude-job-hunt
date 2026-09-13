# Board adapter — Halo oglasi (Serbia): reopened by the 2026-09-07 doctrine, and the transport refuses the client with a static 403 — and served to a browser

<!-- verified: 2026-09-13 -->

<!-- hosts: www.halooglasi.com, halooglasi.com -->
<!-- script: none -->
<!-- countries: RS -->
<!-- content: measured · **476 advertisements stated by the site** — the search form's own button «Prikaži 476 oglasa» on `/posao`, the listing `/posao/ponuda-poslova-pretraga` with `/posao/<category>/<slug>/<id>?kid=4` addresses (41 on its first page) and a map note «only the first 300 results are shown on the map»; read from a connected browser tab; no JobPosting on the listing (an Organization only); the rules as on the 12th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: the site's own «Prikaži 476 oglasa» — the count its search button carries with no filter set; the walk to confirm it was not made · 2026-09-13 -->
<!-- route: browser · 476 · 2026-09-13 -->

**Measured 2026-09-12 at 15:28:10Z UTC for #233, lot 7 — a measurement of the
transport, not a decision about the host.** Every fetch under the declared
identity, the guard on the exact path first, by `bin/fetch-body.py
--allow-refusal` — the four records carry the status, the bytes, the md5 and
the `cf-ray` that answered.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 2173 B, md5 51dca2040069 both times — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True
```

*The file is Cloudflare's managed content block — the `Content-Signal` preamble and nine named crawlers refused, `ClaudeBot` among them — followed by the operator's own lines (2 173 B in all).* Before the decision this host was read as closed by name; the decision reopened it on paper, and this card is the first time its transport was asked under the permitted token.

## The transport — a static 403, the provider default

```
GET https://www.halooglasi.com/           403, 25 B, md5 9ccabba20b9f    (15:28:10Z)
GET https://www.halooglasi.com/           403, 25 B, md5 9ccabba20b9f    (second fetch)
GET https://www.halooglasi.com/posao     403, 25 B, md5 9ccabba20b9f    (15:29:08Z)
GET https://www.halooglasi.com/posao     403, 25 B, md5 9ccabba20b9f    (second fetch)
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

## 2026-09-13 10:48 UTC — the browser route, MEASURED (#222): the count is on the button

One Claude-in-Chrome tab, the guard on `/posao` and
`/posao/ponuda-poslova-pretraga` first. **No challenge** — the 25-byte 403
goes to the declared client alone.

```
navigate /posao                          200 «Posao | Halo oglasi Posao» — the search form; its button reads **«Prikaži 476 oglasa»** with nothing set
fetch /posao/ponuda-poslova-pretraga     200 «Ponuda poslova» — 41 /posao/<category>/<slug>/<13-digit id>?kid=4 addresses; «na mapi je prikazano samo prvih 300 rezultata» (the map shows the first 300)
JSON-LD                                  Organization only on both pages
```

**476 is the site's count and the button is where it says it.** The
advertisement id is the 13-digit number in the address; the procedure a
session follows: guard → tab → read the button → walk the listing's pages
1.5 s apart (its pager was not exercised here), collecting the ids →
**«n emitted, site states 476»** → an advertisement page (not read) →
close. *Halo Oglasi is a classifieds site; `/posao` is its job section
and the only path this card concerns.*

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches each of the root and a listing path, a static refusal.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.
- **Not an AfricaWork host**; the 25-byte refusal is the provider default shared with every static host of #233 — **the body says who fronts the site, not who runs it.** A classifieds site with a jobs section; the only Serbian host of the 61.
