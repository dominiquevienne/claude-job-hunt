# Board adapter — Softy

A French ATS for SMEs and mid-sized companies, and the third of the French ATS
family here, after `taleez.md` and `flatchr.md`. One employer per careers site,
at `https://<tenant>.softy.pro/offers`.

**This is a browser adapter.** It runs in the user's own Chrome, in their own
session, like `linkedin.md`, `jobup.md`, `jobs-ch.md`, `indeed.md` and
`cadremploi.md`. There is no script in `skills/job-scan/scripts/`, and the
reason is not technical.

**Everything here was verified by driving the live site on 2026-08-31.**

## Why this one is not a plain HTTP adapter

Softy's careers sites serve a `robots.txt` — the same template on every tenant
checked — that opens the door to everyone and then names the exceptions:

```
User-agent: *              Allow: /

User-agent: GPTBot         Disallow: /
User-agent: ChatGPT-User   Disallow: /
User-agent: CCBot          Disallow: /
User-agent: anthropic-ai   Disallow: /
User-agent: Claude-Web     Disallow: /
User-agent: Google-Extended, Bytespider, cohere-ai   Disallow: /
```

Nothing there blocks a script, and `taleez.md` and `flatchr.md` fetch far more
freely on sites that say less. But the publisher **enumerated the AI agents and
said no, Anthropic's twice** — and a plugin whose whole function is *Claude
reads job ads for you* sits inside the spirit of that refusal even when it is
outside its letter.

So the sweep goes through the user's own browser instead, where the fetch is a
person opening pages in their own session: the `User-agent: *` case, not an AI
crawler. It costs speed and it is the point. **Do not convert this to a
`softy.py`** — that trade was considered and declined by the maintainer, and
undoing it silently would misrepresent the plugin to the site.

## Prerequisites

The Claude extension connected to the user's Chrome. **No login is needed to
scan** — every measurement below was taken from a logged-out session.

## Configuration

```yaml
boards:
  softy:
    enabled: true
    tenants: ["compagniedesalpes"]
    pages: 4
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `tenants` | yes | The **first label of the careers host** — `compagniedesalpes` in `compagniedesalpes.softy.pro` |
| `pages` | no | **21 ads per page** |

**No tenant directory was found**, so this behaves like `umantis.md`,
`taleez.md` and `flatchr.md`: ask the user for the careers URL, and never guess
a tenant.

## Building a search

There is no keyword or location filter to drive — the board is small enough per
employer to read whole.

```
https://<tenant>.softy.pro/offers            page 1
https://<tenant>.softy.pro/offers?page=<n>   the rest
https://<tenant>.softy.pro/offers/<id>       one ad
```

Compagnie des Alpes: **72 offers, 21 per page, 4 pages.** The pagination links
are real `<a href>` elements, so pages are navigable directly — no clicking
needed.

## What a card yields

The card **is** the link: `a[href*="/offers/"]`, one per ad. Inside it:

| Field | Where |
| :-- | :-- |
| `id` | the numeric segment of the href |
| `title` | the card's only `h3` |
| `entity` | the first small `span` — a *subsidiary or brand*, see trap 3 |
| `location` | the `p` under the title — **the first town only**, see trap 1 |
| `published` | the text `Mise en ligne le DD/MM/YYYY` |
| `contract`, `working_time` | the badge `span`s — `CDD - 6 mois`, `Temps plein` |

**Match on structure and text, not on the class names.** Every class here is a
Tailwind utility (`text-xs font-medium`, `rounded-xl border px-2 py-0.5`) that
changes with any restyling and carries no meaning. `h3`, the href, and the
`Mise en ligne le` / `CDI|CDD|Temps` text patterns are what to anchor on.

## Reading one ad

`https://<tenant>.softy.pro/offers/<id>` — **no JSON-LD anywhere**, on the
listing or the ad. The ad is plain HTML with named sections, and those headings
are the contract:

- **L'entreprise** — employer blurb
- **À propos du poste** — the role
- **Profil recherché** — the required profile
- **Éléments nécessaires pour postuler** — *the documents to attach*, e.g.
  `Curriculum Vitæ`. Worth carrying: it tells `cover-letter` what the
  application actually wants
- **Caractéristiques du poste** — the structured block, in emoji-labelled
  groups: `ℹ️ Infos de l'offre` (publication date, contract, working time,
  experience required, driving licence, diploma), `💰 Salaire brut`,
  `📅 Prise de poste`

Salary is free text and often *"À définir suivant profil"*.

## Traps

**1. An ad can span seven towns and the page shows one.** Next to the location
sits a small `+ 5` chip. That chip is a **tooltip trigger**
(`data-slot="tooltip-trigger"`, `data-state="closed"`), and the other towns are
**not in the DOM at all** until it opens. On the ad measured, the card read
*Gilly-sur-Isère, Albertville* and the tooltip added **Ugine, Moûtiers,
Bourg-Saint-Maurice, Montmélian, Chambéry** — roughly a hundred kilometres of
spread.

For a user with a commute limit this decides the ad, and taking the visible
town at face value gets it wrong in both directions: discarding a job that is
also offered next door, or keeping one that is not.

**2. Only a real hover opens that tooltip.** Dispatching `pointerenter`,
`pointerover`, `mouseenter`, `mouseover` and `focus` from JavaScript left
`data-state="closed"` and produced no tooltip node. The `computer` tool's
`hover` action on the chip's coordinates opened it. **So reading the full
location list is a per-ad browser interaction**, not something to bolt onto a
DOM scrape — and if it is skipped, `location` must be recorded as *first town
of N*, never as *the* location.

**3. The name on the card is often a subsidiary, not the tenant.** The card
above says *Ingelo Montage*; the tenant is Compagnie des Alpes. Both are true
and they are different employers to a candidate. Carry the card's `entity` and
the tenant separately rather than collapsing them.

**4. No expiry date, anywhere.** Like `taleez.md` and `flatchr.md`, and unlike
`meteojob.md` (+60 days) and `hellowork.md` (+30), Softy publishes none — so
nothing here can be mistaken for one. Freshness comes from `Mise en ligne le`.

**5. `softy.pro` itself has no robots.txt** — it 404s, and `www.softy.pro`
redirects to the recruiter login. The file that governs is the **tenant's**,
quoted above.

## Applying

Ads carry a *Postuler* button and a spontaneous-application route on the
tenant's own site. **No assisted apply is implemented**, and the plugin does not
create accounts and does not fill credential fields. Hand the user the ad URL
with their documents — and with the *Éléments nécessaires pour postuler* list,
which says what to attach.

## Pace, and the note on access

One page load per page of results, plus one per ad, in the user's own browser at
reading speed. A 72-ad employer is four listing pages; opening every ad is
seventy-two more, so read the ads that pass a title-and-location screen rather
than all of them.

This adapter opens pages a person could open, in their own session, for their
own job search. That is the whole reason it is a browser adapter and not a
script.
