# Board adapter — JobPaw (`jobpaw.com`, Haiti): `jobpaw.py` since 2026-11-03 (#776) — the generalist, and **the board STATES ITS TOTAL twice** (`totalRows_RS_job=28` and «de 1 à 28 sur 28»), so it has a witness external to our extraction; its list dates every ad and carries a **closing date**, so «what is open» is a question it answers — 0 of the 28 were closed on 2026-11-03. The host is the BARE name: `www.jobpaw.com` fails TLS on a hostname mismatch

<!-- verified: 2026-11-03 -->

<!-- hosts: jobpaw.com -->
<!-- script: jobpaw.py -->
<!-- host-forms: jobpaw.com -->
<!-- host-forms-basis: read — `jobpaw.py:HOST`, a single literal; the list and every ad are paths under it, and the `www.` form is refused in `request()` because it fails TLS on a hostname mismatch · 2026-11-03 -->
<!-- countries: HT -->
<!-- content: measured · **`jobpaw.py` shipped. `/professionals/find-job` (200, 1 171 000 B, md5 720676bbea10, 19:41 UTC) carries 28 `div.jobs-list__card` and the board STATES ITS TOTAL TWICE — `totalRows_RS_job=28` in its pager's link and «Affichage des offres d'emploi de 1 à 28 sur 28» under it. Read 28, stated 28, they AGREE. **The page STEP is 100, not the number shown**: `?pageNum_RS_job=1` returns 200 (1 089 399 B) with ZERO cards and prints «de 101 à 28 sur 28» — so the stated RANGE is nonsense out of range while the total stays right, and the walk reads the total and stops on a page with no card. **Six fields on 28 of 28**: publication date, closing date, title, employer, location and sector. **The list is ordered by CLOSING DATE, furthest first** — monotonic over 28 of 28, while neither publication order holds — so the ads closing soonest are LAST, and a truncation drops the most urgent rather than the dead. **0 of the 28 were closed on 2026-11-03**, the nearest the next day. FOUR things are named something they are not: `jobs-list__price` carries the SECTOR; the two `jobs-list__location` per card are the place and the closing date, told apart by their TAG and their label; the `<h1>` is a marketing banner identical on every ad, so the ad's title comes from its «Titre du poste» ROW; and the list's `Location:` is country + ZONE, the city being on the ad only (measured on 2 ads of 2). The ad is a table of TEN label/value rows, EXTRACTED and not guessed — Titre du poste, Compagnie, Domaine, Spécialité, Date publication, Date limite, Pays, Ville, Zone, Durée — with the label HTML-escaped (`Dur&eacute;e`), so keys are ACCENT-FOLDED rather than enumerated. **The board emits 2 PHP warnings per ad INTO its own markup**, inside an `alt=` attribute, and unstripped they land in the FIRST label and carry the server's file path into a record key. **And it declares `charset=UTF-8` while serving 5 bytes that are not** (of 1 169 653 characters, 0.00043 %), so `decode_body` falls to its declared-total fallback and the CALLER must read which codec was used. Dates come in TWO forms, one per surface: «29 octobre 2026» on the list, «30 Oct 2026» on the ad. `/robots.txt` open, `certain: True`, `state: read`, no Crawl-delay; 3 s is ours** · 2026-11-03 -->
<!-- witness: the board's OWN stated total — `totalRows_RS_job=28` in the pager link and «Affichage des offres d'emploi de 1 à 28 sur 28» in prose, two independent statements of the same number, and 28 cards read against them. **This REPLACES the `witness: none` this card carried from 2026-09-20**, which said «the list states no count»: that was true of what had been looked at and is false of the page. The stated RANGE is NOT a witness — out of range it prints «de 101 à 28 sur 28» · 2026-11-03 -->
<!-- content: measured · **the root (200, 182 771 B, md5 8ddd53324951 identical on two reads) links `/professionals/find-job`, `/entreprises/trouver-un-appel` (tenders, a separate section) and 12 `/professionals/job-details` ads; its prose states «+20,000 offres d'emploi, +5,000 appels d'offres» — a cumulative, not the open count; `/professionals/find-job` (200, 1 177 977 B, 12:16 UTC) lists 32 distinct `job-details?idj=<id>` ads with no pager link and no stated count; no JobPosting; `_robots.allowed('jobpaw.com', '/professionals/find-job')` → open, certain** · 2026-09-20 -->
<!-- witness: none — the front's «+20,000» is a cumulative; the list states no count (32 ads counted on it) · 2026-09-20 -->

## 2026-11-03 — #776: the adapter ships, and the card's own `witness: none` is refuted

The head this card carried until today read «**no adapter yet**» and «32 distinct ads»; both are history. **The premise moved on both halves**: 28 ads now, and «the list states no count» is false — the board states 28 TWICE, which makes this the only Haitian board with a witness external to our extraction. *`emploilenouvelliste.py` (#777, same turn) has none, and its card says so.*

**What the measurement changed in the code:**

- **The caller must read WHICH codec `decode_body` used.** The page declares `charset=UTF-8` and 5 of its 1 169 653 characters are not UTF-8, so the strict decode raises and `_decode` falls to cp1252. **`_decode` is SOUND and says so itself**: «the fallback is chosen for being total, not for being right, and the caller is told which one was used.» The first version of this adapter took `decode_body(...)[0]`, so 28 ads came out «PubliÃ© 13 aoÃ»t 2026» — and the mojibake silently broke the label stripping too, one defect wearing two symptoms. The re-decode fires only when the repository's own readability control prefers the other reading: 0.001 under utf-8/replace against 0.996 under cp1252, threshold 0.5. **NE PAS «réparer» `_decode` sur ce motif** — a Latin-1 board must not be re-decoded, which is the corruption it exists to stop, and a test pins that direction too.
- **The title had to come from the table.** The `<h1>` is a marketing banner identical on every ad; taking it gave 28 ads one wrong title.
- **The board's own PHP warnings had to be stripped first.** Two per ad, inside an `alt=` attribute, landing in the first label — unstripped, a record key carried `/var/www/html/professionals/job-details.php on line 349`.
- **The label map was a GUESS and is now EXTRACTED.** A first version, composed from a loose reading, mapped TWO of the ten labels; the ten were read off the page, and the keys are accent-folded so `Dur&eacute;e` resolves without enumerating forms.
- **The sibling's redaction anchor does NOT transpose.** This board writes its number `+(509) 3701 9232` — parentheses round the dialling code — and `emploilenouvelliste.py`'s `\+\s?509` returns ZERO on it, which is the direction that lets a contact leave. Widened: 1 of the 1 real number, 0 of the 4 other digit strings, where the bare motif takes all five — including **`2147483647`, which is 2³¹−1, a sentinel and not a quantity**. *The remedy transposes between boards; the exact motif does not.*
- **The `www.` form is refused outright.** It fails TLS with «Hostname mismatch, certificate is not valid for 'www.jobpaw.com'», reached by TYPING the host instead of reading it off this card. A refusal written up as a fact about the host would have accused a sound board.

**Named on the Haiti page since the Atlas inventory of 2026-09-04 (#147),
never carded; measured for #771 on 2026-09-20 12:15–12:18 UTC by the declared
client, the guard on the exact path first, `bin/fetch-body.py`, two reads.**
*A measurement, not an adapter.*

The page's 2026-09-04 note («48 annonces, le seul compte vivant») was a count of links, not a count the site states.

```
_robots.allowed('jobpaw.com', '/professionals/find-job')   open
GET https://jobpaw.com/                              200 ×2 — the front, «+20,000 offres» (cumulative)
GET https://jobpaw.com/professionals/find-job        200 — 32 ads, no pager, no count
```

The adapter's first line: whether `find-job` pages (a hidden parameter, a load-more call) or lists everything, the ad `job-details?idj=<id>` — and the tenders kept apart (the `/entreprises/trouver-un-appel` section is not the board).
