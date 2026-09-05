# Board adapter — Rozee (Pakistan)

<!-- verified: 2026-09-05 -->

<!-- hosts: www.rozee.pk -->
<!-- script: none -->
<!-- countries: PK -->
<!-- content: measured · order of magnitude 52 readable advertisements, from 2 607 `<loc>` in `jobs.xml` of which the `.php` form is 52; 4 292 URLs in the index of which 1 685 are not advertisements · 2026-09-05 -->
<!-- witness: none found — the site serves no counter, and the sitemap's own totals count pages rather than advertisements -->
<!-- hosts-source: declared by `www.mihnati.com/robots.txt`, read with `bin/fetch-body.py` · 2026-09-05 -->

**Not built, and the figure is why.** Found because `mihnati.com` — a card of
this repository — declares **`https://www.rozee.pk/sitemap/sitemap_index.xml`**
in its own `robots.txt`. A host naming another host's sitemap is a statement by
the operator, not by an intermediary. Issue #163.

## Three numbers, and the one to publish is neither of the first two

```
jobs.xml            2 607 <loc>    advertisement URLs
job-companies.xml   1 472          employer pages
job-channels.xml      127          facets
job-cities.xml         86          city facets
                    -----
                    4 292 raw = distinct, zero duplicates
```

**Whoever adds up the index publishes 4 292, of which 1 685 are not
advertisements.** That is the `<loc>` trap in its plainest form, and the index
invites it: the four files sit side by side and only their names distinguish
them.

**And 2 607 is not a count of readable advertisements either.** The order of
magnitude is **52** — the URLs carrying the `.php` form. On a stratified
sample: `.php` **4 of 4** serve a real `JobPosting`; without `.php` **0 of 4** —
one 403, two canonical to `rozeegpt.ai`, one homepage. **A factor of about
fifty between the file's length and what it holds.**

## The dissociation, without which "4 of 4" means nothing

**44 of the 52 `.php` URLs are one employer, Mobilink**, so the first three
successes fell there by construction. A `.php` URL from a *different* employer
was fetched to separate the two variables, and it served a `JobPosting` too.

**So it is the form that predicts, not the employer.** Reported by the session
that measured it, and written here because *the sample proves nothing without
the control that split it* — a rate measured on a contiguous block of one
advertiser is the defect `jobsbotswana.md` already carries.

## The sitemap has stopped

**Most recent `lastmod`: 7 June 2026.** Three months before this reading. So
the 2 607 is an archive, not a board, and any freshness count taken from it
would count a file nobody has regenerated.

## Country, and a platform artefact that would poison a location filter

`countries: PK` — `addressCountry: PK`, salaries in **PKR**, and all 86 city
slugs Pakistani.

**`postalCode: 54000` on all three advertisements read** — including one for
**Burewala**, and one carrying no locality at all. **54000 is Lahore.** A
constant stamped by the platform, not a fact about the job, and a filter on
postcode would place the whole board in one city.

*Same family as the PKR on a Saudi line that `mihnati.md` documents: a field
whose value is the platform's habit rather than the advertisement's content.*

## One house, four brands

`mihnati.com` · `rozee.pk` · `rozgar.pk` · `rozeegpt.ai`

**No double count exists today, and that is worth writing down because it is a
prospective risk rather than a present error.** `mihnati.py` enumerates its own
`BASE` and `/EN/` — **not the Pakistani declaration** — and `mihnati.md`
carries no `content:` line, so no figure is published on that side either.

**The risk is born the day somebody follows `mihnati`'s `sitemap:` line
believing they are enumerating a Saudi board.** `_robots.sitemaps_for()` returns
that URL as written, host included, precisely so the reader can see where it
points before asking for it.

## Access

`www.rozee.pk` permits this project's tokens on the paths above; the guard is
taken per path before any fetch, as always. **No adapter is written**: at an
order of magnitude of 52 advertisements in a file whose last update is three
months old, the board does not carry what the count first suggested.
