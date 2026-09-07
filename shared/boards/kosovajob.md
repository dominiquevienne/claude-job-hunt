# Board adapter — KosovaJob (Kosovo)

<!-- verified: 2026-09-07 -->

<!-- hosts: kosovajob.com -->
<!-- host-forms: kosovajob.com -->
<!-- host-forms-basis: read — `kosovajob.py:BASE`, a single literal; `cdn.kosovajob.com` serves logos only and is never fetched · 2026-09-07 -->
<!-- script: kosovajob.py -->
<!-- countries: XK -->
<!-- content: measured · 566 advertisements from one request to the homepage, 516 distinct slugs, 391 employers, 0 unreadable blocks; no sitemap is declared and none was composed · 2026-09-07 -->
<!-- witness: none found — the site states no total, and 566 is the count of rows it rendered rather than a figure it publishes · 2026-09-07 -->
<!-- overlap: ofertapune.md · 148 shared advertisements, slug match confirmed on the employer 148 of 148; 481 read on ofertapune and 566 on kosovajob, both from one request and neither board states a total · 2026-09-07 -->

**Kosovo's second board and the larger one**, measured hours after the first.
`ofertapune` gives 481 the same day; **148 are on both, so the two together
are not 1 047.**

## It shares ofertapune's template and not its database

Both hosts serve `jobListCnts` / `jobListCntsInner` / `jobListTitle date=` /
`jobListCity` / `jobListExpires`, and **the same advertisement leads both
homepages** — Sonnecto's *Call Agent (Deutsch)*, same title, same employer,
same 21 September deadline.

**But the identifiers differ: `109849` there, `47268` here.** *A shared
template names a supplier, not an operator.* Two id spaces carrying the same
vacancy is an employer posting twice, not one board wearing two names — and
the asset origins agree: this host loads logos from `cdn.kosovajob.com`,
which appears nowhere in ofertapune's markup.

## The overlap is 148, and it is a floor rather than a rate

Both boards' listing URLs end in a title-derived slug, so the slug is the only
key on offer. **It is an identifier on one board and not on the other:**

```
ofertapune   481 advertisements   481 distinct slugs
kosovajob    566 advertisements   516 distinct slugs
             `recepsioniste` × 6 · `kamariere-shankiste` × 6
```

So the intersection was confirmed against a second field rather than trusted.
**148 shared slugs, and the employer agrees on 148 of 148.** The five that
first read as disagreements were one employer spelled two ways — `H&M` folds
to `h-m` on one board and `hamp-m` on the other, likewise `Q.T.S`,
`G&G Group` and `Lily's Cafe`.

**Neither 481 nor 566 is a claim about everything either board holds**: both
are what one request returned on 2026-09-07, and neither site states a total.

## Two places where the shared template diverges, and both bite

**1. `jobListExpires` is a countdown here and a date there.** It reads
`15 ditë` — *fifteen days* — where ofertapune prints `21.09.2026`. A parser
copied across would yield `None` on every row, or worse, parse the `15`. The
absolute deadline is in the `date=` attribute of `jobListTitle`, as
`2026-09-21 23:55:00`, and that is what the adapter reads.

**2. `ids=` is a position counter here and the advertisement's id there.** It
runs `"5 0 100"`, `"6 0 101"` down the page. Reading it as an identifier would
mint a ledger key that changes whenever the page is reordered. **The listing
carries no id at all** — `jobID="47268"` exists only on the advertisement
page — so `list` keys on `<employer>/<slug>` and emits `id: null` with
`id_source` saying why.

*Two hosts, one template, and the field that means «deadline» on both carries
a different kind of value.* **Sharing markup is not sharing meaning.**

## The ledger key is the path even where the number is in hand

`ad` sees `jobID` and still keys on `<employer>/<slug>`. Keying it on the
number would give the same vacancy two ledger identities depending on which
command found it — `kosovajob:47268` from `ad` and
`kosovajob:sonnecto/call-agent-deutsch` from `list`, which is what the first
draft did. **A key that depends on the route taken is not a key.** The number
travels in `id`, where it costs nothing and claims nothing.

## The only date is again a deadline

`Skadon 21/09/26 (15 ditë)` on the advertisement page, `date=` on the listing,
**and no posting date anywhere on either board**. `--since` is therefore not
offered: a filter on a field the source does not carry returns everything in
silence, which reads exactly like a board on which nothing is old.

## What was measured, 2026-09-07

```
/robots.txt     44 bytes — `Disallow: /cgi-bin/` and nothing else, no sitemap
homepage        566 blocks · 516 distinct slugs · 391 employers · 0 unreadable
fields          title 566/566 · employer 566/566 (it is in the URL)
                expires 566/566 · city 566/566
ld+json  0      JobPosting  0
exercised       --city Prizren -> 24 · --city Zzzz -> 0
                --expiring-before 2026-09-10 -> 77 · a missing ad -> exit 3
```

The advertisement page adds the category (`Mbështetje e Konsumatorëve, Call
Center`), the schedule (`Full Time`) and **the employer's own domain**, which
the listing does not carry.
