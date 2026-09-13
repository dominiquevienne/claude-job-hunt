# Board adapter — Kariera (Greece): reopened by the 2026-09-07 doctrine, and the transport refuses the client with a static 403 — and served to a browser

<!-- verified: 2026-09-13 -->

<!-- hosts: www.kariera.gr, kariera.gr -->
<!-- script: none -->
<!-- countries: GR -->
<!-- content: measured · **5 959 advertisements stated by the site** — `<title>5959 διαθέσιμες θέσεις εργασίας</title>` on `/jobs`, an `ItemList` of 50 per page in JSON-LD, a pager to page 120 (120 × 50 ≥ 5 959), advertisement addresses `/jobs/<category>/<id>`; pages 1 and 2 read from a connected browser tab (50 + 50), the full walk not made; a JobPosting per advertisement; the rules as on the 12th — `ClaudeBot` refused, `*` open, the 2026-09-07 doctrine and #230 · 2026-09-13 -->
<!-- witness: the site's own count in its `<title>` («5959 διαθέσιμες θέσεις εργασίας»), the same on page 2, and the page's `ItemList` of 50 — the walk to confirm it is 120 pages and was not made · 2026-09-13 -->
<!-- route: browser · 5959 · 2026-09-13 -->

**Measured 2026-09-12 at 11:56:32Z UTC for #233, lot 5 — a measurement of the
transport, not a decision about the host.** Every fetch under the declared
identity, the guard on the exact path first, by `bin/fetch-body.py
--allow-refusal` — the four records carry the status, the bytes, the md5 and
the `cf-ray` that answered.

## The rules — reopened by the doctrine of 2026-09-07 and by #230

```
robots.txt      read twice, certain: True, 2019 B, md5 7bc6de0d4c21 both times — `User-agent: ClaudeBot / Disallow: /`, `*` open
identity("/")   http, claude-user      <- the group naming ClaudeBot does not bind Claude-User (owner, 2026-09-07)
verdict()       sweep True, sweep_token claude-user   <- since #230 (2026-09-11)
allowed("/")    True
```

*The file is Cloudflare's managed content block — the `Content-Signal` preamble and nine named crawlers refused, `ClaudeBot` among them — followed by the operator's own lines (2 019 B in all).* Before the decision this host was read as closed by name; the decision reopened it on paper, and this card is the first time its transport was asked under the permitted token.

## The transport — a static 403, the provider default

```
GET https://www.kariera.gr/          403, 25 B, md5 9ccabba20b9f    (11:56:32Z)
GET https://www.kariera.gr/          403, 25 B, md5 9ccabba20b9f    (second fetch)
GET https://www.kariera.gr/jobs     403, 25 B, md5 9ccabba20b9f    (11:57:46Z)
GET https://www.kariera.gr/jobs     403, 25 B, md5 9ccabba20b9f    (second fetch)
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

## 2026-09-13 10:47 UTC — the browser route, MEASURED (#222): a count in the title, an ItemList per page, a JobPosting per advertisement

One Claude-in-Chrome tab, the guard on `/jobs` and `/jobs/<category>/<id>`
first. **No challenge** — the 25-byte 403 goes to the declared client alone.

```
navigate /jobs                     200 «5959 διαθέσιμες θέσεις εργασίας | kariera.gr» — 50 cards, JSON-LD ItemList (numberOfItems 50), pager ?page=1 … 120
fetch /jobs?page=2                 200 — the same title figure, 50 more; 144 of the page's 191 /jobs/… links are chrome (category pages), the ItemList is the list
the page's own calls               /api/v2/jobseeker/feature-flags · /enums · /profile · /tracking — the listing itself is server-rendered
GET /jobs/engineering-jobs/344986  200 — one JobPosting (Loulis Food Ingredients · Ηλεκτρολόγος Μηχανικός · datePosted 2026-09-13T10:16 · validThrough 2026-10-13 · description 2 693 chars · Σούρπη, Ελλάδα)
```

**The site states 5 959 and its list page states 50 per page; the walk of
120 pages was not made** — the count is the site's, and the procedure a
session follows is: guard → tab → read the `<title>` figure → `fetch
/jobs?page=P` for P = 1 … ⌈N/50⌉ 1.5 s apart, reading the ItemList of
each page (not the links) → **«n emitted, site states N»** → the
JobPosting on a page → close. *The 5 959 is the site's; 100 were read.*

## What this card is, and is not

- **Not a verdict that the host is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: one client, one day, two
  fetches each of the root and a listing path, a static refusal.
- **No script, no configuration.** A user with a URL from this host can hand
  it to `cover-letter`; whether that page is served to a browser is not
  established here.
- **Not an AfricaWork host** (#233: «another managed block naming ClaudeBot»); same 25-byte provider default. The other Greek host of the list, `www.skywalker.gr`, answers a challenge in the same minute — **the rules file predicts nothing about the transport.**
