# Board adapter — Rozee (Pakistan)

<!-- verified: 2026-09-07 -->

<!-- hosts: www.rozee.pk -->
<!-- script: none -->
<!-- countries: PK -->
<!-- content: measured · order of magnitude 52 readable advertisements, from 2 607 `<loc>` in `jobs.xml` of which the `.php` form is 52; 4 292 URLs in the index of which 1 685 are not advertisements · 2026-09-05 -->
<!-- witness: none found — the site serves no counter, and the sitemap's own totals count pages rather than advertisements. **And none is possible from 2026-09-07**: the host answers 403 to its own `robots.txt`, so nothing above can be re-read · figures 2026-09-05, closure 2026-09-07 -->
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

## Where part of the 2 555 goes

**Two advertisement URLs of `jobs.xml` serve the RozeeGPT shell**, byte for
byte identical to `/seeker/`. So a share of the 2 555 non-`.php` URLs are not
failed advertisements: they are a different product's page returned under an
advertisement's address. *That is why the `.php` form predicts and the URL's
directory does not.*

**`rozeegpt.ai` and `recruit-ai.co` are not boards**, and neither is counted
here. `recruit-ai.co` is established as a fifth brand of the house by a
`robots.txt` **identical to the byte** — including two lines naming
subdomains that do not belong to it, which is the kind of copy nobody makes by
accident.

## One house, five brands

`mihnati.com` · `rozee.pk` · `rozgar.pk` · `rozeegpt.ai` · `recruit-ai.co`

**No double count exists today, and that is worth writing down because it is a
prospective risk rather than a present error.** `mihnati.py` enumerates its own
`BASE` and `/EN/` — **not the Pakistani declaration** — and `mihnati.md`
carries no `content:` line, so no figure is published on that side either.

**The risk is born the day somebody follows `mihnati`'s `sitemap:` line
believing they are enumerating a Saudi board.** `_robots.sitemaps_for()` returns
that URL as written, host included, precisely so the reader can see where it
points before asking for it.

## Access — CLOSED since some time between 2026-09-05 and 2026-09-07

**On 2026-09-05 this host permitted this project's tokens, and everything above
was measured under that permission. It no longer does.**

```
2026-09-07 16:02 UTC      www.rozee.pk   AND   rozee.pk
  GET /robots.txt   HTTP 403
  state = refused · kind = host-closed · rule = "/"
  allowed("/") = False · certain = True
```

**This is a change of the HOST's state, not a correction of this card.** *Every
figure above was taken while the door was open and is quoted with its date; a
card corrected for an error and a card overtaken by the world read the same
once rewritten, and only the second one asks the next reader to **re-measure**
rather than to distrust the author.*

### `host-closed` is not `disallowed`, and the difference decides what may be done

**It is NOT the shape the 2026-09-07 decision covers.** *There, the rules opened
a path and a firewall closed that same path — so the browser branch applies.*
**Here the rules file ITSELF answers 403**, so nothing is known about what the
host permits: `host-closed` is the prudent verdict, not the true one.

**And no fingerprint exists to tell a provider wall from the operator.**
`bin/fetch-body.py` stopped at the guard, **before the request** — so there are
no bytes, no vendor header and no md5 to compare against the 25-byte body this
repository holds on ten hosts. *The record is a `rules-refusal`, and
`_provenance` carries no `status`, no `bytes` and no `vendor` for it precisely
because there was no response.*

**What would settle it is one page load in a human browser** — the module says
so itself, and forbids the alternative: *do not rotate, do not retry under
another agent string.* **That question belongs to the repository's owner and is
carried to them; it is not sounded from here.**

### The house is NOT closed — only this host

```
www.rozgar.pk    read · allowed = True · refuses 2 paths to `*`: /beta/, /demo/
www.mihnati.com  read · allowed = True · refuses 17, among them /rozee-a/, /rozee-b/
www.rozee.pk     refused, host-closed          <- this card
```

**`rozee.pk` is the only one of the three that carries an inventory, and the
only one that is shut.** *Written down because a reader who closes the house on
this card's evidence would be closing two hosts that answer.*

### And no adapter, for two independent reasons now

**Before this host closed there was already one**: at an order of magnitude of
52 advertisements in a file whose last update is three months old, the board
does not carry what the count first suggested. **The closure is a second and
sufficient reason, and the first has not gone away** — *if the door reopens, the
52 and the June `lastmod` are still what awaits, and both need re-measuring
before anyone writes a line.*
