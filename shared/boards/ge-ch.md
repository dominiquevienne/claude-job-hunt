# Board adapter — État de Genève (`www.ge.ch`): one employer, and that is the point

<!-- verified: 2026-09-11 -->

<!-- hosts: www.ge.ch -->
<!-- script: gech.py -->
<!-- host-forms: www.ge.ch -->
<!-- host-forms-basis: read — `gech.py:BASE`, a single literal; the apply link points at `ge.ch/sirhrecrutement/…`, which is never fetched · 2026-09-11 -->
<!-- countries: CH -->
<!-- content: measured · 82 advertisements, every one an `<article>` on the single list page `/offres-emploi-etat-geneve/liste-offres` (245 760 bytes, no pagination), each advertisement page carrying exactly one `JobPosting` in JSON-LD; 75 on 2026-09-09 (#203) · 2026-09-11 11:52 UTC -->
<!-- witness: second route of the same operator — the RSS feed `/rss/offres-emploi-etat-geneve` lists 82 `<guid>`, the SAME 82 ids as the page, 2026-09-11 11:52 UTC. Immune to a broken `<article>` pattern (it is read by another pattern), NOT to a defect upstream of both nor to the flow. The page itself states no total · 2026-09-11 -->

**#203 asked for the board; #204 settled that it is admissible.** *«&nbsp;un
adaptateur pour un seul employeur peut avoir un intérêt. Le but d'un adaptateur
n'est pas uniquement de couvrir plus, mais aussi de potentiellement laisser
l'opportunité à un utilisateur de n'utiliser qu'un segment des offres&nbsp;»* —
the owner, 2026-09-09. The canton is one employer in law; on this list it is
eight departments, the judiciary, the court of auditors and the parliament's
secretariat, publishing side by side. **This adapter reads that segment, with
the five filters the site's own form offers, and no apology for the count of
employers.**

**Why it matters, measured (#203, 2026-09-09):** a `jobroom.py` sweep of
VD/GE/FR/NE/JU/VS/BE returned 136 rows, 30 in Geneva across 23 employers —
**none the État de Genève**. LinkedIn carried one of these advertisements as a
title and a place; the two requirements that decided its verdict — «Master en
informatique», «8 ans minimum» — were only on `ge.ch`. *0 of 30 GE rows, one
sweep, one day: a sample, not a proof — and enough to say coverage is not
acquired.*

## The list — one page, server-rendered, five filters, no total

```
GET https://www.ge.ch/offres-emploi-etat-geneve/liste-offres          200, 245 760 B
     82 <article>, 82 distinct ids, 0 <article> without an advertisement link
     0 JSON-LD blocks — on the list; the advertisement page has one (below)
```

**Every vacancy is an `<article>` in the served body** — no browser, no
cookie, no key, and **no pagination was found**: 82 advertisements on one
page, and the RSS lists the same 82. *Whether the page paginates past some
count is not established — it has not been seen to.*

**The filters are the form's** (`<form id="gech-offres-emploi-filters">`,
`method="get"`), five of them, and the URL carries all five with `0` for
«Tous»:

| form key | `gech.py list` | values | exercised 2026-09-11 |
| :-- | :-- | :-- | :-- |
| `type_contrat` | `--type cdd\|cdi\|apprentissage` | the site's literals, `Contrat d'apprentissage` included | `--type cdi` → **51 of 82** |
| `departement` | `--departement <part of the name>` | **UUIDs read off the page at run time**, never hard-coded; ambiguous → refuses and lists | `territoire` → «Département du territoire» → **5**, the unfiltered page's own count for it |
| `classe_fonction_min` | `--classe-min 4..33` | option `n` = classe `n + 3` | `--classe-min 20` → **30**, classes 20–27, none without |
| `taux_activite_max` | `--taux-max 10..100` | tens | not exercised |
| `domaine_activite` | — | 23 UUIDs, `00. Management` … `22. Elaboration et pilotage…` | not exposed, not exercised |

*Each exercised filter REDUCES the 82 — a filter that fails toward everything
looks exactly like one that works, so the reduction is the check.* **With a
filter on, the RSS is not compared**: the feed is unfiltered and would answer
another question.

### The count, and its anchor

**The page states no total** — no «82 offres» anywhere in 245 kB. So the
adapter prints `82 emitted of 82 advertisement(s); 82 <article> on the page, 0
without an advertisement link; page states no total`, and takes its anchor
from the only route that does not share the `<article>` pattern:

```
GET /rss/offres-emploi-etat-geneve?departement=0&domaine_activite=0&classe_fonction_min=0&type_contrat=0&taux_activite_max=0
     208 905 B, 82 <item>, 82 <guid> — the same 82 ids
```

Read by default (one request), skipped with `--no-rss-check`. **Name the
species**: a second route of the same operator on the same day. It catches
an `<article>` pattern that stopped matching — which is the defect this
adapter can have — and nothing upstream of both. *`unlinked` is counted in the
branch where an `<article>` carries no advertisement link, so
`linked + unlinked = <article>` is a check on the pattern and not an
identity.*

## The advertisement — a `JobPosting` in JSON-LD, plus four fields only the page has

`GET /offres-emploi-etat-geneve/liste-offres/2002` — 200, 107 819 B, **exactly
one `JobPosting`** (`_ldjson.postings` reads it as it is):

```
title, description, experienceRequirements, jobBenefits
datePosted 2026-09-09 · validThrough 2026-09-25 · jobStartDate 2026-09-11 (!)
employmentType CDI · hiringOrganization «Etat de Genève»
employmentUnit.url  https://www.ge.ch/organisation/departement-institutions-du-numerique-din
jobLocation.address «Rue du Grand-Pré 64-66 - 1202»   ← one string, street and postcode
```

**`experienceRequirements` is the field #203 says decided its verdict**, and
it is not on the list card — which is what `ad` is for. The page adds what the
JSON-LD lacks: **«Rémunération : classe 25»**, **«Taux d'activité : 80 à
100%»**, **«Délai d'inscription : 25.09.2026»**, «Entrée en fonction : Dès que
possible», and the apply link
`https://ge.ch/sirhrecrutement/recrutement/candidatAction.do?NOREFPOSTE=115353`
— `NOREFPOSTE` is the HR system's own reference, emitted as `reference` beside
the URL id.

## Traps

**Three shapes of the entity block on one page, and a pattern written for the
first read 66 of 82.** The department is a link to
`www.ge.ch/organisation/<slug>` (66 cards), OR a link to another host —
`https://justice.ge.ch/fr` for «Pouvoir judiciaire» (8) — OR a bare `<p>` with
no link at all («Secrétariat général du Grand Conseil», «Autres», 8). *What
the three share is the class `text-label-medium`; the office is the `<p>` that
follows.* Emitted as `entity`, `entity_url` (74 of 82 have one), `office`
(68 of 82 — fourteen are an empty `<p></p>` on the page itself).

**The salary class is carried as written.** «classe 12» on 79 of 82; **«À
définir»** on the three traineeships. A pattern on `classe \d+` reported those
three as having no class, which is not what the page says.

**Two date traps.** The RSS `pubDate` is not the posting date — id 2048 reads
`Fri, 11 Sep 2026 11:50:38 +0200`, the day of the read; the page's
`datePosted` says 2026-09-09 for id 2002. And **`jobStartDate` is the day of
the read when the page says «Dès que possible»** — id 2002: `2026-09-11`, read
2026-09-11, page «Entrée en fonction : Dès que possible». `starts_text` carries
the words; `starts` alone would say a job began the day you looked. *A
traineeship with a real date (id 2067) carries it in both: `2027-01-25` and
«25.01.2027».*

**The JSON-LD strings are HTML-escaped inside the JSON, some twice.**
`description` carries `&#039;`; id 2067's `experienceRequirements` carries
`&amp;#58;`. The adapter unescapes twice and strips the U+200B that opens
`experienceRequirements` and `jobBenefits` — invisible, and kept by `strip()`.
And the site's own text glues a heading to its paragraph («PrérequisMaster
universitaire…»): that is the data, not a reading.

**`grep -rl "ge\.ch" shared/boards/` returns `michaelpage.md`** — «ge.ch» is a
substring of «michaelpa**ge.ch**». A duplicate check on the bare pattern finds a
card that is not this one; anchor on a domain boundary (#203).

## Configuration

```yaml
boards:
  ge-ch:
    enabled: true
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |

No credentials, no browser, no locale. The filters are run-time flags, not
config keys — the segment is chosen per sweep.

## The ledger

`ledger_id` is `gech:<id>`, the integer in the URL — short, stable, and the
RSS `<guid>`. `url` is the advertisement page; `apply_url` is the HR system's
form and is never fetched here.

## Pace

The host declares no `Crawl-delay`; the adapter spaces its own requests at
2 s (`Pace("www.ge.ch", own=2.0)`) — a default, not a margin under a measured
limit. A whole sweep is **two requests** (list + RSS); `ad` is one per
advertisement.

## What is not established

- **Pagination**: the list held all 82 on one page; a longer list has not been
  observed and the adapter does not page.
- **The apply flow**: `sirhrecrutement/…/candidatAction.do` is recorded and not
  followed.
- **The advertisement page shape**: read in full on **two** of 82 — id 2002
  (CDI, classe 25) and id 2067 (traineeship, «À définir») — and the four
  page-only fields were matched on both.
- **Other cantons**: #203 argues the shape repeats across Romandie. Nothing
  here has been run against another canton's portal, so that stays an
  argument, not a measurement.

## 2026-09-11 — shipped

Measured 11:48–11:54 UTC: robots `read`, `sweep: True`, `certain: True`,
`allowed: True` on the list, an advertisement and `/`; list 200 / 245 760 B /
82 ids; RSS 82 `<guid>`, same set; ad 2002 200 / 107 819 B / one `JobPosting`;
`--type cdi` 51, `--departement territoire` 5, `--classe-min 20` 30.
