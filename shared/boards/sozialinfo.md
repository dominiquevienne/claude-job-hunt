# Board adapter — sozialinfo.ch

<!-- verified: 2026-09-02 -->

<!-- hosts: www.sozialinfo.ch -->
**Re-verified 2026-09-02**: 720 read against a stated 729, and the adapter still says it is nine short and that pagination is cumulative — the documented behaviour, working.

**A real multi-employer board, and the only one here that names the employer.**
Switzerland's job portal for the social sector — social work, care, education,
cantonal and municipal services, foundations.

Server-rendered HTML with a `JobPosting` block on every ad. **No key, no cookie,
no browser.**

Read by `skills/job-scan/scripts/sozialinfo.py`.

**Verified 2026-08-29**: the whole board, 708 ads, read in one request.

## Why this one is different

Every other board in this directory either serves one employer (the ATS family)
or hides the employer behind an agency (`michaelpage.md`, `fachkraft.md`). This
one **names it**, and links to its own site:

```json
"hiringOrganization": {"name": "Katholische Kirche im Kanton Zürich",
                       "sameAs": "https://www.zhkath.ch"}
```

Measured on six ads: employer named **6/6**, `sameAs` **6/6**, `validThrough`
**6/6**. And 26 distinct employers across the 27 ads the job-room sweep found.

Two consequences worth stating: **the fuzzy employer-name dedup in
`skills/job-scan/SKILL.md` actually works on this board**, which it cannot do on
an agency board; and the user can research the employer before applying.

## The whole board in one request

**Pagination is cumulative.** `?page=N` returns pages 1..N in a single response,
not page N:

| `--pages` | ads returned |
| --: | --: |
| 1 | 30 |
| 2 | 61 |
| 5 | 151 |
| **24** | **708 — the board's own stated total** |

So `list` defaults to `--pages 24` and fetches everything once. It compares what
it parsed against the figure the page states and says *"708 read, board states
708 (complete)"* — or names the shortfall and tells you to raise `--pages`.

## The card carries everything needed to score

No per-ad request is needed to rank: each `<article>` yields, in order, the
posting date, the title, **the employer**, **the postcode and town**, the
workload and the category.

```
29.08.2026 | Fachperson Netzwerk & Advocacy (70 - 80 %) | Katholische Kirche im
Kanton Zürich | 8006 Zürich | 70 - 80% | Mitarbeit soziale Berufe
```

**The postcode comes free**, in the `8006 Zürich` shape the ORP's job-room.ch
PRE form demands and most boards omit — see `shared/modules/job-room-ch.md`.

## The ledger, and a token that rebuilds its own URL

```
sozialinfo:<token>              e.g. sozialinfo:TA94iHqG
```

The ad path ends in a mixed-case token, and **the token alone is enough**:
`/arbeitsmarkt/stellenportal/TA94iHqG/` answers `200` with the full ad. The slug
in front of it is decorative.

## Traps

**1. The listing's links are relative AND the token is mixed case.** A pattern
written for absolute hrefs, or for lowercase slugs, matches **nothing** and reads
as an empty board — this adapter hit both while being written. The links are
`href="/arbeitsmarkt/stellenportal/<slug>-<Token>/"`.

**2. An unknown token answers `200`, not `404`.** It serves a ~300 kB page with
**no `JobPosting` block** and an **empty `<title>`**. The status code is not a
test here; the presence of the block is. `check` says so in its own `why`.

**3. Counting ad links with a bare regex undercounts.** A grep for the link
pattern returned 701 where parsing `<article>` blocks returned all 708 — some
links are repeated or nested. Parse the cards, do not count the hrefs.

## What it gives step 1b

`validThrough` on every ad, in the `JobPosting` block — the expiry date
`cover-letter` step 1b reads before making any request. `check` returns it with
its verdict, and the registry entry is in `shared/ats-open-check.md`.

## Applying

Each ad links to the employer's own application route — this portal publishes,
it does not mediate. Hand the user the ad URL and their documents.

## Pace

One request for the whole board. `--with-description` costs one per kept ad, so
filter with `--search` and `--place` first.
