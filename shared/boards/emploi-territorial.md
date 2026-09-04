# Board adapter — emploi-territorial.fr

<!-- hosts: www.emploi-territorial.fr -->
<!-- script: emploiterritorial.py -->
<!-- countries: FR -->

The portal of the **centres de gestion**: France's territorial civil service —
communes, departments, regions, CCAS, intercommunalités. **26 613 posts**
nationally, 643 in the Rhône alone.

These are the jobs of French local government, and no private board carries
them. With `talentsoft.md` reaching the state portal
(`choisirleservicepublic.gouv.fr`), the two halves of the French public sector
are now covered.

**Everything here was verified against the live site on 2026-08-31.**

## Search is a session, not a URL

There is no query string to construct. The filter is POSTed once, then pages
are asked for by number and **the server remembers the criteria** — so a cookie
jar is not optional, it is the mechanism.

```
GET  /rechercher                    → page 1, and the session
POST /rechercher                    → applies the filter
POST /recherche_emploi_mobilite/    → page=N&ajax=1, one page of rows
```

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/job-scan/scripts/emploiterritorial.py" \
  search --departement 69 --pages 5
```

Twenty posts a page. Nationally that is over 1 300 pages, so **filter first**:
`--departement` is the axis that matters, and the script reports how many of
the announced total it actually collected.

### `/exportoffres/` is disallowed, and is not used

`robots.txt` is otherwise open — `User-Agent: *` with only two PDF folders and
**`/exportoffres/`** closed. That export is real: the site's own JavaScript
builds `/exportoffres/?format=…&offres_to_add=…` for its "export selection"
button. **This adapter never touches it.** It reads the result pages a
candidate reads.

## Configuration

```yaml
boards:
  emploi-territorial:
    enabled: true
    departements: ["69", "01"]
    pages: 5
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `departements` | recommended | Written how you like — `69` is padded to `069`. Without one, the sweep is the whole country |
| `pages` | no | 20 posts each |

No login, no account, no API key.

## The ad id and its URL

The id is the portal's own reference in lowercase — `o069260831000101` — and
**its first three digits are the department**, so the card carries
`departement` without a lookup.

```
https://www.emploi-territorial.fr/offre/<id>-<slug>
```

In the ledger: `emploi-territorial:<id>`.

## What a row yields

Measured across 40 posts in the Rhône — **every field on every one**:

| Field | Example |
| :-- | :-- |
| `title` | Coordonnateur.trice adjoint.e périscolaire |
| `employer` | **VILLEURBANNE**, METROPOLE LYON |
| `grade` | `Grade(s)` is plural: *Animateur, Animateur principal de 1ère classe* |
| `reference` | O069260831000101 |
| `published` | 31/08/2026 |
| **`closes`** | **04/10/2026** |

**The closing date is real.** It is the *date limite de candidature* the
employer set — not `datePosted` plus a constant, which is what `meteojob.md`
(+60 days) and `hellowork.md` (+30) publish. On this board, an expiry means
something, and it belongs in the ledger.

The employer is the collectivité itself: no intermediary, no anonymity.

## Traps

**1. A department code is three digits, and two digits returns zero.** The
form's own values are `001`, `069`, `02A`. Posting `69` is **accepted** and
matches nothing: `0 results`, no error, no warning — which reads as *"no local
government jobs in the Rhône"*. The script pads, and says so when a search
comes back empty.

**2. `X-Requested-With` on the filter POST silently costs you the total.** Send
it and the server answers with a bare row fragment instead of the results page.
The fragment still contains ads, so the sweep looks fine — but `nb-offres` is
gone with it, and the run no longer knows how much of the board it has. Only
the pagination call is an AJAX call.

**3. The `valeur` span is not text, and two obvious regexes both fail the same
way.** *"Employeur :"* wraps its collectivité in a link containing an icon
span. Capturing `[^<]+` after the span yields whitespace; capturing to the
first `</span>` stops at the inner tag. **Both produce a field that is present
and empty on every single ad** — the shape of failure this repository keeps
meeting. The value is sliced with a depth counter instead
(`span_value`).

**4. Every row renders twice.** The desktop layout and a mobile duplicate live
in the same `<tr>`, so every field appears twice and a naive "collect all
matches" doubles the board. Each field is taken from its first match.

**5. The visible dates are relative; the real ones are in tooltips.** The row
reads *"publié aujourd'hui"* and *"expire dans 29 jours"*. The
`data-tooltip` attributes carry `publié le 31/08/2026` and `Date limite de
candidature le 04/10/2026`. Parse the tooltips; a relative string is worthless
the day after it is read.

## Applying

Applications go to the collectivité, through the portal or by post depending on
the employer — public-sector recruitment often wants a formal letter and a CV
by a stated deadline. **The plugin does not create accounts and does not fill
credential fields.** Hand the user the ad URL, and the `closes` date, which
here is a real one.

## Pace, and the note on access

One request per page of 20, spaced by `--delay` (default 1s), on a site whose
`robots.txt` closes only the bulk export. A filtered department is a handful of
pages; the whole country is not something to sweep, and the script says so
rather than trying.
