# Board adapter — Profesia.cz (Czechia): the Czech front of Profesia's stack, 1 094 advertisements against the listing's own 1 095, read by `profesia.py --host www.profesia.cz`

<!-- verified: 2026-09-13 -->

<!-- hosts: www.profesia.cz, profesia.cz -->
<!-- script: profesia.py -->
<!-- countries: CZ SK -->
<!-- content: measured · rules read twice and certain (2 201 B, the `.sk` file to a few lines, no AI agent named; `identity()` answers `claude-user`, `verdict()` sweeps) — and the transport answers 200: `/sitemap.php` (645 638 B) holds 1 844 `<loc>` of which **1 094** advertisements `/prace/<employer>/O<id>` and 750 facets; `/prace/` states `"count":1095` — 1 short, two witnesses; a Slovak-written advertisement for a Slovak place is served on this host, so `countries` carries SK beside CZ · 2026-09-13 17:13 UTC -->
<!-- witness: the listing page's own `"count":1095 … "scenario":"standard"` beside the sitemap's 1 094 advertisement-shaped URLs, printed apart by `profesia.py list --host www.profesia.cz` — «1 094 emitted, site states 1 095 — 1 short» -->

**Shipped 2026-09-13 with `profesia.md` (#343) — one script, one stack, two
hosts.** The measurement, the rules, the two layouts of the advertisement
page and the tests are on **`profesia.md`**; this card exists so that the
Czech host is counted for Czechia and so that a URL from `profesia.cz` finds
its adapter.

```
profesia.py list --host www.profesia.cz       # 1 094 advertisements on 2026-09-13, 1 095 stated
profesia.py ad --url https://www.profesia.cz/prace/<employer>/O<id>
```

## What is specific to the Czech front

| question | answer (2026-09-13, 17:09–17:13 UTC) |
| :-- | --: |
| the path | `/prace/` (Czech) where `.sk` says `/praca/` — the same `O<id>` shape, the same id sequence (`O5339846` here, `O5338670` there) |
| the rules' diff with `.sk` | `/sk/*?` refused here where `.sk` refuses `/sk/` outright; `/hu/` here, `/hu/*?` there; one extra `search_cv_submit.php`, one `/registrace-firmy`; one Sitemap line instead of two |
| what it serves | **Slovak-written advertisements for Slovak places too** — `/prace/hana-cosmetics/O5339846` is «Malý Cetín, Slovensko», in Slovak, with Slovak labels («Druh pracovného pomeru»): the adapter reads the labels in both languages, `country` is `CZ` (the host's) and `place` says «Malý Cetín» |
| the largest employers in the file | `manpowergroup` 385, `predvyber-cz` 233, `p-p-construction` 53, `adecco` 39 — agencies, as on `.sk` |
| the popup | not seen on `/prace/`; the count comes from the same search payload as on `.sk` |

- **Not a verdict that anything is closed** — nothing refuses us.
- **Not a second adapter** — `profesia.py` with `--host`; a change on one
  host is tested on both (`_sitemap.count` on each file, the same tests).
