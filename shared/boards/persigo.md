# Board adapter — persigo.ch

<!-- verified: 2026-09-02 -->

<!-- hosts: www.persigo.ch -->
<!-- script: persigo.py -->
A Swiss staffing **agency** board, like `michaelpage.md` and `fachkraft.md`:
`hiringOrganization` is *Persigo AG* on every ad and **the client employer is
never named**.

Server-rendered HTML with a `JobPosting` block on every ad. **No key, no cookie,
no browser.**

Read by `skills/job-scan/scripts/persigo.py`.

**Verified 2026-08-29**, re-run 2026-09-02: the whole board in one request,
**887 ads today against the 890 of the first pass** — the board's own stated
figure both times, so the drift is the board's, not the parse.

**The constraint held on re-run**: `hiringOrganization` is *Persigo AG* on
**887 of 887**, and the client employer is named on none. That is the claim
worth re-testing here, because it is the one that decides whether these ads
can ever be matched against an employer's own ATS.

## The whole board in one request

`/stelle-finden/` ships all **887** ads — the figure the page states, 890 on
2026-08-29 — as
`<div class="row listitem listitem-<TOKEN>">` blocks. There is no pagination to
write, and each card already yields:

```
token | title | town | sector | contract type
9YNM68 | (Junior) Techniker:in HF Hochbau … | Raum Sursee |
        Ingenieurwesen / Projektmanagement | Festanstellung
```

The ledger key is that token, and **it rebuilds the URL on its own**:

```
persigo:<token>          e.g. persigo:00G6LE
                         -> /stelle-finden/stelle/00G6LE/
```

## Age is the only staleness signal, and the listing does not carry it

**There is no `validThrough` anywhere on this board** — unlike sozialinfo,
fachkraft or Prospective, so the expiry rule in `shared/ats-open-check.md`
cannot help here.

**And the listing carries no date at all.** Only the ad page does, as
`datePosted` in its `JobPosting` block.

That combination matters more than it would elsewhere, because **this board
keeps ads a long time**. Of 14 ads sampled at random from the 890:

| Posted | Count |
| :-- | --: |
| 2026 | 11 |
| **2025** | **3** — the oldest 2025-05-23, over a year old |

So a listing row on its own says nothing about freshness, and 890 is not 890
current openings. `list` says so on every run that omits `--with-detail`, and
`--with-detail` fetches each kept ad for its date and full text — one request
per ad, and the only way to know an ad's age here. **Filter first.**

## Traps

**1. Local filtering only.** The search form is a TYPO3 Extbase extension
(`tx_wttempro2_employeelisting[...]`) whose POST needs `__trustedProperties` and
`__referrer` tokens. The whole board already arrives in one request, so the
adapter filters locally and does not touch that machinery — which would break on
the next TYPO3 upgrade.

**2. The town is on the card, not in the JSON-LD.** `jobLocation.address`
carries only `addressRegion` (`LU`); the listing card carries the actual place
(`Horw`, `Raum Sursee`). Reading location from the structured data alone loses
it. The adapter takes the town from the card and the region from the ad.

**3. `identifier` is useless.** It is `{"@type": "PropertyValue", "name":
"Persigo AG"}` — the agency, on every ad, with no value. Do not build a key
from it; the URL token is the id.

**4. The employer is never named.** The card carries `company: null` and
`employer_named: false` rather than writing *Persigo AG* where the ledger
expects the company the user would work for. The fuzzy employer-name dedup
cannot match these ads against the same role on an employer's own ATS — expect
that duplicate to survive.

## Is it still open?

| Response | Reading |
| :-- | :-- |
| `200` + a `JobPosting` block | **Listed** — but check `datePosted`, see above |
| `404` | **Not listed** |
| `200`, no `JobPosting` | A page-shape change, **not** a dead ad |

`persigo.py check --token …` returns this with the posting date, and exits `0`
only when open.

## Applying

Through the agency, and through a consultant. The plugin does not create
accounts and does not fill credential fields — hand the user the ad URL and
their documents, and tell them the employer's identity usually arrives only
after contact.

## Pace

One request for the whole board. `--with-detail` is where the cost is: one per
kept ad, so narrow with `--search`, `--place` and `--type` first.
