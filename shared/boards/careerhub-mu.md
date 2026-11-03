# Board adapter — CareerHub (`www.careerhub.mu`, Mauritius): `careerhub.py` since 2026-11-03 (#701) — **every advert is a complete `JobPosting`** (ISO `datePosted` and `validThrough`, `PostalAddress`, `baseSalary` in MUR), and it emits **24 of the 158 the board STATES** on its own `ItemList`, the other 134 sitting behind a client-side loader whose control carries no URL and whose `?page=` is measured as ignored; the board's own canonical uses the BARE host while this card declares the `www.` form, and both are guarded

<!-- verified: 2026-11-03 -->

## 2026-11-03 — #701: the adapter ships, and it emits 15 % of a board whose own total is the denominator

The head this card carried until today read «**no adapter yet**» and «163 offres»; both are history — the count is **158** now, and it is read from the structured `ItemList` rather than from prose. #701 asked for «la liste et l'annonce», neither of which had been read; both are read.

**What the measurement changed in the code:**

- **`one()` is not `label()`, and `_ldjson` says so in its own docstring.** The first version read every text field with `one()` and emitted **24 adverts with an empty title**: `one()` returns `{}` for a bare string *by design* — «a string is not silently turned into a name» — and an `ItemList`'s `name` is a bare string. `one()` is for fields that must be OBJECTS so that `.get()` is always legal; `label()` is for text. **The module is sound; using the wrong half of it was the defect.**
- **The witness is NOT taken from `_ldjson.objects()`.** That helper expands the `ItemList` container into its items — 26 objects here, of types `ListItem`, `Organization`, `WebSite`, and no `ItemList` among them — so `numberOfItems` is gone by the time it has spoken. The adapter reads the raw blocks and finds the container. *A helper that flattens a container loses the container's count, and the count is the only witness external to our extraction.*
- **Two host forms, and the board's canonical is not this card's.** An `ad` that accepted only `www.careerhub.mu` refused the URLs of its own list, all 26 of which use the bare form. Both are guarded and both accepted; the divergence is recorded rather than normalised away. *Third board in one slot where the DATA names a different host from the PAGE.*
- **The redaction is bounded by reading the posting, not the page.** The site's own address and telephone are in the FOOTER; scrubbing the page would declare a withheld contact on every record for one no employer deposited.
- **Neither sibling's phone anchor transposes.** Mauritius dials `+230`, not `+509`, so the anchors of #776 and #777 return ZERO here; and the bare motif takes 8 strings on one advert of which 4 are the page's own identifiers.


<!-- hosts: www.careerhub.mu -->
<!-- script: careerhub.py -->
<!-- host-forms: www.careerhub.mu, careerhub.mu -->
<!-- host-forms-basis: read — `careerhub.py:HOSTS`, both literals; the board's own canonical and every `ItemList` URL use the bare form while this card declares the `www.` one, and both are guarded · 2026-11-03 -->
<!-- countries: MU -->
<!-- content: measured · **`careerhub.py` shipped, and it emits 24 of the 158 the board STATES. `/fr/jobs` (200, 218 980 B, md5 057662b4f12d, 21:1x UTC) carries an `ItemList` whose `numberOfItems` is 158 and whose `itemListElement` holds exactly 24, each with its advert's URL, title and position; 24 `href="/fr/jobs/<uuid>"` in the markup agree. The remaining 134 are behind a CLIENT-SIDE loader: the page is a Next.js App Router app (`self.__next_f` ×16), the «Voir 24 offres de plus» control is a `<button>` with no URL in the markup — no `wire:`, no `hx-`, no `/api/`, no cursor, no offset — and `?page=2` is MEASURED as ignored, returning 200 (219 723 B) with the SAME 24 UUIDs at positions 1–24. So 15 % is served and the denominator is the board's own. **Every advert is a complete `JobPosting`**: `datePosted` and `validThrough` as ISO instants, `hiringOrganization`, `jobLocation` as a `PostalAddress` (Ebene / central / MU), **`baseSalary` MUR 45 000–75 000**, `experienceRequirements`, `identifier` — the richest structured data measured in HT and MU. **TWO HOST FORMS**: this card declares `www.careerhub.mu`, and the page's `rel="canonical"` plus all 26 `ItemList` URLs use the BARE `careerhub.mu`; both are guarded (`*`, no `Disallow`, `state: read`, `certain: True`, and **no `Crawl-delay` is written** — so 3 s is ours, not the host's) and the adapter accepts both, because one that took only this card's form refused the URLs of its own list. The site's own address and telephone live in the page FOOTER, outside the posting, so reading the posting BOUNDS the redaction structurally** · 2026-11-03 -->
<!-- witness: the board's OWN `numberOfItems` on its `ItemList` — 158 — against the 24 it serves. **This REPLACES the «163 offres» of 2026-09-18**: the count moved, and it is now read from the structured container and not from prose. It is NOT taken from `_ldjson.objects()`, which expands the container into its items and loses `numberOfItems` · 2026-11-03 -->
<!-- content: measured · **the root (200, 133 384 B, md5 3721907f3d24 / ac0c1fb99269 — a rendered element moves) is the French front stating «163 offres», with `/fr/jobs`, `/fr/jobs?vertical=tech-ai` and `/fr/post-job`; no JobPosting on the root; `_robots.allowed('www.careerhub.mu','/')` → open, certain; the list and the ad not read** · 2026-09-18 -->
<!-- witness: the front's own «163 offres» · 2026-09-18 -->

**Found by the Mauritius search of #618 (a country never searched),
measured 2026-09-18 06:45–06:47 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #618: one search naming the National Employment Department's portal
and the private boards, no composed host names. *A measurement, not an
adapter.*

```
_robots.allowed('www.careerhub.mu', '/')   open
GET https://www.careerhub.mu/   200 ×2 — see the content line
```

The list, its pager and the ad are the adapter's first line (its `adapter` issue).
