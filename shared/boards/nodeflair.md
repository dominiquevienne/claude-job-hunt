# Board adapter — NodeFlair (Singapore): reopened by the 2026-09-07 doctrine, and the transport refuses the client with a static 403 — and served to a browser

<!-- verified: 2026-09-13 -->

<!-- hosts: www.nodeflair.com, nodeflair.com -->
<!-- script: none -->
<!-- countries: SG -->
<!-- content: measured · **«10,000+ jobs» stated by the page and `total_listings_count: 10000` by its own API** (`/api/v2/jobs?page=1` from the tab — 12 listings a page with `job_path`, `position`, `title`, `salary_min/max`, `currency`, `remuneration_frequency`, `tech_stacks`): a cap, not a count — the site says «10,000+» and the API says exactly 10 000; an aggregator over Asian job sites and career pages, Singapore first; the rules as on the 12th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: the site's own `total_listings_count` beside its own «10,000+» — the two agree that the figure is a ceiling; no page states the count above it · 2026-09-13 -->
<!-- route: browser · 10000 · 2026-09-13 -->

**Measured 2026-09-13 at 10:22:26Z UTC for #233, lot 8 — a measurement of the
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
GET https://www.nodeflair.com/          403, 25 B, md5 9ccabba20b9f    (10:22:26Z)
GET https://www.nodeflair.com/          403, 25 B, md5 9ccabba20b9f    (second fetch)
GET https://www.nodeflair.com/jobs     403, 25 B, md5 9ccabba20b9f    (10:23:35Z)
GET https://www.nodeflair.com/jobs     403, 25 B, md5 9ccabba20b9f    (second fetch)
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

## 2026-09-13 10:57 UTC — the browser route, MEASURED (#222): an aggregator, and a total that is a ceiling

```
navigate /jobs                      200 «NodeFlair Jobs | #1 TECH job portal in Asia» — «Aggregated job listings from popular job sites and career pages» · **«10,000+ jobs»**
fetch /api/v2/jobs?page=1           200, 9 671 B — {job_listings: 12 rows, total_listings_count: **10000**, has_job_alert}
row                                 id 557519 · job_path /jobs/luxoft-…-557519 · position «Data Analyst» · title · salary_min 8000 · salary_max 12000 · currency SGD · remuneration_frequency Monthly · tech_stacks[]
```

No challenge. **The API answers from the tab, and `total_listings_count`
is 10 000 exactly while the page says «10,000+»**: a ceiling the site
states about itself, not the inventory. *An aggregator: its rows are
other boards' advertisements, which `shared/boards/README.md` treats by
reference, not by value.* The procedure: guard → tab → `page=1, 2 …` of
`/api/v2/jobs` 1.5 s apart → «n emitted, site states 10 000 (a cap)» →
close; 12 read. *The tab's renderer froze once on a JSON parse of the
response — the second read parsed the text with a pattern instead.*

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches each of the root and a listing path, a static refusal.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.
- **Not an AfricaWork host**; the 25-byte refusal is the provider default shared with every static host of #233 — **the body says who fronts the site, not who runs it.** The root redirects `www.` to `nodeflair.com` and the bare host answers the same 25 bytes; Singapore's tech board, one of the 61.
