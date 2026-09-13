# Board adapter — Ezega (Ethiopia): reopened by the 2026-09-07 doctrine, and the transport refuses the client with a static 403 — and served to a browser

<!-- verified: 2026-09-13 -->

<!-- hosts: www.ezega.com, ezega.com -->
<!-- script: none -->
<!-- countries: ET -->
<!-- content: measured · **1 advertisement served** — the «Featured Jobs» strip on `/jobs/AllPostedJobs` carries one (Sales Engineer, KAMUR MODERN LIVING, Addis Ababa, Sep 08 2026) and the «Latest Jobs» list answers «No Active Jobs available for the selected criteria»; read from a connected browser tab; the site states no count; the rules as on the 12th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: the site's own sentence «No Active Jobs available for the selected criteria» under its latest-jobs table, beside one featured row — a zero the site states, not one a reader produced · 2026-09-13 -->
<!-- route: browser · 1 · 2026-09-13 -->

**Measured 2026-09-12 at 11:56:27Z UTC for #233, lot 5 — a measurement of the
transport, not a decision about the host.** Every fetch under the declared
identity, the guard on the exact path first, by `bin/fetch-body.py
--allow-refusal` — the four records carry the status, the bytes, the md5 and
the `cf-ray` that answered.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 3174 B, md5 7b987533173b both times — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True
```

*The file is Cloudflare's managed content block — the `Content-Signal` preamble and nine named crawlers refused, `ClaudeBot` among them — followed by the operator's own lines (3 174 B in all).* Before the decision this host was read as closed by name; the decision reopened it on paper, and this card is the first time its transport was asked under the permitted token.

## The transport — a static 403, the provider default

```
GET https://www.ezega.com/          403, 25 B, md5 9ccabba20b9f    (11:56:27Z)
GET https://www.ezega.com/          403, 25 B, md5 9ccabba20b9f    (second fetch)
GET https://www.ezega.com/Jobs     403, 25 B, md5 9ccabba20b9f    (11:57:41Z)
GET https://www.ezega.com/Jobs     403, 25 B, md5 9ccabba20b9f    (second fetch)
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

## 2026-09-13 10:46 UTC — the browser route, MEASURED (#222): served, and nearly empty

One Claude-in-Chrome tab, the guard on `/Jobs` and `/jobs/AllPostedJobs`
first. **No challenge** — the 25-byte 403 goes to the declared client alone.
An ASP.NET WebForms site (`__doPostBack` links, a login pane, an
Amharic/English toggle).

```
navigate /Jobs                     200 «Jobs in Ethiopia | Job Vacancy in Ethiopia | EthioJobs - Ezega Jobs» — a landing page with advice text, links to /jobs/AllPostedJobs
navigate /jobs/AllPostedJobs       200 — «Featured Jobs in Ethiopia»: 1 row (Sep 08 2026 · Sales Engineer – Epoxy Flooring Solutions · KAMUR MODERN LIVING · Addis Ababa)
                                   «Latest Jobs in Ethiopia»: **«No Active Jobs available for the selected criteria»** · filters (category, location, experience, education) unset
```

**One advertisement on the day, and the site's own sentence for the rest.**
A route to one is a route; the count is the site's, and it is 1. *The
advertisement row has no link of its own in the markup read (a WebForms
postback), so no address was opened.* What reopens the volume question: a
day the latest-jobs table is not empty.

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches each of the root and a listing path, a static refusal.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.
- **Not an AfricaWork host** (#233: «another managed block naming ClaudeBot»); its refusal is the same 25-byte provider default — **the body says who fronts the site, not who runs it.** The second Ethiopian host of the list, `www.ethiopiawork.com`, answers the same bytes two seconds later: one read each, dated.
