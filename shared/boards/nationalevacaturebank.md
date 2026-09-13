# Board adapter — Nationale Vacaturebank (`www.nationalevacaturebank.nl`, Netherlands): a search refused in writing and never taken, a sitemap of 89 733 that lists what has left the board, and a sample that says how much

<!-- verified: 2026-09-13 -->

<!-- hosts: www.nationalevacaturebank.nl, nationalevacaturebank.nl -->
<!-- script: nationalevacaturebank.py -->
<!-- host-forms: www.nationalevacaturebank.nl, nationalevacaturebank.nl -->
<!-- host-forms-basis: read — `nationalevacaturebank.py:BASE` for the pages, and the sitemap index sends its two files to the APEX `nationalevacaturebank.nl`; the guard is taken on that host too, on the exact path (`allowed('nationalevacaturebank.nl', '/cdn/sitemaps/vacature/vacature-1.xml')` → True, certain, 15:27 UTC) · 2026-09-13 -->
<!-- countries: NL -->
<!-- content: measured · **89 733 distinct advertisement uuids in the declared sitemap (`/cdn/sitemaps/vacature.xml` → `vacature-1.xml` 50 000 + `vacature-2.xml` 39 733, no `<lastmod>` per entry) — and of 40 drawn at random, 24 served with an open `validThrough`, 12 answered 410 Gone, 4 answered 404: the file lists what has left the board**; `nationalevacaturebank.py sitemap` 15:29 UTC, the sample 15:30–15:31 UTC; the site states no figure by HTTP (its «88.909 banen» is rendered in a tab from the API behind the refused search, 13:07 UTC) · 2026-09-13 -->
<!-- witness: a sample of pages, not a figure — `--sample K` opens K advertisements spread over the files and prints served-open / 410 / 404 / other, because the site's only stated count lives behind a search its rules refuse to `*` and the sitemap's count is the archive plus the live; the two figures (89 733 and «88.909») are 824 apart and neither is corrected · 2026-09-13 -->

**The Netherlands' largest general board, DPG Media's — served to the
declared client on every path read, its search refused in writing to
everyone, its sitemap the route, and that sitemap six-tenths alive.**
Measured 2026-09-13 13:07 UTC (a tab, the «88.909 banen»), 13:27 UTC (the
client, `GET /`), 15:26–15:31 UTC (the client: rules, index, two files,
the open search page, 42 advertisement pages). Shipped the same day,
replacing the morning's measured card (`route: browser · 88909`).

## Rules — the search is refused in writing, the sitemap is declared

```
robots.txt   200, ~2.8 kB — `User-agent: *`: Disallow /vacature/zoeken?*  ·  /vacature/uitgebreid-zoeken  ·  /vacatures/*?page=  ·  /vacatures/*?*&page=  ·  /vacature/bladeren/  ·  /archief/  ·  (accounts, apply, cv, utm/gclid variants …)
             `User-agent: ClaudeBot`: Disallow /          <- names the crawler token; `Claude-User` is under `*` (2026-09-07)
             AdsBot-Google, AdsBot-Google-Mobile, Twitterbot: Allow /vacature/zoeken?*   <- the search is opened to three by name, and to no one else
             ten `Sitemap:` lines — /vacatures/sitemap.xml (241 landing pages), /cdn/sitemaps/vacature.xml (the advertisements), dco-titel, werkgever, plaats, salary, gemeente, overige-functie-titel, trefwoorden
identity("/vacature/zoeken")   http, claude-user — the BARE search page is open; every queried or paginated one is not
```

**Every listing with a query string or a page number is refused to `*`**
— `/vacature/zoeken?*`, `/vacatures/*?page=`, `/vacature/bladeren/`,
`/archief/`. A written refusal is an intention, honoured by every route
(§2 quater, borne 1): the adapter carries the refused shapes in
`REFUSED_RE` and exits 7 before the guard on any of them, whatever a
caller asks. The bare `/vacature/zoeken` is open and was read once: a
Next.js shell (87 496 B) with no count in it — the «88.909 banen» a tab
shows is rendered client-side from `api.nationalevacaturebank.nl`
(`runtimeConfig.api.jobService`), the API behind the search the rules
refuse. **Not taken either**: it is the same search under another host.

## Transport — served, and the refusal the Netherlands page expected was not met

```
GET /                                        200, 183 810 B, server DPES — twice at 13:27 UTC, identical md5
GET /vacature/zoeken                         200, 87 496 B — Next.js shell, `__NEXT_DATA__` with no total; no JSON-LD; no challenge
GET /vacatures                               200, 134 075 B — landing page, no total
GET /cdn/sitemaps/vacature.xml               200, 360 B — ONE <sitemap> element carrying TWO <loc>, lastmod 2026-09-02T06:21:42Z, files on the apex host
GET nationalevacaturebank.nl/cdn/sitemaps/vacature/vacature-1.xml   200, 8 788 578 B — 50 000 <loc>, <changefreq>hourly</changefreq>, no <lastmod>
GET nationalevacaturebank.nl/cdn/sitemaps/vacature/vacature-2.xml   200, 6 985 338 B — 39 733 <loc>
GET /vacature/<uuid>/<slug>                  200, ~107 kB — JobPosting in `<script type="application/ld+json" data-next-head="">`; or 410, 0 B; or 404, 0 B
```

## The sitemap lists what has left the board — and the sample says how much

```
**89 733 distinct advertisement uuid(s)** in 2 file(s) (vacature-1.xml 50 000, vacature-2.xml 39 733); 89 733 emitted; the index's own lastmod 2026-09-02T06:21:42Z.
The site states no figure by HTTP — its «N banen» is rendered in a browser from the API behind the search the rules refuse; no second figure is compared here.
Sample of 12 spread over the file(s): 5 served with a JobPosting whose validThrough is on or after 2026-09-13, 7 gone (410/404) …          <- the first run, 15:29 UTC
40 drawn at random (seed 13), 15:30–15:31 UTC: 24 → 200 with an open validThrough (2026-09-15 … 2026-11-11), 12 → 410 Gone, 4 → 404       <- the check that made the sentence
```

**The index is malformed and readable**: one `<sitemap>` element, two
`<loc>` inside it — a reader that takes one `<loc>` per element keeps one
file and loses 39 733 without a symptom; `locs()` reads every `<loc>` in
document order. The two files sit on the apex host, not `www.`; the guard
is taken there on the exact path.

**89 733 is not the live inventory.** Sixteen of forty random addresses
are gone — 410 for twelve (the site's own «gone», deliberate), 404 for
four — and every served page carried a `validThrough` still ahead. So the
sitemap is the archive plus the live, roughly six-tenths alive on the day
(24 / 40; a proportion from forty draws, not a count), and the index's
`lastmod` is eleven days older than the files it points to. **The site's
«88.909 banen» and the file's 89 733 are 824 apart and answer different
questions** — the API's count of what the search can return, the file's
count of what was ever listed and not yet pruned; neither is corrected
into the other, and the adapter prints the sample instead of either.

## The advertisement — a full JobPosting

```
JobPosting: title · alternateName («productietechnicus») · description (HTML) · datePosted 2026-07-16T22:00:00Z · validThrough 2026-10-07T22:00:00Z
            employmentType INTERN · hiringOrganization {name, email careers@…} · jobLocation {Montfoort, Utrecht, NL, 3417ME, lat/lng}
            baseSalary {EUR, 2559–2559, MONTH} · workHours «1 - 40 uur per week» · educationRequirements {associate degree}
            experienceRequirements {monthsOfExperience "48"} · industry Overig · occupationalCategory Overig · directApply false
```

`ad` reads it; a 410 or 404 exits 3 (gone). The employer's e-mail is
emitted as published — the employer put it in the posting for candidates.
Read in full on one (`0001316e…`), and on the 24 served of the sample for
`validThrough` only.

## Configuration

```yaml
boards:
  nationalevacaturebank:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no browser. `sitemap` is three requests and ~16 MB of
XML; `--sample K` adds K page requests 1.5 s apart; `ad` is one.

## What is not established

- **The live count** — the site states one only behind the refused
  search; the sample gives a proportion (24 of 40), not a count.
- **Which uuids are gone without opening them** — no `<lastmod>` per
  entry, and the 410s are not marked in the file.
- **The sister board `intermediair.nl`** (same group, same rules shape
  expected) — not reached; a `--host` on this script is the likely form.
- **The nine other sitemaps** — landing pages by title, employer, place,
  salary, municipality; not read.
- **Whether `api.nationalevacaturebank.nl` publishes rules of its own** —
  not asked, because the search it serves is refused on the site and
  taking it there would be the same search.

## 2026-09-13 — shipped

`nationalevacaturebank.py sitemap --limit 2 --sample 12`: 89 733 distinct,
5 of 12 served. A 40-draw check: 24 / 12 / 4. `ad` on one. Four tests;
six mutations on a detached worktree (`python3 -B`), six red, each on the
test written for it — the refused-path guard dropped, `locs` read per
element, the uuid dedup dropped, 410 folded into 404, the date test
inverted (inert on the first draw of the sample case, which was symmetric
— one open, one expired — and red once the draw was made 2 + 1 + 1), 410
dropped from `ad`'s gone codes.
