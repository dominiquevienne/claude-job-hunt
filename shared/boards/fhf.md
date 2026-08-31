# Board adapter — emploi.fhf.fr

France's **public hospitals and medico-social sector**, on the Fédération
Hospitalière de France's own board. **No browser, no account, no key.**

CHUs, centres hospitaliers, EHPADs, USLDs, EPSMs — **13 175 ads** on the day
this was written, from aides-soignants and infirmiers to hospital directors,
finance and IT. The board belongs to the hospitals' own federation, so **the
employer is the employer**: never an agency, never an unnamed end client.

**Everything below was measured against the live site on 2026-08-31.**

## Configuration

```yaml
boards:
  fhf:
    enabled: true
```

No settings. Scope is set per search.

## Usage

```bash
fhf.py list --category ADM/INF --pages 3
fhf.py list --department 69 --details
fhf.py list --search "cadre de sante" --posted-within-days 14
fhf.py ad    --id 488708
fhf.py check --id 488708
fhf.py categories
```

## The endpoint

```
GET https://emploi.fhf.fr/emploi/search?keyword=…&type=…&department=…&page=N
GET https://emploi.fhf.fr/emploi/<id>
```

Server-rendered Drupal, **9 ads per page**, fixed — `items_per_page` is accepted
and ignored. `robots.txt` is Drupal's stock file: it closes `/admin/`, `/user/…`
and `/search/`, and **says nothing about `/emploi/search`**, which is a
different path. Nothing here touches a disallowed one.

## The trap that matters most: the first page was four days old

The site sets `cache-control: max-age=604800` — a week — and sits behind
Cloudflare. The same listing, three ways, measured in one minute:

| URL | `age` | Ads announced | Newest ad |
| :-- | --: | --: | :-- |
| `/emploi/search` | **345 688 s — 4.0 days** | 13 520 | 27.08 16:31 |
| `/emploi/search?page=0` | 6 586 s — 1.8 h | 13 159 | 31.08 14:56 |
| `/emploi/search?_=<random>` | **0 s** | 13 175 | 31.08 16:46 |

The bare URL answered **HTTP 200 with nine perfectly plausible ads** and a
headline **345 higher than the board actually held**. Nothing on the page says
it is stale; the only tell is a response header nobody reads. Four days is four
days of new ads a candidate never sees, and four days of ads that closed.

So **every request carries a per-run cache-buster by default**. `--cached` opts
back into the edge cache when speed matters more than the last few hours — and
says so on stderr, because a quiet fallback to a week-old board is exactly the
failure this whole file is about.

## Two more traps, both silent, both 200

**1. The array field names in the site's own HTML do not work as GET
parameters.** The filter form posts `department[]` and `contract[]`; the GET
route honours neither:

```
?department[]=75   → 0 ads, no total, HTTP 200
?department=75     → 377 ads
```

Copying a field name out of the page is the obvious thing to do, and it yields
an empty board that reads as a quiet market. The adapter sends scalars.

**2. Two different `<select>` elements are both named `type`.** One is the job
category (`ADM`, `SOI`, `MED`…), the other is the site-wide *"Que
recherchez-vous"* (`etablissement`, `direction`, `personne`, `service`). They
share one GET parameter. `?type=etablissement` returns an empty page with no
total — indistinguishable from a category with nothing open. `list --category`
therefore refuses a value that is not in `categories` rather than passing it on.

## What the pager does right

Past the last page the site answers 200 with **no cards at all** — not a repeat
of the final page, which is how `randstad.ch` and `free-work.com` behave. An
empty page here is a real end, and the counts prove it: `--category ADM/ENS`
announced **38** ads and the sweep returned **38**, terminating by itself.

## A full postal address on every single ad

36 of 36 sampled ads carried establishment, street, postcode and town:

```json
"address": {"name": "EHPAD Les Cordelières",
            "street": "BP 40009 Avenue de la Boire Salée",
            "postal_code": "49135", "locality": "Les Ponts-de-Cé"}
```

That is the field `shared/modules/job-room-ch.md` records as **the one most
often missing from a PRE**. It comes from the ad page, so it needs `--details`
on a sweep, or `ad --id`.

**The list has no location, and the adapter does not pretend otherwise.** The
establishment line ends in parentheses that are usually a town — *Hôpital
Lapeyronie (MONTPELLIER)* — and sometimes are not: *site de Fleyriat*, *siège*.
That value is passed through as **`site`**, never as `location`. Putting a
building name in the town field of an official declaration is precisely the
failure mode `talentsoft.md` was rewritten for.

## A named contact on half of them — and one thing this adapter will not do

Every ad has a *Personne à contacter*. On 18 of 36 it is a person, their role
and often a direct line; on 17 of 36 it is a link to the hospital's own ATS.

Addresses are wrapped in **Cloudflare's email protection**: the visible text is
the placeholder `[email protected]` and the real address sits in a
`data-cfemail` attribute, trivially reversible.

**It is not reversed here.** That obfuscation exists to stop harvesting, and a
sweep decoding it on every ad is harvesting whatever the intent. The card
carries `email_protected: true` and the ad URL; a candidate opening the page
they are about to apply to reads the address in one click. Same reasoning as
`softy.md`: the rule is read for what it is for, not for what it literally says.

The rest of the block is handed over as **`contact.lines`, unlabelled**, with
only the phone number and the apply URL pulled out by pattern. One ad reads
*MAESEELE Arnaud / Arnaud MAESEELE (DRH) / Laetitia KUBIAK (Cadre de santé)* —
two people, not a person and a job title. A rule promoting line 2 to `role`
would be filled, plausible and wrong on a third of ads.

## What FHF is worth beyond its own ads

**It is a listing for Beetween and a tenant directory for Softy.** Of 36 sampled
ads, 17 pointed at an external ATS:

| Host | Ads |
| :-- | --: |
| `app.beetween.com` | 6 |
| `*.softy.pro` (4 tenants) | 4 |
| the hospital's own site | 5 |
| `mstaff.co`, `mytalentplug.com` | 2 |

`france-travail.md` records Beetween as the **first supplier of France Travail's
partner feed** — 38 of 150 sampled Paris ads — arriving there with **no employer
named**. `README.md` records that no directory of Softy tenants exists. Here the
same ads arrive with the hospital named, its full postal address attached, and
the ATS URL in the open. An adapter that was declined as unbuildable on its own
terms turns out to be enumerable from the side.

## Fields

`ledger_id` is `fhf:<id>` — the numeric id in the URL, stable, no slug.

| Field | Where | Coverage |
| :-- | :-- | :-- |
| `title`, `company`, `published` | list | all |
| `site` | list | the establishment's parenthesis — a town or a building |
| `closes` | list | 10 / 36 — the employer's own deadline, not a formula |
| `teaser` | list | all, truncated by the site |
| `address`, `contracts`, `contact`, `description` | `--details` / `ad` | address all, `contracts` 24 / 36 |
| `external`, `external_host` | `--details` / `ad` | 17 / 36 |

`contracts` is **a list**: the board writes *"Détachement; Mutation; Stage"* for
one ad open to three statuses — one ad, not three.

## Exit codes

| Code | Meaning |
| :-- | :-- |
| `3` | `ad` or `check` on an id that 404s, or an ad past its closing date |
| `2` | an unknown `--category`, or the site unreachable |

`check` distinguishes `open`, `expired` and `closed`. An ad whose closing date
has passed still serves its page: without reading that date, `check` would call
it open forever.

## Pace

One request per page, one per ad under `--details`, `0.4 s` between them
(`--delay`). A department sweep with details is roughly one request per ad —
budget accordingly and filter first. `robots.txt` sets no crawl delay; this is
courtesy, not compliance.
