# Board adapter — Rozgar (Pakistan)

<!-- verified: 2026-09-08 -->

<!-- hosts: www.rozgar.pk -->
<!-- script: none -->
<!-- countries: PK -->
<!-- content: indeterminate · the sitemap holds 3 URLs, frozen since 2020, and the 327 kB homepage carries 0 `JobPosting` — no enumerable surface was found on 2 paths · 2026-09-05 -->
<!-- witness: none found — nothing on the site states a total, and the sitemap counts pages rather than advertisements -->
<!-- hosts-source: third brand of the house that operates `rozee.pk`, itself found through `mihnati.com`'s declaration · 2026-09-05 -->

**Not disqualified. Not qualifiable.** The distinction matters and this card
exists to hold it: a board that refuses us, one that has closed, and one we
cannot count are three different facts, and the third is the easiest to write
as one of the other two.

## The site is in production and nothing enumerates it

```
sitemap          3 URLs, most recent lastmod in 2020
homepage         327 kB, 0 `JobPosting`
```

**Six years without a sitemap update, on a site that serves.** So the sitemap
is not a stale copy of the board — it never described it. And the homepage is
large and carries no structured posting, so the ads it shows are not machine
readable at the two entry points a reader would try.

**`content: indeterminate`, with the figure and the paths.** Not `measured`,
because nothing was counted; not `out-of-domain`, because it *is* a job board;
not `assumed`, because two paths were actually looked at. *A count refused is
worth more than a count reduced* — the module written for that trap says the
same thing about `<loc>` counts.

## The product is not the one the family's other brands sell

Blue-collar recruitment, where `rozee.pk` is white-collar. **That is a reason
to keep the card rather than fold it into `rozee.md`**: a second brand with a
different market is not a mirror, and if it ever publishes a feed it will
publish a different population.

## The house

`mihnati.com` · `rozee.pk` · **`rozgar.pk`** · `rozeegpt.ai` · `recruit-ai.co`

Found by following `mihnati.com`'s own `robots.txt`, which declares
`rozee.pk`'s sitemap index. See `rozee.md` and issue #163.

## What would reopen this

A feed, a sitemap that moves, or a listing page carrying `JobPosting`. **Any of
the three turns `indeterminate` into a number.** Until then this card records
that the question was asked and on which paths — which is the whole difference
between an unread board and an unexamined one.

## Re-measured 2026-09-08 — the listing endpoint answers 200 with an error

**Guard re-taken and it opens.** `robots.txt` disallows only `/beta/` and
`/demo/` and declares the sitemap; nothing here refuses us.

```
/jobs           HTTP 200,  31 bytes:  b'Passing data should be an array'
/sitemap.xml    HTTP 200,  3 <loc>,   every lastmod 2020-08-20
   /  ·  /how-it-works  ·  /post-job
/               HTTP 200, 327 209 bytes, 0 `JobPosting`, TWO internal links —
                both asset paths, so the navigation is in the bundle
```

> **`/jobs` is not empty and not refused: it is a framework error string served
> with a success code.** *«&nbsp;A readable body is not an answer — the code
> decides&nbsp;» has an inverse, and this is it: the code says 200 and the body
> says the handler broke.*

**Nothing measured here says the board has no advertisements**; it says the one
enumerable surface answers an error, the sitemap has been frozen for five
years, and the front page ships its routes inside a bundle. **Still
`indeterminate`, and now for a reason that names its own next step:** read the
bundle's route table, or find the API the front end calls.

*And the sitemap's own contents are the clearest thing on this host:
`/post-job` is in it and no job is.*
