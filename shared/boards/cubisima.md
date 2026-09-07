# Board adapter — Cubisima Empleos (Cuba)

<!-- verified: 2026-09-07 -->

<!-- hosts: www.cubisima.com -->
<!-- host-forms: www.cubisima.com -->
<!-- host-forms-basis: read — `cubisima.py:BASE`, a single literal. The apex `cubisima.com` appears in the site's own links and serves the same rules; only `www.` is fetched · 2026-09-07 -->
<!-- script: cubisima.py -->
<!-- countries: CU -->
<!-- content: measured · 6 068 advertisement ids for `la_habana` from one request, and 9 486 for the unfiltered national set; 30 cards rendered per page against pagination running to page 203 (203 × 30 = 6 090, the same set) · 2026-09-07 -->
<!-- witness: none published by the site — 6 068 is the length of the result array the listing page writes, and 203 is the last page number it links; the two agree to within one page · 2026-09-07 -->

**Cuba's first adapter.** Its country page recorded three open hosts, no
declared sitemap, and no measurement — *«ouverts et non mesurés, ce qui est un
état, pas un échec»*. There is still no sitemap. **There did not need to be
one.**

## One request returns every advertisement id for a province

The listing page renders thirty cards and, in the same response, writes the
complete result set into a JavaScript array:

```js
localStorage.setItem('searchAnuncios', JSON.stringify(["38600!2", "38599!2", …]))
```

```
la_habana        6 068 ids   ·   30 cards rendered   ·   pagination to page 203
                 203 × 30 = 6 090 — the same set, to within one page
```

**So the id list costs one request and the fields cost one request each.**
Those are different prices and the adapter keeps them apart: `list` gives ids
plus the thirty cards, `--fetch` calls the advertisement API per id.

## Nothing here is a guessed URL

**Every path is written down by the site:**

```
/empleos                          linked from the home page
/empleos/por-provincias           linked from /empleos
/empleos/ofertas/-/<place>        linked from /empleos/por-provincias   (199 places)
/empleos/empleo-api/<id>!<type>   the page's own click handler:
                                  fetch(`…/empleos/empleo-api/${guid}`)
```

The `-` in the listing path is **the site's own wildcard for «any category»**,
taken from its links rather than invented.

*`portaljob-madagascar` is the counter-case measured the same day:* there no
route was declared anywhere, and guessing one would have been a probe. **The
difference between the two hosts is not what we were willing to try — it is
what the page told us.**

## An unknown place returns the whole country, not nothing

```
--place zzz_pas_un_lieu    ->    9 486 advertisements, "place": "zzz_pas_un_lieu"
```

**A typo produces a number that is real, large, plausible and about the wrong
thing**, and nothing in the output says so. *A wrong `--place` is not a failure
mode a reader would think to check, because the failure looks like success at
a bigger scale.*

**So the slug is validated against the site's own 199 links before use**, at
the cost of one request, and an unknown one is refused with the closest
matches. *The 9 486 is recorded here because it is the national figure and it
was obtained by accident; it is not offered as a flag, because no national
listing URL is declared.*

## The contact details are on `ad` and never in a sweep

The API returns the poster's **e-mail, mobile, WhatsApp number and street
address**. `ad` emits them — that is the advertisement a person is about to
answer. **`list --fetch` withholds them at any size**, and says so in a
`contact_withheld` field rather than silently dropping them.

*The board publishes them either way; the difference is between a person
reading one advertisement and this project accumulating a contact list for a
country.* **A field being available is not a reason to carry it.**

## The card's date is relative, so `--since` requires `--fetch`

The card says *«Hoy»*, *«Ayer»*. **Turning that into a date at read time would
bake this run's clock into the row**, and a row keeps its value long after the
run. `Fecha` from the API is a real timestamp — `2026-09-07 10:20:26.000` —
and `--since` filters on that.

The card field is emitted as `posted_relative`, named for what it is.

## What the API carries, and what is dropped

43 fields, of which 15 are emitted by name and the rest are internal codes —
`CodigoTipoEmpleo`, `IsConfirmed`, `Visible`, `Destacado` — that mean nothing
outside the site. **Passing them through would invite filtering on them.**

```
title · role · employer · category · province · municipality · contract
level · schedule · shift · salary_text · requirements · details
employer_activity · views · posted
```

`salary_text` is free text (`8 500 a 12 000 cup`) and is named for that: there
is no numeric salary field on this board, and parsing one out of the string
would manufacture a precision the source does not have.

## No structured data, and none needed

`ld+json` and `JobPosting` are absent from every page here. **The API
supersedes them**, and it is the site's own — not a third-party schema
partially filled in.

## An unknown advertisement answers 400, not 404

Empty body, HTTP 400. Treated as **gone** (exit 3) rather than broken: the
request was well formed and the advertisement is not there. *Mutated both
ways — an invented id exits 3, a real one exits 0.*

## What was exercised, 2026-09-07

```
places                                    199 places, from the site's links
list --place la_habana                    6 068 ids · 30 cards
list --place la_habana --fetch --limit 3  3 read · 3 kept · 0 unreadable
                                          contact fields absent
ad --id 38600!2                           contact fields present
list --since without --fetch              exit 2, and it says why
list --fetch --since 2027-01-01 --limit 4 4 read · 0 kept · 4 dropped
list --place zzz_pas_un_lieu              exit 2 — before the fix, 9 486 ads
ad --id 99999999!9                        exit 3
```

**The two other Cuban hosts were measured the same evening**, and neither
adds coverage: `yellocu.md` is a business directory that carries no employment
word at all, and `revolico.md` answers the root with a Cloudflare challenge —
the one thing the browser branch is forbidden to defeat.

*So this is not one third of Cuba's coverage. It is Cuba's coverage.*
