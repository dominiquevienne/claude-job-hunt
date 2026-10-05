# Board assessment — DiData careers (Lausanne): 14 cards, 8 open, and the closure signal is a field another reading called meaningless

<!-- verified: 2026-10-05 -->

<!-- hosts: swissdidata.com, www.swissdidata.com -->
<!-- script: didata.py -->
<!-- countries: CH -->
<!-- content: measured · 14 cards emitted from the listing, of which 8 open and 6 marked «Not available» by three markers that agree on 14 of 14, against 8 hrefs (exactly the open ones) and 13 `/careers/<slug>` pages in the declared sitemap — three enumerators, and the size of this board is NOT established because 6 cards carry no slug at all; the route returns no `JobPosting`, no `ld+json` and no date of any kind on the listing or on 7 ad pages read, so the ledger's date stays empty, and the ad page carries no availability signal whatsoever, read by `didata.py list --all --fetch` · 2026-10-05 -->
<!-- witness: the declared sitemap `/sitemap.xml` → `sitemap-0.xml`, 288 URL of which 42 under `/careers` and 13 `/careers/<slug>` pages in the default locale — **and it is a witness that cannot arbitrate**: it nests cleanly inside the listing's slugs, which says nothing about the six cards that have no slug -->

**Requested in #864, and the premises were re-measured rather than repeated.**
*The most important one was wrong in the direction that hides work.*

## 14 cards, 8 open: the closure signal is the field #864 read as meaningless

```
<span class="hidden">Not available</span>                                        OPEN
<span class="inline-flex … bg-yellow-200 … opacity-100">Not available</span>     CLOSED
```

#864 reports the first form *«present on all 14 cards — a hidden, empty field,
**NOT a closure signal**»* on 2026-09-22. On 2026-10-05 the page carries **14
cards: 8 in the first form and 6 in the second** — a **visible yellow badge**
reading «Not available», on a card whose container also carries
`cursor-not-allowed opacity-60` and whose anchor is `href="#"`.

**Three independent markers, and they agree on 14 of 14**: the badge's
visibility, the greyed container, the dead anchor. *The adapter requires them to
agree and emits no status when they do not* — three redundant markers that
disagree mean the markup changed, and guessing which one still means what is how
a closed position is reported as open.

> **And this resolves what #864 left open.** It counted *«11 distinct hrefs for
> 14 cards — three cards share a description page or link elsewhere; not
> resolved»*. The unlinked cards are the **unavailable** ones. **The href count
> is the count of OPEN positions**, and taking it for the board's size
> under-reads it by six — `zero-lien-nest-pas-zero-contenu` in its partial
> form, a 43 % loss with nothing raised and nothing logged.

*It is not an error in the report: on 2026-09-22 eleven of fourteen were open,
so the reporter saw eleven hrefs and a field that was hidden on every card it
looked at. **The form that carries the meaning was simply not on the page that
day** — the same shape as a guard that cannot fire.*

## The signal lives on the LISTING only — and Fit1Job is the exact mirror

Measured the same afternoon on the ad pages of two positions the listing marks
unavailable:

| URL | code | bytes | notice on the page |
| :-- | :-- | :-- | :-- |
| `/careers/content-writer` | 200 | 32 316 | **none** |
| `/careers/application-engineer-ch` | 200 | 43 507 | **none** |
| `/careers/back-end` *(open)* | 200 | 32 910 | none |

**A closed position's ad page is indistinguishable from an open one's** — same
`h1`, same `Type:` / `Location:`, same apply token, same `mailto`, no «Not
available» anywhere. *So on this host `shared/ats-open-check.md` step 1b must
read the LISTING; the ad page cannot answer.*

**And `fit1job.md`, delivered the same day, is the opposite**: there the listing
silently drops a retired advertisement and the ad page answers 200 **without its
`JobPosting`**, so the signal is on the ad page and only there.

> **Two hosts, one afternoon, opposite answers to the same question.** *Which is
> the general rule rather than two anecdotes: **where a host states availability
> is a property of that host**, and it is found by measuring both surfaces — not
> assumed from whichever one a previous board happened to use.*

## Three enumerators, and a clean inclusion that proves nothing

```
listing cards                        14     8 open, 6 unavailable
listing hrefs                         8     exactly the open ones
sitemap, default locale              13     slugs with a real ad page
```

The sitemap holds ad pages for **five of the six** unavailable cards, plus one
slug — `application-engineer-de` — that has **no card at all**. The listing
holds «Graphic Designer» and «Sales Manager», which the sitemap does not name;
`/careers/sales-manager` answers **404**, so a card can outlive its page.

**All 8 linked slugs are in the sitemap, so slug-against-slug is a clean
inclusion** — and a reader who stops there concludes the sitemap is the
enumerator. **It is not: six cards carry no slug, so the comparison cannot reach
them.**

> **A clean inclusion between the keys the two sides SHARE says nothing about
> the records that have no key.** *So the size of this board is not established.
> Both are walked, the union is emitted, and every record names its
> enumerator.*

*And a card is never joined to a sitemap slug by resembling it.* «Application
Engineer - Switzerland» and `application-engineer-ch` are obviously the same
position to a human; matching them by pattern is an inference, and a wrong join
would attach one position's text to another's status.

## The slug suffix is not one dimension, so it is not a dedup key

| slug | its own `<title>` | `Location:` |
| :-- | :-- | :-- |
| `application-engineer-it` | «Application engineer Italy» | Milan, Italy (Hybrid) |
| `application-engineer-ch` | «Application Engineer Switzerland» | Hybrid (Switzerland-based) |
| `application-engineer-de` | «Application Engineer Schweiz (**Deutsch**)» | — |

**`-it` and `-ch` are places; `-de` is a LANGUAGE.** *Its own title says
Schweiz, so it is the German rendering of the `-ch` position under a different
slug.* **Dedup by slug therefore over-counts by at least one**, and nothing here
guesses which suffixes are languages — it is named, not resolved.

*The locale PATHS are a different matter and are dropped, because the path says
so: `/fr/careers/back-end` is «Développeur·se Backend - Laravel» with
`lang="fr"`, a different document (md5 `1ff46239b4c7` against `561669b7955b`)
and the same position.*

## Open by plain HTTP — no browser, no key, no login

```
GET /careers                      200    55 666 B
GET /sitemap.xml                  200       189 B   (an index)
GET /sitemap-0.xml                200   166 993 B
GET /careers/<slug>               200   ~32–45 000 B
GET /careers/sales-manager        404
```

`robots.txt` read 2026-10-05 (`state: read`, `certain: True`): `User-agent: *`
/ `Allow: /`, a `Host:` line and a `Sitemap:` line. **No `Crawl-delay`, for `*`
or for any named agent** — so this host asks for no rate; the adapter paces
itself at **1 s** and prints that provenance on its first line. *A host that
sets no rate is not a host that wants none asked of it.* Guard taken on
`/`, `/robots.txt`, `/careers`, two ad paths, `/sitemap.xml` and `/_next/data`,
on **both** host forms, in a turn of its own before anything was fetched; the
host that answered is `swissdidata.com` on every form.

## The React Flight payload doubles every count taken on the raw body

`self.__next_f` appears 13 times and **repeats the cards as escaped strings**:
«Not available» occurs **28 times in the body and 14 times in the rendering**.
*A count taken without stripping `<script>` is exactly double*, and the payload
also names a build artefact — `page-2ab93bb6ffa11502` — that looks like a slug.

## What the route does not return

- **No `JobPosting`, no `ld+json`, no date of any kind** — not on the listing,
  not on **7** ad pages read. *So the ledger's date stays EMPTY rather than
  derived: an empty field is a question, a wrong date is an answer.*
- **No salary.** `Type:` (Full-time / Part-time) and sometimes
  `Experience:` (1 of 7 pages) are all the structure there is.
- **The card's title and the ad page's title are different strings** — card
  «Backend Developer», `h1` «Backend - Laravel». *A ledger keyed on the title
  would see two positions*; the slug is the key.

## The apply route, and the one figure this card withholds

Each ad states an application **mailbox** and a **mandatory subject token**:
`frontendev26`, `backendev26`, `DEVOPS26`, `FULLSTACK26`, `QA26`, `APPENG26`,
`marketing26`, `SALESEN26`, `APPENGCH26`, `APPENGIT26`, `CW26`, `DOC26`.

**#864 proposes the token doubles as a rough date** (*«…23 for a posting that
looks evergreen since 2023»*). **The measurement refutes it as a date and keeps
the shape**: the suffix is `26` on **12 of 12** tokens read on 2026-10-05, and
#864 read **`backendev23`** on `back-end` on 2026-09-22. *It is year-shaped and
it MOVED in thirteen days, so it tracks the employer's edit and not the posting
— neither a date for the advertisement nor a stable key.*

**The mailbox value is not written here and the adapter does not emit it.** *It
is the employer's own candidate contact, and `README.md` distinguishes that from
a leak — but this is produced under a standing instruction that no e-mail
address appears in this session's output.* **A rule given to me is not mine to
relax because a precedent would allow it**: the row says an address is present
and where to read it, and the question of whether an employer's published
application mailbox falls inside that instruction is raised rather than worked
around.

## What it adds, and what is not established

**The employer is named** — it is this employer's own list — so the ledger's
employer dedup works against the Indeed mirror, which #864 says carries the
same text word for word and showed 3 positions against 14 here.

*What this adapter adds over an Indeed sweep is therefore the whole list, the
closure marking Indeed's card does not carry, and the apply instruction it
hides.*

- **The `_next/data` route was never called.** The rendered HTML carries every
  card, so nothing needed it; its rules permit and nothing else is known.
- **The `/fr/` and `/de/` listings were never walked** — only one ad page in
  `/fr/`, to establish that the locale paths are translations.
- **No date exists**, so freshness on this board is unmeasurable from here.
  *A position can sit «Not available» indefinitely and nothing times out.*
